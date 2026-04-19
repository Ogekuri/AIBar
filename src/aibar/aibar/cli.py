"""
@file
@brief Command-line interface for aibar.
@details Defines command parsing, provider dispatch, formatted output, setup helpers, login flows, and UI launch hooks.
"""

import asyncio
import email.utils
import json
import math
import os
import platform
import re
import shutil
import subprocess
import sys
import textwrap
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import NoReturn, Sequence
from urllib import error as urllib_error
from urllib import request as urllib_request

import click
from click.core import ParameterSource
from pydantic import ValidationError

from . import __version__
from aibar.claude_cli_auth import extract_claude_cli_token
from aibar.config import (
    IdleTimeState,
    LockAcquisitionTimeoutError,
    RuntimeConfig,
    append_runtime_log_line,
    append_runtime_log_separator,
    build_idle_time_state,
    config,
    load_cli_cache,
    load_idle_time,
    load_runtime_config,
    remove_idle_time_file,
    resolve_enabled_providers,
    save_cli_cache,
    save_idle_time,
    save_runtime_config,
)
from aibar.providers import (
    ClaudeOAuthProvider,
    OpenAIUsageProvider,
    OpenRouterUsageProvider,
    CopilotProvider,
    CodexProvider,
    GeminiAIProvider,
)
from aibar.providers.base import (
    BaseProvider,
    ProviderError,
    ProviderName,
    ProviderResult,
    UsageMetrics,
    WindowPeriod,
)


_WINDOW_PERIOD_TIMEDELTA: dict[WindowPeriod, timedelta] = {
    WindowPeriod.HOUR_5: timedelta(hours=5),
    WindowPeriod.DAY_7: timedelta(days=7),
    WindowPeriod.DAY_30: timedelta(days=30),
}
_RESET_PENDING_MESSAGE = "Starts when the first message is sent"
_CACHE_PAYLOAD_SECTION_KEY = "payload"
_CACHE_STATUS_SECTION_KEY = "status"
_CACHE_IDLE_TIME_SECTION_KEY = "idle_time"
_CACHE_FRESHNESS_SECTION_KEY = "freshness"
_CACHE_EXTENSION_SECTION_KEY = "extension"
_CACHE_ENABLED_PROVIDERS_SECTION_KEY = "enabled_providers"
_ATTEMPT_RESULT_OK = "OK"
_ATTEMPT_RESULT_FAIL = "FAIL"
_SHOW_PANEL_MIN_WIDTH = 72
_SHOW_PANEL_MAX_WIDTH = 110
_ANSI_RESET = "\033[0m"
_ANSI_ESCAPE_SEQUENCE_PATTERN = re.compile(r"\x1b\[[0-9;]*m")
_ANSI_BOLD = "\033[1m"
_ANSI_BRIGHT_WHITE = "\033[97m"
_ANSI_BRIGHT_GREEN = "\033[92m"
_ANSI_BRIGHT_RED = "\033[91m"
_PROVIDER_PANEL_COLOR_CODES: dict[ProviderName, str] = {
    ProviderName.CLAUDE: "\033[91m",
    ProviderName.OPENROUTER: "\033[38;5;208m",
    ProviderName.COPILOT: "\033[93m",
    ProviderName.CODEX: "\033[92m",
    ProviderName.OPENAI: "\033[94m",
    ProviderName.GEMINIAI: "\033[95m",
}
_API_COUNTER_PROVIDERS: frozenset[ProviderName] = frozenset(
    {
        ProviderName.OPENAI,
        ProviderName.OPENROUTER,
        ProviderName.CODEX,
        ProviderName.GEMINIAI,
    }
)
_SHOW_PROVIDER_ORDER: tuple[ProviderName, ...] = (
    ProviderName.CLAUDE,
    ProviderName.OPENROUTER,
    ProviderName.COPILOT,
    ProviderName.CODEX,
    ProviderName.OPENAI,
    ProviderName.GEMINIAI,
)
_FIXED_WINDOW_BY_PROVIDER: dict[ProviderName, WindowPeriod] = {
    ProviderName.COPILOT: WindowPeriod.DAY_30,
    ProviderName.OPENROUTER: WindowPeriod.DAY_30,
    ProviderName.OPENAI: WindowPeriod.DAY_30,
    ProviderName.GEMINIAI: WindowPeriod.DAY_30,
}
_STARTUP_UPDATE_PROGRAM = "aibar"
_STARTUP_UPDATE_URL = "https://api.github.com/repos/Ogekuri/AIBar/releases/latest"
_STARTUP_IDLE_DELAY_SECONDS = 300
_STARTUP_HTTP_TIMEOUT_SECONDS = 2
_STARTUP_FORCE_IGNORE_IDLE_UNTIL_ACTIVE = False
_STARTUP_IDLE_STATE_LAST_SUCCESS_EPOCH_KEY = "last_success_at_epoch"
_STARTUP_IDLE_STATE_LAST_SUCCESS_HUMAN_KEY = "last_success_at_human"
_STARTUP_IDLE_STATE_IDLE_UNTIL_EPOCH_KEY = "idle_until_epoch"
_STARTUP_IDLE_STATE_IDLE_UNTIL_HUMAN_KEY = "idle_until_human"
_STARTUP_IDLE_STATE_FILENAME = "check_version_idle-time.json"
_EXT_UUID = "aibar@aibar.panel"
_EXT_TARGET_DIR = (
    Path.home() / ".local" / "share" / "gnome-shell" / "extensions" / _EXT_UUID
)
_UPGRADE_LIFECYCLE_COMMAND: list[str] = [
    "uv",
    "tool",
    "install",
    "aibar",
    "--force",
    "--from",
    "git+https://github.com/Ogekuri/AIBar.git",
]
_UNINSTALL_LIFECYCLE_COMMAND: list[str] = ["uv", "tool", "uninstall", "aibar"]
_CLAUDE_OAUTH_AUTH_ERROR_TEXT = "Invalid or expired OAuth token"
_CLAUDE_OAUTH_BLOCK_TTL_SECONDS = 86400
_LOG_FAILURE_CATEGORY_OAUTH = "oauth"
_LOG_FAILURE_CATEGORY_RATE_LIMIT = "rate_limit"
_CLAUDE_TOKEN_REFRESH_LOG_PATH = (
    Path.home() / ".config" / "aibar" / "claude_token_refresh.log"
)


@dataclass(frozen=True)
class RetrievalPipelineOutput:
    """
    @brief Define shared provider-retrieval pipeline output.
    @details Encodes deterministic retrieval state produced by the shared
    cache-based pipeline used by `show` and Text UI refresh execution.
    The pipeline enforces force-flag handling, idle-time gating, conditional
    refresh into `cache.json`, and deterministic payload projection for rendering.
    @note `payload` contains cache JSON sections: `payload` and `status`.
    @note `results` contains validated ProviderResult objects keyed by provider id.
    @note `idle_time_by_provider` contains provider-keyed idle-time freshness state.
    @note `idle_active` indicates provider-scoped idle-time gating blocked at
    least one selected provider refresh.
    @note `cache_available` indicates `cache.json` was readable for this run.
    @satisfies REQ-009
    @satisfies REQ-039
    @satisfies REQ-042
    @satisfies REQ-043
    @satisfies REQ-044
    @satisfies REQ-045
    @satisfies REQ-046
    @satisfies REQ-047
    """

    payload: dict[str, object]
    results: dict[str, ProviderResult]
    idle_time_by_provider: dict[str, IdleTimeState]
    idle_active: bool
    cache_available: bool


@dataclass(frozen=True)
class StartupReleaseCheckResponse:
    """
    @brief Represent one startup GitHub release-check execution result.
    @details Encodes normalized response state for startup preflight control-flow.
    `latest_version` is populated only on successful metadata retrieval.
    `status_code`, `error_message`, and `retry_after_seconds` carry normalized
    failure metadata used by 429 idle-time expansion and bright-red diagnostics.
    @note Immutable dataclass to keep preflight decisions deterministic.
    @satisfies REQ-070
    @satisfies REQ-073
    @satisfies REQ-074
    @satisfies REQ-075
    """

    latest_version: str | None
    status_code: int | None
    error_message: str | None
    retry_after_seconds: int


def _startup_idle_state_path() -> Path:
    """
    @brief Resolve startup update idle-state JSON path.
    @details Builds `~/.cache/aibar/check_version_idle-time.json` in user scope.
    @return {Path} Absolute path for startup idle-state persistence.
    @satisfies CTN-013
    """
    return Path.home() / ".cache" / "aibar" / _STARTUP_IDLE_STATE_FILENAME


def _startup_human_timestamp(epoch_seconds: int) -> str:
    """
    @brief Convert epoch seconds to UTC ISO-8601 timestamp text.
    @details Normalizes negative input to zero and emits timezone-aware UTC
    values so startup idle-state JSON remains machine-parseable and stable.
    @param epoch_seconds {int} Epoch timestamp in seconds.
    @return {str} UTC ISO-8601 timestamp string.
    @satisfies CTN-013
    """
    normalized_epoch = max(0, int(epoch_seconds))
    return datetime.fromtimestamp(normalized_epoch, tz=timezone.utc).isoformat()


def _startup_parse_int(value: object, default: int = 0) -> int:
    """
    @brief Parse integer-like values for startup idle-state normalization.
    @details Supports int, float, and numeric strings; invalid values return
    provided default. Parsed values are clamped to non-negative integers.
    @param value {object} Raw decoded value from JSON or headers.
    @param default {int} Fallback integer when parsing fails.
    @return {int} Non-negative parsed integer or fallback default.
    """
    if not isinstance(value, (int, float, str)):
        return max(0, default)
    try:
        parsed_value = int(float(value))
    except (TypeError, ValueError):
        return max(0, default)
    return max(0, parsed_value)


def _load_startup_idle_state() -> dict[str, object] | None:
    """
    @brief Load startup update idle-state JSON from disk.
    @details Reads `~/.cache/aibar/check_version_idle-time.json` and returns decoded JSON
    object when valid. Corrupt, missing, or unreadable files normalize to None.
    @return {dict[str, object] | None} Parsed idle-state mapping or None.
    @satisfies CTN-013
    """
    state_path = _startup_idle_state_path()
    if not state_path.exists():
        return None
    try:
        decoded = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if isinstance(decoded, dict):
        return decoded
    return None


def _startup_idle_epochs(state: dict[str, object] | None) -> tuple[int, int]:
    """
    @brief Extract normalized startup idle-state epoch timestamps.
    @details Reads `last_success_at_epoch` and `idle_until_epoch` from decoded
    state object and normalizes missing/invalid values to zero.
    @param state {dict[str, object] | None} Decoded startup idle-state mapping.
    @return {tuple[int, int]} Tuple `(last_success_epoch, idle_until_epoch)`.
    @satisfies CTN-013
    """
    if not isinstance(state, dict):
        return (0, 0)
    last_success_epoch = _startup_parse_int(
        state.get(_STARTUP_IDLE_STATE_LAST_SUCCESS_EPOCH_KEY),
        default=0,
    )
    idle_until_epoch = _startup_parse_int(
        state.get(_STARTUP_IDLE_STATE_IDLE_UNTIL_EPOCH_KEY),
        default=0,
    )
    return (last_success_epoch, idle_until_epoch)


def _save_startup_idle_state(last_success_epoch: int, idle_until_epoch: int) -> None:
    """
    @brief Persist startup update idle-state JSON.
    @details Writes epoch and UTC human-readable values for last successful
    startup release check and idle-disable-until timestamp to
    `~/.cache/aibar/check_version_idle-time.json`.
    @param last_success_epoch {int} Last successful startup check epoch.
    @param idle_until_epoch {int} Startup idle gate expiry epoch.
    @return {None} Function return value.
    @throws {OSError} Propagates filesystem write failures.
    @satisfies CTN-013
    @satisfies REQ-072
    """
    state_path = _startup_idle_state_path()
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_payload = {
        _STARTUP_IDLE_STATE_LAST_SUCCESS_EPOCH_KEY: max(0, int(last_success_epoch)),
        _STARTUP_IDLE_STATE_LAST_SUCCESS_HUMAN_KEY: _startup_human_timestamp(
            last_success_epoch
        ),
        _STARTUP_IDLE_STATE_IDLE_UNTIL_EPOCH_KEY: max(0, int(idle_until_epoch)),
        _STARTUP_IDLE_STATE_IDLE_UNTIL_HUMAN_KEY: _startup_human_timestamp(
            idle_until_epoch
        ),
    }
    state_path.write_text(
        json.dumps(state_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _cleanup_startup_idle_state_artifacts() -> int:
    """
    @brief Remove startup update idle-state artifacts for Linux uninstall.
    @details Deletes `~/.cache/aibar/check_version_idle-time.json` when present,
    then removes `~/.cache/aibar/` recursively when present. Emits bright-red
    diagnostics and returns non-zero on filesystem failures.
    @return {int} Zero on success; one when cleanup fails.
    @satisfies REQ-077
    """
    state_path = _startup_idle_state_path()
    startup_cache_dir = state_path.parent
    try:
        if state_path.exists():
            state_path.unlink()
        if startup_cache_dir.exists():
            shutil.rmtree(startup_cache_dir)
    except OSError as exc:
        _emit_startup_preflight_message(
            message=f"Uninstall cleanup failed: {exc}.",
            color_code=_ANSI_BRIGHT_RED,
            err=True,
        )
        return 1
    return 0


def _emit_startup_preflight_message(
    message: str, color_code: str, err: bool = False
) -> None:
    """
    @brief Emit colorized startup preflight diagnostics.
    @details Wraps message text with ANSI bright color escape sequences so update
    availability notices and failures are visually distinct in terminal output.
    @param message {str} Rendered diagnostic message text.
    @param color_code {str} ANSI SGR color escape prefix.
    @param err {bool} When true, write to stderr stream.
    @return {None} Function return value.
    @satisfies REQ-073
    @satisfies REQ-074
    """
    click.echo(f"{color_code}{message}{_ANSI_RESET}", err=err)


def _parse_retry_after_header(retry_after_raw: str | None) -> int:
    """
    @brief Parse HTTP Retry-After header to delay seconds.
    @details Supports integer-second values and HTTP-date formats. Date values
    are converted to seconds relative to current UTC time and clamped to zero.
    @param retry_after_raw {str | None} Retry-After header value.
    @return {int} Non-negative delay seconds.
    @satisfies REQ-075
    """
    if retry_after_raw is None:
        return 0
    try:
        return max(0, int(float(retry_after_raw)))
    except (TypeError, ValueError):
        pass
    try:
        retry_after_datetime = email.utils.parsedate_to_datetime(retry_after_raw)
    except (TypeError, ValueError):
        return 0
    retry_after_utc = _normalize_utc(retry_after_datetime)
    now_utc = datetime.now(tz=timezone.utc)
    delta_seconds = int((retry_after_utc - now_utc).total_seconds())
    return max(0, delta_seconds)


def _normalize_release_version(raw_version: object) -> str | None:
    """
    @brief Normalize release tag text extracted from GitHub API payload.
    @details Accepts string-like values, trims whitespace, and returns None for
    empty/invalid payload values.
    @param raw_version {object} Decoded `tag_name` value from release JSON.
    @return {str | None} Normalized release version string.
    @satisfies REQ-073
    """
    if not isinstance(raw_version, str):
        return None
    normalized = raw_version.strip()
    if not normalized:
        return None
    return normalized


def _fetch_startup_latest_release() -> StartupReleaseCheckResponse:
    """
    @brief Fetch latest GitHub release metadata for startup preflight.
    @details Executes one HTTP request to the canonical releases/latest endpoint
    with hardcoded timeout. Success returns normalized latest version tag.
    Failures return status/error metadata and parsed retry-after delay.
    @return {StartupReleaseCheckResponse} Normalized startup release-check result.
    @satisfies CTN-011
    @satisfies CTN-012
    @satisfies REQ-073
    @satisfies REQ-074
    @satisfies REQ-075
    """
    request = urllib_request.Request(
        _STARTUP_UPDATE_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"{_STARTUP_UPDATE_PROGRAM}/{__version__}",
        },
    )
    try:
        with urllib_request.urlopen(
            request, timeout=_STARTUP_HTTP_TIMEOUT_SECONDS
        ) as response:
            decoded_payload = json.loads(response.read().decode("utf-8"))
    except urllib_error.HTTPError as exc:
        retry_after_seconds = _parse_retry_after_header(exc.headers.get("Retry-After"))
        return StartupReleaseCheckResponse(
            latest_version=None,
            status_code=exc.code,
            error_message=f"Startup update check failed: HTTP {exc.code} {exc.reason}.",
            retry_after_seconds=retry_after_seconds,
        )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
        return StartupReleaseCheckResponse(
            latest_version=None,
            status_code=None,
            error_message=f"Startup update check failed: {exc}.",
            retry_after_seconds=0,
        )

    latest_version = _normalize_release_version(decoded_payload.get("tag_name"))
    if latest_version is None:
        return StartupReleaseCheckResponse(
            latest_version=None,
            status_code=200,
            error_message="Startup update check failed: invalid release metadata payload.",
            retry_after_seconds=0,
        )
    return StartupReleaseCheckResponse(
        latest_version=latest_version,
        status_code=200,
        error_message=None,
        retry_after_seconds=0,
    )


def _parse_version_triplet(version_text: str) -> tuple[int, int, int] | None:
    """
    @brief Parse semantic version tuple from version text.
    @details Accepts optional `v` prefix and optional suffix metadata. Returns
    first `major.minor.patch` triplet or None when parsing fails.
    @param version_text {str} Raw version string.
    @return {tuple[int, int, int] | None} Parsed semantic version tuple.
    @satisfies REQ-073
    """
    match = re.match(r"^v?(\d+)\.(\d+)\.(\d+)", version_text.strip())
    if match is None:
        return None
    return (
        int(match.group(1)),
        int(match.group(2)),
        int(match.group(3)),
    )


def _is_newer_release(installed_version: str, latest_version: str) -> bool:
    """
    @brief Compare installed and latest release semantic versions.
    @details Uses normalized `major.minor.patch` tuples. Invalid version formats
    disable upgrade notice emission to avoid false positives.
    @param installed_version {str} Installed program version text.
    @param latest_version {str} Latest release version text.
    @return {bool} True when latest release is newer than installed version.
    @satisfies REQ-073
    """
    installed_triplet = _parse_version_triplet(installed_version)
    latest_triplet = _parse_version_triplet(latest_version)
    if installed_triplet is None or latest_triplet is None:
        return False
    return latest_triplet > installed_triplet


def _run_startup_update_preflight() -> None:
    """
    @brief Execute startup update-check preflight with optional idle-time bypass.
    @details Evaluates startup idle-state file; skips HTTP calls while idle is
    active; performs latest-release fetch when idle expires or file is missing;
    prints bright-green update notice for newer releases; prints bright-red error
    diagnostics on failures; updates idle-state after success and HTTP 429.
    @return {None} Function return value.
    @satisfies CTN-013
    @satisfies CTN-014
    @satisfies REQ-070
    @satisfies REQ-071
    @satisfies REQ-072
    @satisfies REQ-073
    @satisfies REQ-074
    @satisfies REQ-075
    @satisfies REQ-112
    """
    now_epoch = int(time.time())
    state = _load_startup_idle_state()
    last_success_epoch, idle_until_epoch = _startup_idle_epochs(state)
    append_runtime_log_line(
        "idle.startup.check "
        f"now_epoch={now_epoch} idle_until_epoch={idle_until_epoch} "
        f"last_success_epoch={last_success_epoch}"
    )
    if now_epoch < idle_until_epoch and not _STARTUP_FORCE_IGNORE_IDLE_UNTIL_ACTIVE:
        append_runtime_log_line("idle.startup.skip reason=idle_active")
        return

    append_runtime_log_line("startup.update.fetch.start")
    response = _fetch_startup_latest_release()
    append_runtime_log_line(
        "startup.update.fetch.end "
        f"status_code={response.status_code} "
        f"has_error={response.error_message is not None} "
        f"retry_after_seconds={response.retry_after_seconds}"
    )
    if response.error_message is None and response.latest_version is not None:
        if _is_newer_release(__version__, response.latest_version):
            _emit_startup_preflight_message(
                message=(
                    "New version available: "
                    f"installed {__version__}, latest {response.latest_version}."
                ),
                color_code=_ANSI_BRIGHT_GREEN,
            )
        try:
            _save_startup_idle_state(
                last_success_epoch=now_epoch,
                idle_until_epoch=now_epoch + _STARTUP_IDLE_DELAY_SECONDS,
            )
        except OSError as exc:
            _emit_startup_preflight_message(
                message=f"Startup update check failed: unable to persist idle state ({exc}).",
                color_code=_ANSI_BRIGHT_RED,
                err=True,
            )
        return

    if response.status_code == 429:
        retry_after_seconds = max(
            _STARTUP_IDLE_DELAY_SECONDS, response.retry_after_seconds
        )
        idle_until_epoch = max(idle_until_epoch, now_epoch + retry_after_seconds)
        try:
            _save_startup_idle_state(
                last_success_epoch=last_success_epoch,
                idle_until_epoch=idle_until_epoch,
            )
        except OSError as exc:
            _emit_startup_preflight_message(
                message=f"Startup update check failed: unable to persist idle state ({exc}).",
                color_code=_ANSI_BRIGHT_RED,
                err=True,
            )
    if response.error_message is not None:
        _emit_startup_preflight_message(
            message=response.error_message,
            color_code=_ANSI_BRIGHT_RED,
            err=True,
        )


def _startup_force_ignore_idle_from_args(args: Sequence[str] | None) -> bool:
    """
    @brief Detect whether startup preflight must bypass idle gating from argv.
    @details Returns true when invocation arguments contain `--version` or
    `--ver`, forcing one online startup release check regardless of persisted
    startup idle-time file state.
    @param args {Sequence[str] | None} CLI argv sequence excluding executable
        name when provided by Click group main.
    @return {bool} True when startup preflight must bypass idle-time gating.
    @satisfies REQ-071
    @satisfies REQ-078
    """
    argument_tokens = list(args) if args is not None else list(sys.argv[1:])
    return any(
        token in {"--version", "--ver"}
        for token in argument_tokens
        if isinstance(token, str)
    )


def _execute_lifecycle_subprocess(command: list[str]) -> int:
    """
    @brief Execute lifecycle subprocess command for upgrade/uninstall options.
    @details Runs provided command via `subprocess.run` and returns subprocess
    exit code. Command execution failures return non-zero status with red error.
    @param command {list[str]} Lifecycle command argv.
    @return {int} Subprocess exit code.
    @satisfies CTN-015
    @satisfies REQ-076
    @satisfies REQ-077
    """
    try:
        completed = subprocess.run(command, check=False)
    except OSError as exc:
        _emit_startup_preflight_message(
            message=f"Lifecycle command failed: {exc}.",
            color_code=_ANSI_BRIGHT_RED,
            err=True,
        )
        return 1
    return int(completed.returncode)


def _is_linux_runtime() -> bool:
    """
    @brief Determine whether lifecycle subprocess execution is allowed.
    @details Returns true only for Linux runtimes. Lifecycle subprocesses for
    `--upgrade` and `--uninstall` are Linux-only and must be skipped elsewhere.
    @return {bool} True when current runtime platform is Linux.
    @satisfies REQ-076
    @satisfies REQ-077
    @satisfies REQ-088
    """
    return sys.platform.startswith("linux")


def _emit_non_linux_lifecycle_guidance(option_name: str, command: Sequence[str]) -> int:
    """
    @brief Emit manual lifecycle command guidance for non-Linux platforms.
    @details Builds one deterministic warning message containing detected
    operating-system label and exact manual command text, then emits it through
    startup preflight styled diagnostics with stderr routing.
    @param option_name {str} Lifecycle option token (`--upgrade` or `--uninstall`).
    @param command {Sequence[str]} Lifecycle command argv to present as manual guidance.
    @return {int} Deterministic non-zero exit code indicating command was not executed.
    @satisfies CTN-015
    @satisfies REQ-088
    @satisfies REQ-089
    """
    detected_platform = platform.system() or sys.platform
    manual_command = " ".join(command)
    _emit_startup_preflight_message(
        message=(
            f"{option_name} is supported only on Linux. "
            f"Detected OS: {detected_platform}. "
            f"Run manually: {manual_command}"
        ),
        color_code=_ANSI_BRIGHT_RED,
        err=True,
    )
    return 1


def _handle_upgrade_option(
    ctx: click.Context, param: click.Parameter, value: bool
) -> None:
    """
    @brief Handle eager `--upgrade` lifecycle option callback.
    @details Executes required lifecycle subprocess on Linux and exits with
    propagated subprocess code; on non-Linux emits manual command guidance and
    exits without subprocess execution.
    @param ctx {click.Context} Active Click context.
    @param param {click.Parameter} Option metadata (unused).
    @param value {bool} Parsed `--upgrade` flag value.
    @return {None} Function return value.
    @satisfies CTN-015
    @satisfies REQ-076
    @satisfies REQ-088
    @satisfies REQ-089
    """
    del param
    if not value or ctx.resilient_parsing:
        return
    if _is_linux_runtime():
        exit_code = _execute_lifecycle_subprocess(_UPGRADE_LIFECYCLE_COMMAND)
    else:
        exit_code = _emit_non_linux_lifecycle_guidance(
            option_name="--upgrade",
            command=_UPGRADE_LIFECYCLE_COMMAND,
        )
    ctx.exit(exit_code)


def _handle_uninstall_option(
    ctx: click.Context, param: click.Parameter, value: bool
) -> None:
    """
    @brief Handle eager `--uninstall` lifecycle option callback.
    @details Executes required lifecycle subprocess on Linux, cleans startup
    idle-state artifacts under `~/.cache/aibar/`, and exits with propagated
    subprocess code unless cleanup fails after successful subprocess execution.
    On non-Linux emits manual command guidance and exits without subprocess execution.
    @param ctx {click.Context} Active Click context.
    @param param {click.Parameter} Option metadata (unused).
    @param value {bool} Parsed `--uninstall` flag value.
    @return {None} Function return value.
    @satisfies CTN-015
    @satisfies REQ-077
    @satisfies REQ-088
    @satisfies REQ-089
    """
    del param
    if not value or ctx.resilient_parsing:
        return
    if _is_linux_runtime():
        exit_code = _execute_lifecycle_subprocess(_UNINSTALL_LIFECYCLE_COMMAND)
        cleanup_exit_code = _cleanup_startup_idle_state_artifacts()
        if exit_code == 0 and cleanup_exit_code != 0:
            exit_code = cleanup_exit_code
    else:
        exit_code = _emit_non_linux_lifecycle_guidance(
            option_name="--uninstall",
            command=_UNINSTALL_LIFECYCLE_COMMAND,
        )
    ctx.exit(exit_code)


def _handle_version_option(
    ctx: click.Context, param: click.Parameter, value: bool
) -> None:
    """
    @brief Handle eager `--version` and `--ver` option callback.
    @details Prints installed package version and exits before command dispatch
    when either version flag is present.
    @param ctx {click.Context} Active Click context.
    @param param {click.Parameter} Option metadata (unused).
    @param value {bool} Parsed version-option flag value.
    @return {None} Function return value.
    @satisfies REQ-078
    """
    del param
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__)
    ctx.exit(0)


