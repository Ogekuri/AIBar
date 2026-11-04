"""
@file
@brief Claude provider retry and shared CLI fetch tests.
@details Verifies: (1) ClaudeOAuthProvider retries on HTTP 429 respecting
retry-after header, (2) fetch_all_windows uses one API call for dual windows,
(3) CLI shared refresh helper routes Claude 5h/7d reads through one dual-window
fetch implementation without legacy ResultCache usage, (4) in-process 429
retry sleeps stay bounded so server-advised long Retry-After values cannot
stall a `show` execution.
HTTP-pipeline tests restrict assertions to success/error state, window key presence,
and HTTP call count; specific numeric metric values MUST NOT be asserted per TST-021.
@satisfies CTN-003, CTN-004, REQ-002, REQ-040, REQ-041, REQ-042, REQ-043, TST-021
"""

import asyncio
import email.utils
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import httpx

from aibar.config import RuntimeConfig
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


def _format_http_date_retry_after(delay_seconds: int) -> str:
    """
    @brief Build HTTP-date Retry-After header value relative to current UTC.
    @details Produces RFC 7231 IMF-fixdate string for deterministic provider
    header parsing tests where retry-after is not numeric.
    @param delay_seconds {int} Positive delay from current UTC.
    @return {str} Retry-After HTTP-date string.
    """
    retry_after_at = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)
    return email.utils.format_datetime(retry_after_at, usegmt=True)


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


def _make_result(window: WindowPeriod, remaining: float) -> ProviderResult:
    """
    @brief Build a synthetic successful ProviderResult for helper tests.
    @param window {WindowPeriod} Window period for the result.
    @param remaining {float} Remaining quota value to encode.
    @return {ProviderResult} Successful result with deterministic metrics.
    """
    return ProviderResult(
        provider=ProviderName.CLAUDE,
        window=window,
        metrics=UsageMetrics(remaining=remaining, limit=100.0),
        raw={},
    )


class TestClaudeRetryOn429:
    """
    @brief Verify ClaudeOAuthProvider retries on HTTP 429.
    @satisfies CTN-003
    """

    def test_retries_on_429_then_succeeds(self) -> None:
        """
        @brief Verify provider retries after 429 and returns success on subsequent attempt.
        @details Asserts behavioral outcome (success/error state) only; does not assert
        specific parsed metric values per TST-021.
        @satisfies TST-021
        """
        provider = ClaudeOAuthProvider(token="sk-ant-test-token")
        mock_responses = [_make_429_response("0"), _make_200_response()]

        with patch(
            "aibar.providers.claude_oauth.asyncio.sleep", new_callable=AsyncMock
        ):
            with patch("aibar.providers.claude_oauth.random.uniform", return_value=0.0):
                with patch.object(
                    httpx.AsyncClient,
                    "get",
                    new_callable=AsyncMock,
                    side_effect=mock_responses,
                ):
                    result = asyncio.run(provider.fetch(WindowPeriod.DAY_7))

        assert not result.is_error

    def test_returns_error_after_max_retries_exhausted(self) -> None:
        """
        @brief Verify provider returns rate-limit error when all retries fail.
        @details MAX_RETRIES=3 implies one initial request plus three retries.
        """
        provider = ClaudeOAuthProvider(token="sk-ant-test-token")
        all_429 = [_make_429_response("0")] * 4

        with patch(
            "aibar.providers.claude_oauth.asyncio.sleep", new_callable=AsyncMock
        ):
            with patch("aibar.providers.claude_oauth.random.uniform", return_value=0.0):
                with patch.object(
                    httpx.AsyncClient,
                    "get",
                    new_callable=AsyncMock,
                    side_effect=all_429,
                ):
                    result = asyncio.run(provider.fetch(WindowPeriod.DAY_7))

        assert result.is_error
        assert result.error is not None
        assert "Rate limited" in result.error

    def test_http_date_retry_after_is_preserved_for_idle_time(self) -> None:
        """
        @brief Verify final Claude 429 result preserves HTTP-date retry-after delay.
        @details Uses HTTP-date header format (non-numeric) and asserts provider
        stores positive `raw.retry_after_seconds` for CLI idle-time expansion.
        @satisfies REQ-041
        @satisfies TST-011
        """
        provider = ClaudeOAuthProvider(token="sk-ant-test-token")
        retry_after_header = _format_http_date_retry_after(7200)
        all_429 = [_make_429_response(retry_after_header)] * 4

        with patch(
            "aibar.providers.claude_oauth.asyncio.sleep", new_callable=AsyncMock
        ):
            with patch("aibar.providers.claude_oauth.random.uniform", return_value=0.0):
                with patch.object(
                    httpx.AsyncClient,
                    "get",
                    new_callable=AsyncMock,
                    side_effect=all_429,
                ):
                    result = asyncio.run(provider.fetch(WindowPeriod.DAY_7))

        assert result.is_error
        assert result.raw["status_code"] == 429
        assert result.raw["retry_after_seconds"] >= 3600

    def test_epoch_retry_after_header_is_normalized_to_relative_delay(self) -> None:
        """
        @brief Verify epoch Retry-After headers are normalized to relative seconds.
        @details Simulates Claude HTTP 429 responses carrying Unix-epoch seconds in
        `retry-after` and asserts provider output preserves a bounded relative delay
        suitable for idle-time scheduling instead of a raw epoch timestamp.
        @satisfies REQ-041
        @satisfies TST-011
        """
        provider = ClaudeOAuthProvider(token="sk-ant-test-token")
        retry_after_epoch = int(datetime.now(timezone.utc).timestamp()) + 900
        all_429 = [_make_429_response(str(retry_after_epoch))] * 4

        with patch(
            "aibar.providers.claude_oauth.asyncio.sleep", new_callable=AsyncMock
        ):
            with patch("aibar.providers.claude_oauth.random.uniform", return_value=0.0):
                with patch.object(
                    httpx.AsyncClient,
                    "get",
                    new_callable=AsyncMock,
                    side_effect=all_429,
                ):
                    result = asyncio.run(provider.fetch(WindowPeriod.DAY_7))

        assert result.is_error
        assert result.raw["status_code"] == 429
        assert 899 <= result.raw["retry_after_seconds"] <= 901


