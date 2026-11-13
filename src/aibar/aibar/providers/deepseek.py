"""
@file
@brief DeepSeek account balance provider.
@details Fetches the DeepSeek account balance document
(`GET https://api.deepseek.com/user/balance`) authenticated with the inference
API key and projects the `is_available` flag plus the `balance_infos[]` records
into normalized provider metrics. The DeepSeek API key authorizes balance
retrieval only: no public aggregated per-key usage, request, or token report is
exposed, so this provider MUST NOT fabricate usage counters.
"""

import math

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


class DeepSeekProvider(BaseProvider):
    """
    @brief Define DeepSeek balance provider component.
    @details Encapsulates DeepSeek balance retrieval and normalization for AIBar
    runtime flows. One HTTP request returns the availability flag and the
    per-currency balance buckets (`currency`, `total_balance`,
    `granted_balance`, `topped_up_balance`); the provider normalizes them into
    `raw.deepseek_balance_infos` records and one aggregate `UsageMetrics`
    monetary value while leaving every usage counter unset.
    @satisfies REQ-239
    @satisfies REQ-243
    @satisfies REQ-250
    """

    name = ProviderName.DEEPSEEK
    BALANCE_URL = "https://api.deepseek.com/user/balance"
    TOKEN_ENV_VAR = "DEEPSEEK_API_KEY"

    def __init__(self, api_key: str | None = None) -> None:
        """
        @brief Initialize DeepSeek provider with optional explicit API key.
        @details When `api_key` is provided it takes precedence; otherwise the
        key is resolved from `Config.get_token(ProviderName.DEEPSEEK)` using the
        `DEEPSEEK_API_KEY` environment variable -> `~/.config/aibar/env`
        precedence chain.
        @param api_key {str | None} Optional explicit DeepSeek API key.
        @return {None} Function return value.
        @satisfies REQ-240
        """
        if api_key:
            self._api_key = api_key
        else:
            from aibar.config import config

            self._api_key = config.get_token(ProviderName.DEEPSEEK)

    def is_configured(self) -> bool:
        """
        @brief Report whether the DeepSeek API key is available.
        @return {bool} True when a non-empty API key is resolved.
        @satisfies REQ-240
        """
        return bool(self._api_key)

    def get_config_help(self) -> str:
        """
        @brief Render DeepSeek configuration guidance.
        @details Documents that the inference API key authorizes the balance
        endpoint only, so no aggregated per-key usage report is available.
        @return {str} Human-readable configuration help text.
        @satisfies REQ-250
        """
        return f"""DeepSeek Usage Provider Configuration:

1. Create an API key at https://platform.deepseek.com/api_keys
2. Set environment variable:
   export {self.TOKEN_ENV_VAR}=<your-deepseek-api-key>
3. This API key authorizes only the account balance endpoint
   (https://api.deepseek.com/user/balance). Aggregated per-key usage,
   request, and token reporting is available only in the DeepSeek web
   console, so AIBar renders balance rows without usage counters.
"""

    async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult:
        """
        @brief Fetch DeepSeek account balance data.
        @details Ignores the requested window because the balance document
        describes the whole account and the provider is a fixed-window provider
        with effective window `30d`. Maps HTTP 401 to `AuthenticationError`,
        HTTP 429 to a rate-limit error result carrying normalized
        `retry_after_seconds`, and any other non-200 status to a provider error
        result.
        @param window {WindowPeriod} Requested window (ignored; effective window is `30d`).
        @return {ProviderResult} Normalized DeepSeek balance result.
        @throws {AuthenticationError} When the API key is rejected (HTTP 401).
        @throws {ProviderError} When the request fails unexpectedly.
        @satisfies REQ-239
        @satisfies REQ-243
        @satisfies REQ-247
        """
        effective_window = WindowPeriod.DAY_30
        if not self.is_configured():
            return self._make_error_result(
                window=effective_window,
                error=f"Not configured. Set {self.TOKEN_ENV_VAR} environment variable.",
            )

        try:
            from aibar.config import get_api_call_timeout_seconds

            async with httpx.AsyncClient(
                timeout=get_api_call_timeout_seconds()
            ) as client:
                response = await client.get(
                    self.BALANCE_URL,
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Accept": "application/json",
                        "User-Agent": "aibar",
                    },
                )

                if response.status_code == 401:
                    raise AuthenticationError("Invalid API key")

                if response.status_code == 429:
                    retry_after_raw = response.headers.get("retry-after")
                    try:
                        retry_after_seconds = (
                            max(0.0, float(retry_after_raw))
                            if retry_after_raw is not None
                            else 0.0
                        )
                    except (TypeError, ValueError):
                        retry_after_seconds = 0.0
                    return self._make_error_result(
                        window=effective_window,
                        error="Rate limited. Try again later.",
                        raw={
                            "status_code": 429,
                            "retry_after_seconds": retry_after_seconds,
                            "retry_after_unavailable": retry_after_raw is None,
                        },
                    )

                if response.status_code != 200:
                    return self._make_error_result(
                        window=effective_window,
                        error=f"API error: HTTP {response.status_code}",
                        raw={
                            "status_code": response.status_code,
                            "body": response.text,
                        },
                    )

                data = response.json()
                return self._parse_response(data, effective_window)

        except AuthenticationError:
            raise
        except httpx.TimeoutException:
            return self._make_error_result(
                window=effective_window, error="Request timed out"
            )
        except httpx.RequestError as exc:
            return self._make_error_result(
                window=effective_window, error=f"Network error: {exc}"
            )
        except Exception as exc:
            raise ProviderError(f"Unexpected error: {exc}") from exc

    def _parse_response(self, data: dict, window: WindowPeriod) -> ProviderResult:
        """
        @brief Project the DeepSeek balance document into a provider result.
        @details Normalizes `balance_infos[]` entries into
        `raw.deepseek_balance_infos` records carrying the raw currency code, the
        resolved currency symbol, and the total/granted/topped-up balances.
        `metrics.remaining` receives the preferred record total balance while
        `limit`, `cost`, `total_cost`, `reset_at`, and every usage counter stay
        unset because the endpoint exposes no quota or usage basis.
        @param data {dict} Raw DeepSeek balance API response document.
        @param window {WindowPeriod} Effective window (always `30d`).
        @return {ProviderResult} Normalized DeepSeek balance result.
        @satisfies REQ-241
        @satisfies REQ-242
        @satisfies REQ-246
        """
        from aibar.config import resolve_currency_symbol

        currency_symbol = resolve_currency_symbol(data, self.name.value)
        balance_infos = self._normalize_balance_infos(data, currency_symbol)
        preferred_total = balance_infos[0]["total_balance"] if balance_infos else None

        metrics = UsageMetrics(
            cost=None,
            total_cost=None,
            requests=None,
            input_tokens=None,
            output_tokens=None,
            remaining=preferred_total,
            limit=None,
            reset_at=None,
            currency_symbol=currency_symbol,
        )

        return ProviderResult(
            provider=self.name,
            window=window,
            metrics=metrics,
            raw={
                "data": data,
                "is_available": data.get("is_available"),
                "deepseek_balance_infos": balance_infos,
            },
        )

    def _normalize_balance_infos(
        self, data: dict, currency_symbol: str
    ) -> list[dict]:
        """
        @brief Normalize `balance_infos[]` entries into render-ready records.
        @details Keeps only entries that carry a finite `total_balance`; each
        record stores the raw currency code, the provider-wide resolved currency
        symbol, and the parsed total/granted/topped-up monetary values so CLI and
        GNOME surfaces never re-parse API strings.
        @param data {dict} Raw DeepSeek balance API response document.
        @param currency_symbol {str} Provider-wide resolved currency symbol.
        @return {list[dict]} Ordered normalized balance records.
        @satisfies REQ-241
        """
        raw_infos = data.get("balance_infos")
        if not isinstance(raw_infos, list):
            return []

        records: list[dict] = []
        for entry in raw_infos:
            if not isinstance(entry, dict):
                continue
            total_balance = self._to_optional_float(entry.get("total_balance"))
            if total_balance is None:
                continue
            records.append(
                {
                    "currency": entry.get("currency"),
                    "currency_symbol": currency_symbol,
                    "total_balance": total_balance,
                    "granted_balance": self._to_optional_float(
                        entry.get("granted_balance")
                    ),
                    "topped_up_balance": self._to_optional_float(
                        entry.get("topped_up_balance")
                    ),
                }
            )
        return records

    @staticmethod
    def _to_optional_float(value: object) -> float | None:
        """
        @brief Convert one API numeric field to float preserving missing values.
        @details Accepts numbers and numeric strings because the DeepSeek balance
        endpoint serializes balances as decimal strings. Returns None for absent,
        non-numeric, and non-finite values.
        @param value {object} Raw candidate value from the balance payload.
        @return {float | None} Parsed finite float or None when unavailable.
        @satisfies REQ-241
        """
        if not isinstance(value, (int, float, str)):
            return None
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            return None
        return parsed if math.isfinite(parsed) else None
