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
        ├── chrome-extension
        │   ├── background.js
        │   ├── debug.js
        │   ├── parsers.js
        │   └── popup.js
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

# cli.py | Python | 1029L | 31 symbols | 18 imports | 50 comments
> Path: `src/aibar/aibar/cli.py`
- @brief Command-line interface for aibar.
- @details Defines command parsing, provider dispatch, formatted output, setup helpers, login flows, and UI launch hooks.

## Imports
```
import asyncio
import json
import math
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import click
from click.core import ParameterSource
from aibar.cache import ResultCache
from aibar.config import config
from aibar.providers import (
from aibar.providers.base import (
from datetime import datetime, timezone
from aibar.ui import run_ui
from aibar.config import ENV_FILE_PATH, write_env_file
from aibar.claude_cli_auth import ClaudeCLIAuth
from aibar.providers.copilot import CopilotProvider
```

## Definitions

### fn `def _claude_snapshot_path() -> Path` `priv` (L46-59)
- @brief Resolve file path for persisted Claude dual-window success payload.
- @details Uses `XDG_CACHE_HOME` when defined; otherwise falls back to `~/.cache/aibar`. Returned path is used only for Claude HTTP 429 fallback rendering and does not participate in generic ResultCache TTL reads.
- @return {Path} Absolute snapshot path for Claude dual-window payload.
- @satisfies CTN-004

### fn `def _project_next_reset(resets_at_str: str, window: WindowPeriod) -> datetime | None` `priv` (L60-91)
- @brief Compute the next reset boundary after a stale resets_at timestamp.
- @details Advances `resets_at_str` by multiples of the window period until the result is strictly greater than current UTC time. Returns None if `resets_at_str` is unparseable or the window period is not in `_WINDOW_PERIOD_TIMEDELTA`.
- @param resets_at_str {str} ISO 8601 timestamp string of the last known reset boundary. May have a Z suffix (converted to +00:00) or an explicit timezone offset.
- @param window {WindowPeriod} Window period whose duration drives the projection step.
- @return {datetime | None} Projected future reset datetime in UTC, or None on parse error.
- @note Uses `math.ceil` to determine the minimum number of full cycles to advance.
- @satisfies REQ-002

### fn `def _apply_reset_projection(result: ProviderResult) -> ProviderResult` `priv` (L92-126)
- @brief Return a copy of `result` with `metrics.reset_at` set to the projected next reset boundary when it is currently None but the raw payload contains a parseable past `resets_at` string for the result's window.
- @details When a ProviderResult is obtained from stale disk cache (last-good path) or from a cross-window raw re-parse, `_parse_response` correctly sets `reset_at=None` for past timestamps. This function recovers the display information by projecting the next future reset boundary from the raw payload's `resets_at` field, ensuring the 'Resets in:' countdown is shown even when the cached timestamp has already elapsed. If `reset_at` is already non-None, or the raw payload has no parseable `resets_at` for the window, or projection fails, the original result is returned unchanged.
- @param result {ProviderResult} Candidate result whose reset_at may require projection.
- @return {ProviderResult} Original result unchanged if no projection is needed; otherwise a new ProviderResult with metrics.reset_at set to the projected datetime.
- @see _project_next_reset
- @satisfies REQ-002

### fn `def get_providers() -> dict[ProviderName, BaseProvider]` (L127-141)
- @brief Execute get providers.
- @details Applies get providers logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {dict[ProviderName, BaseProvider]} Function return value.

### fn `def parse_window(window: str) -> WindowPeriod` (L142-161)
- @brief Execute parse window.
- @details Applies parse window logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {str} Input parameter `window`.
- @return {WindowPeriod} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def parse_provider(provider: str) -> ProviderName | None` (L162-178)
- @brief Execute parse provider.
- @details Applies parse provider logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param provider {str} Input parameter `provider`.
- @return {ProviderName | None} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _fetch_result(` `priv` (L179-182)

### fn `def _fetch_claude_dual(` `priv` (L224-226)
- @brief Execute provider fetch with cache lookup, store, and last-good fallback.
- @details Applies cache lookup/store/fallback only for non-Claude providers.
Claude provider requests always execute a fresh API fetch and skip cache state.
- @param provider {BaseProvider} Provider instance to fetch from.
- @param window {WindowPeriod} Time window for the fetch.
- @param cache {ResultCache | None} Optional cache instance for TTL-based result reuse.
- @return {ProviderResult} Cached, fresh, or last-good fallback result.
- @satisfies CTN-004

### fn `def _persist_claude_dual_snapshot(` `priv` (L285-287)
- @brief Fetch Claude 5h and 7d results via a single API call.
- @details Executes ClaudeOAuthProvider.fetch_all_windows for 5h and 7d on each invocation.
Cache parameter is accepted for call-site compatibility but intentionally unused
because Claude requests MUST bypass cache reuse.
If Claude returns HTTP 429 for both windows, normalize to a partial-window state:
keep the user-facing error only on 5h, force 5h usage to 100%, and restore 7d
usage/reset plus 5h reset from persisted Claude success payload when available.
- @param provider {ClaudeOAuthProvider} Claude provider instance.
- @param cache {ResultCache} Compatibility parameter; ignored for Claude fetch path.
- @return {tuple[ProviderResult, ProviderResult]} (5h_result, 7d_result).
- @satisfies REQ-002, REQ-036, REQ-037, CTN-004

### fn `def _extract_claude_dual_payload(` `priv` (L312-314)
- @brief Persist latest successful Claude dual-window payload for 429 restoration.
- @details Extracts a valid dual-window raw payload (`five_hour` and `seven_day`)
from successful Claude results and writes it to disk under cache home. Errors
during serialization or I/O are ignored to keep fetch path non-fatal.
- @param result_5h {ProviderResult} Claude five-hour successful result.
- @param result_7d {ProviderResult} Claude seven-day successful result.
- @return {None} Function return value.
- @satisfies CTN-004
- @satisfies REQ-036

### fn `def _load_claude_dual_snapshot() -> dict[str, object] | None` `priv` (L335-364)
- @brief Extract dual-window Claude payload dictionary from successful results.
- @brief Load persisted Claude dual-window payload for HTTP 429 fallback.
- @details Returns first raw payload containing both `five_hour` and `seven_day`
mapping objects. Returns None when payload shape is invalid.
- @details Reads prioritized snapshot candidates from cache home, validates required keys, and returns parsed payload when both `five_hour` and `seven_day` objects exist. Supports direct raw payload files and serialized ProviderResult files (`raw` field). Invalid/missing files return None.
- @param result_5h {ProviderResult} Claude five-hour result.
- @param result_7d {ProviderResult} Claude seven-day result.
- @return {dict[str, object] | None} Serializable payload or None.
- @return {dict[str, object] | None} Parsed payload or None.
- @satisfies CTN-004
- @satisfies REQ-036
- @satisfies REQ-037

### fn `def _normalize_claude_dual_payload(payload: object) -> dict[str, object] | None` `priv` (L365-387)
- @brief Normalize persisted Claude payload shape into dual-window raw dictionary.
- @details Accepts either direct dual-window payload (`five_hour`/`seven_day`) or serialized ProviderResult dictionaries containing a `raw` field with that shape.
- @param payload {object} Decoded JSON object from snapshot candidate file.
- @return {dict[str, object] | None} Normalized dual-window payload or None.
- @satisfies REQ-036

### fn `def _extract_snapshot_reset_at(` `priv` (L388-390)

### fn `def _extract_snapshot_utilization(` `priv` (L413-415)
- @brief Resolve projected reset timestamp from persisted Claude snapshot payload.
- @details Uses window-specific `resets_at` string from persisted payload and
projects next reset boundary through `_project_next_reset`.
- @param snapshot_payload {dict[str, object] | None} Persisted dual-window payload.
- @param window {WindowPeriod} Target window period.
- @return {datetime | None} Projected reset timestamp or None.
- @satisfies REQ-036

### fn `def _is_claude_rate_limited_result(result: ProviderResult) -> bool` `priv` (L444-459)
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

### fn `def _build_claude_rate_limited_partial_result(` `priv` (L460-463)

