"""
@file
@brief Reproducer test for asymmetric post-fetch 429 behavior in _fetch_claude_dual.
@details Verifies that when a live API call returns HTTP 429 (no active cooldown),
and only one window has a last-good cached result on disk, the other window must not
return an error if the available last-good raw payload contains data sufficient to
parse the missing window.
Specifically: 7d disk cache (with full raw payload including five_hour data) must allow
5h to be derived via cross-window re-parse rather than returning "Rate limited. Try
again later.".
@satisfies REQ-002, CTN-004
"""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from aibar.cache import ResultCache
from aibar.providers.base import (
    ProviderName,
    ProviderResult,
    UsageMetrics,
    WindowPeriod,
)
from aibar.providers.claude_oauth import ClaudeOAuthProvider


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_RAW_FULL_PAYLOAD: dict = {
    "five_hour": {
        "utilization": 16.0,
        "resets_at": "2026-03-04T12:00:01+00:00",
    },
    "seven_day": {
        "utilization": 17.0,
        "resets_at": "2026-03-06T06:00:00+00:00",
    },
}


def _make_7d_good_result() -> ProviderResult:
    """
    @brief Build a synthetic successful 7d ProviderResult with full raw payload.
    @details The raw payload contains both five_hour and seven_day keys, matching
    the actual Claude API response shape used by _parse_response.
    @return {ProviderResult} Successful 7d result with full dual-window raw payload.
    """
    return ProviderResult(
        provider=ProviderName.CLAUDE,
        window=WindowPeriod.DAY_7,
        metrics=UsageMetrics(remaining=83.0, limit=100.0),
        raw=_RAW_FULL_PAYLOAD,
    )


def _make_429_results(
    provider: ClaudeOAuthProvider,
) -> dict[WindowPeriod, ProviderResult]:
    """
    @brief Build error results as returned by fetch_all_windows on HTTP 429.
    @details Mirrors the actual shape produced by fetch_all_windows when
    _handle_response returns a 429 error (raw={"status_code": 429}).
    @param provider {ClaudeOAuthProvider} Provider instance used to build error results.
    @return {dict[WindowPeriod, ProviderResult]} Both windows mapped to 429 error results.
    """
    return {
        w: provider._make_error_result(
            window=w,
            error="Rate limited. Try again later.",
            raw={"status_code": 429},
        )
        for w in [WindowPeriod.HOUR_5, WindowPeriod.DAY_7]
    }


# ---------------------------------------------------------------------------
# Reproducer tests (MUST FAIL before fix, MUST PASS after fix)
# ---------------------------------------------------------------------------


