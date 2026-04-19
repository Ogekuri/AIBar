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
from aibar.providers.base import (
    ProviderName,
    ProviderResult,
    UsageMetrics,
    WindowPeriod,
)
from aibar.providers.claude_oauth import ClaudeOAuthProvider
from aibar.providers.openrouter import OpenRouterUsageProvider


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
    monkeypatch.setattr(
        config_module, "RUNTIME_CONFIG_PATH", config_dir / "config.json"
    )
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
        window=WindowPeriod.DAY_30,
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
        window=WindowPeriod.DAY_30,
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
    result = runner.invoke(
        main, ["show", "--provider", "openai", "--window", "7d", "--json"]
    )
    assert result.exit_code == 0
    output_doc = json.loads(result.output)
    freshness_entry = output_doc["freshness"][ProviderName.OPENAI.value]
    assert (
        freshness_entry["last_success_timestamp"]
        == idle_time_state.last_success_timestamp
    )
    assert (
        freshness_entry["idle_until_timestamp"] == idle_time_state.idle_until_timestamp
    )
    assert freshness_entry[
        "last_success_local"
    ] == idle_last_success.astimezone().strftime("%Y-%m-%d %H:%M")
    assert freshness_entry["idle_until_local"] == idle_until.astimezone().strftime(
        "%Y-%m-%d %H:%M"
    )


