"""
@file
@brief Cache status-retention tests for per-provider/window refresh outcomes.
@details Verifies failed refresh attempts preserve last-success payload snapshots,
persist granular `OK`/`FAIL` window statuses with error metadata, and avoid legacy
per-provider snapshot file read/write paths.
@satisfies REQ-044
@satisfies REQ-045
@satisfies REQ-046
@satisfies REQ-047
@satisfies TST-018
@satisfies TST-019
@satisfies TST-020
"""

import json
from datetime import datetime, timedelta, timezone
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
    monkeypatch.setattr(
        config_module, "RUNTIME_CONFIG_PATH", config_dir / "config.json"
    )
    monkeypatch.setattr(config_module, "CACHE_FILE_PATH", cache_dir / "cache.json")
    monkeypatch.setattr(config_module, "IDLE_TIME_PATH", cache_dir / "idle-time.json")


def _make_openrouter_success(source: str) -> ProviderResult:
    """
    @brief Build deterministic successful OpenRouter ProviderResult fixture.
    @param source {str} Marker stored in raw payload.
    @return {ProviderResult} Successful OpenRouter result.
    """
    return ProviderResult(
        provider=ProviderName.OPENROUTER,
        window=WindowPeriod.DAY_30,
        metrics=UsageMetrics(cost=2.0, remaining=80.0, limit=100.0),
        raw={"status_code": 200, "source": source},
    )


def _make_openrouter_429() -> ProviderResult:
    """
    @brief Build deterministic OpenRouter HTTP 429 result fixture.
    @return {ProviderResult} Failed OpenRouter result.
    """
    return ProviderResult(
        provider=ProviderName.OPENROUTER,
        window=WindowPeriod.DAY_30,
        metrics=UsageMetrics(),
        error="Rate limited. Try again later.",
        raw={"status_code": 429, "retry_after_seconds": 120},
    )


def _make_geminiai_success(source: str) -> ProviderResult:
    """
    @brief Build deterministic successful GeminiAI ProviderResult fixture.
    @details Creates 30-day payload with stable monitoring/billing fields and
    caller-provided raw-source marker for cache-retention assertions.
    @param source {str} Marker stored in raw payload.
    @return {ProviderResult} Successful GeminiAI result.
    """
    return ProviderResult(
        provider=ProviderName.GEMINIAI,
        window=WindowPeriod.DAY_30,
        metrics=UsageMetrics(
            cost=3.0, requests=90, input_tokens=600, currency_symbol="€"
        ),
        raw={"status_code": 200, "source": source, "project_id": "demo-project"},
    )


def _make_geminiai_429(retry_after_seconds: int) -> ProviderResult:
    """
    @brief Build deterministic GeminiAI HTTP 429 result fixture.
    @details Produces normalized rate-limit error payload with retry-after
    metadata used by provider-scoped idle-time policy assertions.
    @param retry_after_seconds {int} Retry-after value to persist in raw payload.
    @return {ProviderResult} Failed GeminiAI result.
    """
    return ProviderResult(
        provider=ProviderName.GEMINIAI,
        window=WindowPeriod.DAY_30,
        metrics=UsageMetrics(),
        error="Rate limited. Try again later.",
        raw={"status_code": 429, "retry_after_seconds": retry_after_seconds},
    )


def test_failed_refresh_preserves_previous_payload_and_records_fail_status(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify failed refresh preserves payload while recording `FAIL` status metadata.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-018
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        config_module.RuntimeConfig(
            idle_delay_seconds=300, api_call_delay_milliseconds=20
        )
    )
    cached_success = _make_openrouter_success(source="cached-success")
    config_module.save_cli_cache(
        {
            "payload": {"openrouter": cached_success.model_dump(mode="json")},
            "status": {},
        }
    )

    provider = MagicMock()
    provider.is_configured.return_value = True
    provider.fetch = AsyncMock(return_value=_make_openrouter_429())
    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {ProviderName.OPENROUTER: provider},
    )
    monkeypatch.setattr("aibar.cli._apply_api_call_delay", lambda state: None)

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["show", "--provider", "openrouter", "--window", "7d", "--json", "--force"],
    )
    assert result.exit_code == 0

    output = json.loads(result.output)
    assert output["payload"]["openrouter"]["raw"]["source"] == "cached-success"
    assert output["status"]["openrouter"]["30d"]["result"] == "FAIL"
    assert (
        output["status"]["openrouter"]["30d"]["error"]
        == "Rate limited. Try again later."
    )
    assert isinstance(output["status"]["openrouter"]["30d"]["updated_at"], str)


