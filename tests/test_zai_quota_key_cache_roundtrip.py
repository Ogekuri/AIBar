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
import json
import shutil
import subprocess
import tempfile

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
    @brief Verify the GNOME extension reads quota identifiers shape-tolerantly.
    @details Asserts the panel usage matcher prefers the sanitizer-safe
    `quota_key` field, accepts the legacy `key` field emitted by pre-migration
    CLI builds and cached payloads, and that the card label fallback uses the
    same identifier chain, so panel and card stay consistent for every payload
    shape.
    @return {None} Function return value.
    @satisfies REQ-143
    @satisfies REQ-137
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")

    assert "const quotaKey = quota.quota_key || quota.key || '';" in source
    assert "quota.label || quota.quota_key || quota.key || 'Quota';" in source


def test_zai_panel_values_render_for_all_payload_shapes() -> None:
    """
    @brief Verify Z.ai panel percentages render for every quota payload shape.
    @details Executes the real `getPanelUsageValues` extracted from
    `extension.js` under node against three payload shapes: the current
    `quota_key` shape, the legacy `key` shape emitted by pre-migration CLI
    builds, and a sanitizer-redacted shape. The panel matcher MUST return the
    canonical 5h/weekly percentages in every case, mirroring the card, which
    renders from `label` fields and array order and therefore never hides Z.ai
    quota bars.
    @return {None} Function return value.
    @satisfies REQ-143
    @satisfies REQ-140
    """
    if shutil.which("node") is None:
        pytest.skip("node runtime unavailable")

    harness = """
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
function sliceConst(name, stopMarker) {
    const start = src.indexOf('const ' + name + ' = ');
    const end = src.indexOf(stopMarker, start);
    if (start < 0 || end < 0) throw new Error('slice failed for ' + name);
    return src.slice(start, end).trim().replace(/;$/, '');
}
const toPercentSrc = sliceConst('toPercent', 'const getPanelUsageValues');
const panelSrc = sliceConst(
    'getPanelUsageValues', 'const claudeUsage = getPanelUsageValues'
);
const getPanelUsageValues = eval(toPercentSrc + ';' + panelSrc + ';getPanelUsageValues');
const metrics = {limit: 100.0, remaining: 86.0};
const buildData = (identifierField, identifierValue) => ({
    metrics,
    raw: {zai_quotas: [
        {[identifierField]: identifierValue, label: '5h', percentage: 11.0},
        {[identifierField]: identifierValue === '5h' ? 'weekly' : identifierValue,
            label: '1w', percentage: 7.0},
        {[identifierField]: 'monthly', label: '1m', percentage: 0.0},
    ]},
});
const fresh = getPanelUsageValues('zai', buildData('quota_key', '5h'));
const legacy = getPanelUsageValues('zai', buildData('key', '5h'));
const redacted = getPanelUsageValues('zai', buildData('key', '[REDACTED]'));
console.log(JSON.stringify({fresh, legacy, redacted}));
"""
    with tempfile.NamedTemporaryFile(
        "w", suffix=".js", encoding="utf-8", delete=False
    ) as harness_file:
        harness_file.write(harness)
        harness_path = harness_file.name
    try:
        completed = subprocess.run(
            ["node", harness_path, str(EXTENSION_PATH)],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
    finally:
        Path(harness_path).unlink(missing_ok=True)

    rendered = json.loads(completed.stdout.strip().splitlines()[-1])
    for shape in ("fresh", "legacy", "redacted"):
        assert rendered[shape]["primary"] == pytest.approx(11.0), shape
        assert rendered[shape]["secondary"] == pytest.approx(7.0), shape
        assert rendered[shape]["max"] == pytest.approx(11.0), shape


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
