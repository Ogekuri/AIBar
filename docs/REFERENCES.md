# Files Structure
```
.
└── src
    └── aibar
        └── aibar
            ├── __init__.py
            ├── __main__.py
            ├── cache.py
            ├── claude_cli_auth.py
            ├── cli.py
            ├── config.py
            ├── gnome-extension
            │   └── aibar@aibar.panel
            │       └── extension.js
            └── providers
                ├── __init__.py
                ├── base.py
                ├── claude_oauth.py
                ├── codex.py
                ├── copilot.py
                ├── geminiai.py
                ├── openai_usage.py
                └── openrouter.py
```

# __init__.py | Python | 7L | 0 symbols | 0 imports | 1 comments
> Path: `src/aibar/aibar/__init__.py`
- @brief Package metadata for aibar.
- @details Exposes the package version for the multi-provider usage monitoring application.


---

# __main__.py | Python | 11L | 0 symbols | 1 imports | 1 comments
> Path: `src/aibar/aibar/__main__.py`
- @brief Module execution entry point for aibar.
- @details Delegates to aibar.cli:main to enable `python -m aibar` invocation.
- @satisfies REQ-024

## Imports
```
from aibar.cli import main
```


---

# cache.py | Python | 351L | 24 symbols | 7 imports | 29 comments
> Path: `src/aibar/aibar/cache.py`
- @brief Provider result caching primitives.
- @details Implements in-memory and disk cache entries, TTL invalidation, and raw-payload sanitization for non-Claude provider metrics.

## Imports
```
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from pydantic import BaseModel
from aibar.providers.base import ProviderName, ProviderResult, WindowPeriod
```

## Definitions

### class `class CacheEntry(BaseModel)` : BaseModel (L18-38)
- @brief Define cache entry component.
- @details Encapsulates cache entry state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `def is_expired(self) -> bool` (L28-38)
  - @brief Define cache entry component.
  - @brief Execute is expired.
  - @details Encapsulates cache entry state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
  - @details Applies is expired logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {bool} Function return value.

### class `class ResultCache` (L39-238)
- @brief Define result cache component.
- @details Encapsulates result cache state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces. Caching behavior is disabled for Claude provider results.
- var `DEFAULT_TTL = 120  # 2 minutes` (L45)
  - @brief Define result cache component.
  - @details Encapsulates result cache state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces. Caching behavior is disabled for Claude provider results.
- var `PROVIDER_TTLS =` (L46)
- var `RATE_LIMIT_COOLDOWN = 30  # seconds to wait before retrying after HTTP 429` (L51)
- fn `def __init__(self, cache_dir: Path | None = None) -> None` `priv` (L53-63)
  - @brief Execute init.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param cache_dir {Path | None} Input parameter `cache_dir`.
  - @return {None} Function return value.
- fn `def _default_cache_dir(self) -> Path` `priv` (L64-73)
  - @brief Execute default cache dir.
  - @details Applies default cache dir logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {Path} Function return value.
- fn `def _ensure_cache_dir(self) -> None` `priv` (L74-81)
  - @brief Execute ensure cache dir.
  - @details Applies ensure cache dir logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {None} Function return value.
- fn `def _cache_key(self, provider: ProviderName, window: WindowPeriod) -> str` `priv` (L82-91)
  - @brief Execute cache key.
  - @details Applies cache key logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @param window {WindowPeriod} Input parameter `window`.
  - @return {str} Function return value.
- fn `def _disk_path(self, provider: ProviderName, window: WindowPeriod) -> Path` `priv` (L92-101)
  - @brief Execute disk path.
  - @details Applies disk path logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @param window {WindowPeriod} Input parameter `window`.
  - @return {Path} Function return value.
- fn `def _is_cacheable_provider(self, provider: ProviderName) -> bool` `priv` (L102-111)
  - @brief Check whether result-cache read/write logic is enabled for a provider.
  - @details Returns False for Claude to enforce fresh API reads without memory/disk reuse and rate-limit cooldown markers. Returns True for all other providers.
  - @param provider {ProviderName} Provider identifier to classify.
  - @return {bool} True when provider caching is enabled.
  - @satisfies CTN-004
- fn `def get(self, provider: ProviderName, window: WindowPeriod) -> ProviderResult | None` (L112-133)
  - @brief Execute get.
  - @details Applies get logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @param window {WindowPeriod} Input parameter `window`.
  - @return {ProviderResult | None} Function return value.
- fn `def set(self, result: ProviderResult) -> None` (L134-167)
  - @brief Execute set.
  - @details Applies set logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param result {ProviderResult} Input parameter `result`.
  - @return {None} Function return value.
- fn `def get_last_good(self, provider: ProviderName, window: WindowPeriod) -> ProviderResult | None` (L168-180)
  - @brief Execute get last good.
  - @details Applies get last good logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @param window {WindowPeriod} Input parameter `window`.
  - @return {ProviderResult | None} Function return value.
- fn `def invalidate(` (L181-182)
- fn `def _cooldown_path(self, provider: ProviderName) -> Path` `priv` (L205-213)
  - @brief Execute invalidate.
  - @brief Resolve disk path for provider rate-limit cooldown marker.
  - @details Applies invalidate logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @details Returns path under cache directory keyed by provider name.
  - @param provider {ProviderName | None} Input parameter `provider`.
  - @param window {WindowPeriod | None} Input parameter `window`.
  - @param provider {ProviderName} Provider to resolve cooldown path for.
  - @return {None} Function return value.
  - @return {Path} Absolute path to cooldown marker file.
- fn `def set_rate_limited(self, provider: ProviderName) -> None` (L214-232)
  - @brief Write rate-limit cooldown marker to disk for a provider.
  - @details Persists current UTC timestamp to cooldown file. Subsequent is_rate_limited calls within RATE_LIMIT_COOLDOWN seconds return True. Silently ignores disk write failures.
  - @param provider {ProviderName} Provider to mark as rate-limited.
  - @return {None} No return value.

### fn `def is_rate_limited(self, provider: ProviderName) -> bool` (L233-257)
- @brief Check whether provider is in rate-limit cooldown period.
- @details Reads timestamp from cooldown marker file. Returns True if age is less than RATE_LIMIT_COOLDOWN seconds. Expired markers are deleted.
- @param provider {ProviderName} Provider to check cooldown for.
- @return {bool} True if provider is within cooldown period.

### fn `def clear_rate_limit(self, provider: ProviderName) -> None` (L258-270)
- @brief Remove rate-limit cooldown marker for a provider.
- @details Deletes cooldown marker file if present. Called on successful fetch.
- @param provider {ProviderName} Provider to clear cooldown for.
- @return {None} No return value.

### fn `def _save_to_disk(self, result: ProviderResult) -> None` `priv` (L271-289)
- @brief Execute save to disk.
- @details Applies save to disk logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param result {ProviderResult} Input parameter `result`.
- @return {None} Function return value.

### fn `def _load_from_disk(` `priv` (L290-294)

### fn `def _sanitize_raw(self, raw: dict[str, Any]) -> dict[str, Any]` `priv` (L326-351)
- @brief Execute load from disk.
- @brief Execute sanitize raw.
- @details Applies load from disk logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @details Applies sanitize raw logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param provider {ProviderName} Input parameter `provider`.
- @param window {WindowPeriod} Input parameter `window`.
- @param ignore_ttl {bool} Input parameter `ignore_ttl`.
- @param raw {dict[str, Any]} Input parameter `raw`.
- @return {ProviderResult | None} Function return value.
- @return {dict[str, Any]} Function return value.

