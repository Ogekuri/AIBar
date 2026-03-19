"""
@file
@brief Claude OAuth renewal/retry and refresh-block lifecycle tests.
@details Verifies in-process Claude renewal routine parity with
`scripts/claude_token_refresh.sh once` behavior, one-shot auth retry policy,
and idle-time refresh-block lifecycle (`oauth_refresh_blocked`) including
`--force` clear and hardcoded 86400-second TTL auto-clear.
@satisfies REQ-100
@satisfies REQ-101
@satisfies REQ-102
@satisfies REQ-103
@satisfies REQ-104
@satisfies REQ-105
@satisfies TST-043
@satisfies TST-044
@satisfies TST-045
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from click.testing import CliRunner

from aibar import config as config_module
from aibar.cli import main
from aibar.providers.base import ProviderName


def _patch_config_paths(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Redirect AIBar config/cache file paths to temp directory.
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


def _save_runtime_config() -> None:
    """
    @brief Persist deterministic runtime config for API delay/timeout tests.
    @return {None} Function return value.
    """
    config_module.save_runtime_config(
        config_module.RuntimeConfig(
            idle_delay_seconds=300,
            api_call_delay_milliseconds=15,
            api_call_timeout_milliseconds=1200,
            gnome_refresh_interval_seconds=60,
        )
    )


def _seed_claude_idle_time(
    *,
    blocked: bool,
    last_success_at: datetime,
    idle_until: datetime,
) -> None:
    """
    @brief Seed Claude idle-time state including oauth_refresh_blocked field.
    @param blocked {bool} Refresh-block flag value.
    @param last_success_at {datetime} Claude last-success timestamp.
    @param idle_until {datetime} Claude idle-until timestamp.
    @return {None} Function return value.
    """
    state = config_module.build_idle_time_state(
        last_success_at=last_success_at,
        idle_until=idle_until,
    )
    state = state.model_copy(update={"oauth_refresh_blocked": blocked})
    config_module.save_idle_time({"claude": state})


def _seed_claude_cache_success() -> None:
    """
    @brief Seed deterministic Claude payload baseline in cache.json.
    @details Provides a last-success payload so status-overlay rendering can show
    authentication errors after failed refresh attempts.
    @return {None} Function return value.
    """
    from aibar.providers.base import ProviderResult, UsageMetrics, WindowPeriod

    payload = ProviderResult(
        provider=ProviderName.CLAUDE,
        window=WindowPeriod.DAY_7,
        metrics=UsageMetrics(remaining=75.0, limit=100.0),
        raw={
            "five_hour": {
                "utilization": 20.0,
                "resets_at": "2026-03-20T08:00:00+00:00",
            },
            "seven_day": {
                "utilization": 25.0,
                "resets_at": "2026-03-24T08:00:00+00:00",
            },
        },
    )
    config_module.save_cli_cache(
        {"payload": {"claude": payload.model_dump(mode="json")}, "status": {}}
    )


def _patch_claude_provider(monkeypatch) -> None:
    """
    @brief Patch provider registry with deterministic configured Claude provider.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    """
    from aibar.providers.claude_oauth import ClaudeOAuthProvider

    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {ProviderName.CLAUDE: ClaudeOAuthProvider(token="sk-ant-test-token")},
    )


def test_claude_oauth_recovery_retry_persists_block_on_second_auth_failure(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify one renewal attempt + one retry, then block flag persistence.
    @details Simulates Claude auth failure before and after renewal, asserts
    renewal routine executes once, CLI shows canonical auth error text, and
    idle-time persists `claude.oauth_refresh_blocked=true`.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-044
    """
    _patch_config_paths(monkeypatch, tmp_path)
    _save_runtime_config()
    now = datetime.now(timezone.utc)
    _seed_claude_idle_time(
        blocked=False,
        last_success_at=now,
        idle_until=now - timedelta(seconds=1),
    )

    refresh_calls: list[int] = []
    dual_calls: list[int] = []

    _seed_claude_cache_success()

    def _fake_refresh(runtime_config):
        del runtime_config
        refresh_calls.append(1)
        return True

    def _fake_dual(provider, throttle_state=None):
        del provider, throttle_state
        dual_calls.append(1)
        if len(dual_calls) == 1:
            return (
                _make_claude_error_result(window="5h"),
                _make_claude_error_result(window="7d"),
            )
        return (
            _make_claude_error_result(window="5h"),
            _make_claude_error_result(window="7d"),
        )

    monkeypatch.setattr("aibar.cli._run_claude_oauth_token_refresh", _fake_refresh)
    monkeypatch.setattr("aibar.cli._fetch_claude_dual", _fake_dual)
    _patch_claude_provider(monkeypatch)

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--provider", "claude", "--window", "7d"])
    assert result.exit_code == 0
    assert "Reason: Invalid or expired OAuth token" in result.output
    assert "Error: Invalid or expired OAuth token" not in result.output
    assert len(refresh_calls) == 1
    assert len(dual_calls) == 2

    saved_state = config_module.load_idle_time()["claude"]
    assert saved_state.oauth_refresh_blocked is True


