"""
@file
@brief Reproducer test for stale 5h reset_at projection in _fetch_claude_dual.
@details Verifies that when rate-limit cooldown is active and the only available
cache is a stale 7d result whose five_hour.resets_at is in the past, the 5h
result derived via cross-window re-parse MUST carry a projected future reset_at
(the next 5h boundary after the last known resets_at) rather than None.
The defect: _fetch_claude_dual calls _parse_response(sibling_raw, HOUR_5) which
correctly returns reset_at=None (past timestamp guard), but this causes 'Resets in:'
to be suppressed in _print_result even though the window WILL reset at the next 5h
boundary computed from the last known resets_at.
@satisfies REQ-002
"""

import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

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

_WINDOW_PERIOD_SECONDS: dict[WindowPeriod, float] = {
    WindowPeriod.HOUR_5: 5.0 * 3600.0,
    WindowPeriod.DAY_7: 7.0 * 86400.0,
    WindowPeriod.DAY_30: 30.0 * 86400.0,
}


def _past_iso(hours_ago: float) -> str:
    """
    @brief Build an ISO 8601 UTC timestamp that is `hours_ago` hours before now.
    @param hours_ago {float} Positive offset before current UTC time in hours.
    @return {str} ISO 8601 UTC timestamp string with +00:00 suffix.
    """
    dt = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    return dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")


