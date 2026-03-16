"""
@file
@brief GeminiAI provider integration tests.
@details Verifies GeminiAI provider Monitoring + BigQuery metric normalization,
OAuth-backed fetch flow error handling for HTTP 429 and missing billing tables,
and Monitoring time-series aggregation behavior.
@satisfies REQ-054
@satisfies REQ-057
@satisfies REQ-058
@satisfies REQ-060
@satisfies REQ-064
@satisfies REQ-065
@satisfies TST-026
@satisfies TST-027
"""

import asyncio
from pathlib import Path
from typing import cast

import pytest
from google.api_core.exceptions import Forbidden
from google.cloud import bigquery  # pyright: ignore[reportAttributeAccessIssue]
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from httplib2 import Response

from aibar.providers.base import (
    AuthenticationError,
    ProviderError,
    ProviderName,
    WindowPeriod,
)
from aibar.providers.geminiai import (
    GEMINIAI_OAUTH_SCOPES,
    GeminiAICredentialStore,
    GeminiAIProvider,
)


class _FakeCredentialStore(GeminiAICredentialStore):
    """
    @brief Minimal credential-store stub for GeminiAI provider unit tests.
    @details Supplies deterministic OAuth material without filesystem or network
    dependencies. Inherits from GeminiAICredentialStore for type-safe substitution.
    """

    def __init__(self) -> None:
        """
        @brief Initialize fake credential store with deterministic temp paths.
        @return {None} Function return value.
        """
        super().__init__(
            client_config_path=Path("/tmp/fake-geminiai-client.json"),
            token_path=Path("/tmp/fake-geminiai-token.json"),
        )

    def has_authorized_credentials(self) -> bool:
        """
        @brief Return deterministic configured state for tests.
        @return {bool} Always True.
        """
        return True

    def has_client_config(self) -> bool:
        """
        @brief Return deterministic client-config availability for tests.
        @return {bool} Always True.
        """
        return True

    def load_client_config(self) -> dict:
        """
        @brief Return deterministic OAuth payload fixture.
        @return {dict} Minimal OAuth payload containing `project_id`.
        """
        return {"installed": {"project_id": "demo-project"}}

    def extract_project_id(self, payload: dict) -> str | None:
        """
        @brief Extract project id from payload fixture.
        @param payload {dict} OAuth payload fixture.
        @return {str | None} Embedded project id.
        """
        return payload.get("installed", {}).get("project_id")

    def load_credentials(
        self,
        scopes: tuple[str, ...] = GEMINIAI_OAUTH_SCOPES,
    ) -> Credentials | None:
        """
        @brief Return opaque credential sentinel object cast to Credentials.
        @param scopes {tuple[str, ...]} OAuth scopes (unused in fake).
        @return {Credentials | None} Non-null sentinel used by patched provider internals.
        """
        return cast(Credentials, object())


def test_geminiai_fetch_maps_monitoring_and_billing_metrics(monkeypatch) -> None:
    """
    @brief Verify GeminiAI provider maps Monitoring and billing values into UsageMetrics.
    @details Mocks Google API adapters so no network calls occur; asserts requests,
    token usage, telemetry metrics, and billing cost are propagated to ProviderResult.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    @satisfies REQ-057
    @satisfies REQ-060
    @satisfies REQ-065
    @satisfies TST-026
    """
    from aibar.config import RuntimeConfig

    provider = GeminiAIProvider(
        credential_store=_FakeCredentialStore(),
        project_id="demo-project",
    )

    monkeypatch.setattr(provider, "_build_monitoring_service", lambda credentials: object())
    monkeypatch.setattr(provider, "_build_bigquery_client", lambda credentials, project_id: object())
    monkeypatch.setattr(
        provider,
        "_discover_billing_table_id",
        lambda bigquery_client, project_id, dataset_id: "gcp_billing_export_v1_001",
    )
    monkeypatch.setattr(
        provider,
        "_query_current_month_billing_cost",
        lambda bigquery_client, project_id, billing_dataset, table_id: (
            [
                {
                    "service_description": "Generative Language API",
                    "gross_cost": 4.2,
                    "credits": -1.0,
                    "net_cost": 3.2,
                }
            ],
            3.2,
        ),
    )

    responses = iter(
        [
            (42.0, {"timeSeries": [{"points": [{"value": {"int64Value": "42"}}]}]}),
            (314.0, {"timeSeries": [{"points": [{"value": {"doubleValue": 314.0}}]}]}),
            (8.75, {"timeSeries": [{"points": [{"value": {"doubleValue": 8.75}}]}]}),
            (3.0, {"timeSeries": [{"points": [{"value": {"int64Value": "3"}}]}]}),
        ]
    )

    def _fake_query(
        monitoring_service,
        project_id: str,
        metric_filter: str,
        start_time,
        end_time,
        allow_missing: bool,
    ):
        """
        @brief Return deterministic metric responses in expected query order.
        @return {tuple[float | None, dict]} Next metric aggregate payload.
        """
        del monitoring_service, project_id, metric_filter, start_time, end_time, allow_missing
        return next(responses)

    monkeypatch.setattr(provider, "_query_monitoring_metric", _fake_query)
    monkeypatch.setattr(
        "aibar.config.load_runtime_config",
        lambda: RuntimeConfig(currency_symbols={"geminiai": "$"}, billing_data="custom_billing"),
    )

    result = asyncio.run(provider.fetch(WindowPeriod.DAY_7))
    assert result.provider == ProviderName.GEMINIAI
    assert result.window == WindowPeriod.DAY_7
    assert result.metrics.requests == 42
    assert result.metrics.input_tokens == 314
    assert result.metrics.cost == 3.2
    assert result.metrics.currency_symbol == "$"
    assert result.raw["project_id"] == "demo-project"
    assert result.raw["monitoring"]["latency_total"] == 8.75
    assert result.raw["monitoring"]["error_total"] == 3.0
    assert result.raw["billing"]["table_id"] == "gcp_billing_export_v1_001"
    assert result.raw["billing"]["dataset_id"] == "custom_billing"
    assert result.raw["billing"]["current_month_cost_net"] == 3.2
    assert result.raw["billing"]["services"][0]["service_description"] == "Generative Language API"


