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

# cache.py | Python | 206L | 18 symbols | 7 imports | 23 comments
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

### class `class CacheEntry(BaseModel)` : BaseModel (L18-31)
- fn `def is_expired(self) -> bool` (L25-31)

### class `class ResultCache` (L32-206)
- var `DEFAULT_TTL = 120  # 2 minutes` (L42)
- var `PROVIDER_TTLS =` (L43)
- fn `def __init__(self, cache_dir: Path | None = None) -> None` `priv` (L50-61)
- fn `def _default_cache_dir(self) -> Path` `priv` (L62-67)
- fn `def _ensure_cache_dir(self) -> None` `priv` (L68-71)
- fn `def _cache_key(self, provider: ProviderName, window: WindowPeriod) -> str` `priv` (L72-75)
- fn `def _disk_path(self, provider: ProviderName, window: WindowPeriod) -> Path` `priv` (L76-79)
- fn `def get(self, provider: ProviderName, window: WindowPeriod) -> ProviderResult | None` (L80-96)
- fn `def set(self, result: ProviderResult) -> None` (L97-116)
- fn `def get_last_good(self, provider: ProviderName, window: WindowPeriod) -> ProviderResult | None` (L117-124)
- fn `def invalidate(` (L125-126)
- fn `def _save_to_disk(self, result: ProviderResult) -> None` `priv` (L149-162)
- fn `def _load_from_disk(` `priv` (L163-167)
- fn `def _sanitize_raw(self, raw: dict[str, Any]) -> dict[str, Any]` `priv` (L192-206)
- fn `def clean(obj: Any) -> Any` (L196-205)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`CacheEntry`|class|pub|18-31|class CacheEntry(BaseModel)|
|`CacheEntry.is_expired`|fn|pub|25-31|def is_expired(self) -> bool|
|`ResultCache`|class|pub|32-206|class ResultCache|
|`ResultCache.DEFAULT_TTL`|var|pub|42||
|`ResultCache.PROVIDER_TTLS`|var|pub|43||
|`ResultCache.__init__`|fn|priv|50-61|def __init__(self, cache_dir: Path | None = None) -> None|
|`ResultCache._default_cache_dir`|fn|priv|62-67|def _default_cache_dir(self) -> Path|
|`ResultCache._ensure_cache_dir`|fn|priv|68-71|def _ensure_cache_dir(self) -> None|
|`ResultCache._cache_key`|fn|priv|72-75|def _cache_key(self, provider: ProviderName, window: Wind...|
|`ResultCache._disk_path`|fn|priv|76-79|def _disk_path(self, provider: ProviderName, window: Wind...|
|`ResultCache.get`|fn|pub|80-96|def get(self, provider: ProviderName, window: WindowPerio...|
|`ResultCache.set`|fn|pub|97-116|def set(self, result: ProviderResult) -> None|
|`ResultCache.get_last_good`|fn|pub|117-124|def get_last_good(self, provider: ProviderName, window: W...|
|`ResultCache.invalidate`|fn|pub|125-126|def invalidate(|
|`ResultCache._save_to_disk`|fn|priv|149-162|def _save_to_disk(self, result: ProviderResult) -> None|
|`ResultCache._load_from_disk`|fn|priv|163-167|def _load_from_disk(|
|`ResultCache._sanitize_raw`|fn|priv|192-206|def _sanitize_raw(self, raw: dict[str, Any]) -> dict[str,...|
|`ResultCache.clean`|fn|pub|196-205|def clean(obj: Any) -> Any|


---

# claude_cli_auth.py | Python | 118L | 9 symbols | 4 imports | 11 comments
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

### class `class ClaudeCLIAuth` (L13-109)
- var `DEFAULT_CREDS_PATH = Path.home() / ".claude" / ".credentials.json"` (L22)
- fn `def __init__(self, creds_path: Path | None = None) -> None` `priv` (L24-32)
- fn `def is_available(self) -> bool` (L33-36)
- fn `def get_credentials(self) -> dict[str, Any] | None` (L37-52)
- fn `def get_access_token(self) -> str | None` (L53-57)
- fn `def is_token_expired(self) -> bool` (L58-71)
- fn `def get_token_info(self) -> dict[str, Any]` (L72-109)

### fn `def extract_claude_cli_token() -> str | None` (L110-118)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`ClaudeCLIAuth`|class|pub|13-109|class ClaudeCLIAuth|
|`ClaudeCLIAuth.DEFAULT_CREDS_PATH`|var|pub|22||
|`ClaudeCLIAuth.__init__`|fn|priv|24-32|def __init__(self, creds_path: Path | None = None) -> None|
|`ClaudeCLIAuth.is_available`|fn|pub|33-36|def is_available(self) -> bool|
|`ClaudeCLIAuth.get_credentials`|fn|pub|37-52|def get_credentials(self) -> dict[str, Any] | None|
|`ClaudeCLIAuth.get_access_token`|fn|pub|53-57|def get_access_token(self) -> str | None|
|`ClaudeCLIAuth.is_token_expired`|fn|pub|58-71|def is_token_expired(self) -> bool|
|`ClaudeCLIAuth.get_token_info`|fn|pub|72-109|def get_token_info(self) -> dict[str, Any]|
|`extract_claude_cli_token`|fn|pub|110-118|def extract_claude_cli_token() -> str | None|


---

# cli.py | Python | 442L | 15 symbols | 13 imports | 33 comments
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

### fn `def get_providers() -> dict[ProviderName, BaseProvider]` (L25-35)

### fn `def parse_window(window: str) -> WindowPeriod` (L36-47)

### fn `def parse_provider(provider: str) -> ProviderName | None` (L48-58)

### fn `def _fetch_result(provider: BaseProvider, window: WindowPeriod)` `priv` (L59-68)

### fn `def main() -> None` `@click.version_option()` (L71-75)

### fn `def show(provider: str, window: str, output_json: bool) -> None` (L95-143)

### fn `def _print_result(name: ProviderName, result, label: str | None = None) -> None` `priv` (L144-190)

### fn `def _progress_bar(percent: float, width: int = 20) -> str` `priv` (L191-197)

### fn `def doctor() -> None` `@main.command()` (L199-245)

### fn `def ui() -> None` `@main.command()` (L247-253)

### fn `def env() -> None` `@main.command()` (L255-259)

### fn `def setup() -> None` `@main.command()` (L261-347)

### fn `def login(provider: str) -> None` (L355-371)

### fn `def _login_claude() -> None` `priv` (L372-416)

### fn `def _login_copilot() -> None` `priv` (L417-440)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`get_providers`|fn|pub|25-35|def get_providers() -> dict[ProviderName, BaseProvider]|
|`parse_window`|fn|pub|36-47|def parse_window(window: str) -> WindowPeriod|
|`parse_provider`|fn|pub|48-58|def parse_provider(provider: str) -> ProviderName | None|
|`_fetch_result`|fn|priv|59-68|def _fetch_result(provider: BaseProvider, window: WindowP...|
|`main`|fn|pub|71-75|def main() -> None|
|`show`|fn|pub|95-143|def show(provider: str, window: str, output_json: bool) -...|
|`_print_result`|fn|priv|144-190|def _print_result(name: ProviderName, result, label: str ...|
|`_progress_bar`|fn|priv|191-197|def _progress_bar(percent: float, width: int = 20) -> str|
|`doctor`|fn|pub|199-245|def doctor() -> None|
|`ui`|fn|pub|247-253|def ui() -> None|
|`env`|fn|pub|255-259|def env() -> None|
|`setup`|fn|pub|261-347|def setup() -> None|
|`login`|fn|pub|355-371|def login(provider: str) -> None|
|`_login_claude`|fn|priv|372-416|def _login_claude() -> None|
|`_login_copilot`|fn|priv|417-440|def _login_copilot() -> None|


---

# config.py | Python | 233L | 12 symbols | 8 imports | 19 comments
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
### fn `def load_env_file() -> dict[str, str]` (L18-32)

### fn `def write_env_file(updates: dict[str, str]) -> None` (L33-67)

### class `class Config` (L68-231)
- var `ENV_VARS =` (L77)
- var `PROVIDER_INFO =` (L86)
- fn `def get_token(self, provider: ProviderName) -> str | None` (L119-155)
- fn `def is_provider_configured(self, provider: ProviderName) -> bool` (L156-184)
- fn `def get_provider_status(self, provider: ProviderName) -> dict[str, Any]` (L185-201)
- fn `def get_all_provider_status(self) -> list[dict[str, Any]]` (L202-205)
- fn `def _get_token_preview(self, provider: ProviderName) -> str | None` `priv` (L206-212)
- fn `def get_env_var_help(self) -> str` (L213-231)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`ENV_FILE_PATH`|var|pub|15||
|`load_env_file`|fn|pub|18-32|def load_env_file() -> dict[str, str]|
|`write_env_file`|fn|pub|33-67|def write_env_file(updates: dict[str, str]) -> None|
|`Config`|class|pub|68-231|class Config|
|`Config.ENV_VARS`|var|pub|77||
|`Config.PROVIDER_INFO`|var|pub|86||
|`Config.get_token`|fn|pub|119-155|def get_token(self, provider: ProviderName) -> str | None|
|`Config.is_provider_configured`|fn|pub|156-184|def is_provider_configured(self, provider: ProviderName) ...|
|`Config.get_provider_status`|fn|pub|185-201|def get_provider_status(self, provider: ProviderName) -> ...|
|`Config.get_all_provider_status`|fn|pub|202-205|def get_all_provider_status(self) -> list[dict[str, Any]]|
|`Config._get_token_preview`|fn|priv|206-212|def _get_token_preview(self, provider: ProviderName) -> s...|
|`Config.get_env_var_help`|fn|pub|213-231|def get_env_var_help(self) -> str|


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

# base.py | Python | 147L | 23 symbols | 5 imports | 16 comments
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

### class `class WindowPeriod(str, Enum)` : str, Enum (L15-22)
- var `HOUR_5 = "5h"` (L18)
- var `DAY_7 = "7d"` (L19)
- var `DAY_30 = "30d"` (L20)

### class `class ProviderName(str, Enum)` : str, Enum (L23-32)
- var `CLAUDE = "claude"` (L26)
- var `OPENAI = "openai"` (L27)
- var `OPENROUTER = "openrouter"` (L28)
- var `COPILOT = "copilot"` (L29)
- var `CODEX = "codex"` (L30)

### class `class UsageMetrics(BaseModel)` : BaseModel (L33-60)
- fn `def usage_percent(self) -> float | None` (L45-52)
- fn `def total_tokens(self) -> int | None` (L54-60)

### class `class ProviderResult(BaseModel)` : BaseModel (L61-76)
- fn `def is_error(self) -> bool` (L72-76)

### class `class ProviderError(Exception)` : Exception (L77-82)

### class `class AuthenticationError(ProviderError)` : ProviderError (L83-88)

### class `class RateLimitError(ProviderError)` : ProviderError (L89-94)

### class `class BaseProvider(ABC)` : ABC (L95-147)
- fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L101-116)
- fn `def is_configured(self) -> bool` (L118-126)
- fn `def get_config_help(self) -> str` (L128-136)
- fn `def _make_error_result(` `priv` (L137-138)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`WindowPeriod`|class|pub|15-22|class WindowPeriod(str, Enum)|
|`WindowPeriod.HOUR_5`|var|pub|18||
|`WindowPeriod.DAY_7`|var|pub|19||
|`WindowPeriod.DAY_30`|var|pub|20||
|`ProviderName`|class|pub|23-32|class ProviderName(str, Enum)|
|`ProviderName.CLAUDE`|var|pub|26||
|`ProviderName.OPENAI`|var|pub|27||
|`ProviderName.OPENROUTER`|var|pub|28||
|`ProviderName.COPILOT`|var|pub|29||
|`ProviderName.CODEX`|var|pub|30||
|`UsageMetrics`|class|pub|33-60|class UsageMetrics(BaseModel)|
|`UsageMetrics.usage_percent`|fn|pub|45-52|def usage_percent(self) -> float | None|
|`UsageMetrics.total_tokens`|fn|pub|54-60|def total_tokens(self) -> int | None|
|`ProviderResult`|class|pub|61-76|class ProviderResult(BaseModel)|
|`ProviderResult.is_error`|fn|pub|72-76|def is_error(self) -> bool|
|`ProviderError`|class|pub|77-82|class ProviderError(Exception)|
|`AuthenticationError`|class|pub|83-88|class AuthenticationError(ProviderError)|
|`RateLimitError`|class|pub|89-94|class RateLimitError(ProviderError)|
|`BaseProvider`|class|pub|95-147|class BaseProvider(ABC)|
|`BaseProvider.fetch`|fn|pub|101-116|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`BaseProvider.is_configured`|fn|pub|118-126|def is_configured(self) -> bool|
|`BaseProvider.get_config_help`|fn|pub|128-136|def get_config_help(self) -> str|
|`BaseProvider._make_error_result`|fn|priv|137-138|def _make_error_result(|


---

# claude_oauth.py | Python | 190L | 8 symbols | 5 imports | 13 comments
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
- var `USAGE_URL = "https://api.anthropic.com/api/oauth/usage"` (L38)
- var `TOKEN_ENV_VAR = "CLAUDE_CODE_OAUTH_TOKEN"` (L39)
- fn `def __init__(self, token: str | None = None) -> None` `priv` (L41-50)
- fn `def is_configured(self) -> bool` (L51-54)
- fn `def get_config_help(self) -> str` (L55-58)

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L65-138)

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L139-190)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`ClaudeOAuthProvider`|class|pub|24-58|class ClaudeOAuthProvider(BaseProvider)|
|`ClaudeOAuthProvider.USAGE_URL`|var|pub|38||
|`ClaudeOAuthProvider.TOKEN_ENV_VAR`|var|pub|39||
|`ClaudeOAuthProvider.__init__`|fn|priv|41-50|def __init__(self, token: str | None = None) -> None|
|`ClaudeOAuthProvider.is_configured`|fn|pub|51-54|def is_configured(self) -> bool|
|`ClaudeOAuthProvider.get_config_help`|fn|pub|55-58|def get_config_help(self) -> str|
|`fetch`|fn|pub|65-138|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|139-190|def _parse_response(self, data: dict, window: WindowPerio...|


---

# codex.py | Python | 398L | 21 symbols | 6 imports | 31 comments
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

### class `class CodexCredentials` (L24-73)
- fn `def __init__(` `priv` (L31-37)
- fn `def needs_refresh(self) -> bool` (L45-51)
- fn `def from_auth_json(cls, data: dict) -> "CodexCredentials"` (L53-73)

### class `class CodexCredentialStore` (L74-146)
- fn `def codex_home(self) -> Path` (L80-85)
- fn `def auth_file(self) -> Path` (L87-90)
- fn `def load(self) -> CodexCredentials | None` (L91-126)
- fn `def save(self, credentials: CodexCredentials) -> None` (L127-146)

### class `class CodexTokenRefresher` (L147-213)
- var `REFRESH_URL = "https://auth.openai.com/oauth/token"` (L154)
- var `CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"` (L155)
- fn `async def refresh(self, credentials: CodexCredentials) -> CodexCredentials` (L157-213)

### class `class CodexProvider(BaseProvider)` : BaseProvider (L214-250)
- var `BASE_URL = "https://chatgpt.com/backend-api"` (L229)
- var `USAGE_PATH = "/wham/usage"` (L230)
- fn `def __init__(self, credentials: CodexCredentials | None = None) -> None` `priv` (L232-242)
- fn `def is_configured(self) -> bool` (L243-246)
- fn `def get_config_help(self) -> str` (L247-250)

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L262-327)

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L328-398)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`CodexCredentials`|class|pub|24-73|class CodexCredentials|
|`CodexCredentials.__init__`|fn|priv|31-37|def __init__(|
|`CodexCredentials.needs_refresh`|fn|pub|45-51|def needs_refresh(self) -> bool|
|`CodexCredentials.from_auth_json`|fn|pub|53-73|def from_auth_json(cls, data: dict) -> "CodexCredentials"|
|`CodexCredentialStore`|class|pub|74-146|class CodexCredentialStore|
|`CodexCredentialStore.codex_home`|fn|pub|80-85|def codex_home(self) -> Path|
|`CodexCredentialStore.auth_file`|fn|pub|87-90|def auth_file(self) -> Path|
|`CodexCredentialStore.load`|fn|pub|91-126|def load(self) -> CodexCredentials | None|
|`CodexCredentialStore.save`|fn|pub|127-146|def save(self, credentials: CodexCredentials) -> None|
|`CodexTokenRefresher`|class|pub|147-213|class CodexTokenRefresher|
|`CodexTokenRefresher.REFRESH_URL`|var|pub|154||
|`CodexTokenRefresher.CLIENT_ID`|var|pub|155||
|`CodexTokenRefresher.refresh`|fn|pub|157-213|async def refresh(self, credentials: CodexCredentials) ->...|
|`CodexProvider`|class|pub|214-250|class CodexProvider(BaseProvider)|
|`CodexProvider.BASE_URL`|var|pub|229||
|`CodexProvider.USAGE_PATH`|var|pub|230||
|`CodexProvider.__init__`|fn|priv|232-242|def __init__(self, credentials: CodexCredentials | None =...|
|`CodexProvider.is_configured`|fn|pub|243-246|def is_configured(self) -> bool|
|`CodexProvider.get_config_help`|fn|pub|247-250|def get_config_help(self) -> str|
|`fetch`|fn|pub|262-327|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|328-398|def _parse_response(self, data: dict, window: WindowPerio...|


---

# copilot.py | Python | 412L | 27 symbols | 8 imports | 30 comments
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

### class `class CopilotDeviceFlow` (L26-118)
- var `CLIENT_ID = "Iv1.b507a08c87ecfe98"` (L35)
- var `SCOPES = "read:user"` (L36)
- var `DEVICE_CODE_URL = "https://github.com/login/device/code"` (L38)
- var `TOKEN_URL = "https://github.com/login/oauth/access_token"` (L39)
- fn `async def request_device_code(self) -> dict[str, Any]` (L41-65)
- fn `async def poll_for_token(self, device_code: str, interval: int = 5) -> str` (L66-118)

### class `class CopilotCredentialStore` (L119-175)
- var `CONFIG_DIR = Path.home() / ".config" / "aibar"` (L127)
- var `CREDS_FILE = CONFIG_DIR / "copilot.json"` (L128)
- var `CODEXBAR_CONFIG = Path.home() / ".codexbar" / "config.json"` (L129)
- fn `def load_token(self) -> str | None` (L131-165)
- fn `def save_token(self, token: str) -> None` (L166-175)

### class `class CopilotProvider(BaseProvider)` : BaseProvider (L176-213)
- var `USAGE_URL = "https://api.github.com/copilot_internal/user"` (L188)
- var `EDITOR_VERSION = "vscode/1.96.2"` (L191)
- var `PLUGIN_VERSION = "copilot-chat/0.26.7"` (L192)
- var `USER_AGENT = "GitHubCopilotChat/0.26.7"` (L193)
- var `API_VERSION = "2025-04-01"` (L194)
- fn `def __init__(self, token: str | None = None) -> None` `priv` (L196-205)
- fn `def is_configured(self) -> bool` (L206-209)
- fn `def get_config_help(self) -> str` (L210-213)

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L223-281)

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L282-380)

### fn `def _get_snapshot(key_camel: str, key_snake: str) -> dict` `priv` (L301-303)

### fn `def _extract_quota_data(snapshot: dict) -> tuple[float | None, float | None]` `priv` (L304-331)

### fn `async def login(self) -> str` (L381-412)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`CopilotDeviceFlow`|class|pub|26-118|class CopilotDeviceFlow|
|`CopilotDeviceFlow.CLIENT_ID`|var|pub|35||
|`CopilotDeviceFlow.SCOPES`|var|pub|36||
|`CopilotDeviceFlow.DEVICE_CODE_URL`|var|pub|38||
|`CopilotDeviceFlow.TOKEN_URL`|var|pub|39||
|`CopilotDeviceFlow.request_device_code`|fn|pub|41-65|async def request_device_code(self) -> dict[str, Any]|
|`CopilotDeviceFlow.poll_for_token`|fn|pub|66-118|async def poll_for_token(self, device_code: str, interval...|
|`CopilotCredentialStore`|class|pub|119-175|class CopilotCredentialStore|
|`CopilotCredentialStore.CONFIG_DIR`|var|pub|127||
|`CopilotCredentialStore.CREDS_FILE`|var|pub|128||
|`CopilotCredentialStore.CODEXBAR_CONFIG`|var|pub|129||
|`CopilotCredentialStore.load_token`|fn|pub|131-165|def load_token(self) -> str | None|
|`CopilotCredentialStore.save_token`|fn|pub|166-175|def save_token(self, token: str) -> None|
|`CopilotProvider`|class|pub|176-213|class CopilotProvider(BaseProvider)|
|`CopilotProvider.USAGE_URL`|var|pub|188||
|`CopilotProvider.EDITOR_VERSION`|var|pub|191||
|`CopilotProvider.PLUGIN_VERSION`|var|pub|192||
|`CopilotProvider.USER_AGENT`|var|pub|193||
|`CopilotProvider.API_VERSION`|var|pub|194||
|`CopilotProvider.__init__`|fn|priv|196-205|def __init__(self, token: str | None = None) -> None|
|`CopilotProvider.is_configured`|fn|pub|206-209|def is_configured(self) -> bool|
|`CopilotProvider.get_config_help`|fn|pub|210-213|def get_config_help(self) -> str|
|`fetch`|fn|pub|223-281|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|282-380|def _parse_response(self, data: dict, window: WindowPerio...|
|`_get_snapshot`|fn|priv|301-303|def _get_snapshot(key_camel: str, key_snake: str) -> dict|
|`_extract_quota_data`|fn|priv|304-331|def _extract_quota_data(snapshot: dict) -> tuple[float | ...|
|`login`|fn|pub|381-412|async def login(self) -> str|


---

# openai_usage.py | Python | 195L | 12 symbols | 4 imports | 17 comments
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

### class `class OpenAIUsageProvider(BaseProvider)` : BaseProvider (L22-61)
- var `BASE_URL = "https://api.openai.com/v1/organization"` (L38)
- var `TOKEN_ENV_VAR = "OPENAI_ADMIN_KEY"` (L39)
- fn `def __init__(self, api_key: str | None = None) -> None` `priv` (L41-53)
- fn `def is_configured(self) -> bool` (L54-57)
- fn `def get_config_help(self) -> str` (L58-61)

### fn `def _get_time_range(self, window: WindowPeriod) -> tuple[int, int]` `priv` (L68-74)

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L75-104)

### fn `async def _fetch_usage(` `priv` (L105-110)

### fn `async def _fetch_costs(` `priv` (L125-130)

### fn `def _check_response(self, response: httpx.Response) -> None` `priv` (L145-155)

### fn `def _build_result(` `priv` (L156-157)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`OpenAIUsageProvider`|class|pub|22-61|class OpenAIUsageProvider(BaseProvider)|
|`OpenAIUsageProvider.BASE_URL`|var|pub|38||
|`OpenAIUsageProvider.TOKEN_ENV_VAR`|var|pub|39||
|`OpenAIUsageProvider.__init__`|fn|priv|41-53|def __init__(self, api_key: str | None = None) -> None|
|`OpenAIUsageProvider.is_configured`|fn|pub|54-57|def is_configured(self) -> bool|
|`OpenAIUsageProvider.get_config_help`|fn|pub|58-61|def get_config_help(self) -> str|
|`_get_time_range`|fn|priv|68-74|def _get_time_range(self, window: WindowPeriod) -> tuple[...|
|`fetch`|fn|pub|75-104|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_fetch_usage`|fn|priv|105-110|async def _fetch_usage(|
|`_fetch_costs`|fn|priv|125-130|async def _fetch_costs(|
|`_check_response`|fn|priv|145-155|def _check_response(self, response: httpx.Response) -> None|
|`_build_result`|fn|priv|156-157|def _build_result(|


---

# openrouter.py | Python | 163L | 11 symbols | 3 imports | 11 comments
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

### class `class OpenRouterUsageProvider(BaseProvider)` : BaseProvider (L20-55)
- var `USAGE_URL = "https://openrouter.ai/api/v1/key"` (L32)
- var `TOKEN_ENV_VAR = "OPENROUTER_API_KEY"` (L33)
- fn `def __init__(self, api_key: str | None = None) -> None` `priv` (L35-47)
- fn `def is_configured(self) -> bool` (L48-51)
- fn `def get_config_help(self) -> str` (L52-55)

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L61-115)

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L116-139)

### fn `def _get_usage(self, payload: dict, window: WindowPeriod) -> float` `priv` (L140-147)

### fn `def _get_byok_usage(self, payload: dict, window: WindowPeriod) -> float` `priv` (L148-155)

### fn `def _to_float(self, value: float | int | None) -> float` `priv` (L156-163)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`OpenRouterUsageProvider`|class|pub|20-55|class OpenRouterUsageProvider(BaseProvider)|
|`OpenRouterUsageProvider.USAGE_URL`|var|pub|32||
|`OpenRouterUsageProvider.TOKEN_ENV_VAR`|var|pub|33||
|`OpenRouterUsageProvider.__init__`|fn|priv|35-47|def __init__(self, api_key: str | None = None) -> None|
|`OpenRouterUsageProvider.is_configured`|fn|pub|48-51|def is_configured(self) -> bool|
|`OpenRouterUsageProvider.get_config_help`|fn|pub|52-55|def get_config_help(self) -> str|
|`fetch`|fn|pub|61-115|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|116-139|def _parse_response(self, data: dict, window: WindowPerio...|
|`_get_usage`|fn|priv|140-147|def _get_usage(self, payload: dict, window: WindowPeriod)...|
|`_get_byok_usage`|fn|priv|148-155|def _get_byok_usage(self, payload: dict, window: WindowPe...|
|`_to_float`|fn|priv|156-163|def _to_float(self, value: float | int | None) -> float|


---

# ui.py | Python | 523L | 27 symbols | 12 imports | 35 comments
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
- fn `def __init__(` `priv` (L119-122)
- fn `def compose(self) -> ComposeResult` (L128-146)
- fn `def watch_result(self, result: ProviderResult | None) -> None` (L147-231)
- fn `def watch_is_loading(self, loading: bool) -> None` (L232-239)

### fn `def _format_age(self, seconds: float) -> str` `priv` (L240-248)

### fn `def _format_duration(self, seconds: float) -> str` `priv` (L249-263)

### class `class RawJsonView(Static)` : Static (L264-298)
- fn `def compose(self) -> ComposeResult` (L283-288)
- fn `def watch_data(self, data: dict | None) -> None` (L289-298)

### class `class AIBarUI(App)` : App (L299-498)
- var `BINDINGS = [` (L356)
- var `TITLE = "Usage Metrics UI"` (L364)
- fn `def __init__(self) -> None` `priv` (L369-380)
- fn `def compose(self) -> ComposeResult` (L381-403)
- fn `async def on_mount(self) -> None` (L404-408)
- fn `async def on_refresh_pressed(self) -> None` (L410-413)
- fn `async def on_5h_pressed(self) -> None` (L415-418)
- fn `async def on_7d_pressed(self) -> None` (L420-423)
- fn `async def action_refresh(self) -> None` (L424-458)
- fn `async def action_window_5h(self) -> None` (L459-465)
- fn `async def action_window_7d(self) -> None` (L466-472)
- fn `async def action_toggle_json(self) -> None` (L473-481)
- fn `def _get_card(self, provider: ProviderName) -> ProviderCard | None` `priv` (L482-489)

### fn `def _update_window_buttons(self) -> None` `priv` (L490-505)

### fn `def _update_json_view(self) -> None` `priv` (L506-515)

### fn `def run_ui() -> None` (L516-521)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`ProviderCard`|class|pub|45-244|class ProviderCard(Static)|
|`ProviderCard.__init__`|fn|priv|119-122|def __init__(|
|`ProviderCard.compose`|fn|pub|128-146|def compose(self) -> ComposeResult|
|`ProviderCard.watch_result`|fn|pub|147-231|def watch_result(self, result: ProviderResult | None) -> ...|
|`ProviderCard.watch_is_loading`|fn|pub|232-239|def watch_is_loading(self, loading: bool) -> None|
|`_format_age`|fn|priv|240-248|def _format_age(self, seconds: float) -> str|
|`_format_duration`|fn|priv|249-263|def _format_duration(self, seconds: float) -> str|
|`RawJsonView`|class|pub|264-298|class RawJsonView(Static)|
|`RawJsonView.compose`|fn|pub|283-288|def compose(self) -> ComposeResult|
|`RawJsonView.watch_data`|fn|pub|289-298|def watch_data(self, data: dict | None) -> None|
|`AIBarUI`|class|pub|299-498|class AIBarUI(App)|
|`AIBarUI.BINDINGS`|var|pub|356||
|`AIBarUI.TITLE`|var|pub|364||
|`AIBarUI.__init__`|fn|priv|369-380|def __init__(self) -> None|
|`AIBarUI.compose`|fn|pub|381-403|def compose(self) -> ComposeResult|
|`AIBarUI.on_mount`|fn|pub|404-408|async def on_mount(self) -> None|
|`AIBarUI.on_refresh_pressed`|fn|pub|410-413|async def on_refresh_pressed(self) -> None|
|`AIBarUI.on_5h_pressed`|fn|pub|415-418|async def on_5h_pressed(self) -> None|
|`AIBarUI.on_7d_pressed`|fn|pub|420-423|async def on_7d_pressed(self) -> None|
|`AIBarUI.action_refresh`|fn|pub|424-458|async def action_refresh(self) -> None|
|`AIBarUI.action_window_5h`|fn|pub|459-465|async def action_window_5h(self) -> None|
|`AIBarUI.action_window_7d`|fn|pub|466-472|async def action_window_7d(self) -> None|
|`AIBarUI.action_toggle_json`|fn|pub|473-481|async def action_toggle_json(self) -> None|
|`AIBarUI._get_card`|fn|priv|482-489|def _get_card(self, provider: ProviderName) -> ProviderCa...|
|`_update_window_buttons`|fn|priv|490-505|def _update_window_buttons(self) -> None|
|`_update_json_view`|fn|priv|506-515|def _update_json_view(self) -> None|
|`run_ui`|fn|pub|516-521|def run_ui() -> None|


---

# dev.sh | Shell | 34L | 1 symbols | 0 imports | 4 comments
> Path: `src/aibar/extension/aibar@aibar.panel/dev.sh`

## Definitions

- var `EXT_UUID="aibar@aibar.panel"` (L6)
- @brief Development helper commands for aibar GNOME extension.
- @details Wraps nested-shell start, enable/disable/reload, and log tail commands for local extension workflows.
## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`EXT_UUID`|var||6||


---

# extension.js | JavaScript | 802L | 9 symbols | 8 imports | 6 comments
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
- fn `const createWindowBar = (labelText) =>` (L319-365)

### fn `const updateWindowBar = (bar, pct, resetTime, useDays) =>` (L459-500)

### class `export default class AIBarExtension` (L783-802)
- @brief GNOME extension lifecycle adapter for AIBarIndicator registration. */

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`REFRESH_INTERVAL_SECONDS`|const||16||
|`ENV_FILE_PATH`|const||17||
|`_getAiBarPath`|fn||24-34|function _getAiBarPath()|
|`_loadEnvFromFile`|fn||41-93|function _loadEnvFromFile()|
|`_getProgressClass`|fn||100-106|function _getProgressClass(pct)|
|`AIBarIndicator`|class||110-409|class AIBarIndicator extends PanelMenu.Button|
|`AIBarIndicator.createWindowBar`|fn||319-365|const createWindowBar = (labelText) =>|
|`updateWindowBar`|fn||459-500|const updateWindowBar = (bar, pct, resetTime, useDays) =>|
|`AIBarExtension`|class||783-802|export default class AIBarExtension|

