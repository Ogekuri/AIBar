"""
@file
@brief Claude HTTP 429 partial-window rendering tests.
@details Verifies the CLI dual-window Claude path keeps rate-limit error text in
the 5h section while restoring 7d usage/reset values from persisted Claude payload.
@satisfies REQ-036
@satisfies TST-011
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
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
        raw={"status_code": 429},
    )


def _write_claude_snapshot(
    cache_home: Path,
    reset_5h: datetime,
    reset_7d: datetime,
) -> None:
    """
    @brief Persist synthetic Claude dual-window payload for 429 fallback tests.
    @param cache_home {Path} Temporary cache-home root path.
    @param reset_5h {datetime} Future reset timestamp for five-hour window.
    @param reset_7d {datetime} Future reset timestamp for seven-day window.
    @return {None} Function return value.
    """
    payload = {
        "five_hour": {
            "utilization": 40.0,
            "resets_at": reset_5h.isoformat(),
        },
        "seven_day": {
            "utilization": 40.0,
            "resets_at": reset_7d.isoformat(),
        },
    }
    snapshot_path = cache_home / "aibar" / "claude_dual_last_success.json"
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(json.dumps(payload), encoding="utf-8")


def test_claude_429_renders_partial_window_output(capsys, tmp_path: Path) -> None:
    """
    @brief Verify Claude dual-window CLI output on HTTP 429 keeps persisted 7d metrics.
    @details Asserts 5h keeps rate-limit error and `100.0%` usage, while 7d restores
    usage from persisted payload (`40.0%`) and both windows render reset lines.
    @param capsys {_pytest.capture.CaptureFixture[str]} Output capture fixture.
    @param tmp_path {Path} Temporary cache directory fixture.
    @return {None} Function return value.
    @satisfies REQ-036
    @satisfies TST-011
    """
    now = datetime.now(timezone.utc)
    reset_5h = now + timedelta(hours=1, minutes=25)
    reset_7d = now + timedelta(hours=12, minutes=25)

    with patch.dict("os.environ", {"XDG_CACHE_HOME": str(tmp_path)}):
        _write_claude_snapshot(tmp_path, reset_5h=reset_5h, reset_7d=reset_7d)

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
        assert not result_7d.is_error
        assert result_5h.metrics.usage_percent == 100.0
        assert result_7d.metrics.usage_percent == 40.0
        assert result_5h.metrics.reset_at is not None
        assert result_7d.metrics.reset_at is not None

        delta_5h = result_5h.metrics.reset_at - now
        delta_7d = result_7d.metrics.reset_at - now
        assert 83 * 60 <= delta_5h.total_seconds() <= 86 * 60
        assert 743 * 60 <= delta_7d.total_seconds() <= 746 * 60

        _print_result(ProviderName.CLAUDE, result_5h, label="5h")
        _print_result(ProviderName.CLAUDE, result_7d, label="7d")
        output = capsys.readouterr().out

        assert output.count("Error: Rate limited. Try again later.") == 1
        assert output.count("Usage:") == 2
        assert "100.0%" in output
        assert "40.0%" in output
        assert output.count("Resets in:") == 2
