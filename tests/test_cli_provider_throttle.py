"""
@file
@brief Provider API throttling helper tests.
@details Verifies inter-call delay helper sleeps for the remaining interval
between consecutive provider API calls.
@satisfies REQ-040
@satisfies TST-016
"""

from unittest.mock import patch

from aibar.cli import _apply_api_call_delay


def test_apply_api_call_delay_waits_for_remaining_interval() -> None:
    """
    @brief Verify throttling helper enforces configured minimum spacing.
    @details First call initializes timing state; second call at +0.2s with
    1000ms delay must sleep for ~0.8s before allowing the next call.
    @return {None} Function return value.
    @satisfies REQ-040
    @satisfies TST-016
    """
    throttle_state: dict[str, float | int] = {"delay_milliseconds": 1000}
    with patch("aibar.cli.time.monotonic", side_effect=[100.0, 100.0, 100.2, 100.2]):
        with patch("aibar.cli.time.sleep") as sleep_mock:
            _apply_api_call_delay(throttle_state)
            _apply_api_call_delay(throttle_state)

    sleep_mock.assert_called_once()
    assert abs(float(sleep_mock.call_args.args[0]) - 0.8) < 0.001
