"""
@file
@brief Idle-time cache gating tests for CLI show command.
@details Verifies `show` serves cached JSON payload while idle-time is active and
skips live provider refresh execution.
@satisfies REQ-003
@satisfies REQ-009
@satisfies TST-014
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

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


def test_show_uses_cache_payload_when_idle_time_is_active(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify active idle-time forces cache-only `show --json` behavior.
    @details Persists future idle-time and cache payload, then asserts command
    output equals cached JSON while live fetch helpers are never called.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-003
    @satisfies REQ-009
    @satisfies TST-014
    """
    _patch_config_paths(monkeypatch, tmp_path)
    cached_result = ProviderResult(
        provider=ProviderName.OPENROUTER,
        window=WindowPeriod.DAY_7,
        metrics=UsageMetrics(cost=1.75, remaining=72.0, limit=100.0),
        raw={"status_code": 200, "source": "cached"},
    )
    cached_payload = {
        "payload": {"openrouter": cached_result.model_dump(mode="json")},
        "status": {},
    }
    config_module.save_cli_cache(cached_payload)
    config_module.save_idle_time(
        last_success_at=datetime.now(timezone.utc),
        idle_until=datetime.now(timezone.utc) + timedelta(minutes=30),
    )

    def _unexpected_fetch(*args, **kwargs):
        """
        @brief Fail test when live fetch helper is executed under active idle-time.
        @return {None} No return value; always raises AssertionError.
        """
        del args, kwargs
        raise AssertionError("Live fetch must not run while idle-time is active")

    monkeypatch.setattr("aibar.cli.get_providers", lambda: {})
    monkeypatch.setattr("aibar.cli._fetch_result", _unexpected_fetch)
    monkeypatch.setattr("aibar.cli._fetch_claude_dual", _unexpected_fetch)

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--json"])

    assert result.exit_code == 0
    assert json.loads(result.output) == cached_payload
