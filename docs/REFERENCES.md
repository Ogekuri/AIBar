# Files Structure
```
.
├── scripts
│   ├── aibar.sh
│   ├── claude_token_refresh.sh
│   └── test-gnome-extension.sh
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

# aibar.sh | Shell | 21L | 0 symbols | 0 imports | 11 comments
> Path: `scripts/aibar.sh`


---

# claude_token_refresh.sh | Shell | 174L | 12 symbols | 0 imports | 35 comments
> Path: `scripts/claude_token_refresh.sh`

## Definitions

- var `CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/aibar"` (L20)
- var `PID_FILE="$CONFIG_DIR/claude_token_refresh.pid"` (L21)
- var `LOG_FILE="$CONFIG_DIR/claude_token_refresh.log"` (L22)
- var `INTERVAL="${AIBAR_CLAUDE_REFRESH_INTERVAL_SECONDS:-1800}"` (L23)
- fn `log() {` (L29)
- fn `do_refresh() {` (L43)
- fn `run_loop() {` (L65)
- fn `is_running() {` (L75)
- fn `start_daemon() {` (L87)
- fn `stop_daemon() {` (L101)
- fn `show_status() {` (L122)
- fn `show_usage() {` (L136)
## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`CONFIG_DIR`|var||20||
|`PID_FILE`|var||21||
|`LOG_FILE`|var||22||
|`INTERVAL`|var||23||
|`log`|fn||29|log()|
|`do_refresh`|fn||43|do_refresh()|
|`run_loop`|fn||65|run_loop()|
|`is_running`|fn||75|is_running()|
|`start_daemon`|fn||87|start_daemon()|
|`stop_daemon`|fn||101|stop_daemon()|
|`show_status`|fn||122|show_status()|
|`show_usage`|fn||136|show_usage()|


---

# test-gnome-extension.sh | Shell | 13L | 0 symbols | 0 imports | 8 comments
> Path: `scripts/test-gnome-extension.sh`


---

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

# cli.py | Python | 3560L | 99 symbols | 30 imports | 113 comments
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

### class `class RetrievalPipelineOutput` `@dataclass(frozen=True)` (L136-165)
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

### class `class StartupReleaseCheckResponse` `@dataclass(frozen=True)` (L167-186)
- @brief Represent one startup GitHub release-check execution result.
- @details Encodes normalized response state for startup preflight control-flow. `latest_version` is populated only on successful metadata retrieval. `status_code`, `error_message`, and `retry_after_seconds` carry normalized failure metadata used by 429 idle-time expansion and bright-red diagnostics.
- @note Immutable dataclass to keep preflight decisions deterministic.
- @satisfies REQ-070
- @satisfies REQ-073
- @satisfies REQ-074
- @satisfies REQ-075

### fn `def _startup_idle_state_path() -> Path` `priv` (L187-196)
- @brief Resolve startup update idle-state JSON path.
- @details Builds `~/.cache/aibar/check_version_idle-time.json` in user scope.
- @return {Path} Absolute path for startup idle-state persistence.
- @satisfies CTN-013

### fn `def _startup_human_timestamp(epoch_seconds: int) -> str` `priv` (L197-209)
- @brief Convert epoch seconds to UTC ISO-8601 timestamp text.
- @details Normalizes negative input to zero and emits timezone-aware UTC values so startup idle-state JSON remains machine-parseable and stable.
- @param epoch_seconds {int} Epoch timestamp in seconds.
- @return {str} UTC ISO-8601 timestamp string.
- @satisfies CTN-013

### fn `def _startup_parse_int(value: object, default: int = 0) -> int` `priv` (L210-227)
- @brief Parse integer-like values for startup idle-state normalization.
- @details Supports int, float, and numeric strings; invalid values return provided default. Parsed values are clamped to non-negative integers.
- @param value {object} Raw decoded value from JSON or headers.
- @param default {int} Fallback integer when parsing fails.
- @return {int} Non-negative parsed integer or fallback default.

### fn `def _load_startup_idle_state() -> dict[str, object] | None` `priv` (L228-247)
- @brief Load startup update idle-state JSON from disk.
- @details Reads `~/.cache/aibar/check_version_idle-time.json` and returns decoded JSON object when valid. Corrupt, missing, or unreadable files normalize to None.
- @return {dict[str, object] | None} Parsed idle-state mapping or None.
- @satisfies CTN-013

### fn `def _startup_idle_epochs(state: dict[str, object] | None) -> tuple[int, int]` `priv` (L248-269)
- @brief Extract normalized startup idle-state epoch timestamps.
- @details Reads `last_success_at_epoch` and `idle_until_epoch` from decoded state object and normalizes missing/invalid values to zero.
- @param state {dict[str, object] | None} Decoded startup idle-state mapping.
- @return {tuple[int, int]} Tuple `(last_success_epoch, idle_until_epoch)`.
- @satisfies CTN-013

### fn `def _save_startup_idle_state(last_success_epoch: int, idle_until_epoch: int) -> None` `priv` (L270-300)
- @brief Persist startup update idle-state JSON.
- @details Writes epoch and UTC human-readable values for last successful startup release check and idle-disable-until timestamp to `~/.cache/aibar/check_version_idle-time.json`.
- @param last_success_epoch {int} Last successful startup check epoch.
- @param idle_until_epoch {int} Startup idle gate expiry epoch.
- @return {None} Function return value.
- @throws {OSError} Propagates filesystem write failures.
- @satisfies CTN-013
- @satisfies REQ-072

### fn `def _cleanup_startup_idle_state_artifacts() -> int` `priv` (L301-326)
- @brief Remove startup update idle-state artifacts for Linux uninstall.
- @details Deletes `~/.cache/aibar/check_version_idle-time.json` when present, then removes `~/.cache/aibar/` recursively when present. Emits bright-red diagnostics and returns non-zero on filesystem failures.
- @return {int} Zero on success; one when cleanup fails.
- @satisfies REQ-077

### fn `def _emit_startup_preflight_message(message: str, color_code: str, err: bool = False) -> None` `priv` (L327-341)
- @brief Emit colorized startup preflight diagnostics.
- @details Wraps message text with ANSI bright color escape sequences so update availability notices and failures are visually distinct in terminal output.
- @param message {str} Rendered diagnostic message text.
- @param color_code {str} ANSI SGR color escape prefix.
- @param err {bool} When true, write to stderr stream.
- @return {None} Function return value.
- @satisfies REQ-073
- @satisfies REQ-074

### fn `def _parse_retry_after_header(retry_after_raw: str | None) -> int` `priv` (L342-366)
- @brief Parse HTTP Retry-After header to delay seconds.
- @details Supports integer-second values and HTTP-date formats. Date values are converted to seconds relative to current UTC time and clamped to zero.
- @param retry_after_raw {str | None} Retry-After header value.
- @return {int} Non-negative delay seconds.
- @satisfies REQ-075

### fn `def _normalize_release_version(raw_version: object) -> str | None` `priv` (L367-383)
- @brief Normalize release tag text extracted from GitHub API payload.
- @details Accepts string-like values, trims whitespace, and returns None for empty/invalid payload values.
- @param raw_version {object} Decoded `tag_name` value from release JSON.
- @return {str | None} Normalized release version string.
- @satisfies REQ-073

### fn `def _fetch_startup_latest_release() -> StartupReleaseCheckResponse` `priv` (L384-438)
- @brief Fetch latest GitHub release metadata for startup preflight.
- @details Executes one HTTP request to the canonical releases/latest endpoint with hardcoded timeout. Success returns normalized latest version tag. Failures return status/error metadata and parsed retry-after delay.
- @return {StartupReleaseCheckResponse} Normalized startup release-check result.
- @satisfies CTN-011
- @satisfies CTN-012
- @satisfies REQ-073
- @satisfies REQ-074
- @satisfies REQ-075

### fn `def _parse_version_triplet(version_text: str) -> tuple[int, int, int] | None` `priv` (L439-457)
- @brief Parse semantic version tuple from version text.
- @details Accepts optional `v` prefix and optional suffix metadata. Returns first `major.minor.patch` triplet or None when parsing fails.
- @param version_text {str} Raw version string.
- @return {tuple[int, int, int] | None} Parsed semantic version tuple.
- @satisfies REQ-073

### fn `def _is_newer_release(installed_version: str, latest_version: str) -> bool` `priv` (L458-474)
- @brief Compare installed and latest release semantic versions.
- @details Uses normalized `major.minor.patch` tuples. Invalid version formats disable upgrade notice emission to avoid false positives.
- @param installed_version {str} Installed program version text.
- @param latest_version {str} Latest release version text.
- @return {bool} True when latest release is newer than installed version.
- @satisfies REQ-073

### fn `def _run_startup_update_preflight() -> None` `priv` (L475-542)
- @brief Execute startup update-check preflight with idle-time gating.
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

### fn `def _execute_lifecycle_subprocess(command: list[str]) -> int` `priv` (L543-565)
- @brief Execute lifecycle subprocess command for upgrade/uninstall options.
- @details Runs provided command via `subprocess.run` and returns subprocess exit code. Command execution failures return non-zero status with red error.
- @param command {list[str]} Lifecycle command argv.
- @return {int} Subprocess exit code.
- @satisfies CTN-015
- @satisfies REQ-076
- @satisfies REQ-077

### fn `def _is_linux_runtime() -> bool` `priv` (L566-578)
- @brief Determine whether lifecycle subprocess execution is allowed.
- @details Returns true only for Linux runtimes. Lifecycle subprocesses for `--upgrade` and `--uninstall` are Linux-only and must be skipped elsewhere.
- @return {bool} True when current runtime platform is Linux.
- @satisfies REQ-076
- @satisfies REQ-077
- @satisfies REQ-088

### fn `def _emit_non_linux_lifecycle_guidance(option_name: str, command: Sequence[str]) -> int` `priv` (L579-605)
- @brief Emit manual lifecycle command guidance for non-Linux platforms.
- @details Builds one deterministic warning message containing detected operating-system label and exact manual command text, then emits it through startup preflight styled diagnostics with stderr routing.
- @param option_name {str} Lifecycle option token (`--upgrade` or `--uninstall`).
- @param command {Sequence[str]} Lifecycle command argv to present as manual guidance.
- @return {int} Deterministic non-zero exit code indicating command was not executed.
- @satisfies CTN-015
- @satisfies REQ-088
- @satisfies REQ-089

### fn `def _handle_upgrade_option(` `priv` (L606-607)

### fn `def _handle_uninstall_option(` `priv` (L636-637)
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

### fn `def _handle_version_option(` `priv` (L670-671)
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

### class `class StartupPreflightGroup(click.Group)` : click.Group (L690-753)
- @brief Handle eager `--version` and `--ver` option callback.
- @brief Click group subclass that enforces startup preflight ordering and preserves epilog formatting.
- @details Prints installed package version and exits before command dispatch
when either version flag is present.
- @details Executes startup update-check preflight before Click argument parsing and command dispatch. This guarantees preflight execution even when invocation later fails due to invalid arguments. Overrides epilog rendering to preserve multi-line example formatting without text wrapping.
- @param ctx {click.Context} Active Click context.
- @param param {click.Parameter} Option metadata (unused).
- @param value {bool} Parsed version-option flag value.
- @return {None} Function return value.
- @satisfies REQ-078
- @satisfies REQ-070, REQ-068
- fn `def format_epilog(` (L700-703)
  - @brief Click group subclass that enforces startup preflight ordering and preserves epilog formatting.
  - @details Executes startup update-check preflight before Click argument
parsing and command dispatch. This guarantees preflight execution even when
invocation later fails due to invalid arguments. Overrides epilog rendering
to preserve multi-line example formatting without text wrapping.
  - @satisfies REQ-070, REQ-068
- fn `def main(` (L720-727)
  - @brief Render epilog text preserving explicit line breaks.
  - @details Writes each epilog line verbatim to the help formatter,
bypassing Click's default text-wrapping behavior that collapses
multi-line examples into a single paragraph.
  - @param ctx {click.Context} Click invocation context.
  - @param formatter {click.HelpFormatter} Help output formatter instance.
  - @return {None} Function return value.
  - @satisfies REQ-068

