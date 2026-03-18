"""
@file
@brief Configuration and credential resolution for aibar.
@details Provides environment-file parsing, token precedence resolution, and provider configuration status reporting.
"""

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

# Runtime/config file locations
APP_CONFIG_DIR = Path.home() / ".config" / "aibar"
APP_CACHE_DIR = Path.home() / ".cache" / "aibar"
ENV_FILE_PATH = APP_CONFIG_DIR / "env"
RUNTIME_CONFIG_PATH = APP_CONFIG_DIR / "config.json"
CACHE_FILE_PATH = APP_CACHE_DIR / "cache.json"
IDLE_TIME_PATH = APP_CACHE_DIR / "idle-time.json"

DEFAULT_IDLE_DELAY_SECONDS = 300
DEFAULT_API_CALL_DELAY_MILLISECONDS = 100
DEFAULT_API_CALL_TIMEOUT_MILLISECONDS = 3000
DEFAULT_GNOME_REFRESH_INTERVAL_SECONDS = 60
DEFAULT_BILLING_DATASET = "billing_data"
DEFAULT_CURRENCY_SYMBOL = "$"
VALID_CURRENCY_SYMBOLS: tuple[str, ...] = ("$", "£", "€")
LOCK_POLL_INTERVAL_SECONDS = 0.25

_CURRENCY_CODE_TO_SYMBOL: dict[str, str] = {
    "USD": "$",
    "GBP": "£",
    "EUR": "€",
}


class RuntimeConfig(BaseModel):
    """
    @brief Define runtime configuration component for refresh throttling, timeout, and currency controls.
    @details Encodes persisted CLI runtime controls used by `show` refresh logic,
    GNOME extension scheduling, and per-provider currency symbol resolution.
    Fields are validated with defaults that reduce rate-limit pressure.
    `api_call_delay_milliseconds` defaults to `100` ms inter-call spacing.
    `api_call_timeout_milliseconds` defaults to `3000` ms HTTP response timeout
    applied to all provider API calls via `httpx.AsyncClient(timeout=<value>/1000.0)`.
    `currency_symbols` maps provider name strings to currency symbols (`$`, `£`, `€`);
    missing entries default to `DEFAULT_CURRENCY_SYMBOL` at resolution time.
    `billing_data` stores the Google BigQuery dataset name used for GeminiAI
    billing export table discovery.
    Optional GeminiAI field persists Google Cloud project identifier used by
    OAuth-backed Monitoring API fetch execution.
    @satisfies CTN-008
    @satisfies REQ-049
    @satisfies REQ-095
    @satisfies REQ-096
    """

    idle_delay_seconds: int = Field(default=DEFAULT_IDLE_DELAY_SECONDS, ge=1)
    api_call_delay_milliseconds: int = Field(default=DEFAULT_API_CALL_DELAY_MILLISECONDS, ge=1)
    api_call_timeout_milliseconds: int = Field(default=DEFAULT_API_CALL_TIMEOUT_MILLISECONDS, ge=1)
    gnome_refresh_interval_seconds: int = Field(default=DEFAULT_GNOME_REFRESH_INTERVAL_SECONDS, ge=1)
    billing_data: str = Field(default=DEFAULT_BILLING_DATASET, min_length=1)
    currency_symbols: dict[str, str] = Field(default_factory=dict)
    geminiai_project_id: str | None = Field(default=None)


class IdleTimeState(BaseModel):
    """
    @brief Define persisted idle-time entry for one provider.
    @details Stores provider-local last-success and idle-until timestamps in
    epoch-seconds and local-timezone ISO-8601 formats. Serialized as one value
    under provider key in `~/.cache/aibar/idle-time.json`.
    @satisfies CTN-009
    """

    last_success_timestamp: int
    last_success_human: str
    idle_until_timestamp: int
    idle_until_human: str


