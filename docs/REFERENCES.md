# Files Structure
```
.
└── src
    └── aibar
        ├── aibar
        │   ├── __init__.py
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
        └── extension
            └── aibar@aibar.panel
                ├── dev.sh
                └── extension.js
```

# __init__.py | Python | 7L | 0 symbols | 0 imports | 1 comments
> Path: `src/aibar/aibar/__init__.py`
- @brief Package metadata for aibar.
- @details Exposes the package version for the multi-provider usage monitoring application.


---

# cache.py | Python | 256L | 18 symbols | 7 imports | 24 comments
> Path: `src/aibar/aibar/cache.py`
- @brief Provider result caching primitives.
- @details Implements in-memory and disk cache entries, TTL invalidation, and raw-payload sanitization for provider metrics.

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
- @details Encapsulates result cache state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `DEFAULT_TTL = 120  # 2 minutes` (L45)
  - @brief Define result cache component.
  - @details Encapsulates result cache state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `PROVIDER_TTLS =` (L46)
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
- fn `def get(self, provider: ProviderName, window: WindowPeriod) -> ProviderResult | None` (L102-120)
  - @brief Execute get.
  - @details Applies get logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @param window {WindowPeriod} Input parameter `window`.
  - @return {ProviderResult | None} Function return value.
- fn `def set(self, result: ProviderResult) -> None` (L121-141)
  - @brief Execute set.
  - @details Applies set logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param result {ProviderResult} Input parameter `result`.
  - @return {None} Function return value.
- fn `def get_last_good(self, provider: ProviderName, window: WindowPeriod) -> ProviderResult | None` (L142-151)
  - @brief Execute get last good.
  - @details Applies get last good logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName} Input parameter `provider`.
  - @param window {WindowPeriod} Input parameter `window`.
  - @return {ProviderResult | None} Function return value.
- fn `def invalidate(` (L152-153)
- fn `def _save_to_disk(self, result: ProviderResult) -> None` `priv` (L176-194)
  - @brief Execute invalidate.
  - @brief Execute save to disk.
  - @details Applies invalidate logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @details Applies save to disk logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param provider {ProviderName | None} Input parameter `provider`.
  - @param window {WindowPeriod | None} Input parameter `window`.
  - @param result {ProviderResult} Input parameter `result`.
  - @return {None} Function return value.
  - @return {None} Function return value.
- fn `def _load_from_disk(` `priv` (L195-199)

### fn `def _sanitize_raw(self, raw: dict[str, Any]) -> dict[str, Any]` `priv` (L231-256)
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

