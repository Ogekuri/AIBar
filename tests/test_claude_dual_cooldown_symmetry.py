"""
@file
@brief Claude dual-window cache-bypass tests.
@details Verifies `_fetch_claude_dual` always performs a fresh API request and
never falls back to Claude TTL cache/cooldown artifacts.
@satisfies CTN-004, REQ-002
"""

from pathlib import Path
from unittest.mock import AsyncMock, patch

from aibar.providers.base import (
    ProviderName,
    ProviderResult,
    UsageMetrics,
    WindowPeriod,
)
from aibar.providers.claude_oauth import ClaudeOAuthProvider


def _make_success_result(window: WindowPeriod, remaining: float) -> ProviderResult:
    """
    @brief Build a synthetic successful Claude result.
    @param window {WindowPeriod} Window period for the result.
    @param remaining {float} Remaining percentage to encode in metrics.
    @return {ProviderResult} Successful Claude provider result.
    """
    return ProviderResult(
        provider=ProviderName.CLAUDE,
        window=window,
        metrics=UsageMetrics(remaining=remaining, limit=100.0),
        raw={
            "five_hour": {"utilization": 100.0 - remaining},
            "seven_day": {"utilization": 100.0 - remaining},
        },
    )


def _make_429_result(provider: ClaudeOAuthProvider, window: WindowPeriod) -> ProviderResult:
    """
    @brief Build a Claude 429 error result.
    @param provider {ClaudeOAuthProvider} Provider used to materialize error result.
    @param window {WindowPeriod} Window associated with the error.
    @return {ProviderResult} Error result with status_code=429 marker.
    """
    return provider._make_error_result(
        window=window,
        error="Rate limited. Try again later.",
        raw={"status_code": 429},
    )


class TestClaudeDualFetchBypass:
    """
    @brief Verify Claude dual-window fetch path bypasses cache reads/writes.
    @satisfies CTN-004
    """

    def test_dual_fetch_uses_api_even_when_cache_files_exist(self, tmp_path: Path) -> None:
        """
        @brief Verify `_fetch_claude_dual` ignores pre-existing Claude disk cache files.
        """
        from aibar.cli import _fetch_claude_dual

        with patch.dict("os.environ", {"XDG_CACHE_HOME": str(tmp_path)}):
            provider = ClaudeOAuthProvider(token="sk-ant-test-token")
            fresh = {
                WindowPeriod.HOUR_5: _make_success_result(WindowPeriod.HOUR_5, 55.0),
                WindowPeriod.DAY_7: _make_success_result(WindowPeriod.DAY_7, 44.0),
            }

            with patch.object(
                ClaudeOAuthProvider,
                "fetch_all_windows",
                new=AsyncMock(return_value=fresh),
            ) as mock_fetch:
                result_5h, result_7d = _fetch_claude_dual(provider)

        mock_fetch.assert_awaited_once_with([WindowPeriod.HOUR_5, WindowPeriod.DAY_7])
        assert result_5h.metrics.remaining == 55.0
        assert result_7d.metrics.remaining == 44.0

    def test_dual_fetch_does_not_write_legacy_snapshot_file(
        self,
        tmp_path: Path,
    ) -> None:
        """
        @brief Verify successful dual-window fetch does not write legacy snapshot file.
        @satisfies REQ-047
        """
        from aibar.cli import _fetch_claude_dual

        with patch.dict("os.environ", {"XDG_CACHE_HOME": str(tmp_path)}):
            raw_payload = {
                "five_hour": {
                    "utilization": 22.0,
                    "resets_at": "2026-03-05T19:00:00+00:00",
                },
                "seven_day": {
                    "utilization": 40.0,
                    "resets_at": "2026-03-06T06:00:00+00:00",
                },
            }
            provider = ClaudeOAuthProvider(token="sk-ant-test-token")
            fresh = {
                WindowPeriod.HOUR_5: ProviderResult(
                    provider=ProviderName.CLAUDE,
                    window=WindowPeriod.HOUR_5,
                    metrics=UsageMetrics(remaining=78.0, limit=100.0),
                    raw=raw_payload,
                ),
                WindowPeriod.DAY_7: ProviderResult(
                    provider=ProviderName.CLAUDE,
                    window=WindowPeriod.DAY_7,
                    metrics=UsageMetrics(remaining=60.0, limit=100.0),
                    raw=raw_payload,
                ),
            }

            with patch.object(
                ClaudeOAuthProvider,
                "fetch_all_windows",
                new=AsyncMock(return_value=fresh),
            ):
                result_5h, result_7d = _fetch_claude_dual(provider)

            snapshot_path = tmp_path / "aibar" / "claude_dual_last_success.json"
            assert not snapshot_path.exists()
            assert result_5h.metrics.remaining == 78.0
            assert result_7d.metrics.remaining == 60.0

    def test_dual_fetch_returns_live_errors_without_cache_fallback(
        self,
        tmp_path: Path,
    ) -> None:
        """
        @brief Verify `_fetch_claude_dual` normalizes HTTP 429 to partial-window output.
        """
        from aibar.cli import _fetch_claude_dual

        with patch.dict("os.environ", {"XDG_CACHE_HOME": str(tmp_path)}):
            provider = ClaudeOAuthProvider(token="sk-ant-test-token")
            errors = {
                WindowPeriod.HOUR_5: _make_429_result(provider, WindowPeriod.HOUR_5),
                WindowPeriod.DAY_7: _make_429_result(provider, WindowPeriod.DAY_7),
            }

            with patch.object(
                ClaudeOAuthProvider,
                "fetch_all_windows",
                new=AsyncMock(return_value=errors),
            ):
                result_5h, result_7d = _fetch_claude_dual(provider)

        assert result_5h.is_error
        assert not result_7d.is_error
        assert result_5h.error is not None
        assert "Rate limited" in result_5h.error
        assert result_5h.metrics.usage_percent == 100.0
        assert result_7d.metrics.usage_percent == 100.0
        assert result_5h.metrics.reset_at is not None
        assert result_7d.metrics.reset_at is not None