def test_partial_multi_provider_refresh_records_mixed_statuses(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify partial refresh records mixed per-provider statuses with payload retention.
    @details Simulates `openrouter=FAIL` and `geminiai=OK` in one refresh run and
    verifies both statuses are persisted while the failing provider keeps its
    successful (non-error) cached snapshot and the healthy provider updates.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-019
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        config_module.RuntimeConfig(
            idle_delay_seconds=300, api_call_delay_milliseconds=20
        )
    )
    cached_openrouter = _make_openrouter_success(source="cached-openrouter")
    config_module.save_cli_cache(
        {
            "payload": {"openrouter": cached_openrouter.model_dump(mode="json")},
            "status": {},
        }
    )

    failing_provider = MagicMock()
    failing_provider.is_configured.return_value = True
    failing_provider.name = ProviderName.OPENROUTER
    failing_provider.fetch = AsyncMock(return_value=_make_openrouter_429())
    healthy_provider = MagicMock()
    healthy_provider.is_configured.return_value = True
    healthy_provider.name = ProviderName.GEMINIAI
    healthy_provider.fetch = AsyncMock(return_value=_make_geminiai_success(source="fresh"))
    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {
            ProviderName.OPENROUTER: failing_provider,
            ProviderName.GEMINIAI: healthy_provider,
        },
    )
    monkeypatch.setattr("aibar.cli._apply_api_call_delay", lambda state: None)
    runner = CliRunner()
    result = runner.invoke(main, ["show", "--json", "--force"])
    assert result.exit_code == 0

    output = json.loads(result.output)
    assert output["status"]["openrouter"]["30d"]["result"] == "FAIL"
    assert output["status"]["geminiai"]["30d"]["result"] == "OK"
    assert output["payload"]["openrouter"]["raw"]["source"] == "cached-openrouter"
    assert output["payload"]["geminiai"]["error"] is None


def test_refresh_flow_does_not_create_legacy_snapshot_files(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify refresh flow does not create legacy per-provider snapshot files.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-020
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        config_module.RuntimeConfig(
            idle_delay_seconds=300, api_call_delay_milliseconds=20
        )
    )
    provider = MagicMock()
    provider.is_configured.return_value = True
    provider.name = ProviderName.OPENROUTER
    provider.fetch = AsyncMock(return_value=_make_openrouter_success(source="fresh"))
    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {ProviderName.OPENROUTER: provider},
    )
    monkeypatch.setattr("aibar.cli._apply_api_call_delay", lambda state: None)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["show", "--provider", "openrouter", "--window", "7d", "--json", "--force"],
    )
    assert result.exit_code == 0
    cache_dir = tmp_path / ".cache" / "aibar"
    assert not list(cache_dir.glob("*last_success*"))