def test_geminiai_fetch_supports_consumed_api_metric_series(monkeypatch) -> None:
    """
    @brief Verify GeminiAI fetch supports Monitoring `consumed_api` metric resource type.
    @details Simulates Monitoring responses where request/token metrics are available
    only under `resource.type=\"consumed_api\"` and asserts provider extraction still
    populates requests and token metrics.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    @satisfies REQ-057
    @satisfies REQ-060
    @satisfies TST-026
    """
    provider = GeminiAIProvider(
        credential_store=_FakeCredentialStore(),
        project_id="demo-project",
    )

    monkeypatch.setattr(provider, "_build_monitoring_service", lambda credentials: object())
    monkeypatch.setattr(provider, "_build_bigquery_client", lambda credentials, project_id: object())
    monkeypatch.setattr(
        provider,
        "_discover_billing_table_id",
        lambda bigquery_client, project_id, dataset_id: "gcp_billing_export_v1_001",
    )
    monkeypatch.setattr(
        provider,
        "_query_current_month_billing_cost",
        lambda bigquery_client, project_id, billing_dataset, table_id: ([], 0.0),
    )

    def _fake_query(
        monitoring_service,
        project_id: str,
        metric_filter: str,
        start_time,
        end_time,
        allow_missing: bool,
    ):
        """
        @brief Return deterministic metric payloads keyed by Monitoring filter string.
        @return {tuple[float | None, dict]} Aggregated metric value and raw payload.
        """
        del monitoring_service, project_id, start_time, end_time, allow_missing
        if (
            'resource.type="consumed_api"' in metric_filter
            and 'metric.type="serviceruntime.googleapis.com/api/request_count"' in metric_filter
        ):
            return 19.0, {"timeSeries": [{"points": [{"value": {"int64Value": "19"}}]}]}
        if (
            'resource.type="consumed_api"' in metric_filter
            and 'metric.type="generativelanguage.googleapis.com/request/token_count"' in metric_filter
        ):
            return 19.0, {"timeSeries": [{"points": [{"value": {"int64Value": "19"}}]}]}
        if 'metric.type="serviceruntime.googleapis.com/api/request_latencies"' in metric_filter:
            return 1.0, {"timeSeries": [{"points": [{"value": {"doubleValue": 1.0}}]}]}
        if 'metric.labels.response_code_class!="2xx"' in metric_filter:
            return 0.0, {"timeSeries": [{"points": [{"value": {"int64Value": "0"}}]}]}
        return None, {}

    monkeypatch.setattr(provider, "_query_monitoring_metric", _fake_query)

    result = asyncio.run(provider.fetch(WindowPeriod.DAY_7))
    assert result.metrics.requests == 19
    assert result.metrics.input_tokens == 19
    assert result.raw["monitoring"]["request_metric_filter"] is not None
    assert 'resource.type="consumed_api"' in result.raw["monitoring"]["request_metric_filter"]
    assert result.raw["monitoring"]["token_metric_filter"] is not None
    assert 'resource.type="consumed_api"' in result.raw["monitoring"]["token_metric_filter"]