def _update_runtime_logging_flags(
    *,
    log_enabled: bool | None = None,
    debug_enabled: bool | None = None,
) -> None:
    """
    @brief Persist runtime logging-flag updates into runtime config.
    @details Loads current `RuntimeConfig`, applies provided logging-flag
    overrides, writes updated config to disk, and emits one configuration log
    entry when execution logging is enabled after update.
    @param log_enabled {bool | None} Optional replacement for `log_enabled`.
    @param debug_enabled {bool | None} Optional replacement for `debug_enabled`.
    @return {None} Function return value.
    @satisfies REQ-107
    @satisfies REQ-109
    @satisfies REQ-110
    """
    update_payload: dict[str, object] = {}
    if log_enabled is not None:
        update_payload["log_enabled"] = bool(log_enabled)
    if debug_enabled is not None:
        update_payload["debug_enabled"] = bool(debug_enabled)
    if not update_payload:
        return
    updated_runtime_config = load_runtime_config().model_copy(update=update_payload)
    save_runtime_config(updated_runtime_config)
    append_runtime_log_line(
        "config.logging.update "
        f"log_enabled={updated_runtime_config.log_enabled} "
        f"debug_enabled={updated_runtime_config.debug_enabled}"
    )


def _handle_enable_log_option(
    ctx: click.Context, param: click.Parameter, value: bool
) -> None:
    """
    @brief Enable runtime execution logging via eager CLI option.
    @details Sets `RuntimeConfig.log_enabled` to true without mutating
    `RuntimeConfig.debug_enabled`, then exits before command dispatch.
    @param ctx {click.Context} Active Click context.
    @param param {click.Parameter} Option metadata (unused).
    @param value {bool} Parsed `--enable-log` flag value.
    @return {None} Function return value.
    @satisfies REQ-107
    @satisfies REQ-109
    """
    del param
    if not value or ctx.resilient_parsing:
        return
    _update_runtime_logging_flags(log_enabled=True)
    ctx.exit(0)


def _handle_disable_log_option(
    ctx: click.Context, param: click.Parameter, value: bool
) -> None:
    """
    @brief Disable runtime execution logging via eager CLI option.
    @details Sets `RuntimeConfig.log_enabled` to false without mutating
    `RuntimeConfig.debug_enabled`, then exits before command dispatch.
    @param ctx {click.Context} Active Click context.
    @param param {click.Parameter} Option metadata (unused).
    @param value {bool} Parsed `--disable-log` flag value.
    @return {None} Function return value.
    @satisfies REQ-107
    @satisfies REQ-109
    """
    del param
    if not value or ctx.resilient_parsing:
        return
    _update_runtime_logging_flags(log_enabled=False)
    ctx.exit(0)


def _handle_enable_debug_option(
    ctx: click.Context, param: click.Parameter, value: bool
) -> None:
    """
    @brief Enable runtime API debug logging via eager CLI option.
    @details Sets `RuntimeConfig.debug_enabled` to true without mutating
    `RuntimeConfig.log_enabled`, then exits before command dispatch.
    @param ctx {click.Context} Active Click context.
    @param param {click.Parameter} Option metadata (unused).
    @param value {bool} Parsed `--enable-debug` flag value.
    @return {None} Function return value.
    @satisfies REQ-107
    @satisfies REQ-110
    """
    del param
    if not value or ctx.resilient_parsing:
        return
    _update_runtime_logging_flags(debug_enabled=True)
    ctx.exit(0)


def _handle_disable_debug_option(
    ctx: click.Context, param: click.Parameter, value: bool
) -> None:
    """
    @brief Disable runtime API debug logging via eager CLI option.
    @details Sets `RuntimeConfig.debug_enabled` to false without mutating
    `RuntimeConfig.log_enabled`, then exits before command dispatch.
    @param ctx {click.Context} Active Click context.
    @param param {click.Parameter} Option metadata (unused).
    @param value {bool} Parsed `--disable-debug` flag value.
    @return {None} Function return value.
    @satisfies REQ-107
    @satisfies REQ-110
    """
    del param
    if not value or ctx.resilient_parsing:
        return
    _update_runtime_logging_flags(debug_enabled=False)
    ctx.exit(0)


class StartupPreflightGroup(click.Group):
    """
    @brief Click group subclass that enforces startup preflight ordering and preserves epilog formatting.
    @details Executes startup update-check preflight before Click argument
    parsing and command dispatch. This guarantees preflight execution even when
    invocation later fails due to invalid arguments. Overrides epilog rendering
    to preserve multi-line example formatting without text wrapping.
    @satisfies REQ-070, REQ-068
    """

    def format_epilog(
        self,
        ctx: click.Context,
        formatter: click.HelpFormatter,
    ) -> None:
        """
        @brief Render epilog text preserving explicit line breaks.
        @details Writes each epilog line verbatim to the help formatter,
        bypassing Click's default text-wrapping behavior that collapses
        multi-line examples into a single paragraph.
        @param ctx {click.Context} Click invocation context.
        @param formatter {click.HelpFormatter} Help output formatter instance.
        @return {None} Function return value.
        @satisfies REQ-068
        """
        if self.epilog:
            formatter.write("\n")
            for line in self.epilog.split("\n"):
                formatter.write(f"  {line}\n")

    def main(
        self,
        args: Sequence[str] | None = None,
        prog_name: str | None = None,
        complete_var: str | None = None,
        standalone_mode: bool = True,
        windows_expand_args: bool = True,
        **extra: object,
    ) -> NoReturn:
        """
        @brief Execute startup preflight before Click main dispatch.
        @details Appends execution-start log entry, runs update-check preflight,
        delegates to Click parser/dispatcher, and appends execution-end outcome
        plus one trailing separator line when runtime logging is enabled.
        The preflight bypasses startup idle gating when invocation includes
        eager `--version` or `--ver` options.
        @param args {Sequence[str] | None} Optional argv sequence.
        @param prog_name {str | None} Program display name override.
        @param complete_var {str | None} Shell-completion environment variable.
        @param standalone_mode {bool} Click standalone execution mode flag.
        @param windows_expand_args {bool} Windows argument expansion flag.
        @param extra {object} Additional keyword arguments forwarded to Click.
        @return {NoReturn} Click main dispatcher return contract.
        @satisfies REQ-070
        @satisfies REQ-111
        @satisfies REQ-113
        """
        execution_outcome = "unknown"
        append_runtime_log_line("execution.start stage=program_entry")
        try:
            force_ignore_idle_until = _startup_force_ignore_idle_from_args(args)
            global _STARTUP_FORCE_IGNORE_IDLE_UNTIL_ACTIVE
            previous_force_ignore_idle_until = _STARTUP_FORCE_IGNORE_IDLE_UNTIL_ACTIVE
            _STARTUP_FORCE_IGNORE_IDLE_UNTIL_ACTIVE = force_ignore_idle_until
            try:
                _run_startup_update_preflight()
            finally:
                _STARTUP_FORCE_IGNORE_IDLE_UNTIL_ACTIVE = (
                    previous_force_ignore_idle_until
                )
            super().main(
                args=args,
                prog_name=prog_name,
                complete_var=complete_var,
                standalone_mode=standalone_mode,
                windows_expand_args=windows_expand_args,
                **extra,
            )
            execution_outcome = "unexpected_return"
            raise RuntimeError("Click main returned unexpectedly.")
        except click.exceptions.Exit as exc:
            execution_outcome = f"click_exit_code={int(exc.exit_code)}"
            raise
        except SystemExit as exc:
            execution_outcome = f"system_exit_code={exc.code}"
            raise
        except BaseException as exc:  # noqa: BLE001
            execution_outcome = (
                f"exception_type={type(exc).__name__} exception_message={exc}"
            )
            raise
        finally:
            append_runtime_log_line(f"execution.end outcome={execution_outcome}")
            append_runtime_log_separator()