class TestClaudeRetryDelayBound:
    """
    @brief Verify Claude 429 in-process retry sleeps stay bounded.
    @details Reproducer for the `aibar show` indefinite-stall defect:
    server-advised `Retry-After` values (Anthropic hourly quota ~3600s)
    were passed unbounded to `asyncio.sleep` inside
    `ClaudeOAuthProvider._request_usage`, stalling each CLI execution for
    hours. Asserts (a) every in-process retry sleep respects
    `ClaudeOAuthProvider.IN_PROCESS_RETRY_DELAY_CAP_SECONDS` plus jitter, and
    (b) server-advised delays above the cap short-circuit in-process retries
    (exactly one HTTP call) so the REQ-041 CLI idle-time policy defers the
    next attempt across runs, minimizing provider API requests per REQ-042.
    @satisfies REQ-040
    @satisfies REQ-041
    @satisfies REQ-042
    """

    def test_long_server_retry_after_bounded_in_process(self) -> None:
        """
        @brief Verify long server Retry-After values do not stall `show`.
        @details Rate-limited responses carrying `Retry-After: 3600` must
        surface the 429 result without hour-long in-process sleeps and
        without futile HTTP retries against a server that already advised
        a long wait. Asserts error state, recorded sleep delays, and HTTP
        call count only per TST-021.
        @satisfies REQ-040, REQ-041, REQ-042
        @satisfies TST-021
        """
        provider = ClaudeOAuthProvider(token="sk-ant-test-token")
        all_429 = [_make_429_response("3600")] * 4
        sleep_mock = AsyncMock(return_value=None)

        with patch("aibar.providers.claude_oauth.asyncio.sleep", sleep_mock):
            with patch(
                "aibar.providers.claude_oauth.random.uniform", return_value=0.0
            ):
                with patch.object(
                    httpx.AsyncClient,
                    "get",
                    new_callable=AsyncMock,
                    side_effect=all_429,
                ) as mock_get:
                    result = asyncio.run(provider.fetch(WindowPeriod.DAY_7))

        cap = ClaudeOAuthProvider.IN_PROCESS_RETRY_DELAY_CAP_SECONDS
        max_delay = cap + ClaudeOAuthProvider.RETRY_JITTER_MAX
        recorded_delays = [float(call.args[0]) for call in sleep_mock.await_args_list]
        assert result.is_error
        assert result.raw["status_code"] == 429
        assert all(delay <= max_delay for delay in recorded_delays)
        assert mock_get.call_count == 1

    def test_small_server_retry_after_still_retries_within_cap(self) -> None:
        """
        @brief Verify small server Retry-After values keep the retry path.
        @details `Retry-After` values within the in-process cap must keep the
        documented bounded retry sequence and succeed on the second attempt,
        with every sleep clamped to the cap plus jitter while preserving the
        REQ-040 minimum inter-call delay semantics. Asserts success state,
        recorded sleep delays, and HTTP call count only per TST-021.
        @satisfies REQ-040
        @satisfies TST-021
        """
        provider = ClaudeOAuthProvider(token="sk-ant-test-token")
        mock_responses = [_make_429_response("3"), _make_200_response()]
        sleep_mock = AsyncMock(return_value=None)

        with patch("aibar.providers.claude_oauth.asyncio.sleep", sleep_mock):
            with patch(
                "aibar.providers.claude_oauth.random.uniform", return_value=0.0
            ):
                with patch(
                    "aibar.config.load_runtime_config", return_value=RuntimeConfig()
                ):
                    with patch.object(
                        httpx.AsyncClient,
                        "get",
                        new_callable=AsyncMock,
                        side_effect=mock_responses,
                    ) as mock_get:
                        result = asyncio.run(provider.fetch(WindowPeriod.DAY_7))

        cap = ClaudeOAuthProvider.IN_PROCESS_RETRY_DELAY_CAP_SECONDS
        max_delay = cap + ClaudeOAuthProvider.RETRY_JITTER_MAX
        recorded_delays = [float(call.args[0]) for call in sleep_mock.await_args_list]
        assert not result.is_error
        assert mock_get.call_count == 2
        assert recorded_delays
        assert all(delay <= max_delay for delay in recorded_delays)


