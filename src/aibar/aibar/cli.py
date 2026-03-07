"""
@file
@brief Command-line interface for aibar.
@details Defines command parsing, provider dispatch, formatted output, setup helpers, login flows, and UI launch hooks.
"""

import asyncio
import json
import math
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import click
from click.core import ParameterSource
from pydantic import ValidationError

from aibar.config import (
    RuntimeConfig,
    config,
    load_cli_cache,
    load_idle_time,
    load_runtime_config,
    remove_idle_time_file,
    save_cli_cache,
    save_idle_time,
)
from aibar.providers import (
    ClaudeOAuthProvider,
    OpenAIUsageProvider,
    OpenRouterUsageProvider,
    CopilotProvider,
    CodexProvider,
)
from aibar.providers.base import (
    BaseProvider,
    ProviderError,
    ProviderName,
    ProviderResult,
    UsageMetrics,
    WindowPeriod,
)


_WINDOW_PERIOD_TIMEDELTA: dict[WindowPeriod, timedelta] = {
    WindowPeriod.HOUR_5: timedelta(hours=5),
    WindowPeriod.DAY_7: timedelta(days=7),
    WindowPeriod.DAY_30: timedelta(days=30),
}
_RESET_PENDING_MESSAGE = "Starts when the first message is sent"
_CLAUDE_DUAL_SNAPSHOT_FILENAME = "claude_dual_last_success.json"


@dataclass(frozen=True)
class RetrievalPipelineOutput:
    """
    @brief Define shared provider-retrieval pipeline output.
    @details Encodes deterministic retrieval state produced by the shared
    cache-based pipeline used by `show` and Text UI refresh execution.
    The pipeline enforces force-flag handling, idle-time gating, conditional
    refresh into `cache.json`, and post-refresh readback from `cache.json`.
    @note `payload` contains serialized provider results keyed by provider id.
    @note `results` contains validated ProviderResult objects keyed by provider id.
    @note `idle_active` indicates that idle-time gating blocked refresh.
    @note `cache_available` indicates `cache.json` was readable for this run.
    @satisfies REQ-009
    @satisfies REQ-039
    @satisfies REQ-042
    @satisfies REQ-043
    """

    payload: dict[str, object]
    results: dict[str, ProviderResult]
    idle_active: bool
    cache_available: bool


