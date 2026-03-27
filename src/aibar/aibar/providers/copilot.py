"""
@file
@brief GitHub Copilot usage provider and device-flow authentication.
@details Handles device-code authorization, token storage resolution, Copilot quota retrieval, and normalization to provider result schema.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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


class CopilotDeviceFlow:
    """
    @brief Define copilot device flow component.
    @details Encapsulates copilot device flow state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    # VS Code's public client ID for Copilot
    CLIENT_ID = "Iv1.b507a08c87ecfe98"
    SCOPES = "read:user"

    DEVICE_CODE_URL = "https://github.com/login/device/code"
    TOKEN_URL = "https://github.com/login/oauth/access_token"

    async def request_device_code(self) -> dict[str, Any]:
        """
        @brief Execute request device code.
        @details Applies request device code logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {dict[str, Any]} Function return value.
        @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.
        """
        from aibar.config import get_api_call_timeout_seconds

        async with httpx.AsyncClient(timeout=get_api_call_timeout_seconds()) as client:
            response = await client.post(
                self.DEVICE_CODE_URL,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "client_id": self.CLIENT_ID,
                    "scope": self.SCOPES,
                },
            )

            if response.status_code != 200:
                raise ProviderError(f"Failed to request device code: {response.status_code}")

            return response.json()

    async def poll_for_token(self, device_code: str, interval: int = 5) -> str:
        """
        @brief Execute poll for token.
        @details Applies poll for token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param device_code {str} Input parameter `device_code`.
        @param interval {int} Input parameter `interval`.
        @return {str} Function return value.
        @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.
        """
        import asyncio

        from aibar.config import get_api_call_timeout_seconds

        async with httpx.AsyncClient(timeout=get_api_call_timeout_seconds()) as client:
            while True:
                await asyncio.sleep(interval)

                response = await client.post(
                    self.TOKEN_URL,
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    data={
                        "client_id": self.CLIENT_ID,
                        "device_code": device_code,
                        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    },
                )

                data = response.json()

                if "access_token" in data:
                    return data["access_token"]

                # Handle errors
                if "error" not in data:
                    continue

                error = data["error"]
                if error == "authorization_pending":
                    continue
                if error == "slow_down":
                    interval += 5
                    continue
                if error == "expired_token":
                    raise AuthenticationError("Device code expired. Please try again.")
                if error == "access_denied":
                    raise AuthenticationError("Authorization denied by user.")

                raise AuthenticationError(f"Authorization failed: {error}")


