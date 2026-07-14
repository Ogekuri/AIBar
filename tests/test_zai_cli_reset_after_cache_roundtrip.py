"""
@file
@brief Z.ai CLI reset-countdown cache round-trip regression test.
@details Reproduces the critical defect where Z.ai `Resets in:` rows vanish
from CLI `show` text output after the shared cache pipeline serializes the
provider result via `model_dump(mode="json")` and reloads it via
`ProviderResult.model_validate(...)`. The round-trip converts the untyped
`raw.zai_quotas[i].reset_at` datetime into an ISO-8601 string, which the CLI
renderer previously treated as non-datetime and skipped, so `Resets in:`
disappeared from every Z.ai panel served from cache (the normal `show` path).
The renderer MUST resolve the reset datetime from the round-trip-safe
`reset_at_epoch_ms` field (with ISO-string `reset_at` fallback) so `Resets in:`
rows render consistently with the in-memory fresh-fetch path and with the
GNOME extension card, which already consumes `reset_at_epoch_ms`.
@satisfies REQ-137
"""

from aibar.cli import _build_result_panel, _build_zai_quota_lines
from aibar.providers.base import ProviderName, ProviderResult, WindowPeriod
from aibar.providers.zai import ZaiProvider

# Fixed far-future epoch-millisecond reset timestamp (year ~2065) so the reset
# countdown is always in the future at test time, isolating the type-coercion
# defect from wall-clock drift without depending on `datetime.now()` exactness.
_RESET_EPOCH_MS_FUTURE = 3_000_000_000_000


def _future_quota_document() -> dict:
    """
    @brief Build a synthetic Z.ai monitor document with future reset times.
    @details Wraps three canonical `data.limits` entries (units 3, 6, 5) each
    carrying a far-future `nextResetTime` so the projected `reset_at` datetime is
    always in the future at assertion time.
    @return {dict} Z.ai monitor document with `data.limits` populated.
    """
    return {
        "data": {
            "limits": [
                {
                    "unit": 3,
                    "number": 5,
                    "percentage": 38.0,
                    "nextResetTime": _RESET_EPOCH_MS_FUTURE,
                },
                {
                    "unit": 6,
                    "number": 1,
                    "percentage": 32.0,
                    "nextResetTime": _RESET_EPOCH_MS_FUTURE,
                },
                {
                    "unit": 5,
                    "number": 1,
                    "percentage": 0.0,
                    "nextResetTime": _RESET_EPOCH_MS_FUTURE,
                },
            ]
        }
    }


def _roundtrip_result() -> ProviderResult:
    """
    @brief Produce a Z.ai result that traversed the cache JSON round-trip.
    @details Builds a fresh in-memory result via `ZaiProvider._parse_response`,
    serializes it with `model_dump(mode="json")` (mirroring the shared cache
    pipeline write path in `_serialize_results_payload`), and reloads it via
    `ProviderResult.model_validate` (mirroring `_load_cached_results`). After this
    round-trip `raw.zai_quotas[i].reset_at` is an ISO-8601 string instead of a
    datetime, which is the exact state served to CLI rendering on every cached
    `show` execution.
    @return {ProviderResult} Z.ai result reconstructed from serialized cache data.
    """
    provider = ZaiProvider(api_key="zai-test-key")
    fresh = provider._parse_response(_future_quota_document(), WindowPeriod.DAY_30)
    return ProviderResult.model_validate(fresh.model_dump(mode="json"))


def test_zai_resets_in_renders_after_cache_roundtrip() -> None:
    """
    @brief Verify Z.ai `Resets in:` rows survive the cache JSON round-trip.
    @details Asserts `_build_zai_quota_lines` emits one `Resets in:` row per
    quota (3 total) after the result traversed `model_dump(mode="json")` ->
    `model_validate`, matching the in-memory fresh-fetch rendering and the GNOME
    extension card that already consumes `reset_at_epoch_ms`.
    @return {None} Function return value.
    @satisfies REQ-137
    """
    result = _roundtrip_result()

    lines = _build_zai_quota_lines(result)
    reset_lines = [line for line in lines if line.startswith("Resets in:")]
    assert len(reset_lines) == 3, f"expected 3 reset lines, got {reset_lines!r}"


def test_zai_panel_renders_resets_in_after_cache_roundtrip() -> None:
    """
    @brief Verify the full Z.ai CLI panel renders `Resets in:` after round-trip.
    @details Asserts `_build_result_panel(ProviderName.ZAI, ...)` emits three
    `Resets in:` rows when fed a cache-round-tripped result, proving the panel
    composition path (not only the line builder) restores the reset countdown.
    @return {None} Function return value.
    @satisfies REQ-137
    """
    result = _roundtrip_result()

    _title, panel_lines = _build_result_panel(ProviderName.ZAI, result)
    panel_reset_lines = [
        line for line in panel_lines if line.startswith("Resets in:")
    ]
    assert len(panel_reset_lines) == 3, (
        f"expected 3 panel reset lines, got {panel_reset_lines!r}"
    )


def test_zai_resets_in_renders_in_memory_fresh_fetch() -> None:
    """
    @brief Guard the in-memory fresh-fetch reset rendering against regression.
    @details Asserts the non-serialized datetime path still renders one
    `Resets in:` row per quota so the round-trip-safe fix does not break the
    fresh-fetch rendering used before any cache persistence.
    @return {None} Function return value.
    @satisfies REQ-137
    """
    provider = ZaiProvider(api_key="zai-test-key")
    result = provider._parse_response(_future_quota_document(), WindowPeriod.DAY_30)

    lines = _build_zai_quota_lines(result)
    reset_lines = [line for line in lines if line.startswith("Resets in:")]
    assert len(reset_lines) == 3, f"expected 3 reset lines, got {reset_lines!r}"
