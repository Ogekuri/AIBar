"""
@file
@brief OpenAI organization usage provider.
@details Retrieves organization completion usage and cost buckets, aggregates counters, and maps response data to normalized provider metrics.
"""

from datetime import datetime, timedelta, timezone

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


class OpenAIUsageProvider(BaseProvider):
    """
    @brief Define open a i usage provider component.
    @details Encapsulates open a i usage provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    name = ProviderName.OPENAI
    BASE_URL = "https://api.openai.com/v1/organization"
    TOKEN_ENV_VAR = "OPENAI_ADMIN_KEY"

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
            self._api_key = config.get_token(ProviderName.OPENAI)

    def is_configured(self) -> bool:
        """
        @brief Execute is configured.
        @details Applies is configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {bool} Function return value.
        """
        return self._api_key is not None and self._api_key.startswith("sk-")

    def get_config_help(self) -> str:
        """
        @brief Execute get config help.
        @details Applies get config help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {str} Function return value.
        """
        return f"""OpenAI Usage Provider Configuration:

1. Get an admin API key from your OpenAI organization settings
2. Set environment variable:
   export {self.TOKEN_ENV_VAR}=sk-...

Note: Must be an organization/admin key with usage permissions."""

    def _get_time_range(self, window: WindowPeriod) -> tuple[int, int]:
        """
        @brief Execute get time range.
        @details Applies get time range logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param window {WindowPeriod} Input parameter `window`.
        @return {tuple[int, int]} Function return value.
        """
        now = datetime.now(timezone.utc)
        days = {"5h": 1, "7d": 7, "30d": 30}[window.value]  # 5h maps to 1 day for OpenAI
        start = now - timedelta(days=days)
        return int(start.timestamp()), int(now.timestamp())

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
                headers = {"Authorization": f"Bearer {self._api_key}"}
                start_time, end_time = self._get_time_range(window)

                # Fetch usage and costs in parallel
                usage_task = self._fetch_usage(client, headers, start_time, end_time)
                costs_task = self._fetch_costs(client, headers, start_time, end_time)

                usage_data, costs_data = await usage_task, await costs_task

                return self._build_result(window, usage_data, costs_data)

        except AuthenticationError:
            raise
        except httpx.TimeoutException:
            return self._make_error_result(window=window, error="Request timed out")
        except httpx.RequestError as e:
            return self._make_error_result(window=window, error=f"Network error: {e}")
        except Exception as e:
            raise ProviderError(f"Unexpected error: {e}") from e

    async def _fetch_usage(
        self,
        client: httpx.AsyncClient,
        headers: dict,
        start_time: int,
        end_time: int,
    ) -> dict:
        """
        @brief Execute fetch usage.
        @details Applies fetch usage logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param client {httpx.AsyncClient} Input parameter `client`.
        @param headers {dict} Input parameter `headers`.
        @param start_time {int} Input parameter `start_time`.
        @param end_time {int} Input parameter `end_time`.
        @return {dict} Function return value.
        """
        response = await client.get(
            f"{self.BASE_URL}/usage/completions",
            headers=headers,
            params={
                "start_time": start_time,
                "end_time": end_time,
                "bucket_width": "1d",
            },
        )
        self._check_response(response)
        return response.json()

    async def _fetch_costs(
        self,
        client: httpx.AsyncClient,
        headers: dict,
        start_time: int,
        end_time: int,
    ) -> dict:
        """
        @brief Execute fetch costs.
        @details Applies fetch costs logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param client {httpx.AsyncClient} Input parameter `client`.
        @param headers {dict} Input parameter `headers`.
        @param start_time {int} Input parameter `start_time`.
        @param end_time {int} Input parameter `end_time`.
        @return {dict} Function return value.
        """
        response = await client.get(
            f"{self.BASE_URL}/costs",
            headers=headers,
            params={
                "start_time": start_time,
                "end_time": end_time,
                "bucket_width": "1d",
            },
        )
        self._check_response(response)
        return response.json()

    def _check_response(self, response: httpx.Response) -> None:
        """
        @brief Execute check response.
        @details Applies check response logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param response {httpx.Response} Input parameter `response`.
        @return {None} Function return value.
        @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.
        """
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key")

        if response.status_code == 403:
            raise AuthenticationError("API key lacks required permissions")

        if response.status_code != 200:
            raise ProviderError(f"API error: HTTP {response.status_code}")

    def _build_result(
        self, window: WindowPeriod, usage_data: dict, costs_data: dict
    ) -> ProviderResult:
        """
        @brief Execute build result.
        @details Applies build result logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param window {WindowPeriod} Input parameter `window`.
        @param usage_data {dict} Input parameter `usage_data`.
        @param costs_data {dict} Input parameter `costs_data`.
        @return {ProviderResult} Function return value.
        """
        # Aggregate usage from buckets
        total_input_tokens = 0
        total_output_tokens = 0
        total_requests = 0

        for bucket in usage_data.get("data", []):
            for result in bucket.get("results", []):
                total_input_tokens += result.get("input_tokens", 0)
                total_output_tokens += result.get("output_tokens", 0)
                total_requests += result.get("num_model_requests", 0)

        # Aggregate costs from buckets
        total_cost = 0.0
        for bucket in costs_data.get("data", []):
            for result in bucket.get("results", []):
                # Cost is in cents, convert to dollars
                amount_cents = result.get("amount", {}).get("value", 0)
                total_cost += amount_cents / 100.0

        metrics = UsageMetrics(
            cost=round(total_cost, 4),
            requests=total_requests,
            input_tokens=total_input_tokens,
            output_tokens=total_output_tokens,
            # OpenAI doesn't have quota limits in the same way
            remaining=None,
            limit=None,
            reset_at=None,
        )

        return ProviderResult(
            provider=self.name,
            window=window,
            metrics=metrics,
            raw={"usage": usage_data, "costs": costs_data},
        )
