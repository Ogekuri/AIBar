"""
@file
@brief Runtime logging and logging-flag lifecycle regression tests.
@details Verifies CLI logging flag options persistence, execution start/end log
block formatting, runtime pipeline logging coverage, and debug API log gating.
@satisfies TST-047
@satisfies TST-048
@satisfies TST-049
@satisfies TST-050
"""

import re
from pathlib import Path

from click.testing import CliRunner

from aibar import cli as cli_module
from aibar import config as config_module
from aibar.config import RuntimeConfig
from aibar.providers.claude_oauth import ClaudeOAuthProvider
from aibar.providers.base import (
    BaseProvider,
    ProviderError,
    ProviderName,
    ProviderResult,
    UsageMetrics,
    WindowPeriod,
)


def _patch_paths(monkeypatch, tmp_path: Path) -> tuple[Path, Path]:
    """
    @brief Redirect runtime config/cache paths into temporary directory.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {tuple[Path, Path]} Tuple `(config_dir, cache_dir)` for patched paths.
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
    return (config_dir, cache_dir)


def _read_log(cache_dir: Path) -> str:
    """
    @brief Read runtime log file content from patched cache directory.
    @param cache_dir {Path} Patched cache directory root.
    @return {str} Runtime log file content, empty string when file is absent.
    """
    log_path = cache_dir / "aibar.log"
    if not log_path.exists():
        return ""
    return log_path.read_text(encoding="utf-8")


class _SuccessProvider(BaseProvider):
    """
    @brief Deterministic provider stub returning successful fetch results.
    @details Used by runtime logging tests to trigger refresh, cache write, and
    non-debug/debug API result logging branches without external dependencies.
    """

    name = ProviderName.CODEX

    async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult:
        """
        @brief Return deterministic successful provider result.
        @param window {WindowPeriod} Requested usage window.
        @return {ProviderResult} Successful usage result payload.
        """
        return ProviderResult(
            provider=self.name,
            window=window,
            metrics=UsageMetrics(remaining=75.0, limit=100.0),
            raw={"status_code": 200, "message": "ok"},
        )

    def is_configured(self) -> bool:
        """
        @brief Report deterministic configured state for stub provider.
        @return {bool} Always true.
        """
        return True

    def get_config_help(self) -> str:
        """
        @brief Return deterministic configuration help text.
        @return {str} Static helper text.
        """
        return "configured"


class _ErrorProvider(BaseProvider):
    """
    @brief Deterministic provider stub raising ProviderError on fetch.
    @details Used by runtime logging tests to trigger error-logging branches in
    provider fetch orchestration without external API calls.
    """

    name = ProviderName.OPENROUTER

    async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult:
        """
        @brief Raise deterministic provider failure.
        @param window {WindowPeriod} Requested usage window.
        @return {ProviderResult} Unreachable return contract.
        @throws {ProviderError} Always raised to test error logging path.
        """
        del window
        raise ProviderError("provider boom")

    def is_configured(self) -> bool:
        """
        @brief Report deterministic configured state for error stub provider.
        @return {bool} Always true.
        """
        return True

    def get_config_help(self) -> str:
        """
        @brief Return deterministic configuration help text.
        @return {str} Static helper text.
        """
        return "configured"


class _OAuthErrorProvider(BaseProvider):
    """
    @brief Deterministic provider stub returning OAuth-classified failures.
    @details Produces one failed result carrying OAuth error text without
    retry-after metadata so runtime log classification can assert `oauth` branch
    and missing retry-after evidence logging.
    """

    name = ProviderName.OPENAI

    async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult:
        """
        @brief Return deterministic OAuth failure provider result.
        @param window {WindowPeriod} Requested usage window.
        @return {ProviderResult} Failed result with OAuth error text.
        """
        return ProviderResult(
            provider=self.name,
            window=window,
            metrics=UsageMetrics(),
            raw={"status_code": 401},
            error="OAuth token invalid",
        )

    def is_configured(self) -> bool:
        """
        @brief Report deterministic configured state for OAuth stub provider.
        @return {bool} Always true.
        """
        return True

    def get_config_help(self) -> str:
        """
        @brief Return deterministic configuration help text.
        @return {str} Static helper text.
        """
        return "configured"


class _RateLimitProvider(BaseProvider):
    """
    @brief Deterministic provider stub returning HTTP 429 failures.
    @details Produces one failed result carrying `status_code=429` and
    `retry_after_seconds` metadata for runtime log `rate_limit` assertions.
    """

    name = ProviderName.OPENROUTER

    async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult:
        """
        @brief Return deterministic rate-limit failure provider result.
        @param window {WindowPeriod} Requested usage window.
        @return {ProviderResult} Failed result with retry-after metadata.
        """
        return ProviderResult(
            provider=self.name,
            window=window,
            metrics=UsageMetrics(),
            raw={"status_code": 429, "retry_after_seconds": 45},
            error="API error: HTTP 429",
        )

    def is_configured(self) -> bool:
        """
        @brief Report deterministic configured state for rate-limit stub provider.
        @return {bool} Always true.
        """
        return True

    def get_config_help(self) -> str:
        """
        @brief Return deterministic configuration help text.
        @return {str} Static helper text.
        """
        return "configured"


class _OAuthErrorNoRetryAfterProvider(BaseProvider):
    """
    @brief Deterministic provider stub returning OAuth failures without retry-after keys.
    @details Produces one failed result with OAuth error and raw payload that omits
    retry-after fields to validate `retry_after_unavailable=true` evidence logging.
    """

    name = ProviderName.CLAUDE

    async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult:
        """
        @brief Return deterministic OAuth failure with missing retry-after fields.
        @param window {WindowPeriod} Requested usage window.
        @return {ProviderResult} Failed result without retry-after payload keys.
        """
        return ProviderResult(
            provider=self.name,
            window=window,
            metrics=UsageMetrics(),
            raw={"status_code": 401, "failure_marker": "oauth_without_retry_after"},
            error="OAuth access denied",
        )

    def is_configured(self) -> bool:
        """
        @brief Report deterministic configured state for OAuth no-retry stub provider.
        @return {bool} Always true.
        """
        return True

    def get_config_help(self) -> str:
        """
        @brief Return deterministic configuration help text.
        @return {str} Static helper text.
        """
        return "configured"


class _OAuthErrorWithRawJsonBodyProvider(BaseProvider):
    """
    @brief Deterministic provider stub returning OAuth failure with raw JSON body.
    @details Produces one failed result carrying `raw["body"]` JSON text with
    deliberate whitespace so debug logging can verify payload preservation.
    """

    name = ProviderName.CLAUDE

    async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult:
        """
        @brief Return deterministic OAuth failure with JSON body string payload.
        @param window {WindowPeriod} Requested usage window.
        @return {ProviderResult} Failed result with raw JSON body text.
        """
        return ProviderResult(
            provider=self.name,
            window=window,
            metrics=UsageMetrics(),
            raw={
                "status_code": 401,
                "body": '{"error":{"message":"token expired","code":"oauth_error"},"meta":[1, 2, 3]}',
            },
            error="OAuth access denied",
        )

    def is_configured(self) -> bool:
        """
        @brief Report deterministic configured state for OAuth raw-body stub provider.
        @return {bool} Always true.
        """
        return True

    def get_config_help(self) -> str:
        """
        @brief Return deterministic configuration help text.
        @return {str} Static helper text.
        """
        return "configured"


def test_logging_flag_options_persist_without_cross_side_effects(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify eager logging flags persist independently in runtime config.
    @details Executes `--enable-log`, `--enable-debug`, `--disable-log`, and
    `--disable-debug` in sequence; validates persisted booleans after each
    invocation and verifies no cross-flag mutation side effects.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-047
    """
    _patch_paths(monkeypatch, tmp_path)
    monkeypatch.setattr(cli_module, "_run_startup_update_preflight", lambda: None)
    config_module.save_runtime_config(
        RuntimeConfig(log_enabled=False, debug_enabled=False)
    )
    runner = CliRunner()

    assert runner.invoke(cli_module.main, ["--enable-log"]).exit_code == 0
    runtime_config = config_module.load_runtime_config()
    assert runtime_config.log_enabled is True
    assert runtime_config.debug_enabled is False

    assert runner.invoke(cli_module.main, ["--enable-debug"]).exit_code == 0
    runtime_config = config_module.load_runtime_config()
    assert runtime_config.log_enabled is True
    assert runtime_config.debug_enabled is True

    assert runner.invoke(cli_module.main, ["--disable-log"]).exit_code == 0
    runtime_config = config_module.load_runtime_config()
    assert runtime_config.log_enabled is False
    assert runtime_config.debug_enabled is True

    assert runner.invoke(cli_module.main, ["--disable-debug"]).exit_code == 0
    runtime_config = config_module.load_runtime_config()
    assert runtime_config.log_enabled is False
    assert runtime_config.debug_enabled is False