def _ensure_app_config_dir() -> None:
    """
    @brief Ensure AIBar configuration directory exists before file persistence.
    @details Creates `~/.config/aibar` recursively when missing. This function is
    called by env-file and runtime-config persistence helpers.
    @return {None} Function return value.
    """
    APP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_app_cache_dir() -> None:
    """
    @brief Ensure AIBar cache directory exists before cache and idle-time persistence.
    @details Creates `~/.cache/aibar` recursively when missing. This function is
    called by CLI cache and idle-time persistence helpers.
    @return {None} Function return value.
    """
    APP_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _lock_file_path(target_path: Path) -> Path:
    """
    @brief Resolve lock-file path for one cache artifact.
    @details Produces deterministic lock-file names under `~/.cache/aibar/`
    using `<filename>.lock` to coordinate cross-process read/write exclusion.
    @param target_path {Path} Cache file path guarded by lock.
    @return {Path} Absolute lock-file path.
    @satisfies REQ-066
    """
    return APP_CACHE_DIR / f"{target_path.name}.lock"


@contextmanager
def _blocking_file_lock(target_path: Path):
    """
    @brief Acquire and release blocking lock-file for cache artifact I/O.
    @details Uses atomic `O_CREAT|O_EXCL` lock-file creation. When lock-file
    already exists, polls every `250ms` until lock release, then acquires lock.
    Always removes owned lock-file during exit.
    @param target_path {Path} Cache artifact path protected by this lock.
    @return {Iterator[None]} Context manager yielding while lock is held.
    @satisfies REQ-066
    """
    _ensure_app_cache_dir()
    lock_path = _lock_file_path(target_path)
    while True:
        try:
            lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(lock_fd, "w", encoding="utf-8") as lock_file:
                lock_file.write(f"{os.getpid()}\n")
            break
        except FileExistsError:
            time.sleep(LOCK_POLL_INTERVAL_SECONDS)
    try:
        yield
    finally:
        try:
            lock_path.unlink(missing_ok=True)
        except OSError:
            pass


def _sanitize_cache_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """
    @brief Redact sensitive keys from cache payload before disk persistence.
    @details Recursively traverses dictionaries/lists and replaces values for
    case-insensitive key matches in `{token,key,secret,password,authorization}`
    with deterministic placeholder string `[REDACTED]`.
    @param payload {dict[str, Any]} Cache document containing `payload` and `status` sections.
    @return {dict[str, Any]} Sanitized deep-copy structure safe for persistence.
    @satisfies DES-004
    """
    sensitive_keys = {"token", "key", "secret", "password", "authorization"}

    def clean(value: Any) -> Any:
        """
        @brief Apply recursive redaction to one JSON-compatible node.
        @details Preserves structural type (dict/list/scalar) while replacing
        values of sensitive keys with `[REDACTED]`.
        @param value {Any} JSON-like node to sanitize.
        @return {Any} Sanitized node.
        """
        if isinstance(value, dict):
            sanitized: dict[str, Any] = {}
            for key, node in value.items():
                if isinstance(key, str) and key.lower() in sensitive_keys:
                    sanitized[key] = "[REDACTED]"
                else:
                    sanitized[key] = clean(node)
            return sanitized
        if isinstance(value, list):
            return [clean(item) for item in value]
        return value

    return clean(payload)


def load_runtime_config() -> RuntimeConfig:
    """
    @brief Load runtime refresh configuration from disk with schema validation.
    @details Reads `~/.config/aibar/config.json`, validates fields against
    `RuntimeConfig`, and returns defaults when file is missing or invalid.
    @return {RuntimeConfig} Validated runtime configuration payload.
    @satisfies CTN-008
    """
    try:
        decoded = json.loads(RUNTIME_CONFIG_PATH.read_text(encoding="utf-8"))
        if isinstance(decoded, dict):
            return RuntimeConfig.model_validate(decoded)
    except (OSError, ValueError, ValidationError):
        pass
    return RuntimeConfig()


def save_runtime_config(runtime_config: RuntimeConfig) -> None:
    """
    @brief Persist runtime refresh configuration to disk.
    @details Serializes `RuntimeConfig` to `~/.config/aibar/config.json` using
    stable pretty-printed JSON (`indent=2`) for deterministic readability.
    @param runtime_config {RuntimeConfig} Validated runtime configuration model.
    @return {None} Function return value.
    @satisfies CTN-008
    """
    _ensure_app_config_dir()
    RUNTIME_CONFIG_PATH.write_text(
        runtime_config.model_dump_json(indent=2),
        encoding="utf-8",
    )


