# Files Structure
```
.
├── scripts
│   ├── aibar.sh
│   ├── claude_token_refresh.sh
│   ├── install-gnome-extension.sh
│   └── test-gnome-extension.sh
└── src
    └── aibar
        ├── aibar
        │   ├── __init__.py
        │   ├── __main__.py
        │   ├── cache.py
        │   ├── claude_cli_auth.py
        │   ├── cli.py
        │   ├── config.py
        │   ├── providers
        │   │   ├── __init__.py
        │   │   ├── base.py
        │   │   ├── claude_oauth.py
        │   │   ├── codex.py
        │   │   ├── copilot.py
        │   │   ├── openai_usage.py
        │   │   └── openrouter.py
        │   └── ui.py
        └── gnome-extension
            └── aibar@aibar.panel
                └── extension.js
```

# aibar.sh | Shell | 49L | 6 symbols | 2 imports | 18 comments
> Path: `scripts/aibar.sh`

## Imports
```
source ${VENVDIR}/bin/activate
source ${VENVDIR}/bin/activate
```

## Definitions

- var `FULL_PATH=$(readlink -f "$0")` (L9)
- var `SCRIPT_PATH=$(dirname "$FULL_PATH")` (L12)
- var `SCRIPT_NAME=$(basename "$FULL_PATH")` (L15)
- var `BASE_DIR=$(dirname "$SCRIPT_PATH")` (L18)
- var `VENVDIR="${BASE_DIR}/.venv"` (L26)
- var `PYTHONPATH="${BASE_DIR}/src/aibar:${PYTHONPATH}" \` (L48)
## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`FULL_PATH`|var||9||
|`SCRIPT_PATH`|var||12||
|`SCRIPT_NAME`|var||15||
|`BASE_DIR`|var||18||
|`VENVDIR`|var||26||
|`PYTHONPATH`|var||48||


---

# claude_token_refresh.sh | Shell | 164L | 12 symbols | 0 imports | 26 comments
> Path: `scripts/claude_token_refresh.sh`

## Definitions

- var `CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/aibar"` (L20)
- var `PID_FILE="$CONFIG_DIR/claude_token_refresh.pid"` (L21)
- var `LOG_FILE="$CONFIG_DIR/claude_token_refresh.log"` (L22)
- var `INTERVAL="${AIBAR_CLAUDE_REFRESH_INTERVAL_SECONDS:-1800}"` (L23)
- fn `log() {` (L29)
- fn `do_refresh() {` (L34)
- fn `run_loop() {` (L55)
- fn `is_running() {` (L65)
- fn `start_daemon() {` (L77)
- fn `stop_daemon() {` (L91)
- fn `show_status() {` (L112)
- fn `show_usage() {` (L126)
## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`CONFIG_DIR`|var||20||
|`PID_FILE`|var||21||
|`LOG_FILE`|var||22||
|`INTERVAL`|var||23||
|`log`|fn||29|log()|
|`do_refresh`|fn||34|do_refresh()|
|`run_loop`|fn||55|run_loop()|
|`is_running`|fn||65|is_running()|
|`start_daemon`|fn||77|start_daemon()|
|`stop_daemon`|fn||91|stop_daemon()|
|`show_status`|fn||112|show_status()|
|`show_usage`|fn||126|show_usage()|


---

# install-gnome-extension.sh | Shell | 160L | 18 symbols | 0 imports | 43 comments
> Path: `scripts/install-gnome-extension.sh`

## Definitions

- var `readonly C_RESET='\033[0m'` (L14)
- var `readonly C_BOLD='\033[1m'` (L15)
- var `readonly C_RED='\033[1;31m'` (L16)
- var `readonly C_GREEN='\033[1;32m'` (L17)
- var `readonly C_YELLOW='\033[1;33m'` (L18)
- var `readonly C_BLUE='\033[1;34m'` (L19)
- var `readonly C_CYAN='\033[1;36m'` (L20)
- var `readonly C_DIM='\033[2m'` (L21)
- fn `print_header() {` (L27)
- @brief Prints a formatted header banner.
- @param $1 {string} Header text.
- fn `info() {` (L37)
- @brief Prints an informational message.
- @param $* {string} Message text.
- fn `success() {` (L43)
- @brief Prints a success message.
- @param $* {string} Message text.
- fn `warn() {` (L49)
- @brief Prints a warning message.
- @param $* {string} Message text.
- fn `die() {` (L56)
- @brief Prints an error message to stderr and exits with status 1.
- @param $* {string} Error text.
- @return Does not return; exits with code 1.
- fn `step() {` (L65)
- @brief Prints a step progress marker.
- @param $1 {string} Step number.
- @param $2 {string} Step description.
- var `readonly EXT_UUID="aibar@aibar.panel"` (L70)
- var `readonly EXT_SRC_REL="src/aibar/gnome-extension/${EXT_UUID}"` (L71)
- var `readonly EXT_TARGET_DIR="${HOME}/.local/share/gnome-shell/extensions/${EXT_UUID}"` (L72)
- fn `main() {` (L81)
- @brief Main installation function.
- @details Executes sequential prerequisite checks (git availability, project root
resolution, source directory validation, metadata.json presence), creates the
target directory if absent, and copies all extension files preserving attributes.
- @return Exit 0 on success; exit 1 on any prerequisite failure.
## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`C_RESET`|var||14||
|`C_BOLD`|var||15||
|`C_RED`|var||16||
|`C_GREEN`|var||17||
|`C_YELLOW`|var||18||
|`C_BLUE`|var||19||
|`C_CYAN`|var||20||
|`C_DIM`|var||21||
|`print_header`|fn||27|print_header()|
|`info`|fn||37|info()|
|`success`|fn||43|success()|
|`warn`|fn||49|warn()|
|`die`|fn||56|die()|
|`step`|fn||65|step()|
|`EXT_UUID`|var||70||
|`EXT_SRC_REL`|var||71||
|`EXT_TARGET_DIR`|var||72||
|`main`|fn||81|main()|


---

# test-gnome-extension.sh | Shell | 34L | 3 symbols | 0 imports | 16 comments
> Path: `scripts/test-gnome-extension.sh`

## Definitions

- var `SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"` (L15)
- @brief Resolves the directory containing this script.
- @details Uses readlink -f to resolve symlinks, then extracts dirname.
- @return Absolute path to the script's parent directory.
- var `readonly INSTALL_SCRIPT="${SCRIPT_DIR}/install-gnome-extension.sh"` (L17)
- fn `update_extension() {` (L24)
- @brief Runs the extension installer to update extension files.
- @details Invokes install-gnome-extension.sh from the same scripts/ directory.
Exits with non-zero status if the installer fails.
- @return Exit 0 on success; propagates installer exit code on failure.
- @satisfies REQ-031
## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`SCRIPT_DIR`|var||15||
|`INSTALL_SCRIPT`|var||17||
|`update_extension`|fn||24|update_extension()|


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

# cli.py | Python | 1717L | 50 symbols | 18 imports | 68 comments
> Path: `src/aibar/aibar/cli.py`
- @brief Command-line interface for aibar.
- @details Defines command parsing, provider dispatch, formatted output, setup helpers, login flows, and UI launch hooks.

## Imports
```
import asyncio
import json
import math
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import click
from click.core import ParameterSource
from pydantic import ValidationError
from aibar.config import (
from aibar.providers import (
from aibar.providers.base import (
from datetime import datetime, timezone
from aibar.ui import run_ui
from aibar.config import (
from aibar.claude_cli_auth import ClaudeCLIAuth
from aibar.providers.copilot import CopilotProvider
```

## Definitions

### class `class RetrievalPipelineOutput` `@dataclass(frozen=True)` (L59-85)
- @brief Define shared provider-retrieval pipeline output.
- @details Encodes deterministic retrieval state produced by the shared cache-based pipeline used by `show` and Text UI refresh execution. The pipeline enforces force-flag handling, idle-time gating, conditional refresh into `cache.json`, and post-refresh readback from `cache.json`.
- @note `payload` contains cache JSON sections: `payload` and `status`.
- @note `results` contains validated ProviderResult objects keyed by provider id.
- @note `idle_active` indicates that idle-time gating blocked refresh.
- @note `cache_available` indicates `cache.json` was readable for this run.
- @satisfies REQ-009
- @satisfies REQ-039
- @satisfies REQ-042
- @satisfies REQ-043
- @satisfies REQ-044
- @satisfies REQ-045
- @satisfies REQ-046
- @satisfies REQ-047

### fn `def _normalize_utc(value: datetime) -> datetime` `priv` (L86-98)
- @brief Normalize datetime values to timezone-aware UTC instances.
- @details Ensures consistent timestamp arithmetic for idle-time persistence and refresh-delay computations when source datetimes are naive or non-UTC.
- @param value {datetime} Source datetime to normalize.
- @return {datetime} Timezone-aware UTC datetime.

### fn `def _apply_api_call_delay(throttle_state: dict[str, float | int] | None) -> None` `priv` (L99-127)
- @brief Enforce minimum spacing between consecutive provider API calls.
- @details Uses monotonic clock values in `throttle_state` to sleep before a live API request when elapsed time is below configured delay.
- @param throttle_state {dict[str, float | int] | None} Mutable state containing `delay_seconds` and `last_call_started`.
- @return {None} Function return value.
- @satisfies REQ-040

### fn `def _extract_retry_after_seconds(result: ProviderResult) -> int` `priv` (L128-146)
- @brief Extract normalized retry-after seconds from provider error payload.
- @details Reads `raw.retry_after_seconds` and clamps to non-negative integer seconds. Invalid or missing values normalize to zero.
- @param result {ProviderResult} Provider result to inspect.
- @return {int} Non-negative retry-after delay in seconds.
- @satisfies REQ-041

