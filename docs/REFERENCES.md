# Files Structure
```
.
└── src
    └── aibar
        ├── extension
        │   ├── dev.sh
        │   └── extension.js
        └── usage_tui
            ├── __init__.py
            ├── cache.py
            ├── claude_cli_auth.py
            ├── cli.py
            ├── config.py
            ├── providers
            │   ├── __init__.py
            │   ├── base.py
            │   ├── claude_oauth.py
            │   ├── codex.py
            │   ├── copilot.py
            │   ├── openai_usage.py
            │   └── openrouter.py
            └── tui.py
```

# dev.sh | Shell | 32L | 1 symbols | 0 imports | 2 comments
> Path: `src/aibar/extension/dev.sh`

## Definitions

- var `EXT_UUID="usage-tui@gnome.codexbar"` (L4)
## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`EXT_UUID`|var||4||


---

# extension.js | JavaScript | 784L | 9 symbols | 8 imports | 1 comments
> Path: `src/aibar/extension/extension.js`

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

- const `const REFRESH_INTERVAL_SECONDS = 300;` (L11)
- const `const ENV_FILE_PATH = GLib.get_home_dir() + '/.config/usage-tui/env';` (L12)
### fn `function _getUsageTuiPath()` (L18-28)

### fn `function _loadEnvFromFile()` (L30-82)

### fn `function _getProgressClass(pct)` (L84-90)

### class `class UsageTuiIndicator extends PanelMenu.Button` : PanelMenu.Button (L93-392)
- fn `const createWindowBar = (labelText) =>` (L302-348)

### fn `const updateWindowBar = (bar, pct, resetTime, useDays) =>` (L442-483)

### class `export default class UsageTuiExtension` (L765-784)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`REFRESH_INTERVAL_SECONDS`|const||11||
|`ENV_FILE_PATH`|const||12||
|`_getUsageTuiPath`|fn||18-28|function _getUsageTuiPath()|
|`_loadEnvFromFile`|fn||30-82|function _loadEnvFromFile()|
|`_getProgressClass`|fn||84-90|function _getProgressClass(pct)|
|`UsageTuiIndicator`|class||93-392|class UsageTuiIndicator extends PanelMenu.Button|
|`UsageTuiIndicator.createWindowBar`|fn||302-348|const createWindowBar = (labelText) =>|
|`updateWindowBar`|fn||442-483|const updateWindowBar = (bar, pct, resetTime, useDays) =>|
|`UsageTuiExtension`|class||765-784|export default class UsageTuiExtension|


---

# __init__.py | Python | 3L | 0 symbols | 0 imports | 1 comments
> Path: `src/aibar/usage_tui/__init__.py`


---

# cache.py | Python | 202L | 18 symbols | 7 imports | 23 comments
> Path: `src/aibar/usage_tui/cache.py`

## Imports
```
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from pydantic import BaseModel
from usage_tui.providers.base import ProviderName, ProviderResult, WindowPeriod
```

## Definitions

### class `class CacheEntry(BaseModel)` : BaseModel (L14-27)
- fn `def is_expired(self) -> bool` (L21-27)