class TestFetchClaudeDualPostFetchSymmetry:
    """
    @brief Verify _fetch_claude_dual returns consistent (non-error) results for both
    windows when a live API call returns HTTP 429 and only 7d last-good exists on disk.
    @details Defect scenario (post-fetch path):
        - No active rate-limit cooldown (`claude_rate_limited` absent or expired)
        - Live `fetch_all_windows` call returns 429 error for ALL windows
        - `claude_5h.json` absent (window was never successfully fetched)
        - `claude_7d.json` present (raw payload includes five_hour data)
      Expected: both 5h and 7d results MUST NOT be error results; the 5h result
      MUST be derived from the 7d cached raw payload via cross-window re-parse.
    @satisfies REQ-002, CTN-004
    """

    def test_5h_not_error_when_only_7d_last_good_exists_after_post_fetch_429(
        self,
        tmp_path: Path,
    ) -> None:
        """
        @brief Verify 5h result is non-error when no cooldown, live call returns 429,
        and only 7d disk cache exists (the primary defect reproducer).
        @details Arrange: persist 7d good result to disk (with full raw payload), ensure
        no active cooldown, mock fetch_all_windows to return 429 for both windows.
        Act: call _fetch_claude_dual. Assert: 5h result MUST NOT be an error; its
        metrics.remaining MUST equal 84.0 (100 - 16.0 utilization from five_hour in
        the 7d raw payload). 7d result MUST also be non-error (from disk cache).
        @pre claude_5h.json absent; claude_7d.json present with full raw payload; no cooldown.
        @post Neither 5h nor 7d result is an error result.
        """
        from aibar.cli import _fetch_claude_dual

        cache = ResultCache(cache_dir=tmp_path)
        good_7d = _make_7d_good_result()
        cache._save_to_disk(good_7d)

        # Confirm no active cooldown
        assert not cache.is_rate_limited(ProviderName.CLAUDE), (
            "Cooldown must not be active (this tests the post-fetch path)"
        )
        assert not (tmp_path / "claude_5h.json").exists(), (
            "5h disk cache must be absent"
        )
        assert (tmp_path / "claude_7d.json").exists(), "7d disk cache must be present"

        provider = ClaudeOAuthProvider(token="sk-ant-test-token")
        mock_results = _make_429_results(provider)

        with patch.object(
            ClaudeOAuthProvider,
            "fetch_all_windows",
            new=AsyncMock(return_value=mock_results),
        ):
            result_5h, result_7d = _fetch_claude_dual(provider, cache)

        # 5h result MUST NOT be an error (REQ-002: consistent dual-window output)
        assert not result_5h.is_error, (
            f"Expected 5h result to be non-error but got error: {result_5h.error!r}"
        )
        # 5h metrics must be parsed from five_hour.utilization=16.0 → remaining=84.0
        assert result_5h.metrics.remaining == pytest.approx(84.0), (
            f"Expected 5h remaining=84.0 but got {result_5h.metrics.remaining}"
        )

        # 7d result must also be non-error (falls back to disk cache)
        assert not result_7d.is_error, (
            f"Expected 7d result to be non-error but got error: {result_7d.error!r}"
        )

    def test_7d_not_error_when_only_5h_last_good_exists_after_post_fetch_429(
        self,
        tmp_path: Path,
    ) -> None:
        """
        @brief Verify 7d result is non-error when no cooldown, live call returns 429,
        and only 5h disk cache exists (symmetric scenario).
        @details Arrange: persist 5h good result to disk (with full raw payload), ensure
        no active cooldown, mock fetch_all_windows to return 429 for both windows.
        Act: call _fetch_claude_dual. Assert: 7d result MUST NOT be an error; its
        metrics.remaining MUST equal 83.0 (100 - 17.0 utilization from seven_day in
        the 5h raw payload). 5h result MUST also be non-error (from disk cache).
        @pre claude_7d.json absent; claude_5h.json present with full raw payload; no cooldown.
        @post Neither 5h nor 7d result is an error result.
        """
        from aibar.cli import _fetch_claude_dual

        cache = ResultCache(cache_dir=tmp_path)
        good_5h = ProviderResult(
            provider=ProviderName.CLAUDE,
            window=WindowPeriod.HOUR_5,
            metrics=UsageMetrics(remaining=84.0, limit=100.0),
            raw=_RAW_FULL_PAYLOAD,
        )
        cache._save_to_disk(good_5h)

        assert not cache.is_rate_limited(ProviderName.CLAUDE), (
            "Cooldown must not be active"
        )
        assert not (tmp_path / "claude_7d.json").exists(), (
            "7d disk cache must be absent"
        )
        assert (tmp_path / "claude_5h.json").exists(), "5h disk cache must be present"

        provider = ClaudeOAuthProvider(token="sk-ant-test-token")
        mock_results = _make_429_results(provider)

        with patch.object(
            ClaudeOAuthProvider,
            "fetch_all_windows",
            new=AsyncMock(return_value=mock_results),
        ):
            result_5h, result_7d = _fetch_claude_dual(provider, cache)

        assert not result_7d.is_error, (
            f"Expected 7d result to be non-error but got error: {result_7d.error!r}"
        )
        assert result_7d.metrics.remaining == pytest.approx(83.0), (
            f"Expected 7d remaining=83.0 but got {result_7d.metrics.remaining}"
        )
        assert not result_5h.is_error, (
            f"Expected 5h result to be non-error but got error: {result_5h.error!r}"
        )

    def test_error_returned_when_no_last_good_at_all_after_post_fetch_429(
        self,
        tmp_path: Path,
    ) -> None:
        """
        @brief Verify error result returned for both windows when no cooldown, live call
        returns 429, and no disk cache exists at all for either window.
        @details With no last-good available anywhere, there is no raw payload to parse
        from; both windows must return error results.
        @pre claude_5h.json absent; claude_7d.json absent; no cooldown.
        @post Both 5h and 7d results are error results.
        """
        from aibar.cli import _fetch_claude_dual

        cache = ResultCache(cache_dir=tmp_path)

        assert not cache.is_rate_limited(ProviderName.CLAUDE)
        assert not (tmp_path / "claude_5h.json").exists()
        assert not (tmp_path / "claude_7d.json").exists()

        provider = ClaudeOAuthProvider(token="sk-ant-test-token")
        mock_results = _make_429_results(provider)

        with patch.object(
            ClaudeOAuthProvider,
            "fetch_all_windows",
            new=AsyncMock(return_value=mock_results),
        ):
            result_5h, result_7d = _fetch_claude_dual(provider, cache)

        assert result_5h.is_error, "Expected 5h to be error when no disk cache exists"
        assert result_7d.is_error, "Expected 7d to be error when no disk cache exists"
        assert "Rate limited" in result_5h.error
        assert "Rate limited" in result_7d.error