def test_execution_start_end_and_separator_logged_with_timestamp(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify execution-start/end rows and trailing separator logging behavior.
    @details Enables runtime logging, executes `aibar --help`, and asserts
    timestamped start/end rows plus one trailing empty separator line.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-048
    """
    _, cache_dir = _patch_paths(monkeypatch, tmp_path)
    monkeypatch.setattr(cli_module, "_run_startup_update_preflight", lambda: None)
    config_module.save_runtime_config(
        RuntimeConfig(log_enabled=True, debug_enabled=False)
    )
    runner = CliRunner()
    result = runner.invoke(cli_module.main, ["--help"])
    assert result.exit_code == 0

    log_text = _read_log(cache_dir)
    assert "execution.start stage=program_entry" in log_text
    assert (
        "execution.end outcome=click_exit_code=0" in log_text
        or "execution.end outcome=system_exit_code=0" in log_text
    )
    assert log_text.endswith("\n\n")
    first_line = log_text.splitlines()[0]
    assert re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} ", first_line) is not None


def test_pipeline_logging_covers_idle_fetch_error_and_cache_io(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify runtime log includes idle checks, call/error branches, and cache I/O.
    @details Executes shared retrieval pipeline with one success provider and one
    failing provider; asserts log rows for idle-time evaluation, provider call
    start/end and error handling, `cache.json` load/save, and pipeline outcome.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-048
    """
    _, cache_dir = _patch_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        RuntimeConfig(log_enabled=True, debug_enabled=False)
    )

    providers: dict[ProviderName, BaseProvider] = {
        ProviderName.CODEX: _SuccessProvider(),
        ProviderName.OPENROUTER: _ErrorProvider(),
    }
    output = cli_module.retrieve_results_via_cache_pipeline(
        provider_filter=None,
        target_window=WindowPeriod.DAY_7,
        force_refresh=False,
        providers=providers,
    )
    assert output.cache_available is True

    log_text = _read_log(cache_dir)
    assert "idle.pipeline.start" in log_text
    assert "idle.pipeline.check provider=codex blocked=false" in log_text
    assert "provider.fetch.start provider=codex window=7d" in log_text
    assert (
        "provider.fetch.error provider=openrouter window=30d error=provider boom"
        in log_text
    )
    assert "cache.load.start path=~/.cache/aibar/cache.json" in log_text
    assert "cache.save.start path=~/.cache/aibar/cache.json" in log_text
    assert "idle.pipeline.end cache_available=true source=refresh" in log_text