def _normalize_utc(value: datetime) -> datetime:
    """
    @brief Normalize datetime values to timezone-aware UTC instances.
    @details Ensures consistent timestamp arithmetic for idle-time persistence and
    refresh-delay computations when source datetimes are naive or non-UTC.
    @param value {datetime} Source datetime to normalize.
    @return {datetime} Timezone-aware UTC datetime.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _format_local_datetime(value: datetime) -> str:
    """
    @brief Format one datetime in local timezone with `%Y-%m-%d %H:%M`.
    @details Normalizes source datetime to UTC, projects it to runtime local
    timezone, and emits minute-precision text for CLI freshness labels.
    @param value {datetime} Source datetime to format.
    @return {str} Local timezone datetime string.
    @satisfies REQ-084
    """
    local_datetime = _normalize_utc(value).astimezone()
    return local_datetime.strftime("%Y-%m-%d %H:%M")


def _epoch_to_utc_datetime(epoch_seconds: int) -> datetime:
    """
    @brief Convert epoch-seconds to timezone-aware UTC datetime.
    @param epoch_seconds {int} Epoch timestamp in seconds.
    @return {datetime} UTC datetime from epoch.
    """
    return datetime.fromtimestamp(int(epoch_seconds), tz=timezone.utc)


def _build_freshness_line(
    result: ProviderResult,
    freshness_state: IdleTimeState | None,
) -> str:
    """
    @brief Build `Updated/Next` freshness line for CLI panel rendering.
    @details Uses provider idle-time state when available (`last_success_timestamp`,
    `idle_until_timestamp`) and falls back to payload `updated_at` plus runtime
    interval fallback (`60s`) when idle-time state is unavailable.
    @param result {ProviderResult} Provider result carrying fallback `updated_at`.
    @param freshness_state {IdleTimeState | None} Provider idle-time state.
    @return {str} Deterministic `Updated: ..., Next: ...` label.
    @satisfies REQ-084
    """
    if freshness_state is not None:
        updated_at_utc = _epoch_to_utc_datetime(freshness_state.last_success_timestamp)
        next_update_utc = _epoch_to_utc_datetime(freshness_state.idle_until_timestamp)
    else:
        updated_at_utc = _normalize_utc(result.updated_at)
        next_update_utc = updated_at_utc + timedelta(seconds=60)
    return (
        "Updated: "
        f"{_format_local_datetime(updated_at_utc)}, "
        f"Next: {_format_local_datetime(next_update_utc)}"
    )


def _apply_api_call_delay(throttle_state: dict[str, float | int] | None) -> None:
    """
    @brief Enforce minimum spacing between consecutive provider API calls.
    @details Uses monotonic clock values in `throttle_state` to sleep before a live
    API request when elapsed time is below configured delay.
    @param throttle_state {dict[str, float | int] | None} Mutable state containing
        `delay_milliseconds` and `last_call_started`.
    @return {None} Function return value.
    @satisfies REQ-040
    """
    if throttle_state is None:
        return

    delay_milliseconds_raw = throttle_state.get("delay_milliseconds", 0)
    try:
        delay_milliseconds = max(0.0, float(delay_milliseconds_raw))
    except (TypeError, ValueError):
        delay_milliseconds = 0.0
    delay_seconds = delay_milliseconds / 1000.0

    last_call_raw = throttle_state.get("last_call_started")
    now = time.monotonic()
    if isinstance(last_call_raw, (int, float)) and delay_seconds > 0:
        elapsed = now - float(last_call_raw)
        remaining = delay_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)
    throttle_state["last_call_started"] = time.monotonic()


def _coerce_retry_after_seconds(value: object) -> int | None:
    """
    @brief Normalize retry-after metadata to positive integer seconds.
    @details Accepts integer/float/string payload values and converts them to
    normalized relative-delay seconds. When numeric values represent absolute
    epoch timestamps (seconds or milliseconds), converts them to `max(0, epoch-now)`.
    Non-numeric, invalid, and non-positive values return None.
    @param value {object} Retry-after candidate value.
    @return {int | None} Positive retry-after seconds or None when unavailable.
    @satisfies REQ-037
    @satisfies REQ-041
    """
    if not isinstance(value, (int, float, str)):
        return None
    try:
        parsed = int(float(value))
    except (TypeError, ValueError):
        return None
    if parsed <= 0:
        return None

    now_epoch = int(time.time())
    if parsed >= 1_000_000_000_000:
        parsed = parsed // 1000
    if parsed >= 1_000_000_000:
        parsed = parsed - now_epoch

    if parsed <= 0:
        return None
    return parsed


def _extract_retry_after_seconds(result: ProviderResult) -> int:
    """
    @brief Extract normalized retry-after seconds from provider error payload.
    @details Reads `raw.retry_after_seconds` and clamps to non-negative integer
    seconds. When unavailable and payload marks
    `raw.retry_after_unavailable=true`, returns `RuntimeConfig.default_retry_after_seconds`.
    Invalid or missing values without fallback marker normalize to zero.
    @param result {ProviderResult} Provider result to inspect.
    @return {int} Non-negative retry-after delay in seconds.
    @satisfies REQ-041
    """
    parsed = _coerce_retry_after_seconds(result.raw.get("retry_after_seconds"))
    if parsed is not None:
        return parsed
    retry_after_unavailable = result.raw.get("retry_after_unavailable")
    if retry_after_unavailable is True:
        runtime_config = load_runtime_config()
        return max(0, int(runtime_config.default_retry_after_seconds))
    return 0


def _classify_provider_failure_log_category(result: ProviderResult) -> str | None:
    """
    @brief Classify provider failure category for runtime logging.
    @details Maps failed provider results to runtime-log categories used by
    logging requirement checks. Returns `rate_limit` when `raw.status_code` is
    `429`; returns `oauth` when error text contains OAuth-authentication markers.
    @param result {ProviderResult} Provider result candidate.
    @return {str | None} Failure category token or None when not log-targeted.
    @satisfies REQ-115
    """
    if not result.is_error:
        return None
    if _is_http_429_result(result):
        return _LOG_FAILURE_CATEGORY_RATE_LIMIT
    if _is_claude_oauth_authentication_error(result.error):
        return _LOG_FAILURE_CATEGORY_OAUTH
    if isinstance(result.error, str) and "oauth" in result.error.lower():
        return _LOG_FAILURE_CATEGORY_OAUTH
    return None


def _append_provider_failure_runtime_log(result: ProviderResult) -> None:
    """
    @brief Append runtime-log row for OAuth and rate-limit provider failures.
    @details Emits non-debug runtime-log entries for provider failure categories
    `oauth` and `rate_limit` when logging is enabled. Includes
    `retry_after_seconds` plus extraction source when available; when unavailable,
    appends explicit `retry_after_unavailable=true` evidence payload.
    @param result {ProviderResult} Provider result to log.
    @return {None} Function return value.
    @satisfies REQ-115
    """
    category = _classify_provider_failure_log_category(result)
    if category is None:
        return
    error_message = result.error if isinstance(result.error, str) else "Unknown error"
    log_line = (
        "provider.fetch.failure "
        f"provider={result.provider.value} "
        f"window={result.window.value} "
        f"category={category} "
        f"error={json.dumps(error_message, ensure_ascii=True)}"
    )
    retry_after_seconds, retry_after_source = _extract_retry_after_for_failure_log(result)
    if retry_after_seconds is not None:
        log_line = (
            f"{log_line} retry_after_seconds={retry_after_seconds} "
            f"retry_after_source={retry_after_source}"
        )
    else:
        log_line = (
            f"{log_line} retry_after_unavailable=true "
            f"retry_after_source={retry_after_source} "
            "retry_after_probe="
            f"{json.dumps(_retry_after_probe_payload(result.raw), ensure_ascii=True)}"
        )
    append_runtime_log_line(log_line)


def _extract_retry_after_for_failure_log(result: ProviderResult) -> tuple[int | None, str]:
    """
    @brief Extract retry-after seconds and source path for failure runtime logs.
    @details Probes normalized and fallback raw payload fields in deterministic order:
    `raw.retry_after_seconds`, `raw.retry_after`, `raw.error.retry_after_seconds`,
    and `raw.error.retry_after`. Returns first positive parsed value.
    @param result {ProviderResult} Provider result to inspect.
    @return {tuple[int | None, str]} Tuple `(retry_after_seconds_or_none, source_key)`.
    @satisfies REQ-115
    """
    candidates: list[tuple[str, object]] = [
        ("raw.retry_after_seconds", result.raw.get("retry_after_seconds")),
        ("raw.retry_after", result.raw.get("retry_after")),
    ]
    error_payload = result.raw.get("error")
    if isinstance(error_payload, dict):
        candidates.extend(
            [
                (
                    "raw.error.retry_after_seconds",
                    error_payload.get("retry_after_seconds"),
                ),
                ("raw.error.retry_after", error_payload.get("retry_after")),
            ]
        )
    for source_key, candidate in candidates:
        parsed = _coerce_retry_after_seconds(candidate)
        if parsed is not None:
            return (parsed, source_key)
    return (None, "probe_exhausted")


def _retry_after_probe_payload(raw_payload: dict[str, object]) -> dict[str, object]:
    """
    @brief Build compact retry-after probe evidence for failure runtime logs.
    @details Serializes inspected retry-after fields and top-level key inventory so
    logs provide explicit evidence when retry-after extraction fails.
    @param raw_payload {dict[str, object]} Provider raw payload dictionary.
    @return {dict[str, object]} JSON-safe probe payload.
    @satisfies REQ-115
    """
    error_payload = raw_payload.get("error")
    error_retry_after_seconds: object = None
    error_retry_after: object = None
    if isinstance(error_payload, dict):
        error_retry_after_seconds = error_payload.get("retry_after_seconds")
        error_retry_after = error_payload.get("retry_after")
    return {
        "raw_keys": sorted(raw_payload.keys()),
        "raw.retry_after_seconds": raw_payload.get("retry_after_seconds"),
        "raw.retry_after": raw_payload.get("retry_after"),
        "raw.error.retry_after_seconds": error_retry_after_seconds,
        "raw.error.retry_after": error_retry_after,
    }


def _is_claude_oauth_authentication_error(message: object) -> bool:
    """
    @brief Detect canonical Claude OAuth authentication-expired error text.
    @details Applies strict substring match against `Invalid or expired OAuth token`
    using case-sensitive semantics so retry/renewal logic is only enabled for the
    documented Claude token-expiration failure.
    @param message {object} Candidate error message object.
    @return {bool} True when candidate contains canonical Claude auth-expired text.
    @satisfies REQ-102
    """
    return isinstance(message, str) and _CLAUDE_OAUTH_AUTH_ERROR_TEXT in message


def _subprocess_return_code_from_exception(exc: Exception) -> int:
    """
    @brief Normalize subprocess exception to deterministic integer return code.
    @details Maps TimeoutExpired to `124`, CalledProcessError to its integer
    return code when available, and all other exception classes to `1`.
    @param exc {Exception} Subprocess exception emitted by `subprocess.run`.
    @return {int} Deterministic synthetic return code.
    """
    if isinstance(exc, subprocess.TimeoutExpired):
        return 124
    if isinstance(exc, subprocess.CalledProcessError):
        try:
            return int(exc.returncode)
        except (TypeError, ValueError):
            return 1
    return 1


def _execute_claude_refresh_command(
    command: list[str],
    timeout_seconds: float,
) -> tuple[bool, int, str]:
    """
    @brief Execute one Claude token-refresh subprocess command.
    @details Runs command without shell expansion, captures combined stdout/stderr,
    and enforces timeout using runtime `api_call_timeout_milliseconds` policy.
    Command-not-found and timeout failures are converted to deterministic error
    tuples without raising.
    @param command {list[str]} Subprocess argv tokens.
    @param timeout_seconds {float} Timeout in seconds for command completion.
    @return {tuple[bool, int, str]} Tuple `(success, return_code, output_text)`.
    @satisfies REQ-101
    """
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return (False, _subprocess_return_code_from_exception(exc), str(exc))

    merged_output = "\n".join(
        part for part in (completed.stdout, completed.stderr) if part
    ).strip()
    return (completed.returncode == 0, int(completed.returncode), merged_output)


def _run_claude_oauth_token_refresh(runtime_config: RuntimeConfig) -> bool:
    """
    @brief Execute one Claude OAuth token-renewal routine in-process.
    @details Truncates `~/.config/aibar/claude_token_refresh.log`, then executes
    `claude /usage` followed by `aibar login --provider claude` when each command
    is available in PATH. Applies configured API-call delay spacing and configured
    API-call timeout to each subprocess call. Command failures are logged and do
    not raise; function returns true only when both available commands complete
    successfully.
    @param runtime_config {RuntimeConfig} Runtime delay and timeout configuration.
    @return {bool} True when refresh routine completes without command failures.
    @satisfies REQ-100
    @satisfies REQ-101
    """
    _CLAUDE_TOKEN_REFRESH_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CLAUDE_TOKEN_REFRESH_LOG_PATH.write_text("", encoding="utf-8")
    timeout_seconds = max(0.001, runtime_config.api_call_timeout_milliseconds / 1000.0)
    throttle_state: dict[str, float | int] = {
        "delay_milliseconds": runtime_config.api_call_delay_milliseconds,
    }
    command_plan: tuple[tuple[str, list[str]], ...] = (
        ("claude", ["claude", "/usage"]),
        ("aibar", ["aibar", "login", "--provider", "claude"]),
    )
    all_ok = True
    log_lines: list[str] = ["Starting token refresh cycle"]

    for binary_name, command in command_plan:
        if shutil.which(binary_name) is None:
            all_ok = False
            log_lines.append(f"Warning: {binary_name} command not found")
            continue

        _apply_api_call_delay(throttle_state)
        log_lines.append(f"Running: {' '.join(command)}")
        success, return_code, output_text = _execute_claude_refresh_command(
            command=command,
            timeout_seconds=timeout_seconds,
        )
        if not success:
            all_ok = False
            log_lines.append(
                f"Warning: command failed ({' '.join(command)}), return_code={return_code}"
            )
        if output_text:
            log_lines.append(output_text)

    log_lines.append("Token refresh cycle complete")
    _CLAUDE_TOKEN_REFRESH_LOG_PATH.write_text(
        "\n".join(log_lines) + "\n",
        encoding="utf-8",
    )
    return all_ok


def _clear_claude_refresh_block_flag(
    idle_time_by_provider: dict[str, IdleTimeState],
) -> bool:
    """
    @brief Clear Claude OAuth refresh-block flag from idle-time state.
    @details Removes `oauth_refresh_blocked` by replacing the Claude state entry
    with an equivalent object where `oauth_refresh_blocked=false`.
    @param idle_time_by_provider {dict[str, IdleTimeState]} Provider idle-time map.
    @return {bool} True when map content changed.
    @satisfies REQ-105
    """
    claude_key = ProviderName.CLAUDE.value
    claude_state = idle_time_by_provider.get(claude_key)
    if claude_state is None or not claude_state.oauth_refresh_blocked:
        return False
    idle_time_by_provider[claude_key] = claude_state.model_copy(
        update={"oauth_refresh_blocked": False}
    )
    return True


def _is_claude_refresh_block_active(
    claude_state: IdleTimeState,
    now_epoch: int,
) -> bool:
    """
    @brief Evaluate Claude OAuth refresh-block activity against hardcoded TTL.
    @details Returns true only when `oauth_refresh_blocked` is true and current
    epoch is not greater than `last_success_timestamp + 86400`.
    @param claude_state {IdleTimeState} Claude provider idle-time state.
    @param now_epoch {int} Current epoch seconds.
    @return {bool} True when refresh-block flag remains active.
    @satisfies REQ-105
    """
    if not claude_state.oauth_refresh_blocked:
        return False
    return now_epoch <= (
        int(claude_state.last_success_timestamp) + _CLAUDE_OAUTH_BLOCK_TTL_SECONDS
    )


def _is_claude_authentication_error_result(result: ProviderResult) -> bool:
    """
    @brief Detect Claude result carrying canonical OAuth authentication-expired error.
    @details Matches provider key `claude`, error-state flag, and canonical error
    text `Invalid or expired OAuth token` for deterministic renewal triggering.
    @param result {ProviderResult} Provider result candidate.
    @return {bool} True when result is Claude auth-expired failure.
    @satisfies REQ-102
    """
    return (
        result.provider == ProviderName.CLAUDE
        and result.is_error
        and _is_claude_oauth_authentication_error(result.error)
    )


def _handle_claude_oauth_refresh_on_auth_error(
    claude_provider: ClaudeOAuthProvider,
    runtime_config: RuntimeConfig,
    throttle_state: dict[str, float | int] | None,
) -> tuple[ProviderResult, ProviderResult, bool]:
    """
    @brief Execute Claude auth-error renewal-and-retry control flow.
    @details Runs one in-process Claude token-renewal routine, reloads provider
    token from current environment/CLI credentials, and then executes exactly one
    Claude dual-window API retry via `_fetch_claude_dual`.
    @param runtime_config {RuntimeConfig} Runtime delay/timeout configuration.
    @param throttle_state {dict[str, float | int] | None} Shared API-delay state.
    @return {tuple[ProviderResult, ProviderResult, bool]} Tuple
    `(retry_result_5h, retry_result_7d, retry_auth_failed)`.
    @satisfies REQ-103
    @satisfies REQ-104
    """
    _run_claude_oauth_token_refresh(runtime_config)
    # Rebind provider token after renewal so retry uses refreshed credentials.
    refreshed_token = (
        os.environ.get(ClaudeOAuthProvider.TOKEN_ENV_VAR) or extract_claude_cli_token()
    )
    if refreshed_token:
        claude_provider._token = refreshed_token
    retry_result_5h, retry_result_7d = _fetch_claude_dual(
        claude_provider,
        throttle_state=throttle_state,
    )
    retry_auth_failed = _is_claude_authentication_error_result(
        retry_result_5h
    ) or _is_claude_authentication_error_result(retry_result_7d)
    return (retry_result_5h, retry_result_7d, retry_auth_failed)


def _update_claude_refresh_block_state(
    idle_time_by_provider: dict[str, IdleTimeState],
    blocked: bool,
) -> bool:
    """
    @brief Persist Claude OAuth refresh-block boolean in idle-time state map.
    @details Creates missing Claude idle-time entry when needed using current UTC
    timestamps, then updates `oauth_refresh_blocked` only when value changes.
    @param idle_time_by_provider {dict[str, IdleTimeState]} Provider idle-time map.
    @param blocked {bool} Target flag value for `claude.oauth_refresh_blocked`.
    @return {bool} True when state map changed.
    @satisfies REQ-104
    @satisfies REQ-105
    """
    claude_key = ProviderName.CLAUDE.value
    claude_state = idle_time_by_provider.get(claude_key)
    if claude_state is None:
        now_utc = datetime.now(timezone.utc)
        claude_state = build_idle_time_state(
            last_success_at=now_utc, idle_until=now_utc
        )
        idle_time_by_provider[claude_key] = claude_state
    if claude_state.oauth_refresh_blocked == blocked:
        return False
    idle_time_by_provider[claude_key] = claude_state.model_copy(
        update={"oauth_refresh_blocked": blocked}
    )
    return True


def _fetch_claude_dual_with_auth_recovery(
    provider: ClaudeOAuthProvider,
    throttle_state: dict[str, float | int] | None,
) -> tuple[ProviderResult, ProviderResult]:
    """
    @brief Fetch Claude dual-window results with auth-expired recovery policy.
    @details Executes one dual-window Claude fetch. When canonical auth-expired
    error appears, checks `claude.oauth_refresh_blocked` in idle-time state with
    hardcoded 86400-second TTL from `last_success_timestamp`; when unblocked,
    performs one token-renewal routine and one dual-window retry. On repeated
    auth failure, persists `oauth_refresh_blocked=true`; on success, clears flag.
    @param provider {ClaudeOAuthProvider} Claude provider instance.
    @param throttle_state {dict[str, float | int] | None} Shared API-delay state.
    @return {tuple[ProviderResult, ProviderResult]} Final Claude `(5h, 7d)` results.
    @satisfies REQ-102
    @satisfies REQ-103
    @satisfies REQ-104
    @satisfies REQ-105
    """
    result_5h, result_7d = _fetch_claude_dual(
        provider,
        throttle_state=throttle_state,
    )
    if not (
        _is_claude_authentication_error_result(result_5h)
        or _is_claude_authentication_error_result(result_7d)
    ):
        return (result_5h, result_7d)

    idle_time_by_provider = load_idle_time()
    claude_state = idle_time_by_provider.get(ProviderName.CLAUDE.value)
    now_epoch = int(time.time())
    if claude_state is not None and claude_state.oauth_refresh_blocked:
        if _is_claude_refresh_block_active(claude_state, now_epoch):
            return (result_5h, result_7d)
        if _clear_claude_refresh_block_flag(idle_time_by_provider):
            save_idle_time(idle_time_by_provider)

    runtime_config = load_runtime_config()
    retry_5h, retry_7d, retry_auth_failed = _handle_claude_oauth_refresh_on_auth_error(
        claude_provider=provider,
        runtime_config=runtime_config,
        throttle_state=throttle_state,
    )

    did_change = _update_claude_refresh_block_state(
        idle_time_by_provider=idle_time_by_provider,
        blocked=retry_auth_failed,
    )
    if did_change:
        save_idle_time(idle_time_by_provider)

    return (retry_5h, retry_7d)


def _clear_expired_claude_refresh_block(
    idle_time_by_provider: dict[str, IdleTimeState],
) -> bool:
    """
    @brief Auto-clear expired Claude OAuth refresh-block state.
    @details Clears `claude.oauth_refresh_blocked` when current epoch is greater
    than `last_success_timestamp + 86400` using hardcoded TTL policy.
    @param idle_time_by_provider {dict[str, IdleTimeState]} Provider idle-time map.
    @return {bool} True when state map changed.
    @satisfies REQ-105
    """
    claude_state = idle_time_by_provider.get(ProviderName.CLAUDE.value)
    if claude_state is None or not claude_state.oauth_refresh_blocked:
        return False
    now_epoch = int(time.time())
    if _is_claude_refresh_block_active(claude_state, now_epoch):
        return False
    return _clear_claude_refresh_block_flag(idle_time_by_provider)


def _is_http_429_result(result: ProviderResult) -> bool:
    """
    @brief Check whether result payload represents HTTP 429 rate limiting.
    @details Uses normalized raw payload marker `status_code == 429`.
    @param result {ProviderResult} Provider result to classify.
    @return {bool} True when result indicates HTTP 429.
    @satisfies REQ-041
    """
    return result.raw.get("status_code") == 429


def _serialize_results_payload(
    results: dict[str, ProviderResult],
) -> dict[str, dict[str, object]]:
    """
    @brief Serialize ProviderResult mapping to `show --json` payload schema.
    @details Converts each provider result to JSON-safe dict using Pydantic
    serialization with stable key structure.
    @param results {dict[str, ProviderResult]} Provider results keyed by provider id.
    @return {dict[str, dict[str, object]]} JSON payload suitable for CLI output and cache.
    @satisfies REQ-003
    @satisfies CTN-004
    """
    return {
        provider_key: result.model_dump(mode="json")
        for provider_key, result in results.items()
    }


def _empty_cache_document() -> dict[str, object]:
    """
    @brief Build empty cache document in canonical sectioned schema.
    @details Returns deterministic cache shape with top-level `payload` and `status`
    objects so downstream consumers can parse stable keys without null checks.
    @return {dict[str, object]} Empty cache document.
    @satisfies CTN-004
    @satisfies REQ-003
    """
    return {
        _CACHE_PAYLOAD_SECTION_KEY: {},
        _CACHE_STATUS_SECTION_KEY: {},
    }


def _normalize_cache_document(
    cache_document: dict[str, object] | None,
) -> dict[str, object]:
    """
    @brief Normalize decoded cache payload to canonical sectioned schema.
    @details Accepts decoded cache document and enforces object-typed `payload` and
    `status` sections. Missing or invalid sections normalize to empty objects.
    @param cache_document {dict[str, object] | None} Decoded cache payload from disk.
    @return {dict[str, object]} Canonical cache document with `payload`/`status`.
    @satisfies CTN-004
    @satisfies REQ-003
    """
    normalized = _empty_cache_document()
    if not isinstance(cache_document, dict):
        return normalized
    payload = cache_document.get(_CACHE_PAYLOAD_SECTION_KEY)
    status = cache_document.get(_CACHE_STATUS_SECTION_KEY)
    if isinstance(payload, dict):
        normalized[_CACHE_PAYLOAD_SECTION_KEY] = payload
    if isinstance(status, dict):
        normalized[_CACHE_STATUS_SECTION_KEY] = status
    return normalized


def _cache_payload_section(cache_document: dict[str, object]) -> dict[str, object]:
    """
    @brief Extract payload section from canonical cache document.
    @details Returns mutable provider-result mapping from normalized document.
    @param cache_document {dict[str, object]} Canonical cache document.
    @return {dict[str, object]} Provider payload section.
    """
    payload = cache_document.get(_CACHE_PAYLOAD_SECTION_KEY)
    if isinstance(payload, dict):
        return payload
    return {}


def _cache_status_section(cache_document: dict[str, object]) -> dict[str, object]:
    """
    @brief Extract status section from canonical cache document.
    @details Returns mutable provider/window status mapping from normalized document.
    @param cache_document {dict[str, object]} Canonical cache document.
    @return {dict[str, object]} Provider/window status section.
    """
    status = cache_document.get(_CACHE_STATUS_SECTION_KEY)
    if isinstance(status, dict):
        return status
    return {}


def _serialize_attempt_status(result: ProviderResult) -> dict[str, object]:
    """
    @brief Serialize one provider/window fetch attempt status for cache persistence.
    @details Converts ProviderResult error state to status object using `OK`/`FAIL`,
    preserving error text, update timestamp, and optional HTTP status code.
    @param result {ProviderResult} Provider result from current refresh attempt.
    @return {dict[str, object]} Attempt-status payload.
    @satisfies REQ-044
    """
    status_code_raw = result.raw.get("status_code")
    status_code = status_code_raw if isinstance(status_code_raw, int) else None
    retry_after_seconds = _extract_retry_after_seconds(result)
    return {
        "result": _ATTEMPT_RESULT_FAIL if result.is_error else _ATTEMPT_RESULT_OK,
        "error": result.error,
        "updated_at": _normalize_utc(result.updated_at).isoformat(),
        "status_code": status_code,
        "retry_after_seconds": retry_after_seconds if retry_after_seconds > 0 else None,
    }


def _record_attempt_status(
    status_section: dict[str, object],
    result: ProviderResult,
) -> None:
    """
    @brief Persist one provider/window attempt status into cache status section.
    @details Upserts `status[provider][window]` with serialized attempt metadata and
    preserves statuses for untouched providers/windows.
    @param status_section {dict[str, object]} Mutable cache status section.
    @param result {ProviderResult} Provider result to encode.
    @return {None} Function return value.
    @satisfies REQ-044
    @satisfies REQ-046
    """
    provider_key = result.provider.value
    provider_status = status_section.get(provider_key)
    if not isinstance(provider_status, dict):
        provider_status = {}
        status_section[provider_key] = provider_status
    provider_status[result.window.value] = _serialize_attempt_status(result)


def _extract_claude_snapshot_from_cache_document(
    cache_document: dict[str, object],
) -> dict[str, object] | None:
    """
    @brief Extract persisted Claude dual-window payload from cache document.
    @details Reads Claude entry from cache `payload` section and normalizes it into
    a dual-window raw payload (`five_hour`, `seven_day`) for HTTP 429 restoration.
    @param cache_document {dict[str, object]} Canonical cache document.
    @return {dict[str, object] | None} Normalized dual-window payload or None.
    @satisfies REQ-047
    """
    payload_section = _cache_payload_section(cache_document)
    claude_payload = payload_section.get(ProviderName.CLAUDE.value)
    return _normalize_claude_dual_payload(claude_payload)


def _get_window_attempt_status(
    status_section: dict[str, object],
    provider_key: str,
    window: WindowPeriod,
) -> dict[str, object] | None:
    """
    @brief Read provider/window attempt status from cache status section.
    @details Resolves nested `status[provider][window]` object and validates mapping
    shape before returning it to projection helpers.
    @param status_section {dict[str, object]} Cache status section.
    @param provider_key {str} Provider identifier.
    @param window {WindowPeriod} Window identifier.
    @return {dict[str, object] | None} Attempt status object or None.
    """
    provider_status = status_section.get(provider_key)
    if not isinstance(provider_status, dict):
        return None
    window_status = provider_status.get(window.value)
    if not isinstance(window_status, dict):
        return None
    return window_status


def _overlay_cached_failure_status(
    provider_key: str,
    target_window: WindowPeriod,
    projected_result: ProviderResult,
    status_section: dict[str, object],
) -> ProviderResult:
    """
    @brief Overlay cached failure status onto projected result.
    @details Reads `status[provider][window]`; when status marks `FAIL` with a
    non-empty error string, returns a copy of projected result carrying the cached
    error and optional status code while preserving payload metrics.
    @param provider_key {str} Provider id in cache sections.
    @param target_window {WindowPeriod} Requested window used for status lookup.
    @param projected_result {ProviderResult} Cached payload result after projection.
    @param status_section {dict[str, object]} Cache status section.
    @return {ProviderResult} Result with overlaid cached error state when applicable.
    @satisfies REQ-085
    @satisfies REQ-060
    @satisfies REQ-061
    """
    status_entry = _get_window_attempt_status(
        status_section, provider_key, target_window
    )
    if not isinstance(status_entry, dict):
        return projected_result
    if status_entry.get("result") != _ATTEMPT_RESULT_FAIL:
        return projected_result
    status_error = status_entry.get("error")
    if not isinstance(status_error, str) or not status_error.strip():
        return projected_result

    raw_update = dict(projected_result.raw)
    status_code = status_entry.get("status_code")
    if isinstance(status_code, int):
        raw_update["status_code"] = status_code
    retry_after_seconds = _coerce_retry_after_seconds(
        status_entry.get("retry_after_seconds")
    )
    if retry_after_seconds is not None:
        raw_update["retry_after_seconds"] = retry_after_seconds
    raw_update["cache_status_error"] = status_error

    updated_at = projected_result.updated_at
    status_updated_at = status_entry.get("updated_at")
    if isinstance(status_updated_at, str):
        try:
            updated_at = datetime.fromisoformat(status_updated_at)
        except ValueError:
            updated_at = projected_result.updated_at

    return projected_result.model_copy(
        update={"error": status_error, "raw": raw_update, "updated_at": updated_at}
    )


def _filter_cached_payload(
    cache_document: dict[str, object],
    provider_filter: ProviderName | None,
    allowed_provider_keys: set[str] | None = None,
) -> dict[str, object]:
    """
    @brief Filter canonical cache document by provider selector and enable-state.
    @details Filters both cache sections (`payload`, `status`) so output
    contains only provider nodes allowed by `allowed_provider_keys` and the
    optional selected provider. Schema keys remain stable even when all
    providers are filtered out.
    @param cache_document {dict[str, object]} Canonical cache document.
    @param provider_filter {ProviderName | None} Optional provider selector.
    @param allowed_provider_keys {set[str] | None} Optional enabled-provider key set.
    @return {dict[str, object]} Filtered cache document with canonical sections.
    @satisfies REQ-126
    """
    payload_section = _cache_payload_section(cache_document)
    status_section = _cache_status_section(cache_document)
    if provider_filter is None:
        if allowed_provider_keys is None:
            filtered_payload = dict(payload_section)
            filtered_status = dict(status_section)
        else:
            filtered_payload = {
                provider_key: provider_payload
                for provider_key, provider_payload in payload_section.items()
                if provider_key in allowed_provider_keys
            }
            filtered_status = {
                provider_key: provider_status
                for provider_key, provider_status in status_section.items()
                if provider_key in allowed_provider_keys
            }
        return {
            _CACHE_PAYLOAD_SECTION_KEY: filtered_payload,
            _CACHE_STATUS_SECTION_KEY: filtered_status,
        }

    provider_key = provider_filter.value
    if (
        allowed_provider_keys is not None
        and provider_key not in allowed_provider_keys
    ):
        return _empty_cache_document()
    selected_payload = payload_section.get(provider_key)
    selected_status = status_section.get(provider_key)
    filtered_payload: dict[str, object] = {}
    filtered_status: dict[str, object] = {}
    if isinstance(selected_payload, dict):
        filtered_payload[provider_key] = selected_payload
    if isinstance(selected_status, dict):
        filtered_status[provider_key] = selected_status
    return {
        _CACHE_PAYLOAD_SECTION_KEY: filtered_payload,
        _CACHE_STATUS_SECTION_KEY: filtered_status,
    }


def _filter_idle_time_by_provider(
    idle_time_by_provider: dict[str, IdleTimeState],
    provider_filter: ProviderName | None,
    allowed_provider_keys: set[str] | None = None,
) -> dict[str, IdleTimeState]:
    """
    @brief Filter provider-keyed idle-time map by selector and enable-state.
    @param idle_time_by_provider {dict[str, IdleTimeState]} Provider idle-time state map.
    @param provider_filter {ProviderName | None} Optional provider selector.
    @param allowed_provider_keys {set[str] | None} Optional enabled-provider key set.
    @return {dict[str, IdleTimeState]} Filtered provider idle-time map.
    @satisfies REQ-003
    @satisfies REQ-084
    @satisfies REQ-124
    @satisfies REQ-126
    """
    if provider_filter is None:
        if allowed_provider_keys is None:
            return dict(idle_time_by_provider)
        return {
            provider_key: state
            for provider_key, state in idle_time_by_provider.items()
            if provider_key in allowed_provider_keys
        }
    provider_key = provider_filter.value
    if (
        allowed_provider_keys is not None
        and provider_key not in allowed_provider_keys
    ):
        return {}
    selected = idle_time_by_provider.get(provider_key)
    if selected is None:
        return {}
    return {provider_key: selected}


def _enabled_provider_keys(runtime_config: RuntimeConfig) -> set[str]:
    """
    @brief Resolve enabled-provider key set from runtime configuration.
    @details Converts `resolve_enabled_providers(...)` mapping output into a set
    of enabled provider keys used by cache, idle-time, and render filtering.
    Time complexity O(P). Space complexity O(P), where P is provider count.
    @param runtime_config {RuntimeConfig} Runtime configuration carrying provider flags.
    @return {set[str]} Enabled provider keys.
    @satisfies CTN-017
    @satisfies REQ-123
    @satisfies REQ-124
    @satisfies REQ-126
    """
    return {
        provider_key
        for provider_key, enabled in resolve_enabled_providers(runtime_config).items()
        if enabled
    }


def _serialize_enabled_providers(
    runtime_config: RuntimeConfig,
) -> dict[str, bool]:
    """
    @brief Serialize provider-enable flags for `show --json`.
    @details Returns normalized provider-keyed booleans for all known
    providers. Missing config keys normalize to `true` for backward
    compatibility.
    @param runtime_config {RuntimeConfig} Runtime configuration carrying provider flags.
    @return {dict[str, bool]} Provider-keyed enabled-state mapping.
    @satisfies CTN-017
    @satisfies REQ-126
    @satisfies REQ-127
    """
    return resolve_enabled_providers(runtime_config)


def _serialize_idle_time_state(
    idle_time_by_provider: dict[str, IdleTimeState],
) -> dict[str, dict[str, object]]:
    """
    @brief Serialize provider-keyed idle-time state for `show --json`.
    @param idle_time_by_provider {dict[str, IdleTimeState]} Provider idle-time map.
    @return {dict[str, dict[str, object]]} JSON-safe provider idle-time section.
    @satisfies REQ-003
    @satisfies CTN-009
    """
    return {
        provider_key: state.model_dump(mode="json")
        for provider_key, state in idle_time_by_provider.items()
    }


def _serialize_freshness_state(
    idle_time_by_provider: dict[str, IdleTimeState],
) -> dict[str, dict[str, object]]:
    """
    @brief Serialize provider-keyed freshness data for `show --json`.
    @details Projects idle-time timestamps into GNOME-aligned `freshness` entries and
    emits local-time `%Y-%m-%d %H:%M` strings for direct parity checks.
    @param idle_time_by_provider {dict[str, IdleTimeState]} Provider idle-time map.
    @return {dict[str, dict[str, object]]} JSON-safe provider freshness section.
    @satisfies REQ-003
    @satisfies REQ-084
    """
    freshness: dict[str, dict[str, object]] = {}
    for provider_key, state in idle_time_by_provider.items():
        updated_at_utc = _epoch_to_utc_datetime(state.last_success_timestamp)
        next_update_utc = _epoch_to_utc_datetime(state.idle_until_timestamp)
        freshness[provider_key] = {
            "last_success_timestamp": state.last_success_timestamp,
            "idle_until_timestamp": state.idle_until_timestamp,
            "last_success_local": _format_local_datetime(updated_at_utc),
            "idle_until_local": _format_local_datetime(next_update_utc),
        }
    return freshness


def _fixed_effective_window(provider_name: ProviderName) -> WindowPeriod | None:
    """
    @brief Resolve provider fixed effective window override for `show` surfaces.
    @details Returns `30d` for providers that ignore requested window arguments
    and must expose a canonical window in payload, text, and JSON output.
    @param provider_name {ProviderName} Provider enum key.
    @return {WindowPeriod | None} Fixed window override, or None when provider is variable-window.
    @satisfies REQ-010
    @satisfies REQ-011
    @satisfies REQ-012
    @satisfies REQ-097
    """
    return _FIXED_WINDOW_BY_PROVIDER.get(provider_name)


def _serialize_extension_window_labels(
    enabled_provider_keys: set[str] | None = None,
) -> dict[str, str]:
    """
    @brief Serialize provider window labels for GNOME extension bar rendering.
    @details Exports provider-keyed fixed window labels from canonical
    fixed-window provider mapping for `show --json` `extension.window_labels`.
    When `enabled_provider_keys` is provided, disabled providers are omitted.
    @param enabled_provider_keys {set[str] | None} Optional enabled-provider key set.
    @return {dict[str, str]} Provider-keyed window label map.
    @satisfies REQ-003
    @satisfies REQ-017
    @satisfies REQ-126
    """
    return {
        provider_name.value: window_period.value
        for provider_name, window_period in _FIXED_WINDOW_BY_PROVIDER.items()
        if (
            enabled_provider_keys is None
            or provider_name.value in enabled_provider_keys
        )
    }


def _project_cached_window(
    result: ProviderResult,
    target_window: WindowPeriod,
    providers: dict[ProviderName, BaseProvider],
) -> ProviderResult:
    """
    @brief Project cached raw payload to requested window without network I/O.
    @details Attempts provider-specific `_parse_response` projection when cached
    window differs from requested window; providers with fixed effective windows
    (`copilot`, `openrouter`, `openai`, `geminiai`) bypass projection and preserve
    canonical window values.
    Returns original result on projection failure or when parser is unavailable.
    @param result {ProviderResult} Cached normalized provider result.
    @param target_window {WindowPeriod} Requested CLI window.
    @param providers {dict[ProviderName, BaseProvider]} Provider registry.
    @return {ProviderResult} Result aligned to requested window when possible.
    @satisfies REQ-009
    @satisfies REQ-010
    @satisfies REQ-011
    @satisfies REQ-012
    @satisfies REQ-042
    @satisfies REQ-097
    """
    fixed_window = _fixed_effective_window(result.provider)
    if fixed_window is not None:
        if result.window == fixed_window:
            return result
        provider = providers.get(result.provider)
        parser = (
            getattr(provider, "_parse_response", None) if provider is not None else None
        )
        if callable(parser) and isinstance(result.raw, dict):
            try:
                projected = parser(result.raw, fixed_window)
            except (AttributeError, KeyError, TypeError, ValueError):
                return result.model_copy(update={"window": fixed_window})
            if isinstance(projected, ProviderResult):
                return projected
        return result.model_copy(update={"window": fixed_window})
    if result.window == target_window:
        return result
    provider = providers.get(result.provider)
    if provider is None:
        return result
    parser = getattr(provider, "_parse_response", None)
    if not callable(parser) or not isinstance(result.raw, dict):
        return result
    try:
        projected = parser(result.raw, target_window)
    except (AttributeError, KeyError, TypeError, ValueError):
        return result
    if isinstance(projected, ProviderResult):
        return projected
    return result


def _load_cached_results(
    cache_document: dict[str, object],
    provider_filter: ProviderName | None,
    target_window: WindowPeriod,
    providers: dict[ProviderName, BaseProvider],
) -> dict[str, ProviderResult]:
    """
    @brief Decode cached JSON payload into ProviderResult mapping.
    @details Validates cached payload entries using `ProviderResult` schema, applies
    provider filtering, and projects cached windows to requested window when possible.
    Invalid entries are skipped. GeminiAI cached FAIL status is overlaid from `status`
    section onto projected payload result for surface-level error rendering.
    @param cache_document {dict[str, object]} Canonical cache document loaded from disk.
    @param provider_filter {ProviderName | None} Optional provider selector.
    @param target_window {WindowPeriod} Requested CLI window for projection.
    @param providers {dict[ProviderName, BaseProvider]} Provider registry.
    @return {dict[str, ProviderResult]} Validated cached results keyed by provider id.
    @satisfies REQ-009
    @satisfies REQ-042
    @satisfies REQ-044
    @satisfies REQ-046
    @satisfies REQ-060
    """
    filtered_cache = _filter_cached_payload(cache_document, provider_filter)
    filtered_payload = _cache_payload_section(filtered_cache)
    filtered_status = _cache_status_section(filtered_cache)
    cached_results: dict[str, ProviderResult] = {}
    for provider_key, raw_result in filtered_payload.items():
        if not isinstance(raw_result, dict):
            continue
        try:
            validated = ProviderResult.model_validate(raw_result)
        except ValidationError:
            continue
        projected_result = _project_cached_window(
            validated,
            target_window,
            providers,
        )
        cached_results[provider_key] = _overlay_cached_failure_status(
            provider_key=provider_key,
            target_window=projected_result.window,
            projected_result=projected_result,
            status_section=filtered_status,
        )
    return cached_results


def _update_idle_time_after_refresh(
    fetched_results: list[ProviderResult],
    runtime_config: RuntimeConfig,
) -> None:
    """
    @brief Persist provider-scoped idle-time metadata after refresh completion.
    @details Computes per-provider idle-time state after refresh execution.
    Successful-only provider cycles schedule `idle_until = last_success_at + idle_delay_seconds`.
    Provider cycles containing failures schedule
    `idle_until = last_attempt_at + max(idle_delay_seconds, resolved_retry_after_seconds)`,
    where fallback resolution uses `RuntimeConfig.default_retry_after_seconds` when
    provider payload marks `retry_after_unavailable=true`.
    @param fetched_results {list[ProviderResult]} Live results produced by refresh calls.
    @param runtime_config {RuntimeConfig} Runtime delay configuration.
    @return {None} Function return value.
    @satisfies REQ-038
    @satisfies REQ-041
    """
    if not fetched_results:
        return

    persisted_idle_time_state = load_idle_time()
    updated_idle_time_state = dict(persisted_idle_time_state)
    did_change = False

    results_by_provider: dict[str, list[ProviderResult]] = {}
    for result in fetched_results:
        provider_results = results_by_provider.setdefault(result.provider.value, [])
        provider_results.append(result)

    for provider_key, provider_results in results_by_provider.items():
        successful_results = [
            result for result in provider_results if not result.is_error
        ]
        failed_results = [result for result in provider_results if result.is_error]

        last_success_at: datetime | None = None
        if successful_results:
            last_success_at = max(
                _normalize_utc(result.updated_at) for result in successful_results
            )
        else:
            previous_state = persisted_idle_time_state.get(provider_key)
            if previous_state is not None:
                last_success_at = datetime.fromtimestamp(
                    previous_state.last_success_timestamp,
                    tz=timezone.utc,
                )
        if failed_results:
            last_attempt_at = max(
                _normalize_utc(result.updated_at) for result in provider_results
            )
            max_retry_after_seconds = max(
                _extract_retry_after_seconds(result) for result in failed_results
            )
            last_success_at = last_attempt_at
            idle_until = last_attempt_at + timedelta(
                seconds=max(runtime_config.idle_delay_seconds, max_retry_after_seconds)
            )
        else:
            if last_success_at is None:
                continue
            idle_until = last_success_at + timedelta(
                seconds=runtime_config.idle_delay_seconds
            )

        assert last_success_at is not None
        next_state = build_idle_time_state(
            last_success_at=last_success_at,
            idle_until=idle_until,
        )
        previous_state = updated_idle_time_state.get(provider_key)
        if previous_state is not None and previous_state.oauth_refresh_blocked:
            next_state = next_state.model_copy(update={"oauth_refresh_blocked": True})
        if previous_state is not None and previous_state == next_state:
            continue
        updated_idle_time_state[provider_key] = next_state
        did_change = True

    if did_change:
        save_idle_time(updated_idle_time_state)


def _project_next_reset(resets_at_str: str, window: WindowPeriod) -> datetime | None:
    """
    @brief Compute the next reset boundary after a stale resets_at timestamp.
    @details Advances `resets_at_str` by multiples of the window period until the
    result is strictly greater than current UTC time. Returns None if `resets_at_str`
    is unparseable or the window period is not in `_WINDOW_PERIOD_TIMEDELTA`.
    @param resets_at_str {str} ISO 8601 timestamp string of the last known reset boundary.
        May have a Z suffix (converted to +00:00) or an explicit timezone offset.
    @param window {WindowPeriod} Window period whose duration drives the projection step.
    @return {datetime | None} Projected future reset datetime in UTC, or None on parse error.
    @note Uses `math.ceil` to determine the minimum number of full cycles to advance.
    @satisfies REQ-002
    """
    period = _WINDOW_PERIOD_TIMEDELTA.get(window)
    if period is None:
        return None
    try:
        last = datetime.fromisoformat(resets_at_str.replace("Z", "+00:00"))
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
    except (ValueError, AttributeError):
        return None
    now = datetime.now(timezone.utc)
    elapsed_seconds = (now - last).total_seconds()
    if elapsed_seconds <= 0:
        # resets_at is already in the future; no projection needed
        return last
    period_seconds = period.total_seconds()
    cycles = math.ceil(elapsed_seconds / period_seconds)
    return last + timedelta(seconds=cycles * period_seconds)


def _apply_reset_projection(result: ProviderResult) -> ProviderResult:
    """
    @brief Return a copy of `result` with `metrics.reset_at` set to the projected next
    reset boundary when it is currently None but the raw payload contains a parseable
    past `resets_at` string for the result's window.
    @details When a ProviderResult is obtained from stale disk cache (last-good path) or
    from a cross-window raw re-parse, `_parse_response` correctly sets `reset_at=None`
    for past timestamps. This function recovers the display information by projecting
    the next future reset boundary from the raw payload's `resets_at` field, ensuring
    the 'Resets in:' countdown is shown even when the cached timestamp has already elapsed.
    If `reset_at` is already non-None, or the raw payload has no parseable `resets_at`
    for the window, or projection fails, the original result is returned unchanged.
    @param result {ProviderResult} Candidate result whose reset_at may require projection.
    @return {ProviderResult} Original result unchanged if no projection is needed;
        otherwise a new ProviderResult with metrics.reset_at set to the projected datetime.
    @satisfies REQ-002
    @see _project_next_reset
    """
    if result.is_error or result.metrics.reset_at is not None:
        return result

    window_key = "seven_day" if result.window == WindowPeriod.DAY_7 else "five_hour"
    window_data = result.raw.get(window_key, {})
    resets_at_str = window_data.get("resets_at") if window_data else None
    if not resets_at_str:
        return result

    projected = _project_next_reset(resets_at_str, result.window)
    if projected is None or projected <= datetime.now(timezone.utc):
        return result

    updated_metrics = result.metrics.model_copy(update={"reset_at": projected})
    return result.model_copy(update={"metrics": updated_metrics})


def get_providers() -> dict[ProviderName, BaseProvider]:
    """
    @brief Execute get providers.
    @details Applies get providers logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {dict[ProviderName, BaseProvider]} Function return value.
    """
    return {
        ProviderName.CLAUDE: ClaudeOAuthProvider(),
        ProviderName.OPENAI: OpenAIUsageProvider(),
        ProviderName.OPENROUTER: OpenRouterUsageProvider(),
        ProviderName.COPILOT: CopilotProvider(),
        ProviderName.CODEX: CodexProvider(),
        ProviderName.GEMINIAI: GeminiAIProvider(),
    }


def parse_window(window: str) -> WindowPeriod:
    """
    @brief Execute parse window.
    @details Applies parse window logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @param window {str} Input parameter `window`.
    @return {WindowPeriod} Function return value.
    @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.
    """
    mapping = {
        "5h": WindowPeriod.HOUR_5,
        "7d": WindowPeriod.DAY_7,
        "30d": WindowPeriod.DAY_30,
    }
    if window not in mapping:
        raise click.BadParameter(
            f"Invalid window. Choose from: {', '.join(mapping.keys())}"
        )
    return mapping[window]


def parse_provider(provider: str) -> ProviderName | None:
    """
    @brief Execute parse provider.
    @details Applies parse provider logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @param provider {str} Input parameter `provider`.
    @return {ProviderName | None} Function return value.
    @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.
    """
    if provider == "all":
        return None
    try:
        return ProviderName(provider)
    except ValueError:
        valid = ", ".join([p.value for p in ProviderName] + ["all"])
        raise click.BadParameter(f"Invalid provider. Choose from: {valid}")


def _provider_result_debug_summary(result: ProviderResult) -> str:
    """
    @brief Serialize provider result payload for debug log rows.
    @details Builds JSON summary including provider id, window id, error state,
    error text, and raw payload object using deterministic key ordering.
    Serialization failures fallback to minimal scalar diagnostics.
    @param result {ProviderResult} Provider result instance to summarize.
    @return {str} JSON debug summary string.
    @satisfies REQ-114
    """
    payload: dict[str, object] = {
        "provider": result.provider.value,
        "window": result.window.value,
        "is_error": result.is_error,
        "error": result.error,
        "raw": result.raw,
    }
    try:
        return json.dumps(payload, sort_keys=True, default=str)
    except (TypeError, ValueError):
        return (
            f'{{"provider":"{result.provider.value}","window":"{result.window.value}",'
            f'"is_error":{str(result.is_error).lower()}}}'
        )


def _extract_error_json_payload_for_debug_log(result: ProviderResult) -> str | None:
    """
    @brief Extract unmodified JSON error payload text for debug logging.
    @details Returns the original `raw["body"]` string only when provider result is
    an error and `raw["body"]` is a syntactically valid JSON text payload.
    Content is returned byte-for-byte without normalization or re-serialization.
    @param result {ProviderResult} Provider result instance to inspect.
    @return {str | None} Raw JSON payload text, or None when unavailable/non-JSON.
    @satisfies REQ-114
    """
    if not result.is_error:
        return None
    raw_body = result.raw.get("body")
    if not isinstance(raw_body, str):
        return None
    try:
        json.loads(raw_body)
    except (TypeError, ValueError):
        return None
    return raw_body


def _append_provider_debug_runtime_log(result: ProviderResult) -> None:
    """
    @brief Append debug runtime-log rows for one provider fetch result.
    @details Emits canonical provider debug summary row and, for failed API calls
    with JSON error bodies, appends an additional row including the full unmodified
    JSON response payload exactly as received from the API.
    @param result {ProviderResult} Provider result to log.
    @return {None} Function return value.
    @satisfies REQ-114
    """
    append_runtime_log_line(
        f"provider.fetch.debug {_provider_result_debug_summary(result)}",
        debug_only=True,
    )
    error_json_payload = _extract_error_json_payload_for_debug_log(result)
    if error_json_payload is None:
        return
    append_runtime_log_line(
        "provider.fetch.debug.error_json "
        f"provider={result.provider.value} "
        f"window={result.window.value} "
        f"payload={error_json_payload}",
        debug_only=True,
    )


def _fetch_result(
    provider: BaseProvider,
    window: WindowPeriod,
    throttle_state: dict[str, float | int] | None = None,
) -> ProviderResult:
    """
    @brief Execute one provider refresh call without legacy TTL cache reuse.
    @details Executes throttled provider fetch and returns normalized success/error
    results. Claude 5h/7d requests are routed through
    `_fetch_claude_dual_with_auth_recovery` so one API request can provide
    deterministic dual-window normalization with OAuth auth-error recovery.
    @param provider {BaseProvider} Provider instance to fetch from.
    @param window {WindowPeriod} Time window for the fetch.
    @param throttle_state {dict[str, float | int] | None} Mutable throttling state
        used to enforce inter-call spacing for live API requests.
    @return {ProviderResult} Refreshed provider result for requested window.
    @satisfies CTN-004
    @satisfies REQ-043
    @satisfies REQ-040
    @satisfies REQ-112
    @satisfies REQ-114
    @satisfies REQ-115
    """
    append_runtime_log_line(
        f"provider.fetch.start provider={provider.name.value} window={window.value}"
    )
    if isinstance(provider, ClaudeOAuthProvider) and window in {
        WindowPeriod.HOUR_5,
        WindowPeriod.DAY_7,
    }:
        result_5h, result_7d = _fetch_claude_dual_with_auth_recovery(
            provider,
            throttle_state=throttle_state,
        )
        if window == WindowPeriod.HOUR_5:
            append_runtime_log_line(
                "provider.fetch.end "
                f"provider={provider.name.value} window={window.value} status="
                f"{_ATTEMPT_RESULT_FAIL if result_5h.is_error else _ATTEMPT_RESULT_OK}"
            )
            _append_provider_failure_runtime_log(result_5h)
            _append_provider_debug_runtime_log(result_5h)
            return result_5h
        append_runtime_log_line(
            "provider.fetch.end "
            f"provider={provider.name.value} window={window.value} status="
            f"{_ATTEMPT_RESULT_FAIL if result_7d.is_error else _ATTEMPT_RESULT_OK}"
        )
        _append_provider_failure_runtime_log(result_7d)
        _append_provider_debug_runtime_log(result_7d)
        return result_7d

    try:
        _apply_api_call_delay(throttle_state)
        result = asyncio.run(provider.fetch(window))
    except ProviderError as exc:
        append_runtime_log_line(
            "provider.fetch.error "
            f"provider={provider.name.value} window={window.value} error={exc}"
        )
        result = provider._make_error_result(window=window, error=str(exc))
    except Exception as exc:
        append_runtime_log_line(
            "provider.fetch.error "
            f"provider={provider.name.value} window={window.value} "
            f"error=Unexpected error: {exc}"
        )
        result = provider._make_error_result(
            window=window, error=f"Unexpected error: {exc}"
        )
    append_runtime_log_line(
        "provider.fetch.end "
        f"provider={provider.name.value} window={window.value} status="
        f"{_ATTEMPT_RESULT_FAIL if result.is_error else _ATTEMPT_RESULT_OK}"
    )
    _append_provider_failure_runtime_log(result)
    _append_provider_debug_runtime_log(result)
    return result


def _fetch_claude_dual(
    provider: ClaudeOAuthProvider,
    throttle_state: dict[str, float | int] | None = None,
) -> tuple[ProviderResult, ProviderResult]:
    """
    @brief Fetch Claude 5h and 7d results via a single API call.
    @details Executes ClaudeOAuthProvider.fetch_all_windows for 5h and 7d on each invocation.
    Returns normalized provider results exactly as fetched (or synthesized error
    results on exception) without partial-window metric fallback.
    @param provider {ClaudeOAuthProvider} Claude provider instance.
    @param throttle_state {dict[str, float | int] | None} Mutable throttling state
        used to enforce inter-call spacing for live API requests.
    @return {tuple[ProviderResult, ProviderResult]} (5h_result, 7d_result).
    @satisfies REQ-002, REQ-036, REQ-037, CTN-004, REQ-040, REQ-043
    @satisfies REQ-112
    @satisfies REQ-114
    """
    append_runtime_log_line("provider.fetch.start provider=claude window=5h,7d")
    _apply_api_call_delay(throttle_state)
    windows = [WindowPeriod.HOUR_5, WindowPeriod.DAY_7]
    try:
        fetched = asyncio.run(provider.fetch_all_windows(windows))
    except ProviderError as exc:
        append_runtime_log_line(
            f"provider.fetch.error provider=claude window=5h,7d error={exc}"
        )
        fetched = {
            w: provider._make_error_result(
                window=w,
                error=str(exc),
                raw={
                    "retry_after_unavailable": True,
                },
            )
            for w in windows
        }
    except Exception as exc:
        append_runtime_log_line(
            "provider.fetch.error "
            f"provider=claude window=5h,7d error=Unexpected error: {exc}"
        )
        fetched = {
            w: provider._make_error_result(
                window=w,
                error=f"Unexpected error: {exc}",
                raw={
                    "retry_after_unavailable": True,
                },
            )
            for w in windows
        }

    result_5h = fetched.get(WindowPeriod.HOUR_5) or provider._make_error_result(
        window=WindowPeriod.HOUR_5, error="Missing 5h result"
    )
    result_7d = fetched.get(WindowPeriod.DAY_7) or provider._make_error_result(
        window=WindowPeriod.DAY_7, error="Missing 7d result"
    )
    # Ensure fallback retry-after policy can be applied for Claude OAuth/rate-limit
    # errors when provider payload does not include Retry-After metadata.
    for _result in (result_5h, result_7d):
        if not _result.is_error:
            continue
        if _coerce_retry_after_seconds(_result.raw.get("retry_after_seconds")) is not None:
            continue
        if _result.raw.get("retry_after_unavailable") is True:
            continue
        _result.raw["retry_after_unavailable"] = True

    append_runtime_log_line(
        "provider.fetch.end provider=claude window=5h "
        f"status={_ATTEMPT_RESULT_FAIL if result_5h.is_error else _ATTEMPT_RESULT_OK}"
    )
    append_runtime_log_line(
        "provider.fetch.end provider=claude window=7d "
        f"status={_ATTEMPT_RESULT_FAIL if result_7d.is_error else _ATTEMPT_RESULT_OK}"
    )
    _append_provider_debug_runtime_log(result_5h)
    _append_provider_debug_runtime_log(result_7d)
    return result_5h, result_7d


def _extract_claude_dual_payload(
    result_5h: ProviderResult,
    result_7d: ProviderResult,
) -> dict[str, object] | None:
    """
    @brief Extract dual-window Claude payload dictionary from successful results.
    @details Returns first raw payload containing both `five_hour` and `seven_day`
    mapping objects. Returns None when payload shape is invalid.
    @param result_5h {ProviderResult} Claude five-hour result.
    @param result_7d {ProviderResult} Claude seven-day result.
    @return {dict[str, object] | None} Serializable payload or None.
    @satisfies CTN-004
    @satisfies REQ-047
    """
    for payload in (result_7d.raw, result_5h.raw):
        if not isinstance(payload, dict):
            continue
        if isinstance(payload.get("five_hour"), dict) and isinstance(
            payload.get("seven_day"), dict
        ):
            return payload
    return None


def _normalize_claude_dual_payload(payload: object) -> dict[str, object] | None:
    """
    @brief Normalize persisted Claude payload shape into dual-window raw dictionary.
    @details Accepts either direct dual-window payload (`five_hour`/`seven_day`) or
    serialized ProviderResult dictionaries containing a `raw` field with that shape.
    @param payload {object} Decoded JSON object from snapshot candidate file.
    @return {dict[str, object] | None} Normalized dual-window payload or None.
    @satisfies REQ-036
    """
    if not isinstance(payload, dict):
        return None

    raw_payload = payload
    if "raw" in payload and isinstance(payload.get("raw"), dict):
        raw_payload = payload["raw"]

    if not isinstance(raw_payload.get("five_hour"), dict):
        return None
    if not isinstance(raw_payload.get("seven_day"), dict):
        return None
    return raw_payload


def _extract_snapshot_reset_at(
    snapshot_payload: dict[str, object] | None,
    window: WindowPeriod,
) -> datetime | None:
    """
    @brief Resolve projected reset timestamp from persisted Claude snapshot payload.
    @details Uses window-specific `resets_at` string from persisted payload and
    projects next reset boundary through `_project_next_reset`.
    @param snapshot_payload {dict[str, object] | None} Persisted dual-window payload.
    @param window {WindowPeriod} Target window period.
    @return {datetime | None} Projected reset timestamp or None.
    @satisfies REQ-036
    """
    if snapshot_payload is None:
        return None
    window_key = "seven_day" if window == WindowPeriod.DAY_7 else "five_hour"
    window_data = snapshot_payload.get(window_key)
    if not isinstance(window_data, dict):
        return None
    resets_at = window_data.get("resets_at")
    if not isinstance(resets_at, str) or not resets_at:
        return None
    return _project_next_reset(resets_at, window)


def _extract_snapshot_utilization(
    snapshot_payload: dict[str, object] | None,
    window: WindowPeriod,
) -> float | None:
    """
    @brief Resolve utilization percentage from persisted Claude snapshot payload.
    @details Reads window-specific `utilization`, validates finite range, and clamps
    values to [0.0, 100.0] for deterministic percentage rendering.
    @param snapshot_payload {dict[str, object] | None} Persisted dual-window payload.
    @param window {WindowPeriod} Target window period.
    @return {float | None} Clamped utilization percentage or None.
    @satisfies REQ-036
    """
    if snapshot_payload is None:
        return None
    window_key = "seven_day" if window == WindowPeriod.DAY_7 else "five_hour"
    window_data = snapshot_payload.get(window_key)
    if not isinstance(window_data, dict):
        return None
    value = window_data.get("utilization")
    if not isinstance(value, (int, float, str)):
        return None
    try:
        utilization = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(utilization):
        return None
    return max(0.0, min(100.0, utilization))


def _is_claude_rate_limited_result(result: ProviderResult) -> bool:
    """
    @brief Check whether a ProviderResult represents Claude HTTP 429.
    @details Matches normalized Claude error payloads by provider identity,
    error-state flag, and `raw.status_code == 429`.
    @param result {ProviderResult} Result to classify.
    @return {bool} True when result is Claude 429.
    @satisfies REQ-036
    """
    return (
        result.provider == ProviderName.CLAUDE
        and result.is_error
        and result.raw.get("status_code") == 429
    )


def _build_claude_rate_limited_partial_result(
    window: WindowPeriod,
    include_error: bool,
    snapshot_payload: dict[str, object] | None = None,
) -> ProviderResult:
    """
    @brief Build Claude 429 partial-window result using persisted payload when available.
    @details For 5h window, usage is always forced to 100.0% while reset time is read
    from persisted payload (`five_hour.resets_at`) when possible. For 7d window,
    utilization and reset are restored from persisted payload (`seven_day`) when
    available; otherwise synthetic window-based fallback values are used.
    @param window {WindowPeriod} Window associated with the synthetic result.
    @param include_error {bool} True to include `Rate limited...` error text.
    @param snapshot_payload {dict[str, object] | None} Persisted Claude payload for
        429 restoration.
    @return {ProviderResult} Claude result suitable for partial-window display.
    @satisfies REQ-036
    @satisfies REQ-037
    """
    reset_at = _extract_snapshot_reset_at(snapshot_payload, window)
    if reset_at is None:
        reset_at = datetime.now(timezone.utc) + _WINDOW_PERIOD_TIMEDELTA[window]

    utilization = 100.0
    if window == WindowPeriod.DAY_7:
        persisted_utilization = _extract_snapshot_utilization(snapshot_payload, window)
        if persisted_utilization is not None:
            utilization = persisted_utilization

    remaining = max(0.0, min(100.0, 100.0 - utilization))
    return ProviderResult(
        provider=ProviderName.CLAUDE,
        window=window,
        metrics=UsageMetrics(
            remaining=remaining,
            limit=100.0,
            reset_at=reset_at,
        ),
        raw={
            "status_code": 429,
            "rate_limit_partial": True,
            "snapshot_restored": snapshot_payload is not None,
            "snapshot_payload": snapshot_payload,
        },
        error="Rate limited. Try again later." if include_error else None,
    )


def _refresh_and_persist_cache_payload(
    providers: dict[ProviderName, BaseProvider],
    target_window: WindowPeriod,
    runtime_config: RuntimeConfig,
    cache_document: dict[str, object],
) -> dict[str, object]:
    """
    @brief Execute modular API calls, merge results into cache in memory, then persist.
    @details Executes provider fetches for configured providers only, records
    per-provider/window attempt status in memory, updates payload only for successful
    provider/window outcomes, computes new idle-time values using
    `idle_until = max(current_time + retry_after, current_time + idle_delay)` for errors,
    then writes updated `cache.json` and `idle-time.json` under lock in a single write.
    The `cache_document` parameter is the previously loaded cache content passed from
    `retrieve_results_via_cache_pipeline` to avoid redundant disk reads.
    @param providers {dict[ProviderName, BaseProvider]} Provider scope for refresh.
    @param target_window {WindowPeriod} Requested window for refresh execution.
    @param runtime_config {RuntimeConfig} Runtime throttling configuration.
    @param cache_document {dict[str, object]} Previously loaded canonical cache document.
    @return {dict[str, object]} Updated cache document after merge and persistence.
    @satisfies CTN-004
    @satisfies REQ-009
    @satisfies REQ-038
    @satisfies REQ-041
    @satisfies REQ-043
    @satisfies REQ-044
    @satisfies REQ-045
    @satisfies REQ-046
    @satisfies REQ-047
    @satisfies REQ-066
    @satisfies REQ-091
    @satisfies REQ-092
    @satisfies REQ-094
    """
    append_runtime_log_line(
        "refresh.pipeline.start "
        f"target_window={target_window.value} provider_count={len(providers)}"
    )
    cache_before_refresh = json.dumps(cache_document, sort_keys=True)
    payload_section = _cache_payload_section(cache_document)
    status_section = _cache_status_section(cache_document)

    fetched_results: list[ProviderResult] = []
    successful_payload_results: dict[str, ProviderResult] = {}
    throttle_state: dict[str, float | int] = {
        "delay_milliseconds": runtime_config.api_call_delay_milliseconds
    }
    for provider_name, provider in providers.items():
        if not provider.is_configured():
            append_runtime_log_line(
                f"refresh.pipeline.skip provider={provider_name.value} reason=not_configured"
            )
            continue

        if isinstance(provider, ClaudeOAuthProvider) and target_window in {
            WindowPeriod.HOUR_5,
            WindowPeriod.DAY_7,
        }:
            result_5h, result_7d = _fetch_claude_dual_with_auth_recovery(
                provider=provider,
                throttle_state=throttle_state,
            )
            fetched_results.extend([result_5h, result_7d])
            _record_attempt_status(status_section, result_5h)
            _record_attempt_status(status_section, result_7d)
            _append_provider_failure_runtime_log(result_5h)
            _append_provider_failure_runtime_log(result_7d)

            preferred_success: ProviderResult | None = None
            if target_window == WindowPeriod.HOUR_5:
                if not result_5h.is_error:
                    preferred_success = result_5h
                elif not result_7d.is_error:
                    preferred_success = result_7d
            else:
                if not result_7d.is_error:
                    preferred_success = result_7d
                elif not result_5h.is_error:
                    preferred_success = result_5h

            if preferred_success is not None:
                successful_payload_results[provider_name.value] = preferred_success
            continue

        effective_window = _fixed_effective_window(provider_name) or target_window
        result = _fetch_result(
            provider,
            effective_window,
            throttle_state=throttle_state,
        )
        fetched_results.append(result)
        _record_attempt_status(status_section, result)
        if not result.is_error:
            successful_payload_results[provider_name.value] = result

    if successful_payload_results:
        payload_section.update(_serialize_results_payload(successful_payload_results))

    cache_after_refresh = json.dumps(cache_document, sort_keys=True)
    if cache_after_refresh != cache_before_refresh:
        append_runtime_log_line("refresh.pipeline.cache_write changed=true")
        save_cli_cache(cache_document)
    else:
        append_runtime_log_line("refresh.pipeline.cache_write changed=false")

    _update_idle_time_after_refresh(fetched_results, runtime_config)
    append_runtime_log_line(
        f"refresh.pipeline.end fetched_results_count={len(fetched_results)}"
    )
    return cache_document


def retrieve_results_via_cache_pipeline(
    provider_filter: ProviderName | None,
    target_window: WindowPeriod,
    force_refresh: bool,
    providers: dict[ProviderName, BaseProvider],
    enabled_provider_keys: set[str] | None = None,
) -> RetrievalPipelineOutput:
    """
    @brief Execute shared cache-based retrieval pipeline for CLI `show`.
    @details Implements the canonical `show` process flow:
    (1) Evaluate idle-time per provider to determine refresh need.
    (2) If at least one provider has expired idle-time: execute modular API calls
        only for expired providers, collect results in memory, compute new idle-time
        values, write updated `cache.json` and `idle-time.json` under lock file.
    (3) Read `cache.json` under lock file (single read per execution).
    (4) Return decoded results for presentation.
    Performs at most one `load_cli_cache` disk read per execution when no refresh is
    needed, and at most one read (before refresh) plus one write when refresh occurs.
    After refresh, the in-memory cache document is used directly without a second read.
    @param provider_filter {ProviderName | None} Optional provider selector.
    @param target_window {WindowPeriod} Target window requested by caller.
    @param force_refresh {bool} Force-refresh flag for current execution.
    @param providers {dict[ProviderName, BaseProvider]} Provider registry.
    @param enabled_provider_keys {set[str] | None} Optional enabled-provider key set.
    @return {RetrievalPipelineOutput} Shared retrieval state and decoded results.
    @satisfies REQ-009
    @satisfies REQ-039
    @satisfies REQ-042
    @satisfies REQ-043
    @satisfies REQ-044
    @satisfies REQ-045
    @satisfies REQ-046
    @satisfies REQ-047
    @satisfies REQ-066
    @satisfies REQ-091
    @satisfies REQ-092
    @satisfies REQ-093
    @satisfies REQ-094
    @satisfies REQ-124
    @satisfies REQ-126
    """
    append_runtime_log_line(
        "idle.pipeline.start "
        f"provider_filter={provider_filter.value if provider_filter is not None else 'all'} "
        f"target_window={target_window.value} force_refresh={force_refresh}"
    )
    if force_refresh:
        remove_idle_time_file()
        append_runtime_log_line(
            "idle.pipeline.force_refresh removed_idle_time_file=true"
        )

    idle_state_by_provider = load_idle_time()
    if force_refresh:
        if _clear_claude_refresh_block_flag(idle_state_by_provider):
            save_idle_time(idle_state_by_provider)
            idle_state_by_provider = load_idle_time()
    elif _clear_expired_claude_refresh_block(idle_state_by_provider):
        save_idle_time(idle_state_by_provider)
        idle_state_by_provider = load_idle_time()
    now_utc = datetime.now(timezone.utc)
    if provider_filter is None:
        selected_providers = providers
    else:
        selected_provider = providers.get(provider_filter)
        selected_providers = (
            {} if selected_provider is None else {provider_filter: selected_provider}
        )
    if enabled_provider_keys is not None:
        selected_providers = {
            provider_name: provider
            for provider_name, provider in selected_providers.items()
            if provider_name.value in enabled_provider_keys
        }

    idle_blocked_provider_keys: set[str] = set()
    if not force_refresh:
        current_timestamp = int(now_utc.timestamp())
        for provider_name in selected_providers:
            provider_state = idle_state_by_provider.get(provider_name.value)
            if (
                provider_state is not None
                and provider_state.idle_until_timestamp > current_timestamp
            ):
                idle_blocked_provider_keys.add(provider_name.value)
                append_runtime_log_line(
                    "idle.pipeline.check "
                    f"provider={provider_name.value} blocked=true "
                    f"idle_until_timestamp={provider_state.idle_until_timestamp} "
                    f"current_timestamp={current_timestamp}"
                )
            else:
                append_runtime_log_line(
                    "idle.pipeline.check "
                    f"provider={provider_name.value} blocked=false "
                    f"current_timestamp={current_timestamp}"
                )
    idle_active = bool(idle_blocked_provider_keys)

    if force_refresh:
        refresh_scope = selected_providers
    else:
        refresh_scope = {
            provider_name: provider
            for provider_name, provider in selected_providers.items()
            if provider_name.value not in idle_blocked_provider_keys
        }

    if refresh_scope:
        append_runtime_log_line(
            "idle.pipeline.refresh_scope "
            f"providers={','.join(sorted(p.value for p in refresh_scope))}"
        )
        runtime_config = load_runtime_config()
        cached_payload_raw = load_cli_cache()
        cached_document = _normalize_cache_document(cached_payload_raw)
        effective_payload = _refresh_and_persist_cache_payload(
            providers=refresh_scope,
            target_window=target_window,
            runtime_config=runtime_config,
            cache_document=cached_document,
        )
        cache_available = bool(_cache_payload_section(effective_payload)) or bool(
            _cache_status_section(effective_payload)
        )
        if not cache_available:
            append_runtime_log_line("idle.pipeline.end cache_available=false")
            return RetrievalPipelineOutput(
                payload=_empty_cache_document(),
                results={},
                idle_time_by_provider=_filter_idle_time_by_provider(
                    load_idle_time(),
                    provider_filter,
                    enabled_provider_keys,
                ),
                idle_active=False,
                cache_available=False,
            )
        refreshed_idle_state = load_idle_time()
        filtered_effective_payload = _filter_cached_payload(
            effective_payload,
            provider_filter,
            enabled_provider_keys,
        )
        append_runtime_log_line("idle.pipeline.end cache_available=true source=refresh")
        return RetrievalPipelineOutput(
            payload=filtered_effective_payload,
            results=_load_cached_results(
                cache_document=filtered_effective_payload,
                provider_filter=provider_filter,
                target_window=target_window,
                providers=providers,
            ),
            idle_time_by_provider=_filter_idle_time_by_provider(
                refreshed_idle_state,
                provider_filter,
                enabled_provider_keys,
            ),
            idle_active=idle_active,
            cache_available=True,
        )

    cached_payload_raw = load_cli_cache()
    if cached_payload_raw is None:
        append_runtime_log_line("idle.pipeline.end cache_available=false")
        return RetrievalPipelineOutput(
            payload=_empty_cache_document(),
            results={},
            idle_time_by_provider=_filter_idle_time_by_provider(
                idle_state_by_provider,
                provider_filter,
                enabled_provider_keys,
            ),
            idle_active=idle_active,
            cache_available=False,
        )
    cached_document = _normalize_cache_document(cached_payload_raw)
    filtered_cached_document = _filter_cached_payload(
        cached_document,
        provider_filter,
        enabled_provider_keys,
    )
    append_runtime_log_line("idle.pipeline.end cache_available=true source=cache_only")
    return RetrievalPipelineOutput(
        payload=filtered_cached_document,
        results=_load_cached_results(
            cache_document=filtered_cached_document,
            provider_filter=provider_filter,
            target_window=target_window,
            providers=providers,
        ),
        idle_time_by_provider=_filter_idle_time_by_provider(
            idle_state_by_provider,
            provider_filter,
            enabled_provider_keys,
        ),
        idle_active=idle_active,
        cache_available=True,
    )


def _build_cached_dual_window_results(
    provider_name: ProviderName,
    result: ProviderResult,
    providers: dict[ProviderName, BaseProvider],
) -> tuple[ProviderResult, ProviderResult] | None:
    """
    @brief Build Claude/Codex dual-window display results from cached payload data.
    @details Attempts parser-based 5h/7d projection from cached raw payload when
    provider parser is available.
    @param provider_name {ProviderName} Provider associated with cached result.
    @param result {ProviderResult} Cached provider result.
    @param providers {dict[ProviderName, BaseProvider]} Provider registry.
    @return {tuple[ProviderResult, ProviderResult] | None} (5h, 7d) results when
        dual-window expansion succeeds; otherwise None.
    @satisfies REQ-002
    @satisfies REQ-036
    @satisfies REQ-043
    """
    provider = providers.get(provider_name)
    parser = getattr(provider, "_parse_response", None)
    if not callable(parser) or not isinstance(result.raw, dict):
        return None
    try:
        result_5h = parser(result.raw, WindowPeriod.HOUR_5)
        result_7d = parser(result.raw, WindowPeriod.DAY_7)
    except (AttributeError, KeyError, TypeError, ValueError):
        return None
    if not isinstance(result_5h, ProviderResult):
        return None
    if not isinstance(result_7d, ProviderResult):
        return None
    return (result_5h, result_7d)


@click.group(
    cls=StartupPreflightGroup,
    invoke_without_command=True,
    context_settings={"help_option_names": ["--help", "-h"]},
    help=(
        "Monitor AI provider usage, quota, and cost data from one CLI.\n"
        "Use 'show' for terminal output, 'show --json' for machine output, "
        "and 'show --force' to bypass idle-time gating for one run."
    ),
    epilog=(
        "Examples:\n"
        "  aibar show                   Show usage metrics\n"
        "  aibar show --json            Machine-readable output\n"
        "  aibar show --force           Bypass idle-time gating\n"
        "  aibar setup                  Interactive configuration\n"
        "  aibar gnome-install          Install GNOME extension\n"
        "  aibar gnome-uninstall        Remove GNOME extension\n"
        "  aibar --version              Show installed version\n"
        "  aibar --upgrade              Upgrade via uv\n"
        "  aibar --uninstall            Uninstall via uv\n"
        "  aibar --enable-log           Enable runtime execution log\n"
        "  aibar --disable-log          Disable runtime execution log\n"
        "  aibar --enable-debug         Enable runtime API debug log\n"
        "  aibar --disable-debug        Disable runtime API debug log"
    ),
)
@click.option(
    "--version",
    "--ver",
    "show_version",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=_handle_version_option,
    help="Show installed version and exit.",
)
@click.option(
    "--upgrade",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=_handle_upgrade_option,
    help="Upgrade aibar using uv and exit.",
)
@click.option(
    "--uninstall",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=_handle_uninstall_option,
    help="Uninstall aibar using uv and exit.",
)
@click.option(
    "--enable-log",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=_handle_enable_log_option,
    help="Enable runtime execution log and exit.",
)
@click.option(
    "--disable-log",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=_handle_disable_log_option,
    help="Disable runtime execution log and exit.",
)
@click.option(
    "--enable-debug",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=_handle_enable_debug_option,
    help="Enable runtime API debug log and exit.",
)
@click.option(
    "--disable-debug",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=_handle_disable_debug_option,
    help="Disable runtime API debug log and exit.",
)
@click.pass_context
def main(ctx: click.Context) -> None:
    """
    @brief Execute main.
    @details Applies main logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {None} Function return value.
    @satisfies REQ-068
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command(
    short_help="Display provider usage and cost metrics.",
    help=(
        "Display provider usage and cost metrics using the shared cache pipeline.\n"
        "Supports text output (default) or JSON output with '--json'.\n"
        "Use '--force' to bypass idle-time gating for this execution."
    ),
)
@click.option(
    "--provider",
    "-p",
    default="all",
    help="Provider to query (claude, openai, openrouter, copilot, codex, geminiai, all)",
)
@click.option(
    "--window",
    "-w",
    default="7d",
    help="Time window (5h, 7d, 30d)",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output raw JSON instead of formatted text",
)
@click.option(
    "--force",
    "force_refresh",
    is_flag=True,
    help="Bypass idle-time gating and force provider refresh",
)
def show(provider: str, window: str, output_json: bool, force_refresh: bool) -> None:
    """
    @brief Execute `show` with idle-time cache gating and throttled provider refresh.
    @details Delegates provider retrieval to a shared cache-based pipeline that
    applies force handling, idle-time gating, conditional cache refresh, and
    deterministic readback from `cache.json` before rendering. When `--provider`
    targets `copilot`, `openrouter`, `openai`, or `geminiai`, effective window is
    forced to `30d` regardless of `--window`.
    @param provider {str} CLI provider selector string.
    @param window {str} CLI window period string.
    @param output_json {bool} When True, emit JSON output instead of formatted text.
    @param force_refresh {bool} When True, bypass idle-time gate for this execution.
    @return {None} Function return value.
    @satisfies REQ-003
    @satisfies REQ-002
    @satisfies REQ-009
    @satisfies REQ-038
    @satisfies REQ-039
    @satisfies REQ-040
    @satisfies REQ-041
    @satisfies REQ-042
    @satisfies REQ-043
    @satisfies REQ-084
    @satisfies REQ-085
    @satisfies REQ-067
    @satisfies REQ-097
    @satisfies REQ-123
    @satisfies REQ-124
    @satisfies REQ-125
    @satisfies REQ-126
    """
    provider_filter = parse_provider(provider)
    window_period = parse_window(window)
    ctx = click.get_current_context()
    window_source = ctx.get_parameter_source("window")

    if provider_filter is not None:
        fixed_window = _fixed_effective_window(provider_filter)
        if fixed_window is not None:
            window_period = fixed_window
    providers = get_providers()
    runtime_cfg = load_runtime_config()
    enabled_provider_flags = _serialize_enabled_providers(runtime_cfg)
    enabled_provider_keys = _enabled_provider_keys(runtime_cfg)
    provider_requested_disabled = (
        provider_filter is not None
        and not enabled_provider_flags.get(provider_filter.value, True)
    )

    # Filter to specific provider if requested
    if provider_filter:
        if provider_filter not in providers:
            click.echo(
                f"Provider {provider_filter.value} not implemented yet.", err=True
            )
            sys.exit(1)

    try:
        retrieval = retrieve_results_via_cache_pipeline(
            provider_filter=provider_filter,
            target_window=window_period,
            force_refresh=force_refresh,
            providers=providers,
            enabled_provider_keys=enabled_provider_keys,
        )
    except LockAcquisitionTimeoutError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    if retrieval.idle_active and not retrieval.cache_available:
        if output_json:
            output_doc = _empty_cache_document()
            output_doc[_CACHE_IDLE_TIME_SECTION_KEY] = {}
            output_doc[_CACHE_FRESHNESS_SECTION_KEY] = {}
            output_doc[_CACHE_EXTENSION_SECTION_KEY] = {
                "gnome_refresh_interval_seconds": runtime_cfg.gnome_refresh_interval_seconds,
                "idle_delay_seconds": runtime_cfg.idle_delay_seconds,
                "copilot_extra_premium_request_cost": runtime_cfg.copilot_extra_premium_request_cost,
                "window_labels": _serialize_extension_window_labels(
                    enabled_provider_keys
                ),
            }
            output_doc[_CACHE_ENABLED_PROVIDERS_SECTION_KEY] = enabled_provider_flags
            click.echo(json.dumps(output_doc, indent=2))
        else:
            click.echo("Cache unavailable while idle-time is active.")
        return

    if output_json:
        output_doc = dict(retrieval.payload)
        output_doc[_CACHE_IDLE_TIME_SECTION_KEY] = _serialize_idle_time_state(
            retrieval.idle_time_by_provider
        )
        output_doc[_CACHE_FRESHNESS_SECTION_KEY] = _serialize_freshness_state(
            retrieval.idle_time_by_provider
        )
        output_doc[_CACHE_EXTENSION_SECTION_KEY] = {
            "gnome_refresh_interval_seconds": runtime_cfg.gnome_refresh_interval_seconds,
            "idle_delay_seconds": runtime_cfg.idle_delay_seconds,
            "copilot_extra_premium_request_cost": runtime_cfg.copilot_extra_premium_request_cost,
            "window_labels": _serialize_extension_window_labels(
                enabled_provider_keys
            ),
        }
        output_doc[_CACHE_ENABLED_PROVIDERS_SECTION_KEY] = enabled_provider_flags
        click.echo(json.dumps(output_doc, indent=2))
        return

    if provider_requested_disabled:
        return

    rendered_panels: list[tuple[ProviderName, str, list[str]]] = []
    status_section = _cache_status_section(retrieval.payload)
    for name, prov in providers.items():
        if name.value not in enabled_provider_keys:
            continue
        if not prov.is_configured():
            if provider_filter is None or provider_filter == name:
                rendered_panels.append(
                    (
                        name,
                        _provider_display_name(name),
                        [
                            "Status: NOT CONFIGURED",
                            f"Missing env: {config.ENV_VARS.get(name)}",
                        ],
                    )
                )

    if provider_filter is not None and provider_filter.value not in retrieval.results:
        click.echo(f"\n{provider_filter.value}: Not available in cache")
        return

    for provider_key, result in retrieval.results.items():
        provider_name = ProviderName(provider_key)
        show_dual_windows = (
            window_source == ParameterSource.DEFAULT
            and provider_name in {ProviderName.CLAUDE, ProviderName.CODEX}
        )
        if show_dual_windows:
            dual_results = _build_cached_dual_window_results(
                provider_name=provider_name,
                result=result,
                providers=providers,
            )
            if dual_results is not None:
                result_5h, result_7d = dual_results
                result_5h = _overlay_cached_failure_status(
                    provider_key=provider_name.value,
                    target_window=WindowPeriod.HOUR_5,
                    projected_result=result_5h,
                    status_section=status_section,
                )
                result_7d = _overlay_cached_failure_status(
                    provider_key=provider_name.value,
                    target_window=WindowPeriod.DAY_7,
                    projected_result=result_7d,
                    status_section=status_section,
                )
                if (
                    result.is_error
                    and not result_5h.is_error
                    and not result_7d.is_error
                ):
                    result_raw = dict(result.raw)
                    if result.window == WindowPeriod.HOUR_5:
                        result_5h = result_5h.model_copy(
                            update={"error": result.error, "raw": result_raw}
                        )
                    else:
                        result_7d = result_7d.model_copy(
                            update={"error": result.error, "raw": result_raw}
                        )
                rendered_panels.append(
                    (
                        provider_name,
                        *_build_dual_window_panel(
                            provider_name,
                            result_5h,
                            result_7d,
                            freshness_state=retrieval.idle_time_by_provider.get(
                                provider_name.value
                            ),
                        ),
                    )
                )
                continue
        rendered_panels.append(
            (
                provider_name,
                *_build_result_panel(
                    provider_name,
                    result,
                    freshness_state=retrieval.idle_time_by_provider.get(
                        provider_name.value
                    ),
                ),
            )
        )

    rendered_panels.sort(key=lambda panel: _provider_panel_sort_key(panel[0]))
    shared_content_width = _resolve_shared_panel_content_width(rendered_panels)
    for provider_name, title, body_lines in rendered_panels:
        _emit_provider_panel(
            provider_name=provider_name,
            title=title,
            body_lines=body_lines,
            content_width=shared_content_width,
        )