### fn `def clean(obj: Any) -> Any` (L240-255)
- @brief Execute clean.
- @details Applies clean logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param obj {Any} Input parameter `obj`.
- @return {Any} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`CacheEntry`|class|pub|18-38|class CacheEntry(BaseModel)|
|`CacheEntry.is_expired`|fn|pub|28-38|def is_expired(self) -> bool|
|`ResultCache`|class|pub|39-238|class ResultCache|
|`ResultCache.DEFAULT_TTL`|var|pub|45||
|`ResultCache.PROVIDER_TTLS`|var|pub|46||
|`ResultCache.__init__`|fn|priv|53-63|def __init__(self, cache_dir: Path | None = None) -> None|
|`ResultCache._default_cache_dir`|fn|priv|64-73|def _default_cache_dir(self) -> Path|
|`ResultCache._ensure_cache_dir`|fn|priv|74-81|def _ensure_cache_dir(self) -> None|
|`ResultCache._cache_key`|fn|priv|82-91|def _cache_key(self, provider: ProviderName, window: Wind...|
|`ResultCache._disk_path`|fn|priv|92-101|def _disk_path(self, provider: ProviderName, window: Wind...|
|`ResultCache.get`|fn|pub|102-120|def get(self, provider: ProviderName, window: WindowPerio...|
|`ResultCache.set`|fn|pub|121-141|def set(self, result: ProviderResult) -> None|
|`ResultCache.get_last_good`|fn|pub|142-151|def get_last_good(self, provider: ProviderName, window: W...|
|`ResultCache.invalidate`|fn|pub|152-153|def invalidate(|
|`ResultCache._save_to_disk`|fn|priv|176-194|def _save_to_disk(self, result: ProviderResult) -> None|
|`ResultCache._load_from_disk`|fn|priv|195-199|def _load_from_disk(|
|`_sanitize_raw`|fn|priv|231-256|def _sanitize_raw(self, raw: dict[str, Any]) -> dict[str,...|
|`clean`|fn|pub|240-255|def clean(obj: Any) -> Any|


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

# cli.py | Python | 533L | 16 symbols | 13 imports | 34 comments
> Path: `src/aibar/aibar/cli.py`
- @brief Command-line interface for aibar.
- @details Defines command parsing, provider dispatch, formatted output, setup helpers, login flows, and UI launch hooks.

## Imports
```
import asyncio
import json
import sys
import click
from click.core import ParameterSource
from aibar.config import config
from aibar.providers import (
from aibar.providers.base import BaseProvider, ProviderError, ProviderName, WindowPeriod
from datetime import datetime, timezone
from aibar.ui import run_ui
from aibar.config import ENV_FILE_PATH, write_env_file
from aibar.claude_cli_auth import ClaudeCLIAuth
from aibar.providers.copilot import CopilotProvider
```

## Definitions

### fn `def get_providers() -> dict[ProviderName, BaseProvider]` (L25-39)
- @brief Execute get providers.
- @details Applies get providers logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {dict[ProviderName, BaseProvider]} Function return value.

### fn `def parse_window(window: str) -> WindowPeriod` (L40-57)
- @brief Execute parse window.
- @details Applies parse window logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {str} Input parameter `window`.
- @return {WindowPeriod} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def parse_provider(provider: str) -> ProviderName | None` (L58-74)
- @brief Execute parse provider.
- @details Applies parse provider logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param provider {str} Input parameter `provider`.
- @return {ProviderName | None} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _fetch_result(provider: BaseProvider, window: WindowPeriod)` `priv` (L75-90)
- @brief Execute fetch result.
- @details Applies fetch result logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param provider {BaseProvider} Input parameter `provider`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {None} Function return value.

### fn `def main() -> None` `@click.version_option()` (L93-101)
- @brief Execute main.
- @details Applies main logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def show(provider: str, window: str, output_json: bool) -> None` (L121-176)
- @brief Execute show.
- @details Applies show logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param provider {str} Input parameter `provider`.
- @param window {str} Input parameter `window`.
- @param output_json {bool} Input parameter `output_json`.
- @return {None} Function return value.

### fn `def _print_result(name: ProviderName, result, label: str | None = None) -> None` `priv` (L177-235)
- @brief Execute print result.
- @details Applies print result logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param name {ProviderName} Input parameter `name`.
- @param result {None} Input parameter `result`.
- @param label {str | None} Input parameter `label`.
- @return {None} Function return value.

### fn `def _format_reset_duration(seconds: float) -> str` `priv` (L236-251)
- @brief Execute format reset duration.
- @details Applies format reset duration logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param seconds {float} Input parameter `seconds`.
- @return {str} Function return value.

### fn `def _progress_bar(percent: float, width: int = 20) -> str` `priv` (L252-264)
- @brief Execute progress bar.
- @details Applies progress bar logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param percent {float} Input parameter `percent`.
- @param width {int} Input parameter `width`.
- @return {str} Function return value.

### fn `def doctor() -> None` `@main.command()` (L266-316)
- @brief Execute doctor.
- @details Applies doctor logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def ui() -> None` `@main.command()` (L318-328)
- @brief Execute ui.
- @details Applies ui logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def env() -> None` `@main.command()` (L330-338)
- @brief Execute env.
- @details Applies env logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def setup() -> None` `@main.command()` (L340-430)
- @brief Execute setup.
- @details Applies setup logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def login(provider: str) -> None` (L438-454)
- @brief Execute login.
- @details Applies login logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param provider {str} Input parameter `provider`.
- @return {None} Function return value.

### fn `def _login_claude() -> None` `priv` (L455-503)
- @brief Execute login claude.
- @details Applies login claude logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def _login_copilot() -> None` `priv` (L504-531)
- @brief Execute login copilot.
- @details Applies login copilot logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`get_providers`|fn|pub|25-39|def get_providers() -> dict[ProviderName, BaseProvider]|
|`parse_window`|fn|pub|40-57|def parse_window(window: str) -> WindowPeriod|
|`parse_provider`|fn|pub|58-74|def parse_provider(provider: str) -> ProviderName | None|
|`_fetch_result`|fn|priv|75-90|def _fetch_result(provider: BaseProvider, window: WindowP...|
|`main`|fn|pub|93-101|def main() -> None|
|`show`|fn|pub|121-176|def show(provider: str, window: str, output_json: bool) -...|
|`_print_result`|fn|priv|177-235|def _print_result(name: ProviderName, result, label: str ...|
|`_format_reset_duration`|fn|priv|236-251|def _format_reset_duration(seconds: float) -> str|
|`_progress_bar`|fn|priv|252-264|def _progress_bar(percent: float, width: int = 20) -> str|
|`doctor`|fn|pub|266-316|def doctor() -> None|
|`ui`|fn|pub|318-328|def ui() -> None|
|`env`|fn|pub|330-338|def env() -> None|
|`setup`|fn|pub|340-430|def setup() -> None|
|`login`|fn|pub|438-454|def login(provider: str) -> None|
|`_login_claude`|fn|priv|455-503|def _login_claude() -> None|
|`_login_copilot`|fn|priv|504-531|def _login_copilot() -> None|


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

# claude_oauth.py | Python | 186L | 8 symbols | 5 imports | 13 comments
> Path: `src/aibar/aibar/providers/claude_oauth.py`
- @brief Claude OAuth usage provider.
- @details Fetches Claude subscription utilization through OAuth credentials and normalizes provider quota state into the shared result contract.

## Imports
```
import os
from datetime import datetime
import httpx
from aibar.claude_cli_auth import extract_claude_cli_token
from aibar.providers.base import (
```

## Definitions

### class `class ClaudeOAuthProvider(BaseProvider)` : BaseProvider (L24-58)
- @brief Define claude o auth provider component.
- @details Encapsulates claude o auth provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `USAGE_URL = "https://api.anthropic.com/api/oauth/usage"` (L31)
  - @brief Define claude o auth provider component.
  - @details Encapsulates claude o auth provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `TOKEN_ENV_VAR = "CLAUDE_CODE_OAUTH_TOKEN"` (L32)
- fn `def __init__(self, token: str | None = None) -> None` `priv` (L34-42)
  - @brief Execute init.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param token {str | None} Input parameter `token`.
  - @return {None} Function return value.
- fn `def is_configured(self) -> bool` (L43-50)
  - @brief Execute is configured.
  - @details Applies is configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {bool} Function return value.
- fn `def get_config_help(self) -> str` (L51-58)
  - @brief Execute get config help.
  - @details Applies get config help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {str} Function return value.

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L65-139)
- @brief Execute fetch.
- @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.
- @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L140-186)
- @brief Execute parse response.
- @details Applies parse response logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param data {dict} Input parameter `data`.
- @param window {WindowPeriod} Input parameter `window`.
- @return {ProviderResult} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`ClaudeOAuthProvider`|class|pub|24-58|class ClaudeOAuthProvider(BaseProvider)|
|`ClaudeOAuthProvider.USAGE_URL`|var|pub|31||
|`ClaudeOAuthProvider.TOKEN_ENV_VAR`|var|pub|32||
|`ClaudeOAuthProvider.__init__`|fn|priv|34-42|def __init__(self, token: str | None = None) -> None|
|`ClaudeOAuthProvider.is_configured`|fn|pub|43-50|def is_configured(self) -> bool|
|`ClaudeOAuthProvider.get_config_help`|fn|pub|51-58|def get_config_help(self) -> str|
|`fetch`|fn|pub|65-139|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|140-186|def _parse_response(self, data: dict, window: WindowPerio...|


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

# ui.py | Python | 633L | 27 symbols | 12 imports | 40 comments
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

### fn `def watch_result(self, result: ProviderResult | None) -> None` (L162-251)
- @brief Execute watch result.
- @details Applies watch result logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param result {ProviderResult | None} Input parameter `result`.
- @return {None} Function return value.

### fn `def watch_is_loading(self, loading: bool) -> None` (L252-264)
- @brief Execute watch is loading.
- @details Applies watch is loading logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param loading {bool} Input parameter `loading`.
- @return {None} Function return value.

### fn `def _format_age(self, seconds: float) -> str` `priv` (L265-278)
- @brief Execute format age.
- @details Applies format age logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param seconds {float} Input parameter `seconds`.
- @return {str} Function return value.

### fn `def _format_duration(self, seconds: float) -> str` `priv` (L279-298)
- @brief Execute format duration.
- @details Applies format duration logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param seconds {float} Input parameter `seconds`.
- @return {str} Function return value.

### class `class RawJsonView(Static)` : Static (L299-346)
- @brief Define raw json view component.
- @details Encapsulates raw json view state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- fn `def compose(self) -> ComposeResult` (L321-331)
  - @brief Define raw json view component.
  - @brief Execute compose.
  - @details Encapsulates raw json view state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
  - @details Applies compose logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {ComposeResult} Function return value.
- fn `def watch_data(self, data: dict | None) -> None` (L332-346)
  - @brief Execute watch data.
  - @details Applies watch data logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @param data {dict | None} Input parameter `data`.
  - @return {None} Function return value.

### class `class AIBarUI(App)` : App (L347-546)
- @brief Define a i bar u i component.
- @details Encapsulates a i bar u i state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
- var `BINDINGS = [` (L407)
- var `TITLE = "Usage Metrics UI"` (L415)
- fn `def __init__(self) -> None` `priv` (L420-436)
  - @brief Execute init.
  - @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {None} Function return value.
- fn `def compose(self) -> ComposeResult` (L437-464)
  - @brief Execute compose.
  - @details Applies compose logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {ComposeResult} Function return value.
- fn `async def on_mount(self) -> None` (L465-473)
  - @brief Execute on mount.
  - @details Applies on mount logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {None} Function return value.
- fn `async def on_refresh_pressed(self) -> None` (L475-482)
  - @brief Execute on refresh pressed.
  - @details Applies on refresh pressed logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {None} Function return value.
- fn `async def on_5h_pressed(self) -> None` (L484-491)
  - @brief Execute on 5h pressed.
  - @details Applies on 5h pressed logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {None} Function return value.
- fn `async def on_7d_pressed(self) -> None` (L493-500)
  - @brief Execute on 7d pressed.
  - @details Applies on 7d pressed logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {None} Function return value.
- fn `async def action_refresh(self) -> None` (L501-539)
  - @brief Execute action refresh.
  - @details Applies action refresh logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
  - @return {None} Function return value.

### fn `async def action_window_5h(self) -> None` (L540-550)
- @brief Execute action window 5h.
- @details Applies action window 5h logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `async def action_window_7d(self) -> None` (L551-561)
- @brief Execute action window 7d.
- @details Applies action window 7d logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `async def action_toggle_json(self) -> None` (L562-574)
- @brief Execute action toggle json.
- @details Applies action toggle json logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def _get_card(self, provider: ProviderName) -> ProviderCard | None` `priv` (L575-587)
- @brief Execute get card.
- @details Applies get card logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @param provider {ProviderName} Input parameter `provider`.
- @return {ProviderCard | None} Function return value.

### fn `def _update_window_buttons(self) -> None` `priv` (L588-607)
- @brief Execute update window buttons.
- @details Applies update window buttons logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def _update_json_view(self) -> None` `priv` (L608-621)
- @brief Execute update json view.
- @details Applies update json view logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

### fn `def run_ui() -> None` (L622-631)
- @brief Execute run ui.
- @details Applies run ui logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
- @return {None} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`ProviderCard`|class|pub|45-244|class ProviderCard(Static)|
|`ProviderCard.__init__`|fn|priv|122-125|def __init__(|
|`ProviderCard.compose`|fn|pub|138-161|def compose(self) -> ComposeResult|
|`watch_result`|fn|pub|162-251|def watch_result(self, result: ProviderResult | None) -> ...|
|`watch_is_loading`|fn|pub|252-264|def watch_is_loading(self, loading: bool) -> None|
|`_format_age`|fn|priv|265-278|def _format_age(self, seconds: float) -> str|
|`_format_duration`|fn|priv|279-298|def _format_duration(self, seconds: float) -> str|
|`RawJsonView`|class|pub|299-346|class RawJsonView(Static)|
|`RawJsonView.compose`|fn|pub|321-331|def compose(self) -> ComposeResult|
|`RawJsonView.watch_data`|fn|pub|332-346|def watch_data(self, data: dict | None) -> None|
|`AIBarUI`|class|pub|347-546|class AIBarUI(App)|
|`AIBarUI.BINDINGS`|var|pub|407||
|`AIBarUI.TITLE`|var|pub|415||
|`AIBarUI.__init__`|fn|priv|420-436|def __init__(self) -> None|
|`AIBarUI.compose`|fn|pub|437-464|def compose(self) -> ComposeResult|
|`AIBarUI.on_mount`|fn|pub|465-473|async def on_mount(self) -> None|
|`AIBarUI.on_refresh_pressed`|fn|pub|475-482|async def on_refresh_pressed(self) -> None|
|`AIBarUI.on_5h_pressed`|fn|pub|484-491|async def on_5h_pressed(self) -> None|
|`AIBarUI.on_7d_pressed`|fn|pub|493-500|async def on_7d_pressed(self) -> None|
|`AIBarUI.action_refresh`|fn|pub|501-539|async def action_refresh(self) -> None|
|`action_window_5h`|fn|pub|540-550|async def action_window_5h(self) -> None|
|`action_window_7d`|fn|pub|551-561|async def action_window_7d(self) -> None|
|`action_toggle_json`|fn|pub|562-574|async def action_toggle_json(self) -> None|
|`_get_card`|fn|priv|575-587|def _get_card(self, provider: ProviderName) -> ProviderCa...|
|`_update_window_buttons`|fn|priv|588-607|def _update_window_buttons(self) -> None|
|`_update_json_view`|fn|priv|608-621|def _update_json_view(self) -> None|
|`run_ui`|fn|pub|622-631|def run_ui() -> None|


---

# dev.sh | Shell | 34L | 1 symbols | 0 imports | 4 comments
> Path: `src/aibar/extension/aibar@aibar.panel/dev.sh`

## Definitions

- var `EXT_UUID="aibar@aibar.panel"` (L6)
- @brief Development helper commands for aibar GNOME extension.
- @details Wraps nested-shell start, enable/disable/reload, and log tail commands for local extension workflows with fixed 1024x800 nested-shell resolution.
## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`EXT_UUID`|var||6||


---

# extension.js | JavaScript | 1013L | 10 symbols | 8 imports | 24 comments
> Path: `src/aibar/extension/aibar@aibar.panel/extension.js`
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
### fn `function _getAiBarPath()` (L24-34)
- @brief Resolve aibar executable path.
- @details Prefers PATH discovery and falls back to AIBAR_PATH from the env file.
- @return s {string} Resolved executable path or fallback command name.

### fn `function _loadEnvFromFile()` (L41-93)
- @brief Load key-value environment variables from aibar env file.
- @details Parses export syntax, quoted values, and inline comments.
- @return s {Object<string,string>} Parsed environment map.

### fn `function _getProgressClass(pct)` (L100-106)
- @brief Map percentage usage to CSS progress severity class.
- @param {number} pct Usage percentage.
- @return s {string} CSS class suffix for progress state.

### class `class AIBarIndicator extends PanelMenu.Button` : PanelMenu.Button (L110-409)
- @brief Panel indicator widget that manages popup rendering and refresh lifecycle. */
- @brief Execute init.
- @details Applies init logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
- @return s {any} Function return value.

### fn `const createWindowBar = (labelText) =>` (L391-437)
- @brief Execute create provider card.
- @details Applies create provider card logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
- @param {any} providerName Input parameter `providerName`.
- @return s {any} Function return value.

### fn `const updateWindowBar = (bar, pct, resetTime, useDays) =>` (L540-581)
- @brief Execute populate provider card.
- @details Applies populate provider card logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
- @param {any} card Input parameter `card`.
- @param {any} providerName Input parameter `providerName`.
- @param {any} data Input parameter `data`.
- @return s {any} Function return value.

### fn `const getPanelUsagePercent = (providerName, data) =>` (L821-859)
- @brief Execute update u i.
- @details Applies update u i logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
- @return s {any} Function return value.

### class `export default class AIBarExtension` (L979-1013)
- @brief GNOME extension lifecycle adapter for AIBarIndicator registration. */
- @brief Execute constructor.
- @details Applies constructor logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
- @return s {any} Function return value.

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`REFRESH_INTERVAL_SECONDS`|const||16||
|`ENV_FILE_PATH`|const||17||
|`_getAiBarPath`|fn||24-34|function _getAiBarPath()|
|`_loadEnvFromFile`|fn||41-93|function _loadEnvFromFile()|
|`_getProgressClass`|fn||100-106|function _getProgressClass(pct)|
|`AIBarIndicator`|class||110-409|class AIBarIndicator extends PanelMenu.Button|
|`createWindowBar`|fn||391-437|const createWindowBar = (labelText) =>|
|`updateWindowBar`|fn||540-581|const updateWindowBar = (bar, pct, resetTime, useDays) =>|
|`getPanelUsagePercent`|fn||821-859|const getPanelUsagePercent = (providerName, data) =>|
|`AIBarExtension`|class||979-1013|export default class AIBarExtension|

