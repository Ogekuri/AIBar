"""
@file
@brief OpenRouter key usage and credit provider.
@details Fetches key usage snapshots and quota limits, then transforms provider payloads into normalized cost and quota metrics.
"""

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


class OpenRouterUsageProvider(BaseProvider):
    """
    @brief Define open router usage provider component.
    @details Encapsulates open router usage provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    name = ProviderName.OPENROUTER
    USAGE_URL = "https://openrouter.ai/api/v1/key"
    TOKEN_ENV_VAR = "OPENROUTER_API_KEY"

    def __init__(self, api_key: str | None = None) -> None:
        """
        @brief Execute init.
        @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param api_key {str | None} Input parameter `api_key`.
        @return {None} Function return value.
        """
        if api_key:
            self._api_key = api_key
        else:
            from aibar.config import config
            self._api_key = config.get_token(ProviderName.OPENROUTER)

    def is_configured(self) -> bool:
        """
        @brief Execute is configured.
        @details Applies is configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {bool} Function return value.
        """
        return bool(self._api_key)

    def get_config_help(self) -> str:
        """
        @brief Execute get config help.
        @details Applies get config help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {str} Function return value.
        """
        return f"""OpenRouter Usage Provider Configuration:

1. Create an API key in OpenRouter
2. Set environment variable:
   export {self.TOKEN_ENV_VAR}=sk-or-...
"""

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
                        "Authorization": f"Bearer {self._api_key}",
                        "Accept": "application/json",
                        "User-Agent": "aibar",
                    },
                )

                if response.status_code == 401:
                    raise AuthenticationError("Invalid API key")

                if response.status_code == 402:
                    return self._make_error_result(
                        window=window,
                        error="Payment required (negative balance). Add credits.",
                        raw={"status_code": 402, "body": response.text},
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
        @satisfies REQ-050
        """
        from aibar.config import resolve_currency_symbol

        payload = data.get("data", {})

        usage = self._get_usage(payload, window)
        cost = usage

        currency_symbol = resolve_currency_symbol(data, self.name.value)

        metrics = UsageMetrics(
            cost=cost,
            requests=None,
            input_tokens=None,
            output_tokens=None,
            remaining=payload.get("limit_remaining"),
            limit=payload.get("limit"),
            reset_at=None,
            currency_symbol=currency_symbol,
        )

        return ProviderResult(
            provider=self.name,
            window=window,
            metrics=metrics,
            raw=data,
        )

    def _get_usage(self, payload: dict, window: WindowPeriod) -> float:
        """
        @brief Execute get usage.
        @details Applies get usage logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param payload {dict} Input parameter `payload`.
        @param window {WindowPeriod} Input parameter `window`.
        @return {float} Function return value.
        """
        if window == WindowPeriod.DAY_30:
            return self._to_float(payload.get("usage_monthly"))
        if window == WindowPeriod.HOUR_5:
            return self._to_float(payload.get("usage_daily"))
        return self._to_float(payload.get("usage_weekly"))

    def _get_byok_usage(self, payload: dict, window: WindowPeriod) -> float:
        """
        @brief Execute get byok usage.
        @details Applies get byok usage logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param payload {dict} Input parameter `payload`.
        @param window {WindowPeriod} Input parameter `window`.
        @return {float} Function return value.
        """
        if window == WindowPeriod.DAY_30:
            return self._to_float(payload.get("byok_usage_monthly"))
        if window == WindowPeriod.HOUR_5:
            return self._to_float(payload.get("byok_usage_daily"))
        return self._to_float(payload.get("byok_usage_weekly"))

    def _to_float(self, value: float | int | None) -> float:
        """
        @brief Execute to float.
        @details Applies to float logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param value {float | int | None} Input parameter `value`.
        @return {float} Function return value.
        """
        if value is None:
            return 0.0
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
