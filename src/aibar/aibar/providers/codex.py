"""
@file
@brief OpenAI Codex usage provider and credential helpers.
@details Resolves Codex credentials, refreshes OAuth tokens when required, queries usage endpoints, and normalizes quota metrics.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
import httpx

from aibar.providers.base import (
    AuthenticationError,
    BaseProvider,
    ProviderError,
    ProviderName,
    ProviderResult,
    UsageMetrics,
    WindowPeriod,
)


def _resolve_provider_currency(raw: dict, provider_name: str) -> str:
    """
    @brief Resolve currency symbol from raw API response or configured provider default.
    @details Delegates to `resolve_currency_symbol` in `aibar.config` (lazy import).
    @param raw {dict} Raw API response dict.
    @param provider_name {str} Provider name key.
    @return {str} Resolved currency symbol.
    @satisfies REQ-050
    """
    from aibar.config import resolve_currency_symbol
    return resolve_currency_symbol(raw, provider_name)


class CodexCredentials:
    """
    @brief Define codex credentials component.
    @details Encapsulates codex credentials state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    def __init__(
        self,
        access_token: str,
        refresh_token: str = "",
        id_token: str = "",
        account_id: str | None = None,
        last_refresh: datetime | None = None,
    ) -> None:
        """
        @brief Execute init.
        @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param access_token {str} Input parameter `access_token`.
        @param refresh_token {str} Input parameter `refresh_token`.
        @param id_token {str} Input parameter `id_token`.
        @param account_id {str | None} Input parameter `account_id`.
        @param last_refresh {datetime | None} Input parameter `last_refresh`.
        @return {None} Function return value.
        """
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.id_token = id_token
        self.account_id = account_id
        self.last_refresh = last_refresh or datetime.now(timezone.utc)

    def needs_refresh(self) -> bool:
        """
        @brief Execute needs refresh.
        @details Applies needs refresh logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {bool} Function return value.
        """
        if not self.refresh_token:
            return False
        age = datetime.now(timezone.utc) - self.last_refresh
        return age.days >= 8

    @classmethod
    def from_auth_json(cls, data: dict) -> "CodexCredentials":
        """
        @brief Execute from auth json.
        @details Applies from auth json logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param data {dict} Input parameter `data`.
        @return {'CodexCredentials'} Function return value.
        """
        last_refresh = None
        if lr := data.get("last_refresh"):
            try:
                if isinstance(lr, str):
                    last_refresh = datetime.fromisoformat(lr.replace("Z", "+00:00"))
                elif isinstance(lr, (int, float)):
                    last_refresh = datetime.fromtimestamp(lr, tz=timezone.utc)
            except Exception:
                pass

        return cls(
            access_token=data.get("access_token", ""),
            refresh_token=data.get("refresh_token", ""),
            id_token=data.get("id_token", ""),
            account_id=data.get("account_id"),
            last_refresh=last_refresh,
        )