def test_claude_oauth_recovery_skips_refresh_when_block_flag_active(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify active block flag suppresses renewal routine execution.
    @details Seeds non-expired `oauth_refresh_blocked=true` and asserts auth
    failure does not trigger renewal routine.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-045
    """
    _patch_config_paths(monkeypatch, tmp_path)
    _save_runtime_config()
    now = datetime.now(timezone.utc)
    _seed_claude_idle_time(
        blocked=True,
        last_success_at=now,
        idle_until=now - timedelta(seconds=1),
    )

    refresh_calls: list[int] = []

    _seed_claude_cache_success()

    def _fake_refresh(runtime_config):
        del runtime_config
        refresh_calls.append(1)
        return True

    monkeypatch.setattr("aibar.cli._run_claude_oauth_token_refresh", _fake_refresh)
    monkeypatch.setattr(
        "aibar.cli._fetch_claude_dual",
        lambda provider, throttle_state=None: (
            _make_claude_error_result(window="5h"),
            _make_claude_error_result(window="7d"),
        ),
    )
    _patch_claude_provider(monkeypatch)

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--provider", "claude", "--window", "7d"])
    assert result.exit_code == 0
    assert "Reason: Invalid or expired OAuth token" in result.output
    assert "Error: Invalid or expired OAuth token" not in result.output
    assert len(refresh_calls) == 0


def test_claude_oauth_recovery_auto_clears_expired_block_flag(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify expired refresh-block auto-clears and permits one renewal attempt.
    @details Seeds `oauth_refresh_blocked=true` with stale `last_success_timestamp`
    older than 86400 seconds, then asserts renewal routine executes once and block
    flag is cleared when retry succeeds.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-045
    """
    _patch_config_paths(monkeypatch, tmp_path)
    _save_runtime_config()
    now = datetime.now(timezone.utc)
    _seed_claude_idle_time(
        blocked=True,
        last_success_at=now - timedelta(days=2),
        idle_until=now - timedelta(seconds=1),
    )

    refresh_calls: list[int] = []
    dual_calls: list[int] = []

    _seed_claude_cache_success()

    def _fake_refresh(runtime_config):
        del runtime_config
        refresh_calls.append(1)
        return True

    def _fake_dual(provider, throttle_state=None):
        del provider, throttle_state
        dual_calls.append(1)
        if len(dual_calls) == 1:
            return (
                _make_claude_error_result(window="5h"),
                _make_claude_error_result(window="7d"),
            )
        return (
            _make_claude_success_result(window="5h"),
            _make_claude_success_result(window="7d"),
        )

    monkeypatch.setattr("aibar.cli._run_claude_oauth_token_refresh", _fake_refresh)
    monkeypatch.setattr("aibar.cli._fetch_claude_dual", _fake_dual)
    _patch_claude_provider(monkeypatch)

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--provider", "claude", "--window", "7d"])
    assert result.exit_code == 0
    assert len(refresh_calls) == 1
    assert len(dual_calls) == 2
    saved_state = config_module.load_idle_time()["claude"]
    assert saved_state.oauth_refresh_blocked is False


def test_claude_oauth_recovery_force_clears_block_flag(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify `show --force` clears block flag and allows renewal routine.
    @details Seeds active block flag, invokes `show --force`, and asserts one
    renewal attempt is executed and persisted block flag is false.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-045
    """
    _patch_config_paths(monkeypatch, tmp_path)
    _save_runtime_config()
    now = datetime.now(timezone.utc)
    _seed_claude_idle_time(
        blocked=True,
        last_success_at=now,
        idle_until=now + timedelta(seconds=300),
    )

    refresh_calls: list[int] = []
    dual_calls: list[int] = []

    _seed_claude_cache_success()

    def _fake_refresh(runtime_config):
        del runtime_config
        refresh_calls.append(1)
        return True

    def _fake_dual(provider, throttle_state=None):
        del provider, throttle_state
        dual_calls.append(1)
        if len(dual_calls) == 1:
            return (
                _make_claude_error_result(window="5h"),
                _make_claude_error_result(window="7d"),
            )
        return (
            _make_claude_success_result(window="5h"),
            _make_claude_success_result(window="7d"),
        )

    monkeypatch.setattr("aibar.cli._run_claude_oauth_token_refresh", _fake_refresh)
    monkeypatch.setattr("aibar.cli._fetch_claude_dual", _fake_dual)
    _patch_claude_provider(monkeypatch)

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["show", "--provider", "claude", "--window", "7d", "--force"],
    )
    assert result.exit_code == 0
    assert len(refresh_calls) == 1
    assert len(dual_calls) == 2
    saved_state = config_module.load_idle_time()["claude"]
    assert saved_state.oauth_refresh_blocked is False


def test_run_claude_oauth_token_refresh_truncates_log_and_checks_commands(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify renewal routine truncates log and handles missing commands.
    @details Pre-populates log file, forces `claude` and `aibar` command absence,
    executes refresh routine, then asserts old content is truncated and warning
    lines are emitted for each missing command.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-043
    """
    _patch_config_paths(monkeypatch, tmp_path)
    _save_runtime_config()

    log_path = tmp_path / ".config" / "aibar" / "claude_token_refresh.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("old-line\n", encoding="utf-8")

    monkeypatch.setattr("aibar.cli._CLAUDE_TOKEN_REFRESH_LOG_PATH", log_path)
    monkeypatch.setattr("aibar.cli.shutil.which", lambda name: None)

    from aibar.cli import _run_claude_oauth_token_refresh

    ok = _run_claude_oauth_token_refresh(config_module.load_runtime_config())
    assert ok is False
    content = log_path.read_text(encoding="utf-8")
    assert "old-line" not in content
    assert "Starting token refresh cycle" in content
    assert "Warning: claude command not found" in content
    assert "Warning: aibar command not found" in content
    assert "Token refresh cycle complete" in content


def _make_claude_error_result(window: str):
    """
    @brief Build deterministic Claude auth-error ProviderResult.
    @param window {str} Window literal (`5h` or `7d`).
    @return {aibar.providers.base.ProviderResult} Error result payload.
    """
    from aibar.providers.base import (
        ProviderName,
        ProviderResult,
        UsageMetrics,
        WindowPeriod,
    )

    return ProviderResult(
        provider=ProviderName.CLAUDE,
        window=WindowPeriod(window),
        metrics=UsageMetrics(),
        error="Invalid or expired OAuth token",
        raw={"status_code": 401},
    )


def _make_claude_success_result(window: str):
    """
    @brief Build deterministic Claude success ProviderResult.
    @param window {str} Window literal (`5h` or `7d`).
    @return {aibar.providers.base.ProviderResult} Successful result payload.
    """
    from aibar.providers.base import (
        ProviderName,
        ProviderResult,
        UsageMetrics,
        WindowPeriod,
    )

    return ProviderResult(
        provider=ProviderName.CLAUDE,
        window=WindowPeriod(window),
        metrics=UsageMetrics(remaining=80.0, limit=100.0),
        raw={"status_code": 200},
    )