### fn `def _normalize_utc(value: datetime) -> datetime` `priv` (L754-766)
- @brief Normalize datetime values to timezone-aware UTC instances.
- @details Ensures consistent timestamp arithmetic for idle-time persistence and refresh-delay computations when source datetimes are naive or non-UTC.
- @param value {datetime} Source datetime to normalize.
- @return {datetime} Timezone-aware UTC datetime.

### fn `def _format_local_datetime(value: datetime) -> str` `priv` (L767-779)
- @brief Format one datetime in local timezone with `%Y-%m-%d %H:%M`.
- @details Normalizes source datetime to UTC, projects it to runtime local timezone, and emits minute-precision text for CLI freshness labels.
- @param value {datetime} Source datetime to format.
- @return {str} Local timezone datetime string.
- @satisfies REQ-084

### fn `def _epoch_to_utc_datetime(epoch_seconds: int) -> datetime` `priv` (L780-788)
- @brief Convert epoch-seconds to timezone-aware UTC datetime.
- @param epoch_seconds {int} Epoch timestamp in seconds.
- @return {datetime} UTC datetime from epoch.

### fn `def _build_freshness_line(` `priv` (L789-791)

### fn `def _apply_api_call_delay(throttle_state: dict[str, float | int] | None) -> None` `priv` (L816-845)
- @brief Build `Updated/Next` freshness line for CLI panel rendering.
- @brief Enforce minimum spacing between consecutive provider API calls.
- @details Uses provider idle-time state when available (`last_success_timestamp`,
`idle_until_timestamp`) and falls back to payload `updated_at` plus runtime
interval fallback (`60s`) when idle-time state is unavailable.
- @details Uses monotonic clock values in `throttle_state` to sleep before a live API request when elapsed time is below configured delay.
- @param result {ProviderResult} Provider result carrying fallback `updated_at`.
- @param freshness_state {IdleTimeState | None} Provider idle-time state.
- @param throttle_state {dict[str, float | int] | None} Mutable state containing `delay_milliseconds` and `last_call_started`.
- @return {str} Deterministic `Updated: ..., Next: ...` label.
- @return {None} Function return value.
- @satisfies REQ-084
- @satisfies REQ-040

### fn `def _coerce_retry_after_seconds(value: object) -> int | None` `priv` (L846-866)
- @brief Normalize retry-after metadata to positive integer seconds.
- @details Accepts integer/float/string payload values and converts them to integer seconds; non-numeric, invalid, and non-positive values return None.
- @param value {object} Retry-after candidate value.
- @return {int | None} Positive retry-after seconds or None when unavailable.
- @satisfies REQ-037
- @satisfies REQ-041

### fn `def _extract_retry_after_seconds(result: ProviderResult) -> int` `priv` (L867-881)
- @brief Extract normalized retry-after seconds from provider error payload.
- @details Reads `raw.retry_after_seconds` and clamps to non-negative integer seconds. Invalid or missing values normalize to zero.
- @param result {ProviderResult} Provider result to inspect.
- @return {int} Non-negative retry-after delay in seconds.
- @satisfies REQ-041

### fn `def _is_http_429_result(result: ProviderResult) -> bool` `priv` (L882-892)
- @brief Check whether result payload represents HTTP 429 rate limiting.
- @details Uses normalized raw payload marker `status_code == 429`.
- @param result {ProviderResult} Provider result to classify.
- @return {bool} True when result indicates HTTP 429.
- @satisfies REQ-041

### fn `def _serialize_results_payload(` `priv` (L893-894)

### fn `def _empty_cache_document() -> dict[str, object]` `priv` (L908-922)
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

### fn `def _normalize_cache_document(cache_document: dict[str, object] | None) -> dict[str, object]` `priv` (L923-944)
- @brief Normalize decoded cache payload to canonical sectioned schema.
- @details Accepts decoded cache document and enforces object-typed `payload` and `status` sections. Missing or invalid sections normalize to empty objects.
- @param cache_document {dict[str, object] | None} Decoded cache payload from disk.
- @return {dict[str, object]} Canonical cache document with `payload`/`status`.
- @satisfies CTN-004
- @satisfies REQ-003

### fn `def _cache_payload_section(cache_document: dict[str, object]) -> dict[str, object]` `priv` (L945-957)
- @brief Extract payload section from canonical cache document.
- @details Returns mutable provider-result mapping from normalized document.
- @param cache_document {dict[str, object]} Canonical cache document.
- @return {dict[str, object]} Provider payload section.

### fn `def _cache_status_section(cache_document: dict[str, object]) -> dict[str, object]` `priv` (L958-970)
- @brief Extract status section from canonical cache document.
- @details Returns mutable provider/window status mapping from normalized document.
- @param cache_document {dict[str, object]} Canonical cache document.
- @return {dict[str, object]} Provider/window status section.

### fn `def _serialize_attempt_status(result: ProviderResult) -> dict[str, object]` `priv` (L971-991)
- @brief Serialize one provider/window fetch attempt status for cache persistence.
- @details Converts ProviderResult error state to status object using `OK`/`FAIL`, preserving error text, update timestamp, and optional HTTP status code.
- @param result {ProviderResult} Provider result from current refresh attempt.
- @return {dict[str, object]} Attempt-status payload.
- @satisfies REQ-044

### fn `def _record_attempt_status(` `priv` (L992-994)

### fn `def _extract_claude_snapshot_from_cache_document(` `priv` (L1014-1015)
- @brief Persist one provider/window attempt status into cache status section.
- @details Upserts `status[provider][window]` with serialized attempt metadata and
preserves statuses for untouched providers/windows.
- @param status_section {dict[str, object]} Mutable cache status section.
- @param result {ProviderResult} Provider result to encode.
- @return {None} Function return value.
- @satisfies REQ-044
- @satisfies REQ-046

### fn `def _get_window_attempt_status(` `priv` (L1030-1033)
- @brief Extract persisted Claude dual-window payload from cache document.
- @details Reads Claude entry from cache `payload` section and normalizes it into
a dual-window raw payload (`five_hour`, `seven_day`) for HTTP 429 restoration.
- @param cache_document {dict[str, object]} Canonical cache document.
- @return {dict[str, object] | None} Normalized dual-window payload or None.
- @satisfies REQ-047

### fn `def _overlay_cached_failure_status(` `priv` (L1053-1057)
- @brief Read provider/window attempt status from cache status section.
- @details Resolves nested `status[provider][window]` object and validates mapping
shape before returning it to projection helpers.
- @param status_section {dict[str, object]} Cache status section.
- @param provider_key {str} Provider identifier.
- @param window {WindowPeriod} Window identifier.
- @return {dict[str, object] | None} Attempt status object or None.

### fn `def _filter_cached_payload(` `priv` (L1106-1108)
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

### fn `def _filter_idle_time_by_provider(` `priv` (L1141-1143)
- @brief Filter canonical cache document by optional provider selector.
- @details Filters both cache sections (`payload`, `status`) so selected-provider
output contains only relevant provider nodes while preserving schema keys.
- @param cache_document {dict[str, object]} Canonical cache document.
- @param provider_filter {ProviderName | None} Optional provider selector.
- @return {dict[str, object]} Filtered cache document with canonical sections.

### fn `def _serialize_idle_time_state(` `priv` (L1161-1162)
- @brief Filter provider-keyed idle-time map by optional provider selector.
- @param idle_time_by_provider {dict[str, IdleTimeState]} Provider idle-time state map.
- @param provider_filter {ProviderName | None} Optional provider selector.
- @return {dict[str, IdleTimeState]} Filtered provider idle-time map.
- @satisfies REQ-003
- @satisfies REQ-084

### fn `def _serialize_freshness_state(` `priv` (L1177-1178)
- @brief Serialize provider-keyed idle-time state for `show --json`.
- @param idle_time_by_provider {dict[str, IdleTimeState]} Provider idle-time map.
- @return {dict[str, dict[str, object]]} JSON-safe provider idle-time section.
- @satisfies REQ-003
- @satisfies CTN-009

### fn `def _fixed_effective_window(provider_name: ProviderName) -> WindowPeriod | None` `priv` (L1202-1216)
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

### fn `def _project_cached_window(` `priv` (L1217-1220)

### fn `def _load_cached_results(` `priv` (L1271-1275)
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

### fn `def _update_idle_time_after_refresh(` `priv` (L1319-1321)
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

### fn `def _project_next_reset(resets_at_str: str, window: WindowPeriod) -> datetime | None` `priv` (L1396-1427)
- @brief Persist provider-scoped idle-time metadata after refresh completion.
- @brief Compute the next reset boundary after a stale resets_at timestamp.
- @details Computes per-provider idle-time state after refresh execution.
Successful-only provider cycles schedule `idle_until = last_success_at + idle_delay_seconds`.
Provider cycles containing failures schedule
`idle_until = last_attempt_at + max(idle_delay_seconds, retry_after_seconds_or_0)`.
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

### fn `def _apply_reset_projection(result: ProviderResult) -> ProviderResult` `priv` (L1428-1462)
- @brief Return a copy of `result` with `metrics.reset_at` set to the projected next reset boundary when it is currently None but the raw payload contains a parseable past `resets_at` string for the result's window.
- @details When a ProviderResult is obtained from stale disk cache (last-good path) or from a cross-window raw re-parse, `_parse_response` correctly sets `reset_at=None` for past timestamps. This function recovers the display information by projecting the next future reset boundary from the raw payload's `resets_at` field, ensuring the 'Resets in:' countdown is shown even when the cached timestamp has already elapsed. If `reset_at` is already non-None, or the raw payload has no parseable `resets_at` for the window, or projection fails, the original result is returned unchanged.
- @param result {ProviderResult} Candidate result whose reset_at may require projection.
- @return {ProviderResult} Original result unchanged if no projection is needed; otherwise a new ProviderResult with metrics.reset_at set to the projected datetime.
- @see _project_next_reset
- @satisfies REQ-002

### fn `def get_providers() -> dict[ProviderName, BaseProvider]` (L1463-1478)
- @brief Execute get providers.
- @details Applies get providers logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {dict[ProviderName, BaseProvider]} Function return value.

### fn `def parse_window(window: str) -> WindowPeriod` (L1479-1498)
- @brief Execute parse window.
- @details Applies parse window logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {str} Input parameter `window`.
- @return {WindowPeriod} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def parse_provider(provider: str) -> ProviderName | None` (L1499-1515)
- @brief Execute parse provider.
- @details Applies parse provider logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param provider {str} Input parameter `provider`.
- @return {ProviderName | None} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _fetch_result(` `priv` (L1516-1519)

### fn `def _fetch_claude_dual(` `priv` (L1559-1561)
- @brief Execute one provider refresh call without legacy TTL cache reuse.
- @details Executes throttled provider fetch and returns normalized success/error
results. Claude 5h/7d requests are routed through `_fetch_claude_dual` so one
API request can provide deterministic dual-window rate-limit normalization.
- @param provider {BaseProvider} Provider instance to fetch from.
- @param window {WindowPeriod} Time window for the fetch.
- @param throttle_state {dict[str, float | int] | None} Mutable throttling state
used to enforce inter-call spacing for live API requests.
- @return {ProviderResult} Refreshed provider result for requested window.
- @satisfies CTN-004
- @satisfies REQ-043
- @satisfies REQ-040

### fn `def _extract_claude_dual_payload(` `priv` (L1598-1600)
- @brief Fetch Claude 5h and 7d results via a single API call.
- @details Executes ClaudeOAuthProvider.fetch_all_windows for 5h and 7d on each invocation.
Returns normalized provider results exactly as fetched (or synthesized error
results on exception) without partial-window metric fallback.
- @param provider {ClaudeOAuthProvider} Claude provider instance.
- @param throttle_state {dict[str, float | int] | None} Mutable throttling state
used to enforce inter-call spacing for live API requests.
- @return {tuple[ProviderResult, ProviderResult]} (5h_result, 7d_result).
- @satisfies REQ-002, REQ-036, REQ-037, CTN-004, REQ-040, REQ-043

### fn `def _normalize_claude_dual_payload(payload: object) -> dict[str, object] | None` `priv` (L1622-1644)
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

### fn `def _extract_snapshot_reset_at(` `priv` (L1645-1647)

