"""
@file
@brief Claude OAuth usage provider.
@details Fetches Claude subscription utilization through OAuth credentials and normalizes provider quota state into the shared result contract.
"""

import asyncio
import os
import random
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


def _resolve_provider_currency(raw: dict, provider_name: str) -> str:
    """
    @brief Resolve currency symbol for a provider from raw API response or config.
    @details Delegates to `resolve_currency_symbol` from `aibar.config`. Imported
    lazily inside the function to avoid circular import at module load time.
    @param raw {dict} Raw API response dict.
    @param provider_name {str} Provider name key.
    @return {str} Resolved currency symbol.
    @satisfies REQ-050
    """
    from aibar.config import resolve_currency_symbol
    return resolve_currency_symbol(raw, provider_name)


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
        self._token = (
            token or os.environ.get(self.TOKEN_ENV_VAR) or extract_claude_cli_token()
        )

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

    MAX_RETRIES = 3
    RETRY_BACKOFF_BASE = 2.0
    RETRY_JITTER_MAX = 1.0

    async def _request_usage(self, client: httpx.AsyncClient) -> httpx.Response:
        """
        @brief Execute HTTP GET to usage endpoint with retry on HTTP 429.
        @details Retries up to MAX_RETRIES times on 429 responses, respecting
        the retry-after header with exponential backoff fallback and random
        jitter to prevent thundering-herd synchronization. Backoff sequence
        with RETRY_BACKOFF_BASE=2.0: ~2-3s, ~4-5s, ~8-9s (total ~14-17s).
        @param client {httpx.AsyncClient} Reusable HTTP client session.
        @return {httpx.Response} Final HTTP response after retries exhausted or success.
        """
        headers = {
            "Authorization": f"Bearer {self._token}",
            "anthropic-beta": "oauth-2025-04-20",
            "Accept": "application/json",
            "User-Agent": "aibar",
        }
        response = await client.get(self.USAGE_URL, headers=headers)
        for attempt in range(self.MAX_RETRIES):
            if response.status_code != 429:
                return response
            retry_after_raw = response.headers.get("retry-after", "0")
            try:
                retry_after = max(0.0, float(retry_after_raw))
            except (TypeError, ValueError):
                retry_after = 0.0
            from aibar.config import load_runtime_config

            min_api_delay_seconds = float(load_runtime_config().api_call_delay_seconds)
            jitter = random.uniform(0, self.RETRY_JITTER_MAX)
            delay = max(
                retry_after,
                self.RETRY_BACKOFF_BASE * (2**attempt),
                min_api_delay_seconds,
            ) + jitter
            await asyncio.sleep(delay)
            response = await client.get(self.USAGE_URL, headers=headers)
        return response

    async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult:
        """
        @brief Execute fetch for a single window period.
        @details Makes one HTTP request to the usage endpoint (with retry on 429)
        and parses the response for the requested window.
        @param window {WindowPeriod} Window period to parse from the API response.
        @return {ProviderResult} Parsed result for the requested window.
        @throws {AuthenticationError} When the OAuth token is invalid or expired.
        @throws {ProviderError} On unexpected non-HTTP errors.
        """
        if not self.is_configured():
            return self._make_error_result(
                window=window,
                error=f"Not configured. Set {self.TOKEN_ENV_VAR} environment variable.",
            )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await self._request_usage(client)
                result = self._handle_response(response, window)
                if result is not None:
                    return result
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

    async def fetch_all_windows(
        self, windows: list[WindowPeriod]
    ) -> dict[WindowPeriod, ProviderResult]:
        """
        @brief Execute a single API call and parse results for multiple windows.
        @details The usage endpoint returns data for all windows in one response.
        This method avoids redundant HTTP requests when multiple windows are needed.
        @param windows {list[WindowPeriod]} Window periods to parse from one API response.
        @return {dict[WindowPeriod, ProviderResult]} Map of window to parsed result.
        @throws {AuthenticationError} When the OAuth token is invalid or expired.
        @throws {ProviderError} On unexpected non-HTTP errors.
        """
        if not self.is_configured():
            return {
                w: self._make_error_result(
                    window=w,
                    error=f"Not configured. Set {self.TOKEN_ENV_VAR} environment variable.",
                )
                for w in windows
            }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await self._request_usage(client)

                error_result = self._handle_response(response, windows[0])
                if error_result is not None:
                    return {
                        w: self._make_error_result(
                            window=w,
                            error=error_result.error or "Unknown error",
                            raw=error_result.raw,
                        )
                        for w in windows
                    }

                data = response.json()
                return {w: self._parse_response(data, w) for w in windows}

        except AuthenticationError:
            raise
        except httpx.TimeoutException:
            return {
                w: self._make_error_result(window=w, error="Request timed out")
                for w in windows
            }
        except httpx.RequestError as e:
            return {
                w: self._make_error_result(window=w, error=f"Network error: {e}")
                for w in windows
            }
        except Exception as e:
            raise ProviderError(f"Unexpected error: {e}") from e

    def _handle_response(
        self, response: httpx.Response, window: WindowPeriod
    ) -> ProviderResult | None:
        """
        @brief Map HTTP error status codes to ProviderResult error payloads.
        @details Returns None on HTTP 200 (success), otherwise returns an error
        ProviderResult for the given window. Raises AuthenticationError on 401.
        @param response {httpx.Response} HTTP response to evaluate.
        @param window {WindowPeriod} Window period for error result construction.
        @return {ProviderResult | None} Error result or None if response is 200.
        @throws {AuthenticationError} When HTTP status is 401.
        """
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
            retry_after_raw = response.headers.get("retry-after", "0")
            try:
                retry_after_seconds = max(0.0, float(retry_after_raw))
            except (TypeError, ValueError):
                retry_after_seconds = 0.0
            return self._make_error_result(
                window=window,
                error="Rate limited. Try again later.",
                raw={
                    "status_code": 429,
                    "retry_after_seconds": retry_after_seconds,
                },
            )

        if response.status_code != 200:
            return self._make_error_result(
                window=window,
                error=f"API error: HTTP {response.status_code}",
                raw={"status_code": response.status_code, "body": response.text},
            )

        return None

    def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult:
        """
        @brief Normalize a raw Claude API payload dict into a ProviderResult for the given window.
        @details Selects `five_hour` or `seven_day` sub-dict from `data` based on `window`
        (fallback to `seven_day` if the specific key is absent or empty). Derives
        `remaining` from `utilization` field and `reset_at` from `resets_at` field.
        `reset_at` is set to None when the parsed datetime is already in the past relative
        to the current UTC clock, preventing stale cached timestamps from propagating to
        the display layer and causing asymmetric suppression of the 'Resets in:' output
        between the 5h and 7d windows (REQ-002 symmetry requirement).
        @param data {dict} Raw JSON payload from Claude usage API or stale disk cache.
            Expected keys: `five_hour` and/or `seven_day`, each containing optional
            `utilization` (float, 0-100) and `resets_at` (ISO 8601 string).
        @param window {WindowPeriod} Target window period for result construction.
            `WindowPeriod.DAY_7` selects `seven_day`; all others select `five_hour`.
        @return {ProviderResult} Normalized result with `metrics.remaining` set to
            `100 - utilization`, `metrics.reset_at` set to the parsed future datetime or
            None, and `raw` set to the full unmodified `data` payload.
        @satisfies REQ-002
        """
        from datetime import timezone

        # Select the appropriate window based on the requested period
        window_key = "seven_day" if window == WindowPeriod.DAY_7 else "five_hour"
        window_data = data.get(window_key, {})

        if not window_data:
            # Fallback to seven_day if specific window not available
            window_data = data.get("seven_day", {})

        # Parse reset time if available; discard past timestamps to prevent
        # stale cache data from causing asymmetric 'Resets in:' display suppression.
        reset_at = None
        if resets_at := window_data.get("resets_at"):
            try:
                parsed = datetime.fromisoformat(resets_at.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                if parsed > datetime.now(timezone.utc):
                    reset_at = parsed
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
            currency_symbol=_resolve_provider_currency(data, ProviderName.CLAUDE.value),
        )

        return ProviderResult(
            provider=self.name,
            window=window,
            metrics=metrics,
            raw=data,
        )