### class `class ResultCache` (L28-202)
- var `DEFAULT_TTL = 120  # 2 minutes` (L38)
- var `PROVIDER_TTLS =` (L39)
- fn `def __init__(self, cache_dir: Path | None = None) -> None` `priv` (L46-57)
- fn `def _default_cache_dir(self) -> Path` `priv` (L58-63)
- fn `def _ensure_cache_dir(self) -> None` `priv` (L64-67)
- fn `def _cache_key(self, provider: ProviderName, window: WindowPeriod) -> str` `priv` (L68-71)
- fn `def _disk_path(self, provider: ProviderName, window: WindowPeriod) -> Path` `priv` (L72-75)
- fn `def get(self, provider: ProviderName, window: WindowPeriod) -> ProviderResult | None` (L76-92)
- fn `def set(self, result: ProviderResult) -> None` (L93-112)
- fn `def get_last_good(self, provider: ProviderName, window: WindowPeriod) -> ProviderResult | None` (L113-120)
- fn `def invalidate(` (L121-122)
- fn `def _save_to_disk(self, result: ProviderResult) -> None` `priv` (L145-158)
- fn `def _load_from_disk(` `priv` (L159-163)
- fn `def _sanitize_raw(self, raw: dict[str, Any]) -> dict[str, Any]` `priv` (L188-202)
- fn `def clean(obj: Any) -> Any` (L192-201)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`CacheEntry`|class|pub|14-27|class CacheEntry(BaseModel)|
|`CacheEntry.is_expired`|fn|pub|21-27|def is_expired(self) -> bool|
|`ResultCache`|class|pub|28-202|class ResultCache|
|`ResultCache.DEFAULT_TTL`|var|pub|38||
|`ResultCache.PROVIDER_TTLS`|var|pub|39||
|`ResultCache.__init__`|fn|priv|46-57|def __init__(self, cache_dir: Path | None = None) -> None|
|`ResultCache._default_cache_dir`|fn|priv|58-63|def _default_cache_dir(self) -> Path|
|`ResultCache._ensure_cache_dir`|fn|priv|64-67|def _ensure_cache_dir(self) -> None|
|`ResultCache._cache_key`|fn|priv|68-71|def _cache_key(self, provider: ProviderName, window: Wind...|
|`ResultCache._disk_path`|fn|priv|72-75|def _disk_path(self, provider: ProviderName, window: Wind...|
|`ResultCache.get`|fn|pub|76-92|def get(self, provider: ProviderName, window: WindowPerio...|
|`ResultCache.set`|fn|pub|93-112|def set(self, result: ProviderResult) -> None|
|`ResultCache.get_last_good`|fn|pub|113-120|def get_last_good(self, provider: ProviderName, window: W...|
|`ResultCache.invalidate`|fn|pub|121-122|def invalidate(|
|`ResultCache._save_to_disk`|fn|priv|145-158|def _save_to_disk(self, result: ProviderResult) -> None|
|`ResultCache._load_from_disk`|fn|priv|159-163|def _load_from_disk(|
|`ResultCache._sanitize_raw`|fn|priv|188-202|def _sanitize_raw(self, raw: dict[str, Any]) -> dict[str,...|
|`ResultCache.clean`|fn|pub|192-201|def clean(obj: Any) -> Any|


---

# claude_cli_auth.py | Python | 114L | 9 symbols | 4 imports | 11 comments
> Path: `src/aibar/usage_tui/claude_cli_auth.py`

## Imports
```
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
```

## Definitions

### class `class ClaudeCLIAuth` (L9-105)
- var `DEFAULT_CREDS_PATH = Path.home() / ".claude" / ".credentials.json"` (L18)
- fn `def __init__(self, creds_path: Path | None = None) -> None` `priv` (L20-28)
- fn `def is_available(self) -> bool` (L29-32)
- fn `def get_credentials(self) -> dict[str, Any] | None` (L33-48)
- fn `def get_access_token(self) -> str | None` (L49-53)
- fn `def is_token_expired(self) -> bool` (L54-67)
- fn `def get_token_info(self) -> dict[str, Any]` (L68-105)

### fn `def extract_claude_cli_token() -> str | None` (L106-114)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`ClaudeCLIAuth`|class|pub|9-105|class ClaudeCLIAuth|
|`ClaudeCLIAuth.DEFAULT_CREDS_PATH`|var|pub|18||
|`ClaudeCLIAuth.__init__`|fn|priv|20-28|def __init__(self, creds_path: Path | None = None) -> None|
|`ClaudeCLIAuth.is_available`|fn|pub|29-32|def is_available(self) -> bool|
|`ClaudeCLIAuth.get_credentials`|fn|pub|33-48|def get_credentials(self) -> dict[str, Any] | None|
|`ClaudeCLIAuth.get_access_token`|fn|pub|49-53|def get_access_token(self) -> str | None|
|`ClaudeCLIAuth.is_token_expired`|fn|pub|54-67|def is_token_expired(self) -> bool|
|`ClaudeCLIAuth.get_token_info`|fn|pub|68-105|def get_token_info(self) -> dict[str, Any]|
|`extract_claude_cli_token`|fn|pub|106-114|def extract_claude_cli_token() -> str | None|


---

# cli.py | Python | 438L | 15 symbols | 13 imports | 33 comments
> Path: `src/aibar/usage_tui/cli.py`

## Imports
```
import asyncio
import json
import sys
import click
from click.core import ParameterSource
from usage_tui.config import config
from usage_tui.providers import (
from usage_tui.providers.base import BaseProvider, ProviderError, ProviderName, WindowPeriod
from datetime import datetime, timezone
from usage_tui.tui import run_tui
from usage_tui.config import ENV_FILE_PATH, write_env_file
from usage_tui.claude_cli_auth import ClaudeCLIAuth
from usage_tui.providers.copilot import CopilotProvider
```

## Definitions

### fn `def get_providers() -> dict[ProviderName, BaseProvider]` (L21-31)

### fn `def parse_window(window: str) -> WindowPeriod` (L32-43)

### fn `def parse_provider(provider: str) -> ProviderName | None` (L44-54)

### fn `def _fetch_result(provider: BaseProvider, window: WindowPeriod)` `priv` (L55-64)

### fn `def main() -> None` `@click.version_option()` (L67-71)

### fn `def show(provider: str, window: str, output_json: bool) -> None` (L91-139)

### fn `def _print_result(name: ProviderName, result, label: str | None = None) -> None` `priv` (L140-186)

### fn `def _progress_bar(percent: float, width: int = 20) -> str` `priv` (L187-193)

### fn `def doctor() -> None` `@main.command()` (L195-241)

### fn `def tui() -> None` `@main.command()` (L243-249)

### fn `def env() -> None` `@main.command()` (L251-255)

### fn `def setup() -> None` `@main.command()` (L257-343)

### fn `def login(provider: str) -> None` (L351-367)

### fn `def _login_claude() -> None` `priv` (L368-412)

### fn `def _login_copilot() -> None` `priv` (L413-436)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`get_providers`|fn|pub|21-31|def get_providers() -> dict[ProviderName, BaseProvider]|
|`parse_window`|fn|pub|32-43|def parse_window(window: str) -> WindowPeriod|
|`parse_provider`|fn|pub|44-54|def parse_provider(provider: str) -> ProviderName | None|
|`_fetch_result`|fn|priv|55-64|def _fetch_result(provider: BaseProvider, window: WindowP...|
|`main`|fn|pub|67-71|def main() -> None|
|`show`|fn|pub|91-139|def show(provider: str, window: str, output_json: bool) -...|
|`_print_result`|fn|priv|140-186|def _print_result(name: ProviderName, result, label: str ...|
|`_progress_bar`|fn|priv|187-193|def _progress_bar(percent: float, width: int = 20) -> str|
|`doctor`|fn|pub|195-241|def doctor() -> None|
|`tui`|fn|pub|243-249|def tui() -> None|
|`env`|fn|pub|251-255|def env() -> None|
|`setup`|fn|pub|257-343|def setup() -> None|
|`login`|fn|pub|351-367|def login(provider: str) -> None|
|`_login_claude`|fn|priv|368-412|def _login_claude() -> None|
|`_login_copilot`|fn|priv|413-436|def _login_copilot() -> None|


---

# config.py | Python | 229L | 12 symbols | 8 imports | 19 comments
> Path: `src/aibar/usage_tui/config.py`

## Imports
```
import os
from pathlib import Path
from typing import Any
from usage_tui.claude_cli_auth import extract_claude_cli_token
from usage_tui.providers.base import ProviderName
from usage_tui.providers.codex import CodexCredentialStore
from usage_tui.providers.copilot import CopilotCredentialStore
from usage_tui.providers import (
```

## Definitions

- var `ENV_FILE_PATH = Path.home() / ".config" / "usage-tui" / "env"` (L11)
### fn `def load_env_file() -> dict[str, str]` (L14-28)

### fn `def write_env_file(updates: dict[str, str]) -> None` (L29-63)

### class `class Config` (L64-227)
- var `ENV_VARS =` (L73)
- var `PROVIDER_INFO =` (L82)
- fn `def get_token(self, provider: ProviderName) -> str | None` (L115-151)
- fn `def is_provider_configured(self, provider: ProviderName) -> bool` (L152-180)
- fn `def get_provider_status(self, provider: ProviderName) -> dict[str, Any]` (L181-197)
- fn `def get_all_provider_status(self) -> list[dict[str, Any]]` (L198-201)
- fn `def _get_token_preview(self, provider: ProviderName) -> str | None` `priv` (L202-208)
- fn `def get_env_var_help(self) -> str` (L209-227)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`ENV_FILE_PATH`|var|pub|11||
|`load_env_file`|fn|pub|14-28|def load_env_file() -> dict[str, str]|
|`write_env_file`|fn|pub|29-63|def write_env_file(updates: dict[str, str]) -> None|
|`Config`|class|pub|64-227|class Config|
|`Config.ENV_VARS`|var|pub|73||
|`Config.PROVIDER_INFO`|var|pub|82||
|`Config.get_token`|fn|pub|115-151|def get_token(self, provider: ProviderName) -> str | None|
|`Config.is_provider_configured`|fn|pub|152-180|def is_provider_configured(self, provider: ProviderName) ...|
|`Config.get_provider_status`|fn|pub|181-197|def get_provider_status(self, provider: ProviderName) -> ...|
|`Config.get_all_provider_status`|fn|pub|198-201|def get_all_provider_status(self) -> list[dict[str, Any]]|
|`Config._get_token_preview`|fn|priv|202-208|def _get_token_preview(self, provider: ProviderName) -> s...|
|`Config.get_env_var_help`|fn|pub|209-227|def get_env_var_help(self) -> str|


---

# __init__.py | Python | 19L | 0 symbols | 6 imports | 1 comments
> Path: `src/aibar/usage_tui/providers/__init__.py`

## Imports
```
from usage_tui.providers.base import BaseProvider, UsageMetrics, ProviderResult
from usage_tui.providers.claude_oauth import ClaudeOAuthProvider
from usage_tui.providers.openai_usage import OpenAIUsageProvider
from usage_tui.providers.openrouter import OpenRouterUsageProvider
from usage_tui.providers.copilot import CopilotProvider
from usage_tui.providers.codex import CodexProvider
```


---

# base.py | Python | 143L | 23 symbols | 5 imports | 16 comments
> Path: `src/aibar/usage_tui/providers/base.py`

## Imports
```
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
```

## Definitions

### class `class WindowPeriod(str, Enum)` : str, Enum (L11-18)
- var `HOUR_5 = "5h"` (L14)
- var `DAY_7 = "7d"` (L15)
- var `DAY_30 = "30d"` (L16)

### class `class ProviderName(str, Enum)` : str, Enum (L19-28)
- var `CLAUDE = "claude"` (L22)
- var `OPENAI = "openai"` (L23)
- var `OPENROUTER = "openrouter"` (L24)
- var `COPILOT = "copilot"` (L25)
- var `CODEX = "codex"` (L26)

### class `class UsageMetrics(BaseModel)` : BaseModel (L29-56)
- fn `def usage_percent(self) -> float | None` (L41-48)
- fn `def total_tokens(self) -> int | None` (L50-56)

### class `class ProviderResult(BaseModel)` : BaseModel (L57-72)
- fn `def is_error(self) -> bool` (L68-72)

### class `class ProviderError(Exception)` : Exception (L73-78)

### class `class AuthenticationError(ProviderError)` : ProviderError (L79-84)

### class `class RateLimitError(ProviderError)` : ProviderError (L85-90)

### class `class BaseProvider(ABC)` : ABC (L91-143)
- fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L97-112)
- fn `def is_configured(self) -> bool` (L114-122)
- fn `def get_config_help(self) -> str` (L124-132)
- fn `def _make_error_result(` `priv` (L133-134)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`WindowPeriod`|class|pub|11-18|class WindowPeriod(str, Enum)|
|`WindowPeriod.HOUR_5`|var|pub|14||
|`WindowPeriod.DAY_7`|var|pub|15||
|`WindowPeriod.DAY_30`|var|pub|16||
|`ProviderName`|class|pub|19-28|class ProviderName(str, Enum)|
|`ProviderName.CLAUDE`|var|pub|22||
|`ProviderName.OPENAI`|var|pub|23||
|`ProviderName.OPENROUTER`|var|pub|24||
|`ProviderName.COPILOT`|var|pub|25||
|`ProviderName.CODEX`|var|pub|26||
|`UsageMetrics`|class|pub|29-56|class UsageMetrics(BaseModel)|
|`UsageMetrics.usage_percent`|fn|pub|41-48|def usage_percent(self) -> float | None|
|`UsageMetrics.total_tokens`|fn|pub|50-56|def total_tokens(self) -> int | None|
|`ProviderResult`|class|pub|57-72|class ProviderResult(BaseModel)|
|`ProviderResult.is_error`|fn|pub|68-72|def is_error(self) -> bool|
|`ProviderError`|class|pub|73-78|class ProviderError(Exception)|
|`AuthenticationError`|class|pub|79-84|class AuthenticationError(ProviderError)|
|`RateLimitError`|class|pub|85-90|class RateLimitError(ProviderError)|
|`BaseProvider`|class|pub|91-143|class BaseProvider(ABC)|
|`BaseProvider.fetch`|fn|pub|97-112|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`BaseProvider.is_configured`|fn|pub|114-122|def is_configured(self) -> bool|
|`BaseProvider.get_config_help`|fn|pub|124-132|def get_config_help(self) -> str|
|`BaseProvider._make_error_result`|fn|priv|133-134|def _make_error_result(|


---

# claude_oauth.py | Python | 186L | 8 symbols | 5 imports | 13 comments
> Path: `src/aibar/usage_tui/providers/claude_oauth.py`

## Imports
```
import os
from datetime import datetime
import httpx
from usage_tui.claude_cli_auth import extract_claude_cli_token
from usage_tui.providers.base import (
```

## Definitions

### class `class ClaudeOAuthProvider(BaseProvider)` : BaseProvider (L20-54)
- var `USAGE_URL = "https://api.anthropic.com/api/oauth/usage"` (L34)
- var `TOKEN_ENV_VAR = "CLAUDE_CODE_OAUTH_TOKEN"` (L35)
- fn `def __init__(self, token: str | None = None) -> None` `priv` (L37-46)
- fn `def is_configured(self) -> bool` (L47-50)
- fn `def get_config_help(self) -> str` (L51-54)

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L61-134)

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L135-186)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`ClaudeOAuthProvider`|class|pub|20-54|class ClaudeOAuthProvider(BaseProvider)|
|`ClaudeOAuthProvider.USAGE_URL`|var|pub|34||
|`ClaudeOAuthProvider.TOKEN_ENV_VAR`|var|pub|35||
|`ClaudeOAuthProvider.__init__`|fn|priv|37-46|def __init__(self, token: str | None = None) -> None|
|`ClaudeOAuthProvider.is_configured`|fn|pub|47-50|def is_configured(self) -> bool|
|`ClaudeOAuthProvider.get_config_help`|fn|pub|51-54|def get_config_help(self) -> str|
|`fetch`|fn|pub|61-134|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|135-186|def _parse_response(self, data: dict, window: WindowPerio...|


---

# codex.py | Python | 396L | 21 symbols | 7 imports | 31 comments
> Path: `src/aibar/usage_tui/providers/codex.py`

## Imports
```
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import httpx
from usage_tui.providers.base import (
```

## Definitions

### class `class CodexCredentials` (L22-71)
- fn `def __init__(` `priv` (L29-35)
- fn `def needs_refresh(self) -> bool` (L43-49)
- fn `def from_auth_json(cls, data: dict) -> "CodexCredentials"` (L51-71)

### class `class CodexCredentialStore` (L72-144)
- fn `def codex_home(self) -> Path` (L78-83)
- fn `def auth_file(self) -> Path` (L85-88)
- fn `def load(self) -> CodexCredentials | None` (L89-124)
- fn `def save(self, credentials: CodexCredentials) -> None` (L125-144)

### class `class CodexTokenRefresher` (L145-211)
- var `REFRESH_URL = "https://auth.openai.com/oauth/token"` (L152)
- var `CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"` (L153)
- fn `async def refresh(self, credentials: CodexCredentials) -> CodexCredentials` (L155-211)

### class `class CodexProvider(BaseProvider)` : BaseProvider (L212-248)
- var `BASE_URL = "https://chatgpt.com/backend-api"` (L227)
- var `USAGE_PATH = "/wham/usage"` (L228)
- fn `def __init__(self, credentials: CodexCredentials | None = None) -> None` `priv` (L230-240)
- fn `def is_configured(self) -> bool` (L241-244)
- fn `def get_config_help(self) -> str` (L245-248)

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L260-325)

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L326-396)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`CodexCredentials`|class|pub|22-71|class CodexCredentials|
|`CodexCredentials.__init__`|fn|priv|29-35|def __init__(|
|`CodexCredentials.needs_refresh`|fn|pub|43-49|def needs_refresh(self) -> bool|
|`CodexCredentials.from_auth_json`|fn|pub|51-71|def from_auth_json(cls, data: dict) -> "CodexCredentials"|
|`CodexCredentialStore`|class|pub|72-144|class CodexCredentialStore|
|`CodexCredentialStore.codex_home`|fn|pub|78-83|def codex_home(self) -> Path|
|`CodexCredentialStore.auth_file`|fn|pub|85-88|def auth_file(self) -> Path|
|`CodexCredentialStore.load`|fn|pub|89-124|def load(self) -> CodexCredentials | None|
|`CodexCredentialStore.save`|fn|pub|125-144|def save(self, credentials: CodexCredentials) -> None|
|`CodexTokenRefresher`|class|pub|145-211|class CodexTokenRefresher|
|`CodexTokenRefresher.REFRESH_URL`|var|pub|152||
|`CodexTokenRefresher.CLIENT_ID`|var|pub|153||
|`CodexTokenRefresher.refresh`|fn|pub|155-211|async def refresh(self, credentials: CodexCredentials) ->...|
|`CodexProvider`|class|pub|212-248|class CodexProvider(BaseProvider)|
|`CodexProvider.BASE_URL`|var|pub|227||
|`CodexProvider.USAGE_PATH`|var|pub|228||
|`CodexProvider.__init__`|fn|priv|230-240|def __init__(self, credentials: CodexCredentials | None =...|
|`CodexProvider.is_configured`|fn|pub|241-244|def is_configured(self) -> bool|
|`CodexProvider.get_config_help`|fn|pub|245-248|def get_config_help(self) -> str|
|`fetch`|fn|pub|260-325|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|326-396|def _parse_response(self, data: dict, window: WindowPerio...|


---

# copilot.py | Python | 408L | 27 symbols | 8 imports | 30 comments
> Path: `src/aibar/usage_tui/providers/copilot.py`

## Imports
```
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import httpx
from usage_tui.providers.base import (
import asyncio
```

## Definitions

### class `class CopilotDeviceFlow` (L22-114)
- var `CLIENT_ID = "Iv1.b507a08c87ecfe98"` (L31)
- var `SCOPES = "read:user"` (L32)
- var `DEVICE_CODE_URL = "https://github.com/login/device/code"` (L34)
- var `TOKEN_URL = "https://github.com/login/oauth/access_token"` (L35)
- fn `async def request_device_code(self) -> dict[str, Any]` (L37-61)
- fn `async def poll_for_token(self, device_code: str, interval: int = 5) -> str` (L62-114)

### class `class CopilotCredentialStore` (L115-171)
- var `CONFIG_DIR = Path.home() / ".config" / "usage-tui"` (L123)
- var `CREDS_FILE = CONFIG_DIR / "copilot.json"` (L124)
- var `CODEXBAR_CONFIG = Path.home() / ".codexbar" / "config.json"` (L125)
- fn `def load_token(self) -> str | None` (L127-161)
- fn `def save_token(self, token: str) -> None` (L162-171)

### class `class CopilotProvider(BaseProvider)` : BaseProvider (L172-209)
- var `USAGE_URL = "https://api.github.com/copilot_internal/user"` (L184)
- var `EDITOR_VERSION = "vscode/1.96.2"` (L187)
- var `PLUGIN_VERSION = "copilot-chat/0.26.7"` (L188)
- var `USER_AGENT = "GitHubCopilotChat/0.26.7"` (L189)
- var `API_VERSION = "2025-04-01"` (L190)
- fn `def __init__(self, token: str | None = None) -> None` `priv` (L192-201)
- fn `def is_configured(self) -> bool` (L202-205)
- fn `def get_config_help(self) -> str` (L206-209)

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L219-277)

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L278-376)

### fn `def _get_snapshot(key_camel: str, key_snake: str) -> dict` `priv` (L297-299)

### fn `def _extract_quota_data(snapshot: dict) -> tuple[float | None, float | None]` `priv` (L300-327)

### fn `async def login(self) -> str` (L377-408)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`CopilotDeviceFlow`|class|pub|22-114|class CopilotDeviceFlow|
|`CopilotDeviceFlow.CLIENT_ID`|var|pub|31||
|`CopilotDeviceFlow.SCOPES`|var|pub|32||
|`CopilotDeviceFlow.DEVICE_CODE_URL`|var|pub|34||
|`CopilotDeviceFlow.TOKEN_URL`|var|pub|35||
|`CopilotDeviceFlow.request_device_code`|fn|pub|37-61|async def request_device_code(self) -> dict[str, Any]|
|`CopilotDeviceFlow.poll_for_token`|fn|pub|62-114|async def poll_for_token(self, device_code: str, interval...|
|`CopilotCredentialStore`|class|pub|115-171|class CopilotCredentialStore|
|`CopilotCredentialStore.CONFIG_DIR`|var|pub|123||
|`CopilotCredentialStore.CREDS_FILE`|var|pub|124||
|`CopilotCredentialStore.CODEXBAR_CONFIG`|var|pub|125||
|`CopilotCredentialStore.load_token`|fn|pub|127-161|def load_token(self) -> str | None|
|`CopilotCredentialStore.save_token`|fn|pub|162-171|def save_token(self, token: str) -> None|
|`CopilotProvider`|class|pub|172-209|class CopilotProvider(BaseProvider)|
|`CopilotProvider.USAGE_URL`|var|pub|184||
|`CopilotProvider.EDITOR_VERSION`|var|pub|187||
|`CopilotProvider.PLUGIN_VERSION`|var|pub|188||
|`CopilotProvider.USER_AGENT`|var|pub|189||
|`CopilotProvider.API_VERSION`|var|pub|190||
|`CopilotProvider.__init__`|fn|priv|192-201|def __init__(self, token: str | None = None) -> None|
|`CopilotProvider.is_configured`|fn|pub|202-205|def is_configured(self) -> bool|
|`CopilotProvider.get_config_help`|fn|pub|206-209|def get_config_help(self) -> str|
|`fetch`|fn|pub|219-277|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|278-376|def _parse_response(self, data: dict, window: WindowPerio...|
|`_get_snapshot`|fn|priv|297-299|def _get_snapshot(key_camel: str, key_snake: str) -> dict|
|`_extract_quota_data`|fn|priv|300-327|def _extract_quota_data(snapshot: dict) -> tuple[float | ...|
|`login`|fn|pub|377-408|async def login(self) -> str|


---

# openai_usage.py | Python | 191L | 12 symbols | 4 imports | 17 comments
> Path: `src/aibar/usage_tui/providers/openai_usage.py`

## Imports
```
from datetime import datetime, timedelta, timezone
import httpx
from usage_tui.providers.base import (
from usage_tui.config import config
```

## Definitions

### class `class OpenAIUsageProvider(BaseProvider)` : BaseProvider (L18-57)
- var `BASE_URL = "https://api.openai.com/v1/organization"` (L34)
- var `TOKEN_ENV_VAR = "OPENAI_ADMIN_KEY"` (L35)
- fn `def __init__(self, api_key: str | None = None) -> None` `priv` (L37-49)
- fn `def is_configured(self) -> bool` (L50-53)
- fn `def get_config_help(self) -> str` (L54-57)

### fn `def _get_time_range(self, window: WindowPeriod) -> tuple[int, int]` `priv` (L64-70)

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L71-100)

### fn `async def _fetch_usage(` `priv` (L101-106)

### fn `async def _fetch_costs(` `priv` (L121-126)

### fn `def _check_response(self, response: httpx.Response) -> None` `priv` (L141-151)

### fn `def _build_result(` `priv` (L152-153)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`OpenAIUsageProvider`|class|pub|18-57|class OpenAIUsageProvider(BaseProvider)|
|`OpenAIUsageProvider.BASE_URL`|var|pub|34||
|`OpenAIUsageProvider.TOKEN_ENV_VAR`|var|pub|35||
|`OpenAIUsageProvider.__init__`|fn|priv|37-49|def __init__(self, api_key: str | None = None) -> None|
|`OpenAIUsageProvider.is_configured`|fn|pub|50-53|def is_configured(self) -> bool|
|`OpenAIUsageProvider.get_config_help`|fn|pub|54-57|def get_config_help(self) -> str|
|`_get_time_range`|fn|priv|64-70|def _get_time_range(self, window: WindowPeriod) -> tuple[...|
|`fetch`|fn|pub|71-100|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_fetch_usage`|fn|priv|101-106|async def _fetch_usage(|
|`_fetch_costs`|fn|priv|121-126|async def _fetch_costs(|
|`_check_response`|fn|priv|141-151|def _check_response(self, response: httpx.Response) -> None|
|`_build_result`|fn|priv|152-153|def _build_result(|


---

# openrouter.py | Python | 159L | 11 symbols | 3 imports | 11 comments
> Path: `src/aibar/usage_tui/providers/openrouter.py`

## Imports
```
import httpx
from usage_tui.providers.base import (
from usage_tui.config import config
```

## Definitions

### class `class OpenRouterUsageProvider(BaseProvider)` : BaseProvider (L16-51)
- var `USAGE_URL = "https://openrouter.ai/api/v1/key"` (L28)
- var `TOKEN_ENV_VAR = "OPENROUTER_API_KEY"` (L29)
- fn `def __init__(self, api_key: str | None = None) -> None` `priv` (L31-43)
- fn `def is_configured(self) -> bool` (L44-47)
- fn `def get_config_help(self) -> str` (L48-51)

### fn `async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult` (L57-111)

### fn `def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult` `priv` (L112-135)

### fn `def _get_usage(self, payload: dict, window: WindowPeriod) -> float` `priv` (L136-143)

### fn `def _get_byok_usage(self, payload: dict, window: WindowPeriod) -> float` `priv` (L144-151)

### fn `def _to_float(self, value: float | int | None) -> float` `priv` (L152-159)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`OpenRouterUsageProvider`|class|pub|16-51|class OpenRouterUsageProvider(BaseProvider)|
|`OpenRouterUsageProvider.USAGE_URL`|var|pub|28||
|`OpenRouterUsageProvider.TOKEN_ENV_VAR`|var|pub|29||
|`OpenRouterUsageProvider.__init__`|fn|priv|31-43|def __init__(self, api_key: str | None = None) -> None|
|`OpenRouterUsageProvider.is_configured`|fn|pub|44-47|def is_configured(self) -> bool|
|`OpenRouterUsageProvider.get_config_help`|fn|pub|48-51|def get_config_help(self) -> str|
|`fetch`|fn|pub|57-111|async def fetch(self, window: WindowPeriod = WindowPeriod...|
|`_parse_response`|fn|priv|112-135|def _parse_response(self, data: dict, window: WindowPerio...|
|`_get_usage`|fn|priv|136-143|def _get_usage(self, payload: dict, window: WindowPeriod)...|
|`_get_byok_usage`|fn|priv|144-151|def _get_byok_usage(self, payload: dict, window: WindowPe...|
|`_to_float`|fn|priv|152-159|def _to_float(self, value: float | int | None) -> float|


---

# tui.py | Python | 519L | 27 symbols | 12 imports | 34 comments
> Path: `src/aibar/usage_tui/tui.py`

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
from usage_tui.cache import ResultCache
from usage_tui.config import config
from usage_tui.providers import (
from usage_tui.providers.base import (
```

## Definitions

### class `class ProviderCard(Static)` : Static (L41-240)
- fn `def __init__(` `priv` (L115-118)
- fn `def compose(self) -> ComposeResult` (L124-142)
- fn `def watch_result(self, result: ProviderResult | None) -> None` (L143-227)
- fn `def watch_is_loading(self, loading: bool) -> None` (L228-235)

### fn `def _format_age(self, seconds: float) -> str` `priv` (L236-244)

### fn `def _format_duration(self, seconds: float) -> str` `priv` (L245-259)

### class `class RawJsonView(Static)` : Static (L260-294)
- fn `def compose(self) -> ComposeResult` (L279-284)
- fn `def watch_data(self, data: dict | None) -> None` (L285-294)

### class `class UsageTUI(App)` : App (L295-494)
- var `BINDINGS = [` (L352)
- var `TITLE = "Usage Metrics TUI"` (L360)
- fn `def __init__(self) -> None` `priv` (L365-376)
- fn `def compose(self) -> ComposeResult` (L377-399)
- fn `async def on_mount(self) -> None` (L400-404)
- fn `async def on_refresh_pressed(self) -> None` (L406-409)
- fn `async def on_5h_pressed(self) -> None` (L411-414)
- fn `async def on_7d_pressed(self) -> None` (L416-419)
- fn `async def action_refresh(self) -> None` (L420-454)
- fn `async def action_window_5h(self) -> None` (L455-461)
- fn `async def action_window_7d(self) -> None` (L462-468)
- fn `async def action_toggle_json(self) -> None` (L469-477)
- fn `def _get_card(self, provider: ProviderName) -> ProviderCard | None` `priv` (L478-485)

### fn `def _update_window_buttons(self) -> None` `priv` (L486-501)

### fn `def _update_json_view(self) -> None` `priv` (L502-511)

### fn `def run_tui() -> None` (L512-517)

## Symbol Index
|Symbol|Kind|Vis|Lines|Sig|
|---|---|---|---|---|
|`ProviderCard`|class|pub|41-240|class ProviderCard(Static)|
|`ProviderCard.__init__`|fn|priv|115-118|def __init__(|
|`ProviderCard.compose`|fn|pub|124-142|def compose(self) -> ComposeResult|
|`ProviderCard.watch_result`|fn|pub|143-227|def watch_result(self, result: ProviderResult | None) -> ...|
|`ProviderCard.watch_is_loading`|fn|pub|228-235|def watch_is_loading(self, loading: bool) -> None|
|`_format_age`|fn|priv|236-244|def _format_age(self, seconds: float) -> str|
|`_format_duration`|fn|priv|245-259|def _format_duration(self, seconds: float) -> str|
|`RawJsonView`|class|pub|260-294|class RawJsonView(Static)|
|`RawJsonView.compose`|fn|pub|279-284|def compose(self) -> ComposeResult|
|`RawJsonView.watch_data`|fn|pub|285-294|def watch_data(self, data: dict | None) -> None|
|`UsageTUI`|class|pub|295-494|class UsageTUI(App)|
|`UsageTUI.BINDINGS`|var|pub|352||
|`UsageTUI.TITLE`|var|pub|360||
|`UsageTUI.__init__`|fn|priv|365-376|def __init__(self) -> None|
|`UsageTUI.compose`|fn|pub|377-399|def compose(self) -> ComposeResult|
|`UsageTUI.on_mount`|fn|pub|400-404|async def on_mount(self) -> None|
|`UsageTUI.on_refresh_pressed`|fn|pub|406-409|async def on_refresh_pressed(self) -> None|
|`UsageTUI.on_5h_pressed`|fn|pub|411-414|async def on_5h_pressed(self) -> None|
|`UsageTUI.on_7d_pressed`|fn|pub|416-419|async def on_7d_pressed(self) -> None|
|`UsageTUI.action_refresh`|fn|pub|420-454|async def action_refresh(self) -> None|
|`UsageTUI.action_window_5h`|fn|pub|455-461|async def action_window_5h(self) -> None|
|`UsageTUI.action_window_7d`|fn|pub|462-468|async def action_window_7d(self) -> None|
|`UsageTUI.action_toggle_json`|fn|pub|469-477|async def action_toggle_json(self) -> None|
|`UsageTUI._get_card`|fn|priv|478-485|def _get_card(self, provider: ProviderName) -> ProviderCa...|
|`_update_window_buttons`|fn|priv|486-501|def _update_window_buttons(self) -> None|
|`_update_json_view`|fn|priv|502-511|def _update_json_view(self) -> None|
|`run_tui`|fn|pub|512-517|def run_tui() -> None|

