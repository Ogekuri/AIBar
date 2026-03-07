"""
@file
@brief CLI cache persistence redaction tests.
@details Verifies `save_cli_cache` redacts sensitive raw keys before writing
`cache.json` and `load_cli_cache` returns the sanitized persisted payload.
@satisfies CTN-004
@satisfies DES-004
@satisfies TST-003
"""

import json
from pathlib import Path

from aibar import config as config_module


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


def test_save_cli_cache_redacts_sensitive_payload_keys(monkeypatch, tmp_path: Path) -> None:
    """
    @brief Verify `save_cli_cache` redacts sensitive key paths recursively.
    @details Writes cache payload with nested sensitive keys, then asserts disk
    payload replaces those values with `[REDACTED]` while preserving safe keys.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies DES-004
    @satisfies TST-003
    """
    _patch_config_paths(monkeypatch, tmp_path)
    payload = {
        "openai": {
            "raw": {
                "token": "secret-token",
                "nested": {
                    "authorization": "Bearer abc",
                    "key": "inner-key",
                    "keep": "value",
                },
            }
        }
    }

    config_module.save_cli_cache(payload)

    persisted = json.loads(config_module.CACHE_FILE_PATH.read_text(encoding="utf-8"))
    assert persisted["openai"]["raw"]["token"] == "[REDACTED]"
    assert persisted["openai"]["raw"]["nested"]["authorization"] == "[REDACTED]"
    assert persisted["openai"]["raw"]["nested"]["key"] == "[REDACTED]"
    assert persisted["openai"]["raw"]["nested"]["keep"] == "value"


def test_load_cli_cache_returns_sanitized_persisted_payload(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify `load_cli_cache` returns redacted values persisted by save helper.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies CTN-004
    @satisfies DES-004
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.save_cli_cache(
        {
            "openrouter": {
                "raw": {
                    "password": "private",
                    "usage": 1.5,
                }
            }
        }
    )

    loaded = config_module.load_cli_cache()

    assert loaded is not None
    assert loaded["openrouter"]["raw"]["password"] == "[REDACTED]"
    assert loaded["openrouter"]["raw"]["usage"] == 1.5