### fn `def _extract_snapshot_utilization(` `priv` (L1670-1672)
- @brief Resolve projected reset timestamp from persisted Claude snapshot payload.
- @details Uses window-specific `resets_at` string from persisted payload and
projects next reset boundary through `_project_next_reset`.
- @param snapshot_payload {dict[str, object] | None} Persisted dual-window payload.
- @param window {WindowPeriod} Target window period.
- @return {datetime | None} Projected reset timestamp or None.
- @satisfies REQ-036

### fn `def _is_claude_rate_limited_result(result: ProviderResult) -> bool` `priv` (L1701-1716)
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

### fn `def _build_claude_rate_limited_partial_result(` `priv` (L1717-1720)

### fn `def _refresh_and_persist_cache_payload(` `priv` (L1765-1769)
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

### fn `def retrieve_results_via_cache_pipeline(` (L1862-1866)
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

### fn `def _build_cached_dual_window_results(` `priv` (L2010-2013)
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

### fn `def main(ctx: click.Context) -> None` `@click.pass_context` (L2093-2103)
- @brief Execute main.
- @details Applies main logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.
- @satisfies REQ-068

### fn `def show(provider: str, window: str, output_json: bool, force_refresh: bool) -> None` (L2136-2311)
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

### fn `def _provider_display_name(provider_name: ProviderName) -> str` `priv` (L2312-2326)
- @brief Resolve human-facing provider title for terminal panel rendering.
- @details Maps machine-readable provider keys to display names aligned with CLI and GNOME extension output surfaces; applies uppercase `GEMINIAI` override for provider key `geminiai`.
- @param provider_name {ProviderName} Provider enum key.
- @return {str} Human-facing provider display name.
- @satisfies REQ-062

### fn `def _provider_panel_sort_key(provider_name: ProviderName) -> tuple[int, str]` `priv` (L2327-2342)
- @brief Build deterministic provider sort key for CLI `show` panel ordering.
- @details Applies canonical provider order `claude/openrouter/copilot/codex/openai/geminiai`; unknown providers are appended after known providers using lexical fallback.
- @param provider_name {ProviderName} Provider enum key.
- @return {tuple[int, str]} `(rank, provider_name.value)` sort key.
- @satisfies REQ-067
- @satisfies TST-030

### fn `def _provider_panel_color_code(provider_name: ProviderName) -> str` `priv` (L2343-2352)
- @brief Resolve ANSI color code for one provider output surface.
- @param provider_name {ProviderName} Provider enum key.
- @return {str} ANSI foreground color code.
- @satisfies REQ-067

### fn `def _provider_supports_api_counters(provider_name: ProviderName) -> bool` `priv` (L2353-2364)
- @brief Determine whether provider panels always render API counter lines.
- @details Returns true for providers that expose requests/token counters in CLI and GNOME output surfaces, enforcing null-to-zero normalization.
- @param provider_name {ProviderName} Provider enum key.
- @return {bool} True when requests/tokens lines must render on OK state.
- @satisfies REQ-036

### fn `def _strip_ansi_sequences(value: str) -> str` `priv` (L2365-2376)
- @brief Remove ANSI SGR color escape sequences from terminal text.
- @details Strips `\x1b[...m` segments so panel width calculations can use visible glyph length instead of byte length with hidden control codes.
- @param value {str} Input string that may include ANSI color escapes.
- @return {str} String with ANSI SGR escapes removed.
- @satisfies REQ-067

### fn `def _visible_text_length(value: str) -> int` `priv` (L2377-2388)
- @brief Compute visible text length for terminal panel alignment.
- @details Calculates string length after ANSI SGR stripping to keep bordered-panel width deterministic for colored progress bar rows.
- @param value {str} Input string potentially containing ANSI escapes.
- @return {int} Visible glyph count used by panel width and padding logic.
- @satisfies REQ-067

### fn `def _ansi_ljust(value: str, width: int) -> str` `priv` (L2389-2401)
- @brief Left-pad ANSI-colored text to one visible width.
- @details Appends trailing spaces using visible-length semantics so rows that include ANSI escapes align with border columns exactly.
- @param value {str} Source text rendered inside one panel cell.
- @param width {int} Target visible width for the panel cell.
- @return {str} Padded terminal text preserving existing ANSI sequences.
- @satisfies REQ-067

### fn `def _format_bright_white_bold(value: str) -> str` `priv` (L2402-2414)
- @brief Wrap one metric value with bright-white bold ANSI style.
- @details Applies ANSI SGR sequences for bold (`1`) and bright-white foreground (`97`) and appends reset (`0`) for deterministic inline metric emphasis.
- @param value {str} Visible metric value string.
- @return {str} Styled value with ANSI SGR wrappers.
- @satisfies REQ-035
- @satisfies REQ-051

### fn `def _wrap_panel_lines(body_lines: list[str], wrap_width: int) -> list[str]` `priv` (L2415-2439)
- @brief Wrap panel body lines to one deterministic visible width.
- @details Applies ANSI-aware wrapping: lines containing ANSI SGR sequences are measured by visible glyph length and wrapped on stripped text only when needed.
- @param body_lines {list[str]} Raw panel body lines.
- @param wrap_width {int} Maximum visible width for one wrapped line.
- @return {list[str]} Wrapped panel lines ready for width calculation/rendering.
- @satisfies REQ-067

### fn `def _panel_content_width(title: str, body_lines: list[str]) -> int` `priv` (L2440-2459)
- @brief Resolve one panel visible content width from title and body lines.
- @details Computes width from wrapped visible-line lengths and clamps to configured min/max panel boundaries.
- @param title {str} Panel title string.
- @param body_lines {list[str]} Raw body lines for the panel.
- @return {int} Content width used for bordered panel rendering.
- @satisfies REQ-067

### fn `def _resolve_shared_panel_content_width(` `priv` (L2460-2461)

### fn `def _emit_provider_panel(` `priv` (L2476-2480)
- @brief Resolve shared panel width for one CLI show rendering cycle.
- @details Selects the largest computed content width across all rendered
provider panels, then applies that width to every panel in the cycle.
- @param rendered_panels {list[tuple[ProviderName, str, list[str]]]} Render queue.
- @return {int} Shared content width used by all emitted panels.
- @satisfies REQ-067

### fn `def _format_http_status_retry_line(` `priv` (L2519-2521)
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

### fn `def _build_result_panel(` `priv` (L2543-2547)
- @brief Build normalized HTTP status/retry diagnostic line for text output.
- @details Returns one deterministic line matching requirement wording:
`HTTP status: <code>, Retry after: <seconds> sec.` when both values exist.
- @param status_code_raw {object} Status code candidate from result raw payload.
- @param retry_after_raw {object} Retry-after candidate from result raw payload.
- @return {str | None} Diagnostic line or None when both values are missing.
- @satisfies REQ-037

### fn `def _build_dual_window_panel(` `priv` (L2688-2692)
- @brief Build one provider panel title/body payload for CLI text rendering.
- @details Formats deterministic panel lines for one provider/window result and
preserves provider-specific metrics/error rendering rules used by `show`.
- @param name {ProviderName} Provider name enum value.
- @param result {ProviderResult} Provider result to render.
- @param label {str | None} Optional window label suffix (e.g. `"5h"`, `"7d"`).
- @param freshness_state {IdleTimeState | None} Optional provider idle-time state
carrying `last_success_timestamp` and `idle_until_timestamp` freshness values.
- @return {tuple[str, list[str]]} Panel title and body lines.
- @satisfies REQ-084
- @satisfies REQ-034
- @satisfies REQ-035
- @satisfies REQ-036
- @satisfies REQ-051
- @satisfies REQ-060
- @satisfies REQ-067

### fn `def _print_result(name: ProviderName, result, label: str | None = None) -> None` `priv` (L2787-2805)
- @brief Build one grouped CLI panel for dual-window providers.
- @brief Render CLI text output for one provider result.
- @details Produces one provider panel with a shared metadata block and two
blank-line-separated sections (`5h`, `7d`) derived from window-specific panel
renderings while deduplicating shared lines; Claude/Codex render one shared
`Remaining credits` line after the `7d` section.
- @details Formats usage percentage, reset countdown, remaining credits, cost, requests, and token counts for one provider/window result. Cost is formatted using `metrics.currency_symbol` (never hardcoded `$`).
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
- @satisfies REQ-034
- @satisfies REQ-035
- @satisfies REQ-051
- @satisfies REQ-067

### fn `def _format_reset_duration(seconds: float) -> str` `priv` (L2806-2821)
- @brief Execute format reset duration.
- @details Applies format reset duration logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param seconds {float} Input parameter `seconds`.
- @return {str} Function return value.

### fn `def _should_print_claude_reset_pending_hint(` `priv` (L2822-2824)

### fn `def _is_displayed_zero_percent(percent: float | None) -> bool` `priv` (L2844-2860)
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

### fn `def _progress_bar(percent: float, provider_name: ProviderName, width: int = 20) -> str` `priv` (L2861-2876)
- @brief Execute progress bar.
- @details Applies progress bar logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param percent {float} Input parameter `percent`.
- @param provider_name {ProviderName} Provider enum key for color mapping.
- @param width {int} Input parameter `width`.
- @return {str} Function return value.

### fn `def doctor() -> None` (L2881-2933)
- @brief Execute doctor.
- @details Applies doctor logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def env() -> None` (L2938-2946)
- @brief Execute env.
- @details Applies env logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def setup() -> None` (L2951-3150)
- @brief Execute setup.
- @details Prompts for `idle_delay_seconds`, `api_call_delay_milliseconds`, `api_call_timeout_milliseconds`, `gnome_refresh_interval_seconds`, and `billing_data` in order, then prompts for provider currency symbols including `geminiai` (choices: `$`, `£`, `€`, default `$`), then persists all values to `~/.config/aibar/config.json`. GeminiAI OAuth source supports `skip`, `file`, `paste`, and `login` (re-authorization with current scopes). Also prompts for provider API keys and writes them to `~/.config/aibar/env`.
- @return {None} Function return value.
- @satisfies REQ-005
- @satisfies REQ-049
- @satisfies REQ-055
- @satisfies REQ-056
- @satisfies REQ-059

### fn `def login(provider: str) -> None` (L3219-3237)
- @brief Execute login.
- @details Applies login logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param provider {str} Input parameter `provider`.
- @return {None} Function return value.

### fn `def _login_claude() -> None` `priv` (L3238-3286)
- @brief Execute login claude.
- @details Applies login claude logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def _login_copilot() -> None` `priv` (L3287-3314)
- @brief Execute login copilot.
- @details Applies login copilot logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def _login_geminiai() -> None` `priv` (L3315-3351)
- @brief Execute GeminiAI OAuth login flow.
- @details Reuses persisted OAuth client configuration to launch browser-based authorization and persist refresh-capable Google credentials.
- @return {None} Function return value.
- @satisfies REQ-055
- @satisfies REQ-056

### fn `def _resolve_extension_source_dir() -> Path` `priv` (L3352-3364)
- @brief Resolve GNOME extension source directory from within the `aibar` package.
- @details Uses `Path(__file__).resolve().parent` to locate the `aibar` package directory, then appends `gnome-extension/<UUID>/`. Works in development (editable install), wheel-installed, and `uv tool install` layouts because the extension directory resides inside the `aibar` Python package subtree.
- @return {Path} Absolute path to the extension source directory.
- @satisfies REQ-025, REQ-083

### fn `def gnome_install() -> None` (L3375-3485)
- @brief Install or update the AIBar GNOME Shell extension to the user's local extensions directory.
- @details Resolves extension source from the installed package path, validates source directory contains `metadata.json` and is non-empty, then executes one of two flows: install flow (`target` absent) creates target and copies files before enabling extension; update flow (`target` present) disables extension, copies files, then enables extension. Update flow masks non-zero disable outcomes caused by missing extension and continues. Produces colored Click-styled terminal output for all status messages.
- @return {None} Function return value.
- @throws {SystemExit} Exits with code 1 on prerequisite validation failure.
- @satisfies PRJ-008, REQ-025, REQ-026, REQ-027, REQ-028, REQ-029, REQ-030, REQ-032, REQ-099