### fn `def _is_http_429_result(result: ProviderResult) -> bool` `priv` (L147-157)
- @brief Check whether result payload represents HTTP 429 rate limiting.
- @details Uses normalized raw payload marker `status_code == 429`.
- @param result {ProviderResult} Provider result to classify.
- @return {bool} True when result indicates HTTP 429.
- @satisfies REQ-041

### fn `def _serialize_results_payload(` `priv` (L158-159)

### fn `def _empty_cache_document() -> dict[str, object]` `priv` (L173-187)
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

### fn `def _normalize_cache_document(cache_document: dict[str, object] | None) -> dict[str, object]` `priv` (L188-209)
- @brief Normalize decoded cache payload to canonical sectioned schema.
- @details Accepts decoded cache document and enforces object-typed `payload` and `status` sections. Missing or invalid sections normalize to empty objects.
- @param cache_document {dict[str, object] | None} Decoded cache payload from disk.
- @return {dict[str, object]} Canonical cache document with `payload`/`status`.
- @satisfies CTN-004
- @satisfies REQ-003

### fn `def _cache_payload_section(cache_document: dict[str, object]) -> dict[str, object]` `priv` (L210-222)
- @brief Extract payload section from canonical cache document.
- @details Returns mutable provider-result mapping from normalized document.
- @param cache_document {dict[str, object]} Canonical cache document.
- @return {dict[str, object]} Provider payload section.

### fn `def _cache_status_section(cache_document: dict[str, object]) -> dict[str, object]` `priv` (L223-235)
- @brief Extract status section from canonical cache document.
- @details Returns mutable provider/window status mapping from normalized document.
- @param cache_document {dict[str, object]} Canonical cache document.
- @return {dict[str, object]} Provider/window status section.

### fn `def _serialize_attempt_status(result: ProviderResult) -> dict[str, object]` `priv` (L236-254)
- @brief Serialize one provider/window fetch attempt status for cache persistence.
- @details Converts ProviderResult error state to status object using `OK`/`FAIL`, preserving error text, update timestamp, and optional HTTP status code.
- @param result {ProviderResult} Provider result from current refresh attempt.
- @return {dict[str, object]} Attempt-status payload.
- @satisfies REQ-044

### fn `def _record_attempt_status(` `priv` (L255-257)

### fn `def _extract_claude_snapshot_from_cache_document(` `priv` (L277-278)
- @brief Persist one provider/window attempt status into cache status section.
- @details Upserts `status[provider][window]` with serialized attempt metadata and
preserves statuses for untouched providers/windows.
- @param status_section {dict[str, object]} Mutable cache status section.
- @param result {ProviderResult} Provider result to encode.
- @return {None} Function return value.
- @satisfies REQ-044
- @satisfies REQ-046

### fn `def _get_window_attempt_status(` `priv` (L293-296)
- @brief Extract persisted Claude dual-window payload from cache document.
- @details Reads Claude entry from cache `payload` section and normalizes it into
a dual-window raw payload (`five_hour`, `seven_day`) for HTTP 429 restoration.
- @param cache_document {dict[str, object]} Canonical cache document.
- @return {dict[str, object] | None} Normalized dual-window payload or None.
- @satisfies REQ-047

### fn `def _is_failed_http_429_status(status_entry: dict[str, object] | None) -> bool` `priv` (L316-330)
- @brief Read provider/window attempt status from cache status section.
- @brief Check whether status entry represents failed HTTP 429 attempt.
- @details Resolves nested `status[provider][window]` object and validates mapping
shape before returning it to projection helpers.
- @details Requires `result=FAIL` and integer `status_code=429` in the window status object to trigger Claude partial-window overlay rendering.
- @param status_section {dict[str, object]} Cache status section.
- @param provider_key {str} Provider identifier.
- @param window {WindowPeriod} Window identifier.
- @param status_entry {dict[str, object] | None} Provider/window status object.
- @return {dict[str, object] | None} Attempt status object or None.
- @return {bool} True when status marks failed HTTP 429 attempt.

### fn `def _filter_cached_payload(` `priv` (L331-333)

### fn `def _project_cached_window(` `priv` (L366-369)
- @brief Filter canonical cache document by optional provider selector.
- @details Filters both cache sections (`payload`, `status`) so selected-provider
output contains only relevant provider nodes while preserving schema keys.
- @param cache_document {dict[str, object]} Canonical cache document.
- @param provider_filter {ProviderName | None} Optional provider selector.
- @return {dict[str, object]} Filtered cache document with canonical sections.

### fn `def _load_cached_results(` `priv` (L400-404)
- @brief Project cached raw payload to requested window without network I/O.
- @details Attempts provider-specific `_parse_response` projection when cached
window differs from requested window; returns original result on projection
failure or when parser is unavailable.
- @param result {ProviderResult} Cached normalized provider result.
- @param target_window {WindowPeriod} Requested CLI window.
- @param providers {dict[ProviderName, BaseProvider]} Provider registry.
- @return {ProviderResult} Result aligned to requested window when possible.
- @satisfies REQ-009
- @satisfies REQ-042

### fn `def _update_idle_time_after_refresh(` `priv` (L453-455)
- @brief Decode cached JSON payload into ProviderResult mapping.
- @details Validates cached payload entries using `ProviderResult` schema, applies
provider filtering, and projects cached windows to requested window when possible.
Invalid entries are skipped.
- @param cache_document {dict[str, object]} Canonical cache document loaded from disk.
- @param provider_filter {ProviderName | None} Optional provider selector.
- @param target_window {WindowPeriod} Requested CLI window for projection.
- @param providers {dict[ProviderName, BaseProvider]} Provider registry.
- @return {dict[str, ProviderResult]} Validated cached results keyed by provider id.
- @satisfies REQ-009
- @satisfies REQ-042
- @satisfies REQ-044
- @satisfies REQ-046

### fn `def _project_next_reset(resets_at_str: str, window: WindowPeriod) -> datetime | None` `priv` (L504-535)
- @brief Persist idle-time metadata after refresh completion.
- @brief Compute the next reset boundary after a stale resets_at timestamp.
- @details Computes idle-until from last successful fetch timestamp plus
`idle_delay_seconds`; on HTTP 429, expands idle-until using the greater value
between idle-delay and maximum retry-after observed in the run.
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

### fn `def _apply_reset_projection(result: ProviderResult) -> ProviderResult` `priv` (L536-570)
- @brief Return a copy of `result` with `metrics.reset_at` set to the projected next reset boundary when it is currently None but the raw payload contains a parseable past `resets_at` string for the result's window.
- @details When a ProviderResult is obtained from stale disk cache (last-good path) or from a cross-window raw re-parse, `_parse_response` correctly sets `reset_at=None` for past timestamps. This function recovers the display information by projecting the next future reset boundary from the raw payload's `resets_at` field, ensuring the 'Resets in:' countdown is shown even when the cached timestamp has already elapsed. If `reset_at` is already non-None, or the raw payload has no parseable `resets_at` for the window, or projection fails, the original result is returned unchanged.
- @param result {ProviderResult} Candidate result whose reset_at may require projection.
- @return {ProviderResult} Original result unchanged if no projection is needed; otherwise a new ProviderResult with metrics.reset_at set to the projected datetime.
- @see _project_next_reset
- @satisfies REQ-002

### fn `def get_providers() -> dict[ProviderName, BaseProvider]` (L571-585)
- @brief Execute get providers.
- @details Applies get providers logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {dict[ProviderName, BaseProvider]} Function return value.

### fn `def parse_window(window: str) -> WindowPeriod` (L586-605)
- @brief Execute parse window.
- @details Applies parse window logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {str} Input parameter `window`.
- @return {WindowPeriod} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def parse_provider(provider: str) -> ProviderName | None` (L606-622)
- @brief Execute parse provider.
- @details Applies parse provider logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param provider {str} Input parameter `provider`.
- @return {ProviderName | None} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _fetch_result(` `priv` (L623-626)

### fn `def _fetch_claude_dual(` `priv` (L666-669)
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

### fn `def _extract_claude_dual_payload(` `priv` (L725-727)
- @brief Fetch Claude 5h and 7d results via a single API call.
- @details Executes ClaudeOAuthProvider.fetch_all_windows for 5h and 7d on each invocation.
If Claude returns HTTP 429 for both windows, normalize to a partial-window state
that preserves 5h error visibility and restores persisted reset/utilization
values for deterministic cache-backed rendering.
- @param provider {ClaudeOAuthProvider} Claude provider instance.
- @param throttle_state {dict[str, float | int] | None} Mutable throttling state
used to enforce inter-call spacing for live API requests.
- @param snapshot_payload {dict[str, object] | None} Last successful Claude
dual-window payload loaded from `cache.json`.
- @return {tuple[ProviderResult, ProviderResult]} (5h_result, 7d_result).
- @satisfies REQ-002, REQ-036, REQ-037, CTN-004, REQ-040, REQ-043, REQ-047

### fn `def _normalize_claude_dual_payload(payload: object) -> dict[str, object] | None` `priv` (L749-771)
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

### fn `def _extract_snapshot_reset_at(` `priv` (L772-774)

### fn `def _extract_snapshot_utilization(` `priv` (L797-799)
- @brief Resolve projected reset timestamp from persisted Claude snapshot payload.
- @details Uses window-specific `resets_at` string from persisted payload and
projects next reset boundary through `_project_next_reset`.
- @param snapshot_payload {dict[str, object] | None} Persisted dual-window payload.
- @param window {WindowPeriod} Target window period.
- @return {datetime | None} Projected reset timestamp or None.
- @satisfies REQ-036

