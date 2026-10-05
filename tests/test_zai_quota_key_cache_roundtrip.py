"""
@file
@brief Z.ai quota-key cache-redaction regression test.
@details Reproduces the GNOME status-bar defect where Z.ai panel percentage
labels disappear whenever the rendered payload is served from
`~/.cache/aibar/cache.json` (the normal idle-time-gated startup path). The
cache sanitizer `_sanitize_cache_payload` redacts the value of every dict field
named `key` (DES-004), and Z.ai quota records named their machine-readable
identifier field `key`, so every cache round-trip produced
`raw.zai_quotas[i].key == "[REDACTED]"`. The GNOME panel matcher requires
`quota.key === '5h' | 'weekly'`, so both Z.ai status-bar labels were hidden on
cached executions while the provider card kept rendering correctly from the
`label` field and array order. The fix renames the constructed record field to
`quota_key`, which is outside the sensitive-key set and survives the cache
round-trip consumed by the panel, the card, and the CLI renderer.
@satisfies REQ-143
@satisfies REQ-137
@satisfies DES-004
"""

from pathlib import Path

import pytest

from aibar.cli import _build_zai_quota_lines
from aibar.config import _sanitize_cache_payload
from aibar.providers.base import ProviderResult, WindowPeriod
from aibar.providers.zai import ZaiProvider

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXTENSION_PATH = (
    PROJECT_ROOT
    / "src"
    / "aibar"
    / "aibar"
    / "gnome-extension"
    / "aibar@aibar.panel"
    / "extension.js"
)

_FIXED_RESET_EPOCH_MS = 3_000_000_000_000
_EXPECTED_QUOTA_KEYS = ["5h", "weekly", "monthly"]
_EXPECTED_QUOTA_LABELS = ["5h", "1w", "1m"]


def _quota_document() -> dict:
    """
    @brief Build a deterministic synthetic Z.ai monitor document.
    @details Wraps the three canonical `data.limits` entries (units 3, 6, 5)
    with fixed percentages and a far-future `nextResetTime` so the round-trip
    result is independent of wall-clock drift.
    @return {dict} Z.ai monitor document with `data.limits` populated.
    """
    return {
        "code": 200,
        "data": {
            "limits": [
                {
                    "unit": 3,
                    "number": 5,
                    "percentage": 38.0,
                    "nextResetTime": _FIXED_RESET_EPOCH_MS,
                },
                {
                    "unit": 6,
                    "number": 1,
                    "percentage": 32.0,
                    "nextResetTime": _FIXED_RESET_EPOCH_MS,
                },
                {
                    "unit": 5,
                    "number": 1,
                    "percentage": 0.0,
                    "nextResetTime": _FIXED_RESET_EPOCH_MS,
                },
            ]
        },
    }


def _sanitized_roundtrip_result() -> ProviderResult:
    """
    @brief Produce a Z.ai result that traversed the cache write/read round-trip.
    @details Builds a fresh in-memory result via `ZaiProvider._parse_response`,
    serializes it with `model_dump(mode="json")` (the shared cache pipeline write
    path), applies `_sanitize_cache_payload` (the exact mutation performed by
    `save_cli_cache` before the disk write), and reloads it via
    `ProviderResult.model_validate` (the `_load_cached_results` read path). This
    is the exact payload state served to the GNOME extension on every cached
    `show --json` execution.
    @return {ProviderResult} Z.ai result reconstructed from sanitized cache data.
    """
    provider = ZaiProvider(api_key="zai-test-key")
    fresh = provider._parse_response(_quota_document(), WindowPeriod.DAY_30)
    cache_document = {"payload": {"zai": {"30d": fresh.model_dump(mode="json")}}}
    sanitized = _sanitize_cache_payload(cache_document)
    return ProviderResult.model_validate(sanitized["payload"]["zai"]["30d"])


def test_zai_quota_keys_survive_cache_sanitizer_roundtrip() -> None:
    """
    @brief Verify Z.ai quota identifiers survive the cache sanitizer round-trip.
    @details Asserts the cache-round-tripped quota records expose
    `quota_key` values `5h`, `weekly`, `monthly` -- the exact values the GNOME
    panel matcher compares -- together with the preserved percentages. Before
    the fix the records carried a `key` field that the cache sanitizer replaced
    with `[REDACTED]`, hiding both Z.ai panel status labels on cached payloads.
    @return {None} Function return value.
    @satisfies REQ-143
    @satisfies DES-004
    """
    result = _sanitized_roundtrip_result()

    quotas = result.raw["zai_quotas"]
    assert [quota["quota_key"] for quota in quotas] == _EXPECTED_QUOTA_KEYS
    assert [quota["label"] for quota in quotas] == _EXPECTED_QUOTA_LABELS
    assert [quota["percentage"] for quota in quotas] == pytest.approx(
        [38.0, 32.0, 0.0]
    )
    assert "[REDACTED]" not in str(quotas)


def test_extension_consume_round_trip_safe_quota_key_field() -> None:
    """
    @brief Verify the GNOME extension reads the sanitizer-safe `quota_key` field.
    @details Asserts the panel usage matcher and the card label fallback source
    `quota.quota_key` and that no consumer still reads the sanitizer-redacted
    `quota.key` field, so panel and card stay consistent for cached payloads.
    @return {None} Function return value.
    @satisfies REQ-143
    @satisfies REQ-137
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")

    assert "const quotaKey = quota.quota_key || '';" in source
    assert "quota.label || quota.quota_key || 'Quota';" in source
    assert "quota.key" not in source


def test_zai_cli_quota_labels_render_after_sanitizer_roundtrip() -> None:
    """
    @brief Verify CLI Z.ai quota rows keep canonical labels after the round-trip.
    @details Asserts `_build_zai_quota_lines` emits one usage row per quota whose
    window label resolves to `5h`, `1w`, `1m` from the sanitized round-tripped
    records, guarding the CLI label fallback against the renamed field.
    @return {None} Function return value.
    @satisfies REQ-137
    @satisfies REQ-140
    """
    result = _sanitized_roundtrip_result()

    usage_lines = [
        line
        for line in _build_zai_quota_lines(result)
        if line.startswith("Usage:")
    ]
    assert [line.split(" ")[1] for line in usage_lines] == _EXPECTED_QUOTA_LABELS
