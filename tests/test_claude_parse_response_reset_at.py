"""
@file
@brief Reproducer test for asymmetric 'Resets in:' display in CLAUDE (5h) vs CLAUDE (7d).
@details Verifies that _parse_response sets metrics.reset_at=None when resets_at from
the API payload is already in the past, preventing stale past timestamps from propagating
to the display layer where they would silently suppress 'Resets in:' output asymmetrically
between 5h and 7d windows.
The defect: the 5h window's resets_at in stale cached data is in the past (5h windows
reset every 5 hours), while 7d resets_at may still be in the future. This causes
'Resets in:' to display for 7d but not for 5h even though both windows should render
symmetrically when fresh data is available.
@satisfies REQ-002
"""

from datetime import datetime, timedelta, timezone

from aibar.providers.base import WindowPeriod
from aibar.providers.claude_oauth import ClaudeOAuthProvider


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _future_iso(hours_from_now: float) -> str:
    """
    @brief Build an ISO 8601 timestamp string that is `hours_from_now` hours in the future.
    @param hours_from_now {float} Positive offset from current UTC time in hours.
    @return {str} ISO 8601 UTC timestamp string with +00:00 suffix.
    """
    dt = datetime.now(timezone.utc) + timedelta(hours=hours_from_now)
    return dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")


def _past_iso(hours_ago: float) -> str:
    """
    @brief Build an ISO 8601 timestamp string that is `hours_ago` hours in the past.
    @param hours_ago {float} Positive offset before current UTC time in hours.
    @return {str} ISO 8601 UTC timestamp string with +00:00 suffix.
    """
    dt = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    return dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")


# ---------------------------------------------------------------------------
# Static Analysis Artifact (HDT Generator mode)
# UUT: ClaudeOAuthProvider._parse_response
# Call graph: _parse_response -> datetime.fromisoformat -> UsageMetrics -> ProviderResult
# Level: 0 (atomic - no internal project dependencies called)
# External deps: datetime (standard library; no isolation needed)
# ---------------------------------------------------------------------------


