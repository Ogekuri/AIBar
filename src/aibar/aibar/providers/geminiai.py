"""
@file
@brief GeminiAI provider with Google OAuth, Monitoring, and BigQuery billing integration.
@details Implements OAuth credential persistence, token refresh, usage retrieval from
Cloud Monitoring and current-month billing retrieval from BigQuery, then normalizes
results into AIBar provider result contracts.
"""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.cloud import bigquery  # pyright: ignore[reportAttributeAccessIssue]
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow  # pyright: ignore[reportMissingImports]
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from aibar.providers.base import (
    AuthenticationError,
    BaseProvider,
    ProviderError,
    ProviderName,
    ProviderResult,
    UsageMetrics,
    WindowPeriod,
)

GEMINIAI_OAUTH_SCOPES: tuple[str, ...] = (
    "https://www.googleapis.com/auth/monitoring.read",
    "https://www.googleapis.com/auth/bigquery.readonly",
)
GEMINIAI_OAUTH_CLIENT_PATH = Path.home() / ".config" / "aibar" / "geminiai_oauth_client.json"
GEMINIAI_OAUTH_TOKEN_PATH = Path.home() / ".config" / "aibar" / "geminiai_oauth_token.json"
GEMINIAI_PROJECT_ID_ENV_VAR = "GEMINIAI_PROJECT_ID"
GEMINIAI_ACCESS_TOKEN_ENV_VAR = "GEMINIAI_OAUTH_ACCESS_TOKEN"
BILLING_DATASET_ID = "billing_data"
BILLING_TABLE_PREFIX = "gcp_billing_export_v1_"


def _to_rfc3339_utc(value: datetime) -> str:
    """
    @brief Convert datetime to RFC3339 UTC string accepted by Google APIs.
    @details Normalizes timezone awareness and strips microseconds to produce stable
    API query timestamps.
    @param value {datetime} Input datetime value.
    @return {str} RFC3339 UTC timestamp (e.g. `2026-03-08T11:00:00Z`).
    """
    normalized = value.astimezone(timezone.utc).replace(microsecond=0)
    return normalized.isoformat().replace("+00:00", "Z")


def _extract_http_status(error: HttpError) -> int:
    """
    @brief Extract integer HTTP status from Google API HttpError.
    @details Returns `0` when status is unavailable to preserve deterministic error
    payload shape.
    @param error {HttpError} Google API exception.
    @return {int} HTTP status code or `0`.
    """
    status = getattr(error.resp, "status", None)
    if isinstance(status, int):
        return status
    if status is None:
        return 0
    if not isinstance(status, (str, bytes, bytearray)):
        return 0
    try:
        return int(status)
    except (TypeError, ValueError):
        return 0


def _extract_retry_after_seconds(error: HttpError) -> float:
    """
    @brief Extract retry-after seconds from HttpError response headers.
    @details Reads `retry-after` case-insensitively and normalizes invalid values to
    `0.0`.
    @param error {HttpError} Google API exception.
    @return {float} Non-negative retry-after delay in seconds.
    """
    response = getattr(error, "resp", None)
    if response is None:
        return 0.0
    retry_after_raw = None
    if hasattr(response, "get"):
        retry_after_raw = response.get("retry-after") or response.get("Retry-After")
    if retry_after_raw is None:
        return 0.0
    if not isinstance(retry_after_raw, (int, float, str)):
        return 0.0
    try:
        return max(0.0, float(retry_after_raw))
    except (TypeError, ValueError):
        return 0.0


@dataclass(frozen=True)
class GeminiAIWindowRange:
    """
    @brief Immutable time-range descriptor for one GeminiAI fetch window.
    @details Encodes start and end UTC timestamps used for Monitoring API queries.
    """

    start_time: datetime
    end_time: datetime


