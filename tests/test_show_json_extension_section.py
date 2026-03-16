"""
@file test_show_json_extension_section.py
@brief Tests for the `extension` section emitted by `show --json`.
@details Verifies that `aibar show --json` includes a top-level `extension` object
containing `gnome_refresh_interval_seconds` sourced from the runtime config.
@satisfies REQ-003
@satisfies CTN-008
@satisfies TST-004
"""

import json
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
    @brief Verify `show --json` emits `extension.gnome_refresh_interval_seconds` with default 60.
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
            },
        )(),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--json"])

    assert result.exit_code == 0, result.output
    doc = json.loads(result.output)
    assert "extension" in doc
    assert "gnome_refresh_interval_seconds" in doc["extension"]
    assert doc["extension"]["gnome_refresh_interval_seconds"] == 60


def test_show_json_emits_extension_section_with_configured_gnome_refresh_interval(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify `show --json` emits `extension.gnome_refresh_interval_seconds` from saved config.
    @details Persists runtime config with custom `gnome_refresh_interval_seconds=120`, then asserts
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
        RuntimeConfig(gnome_refresh_interval_seconds=120)
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
            },
        )(),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--json"])

    assert result.exit_code == 0, result.output
    doc = json.loads(result.output)
    assert "extension" in doc
    assert doc["extension"]["gnome_refresh_interval_seconds"] == 120


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
            },
        )(),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--json"])
    assert result.exit_code == 0, result.output
    doc = json.loads(result.output)
    assert "extension" in doc

    cache_file = cache_dir / "cache.json"
    if cache_file.exists():
        cached = json.loads(cache_file.read_text(encoding="utf-8"))
        assert "extension" not in cached
