# Files Structure
```
.
├── scripts
│   ├── aibar.sh
│   ├── check-js-syntax.sh
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
        │   │   ├── geminiai.py
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

# check-js-syntax.sh | Shell | 37L | 2 symbols | 0 imports | 15 comments
> Path: `scripts/check-js-syntax.sh`

## Definitions

- var `FILE="$1"` (L24)
- @brief Syntax-only JavaScript checker for GJS (GNOME JavaScript) source files.
- @details Preprocesses GNOME Shell extension JS files before syntax validation with Node.js.
Replaces gi:// and resource:// import statements (GJS-only URL schemes) with equivalent
const stub declarations so that Node.js syntax checking succeeds without requiring the
GNOME Shell runtime. The original file is never modified.
- @param $1 Path to the .js file to syntax-check.
- @retval 0 Syntax is valid.
- @retval 1 File argument missing, sed preprocessing failed, or syntax error detected.
- @note GJS supports gi:// (GObject introspection) and resource:// (GNOME Shell UI modules)
- var `TMP=$(mktemp /tmp/check-js-syntax-XXXXXX.js)` (L25)
## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`FILE`|var||24||
|`TMP`|var||25||


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

# cli.py | Python | 1886L | 51 symbols | 21 imports | 69 comments
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
from pathlib import Path
import click
from click.core import ParameterSource
from pydantic import ValidationError
from aibar.config import (
from aibar.providers import (
from aibar.providers.base import (
from datetime import datetime, timezone
from aibar.ui import run_ui
from aibar.config import (
from aibar.providers.geminiai import GeminiAICredentialStore
from aibar.claude_cli_auth import ClaudeCLIAuth
from aibar.providers.copilot import CopilotProvider
from aibar.providers.geminiai import GeminiAICredentialStore
```

## Definitions

### class `class RetrievalPipelineOutput` `@dataclass(frozen=True)` (L62-88)
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

### fn `def _normalize_utc(value: datetime) -> datetime` `priv` (L89-101)
- @brief Normalize datetime values to timezone-aware UTC instances.
- @details Ensures consistent timestamp arithmetic for idle-time persistence and refresh-delay computations when source datetimes are naive or non-UTC.
- @param value {datetime} Source datetime to normalize.
- @return {datetime} Timezone-aware UTC datetime.

### fn `def _apply_api_call_delay(throttle_state: dict[str, float | int] | None) -> None` `priv` (L102-130)
- @brief Enforce minimum spacing between consecutive provider API calls.
- @details Uses monotonic clock values in `throttle_state` to sleep before a live API request when elapsed time is below configured delay.
- @param throttle_state {dict[str, float | int] | None} Mutable state containing `delay_seconds` and `last_call_started`.
- @return {None} Function return value.
- @satisfies REQ-040

### fn `def _extract_retry_after_seconds(result: ProviderResult) -> int` `priv` (L131-149)
- @brief Extract normalized retry-after seconds from provider error payload.
- @details Reads `raw.retry_after_seconds` and clamps to non-negative integer seconds. Invalid or missing values normalize to zero.
- @param result {ProviderResult} Provider result to inspect.
- @return {int} Non-negative retry-after delay in seconds.
- @satisfies REQ-041

### fn `def _is_http_429_result(result: ProviderResult) -> bool` `priv` (L150-160)
- @brief Check whether result payload represents HTTP 429 rate limiting.
- @details Uses normalized raw payload marker `status_code == 429`.
- @param result {ProviderResult} Provider result to classify.
- @return {bool} True when result indicates HTTP 429.
- @satisfies REQ-041

### fn `def _serialize_results_payload(` `priv` (L161-162)

### fn `def _empty_cache_document() -> dict[str, object]` `priv` (L176-190)
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

### fn `def _normalize_cache_document(cache_document: dict[str, object] | None) -> dict[str, object]` `priv` (L191-212)
- @brief Normalize decoded cache payload to canonical sectioned schema.
- @details Accepts decoded cache document and enforces object-typed `payload` and `status` sections. Missing or invalid sections normalize to empty objects.
- @param cache_document {dict[str, object] | None} Decoded cache payload from disk.
- @return {dict[str, object]} Canonical cache document with `payload`/`status`.
- @satisfies CTN-004
- @satisfies REQ-003

### fn `def _cache_payload_section(cache_document: dict[str, object]) -> dict[str, object]` `priv` (L213-225)
- @brief Extract payload section from canonical cache document.
- @details Returns mutable provider-result mapping from normalized document.
- @param cache_document {dict[str, object]} Canonical cache document.
- @return {dict[str, object]} Provider payload section.

### fn `def _cache_status_section(cache_document: dict[str, object]) -> dict[str, object]` `priv` (L226-238)
- @brief Extract status section from canonical cache document.
- @details Returns mutable provider/window status mapping from normalized document.
- @param cache_document {dict[str, object]} Canonical cache document.
- @return {dict[str, object]} Provider/window status section.

### fn `def _serialize_attempt_status(result: ProviderResult) -> dict[str, object]` `priv` (L239-257)
- @brief Serialize one provider/window fetch attempt status for cache persistence.
- @details Converts ProviderResult error state to status object using `OK`/`FAIL`, preserving error text, update timestamp, and optional HTTP status code.
- @param result {ProviderResult} Provider result from current refresh attempt.
- @return {dict[str, object]} Attempt-status payload.
- @satisfies REQ-044

### fn `def _record_attempt_status(` `priv` (L258-260)

### fn `def _extract_claude_snapshot_from_cache_document(` `priv` (L280-281)
- @brief Persist one provider/window attempt status into cache status section.
- @details Upserts `status[provider][window]` with serialized attempt metadata and
preserves statuses for untouched providers/windows.
- @param status_section {dict[str, object]} Mutable cache status section.
- @param result {ProviderResult} Provider result to encode.
- @return {None} Function return value.
- @satisfies REQ-044
- @satisfies REQ-046

### fn `def _get_window_attempt_status(` `priv` (L296-299)
- @brief Extract persisted Claude dual-window payload from cache document.
- @details Reads Claude entry from cache `payload` section and normalizes it into
a dual-window raw payload (`five_hour`, `seven_day`) for HTTP 429 restoration.
- @param cache_document {dict[str, object]} Canonical cache document.
- @return {dict[str, object] | None} Normalized dual-window payload or None.
- @satisfies REQ-047

### fn `def _is_failed_http_429_status(status_entry: dict[str, object] | None) -> bool` `priv` (L319-333)
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

### fn `def _filter_cached_payload(` `priv` (L334-336)

### fn `def _project_cached_window(` `priv` (L369-372)
- @brief Filter canonical cache document by optional provider selector.
- @details Filters both cache sections (`payload`, `status`) so selected-provider
output contains only relevant provider nodes while preserving schema keys.
- @param cache_document {dict[str, object]} Canonical cache document.
- @param provider_filter {ProviderName | None} Optional provider selector.
- @return {dict[str, object]} Filtered cache document with canonical sections.

### fn `def _load_cached_results(` `priv` (L403-407)
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

### fn `def _update_idle_time_after_refresh(` `priv` (L456-458)
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

### fn `def _project_next_reset(resets_at_str: str, window: WindowPeriod) -> datetime | None` `priv` (L507-538)
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

### fn `def _apply_reset_projection(result: ProviderResult) -> ProviderResult` `priv` (L539-573)
- @brief Return a copy of `result` with `metrics.reset_at` set to the projected next reset boundary when it is currently None but the raw payload contains a parseable past `resets_at` string for the result's window.
- @details When a ProviderResult is obtained from stale disk cache (last-good path) or from a cross-window raw re-parse, `_parse_response` correctly sets `reset_at=None` for past timestamps. This function recovers the display information by projecting the next future reset boundary from the raw payload's `resets_at` field, ensuring the 'Resets in:' countdown is shown even when the cached timestamp has already elapsed. If `reset_at` is already non-None, or the raw payload has no parseable `resets_at` for the window, or projection fails, the original result is returned unchanged.
- @param result {ProviderResult} Candidate result whose reset_at may require projection.
- @return {ProviderResult} Original result unchanged if no projection is needed; otherwise a new ProviderResult with metrics.reset_at set to the projected datetime.
- @see _project_next_reset
- @satisfies REQ-002

### fn `def get_providers() -> dict[ProviderName, BaseProvider]` (L574-589)
- @brief Execute get providers.
- @details Applies get providers logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {dict[ProviderName, BaseProvider]} Function return value.

### fn `def parse_window(window: str) -> WindowPeriod` (L590-609)
- @brief Execute parse window.
- @details Applies parse window logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {str} Input parameter `window`.
- @return {WindowPeriod} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def parse_provider(provider: str) -> ProviderName | None` (L610-626)
- @brief Execute parse provider.
- @details Applies parse provider logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param provider {str} Input parameter `provider`.
- @return {ProviderName | None} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _fetch_result(` `priv` (L627-630)

### fn `def _fetch_claude_dual(` `priv` (L670-673)
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

### fn `def _extract_claude_dual_payload(` `priv` (L729-731)
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

