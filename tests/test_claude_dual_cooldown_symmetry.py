"""
@file
@brief Claude dual-window cache-bypass tests.
@details Verifies `_fetch_claude_dual` always performs a fresh API request and
never falls back to Claude cache/cooldown artifacts.
@satisfies CTN-004, REQ-002
"""

from pathlib import Path
from unittest.mock import AsyncMock, patch

from aibar.cache import ResultCache
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

        cache = ResultCache(cache_dir=tmp_path)
        cache._save_to_disk(_make_success_result(WindowPeriod.HOUR_5, 77.0))
        cache._save_to_disk(_make_success_result(WindowPeriod.DAY_7, 66.0))
        cache.set_rate_limited(ProviderName.CLAUDE)

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
            result_5h, result_7d = _fetch_claude_dual(provider, cache)

        mock_fetch.assert_awaited_once_with([WindowPeriod.HOUR_5, WindowPeriod.DAY_7])
        assert result_5h.metrics.remaining == 55.0
        assert result_7d.metrics.remaining == 44.0

    def test_dual_fetch_returns_live_errors_without_cache_fallback(
        self,
        tmp_path: Path,
    ) -> None:
        """
        @brief Verify `_fetch_claude_dual` returns live 429 errors even when Claude cache exists.
        """
        from aibar.cli import _fetch_claude_dual

        cache = ResultCache(cache_dir=tmp_path)
        cache._save_to_disk(_make_success_result(WindowPeriod.DAY_7, 83.0))

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
            result_5h, result_7d = _fetch_claude_dual(provider, cache)

        assert result_5h.is_error
        assert result_7d.is_error
        assert "Rate limited" in result_5h.error
        assert "Rate limited" in result_7d.error