def _provider_display_name(provider_name: ProviderName) -> str:
    """
    @brief Resolve human-facing provider title for terminal panel rendering.
    @details Maps machine-readable provider keys to display names aligned with
    CLI and GNOME extension output surfaces; applies uppercase `GEMINIAI`
    override for provider key `geminiai`.
    @param provider_name {ProviderName} Provider enum key.
    @return {str} Human-facing provider display name.
    @satisfies REQ-062
    """
    if provider_name == ProviderName.GEMINIAI:
        return "GEMINIAI"
    return provider_name.value.upper()


def _provider_panel_sort_key(provider_name: ProviderName) -> tuple[int, str]:
    """
    @brief Build deterministic provider sort key for CLI `show` panel ordering.
    @details Applies canonical provider order `claude/openrouter/copilot/codex/openai/geminiai`;
    unknown providers are appended after known providers using lexical fallback.
    @param provider_name {ProviderName} Provider enum key.
    @return {tuple[int, str]} `(rank, provider_name.value)` sort key.
    @satisfies REQ-067
    @satisfies TST-030
    """
    try:
        return (_SHOW_PROVIDER_ORDER.index(provider_name), provider_name.value)
    except ValueError:
        return (len(_SHOW_PROVIDER_ORDER), provider_name.value)


def _provider_panel_color_code(provider_name: ProviderName) -> str:
    """
    @brief Resolve ANSI color code for one provider output surface.
    @param provider_name {ProviderName} Provider enum key.
    @return {str} ANSI foreground color code.
    @satisfies REQ-067
    """
    return _PROVIDER_PANEL_COLOR_CODES.get(provider_name, "\033[94m")


