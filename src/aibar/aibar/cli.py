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
from aibar.config import (
    RuntimeConfig,
    build_idle_time_state,
    config,
    load_cli_cache,
    load_idle_time,
    load_runtime_config,
    remove_idle_time_file,
    save_cli_cache,
    save_idle_time,
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
_CACHE_EXTENSION_SECTION_KEY = "extension"
_ATTEMPT_RESULT_OK = "OK"
_ATTEMPT_RESULT_FAIL = "FAIL"
_SHOW_PANEL_MIN_WIDTH = 72
_SHOW_PANEL_MAX_WIDTH = 110
_ANSI_RESET = "\033[0m"
_ANSI_ESCAPE_SEQUENCE_PATTERN = re.compile(r"\x1b\[[0-9;]*m")
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
_STARTUP_UPDATE_PROGRAM = "aibar"
_STARTUP_UPDATE_URL = "https://api.github.com/repos/Ogekuri/AIBar/releases/latest"
_STARTUP_IDLE_DELAY_SECONDS = 300
_STARTUP_HTTP_TIMEOUT_SECONDS = 2
_STARTUP_IDLE_STATE_LAST_SUCCESS_EPOCH_KEY = "last_success_at_epoch"
_STARTUP_IDLE_STATE_LAST_SUCCESS_HUMAN_KEY = "last_success_at_human"
_STARTUP_IDLE_STATE_IDLE_UNTIL_EPOCH_KEY = "idle_until_epoch"
_STARTUP_IDLE_STATE_IDLE_UNTIL_HUMAN_KEY = "idle_until_human"
_STARTUP_IDLE_STATE_FILENAME = "check_version_idle-time.json"
_EXT_UUID = "aibar@aibar.panel"
_EXT_TARGET_DIR = Path.home() / ".local" / "share" / "gnome-shell" / "extensions" / _EXT_UUID
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


def _emit_startup_preflight_message(message: str, color_code: str, err: bool = False) -> None:
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
        with urllib_request.urlopen(request, timeout=_STARTUP_HTTP_TIMEOUT_SECONDS) as response:
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
    @brief Execute startup update-check preflight with idle-time gating.
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
    """
    now_epoch = int(time.time())
    state = _load_startup_idle_state()
    last_success_epoch, idle_until_epoch = _startup_idle_epochs(state)
    if now_epoch < idle_until_epoch:
        return

    response = _fetch_startup_latest_release()
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
        retry_after_seconds = max(_STARTUP_IDLE_DELAY_SECONDS, response.retry_after_seconds)
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
        @details Runs update-check preflight and then delegates to Click's
        standard command parser and dispatcher.
        @param args {Sequence[str] | None} Optional argv sequence.
        @param prog_name {str | None} Program display name override.
        @param complete_var {str | None} Shell-completion environment variable.
        @param standalone_mode {bool} Click standalone execution mode flag.
        @param windows_expand_args {bool} Windows argument expansion flag.
        @param extra {object} Additional keyword arguments forwarded to Click.
        @return {NoReturn} Click main dispatcher return contract.
        @satisfies REQ-070
        """
        _run_startup_update_preflight()
        super().main(
            args=args,
            prog_name=prog_name,
            complete_var=complete_var,
            standalone_mode=standalone_mode,
            windows_expand_args=windows_expand_args,
            **extra,
        )
        raise RuntimeError("Click main returned unexpectedly.")


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
    integer seconds; non-numeric, invalid, and non-positive values return None.
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
    return parsed


def _extract_retry_after_seconds(result: ProviderResult) -> int:
    """
    @brief Extract normalized retry-after seconds from provider error payload.
    @details Reads `raw.retry_after_seconds` and clamps to non-negative integer
    seconds. Invalid or missing values normalize to zero.
    @param result {ProviderResult} Provider result to inspect.
    @return {int} Non-negative retry-after delay in seconds.
    @satisfies REQ-041
    """
    parsed = _coerce_retry_after_seconds(result.raw.get("retry_after_seconds"))
    if parsed is None:
        return 0
    return parsed


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
    return {provider_key: result.model_dump(mode="json") for provider_key, result in results.items()}


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


def _normalize_cache_document(cache_document: dict[str, object] | None) -> dict[str, object]:
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
    status_entry = _get_window_attempt_status(status_section, provider_key, target_window)
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
) -> dict[str, object]:
    """
    @brief Filter canonical cache document by optional provider selector.
    @details Filters both cache sections (`payload`, `status`) so selected-provider
    output contains only relevant provider nodes while preserving schema keys.
    @param cache_document {dict[str, object]} Canonical cache document.
    @param provider_filter {ProviderName | None} Optional provider selector.
    @return {dict[str, object]} Filtered cache document with canonical sections.
    """
    payload_section = _cache_payload_section(cache_document)
    status_section = _cache_status_section(cache_document)
    if provider_filter is None:
        return {
            _CACHE_PAYLOAD_SECTION_KEY: payload_section,
            _CACHE_STATUS_SECTION_KEY: status_section,
        }

    provider_key = provider_filter.value
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