def _compute_expected_next_reset(resets_at_str: str, window: WindowPeriod) -> datetime:
    """
    @brief Compute the expected next projected reset boundary for a given window.
    @details Advances resets_at by multiples of the window period until the result
    is strictly in the future relative to current UTC time. Used as the canonical
    expected value in assertions to avoid clock-sensitive comparisons.
    @param resets_at_str {str} ISO 8601 timestamp of the last known reset boundary.
    @param window {WindowPeriod} Window period whose duration to use for projection.
    @return {datetime} Projected future reset datetime in UTC.
    """
    period_seconds = _WINDOW_PERIOD_SECONDS[window]
    last = datetime.fromisoformat(resets_at_str.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    elapsed = (now - last).total_seconds()
    if elapsed <= 0:
        return last
    cycles = math.ceil(elapsed / period_seconds)
    return last + timedelta(seconds=cycles * period_seconds)


# ---------------------------------------------------------------------------
# Static Analysis Artifact (HDT Generator mode)
# UUT: cli._fetch_claude_dual (cooldown path + cross-window re-parse)
# Call graph: _fetch_claude_dual -> cache.get_last_good -> provider._parse_response
#             -> _project_next_reset (new helper)
# Level: 1 (depends on ResultCache, ClaudeOAuthProvider._parse_response – Level 0)
# External deps: asyncio, httpx (mocked via patch on fetch_all_windows)
# ---------------------------------------------------------------------------


class TestClaudeDualStaleResetProjection:
    """
    @brief Verify _fetch_claude_dual projects the next 5h reset boundary when the
    cross-window re-parse yields reset_at=None due to a past resets_at timestamp.
    @details
    - MUST FAIL before fix: 5h result.metrics.reset_at is None (past-timestamp guard
      in _parse_response discards the stale resets_at, no projection applied).
    - MUST PASS after fix: 5h result.metrics.reset_at is a projected future datetime
      equal to the next 5h boundary after the last known resets_at.
    @satisfies REQ-002
    """

    def test_5h_reset_at_projected_when_stale_7d_cache_during_cooldown(
        self,
        tmp_path: Path,
    ) -> None:
        """
        @brief Verify 5h reset_at is a projected future datetime when 7d stale cache
        is the only source and its five_hour.resets_at is in the past.
        @details Arrange: stale 7d disk cache with five_hour.resets_at = 25 hours ago
        (simulating 5h windows having cycled multiple times since the cache was written);
        activate rate-limit cooldown; no 5h disk cache present.
        Act: call _fetch_claude_dual.
        Assert: 5h result is not an error AND result.metrics.reset_at is not None AND
        reset_at is strictly in the future AND reset_at is close to the expected projected
        next 5h boundary computed from the stale resets_at.
        @pre claude_5h.json absent; claude_7d.json present with five_hour.resets_at 25h ago.
        @post 5h result.metrics.reset_at is a future datetime within 1 second of expected.
        """
        from aibar.cli import _fetch_claude_dual

        stale_resets_at_str = _past_iso(25.0)
        raw_payload: dict = {
            "five_hour": {
                "utilization": 16.0,
                "resets_at": stale_resets_at_str,
            },
            "seven_day": {
                "utilization": 17.0,
                "resets_at": _past_iso(0.5),  # also past, to avoid sibling being used
            },
        }

        cache = ResultCache(cache_dir=tmp_path)
        good_7d = ProviderResult(
            provider=ProviderName.CLAUDE,
            window=WindowPeriod.DAY_7,
            metrics=UsageMetrics(remaining=83.0, limit=100.0),
            raw=raw_payload,
        )
        cache._save_to_disk(good_7d)
        cache.set_rate_limited(ProviderName.CLAUDE)

        # Confirm preconditions
        assert not (tmp_path / "claude_5h.json").exists(), (
            "5h disk cache must be absent"
        )
        assert (tmp_path / "claude_7d.json").exists(), "7d disk cache must be present"
        assert cache.is_rate_limited(ProviderName.CLAUDE), (
            "Rate limit cooldown must be active"
        )

        provider = ClaudeOAuthProvider(token="sk-ant-test-token")

        with patch.object(ClaudeOAuthProvider, "fetch_all_windows") as mock_fetch:
            result_5h, result_7d = _fetch_claude_dual(provider, cache)

        mock_fetch.assert_not_called()

        # 5h result must not be an error
        assert not result_5h.is_error, (
            f"Expected 5h to be non-error but got: {result_5h.error!r}"
        )

        # reset_at MUST be a projected future datetime (not None)
        assert result_5h.metrics.reset_at is not None, (
            "Expected 5h reset_at to be a projected future datetime, but got None. "
            "This means 'Resets in:' is suppressed in the display for the CLAUDE (5h) "
            "section even though the next 5h reset boundary is known."
        )

        now = datetime.now(timezone.utc)
        assert result_5h.metrics.reset_at > now, (
            f"Expected 5h reset_at to be in the future but got "
            f"{result_5h.metrics.reset_at!r} vs now={now!r}"
        )

        # reset_at should be close to the expected projected boundary (within 2 seconds)
        expected = _compute_expected_next_reset(
            stale_resets_at_str, WindowPeriod.HOUR_5
        )
        delta_seconds = abs((result_5h.metrics.reset_at - expected).total_seconds())
        assert delta_seconds < 2.0, (
            f"Expected 5h reset_at close to projected boundary {expected!r} "
            f"but got {result_5h.metrics.reset_at!r} (delta={delta_seconds:.2f}s)"
        )

    def test_5h_reset_at_not_projected_when_stale_raw_has_future_resets_at(
        self,
        tmp_path: Path,
    ) -> None:
        """
        @brief Verify 5h reset_at is set directly (not projected) when the stale raw
        payload's five_hour.resets_at is already in the future.
        @details This test confirms the projection logic does not interfere when
        _parse_response can already produce a valid future reset_at on its own.
        Arrange: 7d disk cache with five_hour.resets_at = 3 hours from now; activate
        rate-limit cooldown; no 5h disk cache.
        Act: call _fetch_claude_dual.
        Assert: 5h result.metrics.reset_at is not None and is in the future.
        @pre five_hour.resets_at is 3 hours in the future.
        @post 5h result.metrics.reset_at is a future datetime (no projection needed).
        """
        from datetime import timedelta

        from aibar.cli import _fetch_claude_dual

        future_resets_at = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime(
            "%Y-%m-%dT%H:%M:%S+00:00"
        )
        raw_payload: dict = {
            "five_hour": {
                "utilization": 50.0,
                "resets_at": future_resets_at,
            },
            "seven_day": {
                "utilization": 30.0,
                "resets_at": (datetime.now(timezone.utc) + timedelta(days=5)).strftime(
                    "%Y-%m-%dT%H:%M:%S+00:00"
                ),
            },
        }

        cache = ResultCache(cache_dir=tmp_path)
        good_7d = ProviderResult(
            provider=ProviderName.CLAUDE,
            window=WindowPeriod.DAY_7,
            metrics=UsageMetrics(remaining=70.0, limit=100.0),
            raw=raw_payload,
        )
        cache._save_to_disk(good_7d)
        cache.set_rate_limited(ProviderName.CLAUDE)

        assert not (tmp_path / "claude_5h.json").exists()

        provider = ClaudeOAuthProvider(token="sk-ant-test-token")

        with patch.object(ClaudeOAuthProvider, "fetch_all_windows") as mock_fetch:
            result_5h, _ = _fetch_claude_dual(provider, cache)

        mock_fetch.assert_not_called()

        assert not result_5h.is_error
        assert result_5h.metrics.reset_at is not None, (
            "Expected reset_at to be set when resets_at is already in the future"
        )
        assert result_5h.metrics.reset_at > datetime.now(timezone.utc)

    def test_5h_reset_at_projected_when_stale_5h_cache_used_as_last_good(
        self,
        tmp_path: Path,
    ) -> None:
        """
        @brief Verify 5h reset_at is projected when the 5h last-good cache itself
        has a stale (past) resets_at and is returned directly via get_last_good
        after TTL expiry forces the normal cache.get path to miss.
        @details When get_last_good returns the stale 5h disk result directly
        (not via cross-window re-parse), the stored ProviderResult already has
        reset_at=None (set during the original parse). This test verifies the
        projection is applied to that direct last-good path as well.
        Arrange: stale 5h disk cache written with updated_at 25 hours ago (TTL
        expired; cache.get returns None); raw payload has five_hour.resets_at 12h
        ago and reset_at stored as None; activate rate-limit cooldown; no 7d disk
        cache. Act: call _fetch_claude_dual.
        Assert: 5h result.metrics.reset_at is a projected future datetime.
        @pre claude_5h.json present with updated_at 25h ago (TTL-expired, get_last_good
             path) and stored reset_at=None (stale resets_at).
        @post 5h result.metrics.reset_at is projected future datetime.
        """
        import json

        from aibar.cli import _fetch_claude_dual

        stale_resets_at_str = _past_iso(12.0)
        raw_payload: dict = {
            "five_hour": {
                "utilization": 80.0,
                "resets_at": stale_resets_at_str,
            },
            "seven_day": {
                "utilization": 10.0,
                "resets_at": _past_iso(2.0),
            },
        }
        # Write the disk file directly with an old updated_at so that cache.get
        # (TTL check) misses and the result is only accessible via get_last_good.
        stale_updated_at = (datetime.now(timezone.utc) - timedelta(hours=25)).strftime(
            "%Y-%m-%dT%H:%M:%S.%f"
        )
        disk_data: dict = {
            "provider": "claude",
            "window": "5h",
            "metrics": {
                "cost": None,
                "requests": None,
                "input_tokens": None,
                "output_tokens": None,
                "remaining": 20.0,
                "limit": 100.0,
                "reset_at": None,
            },
            "updated_at": stale_updated_at,
            "raw": raw_payload,
            "error": None,
        }
        disk_path = tmp_path / "claude_5h.json"
        disk_path.write_text(json.dumps(disk_data))

        cache = ResultCache(cache_dir=tmp_path)
        cache.set_rate_limited(ProviderName.CLAUDE)

        assert disk_path.exists()
        assert not (tmp_path / "claude_7d.json").exists()

        # Confirm TTL-expired: cache.get must return None; get_last_good must return result
        assert cache.get(ProviderName.CLAUDE, WindowPeriod.HOUR_5) is None, (
            "cache.get must miss (TTL expired) so get_last_good path is exercised"
        )
        assert (
            cache.get_last_good(ProviderName.CLAUDE, WindowPeriod.HOUR_5) is not None
        ), "get_last_good must return the stale disk result"

        provider = ClaudeOAuthProvider(token="sk-ant-test-token")

        with patch.object(ClaudeOAuthProvider, "fetch_all_windows") as mock_fetch:
            result_5h, _ = _fetch_claude_dual(provider, cache)

        mock_fetch.assert_not_called()

        assert not result_5h.is_error, (
            f"Expected 5h non-error but got: {result_5h.error!r}"
        )

        assert result_5h.metrics.reset_at is not None, (
            "Expected 5h reset_at to be projected when last-good has None reset_at "
            "but raw payload contains a past resets_at string."
        )
        assert result_5h.metrics.reset_at > datetime.now(timezone.utc), (
            "Expected projected reset_at to be in the future"
        )
