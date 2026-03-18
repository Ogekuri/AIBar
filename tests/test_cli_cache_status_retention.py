"""
@file
@brief Cache status-retention tests for per-provider/window refresh outcomes.
@details Verifies failed refresh attempts preserve last-success payload snapshots,
persist granular `OK`/`FAIL` window statuses with error metadata, and avoid legacy
`claude_dual_last_success.json` read/write paths.
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
from unittest.mock import AsyncMock, MagicMock, patch

from click.testing import CliRunner

from aibar import config as config_module
from aibar.cli import main
from aibar.providers.base import ProviderName, ProviderResult, UsageMetrics, WindowPeriod
from aibar.providers.claude_oauth import ClaudeOAuthProvider


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


def _make_claude_success(window: WindowPeriod, utilization_7d: float) -> ProviderResult:
    """
    @brief Build deterministic successful Claude dual-window payload fixture.
    @param window {WindowPeriod} Window encoded in ProviderResult wrapper.
    @param utilization_7d {float} Seven-day utilization encoded in raw payload.
    @return {ProviderResult} Successful Claude result with dual-window raw payload.
    """
    dual_raw = {
        "five_hour": {
            "utilization": 35.0,
            "resets_at": "2026-03-08T15:00:00+00:00",
        },
        "seven_day": {
            "utilization": utilization_7d,
            "resets_at": "2026-03-12T08:00:00+00:00",
        },
    }
    return ProviderResult(
        provider=ProviderName.CLAUDE,
        window=window,
        metrics=UsageMetrics(remaining=100.0 - utilization_7d, limit=100.0),
        raw=dual_raw,
        updated_at=datetime.now(timezone.utc),
    )


def _make_claude_429(window: WindowPeriod) -> ProviderResult:
    """
    @brief Build deterministic Claude HTTP 429 result fixture.
    @param window {WindowPeriod} Window identifier.
    @return {ProviderResult} Failed Claude result with 429 marker.
    """
    return ProviderResult(
        provider=ProviderName.CLAUDE,
        window=window,
        metrics=UsageMetrics(),
        error="Rate limited. Try again later.",
        raw={"status_code": 429, "retry_after_seconds": 45},
        updated_at=datetime.now(timezone.utc),
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
        metrics=UsageMetrics(cost=3.0, requests=90, input_tokens=600, currency_symbol="€"),
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
        config_module.RuntimeConfig(idle_delay_seconds=300, api_call_delay_milliseconds=20)
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
    assert output["status"]["openrouter"]["30d"]["error"] == "Rate limited. Try again later."
    assert isinstance(output["status"]["openrouter"]["30d"]["updated_at"], str)


def test_partial_claude_refresh_records_mixed_window_statuses(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify partial Claude refresh records mixed window statuses with payload retention.
    @details Simulates `5h=FAIL` and `7d=OK` in one refresh run and verifies both
    statuses are persisted while payload remains successful (non-error) snapshot.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-019
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        config_module.RuntimeConfig(idle_delay_seconds=300, api_call_delay_milliseconds=20)
    )
    initial_claude = _make_claude_success(WindowPeriod.DAY_7, utilization_7d=30.0)
    config_module.save_cli_cache(
        {
            "payload": {"claude": initial_claude.model_dump(mode="json")},
            "status": {},
        }
    )

    provider = ClaudeOAuthProvider(token="sk-ant-test-token")
    mixed_results = (
        _make_claude_429(WindowPeriod.HOUR_5),
        _make_claude_success(WindowPeriod.DAY_7, utilization_7d=55.0),
    )
    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {ProviderName.CLAUDE: provider},
    )
    monkeypatch.setattr("aibar.cli._apply_api_call_delay", lambda state: None)
    with patch("aibar.cli._fetch_claude_dual", return_value=mixed_results):
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["show", "--provider", "claude", "--window", "5h", "--json", "--force"],
        )
    assert result.exit_code == 0

    output = json.loads(result.output)
    assert output["status"]["claude"]["5h"]["result"] == "FAIL"
    assert output["status"]["claude"]["7d"]["result"] == "OK"
    assert output["payload"]["claude"]["error"] is None
    assert output["payload"]["claude"]["window"] in {"5h", "7d"}


def test_refresh_flow_does_not_create_legacy_claude_snapshot_file(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify refresh flow does not create legacy `claude_dual_last_success.json`.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-020
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        config_module.RuntimeConfig(idle_delay_seconds=300, api_call_delay_milliseconds=20)
    )
    provider = ClaudeOAuthProvider(token="sk-ant-test-token")
    successful = {
        WindowPeriod.HOUR_5: _make_claude_success(WindowPeriod.HOUR_5, utilization_7d=44.0),
        WindowPeriod.DAY_7: _make_claude_success(WindowPeriod.DAY_7, utilization_7d=44.0),
    }
    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {ProviderName.CLAUDE: provider},
    )
    monkeypatch.setattr("aibar.cli._apply_api_call_delay", lambda state: None)
    with patch.object(
        ClaudeOAuthProvider,
        "fetch_all_windows",
        new=AsyncMock(return_value=successful),
    ):
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["show", "--provider", "claude", "--window", "7d", "--json", "--force"],
        )
    assert result.exit_code == 0
    legacy_path = tmp_path / ".cache" / "aibar" / "claude_dual_last_success.json"
    assert not legacy_path.exists()


def test_geminiai_cached_fail_status_is_rendered_in_show_output(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify GeminiAI cached FAIL status propagates to CLI text output.
    @details Writes cache payload with successful GeminiAI metrics plus status FAIL
    for 30d window, activates idle-time gating, and asserts `aibar show` prints the
    cached status error message and renders effective GeminiAI window `30d` even with
    explicit `--window 7d`.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-097
    """
    _patch_config_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        config_module.RuntimeConfig(idle_delay_seconds=300, api_call_delay_milliseconds=20)
    )

    cached_success = ProviderResult(
        provider=ProviderName.GEMINIAI,
        window=WindowPeriod.DAY_30,
        metrics=UsageMetrics(cost=2.75, requests=120, input_tokens=1024, currency_symbol="€"),
        raw={"project_id": "demo-project", "billing": {"table_id": "gcp_billing_export_v1_001"}},
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
    assert "Window: 30d" in result.output
    assert "Error: GeminiAI billing export table was not found in dataset 'billing_data'." in result.output


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
        config_module.RuntimeConfig(idle_delay_seconds=300, api_call_delay_milliseconds=20)
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
        geminiai_state["idle_until_timestamp"] - geminiai_state["last_success_timestamp"]
    )
    openrouter_delta = (
        openrouter_state["idle_until_timestamp"] - openrouter_state["last_success_timestamp"]
    )
    assert 899 <= geminiai_delta <= 901
    assert 299 <= openrouter_delta <= 301
