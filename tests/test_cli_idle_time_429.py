"""
@file
@brief HTTP 429 idle-time update tests for CLI refresh.
@details Verifies provider-scoped idle-time persistence uses
max(idle-delay, retry-after) for provider refresh failures, while successful
providers keep idle-delay scheduling.
@satisfies REQ-041
@satisfies TST-011
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from click.testing import CliRunner

from aibar import config as config_module
from aibar.cli import main
from aibar.providers.base import (
    ProviderName,
    ProviderResult,
    UsageMetrics,
    WindowPeriod,
)


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


def _make_429_provider_result(
    provider_name: ProviderName,
    retry_after_seconds: int | float | str,
) -> ProviderResult:
    """
    @brief Build deterministic HTTP 429 provider result payload.
    @param provider_name {ProviderName} Provider identifier.
    @param retry_after_seconds {int | float | str} Retry-after value to encode.
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


def test_429_idle_time_normalizes_epoch_retry_after_timestamp(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify idle-time normalizes absolute epoch Retry-After timestamps.
    @details Executes one provider HTTP 429 result where `retry_after_seconds`
    carries an absolute future epoch timestamp instead of relative seconds.
    Asserts persisted idle-time delta uses relative delay semantics.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-041
    @satisfies TST-011
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        config_module.RuntimeConfig(
            idle_delay_seconds=300, api_call_delay_milliseconds=20
        )
    )

    retry_after_epoch = int(datetime.now(timezone.utc).timestamp()) + 900

    openrouter = MagicMock()
    openrouter.name = ProviderName.OPENROUTER
    openrouter.is_configured.return_value = True
    openrouter.fetch = AsyncMock(
        return_value=_make_429_provider_result(
            ProviderName.OPENROUTER, retry_after_epoch
        )
    )

    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {ProviderName.OPENROUTER: openrouter},
    )
    monkeypatch.setattr("aibar.cli._apply_api_call_delay", lambda state: None)

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--json", "--force"])
    assert result.exit_code == 0

    idle_state = json.loads(config_module.IDLE_TIME_PATH.read_text(encoding="utf-8"))
    openrouter_state = idle_state[ProviderName.OPENROUTER.value]
    openrouter_delta = (
        openrouter_state["idle_until_timestamp"]
        - openrouter_state["last_success_timestamp"]
    )
    assert 899 <= openrouter_delta <= 901


def _make_success_provider_result(provider_name: ProviderName) -> ProviderResult:
    """
    @brief Build deterministic successful provider result payload.
    @details Encodes a non-error 7-day result with numeric metrics and
    `status_code=200` for idle-time update assertions.
    @param provider_name {ProviderName} Provider identifier.
    @return {ProviderResult} Success result with status metadata.
    """
    return ProviderResult(
        provider=provider_name,
        window=WindowPeriod.DAY_7,
        metrics=UsageMetrics(cost=1.0, remaining=80.0, limit=100.0),
        raw={"status_code": 200},
    )


def _make_auth_failure_provider_result(provider_name: ProviderName) -> ProviderResult:
    """
    @brief Build deterministic authentication failure result fixture.
    @param provider_name {ProviderName} Provider identifier.
    @return {ProviderResult} Authentication failure result.
    """
    return ProviderResult(
        provider=provider_name,
        window=WindowPeriod.DAY_7,
        metrics=UsageMetrics(),
        error="Invalid or expired OAuth token",
        raw={"status_code": 401},
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
        config_module.RuntimeConfig(
            idle_delay_seconds=300, api_call_delay_milliseconds=20
        )
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
    openrouter_state = idle_state[ProviderName.OPENROUTER.value]
    codex_state = idle_state[ProviderName.CODEX.value]
    openrouter_delta = (
        openrouter_state["idle_until_timestamp"]
        - openrouter_state["last_success_timestamp"]
    )
    codex_delta = (
        codex_state["idle_until_timestamp"] - codex_state["last_success_timestamp"]
    )
    assert 299 <= openrouter_delta <= 301
    assert 299 <= codex_delta <= 301


def test_429_only_affects_rate_limited_provider_idle_time(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify rate-limit retry-after applies only to the rate-limited provider.
    @details Executes one OpenRouter HTTP 429 result and one successful Codex result.
    Asserts OpenRouter uses retry-after-expanded idle-time and Codex keeps
    idle-delay scheduling.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-041
    @satisfies TST-011
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        config_module.RuntimeConfig(
            idle_delay_seconds=300, api_call_delay_milliseconds=20
        )
    )

    openrouter = MagicMock()
    openrouter.name = ProviderName.OPENROUTER
    openrouter.is_configured.return_value = True
    openrouter.fetch = AsyncMock(
        return_value=_make_429_provider_result(ProviderName.OPENROUTER, 900)
    )

    codex = MagicMock()
    codex.name = ProviderName.CODEX
    codex.is_configured.return_value = True
    codex.fetch = AsyncMock(
        return_value=_make_success_provider_result(ProviderName.CODEX)
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
    openrouter_state = idle_state[ProviderName.OPENROUTER.value]
    codex_state = idle_state[ProviderName.CODEX.value]
    openrouter_delta = (
        openrouter_state["idle_until_timestamp"]
        - openrouter_state["last_success_timestamp"]
    )
    codex_delta = (
        codex_state["idle_until_timestamp"] - codex_state["last_success_timestamp"]
    )
    assert 899 <= openrouter_delta <= 901
    assert 299 <= codex_delta <= 301


def test_auth_failure_updates_idle_time_with_idle_delay_floor(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify authentication failures still update provider idle-time metadata.
    @details Executes one provider refresh failure without retry-after metadata and
    asserts idle-time uses configured idle-delay floor (`retry_after=0` path).
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-041
    @satisfies TST-011
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        config_module.RuntimeConfig(
            idle_delay_seconds=300, api_call_delay_milliseconds=20
        )
    )

    codex = MagicMock()
    codex.name = ProviderName.CODEX
    codex.is_configured.return_value = True
    codex.fetch = AsyncMock(
        return_value=_make_auth_failure_provider_result(ProviderName.CODEX)
    )

    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {ProviderName.CODEX: codex},
    )
    monkeypatch.setattr("aibar.cli._apply_api_call_delay", lambda state: None)

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--json", "--force"])
    assert result.exit_code == 0

    idle_state = json.loads(config_module.IDLE_TIME_PATH.read_text(encoding="utf-8"))
    codex_state = idle_state[ProviderName.CODEX.value]
    codex_delta = (
        codex_state["idle_until_timestamp"] - codex_state["last_success_timestamp"]
    )
    assert 299 <= codex_delta <= 301