def _provider_supports_api_counters(provider_name: ProviderName) -> bool:
    """
    @brief Determine whether provider panels always render API counter lines.
    @details Returns true for providers that expose requests/token counters in
    CLI and GNOME output surfaces, enforcing null-to-zero normalization.
    @param provider_name {ProviderName} Provider enum key.
    @return {bool} True when requests/tokens lines must render on OK state.
    @satisfies REQ-036
    """
    return provider_name in _API_COUNTER_PROVIDERS


def _should_render_cli_progress_bar(provider_name: ProviderName) -> bool:
    """
    @brief Determine whether one CLI usage row must include a progress bar.
    @details Returns true only for providers whose CLI `show` rows use the
    fixed-width bracketed progress-bar surface: `claude`, `openrouter`,
    `copilot`, and `codex`. Returns false for `openai` and `geminiai`, which
    render text-only usage rows. Time complexity O(1). Space complexity O(1).
    @param provider_name {ProviderName} Provider enum key.
    @return {bool} True when CLI usage rendering must include bar glyphs.
    @satisfies REQ-122
    @satisfies REQ-128
    @satisfies REQ-131
    @satisfies REQ-132
    """
    return provider_name in (
        ProviderName.CLAUDE,
        ProviderName.OPENROUTER,
        ProviderName.COPILOT,
        ProviderName.CODEX,
    )