def _project_cached_window(
    result: ProviderResult,
    target_window: WindowPeriod,
    providers: dict[ProviderName, BaseProvider],
) -> ProviderResult:
    """
    @brief Project cached raw payload to requested window without network I/O.
    @details Attempts provider-specific `_parse_response` projection when cached
    window differs from requested window; returns original result on projection
    failure or when parser is unavailable.
    @param result {ProviderResult} Cached normalized provider result.
    @param target_window {WindowPeriod} Requested CLI window.
    @param providers {dict[ProviderName, BaseProvider]} Provider registry.
    @return {ProviderResult} Result aligned to requested window when possible.
    @satisfies REQ-009
    @satisfies REQ-042
    """
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
            target_window=target_window,
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
    `idle_until = last_attempt_at + max(idle_delay_seconds, retry_after_seconds_or_0)`.
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
        successful_results = [result for result in provider_results if not result.is_error]
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


def _fetch_result(
    provider: BaseProvider,
    window: WindowPeriod,
    throttle_state: dict[str, float | int] | None = None,
) -> ProviderResult:
    """
    @brief Execute one provider refresh call without legacy TTL cache reuse.
    @details Executes throttled provider fetch and returns normalized success/error
    results. Claude 5h/7d requests are routed through `_fetch_claude_dual` so one
    API request can provide deterministic dual-window rate-limit normalization.
    @param provider {BaseProvider} Provider instance to fetch from.
    @param window {WindowPeriod} Time window for the fetch.
    @param throttle_state {dict[str, float | int] | None} Mutable throttling state
        used to enforce inter-call spacing for live API requests.
    @return {ProviderResult} Refreshed provider result for requested window.
    @satisfies CTN-004
    @satisfies REQ-043
    @satisfies REQ-040
    """
    if (
        isinstance(provider, ClaudeOAuthProvider)
        and window in {WindowPeriod.HOUR_5, WindowPeriod.DAY_7}
    ):
        result_5h, result_7d = _fetch_claude_dual(
            provider,
            throttle_state=throttle_state,
        )
        if window == WindowPeriod.HOUR_5:
            return result_5h
        return result_7d

    try:
        _apply_api_call_delay(throttle_state)
        result = asyncio.run(provider.fetch(window))
    except ProviderError as exc:
        result = provider._make_error_result(window=window, error=str(exc))
    except Exception as exc:
        result = provider._make_error_result(
            window=window, error=f"Unexpected error: {exc}"
        )
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
    """
    _apply_api_call_delay(throttle_state)
    windows = [WindowPeriod.HOUR_5, WindowPeriod.DAY_7]
    try:
        fetched = asyncio.run(provider.fetch_all_windows(windows))
    except ProviderError as exc:
        fetched = {
            w: provider._make_error_result(window=w, error=str(exc)) for w in windows
        }
    except Exception as exc:
        fetched = {
            w: provider._make_error_result(window=w, error=f"Unexpected error: {exc}")
            for w in windows
        }

    result_5h = fetched.get(WindowPeriod.HOUR_5) or provider._make_error_result(
        window=WindowPeriod.HOUR_5, error="Missing 5h result"
    )
    result_7d = fetched.get(WindowPeriod.DAY_7) or provider._make_error_result(
        window=WindowPeriod.DAY_7, error="Missing 7d result"
    )

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
) -> dict[str, object]:
    """
    @brief Refresh provider data and persist updates into `cache.json`.
    @details Executes provider fetches for configured providers only, records
    per-provider/window attempt status, updates payload only for successful
    provider/window outcomes, writes canonical cache document only on effective
    content change, and updates idle-time metadata.
    @param providers {dict[ProviderName, BaseProvider]} Provider scope for refresh.
    @param target_window {WindowPeriod} Requested window for refresh execution.
    @param runtime_config {RuntimeConfig} Runtime throttling configuration.
    @return {dict[str, object]} Persisted cache document after merge.
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
    """
    cache_document = _normalize_cache_document(load_cli_cache())
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
            continue

        if isinstance(provider, ClaudeOAuthProvider) and target_window in {
            WindowPeriod.HOUR_5,
            WindowPeriod.DAY_7,
        }:
            result_5h, result_7d = _fetch_claude_dual(
                provider=provider,
                throttle_state=throttle_state,
            )
            fetched_results.extend([result_5h, result_7d])
            _record_attempt_status(status_section, result_5h)
            _record_attempt_status(status_section, result_7d)

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

        result = _fetch_result(
            provider,
            target_window,
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
        save_cli_cache(cache_document)
    _update_idle_time_after_refresh(fetched_results, runtime_config)
    return cache_document


def retrieve_results_via_cache_pipeline(
    provider_filter: ProviderName | None,
    target_window: WindowPeriod,
    force_refresh: bool,
    providers: dict[ProviderName, BaseProvider],
) -> RetrievalPipelineOutput:
    """
    @brief Execute shared cache-based retrieval pipeline for CLI and Text UI.
    @details Applies required operation order: force-flag handling, provider-scoped
    idle-time evaluation, per-provider conditional refresh/update of `cache.json`, then decode of
    effective cache payload for downstream rendering without redundant reload.
    @param provider_filter {ProviderName | None} Optional provider selector.
    @param target_window {WindowPeriod} Target window requested by caller.
    @param force_refresh {bool} Force-refresh flag for current execution.
    @param providers {dict[ProviderName, BaseProvider]} Provider registry.
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
    """
    if force_refresh:
        remove_idle_time_file()

    cached_payload_raw = load_cli_cache()
    cached_document = _normalize_cache_document(cached_payload_raw)
    idle_state_by_provider = load_idle_time()
    now_utc = datetime.now(timezone.utc)
    if provider_filter is None:
        selected_providers = providers
    else:
        selected_provider = providers.get(provider_filter)
        selected_providers = (
            {}
            if selected_provider is None
            else {provider_filter: selected_provider}
        )

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
    idle_active = bool(idle_blocked_provider_keys)

    if force_refresh:
        refresh_scope = selected_providers
    else:
        refresh_scope = {
            provider_name: provider
            for provider_name, provider in selected_providers.items()
            if provider_name.value not in idle_blocked_provider_keys
        }

    if not refresh_scope:
        if cached_payload_raw is None:
            return RetrievalPipelineOutput(
                payload=_empty_cache_document(),
                results={},
                idle_active=idle_active,
                cache_available=False,
            )
        filtered_cached_document = _filter_cached_payload(cached_document, provider_filter)
        return RetrievalPipelineOutput(
            payload=filtered_cached_document,
            results=_load_cached_results(
                cache_document=filtered_cached_document,
                provider_filter=provider_filter,
                target_window=target_window,
                providers=providers,
            ),
            idle_active=idle_active,
            cache_available=True,
        )

    runtime_config = load_runtime_config()
    persisted_payload = _refresh_and_persist_cache_payload(
        providers=refresh_scope,
        target_window=target_window,
        runtime_config=runtime_config,
    )
    effective_payload = persisted_payload
    cache_available = bool(_cache_payload_section(effective_payload)) or bool(
        _cache_status_section(effective_payload)
    )
    if not cache_available:
        return RetrievalPipelineOutput(
            payload=_empty_cache_document(),
            results={},
            idle_active=False,
            cache_available=False,
        )
    filtered_effective_payload = _filter_cached_payload(effective_payload, provider_filter)
    return RetrievalPipelineOutput(
        payload=filtered_effective_payload,
        results=_load_cached_results(
            cache_document=filtered_effective_payload,
            provider_filter=provider_filter,
            target_window=target_window,
            providers=providers,
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
        "  aibar --uninstall            Uninstall via uv"
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
    is `geminiai` and `--window` is omitted, effective window defaults to `30d`.
    @param provider {str} CLI provider selector string.
    @param window {str} CLI window period string.
    @param output_json {bool} When True, emit JSON output instead of formatted text.
    @param force_refresh {bool} When True, bypass idle-time gate for this execution.
    @return {None} Function return value.
    @satisfies REQ-003
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
    """
    provider_filter = parse_provider(provider)
    window_period = parse_window(window)

    ctx = click.get_current_context()
    window_source = ctx.get_parameter_source("window")
    if (
        window_source == ParameterSource.DEFAULT
        and provider_filter is not None
        and provider_filter == ProviderName.GEMINIAI
    ):
        window_period = WindowPeriod.DAY_30
    providers = get_providers()

    # Filter to specific provider if requested
    if provider_filter:
        if provider_filter not in providers:
            click.echo(
                f"Provider {provider_filter.value} not implemented yet.", err=True
            )
            sys.exit(1)

    retrieval = retrieve_results_via_cache_pipeline(
        provider_filter=provider_filter,
        target_window=window_period,
        force_refresh=force_refresh,
        providers=providers,
    )
    if retrieval.idle_active and not retrieval.cache_available:
        if output_json:
            click.echo(json.dumps(_empty_cache_document(), indent=2))
        else:
            click.echo("Cache unavailable while idle-time is active.")
        return

    runtime_cfg = load_runtime_config()
    refresh_interval_seconds = runtime_cfg.gnome_refresh_interval_seconds
    if output_json:
        output_doc = dict(retrieval.payload)
        output_doc[_CACHE_EXTENSION_SECTION_KEY] = {
            "gnome_refresh_interval_seconds": runtime_cfg.gnome_refresh_interval_seconds,
        }
        click.echo(json.dumps(output_doc, indent=2))
        return

    rendered_panels: list[tuple[ProviderName, str, list[str]]] = []
    status_section = _cache_status_section(retrieval.payload)
    for name, prov in providers.items():
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
                if result.is_error and not result_5h.is_error and not result_7d.is_error:
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
                        *_build_result_panel(
                            provider_name,
                            result_5h,
                            label="5h",
                            refresh_interval_seconds=refresh_interval_seconds,
                        ),
                    )
                )
                rendered_panels.append(
                    (
                        provider_name,
                        *_build_result_panel(
                            provider_name,
                            result_7d,
                            label="7d",
                            refresh_interval_seconds=refresh_interval_seconds,
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
                    refresh_interval_seconds=refresh_interval_seconds,
                ),
            )
        )

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


