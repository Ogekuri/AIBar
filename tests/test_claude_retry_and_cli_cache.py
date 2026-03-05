"""
@file
@brief Claude provider retry and cache-bypass tests.
@details Verifies: (1) ClaudeOAuthProvider retries on HTTP 429 respecting
retry-after header, (2) fetch_all_windows uses one API call for dual windows,
(3) Claude CLI fetch path bypasses cache reads/writes and cooldown fallback.
@satisfies CTN-003, CTN-004, REQ-002
"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx

from aibar.cache import ResultCache
from aibar.providers.base import (
    ProviderName,
    ProviderResult,
    UsageMetrics,
    WindowPeriod,
)
from aibar.providers.claude_oauth import ClaudeOAuthProvider


def _make_429_response(retry_after: str = "0") -> httpx.Response:
    """
    @brief Build a mock HTTP 429 response.
    @param retry_after {str} Value for the retry-after header.
    @return {httpx.Response} Mocked 429 response.
    """
    return httpx.Response(
        status_code=429,
        headers={"retry-after": retry_after},
        json={"error": {"message": "Rate limited.", "type": "rate_limit_error"}},
        request=httpx.Request("GET", "https://api.anthropic.com/api/oauth/usage"),
    )


def _make_200_response() -> httpx.Response:
    """
    @brief Build a mock HTTP 200 usage response with both windows.
    @return {httpx.Response} Mocked 200 response.
    """
    return httpx.Response(
        status_code=200,
        json={
            "five_hour": {
                "utilization": 20.0,
                "resets_at": "2026-03-06T12:00:00+00:00",
            },
            "seven_day": {
                "utilization": 30.0,
                "resets_at": "2026-03-10T06:00:00+00:00",
            },
        },
        request=httpx.Request("GET", "https://api.anthropic.com/api/oauth/usage"),
    )


def _make_good_result(window: WindowPeriod) -> ProviderResult:
    """
    @brief Build a synthetic successful ProviderResult.
    @param window {WindowPeriod} Window period for the result.
    @return {ProviderResult} Successful result with sample metrics.
    """
    return ProviderResult(
        provider=ProviderName.CLAUDE,
        window=window,
        metrics=UsageMetrics(remaining=80.0, limit=100.0),
        raw={"five_hour": {"utilization": 20.0}, "seven_day": {"utilization": 30.0}},
    )


class TestClaudeRetryOn429:
    """
    @brief Verify ClaudeOAuthProvider retries on HTTP 429.
    @satisfies CTN-003
    """

    def test_retries_on_429_then_succeeds(self) -> None:
        """
        @brief Verify provider retries after 429 and returns success on subsequent attempt.
        """
        provider = ClaudeOAuthProvider(token="sk-ant-test-token")
        mock_responses = [_make_429_response("0"), _make_200_response()]

        with patch("aibar.providers.claude_oauth.asyncio.sleep", new_callable=AsyncMock):
            with patch("aibar.providers.claude_oauth.random.uniform", return_value=0.0):
                with patch.object(
                    httpx.AsyncClient,
                    "get",
                    new_callable=AsyncMock,
                    side_effect=mock_responses,
                ):
                    result = asyncio.run(provider.fetch(WindowPeriod.DAY_7))

        assert not result.is_error
        assert result.metrics.remaining == 70.0

    def test_returns_error_after_max_retries_exhausted(self) -> None:
        """
        @brief Verify provider returns rate-limit error when all retries fail.
        @details MAX_RETRIES=3 implies one initial request plus three retries.
        """
        provider = ClaudeOAuthProvider(token="sk-ant-test-token")
        all_429 = [_make_429_response("0")] * 4

        with patch("aibar.providers.claude_oauth.asyncio.sleep", new_callable=AsyncMock):
            with patch("aibar.providers.claude_oauth.random.uniform", return_value=0.0):
                with patch.object(
                    httpx.AsyncClient,
                    "get",
                    new_callable=AsyncMock,
                    side_effect=all_429,
                ):
                    result = asyncio.run(provider.fetch(WindowPeriod.DAY_7))

        assert result.is_error
        assert "Rate limited" in result.error


class TestFetchAllWindows:
    """
    @brief Verify fetch_all_windows makes a single API call for multiple windows.
    @satisfies REQ-002
    """

    def test_single_call_returns_both_windows(self) -> None:
        """
        @brief Verify one HTTP request produces results for both 5h and 7d.
        """
        provider = ClaudeOAuthProvider(token="sk-ant-test-token")

        with patch.object(
            httpx.AsyncClient,
            "get",
            new_callable=AsyncMock,
            return_value=_make_200_response(),
        ) as mock_get:
            results = asyncio.run(
                provider.fetch_all_windows([WindowPeriod.HOUR_5, WindowPeriod.DAY_7])
            )

        assert mock_get.call_count == 1
        assert WindowPeriod.HOUR_5 in results
        assert WindowPeriod.DAY_7 in results
        assert results[WindowPeriod.HOUR_5].metrics.remaining == 80.0
        assert results[WindowPeriod.DAY_7].metrics.remaining == 70.0


class TestCLICacheBypassForClaude:
    """
    @brief Verify Claude CLI fetch path bypasses cache and cooldown fallback.
    @satisfies CTN-004
    """

    def test_fetch_result_ignores_cached_value_for_claude(self, tmp_path: Path) -> None:
        """
        @brief Verify _fetch_result calls Claude provider even when a stale disk cache exists.
        """
        from aibar.cli import _fetch_result

        cache = ResultCache(cache_dir=tmp_path)
        cache._save_to_disk(_make_good_result(WindowPeriod.DAY_7))

        fresh_result = ProviderResult(
            provider=ProviderName.CLAUDE,
            window=WindowPeriod.DAY_7,
            metrics=UsageMetrics(remaining=55.0, limit=100.0),
            raw={"fresh": True},
        )

        provider = MagicMock(spec=ClaudeOAuthProvider)
        provider.name = ProviderName.CLAUDE
        provider.fetch = AsyncMock(return_value=fresh_result)

        result = _fetch_result(provider, WindowPeriod.DAY_7, cache=cache)

        provider.fetch.assert_awaited_once_with(WindowPeriod.DAY_7)
        assert result.metrics.remaining == 55.0

    def test_fetch_result_no_last_good_fallback_for_claude_errors(
        self,
        tmp_path: Path,
    ) -> None:
        """
        @brief Verify Claude fetch errors are returned directly without last-good cache fallback.
        """
        from aibar.cli import _fetch_result

        cache = ResultCache(cache_dir=tmp_path)
        cache._save_to_disk(_make_good_result(WindowPeriod.DAY_7))

        error_result = ProviderResult(
            provider=ProviderName.CLAUDE,
            window=WindowPeriod.DAY_7,
            metrics=UsageMetrics(),
            error="Rate limited. Try again later.",
            raw={"status_code": 429},
        )

        provider = ClaudeOAuthProvider(token="sk-ant-test-token")

        with patch.object(
            ClaudeOAuthProvider,
            "fetch",
            new_callable=AsyncMock,
            return_value=error_result,
        ):
            result = _fetch_result(provider, WindowPeriod.DAY_7, cache=cache)

        assert result.is_error
        assert "Rate limited" in result.error


class TestClaudeCooldownBypass:
    """
    @brief Verify ResultCache cooldown markers are disabled for Claude.
    @satisfies CTN-004
    """

    def test_cache_set_does_not_activate_cooldown_on_429_for_claude(
        self,
        tmp_path: Path,
    ) -> None:
        """
        @brief Verify cache.set does not enable Claude cooldown on 429 payload.
        """
        cache = ResultCache(cache_dir=tmp_path)
        error_result = ProviderResult(
            provider=ProviderName.CLAUDE,
            window=WindowPeriod.DAY_7,
            metrics=UsageMetrics(),
            error="Rate limited. Try again later.",
            raw={"status_code": 429},
        )

        cache.set(error_result)

        assert not cache.is_rate_limited(ProviderName.CLAUDE)

    def test_get_last_good_returns_none_for_claude(self, tmp_path: Path) -> None:
        """
        @brief Verify get_last_good ignores Claude disk payloads.
        """
        cache = ResultCache(cache_dir=tmp_path)
        cache._save_to_disk(_make_good_result(WindowPeriod.DAY_7))

        assert cache.get_last_good(ProviderName.CLAUDE, WindowPeriod.DAY_7) is None