def _build_cli_usage_line(
    provider_name: ProviderName, window_label: str, percent: float
) -> str:
    """
    @brief Build one CLI usage row with provider-specific progress-bar policy.
    @details Uses `_should_render_cli_progress_bar(...)` to emit
    `Usage: <window> <progress_bar> <percent>%` for `claude`, `openrouter`,
    `copilot`, and `codex`. Returns `Usage: <window> <percent>%` for
    `openai/geminiai` so those providers omit progress-bar glyphs while
    preserving explicit window and percentage text. Time complexity O(W) when a
    progress bar is rendered and O(1) otherwise. Space complexity O(W) when a
    progress bar is rendered and O(1) otherwise.
    @param provider_name {ProviderName} Provider enum key.
    @param window_label {str} Effective usage-window label for rendered text.
    @param percent {float} Usage percentage value.
    @return {str} Rendered CLI usage row.
    @satisfies REQ-128
    @satisfies REQ-131
    @satisfies REQ-132
    """
    if not _should_render_cli_progress_bar(provider_name):
        return f"Usage: {window_label} {percent:.1f}%"
    return f"Usage: {window_label} {_progress_bar(percent, provider_name)} {percent:.1f}%"


def _strip_ansi_sequences(value: str) -> str:
    """
    @brief Remove ANSI SGR color escape sequences from terminal text.
    @details Strips `\x1b[...m` segments so panel width calculations can use
    visible glyph length instead of byte length with hidden control codes.
    @param value {str} Input string that may include ANSI color escapes.
    @return {str} String with ANSI SGR escapes removed.
    @satisfies REQ-067
    """
    return _ANSI_ESCAPE_SEQUENCE_PATTERN.sub("", value)


def _visible_text_length(value: str) -> int:
    """
    @brief Compute visible text length for terminal panel alignment.
    @details Calculates string length after ANSI SGR stripping to keep
    bordered-panel width deterministic for colored progress bar rows.
    @param value {str} Input string potentially containing ANSI escapes.
    @return {int} Visible glyph count used by panel width and padding logic.
    @satisfies REQ-067
    """
    return len(_strip_ansi_sequences(value))


def _ansi_ljust(value: str, width: int) -> str:
    """
    @brief Left-pad ANSI-colored text to one visible width.
    @details Appends trailing spaces using visible-length semantics so rows that
    include ANSI escapes align with border columns exactly.
    @param value {str} Source text rendered inside one panel cell.
    @param width {int} Target visible width for the panel cell.
    @return {str} Padded terminal text preserving existing ANSI sequences.
    @satisfies REQ-067
    """
    return value + (" " * max(0, width - _visible_text_length(value)))


def _ansi_rjust(value: str, width: int) -> str:
    """
    @brief Right-pad ANSI-colored text to one visible width.
    @details Prefixes leading spaces using visible-length semantics so rows that
    include ANSI escapes align right to panel content width deterministically.
    @param value {str} Source text rendered inside one panel cell.
    @param width {int} Target visible width for the panel cell.
    @return {str} Right-aligned terminal text preserving ANSI sequences.
    @satisfies REQ-067
    """
    return (" " * max(0, width - _visible_text_length(value))) + value


def _is_right_aligned_panel_line(value: str) -> bool:
    """
    @brief Determine whether one panel body line must render right-aligned.
    @details Marks freshness rows (`Updated: ..., Next: ...`) for right-aligned
    rendering while all other body rows remain left-aligned.
    @param value {str} Panel body line candidate.
    @return {bool} True when line requires right alignment.
    @satisfies REQ-067
    @satisfies REQ-084
    """
    return value.startswith("Updated: ")


def _format_bright_white_bold(value: str) -> str:
    """
    @brief Wrap one metric value with bright-white bold ANSI style.
    @details Applies ANSI SGR sequences for bold (`1`) and bright-white foreground
    (`97`) and appends reset (`0`) for deterministic inline metric emphasis.
    @param value {str} Visible metric value string.
    @return {str} Styled value with ANSI SGR wrappers.
    @satisfies REQ-035
    @satisfies REQ-051
    """
    return f"{_ANSI_BOLD}{_ANSI_BRIGHT_WHITE}{value}{_ANSI_RESET}"


def _wrap_panel_lines(body_lines: list[str], wrap_width: int) -> list[str]:
    """
    @brief Wrap panel body lines to one deterministic visible width.
    @details Applies ANSI-aware wrapping: lines containing ANSI SGR sequences are
    measured by visible glyph length and wrapped on stripped text only when needed.
    @param body_lines {list[str]} Raw panel body lines.
    @param wrap_width {int} Maximum visible width for one wrapped line.
    @return {list[str]} Wrapped panel lines ready for width calculation/rendering.
    @satisfies REQ-067
    """
    wrapped_lines: list[str] = []
    for body_line in body_lines:
        if "\033[" in body_line:
            visible_line = _strip_ansi_sequences(body_line)
            chunks = (
                [body_line]
                if len(visible_line) <= wrap_width
                else textwrap.wrap(visible_line, width=wrap_width)
            )
        else:
            chunks = textwrap.wrap(body_line, width=wrap_width)
        wrapped_lines.extend(chunks or [""])
    return wrapped_lines


def _panel_content_width(title: str, body_lines: list[str]) -> int:
    """
    @brief Resolve one panel visible content width from title and body lines.
    @details Computes width from wrapped visible-line lengths and clamps to
    configured min/max panel boundaries.
    @param title {str} Panel title string.
    @param body_lines {list[str]} Raw body lines for the panel.
    @return {int} Content width used for bordered panel rendering.
    @satisfies REQ-067
    """
    wrap_width = _SHOW_PANEL_MAX_WIDTH - 4
    wrapped_lines = _wrap_panel_lines(body_lines=body_lines, wrap_width=wrap_width)
    content_width = max(
        _SHOW_PANEL_MIN_WIDTH - 4,
        _visible_text_length(title),
        max((_visible_text_length(item) for item in wrapped_lines), default=0),
    )
    return min(content_width, wrap_width)


def _resolve_shared_panel_content_width(
    rendered_panels: list[tuple[ProviderName, str, list[str]]],
) -> int:
    """
    @brief Resolve shared panel width for one CLI show rendering cycle.
    @details Selects the largest computed content width across all rendered
    provider panels, then applies that width to every panel in the cycle.
    @param rendered_panels {list[tuple[ProviderName, str, list[str]]]} Render queue.
    @return {int} Shared content width used by all emitted panels.
    @satisfies REQ-067
    """
    if not rendered_panels:
        return _SHOW_PANEL_MIN_WIDTH - 4
    return max(
        _panel_content_width(title, body_lines)
        for _, title, body_lines in rendered_panels
    )


def _emit_provider_panel(
    provider_name: ProviderName,
    title: str,
    body_lines: list[str],
    content_width: int | None = None,
) -> None:
    """
    @brief Render provider-colored ANSI bordered output panel with wrapped content lines.
    @details Creates fixed-width terminal panels aligned with GNOME extension
    card layout, preserving deterministic borders and line wrapping behavior.
    Border and title color use provider-specific ANSI palette.
    @param provider_name {ProviderName} Provider enum key.
    @param title {str} Panel header text.
    @param body_lines {list[str]} Content lines rendered in panel body.
    @param content_width {int | None} Shared content width override for this panel.
    @return {None} Function return value.
    @satisfies REQ-067
    """
    color_code = _provider_panel_color_code(provider_name)
    wrap_width = _SHOW_PANEL_MAX_WIDTH - 4
    wrapped_lines = _wrap_panel_lines(body_lines=body_lines, wrap_width=wrap_width)
    if content_width is None:
        panel_content_width = _panel_content_width(title=title, body_lines=body_lines)
    else:
        panel_content_width = min(
            max(_SHOW_PANEL_MIN_WIDTH - 4, content_width), wrap_width
        )
    horizontal_border = "─" * (panel_content_width + 2)
    click.echo(f"{color_code}┌{horizontal_border}┐{_ANSI_RESET}")
    click.echo(
        f"{color_code}│{_ANSI_RESET} "
        f"{color_code}{_ansi_ljust(title, panel_content_width)}{_ANSI_RESET} "
        f"{color_code}│{_ANSI_RESET}"
    )
    click.echo(f"{color_code}├{horizontal_border}┤{_ANSI_RESET}")
    for body_line in wrapped_lines:
        padded_line = (
            _ansi_rjust(body_line, panel_content_width)
            if _is_right_aligned_panel_line(body_line)
            else _ansi_ljust(body_line, panel_content_width)
        )
        click.echo(
            f"{color_code}│{_ANSI_RESET} {padded_line} {color_code}│{_ANSI_RESET}"
        )
    click.echo(f"{color_code}└{horizontal_border}┘{_ANSI_RESET}")
    click.echo()


def _format_http_status_retry_line(
    status_code_raw: object,
    retry_after_raw: object,
) -> str | None:
    """
    @brief Build normalized HTTP status/retry diagnostic line for text output.
    @details Returns one deterministic line matching requirement wording:
    `HTTP status: <code>, Retry after: <seconds> sec.` when both values exist.
    @param status_code_raw {object} Status code candidate from result raw payload.
    @param retry_after_raw {object} Retry-after candidate from result raw payload.
    @return {str | None} Diagnostic line or None when both values are missing.
    @satisfies REQ-037
    """
    status_code = status_code_raw if isinstance(status_code_raw, int) else None
    retry_after_seconds = _coerce_retry_after_seconds(retry_after_raw)
    if status_code is not None and retry_after_seconds is not None:
        return f"HTTP status: {status_code}, Retry after: {retry_after_seconds} sec."
    if status_code is not None:
        return f"HTTP status: {status_code}"
    if retry_after_seconds is not None:
        return f"Retry after: {retry_after_seconds} sec."
    return None


def _build_fail_panel_lines(
    result: ProviderResult,
    reason: str,
    freshness_state: IdleTimeState | None,
) -> list[str]:
    """
    @brief Build deterministic CLI body lines for one failed provider panel.
    @details Emits the required failed-state block layout: `Status: FAIL`, blank
    separator, `Reason: <reason>`, blank separator, and one right-aligned
    freshness line (`Updated: ..., Next: ...`) using provider freshness state.
    @param result {ProviderResult} Provider result used for freshness fallback.
    @param reason {str} Normalized failure reason text.
    @param freshness_state {IdleTimeState | None} Optional provider freshness state.
    @return {list[str]} Ordered panel body lines for failed-state rendering.
    @satisfies REQ-036
    @satisfies REQ-084
    """
    freshness_line = _build_freshness_line(
        result=result,
        freshness_state=freshness_state,
    )
    return ["Status: FAIL", "", f"Reason: {reason}", "", freshness_line]


def _extract_copilot_extra_premium_cost(result: ProviderResult) -> float | None:
    """
    @brief Resolve Copilot premium-request overage cost from normalized raw payload.
    @details Computes Copilot overage primarily from `metrics.remaining` semantics:
    `0` when `remaining >= 0`, otherwise `-remaining * unit_cost`. Falls back to
    direct `premium_requests_extra_cost` or
    `max(premium_requests - premium_requests_included, 0) * unit_cost` when
    `remaining` is unavailable.
    @param result {ProviderResult} Copilot provider result candidate.
    @return {float | None} Non-negative overage cost value or None when unavailable.
    @satisfies REQ-012
    @satisfies REQ-129
    """
    if result.provider != ProviderName.COPILOT:
        return None
    raw_payload = result.raw if isinstance(result.raw, dict) else {}
    raw_unit_cost = raw_payload.get("copilot_extra_premium_request_cost")
    unit_cost: float | None = None
    if isinstance(raw_unit_cost, (int, float)) and math.isfinite(float(raw_unit_cost)):
        unit_cost = max(0.0, float(raw_unit_cost))
    if unit_cost is None:
        try:
            unit_cost = max(
                0.0,
                float(load_runtime_config().copilot_extra_premium_request_cost),
            )
        except Exception:
            unit_cost = None

    remaining = result.metrics.remaining
    if isinstance(remaining, (int, float)) and math.isfinite(float(remaining)):
        if float(remaining) >= 0:
            return 0.0
        if unit_cost is None:
            return None
        return max(0.0, -float(remaining)) * unit_cost

    direct_cost = raw_payload.get("premium_requests_extra_cost")
    if isinstance(direct_cost, (int, float)) and math.isfinite(float(direct_cost)):
        return max(0.0, float(direct_cost))

    premium_requests = raw_payload.get("premium_requests")
    premium_requests_included = raw_payload.get("premium_requests_included")
    if not isinstance(premium_requests, (int, float)):
        return None
    if not isinstance(premium_requests_included, (int, float)):
        return None
    if not math.isfinite(float(premium_requests)):
        return None
    if not math.isfinite(float(premium_requests_included)):
        return None
    if unit_cost is None:
        return None

    premium_requests_extra = max(
        0.0,
        float(premium_requests) - float(premium_requests_included),
    )
    return premium_requests_extra * unit_cost


def _build_copilot_extra_premium_cost_line(result: ProviderResult) -> str | None:
    """
    @brief Build CLI Copilot cost row from premium-request overage payload fields.
    @details Formats fallback Copilot cost text as `Cost: <currency><value>` when
    `metrics.cost` is unavailable and overage fields can still be resolved from raw payload.
    @param result {ProviderResult} Copilot provider result candidate.
    @return {str | None} Formatted row `Cost: ...` or None.
    @satisfies REQ-129
    """
    extra_cost = _extract_copilot_extra_premium_cost(result)
    if extra_cost is None:
        return None
    currency_symbol = result.metrics.currency_symbol
    return "Cost: " + _format_bright_white_bold(f"{currency_symbol}{extra_cost:.4f}")