def _provider_panel_color_code(provider_name: ProviderName) -> str:
    """
    @brief Resolve ANSI color code for one provider output surface.
    @param provider_name {ProviderName} Provider enum key.
    @return {str} ANSI foreground color code.
    @satisfies REQ-067
    """
    return _PROVIDER_PANEL_COLOR_CODES.get(provider_name, "\033[94m")


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
    return max(_panel_content_width(title, body_lines) for _, title, body_lines in rendered_panels)


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
        panel_content_width = min(max(_SHOW_PANEL_MIN_WIDTH - 4, content_width), wrap_width)
    horizontal_border = "─" * (panel_content_width + 2)
    click.echo(f"{color_code}┌{horizontal_border}┐{_ANSI_RESET}")
    click.echo(
        f"{color_code}│{_ANSI_RESET} "
        f"{color_code}{_ansi_ljust(title, panel_content_width)}{_ANSI_RESET} "
        f"{color_code}│{_ANSI_RESET}"
    )
    click.echo(f"{color_code}├{horizontal_border}┤{_ANSI_RESET}")
    for body_line in wrapped_lines:
        click.echo(
            f"{color_code}│{_ANSI_RESET} "
            f"{_ansi_ljust(body_line, panel_content_width)} "
            f"{color_code}│{_ANSI_RESET}"
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


def _build_result_panel(
    name: ProviderName,
    result: ProviderResult,
    label: str | None = None,
    refresh_interval_seconds: int = 60,
) -> tuple[str, list[str]]:
    """
    @brief Build one provider panel title/body payload for CLI text rendering.
    @details Formats deterministic panel lines for one provider/window result and
    preserves provider-specific metrics/error rendering rules used by `show`.
    @param name {ProviderName} Provider name enum value.
    @param result {ProviderResult} Provider result to render.
    @param label {str | None} Optional window label suffix (e.g. `"5h"`, `"7d"`).
    @param refresh_interval_seconds {int} Refresh cadence (seconds) used to compute
        the `Next` datetime label.
    @return {tuple[str, list[str]]} Panel title and body lines.
    @satisfies REQ-084
    @satisfies REQ-034
    @satisfies REQ-035
    @satisfies REQ-051
    @satisfies REQ-084
    @satisfies REQ-067
    """
    title = _provider_display_name(name)
    window_label = label or result.window.value
    if label:
        title = f"{title} ({label})"

    updated_at_utc = _normalize_utc(result.updated_at)
    next_update_utc = updated_at_utc + timedelta(
        seconds=max(0, int(refresh_interval_seconds))
    )
    lines: list[str] = [
        f"Status: {'FAIL' if result.is_error else 'OK'}",
        f"Window: {window_label}",
        (
            "Updated: "
            f"{_format_local_datetime(updated_at_utc)}, "
            f"Next: {_format_local_datetime(next_update_utc)}"
        ),
    ]
    if result.is_error:
        lines.append(f"Error: {result.error}")
        status_retry_line = _format_http_status_retry_line(
            result.raw.get("status_code"),
            result.raw.get("retry_after_seconds"),
        )
        if status_retry_line is not None:
            lines.append(status_retry_line)
        return title, lines

    m = result.metrics
    if m.usage_percent is not None:
        pct = m.usage_percent
        lines.append(f"Usage: {pct:.1f}% {_progress_bar(pct, name)}")

    if m.reset_at:
        delta = m.reset_at - datetime.now(timezone.utc)
        if delta.total_seconds() > 0:
            reset_value = _format_reset_duration(delta.total_seconds())
            lines.append(f"Resets in: {reset_value}")
    elif _should_print_claude_reset_pending_hint(name, m):
        lines.append(f"Resets in: {_RESET_PENDING_MESSAGE}")

    if (
        name in (
            ProviderName.CLAUDE,
            ProviderName.CODEX,
            ProviderName.COPILOT,
            ProviderName.GEMINIAI,
        )
        and m.remaining is not None
        and m.limit is not None
    ):
        lines.append(f"Remaining credits: {m.remaining:.1f} / {m.limit:.1f}")

    if m.cost is not None:
        if name == ProviderName.OPENROUTER and m.limit is not None:
            lines.append(
                f"Cost: {m.currency_symbol}{m.cost:.4f} / "
                f"{m.currency_symbol}{m.limit:.2f}"
            )
        else:
            lines.append(f"Cost: {m.currency_symbol}{m.cost:.4f}")

    if m.requests is not None:
        lines.append(f"Requests: {m.requests:,}")

    if m.input_tokens is not None or m.output_tokens is not None:
        total = (m.input_tokens or 0) + (m.output_tokens or 0)
        lines.append(
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
            lines.append(f"BYOK: {m.currency_symbol}{float(byok_raw):.4f}")

    if name == ProviderName.GEMINIAI:
        monitoring_raw = result.raw.get("monitoring")
        if isinstance(monitoring_raw, dict):
            latency_total = monitoring_raw.get("latency_total")
            error_total = monitoring_raw.get("error_total")
            if isinstance(latency_total, (int, float)):
                lines.append(f"Monitoring latency total: {float(latency_total):.2f}")
            if isinstance(error_total, (int, float)):
                lines.append(f"Monitoring error total: {float(error_total):.2f}")
        billing_raw = result.raw.get("billing")
        if isinstance(billing_raw, dict):
            table_id = billing_raw.get("table_id")
            table_path = billing_raw.get("table_path")
            services = billing_raw.get("services")
            if isinstance(table_id, str) and table_id:
                lines.append(f"Billing table: {table_id}")
            if isinstance(table_path, str) and table_path:
                lines.append(f"Billing path: {table_path}")
            if isinstance(services, list):
                lines.append(f"Billing services: {len(services)}")

    if not result.is_error:
        status_retry_line = _format_http_status_retry_line(
            result.raw.get("status_code"),
            result.raw.get("retry_after_seconds"),
        )
        if status_retry_line is not None:
            lines.append(status_retry_line)

    return title, lines


def _print_result(name: ProviderName, result, label: str | None = None) -> None:
    """
    @brief Render CLI text output for one provider result.
    @details Formats usage percentage, reset countdown, remaining credits, cost,
    requests, and token counts for one provider/window result. Cost is formatted
    using `metrics.currency_symbol` (never hardcoded `$`).
    @param name {ProviderName} Provider name enum value.
    @param result {ProviderResult} Provider result to render.
    @param label {str | None} Optional window label suffix (e.g. `"5h"`, `"7d"`).
    @return {None} Function return value.
    @satisfies REQ-034
    @satisfies REQ-035
    @satisfies REQ-051
    @satisfies REQ-067
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


def _progress_bar(percent: float, provider_name: ProviderName, width: int = 20) -> str:
    """
    @brief Execute progress bar.
    @details Applies progress bar logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @param percent {float} Input parameter `percent`.
    @param provider_name {ProviderName} Provider enum key for color mapping.
    @param width {int} Input parameter `width`.
    @return {str} Function return value.
    """
    normalized_percent = max(0.0, min(100.0, percent))
    filled = int(width * normalized_percent / 100)
    empty = width - filled
    color_code = _provider_panel_color_code(provider_name)
    return f"[{color_code}{'█' * filled}{_ANSI_RESET}{'░' * empty}]"


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
    @details Prompts for `idle_delay_seconds`, `api_call_delay_milliseconds`,
    `gnome_refresh_interval_seconds`, and `billing_data` in order, then prompts for provider
    currency symbols including `geminiai` (choices: `$`, `£`, `€`, default `$`), then persists
    all values to `~/.config/aibar/config.json`. GeminiAI OAuth source supports
    `skip`, `file`, `paste`, and `login` (re-authorization with current scopes).
    Also prompts for provider API keys and writes them to `~/.config/aibar/env`.
    @return {None} Function return value.
    @satisfies REQ-005
    @satisfies REQ-049
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
    click.echo(click.style("Runtime throttling", bold=True))
    click.echo("  idle-delay controls cache-only mode duration after successful refresh.")
    click.echo("  api-call delay controls minimum spacing between API calls in milliseconds.")
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
    gnome_refresh_interval_seconds = click.prompt(
        "  gnome-refresh-interval seconds",
        type=int,
        default=runtime_config.gnome_refresh_interval_seconds,
    )
    billing_data = click.prompt(
        "  billing_data",
        default=runtime_config.billing_data,
        show_default=True,
    ).strip() or runtime_config.billing_data
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
                click.echo(click.style("  -> GeminiAI OAuth client config not found.", fg="red"))
                click.echo("  -> Configure OAuth client with source 'file' or 'paste' first.")
            else:
                try:
                    credential_store.authorize_interactively(scopes=GEMINIAI_OAUTH_SCOPES)
                    click.echo("  -> OAuth token saved")
                except (FileNotFoundError, ValueError, OSError, ProviderError) as exc:
                    click.echo(click.style(f"  -> GeminiAI OAuth setup failed: {exc}", fg="red"))
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
                click.echo(click.style(f"  -> OAuth JSON decode error: {exc}", fg="red"))
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
                    click.echo(click.style(f"  -> OAuth JSON decode error: {exc}", fg="red"))

        if client_payload_raw is not None:
            try:
                credential_store.save_client_config(client_payload_raw)
                saved_payload = credential_store.load_client_config()
                detected_project_id = credential_store.extract_project_id(saved_payload)
                if detected_project_id is not None:
                    geminiai_project_id = detected_project_id
                click.echo("  -> OAuth client saved")
                if click.confirm("  Open browser and authorize GeminiAI now?", default=True):
                    credential_store.authorize_interactively(scopes=GEMINIAI_OAUTH_SCOPES)
                    click.echo("  -> OAuth token saved")
            except (FileNotFoundError, ValueError, OSError, ProviderError) as exc:
                click.echo(click.style(f"  -> GeminiAI OAuth setup failed: {exc}", fg="red"))

        project_default = geminiai_project_id or ""
        project_input = click.prompt(
            "  geminiai project id",
            default=project_default,
            show_default=bool(project_default),
        ).strip()
        geminiai_project_id = project_input or None

    configured_runtime = RuntimeConfig(
        idle_delay_seconds=idle_delay_seconds,
        api_call_delay_milliseconds=api_call_delay_milliseconds,
        gnome_refresh_interval_seconds=gnome_refresh_interval_seconds,
        billing_data=billing_data,
        currency_symbols=currency_symbols,
        geminiai_project_id=geminiai_project_id,
    )
    save_runtime_config(configured_runtime)
    click.echo("  -> Saved")
    click.echo()

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
        credentials = credential_store.authorize_interactively(scopes=GEMINIAI_OAUTH_SCOPES)
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
        "and enables the extension via gnome-extensions enable."
    ),
)
def gnome_install() -> None:
    """
    @brief Install or update the AIBar GNOME Shell extension to the user's local extensions directory.
    @details Resolves extension source from the installed package path, validates source directory
    contains `metadata.json` and is non-empty, creates target directory if absent, copies all
    extension files replacing existing ones, and enables the extension via `gnome-extensions enable`.
    Produces colored Click-styled terminal output for all status messages.
    @return {None} Function return value.
    @throws {SystemExit} Exits with code 1 on prerequisite validation failure.
    @satisfies PRJ-008, REQ-025, REQ-026, REQ-027, REQ-028, REQ-029, REQ-030, REQ-032
    """
    click.echo()
    click.echo(click.style("  AIBar GNOME Extension Installer", fg="blue", bold=True))
    click.echo()

    src_dir = _resolve_extension_source_dir()
    click.echo(click.style("  [1/4] ", bold=True) + "Validating extension source...")
    if not src_dir.is_dir():
        click.echo(click.style("  [FAIL] ", fg="red") + f"Source directory not found: {src_dir}")
        sys.exit(1)
    metadata_path = src_dir / "metadata.json"
    if not metadata_path.is_file():
        click.echo(click.style("  [FAIL] ", fg="red") + f"metadata.json not found in: {src_dir}")
        sys.exit(1)
    source_files = [f for f in src_dir.iterdir() if f.is_file()]
    if not source_files:
        click.echo(click.style("  [FAIL] ", fg="red") + f"Source directory is empty: {src_dir}")
        sys.exit(1)
    click.echo(
        click.style("  [  OK] ", fg="green")
        + f"Source valid: {src_dir} ({len(source_files)} files)"
    )

    click.echo(click.style("  [2/4] ", bold=True) + "Preparing target directory...")
    target_dir = _EXT_TARGET_DIR
    if target_dir.is_dir():
        click.echo(click.style("  [INFO] ", fg="cyan") + f"Target directory exists: {target_dir}")
    else:
        os.makedirs(target_dir, exist_ok=True)
        click.echo(click.style("  [  OK] ", fg="green") + f"Created: {target_dir}")

    click.echo(click.style("  [3/4] ", bold=True) + "Installing extension files...")
    for src_file in source_files:
        shutil.copy2(str(src_file), str(target_dir / src_file.name))
    click.echo(
        click.style("  [  OK] ", fg="green") + f"Copied {len(source_files)} files to target"
    )

    click.echo(click.style("  [4/4] ", bold=True) + "Enabling extension...")
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
        click.style("  [WARN] ", fg="yellow") + "Restart GNOME Shell to load the extension:"
    )
    click.echo(click.style("  [INFO] ", fg="cyan") + "  Wayland : Log out and log back in")
    click.echo(
        click.style("  [INFO] ", fg="cyan") + "  X11     : Press Alt+F2, type r, press Enter"
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

    click.echo(click.style("  [1/3] ", bold=True) + "Checking extension installation...")
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
                click.style("  [  OK] ", fg="green") + f"Extension disabled: {_EXT_UUID}"
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
    click.echo(click.style("  [INFO] ", fg="cyan") + "  Wayland : Log out and log back in")
    click.echo(
        click.style("  [INFO] ", fg="cyan") + "  X11     : Press Alt+F2, type r, press Enter"
    )
    click.echo()


if __name__ == "__main__":
    main()  # pyright: ignore[reportCallIssue]