### fn `def _is_claude_rate_limited_result(result: ProviderResult) -> bool` `priv` (L828-843)
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

### fn `def _build_claude_rate_limited_partial_result(` `priv` (L844-847)

### fn `def _refresh_and_persist_cache_payload(` `priv` (L892-895)
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

### fn `def retrieve_results_via_cache_pipeline(` (L980-984)
- @brief Refresh provider data and persist updates into `cache.json`.
- @details Executes provider fetches for configured providers only, records
per-provider/window attempt status, updates payload only for successful
provider/window outcomes, writes canonical cache document, and updates
idle-time metadata.
- @param providers {dict[ProviderName, BaseProvider]} Provider scope for refresh.
- @param target_window {WindowPeriod} Requested window for refresh execution.
- @param runtime_config {RuntimeConfig} Runtime throttling configuration.
- @return {dict[str, object]} Persisted cache document after merge.
- @satisfies CTN-004
- @satisfies REQ-009
- @satisfies REQ-038
- @satisfies REQ-041
- @satisfies REQ-043
- @satisfies REQ-044
- @satisfies REQ-045
- @satisfies REQ-046
- @satisfies REQ-047

### fn `def _build_cached_dual_window_results(` `priv` (L1084-1087)
- @brief Execute shared cache-based retrieval pipeline for CLI and Text UI.
- @details Applies required operation order: force-flag handling, idle-time
evaluation, conditional refresh/update of `cache.json`, then readback and
decode of provider data from `cache.json` for downstream rendering.
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

