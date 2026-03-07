"""
@file
@brief HTTP 429 idle-time update tests for CLI refresh.
@details Verifies idle-time persistence uses max(idle-delay, retry-after) and
selects the largest retry-after value when multiple 429 responses are returned.
@satisfies REQ-041
@satisfies TST-011
"""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from click.testing import CliRunner

from aibar import config as config_module
from aibar.cli import main
from aibar.providers.base import ProviderName, ProviderResult, UsageMetrics, WindowPeriod


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
    monkeypatch.setattr(config_module, "RUNTIME_CONFIG_PATH", config_dir / "config.json")
    monkeypatch.setattr(config_module, "CACHE_FILE_PATH", cache_dir / "cache.json")
    monkeypatch.setattr(config_module, "IDLE_TIME_PATH", cache_dir / "idle-time.json")
    return config_dir


def _make_429_provider_result(
    provider_name: ProviderName,
    retry_after_seconds: int,
) -> ProviderResult:
    """
    @brief Build deterministic HTTP 429 provider result payload.
    @param provider_name {ProviderName} Provider identifier.
    @param retry_after_seconds {int} Retry-after delay to encode.
    @return {ProviderResult} Error result with status/retry metadata.
    """
    return ProviderResult(
        provider=provider_name,
        window=WindowPeriod.DAY_7,
        metrics=UsageMetrics(),
        error="Rate limited. Try again later.",
        raw={
            "status_code": 429,
            "retry_after_seconds": retry_after_seconds,
        },
    )


def test_429_idle_time_uses_idle_delay_when_retry_after_is_lower(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify idle-time uses idle-delay floor when all retry-after values are lower.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-041
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        config_module.RuntimeConfig(idle_delay_seconds=300, api_call_delay_seconds=20)
    )

    openrouter = MagicMock()
    openrouter.name = ProviderName.OPENROUTER
    openrouter.is_configured.return_value = True
    openrouter.fetch = AsyncMock(
        return_value=_make_429_provider_result(ProviderName.OPENROUTER, 120)
    )

    codex = MagicMock()
    codex.name = ProviderName.CODEX
    codex.is_configured.return_value = True
    codex.fetch = AsyncMock(
        return_value=_make_429_provider_result(ProviderName.CODEX, 240)
    )

    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {
            ProviderName.OPENROUTER: openrouter,
            ProviderName.CODEX: codex,
        },
    )
    monkeypatch.setattr("aibar.cli._apply_api_call_delay", lambda state: None)

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--json", "--force"])
    assert result.exit_code == 0

    idle_state = json.loads(config_module.IDLE_TIME_PATH.read_text(encoding="utf-8"))
    delta_seconds = idle_state["idle_until_timestamp"] - idle_state["last_success_timestamp"]
    assert 299 <= delta_seconds <= 301


def test_429_idle_time_uses_largest_retry_after_across_multiple_results(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify idle-time uses the largest retry-after value across all 429 results.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-041
    @satisfies TST-011
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        config_module.RuntimeConfig(idle_delay_seconds=300, api_call_delay_seconds=20)
    )

    openrouter = MagicMock()
    openrouter.name = ProviderName.OPENROUTER
    openrouter.is_configured.return_value = True
    openrouter.fetch = AsyncMock(
        return_value=_make_429_provider_result(ProviderName.OPENROUTER, 120)
    )

    codex = MagicMock()
    codex.name = ProviderName.CODEX
    codex.is_configured.return_value = True
    codex.fetch = AsyncMock(
        return_value=_make_429_provider_result(ProviderName.CODEX, 900)
    )

    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {
            ProviderName.OPENROUTER: openrouter,
            ProviderName.CODEX: codex,
        },
    )
    monkeypatch.setattr("aibar.cli._apply_api_call_delay", lambda state: None)

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--json", "--force"])
    assert result.exit_code == 0

    idle_state = json.loads(config_module.IDLE_TIME_PATH.read_text(encoding="utf-8"))
    delta_seconds = idle_state["idle_until_timestamp"] - idle_state["last_success_timestamp"]
    assert 899 <= delta_seconds <= 901