class TestFetchAllWindows:
    """
    @brief Verify fetch_all_windows makes a single API call for multiple windows.
    @satisfies REQ-002
    """

    def test_single_call_returns_both_windows(self) -> None:
        """
        @brief Verify one HTTP request produces results for both 5h and 7d.
        @details Asserts HTTP call count and window key presence only; does not assert
        specific parsed metric values per TST-021.
        @satisfies TST-021
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


class TestCLISharedClaudeFetch:
    """
    @brief Verify CLI helper routes Claude requests through dual-window fetch.
    @satisfies CTN-004
    @satisfies REQ-043
    """

    def test_fetch_result_routes_day7_to_dual_fetch(self) -> None:
        """
        @brief Verify `_fetch_result` returns 7d branch from `_fetch_claude_dual`.
        """
        from aibar.cli import _fetch_result

        provider = ClaudeOAuthProvider(token="sk-ant-test-token")
        result_5h = _make_result(WindowPeriod.HOUR_5, remaining=73.0)
        result_7d = _make_result(WindowPeriod.DAY_7, remaining=64.0)

        with patch(
            "aibar.cli._fetch_claude_dual",
            return_value=(result_5h, result_7d),
        ) as mock_dual:
            selected = _fetch_result(provider, WindowPeriod.DAY_7)

        mock_dual.assert_called_once_with(provider, throttle_state=None)
        assert selected.window == WindowPeriod.DAY_7
        assert selected.metrics.remaining == 64.0

    def test_fetch_result_routes_5h_to_dual_fetch(self) -> None:
        """
        @brief Verify `_fetch_result` returns 5h branch from `_fetch_claude_dual`.
        """
        from aibar.cli import _fetch_result

        provider = ClaudeOAuthProvider(token="sk-ant-test-token")
        result_5h = _make_result(WindowPeriod.HOUR_5, remaining=57.0)
        result_7d = _make_result(WindowPeriod.DAY_7, remaining=48.0)

        with patch(
            "aibar.cli._fetch_claude_dual",
            return_value=(result_5h, result_7d),
        ) as mock_dual:
            selected = _fetch_result(provider, WindowPeriod.HOUR_5)

        mock_dual.assert_called_once_with(provider, throttle_state=None)
        assert selected.window == WindowPeriod.HOUR_5
        assert selected.metrics.remaining == 57.0