### fn `def clean(obj: Any) -> Any` (L335-350)
- @brief Execute sanitize raw.
- @brief Execute clean.
- @details Applies sanitize raw logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @details Applies clean logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param raw {dict[str, Any]} Input parameter `raw`.
- @param obj {Any} Input parameter `obj`.
- @return {dict[str, Any]} Function return value.
- @return {Any} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`CacheEntry`|class|pub|18-38|class CacheEntry(BaseModel)|
|`CacheEntry.is_expired`|fn|pub|28-38|def is_expired(self) -> bool|
|`ResultCache`|class|pub|39-238|class ResultCache|
|`ResultCache.DEFAULT_TTL`|var|pub|45||
|`ResultCache.PROVIDER_TTLS`|var|pub|46||
|`ResultCache.RATE_LIMIT_COOLDOWN`|var|pub|51||
|`ResultCache.__init__`|fn|priv|53-63|def __init__(self, cache_dir: Path | None = None) -> None|
|`ResultCache._default_cache_dir`|fn|priv|64-73|def _default_cache_dir(self) -> Path|
|`ResultCache._ensure_cache_dir`|fn|priv|74-81|def _ensure_cache_dir(self) -> None|
|`ResultCache._cache_key`|fn|priv|82-91|def _cache_key(self, provider: ProviderName, window: Wind...|
|`ResultCache._disk_path`|fn|priv|92-101|def _disk_path(self, provider: ProviderName, window: Wind...|
|`ResultCache._is_cacheable_provider`|fn|priv|102-111|def _is_cacheable_provider(self, provider: ProviderName) ...|
|`ResultCache.get`|fn|pub|112-133|def get(self, provider: ProviderName, window: WindowPerio...|
|`ResultCache.set`|fn|pub|134-167|def set(self, result: ProviderResult) -> None|
|`ResultCache.get_last_good`|fn|pub|168-180|def get_last_good(self, provider: ProviderName, window: W...|
|`ResultCache.invalidate`|fn|pub|181-182|def invalidate(|
|`ResultCache._cooldown_path`|fn|priv|205-213|def _cooldown_path(self, provider: ProviderName) -> Path|
|`ResultCache.set_rate_limited`|fn|pub|214-232|def set_rate_limited(self, provider: ProviderName) -> None|
|`is_rate_limited`|fn|pub|233-257|def is_rate_limited(self, provider: ProviderName) -> bool|
|`clear_rate_limit`|fn|pub|258-270|def clear_rate_limit(self, provider: ProviderName) -> None|
|`_save_to_disk`|fn|priv|271-289|def _save_to_disk(self, result: ProviderResult) -> None|
|`_load_from_disk`|fn|priv|290-294|def _load_from_disk(|
|`_sanitize_raw`|fn|priv|326-351|def _sanitize_raw(self, raw: dict[str, Any]) -> dict[str,...|
|`clean`|fn|pub|335-350|def clean(obj: Any) -> Any|


---

# claude_cli_auth.py | Python | 129L | 9 symbols | 4 imports | 11 comments
> Path: `src/aibar/aibar/claude_cli_auth.py`
- @brief Claude CLI credential extraction helpers.
- @details Reads Claude CLI OAuth credential stores and exposes token/status accessors for provider authentication.

## Imports
```
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
```

## Definitions

### class `class ClaudeCLIAuth` (L13-121)
- @brief Define claude c l i auth component.
- @details Encapsulates claude c l i auth state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `DEFAULT_CREDS_PATH = Path.home() / ".claude" / ".credentials.json"` (L19)
  - @brief Define claude c l i auth component.
  - @details Encapsulates claude c l i auth state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `def __init__(self, creds_path: Path | None = None) -> None` `priv` (L21-29)
  - @brief Execute init.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param creds_path {Path | None} Input parameter `creds_path`.
  - @return {None} Function return value.
- fn `def is_available(self) -> bool` (L30-37)
  - @brief Execute is available.
  - @details Applies is available logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {bool} Function return value.
- fn `def get_credentials(self) -> dict[str, Any] | None` (L38-52)
  - @brief Execute get credentials.
  - @details Applies get credentials logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {dict[str, Any] | None} Function return value.
- fn `def get_access_token(self) -> str | None` (L53-61)
  - @brief Execute get access token.
  - @details Applies get access token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str | None} Function return value.
- fn `def is_token_expired(self) -> bool` (L62-79)
  - @brief Execute is token expired.
  - @details Applies is token expired logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {bool} Function return value.
- fn `def get_token_info(self) -> dict[str, Any]` (L80-121)
  - @brief Execute get token info.
  - @details Applies get token info logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {dict[str, Any]} Function return value.

### fn `def extract_claude_cli_token() -> str | None` (L122-129)
- @brief Execute extract claude cli token.
- @details Applies extract claude cli token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {str | None} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`ClaudeCLIAuth`|class|pub|13-121|class ClaudeCLIAuth|
|`ClaudeCLIAuth.DEFAULT_CREDS_PATH`|var|pub|19||
|`ClaudeCLIAuth.__init__`|fn|priv|21-29|def __init__(self, creds_path: Path | None = None) -> None|
|`ClaudeCLIAuth.is_available`|fn|pub|30-37|def is_available(self) -> bool|
|`ClaudeCLIAuth.get_credentials`|fn|pub|38-52|def get_credentials(self) -> dict[str, Any] | None|
|`ClaudeCLIAuth.get_access_token`|fn|pub|53-61|def get_access_token(self) -> str | None|
|`ClaudeCLIAuth.is_token_expired`|fn|pub|62-79|def is_token_expired(self) -> bool|
|`ClaudeCLIAuth.get_token_info`|fn|pub|80-121|def get_token_info(self) -> dict[str, Any]|
|`extract_claude_cli_token`|fn|pub|122-129|def extract_claude_cli_token() -> str | None|


---

# cli.py | Python | 5150L | 137 symbols | 31 imports | 154 comments
> Path: `src/aibar/aibar/cli.py`
- @brief Command-line interface for aibar.
- @details Defines command parsing, provider dispatch, formatted output, setup helpers, login flows, and UI launch hooks.

## Imports
```
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
from aibar.providers import (
from aibar.providers.base import (
from aibar.config import (
from aibar.providers.geminiai import GEMINIAI_OAUTH_SCOPES, GeminiAICredentialStore
from aibar.claude_cli_auth import ClaudeCLIAuth
from aibar.providers.copilot import CopilotProvider
from aibar.providers.geminiai import GEMINIAI_OAUTH_SCOPES, GeminiAICredentialStore
```

## Definitions

### class `class RetrievalPipelineOutput` `@dataclass(frozen=True)` (L153-182)
- @brief Define shared provider-retrieval pipeline output.
- @details Encodes deterministic retrieval state produced by the shared cache-based pipeline used by `show` and Text UI refresh execution. The pipeline enforces force-flag handling, idle-time gating, conditional refresh into `cache.json`, and deterministic payload projection for rendering.
- @note `payload` contains cache JSON sections: `payload` and `status`.
- @note `results` contains validated ProviderResult objects keyed by provider id.
- @note `idle_time_by_provider` contains provider-keyed idle-time freshness state.
- @note `idle_active` indicates provider-scoped idle-time gating blocked at least one selected provider refresh.
- @note `cache_available` indicates `cache.json` was readable for this run.
- @satisfies REQ-009
- @satisfies REQ-039
- @satisfies REQ-042
- @satisfies REQ-043
- @satisfies REQ-044
- @satisfies REQ-045
- @satisfies REQ-046
- @satisfies REQ-047

### class `class StartupReleaseCheckResponse` `@dataclass(frozen=True)` (L184-203)
- @brief Represent one startup GitHub release-check execution result.
- @details Encodes normalized response state for startup preflight control-flow. `latest_version` is populated only on successful metadata retrieval. `status_code`, `error_message`, and `retry_after_seconds` carry normalized failure metadata used by 429 idle-time expansion and bright-red diagnostics.
- @note Immutable dataclass to keep preflight decisions deterministic.
- @satisfies REQ-070
- @satisfies REQ-073
- @satisfies REQ-074
- @satisfies REQ-075

### fn `def _startup_idle_state_path() -> Path` `priv` (L204-213)
- @brief Resolve startup update idle-state JSON path.
- @details Builds `~/.cache/aibar/check_version_idle-time.json` in user scope.
- @return {Path} Absolute path for startup idle-state persistence.
- @satisfies CTN-013

### fn `def _startup_human_timestamp(epoch_seconds: int) -> str` `priv` (L214-226)
- @brief Convert epoch seconds to UTC ISO-8601 timestamp text.
- @details Normalizes negative input to zero and emits timezone-aware UTC values so startup idle-state JSON remains machine-parseable and stable.
- @param epoch_seconds {int} Epoch timestamp in seconds.
- @return {str} UTC ISO-8601 timestamp string.
- @satisfies CTN-013

### fn `def _startup_parse_int(value: object, default: int = 0) -> int` `priv` (L227-244)
- @brief Parse integer-like values for startup idle-state normalization.
- @details Supports int, float, and numeric strings; invalid values return provided default. Parsed values are clamped to non-negative integers.
- @param value {object} Raw decoded value from JSON or headers.
- @param default {int} Fallback integer when parsing fails.
- @return {int} Non-negative parsed integer or fallback default.

### fn `def _load_startup_idle_state() -> dict[str, object] | None` `priv` (L245-264)
- @brief Load startup update idle-state JSON from disk.
- @details Reads `~/.cache/aibar/check_version_idle-time.json` and returns decoded JSON object when valid. Corrupt, missing, or unreadable files normalize to None.
- @return {dict[str, object] | None} Parsed idle-state mapping or None.
- @satisfies CTN-013

### fn `def _startup_idle_epochs(state: dict[str, object] | None) -> tuple[int, int]` `priv` (L265-286)
- @brief Extract normalized startup idle-state epoch timestamps.
- @details Reads `last_success_at_epoch` and `idle_until_epoch` from decoded state object and normalizes missing/invalid values to zero.
- @param state {dict[str, object] | None} Decoded startup idle-state mapping.
- @return {tuple[int, int]} Tuple `(last_success_epoch, idle_until_epoch)`.
- @satisfies CTN-013

### fn `def _save_startup_idle_state(last_success_epoch: int, idle_until_epoch: int) -> None` `priv` (L287-317)
- @brief Persist startup update idle-state JSON.
- @details Writes epoch and UTC human-readable values for last successful startup release check and idle-disable-until timestamp to `~/.cache/aibar/check_version_idle-time.json`.
- @param last_success_epoch {int} Last successful startup check epoch.
- @param idle_until_epoch {int} Startup idle gate expiry epoch.
- @return {None} Function return value.
- @throws {OSError} Propagates filesystem write failures.
- @satisfies CTN-013
- @satisfies REQ-072

### fn `def _cleanup_startup_idle_state_artifacts() -> int` `priv` (L318-343)
- @brief Remove startup update idle-state artifacts for Linux uninstall.
- @details Deletes `~/.cache/aibar/check_version_idle-time.json` when present, then removes `~/.cache/aibar/` recursively when present. Emits bright-red diagnostics and returns non-zero on filesystem failures.
- @return {int} Zero on success; one when cleanup fails.
- @satisfies REQ-077

### fn `def _emit_startup_preflight_message(` `priv` (L344-345)

### fn `def _parse_retry_after_header(retry_after_raw: str | None) -> int` `priv` (L361-385)
- @brief Emit colorized startup preflight diagnostics.
- @brief Parse HTTP Retry-After header to delay seconds.
- @details Wraps message text with ANSI bright color escape sequences so update
availability notices and failures are visually distinct in terminal output.
- @details Supports integer-second values and HTTP-date formats. Date values are converted to seconds relative to current UTC time and clamped to zero.
- @param message {str} Rendered diagnostic message text.
- @param color_code {str} ANSI SGR color escape prefix.
- @param err {bool} When true, write to stderr stream.
- @param retry_after_raw {str | None} Retry-After header value.
- @return {None} Function return value.
- @return {int} Non-negative delay seconds.
- @satisfies REQ-073
- @satisfies REQ-074
- @satisfies REQ-075

### fn `def _normalize_release_version(raw_version: object) -> str | None` `priv` (L386-402)
- @brief Normalize release tag text extracted from GitHub API payload.
- @details Accepts string-like values, trims whitespace, and returns None for empty/invalid payload values.
- @param raw_version {object} Decoded `tag_name` value from release JSON.
- @return {str | None} Normalized release version string.
- @satisfies REQ-073

### fn `def _fetch_startup_latest_release() -> StartupReleaseCheckResponse` `priv` (L403-459)
- @brief Fetch latest GitHub release metadata for startup preflight.
- @details Executes one HTTP request to the canonical releases/latest endpoint with hardcoded timeout. Success returns normalized latest version tag. Failures return status/error metadata and parsed retry-after delay.
- @return {StartupReleaseCheckResponse} Normalized startup release-check result.
- @satisfies CTN-011
- @satisfies CTN-012
- @satisfies REQ-073
- @satisfies REQ-074
- @satisfies REQ-075

### fn `def _parse_version_triplet(version_text: str) -> tuple[int, int, int] | None` `priv` (L460-478)
- @brief Parse semantic version tuple from version text.
- @details Accepts optional `v` prefix and optional suffix metadata. Returns first `major.minor.patch` triplet or None when parsing fails.
- @param version_text {str} Raw version string.
- @return {tuple[int, int, int] | None} Parsed semantic version tuple.
- @satisfies REQ-073

### fn `def _is_newer_release(installed_version: str, latest_version: str) -> bool` `priv` (L479-495)
- @brief Compare installed and latest release semantic versions.
- @details Uses normalized `major.minor.patch` tuples. Invalid version formats disable upgrade notice emission to avoid false positives.
- @param installed_version {str} Installed program version text.
- @param latest_version {str} Latest release version text.
- @return {bool} True when latest release is newer than installed version.
- @satisfies REQ-073

### fn `def _run_startup_update_preflight() -> None` `priv` (L496-579)
- @brief Execute startup update-check preflight with optional idle-time bypass.
- @details Evaluates startup idle-state file; skips HTTP calls while idle is active; performs latest-release fetch when idle expires or file is missing; prints bright-green update notice for newer releases; prints bright-red error diagnostics on failures; updates idle-state after success and HTTP 429.
- @return {None} Function return value.
- @satisfies CTN-013
- @satisfies CTN-014
- @satisfies REQ-070
- @satisfies REQ-071
- @satisfies REQ-072
- @satisfies REQ-073
- @satisfies REQ-074
- @satisfies REQ-075
- @satisfies REQ-112

### fn `def _startup_force_ignore_idle_from_args(args: Sequence[str] | None) -> bool` `priv` (L580-599)
- @brief Detect whether startup preflight must bypass idle gating from argv.
- @details Returns true when invocation arguments contain `--version` or `--ver`, forcing one online startup release check regardless of persisted startup idle-time file state.
- @param args {Sequence[str] | None} CLI argv sequence excluding executable name when provided by Click group main.
- @return {bool} True when startup preflight must bypass idle-time gating.
- @satisfies REQ-071
- @satisfies REQ-078

### fn `def _execute_lifecycle_subprocess(command: list[str]) -> int` `priv` (L600-622)
- @brief Execute lifecycle subprocess command for upgrade/uninstall options.
- @details Runs provided command via `subprocess.run` and returns subprocess exit code. Command execution failures return non-zero status with red error.
- @param command {list[str]} Lifecycle command argv.
- @return {int} Subprocess exit code.
- @satisfies CTN-015
- @satisfies REQ-076
- @satisfies REQ-077

### fn `def _is_linux_runtime() -> bool` `priv` (L623-635)
- @brief Determine whether lifecycle subprocess execution is allowed.
- @details Returns true only for Linux runtimes. Lifecycle subprocesses for `--upgrade` and `--uninstall` are Linux-only and must be skipped elsewhere.
- @return {bool} True when current runtime platform is Linux.
- @satisfies REQ-076
- @satisfies REQ-077
- @satisfies REQ-088

### fn `def _emit_non_linux_lifecycle_guidance(option_name: str, command: Sequence[str]) -> int` `priv` (L636-662)
- @brief Emit manual lifecycle command guidance for non-Linux platforms.
- @details Builds one deterministic warning message containing detected operating-system label and exact manual command text, then emits it through startup preflight styled diagnostics with stderr routing.
- @param option_name {str} Lifecycle option token (`--upgrade` or `--uninstall`).
- @param command {Sequence[str]} Lifecycle command argv to present as manual guidance.
- @return {int} Deterministic non-zero exit code indicating command was not executed.
- @satisfies CTN-015
- @satisfies REQ-088
- @satisfies REQ-089

### fn `def _handle_upgrade_option(` `priv` (L663-664)

### fn `def _handle_uninstall_option(` `priv` (L693-694)
- @brief Handle eager `--upgrade` lifecycle option callback.
- @details Executes required lifecycle subprocess on Linux and exits with
propagated subprocess code; on non-Linux emits manual command guidance and
exits without subprocess execution.
- @param ctx {click.Context} Active Click context.
- @param param {click.Parameter} Option metadata (unused).
- @param value {bool} Parsed `--upgrade` flag value.
- @return {None} Function return value.
- @satisfies CTN-015
- @satisfies REQ-076
- @satisfies REQ-088
- @satisfies REQ-089

### fn `def _handle_version_option(` `priv` (L727-728)
- @brief Handle eager `--uninstall` lifecycle option callback.
- @details Executes required lifecycle subprocess on Linux, cleans startup
idle-state artifacts under `~/.cache/aibar/`, and exits with propagated
subprocess code unless cleanup fails after successful subprocess execution.
On non-Linux emits manual command guidance and exits without subprocess execution.
- @param ctx {click.Context} Active Click context.
- @param param {click.Parameter} Option metadata (unused).
- @param value {bool} Parsed `--uninstall` flag value.
- @return {None} Function return value.
- @satisfies CTN-015
- @satisfies REQ-077
- @satisfies REQ-088
- @satisfies REQ-089

### fn `def _update_runtime_logging_flags(` `priv` (L747-750)
- @brief Handle eager `--version` and `--ver` option callback.
- @details Prints installed package version and exits before command dispatch
when either version flag is present.
- @param ctx {click.Context} Active Click context.
- @param param {click.Parameter} Option metadata (unused).
- @param value {bool} Parsed version-option flag value.
- @return {None} Function return value.
- @satisfies REQ-078

### fn `def _handle_enable_log_option(` `priv` (L780-781)
- @brief Persist runtime logging-flag updates into runtime config.
- @details Loads current `RuntimeConfig`, applies provided logging-flag
overrides, writes updated config to disk, and emits one configuration log
entry when execution logging is enabled after update.
- @param log_enabled {bool | None} Optional replacement for `log_enabled`.
- @param debug_enabled {bool | None} Optional replacement for `debug_enabled`.
- @return {None} Function return value.
- @satisfies REQ-107
- @satisfies REQ-109
- @satisfies REQ-110

### fn `def _handle_disable_log_option(` `priv` (L801-802)
- @brief Enable runtime execution logging via eager CLI option.
- @details Sets `RuntimeConfig.log_enabled` to true without mutating
`RuntimeConfig.debug_enabled`, then exits before command dispatch.
- @param ctx {click.Context} Active Click context.
- @param param {click.Parameter} Option metadata (unused).
- @param value {bool} Parsed `--enable-log` flag value.
- @return {None} Function return value.
- @satisfies REQ-107
- @satisfies REQ-109

### fn `def _handle_enable_debug_option(` `priv` (L822-823)
- @brief Disable runtime execution logging via eager CLI option.
- @details Sets `RuntimeConfig.log_enabled` to false without mutating
`RuntimeConfig.debug_enabled`, then exits before command dispatch.
- @param ctx {click.Context} Active Click context.
- @param param {click.Parameter} Option metadata (unused).
- @param value {bool} Parsed `--disable-log` flag value.
- @return {None} Function return value.
- @satisfies REQ-107
- @satisfies REQ-109

### fn `def _handle_disable_debug_option(` `priv` (L843-844)
- @brief Enable runtime API debug logging via eager CLI option.
- @details Sets `RuntimeConfig.debug_enabled` to true without mutating
`RuntimeConfig.log_enabled`, then exits before command dispatch.
- @param ctx {click.Context} Active Click context.
- @param param {click.Parameter} Option metadata (unused).
- @param value {bool} Parsed `--enable-debug` flag value.
- @return {None} Function return value.
- @satisfies REQ-107
- @satisfies REQ-110

### class `class StartupPreflightGroup(click.Group)` : click.Group (L864-959)
- @brief Disable runtime API debug logging via eager CLI option.
- @brief Click group subclass that enforces startup preflight ordering and preserves epilog formatting.
- @details Sets `RuntimeConfig.debug_enabled` to false without mutating
`RuntimeConfig.log_enabled`, then exits before command dispatch.
- @details Executes startup update-check preflight before Click argument parsing and command dispatch. This guarantees preflight execution even when invocation later fails due to invalid arguments. Overrides epilog rendering to preserve multi-line example formatting without text wrapping.
- @param ctx {click.Context} Active Click context.
- @param param {click.Parameter} Option metadata (unused).
- @param value {bool} Parsed `--disable-debug` flag value.
- @return {None} Function return value.
- @satisfies REQ-107
- @satisfies REQ-110
- @satisfies REQ-070, REQ-068
- fn `def format_epilog(` (L874-877)
  - @brief Click group subclass that enforces startup preflight ordering and preserves epilog formatting.
  - @details Executes startup update-check preflight before Click argument
parsing and command dispatch. This guarantees preflight execution even when
invocation later fails due to invalid arguments. Overrides epilog rendering
to preserve multi-line example formatting without text wrapping.
  - @satisfies REQ-070, REQ-068
- fn `def main(` (L894-901)
  - @brief Render epilog text preserving explicit line breaks.
  - @details Writes each epilog line verbatim to the help formatter,
bypassing Click's default text-wrapping behavior that collapses
multi-line examples into a single paragraph.
  - @param ctx {click.Context} Click invocation context.
  - @param formatter {click.HelpFormatter} Help output formatter instance.
  - @return {None} Function return value.
  - @satisfies REQ-068

### fn `def _normalize_utc(value: datetime) -> datetime` `priv` (L960-972)
- @brief Normalize datetime values to timezone-aware UTC instances.
- @details Ensures consistent timestamp arithmetic for idle-time persistence and refresh-delay computations when source datetimes are naive or non-UTC.
- @param value {datetime} Source datetime to normalize.
- @return {datetime} Timezone-aware UTC datetime.

### fn `def _format_local_datetime(value: datetime) -> str` `priv` (L973-985)
- @brief Format one datetime in local timezone with `%Y-%m-%d %H:%M`.
- @details Normalizes source datetime to UTC, projects it to runtime local timezone, and emits minute-precision text for CLI freshness labels.
- @param value {datetime} Source datetime to format.
- @return {str} Local timezone datetime string.
- @satisfies REQ-084

### fn `def _epoch_to_utc_datetime(epoch_seconds: int) -> datetime` `priv` (L986-994)
- @brief Convert epoch-seconds to timezone-aware UTC datetime.
- @param epoch_seconds {int} Epoch timestamp in seconds.
- @return {datetime} UTC datetime from epoch.

### fn `def _build_freshness_line(` `priv` (L995-997)

### fn `def _next_utc_month_boundary(reference_time: datetime | None = None) -> datetime` `priv` (L1022-1051)
- @brief Build `Updated/Next` freshness line for CLI panel rendering.
- @brief Resolve the first UTC instant of the next calendar month.
- @details Uses provider idle-time state when available (`last_success_timestamp`,
`idle_until_timestamp`) and falls back to payload `updated_at` plus runtime
interval fallback (`60s`) when idle-time state is unavailable.
- @details Normalizes an optional reference time to UTC, truncates it to the current month boundary, and returns the next month boundary. CLI OpenRouter rendering uses this helper to restore `Resets in:` output when the provider payload omits `metrics.reset_at` for its monthly quota surface. Time complexity O(1). Space complexity O(1).
- @param result {ProviderResult} Provider result carrying fallback `updated_at`.
- @param freshness_state {IdleTimeState | None} Provider idle-time state.
- @param reference_time {datetime | None} Optional source datetime. `None` uses current UTC time.
- @return {str} Deterministic `Updated: ..., Next: ...` label.
- @return {datetime} First UTC instant of the next calendar month.
- @satisfies REQ-084
- @satisfies REQ-011
- @satisfies REQ-034

### fn `def _apply_api_call_delay(throttle_state: dict[str, float | int] | None) -> None` `priv` (L1052-1081)
- @brief Enforce minimum spacing between consecutive provider API calls.
- @details Uses monotonic clock values in `throttle_state` to sleep before a live API request when elapsed time is below configured delay.
- @param throttle_state {dict[str, float | int] | None} Mutable state containing `delay_milliseconds` and `last_call_started`.
- @return {None} Function return value.
- @satisfies REQ-040

### fn `def _coerce_retry_after_seconds(value: object) -> int | None` `priv` (L1082-1113)
- @brief Normalize retry-after metadata to positive integer seconds.
- @details Accepts integer/float/string payload values and converts them to normalized relative-delay seconds. When numeric values represent absolute epoch timestamps (seconds or milliseconds), converts them to `max(0, epoch-now)`. Non-numeric, invalid, and non-positive values return None.
- @param value {object} Retry-after candidate value.
- @return {int | None} Positive retry-after seconds or None when unavailable.
- @satisfies REQ-037
- @satisfies REQ-041

### fn `def _extract_retry_after_seconds(result: ProviderResult) -> int` `priv` (L1114-1134)
- @brief Extract normalized retry-after seconds from provider error payload.
- @details Reads `raw.retry_after_seconds` and clamps to non-negative integer seconds. When unavailable and payload marks `raw.retry_after_unavailable=true`, returns `RuntimeConfig.default_retry_after_seconds`. Invalid or missing values without fallback marker normalize to zero.
- @param result {ProviderResult} Provider result to inspect.
- @return {int} Non-negative retry-after delay in seconds.
- @satisfies REQ-041

### fn `def _classify_provider_failure_log_category(result: ProviderResult) -> str | None` `priv` (L1135-1155)
- @brief Classify provider failure category for runtime logging.
- @details Maps failed provider results to runtime-log categories used by logging requirement checks. Returns `rate_limit` when `raw.status_code` is `429`; returns `oauth` when error text contains OAuth-authentication markers.
- @param result {ProviderResult} Provider result candidate.
- @return {str | None} Failure category token or None when not log-targeted.
- @satisfies REQ-115

### fn `def _append_provider_failure_runtime_log(result: ProviderResult) -> None` `priv` (L1156-1193)
- @brief Append runtime-log row for OAuth and rate-limit provider failures.
- @details Emits non-debug runtime-log entries for provider failure categories `oauth` and `rate_limit` when logging is enabled. Includes `retry_after_seconds` plus extraction source when available; when unavailable, appends explicit `retry_after_unavailable=true` evidence payload.
- @param result {ProviderResult} Provider result to log.
- @return {None} Function return value.
- @satisfies REQ-115

### fn `def _extract_retry_after_for_failure_log(result: ProviderResult) -> tuple[int | None, str]` `priv` (L1194-1225)
- @brief Extract retry-after seconds and source path for failure runtime logs.
- @details Probes normalized and fallback raw payload fields in deterministic order: `raw.retry_after_seconds`, `raw.retry_after`, `raw.error.retry_after_seconds`, and `raw.error.retry_after`. Returns first positive parsed value.
- @param result {ProviderResult} Provider result to inspect.
- @return {tuple[int | None, str]} Tuple `(retry_after_seconds_or_none, source_key)`.
- @satisfies REQ-115

### fn `def _retry_after_probe_payload(raw_payload: dict[str, object]) -> dict[str, object]` `priv` (L1226-1249)
- @brief Build compact retry-after probe evidence for failure runtime logs.
- @details Serializes inspected retry-after fields and top-level key inventory so logs provide explicit evidence when retry-after extraction fails.
- @param raw_payload {dict[str, object]} Provider raw payload dictionary.
- @return {dict[str, object]} JSON-safe probe payload.
- @satisfies REQ-115

### fn `def _is_claude_oauth_authentication_error(message: object) -> bool` `priv` (L1250-1262)
- @brief Detect canonical Claude OAuth authentication-expired error text.
- @details Applies strict substring match against `Invalid or expired OAuth token` using case-sensitive semantics so retry/renewal logic is only enabled for the documented Claude token-expiration failure.
- @param message {object} Candidate error message object.
- @return {bool} True when candidate contains canonical Claude auth-expired text.
- @satisfies REQ-102

### fn `def _subprocess_return_code_from_exception(exc: Exception) -> int` `priv` (L1263-1280)
- @brief Normalize subprocess exception to deterministic integer return code.
- @details Maps TimeoutExpired to `124`, CalledProcessError to its integer return code when available, and all other exception classes to `1`.
- @param exc {Exception} Subprocess exception emitted by `subprocess.run`.
- @return {int} Deterministic synthetic return code.

### fn `def _execute_claude_refresh_command(` `priv` (L1281-1283)

### fn `def _run_claude_oauth_token_refresh(runtime_config: RuntimeConfig) -> bool` `priv` (L1313-1367)
- @brief Execute one Claude token-refresh subprocess command.
- @brief Execute one Claude OAuth token-renewal routine in-process.
- @details Runs command without shell expansion, captures combined stdout/stderr,
and enforces timeout using runtime `api_call_timeout_milliseconds` policy.
Command-not-found and timeout failures are converted to deterministic error
tuples without raising.
- @details Truncates `~/.config/aibar/claude_token_refresh.log`, then executes `claude /usage` followed by `aibar login --provider claude` when each command is available in PATH. Applies configured API-call delay spacing and configured API-call timeout to each subprocess call. Command failures are logged and do not raise; function returns true only when both available commands complete successfully.
- @param command {list[str]} Subprocess argv tokens.
- @param timeout_seconds {float} Timeout in seconds for command completion.
- @param runtime_config {RuntimeConfig} Runtime delay and timeout configuration.
- @return {tuple[bool, int, str]} Tuple `(success, return_code, output_text)`.
- @return {bool} True when refresh routine completes without command failures.
- @satisfies REQ-101
- @satisfies REQ-100
- @satisfies REQ-101

### fn `def _clear_claude_refresh_block_flag(` `priv` (L1368-1369)

### fn `def _is_claude_refresh_block_active(` `priv` (L1389-1391)
- @brief Clear Claude OAuth refresh-block flag from idle-time state.
- @details Removes `oauth_refresh_blocked` by replacing the Claude state entry
with an equivalent object where `oauth_refresh_blocked=false`.
- @param idle_time_by_provider {dict[str, IdleTimeState]} Provider idle-time map.
- @return {bool} True when map content changed.
- @satisfies REQ-105

### fn `def _is_claude_authentication_error_result(result: ProviderResult) -> bool` `priv` (L1409-1424)
- @brief Evaluate Claude OAuth refresh-block activity against hardcoded TTL.
- @brief Detect Claude result carrying canonical OAuth authentication-expired error.
- @details Returns true only when `oauth_refresh_blocked` is true and current
epoch is not greater than `last_success_timestamp + 86400`.
- @details Matches provider key `claude`, error-state flag, and canonical error text `Invalid or expired OAuth token` for deterministic renewal triggering.
- @param claude_state {IdleTimeState} Claude provider idle-time state.
- @param now_epoch {int} Current epoch seconds.
- @param result {ProviderResult} Provider result candidate.
- @return {bool} True when refresh-block flag remains active.
- @return {bool} True when result is Claude auth-expired failure.
- @satisfies REQ-105
- @satisfies REQ-102

### fn `def _handle_claude_oauth_refresh_on_auth_error(` `priv` (L1425-1428)

### fn `def _update_claude_refresh_block_state(` `priv` (L1459-1461)
- @brief Execute Claude auth-error renewal-and-retry control flow.
- @details Runs one in-process Claude token-renewal routine, reloads provider
token from current environment/CLI credentials, and then executes exactly one
Claude dual-window API retry via `_fetch_claude_dual`.
- @param runtime_config {RuntimeConfig} Runtime delay/timeout configuration.
- @param throttle_state {dict[str, float | int] | None} Shared API-delay state.
- @return {tuple[ProviderResult, ProviderResult, bool]} Tuple
`(retry_result_5h, retry_result_7d, retry_auth_failed)`.
- @satisfies REQ-103
- @satisfies REQ-104

### fn `def _fetch_claude_dual_with_auth_recovery(` `priv` (L1489-1491)
- @brief Persist Claude OAuth refresh-block boolean in idle-time state map.
- @details Creates missing Claude idle-time entry when needed using current UTC
timestamps, then updates `oauth_refresh_blocked` only when value changes.
- @param idle_time_by_provider {dict[str, IdleTimeState]} Provider idle-time map.
- @param blocked {bool} Target flag value for `claude.oauth_refresh_blocked`.
- @return {bool} True when state map changed.
- @satisfies REQ-104
- @satisfies REQ-105

### fn `def _clear_expired_claude_refresh_block(` `priv` (L1544-1545)
- @brief Fetch Claude dual-window results with auth-expired recovery policy.
- @details Executes one dual-window Claude fetch. When canonical auth-expired
error appears, checks `claude.oauth_refresh_blocked` in idle-time state with
hardcoded 86400-second TTL from `last_success_timestamp`; when unblocked,
performs one token-renewal routine and one dual-window retry. On repeated
auth failure, persists `oauth_refresh_blocked=true`; on success, clears flag.
- @param provider {ClaudeOAuthProvider} Claude provider instance.
- @param throttle_state {dict[str, float | int] | None} Shared API-delay state.
- @return {tuple[ProviderResult, ProviderResult]} Final Claude `(5h, 7d)` results.
- @satisfies REQ-102
- @satisfies REQ-103
- @satisfies REQ-104
- @satisfies REQ-105

### fn `def _is_http_429_result(result: ProviderResult) -> bool` `priv` (L1564-1574)
- @brief Auto-clear expired Claude OAuth refresh-block state.
- @brief Check whether result payload represents HTTP 429 rate limiting.
- @details Clears `claude.oauth_refresh_blocked` when current epoch is greater
than `last_success_timestamp + 86400` using hardcoded TTL policy.
- @details Uses normalized raw payload marker `status_code == 429`.
- @param idle_time_by_provider {dict[str, IdleTimeState]} Provider idle-time map.
- @param result {ProviderResult} Provider result to classify.
- @return {bool} True when state map changed.
- @return {bool} True when result indicates HTTP 429.
- @satisfies REQ-105
- @satisfies REQ-041

### fn `def _serialize_results_payload(` `priv` (L1575-1576)

### fn `def _empty_cache_document() -> dict[str, object]` `priv` (L1593-1607)
- @brief Serialize ProviderResult mapping to `show --json` payload schema.
- @brief Build empty cache document in canonical sectioned schema.
- @details Converts each provider result to JSON-safe dict using Pydantic
serialization with stable key structure.
- @details Returns deterministic cache shape with top-level `payload` and `status` objects so downstream consumers can parse stable keys without null checks.
- @param results {dict[str, ProviderResult]} Provider results keyed by provider id.
- @return {dict[str, dict[str, object]]} JSON payload suitable for CLI output and cache.
- @return {dict[str, object]} Empty cache document.
- @satisfies REQ-003
- @satisfies CTN-004
- @satisfies CTN-004
- @satisfies REQ-003

### fn `def _normalize_cache_document(` `priv` (L1608-1609)

### fn `def _cache_payload_section(cache_document: dict[str, object]) -> dict[str, object]` `priv` (L1632-1644)
- @brief Normalize decoded cache payload to canonical sectioned schema.
- @brief Extract payload section from canonical cache document.
- @details Accepts decoded cache document and enforces object-typed `payload` and
`status` sections. Missing or invalid sections normalize to empty objects.
- @details Returns mutable provider-result mapping from normalized document.
- @param cache_document {dict[str, object] | None} Decoded cache payload from disk.
- @param cache_document {dict[str, object]} Canonical cache document.
- @return {dict[str, object]} Canonical cache document with `payload`/`status`.
- @return {dict[str, object]} Provider payload section.
- @satisfies CTN-004
- @satisfies REQ-003

### fn `def _cache_status_section(cache_document: dict[str, object]) -> dict[str, object]` `priv` (L1645-1657)
- @brief Extract status section from canonical cache document.
- @details Returns mutable provider/window status mapping from normalized document.
- @param cache_document {dict[str, object]} Canonical cache document.
- @return {dict[str, object]} Provider/window status section.

### fn `def _serialize_attempt_status(result: ProviderResult) -> dict[str, object]` `priv` (L1658-1678)
- @brief Serialize one provider/window fetch attempt status for cache persistence.
- @details Converts ProviderResult error state to status object using `OK`/`FAIL`, preserving error text, update timestamp, and optional HTTP status code.
- @param result {ProviderResult} Provider result from current refresh attempt.
- @return {dict[str, object]} Attempt-status payload.
- @satisfies REQ-044

### fn `def _record_attempt_status(` `priv` (L1679-1681)

### fn `def _extract_claude_snapshot_from_cache_document(` `priv` (L1701-1702)
- @brief Persist one provider/window attempt status into cache status section.
- @details Upserts `status[provider][window]` with serialized attempt metadata and
preserves statuses for untouched providers/windows.
- @param status_section {dict[str, object]} Mutable cache status section.
- @param result {ProviderResult} Provider result to encode.
- @return {None} Function return value.
- @satisfies REQ-044
- @satisfies REQ-046

### fn `def _get_window_attempt_status(` `priv` (L1717-1720)
- @brief Extract persisted Claude dual-window payload from cache document.
- @details Reads Claude entry from cache `payload` section and normalizes it into
a dual-window raw payload (`five_hour`, `seven_day`) for HTTP 429 restoration.
- @param cache_document {dict[str, object]} Canonical cache document.
- @return {dict[str, object] | None} Normalized dual-window payload or None.
- @satisfies REQ-047

### fn `def _overlay_cached_failure_status(` `priv` (L1740-1744)
- @brief Read provider/window attempt status from cache status section.
- @details Resolves nested `status[provider][window]` object and validates mapping
shape before returning it to projection helpers.
- @param status_section {dict[str, object]} Cache status section.
- @param provider_key {str} Provider identifier.
- @param window {WindowPeriod} Window identifier.
- @return {dict[str, object] | None} Attempt status object or None.

### fn `def _filter_cached_payload(` `priv` (L1795-1798)
- @brief Overlay cached failure status onto projected result.
- @details Reads `status[provider][window]`; when status marks `FAIL` with a
non-empty error string, returns a copy of projected result carrying the cached
error and optional status code while preserving payload metrics.
- @param provider_key {str} Provider id in cache sections.
- @param target_window {WindowPeriod} Requested window used for status lookup.
- @param projected_result {ProviderResult} Cached payload result after projection.
- @param status_section {dict[str, object]} Cache status section.
- @return {ProviderResult} Result with overlaid cached error state when applicable.
- @satisfies REQ-085
- @satisfies REQ-060
- @satisfies REQ-061

### fn `def _filter_idle_time_by_provider(` `priv` (L1854-1857)
- @brief Filter canonical cache document by provider selector and enable-state.
- @details Filters both cache sections (`payload`, `status`) so output
contains only provider nodes allowed by `allowed_provider_keys` and the
optional selected provider. Schema keys remain stable even when all
providers are filtered out.
- @param cache_document {dict[str, object]} Canonical cache document.
- @param provider_filter {ProviderName | None} Optional provider selector.
- @param allowed_provider_keys {set[str] | None} Optional enabled-provider key set.
- @return {dict[str, object]} Filtered cache document with canonical sections.
- @satisfies REQ-126

### fn `def _enabled_provider_keys(runtime_config: RuntimeConfig) -> set[str]` `priv` (L1890-1909)
- @brief Filter provider-keyed idle-time map by selector and enable-state.
- @brief Resolve enabled-provider key set from runtime configuration.
- @details Converts `resolve_enabled_providers(...)` mapping output into a set of enabled provider keys used by cache, idle-time, and render filtering. Time complexity O(P). Space complexity O(P), where P is provider count.
- @param idle_time_by_provider {dict[str, IdleTimeState]} Provider idle-time state map.
- @param provider_filter {ProviderName | None} Optional provider selector.
- @param allowed_provider_keys {set[str] | None} Optional enabled-provider key set.
- @param runtime_config {RuntimeConfig} Runtime configuration carrying provider flags.
- @return {dict[str, IdleTimeState]} Filtered provider idle-time map.
- @return {set[str]} Enabled provider keys.
- @satisfies REQ-003
- @satisfies REQ-084
- @satisfies REQ-124
- @satisfies REQ-126
- @satisfies CTN-017
- @satisfies REQ-123
- @satisfies REQ-124
- @satisfies REQ-126

### fn `def _serialize_enabled_providers(` `priv` (L1910-1911)

### fn `def _serialize_idle_time_state(` `priv` (L1927-1928)
- @brief Serialize provider-enable flags for `show --json`.
- @details Returns normalized provider-keyed booleans for all known
providers. Missing config keys normalize to `true` for backward
compatibility.
- @param runtime_config {RuntimeConfig} Runtime configuration carrying provider flags.
- @return {dict[str, bool]} Provider-keyed enabled-state mapping.
- @satisfies CTN-017
- @satisfies REQ-126
- @satisfies REQ-127

### fn `def _serialize_freshness_state(` `priv` (L1943-1944)
- @brief Serialize provider-keyed idle-time state for `show --json`.
- @param idle_time_by_provider {dict[str, IdleTimeState]} Provider idle-time map.
- @return {dict[str, dict[str, object]]} JSON-safe provider idle-time section.
- @satisfies REQ-003
- @satisfies CTN-009

### fn `def _fixed_effective_window(provider_name: ProviderName) -> WindowPeriod | None` `priv` (L1968-1982)
- @brief Serialize provider-keyed freshness data for `show --json`.
- @brief Resolve provider fixed effective window override for `show` surfaces.
- @details Projects idle-time timestamps into GNOME-aligned `freshness` entries and
emits local-time `%Y-%m-%d %H:%M` strings for direct parity checks.
- @details Returns `30d` for providers that ignore requested window arguments and must expose a canonical window in payload, text, and JSON output.
- @param idle_time_by_provider {dict[str, IdleTimeState]} Provider idle-time map.
- @param provider_name {ProviderName} Provider enum key.
- @return {dict[str, dict[str, object]]} JSON-safe provider freshness section.
- @return {WindowPeriod | None} Fixed window override, or None when provider is variable-window.
- @satisfies REQ-003
- @satisfies REQ-084
- @satisfies REQ-010
- @satisfies REQ-011
- @satisfies REQ-012
- @satisfies REQ-097

### fn `def _serialize_extension_window_labels(` `priv` (L1983-1984)

### fn `def _project_cached_window(` `priv` (L2007-2010)
- @brief Serialize provider window labels for GNOME extension bar rendering.
- @details Exports provider-keyed fixed window labels from canonical
fixed-window provider mapping for `show --json` `extension.window_labels`.
When `enabled_provider_keys` is provided, disabled providers are omitted.
- @param enabled_provider_keys {set[str] | None} Optional enabled-provider key set.
- @return {dict[str, str]} Provider-keyed window label map.
- @satisfies REQ-003
- @satisfies REQ-017
- @satisfies REQ-126

### fn `def _load_cached_results(` `priv` (L2063-2067)
- @brief Project cached raw payload to requested window without network I/O.
- @details Attempts provider-specific `_parse_response` projection when cached
window differs from requested window; providers with fixed effective windows
(`copilot`, `openrouter`, `openai`, `geminiai`) bypass projection and preserve
canonical window values.
Returns original result on projection failure or when parser is unavailable.
- @param result {ProviderResult} Cached normalized provider result.
- @param target_window {WindowPeriod} Requested CLI window.
- @param providers {dict[ProviderName, BaseProvider]} Provider registry.
- @return {ProviderResult} Result aligned to requested window when possible.
- @satisfies REQ-009
- @satisfies REQ-010
- @satisfies REQ-011
- @satisfies REQ-012
- @satisfies REQ-042
- @satisfies REQ-097

### fn `def _update_idle_time_after_refresh(` `priv` (L2111-2113)
- @brief Decode cached JSON payload into ProviderResult mapping.
- @details Validates cached payload entries using `ProviderResult` schema, applies
provider filtering, and projects cached windows to requested window when possible.
Invalid entries are skipped. GeminiAI cached FAIL status is overlaid from `status`
section onto projected payload result for surface-level error rendering.
- @param cache_document {dict[str, object]} Canonical cache document loaded from disk.
- @param provider_filter {ProviderName | None} Optional provider selector.
- @param target_window {WindowPeriod} Requested CLI window for projection.
- @param providers {dict[ProviderName, BaseProvider]} Provider registry.
- @return {dict[str, ProviderResult]} Validated cached results keyed by provider id.
- @satisfies REQ-009
- @satisfies REQ-042
- @satisfies REQ-044
- @satisfies REQ-046
- @satisfies REQ-060

### fn `def _project_next_reset(resets_at_str: str, window: WindowPeriod) -> datetime | None` `priv` (L2194-2225)
- @brief Persist provider-scoped idle-time metadata after refresh completion.
- @brief Compute the next reset boundary after a stale resets_at timestamp.
- @details Computes per-provider idle-time state after refresh execution.
Successful-only provider cycles schedule `idle_until = last_success_at + idle_delay_seconds`.
Provider cycles containing failures schedule
`idle_until = last_attempt_at + max(idle_delay_seconds, resolved_retry_after_seconds)`,
where fallback resolution uses `RuntimeConfig.default_retry_after_seconds` when
provider payload marks `retry_after_unavailable=true`.
- @details Advances `resets_at_str` by multiples of the window period until the result is strictly greater than current UTC time. Returns None if `resets_at_str` is unparseable or the window period is not in `_WINDOW_PERIOD_TIMEDELTA`.
- @param fetched_results {list[ProviderResult]} Live results produced by refresh calls.
- @param runtime_config {RuntimeConfig} Runtime delay configuration.
- @param resets_at_str {str} ISO 8601 timestamp string of the last known reset boundary. May have a Z suffix (converted to +00:00) or an explicit timezone offset.
- @param window {WindowPeriod} Window period whose duration drives the projection step.
- @return {None} Function return value.
- @return {datetime | None} Projected future reset datetime in UTC, or None on parse error.
- @note Uses `math.ceil` to determine the minimum number of full cycles to advance.
- @satisfies REQ-038
- @satisfies REQ-041
- @satisfies REQ-002

### fn `def _apply_reset_projection(result: ProviderResult) -> ProviderResult` `priv` (L2226-2260)
- @brief Return a copy of `result` with `metrics.reset_at` set to the projected next reset boundary when it is currently None but the raw payload contains a parseable past `resets_at` string for the result's window.
- @details When a ProviderResult is obtained from stale disk cache (last-good path) or from a cross-window raw re-parse, `_parse_response` correctly sets `reset_at=None` for past timestamps. This function recovers the display information by projecting the next future reset boundary from the raw payload's `resets_at` field, ensuring the 'Resets in:' countdown is shown even when the cached timestamp has already elapsed. If `reset_at` is already non-None, or the raw payload has no parseable `resets_at` for the window, or projection fails, the original result is returned unchanged.
- @param result {ProviderResult} Candidate result whose reset_at may require projection.
- @return {ProviderResult} Original result unchanged if no projection is needed; otherwise a new ProviderResult with metrics.reset_at set to the projected datetime.
- @see _project_next_reset
- @satisfies REQ-002

### fn `def get_providers() -> dict[ProviderName, BaseProvider]` (L2261-2276)
- @brief Execute get providers.
- @details Applies get providers logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {dict[ProviderName, BaseProvider]} Function return value.

### fn `def parse_window(window: str) -> WindowPeriod` (L2277-2296)
- @brief Execute parse window.
- @details Applies parse window logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {str} Input parameter `window`.
- @return {WindowPeriod} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def parse_provider(provider: str) -> ProviderName | None` (L2297-2313)
- @brief Execute parse provider.
- @details Applies parse provider logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param provider {str} Input parameter `provider`.
- @return {ProviderName | None} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _provider_result_debug_summary(result: ProviderResult) -> str` `priv` (L2314-2339)
- @brief Serialize provider result payload for debug log rows.
- @details Builds JSON summary including provider id, window id, error state, error text, and raw payload object using deterministic key ordering. Serialization failures fallback to minimal scalar diagnostics.
- @param result {ProviderResult} Provider result instance to summarize.
- @return {str} JSON debug summary string.
- @satisfies REQ-114

### fn `def _extract_error_json_payload_for_debug_log(result: ProviderResult) -> str | None` `priv` (L2340-2361)
- @brief Extract unmodified JSON error payload text for debug logging.
- @details Returns the original `raw["body"]` string only when provider result is an error and `raw["body"]` is a syntactically valid JSON text payload. Content is returned byte-for-byte without normalization or re-serialization.
- @param result {ProviderResult} Provider result instance to inspect.
- @return {str | None} Raw JSON payload text, or None when unavailable/non-JSON.
- @satisfies REQ-114

### fn `def _append_provider_debug_runtime_log(result: ProviderResult) -> None` `priv` (L2362-2387)
- @brief Append debug runtime-log rows for one provider fetch result.
- @details Emits canonical provider debug summary row and, for failed API calls with JSON error bodies, appends an additional row including the full unmodified JSON response payload exactly as received from the API.
- @param result {ProviderResult} Provider result to log.
- @return {None} Function return value.
- @satisfies REQ-114

### fn `def _fetch_result(` `priv` (L2388-2391)

### fn `def _fetch_claude_dual(` `priv` (L2468-2470)
- @brief Execute one provider refresh call without legacy TTL cache reuse.
- @details Executes throttled provider fetch and returns normalized success/error
results. Claude 5h/7d requests are routed through
`_fetch_claude_dual_with_auth_recovery` so one API request can provide
deterministic dual-window normalization with OAuth auth-error recovery.
- @param provider {BaseProvider} Provider instance to fetch from.
- @param window {WindowPeriod} Time window for the fetch.
- @param throttle_state {dict[str, float | int] | None} Mutable throttling state
used to enforce inter-call spacing for live API requests.
- @return {ProviderResult} Refreshed provider result for requested window.
- @satisfies CTN-004
- @satisfies REQ-043
- @satisfies REQ-040
- @satisfies REQ-112
- @satisfies REQ-114
- @satisfies REQ-115

### fn `def _extract_claude_dual_payload(` `priv` (L2550-2552)
- @brief Fetch Claude 5h and 7d results via a single API call.
- @details Executes ClaudeOAuthProvider.fetch_all_windows for 5h and 7d on each invocation.
Returns normalized provider results exactly as fetched (or synthesized error
results on exception) without partial-window metric fallback.
- @param provider {ClaudeOAuthProvider} Claude provider instance.
- @param throttle_state {dict[str, float | int] | None} Mutable throttling state
used to enforce inter-call spacing for live API requests.
- @return {tuple[ProviderResult, ProviderResult]} (5h_result, 7d_result).
- @satisfies REQ-002, REQ-036, REQ-037, CTN-004, REQ-040, REQ-043
- @satisfies REQ-112
- @satisfies REQ-114

### fn `def _normalize_claude_dual_payload(payload: object) -> dict[str, object] | None` `priv` (L2574-2596)
- @brief Extract dual-window Claude payload dictionary from successful results.
- @brief Normalize persisted Claude payload shape into dual-window raw dictionary.
- @details Returns first raw payload containing both `five_hour` and `seven_day`
mapping objects. Returns None when payload shape is invalid.
- @details Accepts either direct dual-window payload (`five_hour`/`seven_day`) or serialized ProviderResult dictionaries containing a `raw` field with that shape.
- @param result_5h {ProviderResult} Claude five-hour result.
- @param result_7d {ProviderResult} Claude seven-day result.
- @param payload {object} Decoded JSON object from snapshot candidate file.
- @return {dict[str, object] | None} Serializable payload or None.
- @return {dict[str, object] | None} Normalized dual-window payload or None.
- @satisfies CTN-004
- @satisfies REQ-047
- @satisfies REQ-036

### fn `def _extract_snapshot_reset_at(` `priv` (L2597-2599)

### fn `def _extract_snapshot_utilization(` `priv` (L2622-2624)
- @brief Resolve projected reset timestamp from persisted Claude snapshot payload.
- @details Uses window-specific `resets_at` string from persisted payload and
projects next reset boundary through `_project_next_reset`.
- @param snapshot_payload {dict[str, object] | None} Persisted dual-window payload.
- @param window {WindowPeriod} Target window period.
- @return {datetime | None} Projected reset timestamp or None.
- @satisfies REQ-036

### fn `def _is_claude_rate_limited_result(result: ProviderResult) -> bool` `priv` (L2653-2668)
- @brief Resolve utilization percentage from persisted Claude snapshot payload.
- @brief Check whether a ProviderResult represents Claude HTTP 429.
- @details Reads window-specific `utilization`, validates finite range, and clamps
values to [0.0, 100.0] for deterministic percentage rendering.
- @details Matches normalized Claude error payloads by provider identity, error-state flag, and `raw.status_code == 429`.
- @param snapshot_payload {dict[str, object] | None} Persisted dual-window payload.
- @param window {WindowPeriod} Target window period.
- @param result {ProviderResult} Result to classify.
- @return {float | None} Clamped utilization percentage or None.
- @return {bool} True when result is Claude 429.
- @satisfies REQ-036
- @satisfies REQ-036

### fn `def _build_claude_rate_limited_partial_result(` `priv` (L2669-2672)

### fn `def _refresh_and_persist_cache_payload(` `priv` (L2717-2721)
- @brief Build Claude 429 partial-window result using persisted payload when available.
- @details For 5h window, usage is always forced to 100.0% while reset time is read
from persisted payload (`five_hour.resets_at`) when possible. For 7d window,
utilization and reset are restored from persisted payload (`seven_day`) when
available; otherwise synthetic window-based fallback values are used.
- @param window {WindowPeriod} Window associated with the synthetic result.
- @param include_error {bool} True to include `Rate limited...` error text.
- @param snapshot_payload {dict[str, object] | None} Persisted Claude payload for
429 restoration.
- @return {ProviderResult} Claude result suitable for partial-window display.
- @satisfies REQ-036
- @satisfies REQ-037

### fn `def retrieve_results_via_cache_pipeline(` (L2829-2834)
- @brief Execute modular API calls, merge results into cache in memory, then persist.
- @details Executes provider fetches for configured providers only, records
per-provider/window attempt status in memory, updates payload only for successful
provider/window outcomes, computes new idle-time values using
`idle_until = max(current_time + retry_after, current_time + idle_delay)` for errors,
then writes updated `cache.json` and `idle-time.json` under lock in a single write.
The `cache_document` parameter is the previously loaded cache content passed from
`retrieve_results_via_cache_pipeline` to avoid redundant disk reads.
- @param providers {dict[ProviderName, BaseProvider]} Provider scope for refresh.
- @param target_window {WindowPeriod} Requested window for refresh execution.
- @param runtime_config {RuntimeConfig} Runtime throttling configuration.
- @param cache_document {dict[str, object]} Previously loaded canonical cache document.
- @return {dict[str, object]} Updated cache document after merge and persistence.
- @satisfies CTN-004
- @satisfies REQ-009
- @satisfies REQ-038
- @satisfies REQ-041
- @satisfies REQ-043
- @satisfies REQ-044
- @satisfies REQ-045
- @satisfies REQ-046
- @satisfies REQ-047
- @satisfies REQ-066
- @satisfies REQ-091
- @satisfies REQ-092
- @satisfies REQ-094

### fn `def _build_cached_dual_window_results(` `priv` (L3030-3033)
- @brief Execute shared cache-based retrieval pipeline for CLI `show`.
- @details Implements the canonical `show` process flow:
(1) Evaluate idle-time per provider to determine refresh need.
(2) If at least one provider has expired idle-time: execute modular API calls
only for expired providers, collect results in memory, compute new idle-time
values, write updated `cache.json` and `idle-time.json` under lock file.
(3) Read `cache.json` under lock file (single read per execution).
(4) Return decoded results for presentation.
Performs at most one `load_cli_cache` disk read per execution when no refresh is
needed, and at most one read (before refresh) plus one write when refresh occurs.
After refresh, the in-memory cache document is used directly without a second read.
- @param provider_filter {ProviderName | None} Optional provider selector.
- @param target_window {WindowPeriod} Target window requested by caller.
- @param force_refresh {bool} Force-refresh flag for current execution.
- @param providers {dict[ProviderName, BaseProvider]} Provider registry.
- @param enabled_provider_keys {set[str] | None} Optional enabled-provider key set.
- @return {RetrievalPipelineOutput} Shared retrieval state and decoded results.
- @satisfies REQ-009
- @satisfies REQ-039
- @satisfies REQ-042
- @satisfies REQ-043
- @satisfies REQ-044
- @satisfies REQ-045
- @satisfies REQ-046
- @satisfies REQ-047
- @satisfies REQ-066
- @satisfies REQ-091
- @satisfies REQ-092
- @satisfies REQ-093
- @satisfies REQ-094
- @satisfies REQ-124
- @satisfies REQ-126

### fn `def main(ctx: click.Context) -> None` `@click.pass_context` (L3149-3159)
- @brief Execute main.
- @details Applies main logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.
- @satisfies REQ-068

### fn `def show(provider: str, window: str, output_json: bool, force_refresh: bool) -> None` (L3192-3391)
- @brief Execute `show` with idle-time cache gating and throttled provider refresh.
- @details Delegates provider retrieval to a shared cache-based pipeline that applies force handling, idle-time gating, conditional cache refresh, and deterministic readback from `cache.json` before rendering. When `--provider` targets `copilot`, `openrouter`, `openai`, or `geminiai`, effective window is forced to `30d` regardless of `--window`.
- @param provider {str} CLI provider selector string.
- @param window {str} CLI window period string.
- @param output_json {bool} When True, emit JSON output instead of formatted text.
- @param force_refresh {bool} When True, bypass idle-time gate for this execution.
- @return {None} Function return value.
- @satisfies REQ-003
- @satisfies REQ-002
- @satisfies REQ-009
- @satisfies REQ-038
- @satisfies REQ-039
- @satisfies REQ-040
- @satisfies REQ-041
- @satisfies REQ-042
- @satisfies REQ-043
- @satisfies REQ-084
- @satisfies REQ-085
- @satisfies REQ-067
- @satisfies REQ-097
- @satisfies REQ-123
- @satisfies REQ-124
- @satisfies REQ-125
- @satisfies REQ-126

### fn `def _provider_display_name(provider_name: ProviderName) -> str` `priv` (L3402-3416)
- @brief Resolve human-facing provider title for terminal panel rendering.
- @details Maps machine-readable provider keys to display names aligned with CLI and GNOME extension output surfaces; applies uppercase `GEMINIAI` override for provider key `geminiai`.
- @param provider_name {ProviderName} Provider enum key.
- @return {str} Human-facing provider display name.
- @satisfies REQ-062

### fn `def _provider_panel_sort_key(provider_name: ProviderName) -> tuple[int, str]` `priv` (L3417-3432)
- @brief Build deterministic provider sort key for CLI `show` panel ordering.
- @details Applies canonical provider order `claude/openrouter/copilot/codex/openai/geminiai`; unknown providers are appended after known providers using lexical fallback.
- @param provider_name {ProviderName} Provider enum key.
- @return {tuple[int, str]} `(rank, provider_name.value)` sort key.
- @satisfies REQ-067
- @satisfies TST-030

### fn `def _provider_panel_color_code(provider_name: ProviderName) -> str` `priv` (L3433-3442)
- @brief Resolve ANSI color code for one provider output surface.
- @param provider_name {ProviderName} Provider enum key.
- @return {str} ANSI foreground color code.
- @satisfies REQ-067

### fn `def _provider_supports_api_counters(provider_name: ProviderName) -> bool` `priv` (L3443-3454)
- @brief Determine whether provider panels always render API counter lines.
- @details Returns true for providers that expose requests/token counters in CLI and GNOME output surfaces, enforcing null-to-zero normalization.
- @param provider_name {ProviderName} Provider enum key.
- @return {bool} True when requests/tokens lines must render on OK state.
- @satisfies REQ-036

### fn `def _should_render_cli_progress_bar(provider_name: ProviderName) -> bool` `priv` (L3455-3476)
- @brief Determine whether one CLI usage row must include a progress bar.
- @details Returns true only for providers whose CLI `show` rows use the fixed-width bracketed progress-bar surface: `claude`, `openrouter`, `copilot`, and `codex`. Returns false for `openai` and `geminiai`, which render text-only usage rows. Time complexity O(1). Space complexity O(1).
- @param provider_name {ProviderName} Provider enum key.
- @return {bool} True when CLI usage rendering must include bar glyphs.
- @satisfies REQ-122
- @satisfies REQ-128
- @satisfies REQ-131
- @satisfies REQ-132

### fn `def _build_cli_usage_line(` `priv` (L3477-3478)

### fn `def _strip_ansi_sequences(value: str) -> str` `priv` (L3502-3513)
- @brief Build one CLI usage row with provider-specific progress-bar policy.
- @brief Remove ANSI SGR color escape sequences from terminal text.
- @details Uses `_should_render_cli_progress_bar(...)` to emit
`Usage: <window> <progress_bar> <percent>%` for `claude`, `openrouter`,
`copilot`, and `codex`. Returns `Usage: <window> <percent>%` for
`openai/geminiai` so those providers omit progress-bar glyphs while
preserving explicit window and percentage text. Time complexity O(W) when a
progress bar is rendered and O(1) otherwise. Space complexity O(W) when a
progress bar is rendered and O(1) otherwise.
- @details Strips `\x1b[...m` segments so panel width calculations can use visible glyph length instead of byte length with hidden control codes.
- @param provider_name {ProviderName} Provider enum key.
- @param window_label {str} Effective usage-window label for rendered text.
- @param percent {float} Usage percentage value.
- @param value {str} Input string that may include ANSI color escapes.
- @return {str} Rendered CLI usage row.
- @return {str} String with ANSI SGR escapes removed.
- @satisfies REQ-128
- @satisfies REQ-131
- @satisfies REQ-132
- @satisfies REQ-067

### fn `def _visible_text_length(value: str) -> int` `priv` (L3514-3525)
- @brief Compute visible text length for terminal panel alignment.
- @details Calculates string length after ANSI SGR stripping to keep bordered-panel width deterministic for colored progress bar rows.
- @param value {str} Input string potentially containing ANSI escapes.
- @return {int} Visible glyph count used by panel width and padding logic.
- @satisfies REQ-067

### fn `def _ansi_ljust(value: str, width: int) -> str` `priv` (L3526-3538)
- @brief Left-pad ANSI-colored text to one visible width.
- @details Appends trailing spaces using visible-length semantics so rows that include ANSI escapes align with border columns exactly.
- @param value {str} Source text rendered inside one panel cell.
- @param width {int} Target visible width for the panel cell.
- @return {str} Padded terminal text preserving existing ANSI sequences.
- @satisfies REQ-067

### fn `def _ansi_rjust(value: str, width: int) -> str` `priv` (L3539-3551)
- @brief Right-pad ANSI-colored text to one visible width.
- @details Prefixes leading spaces using visible-length semantics so rows that include ANSI escapes align right to panel content width deterministically.
- @param value {str} Source text rendered inside one panel cell.
- @param width {int} Target visible width for the panel cell.
- @return {str} Right-aligned terminal text preserving ANSI sequences.
- @satisfies REQ-067

### fn `def _is_right_aligned_panel_line(value: str) -> bool` `priv` (L3552-3564)
- @brief Determine whether one panel body line must render right-aligned.
- @details Marks freshness rows (`Updated: ..., Next: ...`) for right-aligned rendering while all other body rows remain left-aligned.
- @param value {str} Panel body line candidate.
- @return {bool} True when line requires right alignment.
- @satisfies REQ-067
- @satisfies REQ-084

### fn `def _format_bright_white_bold(value: str) -> str` `priv` (L3565-3577)
- @brief Wrap one metric value with bright-white bold ANSI style.
- @details Applies ANSI SGR sequences for bold (`1`) and bright-white foreground (`97`) and appends reset (`0`) for deterministic inline metric emphasis.
- @param value {str} Visible metric value string.
- @return {str} Styled value with ANSI SGR wrappers.
- @satisfies REQ-035
- @satisfies REQ-051

### fn `def _wrap_panel_lines(body_lines: list[str], wrap_width: int) -> list[str]` `priv` (L3578-3602)
- @brief Wrap panel body lines to one deterministic visible width.
- @details Applies ANSI-aware wrapping: lines containing ANSI SGR sequences are measured by visible glyph length and wrapped on stripped text only when needed.
- @param body_lines {list[str]} Raw panel body lines.
- @param wrap_width {int} Maximum visible width for one wrapped line.
- @return {list[str]} Wrapped panel lines ready for width calculation/rendering.
- @satisfies REQ-067

### fn `def _panel_content_width(title: str, body_lines: list[str]) -> int` `priv` (L3603-3622)
- @brief Resolve one panel visible content width from title and body lines.
- @details Computes width from wrapped visible-line lengths and clamps to configured min/max panel boundaries.
- @param title {str} Panel title string.
- @param body_lines {list[str]} Raw body lines for the panel.
- @return {int} Content width used for bordered panel rendering.
- @satisfies REQ-067

### fn `def _resolve_shared_panel_content_width(` `priv` (L3623-3624)

### fn `def _emit_provider_panel(` `priv` (L3642-3646)
- @brief Resolve shared panel width for one CLI show rendering cycle.
- @details Selects the largest computed content width across all rendered
provider panels, then applies that width to every panel in the cycle.
- @param rendered_panels {list[tuple[ProviderName, str, list[str]]]} Render queue.
- @return {int} Shared content width used by all emitted panels.
- @satisfies REQ-067

### fn `def _format_http_status_retry_line(` `priv` (L3690-3692)
- @brief Render provider-colored ANSI bordered output panel with wrapped content lines.
- @details Creates fixed-width terminal panels aligned with GNOME extension
card layout, preserving deterministic borders and line wrapping behavior.
Border and title color use provider-specific ANSI palette.
- @param provider_name {ProviderName} Provider enum key.
- @param title {str} Panel header text.
- @param body_lines {list[str]} Content lines rendered in panel body.
- @param content_width {int | None} Shared content width override for this panel.
- @return {None} Function return value.
- @satisfies REQ-067

### fn `def _build_fail_panel_lines(` `priv` (L3714-3717)
- @brief Build normalized HTTP status/retry diagnostic line for text output.
- @details Returns one deterministic line matching requirement wording:
`HTTP status: <code>, Retry after: <seconds> sec.` when both values exist.
- @param status_code_raw {object} Status code candidate from result raw payload.
- @param retry_after_raw {object} Retry-after candidate from result raw payload.
- @return {str | None} Diagnostic line or None when both values are missing.
- @satisfies REQ-037

### fn `def _extract_copilot_extra_premium_cost(result: ProviderResult) -> float | None` `priv` (L3738-3798)
- @brief Build deterministic CLI body lines for one failed provider panel.
- @brief Resolve Copilot premium-request overage cost from normalized raw payload.
- @details Emits the required failed-state block layout: `Status: FAIL`, blank
separator, `Reason: <reason>`, blank separator, and one right-aligned
freshness line (`Updated: ..., Next: ...`) using provider freshness state.
- @details Computes Copilot overage primarily from `metrics.remaining` semantics: `0` when `remaining >= 0`, otherwise `-remaining * unit_cost`. Falls back to direct `premium_requests_extra_cost` or `max(premium_requests - premium_requests_included, 0) * unit_cost` when `remaining` is unavailable.
- @param result {ProviderResult} Provider result used for freshness fallback.
- @param reason {str} Normalized failure reason text.
- @param freshness_state {IdleTimeState | None} Optional provider freshness state.
- @param result {ProviderResult} Copilot provider result candidate.
- @return {list[str]} Ordered panel body lines for failed-state rendering.
- @return {float | None} Non-negative overage cost value or None when unavailable.
- @satisfies REQ-036
- @satisfies REQ-084
- @satisfies REQ-012
- @satisfies REQ-129

### fn `def _build_copilot_extra_premium_cost_line(result: ProviderResult) -> str | None` `priv` (L3799-3814)
- @brief Build CLI Copilot cost row from premium-request overage payload fields.
- @details Formats fallback Copilot cost text as `Cost: <currency><value>` when `metrics.cost` is unavailable and overage fields can still be resolved from raw payload.
- @param result {ProviderResult} Copilot provider result candidate.
- @return {str | None} Formatted row `Cost: ...` or None.
- @satisfies REQ-129

### fn `def _build_result_panel(` `priv` (L3815-3819)

### fn `def _format_billing_service_descriptions(services: list[object]) -> str | None` `priv` (L4045-4072)
- @brief Build one provider panel title/body payload for CLI text rendering.
- @brief Build human-readable GeminiAI billing service summary.
- @details Formats deterministic panel lines for one provider/window result and
preserves provider-specific metrics/error rendering rules used by `show`.
`FAIL` states emit `Status: FAIL`, `Reason: <reason>`, and `Updated/Next`
separated by blank lines. `OK` states emit `Status: OK` first, render
`claude/openrouter/copilot/codex` usage rows as
`Usage: <window> <progress_bar> <percent>%`, render `openai/geminiai`
usage rows as `Usage: <window> <percent>%`, default OpenRouter usage display
to `0.0%` when quota inputs are unavailable so the CLI stays aligned with
GNOME single-window progress-bar behavior, do not emit `Window <window>`
headings, insert one blank separator between Copilot `Remaining credits`
and `Cost` rows, and end with one right-aligned freshness line.
- @details Extracts ordered `service_description` values from billing service entries and returns all valid names in source order as one comma-separated summary string.
- @param name {ProviderName} Provider name enum value.
- @param result {ProviderResult} Provider result to render.
- @param label {str | None} Optional window label suffix (e.g. `"5h"`, `"7d"`).
- @param freshness_state {IdleTimeState | None} Optional provider idle-time state
carrying `last_success_timestamp` and `idle_until_timestamp` freshness values.
- @param services {list[object]} Billing service entries from GeminiAI raw billing payload.
- @return {tuple[str, list[str]]} Panel title and body lines.
- @return {str | None} Comma-separated service names summary without surrounding parentheses, or `None` when no valid names exist.
- @satisfies REQ-084
- @satisfies REQ-034
- @satisfies REQ-035
- @satisfies REQ-036
- @satisfies REQ-051
- @satisfies REQ-012
- @satisfies REQ-060
- @satisfies REQ-067
- @satisfies REQ-084
- @satisfies REQ-128
- @satisfies REQ-129
- @satisfies REQ-131
- @satisfies REQ-132
- @satisfies REQ-106

### fn `def _build_dual_window_section(` `priv` (L4073-4075)

### fn `def _build_dual_window_panel(` `priv` (L4091-4095)
- @brief Build one labeled dual-window CLI section.
- @details Prepends the raw window label (`5h` or `7d`) to the ordered detail
lines for one Claude/Codex section. The helper intentionally preserves
duplicate metric text across sections so identical `Usage` or `Resets in`
rows remain visible in both windows.
- @param window_label {str} Window label text rendered as the section heading.
- @param detail_lines {list[str]} Ordered non-empty detail lines for one window.
- @return {list[str]} Section heading followed by the provided detail lines.
- @satisfies REQ-002

### fn `def _print_result(name: ProviderName, result, label: str | None = None) -> None` `priv` (L4201-4225)
- @brief Build one grouped CLI panel for dual-window providers.
- @brief Render CLI text output for one provider result.
- @details Produces one provider panel from `5h` and `7d` results while
keeping explicit `5h` and `7d` section labels and preserving duplicate
section content when both windows render identical metric text. `FAIL`
states emit `Status: FAIL`, `Reason: <reason>`, and `Updated/Next`
separated by blank lines. `OK` states emit `Status: OK` first, preserve
usage rows formatted as `Usage: <window> <progress_bar> <percent>%`, avoid
`Window <window>` headings, and append one trailing right-aligned freshness
line.
- @details Formats provider-specific usage text, reset countdown, remaining credits, cost, requests, and token counts for one provider/window result. `openai/geminiai` usage rows omit progress bars while other providers keep existing bar rendering. Cost is formatted using `metrics.currency_symbol` (never hardcoded `$`).
- @param name {ProviderName} Provider enum value.
- @param result_5h {ProviderResult} Five-hour provider result.
- @param result_7d {ProviderResult} Seven-day provider result.
- @param freshness_state {IdleTimeState | None} Optional provider freshness state.
- @param name {ProviderName} Provider name enum value.
- @param result {ProviderResult} Provider result to render.
- @param label {str | None} Optional window label suffix (e.g. `"5h"`, `"7d"`).
- @return {tuple[str, list[str]]} Provider title and grouped body lines.
- @return {None} Function return value.
- @satisfies REQ-002
- @satisfies REQ-035
- @satisfies REQ-067
- @satisfies REQ-084
- @satisfies REQ-128
- @satisfies REQ-129
- @satisfies REQ-034
- @satisfies REQ-035
- @satisfies REQ-051
- @satisfies REQ-067
- @satisfies REQ-128
- @satisfies REQ-129
- @satisfies REQ-131
- @satisfies REQ-132

### fn `def _format_reset_duration(seconds: float) -> str` `priv` (L4226-4241)
- @brief Execute format reset duration.
- @details Applies format reset duration logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param seconds {float} Input parameter `seconds`.
- @return {str} Function return value.

### fn `def _should_print_claude_reset_pending_hint(` `priv` (L4242-4244)

### fn `def _is_displayed_zero_percent(percent: float | None) -> bool` `priv` (L4264-4280)
- @brief Determine whether CLI output must render the reset-pending fallback hint.
- @brief Check whether a percentage renders as `0.0%` in one-decimal UI output.
- @details The hint is only valid for Claude windows when no reset timestamp is
available yet and usage is exactly zero, which indicates the rate-limit timer has
not started. This preserves the normal countdown path for non-zero usage and for
providers other than Claude.
- @details Uses the same one-decimal rounding semantic as output formatting. This treats small non-zero percentages (e.g. 0.04) as displayed zero, which is required for consistent reset-pending fallback visibility between CLI and GNOME UI.
- @param provider_name {ProviderName} Provider associated with the rendered result.
- @param metrics {UsageMetrics} Normalized quota metrics for the rendered result.
- @param percent {float | None} Raw percentage value.
- @return {bool} True when CLI must print `Resets in: Starts when the first message is sent`.
- @return {bool} True when `percent` is finite, non-negative, and rounds to `0.0`.
- @satisfies REQ-002
- @satisfies REQ-002

### fn `def _progress_bar_layout(percent: float, width: int) -> tuple[int, int, int]` `priv` (L4281-4313)
- @brief Compute fixed-width CLI progress-bar segment widths.
- @details Normalizes `percent` to a non-negative finite value. Percentages up to `100` allocate provider-color fill plus empty cells. Percentages above `100` allocate one 100%-boundary marker cell and one over-limit segment scaled across the extra `0..100` range, clamped for larger values, and forced visible for any positive over-limit usage. Time complexity O(1). Space complexity O(1).
- @param percent {float} Raw usage percentage.
- @param width {int} Total cell width inside the surrounding brackets.
- @return {tuple[int, int, int]} Tuple `(base_width, over_limit_width, marker_width)`.
- @satisfies REQ-122

### fn `def _progress_bar(percent: float, provider_name: ProviderName, width: int = 20) -> str` `priv` (L4314-4338)
- @brief Render one fixed-width CLI usage bar.
- @details Uses provider-color fill for in-limit usage. Percentages above `100` preserve fixed bar width by rendering a bright-white `|` marker at the 100% boundary and a neutral shaded over-limit segment (`▓`) inside the same bar. Time complexity O(width). Space complexity O(width).
- @param percent {float} Raw usage percentage.
- @param provider_name {ProviderName} Provider enum key for base-fill color mapping.
- @param width {int} Total cell width inside the surrounding brackets.
- @return {str} ANSI-colored progress bar string.
- @satisfies REQ-122
- @satisfies REQ-128

### fn `def doctor() -> None` (L4343-4395)
- @brief Execute doctor.
- @details Applies doctor logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def env() -> None` (L4400-4408)
- @brief Execute env.
- @details Applies env logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def setup() -> None` (L4413-4612)
- @brief Execute setup.
- @details Prompts dedicated provider-activation section first, then prompts `idle_delay_seconds`, `api_call_delay_milliseconds`, `api_call_timeout_milliseconds`, `default_retry_after_seconds`, `gnome_refresh_interval_seconds`, and `billing_data` in order, then prompts dedicated Copilot overage pricing field `copilot_extra_premium_request_cost` (USD/request), then prompts provider currency symbols including `geminiai` (choices: `$`, `£`, `€`, default `$`), then persists all values to `~/.config/aibar/config.json`. Final setup section configures logging flags (`log_enabled`, `debug_enabled`). GeminiAI OAuth source supports `skip`, `file`, `paste`, and `login` (re-authorization with current scopes). Also prompts for provider API keys and writes them to `~/.config/aibar/env`.
- @return {None} Function return value.
- @satisfies REQ-005
- @satisfies REQ-049
- @satisfies REQ-123
- @satisfies REQ-108
- @satisfies REQ-116
- @satisfies REQ-055
- @satisfies REQ-056
- @satisfies REQ-059

### fn `def login(provider: str) -> None` (L4785-4803)
- @brief Execute login.
- @details Applies login logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param provider {str} Input parameter `provider`.
- @return {None} Function return value.

### fn `def _login_claude() -> None` `priv` (L4804-4852)
- @brief Execute login claude.
- @details Applies login claude logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def _login_copilot() -> None` `priv` (L4853-4880)
- @brief Execute login copilot.
- @details Applies login copilot logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def _login_geminiai() -> None` `priv` (L4881-4919)
- @brief Execute GeminiAI OAuth login flow.
- @details Reuses persisted OAuth client configuration to launch browser-based authorization and persist refresh-capable Google credentials.
- @return {None} Function return value.
- @satisfies REQ-055
- @satisfies REQ-056

### fn `def _resolve_extension_source_dir() -> Path` `priv` (L4920-4932)
- @brief Resolve GNOME extension source directory from within the `aibar` package.
- @details Uses `Path(__file__).resolve().parent` to locate the `aibar` package directory, then appends `gnome-extension/<UUID>/`. Works in development (editable install), wheel-installed, and `uv tool install` layouts because the extension directory resides inside the `aibar` Python package subtree.
- @return {Path} Absolute path to the extension source directory.
- @satisfies REQ-025, REQ-083

### fn `def gnome_install() -> None` (L4943-5069)
- @brief Install or update the AIBar GNOME Shell extension to the user's local extensions directory.
- @details Resolves extension source from the installed package path, validates source directory contains `metadata.json` and is non-empty, then executes one of two flows: install flow (`target` absent) creates target and copies files before enabling extension; update flow (`target` present) disables extension, copies files, then enables extension. Update flow masks non-zero disable outcomes caused by missing extension and continues. Produces colored Click-styled terminal output for all status messages.
- @return {None} Function return value.
- @throws {SystemExit} Exits with code 1 on prerequisite validation failure.
- @satisfies PRJ-008, REQ-025, REQ-026, REQ-027, REQ-028, REQ-029, REQ-030, REQ-032, REQ-099

### fn `def gnome_uninstall() -> None` (L5079-5148)
- @brief Remove the AIBar GNOME Shell extension from the user's local extensions directory.
- @details Disables the extension via `gnome-extensions disable`, then removes the entire extension directory at `~/.local/share/gnome-shell/extensions/aibar@aibar.panel/`. Exits with code 1 if the extension directory does not exist. Produces colored Click-styled terminal output for all status messages.
- @return {None} Function return value.
- @throws {SystemExit} Exits with code 1 when extension directory does not exist.
- @satisfies REQ-028, REQ-080, REQ-081, REQ-082

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`RetrievalPipelineOutput`|class|pub|153-182|class RetrievalPipelineOutput|
|`StartupReleaseCheckResponse`|class|pub|184-203|class StartupReleaseCheckResponse|
|`_startup_idle_state_path`|fn|priv|204-213|def _startup_idle_state_path() -> Path|
|`_startup_human_timestamp`|fn|priv|214-226|def _startup_human_timestamp(epoch_seconds: int) -> str|
|`_startup_parse_int`|fn|priv|227-244|def _startup_parse_int(value: object, default: int = 0) -...|
|`_load_startup_idle_state`|fn|priv|245-264|def _load_startup_idle_state() -> dict[str, object] | None|
|`_startup_idle_epochs`|fn|priv|265-286|def _startup_idle_epochs(state: dict[str, object] | None)...|
|`_save_startup_idle_state`|fn|priv|287-317|def _save_startup_idle_state(last_success_epoch: int, idl...|
|`_cleanup_startup_idle_state_artifacts`|fn|priv|318-343|def _cleanup_startup_idle_state_artifacts() -> int|
|`_emit_startup_preflight_message`|fn|priv|344-345|def _emit_startup_preflight_message(|
|`_parse_retry_after_header`|fn|priv|361-385|def _parse_retry_after_header(retry_after_raw: str | None...|
|`_normalize_release_version`|fn|priv|386-402|def _normalize_release_version(raw_version: object) -> st...|
|`_fetch_startup_latest_release`|fn|priv|403-459|def _fetch_startup_latest_release() -> StartupReleaseChec...|
|`_parse_version_triplet`|fn|priv|460-478|def _parse_version_triplet(version_text: str) -> tuple[in...|
|`_is_newer_release`|fn|priv|479-495|def _is_newer_release(installed_version: str, latest_vers...|
|`_run_startup_update_preflight`|fn|priv|496-579|def _run_startup_update_preflight() -> None|
|`_startup_force_ignore_idle_from_args`|fn|priv|580-599|def _startup_force_ignore_idle_from_args(args: Sequence[s...|
|`_execute_lifecycle_subprocess`|fn|priv|600-622|def _execute_lifecycle_subprocess(command: list[str]) -> int|
|`_is_linux_runtime`|fn|priv|623-635|def _is_linux_runtime() -> bool|
|`_emit_non_linux_lifecycle_guidance`|fn|priv|636-662|def _emit_non_linux_lifecycle_guidance(option_name: str, ...|
|`_handle_upgrade_option`|fn|priv|663-664|def _handle_upgrade_option(|
|`_handle_uninstall_option`|fn|priv|693-694|def _handle_uninstall_option(|
|`_handle_version_option`|fn|priv|727-728|def _handle_version_option(|
|`_update_runtime_logging_flags`|fn|priv|747-750|def _update_runtime_logging_flags(|
|`_handle_enable_log_option`|fn|priv|780-781|def _handle_enable_log_option(|
|`_handle_disable_log_option`|fn|priv|801-802|def _handle_disable_log_option(|
|`_handle_enable_debug_option`|fn|priv|822-823|def _handle_enable_debug_option(|
|`_handle_disable_debug_option`|fn|priv|843-844|def _handle_disable_debug_option(|
|`StartupPreflightGroup`|class|pub|864-959|class StartupPreflightGroup(click.Group)|
|`StartupPreflightGroup.format_epilog`|fn|pub|874-877|def format_epilog(|
|`StartupPreflightGroup.main`|fn|pub|894-901|def main(|
|`_normalize_utc`|fn|priv|960-972|def _normalize_utc(value: datetime) -> datetime|
|`_format_local_datetime`|fn|priv|973-985|def _format_local_datetime(value: datetime) -> str|
|`_epoch_to_utc_datetime`|fn|priv|986-994|def _epoch_to_utc_datetime(epoch_seconds: int) -> datetime|
|`_build_freshness_line`|fn|priv|995-997|def _build_freshness_line(|
|`_next_utc_month_boundary`|fn|priv|1022-1051|def _next_utc_month_boundary(reference_time: datetime | N...|
|`_apply_api_call_delay`|fn|priv|1052-1081|def _apply_api_call_delay(throttle_state: dict[str, float...|
|`_coerce_retry_after_seconds`|fn|priv|1082-1113|def _coerce_retry_after_seconds(value: object) -> int | None|
|`_extract_retry_after_seconds`|fn|priv|1114-1134|def _extract_retry_after_seconds(result: ProviderResult) ...|
|`_classify_provider_failure_log_category`|fn|priv|1135-1155|def _classify_provider_failure_log_category(result: Provi...|
|`_append_provider_failure_runtime_log`|fn|priv|1156-1193|def _append_provider_failure_runtime_log(result: Provider...|
|`_extract_retry_after_for_failure_log`|fn|priv|1194-1225|def _extract_retry_after_for_failure_log(result: Provider...|
|`_retry_after_probe_payload`|fn|priv|1226-1249|def _retry_after_probe_payload(raw_payload: dict[str, obj...|
|`_is_claude_oauth_authentication_error`|fn|priv|1250-1262|def _is_claude_oauth_authentication_error(message: object...|
|`_subprocess_return_code_from_exception`|fn|priv|1263-1280|def _subprocess_return_code_from_exception(exc: Exception...|
|`_execute_claude_refresh_command`|fn|priv|1281-1283|def _execute_claude_refresh_command(|
|`_run_claude_oauth_token_refresh`|fn|priv|1313-1367|def _run_claude_oauth_token_refresh(runtime_config: Runti...|
|`_clear_claude_refresh_block_flag`|fn|priv|1368-1369|def _clear_claude_refresh_block_flag(|
|`_is_claude_refresh_block_active`|fn|priv|1389-1391|def _is_claude_refresh_block_active(|
|`_is_claude_authentication_error_result`|fn|priv|1409-1424|def _is_claude_authentication_error_result(result: Provid...|
|`_handle_claude_oauth_refresh_on_auth_error`|fn|priv|1425-1428|def _handle_claude_oauth_refresh_on_auth_error(|
|`_update_claude_refresh_block_state`|fn|priv|1459-1461|def _update_claude_refresh_block_state(|
|`_fetch_claude_dual_with_auth_recovery`|fn|priv|1489-1491|def _fetch_claude_dual_with_auth_recovery(|
|`_clear_expired_claude_refresh_block`|fn|priv|1544-1545|def _clear_expired_claude_refresh_block(|
|`_is_http_429_result`|fn|priv|1564-1574|def _is_http_429_result(result: ProviderResult) -> bool|
|`_serialize_results_payload`|fn|priv|1575-1576|def _serialize_results_payload(|
|`_empty_cache_document`|fn|priv|1593-1607|def _empty_cache_document() -> dict[str, object]|
|`_normalize_cache_document`|fn|priv|1608-1609|def _normalize_cache_document(|
|`_cache_payload_section`|fn|priv|1632-1644|def _cache_payload_section(cache_document: dict[str, obje...|
|`_cache_status_section`|fn|priv|1645-1657|def _cache_status_section(cache_document: dict[str, objec...|
|`_serialize_attempt_status`|fn|priv|1658-1678|def _serialize_attempt_status(result: ProviderResult) -> ...|
|`_record_attempt_status`|fn|priv|1679-1681|def _record_attempt_status(|
|`_extract_claude_snapshot_from_cache_document`|fn|priv|1701-1702|def _extract_claude_snapshot_from_cache_document(|
|`_get_window_attempt_status`|fn|priv|1717-1720|def _get_window_attempt_status(|
|`_overlay_cached_failure_status`|fn|priv|1740-1744|def _overlay_cached_failure_status(|
|`_filter_cached_payload`|fn|priv|1795-1798|def _filter_cached_payload(|
|`_filter_idle_time_by_provider`|fn|priv|1854-1857|def _filter_idle_time_by_provider(|
|`_enabled_provider_keys`|fn|priv|1890-1909|def _enabled_provider_keys(runtime_config: RuntimeConfig)...|
|`_serialize_enabled_providers`|fn|priv|1910-1911|def _serialize_enabled_providers(|
|`_serialize_idle_time_state`|fn|priv|1927-1928|def _serialize_idle_time_state(|
|`_serialize_freshness_state`|fn|priv|1943-1944|def _serialize_freshness_state(|
|`_fixed_effective_window`|fn|priv|1968-1982|def _fixed_effective_window(provider_name: ProviderName) ...|
|`_serialize_extension_window_labels`|fn|priv|1983-1984|def _serialize_extension_window_labels(|
|`_project_cached_window`|fn|priv|2007-2010|def _project_cached_window(|
|`_load_cached_results`|fn|priv|2063-2067|def _load_cached_results(|
|`_update_idle_time_after_refresh`|fn|priv|2111-2113|def _update_idle_time_after_refresh(|
|`_project_next_reset`|fn|priv|2194-2225|def _project_next_reset(resets_at_str: str, window: Windo...|
|`_apply_reset_projection`|fn|priv|2226-2260|def _apply_reset_projection(result: ProviderResult) -> Pr...|
|`get_providers`|fn|pub|2261-2276|def get_providers() -> dict[ProviderName, BaseProvider]|
|`parse_window`|fn|pub|2277-2296|def parse_window(window: str) -> WindowPeriod|
|`parse_provider`|fn|pub|2297-2313|def parse_provider(provider: str) -> ProviderName | None|
|`_provider_result_debug_summary`|fn|priv|2314-2339|def _provider_result_debug_summary(result: ProviderResult...|
|`_extract_error_json_payload_for_debug_log`|fn|priv|2340-2361|def _extract_error_json_payload_for_debug_log(result: Pro...|
|`_append_provider_debug_runtime_log`|fn|priv|2362-2387|def _append_provider_debug_runtime_log(result: ProviderRe...|
|`_fetch_result`|fn|priv|2388-2391|def _fetch_result(|
|`_fetch_claude_dual`|fn|priv|2468-2470|def _fetch_claude_dual(|
|`_extract_claude_dual_payload`|fn|priv|2550-2552|def _extract_claude_dual_payload(|
|`_normalize_claude_dual_payload`|fn|priv|2574-2596|def _normalize_claude_dual_payload(payload: object) -> di...|
|`_extract_snapshot_reset_at`|fn|priv|2597-2599|def _extract_snapshot_reset_at(|
|`_extract_snapshot_utilization`|fn|priv|2622-2624|def _extract_snapshot_utilization(|
|`_is_claude_rate_limited_result`|fn|priv|2653-2668|def _is_claude_rate_limited_result(result: ProviderResult...|
|`_build_claude_rate_limited_partial_result`|fn|priv|2669-2672|def _build_claude_rate_limited_partial_result(|
|`_refresh_and_persist_cache_payload`|fn|priv|2717-2721|def _refresh_and_persist_cache_payload(|
|`retrieve_results_via_cache_pipeline`|fn|pub|2829-2834|def retrieve_results_via_cache_pipeline(|
|`_build_cached_dual_window_results`|fn|priv|3030-3033|def _build_cached_dual_window_results(|
|`main`|fn|pub|3149-3159|def main(ctx: click.Context) -> None|
|`show`|fn|pub|3192-3391|def show(provider: str, window: str, output_json: bool, f...|
|`_provider_display_name`|fn|priv|3402-3416|def _provider_display_name(provider_name: ProviderName) -...|
|`_provider_panel_sort_key`|fn|priv|3417-3432|def _provider_panel_sort_key(provider_name: ProviderName)...|
|`_provider_panel_color_code`|fn|priv|3433-3442|def _provider_panel_color_code(provider_name: ProviderNam...|
|`_provider_supports_api_counters`|fn|priv|3443-3454|def _provider_supports_api_counters(provider_name: Provid...|
|`_should_render_cli_progress_bar`|fn|priv|3455-3476|def _should_render_cli_progress_bar(provider_name: Provid...|
|`_build_cli_usage_line`|fn|priv|3477-3478|def _build_cli_usage_line(|
|`_strip_ansi_sequences`|fn|priv|3502-3513|def _strip_ansi_sequences(value: str) -> str|
|`_visible_text_length`|fn|priv|3514-3525|def _visible_text_length(value: str) -> int|
|`_ansi_ljust`|fn|priv|3526-3538|def _ansi_ljust(value: str, width: int) -> str|
|`_ansi_rjust`|fn|priv|3539-3551|def _ansi_rjust(value: str, width: int) -> str|
|`_is_right_aligned_panel_line`|fn|priv|3552-3564|def _is_right_aligned_panel_line(value: str) -> bool|
|`_format_bright_white_bold`|fn|priv|3565-3577|def _format_bright_white_bold(value: str) -> str|
|`_wrap_panel_lines`|fn|priv|3578-3602|def _wrap_panel_lines(body_lines: list[str], wrap_width: ...|
|`_panel_content_width`|fn|priv|3603-3622|def _panel_content_width(title: str, body_lines: list[str...|
|`_resolve_shared_panel_content_width`|fn|priv|3623-3624|def _resolve_shared_panel_content_width(|
|`_emit_provider_panel`|fn|priv|3642-3646|def _emit_provider_panel(|
|`_format_http_status_retry_line`|fn|priv|3690-3692|def _format_http_status_retry_line(|
|`_build_fail_panel_lines`|fn|priv|3714-3717|def _build_fail_panel_lines(|
|`_extract_copilot_extra_premium_cost`|fn|priv|3738-3798|def _extract_copilot_extra_premium_cost(result: ProviderR...|
|`_build_copilot_extra_premium_cost_line`|fn|priv|3799-3814|def _build_copilot_extra_premium_cost_line(result: Provid...|
|`_build_result_panel`|fn|priv|3815-3819|def _build_result_panel(|
|`_format_billing_service_descriptions`|fn|priv|4045-4072|def _format_billing_service_descriptions(services: list[o...|
|`_build_dual_window_section`|fn|priv|4073-4075|def _build_dual_window_section(|
|`_build_dual_window_panel`|fn|priv|4091-4095|def _build_dual_window_panel(|
|`_print_result`|fn|priv|4201-4225|def _print_result(name: ProviderName, result, label: str ...|
|`_format_reset_duration`|fn|priv|4226-4241|def _format_reset_duration(seconds: float) -> str|
|`_should_print_claude_reset_pending_hint`|fn|priv|4242-4244|def _should_print_claude_reset_pending_hint(|
|`_is_displayed_zero_percent`|fn|priv|4264-4280|def _is_displayed_zero_percent(percent: float | None) -> ...|
|`_progress_bar_layout`|fn|priv|4281-4313|def _progress_bar_layout(percent: float, width: int) -> t...|
|`_progress_bar`|fn|priv|4314-4338|def _progress_bar(percent: float, provider_name: Provider...|
|`doctor`|fn|pub|4343-4395|def doctor() -> None|
|`env`|fn|pub|4400-4408|def env() -> None|
|`setup`|fn|pub|4413-4612|def setup() -> None|
|`login`|fn|pub|4785-4803|def login(provider: str) -> None|
|`_login_claude`|fn|priv|4804-4852|def _login_claude() -> None|
|`_login_copilot`|fn|priv|4853-4880|def _login_copilot() -> None|
|`_login_geminiai`|fn|priv|4881-4919|def _login_geminiai() -> None|
|`_resolve_extension_source_dir`|fn|priv|4920-4932|def _resolve_extension_source_dir() -> Path|
|`gnome_install`|fn|pub|4943-5069|def gnome_install() -> None|
|`gnome_uninstall`|fn|pub|5079-5148|def gnome_uninstall() -> None|


---

# config.py | Python | 866L | 54 symbols | 14 imports | 43 comments
> Path: `src/aibar/aibar/config.py`
- @brief Configuration and credential resolution for aibar.
- @details Provides environment-file parsing, token precedence resolution, and provider configuration status reporting.

## Imports
```
import os
import json
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field, ValidationError
from aibar.claude_cli_auth import extract_claude_cli_token
from aibar.providers.base import ProviderName
from aibar.providers.codex import CodexCredentialStore
from aibar.providers.copilot import CopilotCredentialStore
from aibar.providers.geminiai import GeminiAICredentialStore
from aibar.providers import (
```

## Definitions

- var `APP_CONFIG_DIR = Path.home() / ".config" / "aibar"` (L21)
- var `APP_CACHE_DIR = Path.home() / ".cache" / "aibar"` (L22)
- var `ENV_FILE_PATH = APP_CONFIG_DIR / "env"` (L23)
- var `RUNTIME_CONFIG_PATH = APP_CONFIG_DIR / "config.json"` (L24)
- var `CACHE_FILE_PATH = APP_CACHE_DIR / "cache.json"` (L25)
- var `IDLE_TIME_PATH = APP_CACHE_DIR / "idle-time.json"` (L26)
- var `DEFAULT_IDLE_DELAY_SECONDS = 300` (L28)
- var `DEFAULT_API_CALL_DELAY_MILLISECONDS = 100` (L29)
- var `DEFAULT_API_CALL_TIMEOUT_MILLISECONDS = 5000` (L30)
- var `DEFAULT_RETRY_AFTER_SECONDS = 3600` (L31)
- var `DEFAULT_GNOME_REFRESH_INTERVAL_SECONDS = 60` (L32)
- var `DEFAULT_BILLING_DATASET = "billing_data"` (L33)
- var `DEFAULT_COPILOT_EXTRA_PREMIUM_REQUEST_COST = 0.04` (L34)
- var `DEFAULT_CURRENCY_SYMBOL = "$"` (L35)
- var `DEFAULT_LOG_ENABLED = False` (L36)
- var `DEFAULT_DEBUG_ENABLED = False` (L37)
- var `LOG_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"` (L38)
- var `LOCK_POLL_INTERVAL_SECONDS = 0.25` (L40)
- var `LOCK_ACQUIRE_TIMEOUT_SECONDS = 5.0` (L41)
### class `class RuntimeConfig(BaseModel)` : BaseModel (L50-112)
- @brief Define runtime configuration component for refresh throttling, timeout, currency, and provider-activation controls.
- @details Encodes persisted CLI runtime controls used by `show` refresh logic, GNOME extension scheduling, per-provider currency symbol resolution, and provider enable/disable gating. Fields are validated with defaults that reduce rate-limit pressure. `api_call_delay_milliseconds` defaults to `100` ms inter-call spacing. `api_call_timeout_milliseconds` defaults to `5000` ms HTTP response timeout applied to all provider API calls via `httpx.AsyncClient(timeout=<value>/1000.0)`. `default_retry_after_seconds` defaults to `3600` seconds and is used when provider failure payloads explicitly mark `retry_after_unavailable=true`. `currency_symbols` maps provider name strings to currency symbols (`$`, `£`, `€`); missing entries default to `DEFAULT_CURRENCY_SYMBOL` at resolution time. `billing_data` stores the Google BigQuery dataset name used for GeminiAI billing export table discovery. `copilot_extra_premium_request_cost` stores the configured unit price (USD) for one Copilot premium request above included-plan quota. `enabled_providers` stores provider-keyed booleans; missing keys normalize to `true` via `resolve_enabled_providers(...)` for backward compatibility. `log_enabled` controls append logging to `~/.cache/aibar/aibar.log`. `debug_enabled` controls API debug-result logging and requires `log_enabled`. Optional GeminiAI field persists Google Cloud project identifier used by OAuth-backed Monitoring API fetch execution.
- @satisfies CTN-008
- @satisfies REQ-107
- @satisfies REQ-109
- @satisfies REQ-110
- @satisfies REQ-049
- @satisfies REQ-005
- @satisfies REQ-041
- @satisfies REQ-095
- @satisfies REQ-096
- @satisfies REQ-116
- @satisfies CTN-017
- @satisfies REQ-123
- @satisfies REQ-124
- @satisfies REQ-126

### class `class IdleTimeState(BaseModel)` : BaseModel (L113-128)
- @brief Define persisted idle-time entry for one provider.
- @details Stores provider-local last-success and idle-until timestamps in epoch-seconds and local-timezone ISO-8601 formats. Serialized as one value under provider key in `~/.cache/aibar/idle-time.json`.
- @satisfies CTN-009

### class `class LockAcquisitionTimeoutError(RuntimeError)` : RuntimeError (L129-139)
- @brief Define lock-acquisition timeout error for cache-file synchronization.
- @details Raised when lock-file acquisition for `cache.json` or `idle-time.json` remains blocked beyond the configured timeout window.
- @satisfies REQ-066

### fn `def _ensure_app_config_dir() -> None` `priv` (L140-149)
- @brief Ensure AIBar configuration directory exists before file persistence.
- @details Creates `~/.config/aibar` recursively when missing. This function is called by env-file and runtime-config persistence helpers.
- @return {None} Function return value.

### fn `def _ensure_app_cache_dir() -> None` `priv` (L150-159)
- @brief Ensure AIBar cache directory exists before cache and idle-time persistence.
- @details Creates `~/.cache/aibar` recursively when missing. This function is called by CLI cache and idle-time persistence helpers.
- @return {None} Function return value.

### fn `def _runtime_log_path() -> Path` `priv` (L160-170)
- @brief Resolve runtime execution log file path.
- @details Produces deterministic path `~/.cache/aibar/aibar.log` under user cache directory for append-only execution logging.
- @return {Path} Absolute runtime log file path.
- @satisfies REQ-111

### fn `def _runtime_log_flags() -> tuple[bool, bool]` `priv` (L171-187)
- @brief Resolve persisted runtime log and debug flags.
- @details Loads runtime configuration and extracts `log_enabled` and `debug_enabled`; invalid or unreadable config yields `(False, False)`.
- @return {tuple[bool, bool]} Tuple `(log_enabled, debug_enabled)`.
- @satisfies REQ-107
- @satisfies REQ-109
- @satisfies REQ-110

### fn `def append_runtime_log_line(message: str, debug_only: bool = False) -> None` (L188-213)
- @brief Append one timestamped runtime log line.
- @details Writes `<timestamp> <message>` rows in append mode to `~/.cache/aibar/aibar.log` when `log_enabled` is true. Debug-only rows are emitted only when both `log_enabled` and `debug_enabled` are true.
- @param message {str} Runtime log message payload without trailing newline.
- @param debug_only {bool} True to gate emission on debug flag.
- @return {None} Function return value.
- @satisfies REQ-111
- @satisfies REQ-114

### fn `def append_runtime_log_separator() -> None` (L214-232)
- @brief Append one trailing empty line to runtime log.
- @details Emits one blank separator row in append mode when `log_enabled` is true to delimit consecutive execution blocks.
- @return {None} Function return value.
- @satisfies REQ-113

### fn `def _lock_file_path(target_path: Path) -> Path` `priv` (L233-244)
- @brief Resolve lock-file path for one cache artifact.
- @details Produces deterministic lock-file names under `~/.cache/aibar/` using `<filename>.lock` to coordinate cross-process read/write exclusion.
- @param target_path {Path} Cache file path guarded by lock.
- @return {Path} Absolute lock-file path.
- @satisfies REQ-066

### fn `def _blocking_file_lock(target_path: Path)` `priv` `@contextmanager` (L246-294)
- @brief Acquire and release blocking lock-file for cache artifact I/O.
- @details Uses atomic `O_CREAT|O_EXCL` lock-file creation. When lock-file already exists, polls every `250ms` until lock release, then acquires lock. Raises timeout error after `5s` blocked wait and appends timeout diagnostics to runtime log when logging is enabled. Always removes owned lock-file during exit.
- @param target_path {Path} Cache artifact path protected by this lock.
- @return {Iterator[None]} Context manager yielding while lock is held.
- @throws {LockAcquisitionTimeoutError} When lock remains blocked beyond timeout.
- @satisfies REQ-066
- @satisfies REQ-112

### fn `def _sanitize_cache_payload(payload: dict[str, Any]) -> dict[str, Any]` `priv` (L295-329)
- @brief Redact sensitive keys from cache payload before disk persistence.
- @details Recursively traverses dictionaries/lists and replaces values for case-insensitive key matches in `{token,key,secret,password,authorization}` with deterministic placeholder string `[REDACTED]`.
- @param payload {dict[str, Any]} Cache document containing `payload` and `status` sections.
- @return {dict[str, Any]} Sanitized deep-copy structure safe for persistence.
- @satisfies DES-004

### fn `def clean(value: Any) -> Any` (L307-326)
- @brief Redact sensitive keys from cache payload before disk persistence.
- @brief Apply recursive redaction to one JSON-compatible node.
- @details Recursively traverses dictionaries/lists and replaces values for
case-insensitive key matches in `{token,key,secret,password,authorization}`
with deterministic placeholder string `[REDACTED]`.
- @details Preserves structural type (dict/list/scalar) while replacing values of sensitive keys with `[REDACTED]`.
- @param payload {dict[str, Any]} Cache document containing `payload` and `status` sections.
- @param value {Any} JSON-like node to sanitize.
- @return {dict[str, Any]} Sanitized deep-copy structure safe for persistence.
- @return {Any} Sanitized node.
- @satisfies DES-004

### fn `def load_runtime_config() -> RuntimeConfig` (L330-346)
- @brief Load runtime refresh configuration from disk with schema validation.
- @details Reads `~/.config/aibar/config.json`, validates fields against `RuntimeConfig`, and returns defaults when file is missing or invalid.
- @return {RuntimeConfig} Validated runtime configuration payload.
- @satisfies CTN-008

### fn `def save_runtime_config(runtime_config: RuntimeConfig) -> None` (L347-363)
- @brief Persist runtime refresh configuration to disk.
- @details Serializes `RuntimeConfig` to `~/.config/aibar/config.json` using stable pretty-printed JSON (`indent=2`) for deterministic readability.
- @param runtime_config {RuntimeConfig} Validated runtime configuration model.
- @return {None} Function return value.
- @satisfies CTN-008
- @satisfies CTN-017

### fn `def resolve_enabled_providers(` (L364-365)

### fn `def load_cli_cache() -> dict[str, Any] | None` (L388-414)
- @brief Resolve normalized provider-enable flags from runtime configuration.
- @brief Load CLI cache payload from disk.
- @details Produces a provider-keyed boolean map for all `ProviderName`
values. Missing `enabled_providers` keys normalize to `True` to preserve
backward compatibility with pre-flag config documents. Time complexity
O(P). Space complexity O(P), where P is provider count.
- @details Reads `~/.cache/aibar/cache.json` and returns parsed object only when payload root is a JSON object with canonical cache sections.
- @param runtime_config {RuntimeConfig | None} Optional preloaded runtime configuration.
- @return {dict[str, bool]} Provider-keyed enabled-state mapping for all providers.
- @return {dict[str, Any] | None} Parsed cache payload or None if unavailable.
- @satisfies CTN-017
- @satisfies REQ-123
- @satisfies REQ-124
- @satisfies REQ-126
- @satisfies CTN-004
- @satisfies REQ-047
- @satisfies REQ-066
- @satisfies REQ-112

### fn `def resolve_currency_symbol(raw: dict[str, Any] | None, provider_name: str) -> str` (L415-446)
- @brief Resolve currency symbol for a provider result from API response or config.
- @details Extraction priority: 1. `raw["currency"]` field: if a recognized symbol (`$`, `£`, `€`) → use directly; if an ISO-4217 code (`USD`, `GBP`, `EUR`) → map to symbol. 2. `RuntimeConfig.currency_symbols[provider_name]` configured default. 3. `DEFAULT_CURRENCY_SYMBOL` (`"$"`) as final fallback.
- @param raw {dict[str, Any] | None} Raw API response dict from the provider fetch call, or None.
- @param provider_name {str} Provider name string key (e.g. `"claude"`, `"openai"`).
- @return {str} Resolved currency symbol; always a member of `VALID_CURRENCY_SYMBOLS`.
- @satisfies REQ-050

### fn `def save_cli_cache(payload: dict[str, Any]) -> None` (L447-473)
- @brief Persist canonical cache document to disk.
- @details Redacts sensitive keys from nested raw payload objects, then writes sanitized cache document to `~/.cache/aibar/cache.json` using pretty-printed JSON (`indent=2`) preserving `payload` and `status` sections.
- @param payload {dict[str, Any]} Canonical cache document.
- @return {None} Function return value.
- @satisfies CTN-004
- @satisfies DES-004
- @satisfies REQ-044
- @satisfies REQ-045
- @satisfies REQ-046
- @satisfies REQ-047
- @satisfies REQ-066
- @satisfies REQ-112

### fn `def build_idle_time_state(` (L474-475)

### fn `def load_idle_time() -> dict[str, IdleTimeState]` (L509-539)
- @brief Build provider-local idle-time entry from UTC-compatible datetimes.
- @brief Load provider-keyed idle-time state from disk.
- @details Normalizes timestamps to UTC for epoch conversion, then emits
human-readable ISO-8601 values in runtime local timezone for deterministic
parity with CLI/GNOME freshness rendering.
- @details Reads `~/.cache/aibar/idle-time.json` and validates each provider value as `IdleTimeState`. Invalid provider entries are ignored. Missing or unreadable payloads return an empty map.
- @param last_success_at {datetime} Last successful refresh timestamp.
- @param idle_until {datetime} Timestamp until provider refresh remains gated.
- @return {IdleTimeState} Normalized provider idle-time entry.
- @return {dict[str, IdleTimeState]} Provider-keyed idle-time state map.
- @satisfies CTN-009
- @satisfies CTN-009
- @satisfies REQ-066

### fn `def save_idle_time(` (L540-541)

### fn `def remove_idle_time_file() -> None` (L576-591)
- @brief Persist provider-keyed idle-time state map.
- @brief Remove persisted idle-time state file if present.
- @details Validates each provider entry, serializes canonical epoch and
ISO-8601 fields, and writes `~/.cache/aibar/idle-time.json` in pretty-printed JSON.
Invalid map entries are skipped.
- @details Deletes `~/.cache/aibar/idle-time.json` to force immediate refresh behavior on subsequent `show` execution.
- @param idle_time_by_provider {dict[str, IdleTimeState]} Provider-keyed idle-time map.
- @return {dict[str, IdleTimeState]} Persisted provider-keyed idle-time map.
- @return {None} Function return value.
- @satisfies CTN-009
- @satisfies REQ-066
- @satisfies REQ-039
- @satisfies REQ-066

### fn `def get_api_call_timeout_seconds() -> float` (L592-608)
- @brief Resolve HTTP response timeout in seconds from runtime configuration.
- @details Reads `api_call_timeout_milliseconds` from `RuntimeConfig` and converts to seconds. Returns `DEFAULT_API_CALL_TIMEOUT_MILLISECONDS / 1000.0` when configuration is missing or invalid.
- @return {float} HTTP response timeout in seconds (>= 0.001).
- @satisfies REQ-095
- @satisfies CTN-003

### fn `def load_env_file() -> dict[str, str]` (L609-627)
- @brief Execute load env file.
- @details Applies load env file logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {dict[str, str]} Function return value.

### fn `def write_env_file(updates: dict[str, str]) -> None` (L628-667)
- @brief Execute write env file.
- @details Applies write env file logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param updates {dict[str, str]} Input parameter `updates`.
- @return {None} Function return value.

### class `class Config` (L668-864)
- @brief Define config component.
- @details Encapsulates config state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `ENV_VARS =` (L675)
- var `PROVIDER_INFO =` (L685)
- fn `def get_token(self, provider: ProviderName) -> str | None` (L724-767)
  - @brief Execute get token.
  - @details Applies get token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @return {str | None} Function return value.
- fn `def is_provider_configured(self, provider: ProviderName) -> bool` (L768-799)
  - @brief Execute is provider configured.
  - @details Applies is provider configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @return {bool} Function return value.
- fn `def get_provider_status(self, provider: ProviderName) -> dict[str, Any]` (L800-821)
  - @brief Execute get provider status.
  - @details Applies get provider status logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @return {dict[str, Any]} Function return value.
- fn `def get_all_provider_status(self) -> list[dict[str, Any]]` (L822-829)
  - @brief Execute get all provider status.
  - @details Applies get all provider status logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {list[dict[str, Any]]} Function return value.
- fn `def _get_token_preview(self, provider: ProviderName) -> str | None` `priv` (L830-841)
  - @brief Execute get token preview.
  - @details Applies get token preview logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @return {str | None} Function return value.
- fn `def get_env_var_help(self) -> str` (L842-864)
  - @brief Execute get env var help.
  - @details Applies get env var help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`APP_CONFIG_DIR`|var|pub|21||
|`APP_CACHE_DIR`|var|pub|22||
|`ENV_FILE_PATH`|var|pub|23||
|`RUNTIME_CONFIG_PATH`|var|pub|24||
|`CACHE_FILE_PATH`|var|pub|25||
|`IDLE_TIME_PATH`|var|pub|26||
|`DEFAULT_IDLE_DELAY_SECONDS`|var|pub|28||
|`DEFAULT_API_CALL_DELAY_MILLISECONDS`|var|pub|29||
|`DEFAULT_API_CALL_TIMEOUT_MILLISECONDS`|var|pub|30||
|`DEFAULT_RETRY_AFTER_SECONDS`|var|pub|31||
|`DEFAULT_GNOME_REFRESH_INTERVAL_SECONDS`|var|pub|32||
|`DEFAULT_BILLING_DATASET`|var|pub|33||
|`DEFAULT_COPILOT_EXTRA_PREMIUM_REQUEST_COST`|var|pub|34||
|`DEFAULT_CURRENCY_SYMBOL`|var|pub|35||
|`DEFAULT_LOG_ENABLED`|var|pub|36||
|`DEFAULT_DEBUG_ENABLED`|var|pub|37||
|`LOG_TIMESTAMP_FORMAT`|var|pub|38||
|`LOCK_POLL_INTERVAL_SECONDS`|var|pub|40||
|`LOCK_ACQUIRE_TIMEOUT_SECONDS`|var|pub|41||
|`RuntimeConfig`|class|pub|50-112|class RuntimeConfig(BaseModel)|
|`IdleTimeState`|class|pub|113-128|class IdleTimeState(BaseModel)|
|`LockAcquisitionTimeoutError`|class|pub|129-139|class LockAcquisitionTimeoutError(RuntimeError)|
|`_ensure_app_config_dir`|fn|priv|140-149|def _ensure_app_config_dir() -> None|
|`_ensure_app_cache_dir`|fn|priv|150-159|def _ensure_app_cache_dir() -> None|
|`_runtime_log_path`|fn|priv|160-170|def _runtime_log_path() -> Path|
|`_runtime_log_flags`|fn|priv|171-187|def _runtime_log_flags() -> tuple[bool, bool]|
|`append_runtime_log_line`|fn|pub|188-213|def append_runtime_log_line(message: str, debug_only: boo...|
|`append_runtime_log_separator`|fn|pub|214-232|def append_runtime_log_separator() -> None|
|`_lock_file_path`|fn|priv|233-244|def _lock_file_path(target_path: Path) -> Path|
|`_blocking_file_lock`|fn|priv|246-294|def _blocking_file_lock(target_path: Path)|
|`_sanitize_cache_payload`|fn|priv|295-329|def _sanitize_cache_payload(payload: dict[str, Any]) -> d...|
|`clean`|fn|pub|307-326|def clean(value: Any) -> Any|
|`load_runtime_config`|fn|pub|330-346|def load_runtime_config() -> RuntimeConfig|
|`save_runtime_config`|fn|pub|347-363|def save_runtime_config(runtime_config: RuntimeConfig) ->...|
|`resolve_enabled_providers`|fn|pub|364-365|def resolve_enabled_providers(|
|`load_cli_cache`|fn|pub|388-414|def load_cli_cache() -> dict[str, Any] | None|
|`resolve_currency_symbol`|fn|pub|415-446|def resolve_currency_symbol(raw: dict[str, Any] | None, p...|
|`save_cli_cache`|fn|pub|447-473|def save_cli_cache(payload: dict[str, Any]) -> None|
|`build_idle_time_state`|fn|pub|474-475|def build_idle_time_state(|
|`load_idle_time`|fn|pub|509-539|def load_idle_time() -> dict[str, IdleTimeState]|
|`save_idle_time`|fn|pub|540-541|def save_idle_time(|
|`remove_idle_time_file`|fn|pub|576-591|def remove_idle_time_file() -> None|
|`get_api_call_timeout_seconds`|fn|pub|592-608|def get_api_call_timeout_seconds() -> float|
|`load_env_file`|fn|pub|609-627|def load_env_file() -> dict[str, str]|
|`write_env_file`|fn|pub|628-667|def write_env_file(updates: dict[str, str]) -> None|
|`Config`|class|pub|668-864|class Config|
|`Config.ENV_VARS`|var|pub|675||
|`Config.PROVIDER_INFO`|var|pub|685||
|`Config.get_token`|fn|pub|724-767|def get_token(self, provider: ProviderName) -> str | None|
|`Config.is_provider_configured`|fn|pub|768-799|def is_provider_configured(self, provider: ProviderName) ...|
|`Config.get_provider_status`|fn|pub|800-821|def get_provider_status(self, provider: ProviderName) -> ...|
|`Config.get_all_provider_status`|fn|pub|822-829|def get_all_provider_status(self) -> list[dict[str, Any]]|
|`Config._get_token_preview`|fn|priv|830-841|def _get_token_preview(self, provider: ProviderName) -> s...|
|`Config.get_env_var_help`|fn|pub|842-864|def get_env_var_help(self) -> str|


---

# extension.js | JavaScript | 2387L | 51 symbols | 9 imports | 52 comments
> Path: `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js`
- @brief GNOME Shell panel extension for aibar metrics.
- @details Collects usage JSON from the aibar CLI and renders provider-specific quota/cost cards in the GNOME panel popup.
- @note Targets GNOME Shell 45–48; uses ES module imports (gi:// and resource://) as required by GNOME Shell 45+.

## Imports
```
import GLib from 'gi://GLib';
import St from 'gi://St';
import Gio from 'gi://Gio';
import Clutter from 'gi://Clutter';
import GObject from 'gi://GObject';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';
import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js';
```

## Definitions

- const `const REFRESH_INTERVAL_SECONDS = 60;` (L18)
- const `const IDLE_DELAY_SECONDS = 300;` (L19)
- const `const ENV_FILE_PATH = GLib.get_home_dir() + '/.config/aibar/env';` (L20)
- const `const RESET_PENDING_MESSAGE = 'Starts when the first message is sent';` (L21)
- const `const RATE_LIMIT_ERROR_MESSAGE = 'Rate limited. Try again later.';` (L22)
- const `const CLAUDE_OAUTH_ERROR_MESSAGE = 'Invalid or expired OAuth token';` (L23)
- const `const PROVIDER_PROGRESS_CLASSES = {` (L24)
- const `const PANEL_ICON_COLORS = {` (L32)
- const `const PROVIDER_DISPLAY_NAMES = {` (L39)
- const `const API_COUNTER_PROVIDERS = new Set(['openai', 'openrouter', 'codex', 'geminiai']);` (L42)
- const `const PROGRESS_BAR_PROVIDERS = new Set(['claude', 'openrouter', 'copilot', 'codex']);` (L43)
- const `const TEXT_USAGE_PROVIDERS = new Set(['openai', 'geminiai']);` (L44)
- const `const WINDOW_BAR_30D_PROVIDERS = new Set(['copilot', 'openrouter']);` (L45)
- const `const DEFAULT_WINDOW_LABELS = Object.freeze({` (L46)
- const `const ALL_PROVIDER_NAMES = Object.freeze([` (L52)
- const `const DEFAULT_ENABLED_PROVIDERS = Object.freeze({` (L60)
- const `const PROVIDER_VIEWPORT_MAX_HEIGHT_PX = 260;` (L75)
- @brief Maximum popup viewport height for provider cards in pixels.
- @details Caps popup vertical growth while allowing short provider cards to
collapse the viewport height to content size. Time complexity O(1). Space
complexity O(1).
- @satisfies REQ-120
- const `const DEFAULT_COPILOT_EXTRA_PREMIUM_REQUEST_COST = 0.04;` (L76)
- const `const PROGRESS_SEGMENT_SHAPE_CLASSES = Object.freeze([` (L77)
- const `const PROGRESS_ROUNDED_END_MIN_WIDTH_PX = 3;` (L91)
- @brief Minimum overflow width that can render its own rounded right cap.
- @details Overflow widths below this threshold are absorbed into the fixed
100%-boundary marker so slightly-over-limit bars keep a visible rounded end
without forcing a 1px neutral segment to carry the right-edge radius. Time
complexity O(1). Space complexity O(1).
- @satisfies REQ-121
### fn `function _getProviderDisplayName(providerName)` (L98-102)
- @brief Resolve provider label text for GNOME tab/card rendering.
- @param {string} providerName Provider key from JSON payload.
- @return s {string} Display label for provider tab and card.

### fn `function _normalizeEnabledProvidersSection(enabledProviders)` (L113-122)
- @brief Normalize `enabled_providers` JSON section for extension state.
- @details Builds one provider-keyed boolean map for all known providers.
Missing keys normalize to `true` for backward compatibility with CLI JSON
documents emitted before provider-disable support existed.
- @param {Object<string, any> | null} enabledProviders Raw `enabled_providers` JSON section.
- @return s {Object<string, boolean>} Normalized provider-enabled mapping.
- @satisfies REQ-127

### fn `function _filterProviderObjectByEnabledProviders(providerData, enabledProviders)` (L134-144)
- @brief Filter provider-keyed JSON object by normalized enable-state map.
- @details Copies only provider entries whose normalized enabled flag is not
`false`. Non-object inputs normalize to `{}` to keep parser state
deterministic.
- @param {Object<string, any> | null} providerData Provider-keyed JSON section.
- @param {Object<string, boolean>} enabledProviders Normalized provider-enabled mapping.
- @return s {Object<string, any>} Filtered provider-keyed object.
- @satisfies REQ-127

### fn `function _resetMenuItemFocusVisualState(menuItem)` (L155-161)
- @brief Reset popup menu item pseudo-class state to base visual style.
- @details Removes `focus` and `active` pseudo classes from the menu item actor so
focus-loss transitions always return to the original color surface.
Time complexity O(1). Space complexity O(1).
- @param {any} menuItem Popup menu item actor candidate.
- @return s {boolean} True when pseudo-class removal API is available and executed.
- @satisfies DES-006

### fn `function _providerSupportsApiCounters(providerName)` (L171-173)
- @brief Check whether provider cards must render API counter labels.
- @details API-counter providers render `requests` and `tokens` labels on OK states
with null/undefined counters normalized to zero.
- @param {string} providerName Provider key from JSON payload.
- @return s {boolean} True when provider requires API counter label rendering.
- @satisfies REQ-017

### fn `function _resolveCopilotExtraPremiumCost(data, configuredUnitCost)` (L188-228)
- @brief Resolve Copilot premium-request overage monetary value.
- @details Computes overage primarily from `metrics.remaining`: returns `0` when
`remaining >= 0`; returns `-remaining * unit_cost` when `remaining < 0`.
Falls back to raw `premium_requests_extra_cost` or
`max(premium_requests - premium_requests_included, 0) * unit_cost` when
`remaining` is unavailable.
- @param {Object<string, any> | null} data Copilot provider payload.
- @param {number} configuredUnitCost Configured USD unit cost per extra request.
- @return s {number | null} Non-negative overage monetary value or null.
- @satisfies REQ-117
- @satisfies REQ-118

### fn `function _formatLocalDateTime(value)` (L236-247)
- @brief Format one Date object as local datetime for provider freshness labels.
- @details Produces `%Y-%m-%d %H:%M` in runtime local timezone; invalid Date values return null.
- @param {Date} value Date object to format.
- @return s {string | null} Formatted local datetime string or null.

### fn `function _coerceRetryAfterSeconds(value)` (L254-264)
- @brief Normalize retry-after value to positive integer seconds.
- @param {any} value Retry-after candidate value.
- @return s {number | null} Integer retry-after seconds or null when unavailable.

### fn `function _classifyPanelFailureCategory(statusEntry)` (L273-287)
- @brief Classify panel-failure category from cache status metadata.
- @details Returns one of `oauth`, `rate_limit`, or `other` by inspecting
normalized status error text and optional HTTP status code.
- @param {any} statusEntry Window-specific cache status entry.
- @return s {'oauth' | 'rate_limit' | 'other'} Failure category.

### fn `function _panelProviderFailureState(statusData, providerName, windows)` (L298-321)
- @brief Build provider-scoped panel failure state for one provider.
- @details Resolves per-window FAIL entries from status data and computes
`hasFailure` plus failure category for panel collapse logic.
- @param {Object<string, any>} statusData Provider-keyed status section.
- @param {string} providerName Provider key.
- @param {string[]} windows Ordered window keys to inspect.
- @return s {{hasFailure: boolean, category: 'oauth' | 'rate_limit' | 'other'}} Provider failure state.

### fn `function _buildHttpStatusRetryLabel(statusCodeRaw, retryAfterRaw)` (L330-340)
- @brief Build normalized HTTP status/retry metadata label.
- @param {any} statusCodeRaw HTTP status candidate value.
- @param {any} retryAfterRaw Retry-after candidate value.
- @return s {string} Diagnostic label text or empty string.
- @satisfies REQ-037

### fn `function _escapeMarkup(value)` (L347-354)
- @brief Escape text for safe Pango markup insertion.
- @param {string} value Raw text.
- @return s {string} Markup-safe text.

### fn `function _boldWhiteMarkup(value)` (L361-363)
- @brief Wrap one value as bright-white bold Pango markup.
- @param {string} value Raw text value.
- @return s {string} Bright-white bold markup snippet.

### fn `function _buildFallbackFreshnessState(statusEntry, idleDelaySeconds)` (L375-396)
- @brief Build provider freshness fallback from cache-status `updated_at` metadata.
- @details Converts `statusEntry.updated_at` to epoch seconds and derives
`idle_until_timestamp` using configured idle-delay seconds when `freshness`/`idle_time`
sections are unavailable from CLI JSON output.
- @param {any} statusEntry Window-specific cache status entry.
- @param {number} idleDelaySeconds Active idle delay in seconds.
- @return s {{last_success_timestamp: number, idle_until_timestamp: number} | null} Fallback freshness state or null.
- @satisfies REQ-017

### fn `function _resolveProviderFreshnessState(freshnessData, providerName, statusEntry, idleDelaySeconds)` (L410-424)
- @brief Resolve provider freshness state from canonical CLI freshness source.
- @details Uses `freshness.<provider>` (or `idle_time.<provider>` compatibility
alias populated by parser) and falls back to status-derived timestamps only
when freshness state is unavailable in CLI JSON.
- @param {Object<string, any>} freshnessData Provider-keyed freshness object.
- @param {string} providerName Provider key from usage payload.
- @param {any} statusEntry Window-specific cache status entry.
- @param {number} idleDelaySeconds Active idle delay in seconds.
- @return s {{last_success_timestamp: number, idle_until_timestamp: number} | null} Resolved freshness state.
- @satisfies REQ-017

### fn `function _getAiBarPath()` (L431-441)
- @brief Resolve aibar executable path.
- @details Prefers PATH discovery and falls back to AIBAR_PATH from the env file.
- @return s {string} Resolved executable path or fallback command name.

### fn `function _loadEnvFromFile()` (L448-500)
- @brief Load key-value environment variables from aibar env file.
- @details Parses export syntax, quoted values, and inline comments.
- @return s {Object<string,string>} Parsed environment map.

### fn `function _getProviderProgressClass(providerName)` (L507-509)
- @brief Map percentage usage to CSS progress severity class.
- @param {number} pct Usage percentage.
- @return s {string} CSS class suffix for progress state.

### fn `function _isDisplayedZeroPercent(pct)` (L518-525)
- @brief Check whether a percentage renders as `0.0%` in one-decimal UI output.
- @details Mirrors display rounding semantics so fallback reset text is shown when
usage is effectively zero from the user's perspective (e.g. internal 0.04 -> 0.0%).
- @param {number} pct Usage percentage candidate.
- @return s {boolean} True when value is finite, non-negative, and rounds to 0.0.

### fn `function _isDisplayedFullPercent(pct)` (L534-539)
- @brief Check whether a percentage renders as `100.0%` in one-decimal UI output.
- @details Mirrors display rounding semantics so near-full values are treated as
full usage for limit-reached warning rendering.
- @param {number} pct Usage percentage candidate.
- @return s {boolean} True when value is finite and rounds to `100.0`.

### fn `function _attachOverLimitActors(backgroundActor, fillActor)` (L554-568)
- @brief Attach over-limit visualization actors to one progress background.
- @details Appends one bright-neutral 100%-boundary marker actor and one opaque
neutral over-limit fill actor to the same horizontal background container used
by the provider fill.
Stores actor references on `fillActor` so shared geometry updates require only the
existing `_applyProgressFillGeometry(...)` call sites. Time complexity O(1). Space
complexity O(1).
- @param {St.BoxLayout} backgroundActor Progress background container.
- @param {St.Widget} fillActor Primary provider-color fill actor.
- @return s {void} No return value.
- @satisfies REQ-121

### fn `function _applyProgressSegmentRadii(fillActor, markerActor, overLimitActor, fillWidth, markerWidth, overLimitWidth)` (L586-616)
- @brief Apply rounded-edge shape classes to the currently visible progress segments.
- @details Ensures the bar start and end caps are rounded on whichever actors
actually touch the outer edges of the progress bar. This keeps sub-100 bars,
exactly-full bars, and over-limit bars visually correct even when the provider
fill no longer reaches the right edge because neutral overflow segments are
visible. Time complexity O(1). Space complexity O(1).
- @param {St.Widget | null} fillActor Provider-color segment actor.
- @param {St.Widget | null} markerActor Fixed 100%-boundary marker actor.
- @param {St.Widget | null} overLimitActor Neutral overflow segment actor.
- @param {number} fillWidth Computed width of the provider-color segment.
- @param {number} markerWidth Computed width of the 100%-boundary marker.
- @param {number} overLimitWidth Computed width of the neutral overflow segment.
- @return s {void} No return value.
- @satisfies REQ-121

### fn `function _applyProgressFillGeometry(fillActor, backgroundActor, pct)` (L636-684)
- @brief Apply deterministic progress-fill geometry with over-limit segment support.
- @details Computes fixed-width progress geometry from percentage and current
background width. Percentages up to `100` render provider-color fill plus background.
Percentages above `100` render a provider-color base segment, a fixed 2px 100%
boundary marker, and a neutral over-limit segment scaled across the extra `0..100`
range and clamped for larger values. When the neutral overflow segment is too
thin to render a visible rounded end cap, its width is absorbed into the marker
so the right edge stays rounded without widening the bar. The helper preserves
side-label layout by never exceeding the background width. Time complexity O(1).
Space complexity O(1).
- @param {St.Widget} fillActor Progress fill widget receiving width updates.
- @param {St.Widget} backgroundActor Progress background widget providing max width.
- @param {number} pct Usage percentage value.
- @return s {void} No return value.
- @satisfies REQ-119
- @satisfies REQ-121

### class `class AIBarIndicator extends PanelMenu.Button` : PanelMenu.Button (L688-987)
- @brief Panel indicator widget that manages popup rendering and refresh lifecycle. */
- @brief Execute init.
- @details Applies init logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
- @return s {any} Function return value.

### fn `const createWindowBar = (labelText) =>` (L1135-1181)
- @brief Execute create provider card.
- @details Applies create provider card logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
- @param {any} providerName Input parameter `providerName`.
- @return s {any} Function return value.

### fn `const updateWindowBar = (bar, pct, resetTime, useDays, allowResetPendingHint = true) =>` (L1372-1436)
- @brief Execute populate provider card.
- @details Projects provider payload and cached status into one card surface.
Failed states render a strict block with `Status: FAIL` and `Reason: ...`
while keeping `Updated: ..., Next: ...` freshness output and suppressing
usage/reset/quota/cost rows. Successful states render metrics using
existing provider-specific card rules, including Copilot
`Cost: <currency_symbol><value>` row. `claude/openrouter/copilot/codex`
keep progress bars, while `openai/geminiai` render
`Usage: <window> <percent>%` text without bar widgets. Dual-window
providers preserve fixed left labels `5h` and `7d`; progress-width
geometry recalculation must not blank those labels.
- @param {any} card Input parameter `card`.
- @param {any} providerName Input parameter `providerName`.
- @param {any} data Input parameter `data`.
- @param {any} statusEntry Window-specific cached status entry.
- @param {any} freshnessState Provider-scoped freshness entry from `freshness` section.
- @return s {any} Function return value.
- @satisfies REQ-017
- @satisfies REQ-117
- @satisfies REQ-130

### fn `const setResetLabel = (baseText) =>` (L1378-1384)

### fn `const showResetPendingHint = () =>` (L1391-1393)

### fn `const toPercent = (value) =>` (L2053-2058)
- @brief Execute update u i.
- @details Applies update u i logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
Resolves provider-window failure metadata from cache `status` section and forwards it
to card renderers. Panel status row renders fixed-order percentages and per-provider costs.
After card refresh, re-sizes the popup provider viewport to the visible card height.
- @return s {any} Function return value.
- @satisfies REQ-021
- @satisfies REQ-053
- @satisfies REQ-069
- @satisfies REQ-118
- @satisfies REQ-120
- @satisfies REQ-127

### fn `const getPanelUsageValues = (providerName, data) =>` (L2059-2116)

### class `export default class AIBarExtension extends Extension` : Extension (L2361-2387)
- @brief GNOME extension lifecycle adapter for AIBarIndicator registration.
- @brief Execute enable.
- @details Extends Extension (GNOME Shell 45+ API) to integrate with the extension lifecycle.
Uses this.uuid (provided by the Extension base class) as the status-area key.
- @details Instantiates AIBarIndicator and adds it to the GNOME panel status area.
- @return s {void}
- @satisfies PRJ-004

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`REFRESH_INTERVAL_SECONDS`|const||18||
|`IDLE_DELAY_SECONDS`|const||19||
|`ENV_FILE_PATH`|const||20||
|`RESET_PENDING_MESSAGE`|const||21||
|`RATE_LIMIT_ERROR_MESSAGE`|const||22||
|`CLAUDE_OAUTH_ERROR_MESSAGE`|const||23||
|`PROVIDER_PROGRESS_CLASSES`|const||24||
|`PANEL_ICON_COLORS`|const||32||
|`PROVIDER_DISPLAY_NAMES`|const||39||
|`API_COUNTER_PROVIDERS`|const||42||
|`PROGRESS_BAR_PROVIDERS`|const||43||
|`TEXT_USAGE_PROVIDERS`|const||44||
|`WINDOW_BAR_30D_PROVIDERS`|const||45||
|`DEFAULT_WINDOW_LABELS`|const||46||
|`ALL_PROVIDER_NAMES`|const||52||
|`DEFAULT_ENABLED_PROVIDERS`|const||60||
|`PROVIDER_VIEWPORT_MAX_HEIGHT_PX`|const||75||
|`DEFAULT_COPILOT_EXTRA_PREMIUM_REQUEST_COST`|const||76||
|`PROGRESS_SEGMENT_SHAPE_CLASSES`|const||77||
|`PROGRESS_ROUNDED_END_MIN_WIDTH_PX`|const||91||
|`_getProviderDisplayName`|fn||98-102|function _getProviderDisplayName(providerName)|
|`_normalizeEnabledProvidersSection`|fn||113-122|function _normalizeEnabledProvidersSection(enabledProviders)|
|`_filterProviderObjectByEnabledProviders`|fn||134-144|function _filterProviderObjectByEnabledProviders(provider...|
|`_resetMenuItemFocusVisualState`|fn||155-161|function _resetMenuItemFocusVisualState(menuItem)|
|`_providerSupportsApiCounters`|fn||171-173|function _providerSupportsApiCounters(providerName)|
|`_resolveCopilotExtraPremiumCost`|fn||188-228|function _resolveCopilotExtraPremiumCost(data, configured...|
|`_formatLocalDateTime`|fn||236-247|function _formatLocalDateTime(value)|
|`_coerceRetryAfterSeconds`|fn||254-264|function _coerceRetryAfterSeconds(value)|
|`_classifyPanelFailureCategory`|fn||273-287|function _classifyPanelFailureCategory(statusEntry)|
|`_panelProviderFailureState`|fn||298-321|function _panelProviderFailureState(statusData, providerN...|
|`_buildHttpStatusRetryLabel`|fn||330-340|function _buildHttpStatusRetryLabel(statusCodeRaw, retryA...|
|`_escapeMarkup`|fn||347-354|function _escapeMarkup(value)|
|`_boldWhiteMarkup`|fn||361-363|function _boldWhiteMarkup(value)|
|`_buildFallbackFreshnessState`|fn||375-396|function _buildFallbackFreshnessState(statusEntry, idleDe...|
|`_resolveProviderFreshnessState`|fn||410-424|function _resolveProviderFreshnessState(freshnessData, pr...|
|`_getAiBarPath`|fn||431-441|function _getAiBarPath()|
|`_loadEnvFromFile`|fn||448-500|function _loadEnvFromFile()|
|`_getProviderProgressClass`|fn||507-509|function _getProviderProgressClass(providerName)|
|`_isDisplayedZeroPercent`|fn||518-525|function _isDisplayedZeroPercent(pct)|
|`_isDisplayedFullPercent`|fn||534-539|function _isDisplayedFullPercent(pct)|
|`_attachOverLimitActors`|fn||554-568|function _attachOverLimitActors(backgroundActor, fillActor)|
|`_applyProgressSegmentRadii`|fn||586-616|function _applyProgressSegmentRadii(fillActor, markerActo...|
|`_applyProgressFillGeometry`|fn||636-684|function _applyProgressFillGeometry(fillActor, background...|
|`AIBarIndicator`|class||688-987|class AIBarIndicator extends PanelMenu.Button|
|`createWindowBar`|fn||1135-1181|const createWindowBar = (labelText) =>|
|`updateWindowBar`|fn||1372-1436|const updateWindowBar = (bar, pct, resetTime, useDays, al...|
|`setResetLabel`|fn||1378-1384|const setResetLabel = (baseText) =>|
|`showResetPendingHint`|fn||1391-1393|const showResetPendingHint = () =>|
|`toPercent`|fn||2053-2058|const toPercent = (value) =>|
|`getPanelUsageValues`|fn||2059-2116|const getPanelUsageValues = (providerName, data) =>|
|`AIBarExtension`|class||2361-2387|export default class AIBarExtension extends Extension|


---

# __init__.py | Python | 25L | 0 symbols | 7 imports | 1 comments
> Path: `src/aibar/aibar/providers/__init__.py`
- @brief Provider implementation exports.
- @details Re-exports provider contracts and concrete provider classes for centralized CLI/UI provider registration.

## Imports
```
from aibar.providers.base import BaseProvider, UsageMetrics, ProviderResult
from aibar.providers.claude_oauth import ClaudeOAuthProvider
from aibar.providers.openai_usage import OpenAIUsageProvider
from aibar.providers.openrouter import OpenRouterUsageProvider
from aibar.providers.copilot import CopilotProvider
from aibar.providers.codex import CodexProvider
from aibar.providers.geminiai import GeminiAIProvider
```


---

# base.py | Python | 190L | 24 symbols | 5 imports | 16 comments
> Path: `src/aibar/aibar/providers/base.py`
- @brief Base provider abstractions and normalized metric models.
- @details Defines provider/window enums, normalized usage/result payloads, provider exception hierarchy, and the abstract provider interface.

## Imports
```
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
```

## Definitions

### class `class WindowPeriod(str, Enum)` : str, Enum (L15-25)
- @brief Define window period component.
- @details Encapsulates window period state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `HOUR_5 = "5h"` (L21)
  - @brief Define window period component.
  - @details Encapsulates window period state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `DAY_7 = "7d"` (L22)
- var `DAY_30 = "30d"` (L23)

### class `class ProviderName(str, Enum)` : str, Enum (L26-39)
- @brief Define provider name component.
- @details Encapsulates provider name state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `CLAUDE = "claude"` (L32)
  - @brief Define provider name component.
  - @details Encapsulates provider name state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `OPENAI = "openai"` (L33)
- var `OPENROUTER = "openrouter"` (L34)
- var `COPILOT = "copilot"` (L35)
- var `CODEX = "codex"` (L36)
- var `GEMINIAI = "geminiai"` (L37)

### class `class UsageMetrics(BaseModel)` : BaseModel (L40-86)
- @brief Define usage metrics component.
- @details Encapsulates normalized provider usage metrics for AIBar runtime flows. Field `currency_symbol` annotates all monetary fields (`cost`, `remaining`, `limit`) and defaults to `"$"` when not resolved from API response or provider config.
- @satisfies CTN-002
- @satisfies REQ-050
- @satisfies REQ-051
- @satisfies REQ-052
- @satisfies REQ-053
- fn `def usage_percent(self) -> float | None` (L63-74)
  - @brief Execute usage percent.
  - @details Applies usage percent logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {float | None} Function return value.
- fn `def total_tokens(self) -> int | None` (L76-86)
  - @brief Execute total tokens.
  - @details Applies total tokens logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {int | None} Function return value.

### class `class ProviderResult(BaseModel)` : BaseModel (L87-109)
- @brief Define provider result component.
- @details Encapsulates provider result state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `def is_error(self) -> bool` (L101-109)
  - @brief Execute is error.
  - @details Applies is error logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {bool} Function return value.

### class `class ProviderError(Exception)` : Exception (L110-118)
- @brief Define provider error component.
- @details Encapsulates provider error state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.

### class `class AuthenticationError(ProviderError)` : ProviderError (L119-127)
- @brief Define authentication error component.
- @details Encapsulates authentication error state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.

### class `class RateLimitError(ProviderError)` : ProviderError (L128-136)
- @brief Define rate limit error component.
- @details Encapsulates rate limit error state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.

### class `class BaseProvider(ABC)` : ABC (L137-190)
- @brief Define base provider component.
- @details Encapsulates base provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L146-154)
  - @brief Execute fetch.
  - @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param window {WindowPeriod} Input parameter `window`.
  - @return {ProviderResult} Function return value.
- fn `def is_configured(self) -> bool` (L156-163)
  - @brief Execute is configured.
  - @details Applies is configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {bool} Function return value.
- fn `def get_config_help(self) -> str` (L165-172)
  - @brief Execute get config help.
  - @details Applies get config help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str} Function return value.
- fn `def _make_error_result(` `priv` (L173-174)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`WindowPeriod`|class|pub|15-25|class WindowPeriod(str, Enum)|
|`WindowPeriod.HOUR_5`|var|pub|21||
|`WindowPeriod.DAY_7`|var|pub|22||
|`WindowPeriod.DAY_30`|var|pub|23||
|`ProviderName`|class|pub|26-39|class ProviderName(str, Enum)|
|`ProviderName.CLAUDE`|var|pub|32||
|`ProviderName.OPENAI`|var|pub|33||
|`ProviderName.OPENROUTER`|var|pub|34||
|`ProviderName.COPILOT`|var|pub|35||
|`ProviderName.CODEX`|var|pub|36||
|`ProviderName.GEMINIAI`|var|pub|37||
|`UsageMetrics`|class|pub|40-86|class UsageMetrics(BaseModel)|
|`UsageMetrics.usage_percent`|fn|pub|63-74|def usage_percent(self) -> float | None|
|`UsageMetrics.total_tokens`|fn|pub|76-86|def total_tokens(self) -> int | None|
|`ProviderResult`|class|pub|87-109|class ProviderResult(BaseModel)|
|`ProviderResult.is_error`|fn|pub|101-109|def is_error(self) -> bool|
|`ProviderError`|class|pub|110-118|class ProviderError(Exception)|
|`AuthenticationError`|class|pub|119-127|class AuthenticationError(ProviderError)|
|`RateLimitError`|class|pub|128-136|class RateLimitError(ProviderError)|
|`BaseProvider`|class|pub|137-190|class BaseProvider(ABC)|
|`BaseProvider.fetch`|fn|pub|146-154|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`BaseProvider.is_configured`|fn|pub|156-163|def is_configured(self) -> bool|
|`BaseProvider.get_config_help`|fn|pub|165-172|def get_config_help(self) -> str|
|`BaseProvider._make_error_result`|fn|priv|173-174|def _make_error_result(|


---

# claude_oauth.py | Python | 387L | 16 symbols | 13 imports | 19 comments
> Path: `src/aibar/aibar/providers/claude_oauth.py`
- @brief Claude OAuth usage provider.
- @details Fetches Claude subscription utilization through OAuth credentials and normalizes provider quota state into the shared result contract.

## Imports
```
import asyncio
import email.utils
import os
import random
from datetime import datetime, timezone
import httpx
from aibar.claude_cli_auth import extract_claude_cli_token
from aibar.providers.base import (
from aibar.config import resolve_currency_symbol
from aibar.config import load_runtime_config
from aibar.config import get_api_call_timeout_seconds
from aibar.config import get_api_call_timeout_seconds
from datetime import timezone
```

## Definitions

### fn `def _parse_retry_after_header(retry_after_raw: str | None) -> float` `priv` (L27-65)
- @brief Parse HTTP Retry-After header to delay seconds.
- @details Supports numeric and HTTP-date formats. Numeric values are treated as relative seconds by default, but large numeric values are normalized as epoch timestamps (seconds or milliseconds) and converted to relative delay seconds against current UTC time. Date values are converted to seconds relative to current UTC time and clamped to zero.
- @param retry_after_raw {str | None} Retry-After header value.
- @return {float} Non-negative delay seconds as float.

### fn `def _resolve_provider_currency(raw: dict, provider_name: str) -> str` `priv` (L66-80)
- @brief Resolve currency symbol for a provider from raw API response or config.
- @details Delegates to `resolve_currency_symbol` from `aibar.config`. Imported lazily inside the function to avoid circular import at module load time.
- @param raw {dict} Raw API response dict.
- @param provider_name {str} Provider name key.
- @return {str} Resolved currency symbol.
- @satisfies REQ-050

### class `class ClaudeOAuthProvider(BaseProvider)` : BaseProvider (L81-117)
- @brief Define claude o auth provider component.
- @details Encapsulates claude o auth provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `USAGE_URL = "https://api.anthropic.com/api/oauth/usage"` (L88)
  - @brief Define claude o auth provider component.
  - @details Encapsulates claude o auth provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `TOKEN_ENV_VAR = "CLAUDE_CODE_OAUTH_TOKEN"` (L89)
- fn `def __init__(self, token: str | None = None) -> None` `priv` (L91-101)
  - @brief Execute init.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param token {str | None} Input parameter `token`.
  - @return {None} Function return value.
- fn `def is_configured(self) -> bool` (L102-109)
  - @brief Execute is configured.
  - @details Applies is configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {bool} Function return value.
- fn `def get_config_help(self) -> str` (L110-117)
  - @brief Execute get config help.
  - @details Applies get config help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str} Function return value.

- var `MAX_RETRIES = 3` (L124)
- var `RETRY_BACKOFF_BASE = 2.0` (L125)
- var `RETRY_JITTER_MAX = 1.0` (L126)
### fn `async def _request_usage(self, client: httpx.AsyncClient) -> httpx.Response` `priv` (L128-167)
- @brief Execute HTTP GET to usage endpoint with retry on HTTP 429.
- @details Retries up to MAX_RETRIES times on 429 responses, respecting the retry-after header with exponential backoff fallback and random jitter to prevent thundering-herd synchronization. Backoff sequence with RETRY_BACKOFF_BASE=2.0: ~2-3s, ~4-5s, ~8-9s (total ~14-17s).
- @param client {httpx.AsyncClient} Reusable HTTP client session.
- @return {httpx.Response} Final HTTP response after retries exhausted or success.

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L168-211)
- @brief Execute fetch for a single window period.
- @details Makes one HTTP request to the usage endpoint (with retry on 429) and parses the response for the requested window.
- @param window {WindowPeriod} Window period to parse from the API response.
- @return {ProviderResult} Parsed result for the requested window.
- @throws {AuthenticationError} When the OAuth token is invalid or expired.
- @throws {ProviderError} On unexpected non-HTTP errors.

### fn `async def fetch_all_windows(` (L212-213)

### fn `def _handle_response(` `priv` (L270-271)

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L321-387)
- @brief Map HTTP error status codes to ProviderResult error payloads.
- @brief Normalize a raw Claude API payload dict into a ProviderResult for the given window.
- @details Returns None on HTTP 200 (success), otherwise returns an error
ProviderResult for the given window. Raises AuthenticationError on 401.
- @details Selects `five_hour` or `seven_day` sub-dict from `data` based on `window` (fallback to `seven_day` if the specific key is absent or empty). Derives `remaining` from `utilization` field and `reset_at` from `resets_at` field. `reset_at` is set to None when the parsed datetime is already in the past relative to the current UTC clock, preventing stale cached timestamps from propagating to the display layer and causing asymmetric suppression of the 'Resets in:' output between the 5h and 7d windows (REQ-002 symmetry requirement).
- @param response {httpx.Response} HTTP response to evaluate.
- @param window {WindowPeriod} Window period for error result construction.
- @param data {dict} Raw JSON payload from Claude usage API or stale disk cache. Expected keys: `five_hour` and/or `seven_day`, each containing optional `utilization` (float, 0-100) and `resets_at` (ISO 8601 string).
- @param window {WindowPeriod} Target window period for result construction. `WindowPeriod.DAY_7` selects `seven_day`; all others select `five_hour`.
- @return {ProviderResult | None} Error result or None if response is 200.
- @return {ProviderResult} Normalized result with `metrics.remaining` set to `100 - utilization`, `metrics.reset_at` set to the parsed future datetime or None, and `raw` set to the full unmodified `data` payload.
- @throws {AuthenticationError} When HTTP status is 401.
- @satisfies REQ-002

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`_parse_retry_after_header`|fn|priv|27-65|def _parse_retry_after_header(retry_after_raw: str | None...|
|`_resolve_provider_currency`|fn|priv|66-80|def _resolve_provider_currency(raw: dict, provider_name: ...|
|`ClaudeOAuthProvider`|class|pub|81-117|class ClaudeOAuthProvider(BaseProvider)|
|`ClaudeOAuthProvider.USAGE_URL`|var|pub|88||
|`ClaudeOAuthProvider.TOKEN_ENV_VAR`|var|pub|89||
|`ClaudeOAuthProvider.__init__`|fn|priv|91-101|def __init__(self, token: str | None = None) -> None|
|`ClaudeOAuthProvider.is_configured`|fn|pub|102-109|def is_configured(self) -> bool|
|`ClaudeOAuthProvider.get_config_help`|fn|pub|110-117|def get_config_help(self) -> str|
|`MAX_RETRIES`|var|pub|124||
|`RETRY_BACKOFF_BASE`|var|pub|125||
|`RETRY_JITTER_MAX`|var|pub|126||
|`_request_usage`|fn|priv|128-167|async def _request_usage(self, client: httpx.AsyncClient)...|
|`fetch`|fn|pub|168-211|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`fetch_all_windows`|fn|pub|212-213|async def fetch_all_windows(|
|`_handle_response`|fn|priv|270-271|def _handle_response(|
|`_parse_response`|fn|priv|321-387|def _parse_response(self, data: dict, window: WindowPerio...|


---

# codex.py | Python | 452L | 22 symbols | 9 imports | 33 comments
> Path: `src/aibar/aibar/providers/codex.py`
- @brief OpenAI Codex usage provider and credential helpers.
- @details Resolves Codex credentials, refreshes OAuth tokens when required, queries usage endpoints, and normalizes quota metrics.

## Imports
```
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import httpx
from aibar.providers.base import (
from aibar.config import resolve_currency_symbol
from aibar.config import get_api_call_timeout_seconds
from aibar.config import get_api_call_timeout_seconds
```

## Definitions

### fn `def _resolve_provider_currency(raw: dict, provider_name: str) -> str` `priv` (L24-36)
- @brief Resolve currency symbol from raw API response or configured provider default.
- @details Delegates to `resolve_currency_symbol` in `aibar.config` (lazy import).
- @param raw {dict} Raw API response dict.
- @param provider_name {str} Provider name key.
- @return {str} Resolved currency symbol.
- @satisfies REQ-050

### class `class CodexCredentials` (L37-104)
- @brief Define codex credentials component.
- @details Encapsulates codex credentials state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `def __init__(` `priv` (L43-49)
  - @brief Define codex credentials component.
  - @details Encapsulates codex credentials state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `def needs_refresh(self) -> bool` (L67-77)
  - @brief Execute init.
  - @brief Execute needs refresh.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @details Applies needs refresh logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param access_token {str} Input parameter `access_token`.
  - @param refresh_token {str} Input parameter `refresh_token`.
  - @param id_token {str} Input parameter `id_token`.
  - @param account_id {str | None} Input parameter `account_id`.
  - @param last_refresh {datetime | None} Input parameter `last_refresh`.
  - @return {None} Function return value.
  - @return {bool} Function return value.
- fn `def from_auth_json(cls, data: dict) -> "CodexCredentials"` (L79-104)
  - @brief Execute from auth json.
  - @details Applies from auth json logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param data {dict} Input parameter `data`.
  - @return {'CodexCredentials'} Function return value.

### class `class CodexCredentialStore` (L105-195)
- @brief Define codex credential store component.
- @details Encapsulates codex credential store state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `def codex_home(self) -> Path` (L112-121)
  - @brief Execute codex home.
  - @details Applies codex home logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {Path} Function return value.
- fn `def auth_file(self) -> Path` (L123-130)
  - @brief Execute auth file.
  - @details Applies auth file logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {Path} Function return value.
- fn `def load(self) -> CodexCredentials | None` (L131-170)
  - @brief Execute load.
  - @details Applies load logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {CodexCredentials | None} Function return value.
- fn `def save(self, credentials: CodexCredentials) -> None` (L171-195)
  - @brief Execute save.
  - @details Applies save logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param credentials {CodexCredentials} Input parameter `credentials`.
  - @return {None} Function return value.

### class `class CodexTokenRefresher` (L196-261)
- @brief Define codex token refresher component.
- @details Encapsulates codex token refresher state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `REFRESH_URL = "https://auth.openai.com/oauth/token"` (L202)
  - @brief Define codex token refresher component.
  - @details Encapsulates codex token refresher state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"` (L203)
- fn `async def refresh(self, credentials: CodexCredentials) -> CodexCredentials` (L205-261)
  - @brief Execute refresh.
  - @details Applies refresh logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param credentials {CodexCredentials} Input parameter `credentials`.
  - @return {CodexCredentials} Function return value.
  - @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### class `class CodexProvider(BaseProvider)` : BaseProvider (L262-300)
- @brief Define codex provider component.
- @details Encapsulates codex provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `BASE_URL = "https://chatgpt.com/backend-api"` (L271)
- var `USAGE_PATH = "/wham/usage"` (L272)
- fn `def __init__(self, credentials: CodexCredentials | None = None) -> None` `priv` (L274-284)
  - @brief Execute init.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param credentials {CodexCredentials | None} Input parameter `credentials`.
  - @return {None} Function return value.
- fn `def is_configured(self) -> bool` (L285-292)
  - @brief Execute is configured.
  - @details Applies is configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {bool} Function return value.
- fn `def get_config_help(self) -> str` (L293-300)
  - @brief Execute get config help.
  - @details Applies get config help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str} Function return value.

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L312-398)
- @brief Execute fetch.
- @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L399-452)
- @brief Execute parse response.
- @details Applies parse response logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param data {dict} Input parameter `data`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`_resolve_provider_currency`|fn|priv|24-36|def _resolve_provider_currency(raw: dict, provider_name: ...|
|`CodexCredentials`|class|pub|37-104|class CodexCredentials|
|`CodexCredentials.__init__`|fn|priv|43-49|def __init__(|
|`CodexCredentials.needs_refresh`|fn|pub|67-77|def needs_refresh(self) -> bool|
|`CodexCredentials.from_auth_json`|fn|pub|79-104|def from_auth_json(cls, data: dict) -> "CodexCredentials"|
|`CodexCredentialStore`|class|pub|105-195|class CodexCredentialStore|
|`CodexCredentialStore.codex_home`|fn|pub|112-121|def codex_home(self) -> Path|
|`CodexCredentialStore.auth_file`|fn|pub|123-130|def auth_file(self) -> Path|
|`CodexCredentialStore.load`|fn|pub|131-170|def load(self) -> CodexCredentials | None|
|`CodexCredentialStore.save`|fn|pub|171-195|def save(self, credentials: CodexCredentials) -> None|
|`CodexTokenRefresher`|class|pub|196-261|class CodexTokenRefresher|
|`CodexTokenRefresher.REFRESH_URL`|var|pub|202||
|`CodexTokenRefresher.CLIENT_ID`|var|pub|203||
|`CodexTokenRefresher.refresh`|fn|pub|205-261|async def refresh(self, credentials: CodexCredentials) ->...|
|`CodexProvider`|class|pub|262-300|class CodexProvider(BaseProvider)|
|`CodexProvider.BASE_URL`|var|pub|271||
|`CodexProvider.USAGE_PATH`|var|pub|272||
|`CodexProvider.__init__`|fn|priv|274-284|def __init__(self, credentials: CodexCredentials | None =...|
|`CodexProvider.is_configured`|fn|pub|285-292|def is_configured(self) -> bool|
|`CodexProvider.get_config_help`|fn|pub|293-300|def get_config_help(self) -> str|
|`fetch`|fn|pub|312-398|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|399-452|def _parse_response(self, data: dict, window: WindowPerio...|


---

# copilot.py | Python | 614L | 31 symbols | 14 imports | 33 comments
> Path: `src/aibar/aibar/providers/copilot.py`
- @brief GitHub Copilot usage provider and device-flow authentication.
- @details Handles device-code authorization, token storage resolution, Copilot quota retrieval, and normalization to provider result schema.

## Imports
```
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import httpx
from aibar.providers.base import (
from aibar.config import resolve_currency_symbol
from aibar.config import get_api_call_timeout_seconds
import asyncio
from aibar.config import get_api_call_timeout_seconds
from aibar.config import get_api_call_timeout_seconds
from aibar.config import (
```

## Definitions

### fn `def _resolve_provider_currency(raw: dict, provider_name: str) -> str` `priv` (L27-39)
- @brief Resolve currency symbol from raw API response or configured provider default.
- @details Delegates to `resolve_currency_symbol` in `aibar.config` (lazy import).
- @param raw {dict} Raw API response dict.
- @param provider_name {str} Provider name key.
- @return {str} Resolved currency symbol.
- @satisfies REQ-050

### class `class CopilotDeviceFlow` (L40-132)
- @brief Define copilot device flow component.
- @details Encapsulates copilot device flow state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `CLIENT_ID = "Iv1.b507a08c87ecfe98"` (L47)
- var `SCOPES = "read:user"` (L48)
- var `DEVICE_CODE_URL = "https://github.com/login/device/code"` (L50)
- var `TOKEN_URL = "https://github.com/login/oauth/access_token"` (L51)
- fn `async def request_device_code(self) -> dict[str, Any]` (L53-79)
  - @brief Execute request device code.
  - @details Applies request device code logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {dict[str, Any]} Function return value.
  - @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.
- fn `async def poll_for_token(self, device_code: str, interval: int = 5) -> str` (L80-132)
  - @brief Execute poll for token.
  - @details Applies poll for token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param device_code {str} Input parameter `device_code`.
  - @param interval {int} Input parameter `interval`.
  - @return {str} Function return value.
  - @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### class `class CopilotCredentialStore` (L133-189)
- @brief Define copilot credential store component.
- @details Encapsulates copilot credential store state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `CONFIG_DIR = Path.home() / ".config" / "aibar"` (L139)
  - @brief Define copilot credential store component.
  - @details Encapsulates copilot credential store state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `CREDS_FILE = CONFIG_DIR / "copilot.json"` (L140)
- var `CODEXBAR_CONFIG = Path.home() / ".codexbar" / "config.json"` (L141)
- fn `def load_token(self) -> str | None` (L143-174)
  - @brief Execute load token.
  - @details Applies load token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str | None} Function return value.
- fn `def save_token(self, token: str) -> None` (L175-189)
  - @brief Execute save token.
  - @details Applies save token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param token {str} Input parameter `token`.
  - @return {None} Function return value.

### class `class CopilotProvider(BaseProvider)` : BaseProvider (L190-230)
- @brief Define copilot provider component.
- @details Encapsulates copilot provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `USAGE_URL = "https://api.github.com/copilot_internal/user"` (L197)
  - @brief Define copilot provider component.
  - @details Encapsulates copilot provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `EDITOR_VERSION = "vscode/1.96.2"` (L200)
- var `PLUGIN_VERSION = "copilot-chat/0.26.7"` (L201)
- var `USER_AGENT = "GitHubCopilotChat/0.26.7"` (L202)
- var `API_VERSION = "2025-04-01"` (L203)
- fn `def __init__(self, token: str | None = None) -> None` `priv` (L205-214)
  - @brief Execute init.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param token {str | None} Input parameter `token`.
  - @return {None} Function return value.
- fn `def is_configured(self) -> bool` (L215-222)
  - @brief Execute is configured.
  - @details Applies is configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {bool} Function return value.
- fn `def get_config_help(self) -> str` (L223-230)
  - @brief Execute get config help.
  - @details Applies get config help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str} Function return value.

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L240-318)
- @brief Execute fetch.
- @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L319-518)
- @brief Normalize Copilot quota payload to ProviderResult.
- @details Resolves quota snapshot fields and computes Copilot premium-request overage from normalized `remaining` semantics: when `remaining >= 0`, overage is `0`; when `remaining < 0`, overage is `-remaining`. Computes `premium_requests_extra_cost = premium_requests_extra * copilot_extra_premium_request_cost`, sets `metrics.cost` to the computed overage monetary value (fallback `0.0`), and persists normalized premium-overage fields in `raw` for CLI and GNOME rendering.
- @param data {dict} Raw Copilot API JSON payload.
- @param window {WindowPeriod} Effective window (`30d` for Copilot).
- @return {ProviderResult} Normalized provider result payload.
- @satisfies REQ-012
- @satisfies REQ-116
- @satisfies REQ-117
- @satisfies REQ-118

### fn `def _coerce_float(value: Any) -> float | None` `priv` (L338-352)
- @brief Normalize Copilot quota payload to ProviderResult.
- @brief Parse one finite numeric value to float.
- @details Resolves quota snapshot fields and computes Copilot premium-request
overage from normalized `remaining` semantics: when `remaining >= 0`,
overage is `0`; when `remaining < 0`, overage is `-remaining`. Computes
`premium_requests_extra_cost = premium_requests_extra * copilot_extra_premium_request_cost`,
sets `metrics.cost` to the computed overage monetary value (fallback `0.0`),
and persists normalized premium-overage fields in `raw` for CLI and GNOME rendering.
- @details Returns None for non-numeric values and non-finite floats.
- @param data {dict} Raw Copilot API JSON payload.
- @param window {WindowPeriod} Effective window (`30d` for Copilot).
- @param value {object} Candidate numeric value.
- @return {ProviderResult} Normalized provider result payload.
- @return {float | None} Parsed finite float or None.
- @satisfies REQ-012
- @satisfies REQ-116
- @satisfies REQ-117
- @satisfies REQ-118

### fn `def _first_numeric(snapshot: dict[str, Any], keys: tuple[str, ...]) -> float | None` `priv` (L353-368)
- @brief Resolve first available numeric field from snapshot keys.
- @details Scans keys in order and returns the first finite numeric value.
- @param snapshot {dict[str, Any]} Snapshot payload mapping.
- @param keys {tuple[str, ...]} Candidate key sequence.
- @return {float | None} First parsed float value or None.

### fn `def _get_snapshot(key_camel: str, key_snake: str) -> dict` `priv` (L369-377)
- @brief Resolve one quota snapshot object by camel/snake aliases.
- @param key_camel {str} CamelCase snapshot key.
- @param key_snake {str} snake_case snapshot key.
- @return {dict} Snapshot mapping or empty dict.

### fn `def _extract_quota_data(snapshot: dict) -> tuple[float | None, float | None]` `priv` (L378-402)
- @brief Extract remaining and limit values from one quota snapshot.
- @details Prefers entitlement/remaining numeric values and falls back to percentage-normalized `(remaining_percent, 100.0)` representation.
- @param snapshot {dict} Snapshot payload mapping.
- @return {tuple[float | None, float | None]} Tuple `(remaining, limit)`.

### fn `def _extract_premium_request_dimensions(` `priv` (L403-404)

### fn `async def login(self) -> str` (L584-614)
- @brief Execute login.
- @details Applies login logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {str} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`_resolve_provider_currency`|fn|priv|27-39|def _resolve_provider_currency(raw: dict, provider_name: ...|
|`CopilotDeviceFlow`|class|pub|40-132|class CopilotDeviceFlow|
|`CopilotDeviceFlow.CLIENT_ID`|var|pub|47||
|`CopilotDeviceFlow.SCOPES`|var|pub|48||
|`CopilotDeviceFlow.DEVICE_CODE_URL`|var|pub|50||
|`CopilotDeviceFlow.TOKEN_URL`|var|pub|51||
|`CopilotDeviceFlow.request_device_code`|fn|pub|53-79|async def request_device_code(self) -> dict[str, Any]|
|`CopilotDeviceFlow.poll_for_token`|fn|pub|80-132|async def poll_for_token(self, device_code: str, interval...|
|`CopilotCredentialStore`|class|pub|133-189|class CopilotCredentialStore|
|`CopilotCredentialStore.CONFIG_DIR`|var|pub|139||
|`CopilotCredentialStore.CREDS_FILE`|var|pub|140||
|`CopilotCredentialStore.CODEXBAR_CONFIG`|var|pub|141||
|`CopilotCredentialStore.load_token`|fn|pub|143-174|def load_token(self) -> str | None|
|`CopilotCredentialStore.save_token`|fn|pub|175-189|def save_token(self, token: str) -> None|
|`CopilotProvider`|class|pub|190-230|class CopilotProvider(BaseProvider)|
|`CopilotProvider.USAGE_URL`|var|pub|197||
|`CopilotProvider.EDITOR_VERSION`|var|pub|200||
|`CopilotProvider.PLUGIN_VERSION`|var|pub|201||
|`CopilotProvider.USER_AGENT`|var|pub|202||
|`CopilotProvider.API_VERSION`|var|pub|203||
|`CopilotProvider.__init__`|fn|priv|205-214|def __init__(self, token: str | None = None) -> None|
|`CopilotProvider.is_configured`|fn|pub|215-222|def is_configured(self) -> bool|
|`CopilotProvider.get_config_help`|fn|pub|223-230|def get_config_help(self) -> str|
|`fetch`|fn|pub|240-318|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|319-518|def _parse_response(self, data: dict, window: WindowPerio...|
|`_coerce_float`|fn|priv|338-352|def _coerce_float(value: Any) -> float | None|
|`_first_numeric`|fn|priv|353-368|def _first_numeric(snapshot: dict[str, Any], keys: tuple[...|
|`_get_snapshot`|fn|priv|369-377|def _get_snapshot(key_camel: str, key_snake: str) -> dict|
|`_extract_quota_data`|fn|priv|378-402|def _extract_quota_data(snapshot: dict) -> tuple[float | ...|
|`_extract_premium_request_dimensions`|fn|priv|403-404|def _extract_premium_request_dimensions(|
|`login`|fn|pub|584-614|async def login(self) -> str|


---

# geminiai.py | Python | 1045L | 48 symbols | 20 imports | 41 comments
> Path: `src/aibar/aibar/providers/geminiai.py`
- @brief GeminiAI provider with Google OAuth, Monitoring, and BigQuery billing integration.
- @details Implements OAuth credential persistence, token refresh, usage retrieval from
Cloud Monitoring and latest-available billing-period retrieval from BigQuery, then normalizes
results into AIBar provider result contracts.

## Imports
```
from __future__ import annotations
import asyncio
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast
from google.api_core.exceptions import GoogleAPICallError  # pyright: ignore[reportMissingImports]
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.cloud import bigquery  # pyright: ignore[reportAttributeAccessIssue]
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow  # pyright: ignore[reportMissingImports]
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from aibar.providers.base import (
from aibar.config import load_runtime_config
from aibar.config import load_runtime_config
from aibar.config import resolve_currency_symbol
```

## Definitions

- var `GEMINIAI_OAUTH_CLIENT_PATH = Path.home() / ".config" / "aibar" / "geminiai_oauth_client.json"` (L43)
- var `GEMINIAI_OAUTH_TOKEN_PATH = Path.home() / ".config" / "aibar" / "geminiai_oauth_token.json"` (L44)
- var `GEMINIAI_PROJECT_ID_ENV_VAR = "GEMINIAI_PROJECT_ID"` (L45)
- var `GEMINIAI_ACCESS_TOKEN_ENV_VAR = "GEMINIAI_OAUTH_ACCESS_TOKEN"` (L46)
- var `DEFAULT_BILLING_DATASET_ID = "billing_data"` (L47)
- var `BILLING_TABLE_PREFIX = "gcp_billing_export_v1_"` (L48)
### fn `def _to_rfc3339_utc(value: datetime) -> str` `priv` (L51-62)
- @brief Convert datetime to RFC3339 UTC string accepted by Google APIs.
- @details Normalizes timezone awareness and strips microseconds to produce stable API query timestamps.
- @param value {datetime} Input datetime value.
- @return {str} RFC3339 UTC timestamp (e.g. `2026-03-08T11:00:00Z`).

### fn `def _extract_http_status(error: HttpError) -> int` `priv` (L63-83)
- @brief Extract integer HTTP status from Google API HttpError.
- @details Returns `0` when status is unavailable to preserve deterministic error payload shape.
- @param error {HttpError} Google API exception.
- @return {int} HTTP status code or `0`.

### fn `def _extract_retry_after_seconds(error: HttpError) -> float` `priv` (L84-107)
- @brief Extract retry-after seconds from HttpError response headers.
- @details Reads `retry-after` case-insensitively and normalizes invalid values to `0.0`.
- @param error {HttpError} Google API exception.
- @return {float} Non-negative retry-after delay in seconds.

### fn `def _has_retry_after_header(error: HttpError) -> bool` `priv` (L108-124)
- @brief Detect Retry-After header presence in Google HttpError response.
- @details Evaluates case-insensitive `retry-after` header availability using `HttpError.resp.get(...)` access without parsing numeric values.
- @param error {HttpError} Google API exception.
- @return {bool} True when Retry-After header exists.

### fn `def _extract_google_api_status(error: GoogleAPICallError) -> int` `priv` (L125-145)
- @brief Extract HTTP-like status code from Google API Core exceptions.
- @details Normalizes exception `code` payloads to integer status values and returns `0` when status is unavailable.
- @param error {GoogleAPICallError} Google API Core exception.
- @return {int} Status code or `0`.

### fn `def _is_scope_insufficient_error(error: Exception) -> bool` `priv` (L146-169)
- @brief Determine whether exception payload indicates OAuth scope insufficiency.
- @details Matches Google API error reason `ACCESS_TOKEN_SCOPE_INSUFFICIENT` and equivalent human-readable messages.
- @param error {Exception} Exception to inspect.
- @return {bool} True when the error indicates insufficient OAuth scopes.

### fn `def _summarize_google_refresh_error(error: RefreshError) -> str` `priv` (L170-196)
- @brief Build compact diagnostic string from Google OAuth refresh failure payload.
- @details Extracts structured `response.error` and `response.error_description` fields when available, then appends fallback exception message to preserve actionable provider diagnostics for operators.
- @param error {RefreshError} OAuth refresh exception emitted by google-auth.
- @return {str} Stable diagnostic summary for user-facing authentication errors.

### class `class GeminiAIWindowRange` `@dataclass(frozen=True)` (L198-207)
- @brief Immutable time-range descriptor for one GeminiAI fetch window.
- @details Encodes start and end UTC timestamps used for Monitoring API queries.

### class `class GeminiAICredentialStore` (L208-407)
- @brief OAuth credential persistence and validation helper for GeminiAI.
- @details Manages client-secret JSON validation, token-file persistence, and interactive InstalledAppFlow authorization.
- fn `def __init__(` `priv` (L215-218)
  - @brief OAuth credential persistence and validation helper for GeminiAI.
  - @details Manages client-secret JSON validation, token-file persistence, and
interactive InstalledAppFlow authorization.
- fn `def _ensure_config_dir(self) -> None` `priv` (L229-236)
  - @brief Initialize credential store with optional custom file paths.
  - @brief Create parent directories for OAuth files when missing.
  - @param client_config_path {Path | None} Optional OAuth client config path.
  - @param token_path {Path | None} Optional OAuth token path.
  - @return {None} Function return value.
  - @return {None} Function return value.
- fn `def has_client_config(self) -> bool` (L237-243)
  - @brief Check whether GeminiAI client config JSON exists.
  - @return {bool} True when client config file exists.
- fn `def has_authorized_credentials(self) -> bool` (L244-254)
  - @brief Check whether GeminiAI authorized token material exists.
  - @details Environment access-token override is treated as configured token material.
  - @return {bool} True when token file or env token is available.
- fn `def validate_client_config(self, payload: dict[str, Any]) -> dict[str, Any]` (L255-284)
  - @brief Validate Google InstalledApp OAuth client-secret payload.
  - @details Enforces required `installed` section fields used by `InstalledAppFlow.from_client_config`.
  - @param payload {dict[str, Any]} Decoded JSON payload to validate.
  - @return {dict[str, Any]} Normalized payload.
  - @throws {ValueError} When required fields are missing or malformed.
- fn `def save_client_config(self, payload: dict[str, Any]) -> None` (L285-297)
  - @brief Persist validated OAuth client config JSON to disk.
  - @param payload {dict[str, Any]} Validated client payload.
  - @return {None} Function return value.
- fn `def load_client_config(self) -> dict[str, Any]` (L298-316)
  - @brief Load and validate persisted OAuth client config JSON.
  - @return {dict[str, Any]} Validated OAuth client payload.
  - @throws {FileNotFoundError} When client config file is missing.
  - @throws {ValueError} When payload is invalid JSON or fails validation.
- fn `def extract_project_id(self, payload: dict[str, Any]) -> str | None` (L317-330)
  - @brief Extract project_id from validated OAuth payload.
  - @param payload {dict[str, Any]} Validated OAuth payload.
  - @return {str | None} Project identifier or None when absent.
- fn `def save_authorized_credentials(self, credentials: Credentials) -> None` (L331-340)
  - @brief Persist authorized-user OAuth credentials JSON.
  - @param credentials {Credentials} Google OAuth credentials object.
  - @return {None} Function return value.
- fn `def authorize_interactively(` (L341-343)
- fn `def load_access_token(self) -> str | None` (L359-376)
  - @brief Execute OAuth browser flow and persist refresh-capable credentials.
  - @brief Load access token from env override or token file.
  - @details Uses InstalledAppFlow local-server flow (`http://localhost`) and
saves authorized-user token JSON to disk.
  - @param scopes {tuple[str, ...]} OAuth scopes requested during authorization.
  - @return {Credentials} Authorized credentials.
  - @return {str | None} Access token or None when unavailable.
  - @throws {ValueError} When client config is invalid.
- fn `def load_credentials(` (L377-379)

### class `class GeminiAIProvider(BaseProvider)` : BaseProvider (L414-490)
- @brief GeminiAI usage provider backed by Monitoring and BigQuery APIs.
- @details Retrieves Generative Language API usage counters and status telemetry from Cloud Monitoring, retrieves latest-available billing-period costs from BigQuery export, then maps data into AIBar `ProviderResult` models.
- var `SERVICE_FILTER = 'resource.labels.service="generativelanguage.googleapis.com"'` (L424)
  - @brief GeminiAI usage provider backed by Monitoring and BigQuery APIs.
  - @details Retrieves Generative Language API usage counters and status telemetry
from Cloud Monitoring, retrieves latest-available billing-period costs from BigQuery export,
then maps data into AIBar `ProviderResult` models.
- var `REQUEST_COUNT_FILTER = REQUEST_COUNT_FILTERS[0]` (L434)
- var `LATENCY_FILTER = (` (L450)
- var `ERROR_FILTER = (` (L453)
- fn `def __init__(` `priv` (L459-462)
- fn `def is_configured(self) -> bool` (L473-482)
  - @brief Initialize GeminiAI provider with optional overrides.
  - @brief Check whether GeminiAI provider has required auth and project metadata.
  - @param credential_store {GeminiAICredentialStore | None} Optional credential store.
  - @param project_id {str | None} Optional project id override.
  - @return {None} Function return value.
  - @return {bool} True when project id and OAuth token material are available.
- fn `def get_config_help(self) -> str` (L483-490)
  - @brief Return setup guidance for GeminiAI OAuth configuration.
  - @return {str} Provider-specific setup instructions.

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L499-526)
- @brief Fetch GeminiAI monitoring usage metrics for one window.
- @details Executes synchronous Google API calls in a worker thread and returns normalized provider metrics. HTTP 429 responses are normalized as rate-limit provider error payloads with retry-after metadata.
- @param window {WindowPeriod} Requested window period.
- @return {ProviderResult} Provider result payload.
- @throws {AuthenticationError} When OAuth credentials are invalid.

### fn `def _fetch_sync(self, window: WindowPeriod) -> ProviderResult` `priv` (L527-698)
- @brief Execute blocking Google API retrieval flow for GeminiAI metrics.
- @param window {WindowPeriod} Requested window period.
- @return {ProviderResult} Normalized provider result.
- @throws {AuthenticationError} When credentials are missing/invalid.
- @throws {ProviderError} On non-auth API failures.

### fn `def _build_window_range(self, window: WindowPeriod) -> GeminiAIWindowRange` `priv` (L699-717)
- @brief Build current-month UTC interval used for Monitoring queries.
- @details Uses `[UTC month start, current UTC time]` to align Monitoring usage aggregation with current-month GeminiAI billing semantics.
- @param window {WindowPeriod} Requested window period (ignored by interval policy).
- @return {GeminiAIWindowRange} Start/end UTC timestamps.
- @satisfies REQ-098

### fn `def _resolve_project_id(self) -> str | None` `priv` (L718-739)
- @brief Resolve project id from override, env, runtime config, or client JSON.
- @return {str | None} Project id or None when unresolved.

### fn `def _resolve_billing_dataset(self) -> str` `priv` (L740-756)
- @brief Resolve billing dataset id from runtime configuration.
- @details Uses `RuntimeConfig.billing_data` and falls back to `DEFAULT_BILLING_DATASET_ID` when configuration is empty.
- @return {str} BigQuery billing dataset id.
- @satisfies REQ-005
- @satisfies REQ-064

### fn `def _build_monitoring_service(self, credentials: Credentials) -> Any` `priv` (L757-764)
- @brief Build Google Cloud Monitoring API client.
- @param credentials {Credentials} OAuth credentials.
- @return {Any} Monitoring service client.

### fn `def _build_bigquery_client(` `priv` (L765-768)

### fn `def _discover_billing_table_id(` `priv` (L780-784)
- @brief Build BigQuery client for GeminiAI billing export queries.
- @param credentials {Credentials} OAuth credentials with BigQuery read scope.
- @param project_id {str} Google Cloud project id.
- @return {bigquery.Client} BigQuery API client.
- @satisfies REQ-056
- @satisfies REQ-065

### fn `def _query_current_month_billing_cost(` `priv` (L810-815)
- @brief Discover billing export table id in configured billing dataset.
- @details Lists dataset tables and selects the first lexicographically sorted
id that starts with `gcp_billing_export_v1_`.
- @param bigquery_client {bigquery.Client} BigQuery client.
- @param project_id {str} Google Cloud project id.
- @param dataset_id {str} BigQuery dataset id configured by setup.
- @return {str} Billing export table id.
- @throws {ProviderError} When billing export table is unavailable.
- @satisfies REQ-064

### fn `def _coerce_float(self, value: Any) -> float` `priv` (L891-910)
- @brief Query latest-available invoice-month billing costs grouped by service.
- @brief Convert numeric BigQuery row field values to float.
- @details Uses explicit projection and latest invoice-month selection
(`MAX(invoice.month)`), with fallback to current-month `usage_start_time`
filter when invoice month data is unavailable.
- @param bigquery_client {bigquery.Client} BigQuery client.
- @param project_id {str} Google Cloud project id.
- @param billing_dataset {str} BigQuery dataset id configured by setup.
- @param table_id {str} Billing export table id.
- @param value {Any} Numeric row value.
- @return {tuple[list[dict[str, float | str]], float]} Per-service aggregates and
total net monthly cost.
- @return {float} Parsed float value or `0.0` when value is invalid.
- @satisfies REQ-057
- @satisfies REQ-065

### fn `def _query_monitoring_metric(` `priv` (L911-918)

### fn `def _sum_time_series_values(self, response: dict[str, Any]) -> float | None` `priv` (L957-1009)
- @brief Query Monitoring time-series metric and aggregate point values.
- @brief Sum numeric point values in Monitoring `timeSeries` payload.
- @details Returns None when metric is unavailable and `allow_missing=True`.
- @param monitoring_service {Any} Monitoring client.
- @param project_id {str} Google Cloud project id.
- @param metric_filter {str} Monitoring filter expression.
- @param start_time {datetime} Query range start.
- @param end_time {datetime} Query range end.
- @param allow_missing {bool} Allow 400/404 as non-fatal missing metric.
- @param response {dict[str, Any]} Monitoring API response.
- @return {tuple[float | None, dict[str, Any]]} Aggregated value and raw response.
- @return {float | None} Aggregated numeric value or None when no points exist.
- @throws {HttpError} For non-missing API errors.

### fn `def _build_metrics(` `priv` (L1010-1015)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`GEMINIAI_OAUTH_CLIENT_PATH`|var|pub|43||
|`GEMINIAI_OAUTH_TOKEN_PATH`|var|pub|44||
|`GEMINIAI_PROJECT_ID_ENV_VAR`|var|pub|45||
|`GEMINIAI_ACCESS_TOKEN_ENV_VAR`|var|pub|46||
|`DEFAULT_BILLING_DATASET_ID`|var|pub|47||
|`BILLING_TABLE_PREFIX`|var|pub|48||
|`_to_rfc3339_utc`|fn|priv|51-62|def _to_rfc3339_utc(value: datetime) -> str|
|`_extract_http_status`|fn|priv|63-83|def _extract_http_status(error: HttpError) -> int|
|`_extract_retry_after_seconds`|fn|priv|84-107|def _extract_retry_after_seconds(error: HttpError) -> float|
|`_has_retry_after_header`|fn|priv|108-124|def _has_retry_after_header(error: HttpError) -> bool|
|`_extract_google_api_status`|fn|priv|125-145|def _extract_google_api_status(error: GoogleAPICallError)...|
|`_is_scope_insufficient_error`|fn|priv|146-169|def _is_scope_insufficient_error(error: Exception) -> bool|
|`_summarize_google_refresh_error`|fn|priv|170-196|def _summarize_google_refresh_error(error: RefreshError) ...|
|`GeminiAIWindowRange`|class|pub|198-207|class GeminiAIWindowRange|
|`GeminiAICredentialStore`|class|pub|208-407|class GeminiAICredentialStore|
|`GeminiAICredentialStore.__init__`|fn|priv|215-218|def __init__(|
|`GeminiAICredentialStore._ensure_config_dir`|fn|priv|229-236|def _ensure_config_dir(self) -> None|
|`GeminiAICredentialStore.has_client_config`|fn|pub|237-243|def has_client_config(self) -> bool|
|`GeminiAICredentialStore.has_authorized_credentials`|fn|pub|244-254|def has_authorized_credentials(self) -> bool|
|`GeminiAICredentialStore.validate_client_config`|fn|pub|255-284|def validate_client_config(self, payload: dict[str, Any])...|
|`GeminiAICredentialStore.save_client_config`|fn|pub|285-297|def save_client_config(self, payload: dict[str, Any]) -> ...|
|`GeminiAICredentialStore.load_client_config`|fn|pub|298-316|def load_client_config(self) -> dict[str, Any]|
|`GeminiAICredentialStore.extract_project_id`|fn|pub|317-330|def extract_project_id(self, payload: dict[str, Any]) -> ...|
|`GeminiAICredentialStore.save_authorized_credentials`|fn|pub|331-340|def save_authorized_credentials(self, credentials: Creden...|
|`GeminiAICredentialStore.authorize_interactively`|fn|pub|341-343|def authorize_interactively(|
|`GeminiAICredentialStore.load_access_token`|fn|pub|359-376|def load_access_token(self) -> str | None|
|`GeminiAICredentialStore.load_credentials`|fn|pub|377-379|def load_credentials(|
|`GeminiAIProvider`|class|pub|414-490|class GeminiAIProvider(BaseProvider)|
|`GeminiAIProvider.SERVICE_FILTER`|var|pub|424||
|`GeminiAIProvider.REQUEST_COUNT_FILTER`|var|pub|434||
|`GeminiAIProvider.LATENCY_FILTER`|var|pub|450||
|`GeminiAIProvider.ERROR_FILTER`|var|pub|453||
|`GeminiAIProvider.__init__`|fn|priv|459-462|def __init__(|
|`GeminiAIProvider.is_configured`|fn|pub|473-482|def is_configured(self) -> bool|
|`GeminiAIProvider.get_config_help`|fn|pub|483-490|def get_config_help(self) -> str|
|`fetch`|fn|pub|499-526|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_fetch_sync`|fn|priv|527-698|def _fetch_sync(self, window: WindowPeriod) -> ProviderRe...|
|`_build_window_range`|fn|priv|699-717|def _build_window_range(self, window: WindowPeriod) -> Ge...|
|`_resolve_project_id`|fn|priv|718-739|def _resolve_project_id(self) -> str | None|
|`_resolve_billing_dataset`|fn|priv|740-756|def _resolve_billing_dataset(self) -> str|
|`_build_monitoring_service`|fn|priv|757-764|def _build_monitoring_service(self, credentials: Credenti...|
|`_build_bigquery_client`|fn|priv|765-768|def _build_bigquery_client(|
|`_discover_billing_table_id`|fn|priv|780-784|def _discover_billing_table_id(|
|`_query_current_month_billing_cost`|fn|priv|810-815|def _query_current_month_billing_cost(|
|`_coerce_float`|fn|priv|891-910|def _coerce_float(self, value: Any) -> float|
|`_query_monitoring_metric`|fn|priv|911-918|def _query_monitoring_metric(|
|`_sum_time_series_values`|fn|priv|957-1009|def _sum_time_series_values(self, response: dict[str, Any...|
|`_build_metrics`|fn|priv|1010-1015|def _build_metrics(|


---

# openai_usage.py | Python | 246L | 12 symbols | 8 imports | 16 comments
> Path: `src/aibar/aibar/providers/openai_usage.py`
- @brief OpenAI organization usage provider.
- @details Retrieves organization completion usage and cost buckets, aggregates counters, and maps response data to normalized provider metrics.

## Imports
```
import asyncio
from datetime import datetime, timedelta, timezone
import httpx
from aibar.providers.base import (
from aibar.config import config
from aibar.config import get_api_call_timeout_seconds
from aibar.config import load_runtime_config
from aibar.config import resolve_currency_symbol
```

## Definitions

### class `class OpenAIUsageProvider(BaseProvider)` : BaseProvider (L23-61)
- @brief Define open a i usage provider component.
- @details Encapsulates open a i usage provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `BASE_URL = "https://api.openai.com/v1/organization"` (L30)
  - @brief Define open a i usage provider component.
  - @details Encapsulates open a i usage provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `TOKEN_ENV_VAR = "OPENAI_ADMIN_KEY"` (L31)
- fn `def __init__(self, api_key: str | None = None) -> None` `priv` (L33-45)
  - @brief Execute init.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param api_key {str | None} Input parameter `api_key`.
  - @return {None} Function return value.
- fn `def is_configured(self) -> bool` (L46-53)
  - @brief Execute is configured.
  - @details Applies is configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {bool} Function return value.
- fn `def get_config_help(self) -> str` (L54-61)
  - @brief Execute get config help.
  - @details Applies get config help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str} Function return value.

### fn `def _get_time_range(self, window: WindowPeriod) -> tuple[int, int]` `priv` (L68-79)
- @brief Execute get time range.
- @details Applies get time range logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {WindowPeriod} Input parameter `window`.
- @return {tuple[int, int]} Function return value.

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L80-119)
- @brief Execute fetch.
- @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `async def _fetch_usage(` `priv` (L120-125)

### fn `async def _fetch_costs(` `priv` (L148-153)
- @brief Execute fetch usage.
- @details Applies fetch usage logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param client {httpx.AsyncClient} Input parameter `client`.
- @param headers {dict} Input parameter `headers`.
- @param start_time {int} Input parameter `start_time`.
- @param end_time {int} Input parameter `end_time`.
- @return {dict} Function return value.

### fn `def _check_response(self, response: httpx.Response) -> None` `priv` (L176-192)
- @brief Execute fetch costs.
- @brief Execute check response.
- @details Applies fetch costs logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @details Applies check response logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param client {httpx.AsyncClient} Input parameter `client`.
- @param headers {dict} Input parameter `headers`.
- @param start_time {int} Input parameter `start_time`.
- @param end_time {int} Input parameter `end_time`.
- @param response {httpx.Response} Input parameter `response`.
- @return {dict} Function return value.
- @return {None} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _build_result(` `priv` (L193-194)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`OpenAIUsageProvider`|class|pub|23-61|class OpenAIUsageProvider(BaseProvider)|
|`OpenAIUsageProvider.BASE_URL`|var|pub|30||
|`OpenAIUsageProvider.TOKEN_ENV_VAR`|var|pub|31||
|`OpenAIUsageProvider.__init__`|fn|priv|33-45|def __init__(self, api_key: str | None = None) -> None|
|`OpenAIUsageProvider.is_configured`|fn|pub|46-53|def is_configured(self) -> bool|
|`OpenAIUsageProvider.get_config_help`|fn|pub|54-61|def get_config_help(self) -> str|
|`_get_time_range`|fn|priv|68-79|def _get_time_range(self, window: WindowPeriod) -> tuple[...|
|`fetch`|fn|pub|80-119|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_fetch_usage`|fn|priv|120-125|async def _fetch_usage(|
|`_fetch_costs`|fn|priv|148-153|async def _fetch_costs(|
|`_check_response`|fn|priv|176-192|def _check_response(self, response: httpx.Response) -> None|
|`_build_result`|fn|priv|193-194|def _build_result(|


---

# openrouter.py | Python | 216L | 11 symbols | 5 imports | 11 comments
> Path: `src/aibar/aibar/providers/openrouter.py`
- @brief OpenRouter key usage and credit provider.
- @details Fetches key usage snapshots and quota limits, then transforms provider payloads into normalized cost and quota metrics.

## Imports
```
import httpx
from aibar.providers.base import (
from aibar.config import config
from aibar.config import get_api_call_timeout_seconds
from aibar.config import resolve_currency_symbol
```

## Definitions

### class `class OpenRouterUsageProvider(BaseProvider)` : BaseProvider (L20-58)
- @brief Define open router usage provider component.
- @details Encapsulates open router usage provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `USAGE_URL = "https://openrouter.ai/api/v1/key"` (L27)
  - @brief Define open router usage provider component.
  - @details Encapsulates open router usage provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `TOKEN_ENV_VAR = "OPENROUTER_API_KEY"` (L28)
- fn `def __init__(self, api_key: str | None = None) -> None` `priv` (L30-42)
  - @brief Execute init.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param api_key {str | None} Input parameter `api_key`.
  - @return {None} Function return value.
- fn `def is_configured(self) -> bool` (L43-50)
  - @brief Execute is configured.
  - @details Applies is configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {bool} Function return value.
- fn `def get_config_help(self) -> str` (L51-58)
  - @brief Execute get config help.
  - @details Applies get config help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str} Function return value.

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L64-139)
- @brief Execute fetch.
- @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L140-175)
- @brief Execute parse response.
- @details Applies parse response logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param data {dict} Input parameter `data`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.
- @satisfies REQ-050

### fn `def _get_usage(self, payload: dict, window: WindowPeriod) -> float` `priv` (L176-189)
- @brief Execute get usage.
- @details Applies get usage logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param payload {dict} Input parameter `payload`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {float} Function return value.

### fn `def _get_byok_usage(self, payload: dict, window: WindowPeriod) -> float` `priv` (L190-203)
- @brief Execute get byok usage.
- @details Applies get byok usage logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param payload {dict} Input parameter `payload`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {float} Function return value.

### fn `def _to_float(self, value: float | int | None) -> float` `priv` (L204-216)
- @brief Execute to float.
- @details Applies to float logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param value {float | int | None} Input parameter `value`.
- @return {float} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`OpenRouterUsageProvider`|class|pub|20-58|class OpenRouterUsageProvider(BaseProvider)|
|`OpenRouterUsageProvider.USAGE_URL`|var|pub|27||
|`OpenRouterUsageProvider.TOKEN_ENV_VAR`|var|pub|28||
|`OpenRouterUsageProvider.__init__`|fn|priv|30-42|def __init__(self, api_key: str | None = None) -> None|
|`OpenRouterUsageProvider.is_configured`|fn|pub|43-50|def is_configured(self) -> bool|
|`OpenRouterUsageProvider.get_config_help`|fn|pub|51-58|def get_config_help(self) -> str|
|`fetch`|fn|pub|64-139|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|140-175|def _parse_response(self, data: dict, window: WindowPerio...|
|`_get_usage`|fn|priv|176-189|def _get_usage(self, payload: dict, window: WindowPeriod)...|
|`_get_byok_usage`|fn|priv|190-203|def _get_byok_usage(self, payload: dict, window: WindowPe...|
|`_to_float`|fn|priv|204-216|def _to_float(self, value: float | int | None) -> float|