class GeminiAICredentialStore:
    """
    @brief OAuth credential persistence and validation helper for GeminiAI.
    @details Manages client-secret JSON validation, token-file persistence, and
    interactive InstalledAppFlow authorization.
    """

    def __init__(
        self,
        client_config_path: Path | None = None,
        token_path: Path | None = None,
    ) -> None:
        """
        @brief Initialize credential store with optional custom file paths.
        @param client_config_path {Path | None} Optional OAuth client config path.
        @param token_path {Path | None} Optional OAuth token path.
        @return {None} Function return value.
        """
        self.client_config_path = client_config_path or GEMINIAI_OAUTH_CLIENT_PATH
        self.token_path = token_path or GEMINIAI_OAUTH_TOKEN_PATH

    def _ensure_config_dir(self) -> None:
        """
        @brief Create parent directories for OAuth files when missing.
        @return {None} Function return value.
        """
        self.client_config_path.parent.mkdir(parents=True, exist_ok=True)
        self.token_path.parent.mkdir(parents=True, exist_ok=True)

    def has_client_config(self) -> bool:
        """
        @brief Check whether GeminiAI client config JSON exists.
        @return {bool} True when client config file exists.
        """
        return self.client_config_path.exists()

    def has_authorized_credentials(self) -> bool:
        """
        @brief Check whether GeminiAI authorized token material exists.
        @details Environment access-token override is treated as configured token
        material.
        @return {bool} True when token file or env token is available.
        """
        if os.environ.get(GEMINIAI_ACCESS_TOKEN_ENV_VAR):
            return True
        return self.token_path.exists()

    def validate_client_config(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        @brief Validate Google InstalledApp OAuth client-secret payload.
        @details Enforces required `installed` section fields used by
        `InstalledAppFlow.from_client_config`.
        @param payload {dict[str, Any]} Decoded JSON payload to validate.
        @return {dict[str, Any]} Normalized payload.
        @throws {ValueError} When required fields are missing or malformed.
        """
        installed = payload.get("installed")
        if not isinstance(installed, dict):
            raise ValueError("OAuth JSON must contain top-level 'installed' object.")

        required_fields = (
            "client_id",
            "client_secret",
            "auth_uri",
            "token_uri",
            "redirect_uris",
        )
        for field_name in required_fields:
            if field_name not in installed or not installed[field_name]:
                raise ValueError(f"OAuth JSON missing required field: installed.{field_name}")

        redirect_uris = installed.get("redirect_uris")
        if not isinstance(redirect_uris, list) or not redirect_uris:
            raise ValueError("OAuth JSON field installed.redirect_uris must be a non-empty list.")

        return {"installed": installed}

    def save_client_config(self, payload: dict[str, Any]) -> None:
        """
        @brief Persist validated OAuth client config JSON to disk.
        @param payload {dict[str, Any]} Validated client payload.
        @return {None} Function return value.
        """
        validated = self.validate_client_config(payload)
        self._ensure_config_dir()
        self.client_config_path.write_text(
            json.dumps(validated, indent=2),
            encoding="utf-8",
        )

    def load_client_config(self) -> dict[str, Any]:
        """
        @brief Load and validate persisted OAuth client config JSON.
        @return {dict[str, Any]} Validated OAuth client payload.
        @throws {FileNotFoundError} When client config file is missing.
        @throws {ValueError} When payload is invalid JSON or fails validation.
        """
        if not self.client_config_path.exists():
            raise FileNotFoundError(
                "GeminiAI OAuth client config missing. Run 'aibar setup' and configure GeminiAI."
            )
        try:
            decoded = json.loads(self.client_config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("GeminiAI OAuth client config is not valid JSON.") from exc
        if not isinstance(decoded, dict):
            raise ValueError("GeminiAI OAuth client config must decode to a JSON object.")
        return self.validate_client_config(decoded)

    def extract_project_id(self, payload: dict[str, Any]) -> str | None:
        """
        @brief Extract project_id from validated OAuth payload.
        @param payload {dict[str, Any]} Validated OAuth payload.
        @return {str | None} Project identifier or None when absent.
        """
        installed = payload.get("installed")
        if not isinstance(installed, dict):
            return None
        project_id = installed.get("project_id")
        if isinstance(project_id, str) and project_id.strip():
            return project_id.strip()
        return None

    def save_authorized_credentials(self, credentials: Credentials) -> None:
        """
        @brief Persist authorized-user OAuth credentials JSON.
        @param credentials {Credentials} Google OAuth credentials object.
        @return {None} Function return value.
        """
        self._ensure_config_dir()
        serialized = cast(Any, credentials).to_json()
        self.token_path.write_text(serialized, encoding="utf-8")

    def authorize_interactively(
        self,
        scopes: tuple[str, ...] = GEMINIAI_OAUTH_SCOPES,
    ) -> Credentials:
        """
        @brief Execute OAuth browser flow and persist refresh-capable credentials.
        @details Uses InstalledAppFlow local-server flow (`http://localhost`) and
        saves authorized-user token JSON to disk.
        @param scopes {tuple[str, ...]} OAuth scopes requested during authorization.
        @return {Credentials} Authorized credentials.
        @throws {ValueError} When client config is invalid.
        """
        client_payload = self.load_client_config()
        flow = InstalledAppFlow.from_client_config(client_payload, list(scopes))
        credentials = flow.run_local_server(port=0)
        self.save_authorized_credentials(credentials)
        return credentials

    def load_access_token(self) -> str | None:
        """
        @brief Load access token from env override or token file.
        @return {str | None} Access token or None when unavailable.
        """
        if env_token := os.environ.get(GEMINIAI_ACCESS_TOKEN_ENV_VAR):
            return env_token
        if not self.token_path.exists():
            return None
        try:
            decoded = json.loads(self.token_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        token_value = decoded.get("token")
        if isinstance(token_value, str) and token_value:
            return token_value
        return None

    def load_credentials(
        self,
        scopes: tuple[str, ...] = GEMINIAI_OAUTH_SCOPES,
    ) -> Credentials | None:
        """
        @brief Load OAuth credentials and refresh when token is expired.
        @details Supports env-token fallback for non-refreshable runtime contexts.
        @param scopes {tuple[str, ...]} OAuth scopes required by API calls.
        @return {Credentials | None} Valid credentials or None when unavailable.
        @throws {AuthenticationError} When persisted token refresh fails.
        """
        if env_token := os.environ.get(GEMINIAI_ACCESS_TOKEN_ENV_VAR):
            return Credentials(token=env_token, scopes=list(scopes))

        if not self.token_path.exists():
            return None

        credentials = Credentials.from_authorized_user_file(str(self.token_path), list(scopes))
        if credentials.valid:
            return credentials

        if credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
            except RefreshError as exc:
                raise AuthenticationError(
                    "GeminiAI OAuth token refresh failed. Run 'aibar setup' to re-authorize."
                ) from exc
            self.save_authorized_credentials(credentials)
            return credentials

        return None


class GeminiAIProvider(BaseProvider):
    """
    @brief GeminiAI usage provider backed by Monitoring and BigQuery APIs.
    @details Retrieves Generative Language API usage counters and status telemetry
    from Cloud Monitoring, retrieves current-month billing costs from BigQuery export,
    then maps data into AIBar `ProviderResult` models.
    """

    name = ProviderName.GEMINIAI

    SERVICE_FILTER = (
        'resource.type="api" AND resource.labels.service="generativelanguage.googleapis.com"'
    )
    REQUEST_COUNT_FILTER = (
        SERVICE_FILTER + ' AND metric.type="serviceruntime.googleapis.com/api/request_count"'
    )
    TOKEN_COUNT_FILTERS: tuple[str, ...] = (
        SERVICE_FILTER + ' AND metric.type="generativelanguage.googleapis.com/request/token_count"',
        SERVICE_FILTER + ' AND metric.type="aiplatform.googleapis.com/prediction/token_count"',
        REQUEST_COUNT_FILTER,
    )
    LATENCY_FILTER = (
        SERVICE_FILTER + ' AND metric.type="serviceruntime.googleapis.com/api/request_latencies"'
    )
    ERROR_FILTER = (
        SERVICE_FILTER
        + ' AND metric.type="serviceruntime.googleapis.com/api/request_count"'
        + ' AND metric.labels.response_code_class!="2xx"'
    )

    def __init__(
        self,
        credential_store: GeminiAICredentialStore | None = None,
        project_id: str | None = None,
    ) -> None:
        """
        @brief Initialize GeminiAI provider with optional overrides.
        @param credential_store {GeminiAICredentialStore | None} Optional credential store.
        @param project_id {str | None} Optional project id override.
        @return {None} Function return value.
        """
        self._store = credential_store or GeminiAICredentialStore()
        self._project_id = project_id

    def is_configured(self) -> bool:
        """
        @brief Check whether GeminiAI provider has required auth and project metadata.
        @return {bool} True when project id and OAuth token material are available.
        """
        project_id = self._resolve_project_id()
        if project_id is None:
            return False
        return self._store.has_authorized_credentials()

    def get_config_help(self) -> str:
        """
        @brief Return setup guidance for GeminiAI OAuth configuration.
        @return {str} Provider-specific setup instructions.
        """
        scope_lines = "\n".join([f"   - {scope}" for scope in GEMINIAI_OAUTH_SCOPES])
        return f"""GeminiAI Provider Configuration:

1. Run: aibar setup
2. Configure GeminiAI OAuth client JSON (file or paste).
3. Authorize scopes:
{scope_lines}
4. Ensure project id is configured via setup or {GEMINIAI_PROJECT_ID_ENV_VAR}.
"""

    async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult:
        """
        @brief Fetch GeminiAI monitoring usage metrics for one window.
        @details Executes synchronous Google API calls in a worker thread and returns
        normalized provider metrics. HTTP 429 responses are normalized as rate-limit
        provider error payloads with retry-after metadata.
        @param window {WindowPeriod} Requested window period.
        @return {ProviderResult} Provider result payload.
        @throws {AuthenticationError} When OAuth credentials are invalid.
        """
        if not self.is_configured():
            return self._make_error_result(
                window=window,
                error=(
                    "Not configured. Run 'aibar setup' and configure GeminiAI OAuth "
                    "credentials and project id."
                ),
            )

        try:
            return await asyncio.to_thread(self._fetch_sync, window)
        except AuthenticationError:
            raise
        except ProviderError as exc:
            return self._make_error_result(window=window, error=str(exc))
        except Exception as exc:  # noqa: BLE001
            raise ProviderError(f"Unexpected error: {exc}") from exc

    def _fetch_sync(self, window: WindowPeriod) -> ProviderResult:
        """
        @brief Execute blocking Google API retrieval flow for GeminiAI metrics.
        @param window {WindowPeriod} Requested window period.
        @return {ProviderResult} Normalized provider result.
        @throws {AuthenticationError} When credentials are missing/invalid.
        @throws {ProviderError} On non-auth API failures.
        """
        project_id = self._resolve_project_id()
        if project_id is None:
            raise ProviderError(
                "GeminiAI project id is missing. Set GEMINIAI_PROJECT_ID or configure in aibar setup."
            )

        credentials = self._store.load_credentials()
        if credentials is None:
            raise AuthenticationError(
                "GeminiAI OAuth token is missing. Run 'aibar setup' and authorize GeminiAI."
            )

        try:
            monitoring_service = self._build_monitoring_service(credentials)
            time_range = self._build_window_range(window)

            request_total, request_payload = self._query_monitoring_metric(
                monitoring_service=monitoring_service,
                project_id=project_id,
                metric_filter=self.REQUEST_COUNT_FILTER,
                start_time=time_range.start_time,
                end_time=time_range.end_time,
                allow_missing=True,
            )

            token_total: float | None = None
            token_filter_used: str | None = None
            token_payload: dict[str, Any] = {}
            for metric_filter in self.TOKEN_COUNT_FILTERS:
                metric_total, metric_payload = self._query_monitoring_metric(
                    monitoring_service=monitoring_service,
                    project_id=project_id,
                    metric_filter=metric_filter,
                    start_time=time_range.start_time,
                    end_time=time_range.end_time,
                    allow_missing=True,
                )
                if metric_total is not None:
                    token_total = metric_total
                    token_filter_used = metric_filter
                    token_payload = metric_payload
                    break

            latency_total, latency_payload = self._query_monitoring_metric(
                monitoring_service=monitoring_service,
                project_id=project_id,
                metric_filter=self.LATENCY_FILTER,
                start_time=time_range.start_time,
                end_time=time_range.end_time,
                allow_missing=True,
            )

            error_total, error_payload = self._query_monitoring_metric(
                monitoring_service=monitoring_service,
                project_id=project_id,
                metric_filter=self.ERROR_FILTER,
                start_time=time_range.start_time,
                end_time=time_range.end_time,
                allow_missing=True,
            )
            bigquery_client = self._build_bigquery_client(credentials, project_id)
            billing_table_id = self._discover_billing_table_id(bigquery_client, project_id)
            billing_services, billing_cost_total = self._query_current_month_billing_cost(
                bigquery_client,
                project_id,
                billing_table_id,
            )

            raw_payload: dict[str, Any] = {
                "project_id": project_id,
                "monitoring": {
                    "request_metric_filter": self.REQUEST_COUNT_FILTER,
                    "token_metric_filter": token_filter_used,
                    "latency_metric_filter": self.LATENCY_FILTER,
                    "error_metric_filter": self.ERROR_FILTER,
                    "request_metric_payload": request_payload,
                    "token_metric_payload": token_payload,
                    "latency_metric_payload": latency_payload,
                    "error_metric_payload": error_payload,
                    "latency_total": latency_total,
                    "error_total": error_total,
                },
                "billing": {
                    "dataset_id": BILLING_DATASET_ID,
                    "table_id": billing_table_id,
                    "table_path": f"{project_id}.{BILLING_DATASET_ID}.{billing_table_id}",
                    "current_month_cost_net": billing_cost_total,
                    "services": billing_services,
                },
                "window_start": _to_rfc3339_utc(time_range.start_time),
                "window_end": _to_rfc3339_utc(time_range.end_time),
            }
            metrics = self._build_metrics(
                raw_payload=raw_payload,
                request_total=request_total,
                token_total=token_total,
                billing_cost_total=billing_cost_total,
            )
            return ProviderResult(
                provider=self.name,
                window=window,
                metrics=metrics,
                raw=raw_payload,
            )
        except AuthenticationError:
            raise
        except HttpError as exc:
            status_code = _extract_http_status(exc)
            if status_code in {401, 403}:
                raise AuthenticationError(
                    "GeminiAI OAuth token is invalid or missing required Google API scopes."
                ) from exc
            if status_code == 429:
                retry_after_seconds = _extract_retry_after_seconds(exc)
                return self._make_error_result(
                    window=window,
                    error="Rate limited. Try again later.",
                    raw={
                        "status_code": 429,
                        "retry_after_seconds": retry_after_seconds,
                        "body": str(exc),
                    },
                )
            raise ProviderError(f"API error: HTTP {status_code}") from exc
        except RefreshError as exc:
            raise AuthenticationError(
                "GeminiAI OAuth token refresh failed. Run 'aibar setup' and re-authorize."
            ) from exc

    def _build_window_range(self, window: WindowPeriod) -> GeminiAIWindowRange:
        """
        @brief Build UTC time interval used for Monitoring queries.
        @param window {WindowPeriod} Requested window period.
        @return {GeminiAIWindowRange} Start/end UTC timestamps.
        """
        now = datetime.now(timezone.utc)
        if window == WindowPeriod.HOUR_5:
            start = now - timedelta(hours=5)
        elif window == WindowPeriod.DAY_30:
            start = now - timedelta(days=30)
        else:
            start = now - timedelta(days=7)
        return GeminiAIWindowRange(start_time=start, end_time=now)

    def _resolve_project_id(self) -> str | None:
        """
        @brief Resolve project id from override, env, runtime config, or client JSON.
        @return {str | None} Project id or None when unresolved.
        """
        if self._project_id:
            return self._project_id

        if project_env := os.environ.get(GEMINIAI_PROJECT_ID_ENV_VAR):
            return project_env.strip() or None

        from aibar.config import load_runtime_config

        runtime_config = load_runtime_config()
        if runtime_config.geminiai_project_id:
            return runtime_config.geminiai_project_id

        if not self._store.has_client_config():
            return None
        client_payload = self._store.load_client_config()
        return self._store.extract_project_id(client_payload)

    def _build_monitoring_service(self, credentials: Credentials) -> Any:
        """
        @brief Build Google Cloud Monitoring API client.
        @param credentials {Credentials} OAuth credentials.
        @return {Any} Monitoring service client.
        """
        return build("monitoring", "v3", credentials=credentials, cache_discovery=False)

    def _build_bigquery_client(
        self,
        credentials: Credentials,
        project_id: str,
    ) -> bigquery.Client:
        """
        @brief Build BigQuery client for GeminiAI billing export queries.
        @param credentials {Credentials} OAuth credentials with BigQuery read scope.
        @param project_id {str} Google Cloud project id.
        @return {bigquery.Client} BigQuery API client.
        @satisfies REQ-056
        @satisfies REQ-065
        """
        return bigquery.Client(project=project_id, credentials=credentials)

    def _discover_billing_table_id(
        self,
        bigquery_client: bigquery.Client,
        project_id: str,
    ) -> str:
        """
        @brief Discover billing export table id in dataset `billing_data`.
        @details Lists dataset tables and selects the first lexicographically sorted
        id that starts with `gcp_billing_export_v1_`.
        @param bigquery_client {bigquery.Client} BigQuery client.
        @param project_id {str} Google Cloud project id.
        @return {str} Billing export table id.
        @throws {ProviderError} When billing export table is unavailable.
        @satisfies REQ-064
        """
        dataset_ref = bigquery_client.dataset(BILLING_DATASET_ID, project=project_id)
        table_ids = sorted(
            table.table_id
            for table in bigquery_client.list_tables(dataset_ref)
            if table.table_id.startswith(BILLING_TABLE_PREFIX)
        )

        if not table_ids:
            raise ProviderError(
                f"GeminiAI billing export table was not found in dataset '{BILLING_DATASET_ID}'."
            )
        return table_ids[0]

    def _query_current_month_billing_cost(
        self,
        bigquery_client: bigquery.Client,
        project_id: str,
        table_id: str,
    ) -> tuple[list[dict[str, float | str]], float]:
        """
        @brief Query current-month billing costs grouped by Google service.
        @details Uses explicit projection and month-partition filter to reduce scanned
        bytes while preserving per-service gross/credit/net billing aggregates.
        @param bigquery_client {bigquery.Client} BigQuery client.
        @param project_id {str} Google Cloud project id.
        @param table_id {str} Billing export table id.
        @return {tuple[list[dict[str, float | str]], float]} Per-service aggregates and
            total net monthly cost.
        @satisfies REQ-057
        @satisfies REQ-065
        """
        table_path = f"{project_id}.{BILLING_DATASET_ID}.{table_id}"
        query = f"""
SELECT
  service.description AS service_description,
  SUM(cost) AS gross_cost,
  SUM(IFNULL((SELECT SUM(c.amount) FROM UNNEST(credits) c), 0)) AS credits,
  SUM(cost + IFNULL((SELECT SUM(c.amount) FROM UNNEST(credits) c), 0)) AS net_cost
FROM `{table_path}`
WHERE usage_start_time >= TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), MONTH)
GROUP BY service_description
ORDER BY net_cost DESC
"""
        query_job = bigquery_client.query(query)
        services: list[dict[str, float | str]] = []
        total_net = 0.0
        for row in query_job:
            row_data = dict(row.items())
            service_name_raw = row_data.get("service_description")
            service_name = (
                service_name_raw.strip()
                if isinstance(service_name_raw, str) and service_name_raw.strip()
                else "unknown"
            )
            gross_cost = self._coerce_float(row_data.get("gross_cost"))
            credits = self._coerce_float(row_data.get("credits"))
            net_cost = self._coerce_float(row_data.get("net_cost"))
            total_net += net_cost
            services.append(
                {
                    "service_description": service_name,
                    "gross_cost": gross_cost,
                    "credits": credits,
                    "net_cost": net_cost,
                }
            )
        return services, total_net

    def _coerce_float(self, value: Any) -> float:
        """
        @brief Convert numeric BigQuery row field values to float.
        @param value {Any} Numeric row value.
        @return {float} Parsed float value or `0.0` when value is invalid.
        """
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return 0.0
        if value is None:
            return 0.0
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _query_monitoring_metric(
        self,
        monitoring_service: Any,
        project_id: str,
        metric_filter: str,
        start_time: datetime,
        end_time: datetime,
        allow_missing: bool,
    ) -> tuple[float | None, dict[str, Any]]:
        """
        @brief Query Monitoring time-series metric and aggregate point values.
        @details Returns None when metric is unavailable and `allow_missing=True`.
        @param monitoring_service {Any} Monitoring client.
        @param project_id {str} Google Cloud project id.
        @param metric_filter {str} Monitoring filter expression.
        @param start_time {datetime} Query range start.
        @param end_time {datetime} Query range end.
        @param allow_missing {bool} Allow 400/404 as non-fatal missing metric.
        @return {tuple[float | None, dict[str, Any]]} Aggregated value and raw response.
        @throws {HttpError} For non-missing API errors.
        """
        try:
            response = (
                monitoring_service.projects()
                .timeSeries()
                .list(
                    name=f"projects/{project_id}",
                    filter=metric_filter,
                    interval_startTime=_to_rfc3339_utc(start_time),
                    interval_endTime=_to_rfc3339_utc(end_time),
                    aggregation_alignmentPeriod="3600s",
                    aggregation_perSeriesAligner="ALIGN_SUM",
                )
                .execute()
            )
        except HttpError as exc:
            status_code = _extract_http_status(exc)
            if allow_missing and status_code in {400, 404}:
                return None, {"status_code": status_code, "error": str(exc)}
            raise

        if not isinstance(response, dict):
            return None, {}
        value = self._sum_time_series_values(response)
        return value, response

    def _sum_time_series_values(self, response: dict[str, Any]) -> float | None:
        """
        @brief Sum numeric point values in Monitoring `timeSeries` payload.
        @param response {dict[str, Any]} Monitoring API response.
        @return {float | None} Aggregated numeric value or None when no points exist.
        """
        time_series = response.get("timeSeries")
        if not isinstance(time_series, list) or not time_series:
            return None

        total = 0.0
        has_points = False
        for series in time_series:
            if not isinstance(series, dict):
                continue
            points = series.get("points")
            if not isinstance(points, list):
                continue
            for point in points:
                if not isinstance(point, dict):
                    continue
                value_node = point.get("value")
                if not isinstance(value_node, dict):
                    continue
                numeric: float | None = None
                if "doubleValue" in value_node:
                    try:
                        numeric = float(value_node["doubleValue"])
                    except (TypeError, ValueError):
                        numeric = None
                elif "int64Value" in value_node:
                    try:
                        numeric = float(value_node["int64Value"])
                    except (TypeError, ValueError):
                        numeric = None
                elif "distributionValue" in value_node:
                    distribution_node = value_node["distributionValue"]
                    if isinstance(distribution_node, dict):
                        mean_value = distribution_node.get("mean")
                        if mean_value is not None:
                            try:
                                numeric = float(mean_value)
                            except (TypeError, ValueError):
                                numeric = None
                if numeric is None:
                    continue
                has_points = True
                total += numeric

        if not has_points:
            return None
        return total

    def _build_metrics(
        self,
        raw_payload: dict[str, Any],
        request_total: float | None,
        token_total: float | None,
        billing_cost_total: float,
    ) -> UsageMetrics:
        """
        @brief Build normalized UsageMetrics from aggregated API values.
        @param raw_payload {dict[str, Any]} Combined raw payload placeholder.
        @param request_total {float | None} Aggregated request count.
        @param token_total {float | None} Aggregated token count.
        @param billing_cost_total {float} Current-month net billing total.
        @return {UsageMetrics} Normalized metrics object.
        @satisfies REQ-050
        @satisfies REQ-059
        @satisfies REQ-060
        """
        from aibar.config import resolve_currency_symbol

        requests_value = int(request_total) if request_total is not None else None
        input_tokens_value = int(token_total) if token_total is not None else None
        currency_symbol = resolve_currency_symbol(
            raw=raw_payload,
            provider_name=ProviderName.GEMINIAI.value,
        )
        return UsageMetrics(
            cost=billing_cost_total,
            requests=requests_value,
            input_tokens=input_tokens_value,
            output_tokens=None,
            remaining=None,
            limit=None,
            reset_at=None,
            currency_symbol=currency_symbol,
        )
