"""
@file
@brief Copilot cost derivation regression tests.
@details Verifies Copilot monetary overage derives from `metrics.remaining`
sign semantics so `show` text, `show --json`, and GNOME surfaces receive
consistent `metrics.cost` values.
@satisfies REQ-012
@satisfies REQ-117
@satisfies REQ-118
"""

import pytest

from aibar.config import RuntimeConfig
from aibar.providers.base import WindowPeriod
from aibar.providers.copilot import CopilotProvider


def _parse_copilot_snapshot(
    monkeypatch: pytest.MonkeyPatch,
    snapshot: dict[str, float],
    unit_cost: float,
):
    """
    @brief Parse one synthetic Copilot quota snapshot.
    @details Injects deterministic runtime config unit-cost and executes
    `CopilotProvider._parse_response` with one `premiumInteractions` snapshot.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param snapshot {dict[str, float]} Copilot quota snapshot payload.
    @param unit_cost {float} Configured monetary value per extra request.
    @return {ProviderResult} Parsed Copilot provider result.
    """

    def _fake_load_runtime_config() -> RuntimeConfig:
        """
        @brief Return deterministic runtime configuration for test execution.
        @details Restricts runtime configuration surface to configured Copilot
        overage unit cost while preserving defaults for unrelated fields.
        @return {RuntimeConfig} Runtime configuration object.
        """

        return RuntimeConfig(copilot_extra_premium_request_cost=unit_cost)

    monkeypatch.setattr("aibar.config.load_runtime_config", _fake_load_runtime_config)
    provider = CopilotProvider(token="copilot-test-token")
    return provider._parse_response(
        {"quotaSnapshots": {"premiumInteractions": snapshot}},
        WindowPeriod.DAY_30,
    )


def test_copilot_cost_is_zero_when_remaining_is_positive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    @brief Verify positive `remaining` suppresses Copilot overage cost.
    @details Uses contradictory raw premium fields (`premium_requests_extra=20`)
    and asserts normalized result uses `remaining=5` as authority, yielding
    `cost=0` and `premium_requests_extra_cost=0`.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    """
    result = _parse_copilot_snapshot(
        monkeypatch=monkeypatch,
        snapshot={
            "entitlement": 100.0,
            "remaining": 5.0,
            "premium_requests": 120.0,
            "premium_requests_included": 100.0,
            "premium_requests_extra": 20.0,
        },
        unit_cost=0.25,
    )

    assert result.metrics.remaining == pytest.approx(5.0)
    assert result.metrics.limit == pytest.approx(100.0)
    assert result.metrics.cost == pytest.approx(0.0)
    assert result.raw["premium_requests"] == pytest.approx(95.0)
    assert result.raw["premium_requests_extra"] == pytest.approx(0.0)
    assert result.raw["premium_requests_extra_cost"] == pytest.approx(0.0)


def test_copilot_cost_uses_negative_remaining_magnitude(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    @brief Verify negative `remaining` maps to positive monetary overage.
    @details Asserts `cost = -remaining * unit_cost` and normalized premium
    fields are aligned with the same overage semantics.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    """
    result = _parse_copilot_snapshot(
        monkeypatch=monkeypatch,
        snapshot={
            "entitlement": 100.0,
            "remaining": -3.0,
        },
        unit_cost=0.25,
    )

    assert result.metrics.remaining == pytest.approx(-3.0)
    assert result.metrics.limit == pytest.approx(100.0)
    assert result.metrics.cost == pytest.approx(0.75)
    assert result.raw["premium_requests"] == pytest.approx(103.0)
    assert result.raw["premium_requests_extra"] == pytest.approx(3.0)
    assert result.raw["premium_requests_extra_cost"] == pytest.approx(0.75)