def test_show_renders_cached_failure_reason_block_with_freshness(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify CLI `show` renders failed status blocks with reason and freshness lines.
    @details Writes OpenRouter cache payload with `status[openrouter][7d]=FAIL` and
    asserts output prints `Status: FAIL` plus `Reason: ...` and `Updated/Next` while
    suppressing stale payload metrics.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-085
    @satisfies TST-038
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        config_module.RuntimeConfig(
            idle_delay_seconds=300, api_call_delay_milliseconds=20
        )
    )
    cached_success = ProviderResult(
        provider=ProviderName.OPENROUTER,
        window=WindowPeriod.DAY_30,
        metrics=UsageMetrics(cost=2.75),
        raw={"status_code": 200, "source": "cached-success"},
    )
    config_module.save_cli_cache(
        {
            "payload": {"openrouter": cached_success.model_dump(mode="json")},
            "status": {
                "openrouter": {
                    "30d": {
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
    assert "Window 30d:" not in result.output
    assert "Window 7d:" not in result.output
    assert "Reason: Invalid or expired OAuth token" in result.output
    assert "Error: Invalid or expired OAuth token" not in result.output
    assert "HTTP status: 401, Retry after: 300 sec." not in result.output
    assert "Updated:" in result.output
    assert "Next:" in result.output
    assert "Cost:" not in result.output
    assert "Usage:" not in result.output
    assert "Remaining credits:" not in result.output


def test_show_dual_window_cached_fail_status_renders_reason_with_freshness(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify Claude grouped dual-window panel renders deduplicated failed block.
    @details Seeds successful Claude dual-window payload with cached `status[claude][5h|7d]=FAIL`,
    activates idle-time cache read path, and asserts one grouped panel renders one shared
    failed block (`Status`, `Reason`, `Updated/Next`) without `Window` headings.
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
    assert result.output.count("Reason: Invalid or expired OAuth token") == 1
    assert "Error: Invalid or expired OAuth token" not in result.output
    assert "Window 5h:" not in result.output
    assert "Window 7d:" not in result.output
    assert "Window: 5h" not in result.output
    assert "Window: 7d" not in result.output
    assert "Usage:" not in result.output
    assert "Cost:" not in result.output
    assert "Remaining credits:" not in result.output
    assert "Requests:" not in result.output
    assert "Tokens:" not in result.output
    assert "Resets in:" not in result.output
    status_idx = result.output.index("Status: FAIL")
    reason_idx = result.output.index("Reason: Invalid or expired OAuth token")
    updated_idx = result.output.index("Updated:")
    assert status_idx < reason_idx < updated_idx


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


def test_build_result_panel_renders_progress_bar_usage_for_openrouter() -> None:
    """
    @brief Verify OpenRouter usage rows keep the standard CLI progress-bar format.
    @details Builds an OK-state OpenRouter panel with explicit quota metrics and
    asserts output keeps `Usage: <window> <progress_bar> <percent>%` with the
    same bracketed glyph surface used by other CLI bar-enabled providers.
    @return {None} Function return value.
    @satisfies REQ-132
    @satisfies TST-059
    """
    result_payload = ProviderResult(
        provider=ProviderName.OPENROUTER,
        window=WindowPeriod.DAY_30,
        metrics=UsageMetrics(remaining=57.5, limit=100.0),
        raw={"status_code": 200},
    )
    _title, lines = _build_result_panel(ProviderName.OPENROUTER, result_payload)
    usage_line = next(line for line in lines if line.startswith("Usage:"))
    assert usage_line.startswith("Usage: 30d [")
    assert usage_line.endswith(" 42.5%")
    assert "[" in usage_line
    assert "]" in usage_line
    assert "█" in usage_line
    assert "░" in usage_line
    assert "▓" not in usage_line


def test_build_result_panel_defaults_openrouter_usage_to_zero_percent() -> None:
    """
    @brief Verify OpenRouter CLI output preserves the GNOME-aligned zero-percent fallback.
    @details Builds an OK-state OpenRouter panel with missing quota inputs so
    `metrics.usage_percent` resolves to `None`. Asserts CLI rendering still emits
    `Usage: 30d <progress_bar> 0.0%`, matching the GNOME provider-card fallback
    used for single-window bar providers.
    @return {None} Function return value.
    @satisfies REQ-132
    @satisfies TST-059
    """
    result_payload = ProviderResult(
        provider=ProviderName.OPENROUTER,
        window=WindowPeriod.DAY_30,
        metrics=UsageMetrics(cost=0.0, requests=0, input_tokens=0, output_tokens=0),
        raw={"status_code": 200},
    )
    _title, lines = _build_result_panel(ProviderName.OPENROUTER, result_payload)
    usage_line = next(line for line in lines if line.startswith("Usage:"))
    assert usage_line.startswith("Usage: 30d [")
    assert usage_line.endswith(" 0.0%")
    assert "█" not in usage_line
    assert "░" in usage_line


def test_build_result_panel_renders_openrouter_reset_and_spacing() -> None:
    """
    @brief Reproduce missing OpenRouter reset countdown and separator spacing.
    @details Builds an OK-state OpenRouter payload through
    `OpenRouterUsageProvider._parse_response(...)` so `metrics.reset_at` is absent
    before CLI rendering. Asserts `_build_result_panel(...)` still emits a
    `Resets in:` row directly under the usage row and inserts one blank separator
    before the cost block.
    @return {None} Function return value.
    @satisfies REQ-034
    @satisfies REQ-067
    @satisfies REQ-132
    """
    provider = OpenRouterUsageProvider(api_key="test-openrouter-key")
    result_payload = provider._parse_response(
        {
            "data": {
                "usage_monthly": 42.5,
                "limit": 100.0,
                "limit_remaining": 57.5,
            }
        },
        WindowPeriod.DAY_30,
    )

    _title, lines = _build_result_panel(ProviderName.OPENROUTER, result_payload)

    usage_line_index = next(
        index for index, line in enumerate(lines) if line.startswith("Usage:")
    )
    reset_line_index = next(
        index for index, line in enumerate(lines) if line.startswith("Resets in:")
    )
    cost_line_index = next(
        index for index, line in enumerate(lines) if line.startswith("Cost:")
    )

    assert reset_line_index == usage_line_index + 1
    assert lines[reset_line_index + 1] == ""
    assert cost_line_index == reset_line_index + 2


def test_build_result_panel_renders_text_only_usage_for_openai_and_geminiai() -> None:
    """
    @brief Verify OpenAI and GeminiAI usage rows omit CLI progress bars.
    @details Builds OK-state panels for `openai` and `geminiai` with explicit
    usage percentages and asserts output keeps `Usage: <window> <percent>%`
    text without bracketed progress-bar glyphs.
    @return {None} Function return value.
    @satisfies REQ-131
    @satisfies TST-054
    """
    for provider_name in (ProviderName.OPENAI, ProviderName.GEMINIAI):
        result_payload = ProviderResult(
            provider=provider_name,
            window=WindowPeriod.DAY_30,
            metrics=UsageMetrics(remaining=57.5, limit=100.0),
            raw={"status_code": 200},
        )
        _title, lines = _build_result_panel(provider_name, result_payload)
        usage_line = next(line for line in lines if line.startswith("Usage:"))
        assert usage_line == "Usage: 30d 42.5%"
        assert "[" not in usage_line
        assert "]" not in usage_line
        assert "█" not in usage_line
        assert "░" not in usage_line
        assert "▓" not in usage_line


def test_build_result_panel_renders_geminiai_billing_services_human_readable() -> None:
    """
    @brief Verify GeminiAI panel renders human-readable billing service names.
    @details Builds GeminiAI panel lines with ordered billing `service_description`
    entries and verifies output includes count plus parenthesized service list.
    @return {None} Function return value.
    @satisfies REQ-106
    @satisfies TST-046
    """
    result_payload = ProviderResult(
        provider=ProviderName.GEMINIAI,
        window=WindowPeriod.DAY_30,
        metrics=UsageMetrics(cost=12.5, currency_symbol="$"),
        raw={
            "billing": {
                "services": [
                    {"service_description": "Google AI Studio"},
                    {"service_description": "TAX"},
                ]
            }
        },
    )
    _title, lines = _build_result_panel(ProviderName.GEMINIAI, result_payload)
    assert "Billing services: 2 (Google AI Studio, TAX)" in lines


def test_build_result_panel_renders_all_geminiai_billing_services() -> None:
    """
    @brief Verify GeminiAI billing services rendering includes all services.
    @details Builds GeminiAI panel lines with four billing services and asserts
    output preserves order and prints all service names without truncation.
    @return {None} Function return value.
    @satisfies REQ-106
    @satisfies TST-046
    """
    result_payload = ProviderResult(
        provider=ProviderName.GEMINIAI,
        window=WindowPeriod.DAY_30,
        metrics=UsageMetrics(cost=1.0, currency_symbol="$"),
        raw={
            "billing": {
                "services": [
                    {"service_description": "Google AI Studio"},
                    {"service_description": "TAX"},
                    {"service_description": "Vertex AI"},
                    {"service_description": "BigQuery"},
                ]
            }
        },
    )
    _title, lines = _build_result_panel(ProviderName.GEMINIAI, result_payload)
    assert "Billing services: 4 (Google AI Studio, TAX, Vertex AI, BigQuery)" in lines
