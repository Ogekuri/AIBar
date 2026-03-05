"""
@file
@brief Reproducer tests for Claude 429 retry logic and CLI cache integration.
@details Verifies: (1) ClaudeOAuthProvider retries on HTTP 429 respecting
retry-after header, (2) CLI show path uses ResultCache before API calls,
(3) CLI show falls back to last-good cached data on fetch errors,
(4) fetch_all_windows makes a single API call for both 5h and 7d windows.
@satisfies CTN-004, CTN-003, REQ-002
"""

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

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
        """
        provider = ClaudeOAuthProvider(token="sk-ant-test-token")
        all_429 = [_make_429_response("0")] * 3

        with patch("aibar.providers.claude_oauth.asyncio.sleep", new_callable=AsyncMock):
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


class TestCLICacheIntegration:
    """
    @brief Verify CLI show path uses cache (CTN-004) and falls back on errors.
    @satisfies CTN-004
    """

    def test_fetch_result_returns_cached_value(self, tmp_path: Path) -> None:
        """
        @brief Verify _fetch_result returns cached result without calling provider.
        """
        from aibar.cli import _fetch_result

        cache = ResultCache(cache_dir=tmp_path)
        good_result = _make_good_result(WindowPeriod.DAY_7)
        cache.set(good_result)

        provider = MagicMock(spec=ClaudeOAuthProvider)
        provider.name = ProviderName.CLAUDE

        result = _fetch_result(provider, WindowPeriod.DAY_7, cache=cache)
        assert result.metrics.remaining == 80.0
        provider.fetch.assert_not_called()

    def test_fetch_result_falls_back_to_last_good_on_error(self, tmp_path: Path) -> None:
        """
        @brief Verify _fetch_result falls back to last-good cached data on provider error.
        """
        from aibar.cli import _fetch_result

        cache = ResultCache(cache_dir=tmp_path)
        good_result = _make_good_result(WindowPeriod.DAY_7)
        cache._save_to_disk(good_result)
        cache._memory_cache.clear()

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

        assert not result.is_error
        assert result.metrics.remaining == 80.0
