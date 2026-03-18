"""
@file
@brief CLI show freshness/status-message regression tests.
@details Verifies `show` renders `Updated/Next` datetime labels with date+time and
surfaces cached authentication/rate-limit status failures in text output.
@satisfies REQ-084
@satisfies REQ-085
@satisfies TST-038
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock

from click.testing import CliRunner

from aibar import config as config_module
from aibar.cli import RetrievalPipelineOutput, _build_result_panel, main
from aibar.providers.base import ProviderName, ProviderResult, UsageMetrics, WindowPeriod
from aibar.providers.claude_oauth import ClaudeOAuthProvider


def _patch_config_paths(monkeypatch, tmp_path: Path) -> None:
    """
    @brief Redirect AIBar config/cache file paths to temporary test directories.
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


def test_show_renders_updated_next_datetime_from_idle_time_state(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify CLI `show` renders `Updated/Next` labels from provider idle-time state.
    @details Uses deterministic `last_success_timestamp` and `idle_until_timestamp`
    values to assert `Updated: <datetime>, Next: <datetime>` output format in runtime
    local timezone, independent from payload `updated_at`.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-084
    @satisfies TST-038
    """
    _patch_config_paths(monkeypatch, tmp_path)
    payload_updated_at = datetime(2026, 3, 17, 8, 0, tzinfo=timezone.utc)
    idle_last_success = datetime(2026, 3, 18, 8, 58, tzinfo=timezone.utc)
    idle_until = datetime(2026, 3, 18, 8, 59, tzinfo=timezone.utc)
    result_payload = ProviderResult(
        provider=ProviderName.OPENAI,
        window=WindowPeriod.DAY_7,
        metrics=UsageMetrics(cost=1.25),
        updated_at=payload_updated_at,
        raw={"status_code": 200},
    )
    provider = MagicMock()
    provider.is_configured.return_value = True
    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {ProviderName.OPENAI: provider},
    )
    monkeypatch.setattr(
        "aibar.cli.retrieve_results_via_cache_pipeline",
        lambda **_: RetrievalPipelineOutput(
            payload={},
            results={ProviderName.OPENAI.value: result_payload},
            idle_time_by_provider={
                ProviderName.OPENAI.value: config_module.build_idle_time_state(
                    last_success_at=idle_last_success,
                    idle_until=idle_until,
                )
            },
            idle_active=False,
            cache_available=True,
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--provider", "openai", "--window", "7d"])
    assert result.exit_code == 0
    expected_freshness_line = (
        "Updated: "
        f"{idle_last_success.astimezone().strftime('%Y-%m-%d %H:%M')}, "
        f"Next: {idle_until.astimezone().strftime('%Y-%m-%d %H:%M')}"
    )
    assert expected_freshness_line in result.output


def test_show_json_exports_freshness_with_local_datetime_parity(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify CLI `show --json` exports `freshness` aligned to text freshness values.
    @details Uses deterministic idle-time timestamps and asserts `freshness` entries
    include provider timestamps plus local-time `%Y-%m-%d %H:%M` strings.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-084
    @satisfies TST-038
    """
    _patch_config_paths(monkeypatch, tmp_path)
    payload_updated_at = datetime(2026, 3, 17, 8, 0, tzinfo=timezone.utc)
    idle_last_success = datetime(2026, 3, 18, 8, 58, tzinfo=timezone.utc)
    idle_until = datetime(2026, 3, 18, 8, 59, tzinfo=timezone.utc)
    result_payload = ProviderResult(
        provider=ProviderName.OPENAI,
        window=WindowPeriod.DAY_7,
        metrics=UsageMetrics(cost=1.25),
        updated_at=payload_updated_at,
        raw={"status_code": 200},
    )
    provider = MagicMock()
    provider.is_configured.return_value = True
    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {ProviderName.OPENAI: provider},
    )
    idle_time_state = config_module.build_idle_time_state(
        last_success_at=idle_last_success,
        idle_until=idle_until,
    )
    monkeypatch.setattr(
        "aibar.cli.retrieve_results_via_cache_pipeline",
        lambda **_: RetrievalPipelineOutput(
            payload={},
            results={ProviderName.OPENAI.value: result_payload},
            idle_time_by_provider={ProviderName.OPENAI.value: idle_time_state},
            idle_active=False,
            cache_available=True,
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--provider", "openai", "--window", "7d", "--json"])
    assert result.exit_code == 0
    output_doc = json.loads(result.output)
    freshness_entry = output_doc["freshness"][ProviderName.OPENAI.value]
    assert freshness_entry["last_success_timestamp"] == idle_time_state.last_success_timestamp
    assert freshness_entry["idle_until_timestamp"] == idle_time_state.idle_until_timestamp
    assert freshness_entry["last_success_local"] == idle_last_success.astimezone().strftime("%Y-%m-%d %H:%M")
    assert freshness_entry["idle_until_local"] == idle_until.astimezone().strftime("%Y-%m-%d %H:%M")


def test_show_renders_cached_failure_error_only_with_retry_metadata(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify CLI `show` renders failed status blocks without statistics lines.
    @details Writes OpenRouter cache payload with `status[openrouter][7d]=FAIL` and
    asserts output prints cached error plus combined HTTP status/retry metadata while
    suppressing stale payload metrics.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-085
    @satisfies TST-038
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        config_module.RuntimeConfig(idle_delay_seconds=300, api_call_delay_milliseconds=20)
    )
    cached_success = ProviderResult(
        provider=ProviderName.OPENROUTER,
        window=WindowPeriod.DAY_7,
        metrics=UsageMetrics(cost=2.75),
        raw={"status_code": 200, "source": "cached-success"},
    )
    config_module.save_cli_cache(
        {
            "payload": {"openrouter": cached_success.model_dump(mode="json")},
            "status": {
                "openrouter": {
                    "7d": {
                        "result": "FAIL",
                        "error": "Invalid or expired OAuth token",
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                        "status_code": 401,
                        "retry_after_seconds": 300,
                    }
                }
            },
        }
    )
    now_utc = datetime.now(timezone.utc)
    config_module.save_idle_time(
        {
            ProviderName.OPENROUTER.value: config_module.build_idle_time_state(
                now_utc,
                now_utc + timedelta(minutes=5),
            )
        }
    )
    provider = MagicMock()
    provider.is_configured.return_value = True
    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {ProviderName.OPENROUTER: provider},
    )

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--provider", "openrouter", "--window", "7d"])
    assert result.exit_code == 0
    assert "Status: FAIL" in result.output
    assert "Error: Invalid or expired OAuth token" in result.output
    assert "HTTP status: 401, Retry after: 300 sec." in result.output
    assert "Cost:" not in result.output
    assert "Usage:" not in result.output
    assert "Remaining credits:" not in result.output


def test_show_dual_window_cached_fail_status_renders_fail_only_blocks(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify Claude grouped dual-window panel renders deduplicated `FAIL` diagnostics.
    @details Seeds successful Claude dual-window payload with cached `status[claude][5h|7d]=FAIL`,
    activates idle-time cache read path, and asserts one grouped panel contains `5h`/`7d`
    sections while shared failure diagnostics (`Status`, `Updated/Next`, `Error`) render once.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-085
    @satisfies TST-038
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        config_module.RuntimeConfig(
            idle_delay_seconds=300,
            api_call_delay_milliseconds=20,
            gnome_refresh_interval_seconds=120,
        )
    )
    cached_success = ProviderResult(
        provider=ProviderName.CLAUDE,
        window=WindowPeriod.DAY_7,
        metrics=UsageMetrics(remaining=65.0, limit=100.0),
        raw={
            "five_hour": {
                "utilization": 35.0,
                "resets_at": "2026-03-20T08:00:00+00:00",
            },
            "seven_day": {
                "utilization": 45.0,
                "resets_at": "2026-03-24T08:00:00+00:00",
            },
        },
    )
    status_updated_at = datetime.now(timezone.utc).isoformat()
    config_module.save_cli_cache(
        {
            "payload": {"claude": cached_success.model_dump(mode="json")},
            "status": {
                "claude": {
                    "5h": {
                        "result": "FAIL",
                        "error": "Invalid or expired OAuth token",
                        "updated_at": status_updated_at,
                        "status_code": 401,
                        "retry_after_seconds": 300,
                    },
                    "7d": {
                        "result": "FAIL",
                        "error": "Invalid or expired OAuth token",
                        "updated_at": status_updated_at,
                        "status_code": 401,
                        "retry_after_seconds": 300,
                    },
                }
            },
        }
    )
    now_utc = datetime.now(timezone.utc)
    config_module.save_idle_time(
        {
            ProviderName.CLAUDE.value: config_module.build_idle_time_state(
                now_utc,
                now_utc + timedelta(minutes=5),
            )
        }
    )
    provider = ClaudeOAuthProvider(token="sk-ant-test-token")
    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {ProviderName.CLAUDE: provider},
    )

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--provider", "claude"])
    assert result.exit_code == 0
    assert result.output.count("Status: FAIL") == 1
    assert "Status: OK" not in result.output
    assert result.output.count("Error: Invalid or expired OAuth token") == 1
    assert "5h:" in result.output
    assert "7d:" in result.output
    assert "Window: 5h" not in result.output
    assert "Window: 7d" not in result.output
    assert "Usage:" not in result.output
    assert "Cost:" not in result.output
    assert "Remaining credits:" not in result.output
    assert "Requests:" not in result.output
    assert "Tokens:" not in result.output
    assert "Resets in:" not in result.output
    status_idx = result.output.index("Status: FAIL")
    updated_idx = result.output.index("Updated:")
    assert status_idx < result.output.index("5h:") < result.output.index("7d:") < updated_idx


def test_build_result_panel_renders_zero_api_counters_for_null_metrics() -> None:
    """
    @brief Verify API-counter providers render `Requests` and `Tokens` lines as zero on null metrics.
    @details Builds panel lines for `openai`, `openrouter`, `codex`, and `geminiai` with null
    requests/input/output counters and asserts deterministic null-to-zero text rendering.
    @return {None} Function return value.
    @satisfies REQ-036
    @satisfies TST-038
    """
    provider_names = (
        ProviderName.OPENAI,
        ProviderName.OPENROUTER,
        ProviderName.CODEX,
        ProviderName.GEMINIAI,
    )
    for provider_name in provider_names:
        result_payload = ProviderResult(
            provider=provider_name,
            window=WindowPeriod.DAY_7,
            metrics=UsageMetrics(
                requests=None,
                input_tokens=None,
                output_tokens=None,
            ),
            raw={"status_code": 200},
        )
        _title, lines = _build_result_panel(provider_name, result_payload)
        assert "Requests: 0" in lines
        assert "Tokens: 0 (0 in / 0 out)" in lines