### fn `def gnome_uninstall() -> None` (L3495-3558)
- @brief Remove the AIBar GNOME Shell extension from the user's local extensions directory.
- @details Disables the extension via `gnome-extensions disable`, then removes the entire extension directory at `~/.local/share/gnome-shell/extensions/aibar@aibar.panel/`. Exits with code 1 if the extension directory does not exist. Produces colored Click-styled terminal output for all status messages.
- @return {None} Function return value.
- @throws {SystemExit} Exits with code 1 when extension directory does not exist.
- @satisfies REQ-028, REQ-080, REQ-081, REQ-082

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`RetrievalPipelineOutput`|class|pub|136-165|class RetrievalPipelineOutput|
|`StartupReleaseCheckResponse`|class|pub|167-186|class StartupReleaseCheckResponse|
|`_startup_idle_state_path`|fn|priv|187-196|def _startup_idle_state_path() -> Path|
|`_startup_human_timestamp`|fn|priv|197-209|def _startup_human_timestamp(epoch_seconds: int) -> str|
|`_startup_parse_int`|fn|priv|210-227|def _startup_parse_int(value: object, default: int = 0) -...|
|`_load_startup_idle_state`|fn|priv|228-247|def _load_startup_idle_state() -> dict[str, object] | None|
|`_startup_idle_epochs`|fn|priv|248-269|def _startup_idle_epochs(state: dict[str, object] | None)...|
|`_save_startup_idle_state`|fn|priv|270-300|def _save_startup_idle_state(last_success_epoch: int, idl...|
|`_cleanup_startup_idle_state_artifacts`|fn|priv|301-326|def _cleanup_startup_idle_state_artifacts() -> int|
|`_emit_startup_preflight_message`|fn|priv|327-341|def _emit_startup_preflight_message(message: str, color_c...|
|`_parse_retry_after_header`|fn|priv|342-366|def _parse_retry_after_header(retry_after_raw: str | None...|
|`_normalize_release_version`|fn|priv|367-383|def _normalize_release_version(raw_version: object) -> st...|
|`_fetch_startup_latest_release`|fn|priv|384-438|def _fetch_startup_latest_release() -> StartupReleaseChec...|
|`_parse_version_triplet`|fn|priv|439-457|def _parse_version_triplet(version_text: str) -> tuple[in...|
|`_is_newer_release`|fn|priv|458-474|def _is_newer_release(installed_version: str, latest_vers...|
|`_run_startup_update_preflight`|fn|priv|475-542|def _run_startup_update_preflight() -> None|
|`_execute_lifecycle_subprocess`|fn|priv|543-565|def _execute_lifecycle_subprocess(command: list[str]) -> int|
|`_is_linux_runtime`|fn|priv|566-578|def _is_linux_runtime() -> bool|
|`_emit_non_linux_lifecycle_guidance`|fn|priv|579-605|def _emit_non_linux_lifecycle_guidance(option_name: str, ...|
|`_handle_upgrade_option`|fn|priv|606-607|def _handle_upgrade_option(|
|`_handle_uninstall_option`|fn|priv|636-637|def _handle_uninstall_option(|
|`_handle_version_option`|fn|priv|670-671|def _handle_version_option(|
|`StartupPreflightGroup`|class|pub|690-753|class StartupPreflightGroup(click.Group)|
|`StartupPreflightGroup.format_epilog`|fn|pub|700-703|def format_epilog(|
|`StartupPreflightGroup.main`|fn|pub|720-727|def main(|
|`_normalize_utc`|fn|priv|754-766|def _normalize_utc(value: datetime) -> datetime|
|`_format_local_datetime`|fn|priv|767-779|def _format_local_datetime(value: datetime) -> str|
|`_epoch_to_utc_datetime`|fn|priv|780-788|def _epoch_to_utc_datetime(epoch_seconds: int) -> datetime|
|`_build_freshness_line`|fn|priv|789-791|def _build_freshness_line(|
|`_apply_api_call_delay`|fn|priv|816-845|def _apply_api_call_delay(throttle_state: dict[str, float...|
|`_coerce_retry_after_seconds`|fn|priv|846-866|def _coerce_retry_after_seconds(value: object) -> int | None|
|`_extract_retry_after_seconds`|fn|priv|867-881|def _extract_retry_after_seconds(result: ProviderResult) ...|
|`_is_http_429_result`|fn|priv|882-892|def _is_http_429_result(result: ProviderResult) -> bool|
|`_serialize_results_payload`|fn|priv|893-894|def _serialize_results_payload(|
|`_empty_cache_document`|fn|priv|908-922|def _empty_cache_document() -> dict[str, object]|
|`_normalize_cache_document`|fn|priv|923-944|def _normalize_cache_document(cache_document: dict[str, o...|
|`_cache_payload_section`|fn|priv|945-957|def _cache_payload_section(cache_document: dict[str, obje...|
|`_cache_status_section`|fn|priv|958-970|def _cache_status_section(cache_document: dict[str, objec...|
|`_serialize_attempt_status`|fn|priv|971-991|def _serialize_attempt_status(result: ProviderResult) -> ...|
|`_record_attempt_status`|fn|priv|992-994|def _record_attempt_status(|
|`_extract_claude_snapshot_from_cache_document`|fn|priv|1014-1015|def _extract_claude_snapshot_from_cache_document(|
|`_get_window_attempt_status`|fn|priv|1030-1033|def _get_window_attempt_status(|
|`_overlay_cached_failure_status`|fn|priv|1053-1057|def _overlay_cached_failure_status(|
|`_filter_cached_payload`|fn|priv|1106-1108|def _filter_cached_payload(|
|`_filter_idle_time_by_provider`|fn|priv|1141-1143|def _filter_idle_time_by_provider(|
|`_serialize_idle_time_state`|fn|priv|1161-1162|def _serialize_idle_time_state(|
|`_serialize_freshness_state`|fn|priv|1177-1178|def _serialize_freshness_state(|
|`_fixed_effective_window`|fn|priv|1202-1216|def _fixed_effective_window(provider_name: ProviderName) ...|
|`_project_cached_window`|fn|priv|1217-1220|def _project_cached_window(|
|`_load_cached_results`|fn|priv|1271-1275|def _load_cached_results(|
|`_update_idle_time_after_refresh`|fn|priv|1319-1321|def _update_idle_time_after_refresh(|
|`_project_next_reset`|fn|priv|1396-1427|def _project_next_reset(resets_at_str: str, window: Windo...|
|`_apply_reset_projection`|fn|priv|1428-1462|def _apply_reset_projection(result: ProviderResult) -> Pr...|
|`get_providers`|fn|pub|1463-1478|def get_providers() -> dict[ProviderName, BaseProvider]|
|`parse_window`|fn|pub|1479-1498|def parse_window(window: str) -> WindowPeriod|
|`parse_provider`|fn|pub|1499-1515|def parse_provider(provider: str) -> ProviderName | None|
|`_fetch_result`|fn|priv|1516-1519|def _fetch_result(|
|`_fetch_claude_dual`|fn|priv|1559-1561|def _fetch_claude_dual(|
|`_extract_claude_dual_payload`|fn|priv|1598-1600|def _extract_claude_dual_payload(|
|`_normalize_claude_dual_payload`|fn|priv|1622-1644|def _normalize_claude_dual_payload(payload: object) -> di...|
|`_extract_snapshot_reset_at`|fn|priv|1645-1647|def _extract_snapshot_reset_at(|
|`_extract_snapshot_utilization`|fn|priv|1670-1672|def _extract_snapshot_utilization(|
|`_is_claude_rate_limited_result`|fn|priv|1701-1716|def _is_claude_rate_limited_result(result: ProviderResult...|
|`_build_claude_rate_limited_partial_result`|fn|priv|1717-1720|def _build_claude_rate_limited_partial_result(|
|`_refresh_and_persist_cache_payload`|fn|priv|1765-1769|def _refresh_and_persist_cache_payload(|
|`retrieve_results_via_cache_pipeline`|fn|pub|1862-1866|def retrieve_results_via_cache_pipeline(|
|`_build_cached_dual_window_results`|fn|priv|2010-2013|def _build_cached_dual_window_results(|
|`main`|fn|pub|2093-2103|def main(ctx: click.Context) -> None|
|`show`|fn|pub|2136-2311|def show(provider: str, window: str, output_json: bool, f...|
|`_provider_display_name`|fn|priv|2312-2326|def _provider_display_name(provider_name: ProviderName) -...|
|`_provider_panel_sort_key`|fn|priv|2327-2342|def _provider_panel_sort_key(provider_name: ProviderName)...|
|`_provider_panel_color_code`|fn|priv|2343-2352|def _provider_panel_color_code(provider_name: ProviderNam...|
|`_provider_supports_api_counters`|fn|priv|2353-2364|def _provider_supports_api_counters(provider_name: Provid...|
|`_strip_ansi_sequences`|fn|priv|2365-2376|def _strip_ansi_sequences(value: str) -> str|
|`_visible_text_length`|fn|priv|2377-2388|def _visible_text_length(value: str) -> int|
|`_ansi_ljust`|fn|priv|2389-2401|def _ansi_ljust(value: str, width: int) -> str|
|`_format_bright_white_bold`|fn|priv|2402-2414|def _format_bright_white_bold(value: str) -> str|
|`_wrap_panel_lines`|fn|priv|2415-2439|def _wrap_panel_lines(body_lines: list[str], wrap_width: ...|
|`_panel_content_width`|fn|priv|2440-2459|def _panel_content_width(title: str, body_lines: list[str...|
|`_resolve_shared_panel_content_width`|fn|priv|2460-2461|def _resolve_shared_panel_content_width(|
|`_emit_provider_panel`|fn|priv|2476-2480|def _emit_provider_panel(|
|`_format_http_status_retry_line`|fn|priv|2519-2521|def _format_http_status_retry_line(|
|`_build_result_panel`|fn|priv|2543-2547|def _build_result_panel(|
|`_build_dual_window_panel`|fn|priv|2688-2692|def _build_dual_window_panel(|
|`_print_result`|fn|priv|2787-2805|def _print_result(name: ProviderName, result, label: str ...|
|`_format_reset_duration`|fn|priv|2806-2821|def _format_reset_duration(seconds: float) -> str|
|`_should_print_claude_reset_pending_hint`|fn|priv|2822-2824|def _should_print_claude_reset_pending_hint(|
|`_is_displayed_zero_percent`|fn|priv|2844-2860|def _is_displayed_zero_percent(percent: float | None) -> ...|
|`_progress_bar`|fn|priv|2861-2876|def _progress_bar(percent: float, provider_name: Provider...|
|`doctor`|fn|pub|2881-2933|def doctor() -> None|
|`env`|fn|pub|2938-2946|def env() -> None|
|`setup`|fn|pub|2951-3150|def setup() -> None|
|`login`|fn|pub|3219-3237|def login(provider: str) -> None|
|`_login_claude`|fn|priv|3238-3286|def _login_claude() -> None|
|`_login_copilot`|fn|priv|3287-3314|def _login_copilot() -> None|
|`_login_geminiai`|fn|priv|3315-3351|def _login_geminiai() -> None|
|`_resolve_extension_source_dir`|fn|priv|3352-3364|def _resolve_extension_source_dir() -> Path|
|`gnome_install`|fn|pub|3375-3485|def gnome_install() -> None|
|`gnome_uninstall`|fn|pub|3495-3558|def gnome_uninstall() -> None|


---

# config.py | Python | 679L | 42 symbols | 14 imports | 37 comments
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
- var `DEFAULT_API_CALL_TIMEOUT_MILLISECONDS = 3000` (L30)
- var `DEFAULT_GNOME_REFRESH_INTERVAL_SECONDS = 60` (L31)
- var `DEFAULT_BILLING_DATASET = "billing_data"` (L32)
- var `DEFAULT_CURRENCY_SYMBOL = "$"` (L33)
- var `LOCK_POLL_INTERVAL_SECONDS = 0.25` (L35)
### class `class RuntimeConfig(BaseModel)` : BaseModel (L44-73)
- @brief Define runtime configuration component for refresh throttling, timeout, and currency controls.
- @details Encodes persisted CLI runtime controls used by `show` refresh logic, GNOME extension scheduling, and per-provider currency symbol resolution. Fields are validated with defaults that reduce rate-limit pressure. `api_call_delay_milliseconds` defaults to `100` ms inter-call spacing. `api_call_timeout_milliseconds` defaults to `3000` ms HTTP response timeout applied to all provider API calls via `httpx.AsyncClient(timeout=<value>/1000.0)`. `currency_symbols` maps provider name strings to currency symbols (`$`, `£`, `€`); missing entries default to `DEFAULT_CURRENCY_SYMBOL` at resolution time. `billing_data` stores the Google BigQuery dataset name used for GeminiAI billing export table discovery. Optional GeminiAI field persists Google Cloud project identifier used by OAuth-backed Monitoring API fetch execution.
- @satisfies CTN-008
- @satisfies REQ-049
- @satisfies REQ-095
- @satisfies REQ-096

### class `class IdleTimeState(BaseModel)` : BaseModel (L74-88)
- @brief Define persisted idle-time entry for one provider.
- @details Stores provider-local last-success and idle-until timestamps in epoch-seconds and local-timezone ISO-8601 formats. Serialized as one value under provider key in `~/.cache/aibar/idle-time.json`.
- @satisfies CTN-009

### fn `def _ensure_app_config_dir() -> None` `priv` (L89-98)
- @brief Ensure AIBar configuration directory exists before file persistence.
- @details Creates `~/.config/aibar` recursively when missing. This function is called by env-file and runtime-config persistence helpers.
- @return {None} Function return value.

### fn `def _ensure_app_cache_dir() -> None` `priv` (L99-108)
- @brief Ensure AIBar cache directory exists before cache and idle-time persistence.
- @details Creates `~/.cache/aibar` recursively when missing. This function is called by CLI cache and idle-time persistence helpers.
- @return {None} Function return value.

### fn `def _lock_file_path(target_path: Path) -> Path` `priv` (L109-120)
- @brief Resolve lock-file path for one cache artifact.
- @details Produces deterministic lock-file names under `~/.cache/aibar/` using `<filename>.lock` to coordinate cross-process read/write exclusion.
- @param target_path {Path} Cache file path guarded by lock.
- @return {Path} Absolute lock-file path.
- @satisfies REQ-066

### fn `def _blocking_file_lock(target_path: Path)` `priv` `@contextmanager` (L122-150)
- @brief Acquire and release blocking lock-file for cache artifact I/O.
- @details Uses atomic `O_CREAT|O_EXCL` lock-file creation. When lock-file already exists, polls every `250ms` until lock release, then acquires lock. Always removes owned lock-file during exit.
- @param target_path {Path} Cache artifact path protected by this lock.
- @return {Iterator[None]} Context manager yielding while lock is held.
- @satisfies REQ-066

### fn `def _sanitize_cache_payload(payload: dict[str, Any]) -> dict[str, Any]` `priv` (L151-185)
- @brief Redact sensitive keys from cache payload before disk persistence.
- @details Recursively traverses dictionaries/lists and replaces values for case-insensitive key matches in `{token,key,secret,password,authorization}` with deterministic placeholder string `[REDACTED]`.
- @param payload {dict[str, Any]} Cache document containing `payload` and `status` sections.
- @return {dict[str, Any]} Sanitized deep-copy structure safe for persistence.
- @satisfies DES-004

### fn `def clean(value: Any) -> Any` (L163-182)
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

### fn `def load_runtime_config() -> RuntimeConfig` (L186-202)
- @brief Load runtime refresh configuration from disk with schema validation.
- @details Reads `~/.config/aibar/config.json`, validates fields against `RuntimeConfig`, and returns defaults when file is missing or invalid.
- @return {RuntimeConfig} Validated runtime configuration payload.
- @satisfies CTN-008

### fn `def save_runtime_config(runtime_config: RuntimeConfig) -> None` (L203-218)
- @brief Persist runtime refresh configuration to disk.
- @details Serializes `RuntimeConfig` to `~/.config/aibar/config.json` using stable pretty-printed JSON (`indent=2`) for deterministic readability.
- @param runtime_config {RuntimeConfig} Validated runtime configuration model.
- @return {None} Function return value.
- @satisfies CTN-008

### fn `def load_cli_cache() -> dict[str, Any] | None` (L219-238)
- @brief Load CLI cache payload from disk.
- @details Reads `~/.cache/aibar/cache.json` and returns parsed object only when payload root is a JSON object with canonical cache sections.
- @return {dict[str, Any] | None} Parsed cache payload or None if unavailable.
- @satisfies CTN-004
- @satisfies REQ-047
- @satisfies REQ-066

### fn `def resolve_currency_symbol(raw: dict[str, Any] | None, provider_name: str) -> str` (L239-268)
- @brief Resolve currency symbol for a provider result from API response or config.
- @details Extraction priority: 1. `raw["currency"]` field: if a recognized symbol (`$`, `£`, `€`) → use directly; if an ISO-4217 code (`USD`, `GBP`, `EUR`) → map to symbol. 2. `RuntimeConfig.currency_symbols[provider_name]` configured default. 3. `DEFAULT_CURRENCY_SYMBOL` (`"$"`) as final fallback.
- @param raw {dict[str, Any] | None} Raw API response dict from the provider fetch call, or None.
- @param provider_name {str} Provider name string key (e.g. `"claude"`, `"openai"`).
- @return {str} Resolved currency symbol; always a member of `VALID_CURRENCY_SYMBOLS`.
- @satisfies REQ-050

### fn `def save_cli_cache(payload: dict[str, Any]) -> None` (L269-292)
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

### fn `def build_idle_time_state(last_success_at: datetime, idle_until: datetime) -> IdleTimeState` (L293-325)
- @brief Build provider-local idle-time entry from UTC-compatible datetimes.
- @details Normalizes timestamps to UTC for epoch conversion, then emits human-readable ISO-8601 values in runtime local timezone for deterministic parity with CLI/GNOME freshness rendering.
- @param last_success_at {datetime} Last successful refresh timestamp.
- @param idle_until {datetime} Timestamp until provider refresh remains gated.
- @return {IdleTimeState} Normalized provider idle-time entry.
- @satisfies CTN-009

### fn `def load_idle_time() -> dict[str, IdleTimeState]` (L326-354)
- @brief Load provider-keyed idle-time state from disk.
- @details Reads `~/.cache/aibar/idle-time.json` and validates each provider value as `IdleTimeState`. Invalid provider entries are ignored. Missing or unreadable payloads return an empty map.
- @return {dict[str, IdleTimeState]} Provider-keyed idle-time state map.
- @satisfies CTN-009
- @satisfies REQ-066

### fn `def save_idle_time(idle_time_by_provider: dict[str, IdleTimeState]) -> dict[str, IdleTimeState]` (L355-388)
- @brief Persist provider-keyed idle-time state map.
- @details Validates each provider entry, serializes canonical epoch and ISO-8601 fields, and writes `~/.cache/aibar/idle-time.json` in pretty-printed JSON. Invalid map entries are skipped.
- @param idle_time_by_provider {dict[str, IdleTimeState]} Provider-keyed idle-time map.
- @return {dict[str, IdleTimeState]} Persisted provider-keyed idle-time map.
- @satisfies CTN-009
- @satisfies REQ-066

### fn `def remove_idle_time_file() -> None` (L389-404)
- @brief Remove persisted idle-time state file if present.
- @details Deletes `~/.cache/aibar/idle-time.json` to force immediate refresh behavior on subsequent `show` execution.
- @return {None} Function return value.
- @satisfies REQ-039
- @satisfies REQ-066

### fn `def get_api_call_timeout_seconds() -> float` (L405-421)
- @brief Resolve HTTP response timeout in seconds from runtime configuration.
- @details Reads `api_call_timeout_milliseconds` from `RuntimeConfig` and converts to seconds. Returns `DEFAULT_API_CALL_TIMEOUT_MILLISECONDS / 1000.0` when configuration is missing or invalid.
- @return {float} HTTP response timeout in seconds (>= 0.001).
- @satisfies REQ-095
- @satisfies CTN-003

### fn `def load_env_file() -> dict[str, str]` (L422-440)
- @brief Execute load env file.
- @details Applies load env file logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {dict[str, str]} Function return value.

### fn `def write_env_file(updates: dict[str, str]) -> None` (L441-480)
- @brief Execute write env file.
- @details Applies write env file logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param updates {dict[str, str]} Input parameter `updates`.
- @return {None} Function return value.

### class `class Config` (L481-677)
- @brief Define config component.
- @details Encapsulates config state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `ENV_VARS =` (L488)
- var `PROVIDER_INFO =` (L498)
- fn `def get_token(self, provider: ProviderName) -> str | None` (L537-580)
  - @brief Execute get token.
  - @details Applies get token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @return {str | None} Function return value.
- fn `def is_provider_configured(self, provider: ProviderName) -> bool` (L581-612)
  - @brief Execute is provider configured.
  - @details Applies is provider configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @return {bool} Function return value.
- fn `def get_provider_status(self, provider: ProviderName) -> dict[str, Any]` (L613-634)
  - @brief Execute get provider status.
  - @details Applies get provider status logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @return {dict[str, Any]} Function return value.
- fn `def get_all_provider_status(self) -> list[dict[str, Any]]` (L635-642)
  - @brief Execute get all provider status.
  - @details Applies get all provider status logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {list[dict[str, Any]]} Function return value.
- fn `def _get_token_preview(self, provider: ProviderName) -> str | None` `priv` (L643-654)
  - @brief Execute get token preview.
  - @details Applies get token preview logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @return {str | None} Function return value.
- fn `def get_env_var_help(self) -> str` (L655-677)
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
|`DEFAULT_GNOME_REFRESH_INTERVAL_SECONDS`|var|pub|31||
|`DEFAULT_BILLING_DATASET`|var|pub|32||
|`DEFAULT_CURRENCY_SYMBOL`|var|pub|33||
|`LOCK_POLL_INTERVAL_SECONDS`|var|pub|35||
|`RuntimeConfig`|class|pub|44-73|class RuntimeConfig(BaseModel)|
|`IdleTimeState`|class|pub|74-88|class IdleTimeState(BaseModel)|
|`_ensure_app_config_dir`|fn|priv|89-98|def _ensure_app_config_dir() -> None|
|`_ensure_app_cache_dir`|fn|priv|99-108|def _ensure_app_cache_dir() -> None|
|`_lock_file_path`|fn|priv|109-120|def _lock_file_path(target_path: Path) -> Path|
|`_blocking_file_lock`|fn|priv|122-150|def _blocking_file_lock(target_path: Path)|
|`_sanitize_cache_payload`|fn|priv|151-185|def _sanitize_cache_payload(payload: dict[str, Any]) -> d...|
|`clean`|fn|pub|163-182|def clean(value: Any) -> Any|
|`load_runtime_config`|fn|pub|186-202|def load_runtime_config() -> RuntimeConfig|
|`save_runtime_config`|fn|pub|203-218|def save_runtime_config(runtime_config: RuntimeConfig) ->...|
|`load_cli_cache`|fn|pub|219-238|def load_cli_cache() -> dict[str, Any] | None|
|`resolve_currency_symbol`|fn|pub|239-268|def resolve_currency_symbol(raw: dict[str, Any] | None, p...|
|`save_cli_cache`|fn|pub|269-292|def save_cli_cache(payload: dict[str, Any]) -> None|
|`build_idle_time_state`|fn|pub|293-325|def build_idle_time_state(last_success_at: datetime, idle...|
|`load_idle_time`|fn|pub|326-354|def load_idle_time() -> dict[str, IdleTimeState]|
|`save_idle_time`|fn|pub|355-388|def save_idle_time(idle_time_by_provider: dict[str, IdleT...|
|`remove_idle_time_file`|fn|pub|389-404|def remove_idle_time_file() -> None|
|`get_api_call_timeout_seconds`|fn|pub|405-421|def get_api_call_timeout_seconds() -> float|
|`load_env_file`|fn|pub|422-440|def load_env_file() -> dict[str, str]|
|`write_env_file`|fn|pub|441-480|def write_env_file(updates: dict[str, str]) -> None|
|`Config`|class|pub|481-677|class Config|
|`Config.ENV_VARS`|var|pub|488||
|`Config.PROVIDER_INFO`|var|pub|498||
|`Config.get_token`|fn|pub|537-580|def get_token(self, provider: ProviderName) -> str | None|
|`Config.is_provider_configured`|fn|pub|581-612|def is_provider_configured(self, provider: ProviderName) ...|
|`Config.get_provider_status`|fn|pub|613-634|def get_provider_status(self, provider: ProviderName) -> ...|
|`Config.get_all_provider_status`|fn|pub|635-642|def get_all_provider_status(self) -> list[dict[str, Any]]|
|`Config._get_token_preview`|fn|priv|643-654|def _get_token_preview(self, provider: ProviderName) -> s...|
|`Config.get_env_var_help`|fn|pub|655-677|def get_env_var_help(self) -> str|


---

# extension.js | JavaScript | 1717L | 32 symbols | 9 imports | 39 comments
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
- const `const PROVIDER_PROGRESS_CLASSES = {` (L23)
- const `const PANEL_ICON_COLORS = {` (L31)
- const `const PROVIDER_DISPLAY_NAMES = {` (L38)
- const `const API_COUNTER_PROVIDERS = new Set(['openai', 'openrouter', 'codex', 'geminiai']);` (L41)
- const `const WINDOW_BAR_30D_PROVIDERS = new Set(['copilot', 'openrouter', 'openai', 'geminiai']);` (L42)
### fn `function _getProviderDisplayName(providerName)` (L49-53)
- @brief Resolve provider label text for GNOME tab/card rendering.
- @param {string} providerName Provider key from JSON payload.
- @return s {string} Display label for provider tab and card.

### fn `function _providerSupportsApiCounters(providerName)` (L63-65)
- @brief Check whether provider cards must render API counter labels.
- @details API-counter providers render `requests` and `tokens` labels on OK states
with null/undefined counters normalized to zero.
- @param {string} providerName Provider key from JSON payload.
- @return s {boolean} True when provider requires API counter label rendering.
- @satisfies REQ-017

### fn `function _formatLocalDateTime(value)` (L73-84)
- @brief Format one Date object as local datetime for provider freshness labels.
- @details Produces `%Y-%m-%d %H:%M` in runtime local timezone; invalid Date values return null.
- @param {Date} value Date object to format.
- @return s {string | null} Formatted local datetime string or null.

### fn `function _coerceRetryAfterSeconds(value)` (L91-101)
- @brief Normalize retry-after value to positive integer seconds.
- @param {any} value Retry-after candidate value.
- @return s {number | null} Integer retry-after seconds or null when unavailable.

### fn `function _buildHttpStatusRetryLabel(statusCodeRaw, retryAfterRaw)` (L110-120)
- @brief Build normalized HTTP status/retry metadata label.
- @param {any} statusCodeRaw HTTP status candidate value.
- @param {any} retryAfterRaw Retry-after candidate value.
- @return s {string} Diagnostic label text or empty string.
- @satisfies REQ-037

### fn `function _escapeMarkup(value)` (L127-134)
- @brief Escape text for safe Pango markup insertion.
- @param {string} value Raw text.
- @return s {string} Markup-safe text.

### fn `function _boldWhiteMarkup(value)` (L141-143)
- @brief Wrap one value as bright-white bold Pango markup.
- @param {string} value Raw text value.
- @return s {string} Bright-white bold markup snippet.

### fn `function _buildFallbackFreshnessState(statusEntry, idleDelaySeconds)` (L155-176)
- @brief Build provider freshness fallback from cache-status `updated_at` metadata.
- @details Converts `statusEntry.updated_at` to epoch seconds and derives
`idle_until_timestamp` using configured idle-delay seconds when `freshness`/`idle_time`
sections are unavailable from CLI JSON output.
- @param {any} statusEntry Window-specific cache status entry.
- @param {number} idleDelaySeconds Active idle delay in seconds.
- @return s {{last_success_timestamp: number, idle_until_timestamp: number} | null} Fallback freshness state or null.
- @satisfies REQ-017

### fn `function _resolveProviderFreshnessState(freshnessData, providerName, statusEntry, idleDelaySeconds)` (L190-204)
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

### fn `function _getAiBarPath()` (L211-221)
- @brief Resolve aibar executable path.
- @details Prefers PATH discovery and falls back to AIBAR_PATH from the env file.
- @return s {string} Resolved executable path or fallback command name.

### fn `function _loadEnvFromFile()` (L228-280)
- @brief Load key-value environment variables from aibar env file.
- @details Parses export syntax, quoted values, and inline comments.
- @return s {Object<string,string>} Parsed environment map.

### fn `function _getProviderProgressClass(providerName)` (L287-289)
- @brief Map percentage usage to CSS progress severity class.
- @param {number} pct Usage percentage.
- @return s {string} CSS class suffix for progress state.

### fn `function _isDisplayedZeroPercent(pct)` (L298-305)
- @brief Check whether a percentage renders as `0.0%` in one-decimal UI output.
- @details Mirrors display rounding semantics so fallback reset text is shown when
usage is effectively zero from the user's perspective (e.g. internal 0.04 -> 0.0%).
- @param {number} pct Usage percentage candidate.
- @return s {boolean} True when value is finite, non-negative, and rounds to 0.0.

### fn `function _isDisplayedFullPercent(pct)` (L314-319)
- @brief Check whether a percentage renders as `100.0%` in one-decimal UI output.
- @details Mirrors display rounding semantics so near-full values are treated as
full usage for limit-reached warning rendering.
- @param {number} pct Usage percentage candidate.
- @return s {boolean} True when value is finite and rounds to `100.0`.

### class `class AIBarIndicator extends PanelMenu.Button` : PanelMenu.Button (L323-622)
- @brief Panel indicator widget that manages popup rendering and refresh lifecycle. */
- @brief Execute init.
- @details Applies init logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
- @return s {any} Function return value.

### fn `const createWindowBar = (labelText) =>` (L732-778)
- @brief Execute create provider card.
- @details Applies create provider card logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
- @param {any} providerName Input parameter `providerName`.
- @return s {any} Function return value.

### fn `const updateWindowBar = (bar, pct, resetTime, useDays) =>` (L952-1010)
- @brief Execute populate provider card.
- @details Applies populate provider card logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
- @param {any} card Input parameter `card`.
- @param {any} providerName Input parameter `providerName`.
- @param {any} data Input parameter `data`.
- @param {any} statusEntry Window-specific cached status entry.
- @param {any} freshnessState Provider-scoped freshness entry from `freshness` section.
- @return s {any} Function return value.

### fn `const setResetLabel = (baseText) =>` (L958-964)

### fn `const showResetPendingHint = () =>` (L975-977)

### fn `const toPercent = (value) =>` (L1452-1457)
- @brief Execute update u i.
- @details Applies update u i logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
Resolves provider-window failure metadata from cache `status` section and forwards it
to card renderers. Panel status row renders fixed-order percentages and per-provider costs.
- @return s {any} Function return value.
- @satisfies REQ-021
- @satisfies REQ-053
- @satisfies REQ-069

### fn `const getPanelUsageValues = (providerName, data) =>` (L1459-1516)

### class `export default class AIBarExtension extends Extension` : Extension (L1691-1717)
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
|`PROVIDER_PROGRESS_CLASSES`|const||23||
|`PANEL_ICON_COLORS`|const||31||
|`PROVIDER_DISPLAY_NAMES`|const||38||
|`API_COUNTER_PROVIDERS`|const||41||
|`WINDOW_BAR_30D_PROVIDERS`|const||42||
|`_getProviderDisplayName`|fn||49-53|function _getProviderDisplayName(providerName)|
|`_providerSupportsApiCounters`|fn||63-65|function _providerSupportsApiCounters(providerName)|
|`_formatLocalDateTime`|fn||73-84|function _formatLocalDateTime(value)|
|`_coerceRetryAfterSeconds`|fn||91-101|function _coerceRetryAfterSeconds(value)|
|`_buildHttpStatusRetryLabel`|fn||110-120|function _buildHttpStatusRetryLabel(statusCodeRaw, retryA...|
|`_escapeMarkup`|fn||127-134|function _escapeMarkup(value)|
|`_boldWhiteMarkup`|fn||141-143|function _boldWhiteMarkup(value)|
|`_buildFallbackFreshnessState`|fn||155-176|function _buildFallbackFreshnessState(statusEntry, idleDe...|
|`_resolveProviderFreshnessState`|fn||190-204|function _resolveProviderFreshnessState(freshnessData, pr...|
|`_getAiBarPath`|fn||211-221|function _getAiBarPath()|
|`_loadEnvFromFile`|fn||228-280|function _loadEnvFromFile()|
|`_getProviderProgressClass`|fn||287-289|function _getProviderProgressClass(providerName)|
|`_isDisplayedZeroPercent`|fn||298-305|function _isDisplayedZeroPercent(pct)|
|`_isDisplayedFullPercent`|fn||314-319|function _isDisplayedFullPercent(pct)|
|`AIBarIndicator`|class||323-622|class AIBarIndicator extends PanelMenu.Button|
|`createWindowBar`|fn||732-778|const createWindowBar = (labelText) =>|
|`updateWindowBar`|fn||952-1010|const updateWindowBar = (bar, pct, resetTime, useDays) =>|
|`setResetLabel`|fn||958-964|const setResetLabel = (baseText) =>|
|`showResetPendingHint`|fn||975-977|const showResetPendingHint = () =>|
|`toPercent`|fn||1452-1457|const toPercent = (value) =>|
|`getPanelUsageValues`|fn||1459-1516|const getPanelUsageValues = (providerName, data) =>|
|`AIBarExtension`|class||1691-1717|export default class AIBarExtension extends Extension|


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

# claude_oauth.py | Python | 344L | 15 symbols | 12 imports | 18 comments
> Path: `src/aibar/aibar/providers/claude_oauth.py`
- @brief Claude OAuth usage provider.
- @details Fetches Claude subscription utilization through OAuth credentials and normalizes provider quota state into the shared result contract.

## Imports
```
import asyncio
import os
import random
from datetime import datetime
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

### fn `def _resolve_provider_currency(raw: dict, provider_name: str) -> str` `priv` (L26-39)
- @brief Resolve currency symbol for a provider from raw API response or config.
- @details Delegates to `resolve_currency_symbol` from `aibar.config`. Imported lazily inside the function to avoid circular import at module load time.
- @param raw {dict} Raw API response dict.
- @param provider_name {str} Provider name key.
- @return {str} Resolved currency symbol.
- @satisfies REQ-050

### class `class ClaudeOAuthProvider(BaseProvider)` : BaseProvider (L40-76)
- @brief Define claude o auth provider component.
- @details Encapsulates claude o auth provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `USAGE_URL = "https://api.anthropic.com/api/oauth/usage"` (L47)
  - @brief Define claude o auth provider component.
  - @details Encapsulates claude o auth provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `TOKEN_ENV_VAR = "CLAUDE_CODE_OAUTH_TOKEN"` (L48)
- fn `def __init__(self, token: str | None = None) -> None` `priv` (L50-60)
  - @brief Execute init.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param token {str | None} Input parameter `token`.
  - @return {None} Function return value.
- fn `def is_configured(self) -> bool` (L61-68)
  - @brief Execute is configured.
  - @details Applies is configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {bool} Function return value.
- fn `def get_config_help(self) -> str` (L69-76)
  - @brief Execute get config help.
  - @details Applies get config help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str} Function return value.

- var `MAX_RETRIES = 3` (L83)
- var `RETRY_BACKOFF_BASE = 2.0` (L84)
- var `RETRY_JITTER_MAX = 1.0` (L85)
### fn `async def _request_usage(self, client: httpx.AsyncClient) -> httpx.Response` `priv` (L87-126)
- @brief Execute HTTP GET to usage endpoint with retry on HTTP 429.
- @details Retries up to MAX_RETRIES times on 429 responses, respecting the retry-after header with exponential backoff fallback and random jitter to prevent thundering-herd synchronization. Backoff sequence with RETRY_BACKOFF_BASE=2.0: ~2-3s, ~4-5s, ~8-9s (total ~14-17s).
- @param client {httpx.AsyncClient} Reusable HTTP client session.
- @return {httpx.Response} Final HTTP response after retries exhausted or success.

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L127-168)
- @brief Execute fetch for a single window period.
- @details Makes one HTTP request to the usage endpoint (with retry on 429) and parses the response for the requested window.
- @param window {WindowPeriod} Window period to parse from the API response.
- @return {ProviderResult} Parsed result for the requested window.
- @throws {AuthenticationError} When the OAuth token is invalid or expired.
- @throws {ProviderError} On unexpected non-HTTP errors.

### fn `async def fetch_all_windows(` (L169-170)

### fn `def _handle_response(` `priv` (L225-226)

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L278-344)
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
|`_resolve_provider_currency`|fn|priv|26-39|def _resolve_provider_currency(raw: dict, provider_name: ...|
|`ClaudeOAuthProvider`|class|pub|40-76|class ClaudeOAuthProvider(BaseProvider)|
|`ClaudeOAuthProvider.USAGE_URL`|var|pub|47||
|`ClaudeOAuthProvider.TOKEN_ENV_VAR`|var|pub|48||
|`ClaudeOAuthProvider.__init__`|fn|priv|50-60|def __init__(self, token: str | None = None) -> None|
|`ClaudeOAuthProvider.is_configured`|fn|pub|61-68|def is_configured(self) -> bool|
|`ClaudeOAuthProvider.get_config_help`|fn|pub|69-76|def get_config_help(self) -> str|
|`MAX_RETRIES`|var|pub|83||
|`RETRY_BACKOFF_BASE`|var|pub|84||
|`RETRY_JITTER_MAX`|var|pub|85||
|`_request_usage`|fn|priv|87-126|async def _request_usage(self, client: httpx.AsyncClient)...|
|`fetch`|fn|pub|127-168|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`fetch_all_windows`|fn|pub|169-170|async def fetch_all_windows(|
|`_handle_response`|fn|priv|225-226|def _handle_response(|
|`_parse_response`|fn|priv|278-344|def _parse_response(self, data: dict, window: WindowPerio...|


---

# codex.py | Python | 447L | 22 symbols | 9 imports | 33 comments
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

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L312-393)
- @brief Execute fetch.
- @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L394-447)
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
|`fetch`|fn|pub|312-393|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|394-447|def _parse_response(self, data: dict, window: WindowPerio...|


---

# copilot.py | Python | 440L | 28 symbols | 12 imports | 32 comments
> Path: `src/aibar/aibar/providers/copilot.py`
- @brief GitHub Copilot usage provider and device-flow authentication.
- @details Handles device-code authorization, token storage resolution, Copilot quota retrieval, and normalization to provider result schema.

## Imports
```
import json
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
```

## Definitions

### fn `def _resolve_provider_currency(raw: dict, provider_name: str) -> str` `priv` (L26-38)
- @brief Resolve currency symbol from raw API response or configured provider default.
- @details Delegates to `resolve_currency_symbol` in `aibar.config` (lazy import).
- @param raw {dict} Raw API response dict.
- @param provider_name {str} Provider name key.
- @return {str} Resolved currency symbol.
- @satisfies REQ-050

### class `class CopilotDeviceFlow` (L39-131)
- @brief Define copilot device flow component.
- @details Encapsulates copilot device flow state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `CLIENT_ID = "Iv1.b507a08c87ecfe98"` (L46)
- var `SCOPES = "read:user"` (L47)
- var `DEVICE_CODE_URL = "https://github.com/login/device/code"` (L49)
- var `TOKEN_URL = "https://github.com/login/oauth/access_token"` (L50)
- fn `async def request_device_code(self) -> dict[str, Any]` (L52-78)
  - @brief Execute request device code.
  - @details Applies request device code logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {dict[str, Any]} Function return value.
  - @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.
- fn `async def poll_for_token(self, device_code: str, interval: int = 5) -> str` (L79-131)
  - @brief Execute poll for token.
  - @details Applies poll for token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param device_code {str} Input parameter `device_code`.
  - @param interval {int} Input parameter `interval`.
  - @return {str} Function return value.
  - @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### class `class CopilotCredentialStore` (L132-188)
- @brief Define copilot credential store component.
- @details Encapsulates copilot credential store state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `CONFIG_DIR = Path.home() / ".config" / "aibar"` (L138)
  - @brief Define copilot credential store component.
  - @details Encapsulates copilot credential store state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `CREDS_FILE = CONFIG_DIR / "copilot.json"` (L139)
- var `CODEXBAR_CONFIG = Path.home() / ".codexbar" / "config.json"` (L140)
- fn `def load_token(self) -> str | None` (L142-173)
  - @brief Execute load token.
  - @details Applies load token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str | None} Function return value.
- fn `def save_token(self, token: str) -> None` (L174-188)
  - @brief Execute save token.
  - @details Applies save token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param token {str} Input parameter `token`.
  - @return {None} Function return value.

### class `class CopilotProvider(BaseProvider)` : BaseProvider (L189-229)
- @brief Define copilot provider component.
- @details Encapsulates copilot provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `USAGE_URL = "https://api.github.com/copilot_internal/user"` (L196)
  - @brief Define copilot provider component.
  - @details Encapsulates copilot provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `EDITOR_VERSION = "vscode/1.96.2"` (L199)
- var `PLUGIN_VERSION = "copilot-chat/0.26.7"` (L200)
- var `USER_AGENT = "GitHubCopilotChat/0.26.7"` (L201)
- var `API_VERSION = "2025-04-01"` (L202)
- fn `def __init__(self, token: str | None = None) -> None` `priv` (L204-213)
  - @brief Execute init.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param token {str | None} Input parameter `token`.
  - @return {None} Function return value.
- fn `def is_configured(self) -> bool` (L214-221)
  - @brief Execute is configured.
  - @details Applies is configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {bool} Function return value.
- fn `def get_config_help(self) -> str` (L222-229)
  - @brief Execute get config help.
  - @details Applies get config help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str} Function return value.

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L239-312)
- @brief Execute fetch.
- @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L313-409)
- @brief Execute parse response.
- @details Applies parse response logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param data {dict} Input parameter `data`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.

### fn `def _get_snapshot(key_camel: str, key_snake: str) -> dict` `priv` (L323-332)
- @brief Execute parse response.
- @brief Execute get snapshot.
- @details Applies parse response logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @details Applies get snapshot logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param data {dict} Input parameter `data`.
- @param window {WindowPeriod} Input parameter `window`.
- @param key_camel {str} Input parameter `key_camel`.
- @param key_snake {str} Input parameter `key_snake`.
- @return {ProviderResult} Function return value.
- @return {dict} Function return value.

### fn `def _extract_quota_data(snapshot: dict) -> tuple[float | None, float | None]` `priv` (L333-359)
- @brief Execute extract quota data.
- @details Applies extract quota data logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param snapshot {dict} Input parameter `snapshot`.
- @return {tuple[float | None, float | None]} Function return value.

### fn `async def login(self) -> str` (L410-440)
- @brief Execute login.
- @details Applies login logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {str} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`_resolve_provider_currency`|fn|priv|26-38|def _resolve_provider_currency(raw: dict, provider_name: ...|
|`CopilotDeviceFlow`|class|pub|39-131|class CopilotDeviceFlow|
|`CopilotDeviceFlow.CLIENT_ID`|var|pub|46||
|`CopilotDeviceFlow.SCOPES`|var|pub|47||
|`CopilotDeviceFlow.DEVICE_CODE_URL`|var|pub|49||
|`CopilotDeviceFlow.TOKEN_URL`|var|pub|50||
|`CopilotDeviceFlow.request_device_code`|fn|pub|52-78|async def request_device_code(self) -> dict[str, Any]|
|`CopilotDeviceFlow.poll_for_token`|fn|pub|79-131|async def poll_for_token(self, device_code: str, interval...|
|`CopilotCredentialStore`|class|pub|132-188|class CopilotCredentialStore|
|`CopilotCredentialStore.CONFIG_DIR`|var|pub|138||
|`CopilotCredentialStore.CREDS_FILE`|var|pub|139||
|`CopilotCredentialStore.CODEXBAR_CONFIG`|var|pub|140||
|`CopilotCredentialStore.load_token`|fn|pub|142-173|def load_token(self) -> str | None|
|`CopilotCredentialStore.save_token`|fn|pub|174-188|def save_token(self, token: str) -> None|
|`CopilotProvider`|class|pub|189-229|class CopilotProvider(BaseProvider)|
|`CopilotProvider.USAGE_URL`|var|pub|196||
|`CopilotProvider.EDITOR_VERSION`|var|pub|199||
|`CopilotProvider.PLUGIN_VERSION`|var|pub|200||
|`CopilotProvider.USER_AGENT`|var|pub|201||
|`CopilotProvider.API_VERSION`|var|pub|202||
|`CopilotProvider.__init__`|fn|priv|204-213|def __init__(self, token: str | None = None) -> None|
|`CopilotProvider.is_configured`|fn|pub|214-221|def is_configured(self) -> bool|
|`CopilotProvider.get_config_help`|fn|pub|222-229|def get_config_help(self) -> str|
|`fetch`|fn|pub|239-312|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|313-409|def _parse_response(self, data: dict, window: WindowPerio...|
|`_get_snapshot`|fn|priv|323-332|def _get_snapshot(key_camel: str, key_snake: str) -> dict|
|`_extract_quota_data`|fn|priv|333-359|def _extract_quota_data(snapshot: dict) -> tuple[float | ...|
|`login`|fn|pub|410-440|async def login(self) -> str|


---

# geminiai.py | Python | 995L | 46 symbols | 20 imports | 39 comments
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

### fn `def _extract_google_api_status(error: GoogleAPICallError) -> int` `priv` (L108-128)
- @brief Extract HTTP-like status code from Google API Core exceptions.
- @details Normalizes exception `code` payloads to integer status values and returns `0` when status is unavailable.
- @param error {GoogleAPICallError} Google API Core exception.
- @return {int} Status code or `0`.

### fn `def _is_scope_insufficient_error(error: Exception) -> bool` `priv` (L129-152)
- @brief Determine whether exception payload indicates OAuth scope insufficiency.
- @details Matches Google API error reason `ACCESS_TOKEN_SCOPE_INSUFFICIENT` and equivalent human-readable messages.
- @param error {Exception} Exception to inspect.
- @return {bool} True when the error indicates insufficient OAuth scopes.

### class `class GeminiAIWindowRange` `@dataclass(frozen=True)` (L154-163)
- @brief Immutable time-range descriptor for one GeminiAI fetch window.
- @details Encodes start and end UTC timestamps used for Monitoring API queries.

### class `class GeminiAICredentialStore` (L164-363)
- @brief OAuth credential persistence and validation helper for GeminiAI.
- @details Manages client-secret JSON validation, token-file persistence, and interactive InstalledAppFlow authorization.
- fn `def __init__(` `priv` (L171-174)
  - @brief OAuth credential persistence and validation helper for GeminiAI.
  - @details Manages client-secret JSON validation, token-file persistence, and
interactive InstalledAppFlow authorization.
- fn `def _ensure_config_dir(self) -> None` `priv` (L185-192)
  - @brief Initialize credential store with optional custom file paths.
  - @brief Create parent directories for OAuth files when missing.
  - @param client_config_path {Path | None} Optional OAuth client config path.
  - @param token_path {Path | None} Optional OAuth token path.
  - @return {None} Function return value.
  - @return {None} Function return value.
- fn `def has_client_config(self) -> bool` (L193-199)
  - @brief Check whether GeminiAI client config JSON exists.
  - @return {bool} True when client config file exists.
- fn `def has_authorized_credentials(self) -> bool` (L200-210)
  - @brief Check whether GeminiAI authorized token material exists.
  - @details Environment access-token override is treated as configured token material.
  - @return {bool} True when token file or env token is available.
- fn `def validate_client_config(self, payload: dict[str, Any]) -> dict[str, Any]` (L211-240)
  - @brief Validate Google InstalledApp OAuth client-secret payload.
  - @details Enforces required `installed` section fields used by `InstalledAppFlow.from_client_config`.
  - @param payload {dict[str, Any]} Decoded JSON payload to validate.
  - @return {dict[str, Any]} Normalized payload.
  - @throws {ValueError} When required fields are missing or malformed.
- fn `def save_client_config(self, payload: dict[str, Any]) -> None` (L241-253)
  - @brief Persist validated OAuth client config JSON to disk.
  - @param payload {dict[str, Any]} Validated client payload.
  - @return {None} Function return value.
- fn `def load_client_config(self) -> dict[str, Any]` (L254-272)
  - @brief Load and validate persisted OAuth client config JSON.
  - @return {dict[str, Any]} Validated OAuth client payload.
  - @throws {FileNotFoundError} When client config file is missing.
  - @throws {ValueError} When payload is invalid JSON or fails validation.
- fn `def extract_project_id(self, payload: dict[str, Any]) -> str | None` (L273-286)
  - @brief Extract project_id from validated OAuth payload.
  - @param payload {dict[str, Any]} Validated OAuth payload.
  - @return {str | None} Project identifier or None when absent.
- fn `def save_authorized_credentials(self, credentials: Credentials) -> None` (L287-296)
  - @brief Persist authorized-user OAuth credentials JSON.
  - @param credentials {Credentials} Google OAuth credentials object.
  - @return {None} Function return value.
- fn `def authorize_interactively(` (L297-299)
- fn `def load_access_token(self) -> str | None` (L315-332)
  - @brief Execute OAuth browser flow and persist refresh-capable credentials.
  - @brief Load access token from env override or token file.
  - @details Uses InstalledAppFlow local-server flow (`http://localhost`) and
saves authorized-user token JSON to disk.
  - @param scopes {tuple[str, ...]} OAuth scopes requested during authorization.
  - @return {Credentials} Authorized credentials.
  - @return {str | None} Access token or None when unavailable.
  - @throws {ValueError} When client config is invalid.
- fn `def load_credentials(` (L333-335)

### class `class GeminiAIProvider(BaseProvider)` : BaseProvider (L367-443)
- @brief GeminiAI usage provider backed by Monitoring and BigQuery APIs.
- @details Retrieves Generative Language API usage counters and status telemetry from Cloud Monitoring, retrieves latest-available billing-period costs from BigQuery export, then maps data into AIBar `ProviderResult` models.
- var `SERVICE_FILTER = 'resource.labels.service="generativelanguage.googleapis.com"'` (L377)
  - @brief GeminiAI usage provider backed by Monitoring and BigQuery APIs.
  - @details Retrieves Generative Language API usage counters and status telemetry
from Cloud Monitoring, retrieves latest-available billing-period costs from BigQuery export,
then maps data into AIBar `ProviderResult` models.
- var `REQUEST_COUNT_FILTER = REQUEST_COUNT_FILTERS[0]` (L387)
- var `LATENCY_FILTER = (` (L403)
- var `ERROR_FILTER = (` (L406)
- fn `def __init__(` `priv` (L412-415)
- fn `def is_configured(self) -> bool` (L426-435)
  - @brief Initialize GeminiAI provider with optional overrides.
  - @brief Check whether GeminiAI provider has required auth and project metadata.
  - @param credential_store {GeminiAICredentialStore | None} Optional credential store.
  - @param project_id {str | None} Optional project id override.
  - @return {None} Function return value.
  - @return {bool} True when project id and OAuth token material are available.
- fn `def get_config_help(self) -> str` (L436-443)
  - @brief Return setup guidance for GeminiAI OAuth configuration.
  - @return {str} Provider-specific setup instructions.

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L452-479)
- @brief Fetch GeminiAI monitoring usage metrics for one window.
- @details Executes synchronous Google API calls in a worker thread and returns normalized provider metrics. HTTP 429 responses are normalized as rate-limit provider error payloads with retry-after metadata.
- @param window {WindowPeriod} Requested window period.
- @return {ProviderResult} Provider result payload.
- @throws {AuthenticationError} When OAuth credentials are invalid.

### fn `def _fetch_sync(self, window: WindowPeriod) -> ProviderResult` `priv` (L480-648)
- @brief Execute blocking Google API retrieval flow for GeminiAI metrics.
- @param window {WindowPeriod} Requested window period.
- @return {ProviderResult} Normalized provider result.
- @throws {AuthenticationError} When credentials are missing/invalid.
- @throws {ProviderError} On non-auth API failures.

### fn `def _build_window_range(self, window: WindowPeriod) -> GeminiAIWindowRange` `priv` (L649-667)
- @brief Build current-month UTC interval used for Monitoring queries.
- @details Uses `[UTC month start, current UTC time]` to align Monitoring usage aggregation with current-month GeminiAI billing semantics.
- @param window {WindowPeriod} Requested window period (ignored by interval policy).
- @return {GeminiAIWindowRange} Start/end UTC timestamps.
- @satisfies REQ-098

### fn `def _resolve_project_id(self) -> str | None` `priv` (L668-689)
- @brief Resolve project id from override, env, runtime config, or client JSON.
- @return {str | None} Project id or None when unresolved.

### fn `def _resolve_billing_dataset(self) -> str` `priv` (L690-706)
- @brief Resolve billing dataset id from runtime configuration.
- @details Uses `RuntimeConfig.billing_data` and falls back to `DEFAULT_BILLING_DATASET_ID` when configuration is empty.
- @return {str} BigQuery billing dataset id.
- @satisfies REQ-005
- @satisfies REQ-064

### fn `def _build_monitoring_service(self, credentials: Credentials) -> Any` `priv` (L707-714)
- @brief Build Google Cloud Monitoring API client.
- @param credentials {Credentials} OAuth credentials.
- @return {Any} Monitoring service client.

### fn `def _build_bigquery_client(` `priv` (L715-718)

### fn `def _discover_billing_table_id(` `priv` (L730-734)
- @brief Build BigQuery client for GeminiAI billing export queries.
- @param credentials {Credentials} OAuth credentials with BigQuery read scope.
- @param project_id {str} Google Cloud project id.
- @return {bigquery.Client} BigQuery API client.
- @satisfies REQ-056
- @satisfies REQ-065

### fn `def _query_current_month_billing_cost(` `priv` (L760-765)
- @brief Discover billing export table id in configured billing dataset.
- @details Lists dataset tables and selects the first lexicographically sorted
id that starts with `gcp_billing_export_v1_`.
- @param bigquery_client {bigquery.Client} BigQuery client.
- @param project_id {str} Google Cloud project id.
- @param dataset_id {str} BigQuery dataset id configured by setup.
- @return {str} Billing export table id.
- @throws {ProviderError} When billing export table is unavailable.
- @satisfies REQ-064

### fn `def _coerce_float(self, value: Any) -> float` `priv` (L841-860)
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

### fn `def _query_monitoring_metric(` `priv` (L861-868)

### fn `def _sum_time_series_values(self, response: dict[str, Any]) -> float | None` `priv` (L907-959)
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

### fn `def _build_metrics(` `priv` (L960-965)

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
|`_extract_google_api_status`|fn|priv|108-128|def _extract_google_api_status(error: GoogleAPICallError)...|
|`_is_scope_insufficient_error`|fn|priv|129-152|def _is_scope_insufficient_error(error: Exception) -> bool|
|`GeminiAIWindowRange`|class|pub|154-163|class GeminiAIWindowRange|
|`GeminiAICredentialStore`|class|pub|164-363|class GeminiAICredentialStore|
|`GeminiAICredentialStore.__init__`|fn|priv|171-174|def __init__(|
|`GeminiAICredentialStore._ensure_config_dir`|fn|priv|185-192|def _ensure_config_dir(self) -> None|
|`GeminiAICredentialStore.has_client_config`|fn|pub|193-199|def has_client_config(self) -> bool|
|`GeminiAICredentialStore.has_authorized_credentials`|fn|pub|200-210|def has_authorized_credentials(self) -> bool|
|`GeminiAICredentialStore.validate_client_config`|fn|pub|211-240|def validate_client_config(self, payload: dict[str, Any])...|
|`GeminiAICredentialStore.save_client_config`|fn|pub|241-253|def save_client_config(self, payload: dict[str, Any]) -> ...|
|`GeminiAICredentialStore.load_client_config`|fn|pub|254-272|def load_client_config(self) -> dict[str, Any]|
|`GeminiAICredentialStore.extract_project_id`|fn|pub|273-286|def extract_project_id(self, payload: dict[str, Any]) -> ...|
|`GeminiAICredentialStore.save_authorized_credentials`|fn|pub|287-296|def save_authorized_credentials(self, credentials: Creden...|
|`GeminiAICredentialStore.authorize_interactively`|fn|pub|297-299|def authorize_interactively(|
|`GeminiAICredentialStore.load_access_token`|fn|pub|315-332|def load_access_token(self) -> str | None|
|`GeminiAICredentialStore.load_credentials`|fn|pub|333-335|def load_credentials(|
|`GeminiAIProvider`|class|pub|367-443|class GeminiAIProvider(BaseProvider)|
|`GeminiAIProvider.SERVICE_FILTER`|var|pub|377||
|`GeminiAIProvider.REQUEST_COUNT_FILTER`|var|pub|387||
|`GeminiAIProvider.LATENCY_FILTER`|var|pub|403||
|`GeminiAIProvider.ERROR_FILTER`|var|pub|406||
|`GeminiAIProvider.__init__`|fn|priv|412-415|def __init__(|
|`GeminiAIProvider.is_configured`|fn|pub|426-435|def is_configured(self) -> bool|
|`GeminiAIProvider.get_config_help`|fn|pub|436-443|def get_config_help(self) -> str|
|`fetch`|fn|pub|452-479|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_fetch_sync`|fn|priv|480-648|def _fetch_sync(self, window: WindowPeriod) -> ProviderRe...|
|`_build_window_range`|fn|priv|649-667|def _build_window_range(self, window: WindowPeriod) -> Ge...|
|`_resolve_project_id`|fn|priv|668-689|def _resolve_project_id(self) -> str | None|
|`_resolve_billing_dataset`|fn|priv|690-706|def _resolve_billing_dataset(self) -> str|
|`_build_monitoring_service`|fn|priv|707-714|def _build_monitoring_service(self, credentials: Credenti...|
|`_build_bigquery_client`|fn|priv|715-718|def _build_bigquery_client(|
|`_discover_billing_table_id`|fn|priv|730-734|def _discover_billing_table_id(|
|`_query_current_month_billing_cost`|fn|priv|760-765|def _query_current_month_billing_cost(|
|`_coerce_float`|fn|priv|841-860|def _coerce_float(self, value: Any) -> float|
|`_query_monitoring_metric`|fn|priv|861-868|def _query_monitoring_metric(|
|`_sum_time_series_values`|fn|priv|907-959|def _sum_time_series_values(self, response: dict[str, Any...|
|`_build_metrics`|fn|priv|960-965|def _build_metrics(|


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

# openrouter.py | Python | 211L | 11 symbols | 5 imports | 11 comments
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

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L64-134)
- @brief Execute fetch.
- @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L135-170)
- @brief Execute parse response.
- @details Applies parse response logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param data {dict} Input parameter `data`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.
- @satisfies REQ-050

### fn `def _get_usage(self, payload: dict, window: WindowPeriod) -> float` `priv` (L171-184)
- @brief Execute get usage.
- @details Applies get usage logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param payload {dict} Input parameter `payload`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {float} Function return value.

### fn `def _get_byok_usage(self, payload: dict, window: WindowPeriod) -> float` `priv` (L185-198)
- @brief Execute get byok usage.
- @details Applies get byok usage logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param payload {dict} Input parameter `payload`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {float} Function return value.

### fn `def _to_float(self, value: float | int | None) -> float` `priv` (L199-211)
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
|`fetch`|fn|pub|64-134|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|135-170|def _parse_response(self, data: dict, window: WindowPerio...|
|`_get_usage`|fn|priv|171-184|def _get_usage(self, payload: dict, window: WindowPeriod)...|
|`_get_byok_usage`|fn|priv|185-198|def _get_byok_usage(self, payload: dict, window: WindowPe...|
|`_to_float`|fn|priv|199-211|def _to_float(self, value: float | int | None) -> float|

