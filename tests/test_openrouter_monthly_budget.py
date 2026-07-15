"""
@file
@brief OpenRouter monthly budget progress-bar regression tests.
@details Verifies OpenRouter usage metrics and progress bars derive from the
configured `openrouter_monthly_budget` (default `200`) so the percentage equals
`cost / budget * 100`, over-budget spend renders the shared >100 over-limit
segment identically to Copilot over-quota bars, and the API key limit is no
longer the progress-bar denominator. Setup-persistence coverage for the budget
field lives in `tests/test_setup_runtime_config.py`.
@satisfies REQ-011
@satisfies REQ-148
@satisfies REQ-149
@satisfies REQ-150
@satisfies TST-063
"""

import re
from pathlib import Path

from aibar import config as config_module
from aibar.cli import _build_result_panel
from aibar.providers.base import ProviderName, ProviderResult, UsageMetrics, WindowPeriod
from aibar.providers.openrouter import OpenRouterUsageProvider

_ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[[0-9;]*m")
_BUDGET = 200.0


def _patch_config_paths(monkeypatch, tmp_path: Path) -> Path:
    """
    @brief Redirect AIBar config/cache file paths to a temporary directory.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {Path} Effective `~/.config/aibar` replacement directory.
    """
    config_dir = tmp_path / ".config" / "aibar"
    cache_dir = tmp_path / ".cache" / "aibar"
    monkeypatch.setattr(config_module, "APP_CONFIG_DIR", config_dir)
    monkeypatch.setattr(config_module, "APP_CACHE_DIR", cache_dir)
    monkeypatch.setattr(config_module, "ENV_FILE_PATH", config_dir / "env")
    monkeypatch.setattr(
        config_module, "RUNTIME_CONFIG_PATH", config_dir / "config.json"
    )
    monkeypatch.setattr(config_module, "CACHE_FILE_PATH", cache_dir / "cache.json")
    monkeypatch.setattr(config_module, "IDLE_TIME_PATH", cache_dir / "idle-time.json")
    return config_dir


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


def test_openrouter_parse_response_projects_spend_against_configured_budget(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify OpenRouter metrics derive percentage from configured budget.
    @details With `openrouter_monthly_budget=200`, in-budget spend yields
    `usage_percent = cost / budget * 100` with `metrics.limit=budget` and
    `metrics.remaining=budget-cost`; the API key `limit`/`limit_remaining`
    remain in `raw.data` but MUST NOT drive the metrics. Over-budget spend
    yields a negative `remaining` and a percentage above `100`.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-011
    @satisfies REQ-148
    @satisfies REQ-149
    @satisfies TST-063
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        config_module.RuntimeConfig(openrouter_monthly_budget=_BUDGET)
    )
    provider = OpenRouterUsageProvider(api_key="test-openrouter-key")

    in_budget = provider._parse_response(
        {"data": {"usage_monthly": 50.0, "limit": 10.0, "limit_remaining": 5.0}},
        WindowPeriod.DAY_30,
    )
    assert in_budget.metrics.limit == _BUDGET
    assert in_budget.metrics.remaining == _BUDGET - 50.0
    assert in_budget.metrics.cost == 50.0
    assert abs(in_budget.metrics.usage_percent - 25.0) < 1e-9
    assert in_budget.raw["data"]["limit"] == 10.0
    assert in_budget.raw["data"]["limit_remaining"] == 5.0

    over_budget = provider._parse_response(
        {"data": {"usage_monthly": 300.0}},
        WindowPeriod.DAY_30,
    )
    assert over_budget.metrics.limit == _BUDGET
    assert over_budget.metrics.remaining == _BUDGET - 300.0
    assert over_budget.metrics.usage_percent is not None
    assert over_budget.metrics.usage_percent > 100.0
    assert abs(over_budget.metrics.usage_percent - 150.0) < 1e-9


def test_openrouter_over_budget_bar_matches_copilot_over_quota_bar(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify over-budget OpenRouter bar reuses the Copilot over-quota bar mechanism.
    @details At the same >100 percentage, the OpenRouter over-budget bar and a
    Copilot over-quota bar share identical structure (100% boundary marker `|`
    and over-limit segment `▓`) after stripping provider-color ANSI codes,
    proving REQ-150 parity with the Copilot over-quota rendering.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-149
    @satisfies REQ-150
    @satisfies TST-063
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        config_module.RuntimeConfig(openrouter_monthly_budget=_BUDGET)
    )
    provider = OpenRouterUsageProvider(api_key="test-openrouter-key")
    openrouter_result = provider._parse_response(
        {"data": {"usage_monthly": 300.0}},
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