class CodexCredentialStore:
    """
    @brief Define codex credential store component.
    @details Encapsulates codex credential store state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    @property
    def codex_home(self) -> Path:
        """
        @brief Execute codex home.
        @details Applies codex home logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {Path} Function return value.
        """
        if env_home := os.environ.get("CODEX_HOME"):
            return Path(env_home)
        return Path.home() / ".codex"

    @property
    def auth_file(self) -> Path:
        """
        @brief Execute auth file.
        @details Applies auth file logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {Path} Function return value.
        """
        return self.codex_home / "auth.json"

    def load(self) -> CodexCredentials | None:
        """
        @brief Execute load.
        @details Applies load logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {CodexCredentials | None} Function return value.
        """
        # First check environment variable
        if token := os.environ.get("CODEX_ACCESS_TOKEN"):
            return CodexCredentials(access_token=token)

        # Then check auth.json
        if not self.auth_file.exists():
            return None

        try:
            data = json.loads(self.auth_file.read_text())

            # Handle nested 'tokens' structure (Codex CLI format)
            tokens = data.get("tokens", {})
            if tokens:
                last_refresh = None
                if lr := data.get("last_refresh"):
                    try:
                        last_refresh = datetime.fromisoformat(lr.replace("Z", "+00:00"))
                    except Exception:
                        pass

                return CodexCredentials(
                    access_token=tokens.get("access_token", ""),
                    refresh_token=tokens.get("refresh_token", ""),
                    id_token=tokens.get("id_token", ""),
                    account_id=tokens.get("account_id"),
                    last_refresh=last_refresh,
                )

            # Fallback to flat structure
            return CodexCredentials.from_auth_json(data)
        except Exception:
            return None

    def save(self, credentials: CodexCredentials) -> None:
        """
        @brief Execute save.
        @details Applies save logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param credentials {CodexCredentials} Input parameter `credentials`.
        @return {None} Function return value.
        """
        self.codex_home.mkdir(parents=True, exist_ok=True)

        # Use the nested format to match Codex CLI
        data = {
            "OPENAI_API_KEY": None,
            "tokens": {
                "access_token": credentials.access_token,
                "refresh_token": credentials.refresh_token,
                "id_token": credentials.id_token,
                "account_id": credentials.account_id,
            },
            "last_refresh": credentials.last_refresh.isoformat()
            if credentials.last_refresh
            else None,
        }
        self.auth_file.write_text(json.dumps(data, indent=2))


class CodexTokenRefresher:
    """
    @brief Define codex token refresher component.
    @details Encapsulates codex token refresher state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    REFRESH_URL = "https://auth.openai.com/oauth/token"
    CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"

    async def refresh(self, credentials: CodexCredentials) -> CodexCredentials:
        """
        @brief Execute refresh.
        @details Applies refresh logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param credentials {CodexCredentials} Input parameter `credentials`.
        @return {CodexCredentials} Function return value.
        @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.
        """
        if not credentials.refresh_token:
            return credentials

        from aibar.config import get_api_call_timeout_seconds

        async with httpx.AsyncClient(timeout=get_api_call_timeout_seconds()) as client:
            response = await client.post(
                self.REFRESH_URL,
                headers={"Content-Type": "application/json"},
                json={
                    "client_id": self.CLIENT_ID,
                    "grant_type": "refresh_token",
                    "refresh_token": credentials.refresh_token,
                    "scope": "openid profile email",
                },
            )

            if response.status_code == 401:
                data = response.json()
                error_code = None
                if isinstance(data.get("error"), dict):
                    error_code = data["error"].get("code", "")
                elif isinstance(data.get("error"), str):
                    error_code = data["error"]

                if error_code in (
                    "refresh_token_expired",
                    "refresh_token_reused",
                    "refresh_token_invalidated",
                ):
                    raise AuthenticationError(
                        "Codex refresh token expired. Run 'codex' to re-authenticate."
                    )
                raise AuthenticationError("Codex authentication failed.")

            if response.status_code != 200:
                raise ProviderError(f"Token refresh failed: {response.status_code}")

            data = response.json()

            return CodexCredentials(
                access_token=data.get("access_token", credentials.access_token),
                refresh_token=data.get("refresh_token", credentials.refresh_token),
                id_token=data.get("id_token", credentials.id_token),
                account_id=credentials.account_id,
                last_refresh=datetime.now(timezone.utc),
            )


class CodexProvider(BaseProvider):
    """
    @brief Define codex provider component.
    @details Encapsulates codex provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    name = ProviderName.CODEX

    # API endpoints
    BASE_URL = "https://chatgpt.com/backend-api"
    USAGE_PATH = "/wham/usage"

    def __init__(self, credentials: CodexCredentials | None = None) -> None:
        """
        @brief Execute init.
        @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param credentials {CodexCredentials | None} Input parameter `credentials`.
        @return {None} Function return value.
        """
        self._store = CodexCredentialStore()
        self._refresher = CodexTokenRefresher()
        self._credentials = credentials or self._store.load()

    def is_configured(self) -> bool:
        """
        @brief Execute is configured.
        @details Applies is configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {bool} Function return value.
        """
        return self._credentials is not None and len(self._credentials.access_token) > 0

    def get_config_help(self) -> str:
        """
        @brief Execute get config help.
        @details Applies get config help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {str} Function return value.
        """
        return """OpenAI Codex Provider Configuration:

1. Install Codex CLI and authenticate:
   npm install -g @openai/codex
   codex

2. Credentials will be read from ~/.codex/auth.json