def test_geminiai_fetch_converts_http_429_to_rate_limit_error(monkeypatch) -> None:
    """
    @brief Verify GeminiAI provider maps Google API HTTP 429 to standard rate-limit error.
    @details Asserts provider returns normalized `status_code=429` and retry-after
    metadata used by idle-time retry policy.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    @satisfies REQ-058
    @satisfies TST-027
    """
    provider = GeminiAIProvider(
        credential_store=_FakeCredentialStore(),
        project_id="demo-project",
    )

    monkeypatch.setattr(provider, "_build_monitoring_service", lambda credentials: object())

    response = Response({"status": "429", "retry-after": "120"})
    http_error = HttpError(resp=response, content=b'{"error":"rate limit"}')
    monkeypatch.setattr(
        provider,
        "_query_monitoring_metric",
        lambda *args, **kwargs: (_ for _ in ()).throw(http_error),
    )

    result = asyncio.run(provider.fetch(WindowPeriod.DAY_7))
    assert result.is_error
    assert result.error == "Rate limited. Try again later."
    assert result.raw["status_code"] == 429
    assert result.raw["retry_after_seconds"] == 120.0


def test_geminiai_fetch_missing_billing_table_sets_error_result(monkeypatch) -> None:
    """
    @brief Verify GeminiAI provider returns structured error when billing table is missing.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    @satisfies REQ-058
    @satisfies REQ-064
    @satisfies TST-027
    """
    provider = GeminiAIProvider(
        credential_store=_FakeCredentialStore(),
        project_id="demo-project",
    )

    monkeypatch.setattr(provider, "_build_monitoring_service", lambda credentials: object())
    monkeypatch.setattr(provider, "_build_bigquery_client", lambda credentials, project_id: object())
    monkeypatch.setattr(
        provider,
        "_query_monitoring_metric",
        lambda *args, **kwargs: (1.0, {"timeSeries": [{"points": [{"value": {"int64Value": "1"}}]}]}),
    )

    def _missing_table(*args, **kwargs):
        del args, kwargs
        raise ProviderError("GeminiAI billing export table was not found in dataset 'billing_data'.")

    monkeypatch.setattr(provider, "_discover_billing_table_id", _missing_table)

    result = asyncio.run(provider.fetch(WindowPeriod.DAY_7))
    assert result.is_error
    assert result.error is not None
    assert "billing export table" in result.error


def test_geminiai_fetch_raises_authentication_error_on_insufficient_scope(
    monkeypatch,
) -> None:
    """
    @brief Verify GeminiAI fetch maps BigQuery insufficient-scope failures to AuthenticationError.
    @details Reproduces real BigQuery `ACCESS_TOKEN_SCOPE_INSUFFICIENT` 403 payload shape
    and asserts fetch raises explicit AuthenticationError instead of generic unexpected
    provider failure text.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    @satisfies REQ-056
    @satisfies REQ-060
    """
    provider = GeminiAIProvider(
        credential_store=_FakeCredentialStore(),
        project_id="demo-project",
    )

    monkeypatch.setattr(provider, "_build_monitoring_service", lambda credentials: object())
    monkeypatch.setattr(provider, "_build_bigquery_client", lambda credentials, project_id: object())
    monkeypatch.setattr(
        provider,
        "_query_monitoring_metric",
        lambda *args, **kwargs: (
            1.0,
            {"timeSeries": [{"points": [{"value": {"int64Value": "1"}}]}]},
        ),
    )
    scope_error = Forbidden(
        "403 GET https://bigquery.googleapis.com/bigquery/v2/projects/demo-project/"
        "datasets/billing_data/tables?prettyPrint=false: Request had insufficient "
        "authentication scopes. [{'reason': 'ACCESS_TOKEN_SCOPE_INSUFFICIENT'}]"
    )
    monkeypatch.setattr(
        provider,
        "_discover_billing_table_id",
        lambda bigquery_client, project_id, dataset_id: (_ for _ in ()).throw(scope_error),
    )

    with pytest.raises(AuthenticationError) as exc_info:
        asyncio.run(provider.fetch(WindowPeriod.DAY_7))
    assert "missing required Google API scopes" in str(exc_info.value)
    assert "Unexpected error" not in str(exc_info.value)