class CopilotCredentialStore:
    """
    @brief Define copilot credential store component.
    @details Encapsulates copilot credential store state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    CONFIG_DIR = Path.home() / ".config" / "aibar"
    CREDS_FILE = CONFIG_DIR / "copilot.json"
    CODEXBAR_CONFIG = Path.home() / ".codexbar" / "config.json"

    def load_token(self) -> str | None:
        """
        @brief Execute load token.
        @details Applies load token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {str | None} Function return value.
        """
        # 1. Environment variable
        if token := os.environ.get("GITHUB_TOKEN"):
            return token

        # 2. Our credentials file
        if self.CREDS_FILE.exists():
            try:
                data = json.loads(self.CREDS_FILE.read_text())
                if token := data.get("access_token"):
                    return token
            except Exception:
                pass

        # 3. CodexBar config
        if self.CODEXBAR_CONFIG.exists():
            try:
                data = json.loads(self.CODEXBAR_CONFIG.read_text())
                for provider in data.get("providers", []):
                    if provider.get("id") == "copilot":
                        if token := provider.get("apiKey"):
                            return token
            except Exception:
                pass

        return None

    def save_token(self, token: str) -> None:
        """
        @brief Execute save token.
        @details Applies save token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param token {str} Input parameter `token`.
        @return {None} Function return value.
        """
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "access_token": token,
            "saved_at": datetime.now().isoformat(),
        }
        self.CREDS_FILE.write_text(json.dumps(data, indent=2))


class CopilotProvider(BaseProvider):
    """
    @brief Define copilot provider component.
    @details Encapsulates copilot provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    name = ProviderName.COPILOT
    USAGE_URL = "https://api.github.com/copilot_internal/user"

    # Headers that mimic VS Code Copilot extension
    EDITOR_VERSION = "vscode/1.96.2"
    PLUGIN_VERSION = "copilot-chat/0.26.7"
    USER_AGENT = "GitHubCopilotChat/0.26.7"
    API_VERSION = "2025-04-01"

    def __init__(self, token: str | None = None) -> None:
        """
        @brief Execute init.
        @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param token {str | None} Input parameter `token`.
        @return {None} Function return value.
        """
        self._store = CopilotCredentialStore()
        self._token = token or self._store.load_token()

    def is_configured(self) -> bool:
        """
        @brief Execute is configured.
        @details Applies is configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {bool} Function return value.
        """
        return self._token is not None and len(self._token) > 0

    def get_config_help(self) -> str:
        """
        @brief Execute get config help.
        @details Applies get config help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {str} Function return value.
        """
        return """GitHub Copilot Provider Configuration:

1. Run: aibar login --provider copilot
2. Follow the browser authorization flow
3. Token will be saved automatically

Or set environment variable:
   export GITHUB_TOKEN=ghp_...

Note: Token needs 'read:user' scope."""

    async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult:
        """
        @brief Execute fetch.
        @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param window {WindowPeriod} Input parameter `window`.
        @return {ProviderResult} Function return value.
        @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.
        """
        effective_window = WindowPeriod.DAY_30
        if not self.is_configured():
            return self._make_error_result(
                window=effective_window,
                error="Not configured. Run 'aibar login --provider copilot'",
            )

        try:
            from aibar.config import get_api_call_timeout_seconds

            async with httpx.AsyncClient(timeout=get_api_call_timeout_seconds()) as client:
                response = await client.get(
                    self.USAGE_URL,
                    headers={
                        "Authorization": f"token {self._token}",
                        "Accept": "application/json",
                        "Editor-Version": self.EDITOR_VERSION,
                        "Editor-Plugin-Version": self.PLUGIN_VERSION,
                        "User-Agent": self.USER_AGENT,
                        "X-Github-Api-Version": self.API_VERSION,
                    },
                )

                if response.status_code in (401, 403):
                    raise AuthenticationError(
                        "GitHub token invalid or lacks Copilot access. "
                        "Run 'aibar login --provider copilot'"
                    )

                if response.status_code == 404:
                    return self._make_error_result(
                        window=effective_window,
                        error="Copilot not enabled for this account",
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
                        window=effective_window,
                        error=f"API error: HTTP {response.status_code}",
                        raw=raw_payload,
                    )

                data = response.json()
                return self._parse_response(data, effective_window)

        except AuthenticationError:
            raise
        except httpx.TimeoutException:
            return self._make_error_result(window=effective_window, error="Request timed out")
        except httpx.RequestError as e:
            return self._make_error_result(window=effective_window, error=f"Network error: {e}")
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
        quota = data.get("quotaSnapshots") or data.get("quota_snapshots") or {}

        def _get_snapshot(key_camel: str, key_snake: str) -> dict:
            """
            @brief Execute get snapshot.
            @details Applies get snapshot logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
            @param key_camel {str} Input parameter `key_camel`.
            @param key_snake {str} Input parameter `key_snake`.
            @return {dict} Function return value.
            """
            return quota.get(key_camel) or quota.get(key_snake) or {}

        def _extract_quota_data(snapshot: dict) -> tuple[float | None, float | None]:
            """
            @brief Execute extract quota data.
            @details Applies extract quota data logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
            @param snapshot {dict} Input parameter `snapshot`.
            @return {tuple[float | None, float | None]} Function return value.
            """
            # Try to get actual credit numbers first
            entitlement = snapshot.get("entitlement")
            quota_remaining = snapshot.get("quota_remaining") or snapshot.get("remaining")

            if entitlement is not None and quota_remaining is not None:
                try:
                    return (float(quota_remaining), float(entitlement))
                except (TypeError, ValueError):
                    pass

            # Fall back to percentage if available
            percent = snapshot.get("percentRemaining") or snapshot.get("percent_remaining")
            if percent is not None:
                try:
                    return (float(percent), 100.0)
                except (TypeError, ValueError):
                    pass

            return (None, None)

        # Try quota snapshots in priority order
        snapshots_to_try = [
            ("premiumInteractions", "premium_interactions"),
            ("chat", "chat"),
            ("completions", "completions"),
        ]

        remaining = None
        limit = None
        for camel, snake in snapshots_to_try:
            snapshot = _get_snapshot(camel, snake)
            remaining, limit = _extract_quota_data(snapshot)
            if remaining is not None:
                break

        # Parse reset date from various possible field names
        reset_raw = (
            data.get("quota_reset_date_utc")
            or data.get("quotaResetDateUtc")
            or data.get("quota_reset_date")
            or data.get("quotaResetDate")
        )

        reset_at = None
        if reset_raw:
            try:
                reset_at = datetime.fromisoformat(str(reset_raw).replace("Z", "+00:00"))
                if reset_at.tzinfo is None:
                    reset_at = reset_at.replace(tzinfo=timezone.utc)
            except ValueError:
                pass

        metrics = UsageMetrics(
            remaining=remaining,
            limit=limit,
            reset_at=reset_at,
            cost=None,
            requests=None,
            input_tokens=None,
            output_tokens=None,
            currency_symbol=_resolve_provider_currency(data, ProviderName.COPILOT.value),
        )

        return ProviderResult(
            provider=self.name,
            window=window,
            metrics=metrics,
            raw=data,
        )

    async def login(self) -> str:
        """
        @brief Execute login.
        @details Applies login logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {str} Function return value.
        """
        flow = CopilotDeviceFlow()

        # Request device code
        device_response = await flow.request_device_code()

        user_code = device_response["user_code"]
        verification_uri = device_response["verification_uri"]
        interval = device_response.get("interval", 5)
        device_code = device_response["device_code"]

        # Display instructions to user
        print("\nTo authorize GitHub Copilot access:")
        print(f"  1. Open: {verification_uri}")
        print(f"  2. Enter code: {user_code}")
        print("\nWaiting for authorization...")

        # Poll for token
        token = await flow.poll_for_token(device_code, interval)

        # Save token
        self._store.save_token(token)
        self._token = token

        print("Authorization successful!")
        return token