def _normalize_utc(value: datetime) -> datetime:
    """
    @brief Normalize datetime values to timezone-aware UTC instances.
    @details Ensures consistent timestamp arithmetic for idle-time persistence and
    refresh-delay computations when source datetimes are naive or non-UTC.
    @param value {datetime} Source datetime to normalize.
    @return {datetime} Timezone-aware UTC datetime.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _apply_api_call_delay(throttle_state: dict[str, float | int] | None) -> None:
    """
    @brief Enforce minimum spacing between consecutive provider API calls.
    @details Uses monotonic clock values in `throttle_state` to sleep before a live
    API request when elapsed time is below configured delay.
    @param throttle_state {dict[str, float | int] | None} Mutable state containing
        `delay_seconds` and `last_call_started`.
    @return {None} Function return value.
    @satisfies REQ-040
    """
    if throttle_state is None:
        return

    delay_seconds_raw = throttle_state.get("delay_seconds", 0)
    try:
        delay_seconds = max(0.0, float(delay_seconds_raw))
    except (TypeError, ValueError):
        delay_seconds = 0.0

    last_call_raw = throttle_state.get("last_call_started")
    now = time.monotonic()
    if isinstance(last_call_raw, (int, float)) and delay_seconds > 0:
        elapsed = now - float(last_call_raw)
        remaining = delay_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)
    throttle_state["last_call_started"] = time.monotonic()


def _extract_retry_after_seconds(result: ProviderResult) -> int:
    """
    @brief Extract normalized retry-after seconds from provider error payload.
    @details Reads `raw.retry_after_seconds` and clamps to non-negative integer
    seconds. Invalid or missing values normalize to zero.
    @param result {ProviderResult} Provider result to inspect.
    @return {int} Non-negative retry-after delay in seconds.
    @satisfies REQ-041
    """
    value = result.raw.get("retry_after_seconds")
    if not isinstance(value, (int, float, str)):
        return 0
    try:
        parsed = int(float(value))
    except (TypeError, ValueError):
        return 0
    return max(0, parsed)


def _is_http_429_result(result: ProviderResult) -> bool:
    """
    @brief Check whether result payload represents HTTP 429 rate limiting.
    @details Uses normalized raw payload marker `status_code == 429`.
    @param result {ProviderResult} Provider result to classify.
    @return {bool} True when result indicates HTTP 429.
    @satisfies REQ-041
    """
    return result.raw.get("status_code") == 429


def _serialize_results_payload(
    results: dict[str, ProviderResult],
) -> dict[str, dict[str, object]]:
    """
    @brief Serialize ProviderResult mapping to `show --json` payload schema.
    @details Converts each provider result to JSON-safe dict using Pydantic
    serialization with stable key structure.
    @param results {dict[str, ProviderResult]} Provider results keyed by provider id.
    @return {dict[str, dict[str, object]]} JSON payload suitable for CLI output and cache.
    @satisfies REQ-003
    @satisfies CTN-004
    """
    return {provider_key: result.model_dump(mode="json") for provider_key, result in results.items()}


def _filter_cached_payload(
    payload: dict[str, object],
    provider_filter: ProviderName | None,
) -> dict[str, object]:
    """
    @brief Filter cached JSON payload by CLI provider selector.
    @details Returns all providers when filter is None; otherwise returns only
    selected provider payload when present.
    @param payload {dict[str, object]} Cached JSON payload mapping provider keys to result dicts.
    @param provider_filter {ProviderName | None} Optional provider selector.
    @return {dict[str, object]} Filtered payload subset.
    """
    if provider_filter is None:
        return payload
    selected = payload.get(provider_filter.value)
    if isinstance(selected, dict):
        return {provider_filter.value: selected}
    return {}


def _project_cached_window(
    result: ProviderResult,
    target_window: WindowPeriod,
    providers: dict[ProviderName, BaseProvider],
) -> ProviderResult:
    """
    @brief Project cached raw payload to requested window without network I/O.
    @details Attempts provider-specific `_parse_response` projection when cached
    window differs from requested window; returns original result on projection
    failure or when parser is unavailable.
    @param result {ProviderResult} Cached normalized provider result.
    @param target_window {WindowPeriod} Requested CLI window.
    @param providers {dict[ProviderName, BaseProvider]} Provider registry.
    @return {ProviderResult} Result aligned to requested window when possible.
    @satisfies REQ-009
    @satisfies REQ-042
    """
    if result.window == target_window:
        return result
    provider = providers.get(result.provider)
    if provider is None:
        return result
    parser = getattr(provider, "_parse_response", None)
    if not callable(parser) or not isinstance(result.raw, dict):
        return result
    try:
        projected = parser(result.raw, target_window)
    except (AttributeError, KeyError, TypeError, ValueError):
        return result
    if isinstance(projected, ProviderResult):
        return projected
    return result


def _load_cached_results(
    payload: dict[str, object],
    provider_filter: ProviderName | None,
    target_window: WindowPeriod,
    providers: dict[ProviderName, BaseProvider],
) -> dict[str, ProviderResult]:
    """
    @brief Decode cached JSON payload into ProviderResult mapping.
    @details Validates cached payload entries using `ProviderResult` schema, applies
    provider filtering, and projects cached windows to requested window when possible.
    Invalid entries are skipped.
    @param payload {dict[str, object]} Cached JSON payload loaded from disk.
    @param provider_filter {ProviderName | None} Optional provider selector.
    @param target_window {WindowPeriod} Requested CLI window for projection.
    @param providers {dict[ProviderName, BaseProvider]} Provider registry.
    @return {dict[str, ProviderResult]} Validated cached results keyed by provider id.
    @satisfies REQ-009
    @satisfies REQ-042
    """
    filtered_payload = _filter_cached_payload(payload, provider_filter)
    cached_results: dict[str, ProviderResult] = {}
    for provider_key, raw_result in filtered_payload.items():
        if not isinstance(raw_result, dict):
            continue
        try:
            validated = ProviderResult.model_validate(raw_result)
        except ValidationError:
            continue
        cached_results[provider_key] = _project_cached_window(
            validated,
            target_window,
            providers,
        )
    return cached_results


def _update_idle_time_after_refresh(
    fetched_results: list[ProviderResult],
    runtime_config: RuntimeConfig,
) -> None:
    """
    @brief Persist idle-time metadata after refresh completion.
    @details Computes idle-until from last successful fetch timestamp plus
    `idle_delay_seconds`; on HTTP 429, expands idle-until using the greater value
    between idle-delay and maximum retry-after observed in the run.
    @param fetched_results {list[ProviderResult]} Live results produced by refresh calls.
    @param runtime_config {RuntimeConfig} Runtime delay configuration.
    @return {None} Function return value.
    @satisfies REQ-038
    @satisfies REQ-041
    """
    if not fetched_results:
        return

    now_utc = datetime.now(timezone.utc)
    successful_results = [result for result in fetched_results if not result.is_error]
    rate_limited_results = [result for result in fetched_results if _is_http_429_result(result)]

    last_success_at: datetime | None = None
    if successful_results:
        last_success_at = max(_normalize_utc(result.updated_at) for result in successful_results)
    else:
        previous_state = load_idle_time()
        if previous_state is not None:
            last_success_at = datetime.fromtimestamp(
                previous_state.last_success_timestamp,
                tz=timezone.utc,
            )

    if last_success_at is None and rate_limited_results:
        last_success_at = now_utc
    if last_success_at is None:
        return

    base_idle_until = last_success_at + timedelta(seconds=runtime_config.idle_delay_seconds)
    idle_until = base_idle_until
    if rate_limited_results:
        max_retry_after_seconds = max(
            _extract_retry_after_seconds(result) for result in rate_limited_results
        )
        retry_idle_until = now_utc + timedelta(
            seconds=max(runtime_config.idle_delay_seconds, max_retry_after_seconds)
        )
        idle_until = max(base_idle_until, retry_idle_until)
    save_idle_time(last_success_at, idle_until)


def _claude_snapshot_path() -> Path:
    """
    @brief Resolve file path for persisted Claude dual-window success payload.
    @details Uses `XDG_CACHE_HOME` when defined; otherwise falls back to
    `~/.cache/aibar`. Returned path is used only for Claude HTTP 429 fallback
    rendering and does not participate in generic ResultCache TTL reads.
    @return {Path} Absolute snapshot path for Claude dual-window payload.
    @satisfies CTN-004
    """
    xdg_cache = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg_cache) if xdg_cache else Path.home() / ".cache"
    return base / "aibar" / _CLAUDE_DUAL_SNAPSHOT_FILENAME


def _project_next_reset(resets_at_str: str, window: WindowPeriod) -> datetime | None:
    """
    @brief Compute the next reset boundary after a stale resets_at timestamp.
    @details Advances `resets_at_str` by multiples of the window period until the
    result is strictly greater than current UTC time. Returns None if `resets_at_str`
    is unparseable or the window period is not in `_WINDOW_PERIOD_TIMEDELTA`.
    @param resets_at_str {str} ISO 8601 timestamp string of the last known reset boundary.
        May have a Z suffix (converted to +00:00) or an explicit timezone offset.
    @param window {WindowPeriod} Window period whose duration drives the projection step.
    @return {datetime | None} Projected future reset datetime in UTC, or None on parse error.
    @note Uses `math.ceil` to determine the minimum number of full cycles to advance.
    @satisfies REQ-002
    """
    period = _WINDOW_PERIOD_TIMEDELTA.get(window)
    if period is None:
        return None
    try:
        last = datetime.fromisoformat(resets_at_str.replace("Z", "+00:00"))
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
    except (ValueError, AttributeError):
        return None
    now = datetime.now(timezone.utc)
    elapsed_seconds = (now - last).total_seconds()
    if elapsed_seconds <= 0:
        # resets_at is already in the future; no projection needed
        return last
    period_seconds = period.total_seconds()
    cycles = math.ceil(elapsed_seconds / period_seconds)
    return last + timedelta(seconds=cycles * period_seconds)


def _apply_reset_projection(result: ProviderResult) -> ProviderResult:
    """
    @brief Return a copy of `result` with `metrics.reset_at` set to the projected next
    reset boundary when it is currently None but the raw payload contains a parseable
    past `resets_at` string for the result's window.
    @details When a ProviderResult is obtained from stale disk cache (last-good path) or
    from a cross-window raw re-parse, `_parse_response` correctly sets `reset_at=None`
    for past timestamps. This function recovers the display information by projecting
    the next future reset boundary from the raw payload's `resets_at` field, ensuring
    the 'Resets in:' countdown is shown even when the cached timestamp has already elapsed.
    If `reset_at` is already non-None, or the raw payload has no parseable `resets_at`
    for the window, or projection fails, the original result is returned unchanged.
    @param result {ProviderResult} Candidate result whose reset_at may require projection.
    @return {ProviderResult} Original result unchanged if no projection is needed;
        otherwise a new ProviderResult with metrics.reset_at set to the projected datetime.
    @satisfies REQ-002
    @see _project_next_reset
    """
    if result.is_error or result.metrics.reset_at is not None:
        return result

    window_key = "seven_day" if result.window == WindowPeriod.DAY_7 else "five_hour"
    window_data = result.raw.get(window_key, {})
    resets_at_str = window_data.get("resets_at") if window_data else None
    if not resets_at_str:
        return result

    projected = _project_next_reset(resets_at_str, result.window)
    if projected is None or projected <= datetime.now(timezone.utc):
        return result

    updated_metrics = result.metrics.model_copy(update={"reset_at": projected})
    return result.model_copy(update={"metrics": updated_metrics})


def get_providers() -> dict[ProviderName, BaseProvider]:
    """
    @brief Execute get providers.
    @details Applies get providers logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {dict[ProviderName, BaseProvider]} Function return value.
    """
    return {
        ProviderName.CLAUDE: ClaudeOAuthProvider(),
        ProviderName.OPENAI: OpenAIUsageProvider(),
        ProviderName.OPENROUTER: OpenRouterUsageProvider(),
        ProviderName.COPILOT: CopilotProvider(),
        ProviderName.CODEX: CodexProvider(),
    }


def parse_window(window: str) -> WindowPeriod:
    """
    @brief Execute parse window.
    @details Applies parse window logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @param window {str} Input parameter `window`.
    @return {WindowPeriod} Function return value.
    @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.
    """
    mapping = {
        "5h": WindowPeriod.HOUR_5,
        "7d": WindowPeriod.DAY_7,
        "30d": WindowPeriod.DAY_30,
    }
    if window not in mapping:
        raise click.BadParameter(
            f"Invalid window. Choose from: {', '.join(mapping.keys())}"
        )
    return mapping[window]


def parse_provider(provider: str) -> ProviderName | None:
    """
    @brief Execute parse provider.
    @details Applies parse provider logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @param provider {str} Input parameter `provider`.
    @return {ProviderName | None} Function return value.
    @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.
    """
    if provider == "all":
        return None
    try:
        return ProviderName(provider)
    except ValueError:
        valid = ", ".join([p.value for p in ProviderName] + ["all"])
        raise click.BadParameter(f"Invalid provider. Choose from: {valid}")


def _fetch_result(
    provider: BaseProvider,
    window: WindowPeriod,
    throttle_state: dict[str, float | int] | None = None,
) -> ProviderResult:
    """
    @brief Execute one provider refresh call without legacy TTL cache reuse.
    @details Executes throttled provider fetch and returns normalized success/error
    results. Claude 5h/7d requests are routed through `_fetch_claude_dual` so one
    API request can provide deterministic dual-window rate-limit normalization.
    @param provider {BaseProvider} Provider instance to fetch from.
    @param window {WindowPeriod} Time window for the fetch.
    @param throttle_state {dict[str, float | int] | None} Mutable throttling state
        used to enforce inter-call spacing for live API requests.
    @return {ProviderResult} Refreshed provider result for requested window.
    @satisfies CTN-004
    @satisfies REQ-043
    @satisfies REQ-040
    """
    if (
        isinstance(provider, ClaudeOAuthProvider)
        and window in {WindowPeriod.HOUR_5, WindowPeriod.DAY_7}
    ):
        result_5h, result_7d = _fetch_claude_dual(
            provider,
            throttle_state=throttle_state,
        )
        if window == WindowPeriod.HOUR_5:
            return result_5h
        return result_7d

    try:
        _apply_api_call_delay(throttle_state)
        result = asyncio.run(provider.fetch(window))
    except ProviderError as exc:
        result = provider._make_error_result(window=window, error=str(exc))
    except Exception as exc:
        result = provider._make_error_result(
            window=window, error=f"Unexpected error: {exc}"
        )
    return result


def _fetch_claude_dual(
    provider: ClaudeOAuthProvider,
    throttle_state: dict[str, float | int] | None = None,
) -> tuple[ProviderResult, ProviderResult]:
    """
    @brief Fetch Claude 5h and 7d results via a single API call.
    @details Executes ClaudeOAuthProvider.fetch_all_windows for 5h and 7d on each invocation.
    If Claude returns HTTP 429 for both windows, normalize to a partial-window state
    that preserves 5h error visibility and restores persisted reset/utilization
    values for deterministic cache-backed rendering.
    @param provider {ClaudeOAuthProvider} Claude provider instance.
    @param throttle_state {dict[str, float | int] | None} Mutable throttling state
        used to enforce inter-call spacing for live API requests.
    @return {tuple[ProviderResult, ProviderResult]} (5h_result, 7d_result).
    @satisfies REQ-002, REQ-036, REQ-037, CTN-004, REQ-040, REQ-043
    """
    _apply_api_call_delay(throttle_state)
    windows = [WindowPeriod.HOUR_5, WindowPeriod.DAY_7]
    try:
        fetched = asyncio.run(provider.fetch_all_windows(windows))
    except ProviderError as exc:
        fetched = {
            w: provider._make_error_result(window=w, error=str(exc)) for w in windows
        }
    except Exception as exc:
        fetched = {
            w: provider._make_error_result(window=w, error=f"Unexpected error: {exc}")
            for w in windows
        }

    result_5h = fetched.get(WindowPeriod.HOUR_5) or provider._make_error_result(
        window=WindowPeriod.HOUR_5, error="Missing 5h result"
    )
    result_7d = fetched.get(WindowPeriod.DAY_7) or provider._make_error_result(
        window=WindowPeriod.DAY_7, error="Missing 7d result"
    )

    if not result_5h.is_error and not result_7d.is_error:
        _persist_claude_dual_snapshot(result_5h, result_7d)

    if _is_claude_rate_limited_result(result_5h) and _is_claude_rate_limited_result(
        result_7d
    ):
        snapshot_payload = _load_claude_dual_snapshot()
        return (
            _build_claude_rate_limited_partial_result(
                WindowPeriod.HOUR_5,
                include_error=True,
                snapshot_payload=snapshot_payload,
            ),
            _build_claude_rate_limited_partial_result(
                WindowPeriod.DAY_7,
                include_error=False,
                snapshot_payload=snapshot_payload,
            ),
        )

    return result_5h, result_7d


def _persist_claude_dual_snapshot(
    result_5h: ProviderResult,
    result_7d: ProviderResult,
) -> None:
    """
    @brief Persist latest successful Claude dual-window payload for 429 restoration.
    @details Extracts a valid dual-window raw payload (`five_hour` and `seven_day`)
    from successful Claude results and writes it to disk under cache home. Errors
    during serialization or I/O are ignored to keep fetch path non-fatal.
    @param result_5h {ProviderResult} Claude five-hour successful result.
    @param result_7d {ProviderResult} Claude seven-day successful result.
    @return {None} Function return value.
    @satisfies CTN-004
    @satisfies REQ-036
    """
    payload = _extract_claude_dual_payload(result_5h, result_7d)
    if payload is None:
        return

    path = _claude_snapshot_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
    except (OSError, ValueError, TypeError):
        return


def _extract_claude_dual_payload(
    result_5h: ProviderResult,
    result_7d: ProviderResult,
) -> dict[str, object] | None:
    """
    @brief Extract dual-window Claude payload dictionary from successful results.
    @details Returns first raw payload containing both `five_hour` and `seven_day`
    mapping objects. Returns None when payload shape is invalid.
    @param result_5h {ProviderResult} Claude five-hour result.
    @param result_7d {ProviderResult} Claude seven-day result.
    @return {dict[str, object] | None} Serializable payload or None.
    @satisfies CTN-004
    """
    for payload in (result_7d.raw, result_5h.raw):
        if not isinstance(payload, dict):
            continue
        if isinstance(payload.get("five_hour"), dict) and isinstance(
            payload.get("seven_day"), dict
        ):
            return payload
    return None


def _load_claude_dual_snapshot() -> dict[str, object] | None:
    """
    @brief Load persisted Claude dual-window payload for HTTP 429 fallback.
    @details Reads prioritized snapshot candidates from cache home, validates
    required keys, and returns parsed payload when both `five_hour` and
    `seven_day` objects exist. Supports direct raw payload files and serialized
    ProviderResult files (`raw` field). Invalid/missing files return None.
    @return {dict[str, object] | None} Parsed payload or None.
    @satisfies REQ-036
    @satisfies REQ-037
    """
    primary = _claude_snapshot_path()
    candidates = [
        primary,
        primary.with_name("claude_7d.json"),
        primary.with_name("claude_5h.json"),
    ]
    for path in candidates:
        if not path.exists():
            continue
        try:
            decoded = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        payload = _normalize_claude_dual_payload(decoded)
        if payload is not None:
            return payload
    return None


def _normalize_claude_dual_payload(payload: object) -> dict[str, object] | None:
    """
    @brief Normalize persisted Claude payload shape into dual-window raw dictionary.
    @details Accepts either direct dual-window payload (`five_hour`/`seven_day`) or
    serialized ProviderResult dictionaries containing a `raw` field with that shape.
    @param payload {object} Decoded JSON object from snapshot candidate file.
    @return {dict[str, object] | None} Normalized dual-window payload or None.
    @satisfies REQ-036
    """
    if not isinstance(payload, dict):
        return None

    raw_payload = payload
    if "raw" in payload and isinstance(payload.get("raw"), dict):
        raw_payload = payload["raw"]

    if not isinstance(raw_payload.get("five_hour"), dict):
        return None
    if not isinstance(raw_payload.get("seven_day"), dict):
        return None
    return raw_payload


def _extract_snapshot_reset_at(
    snapshot_payload: dict[str, object] | None,
    window: WindowPeriod,
) -> datetime | None:
    """
    @brief Resolve projected reset timestamp from persisted Claude snapshot payload.
    @details Uses window-specific `resets_at` string from persisted payload and
    projects next reset boundary through `_project_next_reset`.
    @param snapshot_payload {dict[str, object] | None} Persisted dual-window payload.
    @param window {WindowPeriod} Target window period.
    @return {datetime | None} Projected reset timestamp or None.
    @satisfies REQ-036
    """
    if snapshot_payload is None:
        return None
    window_key = "seven_day" if window == WindowPeriod.DAY_7 else "five_hour"
    window_data = snapshot_payload.get(window_key)
    if not isinstance(window_data, dict):
        return None
    resets_at = window_data.get("resets_at")
    if not isinstance(resets_at, str) or not resets_at:
        return None
    return _project_next_reset(resets_at, window)


def _extract_snapshot_utilization(
    snapshot_payload: dict[str, object] | None,
    window: WindowPeriod,
) -> float | None:
    """
    @brief Resolve utilization percentage from persisted Claude snapshot payload.
    @details Reads window-specific `utilization`, validates finite range, and clamps
    values to [0.0, 100.0] for deterministic percentage rendering.
    @param snapshot_payload {dict[str, object] | None} Persisted dual-window payload.
    @param window {WindowPeriod} Target window period.
    @return {float | None} Clamped utilization percentage or None.
    @satisfies REQ-036
    """
    if snapshot_payload is None:
        return None
    window_key = "seven_day" if window == WindowPeriod.DAY_7 else "five_hour"
    window_data = snapshot_payload.get(window_key)
    if not isinstance(window_data, dict):
        return None
    value = window_data.get("utilization")
    if not isinstance(value, (int, float, str)):
        return None
    try:
        utilization = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(utilization):
        return None
    return max(0.0, min(100.0, utilization))


def _is_claude_rate_limited_result(result: ProviderResult) -> bool:
    """
    @brief Check whether a ProviderResult represents Claude HTTP 429.
    @details Matches normalized Claude error payloads by provider identity,
    error-state flag, and `raw.status_code == 429`.
    @param result {ProviderResult} Result to classify.
    @return {bool} True when result is Claude 429.
    @satisfies REQ-036
    """
    return (
        result.provider == ProviderName.CLAUDE
        and result.is_error
        and result.raw.get("status_code") == 429
    )


def _build_claude_rate_limited_partial_result(
    window: WindowPeriod,
    include_error: bool,
    snapshot_payload: dict[str, object] | None = None,
) -> ProviderResult:
    """
    @brief Build Claude 429 partial-window result using persisted payload when available.
    @details For 5h window, usage is always forced to 100.0% while reset time is read
    from persisted payload (`five_hour.resets_at`) when possible. For 7d window,
    utilization and reset are restored from persisted payload (`seven_day`) when
    available; otherwise synthetic window-based fallback values are used.
    @param window {WindowPeriod} Window associated with the synthetic result.
    @param include_error {bool} True to include `Rate limited...` error text.
    @param snapshot_payload {dict[str, object] | None} Persisted Claude payload for
        429 restoration.
    @return {ProviderResult} Claude result suitable for partial-window display.
    @satisfies REQ-036
    @satisfies REQ-037
    """
    reset_at = _extract_snapshot_reset_at(snapshot_payload, window)
    if reset_at is None:
        reset_at = datetime.now(timezone.utc) + _WINDOW_PERIOD_TIMEDELTA[window]

    utilization = 100.0
    if window == WindowPeriod.DAY_7:
        persisted_utilization = _extract_snapshot_utilization(snapshot_payload, window)
        if persisted_utilization is not None:
            utilization = persisted_utilization

    remaining = max(0.0, min(100.0, 100.0 - utilization))
    return ProviderResult(
        provider=ProviderName.CLAUDE,
        window=window,
        metrics=UsageMetrics(
            remaining=remaining,
            limit=100.0,
            reset_at=reset_at,
        ),
        raw={
            "status_code": 429,
            "rate_limit_partial": True,
            "snapshot_restored": snapshot_payload is not None,
            "snapshot_payload": snapshot_payload,
        },
        error="Rate limited. Try again later." if include_error else None,
    )


def _refresh_and_persist_cache_payload(
    providers: dict[ProviderName, BaseProvider],
    target_window: WindowPeriod,
    runtime_config: RuntimeConfig,
) -> dict[str, object]:
    """
    @brief Refresh provider data and persist updates into `cache.json`.
    @details Executes provider fetches for configured providers only, updates
    idle-time metadata, merges refreshed provider payloads with existing
    persisted payload, and writes canonical JSON output to `cache.json`.
    @param providers {dict[ProviderName, BaseProvider]} Provider scope for refresh.
    @param target_window {WindowPeriod} Requested window for refresh execution.
    @param runtime_config {RuntimeConfig} Runtime throttling configuration.
    @return {dict[str, object]} Persisted payload after merge.
    @satisfies CTN-004
    @satisfies REQ-009
    @satisfies REQ-038
    @satisfies REQ-041
    @satisfies REQ-043
    """
    fetched_results: list[ProviderResult] = []
    refreshed_results: dict[str, ProviderResult] = {}
    throttle_state: dict[str, float | int] = {
        "delay_seconds": runtime_config.api_call_delay_seconds
    }
    for provider_name, provider in providers.items():
        if not provider.is_configured():
            continue
        result = _fetch_result(
            provider,
            target_window,
            throttle_state=throttle_state,
        )
        fetched_results.append(result)
        refreshed_results[provider_name.value] = result

    persisted_payload = load_cli_cache() or {}
    if refreshed_results:
        refreshed_payload = _serialize_results_payload(refreshed_results)
        persisted_payload = {**persisted_payload, **refreshed_payload}
        save_cli_cache(persisted_payload)
    _update_idle_time_after_refresh(fetched_results, runtime_config)
    return persisted_payload


def retrieve_results_via_cache_pipeline(
    provider_filter: ProviderName | None,
    target_window: WindowPeriod,
    force_refresh: bool,
    providers: dict[ProviderName, BaseProvider],
) -> RetrievalPipelineOutput:
    """
    @brief Execute shared cache-based retrieval pipeline for CLI and Text UI.
    @details Applies required operation order: force-flag handling, idle-time
    evaluation, conditional refresh/update of `cache.json`, then readback and
    decode of provider data from `cache.json` for downstream rendering.
    @param provider_filter {ProviderName | None} Optional provider selector.
    @param target_window {WindowPeriod} Target window requested by caller.
    @param force_refresh {bool} Force-refresh flag for current execution.
    @param providers {dict[ProviderName, BaseProvider]} Provider registry.
    @return {RetrievalPipelineOutput} Shared retrieval state and decoded results.
    @satisfies REQ-009
    @satisfies REQ-039
    @satisfies REQ-042
    @satisfies REQ-043
    """
    if force_refresh:
        remove_idle_time_file()

    cached_payload = load_cli_cache()
    idle_state = load_idle_time()
    now_utc = datetime.now(timezone.utc)
    idle_active = (
        not force_refresh
        and idle_state is not None
        and idle_state.idle_until_timestamp > int(now_utc.timestamp())
    )
    if idle_active:
        if cached_payload is None:
            return RetrievalPipelineOutput(
                payload={},
                results={},
                idle_active=True,
                cache_available=False,
            )
        return RetrievalPipelineOutput(
            payload=_filter_cached_payload(cached_payload, provider_filter),
            results=_load_cached_results(
                payload=cached_payload,
                provider_filter=provider_filter,
                target_window=target_window,
                providers=providers,
            ),
            idle_active=True,
            cache_available=True,
        )

    runtime_config = load_runtime_config()
    if provider_filter is None:
        refresh_scope = providers
    else:
        selected_provider = providers.get(provider_filter)
        refresh_scope = (
            {}
            if selected_provider is None
            else {provider_filter: selected_provider}
        )

    persisted_payload = _refresh_and_persist_cache_payload(
        providers=refresh_scope,
        target_window=target_window,
        runtime_config=runtime_config,
    )
    reloaded_payload = load_cli_cache()
    effective_payload = reloaded_payload or persisted_payload
    cache_available = reloaded_payload is not None or bool(persisted_payload)
    if not cache_available:
        return RetrievalPipelineOutput(
            payload={},
            results={},
            idle_active=False,
            cache_available=False,
        )
    return RetrievalPipelineOutput(
        payload=_filter_cached_payload(effective_payload, provider_filter),
        results=_load_cached_results(
            payload=effective_payload,
            provider_filter=provider_filter,
            target_window=target_window,
            providers=providers,
        ),
        idle_active=False,
        cache_available=True,
    )


def _build_cached_dual_window_results(
    provider_name: ProviderName,
    result: ProviderResult,
    providers: dict[ProviderName, BaseProvider],
) -> tuple[ProviderResult, ProviderResult] | None:
    """
    @brief Build Claude/Codex dual-window display results from cached payload data.
    @details For cached Claude partial-rate-limit payloads, reconstructs the 5h
    error window and 7d restored-metrics window using persisted snapshot data.
    For other payloads, attempts parser-based 5h/7d projection from cached raw.
    @param provider_name {ProviderName} Provider associated with cached result.
    @param result {ProviderResult} Cached provider result.
    @param providers {dict[ProviderName, BaseProvider]} Provider registry.
    @return {tuple[ProviderResult, ProviderResult] | None} (5h, 7d) results when
        dual-window expansion succeeds; otherwise None.
    @satisfies REQ-002
    @satisfies REQ-036
    @satisfies REQ-043
    """
    if (
        provider_name == ProviderName.CLAUDE
        and isinstance(result.raw, dict)
        and result.raw.get("rate_limit_partial")
    ):
        snapshot_payload = result.raw.get("snapshot_payload")
        normalized_snapshot = (
            snapshot_payload if isinstance(snapshot_payload, dict) else None
        )
        return (
            _build_claude_rate_limited_partial_result(
                WindowPeriod.HOUR_5,
                include_error=True,
                snapshot_payload=normalized_snapshot,
            ),
            _build_claude_rate_limited_partial_result(
                WindowPeriod.DAY_7,
                include_error=False,
                snapshot_payload=normalized_snapshot,
            ),
        )

    provider = providers.get(provider_name)
    parser = getattr(provider, "_parse_response", None)
    if not callable(parser) or not isinstance(result.raw, dict):
        return None
    try:
        result_5h = parser(result.raw, WindowPeriod.HOUR_5)
        result_7d = parser(result.raw, WindowPeriod.DAY_7)
    except (AttributeError, KeyError, TypeError, ValueError):
        return None
    if not isinstance(result_5h, ProviderResult):
        return None
    if not isinstance(result_7d, ProviderResult):
        return None
    return (result_5h, result_7d)


@click.group()
@click.version_option()
def main() -> None:
    """
    @brief Execute main.
    @details Applies main logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {None} Function return value.
    """
    pass


@main.command()
@click.option(
    "--provider",
    "-p",
    default="all",
    help="Provider to query (claude, openai, openrouter, copilot, codex, all)",
)
@click.option(
    "--window",
    "-w",
    default="7d",
    help="Time window (5h, 7d, 30d)",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output raw JSON instead of formatted text",
)
@click.option(
    "--force",
    "force_refresh",
    is_flag=True,
    help="Bypass idle-time gating and force provider refresh",
)
def show(provider: str, window: str, output_json: bool, force_refresh: bool) -> None:
    """
    @brief Execute `show` with idle-time cache gating and throttled provider refresh.
    @details Delegates provider retrieval to a shared cache-based pipeline that
    applies force handling, idle-time gating, conditional cache refresh, and
    deterministic readback from `cache.json` before rendering.
    @param provider {str} CLI provider selector string.
    @param window {str} CLI window period string.
    @param output_json {bool} When True, emit JSON output instead of formatted text.
    @param force_refresh {bool} When True, bypass idle-time gate for this execution.
    @return {None} Function return value.
    @satisfies REQ-003
    @satisfies REQ-009
    @satisfies REQ-038
    @satisfies REQ-039
    @satisfies REQ-040
    @satisfies REQ-041
    @satisfies REQ-042
    @satisfies REQ-043
    """
    window_period = parse_window(window)
    provider_filter = parse_provider(provider)

    ctx = click.get_current_context()
    window_source = ctx.get_parameter_source("window")
    providers = get_providers()

    # Filter to specific provider if requested
    if provider_filter:
        if provider_filter not in providers:
            click.echo(
                f"Provider {provider_filter.value} not implemented yet.", err=True
            )
            sys.exit(1)

    retrieval = retrieve_results_via_cache_pipeline(
        provider_filter=provider_filter,
        target_window=window_period,
        force_refresh=force_refresh,
        providers=providers,
    )
    if retrieval.idle_active and not retrieval.cache_available:
        if output_json:
            click.echo(json.dumps({}, indent=2))
        else:
            click.echo("Cache unavailable while idle-time is active.")
        return

    if output_json:
        click.echo(json.dumps(retrieval.payload, indent=2))
        return

    for name, prov in providers.items():
        if not prov.is_configured():
            if provider_filter is None or provider_filter == name:
                click.echo(f"\n{name.value}: Not configured")
                click.echo(f"  Set {config.ENV_VARS.get(name)} environment variable")

    if provider_filter is not None and provider_filter.value not in retrieval.results:
        click.echo(f"\n{provider_filter.value}: Not available in cache")
        return

    for provider_key, result in retrieval.results.items():
        provider_name = ProviderName(provider_key)
        show_dual_windows = (
            window_source == ParameterSource.DEFAULT
            and provider_name in {ProviderName.CLAUDE, ProviderName.CODEX}
        )
        if show_dual_windows:
            dual_results = _build_cached_dual_window_results(
                provider_name=provider_name,
                result=result,
                providers=providers,
            )
            if dual_results is not None:
                result_5h, result_7d = dual_results
                _print_result(provider_name, result_5h, label="5h")
                _print_result(provider_name, result_7d, label="7d")
                continue
        _print_result(provider_name, result)


def _print_result(name: ProviderName, result, label: str | None = None) -> None:
    """
    @brief Execute print result.
    @details Applies print result logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @param name {ProviderName} Input parameter `name`.
    @param result {None} Input parameter `result`.
    @param label {str | None} Input parameter `label`.
    @return {None} Function return value.
    """
    title = name.value.upper()
    if label:
        title = f"{title} ({label})"
    click.echo(f"\n{click.style(title, bold=True)}")
    click.echo("-" * 40)

    if result.is_error:
        click.echo(click.style(f"Error: {result.error}", fg="red"))
        if not _should_render_metrics_after_error(name, result):
            return

    m = result.metrics

    # Usage percentage (Claude)
    if m.usage_percent is not None:
        pct = m.usage_percent
        color = "green" if pct < 50 else ("yellow" if pct < 80 else "red")
        bar = _progress_bar(pct)
        click.echo(f"Usage:    {bar} {click.style(f'{pct:.1f}%', fg=color)}")

    # Reset time
    if m.reset_at:
        from datetime import datetime, timezone

        delta = m.reset_at - datetime.now(timezone.utc)
        if delta.total_seconds() > 0:
            click.echo(f"Resets in: {_format_reset_duration(delta.total_seconds())}")
    elif _should_print_claude_reset_pending_hint(name, m):
        click.echo(f"Resets in: {_RESET_PENDING_MESSAGE}")

    if (
        name in (ProviderName.CLAUDE, ProviderName.CODEX, ProviderName.COPILOT)
        and m.remaining is not None
        and m.limit is not None
    ):
        click.echo(f"Remaining credits: {m.remaining:.1f} / {m.limit:.1f}")

    # Cost
    if m.cost is not None:
        click.echo(f"Cost:     ${m.cost:.4f}")

    # Requests
    if m.requests is not None:
        click.echo(f"Requests: {m.requests:,}")

    # Tokens
    if m.input_tokens is not None or m.output_tokens is not None:
        total = (m.input_tokens or 0) + (m.output_tokens or 0)
        click.echo(
            f"Tokens:   {total:,} ({m.input_tokens or 0:,} in / {m.output_tokens or 0:,} out)"
        )


def _format_reset_duration(seconds: float) -> str:
    """
    @brief Execute format reset duration.
    @details Applies format reset duration logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @param seconds {float} Input parameter `seconds`.
    @return {str} Function return value.
    """
    total_minutes = int(seconds // 60)
    days = total_minutes // (24 * 60)
    hours = (total_minutes // 60) % 24
    minutes = total_minutes % 60
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    return f"{hours}h {minutes}m"


def _should_render_metrics_after_error(
    provider_name: ProviderName,
    result: ProviderResult,
) -> bool:
    """
    @brief Check whether CLI output must render metrics after printing an error line.
    @details Allows continuation only for Claude HTTP 429 partial-window state so the
    5h section can include `Error:` and still display usage/reset lines.
    @param provider_name {ProviderName} Provider associated with rendered section.
    @param result {ProviderResult} Result being rendered.
    @return {bool} True when metrics should still be rendered after error line.
    @satisfies REQ-036
    """
    if provider_name != ProviderName.CLAUDE:
        return False
    if result.raw.get("status_code") != 429:
        return False
    return result.metrics.limit is not None and result.metrics.remaining is not None


def _should_print_claude_reset_pending_hint(
    provider_name: ProviderName,
    metrics: UsageMetrics,
) -> bool:
    """
    @brief Determine whether CLI output must render the reset-pending fallback hint.
    @details The hint is only valid for Claude windows when no reset timestamp is
    available yet and usage is exactly zero, which indicates the rate-limit timer has
    not started. This preserves the normal countdown path for non-zero usage and for
    providers other than Claude.
    @param provider_name {ProviderName} Provider associated with the rendered result.
    @param metrics {UsageMetrics} Normalized quota metrics for the rendered result.
    @return {bool} True when CLI must print `Resets in: Starts when the first message is sent`.
    @satisfies REQ-002
    """
    if provider_name != ProviderName.CLAUDE:
        return False
    if metrics.reset_at is not None:
        return False
    return _is_displayed_zero_percent(metrics.usage_percent)


def _is_displayed_zero_percent(percent: float | None) -> bool:
    """
    @brief Check whether a percentage renders as `0.0%` in one-decimal UI output.
    @details Uses the same one-decimal rounding semantic as output formatting. This
    treats small non-zero percentages (e.g. 0.04) as displayed zero, which is required
    for consistent reset-pending fallback visibility between CLI and GNOME UI.
    @param percent {float | None} Raw percentage value.
    @return {bool} True when `percent` is finite, non-negative, and rounds to `0.0`.
    @satisfies REQ-002
    """
    if percent is None or not math.isfinite(percent):
        return False
    if percent < 0:
        return False
    return round(percent, 1) == 0.0


def _progress_bar(percent: float, width: int = 20) -> str:
    """
    @brief Execute progress bar.
    @details Applies progress bar logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @param percent {float} Input parameter `percent`.
    @param width {int} Input parameter `width`.
    @return {str} Function return value.
    """
    filled = int(width * percent / 100)
    empty = width - filled
    return f"[{'#' * filled}{'-' * empty}]"


@main.command()
def doctor() -> None:
    """
    @brief Execute doctor.
    @details Applies doctor logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {None} Function return value.
    """
    click.echo("Usage UI Doctor")
    click.echo("=" * 40)
    click.echo()

    providers = get_providers()
    all_ok = True

    for name, provider in providers.items():
        info = config.get_provider_status(name)

        click.echo(f"{click.style(info['name'], bold=True)}")

        # Check configuration
        if info["configured"]:
            click.echo(
                f"  Config:     {click.style('OK', fg='green')} ({info['token_preview']})"
            )
        else:
            click.echo(f"  Config:     {click.style('MISSING', fg='red')}")
            click.echo(f"              Set: {info['env_var']}")
            all_ok = False
            click.echo()
            continue

        # Test connectivity
        click.echo("  Testing:    ", nl=False)
        result = _fetch_result(provider, WindowPeriod.HOUR_5)
        if result.is_error:
            click.echo(click.style(f"FAILED - {result.error}", fg="red"))
            all_ok = False
        else:
            click.echo(click.style("OK", fg="green"))

        # Show notes
        if info.get("note"):
            click.echo(f"  Note:       {info['note']}")

        click.echo()

    # Summary
    click.echo("-" * 40)
    if all_ok:
        click.echo(click.style("All providers healthy!", fg="green"))
    else:
        click.echo(click.style("Some providers need attention.", fg="yellow"))


@main.command()
def ui() -> None:
    """
    @brief Execute ui.
    @details Applies ui logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {None} Function return value.
    """
    from aibar.ui import run_ui

    run_ui()


@main.command()
def env() -> None:
    """
    @brief Execute env.
    @details Applies env logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {None} Function return value.
    """
    click.echo(config.get_env_var_help())


@main.command()
def setup() -> None:
    """
    @brief Execute setup.
    @details Applies setup logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {None} Function return value.
    """
    from aibar.config import (
        ENV_FILE_PATH,
        RUNTIME_CONFIG_PATH,
        RuntimeConfig,
        load_runtime_config,
        save_runtime_config,
        write_env_file,
    )

    click.echo()
    click.echo("Usage UI Setup")
    click.echo("=" * 40)
    click.echo()
    click.echo(f"Keys will be saved to: {ENV_FILE_PATH}")
    click.echo(f"Runtime settings will be saved to: {RUNTIME_CONFIG_PATH}")
    click.echo("Press Enter to skip any key.")
    click.echo()

    runtime_config = load_runtime_config()
    click.echo(click.style("Runtime throttling", bold=True))
    click.echo("  idle-delay controls cache-only mode duration after successful refresh.")
    click.echo("  api-call delay controls minimum spacing between API calls.")
    idle_delay_seconds = click.prompt(
        "  idle-delay seconds",
        type=int,
        default=runtime_config.idle_delay_seconds,
    )
    api_call_delay_seconds = click.prompt(
        "  api-call delay seconds",
        type=int,
        default=runtime_config.api_call_delay_seconds,
    )
    configured_runtime = RuntimeConfig(
        idle_delay_seconds=idle_delay_seconds,
        api_call_delay_seconds=api_call_delay_seconds,
    )
    save_runtime_config(configured_runtime)
    click.echo("  -> Saved")
    click.echo()

    updates: dict[str, str] = {}

    # OpenRouter API key
    click.echo(click.style("OpenRouter", bold=True))
    click.echo("  Get your API key from: https://openrouter.ai/keys")
    openrouter_key = click.prompt(
        "  OPENROUTER_API_KEY", default="", show_default=False
    ).strip()
    if openrouter_key:
        updates["OPENROUTER_API_KEY"] = openrouter_key
        click.echo("  -> Set")
    else:
        click.echo("  -> Skipped")
    click.echo()

    # OpenAI Admin key
    click.echo(click.style("OpenAI", bold=True))
    click.echo("  Requires organization admin API key.")
    click.echo(
        "  Get it from: https://platform.openai.com/settings/organization/admin-keys"
    )
    openai_key = click.prompt(
        "  OPENAI_ADMIN_KEY", default="", show_default=False
    ).strip()
    if openai_key:
        updates["OPENAI_ADMIN_KEY"] = openai_key
        click.echo("  -> Set")
    else:
        click.echo("  -> Skipped")
    click.echo()

    # GitHub token (optional)
    click.echo(click.style("GitHub Copilot", bold=True))
    click.echo("  Optional: provide a GitHub token, or use device flow login later.")
    click.echo("  Recommended: run 'aibar login --provider copilot' instead.")
    github_token = click.prompt(
        "  GITHUB_TOKEN", default="", show_default=False
    ).strip()
    if github_token:
        updates["GITHUB_TOKEN"] = github_token
        click.echo("  -> Set")
    else:
        click.echo("  -> Skipped")
    click.echo()

    # Claude - print instructions only
    click.echo(click.style("Claude Code", bold=True))
    click.echo("  Uses Claude CLI credentials automatically.")
    click.echo("  To set up:")
    click.echo("    npm install -g @anthropics/claude")
    click.echo("    claude setup-token")
    click.echo()

    # Codex - print instructions only
    click.echo(click.style("OpenAI Codex", bold=True))
    click.echo("  Uses Codex CLI credentials automatically.")
    click.echo("  To set up:")
    click.echo("    npm install -g @openai/codex")
    click.echo("    codex")
    click.echo()

    # Write to env file
    if updates:
        write_env_file(updates)
        click.echo("-" * 40)
        click.echo(click.style("Configuration saved!", fg="green"))
        click.echo(f"File: {ENV_FILE_PATH}")
        click.echo()
        click.echo("Keys saved:")
        for key in updates:
            click.echo(f"  {key}: set")
    else:
        click.echo("-" * 40)
        click.echo("No keys provided. Nothing saved.")

    click.echo()
    click.echo("Next steps:")
    click.echo("  aibar show --json")
    click.echo("  aibar show")
    click.echo("  aibar doctor")
    click.echo("  aibar ui")


@main.command()
@click.option(
    "--provider",
    "-p",
    default="claude",
    help="Provider to login to (claude, copilot)",
)
def login(provider: str) -> None:
    """
    @brief Execute login.
    @details Applies login logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @param provider {str} Input parameter `provider`.
    @return {None} Function return value.
    """
    if provider == "claude":
        _login_claude()
    elif provider == "copilot":
        _login_copilot()
    else:
        click.echo(f"Login not supported for provider: {provider}")
        click.echo("Supported providers: claude, copilot")
        sys.exit(1)


def _login_claude() -> None:
    """
    @brief Execute login claude.
    @details Applies login claude logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {None} Function return value.
    """
    from aibar.claude_cli_auth import ClaudeCLIAuth

    auth = ClaudeCLIAuth()

    if not auth.is_available():
        click.echo(click.style("\n Claude CLI credentials not found", fg="red"))
        click.echo()
        click.echo("To set up Claude CLI:")
        click.echo("  1. Install: npm install -g @anthropics/claude")
        click.echo("  2. Authenticate: claude setup-token")
        click.echo("  3. Then run 'aibar login' again")
        sys.exit(1)

    info = auth.get_token_info()

    if info["expired"]:
        click.echo(click.style("\n Token expired", fg="yellow"))
        click.echo()
        click.echo("Run this to refresh:")
        click.echo("  claude setup-token")
        sys.exit(1)

    token = auth.get_access_token()

    if token:
        click.echo()
        click.echo("=" * 60)
        click.echo(click.style(" Token extracted successfully!", fg="green", bold=True))
        click.echo()
        click.echo(f"  Token:      {token[:15]}...")
        if expires_in := info.get("expires_in_hours"):
            click.echo(f"  Expires in: {expires_in} hours")
        if scopes := info.get("scopes"):
            click.echo(f"  Scopes:     {', '.join(scopes)}")
        click.echo()
        click.echo("Token auto-loaded from ~/.claude/.credentials.json")
        click.echo("You can now run: aibar show --provider claude")
        click.echo("=" * 60)
    else:
        click.echo(click.style("\n Could not extract token", fg="red"))
        sys.exit(1)


def _login_copilot() -> None:
    """
    @brief Execute login copilot.
    @details Applies login copilot logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {None} Function return value.
    """
    from aibar.providers.copilot import CopilotProvider

    click.echo()
    click.echo("GitHub Copilot Login")
    click.echo("=" * 40)
    click.echo()

    provider = CopilotProvider()

    try:
        asyncio.run(provider.login())
        click.echo()
        click.echo(click.style(" Login successful!", fg="green", bold=True))
        click.echo()
        click.echo("  Token saved to: ~/.config/aibar/copilot.json")
        click.echo()
        click.echo("You can now run: aibar show --provider copilot")
    except Exception as e:
        click.echo(click.style(f"\n Login failed: {e}", fg="red"))
        sys.exit(1)


if __name__ == "__main__":
    main()
