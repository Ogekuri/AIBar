"""
@file
@brief Configuration and credential resolution for aibar.
@details Provides environment-file parsing, token precedence resolution, and provider configuration status reporting.
"""

import os
import json
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
DEFAULT_API_CALL_DELAY_SECONDS = 20


class RuntimeConfig(BaseModel):
    """
    @brief Define runtime configuration component for refresh throttling controls.
    @details Encodes persisted CLI runtime controls used by `show` refresh logic.
    Fields are validated as positive integers and default to conservative values
    that reduce rate-limit pressure while preserving configurability.
    @satisfies CTN-008
    """

    idle_delay_seconds: int = Field(default=DEFAULT_IDLE_DELAY_SECONDS, ge=1)
    api_call_delay_seconds: int = Field(default=DEFAULT_API_CALL_DELAY_SECONDS, ge=1)


class IdleTimeState(BaseModel):
    """
    @brief Define persisted idle-time state component.
    @details Stores last successful refresh timestamp and computed idle-until
    timestamp in both epoch and human-readable ISO-8601 UTC formats.
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


def _sanitize_cache_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """
    @brief Redact sensitive keys from cache payload before disk persistence.
    @details Recursively traverses dictionaries/lists and replaces values for
    case-insensitive key matches in `{token,key,secret,password,authorization}`
    with deterministic placeholder string `[REDACTED]`.
    @param payload {dict[str, Any]} Provider payload in `show --json` schema.
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
    when payload root is a JSON object.
    @return {dict[str, Any] | None} Parsed cache payload or None if unavailable.
    @satisfies CTN-004
    """
    try:
        decoded = json.loads(CACHE_FILE_PATH.read_text(encoding="utf-8"))
        if isinstance(decoded, dict):
            return decoded
    except (OSError, ValueError):
        return None
    return None


def save_cli_cache(payload: dict[str, Any]) -> None:
    """
    @brief Persist CLI cache payload in the canonical `show --json` schema.
    @details Redacts sensitive keys from provider raw payloads, then writes
    sanitized payload to `~/.cache/aibar/cache.json` using pretty-printed JSON
    (`indent=2`) so the file matches CLI JSON rendering format exactly.
    @param payload {dict[str, Any]} Cache payload in `show --json` shape.
    @return {None} Function return value.
    @satisfies CTN-004
    @satisfies DES-004
    """
    sanitized_payload = _sanitize_cache_payload(payload)
    _ensure_app_cache_dir()
    CACHE_FILE_PATH.write_text(
        json.dumps(sanitized_payload, indent=2),
        encoding="utf-8",
    )


def load_idle_time() -> IdleTimeState | None:
    """
    @brief Load idle-time control state from disk.
    @details Reads and validates `~/.cache/aibar/idle-time.json`. Invalid or
    unreadable payloads return None and are treated as missing state.
    @return {IdleTimeState | None} Validated idle-time state or None.
    @satisfies CTN-009
    """
    try:
        decoded = json.loads(IDLE_TIME_PATH.read_text(encoding="utf-8"))
        if isinstance(decoded, dict):
            return IdleTimeState.model_validate(decoded)
    except (OSError, ValueError, ValidationError):
        return None
    return None


def save_idle_time(last_success_at: datetime, idle_until: datetime) -> IdleTimeState:
    """
    @brief Persist idle-time state using epoch and human-readable timestamp fields.
    @details Normalizes timestamps to UTC, serializes both epoch and ISO strings,
    and writes `~/.cache/aibar/idle-time.json` in pretty-printed JSON.
    @param last_success_at {datetime} Last successful refresh timestamp.
    @param idle_until {datetime} Timestamp until refresh must remain disabled.
    @return {IdleTimeState} Persisted idle-time model.
    @satisfies CTN-009
    """
    last_success_utc = last_success_at.astimezone(timezone.utc)
    idle_until_utc = idle_until.astimezone(timezone.utc)
    state = IdleTimeState(
        last_success_timestamp=int(last_success_utc.timestamp()),
        last_success_human=last_success_utc.isoformat(),
        idle_until_timestamp=int(idle_until_utc.timestamp()),
        idle_until_human=idle_until_utc.isoformat(),
    )
    _ensure_app_cache_dir()
    IDLE_TIME_PATH.write_text(
        state.model_dump_json(indent=2),
        encoding="utf-8",
    )
    return state


def remove_idle_time_file() -> None:
    """
    @brief Remove persisted idle-time state file if present.
    @details Deletes `~/.cache/aibar/idle-time.json` to force immediate refresh
    behavior on subsequent `show` execution.
    @return {None} Function return value.
    @satisfies REQ-039
    """
    try:
        IDLE_TIME_PATH.unlink(missing_ok=True)
    except OSError:
        return


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
        )

        provider_map = {
            ProviderName.CLAUDE: ClaudeOAuthProvider,
            ProviderName.OPENAI: OpenAIUsageProvider,
            ProviderName.OPENROUTER: OpenRouterUsageProvider,
            ProviderName.COPILOT: CopilotProvider,
            ProviderName.CODEX: CodexProvider,
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