class TestParseResponseResetAt:
    """
    @brief Verify _parse_response correctly propagates or nullifies reset_at based on
    whether the resets_at timestamp in the API payload is in the future or the past.
    @details
    - MUST FAIL before fix: past resets_at propagated as non-None reset_at → display
      incorrectly suppressed in _print_result via `delta.total_seconds() > 0` guard.
    - MUST PASS after fix: past resets_at yields reset_at=None; future yields valid datetime.
    @satisfies REQ-002
    """

    def test_reset_at_is_none_when_resets_at_is_in_the_past_for_5h_window(self) -> None:
        """
        @brief Verify reset_at is None when five_hour.resets_at is in the past.
        @details Arrange: full API payload with five_hour.resets_at set to 1 hour ago.
        Act: call _parse_response for HOUR_5 window. Assert: result.metrics.reset_at is None.
        This is the primary defect reproducer: a past resets_at must not propagate.
        @pre five_hour.resets_at is 1 hour before current UTC time.
        @post result.metrics.reset_at is None.
        """
        provider = ClaudeOAuthProvider(token="sk-ant-test-token")
        data = {
            "five_hour": {
                "utilization": 16.0,
                "resets_at": _past_iso(1.0),
            },
            "seven_day": {
                "utilization": 17.0,
                "resets_at": _future_iso(48.0),
            },
        }

        result = provider._parse_response(data, WindowPeriod.HOUR_5)

        assert not result.is_error
        assert result.metrics.reset_at is None, (
            f"Expected reset_at=None for past resets_at but got {result.metrics.reset_at!r}"
        )

    def test_reset_at_is_none_when_resets_at_is_in_the_past_for_7d_window(self) -> None:
        """
        @brief Verify reset_at is None when seven_day.resets_at is in the past.
        @details Arrange: full API payload with seven_day.resets_at set to 2 hours ago.
        Act: call _parse_response for DAY_7 window. Assert: result.metrics.reset_at is None.
        Symmetric case: past resets_at must be suppressed regardless of window.
        @pre seven_day.resets_at is 2 hours before current UTC time.
        @post result.metrics.reset_at is None.
        """
        provider = ClaudeOAuthProvider(token="sk-ant-test-token")
        data = {
            "five_hour": {
                "utilization": 16.0,
                "resets_at": _future_iso(3.0),
            },
            "seven_day": {
                "utilization": 17.0,
                "resets_at": _past_iso(2.0),
            },
        }

        result = provider._parse_response(data, WindowPeriod.DAY_7)

        assert not result.is_error
        assert result.metrics.reset_at is None, (
            f"Expected reset_at=None for past resets_at but got {result.metrics.reset_at!r}"
        )

    def test_reset_at_is_set_when_resets_at_is_in_the_future_for_5h_window(
        self,
    ) -> None:
        """
        @brief Verify reset_at is a valid future datetime when five_hour.resets_at is in future.
        @details Arrange: full API payload with five_hour.resets_at set to 4 hours from now.
        Act: call _parse_response for HOUR_5 window. Assert: result.metrics.reset_at is not None
        and is in the future (total_seconds > 0).
        Happy path: fresh API data with future resets_at must propagate.
        @pre five_hour.resets_at is 4 hours after current UTC time.
        @post result.metrics.reset_at is a non-None datetime in the future.
        """
        provider = ClaudeOAuthProvider(token="sk-ant-test-token")
        data = {
            "five_hour": {
                "utilization": 16.0,
                "resets_at": _future_iso(4.0),
            },
            "seven_day": {
                "utilization": 17.0,
                "resets_at": _future_iso(48.0),
            },
        }

        result = provider._parse_response(data, WindowPeriod.HOUR_5)

        assert not result.is_error
        assert result.metrics.reset_at is not None, (
            "Expected reset_at to be set for future resets_at"
        )
        delta = result.metrics.reset_at - datetime.now(timezone.utc)
        assert delta.total_seconds() > 0, (
            f"Expected future reset_at but delta={delta.total_seconds():.1f}s"
        )

    def test_reset_at_is_set_when_resets_at_is_in_the_future_for_7d_window(
        self,
    ) -> None:
        """
        @brief Verify reset_at is a valid future datetime when seven_day.resets_at is in future.
        @details Arrange: full API payload with seven_day.resets_at set to 48 hours from now.
        Act: call _parse_response for DAY_7 window. Assert: result.metrics.reset_at is not None
        and is in the future.
        Symmetric happy path: future resets_at must propagate for 7d window.
        @pre seven_day.resets_at is 48 hours after current UTC time.
        @post result.metrics.reset_at is a non-None datetime in the future.
        """
        provider = ClaudeOAuthProvider(token="sk-ant-test-token")
        data = {
            "five_hour": {
                "utilization": 16.0,
                "resets_at": _future_iso(4.0),
            },
            "seven_day": {
                "utilization": 17.0,
                "resets_at": _future_iso(48.0),
            },
        }

        result = provider._parse_response(data, WindowPeriod.DAY_7)

        assert not result.is_error
        assert result.metrics.reset_at is not None, (
            "Expected reset_at to be set for future resets_at"
        )
        delta = result.metrics.reset_at - datetime.now(timezone.utc)
        assert delta.total_seconds() > 0, (
            f"Expected future reset_at but delta={delta.total_seconds():.1f}s"
        )

    def test_reset_at_is_none_when_resets_at_field_absent(self) -> None:
        """
        @brief Verify reset_at is None when resets_at key is absent from window data.
        @details Arrange: API payload without resets_at in five_hour section.
        Act: call _parse_response for HOUR_5 window. Assert: result.metrics.reset_at is None.
        Boundary case: missing resets_at must not raise and must yield None.
        @pre five_hour has no resets_at key.
        @post result.metrics.reset_at is None; result.is_error is False.
        """
        provider = ClaudeOAuthProvider(token="sk-ant-test-token")
        data = {
            "five_hour": {
                "utilization": 30.0,
            },
            "seven_day": {
                "utilization": 20.0,
                "resets_at": _future_iso(48.0),
            },
        }

        result = provider._parse_response(data, WindowPeriod.HOUR_5)

        assert not result.is_error
        assert result.metrics.reset_at is None, (
            f"Expected reset_at=None when resets_at absent but got {result.metrics.reset_at!r}"
        )

    def test_reset_at_is_none_when_resets_at_is_invalid_iso_string(self) -> None:
        """
        @brief Verify reset_at is None when resets_at contains an unparseable string.
        @details Arrange: API payload with five_hour.resets_at set to a non-ISO string.
        Act: call _parse_response for HOUR_5 window. Assert: result.metrics.reset_at is None.
        Error boundary: malformed resets_at must be silently ignored per existing try/except.
        @pre five_hour.resets_at is "not-a-datetime".
        @post result.metrics.reset_at is None; result.is_error is False.
        """
        provider = ClaudeOAuthProvider(token="sk-ant-test-token")
        data = {
            "five_hour": {
                "utilization": 30.0,
                "resets_at": "not-a-datetime",
            },
        }

        result = provider._parse_response(data, WindowPeriod.HOUR_5)

        assert not result.is_error
        assert result.metrics.reset_at is None, (
            f"Expected reset_at=None for invalid resets_at but got {result.metrics.reset_at!r}"
        )