def load_cli_cache() -> dict[str, Any] | None:
    """
    @brief Load CLI cache payload from disk.
    @details Reads `~/.cache/aibar/cache.json` and returns parsed object only
    when payload root is a JSON object with canonical cache sections.
    @return {dict[str, Any] | None} Parsed cache payload or None if unavailable.
    @satisfies CTN-004
    @satisfies REQ-047
    @satisfies REQ-066
    """
    try:
        with _blocking_file_lock(CACHE_FILE_PATH):
            decoded = json.loads(CACHE_FILE_PATH.read_text(encoding="utf-8"))
            if isinstance(decoded, dict):
                return decoded
    except (OSError, ValueError):
        return None
    return None


def resolve_currency_symbol(raw: dict[str, Any] | None, provider_name: str) -> str:
    """
    @brief Resolve currency symbol for a provider result from API response or config.
    @details Extraction priority:
    1. `raw["currency"]` field: if a recognized symbol (`$`, `£`, `€`) → use directly;
       if an ISO-4217 code (`USD`, `GBP`, `EUR`) → map to symbol.
    2. `RuntimeConfig.currency_symbols[provider_name]` configured default.
    3. `DEFAULT_CURRENCY_SYMBOL` (`"$"`) as final fallback.
    @param raw {dict[str, Any] | None} Raw API response dict from the provider fetch call, or None.
    @param provider_name {str} Provider name string key (e.g. `"claude"`, `"openai"`).
    @return {str} Resolved currency symbol; always a member of `VALID_CURRENCY_SYMBOLS`.
    @satisfies REQ-050
    """
    raw_currency = raw.get("currency") if isinstance(raw, dict) else None
    if isinstance(raw_currency, str):
        if raw_currency in VALID_CURRENCY_SYMBOLS:
            return raw_currency
        mapped = _CURRENCY_CODE_TO_SYMBOL.get(raw_currency.upper())
        if mapped is not None:
            return mapped
    try:
        runtime_config = load_runtime_config()
        symbol = runtime_config.currency_symbols.get(provider_name, DEFAULT_CURRENCY_SYMBOL)
        if symbol in VALID_CURRENCY_SYMBOLS:
            return symbol
    except Exception:  # noqa: BLE001
        pass
    return DEFAULT_CURRENCY_SYMBOL


def save_cli_cache(payload: dict[str, Any]) -> None:
    """
    @brief Persist canonical cache document to disk.
    @details Redacts sensitive keys from nested raw payload objects, then writes
    sanitized cache document to `~/.cache/aibar/cache.json` using pretty-printed
    JSON (`indent=2`) preserving `payload` and `status` sections.
    @param payload {dict[str, Any]} Canonical cache document.
    @return {None} Function return value.
    @satisfies CTN-004
    @satisfies DES-004
    @satisfies REQ-044
    @satisfies REQ-045
    @satisfies REQ-046
    @satisfies REQ-047
    @satisfies REQ-066
    """
    sanitized_payload = _sanitize_cache_payload(payload)
    with _blocking_file_lock(CACHE_FILE_PATH):
        CACHE_FILE_PATH.write_text(
            json.dumps(sanitized_payload, indent=2),
            encoding="utf-8",
        )