Or set environment variable:
   export CODEX_ACCESS_TOKEN=eyJ...

Note: Token is refreshed automatically when needed."""

    async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult:
        """
        @brief Execute fetch.
        @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param window {WindowPeriod} Input parameter `window`.
        @return {ProviderResult} Function return value.
        @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.
        """
        if not self.is_configured():
            return self._make_error_result(
                window=window,
                error="Not configured. Run 'codex' CLI to authenticate.",
            )

        # Refresh token if needed
        if self._credentials and self._credentials.needs_refresh():
            try:
                self._credentials = await self._refresher.refresh(self._credentials)
                self._store.save(self._credentials)
            except AuthenticationError:
                raise
            except Exception:
                pass  # Continue with existing token

        try:
            from aibar.config import get_api_call_timeout_seconds

            async with httpx.AsyncClient(timeout=get_api_call_timeout_seconds()) as client:
                # Safe to use _credentials here since is_configured() passed
                assert self._credentials is not None

                headers = {
                    "Authorization": f"Bearer {self._credentials.access_token}",
                    "Accept": "application/json",
                    "User-Agent": "aibar",
                }

                # Add account ID if available
                if self._credentials.account_id:
                    headers["ChatGPT-Account-Id"] = self._credentials.account_id

                response = await client.get(
                    f"{self.BASE_URL}{self.USAGE_PATH}",
                    headers=headers,
                )

                if response.status_code in (401, 403):
                    raise AuthenticationError(
                        "Codex token expired. Run 'codex' CLI to re-authenticate."
                    )

                if response.status_code != 200:
                    raw_payload = {
                        "status_code": response.status_code,
                        "body": response.text,
                    }
                    if response.status_code == 429:
                        retry_after_raw = response.headers.get("retry-after")
                        try:
                            raw_payload["retry_after_seconds"] = (
                                max(0.0, float(retry_after_raw))
                                if retry_after_raw is not None
                                else 0.0
                            )
                        except (TypeError, ValueError):
                            raw_payload["retry_after_seconds"] = 0.0
                        raw_payload["retry_after_unavailable"] = (
                            retry_after_raw is None
                        )
                    return self._make_error_result(
                        window=window,
                        error=f"API error: HTTP {response.status_code}",
                        raw=raw_payload,
                    )

                data = response.json()
                return self._parse_response(data, window)

        except AuthenticationError:
            raise
        except httpx.TimeoutException:
            return self._make_error_result(window=window, error="Request timed out")
        except httpx.RequestError as e:
            return self._make_error_result(window=window, error=f"Network error: {e}")
        except Exception as e:
            raise ProviderError(f"Unexpected error: {e}") from e

    def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult:
        """
        @brief Execute parse response.
        @details Applies parse response logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param data {dict} Input parameter `data`.
        @param window {WindowPeriod} Input parameter `window`.
        @return {ProviderResult} Function return value.
        """
        rate_limit = data.get("rate_limit", {})

        # Use primary window (5-hour) or secondary (weekly) based on requested period
        window_key = "primary_window" if window == WindowPeriod.HOUR_5 else "secondary_window"
        window_data = rate_limit.get(window_key) or rate_limit.get("primary_window", {})

        # Parse usage percentage
        used_percent = window_data.get("used_percent")
        remaining = None
        if used_percent is not None:
            remaining = 100.0 - float(used_percent)

        # Parse reset time
        reset_at = None
        if reset_ts := window_data.get("reset_at"):
            try:
                reset_at = datetime.fromtimestamp(reset_ts, tz=timezone.utc)
            except Exception:
                pass

        # Parse credits
        credits = data.get("credits", {})
        cost = None
        if balance := credits.get("balance"):
            try:
                cost = float(balance)
            except (TypeError, ValueError):
                pass

        metrics = UsageMetrics(
            remaining=remaining,
            limit=100.0,  # Percentage-based
            reset_at=reset_at,
            cost=cost,  # Credits balance
            requests=None,
            input_tokens=None,
            output_tokens=None,
            currency_symbol=_resolve_provider_currency(data, ProviderName.CODEX.value),
        )

        return ProviderResult(
            provider=self.name,
            window=window,
            metrics=metrics,
            raw=data,
        )
