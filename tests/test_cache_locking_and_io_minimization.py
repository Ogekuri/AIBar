"""
@file
@brief Cache lock-file and cache I/O minimization tests.
@details Verifies blocking lock behavior for `cache.json`/`idle-time.json` with
250ms polling, and verifies retrieval flow avoids redundant cache reads/writes
within one refresh execution.
@satisfies REQ-042
@satisfies REQ-066
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from aibar import cli as cli_module
from aibar import config as config_module
from aibar.config import RuntimeConfig
from aibar.providers.base import WindowPeriod


def _patch_config_paths(monkeypatch, tmp_path: Path) -> None:
    """
    @brief Redirect AIBar config/cache paths to temporary directories.
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


def test_save_cli_cache_waits_for_lock_release_with_250ms_poll(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify `save_cli_cache` blocks on existing lock and polls at 250ms.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-066
    """
    _patch_config_paths(monkeypatch, tmp_path)
    lock_path = config_module.APP_CACHE_DIR / "cache.json.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text("locked", encoding="utf-8")

    sleep_calls: list[float] = []

    def _fake_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)
        lock_path.unlink(missing_ok=True)

    monkeypatch.setattr(config_module.time, "sleep", _fake_sleep)
    config_module.save_cli_cache({"payload": {}, "status": {}})

    assert sleep_calls == [0.25]
    assert config_module.CACHE_FILE_PATH.exists()


def test_load_idle_time_waits_for_lock_release_with_250ms_poll(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify `load_idle_time` blocks on existing lock and polls at 250ms.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-066
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.IDLE_TIME_PATH.parent.mkdir(parents=True, exist_ok=True)
    config_module.IDLE_TIME_PATH.write_text(
        json.dumps(
            {
                "openrouter": {
                    "last_success_timestamp": 1,
                    "last_success_human": datetime.now(timezone.utc).isoformat(),
                    "idle_until_timestamp": 2,
                    "idle_until_human": datetime.now(timezone.utc).isoformat(),
                }
            }
        ),
        encoding="utf-8",
    )
    lock_path = config_module.APP_CACHE_DIR / "idle-time.json.lock"
    lock_path.write_text("locked", encoding="utf-8")

    sleep_calls: list[float] = []

    def _fake_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)
        lock_path.unlink(missing_ok=True)

    monkeypatch.setattr(config_module.time, "sleep", _fake_sleep)
    state = config_module.load_idle_time()

    assert sleep_calls == [0.25]
    assert "openrouter" in state
    assert state["openrouter"].idle_until_timestamp == 2


def test_retrieve_pipeline_avoids_redundant_cache_reload_after_refresh(monkeypatch) -> None:
    """
    @brief Verify retrieval pipeline loads cache only once per non-idle refresh run.
    @details Asserts no post-refresh `load_cli_cache` reload occurs when refresh
    helper already returns the effective in-memory payload.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    @satisfies REQ-042
    """
    load_calls = {"count": 0}

    def _single_cache_load():
        load_calls["count"] += 1
        if load_calls["count"] > 1:
            raise AssertionError("retrieve_results_via_cache_pipeline must not reload cache")
        return None

    monkeypatch.setattr(cli_module, "load_cli_cache", _single_cache_load)
    monkeypatch.setattr(cli_module, "load_idle_time", lambda: {})
    monkeypatch.setattr(cli_module, "load_runtime_config", lambda: RuntimeConfig())
    monkeypatch.setattr(
        cli_module,
        "_refresh_and_persist_cache_payload",
        lambda providers, target_window, runtime_config, cache_document: {"payload": {}, "status": {}},
    )

    output = cli_module.retrieve_results_via_cache_pipeline(
        provider_filter=None,
        target_window=WindowPeriod.DAY_7,
        force_refresh=False,
        providers={},
    )
    assert load_calls["count"] == 1
    assert not output.cache_available


def test_refresh_skips_cache_write_when_document_is_unchanged(monkeypatch) -> None:
    """
    @brief Verify refresh helper skips `save_cli_cache` when cache document is unchanged.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    @satisfies REQ-042
    """
    write_calls: list[dict[str, object]] = []
    monkeypatch.setattr(
        cli_module,
        "save_cli_cache",
        lambda payload: write_calls.append(payload),
    )
    monkeypatch.setattr(
        cli_module,
        "_update_idle_time_after_refresh",
        lambda results, runtime_config: None,
    )

    cli_module._refresh_and_persist_cache_payload(
        providers={},
        target_window=WindowPeriod.DAY_7,
        runtime_config=RuntimeConfig(),
        cache_document={"payload": {}, "status": {}},
    )
    assert write_calls == []