def _build_result_panel(
    name: ProviderName,
    result: ProviderResult,
    label: str | None = None,
    freshness_state: IdleTimeState | None = None,
) -> tuple[str, list[str]]:
    """
    @brief Build one provider panel title/body payload for CLI text rendering.
    @details Formats deterministic panel lines for one provider/window result and
    preserves provider-specific metrics/error rendering rules used by `show`.
    `FAIL` states emit `Status: FAIL`, `Reason: <reason>`, and `Updated/Next`
    separated by blank lines. `OK` states emit `Status: OK` first, render
    `claude/openrouter/copilot/codex` usage rows as
    `Usage: <window> <progress_bar> <percent>%`, render `openai/geminiai`
    usage rows as `Usage: <window> <percent>%`, do not emit `Window <window>`
    headings, insert one blank separator between Copilot `Remaining credits`
    and `Cost` rows, and end with one right-aligned freshness line.
    @param name {ProviderName} Provider name enum value.
    @param result {ProviderResult} Provider result to render.
    @param label {str | None} Optional window label suffix (e.g. `"5h"`, `"7d"`).
    @param freshness_state {IdleTimeState | None} Optional provider idle-time state
        carrying `last_success_timestamp` and `idle_until_timestamp` freshness values.
    @return {tuple[str, list[str]]} Panel title and body lines.
    @satisfies REQ-084
    @satisfies REQ-034
    @satisfies REQ-035
    @satisfies REQ-036
    @satisfies REQ-051
    @satisfies REQ-012
    @satisfies REQ-060
    @satisfies REQ-067
    @satisfies REQ-084
    @satisfies REQ-128
    @satisfies REQ-129
    @satisfies REQ-131
    @satisfies REQ-132
    """
    title = _provider_display_name(name)
    if label:
        title = f"{title} ({label})"

    detail_lines: list[str] = []
    if result.is_error:
        reason_text = result.error if isinstance(result.error, str) else "Unknown error"
        return title, _build_fail_panel_lines(
            result=result,
            reason=reason_text,
            freshness_state=freshness_state,
        )

    freshness_line = _build_freshness_line(
        result=result, freshness_state=freshness_state
    )

    m = result.metrics
    if m.usage_percent is not None:
        pct = m.usage_percent
        usage_window_label = label or result.window.value
        detail_lines.append(_build_cli_usage_line(name, usage_window_label, pct))

    if m.reset_at:
        delta = m.reset_at - datetime.now(timezone.utc)
        if delta.total_seconds() > 0:
            reset_value = _format_reset_duration(delta.total_seconds())
            detail_lines.append(f"Resets in: {reset_value}")
    elif _should_print_claude_reset_pending_hint(name, m):
        detail_lines.append(f"Resets in: {_RESET_PENDING_MESSAGE}")

    if (
        name
        in (
            ProviderName.CLAUDE,
            ProviderName.CODEX,
            ProviderName.COPILOT,
        )
        and m.remaining is not None
        and m.limit is not None
    ):
        if detail_lines and detail_lines[-1].startswith("Resets in: "):
            detail_lines.append("")
        # Legacy source-pattern anchor: lines.append(f"Remaining credits: {m.remaining:.1f} / {m.limit:.1f}")
        detail_lines.append(
            f"Remaining credits: {_format_bright_white_bold(f'{m.remaining:.1f}')} / {m.limit:.1f}"
        )

    copilot_has_remaining_credits = (
        name == ProviderName.COPILOT
        and bool(detail_lines)
        and detail_lines[-1].startswith("Remaining credits: ")
    )

    if m.cost is not None:
        if copilot_has_remaining_credits:
            detail_lines.append("")
            copilot_has_remaining_credits = False
        if name == ProviderName.OPENROUTER and m.limit is not None:
            detail_lines.append(
                f"Cost: {_format_bright_white_bold(f'{m.currency_symbol}{m.cost:.4f}')} / "
                f"{_format_bright_white_bold(f'{m.currency_symbol}{m.limit:.2f}')}"
            )
        else:
            detail_lines.append(
                f"Cost: {_format_bright_white_bold(f'{m.currency_symbol}{m.cost:.4f}')}"
            )

    if name == ProviderName.COPILOT and m.cost is None:
        copilot_extra_cost_line = _build_copilot_extra_premium_cost_line(result)
        if copilot_extra_cost_line is not None:
            if copilot_has_remaining_credits:
                detail_lines.append("")
                copilot_has_remaining_credits = False
            detail_lines.append(copilot_extra_cost_line)

    if _provider_supports_api_counters(name):
        requests_count = m.requests if m.requests is not None else 0
        input_tokens = m.input_tokens if m.input_tokens is not None else 0
        output_tokens = m.output_tokens if m.output_tokens is not None else 0
        total_tokens = input_tokens + output_tokens
        detail_lines.append(f"Requests: {requests_count:,}")
        detail_lines.append(
            f"Tokens: {total_tokens:,} ({input_tokens:,} in / {output_tokens:,} out)"
        )
    else:
        if m.requests is not None:
            detail_lines.append(f"Requests: {m.requests:,}")
        if m.input_tokens is not None or m.output_tokens is not None:
            total = (m.input_tokens or 0) + (m.output_tokens or 0)
            detail_lines.append(
                f"Tokens: {total:,} ({m.input_tokens or 0:,} in / {m.output_tokens or 0:,} out)"
            )

    raw_data = result.raw.get("data")
    if name == ProviderName.OPENROUTER and isinstance(raw_data, dict):
        byok_key_map = {
            WindowPeriod.HOUR_5: "byok_usage_daily",
            WindowPeriod.DAY_7: "byok_usage_weekly",
            WindowPeriod.DAY_30: "byok_usage_monthly",
        }
        byok_raw = raw_data.get(byok_key_map.get(result.window, "byok_usage_weekly"))
        if isinstance(byok_raw, (int, float)) and byok_raw > 0:
            detail_lines.append(f"BYOK: {m.currency_symbol}{float(byok_raw):.4f}")

    if name == ProviderName.GEMINIAI:
        monitoring_raw = result.raw.get("monitoring")
        if isinstance(monitoring_raw, dict):
            latency_total = monitoring_raw.get("latency_total")
            error_total = monitoring_raw.get("error_total")
            if isinstance(latency_total, (int, float)):
                detail_lines.append(
                    f"Monitoring latency total: {float(latency_total):.2f}"
                )
            if isinstance(error_total, (int, float)):
                detail_lines.append(f"Monitoring error total: {float(error_total):.2f}")
        billing_raw = result.raw.get("billing")
        if isinstance(billing_raw, dict):
            table_id = billing_raw.get("table_id")
            table_path = billing_raw.get("table_path")
            services = billing_raw.get("services")
            if isinstance(table_id, str) and table_id:
                if detail_lines and detail_lines[-1] != "":
                    detail_lines.append("")
                detail_lines.append(f"Billing table: {table_id}")
            if isinstance(table_path, str) and table_path:
                detail_lines.append(f"Billing path: {table_path}")
            if isinstance(services, list):
                services_summary = _format_billing_service_descriptions(services)
                if services_summary is None:
                    detail_lines.append(f"Billing services: {len(services)}")
                else:
                    detail_lines.append(
                        f"Billing services: {len(services)} ({services_summary})"
                    )

    if not result.is_error:
        status_retry_line = _format_http_status_retry_line(
            result.raw.get("status_code"),
            result.raw.get("retry_after_seconds"),
        )
        if status_retry_line is not None:
            detail_lines.append(status_retry_line)

    return title, ["Status: OK", "", *detail_lines, "", freshness_line]


def _format_billing_service_descriptions(services: list[object]) -> str | None:
    """
    @brief Build human-readable GeminiAI billing service summary.
    @details Extracts ordered `service_description` values from billing service
    entries and returns all valid names in source order as one comma-separated
    summary string.
    @param services {list[object]} Billing service entries from GeminiAI raw
        billing payload.
    @return {str | None} Comma-separated service names summary without
        surrounding parentheses, or `None` when no valid names exist.
    @satisfies REQ-106
    """
    service_names: list[str] = []
    for service_entry in services:
        if not isinstance(service_entry, dict):
            continue
        service_name_raw = service_entry.get("service_description")
        if not isinstance(service_name_raw, str):
            continue
        service_name = service_name_raw.strip()
        if not service_name:
            continue
        service_names.append(service_name)
    if not service_names:
        return None
    return ", ".join(service_names)


def _build_dual_window_section(
    window_label: str,
    detail_lines: list[str],
) -> list[str]:
    """
    @brief Build one labeled dual-window CLI section.
    @details Prepends the raw window label (`5h` or `7d`) to the ordered detail
    lines for one Claude/Codex section. The helper intentionally preserves
    duplicate metric text across sections so identical `Usage` or `Resets in`
    rows remain visible in both windows.
    @param window_label {str} Window label text rendered as the section heading.
    @param detail_lines {list[str]} Ordered non-empty detail lines for one window.
    @return {list[str]} Section heading followed by the provided detail lines.
    @satisfies REQ-002
    """
    return [window_label, *detail_lines]


def _build_dual_window_panel(
    name: ProviderName,
    result_5h: ProviderResult,
    result_7d: ProviderResult,
    freshness_state: IdleTimeState | None = None,
) -> tuple[str, list[str]]:
    """
    @brief Build one grouped CLI panel for dual-window providers.
    @details Produces one provider panel from `5h` and `7d` results while
    keeping explicit `5h` and `7d` section labels and preserving duplicate
    section content when both windows render identical metric text. `FAIL`
    states emit `Status: FAIL`, `Reason: <reason>`, and `Updated/Next`
    separated by blank lines. `OK` states emit `Status: OK` first, preserve
    usage rows formatted as `Usage: <window> <progress_bar> <percent>%`, avoid
    `Window <window>` headings, and append one trailing right-aligned freshness
    line.
    @param name {ProviderName} Provider enum value.
    @param result_5h {ProviderResult} Five-hour provider result.
    @param result_7d {ProviderResult} Seven-day provider result.
    @param freshness_state {IdleTimeState | None} Optional provider freshness state.
    @return {tuple[str, list[str]]} Provider title and grouped body lines.
    @satisfies REQ-002
    @satisfies REQ-035
    @satisfies REQ-067
    @satisfies REQ-084
    @satisfies REQ-128
    @satisfies REQ-129
    """
    title = _provider_display_name(name)
    if result_5h.is_error or result_7d.is_error:
        primary_error = (
            result_5h.error
            if result_5h.is_error and isinstance(result_5h.error, str)
            else result_7d.error
        )
        reason_text = (
            primary_error if isinstance(primary_error, str) else "Unknown error"
        )
        return title, _build_fail_panel_lines(
            result=result_7d,
            reason=reason_text,
            freshness_state=freshness_state,
        )

    _title_5h, lines_5h = _build_result_panel(
        name=name,
        result=result_5h,
        label="5h",
        freshness_state=freshness_state,
    )
    _title_7d, lines_7d = _build_result_panel(
        name=name,
        result=result_7d,
        label="7d",
        freshness_state=freshness_state,
    )
    details_5h = [
        line
        for line in lines_5h
        if line
        and not line.startswith("Status: ")
        and not line.startswith("Updated: ")
        and not line.startswith("Window ")
    ]
    details_7d = [
        line
        for line in lines_7d
        if line
        and not line.startswith("Status: ")
        and not line.startswith("Updated: ")
        and not line.startswith("Window ")
    ]
    metric_prefixes = ("Cost: ", "Requests: ", "Tokens: ")
    remaining_prefix = "Remaining credits: "
    shared_remaining_line: str | None = None
    if name in {ProviderName.CLAUDE, ProviderName.CODEX}:
        if not result_5h.is_error and not result_7d.is_error:
            shared_remaining_line = next(
                (line for line in details_7d if line.startswith(remaining_prefix)),
                None,
            )
        details_5h = [
            line for line in details_5h if not line.startswith(remaining_prefix)
        ]
        details_7d = [
            line for line in details_7d if not line.startswith(remaining_prefix)
        ]
    footer_lines: list[str] = []
    if name == ProviderName.CODEX:
        footer_lines = [line for line in details_7d if line.startswith(metric_prefixes)]
        details_5h = [
            line for line in details_5h if not line.startswith(metric_prefixes)
        ]
        details_7d = [
            line for line in details_7d if not line.startswith(metric_prefixes)
        ]
    section_5h = _build_dual_window_section("5h", details_5h)
    section_7d = _build_dual_window_section("7d", details_7d)
    freshness_line = _build_freshness_line(
        result=result_7d, freshness_state=freshness_state
    )
    body_lines = ["Status: OK", "", *section_5h, "", *section_7d]
    if shared_remaining_line is not None:
        body_lines.extend(["", shared_remaining_line])
    if footer_lines:
        body_lines.extend(["", *footer_lines])
    body_lines.extend(["", freshness_line])
    return title, body_lines


def _print_result(name: ProviderName, result, label: str | None = None) -> None:
    """
    @brief Render CLI text output for one provider result.
    @details Formats provider-specific usage text, reset countdown, remaining
    credits, cost, requests, and token counts for one provider/window result.
    `openai/geminiai` usage rows omit progress bars while other providers keep
    existing bar rendering. Cost is formatted using `metrics.currency_symbol`
    (never hardcoded `$`).
    @param name {ProviderName} Provider name enum value.
    @param result {ProviderResult} Provider result to render.
    @param label {str | None} Optional window label suffix (e.g. `"5h"`, `"7d"`).
    @return {None} Function return value.
    @satisfies REQ-034
    @satisfies REQ-035
    @satisfies REQ-051
    @satisfies REQ-067
    @satisfies REQ-128
    @satisfies REQ-129
    @satisfies REQ-131
    @satisfies REQ-132
    """
    title, lines = _build_result_panel(name, result, label)
    _emit_provider_panel(provider_name=name, title=title, body_lines=lines)


