"""
@file
@brief Textual UI rate-limit rendering regressions.
@details Verifies ProviderCard helper logic suppresses rate-limit error banner text
for quota-carrying payloads and appends `⚠️ Limit reached!` to reset labels when
usage renders as `100.0%`.
@satisfies REQ-008
@satisfies TST-012
"""

from aibar.providers.base import ProviderName, ProviderResult, UsageMetrics, WindowPeriod
from aibar.ui import ProviderCard


def _make_result(
    provider: ProviderName,
    window: WindowPeriod,
    *,
    remaining: float | None,
    limit: float | None,
    error: str | None = None,
) -> ProviderResult:
    """
    @brief Build ProviderResult fixture for ProviderCard helper-method tests.
    @param provider {ProviderName} Provider identity for the result.
    @param window {WindowPeriod} Window identity for the result.
    @param remaining {float | None} Remaining credits value.
    @param limit {float | None} Limit credits value.
    @param error {str | None} Optional error string.
    @return {ProviderResult} Deterministic ProviderResult fixture.
    """
    return ProviderResult(
        provider=provider,
        window=window,
        metrics=UsageMetrics(
            remaining=remaining,
            limit=limit,
            reset_at=None,
            cost=None,
            requests=None,
            input_tokens=None,
            output_tokens=None,
        ),
        error=error,
        raw={},
    )


def test_provider_card_classifies_rate_limit_quota_errors() -> None:
    """
    @brief Verify rate-limit quota payload classification for Textual cards.
    @satisfies REQ-008
    @satisfies TST-012
    """
    card = ProviderCard(ProviderName.CLAUDE)

    rate_limited = _make_result(
        ProviderName.CLAUDE,
        WindowPeriod.HOUR_5,
        remaining=0.0,
        limit=100.0,
        error="Rate limited. Try again later.",
    )
    assert card._is_rate_limit_quota_error(rate_limited)

    not_rate_limited = _make_result(
        ProviderName.CLAUDE,
        WindowPeriod.HOUR_5,
        remaining=0.0,
        limit=100.0,
        error="Unexpected error",
    )
    assert not card._is_rate_limit_quota_error(not_rate_limited)

    no_quota_metrics = _make_result(
        ProviderName.CLAUDE,
        WindowPeriod.HOUR_5,
        remaining=None,
        limit=None,
        error="Rate limited. Try again later.",
    )
    assert not card._is_rate_limit_quota_error(no_quota_metrics)


def test_provider_card_limit_reached_hint_scope_and_rounding() -> None:
    """
    @brief Verify `Limit reached!` hint is restricted to requested provider/windows.
    @details Also verifies one-decimal display rounding, where `99.96` maps to `100.0`.
    @satisfies REQ-008
    @satisfies TST-012
    """
    card = ProviderCard(ProviderName.CLAUDE)

    claude_rounded_full = _make_result(
        ProviderName.CLAUDE,
        WindowPeriod.HOUR_5,
        remaining=0.04,
        limit=100.0,
    )
    assert card._should_show_limit_reached_hint(claude_rounded_full)

    codex_full = _make_result(
        ProviderName.CODEX,
        WindowPeriod.DAY_7,
        remaining=0.0,
        limit=100.0,
    )
    assert card._should_show_limit_reached_hint(codex_full)

    copilot_full = _make_result(
        ProviderName.COPILOT,
        WindowPeriod.DAY_30,
        remaining=0.0,
        limit=100.0,
    )
    assert card._should_show_limit_reached_hint(copilot_full)

    openrouter_full = _make_result(
        ProviderName.OPENROUTER,
        WindowPeriod.DAY_7,
        remaining=0.0,
        limit=100.0,
    )
    assert not card._should_show_limit_reached_hint(openrouter_full)


def test_provider_card_formats_reset_value_with_limit_reached_suffix() -> None:
    """
    @brief Verify reset value formatter appends warning suffix only when required.
    @satisfies REQ-008
    @satisfies TST-012
    """
    card = ProviderCard(ProviderName.CLAUDE)

    full_usage = _make_result(
        ProviderName.CLAUDE,
        WindowPeriod.HOUR_5,
        remaining=0.0,
        limit=100.0,
    )
    assert card._format_reset_value("1h 25m", full_usage) == "1h 25m ⚠️ Limit reached!"

    partial_usage = _make_result(
        ProviderName.CLAUDE,
        WindowPeriod.HOUR_5,
        remaining=60.0,
        limit=100.0,
    )
    assert card._format_reset_value("1h 25m", partial_usage) == "1h 25m"