def test_debug_api_log_rows_require_both_log_and_debug_flags(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify API debug rows are emitted only when both flags are enabled.
    @details Executes refresh twice: first with debug disabled, then with debug
    enabled; asserts `provider.fetch.debug` rows are absent in first run and
    present in second run.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-049
    """
    _, cache_dir = _patch_paths(monkeypatch, tmp_path)
    providers: dict[ProviderName, BaseProvider] = {
        ProviderName.CODEX: _SuccessProvider()
    }

    config_module.save_runtime_config(
        RuntimeConfig(log_enabled=True, debug_enabled=False)
    )
    cli_module.retrieve_results_via_cache_pipeline(
        provider_filter=None,
        target_window=WindowPeriod.DAY_7,
        force_refresh=True,
        providers=providers,
    )
    log_without_debug = _read_log(cache_dir)
    assert "provider.fetch.debug" not in log_without_debug

    config_module.save_runtime_config(
        RuntimeConfig(log_enabled=True, debug_enabled=True)
    )
    cli_module.retrieve_results_via_cache_pipeline(
        provider_filter=None,
        target_window=WindowPeriod.DAY_7,
        force_refresh=True,
        providers=providers,
    )
    log_with_debug = _read_log(cache_dir)
    assert "provider.fetch.debug" in log_with_debug


def test_debug_api_log_rows_include_unmodified_error_json_payload(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify debug logging includes raw JSON error payload without mutation.
    @details Executes failed refresh twice using provider payload with `raw.body`
    JSON text; asserts no debug rows while debug flag is disabled, then asserts
    debug rows include `provider.fetch.debug.error_json` containing exact payload.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-049
    """
    _, cache_dir = _patch_paths(monkeypatch, tmp_path)
    raw_payload = (
        '{"error":{"message":"token expired","code":"oauth_error"},"meta":[1, 2, 3]}'
    )
    providers: dict[ProviderName, BaseProvider] = {
        ProviderName.CLAUDE: _OAuthErrorWithRawJsonBodyProvider(),
    }

    config_module.save_runtime_config(
        RuntimeConfig(log_enabled=True, debug_enabled=False)
    )
    cli_module.retrieve_results_via_cache_pipeline(
        provider_filter=None,
        target_window=WindowPeriod.DAY_7,
        force_refresh=True,
        providers=providers,
    )
    log_without_debug = _read_log(cache_dir)
    assert "provider.fetch.debug.error_json" not in log_without_debug

    config_module.save_runtime_config(
        RuntimeConfig(log_enabled=True, debug_enabled=True)
    )
    cli_module.retrieve_results_via_cache_pipeline(
        provider_filter=None,
        target_window=WindowPeriod.DAY_7,
        force_refresh=True,
        providers=providers,
    )
    log_with_debug = _read_log(cache_dir)
    assert "provider.fetch.debug.error_json provider=claude window=7d payload=" in log_with_debug
    assert f"payload={raw_payload}" in log_with_debug


def test_failure_logging_captures_oauth_and_rate_limit_with_retry_after(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify runtime log records oauth/rate_limit failure categories.
    @details Executes refresh with deterministic OAuth and HTTP-429 providers,
    then asserts runtime log rows contain category tokens and includes
    `retry_after_seconds` for rate-limit entries when available.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-050
    """
    _, cache_dir = _patch_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        RuntimeConfig(log_enabled=True, debug_enabled=False)
    )
    providers: dict[ProviderName, BaseProvider] = {
        ProviderName.OPENAI: _OAuthErrorProvider(),
        ProviderName.OPENROUTER: _RateLimitProvider(),
    }

    cli_module.retrieve_results_via_cache_pipeline(
        provider_filter=None,
        target_window=WindowPeriod.DAY_7,
        force_refresh=True,
        providers=providers,
    )

    log_text = _read_log(cache_dir)
    assert (
        "provider.fetch.failure provider=openai window=30d category=oauth" in log_text
    )
    assert (
        "provider.fetch.failure provider=openrouter window=30d category=rate_limit"
    ) in log_text
    assert "retry_after_seconds=45" in log_text


def test_failure_logging_records_retry_after_unavailable_evidence(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify oauth failure logs include explicit retry-after extraction evidence.
    @details Executes refresh with OAuth failure payload that omits retry-after keys
    and asserts runtime log row contains `retry_after_unavailable=true` plus
    extraction probe evidence fields.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-050
    """
    _, cache_dir = _patch_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        RuntimeConfig(log_enabled=True, debug_enabled=False)
    )
    providers: dict[ProviderName, BaseProvider] = {
        ProviderName.CLAUDE: _OAuthErrorNoRetryAfterProvider(),
    }

    cli_module.retrieve_results_via_cache_pipeline(
        provider_filter=None,
        target_window=WindowPeriod.DAY_7,
        force_refresh=True,
        providers=providers,
    )

    log_text = _read_log(cache_dir)
    assert (
        "provider.fetch.failure provider=claude window=7d category=oauth"
        in log_text
    )
    assert "retry_after_unavailable=true" in log_text
    assert "retry_after_source=probe_exhausted" in log_text
    assert '"raw.retry_after_seconds": null' in log_text


def test_claude_dual_window_failures_log_retry_after_and_unavailable_evidence(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify Claude dual-window fail results emit retry-after and unavailable evidence.
    @details Routes retrieval through Claude dual-window refresh branch and asserts
    runtime log contains one rate-limit row with `retry_after_seconds` plus one
    oauth row with `retry_after_unavailable=true` evidence payload.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-050
    """
    _, cache_dir = _patch_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        RuntimeConfig(log_enabled=True, debug_enabled=False)
    )
    claude_provider = ClaudeOAuthProvider(token="sk-ant-test-token")
    providers: dict[ProviderName, BaseProvider] = {
        ProviderName.CLAUDE: claude_provider,
    }
    claude_rate_limit = ProviderResult(
        provider=ProviderName.CLAUDE,
        window=WindowPeriod.HOUR_5,
        metrics=UsageMetrics(),
        raw={"status_code": 429, "retry_after_seconds": 180},
        error="Rate limited. Try again later.",
    )
    claude_oauth = ProviderResult(
        provider=ProviderName.CLAUDE,
        window=WindowPeriod.DAY_7,
        metrics=UsageMetrics(),
        raw={"status_code": 401, "oauth_marker": "missing_retry_after"},
        error="OAuth access denied",
    )
    monkeypatch.setattr(
        cli_module,
        "_fetch_claude_dual_with_auth_recovery",
        lambda provider, throttle_state=None: (claude_rate_limit, claude_oauth),
    )

    cli_module.retrieve_results_via_cache_pipeline(
        provider_filter=None,
        target_window=WindowPeriod.DAY_7,
        force_refresh=True,
        providers=providers,
    )

    log_text = _read_log(cache_dir)
    assert (
        "provider.fetch.failure provider=claude window=5h category=rate_limit"
        in log_text
    )
    assert "retry_after_seconds=180" in log_text
    assert "retry_after_source=raw.retry_after_seconds" in log_text
    assert (
        "provider.fetch.failure provider=claude window=7d category=oauth"
        in log_text
    )
    assert "retry_after_unavailable=true" in log_text
    assert "retry_after_source=probe_exhausted" in log_text


def test_show_lock_timeout_logs_and_exits_with_explicit_error(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify `show` logs lock timeout and exits non-zero with explicit diagnostic.
    @details Enables runtime logging, forces lock-file acquisition timeout for
    `cache.json`, executes `show --json`, and asserts stderr includes timeout
    diagnostic while runtime log contains `lock.acquire.timeout` row.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-066
    @satisfies REQ-112
    @satisfies TST-051
    """
    _, cache_dir = _patch_paths(monkeypatch, tmp_path)
    config_module.save_runtime_config(
        RuntimeConfig(log_enabled=True, debug_enabled=False)
    )
    monkeypatch.setattr(cli_module, "_run_startup_update_preflight", lambda: None)
    real_os_open = config_module.os.open

    def _always_locked_os_open(path, flags, mode=0o777):
        """
        @brief Raise FileExistsError for lock-file acquisition open operations.
        @details Simulates persistent lock contention while preserving default
        os.open behavior for non-lock paths and non-exclusive create operations.
        @param path {Any} Path argument received by `os.open`.
        @param flags {int} Open flags bitmask.
        @param mode {int} POSIX mode value for file creation.
        @return {int} File descriptor for delegated non-lock operations.
        @throws {FileExistsError} Always for lock-file `O_CREAT|O_EXCL|O_WRONLY`.
        """
        path_str = str(path)
        lock_acquire_flags = (
            config_module.os.O_CREAT | config_module.os.O_EXCL | config_module.os.O_WRONLY
        )
        if path_str.endswith(".lock") and flags == lock_acquire_flags:
            raise FileExistsError(path_str)
        return real_os_open(path, flags, mode)

    monkeypatch.setattr(config_module.os, "open", _always_locked_os_open)
    monkeypatch.setattr(config_module.time, "sleep", lambda _: None)
    monotonic_values = iter([0.0, 5.1])
    monkeypatch.setattr(config_module.time, "monotonic", lambda: next(monotonic_values))

    runner = CliRunner()
    result = runner.invoke(cli_module.main, ["show", "--json"])

    assert result.exit_code == 1
    assert "Lock acquisition timeout after 5 seconds" in result.output
    assert "~/.cache/aibar/" in result.output
    assert ".lock" in result.output
    log_text = _read_log(cache_dir)
    assert "lock.acquire.timeout target=~/.cache/aibar/" in log_text