def build_idle_time_state(last_success_at: datetime, idle_until: datetime) -> IdleTimeState:
    """
    @brief Build provider-local idle-time entry from UTC-compatible datetimes.
    @details Normalizes timestamps to UTC for epoch conversion, then emits
    human-readable ISO-8601 values in runtime local timezone for deterministic
    parity with CLI/GNOME freshness rendering.
    @param last_success_at {datetime} Last successful refresh timestamp.
    @param idle_until {datetime} Timestamp until provider refresh remains gated.
    @return {IdleTimeState} Normalized provider idle-time entry.
    @satisfies CTN-009
    """
    last_success_utc = last_success_at.astimezone(timezone.utc)
    idle_until_utc = idle_until.astimezone(timezone.utc)
    last_success_timestamp = int(last_success_utc.timestamp())
    idle_until_timestamp = int(idle_until_utc.timestamp())
    local_timezone = datetime.now().astimezone().tzinfo
    assert local_timezone is not None
    last_success_local = datetime.fromtimestamp(
        last_success_timestamp,
        tz=local_timezone,
    )
    idle_until_local = datetime.fromtimestamp(
        idle_until_timestamp,
        tz=local_timezone,
    )
    return IdleTimeState(
        last_success_timestamp=last_success_timestamp,
        last_success_human=last_success_local.isoformat(),
        idle_until_timestamp=idle_until_timestamp,
        idle_until_human=idle_until_local.isoformat(),
    )


def load_idle_time() -> dict[str, IdleTimeState]:
    """
    @brief Load provider-keyed idle-time state from disk.
    @details Reads `~/.cache/aibar/idle-time.json` and validates each provider
    value as `IdleTimeState`. Invalid provider entries are ignored. Missing or
    unreadable payloads return an empty map.
    @return {dict[str, IdleTimeState]} Provider-keyed idle-time state map.
    @satisfies CTN-009
    @satisfies REQ-066
    """
    parsed_state: dict[str, IdleTimeState] = {}
    try:
        with _blocking_file_lock(IDLE_TIME_PATH):
            decoded = json.loads(IDLE_TIME_PATH.read_text(encoding="utf-8"))
            if isinstance(decoded, dict):
                for provider_key, raw_state in decoded.items():
                    if not isinstance(provider_key, str):
                        continue
                    if not isinstance(raw_state, dict):
                        continue
                    try:
                        parsed_state[provider_key] = IdleTimeState.model_validate(raw_state)
                    except ValidationError:
                        continue
    except (OSError, ValueError, ValidationError):
        return {}
    return parsed_state


def save_idle_time(idle_time_by_provider: dict[str, IdleTimeState]) -> dict[str, IdleTimeState]:
    """
    @brief Persist provider-keyed idle-time state map.
    @details Validates each provider entry, serializes canonical epoch and
    ISO-8601 fields, and writes `~/.cache/aibar/idle-time.json` in pretty-printed JSON.
    Invalid map entries are skipped.
    @param idle_time_by_provider {dict[str, IdleTimeState]} Provider-keyed idle-time map.
    @return {dict[str, IdleTimeState]} Persisted provider-keyed idle-time map.
    @satisfies CTN-009
    @satisfies REQ-066
    """
    normalized_state: dict[str, IdleTimeState] = {}
    serialized_state: dict[str, dict[str, object]] = {}
    for provider_key, provider_state in idle_time_by_provider.items():
        if not isinstance(provider_key, str):
            continue
        try:
            validated_state = (
                provider_state
                if isinstance(provider_state, IdleTimeState)
                else IdleTimeState.model_validate(provider_state)
            )
        except ValidationError:
            continue
        normalized_state[provider_key] = validated_state
        serialized_state[provider_key] = validated_state.model_dump(mode="json")
    with _blocking_file_lock(IDLE_TIME_PATH):
        IDLE_TIME_PATH.write_text(
            json.dumps(serialized_state, indent=2),
            encoding="utf-8",
        )
    return normalized_state


def remove_idle_time_file() -> None:
    """
    @brief Remove persisted idle-time state file if present.
    @details Deletes `~/.cache/aibar/idle-time.json` to force immediate refresh
    behavior on subsequent `show` execution.
    @return {None} Function return value.
    @satisfies REQ-039
    @satisfies REQ-066
    """
    try:
        with _blocking_file_lock(IDLE_TIME_PATH):
            IDLE_TIME_PATH.unlink(missing_ok=True)
    except OSError:
        return