def test_geminiai_cached_fail_status_is_rendered_in_show_output(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify GeminiAI cached FAIL status propagates with status-reason block.
    @details Writes cache payload with successful GeminiAI metrics plus status FAIL
    for 30d window, activates idle-time gating, and asserts `aibar show` prints
    status/reason lines without `Window` heading rows even with explicit `--window 7d`.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-097
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        config_module.RuntimeConfig(
            idle_delay_seconds=300, api_call_delay_milliseconds=20
        )
    )

    cached_success = ProviderResult(
        provider=ProviderName.GEMINIAI,
        window=WindowPeriod.DAY_30,
        metrics=UsageMetrics(
            cost=2.75, requests=120, input_tokens=1024, currency_symbol="€"
        ),
        raw={
            "project_id": "demo-project",
            "billing": {"table_id": "gcp_billing_export_v1_001"},
        },
    )
    config_module.save_cli_cache(
        {
            "payload": {"geminiai": cached_success.model_dump(mode="json")},
            "status": {
                "geminiai": {
                    "30d": {
                        "result": "FAIL",
                        "error": "GeminiAI billing export table was not found in dataset 'billing_data'.",
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                        "status_code": None,
                    }
                }
            },
        }
    )
    now_utc = datetime.now(timezone.utc)
    config_module.save_idle_time(
        {
            ProviderName.GEMINIAI.value: config_module.build_idle_time_state(
                now_utc,
                now_utc + timedelta(minutes=5),
            )
        }
    )

    provider = MagicMock()
    provider.is_configured.return_value = True
    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {ProviderName.GEMINIAI: provider},
    )

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--provider", "geminiai", "--window", "7d"])
    assert result.exit_code == 0
    assert "Window 30d:" not in result.output
    assert "Status: FAIL" in result.output
    assert (
        "Reason: GeminiAI billing export table was not found in dataset 'billing_data'."
        in result.output
    )
    assert (
        "Error: GeminiAI billing export table was not found in dataset 'billing_data'."
        not in result.output
    )


def test_geminiai_rate_limit_preserves_payload_and_updates_only_its_idle_state(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify GeminiAI HTTP 429 preserves payload and updates only GeminiAI retry idle-time.
    @details Executes refresh with cached GeminiAI payload, GeminiAI HTTP 429 failure,
    and OpenRouter success. Asserts GeminiAI payload snapshot is retained with
    `status=FAIL`, and idle-time entries apply retry-after expansion only to GeminiAI.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-041
    @satisfies REQ-058
    @satisfies TST-027
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        config_module.RuntimeConfig(
            idle_delay_seconds=300, api_call_delay_milliseconds=20
        )
    )
    cached_geminiai = _make_geminiai_success(source="cached-geminiai")
    config_module.save_cli_cache(
        {
            "payload": {"geminiai": cached_geminiai.model_dump(mode="json")},
            "status": {},
        }
    )

    geminiai_provider = MagicMock()
    geminiai_provider.is_configured.return_value = True
    geminiai_provider.fetch = AsyncMock(
        return_value=_make_geminiai_429(retry_after_seconds=900)
    )
    openrouter_provider = MagicMock()
    openrouter_provider.is_configured.return_value = True
    openrouter_provider.fetch = AsyncMock(
        return_value=_make_openrouter_success(source="live-openrouter")
    )
    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {
            ProviderName.GEMINIAI: geminiai_provider,
            ProviderName.OPENROUTER: openrouter_provider,
        },
    )
    monkeypatch.setattr("aibar.cli._apply_api_call_delay", lambda state: None)

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--json", "--force"])
    assert result.exit_code == 0

    output = json.loads(result.output)
    assert output["payload"]["geminiai"]["raw"]["source"] == "cached-geminiai"
    assert output["status"]["geminiai"]["30d"]["result"] == "FAIL"
    assert output["status"]["geminiai"]["30d"]["status_code"] == 429

    idle_state = json.loads(config_module.IDLE_TIME_PATH.read_text(encoding="utf-8"))
    geminiai_state = idle_state[ProviderName.GEMINIAI.value]
    openrouter_state = idle_state[ProviderName.OPENROUTER.value]
    geminiai_delta = (
        geminiai_state["idle_until_timestamp"]
        - geminiai_state["last_success_timestamp"]
    )
    openrouter_delta = (
        openrouter_state["idle_until_timestamp"]
        - openrouter_state["last_success_timestamp"]
    )
    assert 899 <= geminiai_delta <= 901
    assert 299 <= openrouter_delta <= 301