### fn `def _normalize_claude_dual_payload(payload: object) -> dict[str, object] | None` `priv` (L753-775)
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

### fn `def _extract_snapshot_reset_at(` `priv` (L776-778)

### fn `def _extract_snapshot_utilization(` `priv` (L801-803)
- @brief Resolve projected reset timestamp from persisted Claude snapshot payload.
- @details Uses window-specific `resets_at` string from persisted payload and
projects next reset boundary through `_project_next_reset`.
- @param snapshot_payload {dict[str, object] | None} Persisted dual-window payload.
- @param window {WindowPeriod} Target window period.
- @return {datetime | None} Projected reset timestamp or None.
- @satisfies REQ-036

### fn `def _is_claude_rate_limited_result(result: ProviderResult) -> bool` `priv` (L832-847)
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

### fn `def _build_claude_rate_limited_partial_result(` `priv` (L848-851)

### fn `def _refresh_and_persist_cache_payload(` `priv` (L896-899)
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

### fn `def retrieve_results_via_cache_pipeline(` (L984-988)
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

### fn `def _build_cached_dual_window_results(` `priv` (L1088-1091)
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

### fn `def main() -> None` `@click.version_option()` (L1147-1155)
- @brief Execute main.
- @details Applies main logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def show(provider: str, window: str, output_json: bool, force_refresh: bool) -> None` (L1181-1267)
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

### fn `def _print_result(name: ProviderName, result, label: str | None = None) -> None` `priv` (L1268-1339)
- @brief Render CLI text output for one provider result.
- @details Formats usage percentage, reset countdown, remaining credits, cost, requests, and token counts for one provider/window result. Cost is formatted using `metrics.currency_symbol` (never hardcoded `$`).
- @param name {ProviderName} Provider name enum value.
- @param result {ProviderResult} Provider result to render.
- @param label {str | None} Optional window label suffix (e.g. `"5h"`, `"7d"`).
- @return {None} Function return value.
- @satisfies REQ-034
- @satisfies REQ-035
- @satisfies REQ-051

### fn `def _format_reset_duration(seconds: float) -> str` `priv` (L1340-1355)
- @brief Execute format reset duration.
- @details Applies format reset duration logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param seconds {float} Input parameter `seconds`.
- @return {str} Function return value.

### fn `def _should_render_metrics_after_error(` `priv` (L1356-1358)

### fn `def _should_print_claude_reset_pending_hint(` `priv` (L1376-1378)
- @brief Check whether CLI output must render metrics after printing an error line.
- @details Allows continuation only for Claude HTTP 429 partial-window state so the
5h section can include `Error:` and still display usage/reset lines.
- @param provider_name {ProviderName} Provider associated with rendered section.
- @param result {ProviderResult} Result being rendered.
- @return {bool} True when metrics should still be rendered after error line.
- @satisfies REQ-036

### fn `def _is_displayed_zero_percent(percent: float | None) -> bool` `priv` (L1398-1414)
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

### fn `def _progress_bar(percent: float, width: int = 20) -> str` `priv` (L1415-1427)
- @brief Execute progress bar.
- @details Applies progress bar logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param percent {float} Input parameter `percent`.
- @param width {int} Input parameter `width`.
- @return {str} Function return value.

### fn `def doctor() -> None` `@main.command()` (L1429-1481)
- @brief Execute doctor.
- @details Applies doctor logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def ui() -> None` `@main.command()` (L1483-1493)
- @brief Execute ui.
- @details Applies ui logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def env() -> None` `@main.command()` (L1495-1503)
- @brief Execute env.
- @details Applies env logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def setup() -> None` `@main.command()` (L1505-1704)
- @brief Execute setup.
- @details Prompts for `idle_delay_seconds`, `api_call_delay_seconds`, and `gnome_refresh_interval_seconds` in order, then prompts for per-provider currency symbols (choices: `$`, `£`, `€`, default `$`), then persists all values to `~/.config/aibar/config.json`. Also prompts for provider API keys and writes them to `~/.config/aibar/env`.
- @return {None} Function return value.
- @satisfies REQ-005
- @satisfies REQ-049
- @satisfies REQ-055
- @satisfies REQ-056
- @satisfies REQ-059

### fn `def login(provider: str) -> None` (L1752-1770)
- @brief Execute login.
- @details Applies login logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param provider {str} Input parameter `provider`.
- @return {None} Function return value.

### fn `def _login_claude() -> None` `priv` (L1771-1819)
- @brief Execute login claude.
- @details Applies login claude logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def _login_copilot() -> None` `priv` (L1820-1847)
- @brief Execute login copilot.
- @details Applies login copilot logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def _login_geminiai() -> None` `priv` (L1848-1884)
- @brief Execute GeminiAI OAuth login flow.
- @details Reuses persisted OAuth client configuration to launch browser-based authorization and persist refresh-capable Google credentials.
- @return {None} Function return value.
- @satisfies REQ-055
- @satisfies REQ-056

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`RetrievalPipelineOutput`|class|pub|62-88|class RetrievalPipelineOutput|
|`_normalize_utc`|fn|priv|89-101|def _normalize_utc(value: datetime) -> datetime|
|`_apply_api_call_delay`|fn|priv|102-130|def _apply_api_call_delay(throttle_state: dict[str, float...|
|`_extract_retry_after_seconds`|fn|priv|131-149|def _extract_retry_after_seconds(result: ProviderResult) ...|
|`_is_http_429_result`|fn|priv|150-160|def _is_http_429_result(result: ProviderResult) -> bool|
|`_serialize_results_payload`|fn|priv|161-162|def _serialize_results_payload(|
|`_empty_cache_document`|fn|priv|176-190|def _empty_cache_document() -> dict[str, object]|
|`_normalize_cache_document`|fn|priv|191-212|def _normalize_cache_document(cache_document: dict[str, o...|
|`_cache_payload_section`|fn|priv|213-225|def _cache_payload_section(cache_document: dict[str, obje...|
|`_cache_status_section`|fn|priv|226-238|def _cache_status_section(cache_document: dict[str, objec...|
|`_serialize_attempt_status`|fn|priv|239-257|def _serialize_attempt_status(result: ProviderResult) -> ...|
|`_record_attempt_status`|fn|priv|258-260|def _record_attempt_status(|
|`_extract_claude_snapshot_from_cache_document`|fn|priv|280-281|def _extract_claude_snapshot_from_cache_document(|
|`_get_window_attempt_status`|fn|priv|296-299|def _get_window_attempt_status(|
|`_is_failed_http_429_status`|fn|priv|319-333|def _is_failed_http_429_status(status_entry: dict[str, ob...|
|`_filter_cached_payload`|fn|priv|334-336|def _filter_cached_payload(|
|`_project_cached_window`|fn|priv|369-372|def _project_cached_window(|
|`_load_cached_results`|fn|priv|403-407|def _load_cached_results(|
|`_update_idle_time_after_refresh`|fn|priv|456-458|def _update_idle_time_after_refresh(|
|`_project_next_reset`|fn|priv|507-538|def _project_next_reset(resets_at_str: str, window: Windo...|
|`_apply_reset_projection`|fn|priv|539-573|def _apply_reset_projection(result: ProviderResult) -> Pr...|
|`get_providers`|fn|pub|574-589|def get_providers() -> dict[ProviderName, BaseProvider]|
|`parse_window`|fn|pub|590-609|def parse_window(window: str) -> WindowPeriod|
|`parse_provider`|fn|pub|610-626|def parse_provider(provider: str) -> ProviderName | None|
|`_fetch_result`|fn|priv|627-630|def _fetch_result(|
|`_fetch_claude_dual`|fn|priv|670-673|def _fetch_claude_dual(|
|`_extract_claude_dual_payload`|fn|priv|729-731|def _extract_claude_dual_payload(|
|`_normalize_claude_dual_payload`|fn|priv|753-775|def _normalize_claude_dual_payload(payload: object) -> di...|
|`_extract_snapshot_reset_at`|fn|priv|776-778|def _extract_snapshot_reset_at(|
|`_extract_snapshot_utilization`|fn|priv|801-803|def _extract_snapshot_utilization(|
|`_is_claude_rate_limited_result`|fn|priv|832-847|def _is_claude_rate_limited_result(result: ProviderResult...|
|`_build_claude_rate_limited_partial_result`|fn|priv|848-851|def _build_claude_rate_limited_partial_result(|
|`_refresh_and_persist_cache_payload`|fn|priv|896-899|def _refresh_and_persist_cache_payload(|
|`retrieve_results_via_cache_pipeline`|fn|pub|984-988|def retrieve_results_via_cache_pipeline(|
|`_build_cached_dual_window_results`|fn|priv|1088-1091|def _build_cached_dual_window_results(|
|`main`|fn|pub|1147-1155|def main() -> None|
|`show`|fn|pub|1181-1267|def show(provider: str, window: str, output_json: bool, f...|
|`_print_result`|fn|priv|1268-1339|def _print_result(name: ProviderName, result, label: str ...|
|`_format_reset_duration`|fn|priv|1340-1355|def _format_reset_duration(seconds: float) -> str|
|`_should_render_metrics_after_error`|fn|priv|1356-1358|def _should_render_metrics_after_error(|
|`_should_print_claude_reset_pending_hint`|fn|priv|1376-1378|def _should_print_claude_reset_pending_hint(|
|`_is_displayed_zero_percent`|fn|priv|1398-1414|def _is_displayed_zero_percent(percent: float | None) -> ...|
|`_progress_bar`|fn|priv|1415-1427|def _progress_bar(percent: float, width: int = 20) -> str|
|`doctor`|fn|pub|1429-1481|def doctor() -> None|
|`ui`|fn|pub|1483-1493|def ui() -> None|
|`env`|fn|pub|1495-1503|def env() -> None|
|`setup`|fn|pub|1505-1704|def setup() -> None|
|`login`|fn|pub|1752-1770|def login(provider: str) -> None|
|`_login_claude`|fn|priv|1771-1819|def _login_claude() -> None|
|`_login_copilot`|fn|priv|1820-1847|def _login_copilot() -> None|
|`_login_geminiai`|fn|priv|1848-1884|def _login_geminiai() -> None|


---

# config.py | Python | 548L | 35 symbols | 12 imports | 33 comments
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
from aibar.providers.geminiai import GeminiAICredentialStore
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
- var `DEFAULT_GNOME_REFRESH_INTERVAL_SECONDS = 60` (L28)
- var `DEFAULT_CURRENCY_SYMBOL = "$"` (L29)
### class `class RuntimeConfig(BaseModel)` : BaseModel (L39-60)
- @brief Define runtime configuration component for refresh throttling and currency controls.
- @details Encodes persisted CLI runtime controls used by `show` refresh logic, GNOME extension scheduling, and per-provider currency symbol resolution. Fields are validated with defaults that reduce rate-limit pressure. `currency_symbols` maps provider name strings to currency symbols (`$`, `£`, `€`); missing entries default to `DEFAULT_CURRENCY_SYMBOL` at resolution time. Optional GeminiAI fields persist Google Cloud project/billing identifiers used by OAuth-backed Monitoring/Billing API fetch execution.
- @satisfies CTN-008
- @satisfies REQ-049

### class `class IdleTimeState(BaseModel)` : BaseModel (L61-74)
- @brief Define persisted idle-time state component.
- @details Stores last successful refresh timestamp and computed idle-until timestamp in both epoch and human-readable ISO-8601 UTC formats.
- @satisfies CTN-009

### fn `def _ensure_app_config_dir() -> None` `priv` (L75-84)
- @brief Ensure AIBar configuration directory exists before file persistence.
- @details Creates `~/.config/aibar` recursively when missing. This function is called by env-file and runtime-config persistence helpers.
- @return {None} Function return value.

### fn `def _ensure_app_cache_dir() -> None` `priv` (L85-94)
- @brief Ensure AIBar cache directory exists before cache and idle-time persistence.
- @details Creates `~/.cache/aibar` recursively when missing. This function is called by CLI cache and idle-time persistence helpers.
- @return {None} Function return value.

### fn `def _sanitize_cache_payload(payload: dict[str, Any]) -> dict[str, Any]` `priv` (L95-129)
- @brief Redact sensitive keys from cache payload before disk persistence.
- @details Recursively traverses dictionaries/lists and replaces values for case-insensitive key matches in `{token,key,secret,password,authorization}` with deterministic placeholder string `[REDACTED]`.
- @param payload {dict[str, Any]} Cache document containing `payload` and `status` sections.
- @return {dict[str, Any]} Sanitized deep-copy structure safe for persistence.
- @satisfies DES-004

### fn `def clean(value: Any) -> Any` (L107-126)
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

### fn `def load_runtime_config() -> RuntimeConfig` (L130-146)
- @brief Load runtime refresh configuration from disk with schema validation.
- @details Reads `~/.config/aibar/config.json`, validates fields against `RuntimeConfig`, and returns defaults when file is missing or invalid.
- @return {RuntimeConfig} Validated runtime configuration payload.
- @satisfies CTN-008

### fn `def save_runtime_config(runtime_config: RuntimeConfig) -> None` (L147-162)
- @brief Persist runtime refresh configuration to disk.
- @details Serializes `RuntimeConfig` to `~/.config/aibar/config.json` using stable pretty-printed JSON (`indent=2`) for deterministic readability.
- @param runtime_config {RuntimeConfig} Validated runtime configuration model.
- @return {None} Function return value.
- @satisfies CTN-008

### fn `def load_cli_cache() -> dict[str, Any] | None` (L163-180)
- @brief Load CLI cache payload from disk.
- @details Reads `~/.cache/aibar/cache.json` and returns parsed object only when payload root is a JSON object with canonical cache sections.
- @return {dict[str, Any] | None} Parsed cache payload or None if unavailable.
- @satisfies CTN-004
- @satisfies REQ-047

### fn `def resolve_currency_symbol(raw: dict[str, Any], provider_name: str) -> str` (L181-210)
- @brief Resolve currency symbol for a provider result from API response or config.
- @details Extraction priority: 1. `raw["currency"]` field: if a recognized symbol (`$`, `£`, `€`) → use directly; if an ISO-4217 code (`USD`, `GBP`, `EUR`) → map to symbol. 2. `RuntimeConfig.currency_symbols[provider_name]` configured default. 3. `DEFAULT_CURRENCY_SYMBOL` (`"$"`) as final fallback.
- @param raw {dict[str, Any]} Raw API response dict from the provider fetch call.
- @param provider_name {str} Provider name string key (e.g. `"claude"`, `"openai"`).
- @return {str} Resolved currency symbol; always a member of `VALID_CURRENCY_SYMBOLS`.
- @satisfies REQ-050

### fn `def save_cli_cache(payload: dict[str, Any]) -> None` (L211-233)
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

### fn `def load_idle_time() -> IdleTimeState | None` (L234-250)
- @brief Load idle-time control state from disk.
- @details Reads and validates `~/.cache/aibar/idle-time.json`. Invalid or unreadable payloads return None and are treated as missing state.
- @return {IdleTimeState | None} Validated idle-time state or None.
- @satisfies CTN-009

### fn `def save_idle_time(last_success_at: datetime, idle_until: datetime) -> IdleTimeState` (L251-276)
- @brief Persist idle-time state using epoch and human-readable timestamp fields.
- @details Normalizes timestamps to UTC, serializes both epoch and ISO strings, and writes `~/.cache/aibar/idle-time.json` in pretty-printed JSON.
- @param last_success_at {datetime} Last successful refresh timestamp.
- @param idle_until {datetime} Timestamp until refresh must remain disabled.
- @return {IdleTimeState} Persisted idle-time model.
- @satisfies CTN-009

### fn `def remove_idle_time_file() -> None` (L277-290)
- @brief Remove persisted idle-time state file if present.
- @details Deletes `~/.cache/aibar/idle-time.json` to force immediate refresh behavior on subsequent `show` execution.
- @return {None} Function return value.
- @satisfies REQ-039

### fn `def load_env_file() -> dict[str, str]` (L291-309)
- @brief Execute load env file.
- @details Applies load env file logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {dict[str, str]} Function return value.

### fn `def write_env_file(updates: dict[str, str]) -> None` (L310-349)
- @brief Execute write env file.
- @details Applies write env file logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param updates {dict[str, str]} Input parameter `updates`.
- @return {None} Function return value.

### class `class Config` (L350-546)
- @brief Define config component.
- @details Encapsulates config state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `ENV_VARS =` (L357)
- var `PROVIDER_INFO =` (L367)
- fn `def get_token(self, provider: ProviderName) -> str | None` (L406-449)
  - @brief Execute get token.
  - @details Applies get token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @return {str | None} Function return value.
- fn `def is_provider_configured(self, provider: ProviderName) -> bool` (L450-481)
  - @brief Execute is provider configured.
  - @details Applies is provider configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @return {bool} Function return value.
- fn `def get_provider_status(self, provider: ProviderName) -> dict[str, Any]` (L482-503)
  - @brief Execute get provider status.
  - @details Applies get provider status logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @return {dict[str, Any]} Function return value.
- fn `def get_all_provider_status(self) -> list[dict[str, Any]]` (L504-511)
  - @brief Execute get all provider status.
  - @details Applies get all provider status logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {list[dict[str, Any]]} Function return value.
- fn `def _get_token_preview(self, provider: ProviderName) -> str | None` `priv` (L512-523)
  - @brief Execute get token preview.
  - @details Applies get token preview logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @return {str | None} Function return value.
- fn `def get_env_var_help(self) -> str` (L524-546)
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
|`DEFAULT_GNOME_REFRESH_INTERVAL_SECONDS`|var|pub|28||
|`DEFAULT_CURRENCY_SYMBOL`|var|pub|29||
|`RuntimeConfig`|class|pub|39-60|class RuntimeConfig(BaseModel)|
|`IdleTimeState`|class|pub|61-74|class IdleTimeState(BaseModel)|
|`_ensure_app_config_dir`|fn|priv|75-84|def _ensure_app_config_dir() -> None|
|`_ensure_app_cache_dir`|fn|priv|85-94|def _ensure_app_cache_dir() -> None|
|`_sanitize_cache_payload`|fn|priv|95-129|def _sanitize_cache_payload(payload: dict[str, Any]) -> d...|
|`clean`|fn|pub|107-126|def clean(value: Any) -> Any|
|`load_runtime_config`|fn|pub|130-146|def load_runtime_config() -> RuntimeConfig|
|`save_runtime_config`|fn|pub|147-162|def save_runtime_config(runtime_config: RuntimeConfig) ->...|
|`load_cli_cache`|fn|pub|163-180|def load_cli_cache() -> dict[str, Any] | None|
|`resolve_currency_symbol`|fn|pub|181-210|def resolve_currency_symbol(raw: dict[str, Any], provider...|
|`save_cli_cache`|fn|pub|211-233|def save_cli_cache(payload: dict[str, Any]) -> None|
|`load_idle_time`|fn|pub|234-250|def load_idle_time() -> IdleTimeState | None|
|`save_idle_time`|fn|pub|251-276|def save_idle_time(last_success_at: datetime, idle_until:...|
|`remove_idle_time_file`|fn|pub|277-290|def remove_idle_time_file() -> None|
|`load_env_file`|fn|pub|291-309|def load_env_file() -> dict[str, str]|
|`write_env_file`|fn|pub|310-349|def write_env_file(updates: dict[str, str]) -> None|
|`Config`|class|pub|350-546|class Config|
|`Config.ENV_VARS`|var|pub|357||
|`Config.PROVIDER_INFO`|var|pub|367||
|`Config.get_token`|fn|pub|406-449|def get_token(self, provider: ProviderName) -> str | None|
|`Config.is_provider_configured`|fn|pub|450-481|def is_provider_configured(self, provider: ProviderName) ...|
|`Config.get_provider_status`|fn|pub|482-503|def get_provider_status(self, provider: ProviderName) -> ...|
|`Config.get_all_provider_status`|fn|pub|504-511|def get_all_provider_status(self) -> list[dict[str, Any]]|
|`Config._get_token_preview`|fn|priv|512-523|def _get_token_preview(self, provider: ProviderName) -> s...|
|`Config.get_env_var_help`|fn|pub|524-546|def get_env_var_help(self) -> str|


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

# claude_oauth.py | Python | 338L | 15 symbols | 10 imports | 18 comments
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
### fn `async def _request_usage(self, client: httpx.AsyncClient) -> httpx.Response` `priv` (L87-124)
- @brief Execute HTTP GET to usage endpoint with retry on HTTP 429.
- @details Retries up to MAX_RETRIES times on 429 responses, respecting the retry-after header with exponential backoff fallback and random jitter to prevent thundering-herd synchronization. Backoff sequence with RETRY_BACKOFF_BASE=2.0: ~2-3s, ~4-5s, ~8-9s (total ~14-17s).
- @param client {httpx.AsyncClient} Reusable HTTP client session.
- @return {httpx.Response} Final HTTP response after retries exhausted or success.

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L125-164)
- @brief Execute fetch for a single window period.
- @details Makes one HTTP request to the usage endpoint (with retry on 429) and parses the response for the requested window.
- @param window {WindowPeriod} Window period to parse from the API response.
- @return {ProviderResult} Parsed result for the requested window.
- @throws {AuthenticationError} When the OAuth token is invalid or expired.
- @throws {ProviderError} On unexpected non-HTTP errors.

### fn `async def fetch_all_windows(` (L165-166)

### fn `def _handle_response(` `priv` (L219-220)
- @brief Execute a single API call and parse results for multiple windows.
- @details The usage endpoint returns data for all windows in one response.
This method avoids redundant HTTP requests when multiple windows are needed.
- @param windows {list[WindowPeriod]} Window periods to parse from one API response.
- @return {dict[WindowPeriod, ProviderResult]} Map of window to parsed result.
- @throws {AuthenticationError} When the OAuth token is invalid or expired.
- @throws {ProviderError} On unexpected non-HTTP errors.

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L272-338)
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
|`_request_usage`|fn|priv|87-124|async def _request_usage(self, client: httpx.AsyncClient)...|
|`fetch`|fn|pub|125-164|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`fetch_all_windows`|fn|pub|165-166|async def fetch_all_windows(|
|`_handle_response`|fn|priv|219-220|def _handle_response(|
|`_parse_response`|fn|priv|272-338|def _parse_response(self, data: dict, window: WindowPerio...|


---

# codex.py | Python | 443L | 22 symbols | 7 imports | 33 comments
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

### class `class CodexTokenRefresher` (L196-259)
- @brief Define codex token refresher component.
- @details Encapsulates codex token refresher state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `REFRESH_URL = "https://auth.openai.com/oauth/token"` (L202)
  - @brief Define codex token refresher component.
  - @details Encapsulates codex token refresher state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"` (L203)
- fn `async def refresh(self, credentials: CodexCredentials) -> CodexCredentials` (L205-259)
  - @brief Execute refresh.
  - @details Applies refresh logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param credentials {CodexCredentials} Input parameter `credentials`.
  - @return {CodexCredentials} Function return value.
  - @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### class `class CodexProvider(BaseProvider)` : BaseProvider (L260-298)
- @brief Define codex provider component.
- @details Encapsulates codex provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `BASE_URL = "https://chatgpt.com/backend-api"` (L269)
- var `USAGE_PATH = "/wham/usage"` (L270)
- fn `def __init__(self, credentials: CodexCredentials | None = None) -> None` `priv` (L272-282)
  - @brief Execute init.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param credentials {CodexCredentials | None} Input parameter `credentials`.
  - @return {None} Function return value.
- fn `def is_configured(self) -> bool` (L283-290)
  - @brief Execute is configured.
  - @details Applies is configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {bool} Function return value.
- fn `def get_config_help(self) -> str` (L291-298)
  - @brief Execute get config help.
  - @details Applies get config help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str} Function return value.

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L310-389)
- @brief Execute fetch.
- @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L390-443)
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
|`CodexTokenRefresher`|class|pub|196-259|class CodexTokenRefresher|
|`CodexTokenRefresher.REFRESH_URL`|var|pub|202||
|`CodexTokenRefresher.CLIENT_ID`|var|pub|203||
|`CodexTokenRefresher.refresh`|fn|pub|205-259|async def refresh(self, credentials: CodexCredentials) ->...|
|`CodexProvider`|class|pub|260-298|class CodexProvider(BaseProvider)|
|`CodexProvider.BASE_URL`|var|pub|269||
|`CodexProvider.USAGE_PATH`|var|pub|270||
|`CodexProvider.__init__`|fn|priv|272-282|def __init__(self, credentials: CodexCredentials | None =...|
|`CodexProvider.is_configured`|fn|pub|283-290|def is_configured(self) -> bool|
|`CodexProvider.get_config_help`|fn|pub|291-298|def get_config_help(self) -> str|
|`fetch`|fn|pub|310-389|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|390-443|def _parse_response(self, data: dict, window: WindowPerio...|


---

# copilot.py | Python | 434L | 28 symbols | 9 imports | 32 comments
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
import asyncio
```

## Definitions

### fn `def _resolve_provider_currency(raw: dict, provider_name: str) -> str` `priv` (L26-38)
- @brief Resolve currency symbol from raw API response or configured provider default.
- @details Delegates to `resolve_currency_symbol` in `aibar.config` (lazy import).
- @param raw {dict} Raw API response dict.
- @param provider_name {str} Provider name key.
- @return {str} Resolved currency symbol.
- @satisfies REQ-050

### class `class CopilotDeviceFlow` (L39-127)
- @brief Define copilot device flow component.
- @details Encapsulates copilot device flow state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `CLIENT_ID = "Iv1.b507a08c87ecfe98"` (L46)
- var `SCOPES = "read:user"` (L47)
- var `DEVICE_CODE_URL = "https://github.com/login/device/code"` (L49)
- var `TOKEN_URL = "https://github.com/login/oauth/access_token"` (L50)
- fn `async def request_device_code(self) -> dict[str, Any]` (L52-76)
  - @brief Execute request device code.
  - @details Applies request device code logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {dict[str, Any]} Function return value.
  - @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.
- fn `async def poll_for_token(self, device_code: str, interval: int = 5) -> str` (L77-127)
  - @brief Execute poll for token.
  - @details Applies poll for token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param device_code {str} Input parameter `device_code`.
  - @param interval {int} Input parameter `interval`.
  - @return {str} Function return value.
  - @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### class `class CopilotCredentialStore` (L128-184)
- @brief Define copilot credential store component.
- @details Encapsulates copilot credential store state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `CONFIG_DIR = Path.home() / ".config" / "aibar"` (L134)
  - @brief Define copilot credential store component.
  - @details Encapsulates copilot credential store state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `CREDS_FILE = CONFIG_DIR / "copilot.json"` (L135)
- var `CODEXBAR_CONFIG = Path.home() / ".codexbar" / "config.json"` (L136)
- fn `def load_token(self) -> str | None` (L138-169)
  - @brief Execute load token.
  - @details Applies load token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str | None} Function return value.
- fn `def save_token(self, token: str) -> None` (L170-184)
  - @brief Execute save token.
  - @details Applies save token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param token {str} Input parameter `token`.
  - @return {None} Function return value.

### class `class CopilotProvider(BaseProvider)` : BaseProvider (L185-225)
- @brief Define copilot provider component.
- @details Encapsulates copilot provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `USAGE_URL = "https://api.github.com/copilot_internal/user"` (L192)
  - @brief Define copilot provider component.
  - @details Encapsulates copilot provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `EDITOR_VERSION = "vscode/1.96.2"` (L195)
- var `PLUGIN_VERSION = "copilot-chat/0.26.7"` (L196)
- var `USER_AGENT = "GitHubCopilotChat/0.26.7"` (L197)
- var `API_VERSION = "2025-04-01"` (L198)
- fn `def __init__(self, token: str | None = None) -> None` `priv` (L200-209)
  - @brief Execute init.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param token {str | None} Input parameter `token`.
  - @return {None} Function return value.
- fn `def is_configured(self) -> bool` (L210-217)
  - @brief Execute is configured.
  - @details Applies is configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {bool} Function return value.
- fn `def get_config_help(self) -> str` (L218-225)
  - @brief Execute get config help.
  - @details Applies get config help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str} Function return value.

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L235-306)
- @brief Execute fetch.
- @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L307-403)
- @brief Execute parse response.
- @details Applies parse response logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param data {dict} Input parameter `data`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.

### fn `def _get_snapshot(key_camel: str, key_snake: str) -> dict` `priv` (L317-326)
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

### fn `def _extract_quota_data(snapshot: dict) -> tuple[float | None, float | None]` `priv` (L327-353)
- @brief Execute extract quota data.
- @details Applies extract quota data logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param snapshot {dict} Input parameter `snapshot`.
- @return {tuple[float | None, float | None]} Function return value.

### fn `async def login(self) -> str` (L404-434)
- @brief Execute login.
- @details Applies login logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {str} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`_resolve_provider_currency`|fn|priv|26-38|def _resolve_provider_currency(raw: dict, provider_name: ...|
|`CopilotDeviceFlow`|class|pub|39-127|class CopilotDeviceFlow|
|`CopilotDeviceFlow.CLIENT_ID`|var|pub|46||
|`CopilotDeviceFlow.SCOPES`|var|pub|47||
|`CopilotDeviceFlow.DEVICE_CODE_URL`|var|pub|49||
|`CopilotDeviceFlow.TOKEN_URL`|var|pub|50||
|`CopilotDeviceFlow.request_device_code`|fn|pub|52-76|async def request_device_code(self) -> dict[str, Any]|
|`CopilotDeviceFlow.poll_for_token`|fn|pub|77-127|async def poll_for_token(self, device_code: str, interval...|
|`CopilotCredentialStore`|class|pub|128-184|class CopilotCredentialStore|
|`CopilotCredentialStore.CONFIG_DIR`|var|pub|134||
|`CopilotCredentialStore.CREDS_FILE`|var|pub|135||
|`CopilotCredentialStore.CODEXBAR_CONFIG`|var|pub|136||
|`CopilotCredentialStore.load_token`|fn|pub|138-169|def load_token(self) -> str | None|
|`CopilotCredentialStore.save_token`|fn|pub|170-184|def save_token(self, token: str) -> None|
|`CopilotProvider`|class|pub|185-225|class CopilotProvider(BaseProvider)|
|`CopilotProvider.USAGE_URL`|var|pub|192||
|`CopilotProvider.EDITOR_VERSION`|var|pub|195||
|`CopilotProvider.PLUGIN_VERSION`|var|pub|196||
|`CopilotProvider.USER_AGENT`|var|pub|197||
|`CopilotProvider.API_VERSION`|var|pub|198||
|`CopilotProvider.__init__`|fn|priv|200-209|def __init__(self, token: str | None = None) -> None|
|`CopilotProvider.is_configured`|fn|pub|210-217|def is_configured(self) -> bool|
|`CopilotProvider.get_config_help`|fn|pub|218-225|def get_config_help(self) -> str|
|`fetch`|fn|pub|235-306|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|307-403|def _parse_response(self, data: dict, window: WindowPerio...|
|`_get_snapshot`|fn|priv|317-326|def _get_snapshot(key_camel: str, key_snake: str) -> dict|
|`_extract_quota_data`|fn|priv|327-353|def _extract_quota_data(snapshot: dict) -> tuple[float | ...|
|`login`|fn|pub|404-434|async def login(self) -> str|


---

# geminiai.py | Python | 802L | 41 symbols | 18 imports | 36 comments
> Path: `src/aibar/aibar/providers/geminiai.py`
- @brief GeminiAI provider with Google OAuth, Cloud Monitoring, and Cloud Billing integration.
- @details Implements OAuth credential persistence, token refresh, usage retrieval from
Cloud Monitoring, billing metadata retrieval from Cloud Billing, and normalization into
AIBar provider result contracts.

## Imports
```
from __future__ import annotations
import asyncio
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
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

- var `GEMINIAI_OAUTH_CLIENT_PATH = Path.home() / ".config" / "aibar" / "geminiai_oauth_client.json"` (L40)
- var `GEMINIAI_OAUTH_TOKEN_PATH = Path.home() / ".config" / "aibar" / "geminiai_oauth_token.json"` (L41)
- var `GEMINIAI_PROJECT_ID_ENV_VAR = "GEMINIAI_PROJECT_ID"` (L42)
- var `GEMINIAI_BILLING_ACCOUNT_ENV_VAR = "GEMINIAI_BILLING_ACCOUNT"` (L43)
- var `GEMINIAI_ACCESS_TOKEN_ENV_VAR = "GEMINIAI_OAUTH_ACCESS_TOKEN"` (L44)
### fn `def _to_rfc3339_utc(value: datetime) -> str` `priv` (L47-58)
- @brief Convert datetime to RFC3339 UTC string accepted by Google APIs.
- @details Normalizes timezone awareness and strips microseconds to produce stable API query timestamps.
- @param value {datetime} Input datetime value.
- @return {str} RFC3339 UTC timestamp (e.g. `2026-03-08T11:00:00Z`).

### fn `def _extract_http_status(error: HttpError) -> int` `priv` (L59-79)
- @brief Extract integer HTTP status from Google API HttpError.
- @details Returns `0` when status is unavailable to preserve deterministic error payload shape.
- @param error {HttpError} Google API exception.
- @return {int} HTTP status code or `0`.

### fn `def _extract_retry_after_seconds(error: HttpError) -> float` `priv` (L80-103)
- @brief Extract retry-after seconds from HttpError response headers.
- @details Reads `retry-after` case-insensitively and normalizes invalid values to `0.0`.
- @param error {HttpError} Google API exception.
- @return {float} Non-negative retry-after delay in seconds.

### class `class GeminiAIWindowRange` `@dataclass(frozen=True)` (L105-114)
- @brief Immutable time-range descriptor for one GeminiAI fetch window.
- @details Encodes start and end UTC timestamps used for Monitoring API queries.

### class `class GeminiAICredentialStore` (L115-314)
- @brief OAuth credential persistence and validation helper for GeminiAI.
- @details Manages client-secret JSON validation, token-file persistence, and interactive InstalledAppFlow authorization.
- fn `def __init__(` `priv` (L122-125)
  - @brief OAuth credential persistence and validation helper for GeminiAI.
  - @details Manages client-secret JSON validation, token-file persistence, and
interactive InstalledAppFlow authorization.
- fn `def _ensure_config_dir(self) -> None` `priv` (L136-143)
  - @brief Initialize credential store with optional custom file paths.
  - @brief Create parent directories for OAuth files when missing.
  - @param client_config_path {Path | None} Optional OAuth client config path.
  - @param token_path {Path | None} Optional OAuth token path.
  - @return {None} Function return value.
  - @return {None} Function return value.
- fn `def has_client_config(self) -> bool` (L144-150)
  - @brief Check whether GeminiAI client config JSON exists.
  - @return {bool} True when client config file exists.
- fn `def has_authorized_credentials(self) -> bool` (L151-161)
  - @brief Check whether GeminiAI authorized token material exists.
  - @details Environment access-token override is treated as configured token material.
  - @return {bool} True when token file or env token is available.
- fn `def validate_client_config(self, payload: dict[str, Any]) -> dict[str, Any]` (L162-191)
  - @brief Validate Google InstalledApp OAuth client-secret payload.
  - @details Enforces required `installed` section fields used by `InstalledAppFlow.from_client_config`.
  - @param payload {dict[str, Any]} Decoded JSON payload to validate.
  - @return {dict[str, Any]} Normalized payload.
  - @throws {ValueError} When required fields are missing or malformed.
- fn `def save_client_config(self, payload: dict[str, Any]) -> None` (L192-204)
  - @brief Persist validated OAuth client config JSON to disk.
  - @param payload {dict[str, Any]} Validated client payload.
  - @return {None} Function return value.
- fn `def load_client_config(self) -> dict[str, Any]` (L205-223)
  - @brief Load and validate persisted OAuth client config JSON.
  - @return {dict[str, Any]} Validated OAuth client payload.
  - @throws {FileNotFoundError} When client config file is missing.
  - @throws {ValueError} When payload is invalid JSON or fails validation.
- fn `def extract_project_id(self, payload: dict[str, Any]) -> str | None` (L224-237)
  - @brief Extract project_id from validated OAuth payload.
  - @param payload {dict[str, Any]} Validated OAuth payload.
  - @return {str | None} Project identifier or None when absent.
- fn `def save_authorized_credentials(self, credentials: Credentials) -> None` (L238-247)
  - @brief Persist authorized-user OAuth credentials JSON.
  - @param credentials {Credentials} Google OAuth credentials object.
  - @return {None} Function return value.
- fn `def authorize_interactively(` (L248-250)
- fn `def load_access_token(self) -> str | None` (L266-283)
  - @brief Execute OAuth browser flow and persist refresh-capable credentials.
  - @brief Load access token from env override or token file.
  - @details Uses InstalledAppFlow local-server flow (`http://localhost`) and
saves authorized-user token JSON to disk.
  - @param scopes {tuple[str, ...]} OAuth scopes requested during authorization.
  - @return {Credentials} Authorized credentials.
  - @return {str | None} Access token or None when unavailable.
  - @throws {ValueError} When client config is invalid.
- fn `def load_credentials(` (L284-286)

### class `class GeminiAIProvider(BaseProvider)` : BaseProvider (L318-368)
- @brief GeminiAI usage provider backed by Google Cloud APIs.
- @details Retrieves usage counters from Cloud Monitoring and billing metadata from Cloud Billing, then maps data into AIBar `ProviderResult` models.
- var `REQUEST_COUNT_FILTER = 'metric.type="serviceruntime.googleapis.com/api/request_count"'` (L327)
  - @brief GeminiAI usage provider backed by Google Cloud APIs.
  - @details Retrieves usage counters from Cloud Monitoring and billing metadata from
Cloud Billing, then maps data into AIBar `ProviderResult` models.
- var `COST_FILTER = 'metric.type="billing.googleapis.com/billing/account/cost"'` (L333)
- fn `def __init__(` `priv` (L335-339)
- fn `def is_configured(self) -> bool` (L352-361)
  - @brief Initialize GeminiAI provider with optional overrides.
  - @brief Check whether GeminiAI provider has required auth and project metadata.
  - @param credential_store {GeminiAICredentialStore | None} Optional credential store.
  - @param project_id {str | None} Optional project id override.
  - @param billing_account {str | None} Optional billing account override.
  - @return {None} Function return value.
  - @return {bool} True when project id and OAuth token material are available.
- fn `def get_config_help(self) -> str` (L362-368)
  - @brief Return setup guidance for GeminiAI OAuth configuration.
  - @return {str} Provider-specific setup instructions.

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L377-404)
- @brief Fetch GeminiAI usage/cost metrics for one window.
- @details Executes synchronous Google API calls in a worker thread and returns normalized provider metrics. HTTP 429 responses are normalized as rate-limit provider error payloads with retry-after metadata.
- @param window {WindowPeriod} Requested window period.
- @return {ProviderResult} Provider result payload.
- @throws {AuthenticationError} When OAuth credentials are invalid.

### fn `def _fetch_sync(self, window: WindowPeriod) -> ProviderResult` `priv` (L405-538)
- @brief Execute blocking Google API retrieval flow for GeminiAI metrics.
- @param window {WindowPeriod} Requested window period.
- @return {ProviderResult} Normalized provider result.
- @throws {AuthenticationError} When credentials are missing/invalid.
- @throws {ProviderError} On non-auth API failures.

### fn `def _build_window_range(self, window: WindowPeriod) -> GeminiAIWindowRange` `priv` (L539-553)
- @brief Build UTC time interval used for Monitoring queries.
- @param window {WindowPeriod} Requested window period.
- @return {GeminiAIWindowRange} Start/end UTC timestamps.

### fn `def _resolve_project_id(self) -> str | None` `priv` (L554-575)
- @brief Resolve project id from override, env, runtime config, or client JSON.
- @return {str | None} Project id or None when unresolved.

### fn `def _resolve_billing_account(` `priv` (L576-579)

### fn `def _normalize_billing_account(self, value: str) -> str | None` `priv` (L615-627)
- @brief Normalize billing account identifier to canonical path format.
- @param value {str} Candidate billing account identifier.
- @return {str | None} Canonical `billingAccounts/<id>` or None.

### fn `def _build_monitoring_service(self, credentials: Credentials) -> Any` `priv` (L628-635)
- @brief Build Google Cloud Monitoring API client.
- @param credentials {Credentials} OAuth credentials.
- @return {Any} Monitoring service client.

### fn `def _build_billing_service(self, credentials: Credentials) -> Any` `priv` (L636-643)
- @brief Build Google Cloud Billing API client.
- @param credentials {Credentials} OAuth credentials.
- @return {Any} Billing service client.

### fn `def _query_monitoring_metric(` `priv` (L644-651)

### fn `def _sum_time_series_values(self, response: dict[str, Any]) -> float | None` `priv` (L690-733)
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

### fn `def _list_billing_accounts(self, billing_service: Any) -> list[dict[str, Any]]` `priv` (L734-745)
- @brief List billing accounts visible to current OAuth identity.
- @param billing_service {Any} Cloud Billing client.
- @return {list[dict[str, Any]]} Billing account payload list.

### fn `def _get_project_billing_info(` `priv` (L746-749)

### fn `def _build_metrics(` `priv` (L772-777)
- @brief Retrieve billing-account linkage metadata for one project.
- @param billing_service {Any} Cloud Billing client.
- @param project_id {str} Google Cloud project id.
- @return {dict[str, Any]} Billing info payload or empty object.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`GEMINIAI_OAUTH_CLIENT_PATH`|var|pub|40||
|`GEMINIAI_OAUTH_TOKEN_PATH`|var|pub|41||
|`GEMINIAI_PROJECT_ID_ENV_VAR`|var|pub|42||
|`GEMINIAI_BILLING_ACCOUNT_ENV_VAR`|var|pub|43||
|`GEMINIAI_ACCESS_TOKEN_ENV_VAR`|var|pub|44||
|`_to_rfc3339_utc`|fn|priv|47-58|def _to_rfc3339_utc(value: datetime) -> str|
|`_extract_http_status`|fn|priv|59-79|def _extract_http_status(error: HttpError) -> int|
|`_extract_retry_after_seconds`|fn|priv|80-103|def _extract_retry_after_seconds(error: HttpError) -> float|
|`GeminiAIWindowRange`|class|pub|105-114|class GeminiAIWindowRange|
|`GeminiAICredentialStore`|class|pub|115-314|class GeminiAICredentialStore|
|`GeminiAICredentialStore.__init__`|fn|priv|122-125|def __init__(|
|`GeminiAICredentialStore._ensure_config_dir`|fn|priv|136-143|def _ensure_config_dir(self) -> None|
|`GeminiAICredentialStore.has_client_config`|fn|pub|144-150|def has_client_config(self) -> bool|
|`GeminiAICredentialStore.has_authorized_credentials`|fn|pub|151-161|def has_authorized_credentials(self) -> bool|
|`GeminiAICredentialStore.validate_client_config`|fn|pub|162-191|def validate_client_config(self, payload: dict[str, Any])...|
|`GeminiAICredentialStore.save_client_config`|fn|pub|192-204|def save_client_config(self, payload: dict[str, Any]) -> ...|
|`GeminiAICredentialStore.load_client_config`|fn|pub|205-223|def load_client_config(self) -> dict[str, Any]|
|`GeminiAICredentialStore.extract_project_id`|fn|pub|224-237|def extract_project_id(self, payload: dict[str, Any]) -> ...|
|`GeminiAICredentialStore.save_authorized_credentials`|fn|pub|238-247|def save_authorized_credentials(self, credentials: Creden...|
|`GeminiAICredentialStore.authorize_interactively`|fn|pub|248-250|def authorize_interactively(|
|`GeminiAICredentialStore.load_access_token`|fn|pub|266-283|def load_access_token(self) -> str | None|
|`GeminiAICredentialStore.load_credentials`|fn|pub|284-286|def load_credentials(|
|`GeminiAIProvider`|class|pub|318-368|class GeminiAIProvider(BaseProvider)|
|`GeminiAIProvider.REQUEST_COUNT_FILTER`|var|pub|327||
|`GeminiAIProvider.COST_FILTER`|var|pub|333||
|`GeminiAIProvider.__init__`|fn|priv|335-339|def __init__(|
|`GeminiAIProvider.is_configured`|fn|pub|352-361|def is_configured(self) -> bool|
|`GeminiAIProvider.get_config_help`|fn|pub|362-368|def get_config_help(self) -> str|
|`fetch`|fn|pub|377-404|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_fetch_sync`|fn|priv|405-538|def _fetch_sync(self, window: WindowPeriod) -> ProviderRe...|
|`_build_window_range`|fn|priv|539-553|def _build_window_range(self, window: WindowPeriod) -> Ge...|
|`_resolve_project_id`|fn|priv|554-575|def _resolve_project_id(self) -> str | None|
|`_resolve_billing_account`|fn|priv|576-579|def _resolve_billing_account(|
|`_normalize_billing_account`|fn|priv|615-627|def _normalize_billing_account(self, value: str) -> str |...|
|`_build_monitoring_service`|fn|priv|628-635|def _build_monitoring_service(self, credentials: Credenti...|
|`_build_billing_service`|fn|priv|636-643|def _build_billing_service(self, credentials: Credentials...|
|`_query_monitoring_metric`|fn|priv|644-651|def _query_monitoring_metric(|
|`_sum_time_series_values`|fn|priv|690-733|def _sum_time_series_values(self, response: dict[str, Any...|
|`_list_billing_accounts`|fn|priv|734-745|def _list_billing_accounts(self, billing_service: Any) ->...|
|`_get_project_billing_info`|fn|priv|746-749|def _get_project_billing_info(|
|`_build_metrics`|fn|priv|772-777|def _build_metrics(|


---

# openai_usage.py | Python | 242L | 12 symbols | 7 imports | 16 comments
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

# openrouter.py | Python | 209L | 11 symbols | 4 imports | 11 comments
> Path: `src/aibar/aibar/providers/openrouter.py`
- @brief OpenRouter key usage and credit provider.
- @details Fetches key usage snapshots and quota limits, then transforms provider payloads into normalized cost and quota metrics.

## Imports
```
import httpx
from aibar.providers.base import (
from aibar.config import config
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

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L64-132)
- @brief Execute fetch.
- @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L133-168)
- @brief Execute parse response.
- @details Applies parse response logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param data {dict} Input parameter `data`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.
- @satisfies REQ-050

### fn `def _get_usage(self, payload: dict, window: WindowPeriod) -> float` `priv` (L169-182)
- @brief Execute get usage.
- @details Applies get usage logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param payload {dict} Input parameter `payload`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {float} Function return value.

### fn `def _get_byok_usage(self, payload: dict, window: WindowPeriod) -> float` `priv` (L183-196)
- @brief Execute get byok usage.
- @details Applies get byok usage logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param payload {dict} Input parameter `payload`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {float} Function return value.

### fn `def _to_float(self, value: float | int | None) -> float` `priv` (L197-209)
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
|`_parse_response`|fn|priv|133-168|def _parse_response(self, data: dict, window: WindowPerio...|
|`_get_usage`|fn|priv|169-182|def _get_usage(self, payload: dict, window: WindowPeriod)...|
|`_get_byok_usage`|fn|priv|183-196|def _get_byok_usage(self, payload: dict, window: WindowPe...|
|`_to_float`|fn|priv|197-209|def _to_float(self, value: float | int | None) -> float|


---

# ui.py | Python | 722L | 32 symbols | 13 imports | 43 comments
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

### class `class ProviderCard(Static)` : Static (L47-246)
- @brief Define provider card component.
- @details Encapsulates provider card state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `def __init__(` `priv` (L124-127)
  - @brief Define provider card component.
  - @details Encapsulates provider card state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `def compose(self) -> ComposeResult` (L140-163)
  - @brief Execute init.
  - @brief Execute compose.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @details Applies compose logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider_name {ProviderName} Input parameter `provider_name`.
  - @param kwargs {None} Input parameter `kwargs`.
  - @return {None} Function return value.
  - @return {ComposeResult} Function return value.

### fn `def watch_result(self, result: ProviderResult | None) -> None` (L164-260)
- @brief Render provider metrics into the TUI card widget.
- @details Triggered when the reactive `result` attribute changes. Builds usage bar, cost, requests, and token rows. Cost label uses `metrics.currency_symbol` (never hardcoded `$`).
- @param result {ProviderResult | None} Updated provider result; no-op when `None`.
- @return {None} Function return value.
- @satisfies REQ-043
- @satisfies REQ-052

### fn `def watch_is_loading(self, loading: bool) -> None` (L261-273)
- @brief Execute watch is loading.
- @details Applies watch is loading logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param loading {bool} Input parameter `loading`.
- @return {None} Function return value.

### fn `def _is_rate_limit_quota_error(self, result: ProviderResult) -> bool` `priv` (L274-288)
- @brief Check whether result is a rate-limit payload that still carries quota metrics.
- @details Detects the normalized Claude/Codex/Copilot rate-limit message with available `limit` and `remaining` values so card rendering can continue without showing the textual error banner.
- @param result {ProviderResult} Provider result candidate.
- @return {bool} True when result error is rate-limit with quota metrics.

### fn `def _is_displayed_full_percent(self, percent: float | None) -> bool` `priv` (L289-300)
- @brief Check whether usage renders as `100.0%` in one-decimal output.
- @details Applies display-rounding semantics used by Textual labels so near-full values (for example `99.96`) are treated as full usage.
- @param percent {float | None} Candidate usage percentage.
- @return {bool} True when rendered one-decimal value is `100.0%`.

### fn `def _supports_limit_reached_hint(self, result: ProviderResult) -> bool` `priv` (L301-314)
- @brief Validate whether provider/window pair supports `Limit reached!` hint.
- @details Limits warning rendering scope to Claude/Codex `5h` or `7d` cards and Copilot `30d` cards.
- @param result {ProviderResult} Provider result candidate.
- @return {bool} True when provider/window pair is eligible.

### fn `def _should_show_limit_reached_hint(self, result: ProviderResult) -> bool` `priv` (L315-325)
- @brief Determine whether reset text must include `⚠️ Limit reached!`.
- @details Evaluates provider/window scope and displayed usage rounding.
- @param result {ProviderResult} Provider result candidate.
- @return {bool} True when reset label must include limit-reached hint.

### fn `def _format_reset_value(self, reset_str: str, result: ProviderResult) -> str` `priv` (L326-336)
- @brief Compose reset label value with optional limit-reached suffix.
- @param reset_str {str} Countdown text from `_format_duration`.
- @param result {ProviderResult} Provider result candidate.
- @return {str} Reset value with optional `⚠️ Limit reached!` suffix.

### fn `def _format_age(self, seconds: float) -> str` `priv` (L337-350)
- @brief Execute format age.
- @details Applies format age logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param seconds {float} Input parameter `seconds`.
- @return {str} Function return value.

### fn `def _format_duration(self, seconds: float) -> str` `priv` (L351-370)
- @brief Execute format duration.
- @details Applies format duration logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param seconds {float} Input parameter `seconds`.
- @return {str} Function return value.

### class `class RawJsonView(Static)` : Static (L371-418)
- @brief Define raw json view component.
- @details Encapsulates raw json view state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `def compose(self) -> ComposeResult` (L393-403)
  - @brief Define raw json view component.
  - @brief Execute compose.
  - @details Encapsulates raw json view state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
  - @details Applies compose logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {ComposeResult} Function return value.
- fn `def watch_data(self, data: dict | None) -> None` (L404-418)
  - @brief Execute watch data.
  - @details Applies watch data logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param data {dict | None} Input parameter `data`.
  - @return {None} Function return value.

### class `class AIBarUI(App)` : App (L419-618)
- @brief Define a i bar u i component.
- @details Encapsulates a i bar u i state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `BINDINGS = [` (L479)
- var `TITLE = "Usage Metrics UI"` (L487)
- fn `def __init__(self) -> None` `priv` (L492-508)
  - @brief Execute init.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {None} Function return value.
- fn `def compose(self) -> ComposeResult` (L509-537)
  - @brief Execute compose.
  - @details Applies compose logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {ComposeResult} Function return value.
- fn `async def on_mount(self) -> None` (L538-546)
  - @brief Execute on mount.
  - @details Applies on mount logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {None} Function return value.
- fn `async def on_refresh_pressed(self) -> None` (L548-555)
  - @brief Execute on refresh pressed.
  - @details Applies on refresh pressed logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {None} Function return value.
- fn `async def on_5h_pressed(self) -> None` (L557-564)
  - @brief Execute on 5h pressed.
  - @details Applies on 5h pressed logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {None} Function return value.
- fn `async def on_7d_pressed(self) -> None` (L566-573)
  - @brief Execute on 7d pressed.
  - @details Applies on 7d pressed logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {None} Function return value.

### fn `async def action_refresh(self) -> None` (L574-630)
- @brief Execute action refresh.
- @details Executes shared cache-based retrieval pipeline reused by CLI `show`: force-flag evaluation, idle-time gate check, conditional cache refresh, and readback from `cache.json` before card projection.
- @return {None} Function return value.
- @satisfies REQ-009
- @satisfies REQ-043

### fn `async def action_window_5h(self) -> None` (L631-640)
- @brief Execute action window 5h.
- @details Applies action window 5h logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `async def action_window_7d(self) -> None` (L641-650)
- @brief Execute action window 7d.
- @details Applies action window 7d logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `async def action_toggle_json(self) -> None` (L651-663)
- @brief Execute action toggle json.
- @details Applies action toggle json logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def _get_card(self, provider: ProviderName) -> ProviderCard | None` `priv` (L664-676)
- @brief Execute get card.
- @details Applies get card logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param provider {ProviderName} Input parameter `provider`.
- @return {ProviderCard | None} Function return value.

### fn `def _update_window_buttons(self) -> None` `priv` (L677-696)
- @brief Execute update window buttons.
- @details Applies update window buttons logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def _update_json_view(self) -> None` `priv` (L697-710)
- @brief Execute update json view.
- @details Applies update json view logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def run_ui() -> None` (L711-720)
- @brief Execute run ui.
- @details Applies run ui logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`ProviderCard`|class|pub|47-246|class ProviderCard(Static)|
|`ProviderCard.__init__`|fn|priv|124-127|def __init__(|
|`ProviderCard.compose`|fn|pub|140-163|def compose(self) -> ComposeResult|
|`watch_result`|fn|pub|164-260|def watch_result(self, result: ProviderResult | None) -> ...|
|`watch_is_loading`|fn|pub|261-273|def watch_is_loading(self, loading: bool) -> None|
|`_is_rate_limit_quota_error`|fn|priv|274-288|def _is_rate_limit_quota_error(self, result: ProviderResu...|
|`_is_displayed_full_percent`|fn|priv|289-300|def _is_displayed_full_percent(self, percent: float | Non...|
|`_supports_limit_reached_hint`|fn|priv|301-314|def _supports_limit_reached_hint(self, result: ProviderRe...|
|`_should_show_limit_reached_hint`|fn|priv|315-325|def _should_show_limit_reached_hint(self, result: Provide...|
|`_format_reset_value`|fn|priv|326-336|def _format_reset_value(self, reset_str: str, result: Pro...|
|`_format_age`|fn|priv|337-350|def _format_age(self, seconds: float) -> str|
|`_format_duration`|fn|priv|351-370|def _format_duration(self, seconds: float) -> str|
|`RawJsonView`|class|pub|371-418|class RawJsonView(Static)|
|`RawJsonView.compose`|fn|pub|393-403|def compose(self) -> ComposeResult|
|`RawJsonView.watch_data`|fn|pub|404-418|def watch_data(self, data: dict | None) -> None|
|`AIBarUI`|class|pub|419-618|class AIBarUI(App)|
|`AIBarUI.BINDINGS`|var|pub|479||
|`AIBarUI.TITLE`|var|pub|487||
|`AIBarUI.__init__`|fn|priv|492-508|def __init__(self) -> None|
|`AIBarUI.compose`|fn|pub|509-537|def compose(self) -> ComposeResult|
|`AIBarUI.on_mount`|fn|pub|538-546|async def on_mount(self) -> None|
|`AIBarUI.on_refresh_pressed`|fn|pub|548-555|async def on_refresh_pressed(self) -> None|
|`AIBarUI.on_5h_pressed`|fn|pub|557-564|async def on_5h_pressed(self) -> None|
|`AIBarUI.on_7d_pressed`|fn|pub|566-573|async def on_7d_pressed(self) -> None|
|`action_refresh`|fn|pub|574-630|async def action_refresh(self) -> None|
|`action_window_5h`|fn|pub|631-640|async def action_window_5h(self) -> None|
|`action_window_7d`|fn|pub|641-650|async def action_window_7d(self) -> None|
|`action_toggle_json`|fn|pub|651-663|async def action_toggle_json(self) -> None|
|`_get_card`|fn|priv|664-676|def _get_card(self, provider: ProviderName) -> ProviderCa...|
|`_update_window_buttons`|fn|priv|677-696|def _update_window_buttons(self) -> None|
|`_update_json_view`|fn|priv|697-710|def _update_json_view(self) -> None|
|`run_ui`|fn|pub|711-720|def run_ui() -> None|


---

# extension.js | JavaScript | 1253L | 19 symbols | 9 imports | 27 comments
> Path: `src/aibar/gnome-extension/aibar@aibar.panel/extension.js`
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
- const `const ENV_FILE_PATH = GLib.get_home_dir() + '/.config/aibar/env';` (L19)
- const `const RESET_PENDING_MESSAGE = 'Starts when the first message is sent';` (L20)
- const `const RATE_LIMIT_ERROR_MESSAGE = 'Rate limited. Try again later.';` (L21)
- const `const PROVIDER_DISPLAY_NAMES = {` (L22)
### fn `function _getProviderDisplayName(providerName)` (L31-35)
- @brief Resolve provider label text for GNOME tab/card rendering.
- @param {string} providerName Provider key from JSON payload.
- @return s {string} Display label for provider tab and card.

### fn `function _getAiBarPath()` (L42-52)
- @brief Resolve aibar executable path.
- @details Prefers PATH discovery and falls back to AIBAR_PATH from the env file.
- @return s {string} Resolved executable path or fallback command name.

### fn `function _loadEnvFromFile()` (L59-111)
- @brief Load key-value environment variables from aibar env file.
- @details Parses export syntax, quoted values, and inline comments.
- @return s {Object<string,string>} Parsed environment map.

### fn `function _getProgressClass(pct)` (L118-124)
- @brief Map percentage usage to CSS progress severity class.
- @param {number} pct Usage percentage.
- @return s {string} CSS class suffix for progress state.

### fn `function _isDisplayedZeroPercent(pct)` (L133-140)
- @brief Check whether a percentage renders as `0.0%` in one-decimal UI output.
- @details Mirrors display rounding semantics so fallback reset text is shown when
usage is effectively zero from the user's perspective (e.g. internal 0.04 -> 0.0%).
- @param {number} pct Usage percentage candidate.
- @return s {boolean} True when value is finite, non-negative, and rounds to 0.0.

### fn `function _isDisplayedFullPercent(pct)` (L149-154)
- @brief Check whether a percentage renders as `100.0%` in one-decimal UI output.
- @details Mirrors display rounding semantics so near-full values are treated as
full usage for limit-reached warning rendering.
- @param {number} pct Usage percentage candidate.
- @return s {boolean} True when value is finite and rounds to `100.0`.

### class `class AIBarIndicator extends PanelMenu.Button` : PanelMenu.Button (L158-457)
- @brief Panel indicator widget that manages popup rendering and refresh lifecycle. */
- @brief Execute init.
- @details Applies init logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
- @return s {any} Function return value.

### fn `const createWindowBar = (labelText) =>` (L494-540)

### fn `const updateWindowBar = (bar, pct, resetTime, useDays) =>` (L666-724)
- @brief Execute populate provider card.
- @details Applies populate provider card logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
- @param {any} card Input parameter `card`.
- @param {any} providerName Input parameter `providerName`.
- @param {any} data Input parameter `data`.
- @return s {any} Function return value.

### fn `const setResetLabel = (baseText) =>` (L672-678)

### fn `const showResetPendingHint = () =>` (L689-691)

### fn `const toPercent = (value) =>` (L1028-1033)
- @brief Execute update u i.
- @details Applies update u i logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
Uses `metrics.currency_symbol` from the first cost-bearing provider for the panel summary label.
- @return s {any} Function return value.
- @satisfies REQ-053

### fn `const getPanelUsageValues = (providerName, data) =>` (L1035-1092)

### class `export default class AIBarExtension extends Extension` : Extension (L1227-1253)
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
|`ENV_FILE_PATH`|const||19||
|`RESET_PENDING_MESSAGE`|const||20||
|`RATE_LIMIT_ERROR_MESSAGE`|const||21||
|`PROVIDER_DISPLAY_NAMES`|const||22||
|`_getProviderDisplayName`|fn||31-35|function _getProviderDisplayName(providerName)|
|`_getAiBarPath`|fn||42-52|function _getAiBarPath()|
|`_loadEnvFromFile`|fn||59-111|function _loadEnvFromFile()|
|`_getProgressClass`|fn||118-124|function _getProgressClass(pct)|
|`_isDisplayedZeroPercent`|fn||133-140|function _isDisplayedZeroPercent(pct)|
|`_isDisplayedFullPercent`|fn||149-154|function _isDisplayedFullPercent(pct)|
|`AIBarIndicator`|class||158-457|class AIBarIndicator extends PanelMenu.Button|
|`createWindowBar`|fn||494-540|const createWindowBar = (labelText) =>|
|`updateWindowBar`|fn||666-724|const updateWindowBar = (bar, pct, resetTime, useDays) =>|
|`setResetLabel`|fn||672-678|const setResetLabel = (baseText) =>|
|`showResetPendingHint`|fn||689-691|const showResetPendingHint = () =>|
|`toPercent`|fn||1028-1033|const toPercent = (value) =>|
|`getPanelUsageValues`|fn||1035-1092|const getPanelUsageValues = (providerName, data) =>|
|`AIBarExtension`|class||1227-1253|export default class AIBarExtension extends Extension|

