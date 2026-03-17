"""
@file
@brief CLI show freshness/status-message regression tests.
@details Verifies `show` renders `Updated/Next` datetime labels with date+time and
surfaces cached authentication/rate-limit status failures in text output.
@satisfies REQ-084
@satisfies REQ-085
@satisfies TST-038
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock

from click.testing import CliRunner

from aibar import config as config_module
from aibar.cli import RetrievalPipelineOutput, main
from aibar.providers.base import ProviderName, ProviderResult, UsageMetrics, WindowPeriod


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


def test_show_renders_updated_next_datetime_with_runtime_refresh_interval(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify CLI `show` renders date+time `Updated/Next` labels.
    @details Uses deterministic `updated_at` plus runtime refresh interval to assert
    `Updated: <datetime>, Next: <datetime>` output format in runtime local timezone.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-084
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
    updated_at = datetime(2026, 3, 17, 8, 0, tzinfo=timezone.utc)
    result_payload = ProviderResult(
        provider=ProviderName.OPENAI,
        window=WindowPeriod.DAY_7,
        metrics=UsageMetrics(cost=1.25),
        updated_at=updated_at,
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
            idle_active=False,
            cache_available=True,
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--provider", "openai", "--window", "7d"])
    assert result.exit_code == 0
    expected_freshness_line = (
        "Updated: "
        f"{updated_at.astimezone().strftime('%Y-%m-%d %H:%M')}, "
        f"Next: {(updated_at + timedelta(seconds=120)).astimezone().strftime('%Y-%m-%d %H:%M')}"
    )
    assert expected_freshness_line in result.output


def test_show_renders_cached_authentication_failure_from_status_section(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify CLI `show` surfaces cached authentication failures for non-Gemini providers.
    @details Writes OpenRouter cache payload with `status[openrouter][7d]=FAIL` and
    asserts text output prints cached authentication error during idle-time serving.
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
    assert "HTTP status: 401" in result.output
