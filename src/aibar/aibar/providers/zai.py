"""
@file
@brief Z.ai quota usage provider.
@details Fetches the Z.ai account quota-limit document from the Z.ai monitor API
and projects the returned limit entries into normalized per-quota usage metrics
covering the 5 Hours Quota, the Weekly Quota, and the Total Monthly Web
Search/Reader/Zread Quota.
"""

from datetime import datetime, timezone

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


class ZaiProvider(BaseProvider):
    """
    @brief Define Z.ai quota provider component.
    @details Encapsulates Z.ai quota retrieval and normalization for AIBar
    runtime flows. The provider issues one API call to the Z.ai monitor
    quota-limit endpoint and parses the three canonical limit entries into one
    normalized result carrying per-quota percentages, reset times, and (for the
    monthly web-search quota) usage/limit/remaining counters.
    @satisfies REQ-134
    @satisfies REQ-136
    @satisfies REQ-141
    """

    name = ProviderName.ZAI
    QUOTA_URL = "https://api.z.ai/api/monitor/usage/quota/limit"
    TOKEN_ENV_VAR = "ZAI_API_KEY"
    _UNIT_HOURS = 3
    _UNIT_DAYS = 6
    _UNIT_MONTHS = 5

    def __init__(self, api_key: str | None = None) -> None:
        """
        @brief Initialize Z.ai provider with optional explicit API key.
        @details When `api_key` is provided it takes precedence; otherwise the
        key is resolved from `Config.get_token(ProviderName.ZAI)` using the
        `ZAI_API_KEY` env var -> `~/.config/aibar/env` precedence chain.
        @param api_key {str | None} Optional explicit Z.ai API key.
        @return {None} Function return value.
        @satisfies REQ-135
        """
        if api_key:
            self._api_key = api_key
        else:
            from aibar.config import config

            self._api_key = config.get_token(ProviderName.ZAI)

    def is_configured(self) -> bool:
        """
        @brief Report whether the Z.ai API key is available.
        @return {bool} True when a non-empty API key is resolved.
        @satisfies REQ-135
        """
        return bool(self._api_key)

    def get_config_help(self) -> str:
        """
        @brief Render Z.ai configuration guidance.
        @return {str} Human-readable configuration help text.
        """
        return f"""Z.ai Usage Provider Configuration:

1. Get your API key from the Z.ai account/monitor dashboard.
2. Set environment variable:
   export {self.TOKEN_ENV_VAR}=<your-z.ai-api-key>
"""

    async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult:
        """
        @brief Fetch Z.ai quota data from the monitor API.
        @details Ignores the requested window because Z.ai returns all quotas in
        one document and is treated as a fixed-window provider with effective
        window `30d`. Maps HTTP 401 to `AuthenticationError`, HTTP 429 to a
        rate-limit error result carrying normalized `retry_after_seconds`, and
        any other non-200 status to a provider error result.
        @param window {WindowPeriod} Requested window (ignored; effective window is `30d`).
        @return {ProviderResult} Normalized Z.ai quota result.
        @throws {AuthenticationError} When the API key is rejected (HTTP 401).
        @satisfies REQ-134
        @satisfies REQ-141
        @satisfies REQ-142
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
                    self.QUOTA_URL,
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
        except httpx.RequestError as e:
            return self._make_error_result(
                window=effective_window, error=f"Network error: {e}"
            )
        except Exception as e:
            raise ProviderError(f"Unexpected error: {e}") from e

    def _parse_response(
        self, data: dict, window: WindowPeriod
    ) -> ProviderResult:
        """
        @brief Project raw Z.ai API document into normalized provider result.
        @details Extracts `data.limits` entries keyed by `unit` into the three
        canonical quotas, normalizes each quota percentage and reset time, and
        derives the representative aggregate percentage as the maximum quota
        percentage so the status bar and panel icon reflect the most-consumed
        quota. The full original document is preserved in `raw` under `data`,
        and a normalized `zai_quotas` array is attached for deterministic CLI
        and GNOME rendering.
        @param data {dict} Raw Z.ai API response document.
        @param window {WindowPeriod} Effective window (always `30d`).
        @return {ProviderResult} Normalized Z.ai result with per-quota raw data.
        @satisfies REQ-050
        @satisfies REQ-136
        @satisfies REQ-137
        @satisfies REQ-139
        """
        from aibar.config import resolve_currency_symbol

        currency_symbol = resolve_currency_symbol(data, self.name.value)
        quotas = self._extract_quotas(data)
        max_percentage = self._max_percentage(quotas)

        metrics = UsageMetrics(
            cost=None,
            requests=None,
            input_tokens=None,
            output_tokens=None,
            remaining=100.0 - max_percentage,
            limit=100.0,
            reset_at=None,
            currency_symbol=currency_symbol,
        )

        return ProviderResult(
            provider=self.name,
            window=window,
            metrics=metrics,
            raw={"data": data, "zai_quotas": quotas},
        )

    def _extract_quotas(self, data: dict) -> list[dict]:
        """
        @brief Map Z.ai `data.limits` entries into normalized quota records.
        @details Selects limit entries by `unit` value: `3`/`number=5` -> 5 Hours
        Quota, `6`/`number=1` -> Weekly Quota, `5`/`number=1` -> Total Monthly
        Web Search/Reader/Zread Quota. Each record carries `key`, `label`,
        `percentage`, `reset_at_epoch_ms`, `reset_at` (UTC datetime), and (for
        the monthly web-search quota) `used`, `limit`, `remaining`, and
        `usage_details`.
        @param data {dict} Raw Z.ai API response document.
        @return {list[dict]} Ordered normalized quota records (5h, weekly, monthly).
        @satisfies REQ-136
        @satisfies REQ-137
        """
        data_section = data.get("data") if isinstance(data, dict) else None
        if not isinstance(data_section, dict):
            data_section = {}
        limits = data_section.get("limits")
        if not isinstance(limits, list):
            limits = []

        by_unit: dict[int, dict] = {}
        for entry in limits:
            if not isinstance(entry, dict):
                continue
            unit = entry.get("unit")
            if not isinstance(unit, int):
                continue
            by_unit[unit] = entry

        quotas: list[dict] = []
        five_hours = by_unit.get(self._UNIT_HOURS)
        if isinstance(five_hours, dict):
            quotas.append(self._build_quota(five_hours, "5h", "5 Hours"))
        weekly = by_unit.get(self._UNIT_DAYS)
        if isinstance(weekly, dict):
            quotas.append(self._build_quota(weekly, "weekly", "Weekly"))
        monthly = by_unit.get(self._UNIT_MONTHS)
        if isinstance(monthly, dict):
            quotas.append(self._build_quota(monthly, "monthly", "Monthly Web Search"))
        return quotas

    def _build_quota(self, entry: dict, key: str, label: str) -> dict:
        """
        @brief Build one normalized Z.ai quota record from a raw limit entry.
        @details Coerces `percentage` to a float, converts `nextResetTime`
        (epoch milliseconds) to a UTC datetime `reset_at`, and preserves monthly
        web-search usage counters (`usage`, `currentValue`, `remaining`,
        `usageDetails`) when present.
        @param entry {dict} Raw Z.ai limit entry.
        @param key {str} Machine-readable quota key (`5h`, `weekly`, `monthly`).
        @param label {str} Human-readable quota label.
        @return {dict} Normalized quota record.
        @satisfies REQ-136
        @satisfies REQ-137
        """
        quota: dict = {
            "key": key,
            "label": label,
            "percentage": self._to_float(entry.get("percentage")),
            "reset_at_epoch_ms": entry.get("nextResetTime"),
            "reset_at": self._epoch_ms_to_datetime(entry.get("nextResetTime")),
        }
        if key == "monthly":
            quota["used"] = self._to_int(entry.get("currentValue"))
            quota["limit"] = self._to_int(entry.get("usage"))
            quota["remaining"] = self._to_int(entry.get("remaining"))
            usage_details = entry.get("usageDetails")
            quota["usage_details"] = (
                usage_details if isinstance(usage_details, list) else []
            )
        return quota

    def _max_percentage(self, quotas: list[dict]) -> float:
        """
        @brief Compute the maximum quota percentage for status-bar aggregation.
        @param quotas {list[dict]} Normalized quota records.
        @return {float} Maximum percentage clamped to `>= 0`.
        @satisfies REQ-139
        """
        percentages = [
            quota["percentage"]
            for quota in quotas
            if isinstance(quota.get("percentage"), (int, float))
        ]
        if not percentages:
            return 0.0
        return float(max(percentages))

    @staticmethod
    def _epoch_ms_to_datetime(value: object) -> datetime | None:
        """
        @brief Convert an epoch-millisecond timestamp to a UTC datetime.
        @param value {object} Epoch-millisecond integer or None.
        @return {datetime | None} UTC datetime or None when input is invalid.
        """
        if not isinstance(value, int):
            return None
        try:
            return datetime.fromtimestamp(value / 1000.0, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None

    @staticmethod
    def _to_float(value: float | int | None) -> float:
        """
        @brief Coerce a numeric value to float with `0.0` fallback.
        @param value {float | int | None} Numeric or None value.
        @return {float} Coerced float value.
        """
        if value is None:
            return 0.0
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _to_int(value: int | float | None) -> int | None:
        """
        @brief Coerce a numeric value to int preserving None.
        @param value {int | float | None} Numeric or None value.
        @return {int | None} Coerced int value or None.
        """
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
