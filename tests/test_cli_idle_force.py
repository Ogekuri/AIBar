"""
@file
@brief Forced refresh tests for CLI idle-time behavior.
@details Verifies `show --force` bypasses idle gating, refreshes provider data,
rewrites cache payload, and regenerates idle-time state.
@satisfies REQ-039
@satisfies TST-015
"""

import json
from datetime import datetime, timedelta, timezone
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


def test_show_force_bypasses_idle_time_and_recreates_state(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify `show --force` ignores existing idle-time and performs refresh.
    @details Starts from active idle-time and stale cache, then asserts forced run
    fetches provider data, rewrites cache, and regenerates idle-time metadata.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-039
    @satisfies TST-015
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        config_module.RuntimeConfig(idle_delay_seconds=300, api_call_delay_milliseconds=20)
    )
    stale_state = config_module.build_idle_time_state(
        last_success_at=datetime.now(timezone.utc) - timedelta(hours=1),
        idle_until=datetime.now(timezone.utc) + timedelta(hours=2),
    )
    config_module.save_idle_time(
        {
            ProviderName.OPENROUTER.value: stale_state,
        }
    )
    config_module.save_cli_cache(
        {
            "payload": {"openrouter": {"stale": True}},
            "status": {},
        }
    )

    fresh_result = ProviderResult(
        provider=ProviderName.OPENROUTER,
        window=WindowPeriod.DAY_7,
        metrics=UsageMetrics(cost=2.5, remaining=44.0, limit=100.0),
        raw={"status_code": 200, "source": "live"},
    )
    provider = MagicMock()
    provider.name = ProviderName.OPENROUTER
    provider.is_configured.return_value = True
    provider.fetch = AsyncMock(return_value=fresh_result)

    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {ProviderName.OPENROUTER: provider},
    )
    monkeypatch.setattr("aibar.cli._apply_api_call_delay", lambda state: None)

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "show",
            "--provider",
            "openrouter",
            "--window",
            "7d",
            "--json",
            "--force",
        ],
    )

    assert result.exit_code == 0
    provider.fetch.assert_awaited_once_with(WindowPeriod.DAY_7)
    output_payload = json.loads(result.output)
    persisted_cache = json.loads(config_module.CACHE_FILE_PATH.read_text(encoding="utf-8"))
    output_without_extension = {
        k: v for k, v in output_payload.items() if k not in {"extension", "idle_time"}
    }
    assert output_without_extension == persisted_cache
    assert "extension" in output_payload
    assert "idle_time" in output_payload
    assert output_payload["payload"]["openrouter"]["raw"]["source"] == "live"

    refreshed_state = json.loads(config_module.IDLE_TIME_PATH.read_text(encoding="utf-8"))
    openrouter_state = refreshed_state[ProviderName.OPENROUTER.value]
    assert openrouter_state["last_success_timestamp"] >= stale_state.last_success_timestamp
    assert openrouter_state["idle_until_timestamp"] > openrouter_state["last_success_timestamp"]
    assert (
        openrouter_state["last_success_human"]
        == datetime.fromtimestamp(
            openrouter_state["last_success_timestamp"]
        ).astimezone().isoformat()
    )
    assert (
        openrouter_state["idle_until_human"]
        == datetime.fromtimestamp(
            openrouter_state["idle_until_timestamp"]
        ).astimezone().isoformat()
    )


def test_show_geminiai_forces_30d_even_when_window_is_explicitly_7d(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify `show --provider geminiai` forces effective window `30d`.
    @details Invokes `show` with explicit `--window 7d` and asserts GeminiAI fetch
    still executes with `WindowPeriod.DAY_30`.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-097
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        config_module.RuntimeConfig(idle_delay_seconds=300, api_call_delay_milliseconds=20)
    )

    geminiai_result = ProviderResult(
        provider=ProviderName.GEMINIAI,
        window=WindowPeriod.DAY_30,
        metrics=UsageMetrics(cost=0.207369, requests=19, input_tokens=19, currency_symbol="€"),
        raw={"status_code": 200, "billing": {"services": []}},
    )
    provider = MagicMock()
    provider.name = ProviderName.GEMINIAI
    provider.is_configured.return_value = True
    provider.fetch = AsyncMock(return_value=geminiai_result)

    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {ProviderName.GEMINIAI: provider},
    )
    monkeypatch.setattr("aibar.cli._apply_api_call_delay", lambda state: None)

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "show",
            "--provider",
            "geminiai",
            "--window",
            "7d",
            "--json",
            "--force",
        ],
    )

    assert result.exit_code == 0
    provider.fetch.assert_awaited_once_with(WindowPeriod.DAY_30)
    output_payload = json.loads(result.output)
    assert output_payload["payload"]["geminiai"]["window"] == "30d"
