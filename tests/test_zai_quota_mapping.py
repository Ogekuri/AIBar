"""
@file
@brief Z.ai quota unit-mapping regression tests.
@details Verifies ZaiProvider projects the Z.ai monitor `data.limits` entries
into the three canonical quotas (5 Hours, Weekly, Monthly Web Search) keyed by
`unit` (3, 6, 5) and exposes each quota `percentage` and `nextResetTime`-derived
`reset_at`. Tests are deterministic and isolated: they exercise the pure
projection path with synthetic documents and never touch network, filesystem,
clock, or configuration state.
@satisfies TST-060
@satisfies REQ-136
@satisfies REQ-137
"""
from datetime import datetime, timezone
import pytest
from aibar.providers.zai import ZaiProvider
_RESET_EPOCH_MS = 1_700_000_000_000
_EXPECTED_RESET_AT = datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc)
def _limit_entry(unit: int, percentage: float, *, number: int) -> dict:
    """
    @brief Build one synthetic Z.ai limit entry for test execution.
    @details Constructs a deterministic `data.limits` record carrying the `unit`
    discriminator, display `number`, `percentage`, and `nextResetTime`
    epoch-millisecond reset timestamp consumed by ZaiProvider projection.
    @param unit {int} Z.ai quota discriminator (3, 6, or 5).
    @param percentage {float} Normalized quota consumption percentage.
    @param number {int} Display-number field preserved from the raw document.
    @return {dict} Synthetic Z.ai limit entry.
    """
    return {
        "unit": unit,
        "number": number,
        "percentage": percentage,
        "nextResetTime": _RESET_EPOCH_MS,
    }
def _zai_document(limits: list[object]) -> dict:
    """
    @brief Wrap synthetic limit entries in the Z.ai monitor document shape.
    @param limits {list[object]} Synthetic limit entries, including malformed
    non-dict values consumed by malformed-entry regression cases.
    @return {dict} Z.ai monitor document with `data.limits` populated.
    """
    return {"code": 200, "data": {"limits": limits}}
def _provider() -> ZaiProvider:
    """
    @brief Construct an isolated ZaiProvider instance for projection tests.
    @details Supplies an explicit API key so initialization never reaches the
    real `Config.get_token` credential-resolution path.
    @return {ZaiProvider} Z.ai provider instance with no external dependencies.
    """
    return ZaiProvider(api_key="zai-test-key")
def test_extract_quotas_maps_all_three_units_in_order() -> None:
    """
    @brief Verify all three unit entries map to canonical quotas in order.
    @details Asserts `data.limits` units 3, 6, 5 project to ordered records with
    keys `5h`, `weekly`, `monthly`, labels `5h`, `1w`, `1m`,
    and that each quota exposes its `percentage` and `nextResetTime`-
    derived `reset_at` plus the raw epoch-millisecond reset value.
    @return {None} Function return value.
    """
    document = _zai_document(
        [
            _limit_entry(unit=3, percentage=42.0, number=5),
            _limit_entry(unit=6, percentage=75.0, number=1),
            _limit_entry(unit=5, percentage=10.0, number=1),
        ]
    )
    quotas = _provider()._extract_quotas(document)
    assert [quota["key"] for quota in quotas] == ["5h", "weekly", "monthly"]
    assert [quota["label"] for quota in quotas] == [
        "5h",
        "1w",
        "1m",
    ]
    assert [quota["percentage"] for quota in quotas] == pytest.approx(
        [42.0, 75.0, 10.0]
    )
    assert all(quota["reset_at"] == _EXPECTED_RESET_AT for quota in quotas)
    assert all(
        quota["reset_at_epoch_ms"] == _RESET_EPOCH_MS for quota in quotas
    )
def test_extract_quotas_returns_only_present_units() -> None:
    """
    @brief Verify absent unit entries are omitted from the projection.
    @details Asserts a document containing only the `unit=3` entry yields exactly
    one `5h` quota without synthesizing missing Weekly or Monthly entries.
    @return {None} Function return value.
    """
    document = _zai_document([_limit_entry(unit=3, percentage=12.5, number=5)])
    quotas = _provider()._extract_quotas(document)
    assert len(quotas) == 1
    assert quotas[0]["key"] == "5h"
    assert quotas[0]["label"] == "5h"
    assert quotas[0]["percentage"] == pytest.approx(12.5)
def test_extract_quotas_normalizes_missing_fields() -> None:
    """
    @brief Verify missing `percentage` and `nextResetTime` normalize safely.
    @details Asserts an entry lacking `percentage` and `nextResetTime` still maps
    to its canonical quota with `percentage=0.0`, `reset_at=None`, and
    `reset_at_epoch_ms=None` rather than raising.
    @return {None} Function return value.
    """
    document = _zai_document([{"unit": 6, "number": 1}])
    quotas = _provider()._extract_quotas(document)
    assert len(quotas) == 1
    assert quotas[0]["key"] == "weekly"
    assert quotas[0]["percentage"] == pytest.approx(0.0)
    assert quotas[0]["reset_at"] is None
    assert quotas[0]["reset_at_epoch_ms"] is None
def test_extract_quotas_ignores_malformed_entries() -> None:
    """
    @brief Verify malformed limit entries are skipped during projection.
    @details Asserts non-dict entries, entries with non-integer `unit`, and
    entries with unknown `unit` values are ignored so only valid quotas project.
    @return {None} Function return value.
    """
    document = _zai_document(
        [
            "not-a-dict",
            {"unit": "bad", "number": 1},
            {"unit": 99, "number": 1},
            _limit_entry(unit=5, percentage=20.0, number=1),
        ]
    )
    quotas = _provider()._extract_quotas(document)
    assert len(quotas) == 1
    assert quotas[0]["key"] == "monthly"
def test_max_percentage_derives_from_highest_quota() -> None:
    """
    @brief Verify aggregate percentage equals the maximum quota percentage.
    @details Asserts `_max_percentage` selects the largest quota percentage so
    the GNOME panel status bar and icon threshold reflect peak consumption.
    @return {None} Function return value.
    """
    provider = _provider()
    quotas = provider._extract_quotas(
        _zai_document(
            [
                _limit_entry(unit=3, percentage=42.0, number=5),
                _limit_entry(unit=6, percentage=75.0, number=1),
                _limit_entry(unit=5, percentage=10.0, number=1),
            ]
        )
    )
    assert provider._max_percentage(quotas) == pytest.approx(75.0)