### fn `def main() -> None` `@click.version_option()` (L509-517)
- @brief Execute main.
- @details Applies main logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def show(provider: str, window: str, output_json: bool) -> None` (L537-600)
- @brief Execute show with per-provider TTL cache and single-call dual-window optimization.
- @details Instantiates a ResultCache for non-Claude providers (CTN-004). Claude dual-window mode uses fetch_all_windows to make one API call instead of two and bypasses cache reuse.
- @param provider {str} CLI provider selector string.
- @param window {str} CLI window period string.
- @param output_json {bool} When True, emit JSON output instead of formatted text.
- @return {None} Function return value.

### fn `def _print_result(name: ProviderName, result, label: str | None = None) -> None` `priv` (L601-662)
- @brief Execute print result.
- @details Applies print result logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param name {ProviderName} Input parameter `name`.
- @param result {None} Input parameter `result`.
- @param label {str | None} Input parameter `label`.
- @return {None} Function return value.

### fn `def _format_reset_duration(seconds: float) -> str` `priv` (L663-678)
- @brief Execute format reset duration.
- @details Applies format reset duration logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param seconds {float} Input parameter `seconds`.
- @return {str} Function return value.

### fn `def _should_render_metrics_after_error(` `priv` (L679-681)

### fn `def _should_print_claude_reset_pending_hint(` `priv` (L699-701)
- @brief Check whether CLI output must render metrics after printing an error line.
- @details Allows continuation only for Claude HTTP 429 partial-window state so the
5h section can include `Error:` and still display usage/reset lines.
- @param provider_name {ProviderName} Provider associated with rendered section.
- @param result {ProviderResult} Result being rendered.
- @return {bool} True when metrics should still be rendered after error line.
- @satisfies REQ-036

### fn `def _is_displayed_zero_percent(percent: float | None) -> bool` `priv` (L721-737)
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

### fn `def _progress_bar(percent: float, width: int = 20) -> str` `priv` (L738-750)
- @brief Execute progress bar.
- @details Applies progress bar logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param percent {float} Input parameter `percent`.
- @param width {int} Input parameter `width`.
- @return {str} Function return value.

### fn `def doctor() -> None` `@main.command()` (L752-804)
- @brief Execute doctor.
- @details Applies doctor logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def ui() -> None` `@main.command()` (L806-816)
- @brief Execute ui.
- @details Applies ui logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def env() -> None` `@main.command()` (L818-826)
- @brief Execute env.
- @details Applies env logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def setup() -> None` `@main.command()` (L828-926)
- @brief Execute setup.
- @details Applies setup logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def login(provider: str) -> None` (L934-950)
- @brief Execute login.
- @details Applies login logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param provider {str} Input parameter `provider`.
- @return {None} Function return value.

### fn `def _login_claude() -> None` `priv` (L951-999)
- @brief Execute login claude.
- @details Applies login claude logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def _login_copilot() -> None` `priv` (L1000-1027)
- @brief Execute login copilot.
- @details Applies login copilot logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`_claude_snapshot_path`|fn|priv|46-59|def _claude_snapshot_path() -> Path|
|`_project_next_reset`|fn|priv|60-91|def _project_next_reset(resets_at_str: str, window: Windo...|
|`_apply_reset_projection`|fn|priv|92-126|def _apply_reset_projection(result: ProviderResult) -> Pr...|
|`get_providers`|fn|pub|127-141|def get_providers() -> dict[ProviderName, BaseProvider]|
|`parse_window`|fn|pub|142-161|def parse_window(window: str) -> WindowPeriod|
|`parse_provider`|fn|pub|162-178|def parse_provider(provider: str) -> ProviderName | None|
|`_fetch_result`|fn|priv|179-182|def _fetch_result(|
|`_fetch_claude_dual`|fn|priv|224-226|def _fetch_claude_dual(|
|`_persist_claude_dual_snapshot`|fn|priv|285-287|def _persist_claude_dual_snapshot(|
|`_extract_claude_dual_payload`|fn|priv|312-314|def _extract_claude_dual_payload(|
|`_load_claude_dual_snapshot`|fn|priv|335-364|def _load_claude_dual_snapshot() -> dict[str, object] | None|
|`_normalize_claude_dual_payload`|fn|priv|365-387|def _normalize_claude_dual_payload(payload: object) -> di...|
|`_extract_snapshot_reset_at`|fn|priv|388-390|def _extract_snapshot_reset_at(|
|`_extract_snapshot_utilization`|fn|priv|413-415|def _extract_snapshot_utilization(|
|`_is_claude_rate_limited_result`|fn|priv|444-459|def _is_claude_rate_limited_result(result: ProviderResult...|
|`_build_claude_rate_limited_partial_result`|fn|priv|460-463|def _build_claude_rate_limited_partial_result(|
|`main`|fn|pub|509-517|def main() -> None|
|`show`|fn|pub|537-600|def show(provider: str, window: str, output_json: bool) -...|
|`_print_result`|fn|priv|601-662|def _print_result(name: ProviderName, result, label: str ...|
|`_format_reset_duration`|fn|priv|663-678|def _format_reset_duration(seconds: float) -> str|
|`_should_render_metrics_after_error`|fn|priv|679-681|def _should_render_metrics_after_error(|
|`_should_print_claude_reset_pending_hint`|fn|priv|699-701|def _should_print_claude_reset_pending_hint(|
|`_is_displayed_zero_percent`|fn|priv|721-737|def _is_displayed_zero_percent(percent: float | None) -> ...|
|`_progress_bar`|fn|priv|738-750|def _progress_bar(percent: float, width: int = 20) -> str|
|`doctor`|fn|pub|752-804|def doctor() -> None|
|`ui`|fn|pub|806-816|def ui() -> None|
|`env`|fn|pub|818-826|def env() -> None|
|`setup`|fn|pub|828-926|def setup() -> None|
|`login`|fn|pub|934-950|def login(provider: str) -> None|
|`_login_claude`|fn|priv|951-999|def _login_claude() -> None|
|`_login_copilot`|fn|priv|1000-1027|def _login_copilot() -> None|


---

# config.py | Python | 260L | 12 symbols | 8 imports | 19 comments
> Path: `src/aibar/aibar/config.py`
- @brief Configuration and credential resolution for aibar.
- @details Provides environment-file parsing, token precedence resolution, and provider configuration status reporting.

## Imports
```
import os
from pathlib import Path
from typing import Any
from aibar.claude_cli_auth import extract_claude_cli_token
from aibar.providers.base import ProviderName
from aibar.providers.codex import CodexCredentialStore
from aibar.providers.copilot import CopilotCredentialStore
from aibar.providers import (
```

## Definitions

- var `ENV_FILE_PATH = Path.home() / ".config" / "aibar" / "env"` (L15)
### fn `def load_env_file() -> dict[str, str]` (L18-36)
- @brief Execute load env file.
- @details Applies load env file logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {dict[str, str]} Function return value.

### fn `def write_env_file(updates: dict[str, str]) -> None` (L37-76)
- @brief Execute write env file.
- @details Applies write env file logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param updates {dict[str, str]} Input parameter `updates`.
- @return {None} Function return value.

### class `class Config` (L77-258)
- @brief Define config component.
- @details Encapsulates config state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `ENV_VARS =` (L84)
- var `PROVIDER_INFO =` (L93)
- fn `def get_token(self, provider: ProviderName) -> str | None` (L126-163)
  - @brief Execute get token.
  - @details Applies get token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @return {str | None} Function return value.
- fn `def is_provider_configured(self, provider: ProviderName) -> bool` (L164-193)
  - @brief Execute is provider configured.
  - @details Applies is provider configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @return {bool} Function return value.
- fn `def get_provider_status(self, provider: ProviderName) -> dict[str, Any]` (L194-215)
  - @brief Execute get provider status.
  - @details Applies get provider status logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @return {dict[str, Any]} Function return value.
- fn `def get_all_provider_status(self) -> list[dict[str, Any]]` (L216-223)
  - @brief Execute get all provider status.
  - @details Applies get all provider status logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {list[dict[str, Any]]} Function return value.
- fn `def _get_token_preview(self, provider: ProviderName) -> str | None` `priv` (L224-235)
  - @brief Execute get token preview.
  - @details Applies get token preview logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @return {str | None} Function return value.
- fn `def get_env_var_help(self) -> str` (L236-258)
  - @brief Execute get env var help.
  - @details Applies get env var help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`ENV_FILE_PATH`|var|pub|15||
|`load_env_file`|fn|pub|18-36|def load_env_file() -> dict[str, str]|
|`write_env_file`|fn|pub|37-76|def write_env_file(updates: dict[str, str]) -> None|
|`Config`|class|pub|77-258|class Config|
|`Config.ENV_VARS`|var|pub|84||
|`Config.PROVIDER_INFO`|var|pub|93||
|`Config.get_token`|fn|pub|126-163|def get_token(self, provider: ProviderName) -> str | None|
|`Config.is_provider_configured`|fn|pub|164-193|def is_provider_configured(self, provider: ProviderName) ...|
|`Config.get_provider_status`|fn|pub|194-215|def get_provider_status(self, provider: ProviderName) -> ...|
|`Config.get_all_provider_status`|fn|pub|216-223|def get_all_provider_status(self) -> list[dict[str, Any]]|
|`Config._get_token_preview`|fn|priv|224-235|def _get_token_preview(self, provider: ProviderName) -> s...|
|`Config.get_env_var_help`|fn|pub|236-258|def get_env_var_help(self) -> str|


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

# claude_oauth.py | Python | 304L | 14 symbols | 8 imports | 17 comments
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
### fn `async def _request_usage(self, client: httpx.AsyncClient) -> httpx.Response` `priv` (L73-99)
- @brief Execute HTTP GET to usage endpoint with retry on HTTP 429.
- @details Retries up to MAX_RETRIES times on 429 responses, respecting the retry-after header with exponential backoff fallback and random jitter to prevent thundering-herd synchronization. Backoff sequence with RETRY_BACKOFF_BASE=2.0: ~2-3s, ~4-5s, ~8-9s (total ~14-17s).
- @param client {httpx.AsyncClient} Reusable HTTP client session.
- @return {httpx.Response} Final HTTP response after retries exhausted or success.

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L100-139)
- @brief Execute fetch for a single window period.
- @details Makes one HTTP request to the usage endpoint (with retry on 429) and parses the response for the requested window.
- @param window {WindowPeriod} Window period to parse from the API response.
- @return {ProviderResult} Parsed result for the requested window.
- @throws {AuthenticationError} When the OAuth token is invalid or expired.
- @throws {ProviderError} On unexpected non-HTTP errors.

### fn `async def fetch_all_windows(` (L140-141)

### fn `def _handle_response(` `priv` (L194-195)
- @brief Execute a single API call and parse results for multiple windows.
- @details The usage endpoint returns data for all windows in one response.
This method avoids redundant HTTP requests when multiple windows are needed.
- @param windows {list[WindowPeriod]} Window periods to parse from one API response.
- @return {dict[WindowPeriod, ProviderResult]} Map of window to parsed result.
- @throws {AuthenticationError} When the OAuth token is invalid or expired.
- @throws {ProviderError} On unexpected non-HTTP errors.

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L239-304)
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
|`_request_usage`|fn|priv|73-99|async def _request_usage(self, client: httpx.AsyncClient)...|
|`fetch`|fn|pub|100-139|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`fetch_all_windows`|fn|pub|140-141|async def fetch_all_windows(|
|`_handle_response`|fn|priv|194-195|def _handle_response(|
|`_parse_response`|fn|priv|239-304|def _parse_response(self, data: dict, window: WindowPerio...|


---

# codex.py | Python | 417L | 21 symbols | 6 imports | 32 comments
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

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L297-364)
- @brief Execute fetch.
- @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L365-417)
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
|`fetch`|fn|pub|297-364|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|365-417|def _parse_response(self, data: dict, window: WindowPerio...|


---

# copilot.py | Python | 408L | 27 symbols | 8 imports | 31 comments
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

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L222-281)
- @brief Execute fetch.
- @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L282-377)
- @brief Execute parse response.
- @details Applies parse response logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param data {dict} Input parameter `data`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.

### fn `def _get_snapshot(key_camel: str, key_snake: str) -> dict` `priv` (L292-301)
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

### fn `def _extract_quota_data(snapshot: dict) -> tuple[float | None, float | None]` `priv` (L302-328)
- @brief Execute extract quota data.
- @details Applies extract quota data logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param snapshot {dict} Input parameter `snapshot`.
- @return {tuple[float | None, float | None]} Function return value.

### fn `async def login(self) -> str` (L378-408)
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
|`fetch`|fn|pub|222-281|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|282-377|def _parse_response(self, data: dict, window: WindowPerio...|
|`_get_snapshot`|fn|priv|292-301|def _get_snapshot(key_camel: str, key_snake: str) -> dict|
|`_extract_quota_data`|fn|priv|302-328|def _extract_quota_data(snapshot: dict) -> tuple[float | ...|
|`login`|fn|pub|378-408|async def login(self) -> str|


---

# openai_usage.py | Python | 234L | 12 symbols | 4 imports | 17 comments
> Path: `src/aibar/aibar/providers/openai_usage.py`
- @brief OpenAI organization usage provider.
- @details Retrieves organization completion usage and cost buckets, aggregates counters, and maps response data to normalized provider metrics.

## Imports
```
from datetime import datetime, timedelta, timezone
import httpx
from aibar.providers.base import (
from aibar.config import config
```

## Definitions

### class `class OpenAIUsageProvider(BaseProvider)` : BaseProvider (L22-60)
- @brief Define open a i usage provider component.
- @details Encapsulates open a i usage provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `BASE_URL = "https://api.openai.com/v1/organization"` (L29)
  - @brief Define open a i usage provider component.
  - @details Encapsulates open a i usage provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `TOKEN_ENV_VAR = "OPENAI_ADMIN_KEY"` (L30)
- fn `def __init__(self, api_key: str | None = None) -> None` `priv` (L32-44)
  - @brief Execute init.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param api_key {str | None} Input parameter `api_key`.
  - @return {None} Function return value.
- fn `def is_configured(self) -> bool` (L45-52)
  - @brief Execute is configured.
  - @details Applies is configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {bool} Function return value.
- fn `def get_config_help(self) -> str` (L53-60)
  - @brief Execute get config help.
  - @details Applies get config help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str} Function return value.

### fn `def _get_time_range(self, window: WindowPeriod) -> tuple[int, int]` `priv` (L67-78)
- @brief Execute get time range.
- @details Applies get time range logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {WindowPeriod} Input parameter `window`.
- @return {tuple[int, int]} Function return value.

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L79-114)
- @brief Execute fetch.
- @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `async def _fetch_usage(` `priv` (L115-120)

### fn `async def _fetch_costs(` `priv` (L143-148)
- @brief Execute fetch usage.
- @details Applies fetch usage logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param client {httpx.AsyncClient} Input parameter `client`.
- @param headers {dict} Input parameter `headers`.
- @param start_time {int} Input parameter `start_time`.
- @param end_time {int} Input parameter `end_time`.
- @return {dict} Function return value.

### fn `def _check_response(self, response: httpx.Response) -> None` `priv` (L171-187)
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

### fn `def _build_result(` `priv` (L188-189)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`OpenAIUsageProvider`|class|pub|22-60|class OpenAIUsageProvider(BaseProvider)|
|`OpenAIUsageProvider.BASE_URL`|var|pub|29||
|`OpenAIUsageProvider.TOKEN_ENV_VAR`|var|pub|30||
|`OpenAIUsageProvider.__init__`|fn|priv|32-44|def __init__(self, api_key: str | None = None) -> None|
|`OpenAIUsageProvider.is_configured`|fn|pub|45-52|def is_configured(self) -> bool|
|`OpenAIUsageProvider.get_config_help`|fn|pub|53-60|def get_config_help(self) -> str|
|`_get_time_range`|fn|priv|67-78|def _get_time_range(self, window: WindowPeriod) -> tuple[...|
|`fetch`|fn|pub|79-114|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_fetch_usage`|fn|priv|115-120|async def _fetch_usage(|
|`_fetch_costs`|fn|priv|143-148|async def _fetch_costs(|
|`_check_response`|fn|priv|171-187|def _check_response(self, response: httpx.Response) -> None|
|`_build_result`|fn|priv|188-189|def _build_result(|


---

# openrouter.py | Python | 195L | 11 symbols | 3 imports | 11 comments
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

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L64-124)
- @brief Execute fetch.
- @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L125-154)
- @brief Execute parse response.
- @details Applies parse response logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param data {dict} Input parameter `data`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.

### fn `def _get_usage(self, payload: dict, window: WindowPeriod) -> float` `priv` (L155-168)
- @brief Execute get usage.
- @details Applies get usage logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param payload {dict} Input parameter `payload`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {float} Function return value.

### fn `def _get_byok_usage(self, payload: dict, window: WindowPeriod) -> float` `priv` (L169-182)
- @brief Execute get byok usage.
- @details Applies get byok usage logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param payload {dict} Input parameter `payload`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {float} Function return value.

### fn `def _to_float(self, value: float | int | None) -> float` `priv` (L183-195)
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
|`fetch`|fn|pub|64-124|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|125-154|def _parse_response(self, data: dict, window: WindowPerio...|
|`_get_usage`|fn|priv|155-168|def _get_usage(self, payload: dict, window: WindowPeriod)...|
|`_get_byok_usage`|fn|priv|169-182|def _get_byok_usage(self, payload: dict, window: WindowPe...|
|`_to_float`|fn|priv|183-195|def _to_float(self, value: float | int | None) -> float|


---

# ui.py | Python | 703L | 32 symbols | 12 imports | 45 comments
> Path: `src/aibar/aibar/ui.py`
- @brief Textual terminal UI for usage metrics.
- @details Implements provider cards, refresh controls, window switching, and raw JSON visualization over normalized provider results.

## Imports
```
import json
from datetime import datetime, timezone
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalGroup, VerticalScroll
from textual.reactive import reactive
from textual.widgets import (
from aibar.cache import ResultCache
from aibar.config import config
from aibar.providers import (
from aibar.providers.base import (
```

## Definitions

### class `class ProviderCard(Static)` : Static (L45-244)
- @brief Define provider card component.
- @details Encapsulates provider card state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `def __init__(` `priv` (L122-125)
  - @brief Define provider card component.
  - @details Encapsulates provider card state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `def compose(self) -> ComposeResult` (L138-161)
  - @brief Execute init.
  - @brief Execute compose.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @details Applies compose logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider_name {ProviderName} Input parameter `provider_name`.
  - @param kwargs {None} Input parameter `kwargs`.
  - @return {None} Function return value.
  - @return {ComposeResult} Function return value.

### fn `def watch_result(self, result: ProviderResult | None) -> None` (L162-254)
- @brief Execute watch result.
- @details Applies watch result logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param result {ProviderResult | None} Input parameter `result`.
- @return {None} Function return value.

### fn `def watch_is_loading(self, loading: bool) -> None` (L255-267)
- @brief Execute watch is loading.
- @details Applies watch is loading logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param loading {bool} Input parameter `loading`.
- @return {None} Function return value.

### fn `def _is_rate_limit_quota_error(self, result: ProviderResult) -> bool` `priv` (L268-282)
- @brief Check whether result is a rate-limit payload that still carries quota metrics.
- @details Detects the normalized Claude/Codex/Copilot rate-limit message with available `limit` and `remaining` values so card rendering can continue without showing the textual error banner.
- @param result {ProviderResult} Provider result candidate.
- @return {bool} True when result error is rate-limit with quota metrics.

### fn `def _is_displayed_full_percent(self, percent: float | None) -> bool` `priv` (L283-294)
- @brief Check whether usage renders as `100.0%` in one-decimal output.
- @details Applies display-rounding semantics used by Textual labels so near-full values (for example `99.96`) are treated as full usage.
- @param percent {float | None} Candidate usage percentage.
- @return {bool} True when rendered one-decimal value is `100.0%`.

### fn `def _supports_limit_reached_hint(self, result: ProviderResult) -> bool` `priv` (L295-308)
- @brief Validate whether provider/window pair supports `Limit reached!` hint.
- @details Limits warning rendering scope to Claude/Codex `5h` or `7d` cards and Copilot `30d` cards.
- @param result {ProviderResult} Provider result candidate.
- @return {bool} True when provider/window pair is eligible.

### fn `def _should_show_limit_reached_hint(self, result: ProviderResult) -> bool` `priv` (L309-319)
- @brief Determine whether reset text must include `⚠️ Limit reached!`.
- @details Evaluates provider/window scope and displayed usage rounding.
- @param result {ProviderResult} Provider result candidate.
- @return {bool} True when reset label must include limit-reached hint.

### fn `def _format_reset_value(self, reset_str: str, result: ProviderResult) -> str` `priv` (L320-330)
- @brief Compose reset label value with optional limit-reached suffix.
- @param reset_str {str} Countdown text from `_format_duration`.
- @param result {ProviderResult} Provider result candidate.
- @return {str} Reset value with optional `⚠️ Limit reached!` suffix.

### fn `def _format_age(self, seconds: float) -> str` `priv` (L331-344)
- @brief Execute format age.
- @details Applies format age logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param seconds {float} Input parameter `seconds`.
- @return {str} Function return value.

### fn `def _format_duration(self, seconds: float) -> str` `priv` (L345-364)
- @brief Execute format duration.
- @details Applies format duration logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param seconds {float} Input parameter `seconds`.
- @return {str} Function return value.

### class `class RawJsonView(Static)` : Static (L365-412)
- @brief Define raw json view component.
- @details Encapsulates raw json view state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `def compose(self) -> ComposeResult` (L387-397)
  - @brief Define raw json view component.
  - @brief Execute compose.
  - @details Encapsulates raw json view state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
  - @details Applies compose logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {ComposeResult} Function return value.
- fn `def watch_data(self, data: dict | None) -> None` (L398-412)
  - @brief Execute watch data.
  - @details Applies watch data logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param data {dict | None} Input parameter `data`.
  - @return {None} Function return value.

### class `class AIBarUI(App)` : App (L413-612)
- @brief Define a i bar u i component.
- @details Encapsulates a i bar u i state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `BINDINGS = [` (L473)
- var `TITLE = "Usage Metrics UI"` (L481)
- fn `def __init__(self) -> None` `priv` (L486-502)
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
- fn `async def action_refresh(self) -> None` (L567-609)
  - @brief Execute action refresh.
  - @details Applies action refresh logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects. Cache hits are used only for non-Claude providers.
  - @return {None} Function return value.
  - @satisfies REQ-009

### fn `async def action_window_5h(self) -> None` (L610-620)
- @brief Execute action window 5h.
- @details Applies action window 5h logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `async def action_window_7d(self) -> None` (L621-631)
- @brief Execute action window 7d.
- @details Applies action window 7d logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `async def action_toggle_json(self) -> None` (L632-644)
- @brief Execute action toggle json.
- @details Applies action toggle json logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def _get_card(self, provider: ProviderName) -> ProviderCard | None` `priv` (L645-657)
- @brief Execute get card.
- @details Applies get card logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param provider {ProviderName} Input parameter `provider`.
- @return {ProviderCard | None} Function return value.

### fn `def _update_window_buttons(self) -> None` `priv` (L658-677)
- @brief Execute update window buttons.
- @details Applies update window buttons logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def _update_json_view(self) -> None` `priv` (L678-691)
- @brief Execute update json view.
- @details Applies update json view logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def run_ui() -> None` (L692-701)
- @brief Execute run ui.
- @details Applies run ui logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`ProviderCard`|class|pub|45-244|class ProviderCard(Static)|
|`ProviderCard.__init__`|fn|priv|122-125|def __init__(|
|`ProviderCard.compose`|fn|pub|138-161|def compose(self) -> ComposeResult|
|`watch_result`|fn|pub|162-254|def watch_result(self, result: ProviderResult | None) -> ...|
|`watch_is_loading`|fn|pub|255-267|def watch_is_loading(self, loading: bool) -> None|
|`_is_rate_limit_quota_error`|fn|priv|268-282|def _is_rate_limit_quota_error(self, result: ProviderResu...|
|`_is_displayed_full_percent`|fn|priv|283-294|def _is_displayed_full_percent(self, percent: float | Non...|
|`_supports_limit_reached_hint`|fn|priv|295-308|def _supports_limit_reached_hint(self, result: ProviderRe...|
|`_should_show_limit_reached_hint`|fn|priv|309-319|def _should_show_limit_reached_hint(self, result: Provide...|
|`_format_reset_value`|fn|priv|320-330|def _format_reset_value(self, reset_str: str, result: Pro...|
|`_format_age`|fn|priv|331-344|def _format_age(self, seconds: float) -> str|
|`_format_duration`|fn|priv|345-364|def _format_duration(self, seconds: float) -> str|
|`RawJsonView`|class|pub|365-412|class RawJsonView(Static)|
|`RawJsonView.compose`|fn|pub|387-397|def compose(self) -> ComposeResult|
|`RawJsonView.watch_data`|fn|pub|398-412|def watch_data(self, data: dict | None) -> None|
|`AIBarUI`|class|pub|413-612|class AIBarUI(App)|
|`AIBarUI.BINDINGS`|var|pub|473||
|`AIBarUI.TITLE`|var|pub|481||
|`AIBarUI.__init__`|fn|priv|486-502|def __init__(self) -> None|
|`AIBarUI.compose`|fn|pub|503-530|def compose(self) -> ComposeResult|
|`AIBarUI.on_mount`|fn|pub|531-539|async def on_mount(self) -> None|
|`AIBarUI.on_refresh_pressed`|fn|pub|541-548|async def on_refresh_pressed(self) -> None|
|`AIBarUI.on_5h_pressed`|fn|pub|550-557|async def on_5h_pressed(self) -> None|
|`AIBarUI.on_7d_pressed`|fn|pub|559-566|async def on_7d_pressed(self) -> None|
|`AIBarUI.action_refresh`|fn|pub|567-609|async def action_refresh(self) -> None|
|`action_window_5h`|fn|pub|610-620|async def action_window_5h(self) -> None|
|`action_window_7d`|fn|pub|621-631|async def action_window_7d(self) -> None|
|`action_toggle_json`|fn|pub|632-644|async def action_toggle_json(self) -> None|
|`_get_card`|fn|priv|645-657|def _get_card(self, provider: ProviderName) -> ProviderCa...|
|`_update_window_buttons`|fn|priv|658-677|def _update_window_buttons(self) -> None|
|`_update_json_view`|fn|priv|678-691|def _update_json_view(self) -> None|
|`run_ui`|fn|pub|692-701|def run_ui() -> None|


---

# background.js | JavaScript | 1524L | 55 symbols | 2 imports | 62 comments
> Path: `src/aibar/chrome-extension/background.js`
- @brief Chrome extension service-worker runtime for autonomous provider refresh.
- @details Executes ordered provider page downloads, parser normalization, state
persistence, and debug instrumentation on a recurring alarm interval.
- @satisfies PRJ-009
- @satisfies PRJ-010
- @satisfies CTN-008
- @satisfies CTN-009
- @satisfies CTN-012
- @satisfies CTN-013
- @satisfies CTN-014
- @satisfies REQ-043
- @satisfies REQ-044
- @satisfies REQ-046
- @satisfies REQ-047
- @satisfies REQ-048
- @satisfies REQ-049
- @satisfies REQ-050
- @satisfies REQ-051
- @satisfies REQ-052
- @satisfies REQ-045

## Imports
```
import {
import {
```

## Definitions

- const `export const REFRESH_INTERVAL_SECONDS = 180;` (L43)
- @brief Default hardcoded refresh interval in seconds. */
- const `const STATE_STORAGE_KEY = "aibar.chrome.state";` (L46)
- @brief Storage key for normalized runtime state. */
- const `const INTERVAL_OVERRIDE_STORAGE_KEY = "aibar.chrome.refresh_interval_seconds";` (L49)
- @brief Storage key for optional refresh interval override. */
- const `const REFRESH_ALARM_NAME = "aibar-refresh";` (L52)
- @brief Alarm name used by service-worker scheduler. */
- const `const PROVIDER_FETCH_SEQUENCE = [` (L55)
- @brief Fixed provider download sequence required by requirements. */
- const `const MAIN_API_TAB_ORDER = ["claude", "copilot", "codex"];` (L63)
- @brief Canonical popup tab order represented by the primary API snapshot. */
- const `const MAIN_API_PROVIDER_WINDOWS = {` (L66)
- @brief Canonical window order by provider for popup progress-bar rendering. */
- const `const DEBUG_API_SUPPORTED_COMMANDS = [` (L73)
- @brief Debug API command identifiers exposed by runtime messaging. */
- const `const DEBUG_API_ALLOWED_HOSTS = new Set(["claude.ai", "chatgpt.com", "github.com"]);` (L88)
- @brief Allowed hostnames for debug HTTP retrieval command. */
- const `const DEBUG_API_DEFAULT_MAX_CHARS = 16000;` (L91)
- @brief Default debug-body preview cap in characters. */
- const `const DEBUG_API_MAX_CHARS = 120000;` (L94)
- @brief Absolute debug-body preview cap in characters. */
- const `const DEBUG_API_DISABLED_ERROR = "Debug API disabled: enable it in popup configuration for this runtime session.";` (L97)
- @brief Deterministic debug-disabled error returned by all debug API routes. */
- const `const DEBUG_API_PROVIDER_DEFAULT_URLS = {` (L100)
- @brief Provider default URLs used by debug parser command. */
- const `const DEBUG_API_DEFAULT_PROVIDER_DIAGNOSE_SET = ["claude", "codex", "copilot_merged"];` (L108)
- @brief Default provider set used by aggregate diagnose command. */
- const `const DEBUG_API_PROVIDER_PAGES = [` (L111)
- @brief Required provider pages for one-call debug download diagnostics. */
- const `const DEBUG_API_PROVIDER_PAGES_DEFAULT_RELATED_LIMIT = 6;` (L123)
- @brief Default maximum same-origin related resources fetched per provider page. */
### fn `function _emptyProviderState(provider)` (L133-144)
- @brief Build empty provider state object.
- @param {string} provider Provider identifier.
- @return s {Record<string, unknown>} Empty provider state.

### fn `function _emptyState()` (L150-164)
- @brief Build empty extension runtime state.
- @return s {Record<string, unknown>} Empty state snapshot.

### fn `function _cloneState()` (L179-181)
- @brief Deep clone state into message-safe payload.
- @return s {Record<string, unknown>} Cloned state snapshot.

### fn `function _toFiniteMetricNumber(token)` (L188-194)
- @brief Convert optional metric token into finite number without null coercion.
- @param {unknown} token Candidate token.
- @return s {number | null} Finite number or null when token is empty/invalid.

### fn `function _normalizeMainApiWindow(windowData)` (L206-217)
- @brief Normalize one window metric payload for primary API transport.
- @details Restricts window payload shape to popup-rendered progress and quota
fields so API consumers can rebuild tab cards deterministically.
Time complexity: O(1).
Space complexity: O(1).
- @param {Record<string, unknown> | null | undefined} windowData Candidate window payload.
- @return s {{usage_percent: number | null, remaining: number | null, limit: number | null, reset_at: string | null}} Normalized window metrics.
- @satisfies REQ-046

### fn `function _buildMainApiSnapshot()` (L228-262)
- @brief Build machine-readable primary API snapshot payload.
- @details Returns one-call popup/UI model with tab order plus per-provider
progress/quota windows, preserving runtime error and scheduler fields.
Time complexity: O(P*W), where P=provider count and W=window count.
Space complexity: O(P*W).
- @return s {Record<string, unknown>} Primary API snapshot payload.
- @satisfies REQ-046

### fn `function _ensureDebugAccessEnabled()` (L275-282)
- @brief Enforce runtime debug-access gate before serving debug routes.
- @details Uses non-persistent in-memory flag and throws deterministic error to
ensure all debug message routes fail uniformly when disabled.
Time complexity: O(1).
Space complexity: O(1).
- @return s {void}
- @throws {Error} If debug access is disabled.
- @satisfies CTN-014
- @satisfies REQ-051

### fn `async function _loadPersistedState()` (L290-314)
- @brief Merge persisted state into in-memory runtime state.
- @details Preserves last successful provider payloads across service-worker restarts
to satisfy failure fallback requirements.
- @return s {Promise<void>} Completion promise.

### fn `async function _persistState()` (L320-322)
- @brief Persist current runtime state to extension storage.
- @return s {Promise<void>} Completion promise.

### fn `async function _getRefreshIntervalSeconds()` (L330-337)
- @brief Read configured refresh interval with override support.
- @details Uses hardcoded default REFRESH_INTERVAL_SECONDS and allows optional
storage override to support field debugging with shorter/longer cycles.
- @return s {Promise<number>} Effective interval in seconds.

### fn `async function _scheduleRefreshAlarm()` (L343-356)
- @brief Configure periodic refresh alarm.
- @return s {Promise<void>} Completion promise.

### fn `async function _fetchHtml(url)` (L364-376)
- @brief Download one provider page using authenticated extension fetch.
- @param {string} url Target page URL.
- @return s {Promise<string>} Downloaded HTML content.
- @throws {Error} When HTTP status is not OK.

### fn `function _normalizeDebugMaxChars(token)` (L388-394)
- @brief Normalize debug-body preview length with hard bounds.
- @details Converts caller-provided `max_chars` tokens into bounded integers to
avoid oversized responses in debug API payloads.
Time complexity: O(1).
Space complexity: O(1).
- @param {unknown} token Requested max preview characters.
- @return s {number} Bounded preview length.
- @satisfies CTN-013

### fn `function _normalizeDebugUrl(token)` (L407-428)
- @brief Normalize and validate debug URL token.
- @details Enforces `https` scheme and allowlisted hosts for debug retrieval
commands to reduce abuse surface.
Time complexity: O(1).
Space complexity: O(1).
- @param {unknown} token Candidate URL.
- @return s {string} Normalized URL string.
- @throws {Error} If URL is invalid, non-HTTPS, or host is not allowed.
- @satisfies CTN-012

### fn `function _serializeHeaders(headers)` (L436-447)
- @brief Convert response headers into bounded JSON-safe object.
- @details Serializes at most 30 headers to constrain debug response footprint.
- @param {Headers} headers Response headers object.
- @return s {Record<string, string>} Serialized headers map.

### fn `function _buildHtmlProbe(html)` (L454-468)
- @brief Build deterministic HTML probe metadata for parser diagnostics.
- @param {string} html Raw HTML text.
- @return s {Record<string, unknown>} Probe metadata object.

### fn `async function _sha256Hex(text)` (L475-481)
- @brief Compute SHA-256 hash for deterministic body identity checks.
- @param {string} text Input text payload.
- @return s {Promise<string>} Hex-encoded digest.

### fn `function _buildPayloadQuality(payload)` (L488-518)
- @brief Build payload-quality summary for parsed provider windows.
- @param {Record<string, unknown>} payload Parsed provider payload.
- @return s {Record<string, unknown>} Quality summary object.

### fn `function _assertProviderPayloadUsable(provider, payload)` (L527-535)
- @brief Build parser failure error when payload has no usable metrics.
- @param {string} provider Provider key.
- @param {Record<string, unknown>} payload Parsed payload.
- @return s {void}
- @throws {Error} If payload is missing quota/progress metrics.

### fn `async function _downloadDebugUrl(urlToken)` (L543-561)
- @brief Download one debug URL and capture response metadata.
- @param {string} urlToken Debug URL token.
- @return s {Promise<Record<string, unknown>>} Download result with full body.
- @satisfies REQ-047

### fn `async function _buildDebugHttpResponse(download, maxChars)` (L569-586)
- @brief Build debug HTTP response payload with bounded preview and hash metadata.
- @param {Record<string, unknown>} download Raw download payload.
- @param {number} maxChars Bounded preview size.
- @return s {Promise<Record<string, unknown>>} HTTP response payload.

### fn `function _normalizeDebugRelatedLimit(token)` (L598-604)
- @brief Normalize max related-resource downloads for providers.pages.get.
- @details Applies deterministic hard bounds to prevent unbounded secondary page
downloads during debug diagnostics runs.
Time complexity: O(1).
Space complexity: O(1).
- @param {unknown} token Candidate limit value.
- @return s {number} Bounded related-resource limit.
- @satisfies REQ-048

### fn `function _extractRelatedResourceUrls(html, pageUrl)` (L617-645)
- @brief Extract same-origin related resource URLs from one HTML page.
- @details Parses script/link resource attributes and keeps only `https`
same-origin URLs so follow-up debug downloads remain within current host scope.
Time complexity: O(N) on HTML length.
Space complexity: O(M) on extracted URLs.
- @param {string} html Source HTML.
- @param {string} pageUrl Base page URL used for URL resolution.
- @return s {Array<string>} Ordered unique same-origin resource URLs.
- @satisfies REQ-048

### fn `function _buildProviderPayloadAnalysis(provider, payload)` (L654-663)
- @brief Build parser-centric quality summary for one provider payload.
- @param {string} provider Provider token.
- @param {Record<string, unknown>} payload Parsed payload.
- @return s {Record<string, unknown>} Structured quality summary.
- @satisfies REQ-048

### fn `async function _downloadRelatedResources(html, pageUrl, maxChars, maxRelated)` (L674-700)
- @brief Download same-origin related resources for one provider page.
- @param {string} html Page HTML.
- @param {string} pageUrl Source page URL.
- @param {number} maxChars Preview size limit.
- @param {number} maxRelated Resource download limit.
- @return s {Promise<Record<string, unknown>>} Related-resource diagnostics payload.
- @satisfies REQ-048

### fn `async function _executeProviderPageDownload(descriptor, maxChars, maxRelated)` (L710-737)
- @brief Execute one provider-page download diagnostic entry.
- @param {{key: string, url: string, parser: string}} descriptor Provider page descriptor.
- @param {number} maxChars Preview-size limit.
- @param {number} maxRelated Related-resource download limit.
- @return s {Promise<Record<string, unknown>>} Page diagnostics payload.
- @satisfies REQ-048

### fn `async function _executeProvidersPagesGetCommand(args)` (L747-782)
- @brief Execute providers.pages.get debug command.
- @details Downloads required provider pages and same-origin related resources,
runs provider-specific parsers, and returns one aggregate diagnostics payload.
- @param {Record<string, unknown>} args Debug command arguments.
- @return s {Promise<Record<string, unknown>>} Aggregate page diagnostics payload.
- @satisfies REQ-048

### fn `function _buildPayloadAssertion(provider, payload)` (L792-805)
- @brief Build payload-usability assertion status for diagnostics commands.
- @details Reuses runtime parser-usability gate and returns structured pass/fail
metadata without throwing to simplify field-debug report consumption.
- @param {string} provider Provider key.
- @param {Record<string, unknown>} payload Parsed payload.
- @return s {{ok: boolean, error: string | null}} Assertion status payload.

### fn `function _buildWindowAssignmentDiagnostics(html, provider)` (L815-824)
- @brief Build window-assignment diagnostics for one parser HTML source.
- @details Wraps parser trace extraction in non-throwing envelope to keep debug
API responses stable even when trace generation fails.
- @param {string} html Raw HTML payload.
- @param {string} provider Provider token for window-key selection.
- @return s {Record<string, unknown>} Window-trace payload or structured error.

### fn `async function _executeProviderDiagnoseCommand(provider, args, maxChars)` (L835-900)
- @brief Execute provider-level diagnose routine for one provider token.
- @details Downloads provider pages, executes parser flows, and returns combined
response probes, parser payloads, usability checks, and window traces.
- @param {string} provider Provider token.
- @param {Record<string, unknown>} args Debug command arguments.
- @param {number} maxChars Bounded response preview size.
- @return s {Promise<Record<string, unknown>>} Diagnose payload.

### fn `function _resolveDebugParser(provider)` (L908-921)
- @brief Resolve parser function by debug provider key.
- @param {string} provider Provider key token.
- @return s {(html: string) => Record<string, unknown>} Parser function.
- @throws {Error} If provider key is unsupported.

### fn `function _summarizeDebugArgs(args)` (L929-944)
- @brief Build summary-safe command args for debug logging.
- @details Redacts large inline HTML fields by replacing them with length metadata.
- @param {Record<string, unknown>} args Debug command args.
- @return s {Record<string, unknown>} Sanitized argument summary.

### fn `function _describeDebugApi()` (L951-971)
- @brief Build debug API command catalog payload.
- @return s {Record<string, unknown>} Supported command catalog.
- @satisfies REQ-046

### fn `async function _executeDebugApiCommand(command, args)` (L985-1155)
- @brief Execute one debug API command.
- @details Dispatches debug commands for HTTP retrieval, parser execution, and
standard runtime operations with deterministic structured responses.
- @param {string} command Debug command identifier.
- @param {Record<string, unknown>} args Debug command arguments.
- @return s {Promise<Record<string, unknown>>} Command execution payload.
- @throws {Error} If command or arguments are invalid.
- @satisfies REQ-047
- @satisfies REQ-048
- @satisfies REQ-049

### fn `function _applyProviderSuccess(provider, payload)` (L1163-1170)
- @brief Apply successful provider refresh payload.
- @param {string} provider Provider key.
- @param {Record<string, unknown>} payload Parsed provider payload.
- @return s {void}

### fn `function _applyProviderFailure(provider, error)` (L1178-1184)
- @brief Apply provider refresh failure while preserving last successful windows.
- @param {string} provider Provider key.
- @param {Error} error Failure object.
- @return s {void}

### fn `async function _refreshAllProviders(trigger)` (L1192-1299)
- @brief Execute one ordered refresh cycle across all provider pages.
- @details Preserves successful state on errors and emits debug logs for each step.
- @param {string} trigger Refresh trigger source.
- @return s {Promise<void>} Completion promise.

### fn `async function _initializeRuntime(trigger)` (L1306-1311)
- @brief Initialize scheduler and persisted state for service-worker lifecycle.
- @param {string} trigger Initialization trigger label.
- @return s {Promise<void>} Completion promise.

### fn `async function _handleMessage(message, sendResponse)` (L1321-1488)
- @brief Handle incoming runtime messages from popup/UI contexts.
- @details Supports state retrieval, manual refresh, debug log operations, and
refresh-interval override updates.
- @param {Record<string, unknown>} message Message payload.
- @param {(response: Record<string, unknown>) => void} sendResponse Response callback.
- @return s {Promise<void>} Completion promise.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`REFRESH_INTERVAL_SECONDS`|const||43||
|`STATE_STORAGE_KEY`|const||46||
|`INTERVAL_OVERRIDE_STORAGE_KEY`|const||49||
|`REFRESH_ALARM_NAME`|const||52||
|`PROVIDER_FETCH_SEQUENCE`|const||55||
|`MAIN_API_TAB_ORDER`|const||63||
|`MAIN_API_PROVIDER_WINDOWS`|const||66||
|`DEBUG_API_SUPPORTED_COMMANDS`|const||73||
|`DEBUG_API_ALLOWED_HOSTS`|const||88||
|`DEBUG_API_DEFAULT_MAX_CHARS`|const||91||
|`DEBUG_API_MAX_CHARS`|const||94||
|`DEBUG_API_DISABLED_ERROR`|const||97||
|`DEBUG_API_PROVIDER_DEFAULT_URLS`|const||100||
|`DEBUG_API_DEFAULT_PROVIDER_DIAGNOSE_SET`|const||108||
|`DEBUG_API_PROVIDER_PAGES`|const||111||
|`DEBUG_API_PROVIDER_PAGES_DEFAULT_RELATED_LIMIT`|const||123||
|`_emptyProviderState`|fn||133-144|function _emptyProviderState(provider)|
|`_emptyState`|fn||150-164|function _emptyState()|
|`_cloneState`|fn||179-181|function _cloneState()|
|`_toFiniteMetricNumber`|fn||188-194|function _toFiniteMetricNumber(token)|
|`_normalizeMainApiWindow`|fn||206-217|function _normalizeMainApiWindow(windowData)|
|`_buildMainApiSnapshot`|fn||228-262|function _buildMainApiSnapshot()|
|`_ensureDebugAccessEnabled`|fn||275-282|function _ensureDebugAccessEnabled()|
|`_loadPersistedState`|fn||290-314|async function _loadPersistedState()|
|`_persistState`|fn||320-322|async function _persistState()|
|`_getRefreshIntervalSeconds`|fn||330-337|async function _getRefreshIntervalSeconds()|
|`_scheduleRefreshAlarm`|fn||343-356|async function _scheduleRefreshAlarm()|
|`_fetchHtml`|fn||364-376|async function _fetchHtml(url)|
|`_normalizeDebugMaxChars`|fn||388-394|function _normalizeDebugMaxChars(token)|
|`_normalizeDebugUrl`|fn||407-428|function _normalizeDebugUrl(token)|
|`_serializeHeaders`|fn||436-447|function _serializeHeaders(headers)|
|`_buildHtmlProbe`|fn||454-468|function _buildHtmlProbe(html)|
|`_sha256Hex`|fn||475-481|async function _sha256Hex(text)|
|`_buildPayloadQuality`|fn||488-518|function _buildPayloadQuality(payload)|
|`_assertProviderPayloadUsable`|fn||527-535|function _assertProviderPayloadUsable(provider, payload)|
|`_downloadDebugUrl`|fn||543-561|async function _downloadDebugUrl(urlToken)|
|`_buildDebugHttpResponse`|fn||569-586|async function _buildDebugHttpResponse(download, maxChars)|
|`_normalizeDebugRelatedLimit`|fn||598-604|function _normalizeDebugRelatedLimit(token)|
|`_extractRelatedResourceUrls`|fn||617-645|function _extractRelatedResourceUrls(html, pageUrl)|
|`_buildProviderPayloadAnalysis`|fn||654-663|function _buildProviderPayloadAnalysis(provider, payload)|
|`_downloadRelatedResources`|fn||674-700|async function _downloadRelatedResources(html, pageUrl, m...|
|`_executeProviderPageDownload`|fn||710-737|async function _executeProviderPageDownload(descriptor, m...|
|`_executeProvidersPagesGetCommand`|fn||747-782|async function _executeProvidersPagesGetCommand(args)|
|`_buildPayloadAssertion`|fn||792-805|function _buildPayloadAssertion(provider, payload)|
|`_buildWindowAssignmentDiagnostics`|fn||815-824|function _buildWindowAssignmentDiagnostics(html, provider)|
|`_executeProviderDiagnoseCommand`|fn||835-900|async function _executeProviderDiagnoseCommand(provider, ...|
|`_resolveDebugParser`|fn||908-921|function _resolveDebugParser(provider)|
|`_summarizeDebugArgs`|fn||929-944|function _summarizeDebugArgs(args)|
|`_describeDebugApi`|fn||951-971|function _describeDebugApi()|
|`_executeDebugApiCommand`|fn||985-1155|async function _executeDebugApiCommand(command, args)|
|`_applyProviderSuccess`|fn||1163-1170|function _applyProviderSuccess(provider, payload)|
|`_applyProviderFailure`|fn||1178-1184|function _applyProviderFailure(provider, error)|
|`_refreshAllProviders`|fn||1192-1299|async function _refreshAllProviders(trigger)|
|`_initializeRuntime`|fn||1306-1311|async function _initializeRuntime(trigger)|
|`_handleMessage`|fn||1321-1488|async function _handleMessage(message, sendResponse)|


---

# debug.js | JavaScript | 226L | 13 symbols | 0 imports | 19 comments
> Path: `src/aibar/chrome-extension/debug.js`
- @brief Structured debug instrumentation for AIBar Chrome extension runtime.
- @details Provides console logging, persisted ring-buffer logging in chrome.storage.local,
and debug-bundle utilities used by background and popup execution units.
- @satisfies CTN-011
- @satisfies REQ-044
- @satisfies REQ-045
- @satisfies REQ-050

## Definitions

- const `export const DEBUG_LOG_STORAGE_KEY = "aibar.debug.logs";` (L13)
- @brief Storage key containing persisted debug records. */
- const `export const DEBUG_LOG_MAX_RECORDS = 600;` (L16)
- @brief Maximum persisted debug records retained in storage. */
- const `const DEBUG_VALUE_MAX_LENGTH = 2048;` (L19)
- @brief Maximum serialized string length per persisted value. */
- const `const DEBUG_CLONE_DEPTH_LIMIT = 3;` (L22)
- @brief Maximum recursion depth allowed for debug-value cloning. */
### fn `function _cloneDebugValue(value, depth = 0)` (L34-63)
- @brief Produce bounded serialization-safe values for persisted logging.
- @details Recursively clones primitive/object inputs with explicit depth and collection
size limits to prevent storage exhaustion and cyclic-reference crashes.
Time complexity: O(N) on traversed properties up to bounded depth.
Space complexity: O(N) on cloned projection size.
- @param {unknown} value Input value.
- @param {number} depth Current recursion depth.
- @return s {unknown} Serialization-safe bounded value.

### fn `function _resolveConsoleMethod(level)` (L75-87)
- @brief Resolve one bound console sink method for safe invocation.
- @details Avoids illegal-invocation runtime errors by binding console methods
and returning null when the requested sink is unavailable.
Time complexity: O(1).
Space complexity: O(1).
- @param {string} level Log sink identifier.
- @return s {((...args: Array<unknown>) => void) | null} Bound console method or null.
- @satisfies REQ-050

### fn `function _emitConsoleSafe(level, prefix, safeDetails)` (L101-111)
- @brief Emit one console log entry while suppressing sink-level failures.
- @details Prevents logging-path exceptions from breaking caller execution by
guarding bound console method invocation in a local try/catch block.
Time complexity: O(1).
Space complexity: O(1).
- @param {string} level Log level.
- @param {string} prefix Console prefix.
- @param {unknown} safeDetails Serialization-safe details payload.
- @return s {void}
- @satisfies REQ-050

### fn `export async function appendDebugRecord(record)` (L122-129)
- @brief Persist one debug record into storage ring buffer.
- @details Appends a single record under DEBUG_LOG_STORAGE_KEY and truncates
older records to DEBUG_LOG_MAX_RECORDS to keep bounded storage usage.
Time complexity: O(N) on retained log count.
Space complexity: O(N) for stored log array.
- @param {Record<string, unknown>} record Structured log record.
- @return s {Promise<void>} Completion promise.

### fn `export function createLogger(scope)` (L138-190)
- @brief Create scoped logger with console + persisted logging sinks.
- @brief Emit one structured log event.
- @details Each log method emits to the browser console and asynchronously appends
one structured record to storage while preserving refresh/runtime execution flow.
- @details Normalizes payload values through bounded cloning and appends one timestamped record to storage while mirroring output in console.
- @param {string} scope Logger scope label.
- @param {"debug"|"info"|"warn"|"error"} level Log level.
- @param {string} event Event identifier.
- @param {Record<string, unknown>} details Structured context payload.
- @return s {{debug: Function, info: Function, warn: Function, error: Function}} Scoped logger API.
- @return s {Promise<void>} Completion promise.

### fn `async function write(level, event, details = {})` (L148-170)
- @brief Emit one structured log event.
- @details Normalizes payload values through bounded cloning and appends one
timestamped record to storage while mirroring output in console.
- @param {"debug"|"info"|"warn"|"error"} level Log level.
- @param {string} event Event identifier.
- @param {Record<string, unknown>} details Structured context payload.
- @return s {Promise<void>} Completion promise.

### fn `export async function readDebugRecords()` (L198-202)
- @brief Load persisted debug records from storage.
- @details Returns records as-is from storage ring buffer key; returns empty array
when no records are available.
- @return s {Promise<Array<Record<string, unknown>>>} Persisted records.

### fn `export async function clearDebugRecords()` (L209-211)
- @brief Remove all persisted debug records.
- @details Deletes the storage key used for ring-buffer logs.
- @return s {Promise<void>} Completion promise.

### fn `export async function buildDebugBundle(state)` (L219-226)
- @brief Build one export-ready debug bundle from state and records.
- @details Produces deterministic JSON payload used by popup export action.
- @param {Record<string, unknown>} state Current extension state snapshot.
- @return s {Promise<Record<string, unknown>>} Export payload.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`DEBUG_LOG_STORAGE_KEY`|const||13||
|`DEBUG_LOG_MAX_RECORDS`|const||16||
|`DEBUG_VALUE_MAX_LENGTH`|const||19||
|`DEBUG_CLONE_DEPTH_LIMIT`|const||22||
|`_cloneDebugValue`|fn||34-63|function _cloneDebugValue(value, depth = 0)|
|`_resolveConsoleMethod`|fn||75-87|function _resolveConsoleMethod(level)|
|`_emitConsoleSafe`|fn||101-111|function _emitConsoleSafe(level, prefix, safeDetails)|
|`appendDebugRecord`|fn||122-129|export async function appendDebugRecord(record)|
|`createLogger`|fn||138-190|export function createLogger(scope)|
|`write`|fn||148-170|async function write(level, event, details = {})|
|`readDebugRecords`|fn||198-202|export async function readDebugRecords()|
|`clearDebugRecords`|fn||209-211|export async function clearDebugRecords()|
|`buildDebugBundle`|fn||219-226|export async function buildDebugBundle(state)|


---

# parsers.js | JavaScript | 1830L | 64 symbols | 0 imports | 69 comments
> Path: `src/aibar/chrome-extension/parsers.js`
- @brief Localization-independent HTML parser primitives for AIBar Chrome extension.
- @details Extracts quota and progress metrics from provider usage pages by using
DOM semantics (`role=progressbar`, numeric attributes, `datetime`, embedded JSON)
plus script bootstrap payload extraction, instead of localized visible labels.
- @satisfies CTN-010
- @satisfies REQ-040
- @satisfies REQ-041
- @satisfies REQ-042

## Definitions

- const `export const PARSER_VERSION = "2026.03.06.3";` (L14)
- @brief Parser semantic version for debug payloads. */
- const `const WINDOW_HINT_REGEX = /\b(5h|7d|30d)\b/i;` (L17)
- @brief Token regex for window hints. */
- const `const WINDOW_HINT_GLOBAL_REGEX = /\b(5h|7d|30d)\b/ig;` (L20)
- @brief Global token regex for iterating over window hints in text streams. */
- const `const FRACTION_REGEX = /([0-9][0-9\s.,]*)\s*\/\s*([0-9][0-9\s.,]*)/g;` (L23)
- @brief Token regex for numeric fractions. */
- const `const FRACTION_OF_REGEX = /([0-9][0-9\s.,]*)\s*(?:of|out\s+of|de|su|von|sur)\s*([0-9][0-9\s.,]*)/gi;` (L26)
- @brief Token regex for textual fraction forms (`A of B`, `A de B`, `A su B`). */
- const `const PERCENT_REGEX = /([0-9][0-9\s.,]*)\s*%/g;` (L29)
- @brief Token regex for percentage values. */
- const `const ISO_DATETIME_REGEX = /\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})\b/g;` (L32)
- @brief ISO datetime token regex for inline/script extraction. */
- const `const JSON_BOOTSTRAP_KEYS = [` (L35)
- @brief Bootstrap variable names that frequently carry usage payloads. */
- const `const REMAINING_KEY_FRAGMENTS = [` (L45)
- @brief Key fragments used to infer remaining quota values. */
- const `const LIMIT_KEY_FRAGMENTS = [` (L55)
- @brief Key fragments used to infer limit quota values. */
- const `const USED_KEY_FRAGMENTS = [` (L66)
- @brief Key fragments used to infer used/consumed values. */
- const `const USAGE_PERCENT_KEY_FRAGMENTS = [` (L76)
- @brief Key fragments used to infer usage percentage values. */
### fn `export function parseLocalizedNumber(token)` (L92-136)
- @brief Parse localized numeric token into a finite number.
- @details Supports comma/dot decimal formats and thousands separators by
deterministic normalization rules; rejects non-finite values.
- @param {string | number | null | undefined} token Candidate numeric token.
- @return s {number | null} Parsed finite number or null when invalid.

### fn `function _isPlausibleFractionToken(rawToken)` (L145-154)
- @brief Validate one raw numeric token extracted from fraction regex matches.
- @details Rejects ambiguous mixed-number fragments (for example `6 8`) while
accepting locale thousands grouping (for example `1 500`).
- @param {string} rawToken Raw regex capture token.
- @return s {boolean} True when token shape is numerically plausible.

- const `const MONTH_TOKEN_TO_INDEX = {` (L157)
- @brief Locale-agnostic month token lookup for natural-language datetime parsing. */
### fn `function _resolveMonthIndex(token)` (L218-225)
- @brief Resolve month index from locale-dependent month token.
- @param {string} token Month token.
- @return s {number | null} Month index in range [1, 12] or null.

### fn `function _buildIsoFromDateParts(year, monthIndex, day, hour, minute)` (L236-247)
- @brief Build deterministic ISO timestamp from parsed date/time components.
- @param {number} year Full year.
- @param {number} monthIndex Month index in range [1, 12].
- @param {number} day Day of month.
- @param {number | null} hour Hour component.
- @param {number | null} minute Minute component.
- @return s {string | null} ISO timestamp or null.

### fn `function _clamp(value, min, max)` (L256-261)
- @brief Clamp value into inclusive min/max interval.
- @param {number | null} value Candidate number.
- @param {number} min Inclusive minimum.
- @param {number} max Inclusive maximum.
- @return s {number | null} Clamped value or null.

### fn `function _extractAttribute(tagHtml, attributeName)` (L270-277)
- @brief Parse one HTML tag attribute value.
- @details Parses quoted/unquoted HTML attributes using regex extraction.
- @param {string} tagHtml Full tag HTML.
- @param {string} attributeName Attribute name to extract.
- @return s {string | null} Attribute value or null.

### fn `function _extractWindowHint(context)` (L284-300)
- @brief Infer usage window token from local HTML context.
- @param {string} context Text context around parsed metric element.
- @return s {string | null} Window hint token (`5h`, `7d`, `30d`) or null.

### fn `function _extractPlainText(html)` (L308-317)
- @brief Strip script/style blocks and tags from HTML.
- @details Produces compact text stream used for fraction/percent extraction.
- @param {string} html Raw HTML.
- @return s {string} Plain text approximation.

### fn `function _extractScriptEntries(html)` (L324-336)
- @brief Extract script-tag entries with full tag and body slices.
- @param {string} html Raw HTML.
- @return s {Array<Record<string, string>>} Script entries.

### fn `function _extractScriptText(html)` (L343-348)
- @brief Join all script bodies into one diagnostic text stream.
- @param {string} html Raw HTML.
- @return s {string} Concatenated script text.

### fn `function _extractProgressMetrics(html)` (L357-393)
- @brief Extract progress-bar metrics from semantic HTML attributes.
- @details Supports both generic tags with `role=progressbar` and `<progress>`
elements using `aria-valuenow/max` or `value/max` attributes.
- @param {string} html Raw HTML.
- @return s {Array<Record<string, number | string | null>>} Ordered progress-bar records.

### fn `function _extractFractionCandidatesFromText(text)` (L402-436)
- @brief Extract numeric fraction candidates from one generic text stream.
- @details Captures raw numeric pairs (`A/B`) that may encode used/limit or
remaining/limit values independent from natural-language labels.
- @param {string} text Generic text stream.
- @return s {Array<Record<string, number>>} Ordered fraction records.

### fn `function _extractPercentCandidatesFromText(text)` (L443-454)
- @brief Extract percentage literals from one generic text stream.
- @param {string} text Generic text stream.
- @return s {Array<number>} Ordered percentage numbers.

### fn `function _extractDatetimeCandidatesFromText(text)` (L461-513)
- @brief Extract ISO-like datetime tokens from one generic text stream.
- @param {string} text Generic text stream.
- @return s {Array<{value: string, window_hint: string | null}>} Ordered datetime candidates.

### fn `function _dedupeByKey(values, keySelector)` (L522-534)
- @brief Deduplicate array values while preserving original ordering.
@template T
- @param {Array<T>} values Candidate values.
- @param {(entry: T) => string} keySelector Unique-key selector.
- @return s {Array<T>} Deduplicated values.

### fn `function _escapeRegexToken(token)` (L541-543)
- @brief Escape regex-reserved characters in token for literal pattern use.
- @param {string} token Raw token.
- @return s {string} Escaped token.

### fn `function _extractNumericKeyMatches(text, keyFragments)` (L551-573)
- @brief Extract numeric key-value matches from one text fragment.
- @param {string} text Source text.
- @param {Array<string>} keyFragments Key-name fragments.
- @return s {Array<Record<string, number | string>>} Ordered key matches.

### fn `function _selectNumericFromMatches(keyMatches, anchorIndex, preferBeforeAnchor)` (L582-601)
- @brief Select one representative value from matched key-value records.
- @param {Array<Record<string, number | string>>} keyMatches Numeric key matches.
- @param {number} anchorIndex Anchor position used to select nearest value.
- @param {boolean} preferBeforeAnchor Whether to prioritize key matches before anchor.
- @return s {{value: number | null, key: string | null}} Selected value/key pair.

### fn `function _buildScriptContextCandidate(scriptText, centerIndex, resetAt, preferBeforeAnchor)` (L611-679)
- @brief Build script-context metric candidate around a target token index.
- @param {string} scriptText Script text stream.
- @param {number} centerIndex Center index for context extraction.
- @param {string | null} resetAt Optional reset timestamp.
- @param {boolean} preferBeforeAnchor Whether to prioritize matches before center.
- @return s {Record<string, unknown> | null} Candidate payload or null.

### fn `function _extractEscapedScriptMetricCandidates(html)` (L688-761)
- @brief Extract metric candidates from escaped script key-value artifacts.
- @details Targets script contexts around datetime and window tokens to recover
quota/progress values when app-shell HTML contains no visible usage rows.
- @param {string} html Raw HTML.
- @return s {Array<Record<string, unknown>>} Ordered script-derived candidates.

### fn `function _extractFractionCandidates(html)` (L768-772)
- @brief Extract numeric fraction candidates from visible and script text streams.
- @param {string} html Raw HTML.
- @return s {Array<Record<string, number>>} Ordered fraction records.

### fn `function _extractPercentCandidates(html)` (L779-783)
- @brief Extract percentage literals from visible and script text streams.
- @param {string} html Raw HTML.
- @return s {Array<number>} Ordered percentage numbers.

### fn `function _extractDatetimeCandidates(html)` (L791-812)
- @brief Extract ISO-like datetime tokens from markup and script content.
- @details Reads `datetime="..."` attributes and optional ISO literals in script.
- @param {string} html Raw HTML.
- @return s {Array<{value: string, window_hint: string | null}>} Ordered datetime candidates.

### fn `function _normalizeDatetimeCandidate(entry)` (L819-838)
- @brief Normalize one datetime candidate into deterministic value/hint tuple.
- @param {unknown} entry Datetime candidate entry.
- @return s {{value: string, window_hint: string | null} | null} Normalized candidate.

### fn `function _pickDatetimeCandidate(datetimeCandidates, windowKey, index)` (L847-876)
- @brief Select best datetime candidate for target window by hint + index fallback.
- @param {Array<string | {value: string, window_hint: string | null}>} datetimeCandidates Datetime candidates.
- @param {string} windowKey Target window key.
- @param {number} index Ordered fallback index.
- @return s {string | null} Selected datetime ISO value.

### fn `function _extractBalancedJsonSlice(source, startIndex)` (L884-932)
- @brief Extract balanced JSON slice starting at object/array token.
- @param {string} source Source text.
- @param {number} startIndex Start index for `{` or `[` token.
- @return s {string | null} Balanced JSON slice or null.

### fn `function _extractEnclosingJsonObjectContext(source, centerIndex)` (L940-1239)
- @brief Resolve smallest enclosing JSON-object slice around one center index.
- @param {string} source Source text.
- @param {number} centerIndex Center index.
- @return s {{context_start: number, context_end: number} | null} Context bounds.

### fn `function _decodeQuotedJsonPayload(quotedToken)` (L967-1266)
- @brief Decode quoted JSON payload and parse into object when possible.
- @param {string} quotedToken Quoted JS/JSON token.
- @return s {unknown | null} Parsed payload or null.

### fn `function _extractBootstrapJsonFromScriptBody(scriptBody)` (L987-1286)
- @brief Extract bootstrap JSON objects from script assignment statements.
- @param {string} scriptBody Script body text.
- @return s {Array<unknown>} Parsed JSON roots.

### fn `function _extractEmbeddedJsonObjects(html)` (L1036-1058)
- @brief Collect embedded JSON payloads from script tags.
- @details Parses `application/json`, `application/ld+json`, and `__NEXT_DATA__`
scripts plus bootstrap assignment payloads into objects for language-agnostic
metric extraction.
- @param {string} html Raw HTML.
- @return s {Array<unknown>} Parsed JSON roots.

### fn `function _pickNumericEntryByKey(obj, keyRegexes, excludeKeyRegexes = [])` (L1067-1087)
- @brief Resolve first numeric entry from object keys matching regex list.
- @param {Record<string, unknown>} obj Object candidate.
- @param {Array<RegExp>} keyRegexes Key regex matchers.
- @param {Array<RegExp>} excludeKeyRegexes Key regexes excluded from selection.
- @return s {{key: string | null, value: number | null}} First parsed numeric entry.

### fn `function _pickDatetimeByKey(obj, keyRegexes)` (L1095-1109)
- @brief Resolve first datetime-like value from object keys matching regex list.
- @param {Record<string, unknown>} obj Object candidate.
- @param {Array<RegExp>} keyRegexes Key regex matchers.
- @return s {string | null} ISO timestamp or null.

### fn `function _extractJsonMetricCandidates(root)` (L1118-1204)
- @brief Recursively extract metric candidates from parsed JSON roots.
- @details Uses provider-agnostic key families for quota/usage/reset values and
window hints; traversal is bounded by visited-object set.
- @param {unknown} root Parsed JSON root.
- @return s {Array<Record<string, number | string | null>>} Candidate metrics.

### fn `function walk(node)` (L1127-1200)
- @brief Depth-first traversal over JSON object graph.
- @param {unknown} node Current node.
- @return s {void}

### fn `function _candidateScore(candidate, windowKey)` (L1212-1248)
- @brief Compute normalized candidate score for window assignment.
- @param {Record<string, unknown>} candidate Candidate payload.
- @param {string} windowKey Target window key.
- @return s {number} Descending score; negative values indicate poor fit.

### fn `function _rankCandidates(candidates, windowKey, index)` (L1259-1267)
- @brief Rank candidates by score and fallback distance for one window.
- @details Produces deterministic ranking tuples used both by runtime selection
and by debug diagnostics so parser decisions remain explainable.
- @param {Array<Record<string, unknown>>} candidates Candidate list.
- @param {string} windowKey Target window key.
- @param {number} index Ordered fallback index.
- @return s {Array<Record<string, unknown>>} Ranked tuples with `item`, `score`, and `distance`.

### fn `function _traceCandidate(candidate)` (L1274-1288)
- @brief Normalize candidate payload into compact debug-trace shape.
- @param {Record<string, unknown> | null} candidate Candidate payload.
- @return s {Record<string, unknown> | null} Compact trace payload.

### fn `function _pickCandidate(candidates, windowKey, index)` (L1297-1305)
- @brief Select one best-matching candidate by score and index proximity.
- @param {Array<Record<string, unknown>>} candidates Candidate list.
- @param {string} windowKey Target window key.
- @param {number} index Ordered fallback index.
- @return s {Record<string, unknown> | null} Selected candidate.

### fn `function _inferQuotaFromFraction(fraction, usagePercent)` (L1315-1345)
- @brief Infer remaining/limit from fraction candidate and usage percentage.
- @details Chooses interpretation (`used/limit` vs `remaining/limit`) minimizing
percentage-distance from known usage value when available.
- @param {{first: number, second: number}} fraction Fraction candidate.
- @param {number | null} usagePercent Known usage percentage.
- @return s {{remaining: number | null, limit: number | null}} Inferred values.

### fn `function _buildWindows(` (L1358-1497)
- @brief Build one normalized window metrics record.
- @param {Array<string>} windowKeys Ordered window keys.
- @param {Array<Record<string, number | string | null>>} progressCandidates Progress candidates.
- @param {Array<Record<string, number>>} fractionCandidates Fraction candidates.
- @param {Array<number | null>} percentCandidates Percent candidates.
- @param {Array<string | {value: string, window_hint: string | null}>} datetimeCandidates Datetime candidates.
- @param {Array<Record<string, number | string | null>>} jsonCandidates JSON-derived candidates.
- @param {Record<string, unknown> | null} traceOutput Mutable trace object populated when requested.
- @return s {Record<string, Record<string, number | string | null>>} Window metrics map.

### fn `function _extractSignals(html)` (L1504-1530)
- @brief Extract all parser signal families from one HTML payload.
- @param {string} html Raw HTML page source.
- @return s {Record<string, unknown>} Signal bundle.

### fn `function _buildProviderPayload(provider, windows, signals, sourcePages)` (L1540-1560)
- @brief Build normalized provider payload with parser diagnostics.
- @param {string} provider Provider key.
- @param {Record<string, Record<string, number | string | null>>} windows Window map.
- @param {Record<string, unknown>} signals Parser signal bundle.
- @param {Array<string>} sourcePages Source page URLs.
- @return s {Record<string, unknown>} Provider payload.

### fn `export function providerPayloadHasUsableMetrics(payload)` (L1569-1581)
- @brief Determine whether payload contains usable quota/usage metrics.
- @details Rejects payloads that contain only reset timestamps without
quota/progress numbers to avoid false-positive parser success states.
- @param {Record<string, unknown> | null | undefined} payload Parsed payload.
- @return s {boolean} True when at least one window has quota or usage metrics.

### fn `function _sample(values, maxItems)` (L1589-1591)
- @brief Build compact signal sample payload for debug API responses.
- @param {Array<unknown>} values Candidate values.
- @param {number} maxItems Maximum number of sample entries.
- @return s {Array<unknown>} Bounded sample array.

### fn `export function extractSignalDiagnostics(html)` (L1598-1634)
- @brief Extract parser signal counts and bounded samples for diagnostics.
- @param {string} html Raw HTML page source.
- @return s {Record<string, unknown>} Signal diagnostics.

### fn `export function extractWindowAssignmentDiagnostics(html, options = {})` (L1647-1691)
- @brief Extract per-window candidate-selection trace for parser diagnostics.
- @details Replays window assembly using provider-specific window keys and emits
deterministic candidate rankings plus derived output values for each window.
Time complexity: O(N log N) over candidate counts due to per-window ranking.
Space complexity: O(N) for trace snapshots.
- @param {string} html Raw HTML page source.
- @param {{provider?: string} | null | undefined} options Diagnostic options.
- @return s {Record<string, unknown>} Window-assignment diagnostic payload.
- @throws {Error} If provider token is unsupported.

### fn `export function parseClaudeUsageHtml(html)` (L1700-1711)
- @brief Parse Claude usage HTML into normalized window metrics.
- @details Targets windows `5h` and `7d` using ordered semantic extraction.
- @param {string} html Claude usage page HTML.
- @return s {Record<string, unknown>} Normalized Claude payload.
- @satisfies REQ-040

### fn `export function parseCodexUsageHtml(html)` (L1720-1731)
- @brief Parse Codex usage HTML into normalized window metrics.
- @details Targets windows `5h` and `7d` using ordered semantic extraction.
- @param {string} html Codex usage page HTML.
- @return s {Record<string, unknown>} Normalized Codex payload.
- @satisfies REQ-041

### fn `export function parseCopilotFeaturesHtml(html)` (L1738-1754)
- @brief Parse Copilot features-page HTML into normalized window metrics.
- @param {string} html Copilot features page HTML.
- @return s {Record<string, unknown>} Normalized features payload.

### fn `export function parseCopilotPremiumHtml(html)` (L1761-1777)
- @brief Parse Copilot premium-requests HTML into normalized window metrics.
- @param {string} html Copilot premium page HTML.
- @return s {Record<string, unknown>} Normalized premium payload.

### fn `export function mergeCopilotPayloads(featuresPayload, premiumPayload)` (L1788-1830)
- @brief Merge Copilot feature and premium payloads into one consumer payload.
- @details Selects the richest `30d` window metrics and aggregates source-page and
parser signal counters for traceable diagnostics.
- @param {Record<string, unknown>} featuresPayload Copilot features parsed payload.
- @param {Record<string, unknown>} premiumPayload Copilot premium parsed payload.
- @return s {Record<string, unknown>} Merged Copilot payload.
- @satisfies REQ-042

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`PARSER_VERSION`|const||14||
|`WINDOW_HINT_REGEX`|const||17||
|`WINDOW_HINT_GLOBAL_REGEX`|const||20||
|`FRACTION_REGEX`|const||23||
|`FRACTION_OF_REGEX`|const||26||
|`PERCENT_REGEX`|const||29||
|`ISO_DATETIME_REGEX`|const||32||
|`JSON_BOOTSTRAP_KEYS`|const||35||
|`REMAINING_KEY_FRAGMENTS`|const||45||
|`LIMIT_KEY_FRAGMENTS`|const||55||
|`USED_KEY_FRAGMENTS`|const||66||
|`USAGE_PERCENT_KEY_FRAGMENTS`|const||76||
|`parseLocalizedNumber`|fn||92-136|export function parseLocalizedNumber(token)|
|`_isPlausibleFractionToken`|fn||145-154|function _isPlausibleFractionToken(rawToken)|
|`MONTH_TOKEN_TO_INDEX`|const||157||
|`_resolveMonthIndex`|fn||218-225|function _resolveMonthIndex(token)|
|`_buildIsoFromDateParts`|fn||236-247|function _buildIsoFromDateParts(year, monthIndex, day, ho...|
|`_clamp`|fn||256-261|function _clamp(value, min, max)|
|`_extractAttribute`|fn||270-277|function _extractAttribute(tagHtml, attributeName)|
|`_extractWindowHint`|fn||284-300|function _extractWindowHint(context)|
|`_extractPlainText`|fn||308-317|function _extractPlainText(html)|
|`_extractScriptEntries`|fn||324-336|function _extractScriptEntries(html)|
|`_extractScriptText`|fn||343-348|function _extractScriptText(html)|
|`_extractProgressMetrics`|fn||357-393|function _extractProgressMetrics(html)|
|`_extractFractionCandidatesFromText`|fn||402-436|function _extractFractionCandidatesFromText(text)|
|`_extractPercentCandidatesFromText`|fn||443-454|function _extractPercentCandidatesFromText(text)|
|`_extractDatetimeCandidatesFromText`|fn||461-513|function _extractDatetimeCandidatesFromText(text)|
|`_dedupeByKey`|fn||522-534|function _dedupeByKey(values, keySelector)|
|`_escapeRegexToken`|fn||541-543|function _escapeRegexToken(token)|
|`_extractNumericKeyMatches`|fn||551-573|function _extractNumericKeyMatches(text, keyFragments)|
|`_selectNumericFromMatches`|fn||582-601|function _selectNumericFromMatches(keyMatches, anchorInde...|
|`_buildScriptContextCandidate`|fn||611-679|function _buildScriptContextCandidate(scriptText, centerI...|
|`_extractEscapedScriptMetricCandidates`|fn||688-761|function _extractEscapedScriptMetricCandidates(html)|
|`_extractFractionCandidates`|fn||768-772|function _extractFractionCandidates(html)|
|`_extractPercentCandidates`|fn||779-783|function _extractPercentCandidates(html)|
|`_extractDatetimeCandidates`|fn||791-812|function _extractDatetimeCandidates(html)|
|`_normalizeDatetimeCandidate`|fn||819-838|function _normalizeDatetimeCandidate(entry)|
|`_pickDatetimeCandidate`|fn||847-876|function _pickDatetimeCandidate(datetimeCandidates, windo...|
|`_extractBalancedJsonSlice`|fn||884-932|function _extractBalancedJsonSlice(source, startIndex)|
|`_extractEnclosingJsonObjectContext`|fn||940-1239|function _extractEnclosingJsonObjectContext(source, cente...|
|`_decodeQuotedJsonPayload`|fn||967-1266|function _decodeQuotedJsonPayload(quotedToken)|
|`_extractBootstrapJsonFromScriptBody`|fn||987-1286|function _extractBootstrapJsonFromScriptBody(scriptBody)|
|`_extractEmbeddedJsonObjects`|fn||1036-1058|function _extractEmbeddedJsonObjects(html)|
|`_pickNumericEntryByKey`|fn||1067-1087|function _pickNumericEntryByKey(obj, keyRegexes, excludeK...|
|`_pickDatetimeByKey`|fn||1095-1109|function _pickDatetimeByKey(obj, keyRegexes)|
|`_extractJsonMetricCandidates`|fn||1118-1204|function _extractJsonMetricCandidates(root)|
|`walk`|fn||1127-1200|function walk(node)|
|`_candidateScore`|fn||1212-1248|function _candidateScore(candidate, windowKey)|
|`_rankCandidates`|fn||1259-1267|function _rankCandidates(candidates, windowKey, index)|
|`_traceCandidate`|fn||1274-1288|function _traceCandidate(candidate)|
|`_pickCandidate`|fn||1297-1305|function _pickCandidate(candidates, windowKey, index)|
|`_inferQuotaFromFraction`|fn||1315-1345|function _inferQuotaFromFraction(fraction, usagePercent)|
|`_buildWindows`|fn||1358-1497|function _buildWindows(|
|`_extractSignals`|fn||1504-1530|function _extractSignals(html)|
|`_buildProviderPayload`|fn||1540-1560|function _buildProviderPayload(provider, windows, signals...|
|`providerPayloadHasUsableMetrics`|fn||1569-1581|export function providerPayloadHasUsableMetrics(payload)|
|`_sample`|fn||1589-1591|function _sample(values, maxItems)|
|`extractSignalDiagnostics`|fn||1598-1634|export function extractSignalDiagnostics(html)|
|`extractWindowAssignmentDiagnostics`|fn||1647-1691|export function extractWindowAssignmentDiagnostics(html, ...|
|`parseClaudeUsageHtml`|fn||1700-1711|export function parseClaudeUsageHtml(html)|
|`parseCodexUsageHtml`|fn||1720-1731|export function parseCodexUsageHtml(html)|
|`parseCopilotFeaturesHtml`|fn||1738-1754|export function parseCopilotFeaturesHtml(html)|
|`parseCopilotPremiumHtml`|fn||1761-1777|export function parseCopilotPremiumHtml(html)|
|`mergeCopilotPayloads`|fn||1788-1830|export function mergeCopilotPayloads(featuresPayload, pre...|


---

# popup.js | JavaScript | 535L | 22 symbols | 1 imports | 28 comments
> Path: `src/aibar/chrome-extension/popup.js`
- @brief Popup controller for rendering provider tabs and debug actions.
- @details Consumes normalized state emitted by background service-worker and renders
GNOME-parity card/progress visuals for Claude, Copilot, and Codex providers.
- @satisfies REQ-038
- @satisfies REQ-039
- @satisfies REQ-044
- @satisfies REQ-053
- @satisfies REQ-055
- @satisfies REQ-056

## Imports
```
import { createLogger } from "./debug.js";
```

## Definitions

- const `const PROVIDER_TABS = ["claude", "copilot", "codex"];` (L18)
- @brief Supported provider tab order. */
- const `const PROVIDER_WINDOWS = {` (L21)
- @brief Window render ordering by provider. */
### fn `function _applyDebugAccessState(enabled)` (L67-79)
- @brief Apply debug-access status to popup control interactivity.
- @details Ensures UI mirrors runtime debug guard by disabling debug-only actions
whenever the non-persistent debug flag is not enabled.
- @param {boolean} enabled Runtime debug-access state.
- @return s {void}
- @satisfies REQ-053

### fn `function _setDebugOutput(payload)` (L87-90)
- @brief Write compact debug command output payload in popup panel.
- @param {unknown} payload Debug command payload.
- @return s {void}
- @satisfies REQ-053

### fn `function _progressClass(usagePercent)` (L97-108)
- @brief Resolve CSS class for progress severity by percentage.
- @param {number | null} usagePercent Usage percentage value.
- @return s {string} CSS class name.

### fn `function _formatPercent(value)` (L115-120)
- @brief Format percentage for UI display.
- @param {number | null} value Percentage value.
- @return s {string} UI label.

### fn `function _formatMetric(value)` (L127-132)
- @brief Format numeric metric for UI display.
- @param {number | null} value Numeric metric.
- @return s {string} UI label.

### fn `function _formatReset(resetAt)` (L139-162)
- @brief Format reset timestamp into compact relative text.
- @param {string | null | undefined} resetAt ISO timestamp.
- @return s {string} Relative-time display label.

### fn `function _buildWindowRow(windowKey, windowData)` (L170-214)
- @brief Build one window progress-bar row element.
- @param {string} windowKey Window key (`5h`, `7d`, `30d`).
- @param {Record<string, number | string | null> | null} windowData Window data object.
- @return s {HTMLElement} Rendered row container.

### fn `function _hasPopulatedWindows(provider, windows)` (L227-245)
- @brief Test whether provider windows object contains any populated metric data.
- @details Iterates expected window keys for the provider and returns true when at
least one window entry contains a finite `usage_percent`, `remaining`, or `limit`
value.  Used to decide whether window progress bars should render alongside errors.
- @param {string} provider Provider key.
- @param {Record<string, unknown> | null | undefined} windows Windows data object from provider state.
- @return s {boolean} True when at least one window has a usable numeric metric.
- @satisfies REQ-055
- @satisfies REQ-056

### fn `function _renderProviderCard(provider)` (L257-292)
- @brief Render one provider card from current state.
- @details Hides window progress bars and quota elements when the provider has an
error and no prior populated window data (REQ-055).  Renders both windows and
error when prior window data persists (REQ-056).
- @param {string} provider Provider key.
- @return s {void}
- @satisfies REQ-055
- @satisfies REQ-056

### fn `function _renderState()` (L298-313)
- @brief Render popup-wide status/footer labels and all provider cards.
- @return s {void}

### fn `function _setActiveProvider(provider)` (L320-336)
- @brief Apply active tab classes and card visibility state.
- @param {string} provider Target provider.
- @return s {void}

### fn `async function _requestState()` (L342-349)
- @brief Request latest state from background service worker.
- @return s {Promise<void>} Completion promise.

### fn `async function _refreshNow()` (L355-362)
- @brief Trigger manual refresh request.
- @return s {Promise<void>} Completion promise.

### fn `async function _requestDebugAccessState()` (L370-376)
- @brief Fetch runtime debug-access configuration.
- @return s {Promise<void>} Completion promise.
- @satisfies REQ-052
- @satisfies REQ-053

### fn `async function _setDebugAccessState(enabled)` (L385-394)
- @brief Set runtime debug-access configuration.
- @param {boolean} enabled Desired debug-access state.
- @return s {Promise<void>} Completion promise.
- @satisfies REQ-052
- @satisfies REQ-053

### fn `async function _exportDebugBundle()` (L400-416)
- @brief Export debug bundle as downloadable JSON file.
- @return s {Promise<void>} Completion promise.

### fn `async function _clearLogs()` (L422-427)
- @brief Clear persisted debug logs.
- @return s {Promise<void>} Completion promise.

### fn `async function _setIntervalOverride()` (L433-443)
- @brief Apply refresh interval override from popup input.
- @return s {Promise<void>} Completion promise.

### fn `async function _fetchProviderPagesDiagnostics()` (L450-463)
- @brief Fetch required provider pages through debug API and render diagnostics.
- @return s {Promise<void>} Completion promise.
- @satisfies REQ-053

### fn `function _wireUiEvents()` (L469-517)
- @brief Register popup event handlers.
- @return s {void}

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`PROVIDER_TABS`|const||18||
|`PROVIDER_WINDOWS`|const||21||
|`_applyDebugAccessState`|fn||67-79|function _applyDebugAccessState(enabled)|
|`_setDebugOutput`|fn||87-90|function _setDebugOutput(payload)|
|`_progressClass`|fn||97-108|function _progressClass(usagePercent)|
|`_formatPercent`|fn||115-120|function _formatPercent(value)|
|`_formatMetric`|fn||127-132|function _formatMetric(value)|
|`_formatReset`|fn||139-162|function _formatReset(resetAt)|
|`_buildWindowRow`|fn||170-214|function _buildWindowRow(windowKey, windowData)|
|`_hasPopulatedWindows`|fn||227-245|function _hasPopulatedWindows(provider, windows)|
|`_renderProviderCard`|fn||257-292|function _renderProviderCard(provider)|
|`_renderState`|fn||298-313|function _renderState()|
|`_setActiveProvider`|fn||320-336|function _setActiveProvider(provider)|
|`_requestState`|fn||342-349|async function _requestState()|
|`_refreshNow`|fn||355-362|async function _refreshNow()|
|`_requestDebugAccessState`|fn||370-376|async function _requestDebugAccessState()|
|`_setDebugAccessState`|fn||385-394|async function _setDebugAccessState(enabled)|
|`_exportDebugBundle`|fn||400-416|async function _exportDebugBundle()|
|`_clearLogs`|fn||422-427|async function _clearLogs()|
|`_setIntervalOverride`|fn||433-443|async function _setIntervalOverride()|
|`_fetchProviderPagesDiagnostics`|fn||450-463|async function _fetchProviderPagesDiagnostics()|
|`_wireUiEvents`|fn||469-517|function _wireUiEvents()|


---

# extension.js | JavaScript | 1173L | 17 symbols | 8 imports | 27 comments
> Path: `src/aibar/gnome-extension/aibar@aibar.panel/extension.js`
- @brief GNOME Shell panel extension for aibar metrics.
- @details Collects usage JSON from the aibar CLI and renders provider-specific quota/cost cards in the GNOME panel popup.

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
```

## Definitions

- const `const REFRESH_INTERVAL_SECONDS = 300;` (L16)
- const `const ENV_FILE_PATH = GLib.get_home_dir() + '/.config/aibar/env';` (L17)
- const `const RESET_PENDING_MESSAGE = 'Starts when the first message is sent';` (L18)
- const `const RATE_LIMIT_ERROR_MESSAGE = 'Rate limited. Try again later.';` (L19)
### fn `function _getAiBarPath()` (L26-36)
- @brief Resolve aibar executable path.
- @details Prefers PATH discovery and falls back to AIBAR_PATH from the env file.
- @return s {string} Resolved executable path or fallback command name.

### fn `function _loadEnvFromFile()` (L43-95)
- @brief Load key-value environment variables from aibar env file.
- @details Parses export syntax, quoted values, and inline comments.
- @return s {Object<string,string>} Parsed environment map.

### fn `function _getProgressClass(pct)` (L102-108)
- @brief Map percentage usage to CSS progress severity class.
- @param {number} pct Usage percentage.
- @return s {string} CSS class suffix for progress state.

### fn `function _isDisplayedZeroPercent(pct)` (L117-124)
- @brief Check whether a percentage renders as `0.0%` in one-decimal UI output.
- @details Mirrors display rounding semantics so fallback reset text is shown when
usage is effectively zero from the user's perspective (e.g. internal 0.04 -> 0.0%).
- @param {number} pct Usage percentage candidate.
- @return s {boolean} True when value is finite, non-negative, and rounds to 0.0.

### fn `function _isDisplayedFullPercent(pct)` (L133-138)
- @brief Check whether a percentage renders as `100.0%` in one-decimal UI output.
- @details Mirrors display rounding semantics so near-full values are treated as
full usage for limit-reached warning rendering.
- @param {number} pct Usage percentage candidate.
- @return s {boolean} True when value is finite and rounds to `100.0`.

### class `class AIBarIndicator extends PanelMenu.Button` : PanelMenu.Button (L142-441)
- @brief Panel indicator widget that manages popup rendering and refresh lifecycle. */
- @brief Execute init.
- @details Applies init logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
- @return s {any} Function return value.

### fn `const createWindowBar = (labelText) =>` (L485-531)
- @brief Execute create provider card.
- @details Applies create provider card logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
- @param {any} providerName Input parameter `providerName`.
- @return s {any} Function return value.

### fn `const updateWindowBar = (bar, pct, resetTime, useDays) =>` (L640-698)
- @brief Execute populate provider card.
- @details Applies populate provider card logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
- @param {any} card Input parameter `card`.
- @param {any} providerName Input parameter `providerName`.
- @param {any} data Input parameter `data`.
- @return s {any} Function return value.

### fn `const setResetLabel = (baseText) =>` (L646-652)

### fn `const showResetPendingHint = () =>` (L663-665)

### fn `const toPercent = (value) =>` (L940-945)
- @brief Execute update u i.
- @details Applies update u i logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
- @return s {any} Function return value.

### fn `const getPanelUsageValues = (providerName, data) =>` (L947-1004)

### class `export default class AIBarExtension` (L1139-1173)
- @brief GNOME extension lifecycle adapter for AIBarIndicator registration. */
- @brief Execute constructor.
- @details Applies constructor logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
- @return s {any} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`REFRESH_INTERVAL_SECONDS`|const||16||
|`ENV_FILE_PATH`|const||17||
|`RESET_PENDING_MESSAGE`|const||18||
|`RATE_LIMIT_ERROR_MESSAGE`|const||19||
|`_getAiBarPath`|fn||26-36|function _getAiBarPath()|
|`_loadEnvFromFile`|fn||43-95|function _loadEnvFromFile()|
|`_getProgressClass`|fn||102-108|function _getProgressClass(pct)|
|`_isDisplayedZeroPercent`|fn||117-124|function _isDisplayedZeroPercent(pct)|
|`_isDisplayedFullPercent`|fn||133-138|function _isDisplayedFullPercent(pct)|
|`AIBarIndicator`|class||142-441|class AIBarIndicator extends PanelMenu.Button|
|`createWindowBar`|fn||485-531|const createWindowBar = (labelText) =>|
|`updateWindowBar`|fn||640-698|const updateWindowBar = (bar, pct, resetTime, useDays) =>|
|`setResetLabel`|fn||646-652|const setResetLabel = (baseText) =>|
|`showResetPendingHint`|fn||663-665|const showResetPendingHint = () =>|
|`toPercent`|fn||940-945|const toPercent = (value) =>|
|`getPanelUsageValues`|fn||947-1004|const getPanelUsageValues = (providerName, data) =>|
|`AIBarExtension`|class||1139-1173|export default class AIBarExtension|

