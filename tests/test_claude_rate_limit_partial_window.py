"""
@file
@brief Claude HTTP 429 error-only rendering tests.
@details Verifies Claude dual-window fetch preserves explicit errors for both
windows and CLI output suppresses metric/statistic lines on failed states.
@satisfies REQ-036
@satisfies REQ-037
@satisfies TST-038
"""

from unittest.mock import AsyncMock, patch

from aibar.cli import _fetch_claude_dual, _print_result
from aibar.providers.base import ProviderName, ProviderResult, UsageMetrics, WindowPeriod
from aibar.providers.claude_oauth import ClaudeOAuthProvider


def _make_429_result(window: WindowPeriod) -> ProviderResult:
    """
    @brief Build synthetic Claude HTTP 429 ProviderResult for a window.
    @param window {WindowPeriod} Target window period.
    @return {ProviderResult} Error result with status marker payload.
    """
    return ProviderResult(
        provider=ProviderName.CLAUDE,
        window=window,
        metrics=UsageMetrics(),
        error="Rate limited. Try again later.",
        raw={"status_code": 429, "retry_after_seconds": 300},
    )


def test_claude_429_renders_error_only_output_for_both_windows(capsys) -> None:
    """
    @brief Verify Claude dual-window CLI output suppresses all statistics on HTTP 429.
    @details Asserts both windows remain in failed state and only render error plus
    combined HTTP status/retry diagnostics.
    @param capsys {_pytest.capture.CaptureFixture[str]} Output capture fixture.
    @return {None} Function return value.
    @satisfies REQ-036
    @satisfies REQ-037
    @satisfies TST-038
    """
    provider = ClaudeOAuthProvider(token="sk-ant-test-token")
    live_429 = {
        WindowPeriod.HOUR_5: _make_429_result(WindowPeriod.HOUR_5),
        WindowPeriod.DAY_7: _make_429_result(WindowPeriod.DAY_7),
    }

    with patch.object(
        ClaudeOAuthProvider,
        "fetch_all_windows",
        new=AsyncMock(return_value=live_429),
    ):
        result_5h, result_7d = _fetch_claude_dual(provider)

    assert result_5h.is_error
    assert result_7d.is_error

    _print_result(ProviderName.CLAUDE, result_5h, label="5h")
    _print_result(ProviderName.CLAUDE, result_7d, label="7d")
    output = capsys.readouterr().out

    assert output.count("Error: Rate limited. Try again later.") == 2
    assert output.count("HTTP status: 429, Retry after: 300 sec.") == 2
    assert "Usage:" not in output
    assert "Resets in:" not in output
    assert "Remaining credits:" not in output