def get_api_call_timeout_seconds() -> float:
    """
    @brief Resolve HTTP response timeout in seconds from runtime configuration.
    @details Reads `api_call_timeout_milliseconds` from `RuntimeConfig` and converts
    to seconds. Returns `DEFAULT_API_CALL_TIMEOUT_MILLISECONDS / 1000.0` when
    configuration is missing or invalid.
    @return {float} HTTP response timeout in seconds (>= 0.001).
    @satisfies REQ-095
    @satisfies CTN-003
    """
    try:
        runtime_config = load_runtime_config()
        return max(0.001, runtime_config.api_call_timeout_milliseconds / 1000.0)
    except Exception:  # noqa: BLE001
        return DEFAULT_API_CALL_TIMEOUT_MILLISECONDS / 1000.0


def load_env_file() -> dict[str, str]:
    """
    @brief Execute load env file.
    @details Applies load env file logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {dict[str, str]} Function return value.
    """
    result: dict[str, str] = {}
    try:
        if ENV_FILE_PATH.exists():
            for line in ENV_FILE_PATH.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    result[key.strip()] = value.strip()
    except (OSError, PermissionError):
        pass
    return result


def write_env_file(updates: dict[str, str]) -> None:
    """
    @brief Execute write env file.
    @details Applies write env file logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @param updates {dict[str, str]} Input parameter `updates`.
    @return {None} Function return value.
    """
    ENV_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

    existing_lines: list[str] = []
    existing_keys: set[str] = set()

    try:
        if ENV_FILE_PATH.exists():
            existing_lines = ENV_FILE_PATH.read_text().splitlines()
    except (OSError, PermissionError):
        pass

    new_lines: list[str] = []
    for line in existing_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key, _, _ = stripped.partition("=")
            key = key.strip()
            if key in updates:
                new_lines.append(f"{key}={updates[key]}")
                existing_keys.add(key)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    # Add new keys not already in file
    for key, value in updates.items():
        if key not in existing_keys:
            new_lines.append(f"{key}={value}")

    ENV_FILE_PATH.write_text("\n".join(new_lines) + "\n")


