"""
@file
@brief Claude OAuth usage provider.
@details Fetches Claude subscription utilization through OAuth credentials and normalizes provider quota state into the shared result contract.
"""

import os
from datetime import datetime

import httpx

from aibar.claude_cli_auth import extract_claude_cli_token
from aibar.providers.base import (
    AuthenticationError,
    BaseProvider,
    ProviderError,
    ProviderName,
    ProviderResult,
    UsageMetrics,
    WindowPeriod,
)


class ClaudeOAuthProvider(BaseProvider):
    """
    @brief Define claude o auth provider component.
    @details Encapsulates claude o auth provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    name = ProviderName.CLAUDE
    USAGE_URL = "https://api.anthropic.com/api/oauth/usage"
    TOKEN_ENV_VAR = "CLAUDE_CODE_OAUTH_TOKEN"

    def __init__(self, token: str | None = None) -> None:
        """
        @brief Execute init.
        @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param token {str | None} Input parameter `token`.
        @return {None} Function return value.
        """
        self._token = token or os.environ.get(self.TOKEN_ENV_VAR) or extract_claude_cli_token()

    def is_configured(self) -> bool:
        """
        @brief Execute is configured.
        @details Applies is configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {bool} Function return value.
        """
        return self._token is not None and self._token.startswith("sk-ant-")

    def get_config_help(self) -> str:
        """
        @brief Execute get config help.
        @details Applies get config help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {str} Function return value.
        """
        return f"""Claude OAuth Provider Configuration:

1. Run: claude setup-token
2. Set environment variable:
   export {self.TOKEN_ENV_VAR}=sk-ant-oat01-...

Note: Token must start with 'sk-ant-' prefix."""

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
                error=f"Not configured. Set {self.TOKEN_ENV_VAR} environment variable.",
            )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self.USAGE_URL,
                    headers={
                        "Authorization": f"Bearer {self._token}",
                        "anthropic-beta": "oauth-2025-04-20",
                        "Accept": "application/json",
                        "User-Agent": "aibar",
                    },
                )

                if response.status_code == 401:
                    raise AuthenticationError("Invalid or expired OAuth token")

                if response.status_code == 403:
                    error_body = response.text
                    if "user:profile" in error_body:
                        return self._make_error_result(
                            window=window,
                            error="OAuth scope error. Fix: unset CLAUDE_CODE_OAUTH_TOKEN && claude setup-token",
                            raw={"status_code": 403, "body": error_body},
                        )
                    return self._make_error_result(
                        window=window,
                        error=f"API forbidden: HTTP {response.status_code}",
                        raw={"status_code": 403, "body": error_body},
                    )

                if response.status_code == 429:
                    return self._make_error_result(
                        window=window,
                        error="Rate limited. Try again later.",
                        raw={"status_code": 429},
                    )

                if response.status_code != 200:
                    return self._make_error_result(
                        window=window,
                        error=f"API error: HTTP {response.status_code}",
                        raw={"status_code": response.status_code, "body": response.text},
                    )

                data = response.json()
                return self._parse_response(data, window)

        except AuthenticationError:
            raise
        except httpx.TimeoutException:
            return self._make_error_result(
                window=window,
                error="Request timed out",
            )
        except httpx.RequestError as e:
            return self._make_error_result(
                window=window,
                error=f"Network error: {e}",
            )
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
        # Select the appropriate window based on the requested period
        window_key = "seven_day" if window == WindowPeriod.DAY_7 else "five_hour"
        window_data = data.get(window_key, {})

        if not window_data:
            # Fallback to seven_day if specific window not available
            window_data = data.get("seven_day", {})

        # Parse reset time if available
        reset_at = None
        if resets_at := window_data.get("resets_at"):
            try:
                reset_at = datetime.fromisoformat(resets_at.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        # Parse utilization percentage (0-100)
        utilization = window_data.get("utilization")
        remaining_percent = None
        if utilization is not None:
            remaining_percent = 100.0 - utilization

        metrics = UsageMetrics(
            remaining=remaining_percent,  # Store as percentage remaining
            limit=100.0,  # Total quota is 100%
            reset_at=reset_at,
            # Claude doesn't provide these in OAuth endpoint
            cost=None,
            requests=None,
            input_tokens=None,
            output_tokens=None,
        )

        return ProviderResult(
            provider=self.name,
            window=window,
            metrics=metrics,
            raw=data,
        )