def _format_reset_duration(seconds: float) -> str:
    """
    @brief Execute format reset duration.
    @details Applies format reset duration logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @param seconds {float} Input parameter `seconds`.
    @return {str} Function return value.
    """
    total_minutes = int(seconds // 60)
    days = total_minutes // (24 * 60)
    hours = (total_minutes // 60) % 24
    minutes = total_minutes % 60
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    return f"{hours}h {minutes}m"


def _should_print_claude_reset_pending_hint(
    provider_name: ProviderName,
    metrics: UsageMetrics,
) -> bool:
    """
    @brief Determine whether CLI output must render the reset-pending fallback hint.
    @details The hint is only valid for Claude windows when no reset timestamp is
    available yet and usage is exactly zero, which indicates the rate-limit timer has
    not started. This preserves the normal countdown path for non-zero usage and for
    providers other than Claude.
    @param provider_name {ProviderName} Provider associated with the rendered result.
    @param metrics {UsageMetrics} Normalized quota metrics for the rendered result.
    @return {bool} True when CLI must print `Resets in: Starts when the first message is sent`.
    @satisfies REQ-002
    """
    if provider_name != ProviderName.CLAUDE:
        return False
    if metrics.reset_at is not None:
        return False
    return _is_displayed_zero_percent(metrics.usage_percent)


def _is_displayed_zero_percent(percent: float | None) -> bool:
    """
    @brief Check whether a percentage renders as `0.0%` in one-decimal UI output.
    @details Uses the same one-decimal rounding semantic as output formatting. This
    treats small non-zero percentages (e.g. 0.04) as displayed zero, which is required
    for consistent reset-pending fallback visibility between CLI and GNOME UI.
    @param percent {float | None} Raw percentage value.
    @return {bool} True when `percent` is finite, non-negative, and rounds to `0.0`.
    @satisfies REQ-002
    """
    if percent is None or not math.isfinite(percent):
        return False
    if percent < 0:
        return False
    return round(percent, 1) == 0.0


def _progress_bar_layout(percent: float, width: int) -> tuple[int, int, int]:
    """
    @brief Compute fixed-width CLI progress-bar segment widths.
    @details Normalizes `percent` to a non-negative finite value. Percentages up to
    `100` allocate provider-color fill plus empty cells. Percentages above `100`
    allocate one 100%-boundary marker cell and one over-limit segment scaled across
    the extra `0..100` range, clamped for larger values, and forced visible for any
    positive over-limit usage. Time complexity O(1). Space complexity O(1).
    @param percent {float} Raw usage percentage.
    @param width {int} Total cell width inside the surrounding brackets.
    @return {tuple[int, int, int]} Tuple `(base_width, over_limit_width, marker_width)`.
    @satisfies REQ-122
    """
    safe_width = max(0, width)
    if safe_width == 0 or not math.isfinite(percent):
        return 0, 0, 0

    normalized_percent = max(0.0, percent)
    if normalized_percent <= 100.0:
        base_width = min(safe_width, int(safe_width * normalized_percent / 100))
        return base_width, 0, 0

    marker_width = 1
    available_width = max(0, safe_width - marker_width)
    over_limit_percent = min(normalized_percent - 100.0, 100.0)
    over_limit_width = int(round((over_limit_percent / 100.0) * available_width))
    if over_limit_percent > 0 and available_width > 0:
        over_limit_width = max(1, over_limit_width)
    over_limit_width = min(available_width, over_limit_width)
    base_width = max(0, available_width - over_limit_width)
    return base_width, over_limit_width, marker_width


def _progress_bar(percent: float, provider_name: ProviderName, width: int = 20) -> str:
    """
    @brief Render one fixed-width CLI usage bar.
    @details Uses provider-color fill for in-limit usage. Percentages above `100`
    preserve fixed bar width by rendering a bright-white `|` marker at the 100%
    boundary and a neutral shaded over-limit segment (`▓`) inside the same bar.
    Time complexity O(width). Space complexity O(width).
    @param percent {float} Raw usage percentage.
    @param provider_name {ProviderName} Provider enum key for base-fill color mapping.
    @param width {int} Total cell width inside the surrounding brackets.
    @return {str} ANSI-colored progress bar string.
    @satisfies REQ-122
    @satisfies REQ-128
    """
    base_width, over_limit_width, marker_width = _progress_bar_layout(percent, width)
    color_code = _provider_panel_color_code(provider_name)
    if marker_width == 0:
        empty_width = max(0, width - base_width)
        return f"[{color_code}{'█' * base_width}{_ANSI_RESET}{'░' * empty_width}]"

    marker = f"{_ANSI_BOLD}{_ANSI_BRIGHT_WHITE}|{_ANSI_RESET}"
    over_limit_fill = f"\033[90m{'▓' * over_limit_width}{_ANSI_RESET}"
    return f"[{color_code}{'█' * base_width}{_ANSI_RESET}{marker}{over_limit_fill}]"


@main.command(
    short_help="Run provider diagnostics.",
    help="Run per-provider configuration checks and 5h fetch diagnostics.",
)
def doctor() -> None:
    """
    @brief Execute doctor.
    @details Applies doctor logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {None} Function return value.
    """
    click.echo("Usage UI Doctor")
    click.echo("=" * 40)
    click.echo()

    providers = get_providers()
    all_ok = True

    for name, provider in providers.items():
        info = config.get_provider_status(name)

        click.echo(f"{click.style(info['name'], bold=True)}")

        # Check configuration
        if info["configured"]:
            click.echo(
                f"  Config:     {click.style('OK', fg='green')} ({info['token_preview']})"
            )
        else:
            click.echo(f"  Config:     {click.style('MISSING', fg='red')}")
            click.echo(f"              Set: {info['env_var']}")
            all_ok = False
            click.echo()
            continue

        # Test connectivity
        click.echo("  Testing:    ", nl=False)
        result = _fetch_result(provider, WindowPeriod.HOUR_5)
        if result.is_error:
            click.echo(click.style(f"FAILED - {result.error}", fg="red"))
            all_ok = False
        else:
            click.echo(click.style("OK", fg="green"))

        # Show notes
        if info.get("note"):
            click.echo(f"  Note:       {info['note']}")

        click.echo()

    # Summary
    click.echo("-" * 40)
    if all_ok:
        click.echo(click.style("All providers healthy!", fg="green"))
    else:
        click.echo(click.style("Some providers need attention.", fg="yellow"))


@main.command(
    short_help="Show environment variable guidance.",
    help="Print provider environment-variable configuration guidance.",
)
def env() -> None:
    """
    @brief Execute env.
    @details Applies env logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {None} Function return value.
    """
    click.echo(config.get_env_var_help())


@main.command(
    short_help="Run interactive setup.",
    help="Configure runtime settings, currency symbols, and provider credentials.",
)
def setup() -> None:
    """
    @brief Execute setup.
    @details Prompts dedicated provider-activation section first, then prompts
    `idle_delay_seconds`, `api_call_delay_milliseconds`,
    `api_call_timeout_milliseconds`, `default_retry_after_seconds`,
    `gnome_refresh_interval_seconds`, and `billing_data` in order, then prompts
    dedicated Copilot overage pricing field `copilot_extra_premium_request_cost`
    (USD/request), then prompts provider currency symbols including `geminiai`
    (choices: `$`, `£`, `€`, default `$`), then persists all values to
    `~/.config/aibar/config.json`. Final setup section configures logging flags
    (`log_enabled`, `debug_enabled`). GeminiAI OAuth source supports `skip`,
    `file`, `paste`, and `login` (re-authorization with current scopes). Also
    prompts for provider API keys and writes them to `~/.config/aibar/env`.
    @return {None} Function return value.
    @satisfies REQ-005
    @satisfies REQ-049
    @satisfies REQ-123
    @satisfies REQ-108
    @satisfies REQ-116
    @satisfies REQ-055
    @satisfies REQ-056
    @satisfies REQ-059
    """
    from aibar.config import (
        ENV_FILE_PATH,
        RUNTIME_CONFIG_PATH,
        RuntimeConfig,
        VALID_CURRENCY_SYMBOLS,
        load_runtime_config,
        resolve_enabled_providers,
        save_runtime_config,
        write_env_file,
    )
    from aibar.providers.geminiai import GEMINIAI_OAUTH_SCOPES, GeminiAICredentialStore

    click.echo()
    click.echo("Usage UI Setup")
    click.echo("=" * 40)
    click.echo()
    click.echo(f"Keys will be saved to: {ENV_FILE_PATH}")
    click.echo(f"Runtime settings will be saved to: {RUNTIME_CONFIG_PATH}")
    click.echo("Press Enter to skip any key.")
    click.echo()

    runtime_config = load_runtime_config()
    click.echo(click.style("Provider activation", bold=True))
    click.echo("  Configure whether each provider participates in refresh and UI output.")
    configured_enabled_providers = resolve_enabled_providers(runtime_config)
    activation_provider_order = [
        ProviderName.CLAUDE,
        ProviderName.OPENROUTER,
        ProviderName.COPILOT,
        ProviderName.CODEX,
        ProviderName.OPENAI,
        ProviderName.GEMINIAI,
    ]
    enabled_providers: dict[str, bool] = {}
    for activation_provider in activation_provider_order:
        activation_default = (
            "enable"
            if configured_enabled_providers.get(activation_provider.value, True)
            else "disable"
        )
        activation_mode = click.prompt(
            f"  {activation_provider.value} statistics mode",
            type=click.Choice(["enable", "disable"]),
            default=activation_default,
            show_choices=True,
        )
        enabled_providers[activation_provider.value] = activation_mode == "enable"
    click.echo()
    click.echo(click.style("Runtime throttling", bold=True))
    click.echo(
        "  idle-delay controls cache-only mode duration after successful refresh."
    )
    click.echo(
        "  api-call delay controls minimum spacing between API calls in milliseconds."
    )
    click.echo(
        "  api-call timeout controls HTTP response timeout for provider API calls."
    )
    click.echo(
        "  default-retry-after controls fallback delay when API errors omit Retry-After."
    )
    click.echo("  gnome-refresh-interval controls GNOME extension auto-refresh rate.")
    idle_delay_seconds = click.prompt(
        "  idle-delay seconds",
        type=int,
        default=runtime_config.idle_delay_seconds,
    )
    api_call_delay_milliseconds = click.prompt(
        "  api-call delay milliseconds",
        type=int,
        default=runtime_config.api_call_delay_milliseconds,
    )
    api_call_timeout_milliseconds = click.prompt(
        "  api-call timeout milliseconds",
        type=int,
        default=runtime_config.api_call_timeout_milliseconds,
    )
    default_retry_after_seconds = click.prompt(
        "  default-retry-after seconds",
        type=int,
        default=runtime_config.default_retry_after_seconds,
    )
    gnome_refresh_interval_seconds = click.prompt(
        "  gnome-refresh-interval seconds",
        type=int,
        default=runtime_config.gnome_refresh_interval_seconds,
    )
    billing_data = (
        click.prompt(
            "  billing_data",
            default=runtime_config.billing_data,
            show_default=True,
        ).strip()
        or runtime_config.billing_data
    )
    click.echo()
    click.echo(click.style("Copilot premium overage", bold=True))
    click.echo(
        "  Configure extra cost per Copilot premium request above included plan quota."
    )
    copilot_extra_premium_request_cost = click.prompt(
        "  copilot extra premium request cost (USD/request)",
        type=float,
        default=runtime_config.copilot_extra_premium_request_cost,
        show_default=True,
    )
    click.echo()
    click.echo(click.style("Currency symbols", bold=True))
    click.echo("  Configure the default currency symbol for cost display per provider.")
    click.echo(f"  Valid choices: {', '.join(VALID_CURRENCY_SYMBOLS)}")
    _currency_provider_names = [p.value for p in ProviderName]
    currency_symbols: dict[str, str] = {}
    for _provider_name in _currency_provider_names:
        _current_symbol = runtime_config.currency_symbols.get(_provider_name, "$")
        _chosen = click.prompt(
            f"  {_provider_name} currency symbol",
            type=click.Choice(list(VALID_CURRENCY_SYMBOLS)),
            default=_current_symbol,
            show_choices=True,
        )
        currency_symbols[_provider_name] = _chosen

    geminiai_project_id = runtime_config.geminiai_project_id
    credential_store = GeminiAICredentialStore()

    click.echo()
    click.echo(click.style("GeminiAI (Google Cloud OAuth)", bold=True))
    click.echo(
        "  Configure OAuth desktop client JSON for Cloud Monitoring and BigQuery billing access."
    )
    click.echo(
        "  billing_data must be the dataset name created in Google BigQuery console."
    )
    oauth_source = click.prompt(
        "  geminiai oauth source",
        type=click.Choice(["skip", "file", "paste", "login"]),
        default="skip",
        show_choices=True,
    )
    if oauth_source == "skip":
        click.echo("  -> Skipped")
    else:
        client_payload_raw: dict[str, object] | None = None
        if oauth_source == "login":
            if not credential_store.has_client_config():
                click.echo(
                    click.style(
                        "  -> GeminiAI OAuth client config not found.", fg="red"
                    )
                )
                click.echo(
                    "  -> Configure OAuth client with source 'file' or 'paste' first."
                )
            else:
                try:
                    credential_store.authorize_interactively(
                        scopes=GEMINIAI_OAUTH_SCOPES
                    )
                    click.echo("  -> OAuth token saved")
                except (FileNotFoundError, ValueError, OSError, ProviderError) as exc:
                    click.echo(
                        click.style(
                            f"  -> GeminiAI OAuth setup failed: {exc}", fg="red"
                        )
                    )
        elif oauth_source == "file":
            default_path = str(credential_store.client_config_path)
            oauth_path_raw = click.prompt(
                "  geminiai oauth client json path",
                default=default_path,
                show_default=True,
            ).strip()
            try:
                client_payload_raw = json.loads(
                    Path(oauth_path_raw).read_text(encoding="utf-8")
                )
            except OSError as exc:
                click.echo(click.style(f"  -> OAuth file error: {exc}", fg="red"))
            except ValueError as exc:
                click.echo(
                    click.style(f"  -> OAuth JSON decode error: {exc}", fg="red")
                )
        else:
            pasted_json = click.prompt(
                "  geminiai oauth client json (single-line)",
                default="",
                show_default=False,
            ).strip()
            if pasted_json:
                try:
                    client_payload_raw = json.loads(pasted_json)
                except ValueError as exc:
                    click.echo(
                        click.style(f"  -> OAuth JSON decode error: {exc}", fg="red")
                    )

        if client_payload_raw is not None:
            try:
                credential_store.save_client_config(client_payload_raw)
                saved_payload = credential_store.load_client_config()
                detected_project_id = credential_store.extract_project_id(saved_payload)
                if detected_project_id is not None:
                    geminiai_project_id = detected_project_id
                click.echo("  -> OAuth client saved")
                if click.confirm(
                    "  Open browser and authorize GeminiAI now?", default=True
                ):
                    credential_store.authorize_interactively(
                        scopes=GEMINIAI_OAUTH_SCOPES
                    )
                    click.echo("  -> OAuth token saved")
            except (FileNotFoundError, ValueError, OSError, ProviderError) as exc:
                click.echo(
                    click.style(f"  -> GeminiAI OAuth setup failed: {exc}", fg="red")
                )

        project_default = geminiai_project_id or ""
        project_input = click.prompt(
            "  geminiai project id",
            default=project_default,
            show_default=bool(project_default),
        ).strip()
        geminiai_project_id = project_input or None

    updates: dict[str, str] = {}

    # OpenRouter API key
    click.echo(click.style("OpenRouter", bold=True))
    click.echo("  Get your API key from: https://openrouter.ai/keys")
    openrouter_key = click.prompt(
        "  OPENROUTER_API_KEY", default="", show_default=False
    ).strip()
    if openrouter_key:
        updates["OPENROUTER_API_KEY"] = openrouter_key
        click.echo("  -> Set")
    else:
        click.echo("  -> Skipped")
    click.echo()

    # OpenAI Admin key
    click.echo(click.style("OpenAI", bold=True))
    click.echo("  Requires organization admin API key.")
    click.echo(
        "  Get it from: https://platform.openai.com/settings/organization/admin-keys"
    )
    openai_key = click.prompt(
        "  OPENAI_ADMIN_KEY", default="", show_default=False
    ).strip()
    if openai_key:
        updates["OPENAI_ADMIN_KEY"] = openai_key
        click.echo("  -> Set")
    else:
        click.echo("  -> Skipped")
    click.echo()

    # GitHub token (optional)
    click.echo(click.style("GitHub Copilot", bold=True))
    click.echo("  Optional: provide a GitHub token, or use device flow login later.")
    click.echo("  Recommended: run 'aibar login --provider copilot' instead.")
    github_token = click.prompt(
        "  GITHUB_TOKEN", default="", show_default=False
    ).strip()
    if github_token:
        updates["GITHUB_TOKEN"] = github_token
        click.echo("  -> Set")
    else:
        click.echo("  -> Skipped")
    click.echo()

    # Claude - print instructions only
    click.echo(click.style("Claude Code", bold=True))
    click.echo("  Uses Claude CLI credentials automatically.")
    click.echo("  To set up:")
    click.echo("    npm install -g @anthropics/claude")
    click.echo("    claude setup-token")
    click.echo()

    # Codex - print instructions only
    click.echo(click.style("OpenAI Codex", bold=True))
    click.echo("  Uses Codex CLI credentials automatically.")
    click.echo("  To set up:")
    click.echo("    npm install -g @openai/codex")
    click.echo("    codex")
    click.echo()

    # Write to env file
    if updates:
        write_env_file(updates)
        click.echo("-" * 40)
        click.echo(click.style("Configuration saved!", fg="green"))
        click.echo(f"File: {ENV_FILE_PATH}")
        click.echo()
        click.echo("Keys saved:")
        for key in updates:
            click.echo(f"  {key}: set")
    else:
        click.echo("-" * 40)
        click.echo("No keys provided. Nothing saved.")

    click.echo()
    click.echo(click.style("Logging", bold=True))
    click.echo("  Configure runtime execution logging and API debug logging.")
    log_mode = click.prompt(
        "  execution log mode",
        type=click.Choice(["enable", "disable"]),
        default="enable" if runtime_config.log_enabled else "disable",
        show_choices=True,
    )
    debug_mode = click.prompt(
        "  debug api log mode",
        type=click.Choice(["enable", "disable"]),
        default="enable" if runtime_config.debug_enabled else "disable",
        show_choices=True,
    )
    configured_runtime = RuntimeConfig(
        idle_delay_seconds=idle_delay_seconds,
        api_call_delay_milliseconds=api_call_delay_milliseconds,
        api_call_timeout_milliseconds=api_call_timeout_milliseconds,
        default_retry_after_seconds=default_retry_after_seconds,
        gnome_refresh_interval_seconds=gnome_refresh_interval_seconds,
        billing_data=billing_data,
        enabled_providers=enabled_providers,
        copilot_extra_premium_request_cost=copilot_extra_premium_request_cost,
        currency_symbols=currency_symbols,
        log_enabled=(log_mode == "enable"),
        debug_enabled=(debug_mode == "enable"),
        geminiai_project_id=geminiai_project_id,
    )
    save_runtime_config(configured_runtime)
    click.echo("  -> Runtime settings saved")

    click.echo()
    click.echo("Next steps:")
    click.echo("  aibar show --json")
    click.echo("  aibar show")
    click.echo("  aibar doctor")


@main.command(
    short_help="Authenticate provider accounts.",
    help="Authenticate supported providers (claude, copilot, geminiai).",
)
@click.option(
    "--provider",
    "-p",
    default="claude",
    help="Provider to login to (claude, copilot, geminiai)",
)
def login(provider: str) -> None:
    """
    @brief Execute login.
    @details Applies login logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @param provider {str} Input parameter `provider`.
    @return {None} Function return value.
    """
    if provider == "claude":
        _login_claude()
    elif provider == "copilot":
        _login_copilot()
    elif provider == "geminiai":
        _login_geminiai()
    else:
        click.echo(f"Login not supported for provider: {provider}")
        click.echo("Supported providers: claude, copilot, geminiai")
        sys.exit(1)


def _login_claude() -> None:
    """
    @brief Execute login claude.
    @details Applies login claude logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {None} Function return value.
    """
    from aibar.claude_cli_auth import ClaudeCLIAuth

    auth = ClaudeCLIAuth()

    if not auth.is_available():
        click.echo(click.style("\n Claude CLI credentials not found", fg="red"))
        click.echo()
        click.echo("To set up Claude CLI:")
        click.echo("  1. Install: npm install -g @anthropics/claude")
        click.echo("  2. Authenticate: claude setup-token")
        click.echo("  3. Then run 'aibar login' again")
        sys.exit(1)

    info = auth.get_token_info()

    if info["expired"]:
        click.echo(click.style("\n Token expired", fg="yellow"))
        click.echo()
        click.echo("Run this to refresh:")
        click.echo("  claude setup-token")
        sys.exit(1)

    token = auth.get_access_token()

    if token:
        click.echo()
        click.echo("=" * 60)
        click.echo(click.style(" Token extracted successfully!", fg="green", bold=True))
        click.echo()
        click.echo(f"  Token:      {token[:15]}...")
        if expires_in := info.get("expires_in_hours"):
            click.echo(f"  Expires in: {expires_in} hours")
        if scopes := info.get("scopes"):
            click.echo(f"  Scopes:     {', '.join(scopes)}")
        click.echo()
        click.echo("Token auto-loaded from ~/.claude/.credentials.json")
        click.echo("You can now run: aibar show --provider claude")
        click.echo("=" * 60)
    else:
        click.echo(click.style("\n Could not extract token", fg="red"))
        sys.exit(1)


def _login_copilot() -> None:
    """
    @brief Execute login copilot.
    @details Applies login copilot logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {None} Function return value.
    """
    from aibar.providers.copilot import CopilotProvider

    click.echo()
    click.echo("GitHub Copilot Login")
    click.echo("=" * 40)
    click.echo()

    provider = CopilotProvider()

    try:
        asyncio.run(provider.login())
        click.echo()
        click.echo(click.style(" Login successful!", fg="green", bold=True))
        click.echo()
        click.echo("  Token saved to: ~/.config/aibar/copilot.json")
        click.echo()
        click.echo("You can now run: aibar show --provider copilot")
    except Exception as e:
        click.echo(click.style(f"\n Login failed: {e}", fg="red"))
        sys.exit(1)


def _login_geminiai() -> None:
    """
    @brief Execute GeminiAI OAuth login flow.
    @details Reuses persisted OAuth client configuration to launch browser-based
    authorization and persist refresh-capable Google credentials.
    @return {None} Function return value.
    @satisfies REQ-055
    @satisfies REQ-056
    """
    from aibar.providers.geminiai import GEMINIAI_OAUTH_SCOPES, GeminiAICredentialStore

    click.echo()
    click.echo("GeminiAI Login")
    click.echo("=" * 40)
    click.echo()

    credential_store = GeminiAICredentialStore()
    if not credential_store.has_client_config():
        click.echo(click.style(" GeminiAI OAuth client config not found.", fg="red"))
        click.echo("Run 'aibar setup' and configure GeminiAI OAuth first.")
        sys.exit(1)

    try:
        credentials = credential_store.authorize_interactively(
            scopes=GEMINIAI_OAUTH_SCOPES
        )
    except (FileNotFoundError, ValueError, OSError, ProviderError) as exc:
        click.echo(click.style(f"\n Login failed: {exc}", fg="red"))
        sys.exit(1)

    click.echo(click.style(" Login successful!", fg="green", bold=True))
    click.echo()
    click.echo(f"  OAuth token saved to: {credential_store.token_path}")
    if credentials.token:
        click.echo(f"  Access token: {credentials.token[:12]}...")
    click.echo()
    click.echo("You can now run: aibar show --provider geminiai")


def _resolve_extension_source_dir() -> Path:
    """
    @brief Resolve GNOME extension source directory from within the `aibar` package.
    @details Uses `Path(__file__).resolve().parent` to locate the `aibar` package directory,
    then appends `gnome-extension/<UUID>/`. Works in development (editable install),
    wheel-installed, and `uv tool install` layouts because the extension directory resides
    inside the `aibar` Python package subtree.
    @return {Path} Absolute path to the extension source directory.
    @satisfies REQ-025, REQ-083
    """
    return Path(__file__).resolve().parent / "gnome-extension" / _EXT_UUID


@main.command(
    name="gnome-install",
    short_help="Install or update the GNOME Shell extension.",
    help=(
        "Install or update the AIBar GNOME Shell extension.\n"
        "Copies extension files from the package source directory to "
        "~/.local/share/gnome-shell/extensions/aibar@aibar.panel/ "
        "using install/update flow semantics, then enables the extension."
    ),
)
def gnome_install() -> None:
    """
    @brief Install or update the AIBar GNOME Shell extension to the user's local extensions directory.
    @details Resolves extension source from the installed package path, validates source directory
    contains `metadata.json` and is non-empty, then executes one of two flows:
    install flow (`target` absent) creates target and copies files before enabling extension;
    update flow (`target` present) disables extension, copies files, then enables extension.
    Update flow masks non-zero disable outcomes caused by missing extension and continues.
    Produces colored Click-styled terminal output for all status messages.
    @return {None} Function return value.
    @throws {SystemExit} Exits with code 1 on prerequisite validation failure.
    @satisfies PRJ-008, REQ-025, REQ-026, REQ-027, REQ-028, REQ-029, REQ-030, REQ-032, REQ-099
    """
    click.echo()
    click.echo(click.style("  AIBar GNOME Extension Installer", fg="blue", bold=True))
    click.echo()

    src_dir = _resolve_extension_source_dir()
    click.echo(click.style("  [1/4] ", bold=True) + "Validating extension source...")
    if not src_dir.is_dir():
        click.echo(
            click.style("  [FAIL] ", fg="red")
            + f"Source directory not found: {src_dir}"
        )
        sys.exit(1)
    metadata_path = src_dir / "metadata.json"
    if not metadata_path.is_file():
        click.echo(
            click.style("  [FAIL] ", fg="red")
            + f"metadata.json not found in: {src_dir}"
        )
        sys.exit(1)
    source_files = [f for f in src_dir.iterdir() if f.is_file()]
    if not source_files:
        click.echo(
            click.style("  [FAIL] ", fg="red") + f"Source directory is empty: {src_dir}"
        )
        sys.exit(1)
    click.echo(
        click.style("  [  OK] ", fg="green")
        + f"Source valid: {src_dir} ({len(source_files)} files)"
    )

    click.echo(click.style("  [2/5] ", bold=True) + "Preparing target directory...")
    target_dir = _EXT_TARGET_DIR
    is_update_mode = target_dir.is_dir()
    if is_update_mode:
        click.echo(click.style("  [INFO] ", fg="cyan") + f"Update mode: {target_dir}")
    else:
        os.makedirs(target_dir, exist_ok=True)
        click.echo(click.style("  [INFO] ", fg="cyan") + f"Install mode: {target_dir}")
        click.echo(click.style("  [  OK] ", fg="green") + f"Created: {target_dir}")

    if is_update_mode:
        click.echo(
            click.style("  [3/5] ", bold=True) + "Disabling extension for update..."
        )
        if shutil.which("gnome-extensions") is not None:
            disable_result = subprocess.run(
                ["gnome-extensions", "disable", _EXT_UUID],
                capture_output=True,
            )
            if disable_result.returncode == 0:
                click.echo(
                    click.style("  [  OK] ", fg="green")
                    + f"Extension disabled: {_EXT_UUID}"
                )
            else:
                click.echo(
                    click.style("  [INFO] ", fg="cyan")
                    + "Disable returned non-zero; extension may be absent. Continuing update."
                )
        else:
            click.echo(
                click.style("  [WARN] ", fg="yellow")
                + "gnome-extensions CLI not found; update proceeds without disable"
            )

    click.echo(click.style("  [4/5] ", bold=True) + "Installing extension files...")
    for src_file in source_files:
        shutil.copy2(str(src_file), str(target_dir / src_file.name))
    click.echo(
        click.style("  [  OK] ", fg="green")
        + f"Copied {len(source_files)} files to target"
    )

    click.echo(click.style("  [5/5] ", bold=True) + "Enabling extension...")
    if shutil.which("gnome-extensions") is not None:
        result = subprocess.run(
            ["gnome-extensions", "enable", _EXT_UUID],
            capture_output=True,
        )
        if result.returncode == 0:
            click.echo(
                click.style("  [  OK] ", fg="green") + f"Extension enabled: {_EXT_UUID}"
            )
        else:
            click.echo(
                click.style("  [WARN] ", fg="yellow")
                + "Could not enable extension (GNOME Shell may not be running)"
            )
    else:
        click.echo(
            click.style("  [WARN] ", fg="yellow")
            + "gnome-extensions CLI not found; enable manually after GNOME Shell restart"
        )

    click.echo()
    click.echo(click.style("  Installation complete!", fg="green", bold=True))
    click.echo()
    click.echo(click.style("  [INFO] ", fg="cyan") + f"Extension UUID : {_EXT_UUID}")
    click.echo(click.style("  [INFO] ", fg="cyan") + f"Installed to   : {target_dir}")
    click.echo()
    click.echo(
        click.style("  [WARN] ", fg="yellow")
        + "Restart GNOME Shell to load the extension:"
    )
    click.echo(
        click.style("  [INFO] ", fg="cyan") + "  Wayland : Log out and log back in"
    )
    click.echo(
        click.style("  [INFO] ", fg="cyan")
        + "  X11     : Press Alt+F2, type r, press Enter"
    )
    click.echo()


@main.command(
    name="gnome-uninstall",
    short_help="Remove the GNOME Shell extension.",
    help=(
        "Remove the AIBar GNOME Shell extension.\n"
        "Disables the extension via gnome-extensions disable and removes "
        "the extension directory ~/.local/share/gnome-shell/extensions/aibar@aibar.panel/."
    ),
)
def gnome_uninstall() -> None:
    """
    @brief Remove the AIBar GNOME Shell extension from the user's local extensions directory.
    @details Disables the extension via `gnome-extensions disable`, then removes the entire
    extension directory at `~/.local/share/gnome-shell/extensions/aibar@aibar.panel/`.
    Exits with code 1 if the extension directory does not exist. Produces colored
    Click-styled terminal output for all status messages.
    @return {None} Function return value.
    @throws {SystemExit} Exits with code 1 when extension directory does not exist.
    @satisfies REQ-028, REQ-080, REQ-081, REQ-082
    """
    click.echo()
    click.echo(click.style("  AIBar GNOME Extension Uninstaller", fg="blue", bold=True))
    click.echo()

    target_dir = _EXT_TARGET_DIR

    click.echo(
        click.style("  [1/3] ", bold=True) + "Checking extension installation..."
    )
    if not target_dir.is_dir():
        click.echo(
            click.style("  [FAIL] ", fg="red")
            + f"Extension directory not found: {target_dir}"
        )
        sys.exit(1)
    click.echo(click.style("  [  OK] ", fg="green") + f"Extension found: {target_dir}")

    click.echo(click.style("  [2/3] ", bold=True) + "Disabling extension...")
    if shutil.which("gnome-extensions") is not None:
        result = subprocess.run(
            ["gnome-extensions", "disable", _EXT_UUID],
            capture_output=True,
        )
        if result.returncode == 0:
            click.echo(
                click.style("  [  OK] ", fg="green")
                + f"Extension disabled: {_EXT_UUID}"
            )
        else:
            click.echo(
                click.style("  [WARN] ", fg="yellow")
                + "Could not disable extension (GNOME Shell may not be running)"
            )
    else:
        click.echo(
            click.style("  [WARN] ", fg="yellow")
            + "gnome-extensions CLI not found; extension may remain enabled until restart"
        )

    click.echo(click.style("  [3/3] ", bold=True) + "Removing extension files...")
    shutil.rmtree(str(target_dir))
    click.echo(click.style("  [  OK] ", fg="green") + f"Removed: {target_dir}")

    click.echo()
    click.echo(click.style("  Uninstallation complete!", fg="green", bold=True))
    click.echo()
    click.echo(
        click.style("  [WARN] ", fg="yellow") + "Restart GNOME Shell to apply changes:"
    )
    click.echo(
        click.style("  [INFO] ", fg="cyan") + "  Wayland : Log out and log back in"
    )
    click.echo(
        click.style("  [INFO] ", fg="cyan")
        + "  X11     : Press Alt+F2, type r, press Enter"
    )
    click.echo()


if __name__ == "__main__":
    main()  # pyright: ignore[reportCallIssue]
