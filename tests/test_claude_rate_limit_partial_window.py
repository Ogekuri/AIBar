"""
@file
@brief Claude HTTP 429 partial-window rendering tests.
@details Verifies the CLI dual-window Claude path keeps the rate-limit error in
the 5h section only while rendering 100% usage and reset lines for both 5h/7d.
@satisfies REQ-036
@satisfies TST-011
"""

from pathlib import Path
from unittest.mock import AsyncMock, patch

from aibar.cache import ResultCache
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
        raw={"status_code": 429},
    )


def test_claude_429_renders_partial_window_output(capsys, tmp_path: Path) -> None:
    """
    @brief Verify Claude dual-window CLI output on HTTP 429 is asymmetric by design.
    @details Asserts 5h keeps the error line while 7d suppresses it, and both windows
    preserve 100.0% usage plus `Resets in:` rendering.
    @param capsys {_pytest.capture.CaptureFixture[str]} Output capture fixture.
    @param tmp_path {Path} Temporary cache directory fixture.
    @return {None} Function return value.
    @satisfies REQ-036
    @satisfies TST-011
    """
    provider = ClaudeOAuthProvider(token="sk-ant-test-token")
    cache = ResultCache(cache_dir=tmp_path)
    live_429 = {
        WindowPeriod.HOUR_5: _make_429_result(WindowPeriod.HOUR_5),
        WindowPeriod.DAY_7: _make_429_result(WindowPeriod.DAY_7),
    }

    with patch.object(
        ClaudeOAuthProvider,
        "fetch_all_windows",
        new=AsyncMock(return_value=live_429),
    ):
        result_5h, result_7d = _fetch_claude_dual(provider, cache)

    assert result_5h.is_error
    assert not result_7d.is_error
    assert result_5h.metrics.usage_percent == 100.0
    assert result_7d.metrics.usage_percent == 100.0
    assert result_5h.metrics.reset_at is not None
    assert result_7d.metrics.reset_at is not None

    _print_result(ProviderName.CLAUDE, result_5h, label="5h")
    _print_result(ProviderName.CLAUDE, result_7d, label="7d")
    output = capsys.readouterr().out

    assert output.count("Error: Rate limited. Try again later.") == 1
    assert output.count("Usage:") == 2
    assert output.count("100.0%") == 2
    assert output.count("Resets in:") == 2
