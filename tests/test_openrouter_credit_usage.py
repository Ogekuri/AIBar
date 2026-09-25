"""
@file
@brief OpenRouter API credit progress-bar regression tests.
@details Verifies OpenRouter usage metrics and progress bars derive from the
OpenRouter key credit total `data.limit` so the percentage equals
`cost / (cost + remaining) * 100` (equivalent to `cost / limit * 100`),
over-credit spend renders the shared >100 over-limit segment identically to
Copilot over-quota bars, and absent API credit fields normalize to `None`
so renderers fall back to the zero-percent usage display.
@satisfies REQ-011
@satisfies REQ-148
@satisfies REQ-149
@satisfies REQ-150
@satisfies TST-063
"""

import re

from aibar.cli import _build_result_panel
from aibar.providers.base import ProviderName, ProviderResult, UsageMetrics, WindowPeriod
from aibar.providers.openrouter import OpenRouterUsageProvider

_ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    """
    @brief Remove ANSI SGR escape sequences from one string.
    @details Strips provider-color codes so structural bar equality can be compared
    across providers that differ only by base-fill color.
    @param text {str} Possibly ANSI-decorated string.
    @return {str} String with all `\\x1b[...m` sequences removed.
    """
    return _ANSI_ESCAPE_PATTERN.sub("", text)


def _usage_line(name: ProviderName, result: ProviderResult) -> str:
    """
    @brief Extract the first `Usage:` row from one provider panel.
    @param name {ProviderName} Provider enum key for panel rendering.
    @param result {ProviderResult} Provider result payload.
    @return {str} Rendered `Usage: <window> <progress_bar> <percent>%` row.
    """
    _title, lines = _build_result_panel(name, result)
    return next(line for line in lines if line.startswith("Usage:"))


def test_openrouter_parse_response_projects_spend_against_api_credit() -> None:
    """
    @brief Verify OpenRouter metrics derive percentage from API credit total.
    @details With `data.limit=100` and `usage_monthly=50`, `metrics.limit` equals
    the API credit total, `metrics.remaining` equals `limit - cost` residual
    credit, and `usage_percent = cost / (cost + remaining) * 100` resolves to
    `50.0`. Missing `data.limit` normalizes `limit`/`remaining` to `None` so
    `usage_percent` becomes `None` and renderers fall back to zero-percent.
    @return {None} Function return value.
    @satisfies REQ-011
    @satisfies REQ-148
    @satisfies REQ-149
    @satisfies TST-063
    """
    provider = OpenRouterUsageProvider(api_key="test-openrouter-key")

    in_credit = provider._parse_response(
        {"data": {"usage_monthly": 50.0, "limit": 100.0, "limit_remaining": 50.0}},
        WindowPeriod.DAY_30,
    )
    assert in_credit.metrics.limit == 100.0
    assert in_credit.metrics.remaining == 50.0
    assert in_credit.metrics.cost == 50.0
    assert abs(in_credit.metrics.usage_percent - 50.0) < 1e-9
    assert in_credit.raw["data"]["limit"] == 100.0
    assert in_credit.raw["data"]["limit_remaining"] == 50.0

    over_credit = provider._parse_response(
        {"data": {"usage_monthly": 300.0, "limit": 100.0}},
        WindowPeriod.DAY_30,
    )
    assert over_credit.metrics.limit == 100.0
    assert over_credit.metrics.remaining == -200.0
    assert over_credit.metrics.usage_percent is not None
    assert over_credit.metrics.usage_percent > 100.0
    assert abs(over_credit.metrics.usage_percent - 300.0) < 1e-9

    missing_limit = provider._parse_response(
        {"data": {"usage_monthly": 50.0}},
        WindowPeriod.DAY_30,
    )
    assert missing_limit.metrics.limit is None
    assert missing_limit.metrics.remaining is None
    assert missing_limit.metrics.usage_percent is None


def test_openrouter_over_credit_bar_matches_copilot_over_quota_bar() -> None:
    """
    @brief Verify over-credit OpenRouter bar reuses the Copilot over-quota bar mechanism.
    @details At the same >100 percentage, the OpenRouter over-credit bar and a
    Copilot over-quota bar share identical structure (100% boundary marker `|`
    and over-limit segment `▓`) after stripping provider-color ANSI codes,
    proving REQ-150 parity with the Copilot over-quota rendering.
    @return {None} Function return value.
    @satisfies REQ-149
    @satisfies REQ-150
    @satisfies TST-063
    """
    provider = OpenRouterUsageProvider(api_key="test-openrouter-key")
    openrouter_result = provider._parse_response(
        {"data": {"usage_monthly": 150.0, "limit": 100.0}},
        WindowPeriod.DAY_30,
    )
    copilot_result = ProviderResult(
        provider=ProviderName.COPILOT,
        window=WindowPeriod.DAY_30,
        metrics=UsageMetrics(remaining=-50.0, limit=100.0),
    )

    assert abs(openrouter_result.metrics.usage_percent - 150.0) < 1e-9

    openrouter_line = _usage_line(ProviderName.OPENROUTER, openrouter_result)
    copilot_line = _usage_line(ProviderName.COPILOT, copilot_result)

    assert openrouter_line.endswith(" 150.0%")
    assert copilot_line.endswith(" 150.0%")
    assert _strip_ansi(openrouter_line) == _strip_ansi(copilot_line)
    assert "▓" in _strip_ansi(openrouter_line)
    assert "|" in _strip_ansi(openrouter_line)