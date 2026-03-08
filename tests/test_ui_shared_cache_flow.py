"""
@file
@brief Shared cache-retrieval tests for Text UI refresh flow.
@details Verifies Text UI refresh uses the same cache pipeline as CLI `show`:
idle-time gate reads from `cache.json`, missing/expired idle-time triggers live
refresh and cache persistence, and UI code no longer calls legacy ResultCache APIs.
@satisfies REQ-009
@satisfies REQ-039
@satisfies REQ-042
@satisfies REQ-043
@satisfies TST-014
@satisfies TST-015
@satisfies TST-017
"""

import asyncio
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from aibar import config as config_module
from aibar.providers.base import ProviderName, ProviderResult, UsageMetrics, WindowPeriod
from aibar.ui import AIBarUI


def _patch_config_paths(monkeypatch, tmp_path: Path) -> None:
    """
    @brief Redirect AIBar config/cache paths to temporary test directories.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    """
    config_dir = tmp_path / ".config" / "aibar"
    cache_dir = tmp_path / ".cache" / "aibar"
    monkeypatch.setattr(config_module, "APP_CONFIG_DIR", config_dir)
    monkeypatch.setattr(config_module, "APP_CACHE_DIR", cache_dir)
    monkeypatch.setattr(config_module, "ENV_FILE_PATH", config_dir / "env")
    monkeypatch.setattr(config_module, "RUNTIME_CONFIG_PATH", config_dir / "config.json")
    monkeypatch.setattr(config_module, "CACHE_FILE_PATH", cache_dir / "cache.json")
    monkeypatch.setattr(config_module, "IDLE_TIME_PATH", cache_dir / "idle-time.json")


def _make_result(source: str) -> ProviderResult:
    """
    @brief Build deterministic OpenRouter ProviderResult payload for UI tests.
    @param source {str} Marker inserted into raw payload.
    @return {ProviderResult} OpenRouter result with stable metrics.
    """
    return ProviderResult(
        provider=ProviderName.OPENROUTER,
        window=WindowPeriod.DAY_7,
        metrics=UsageMetrics(cost=1.25, remaining=71.0, limit=100.0),
        raw={"status_code": 200, "source": source},
    )


def test_ui_refresh_uses_cache_payload_when_idle_time_is_active(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify active idle-time forces Text UI refresh to use `cache.json`.
    @details Persists future idle-time state and cached payload, then asserts
    Text UI refresh does not trigger provider network fetch.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-009
    @satisfies TST-014
    """
    _patch_config_paths(monkeypatch, tmp_path)
    cached_result = _make_result(source="cached")
    config_module.save_cli_cache(
        {
            "payload": {"openrouter": cached_result.model_dump(mode="json")},
            "status": {},
        }
    )
    config_module.save_idle_time(
        last_success_at=datetime.now(timezone.utc),
        idle_until=datetime.now(timezone.utc) + timedelta(minutes=20),
    )

    provider = MagicMock()
    provider.is_configured.return_value = True
    provider.fetch = AsyncMock(side_effect=AssertionError("Fetch must not run while idle"))

    ui = AIBarUI()
    ui.window = WindowPeriod.DAY_7
    ui.providers = {ProviderName.OPENROUTER: provider}
    ui._get_card = MagicMock(return_value=None)
    ui._update_json_view = MagicMock()

    asyncio.run(ui.action_refresh())

    provider.fetch.assert_not_called()
    assert ui.results[ProviderName.OPENROUTER].raw["source"] == "cached"


def test_ui_refresh_fetches_and_persists_cache_when_idle_state_missing(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify Text UI refresh performs live fetch when idle-time file is missing.
    @details Asserts provider fetch executes once, refreshed payload is persisted
    into `cache.json`, and UI state is updated from cache-backed retrieval output.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-009
    @satisfies REQ-042
    @satisfies TST-014
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        config_module.RuntimeConfig(idle_delay_seconds=300, api_call_delay_seconds=20)
    )

    live_result = _make_result(source="live")
    provider = MagicMock()
    provider.is_configured.return_value = True
    provider.fetch = AsyncMock(return_value=live_result)

    ui = AIBarUI()
    ui.window = WindowPeriod.DAY_7
    ui.providers = {ProviderName.OPENROUTER: provider}
    ui._get_card = MagicMock(return_value=None)
    ui._update_json_view = MagicMock()

    asyncio.run(ui.action_refresh())

    provider.fetch.assert_awaited_once_with(WindowPeriod.DAY_7)
    persisted = json.loads(config_module.CACHE_FILE_PATH.read_text(encoding="utf-8"))
    assert persisted["payload"]["openrouter"]["raw"]["source"] == "live"
    assert ui.results[ProviderName.OPENROUTER].raw["source"] == "live"


def test_ui_and_show_share_cache_pipeline_without_result_cache_usage() -> None:
    """
    @brief Verify UI and CLI reference one shared retrieval function.
    @details Performs deterministic source-structure assertions proving Text UI
    and CLI `show` call `retrieve_results_via_cache_pipeline`, and Text UI source
    no longer imports or calls legacy ResultCache APIs.
    @return {None} Function return value.
    @satisfies REQ-043
    @satisfies TST-017
    """
    ui_source = Path("src/aibar/aibar/ui.py").read_text(encoding="utf-8")
    cli_source = Path("src/aibar/aibar/cli.py").read_text(encoding="utf-8")

    assert "retrieve_results_via_cache_pipeline" in ui_source
    assert "retrieve_results_via_cache_pipeline" in cli_source
    assert "from aibar.cache import ResultCache" not in ui_source
    assert ".cache.get(" not in ui_source
    assert ".cache.set(" not in ui_source