def test_geminiai_fetch_uses_runtime_config_currency_symbol(monkeypatch) -> None:
    """
    @brief Verify GeminiAI metrics currency resolves from runtime-config fallback.
    @details Patches runtime config loader to return `currency_symbols.geminiai = "€"`
    and asserts provider fetch propagates that symbol when API payload omits currency.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    @satisfies REQ-059
    """
    from aibar.config import RuntimeConfig

    provider = GeminiAIProvider(
        credential_store=_FakeCredentialStore(),
        project_id="demo-project",
    )

    monkeypatch.setattr(provider, "_build_monitoring_service", lambda credentials: object())
    monkeypatch.setattr(provider, "_build_bigquery_client", lambda credentials, project_id: object())
    monkeypatch.setattr(
        provider,
        "_discover_billing_table_id",
        lambda bigquery_client, project_id, dataset_id: "gcp_billing_export_v1_001",
    )
    monkeypatch.setattr(
        provider,
        "_query_current_month_billing_cost",
        lambda bigquery_client, project_id, billing_dataset, table_id: ([], 1.25),
    )
    metric_payload = {"timeSeries": [{"points": [{"value": {"int64Value": "2"}}]}]}
    monkeypatch.setattr(
        provider,
        "_query_monitoring_metric",
        lambda *args, **kwargs: (2.0, metric_payload),
    )
    monkeypatch.setattr(
        "aibar.config.load_runtime_config",
        lambda: RuntimeConfig(currency_symbols={"geminiai": "€"}, billing_data="billing_data"),
    )

    result = asyncio.run(provider.fetch(WindowPeriod.DAY_7))
    assert result.metrics.currency_symbol == "€"


def test_geminiai_sum_time_series_values_aggregates_numeric_points() -> None:
    """
    @brief Verify GeminiAI time-series aggregator sums int64 and double values.
    @return {None} Function return value.
    @satisfies REQ-057
    """
    provider = GeminiAIProvider(
        credential_store=_FakeCredentialStore(),
        project_id="demo-project",
    )
    response = {
        "timeSeries": [
            {
                "points": [
                    {"value": {"int64Value": "3"}},
                    {"value": {"doubleValue": 2.5}},
                    {"value": {"distributionValue": {"mean": 1.5}}},
                ]
            },
            {
                "points": [
                    {"value": {"int64Value": "4"}},
                ]
            },
        ]
    }
    assert provider._sum_time_series_values(response) == 11.0


def test_geminiai_oauth_scopes_include_monitoring_bigquery_and_cloud_platform() -> None:
    """
    @brief Verify GeminiAI OAuth scopes include Monitoring, BigQuery read, and cloud-platform.
    @return {None} Function return value.
    @satisfies REQ-056
    @satisfies TST-025
    """
    assert GEMINIAI_OAUTH_SCOPES == (
        "https://www.googleapis.com/auth/bigquery.readonly",
        "https://www.googleapis.com/auth/monitoring.read",
        "https://www.googleapis.com/auth/cloud-platform",
    )


def test_geminiai_billing_query_uses_latest_invoice_month_with_fallback() -> None:
    """
    @brief Verify GeminiAI billing SQL targets latest available invoice month.
    @details Asserts generated query includes `MAX(invoice.month)` selection and
    current-month `usage_start_time` fallback predicate.
    @return {None} Function return value.
    @satisfies REQ-065
    @satisfies TST-026
    """
    provider = GeminiAIProvider(
        credential_store=_FakeCredentialStore(),
        project_id="demo-project",
    )

    class _FakeBigQueryClient:
        """
        @brief Minimal fake BigQuery client capturing submitted query text.
        """

        def __init__(self) -> None:
            self.last_query: str | None = None

        def query(self, query_text: str):
            """
            @brief Capture query text and return deterministic row iterator.
            @param query_text {str} Submitted SQL query.
            @return {list[dict[str, object]]} Deterministic billing aggregate rows.
            """
            self.last_query = query_text
            return [
                {
                    "service_description": "AIStudio",
                    "gross_cost": 0.210576,
                    "credits": 0.0,
                    "net_cost": 0.210576,
                },
                {
                    "service_description": "tax",
                    "gross_cost": -0.000576,
                    "credits": 0.0,
                    "net_cost": -0.000576,
                },
                {
                    "service_description": "rounding_error",
                    "gross_cost": -0.002631,
                    "credits": 0.0,
                    "net_cost": -0.002631,
                },
            ]

    fake_client = _FakeBigQueryClient()
    services, total_net = provider._query_current_month_billing_cost(
        cast(bigquery.Client, fake_client),
        "demo-project",
        "billing_data",
        "gcp_billing_export_v1_017F15_EC6BA0_8220E3",
    )

    assert fake_client.last_query is not None
    assert "MAX(invoice.month)" in fake_client.last_query
    assert "invoice.month = (" in fake_client.last_query
    assert "usage_start_time >= TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), MONTH)" in fake_client.last_query
    assert len(services) == 3
    assert total_net == pytest.approx(0.207369)
