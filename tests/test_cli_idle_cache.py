"""
@file
@brief Idle-time cache gating tests for CLI show command.
@details Verifies `show` serves cached JSON payload while idle-time is active,
skips live provider refresh execution, and omits providers disabled by runtime
configuration.
@satisfies REQ-003
@satisfies REQ-009
@satisfies REQ-124
@satisfies REQ-126
@satisfies TST-014
@satisfies TST-056
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


def test_show_uses_cache_for_idle_provider_and_refreshes_non_idle_provider(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify provider-scoped idle-time gates only matching providers.
    @details Persists future idle-time only for OpenRouter, then runs `show --json`
    with OpenRouter and OpenAI configured. Asserts OpenRouter uses cached payload
    while OpenAI executes live refresh and updates cache output.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-003
    @satisfies REQ-009
    @satisfies TST-014
    """
    _patch_config_paths(monkeypatch, tmp_path)
    cached_openrouter = ProviderResult(
        provider=ProviderName.OPENROUTER,
        window=WindowPeriod.DAY_30,
        metrics=UsageMetrics(cost=1.75, remaining=72.0, limit=100.0),
        raw={"status_code": 200, "source": "cached-openrouter"},
    )
    cached_openai = ProviderResult(
        provider=ProviderName.OPENAI,
        window=WindowPeriod.DAY_30,
        metrics=UsageMetrics(cost=0.25, remaining=95.0, limit=100.0),
        raw={"status_code": 200, "source": "cached-openai"},
    )
    cached_payload = {
        "payload": {
            "openrouter": cached_openrouter.model_dump(mode="json"),
            "openai": cached_openai.model_dump(mode="json"),
        },
        "status": {},
    }
    config_module.save_cli_cache(cached_payload)
    now_utc = datetime.now(timezone.utc)
    config_module.save_idle_time(
        {
            ProviderName.OPENROUTER.value: config_module.build_idle_time_state(
                last_success_at=now_utc,
                idle_until=now_utc + timedelta(minutes=30),
            )
        }
    )

    openrouter_provider = MagicMock()
    openrouter_provider.is_configured.return_value = True
    openrouter_provider.fetch = AsyncMock(return_value=cached_openrouter)

    openai_live = ProviderResult(
        provider=ProviderName.OPENAI,
        window=WindowPeriod.DAY_30,
        metrics=UsageMetrics(cost=2.10, remaining=70.0, limit=100.0),
        raw={"status_code": 200, "source": "live-openai"},
    )
    openai_provider = MagicMock()
    openai_provider.is_configured.return_value = True
    openai_provider.fetch = AsyncMock(return_value=openai_live)

    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {
            ProviderName.OPENROUTER: openrouter_provider,
            ProviderName.OPENAI: openai_provider,
        },
    )
    monkeypatch.setattr("aibar.cli._apply_api_call_delay", lambda state: None)

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--json"])

    assert result.exit_code == 0
    openrouter_provider.fetch.assert_not_awaited()
    openai_provider.fetch.assert_awaited_once_with(WindowPeriod.DAY_30)

    output = json.loads(result.output)
    assert output["payload"]["openrouter"]["raw"]["source"] == "cached-openrouter"
    assert output["payload"]["openai"]["raw"]["source"] == "live-openai"
    assert output["extension"]["gnome_refresh_interval_seconds"] == 60

    persisted_idle_state = json.loads(config_module.IDLE_TIME_PATH.read_text(encoding="utf-8"))
    assert ProviderName.OPENROUTER.value in persisted_idle_state
    assert ProviderName.OPENAI.value in persisted_idle_state


def test_show_omits_disabled_provider_from_refresh_and_output(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify disabled providers are omitted from refresh, text, and JSON output.
    @details Persists cached payload for enabled OpenRouter and disabled OpenAI.
    Runtime config marks OpenAI disabled, then `show --json` and `show` are
    executed. OpenAI refresh MUST remain skipped, OpenAI sections MUST be absent
    from output payloads, and `enabled_providers.openai` MUST be `False`.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-124
    @satisfies REQ-125
    @satisfies REQ-126
    @satisfies TST-056
    """
    _patch_config_paths(monkeypatch, tmp_path)
    cached_openrouter = ProviderResult(
        provider=ProviderName.OPENROUTER,
        window=WindowPeriod.DAY_30,
        metrics=UsageMetrics(cost=1.75, remaining=72.0, limit=100.0),
        raw={"status_code": 200, "source": "cached-openrouter"},
    )
    cached_openai = ProviderResult(
        provider=ProviderName.OPENAI,
        window=WindowPeriod.DAY_30,
        metrics=UsageMetrics(cost=0.25, remaining=95.0, limit=100.0),
        raw={"status_code": 200, "source": "cached-openai"},
    )
    config_module.save_cli_cache(
        {
            "payload": {
                "openrouter": cached_openrouter.model_dump(mode="json"),
                "openai": cached_openai.model_dump(mode="json"),
            },
            "status": {},
        }
    )
    config_module.save_runtime_config(
        config_module.RuntimeConfig(
            enabled_providers={
                "claude": True,
                "openrouter": True,
                "copilot": True,
                "codex": True,
                "openai": False,
                "geminiai": True,
            }
        )
    )
    now_utc = datetime.now(timezone.utc)
    config_module.save_idle_time(
        {
            ProviderName.OPENROUTER.value: config_module.build_idle_time_state(
                last_success_at=now_utc,
                idle_until=now_utc + timedelta(minutes=30),
            )
        }
    )

    openrouter_provider = MagicMock()
    openrouter_provider.is_configured.return_value = True
    openrouter_provider.fetch = AsyncMock(return_value=cached_openrouter)

    openai_provider = MagicMock()
    openai_provider.is_configured.return_value = True
    openai_provider.fetch = AsyncMock(return_value=cached_openai)

    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {
            ProviderName.OPENROUTER: openrouter_provider,
            ProviderName.OPENAI: openai_provider,
        },
    )
    monkeypatch.setattr("aibar.cli._apply_api_call_delay", lambda state: None)

    runner = CliRunner()
    json_result = runner.invoke(main, ["show", "--json"])
    assert json_result.exit_code == 0, json_result.output
    openrouter_provider.fetch.assert_not_awaited()
    openai_provider.fetch.assert_not_awaited()

    output_doc = json.loads(json_result.output)
    assert "openrouter" in output_doc["payload"]
    assert "openai" not in output_doc["payload"]
    assert output_doc["enabled_providers"]["openai"] is False
    assert output_doc["extension"]["window_labels"] == {
        "copilot": "30d",
        "openrouter": "30d",
        "geminiai": "30d",
    }

    text_result = runner.invoke(main, ["show"])
    assert text_result.exit_code == 0, text_result.output
    assert "OPENAI" not in text_result.output
    assert "OPENROUTER" in text_result.output

    persisted_idle_state = json.loads(
        config_module.IDLE_TIME_PATH.read_text(encoding="utf-8")
    )
    assert ProviderName.OPENROUTER.value in persisted_idle_state
    assert ProviderName.OPENAI.value not in persisted_idle_state
