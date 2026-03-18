"""
@file test_show_json_extension_section.py
@brief Tests for the `extension` section emitted by `show --json`.
@details Verifies that `aibar show --json` includes top-level `idle_time`,
`freshness`, and `extension` objects, with
`extension.gnome_refresh_interval_seconds` and `extension.idle_delay_seconds`
sourced from runtime config.
@satisfies REQ-003
@satisfies CTN-008
@satisfies TST-004
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from click.testing import CliRunner

from aibar import config as config_module
from aibar.cli import main
from aibar.config import RuntimeConfig


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


def test_show_json_emits_extension_section_with_default_gnome_refresh_interval(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify `show --json` emits default extension refresh and idle-delay values.
    @details Persists an empty cache, ensures no idle-time gate is active, then asserts
    the JSON output contains an `extension` section with the default refresh interval.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-003
    @satisfies CTN-008
    """
    _patch_config_paths(monkeypatch, tmp_path)
    empty_cache = {"payload": {}, "status": {}}
    config_module.save_cli_cache(empty_cache)
    config_module.save_runtime_config(RuntimeConfig())

    monkeypatch.setattr("aibar.cli.get_providers", lambda: {})
    monkeypatch.setattr(
        "aibar.cli.retrieve_results_via_cache_pipeline",
        lambda **kwargs: type(
            "R",
            (),
            {
                "idle_active": False,
                "cache_available": True,
                "payload": empty_cache,
                "results": {},
                "idle_time_by_provider": {},
            },
        )(),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--json"])

    assert result.exit_code == 0, result.output
    doc = json.loads(result.output)
    assert "extension" in doc
    assert "idle_time" in doc
    assert "freshness" in doc
    assert doc["idle_time"] == {}
    assert doc["freshness"] == {}
    assert "gnome_refresh_interval_seconds" in doc["extension"]
    assert "idle_delay_seconds" in doc["extension"]
    assert doc["extension"]["gnome_refresh_interval_seconds"] == 60
    assert doc["extension"]["idle_delay_seconds"] == 300


def test_show_json_emits_extension_section_with_configured_gnome_refresh_interval(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify `show --json` emits extension refresh and idle-delay values from config.
    @details Persists runtime config with custom refresh and idle-delay values, then asserts
    the JSON output reflects that configured value in the `extension` section.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-003
    @satisfies CTN-008
    """
    _patch_config_paths(monkeypatch, tmp_path)
    empty_cache = {"payload": {}, "status": {}}
    config_module.save_cli_cache(empty_cache)
    config_module.save_runtime_config(
        RuntimeConfig(gnome_refresh_interval_seconds=120, idle_delay_seconds=420)
    )

    monkeypatch.setattr("aibar.cli.get_providers", lambda: {})
    monkeypatch.setattr(
        "aibar.cli.retrieve_results_via_cache_pipeline",
        lambda **kwargs: type(
            "R",
            (),
            {
                "idle_active": False,
                "cache_available": True,
                "payload": empty_cache,
                "results": {},
                "idle_time_by_provider": {},
            },
        )(),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--json"])

    assert result.exit_code == 0, result.output
    doc = json.loads(result.output)
    assert "extension" in doc
    assert "idle_time" in doc
    assert "freshness" in doc
    assert doc["idle_time"] == {}
    assert doc["freshness"] == {}
    assert doc["extension"]["gnome_refresh_interval_seconds"] == 120
    assert doc["extension"]["idle_delay_seconds"] == 420


def test_show_json_extension_section_does_not_appear_in_cache_payload(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify `extension` section is injected at emit time, not stored in cache.
    @details Persists a cache document without an `extension` key, invokes `show --json`,
    and asserts the output's `extension` section appears only in the response, not in
    the cached file on disk.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-003
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    cache_dir = config_dir.parent.parent / ".cache" / "aibar"
    empty_cache = {"payload": {}, "status": {}}
    config_module.save_cli_cache(empty_cache)
    config_module.save_runtime_config(RuntimeConfig())

    monkeypatch.setattr("aibar.cli.get_providers", lambda: {})
    monkeypatch.setattr(
        "aibar.cli.retrieve_results_via_cache_pipeline",
        lambda **kwargs: type(
            "R",
            (),
            {
                "idle_active": False,
                "cache_available": True,
                "payload": empty_cache,
                "results": {},
                "idle_time_by_provider": {},
            },
        )(),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--json"])
    assert result.exit_code == 0, result.output
    doc = json.loads(result.output)
    assert "extension" in doc
    assert "idle_time" in doc
    assert "freshness" in doc
    assert doc["extension"]["idle_delay_seconds"] == 300

    cache_file = cache_dir / "cache.json"
    if cache_file.exists():
        cached = json.loads(cache_file.read_text(encoding="utf-8"))
        assert "extension" not in cached
        assert "freshness" not in cached


def test_show_json_emits_provider_freshness_from_idle_time_timestamps(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify `show --json` emits provider `freshness` from idle-time timestamps.
    @details Injects one provider idle-time state and asserts the `freshness` section
    exports matching epoch values and local-time `%Y-%m-%d %H:%M` strings.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-003
    @satisfies REQ-084
    @satisfies TST-038
    """
    _patch_config_paths(monkeypatch, tmp_path)
    empty_cache = {"payload": {}, "status": {}}
    config_module.save_cli_cache(empty_cache)
    config_module.save_runtime_config(RuntimeConfig())
    last_success = datetime(2026, 3, 18, 8, 58, tzinfo=timezone.utc)
    idle_until = datetime(2026, 3, 18, 8, 59, tzinfo=timezone.utc)
    idle_state = config_module.build_idle_time_state(
        last_success_at=last_success,
        idle_until=idle_until,
    )

    monkeypatch.setattr("aibar.cli.get_providers", lambda: {})
    monkeypatch.setattr(
        "aibar.cli.retrieve_results_via_cache_pipeline",
        lambda **kwargs: type(
            "R",
            (),
            {
                "idle_active": False,
                "cache_available": True,
                "payload": empty_cache,
                "results": {},
                "idle_time_by_provider": {"openai": idle_state},
            },
        )(),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--json"])

    assert result.exit_code == 0, result.output
    doc = json.loads(result.output)
    assert doc["freshness"]["openai"]["last_success_timestamp"] == idle_state.last_success_timestamp
    assert doc["freshness"]["openai"]["idle_until_timestamp"] == idle_state.idle_until_timestamp
    assert doc["freshness"]["openai"]["last_success_local"] == last_success.astimezone().strftime("%Y-%m-%d %H:%M")
    assert doc["freshness"]["openai"]["idle_until_local"] == idle_until.astimezone().strftime("%Y-%m-%d %H:%M")