class Config:
    """
    @brief Define config component.
    @details Encapsulates config state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    # Environment variable mappings
    ENV_VARS = {
        ProviderName.CLAUDE: "CLAUDE_CODE_OAUTH_TOKEN",
        ProviderName.OPENAI: "OPENAI_ADMIN_KEY",
        ProviderName.OPENROUTER: "OPENROUTER_API_KEY",
        ProviderName.COPILOT: "GITHUB_TOKEN",
        ProviderName.CODEX: "CODEX_ACCESS_TOKEN",
        ProviderName.GEMINIAI: "GEMINIAI_OAUTH_ACCESS_TOKEN",
    }

    # Provider descriptions
    PROVIDER_INFO = {
        ProviderName.CLAUDE: {
            "name": "Claude Code",
            "description": "Claude Code subscription quota via OAuth",
            "official": False,
            "note": "Uses unofficial OAuth endpoint with beta header",
        },
        ProviderName.OPENAI: {
            "name": "OpenAI",
            "description": "OpenAI API usage and costs",
            "official": True,
            "note": "Requires organization admin API key",
        },
        ProviderName.OPENROUTER: {
            "name": "OpenRouter",
            "description": "OpenRouter API credits and usage",
            "official": True,
            "note": "Uses /api/v1/key for credits and limits",
        },
        ProviderName.COPILOT: {
            "name": "GitHub Copilot",
            "description": "GitHub Copilot quota via internal API",
            "official": False,
            "note": "Uses VS Code client ID for device flow auth",
        },
        ProviderName.CODEX: {
            "name": "OpenAI Codex",
            "description": "OpenAI Codex usage via ChatGPT backend",
            "official": False,
            "note": "Reads credentials from ~/.codex/auth.json",
        },
        ProviderName.GEMINIAI: {
            "name": "GeminiAI",
            "description": "Google Gemini API usage via OAuth",
            "official": True,
            "note": "Uses Google Cloud Monitoring API",
        },
    }

    def get_token(self, provider: ProviderName) -> str | None:
        """
        @brief Execute get token.
        @details Applies get token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param provider {ProviderName} Input parameter `provider`.
        @return {str | None} Function return value.
        """
        env_var = self.ENV_VARS.get(provider)

        # 1. Check environment variable (highest priority)
        if env_var and (token := os.environ.get(env_var)):
            return token

        # 2. Check env file
        if env_var:
            env_file_values = load_env_file()
            if token := env_file_values.get(env_var):
                return token

        # 3. Provider-specific credential stores
        if provider == ProviderName.CLAUDE:
            return extract_claude_cli_token()

        if provider == ProviderName.CODEX:
            from aibar.providers.codex import CodexCredentialStore

            store = CodexCredentialStore()
            creds = store.load()
            return creds.access_token if creds else None

        if provider == ProviderName.COPILOT:
            from aibar.providers.copilot import CopilotCredentialStore

            store = CopilotCredentialStore()
            return store.load_token()

        if provider == ProviderName.GEMINIAI:
            from aibar.providers.geminiai import GeminiAICredentialStore

            store = GeminiAICredentialStore()
            return store.load_access_token()

        return None

    def is_provider_configured(self, provider: ProviderName) -> bool:
        """
        @brief Execute is provider configured.
        @details Applies is provider configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param provider {ProviderName} Input parameter `provider`.
        @return {bool} Function return value.
        """
        # Import providers lazily to avoid circular imports
        from aibar.providers import (
            ClaudeOAuthProvider,
            OpenAIUsageProvider,
            OpenRouterUsageProvider,
            CopilotProvider,
            CodexProvider,
            GeminiAIProvider,
        )

        provider_map = {
            ProviderName.CLAUDE: ClaudeOAuthProvider,
            ProviderName.OPENAI: OpenAIUsageProvider,
            ProviderName.OPENROUTER: OpenRouterUsageProvider,
            ProviderName.COPILOT: CopilotProvider,
            ProviderName.CODEX: CodexProvider,
            ProviderName.GEMINIAI: GeminiAIProvider,
        }

        provider_class = provider_map.get(provider)
        if provider_class:
            return provider_class().is_configured()

        return False

    def get_provider_status(self, provider: ProviderName) -> dict[str, Any]:
        """
        @brief Execute get provider status.
        @details Applies get provider status logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param provider {ProviderName} Input parameter `provider`.
        @return {dict[str, Any]} Function return value.
        """
        info = self.PROVIDER_INFO.get(provider, {})
        env_var = self.ENV_VARS.get(provider, "UNKNOWN")
        configured = self.is_provider_configured(provider)

        return {
            "provider": provider.value,
            "name": info.get("name", provider.value),
            "description": info.get("description", ""),
            "official": info.get("official", False),
            "note": info.get("note", ""),
            "env_var": env_var,
            "configured": configured,
            "token_preview": self._get_token_preview(provider) if configured else None,
        }

    def get_all_provider_status(self) -> list[dict[str, Any]]:
        """
        @brief Execute get all provider status.
        @details Applies get all provider status logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {list[dict[str, Any]]} Function return value.
        """
        return [self.get_provider_status(p) for p in ProviderName]

    def _get_token_preview(self, provider: ProviderName) -> str | None:
        """
        @brief Execute get token preview.
        @details Applies get token preview logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param provider {ProviderName} Input parameter `provider`.
        @return {str | None} Function return value.
        """
        token = self.get_token(provider)
        if not token or len(token) < 12:
            return None
        return f"{token[:8]}...{token[-4:]}"

    def get_env_var_help(self) -> str:
        """
        @brief Execute get env var help.
        @details Applies get env var help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {str} Function return value.
        """
        lines = ["Required environment variables:\n"]

        for provider in ProviderName:
            env_var = self.ENV_VARS.get(provider)
            info = self.PROVIDER_INFO.get(provider, {})
            configured = self.is_provider_configured(provider)
            status = "[OK]" if configured else "[NOT SET]"

            lines.append(f"  {env_var}  {status}")
            lines.append(f"    {info.get('description', '')}")
            if note := info.get("note"):
                lines.append(f"    Note: {note}")
            lines.append("")

        return "\n".join(lines)


# Global config instance
config = Config()