### fn `def main() -> None` `@click.version_option()` (L1143-1151)
- @brief Execute main.
- @details Applies main logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def show(provider: str, window: str, output_json: bool, force_refresh: bool) -> None` (L1177-1258)
- @brief Execute `show` with idle-time cache gating and throttled provider refresh.
- @details Delegates provider retrieval to a shared cache-based pipeline that applies force handling, idle-time gating, conditional cache refresh, and deterministic readback from `cache.json` before rendering.
- @param provider {str} CLI provider selector string.
- @param window {str} CLI window period string.
- @param output_json {bool} When True, emit JSON output instead of formatted text.
- @param force_refresh {bool} When True, bypass idle-time gate for this execution.
- @return {None} Function return value.
- @satisfies REQ-003
- @satisfies REQ-009
- @satisfies REQ-038
- @satisfies REQ-039
- @satisfies REQ-040
- @satisfies REQ-041
- @satisfies REQ-042
- @satisfies REQ-043

### fn `def _print_result(name: ProviderName, result, label: str | None = None) -> None` `priv` (L1259-1320)
- @brief Execute print result.
- @details Applies print result logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param name {ProviderName} Input parameter `name`.
- @param result {None} Input parameter `result`.
- @param label {str | None} Input parameter `label`.
- @return {None} Function return value.

### fn `def _format_reset_duration(seconds: float) -> str` `priv` (L1321-1336)
- @brief Execute format reset duration.
- @details Applies format reset duration logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param seconds {float} Input parameter `seconds`.
- @return {str} Function return value.

### fn `def _should_render_metrics_after_error(` `priv` (L1337-1339)

### fn `def _should_print_claude_reset_pending_hint(` `priv` (L1357-1359)
- @brief Check whether CLI output must render metrics after printing an error line.
- @details Allows continuation only for Claude HTTP 429 partial-window state so the
5h section can include `Error:` and still display usage/reset lines.
- @param provider_name {ProviderName} Provider associated with rendered section.
- @param result {ProviderResult} Result being rendered.
- @return {bool} True when metrics should still be rendered after error line.
- @satisfies REQ-036

### fn `def _is_displayed_zero_percent(percent: float | None) -> bool` `priv` (L1379-1395)
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

### fn `def _progress_bar(percent: float, width: int = 20) -> str` `priv` (L1396-1408)
- @brief Execute progress bar.
- @details Applies progress bar logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param percent {float} Input parameter `percent`.
- @param width {int} Input parameter `width`.
- @return {str} Function return value.

### fn `def doctor() -> None` `@main.command()` (L1410-1462)
- @brief Execute doctor.
- @details Applies doctor logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def ui() -> None` `@main.command()` (L1464-1474)
- @brief Execute ui.
- @details Applies ui logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def env() -> None` `@main.command()` (L1476-1484)
- @brief Execute env.
- @details Applies env logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def setup() -> None` `@main.command()` (L1486-1614)
- @brief Execute setup.
- @details Applies setup logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def login(provider: str) -> None` (L1622-1638)
- @brief Execute login.
- @details Applies login logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param provider {str} Input parameter `provider`.
- @return {None} Function return value.

### fn `def _login_claude() -> None` `priv` (L1639-1687)
- @brief Execute login claude.
- @details Applies login claude logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def _login_copilot() -> None` `priv` (L1688-1715)
- @brief Execute login copilot.
- @details Applies login copilot logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`RetrievalPipelineOutput`|class|pub|59-85|class RetrievalPipelineOutput|
|`_normalize_utc`|fn|priv|86-98|def _normalize_utc(value: datetime) -> datetime|
|`_apply_api_call_delay`|fn|priv|99-127|def _apply_api_call_delay(throttle_state: dict[str, float...|
|`_extract_retry_after_seconds`|fn|priv|128-146|def _extract_retry_after_seconds(result: ProviderResult) ...|
|`_is_http_429_result`|fn|priv|147-157|def _is_http_429_result(result: ProviderResult) -> bool|
|`_serialize_results_payload`|fn|priv|158-159|def _serialize_results_payload(|
|`_empty_cache_document`|fn|priv|173-187|def _empty_cache_document() -> dict[str, object]|
|`_normalize_cache_document`|fn|priv|188-209|def _normalize_cache_document(cache_document: dict[str, o...|
|`_cache_payload_section`|fn|priv|210-222|def _cache_payload_section(cache_document: dict[str, obje...|
|`_cache_status_section`|fn|priv|223-235|def _cache_status_section(cache_document: dict[str, objec...|
|`_serialize_attempt_status`|fn|priv|236-254|def _serialize_attempt_status(result: ProviderResult) -> ...|
|`_record_attempt_status`|fn|priv|255-257|def _record_attempt_status(|
|`_extract_claude_snapshot_from_cache_document`|fn|priv|277-278|def _extract_claude_snapshot_from_cache_document(|
|`_get_window_attempt_status`|fn|priv|293-296|def _get_window_attempt_status(|
|`_is_failed_http_429_status`|fn|priv|316-330|def _is_failed_http_429_status(status_entry: dict[str, ob...|
|`_filter_cached_payload`|fn|priv|331-333|def _filter_cached_payload(|
|`_project_cached_window`|fn|priv|366-369|def _project_cached_window(|
|`_load_cached_results`|fn|priv|400-404|def _load_cached_results(|
|`_update_idle_time_after_refresh`|fn|priv|453-455|def _update_idle_time_after_refresh(|
|`_project_next_reset`|fn|priv|504-535|def _project_next_reset(resets_at_str: str, window: Windo...|
|`_apply_reset_projection`|fn|priv|536-570|def _apply_reset_projection(result: ProviderResult) -> Pr...|
|`get_providers`|fn|pub|571-585|def get_providers() -> dict[ProviderName, BaseProvider]|
|`parse_window`|fn|pub|586-605|def parse_window(window: str) -> WindowPeriod|
|`parse_provider`|fn|pub|606-622|def parse_provider(provider: str) -> ProviderName | None|
|`_fetch_result`|fn|priv|623-626|def _fetch_result(|
|`_fetch_claude_dual`|fn|priv|666-669|def _fetch_claude_dual(|
|`_extract_claude_dual_payload`|fn|priv|725-727|def _extract_claude_dual_payload(|
|`_normalize_claude_dual_payload`|fn|priv|749-771|def _normalize_claude_dual_payload(payload: object) -> di...|
|`_extract_snapshot_reset_at`|fn|priv|772-774|def _extract_snapshot_reset_at(|
|`_extract_snapshot_utilization`|fn|priv|797-799|def _extract_snapshot_utilization(|
|`_is_claude_rate_limited_result`|fn|priv|828-843|def _is_claude_rate_limited_result(result: ProviderResult...|
|`_build_claude_rate_limited_partial_result`|fn|priv|844-847|def _build_claude_rate_limited_partial_result(|
|`_refresh_and_persist_cache_payload`|fn|priv|892-895|def _refresh_and_persist_cache_payload(|
|`retrieve_results_via_cache_pipeline`|fn|pub|980-984|def retrieve_results_via_cache_pipeline(|
|`_build_cached_dual_window_results`|fn|priv|1084-1087|def _build_cached_dual_window_results(|
|`main`|fn|pub|1143-1151|def main() -> None|
|`show`|fn|pub|1177-1258|def show(provider: str, window: str, output_json: bool, f...|
|`_print_result`|fn|priv|1259-1320|def _print_result(name: ProviderName, result, label: str ...|
|`_format_reset_duration`|fn|priv|1321-1336|def _format_reset_duration(seconds: float) -> str|
|`_should_render_metrics_after_error`|fn|priv|1337-1339|def _should_render_metrics_after_error(|
|`_should_print_claude_reset_pending_hint`|fn|priv|1357-1359|def _should_print_claude_reset_pending_hint(|
|`_is_displayed_zero_percent`|fn|priv|1379-1395|def _is_displayed_zero_percent(percent: float | None) -> ...|
|`_progress_bar`|fn|priv|1396-1408|def _progress_bar(percent: float, width: int = 20) -> str|
|`doctor`|fn|pub|1410-1462|def doctor() -> None|
|`ui`|fn|pub|1464-1474|def ui() -> None|
|`env`|fn|pub|1476-1484|def env() -> None|
|`setup`|fn|pub|1486-1614|def setup() -> None|
|`login`|fn|pub|1622-1638|def login(provider: str) -> None|
|`_login_claude`|fn|priv|1639-1687|def _login_claude() -> None|
|`_login_copilot`|fn|priv|1688-1715|def _login_copilot() -> None|


---

# config.py | Python | 485L | 32 symbols | 11 imports | 32 comments
> Path: `src/aibar/aibar/config.py`
- @brief Configuration and credential resolution for aibar.
- @details Provides environment-file parsing, token precedence resolution, and provider configuration status reporting.

## Imports
```
import os
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field, ValidationError
from aibar.claude_cli_auth import extract_claude_cli_token
from aibar.providers.base import ProviderName
from aibar.providers.codex import CodexCredentialStore
from aibar.providers.copilot import CopilotCredentialStore
from aibar.providers import (
```

## Definitions

- var `APP_CONFIG_DIR = Path.home() / ".config" / "aibar"` (L19)
- var `APP_CACHE_DIR = Path.home() / ".cache" / "aibar"` (L20)
- var `ENV_FILE_PATH = APP_CONFIG_DIR / "env"` (L21)
- var `RUNTIME_CONFIG_PATH = APP_CONFIG_DIR / "config.json"` (L22)
- var `CACHE_FILE_PATH = APP_CACHE_DIR / "cache.json"` (L23)
- var `IDLE_TIME_PATH = APP_CACHE_DIR / "idle-time.json"` (L24)
- var `DEFAULT_IDLE_DELAY_SECONDS = 300` (L26)
- var `DEFAULT_API_CALL_DELAY_SECONDS = 20` (L27)
### class `class RuntimeConfig(BaseModel)` : BaseModel (L30-42)
- @brief Define runtime configuration component for refresh throttling controls.
- @details Encodes persisted CLI runtime controls used by `show` refresh logic. Fields are validated as positive integers and default to conservative values that reduce rate-limit pressure while preserving configurability.
- @satisfies CTN-008

### class `class IdleTimeState(BaseModel)` : BaseModel (L43-56)
- @brief Define persisted idle-time state component.
- @details Stores last successful refresh timestamp and computed idle-until timestamp in both epoch and human-readable ISO-8601 UTC formats.
- @satisfies CTN-009

### fn `def _ensure_app_config_dir() -> None` `priv` (L57-66)
- @brief Ensure AIBar configuration directory exists before file persistence.
- @details Creates `~/.config/aibar` recursively when missing. This function is called by env-file and runtime-config persistence helpers.
- @return {None} Function return value.

### fn `def _ensure_app_cache_dir() -> None` `priv` (L67-76)
- @brief Ensure AIBar cache directory exists before cache and idle-time persistence.
- @details Creates `~/.cache/aibar` recursively when missing. This function is called by CLI cache and idle-time persistence helpers.
- @return {None} Function return value.

### fn `def _sanitize_cache_payload(payload: dict[str, Any]) -> dict[str, Any]` `priv` (L77-111)
- @brief Redact sensitive keys from cache payload before disk persistence.
- @details Recursively traverses dictionaries/lists and replaces values for case-insensitive key matches in `{token,key,secret,password,authorization}` with deterministic placeholder string `[REDACTED]`.
- @param payload {dict[str, Any]} Cache document containing `payload` and `status` sections.
- @return {dict[str, Any]} Sanitized deep-copy structure safe for persistence.
- @satisfies DES-004

### fn `def clean(value: Any) -> Any` (L89-108)
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

### fn `def load_runtime_config() -> RuntimeConfig` (L112-128)
- @brief Load runtime refresh configuration from disk with schema validation.
- @details Reads `~/.config/aibar/config.json`, validates fields against `RuntimeConfig`, and returns defaults when file is missing or invalid.
- @return {RuntimeConfig} Validated runtime configuration payload.
- @satisfies CTN-008

### fn `def save_runtime_config(runtime_config: RuntimeConfig) -> None` (L129-144)
- @brief Persist runtime refresh configuration to disk.
- @details Serializes `RuntimeConfig` to `~/.config/aibar/config.json` using stable pretty-printed JSON (`indent=2`) for deterministic readability.
- @param runtime_config {RuntimeConfig} Validated runtime configuration model.
- @return {None} Function return value.
- @satisfies CTN-008

### fn `def load_cli_cache() -> dict[str, Any] | None` (L145-162)
- @brief Load CLI cache payload from disk.
- @details Reads `~/.cache/aibar/cache.json` and returns parsed object only when payload root is a JSON object with canonical cache sections.
- @return {dict[str, Any] | None} Parsed cache payload or None if unavailable.
- @satisfies CTN-004
- @satisfies REQ-047

### fn `def save_cli_cache(payload: dict[str, Any]) -> None` (L163-185)
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

### fn `def load_idle_time() -> IdleTimeState | None` (L186-202)
- @brief Load idle-time control state from disk.
- @details Reads and validates `~/.cache/aibar/idle-time.json`. Invalid or unreadable payloads return None and are treated as missing state.
- @return {IdleTimeState | None} Validated idle-time state or None.
- @satisfies CTN-009

### fn `def save_idle_time(last_success_at: datetime, idle_until: datetime) -> IdleTimeState` (L203-228)
- @brief Persist idle-time state using epoch and human-readable timestamp fields.
- @details Normalizes timestamps to UTC, serializes both epoch and ISO strings, and writes `~/.cache/aibar/idle-time.json` in pretty-printed JSON.
- @param last_success_at {datetime} Last successful refresh timestamp.
- @param idle_until {datetime} Timestamp until refresh must remain disabled.
- @return {IdleTimeState} Persisted idle-time model.
- @satisfies CTN-009

### fn `def remove_idle_time_file() -> None` (L229-242)
- @brief Remove persisted idle-time state file if present.
- @details Deletes `~/.cache/aibar/idle-time.json` to force immediate refresh behavior on subsequent `show` execution.
- @return {None} Function return value.
- @satisfies REQ-039

### fn `def load_env_file() -> dict[str, str]` (L243-261)
- @brief Execute load env file.
- @details Applies load env file logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {dict[str, str]} Function return value.

### fn `def write_env_file(updates: dict[str, str]) -> None` (L262-301)
- @brief Execute write env file.
- @details Applies write env file logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param updates {dict[str, str]} Input parameter `updates`.
- @return {None} Function return value.

### class `class Config` (L302-483)
- @brief Define config component.
- @details Encapsulates config state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `ENV_VARS =` (L309)
- var `PROVIDER_INFO =` (L318)
- fn `def get_token(self, provider: ProviderName) -> str | None` (L351-388)
  - @brief Execute get token.
  - @details Applies get token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @return {str | None} Function return value.
- fn `def is_provider_configured(self, provider: ProviderName) -> bool` (L389-418)
  - @brief Execute is provider configured.
  - @details Applies is provider configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @return {bool} Function return value.
- fn `def get_provider_status(self, provider: ProviderName) -> dict[str, Any]` (L419-440)
  - @brief Execute get provider status.
  - @details Applies get provider status logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @return {dict[str, Any]} Function return value.
- fn `def get_all_provider_status(self) -> list[dict[str, Any]]` (L441-448)
  - @brief Execute get all provider status.
  - @details Applies get all provider status logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {list[dict[str, Any]]} Function return value.
- fn `def _get_token_preview(self, provider: ProviderName) -> str | None` `priv` (L449-460)
  - @brief Execute get token preview.
  - @details Applies get token preview logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @return {str | None} Function return value.
- fn `def get_env_var_help(self) -> str` (L461-483)
  - @brief Execute get env var help.
  - @details Applies get env var help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`APP_CONFIG_DIR`|var|pub|19||
|`APP_CACHE_DIR`|var|pub|20||
|`ENV_FILE_PATH`|var|pub|21||
|`RUNTIME_CONFIG_PATH`|var|pub|22||
|`CACHE_FILE_PATH`|var|pub|23||
|`IDLE_TIME_PATH`|var|pub|24||
|`DEFAULT_IDLE_DELAY_SECONDS`|var|pub|26||
|`DEFAULT_API_CALL_DELAY_SECONDS`|var|pub|27||
|`RuntimeConfig`|class|pub|30-42|class RuntimeConfig(BaseModel)|
|`IdleTimeState`|class|pub|43-56|class IdleTimeState(BaseModel)|
|`_ensure_app_config_dir`|fn|priv|57-66|def _ensure_app_config_dir() -> None|
|`_ensure_app_cache_dir`|fn|priv|67-76|def _ensure_app_cache_dir() -> None|
|`_sanitize_cache_payload`|fn|priv|77-111|def _sanitize_cache_payload(payload: dict[str, Any]) -> d...|
|`clean`|fn|pub|89-108|def clean(value: Any) -> Any|
|`load_runtime_config`|fn|pub|112-128|def load_runtime_config() -> RuntimeConfig|
|`save_runtime_config`|fn|pub|129-144|def save_runtime_config(runtime_config: RuntimeConfig) ->...|
|`load_cli_cache`|fn|pub|145-162|def load_cli_cache() -> dict[str, Any] | None|
|`save_cli_cache`|fn|pub|163-185|def save_cli_cache(payload: dict[str, Any]) -> None|
|`load_idle_time`|fn|pub|186-202|def load_idle_time() -> IdleTimeState | None|
|`save_idle_time`|fn|pub|203-228|def save_idle_time(last_success_at: datetime, idle_until:...|
|`remove_idle_time_file`|fn|pub|229-242|def remove_idle_time_file() -> None|
|`load_env_file`|fn|pub|243-261|def load_env_file() -> dict[str, str]|
|`write_env_file`|fn|pub|262-301|def write_env_file(updates: dict[str, str]) -> None|
|`Config`|class|pub|302-483|class Config|
|`Config.ENV_VARS`|var|pub|309||
|`Config.PROVIDER_INFO`|var|pub|318||
|`Config.get_token`|fn|pub|351-388|def get_token(self, provider: ProviderName) -> str | None|
|`Config.is_provider_configured`|fn|pub|389-418|def is_provider_configured(self, provider: ProviderName) ...|
|`Config.get_provider_status`|fn|pub|419-440|def get_provider_status(self, provider: ProviderName) -> ...|
|`Config.get_all_provider_status`|fn|pub|441-448|def get_all_provider_status(self) -> list[dict[str, Any]]|
|`Config._get_token_preview`|fn|priv|449-460|def _get_token_preview(self, provider: ProviderName) -> s...|
|`Config.get_env_var_help`|fn|pub|461-483|def get_env_var_help(self) -> str|


---

# __init__.py | Python | 23L | 0 symbols | 6 imports | 1 comments
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
```


---

# base.py | Python | 181L | 23 symbols | 5 imports | 16 comments
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

### class `class ProviderName(str, Enum)` : str, Enum (L26-38)
- @brief Define provider name component.
- @details Encapsulates provider name state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `CLAUDE = "claude"` (L32)
  - @brief Define provider name component.
  - @details Encapsulates provider name state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `OPENAI = "openai"` (L33)
- var `OPENROUTER = "openrouter"` (L34)
- var `COPILOT = "copilot"` (L35)
- var `CODEX = "codex"` (L36)

### class `class UsageMetrics(BaseModel)` : BaseModel (L39-77)
- @brief Define usage metrics component.
- @details Encapsulates usage metrics state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `def usage_percent(self) -> float | None` (L54-65)
  - @brief Execute usage percent.
  - @details Applies usage percent logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {float | None} Function return value.
- fn `def total_tokens(self) -> int | None` (L67-77)
  - @brief Execute total tokens.
  - @details Applies total tokens logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {int | None} Function return value.

### class `class ProviderResult(BaseModel)` : BaseModel (L78-100)
- @brief Define provider result component.
- @details Encapsulates provider result state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `def is_error(self) -> bool` (L92-100)
  - @brief Execute is error.
  - @details Applies is error logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {bool} Function return value.

### class `class ProviderError(Exception)` : Exception (L101-109)
- @brief Define provider error component.
- @details Encapsulates provider error state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.

### class `class AuthenticationError(ProviderError)` : ProviderError (L110-118)
- @brief Define authentication error component.
- @details Encapsulates authentication error state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.

### class `class RateLimitError(ProviderError)` : ProviderError (L119-127)
- @brief Define rate limit error component.
- @details Encapsulates rate limit error state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.

### class `class BaseProvider(ABC)` : ABC (L128-181)
- @brief Define base provider component.
- @details Encapsulates base provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L137-145)
  - @brief Execute fetch.
  - @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param window {WindowPeriod} Input parameter `window`.
  - @return {ProviderResult} Function return value.
- fn `def is_configured(self) -> bool` (L147-154)
  - @brief Execute is configured.
  - @details Applies is configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {bool} Function return value.
- fn `def get_config_help(self) -> str` (L156-163)
  - @brief Execute get config help.
  - @details Applies get config help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str} Function return value.
- fn `def _make_error_result(` `priv` (L164-165)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`WindowPeriod`|class|pub|15-25|class WindowPeriod(str, Enum)|
|`WindowPeriod.HOUR_5`|var|pub|21||
|`WindowPeriod.DAY_7`|var|pub|22||
|`WindowPeriod.DAY_30`|var|pub|23||
|`ProviderName`|class|pub|26-38|class ProviderName(str, Enum)|
|`ProviderName.CLAUDE`|var|pub|32||
|`ProviderName.OPENAI`|var|pub|33||
|`ProviderName.OPENROUTER`|var|pub|34||
|`ProviderName.COPILOT`|var|pub|35||
|`ProviderName.CODEX`|var|pub|36||
|`UsageMetrics`|class|pub|39-77|class UsageMetrics(BaseModel)|
|`UsageMetrics.usage_percent`|fn|pub|54-65|def usage_percent(self) -> float | None|
|`UsageMetrics.total_tokens`|fn|pub|67-77|def total_tokens(self) -> int | None|
|`ProviderResult`|class|pub|78-100|class ProviderResult(BaseModel)|
|`ProviderResult.is_error`|fn|pub|92-100|def is_error(self) -> bool|
|`ProviderError`|class|pub|101-109|class ProviderError(Exception)|
|`AuthenticationError`|class|pub|110-118|class AuthenticationError(ProviderError)|
|`RateLimitError`|class|pub|119-127|class RateLimitError(ProviderError)|
|`BaseProvider`|class|pub|128-181|class BaseProvider(ABC)|
|`BaseProvider.fetch`|fn|pub|137-145|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`BaseProvider.is_configured`|fn|pub|147-154|def is_configured(self) -> bool|
|`BaseProvider.get_config_help`|fn|pub|156-163|def get_config_help(self) -> str|
|`BaseProvider._make_error_result`|fn|priv|164-165|def _make_error_result(|


---

# claude_oauth.py | Python | 323L | 14 symbols | 9 imports | 17 comments
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
from aibar.config import load_runtime_config
from datetime import timezone
```

## Definitions

### class `class ClaudeOAuthProvider(BaseProvider)` : BaseProvider (L26-62)
- @brief Define claude o auth provider component.
- @details Encapsulates claude o auth provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `USAGE_URL = "https://api.anthropic.com/api/oauth/usage"` (L33)
  - @brief Define claude o auth provider component.
  - @details Encapsulates claude o auth provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `TOKEN_ENV_VAR = "CLAUDE_CODE_OAUTH_TOKEN"` (L34)
- fn `def __init__(self, token: str | None = None) -> None` `priv` (L36-46)
  - @brief Execute init.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param token {str | None} Input parameter `token`.
  - @return {None} Function return value.
- fn `def is_configured(self) -> bool` (L47-54)
  - @brief Execute is configured.
  - @details Applies is configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {bool} Function return value.
- fn `def get_config_help(self) -> str` (L55-62)
  - @brief Execute get config help.
  - @details Applies get config help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str} Function return value.

- var `MAX_RETRIES = 3` (L69)
- var `RETRY_BACKOFF_BASE = 2.0` (L70)
- var `RETRY_JITTER_MAX = 1.0` (L71)
### fn `async def _request_usage(self, client: httpx.AsyncClient) -> httpx.Response` `priv` (L73-110)
- @brief Execute HTTP GET to usage endpoint with retry on HTTP 429.
- @details Retries up to MAX_RETRIES times on 429 responses, respecting the retry-after header with exponential backoff fallback and random jitter to prevent thundering-herd synchronization. Backoff sequence with RETRY_BACKOFF_BASE=2.0: ~2-3s, ~4-5s, ~8-9s (total ~14-17s).
- @param client {httpx.AsyncClient} Reusable HTTP client session.
- @return {httpx.Response} Final HTTP response after retries exhausted or success.

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L111-150)
- @brief Execute fetch for a single window period.
- @details Makes one HTTP request to the usage endpoint (with retry on 429) and parses the response for the requested window.
- @param window {WindowPeriod} Window period to parse from the API response.
- @return {ProviderResult} Parsed result for the requested window.
- @throws {AuthenticationError} When the OAuth token is invalid or expired.
- @throws {ProviderError} On unexpected non-HTTP errors.

### fn `async def fetch_all_windows(` (L151-152)

### fn `def _handle_response(` `priv` (L205-206)
- @brief Execute a single API call and parse results for multiple windows.
- @details The usage endpoint returns data for all windows in one response.
This method avoids redundant HTTP requests when multiple windows are needed.
- @param windows {list[WindowPeriod]} Window periods to parse from one API response.
- @return {dict[WindowPeriod, ProviderResult]} Map of window to parsed result.
- @throws {AuthenticationError} When the OAuth token is invalid or expired.
- @throws {ProviderError} On unexpected non-HTTP errors.

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L258-323)
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
|`ClaudeOAuthProvider`|class|pub|26-62|class ClaudeOAuthProvider(BaseProvider)|
|`ClaudeOAuthProvider.USAGE_URL`|var|pub|33||
|`ClaudeOAuthProvider.TOKEN_ENV_VAR`|var|pub|34||
|`ClaudeOAuthProvider.__init__`|fn|priv|36-46|def __init__(self, token: str | None = None) -> None|
|`ClaudeOAuthProvider.is_configured`|fn|pub|47-54|def is_configured(self) -> bool|
|`ClaudeOAuthProvider.get_config_help`|fn|pub|55-62|def get_config_help(self) -> str|
|`MAX_RETRIES`|var|pub|69||
|`RETRY_BACKOFF_BASE`|var|pub|70||
|`RETRY_JITTER_MAX`|var|pub|71||
|`_request_usage`|fn|priv|73-110|async def _request_usage(self, client: httpx.AsyncClient)...|
|`fetch`|fn|pub|111-150|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`fetch_all_windows`|fn|pub|151-152|async def fetch_all_windows(|
|`_handle_response`|fn|priv|205-206|def _handle_response(|
|`_parse_response`|fn|priv|258-323|def _parse_response(self, data: dict, window: WindowPerio...|


---

# codex.py | Python | 429L | 21 symbols | 6 imports | 32 comments
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
```

## Definitions

### class `class CodexCredentials` (L24-91)
- @brief Define codex credentials component.
- @details Encapsulates codex credentials state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `def __init__(` `priv` (L30-36)
  - @brief Define codex credentials component.
  - @details Encapsulates codex credentials state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `def needs_refresh(self) -> bool` (L54-64)
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
- fn `def from_auth_json(cls, data: dict) -> "CodexCredentials"` (L66-91)
  - @brief Execute from auth json.
  - @details Applies from auth json logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param data {dict} Input parameter `data`.
  - @return {'CodexCredentials'} Function return value.

### class `class CodexCredentialStore` (L92-182)
- @brief Define codex credential store component.
- @details Encapsulates codex credential store state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `def codex_home(self) -> Path` (L99-108)
  - @brief Execute codex home.
  - @details Applies codex home logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {Path} Function return value.
- fn `def auth_file(self) -> Path` (L110-117)
  - @brief Execute auth file.
  - @details Applies auth file logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {Path} Function return value.
- fn `def load(self) -> CodexCredentials | None` (L118-157)
  - @brief Execute load.
  - @details Applies load logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {CodexCredentials | None} Function return value.
- fn `def save(self, credentials: CodexCredentials) -> None` (L158-182)
  - @brief Execute save.
  - @details Applies save logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param credentials {CodexCredentials} Input parameter `credentials`.
  - @return {None} Function return value.

### class `class CodexTokenRefresher` (L183-246)
- @brief Define codex token refresher component.
- @details Encapsulates codex token refresher state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `REFRESH_URL = "https://auth.openai.com/oauth/token"` (L189)
  - @brief Define codex token refresher component.
  - @details Encapsulates codex token refresher state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"` (L190)
- fn `async def refresh(self, credentials: CodexCredentials) -> CodexCredentials` (L192-246)
  - @brief Execute refresh.
  - @details Applies refresh logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param credentials {CodexCredentials} Input parameter `credentials`.
  - @return {CodexCredentials} Function return value.
  - @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### class `class CodexProvider(BaseProvider)` : BaseProvider (L247-285)
- @brief Define codex provider component.
- @details Encapsulates codex provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `BASE_URL = "https://chatgpt.com/backend-api"` (L256)
- var `USAGE_PATH = "/wham/usage"` (L257)
- fn `def __init__(self, credentials: CodexCredentials | None = None) -> None` `priv` (L259-269)
  - @brief Execute init.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param credentials {CodexCredentials | None} Input parameter `credentials`.
  - @return {None} Function return value.
- fn `def is_configured(self) -> bool` (L270-277)
  - @brief Execute is configured.
  - @details Applies is configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {bool} Function return value.
- fn `def get_config_help(self) -> str` (L278-285)
  - @brief Execute get config help.
  - @details Applies get config help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str} Function return value.

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L297-376)
- @brief Execute fetch.
- @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L377-429)
- @brief Execute parse response.
- @details Applies parse response logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param data {dict} Input parameter `data`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`CodexCredentials`|class|pub|24-91|class CodexCredentials|
|`CodexCredentials.__init__`|fn|priv|30-36|def __init__(|
|`CodexCredentials.needs_refresh`|fn|pub|54-64|def needs_refresh(self) -> bool|
|`CodexCredentials.from_auth_json`|fn|pub|66-91|def from_auth_json(cls, data: dict) -> "CodexCredentials"|
|`CodexCredentialStore`|class|pub|92-182|class CodexCredentialStore|
|`CodexCredentialStore.codex_home`|fn|pub|99-108|def codex_home(self) -> Path|
|`CodexCredentialStore.auth_file`|fn|pub|110-117|def auth_file(self) -> Path|
|`CodexCredentialStore.load`|fn|pub|118-157|def load(self) -> CodexCredentials | None|
|`CodexCredentialStore.save`|fn|pub|158-182|def save(self, credentials: CodexCredentials) -> None|
|`CodexTokenRefresher`|class|pub|183-246|class CodexTokenRefresher|
|`CodexTokenRefresher.REFRESH_URL`|var|pub|189||
|`CodexTokenRefresher.CLIENT_ID`|var|pub|190||
|`CodexTokenRefresher.refresh`|fn|pub|192-246|async def refresh(self, credentials: CodexCredentials) ->...|
|`CodexProvider`|class|pub|247-285|class CodexProvider(BaseProvider)|
|`CodexProvider.BASE_URL`|var|pub|256||
|`CodexProvider.USAGE_PATH`|var|pub|257||
|`CodexProvider.__init__`|fn|priv|259-269|def __init__(self, credentials: CodexCredentials | None =...|
|`CodexProvider.is_configured`|fn|pub|270-277|def is_configured(self) -> bool|
|`CodexProvider.get_config_help`|fn|pub|278-285|def get_config_help(self) -> str|
|`fetch`|fn|pub|297-376|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|377-429|def _parse_response(self, data: dict, window: WindowPerio...|


---

# copilot.py | Python | 420L | 27 symbols | 8 imports | 31 comments
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
import asyncio
```

## Definitions

### class `class CopilotDeviceFlow` (L26-114)
- @brief Define copilot device flow component.
- @details Encapsulates copilot device flow state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `CLIENT_ID = "Iv1.b507a08c87ecfe98"` (L33)
- var `SCOPES = "read:user"` (L34)
- var `DEVICE_CODE_URL = "https://github.com/login/device/code"` (L36)
- var `TOKEN_URL = "https://github.com/login/oauth/access_token"` (L37)
- fn `async def request_device_code(self) -> dict[str, Any]` (L39-63)
  - @brief Execute request device code.
  - @details Applies request device code logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {dict[str, Any]} Function return value.
  - @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.
- fn `async def poll_for_token(self, device_code: str, interval: int = 5) -> str` (L64-114)
  - @brief Execute poll for token.
  - @details Applies poll for token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param device_code {str} Input parameter `device_code`.
  - @param interval {int} Input parameter `interval`.
  - @return {str} Function return value.
  - @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### class `class CopilotCredentialStore` (L115-171)
- @brief Define copilot credential store component.
- @details Encapsulates copilot credential store state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `CONFIG_DIR = Path.home() / ".config" / "aibar"` (L121)
  - @brief Define copilot credential store component.
  - @details Encapsulates copilot credential store state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `CREDS_FILE = CONFIG_DIR / "copilot.json"` (L122)
- var `CODEXBAR_CONFIG = Path.home() / ".codexbar" / "config.json"` (L123)
- fn `def load_token(self) -> str | None` (L125-156)
  - @brief Execute load token.
  - @details Applies load token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str | None} Function return value.
- fn `def save_token(self, token: str) -> None` (L157-171)
  - @brief Execute save token.
  - @details Applies save token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param token {str} Input parameter `token`.
  - @return {None} Function return value.

### class `class CopilotProvider(BaseProvider)` : BaseProvider (L172-212)
- @brief Define copilot provider component.
- @details Encapsulates copilot provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `USAGE_URL = "https://api.github.com/copilot_internal/user"` (L179)
  - @brief Define copilot provider component.
  - @details Encapsulates copilot provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `EDITOR_VERSION = "vscode/1.96.2"` (L182)
- var `PLUGIN_VERSION = "copilot-chat/0.26.7"` (L183)
- var `USER_AGENT = "GitHubCopilotChat/0.26.7"` (L184)
- var `API_VERSION = "2025-04-01"` (L185)
- fn `def __init__(self, token: str | None = None) -> None` `priv` (L187-196)
  - @brief Execute init.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param token {str | None} Input parameter `token`.
  - @return {None} Function return value.
- fn `def is_configured(self) -> bool` (L197-204)
  - @brief Execute is configured.
  - @details Applies is configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {bool} Function return value.
- fn `def get_config_help(self) -> str` (L205-212)
  - @brief Execute get config help.
  - @details Applies get config help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str} Function return value.

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L222-293)
- @brief Execute fetch.
- @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L294-389)
- @brief Execute parse response.
- @details Applies parse response logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param data {dict} Input parameter `data`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.

### fn `def _get_snapshot(key_camel: str, key_snake: str) -> dict` `priv` (L304-313)
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

### fn `def _extract_quota_data(snapshot: dict) -> tuple[float | None, float | None]` `priv` (L314-340)
- @brief Execute extract quota data.
- @details Applies extract quota data logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param snapshot {dict} Input parameter `snapshot`.
- @return {tuple[float | None, float | None]} Function return value.

### fn `async def login(self) -> str` (L390-420)
- @brief Execute login.
- @details Applies login logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {str} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`CopilotDeviceFlow`|class|pub|26-114|class CopilotDeviceFlow|
|`CopilotDeviceFlow.CLIENT_ID`|var|pub|33||
|`CopilotDeviceFlow.SCOPES`|var|pub|34||
|`CopilotDeviceFlow.DEVICE_CODE_URL`|var|pub|36||
|`CopilotDeviceFlow.TOKEN_URL`|var|pub|37||
|`CopilotDeviceFlow.request_device_code`|fn|pub|39-63|async def request_device_code(self) -> dict[str, Any]|
|`CopilotDeviceFlow.poll_for_token`|fn|pub|64-114|async def poll_for_token(self, device_code: str, interval...|
|`CopilotCredentialStore`|class|pub|115-171|class CopilotCredentialStore|
|`CopilotCredentialStore.CONFIG_DIR`|var|pub|121||
|`CopilotCredentialStore.CREDS_FILE`|var|pub|122||
|`CopilotCredentialStore.CODEXBAR_CONFIG`|var|pub|123||
|`CopilotCredentialStore.load_token`|fn|pub|125-156|def load_token(self) -> str | None|
|`CopilotCredentialStore.save_token`|fn|pub|157-171|def save_token(self, token: str) -> None|
|`CopilotProvider`|class|pub|172-212|class CopilotProvider(BaseProvider)|
|`CopilotProvider.USAGE_URL`|var|pub|179||
|`CopilotProvider.EDITOR_VERSION`|var|pub|182||
|`CopilotProvider.PLUGIN_VERSION`|var|pub|183||
|`CopilotProvider.USER_AGENT`|var|pub|184||
|`CopilotProvider.API_VERSION`|var|pub|185||
|`CopilotProvider.__init__`|fn|priv|187-196|def __init__(self, token: str | None = None) -> None|
|`CopilotProvider.is_configured`|fn|pub|197-204|def is_configured(self) -> bool|
|`CopilotProvider.get_config_help`|fn|pub|205-212|def get_config_help(self) -> str|
|`fetch`|fn|pub|222-293|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|294-389|def _parse_response(self, data: dict, window: WindowPerio...|
|`_get_snapshot`|fn|priv|304-313|def _get_snapshot(key_camel: str, key_snake: str) -> dict|
|`_extract_quota_data`|fn|priv|314-340|def _extract_quota_data(snapshot: dict) -> tuple[float | ...|
|`login`|fn|pub|390-420|async def login(self) -> str|


---

# openai_usage.py | Python | 235L | 12 symbols | 6 imports | 16 comments
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
from aibar.config import load_runtime_config
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

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L80-115)
- @brief Execute fetch.
- @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `async def _fetch_usage(` `priv` (L116-121)

### fn `async def _fetch_costs(` `priv` (L144-149)
- @brief Execute fetch usage.
- @details Applies fetch usage logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param client {httpx.AsyncClient} Input parameter `client`.
- @param headers {dict} Input parameter `headers`.
- @param start_time {int} Input parameter `start_time`.
- @param end_time {int} Input parameter `end_time`.
- @return {dict} Function return value.

### fn `def _check_response(self, response: httpx.Response) -> None` `priv` (L172-188)
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

### fn `def _build_result(` `priv` (L189-190)

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
|`fetch`|fn|pub|80-115|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_fetch_usage`|fn|priv|116-121|async def _fetch_usage(|
|`_fetch_costs`|fn|priv|144-149|async def _fetch_costs(|
|`_check_response`|fn|priv|172-188|def _check_response(self, response: httpx.Response) -> None|
|`_build_result`|fn|priv|189-190|def _build_result(|


---

# openrouter.py | Python | 203L | 11 symbols | 3 imports | 11 comments
> Path: `src/aibar/aibar/providers/openrouter.py`
- @brief OpenRouter key usage and credit provider.
- @details Fetches key usage snapshots and quota limits, then transforms provider payloads into normalized cost and quota metrics.

## Imports
```
import httpx
from aibar.providers.base import (
from aibar.config import config
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

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L64-132)
- @brief Execute fetch.
- @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L133-162)
- @brief Execute parse response.
- @details Applies parse response logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param data {dict} Input parameter `data`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.

### fn `def _get_usage(self, payload: dict, window: WindowPeriod) -> float` `priv` (L163-176)
- @brief Execute get usage.
- @details Applies get usage logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param payload {dict} Input parameter `payload`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {float} Function return value.

### fn `def _get_byok_usage(self, payload: dict, window: WindowPeriod) -> float` `priv` (L177-190)
- @brief Execute get byok usage.
- @details Applies get byok usage logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param payload {dict} Input parameter `payload`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {float} Function return value.

### fn `def _to_float(self, value: float | int | None) -> float` `priv` (L191-203)
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
|`fetch`|fn|pub|64-132|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|133-162|def _parse_response(self, data: dict, window: WindowPerio...|
|`_get_usage`|fn|priv|163-176|def _get_usage(self, payload: dict, window: WindowPeriod)...|
|`_get_byok_usage`|fn|priv|177-190|def _get_byok_usage(self, payload: dict, window: WindowPe...|
|`_to_float`|fn|priv|191-203|def _to_float(self, value: float | int | None) -> float|


---

# ui.py | Python | 715L | 32 symbols | 13 imports | 43 comments
> Path: `src/aibar/aibar/ui.py`
- @brief Textual terminal UI for usage metrics.
- @details Implements provider cards, refresh controls, window switching, and raw JSON visualization over normalized provider results.

## Imports
```
import asyncio
import json
from datetime import datetime, timezone
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalGroup, VerticalScroll
from textual.reactive import reactive
from textual.widgets import (
from aibar.cli import retrieve_results_via_cache_pipeline
from aibar.config import config
from aibar.providers import (
from aibar.providers.base import (
```

## Definitions

### class `class ProviderCard(Static)` : Static (L46-245)
- @brief Define provider card component.
- @details Encapsulates provider card state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `def __init__(` `priv` (L123-126)
  - @brief Define provider card component.
  - @details Encapsulates provider card state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `def compose(self) -> ComposeResult` (L139-162)
  - @brief Execute init.
  - @brief Execute compose.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @details Applies compose logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider_name {ProviderName} Input parameter `provider_name`.
  - @param kwargs {None} Input parameter `kwargs`.
  - @return {None} Function return value.
  - @return {ComposeResult} Function return value.

### fn `def watch_result(self, result: ProviderResult | None) -> None` (L163-255)
- @brief Execute watch result.
- @details Applies watch result logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param result {ProviderResult | None} Input parameter `result`.
- @return {None} Function return value.

### fn `def watch_is_loading(self, loading: bool) -> None` (L256-268)
- @brief Execute watch is loading.
- @details Applies watch is loading logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param loading {bool} Input parameter `loading`.
- @return {None} Function return value.

### fn `def _is_rate_limit_quota_error(self, result: ProviderResult) -> bool` `priv` (L269-283)
- @brief Check whether result is a rate-limit payload that still carries quota metrics.
- @details Detects the normalized Claude/Codex/Copilot rate-limit message with available `limit` and `remaining` values so card rendering can continue without showing the textual error banner.
- @param result {ProviderResult} Provider result candidate.
- @return {bool} True when result error is rate-limit with quota metrics.

### fn `def _is_displayed_full_percent(self, percent: float | None) -> bool` `priv` (L284-295)
- @brief Check whether usage renders as `100.0%` in one-decimal output.
- @details Applies display-rounding semantics used by Textual labels so near-full values (for example `99.96`) are treated as full usage.
- @param percent {float | None} Candidate usage percentage.
- @return {bool} True when rendered one-decimal value is `100.0%`.

### fn `def _supports_limit_reached_hint(self, result: ProviderResult) -> bool` `priv` (L296-309)
- @brief Validate whether provider/window pair supports `Limit reached!` hint.
- @details Limits warning rendering scope to Claude/Codex `5h` or `7d` cards and Copilot `30d` cards.
- @param result {ProviderResult} Provider result candidate.
- @return {bool} True when provider/window pair is eligible.

### fn `def _should_show_limit_reached_hint(self, result: ProviderResult) -> bool` `priv` (L310-320)
- @brief Determine whether reset text must include `⚠️ Limit reached!`.
- @details Evaluates provider/window scope and displayed usage rounding.
- @param result {ProviderResult} Provider result candidate.
- @return {bool} True when reset label must include limit-reached hint.

### fn `def _format_reset_value(self, reset_str: str, result: ProviderResult) -> str` `priv` (L321-331)
- @brief Compose reset label value with optional limit-reached suffix.
- @param reset_str {str} Countdown text from `_format_duration`.
- @param result {ProviderResult} Provider result candidate.
- @return {str} Reset value with optional `⚠️ Limit reached!` suffix.

### fn `def _format_age(self, seconds: float) -> str` `priv` (L332-345)
- @brief Execute format age.
- @details Applies format age logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param seconds {float} Input parameter `seconds`.
- @return {str} Function return value.

### fn `def _format_duration(self, seconds: float) -> str` `priv` (L346-365)
- @brief Execute format duration.
- @details Applies format duration logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param seconds {float} Input parameter `seconds`.
- @return {str} Function return value.

### class `class RawJsonView(Static)` : Static (L366-413)
- @brief Define raw json view component.
- @details Encapsulates raw json view state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `def compose(self) -> ComposeResult` (L388-398)
  - @brief Define raw json view component.
  - @brief Execute compose.
  - @details Encapsulates raw json view state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
  - @details Applies compose logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {ComposeResult} Function return value.
- fn `def watch_data(self, data: dict | None) -> None` (L399-413)
  - @brief Execute watch data.
  - @details Applies watch data logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param data {dict | None} Input parameter `data`.
  - @return {None} Function return value.

### class `class AIBarUI(App)` : App (L414-613)
- @brief Define a i bar u i component.
- @details Encapsulates a i bar u i state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `BINDINGS = [` (L474)
- var `TITLE = "Usage Metrics UI"` (L482)
- fn `def __init__(self) -> None` `priv` (L487-502)
  - @brief Execute init.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {None} Function return value.
- fn `def compose(self) -> ComposeResult` (L503-530)
  - @brief Execute compose.
  - @details Applies compose logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {ComposeResult} Function return value.
- fn `async def on_mount(self) -> None` (L531-539)
  - @brief Execute on mount.
  - @details Applies on mount logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {None} Function return value.
- fn `async def on_refresh_pressed(self) -> None` (L541-548)
  - @brief Execute on refresh pressed.
  - @details Applies on refresh pressed logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {None} Function return value.
- fn `async def on_5h_pressed(self) -> None` (L550-557)
  - @brief Execute on 5h pressed.
  - @details Applies on 5h pressed logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {None} Function return value.
- fn `async def on_7d_pressed(self) -> None` (L559-566)
  - @brief Execute on 7d pressed.
  - @details Applies on 7d pressed logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {None} Function return value.

### fn `async def action_refresh(self) -> None` (L567-623)
- @brief Execute action refresh.
- @details Executes shared cache-based retrieval pipeline reused by CLI `show`: force-flag evaluation, idle-time gate check, conditional cache refresh, and readback from `cache.json` before card projection.
- @return {None} Function return value.
- @satisfies REQ-009
- @satisfies REQ-043

### fn `async def action_window_5h(self) -> None` (L624-633)
- @brief Execute action window 5h.
- @details Applies action window 5h logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `async def action_window_7d(self) -> None` (L634-643)
- @brief Execute action window 7d.
- @details Applies action window 7d logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `async def action_toggle_json(self) -> None` (L644-656)
- @brief Execute action toggle json.
- @details Applies action toggle json logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def _get_card(self, provider: ProviderName) -> ProviderCard | None` `priv` (L657-669)
- @brief Execute get card.
- @details Applies get card logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param provider {ProviderName} Input parameter `provider`.
- @return {ProviderCard | None} Function return value.

### fn `def _update_window_buttons(self) -> None` `priv` (L670-689)
- @brief Execute update window buttons.
- @details Applies update window buttons logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def _update_json_view(self) -> None` `priv` (L690-703)
- @brief Execute update json view.
- @details Applies update json view logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def run_ui() -> None` (L704-713)
- @brief Execute run ui.
- @details Applies run ui logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`ProviderCard`|class|pub|46-245|class ProviderCard(Static)|
|`ProviderCard.__init__`|fn|priv|123-126|def __init__(|
|`ProviderCard.compose`|fn|pub|139-162|def compose(self) -> ComposeResult|
|`watch_result`|fn|pub|163-255|def watch_result(self, result: ProviderResult | None) -> ...|
|`watch_is_loading`|fn|pub|256-268|def watch_is_loading(self, loading: bool) -> None|
|`_is_rate_limit_quota_error`|fn|priv|269-283|def _is_rate_limit_quota_error(self, result: ProviderResu...|
|`_is_displayed_full_percent`|fn|priv|284-295|def _is_displayed_full_percent(self, percent: float | Non...|
|`_supports_limit_reached_hint`|fn|priv|296-309|def _supports_limit_reached_hint(self, result: ProviderRe...|
|`_should_show_limit_reached_hint`|fn|priv|310-320|def _should_show_limit_reached_hint(self, result: Provide...|
|`_format_reset_value`|fn|priv|321-331|def _format_reset_value(self, reset_str: str, result: Pro...|
|`_format_age`|fn|priv|332-345|def _format_age(self, seconds: float) -> str|
|`_format_duration`|fn|priv|346-365|def _format_duration(self, seconds: float) -> str|
|`RawJsonView`|class|pub|366-413|class RawJsonView(Static)|
|`RawJsonView.compose`|fn|pub|388-398|def compose(self) -> ComposeResult|
|`RawJsonView.watch_data`|fn|pub|399-413|def watch_data(self, data: dict | None) -> None|
|`AIBarUI`|class|pub|414-613|class AIBarUI(App)|
|`AIBarUI.BINDINGS`|var|pub|474||
|`AIBarUI.TITLE`|var|pub|482||
|`AIBarUI.__init__`|fn|priv|487-502|def __init__(self) -> None|
|`AIBarUI.compose`|fn|pub|503-530|def compose(self) -> ComposeResult|
|`AIBarUI.on_mount`|fn|pub|531-539|async def on_mount(self) -> None|
|`AIBarUI.on_refresh_pressed`|fn|pub|541-548|async def on_refresh_pressed(self) -> None|
|`AIBarUI.on_5h_pressed`|fn|pub|550-557|async def on_5h_pressed(self) -> None|
|`AIBarUI.on_7d_pressed`|fn|pub|559-566|async def on_7d_pressed(self) -> None|
|`action_refresh`|fn|pub|567-623|async def action_refresh(self) -> None|
|`action_window_5h`|fn|pub|624-633|async def action_window_5h(self) -> None|
|`action_window_7d`|fn|pub|634-643|async def action_window_7d(self) -> None|
|`action_toggle_json`|fn|pub|644-656|async def action_toggle_json(self) -> None|
|`_get_card`|fn|priv|657-669|def _get_card(self, provider: ProviderName) -> ProviderCa...|
|`_update_window_buttons`|fn|priv|670-689|def _update_window_buttons(self) -> None|
|`_update_json_view`|fn|priv|690-703|def _update_json_view(self) -> None|
|`run_ui`|fn|pub|704-713|def run_ui() -> None|


---

# extension.js | JavaScript | 1240L | 17 symbols | 0 imports | 28 comments
> Path: `src/aibar/gnome-extension/aibar@aibar.panel/extension.js`
- @brief GNOME Shell panel extension for aibar metrics.
- @details Collects usage JSON from the aibar CLI and renders provider-specific quota/cost cards in the GNOME panel popup.

## Definitions

- const `const REFRESH_INTERVAL_SECONDS = 300;` (L39)
- const `const ENV_FILE_PATH = GLib.get_home_dir() + '/.config/aibar/env';` (L40)
- const `const RESET_PENDING_MESSAGE = 'Starts when the first message is sent';` (L41)
- const `const RATE_LIMIT_ERROR_MESSAGE = 'Rate limited. Try again later.';` (L42)
### fn `function _getAiBarPath()` (L49-59)
- @brief Resolve aibar executable path.
- @details Prefers PATH discovery and falls back to AIBAR_PATH from the env file.
- @return s {string} Resolved executable path or fallback command name.

### fn `function _loadEnvFromFile()` (L66-118)
- @brief Load key-value environment variables from aibar env file.
- @details Parses export syntax, quoted values, and inline comments.
- @return s {Object<string,string>} Parsed environment map.

### fn `function _getProgressClass(pct)` (L125-131)
- @brief Map percentage usage to CSS progress severity class.
- @param {number} pct Usage percentage.
- @return s {string} CSS class suffix for progress state.

### fn `function _isDisplayedZeroPercent(pct)` (L140-147)
- @brief Check whether a percentage renders as `0.0%` in one-decimal UI output.
- @details Mirrors display rounding semantics so fallback reset text is shown when
usage is effectively zero from the user's perspective (e.g. internal 0.04 -> 0.0%).
- @param {number} pct Usage percentage candidate.
- @return s {boolean} True when value is finite, non-negative, and rounds to 0.0.

### fn `function _isDisplayedFullPercent(pct)` (L156-161)
- @brief Check whether a percentage renders as `100.0%` in one-decimal UI output.
- @details Mirrors display rounding semantics so near-full values are treated as
full usage for limit-reached warning rendering.
- @param {number} pct Usage percentage candidate.
- @return s {boolean} True when value is finite and rounds to `100.0`.

### class `class AIBarIndicator extends PanelMenu.Button` : PanelMenu.Button (L165-464)
- @brief Panel indicator widget that manages popup rendering and refresh lifecycle. */
- @brief Execute init.
- @details Applies init logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
- @return s {any} Function return value.

### fn `const createWindowBar = (labelText) =>` (L509-555)
- @brief Execute create provider card.
- @details Applies create provider card logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
- @param {any} providerName Input parameter `providerName`.
- @return s {any} Function return value.

### fn `const updateWindowBar = (bar, pct, resetTime, useDays) =>` (L664-722)
- @brief Execute populate provider card.
- @details Applies populate provider card logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
- @param {any} card Input parameter `card`.
- @param {any} providerName Input parameter `providerName`.
- @param {any} data Input parameter `data`.
- @return s {any} Function return value.

### fn `const setResetLabel = (baseText) =>` (L670-676)

### fn `const showResetPendingHint = () =>` (L687-689)

### fn `const toPercent = (value) =>` (L1006-1011)
- @brief Execute update u i.
- @details Applies update u i logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
- @return s {any} Function return value.

### fn `const getPanelUsageValues = (providerName, data) =>` (L1013-1070)

### class `export default class AIBarExtension` (L1206-1240)
- @brief GNOME extension lifecycle adapter for AIBarIndicator registration. */
- @brief Execute constructor.
- @details Applies constructor logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
- @return s {any} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`REFRESH_INTERVAL_SECONDS`|const||39||
|`ENV_FILE_PATH`|const||40||
|`RESET_PENDING_MESSAGE`|const||41||
|`RATE_LIMIT_ERROR_MESSAGE`|const||42||
|`_getAiBarPath`|fn||49-59|function _getAiBarPath()|
|`_loadEnvFromFile`|fn||66-118|function _loadEnvFromFile()|
|`_getProgressClass`|fn||125-131|function _getProgressClass(pct)|
|`_isDisplayedZeroPercent`|fn||140-147|function _isDisplayedZeroPercent(pct)|
|`_isDisplayedFullPercent`|fn||156-161|function _isDisplayedFullPercent(pct)|
|`AIBarIndicator`|class||165-464|class AIBarIndicator extends PanelMenu.Button|
|`createWindowBar`|fn||509-555|const createWindowBar = (labelText) =>|
|`updateWindowBar`|fn||664-722|const updateWindowBar = (bar, pct, resetTime, useDays) =>|
|`setResetLabel`|fn||670-676|const setResetLabel = (baseText) =>|
|`showResetPendingHint`|fn||687-689|const showResetPendingHint = () =>|
|`toPercent`|fn||1006-1011|const toPercent = (value) =>|
|`getPanelUsageValues`|fn||1013-1070|const getPanelUsageValues = (providerName, data) =>|
|`AIBarExtension`|class||1206-1240|export default class AIBarExtension|

