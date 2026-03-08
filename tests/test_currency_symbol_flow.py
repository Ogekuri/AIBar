"""
@file
@brief Currency symbol resolution and display tests.
@details Verifies UsageMetrics.currency_symbol default, resolve_currency_symbol
ISO-code and symbol-passthrough logic, and that CLI / GNOME cost rendering
uses metrics.currency_symbol instead of a hardcoded `$`.
@satisfies REQ-049
@satisfies REQ-050
@satisfies REQ-051
@satisfies TST-023
"""

from unittest.mock import MagicMock, patch

import pytest

from aibar.config import (
    DEFAULT_CURRENCY_SYMBOL,
    VALID_CURRENCY_SYMBOLS,
    resolve_currency_symbol,
)
from aibar.providers.base import UsageMetrics


class TestUsageMetricsDefaults:
    """
    @brief UsageMetrics currency_symbol default value tests.
    @satisfies CTN-002
    @satisfies REQ-050
    """

    def test_default_currency_symbol_is_dollar(self) -> None:
        """
        @brief Verify `UsageMetrics.currency_symbol` defaults to `"$"`.
        @return {None} Function return value.
        @satisfies CTN-002
        """
        m = UsageMetrics()
        assert m.currency_symbol == "$"

    def test_currency_symbol_can_be_set_on_construction(self) -> None:
        """
        @brief Verify `UsageMetrics.currency_symbol` accepts any valid symbol at construction.
        @return {None} Function return value.
        @satisfies CTN-002
        """
        for symbol in VALID_CURRENCY_SYMBOLS:
            m = UsageMetrics(currency_symbol=symbol)
            assert m.currency_symbol == symbol


class TestDefaultCurrencySymbolConstant:
    """
    @brief DEFAULT_CURRENCY_SYMBOL constant tests.
    @satisfies REQ-049
    """

    def test_default_currency_symbol_is_dollar(self) -> None:
        """
        @brief Verify `DEFAULT_CURRENCY_SYMBOL` constant equals `"$"`.
        @return {None} Function return value.
        @satisfies REQ-049
        """
        assert DEFAULT_CURRENCY_SYMBOL == "$"

    def test_valid_currency_symbols_contains_expected_set(self) -> None:
        """
        @brief Verify `VALID_CURRENCY_SYMBOLS` contains `$`, `£`, `€`.
        @return {None} Function return value.
        @satisfies REQ-049
        """
        assert "$" in VALID_CURRENCY_SYMBOLS
        assert "£" in VALID_CURRENCY_SYMBOLS
        assert "€" in VALID_CURRENCY_SYMBOLS


class TestResolveCurrencySymbol:
    """
    @brief resolve_currency_symbol unit tests.
    @satisfies REQ-050
    """

    def test_iso_usd_maps_to_dollar(self) -> None:
        """
        @brief Verify ISO code `"USD"` in API raw resolves to `"$"`.
        @return {None} Function return value.
        @satisfies REQ-050
        """
        result = resolve_currency_symbol({"currency": "USD"}, "claude")
        assert result == "$"

    def test_iso_gbp_maps_to_pound(self) -> None:
        """
        @brief Verify ISO code `"GBP"` in API raw resolves to `"£"`.
        @return {None} Function return value.
        @satisfies REQ-050
        """
        result = resolve_currency_symbol({"currency": "GBP"}, "claude")
        assert result == "£"

    def test_iso_eur_maps_to_euro(self) -> None:
        """
        @brief Verify ISO code `"EUR"` in API raw resolves to `"€"`.
        @return {None} Function return value.
        @satisfies REQ-050
        """
        result = resolve_currency_symbol({"currency": "EUR"}, "openrouter")
        assert result == "€"

    def test_symbol_passthrough_dollar(self) -> None:
        """
        @brief Verify direct symbol `"$"` in API raw is returned as-is.
        @return {None} Function return value.
        @satisfies REQ-050
        """
        result = resolve_currency_symbol({"currency": "$"}, "openai")
        assert result == "$"

    def test_symbol_passthrough_pound(self) -> None:
        """
        @brief Verify direct symbol `"£"` in API raw is returned as-is.
        @return {None} Function return value.
        @satisfies REQ-050
        """
        result = resolve_currency_symbol({"currency": "£"}, "openai")
        assert result == "£"

    def test_symbol_passthrough_euro(self) -> None:
        """
        @brief Verify direct symbol `"€"` in API raw is returned as-is.
        @return {None} Function return value.
        @satisfies REQ-050
        """
        result = resolve_currency_symbol({"currency": "€"}, "openai")
        assert result == "€"

    def test_missing_currency_key_falls_back_to_config(self) -> None:
        """
        @brief Verify missing `currency` key falls back to configured provider symbol.
        @return {None} Function return value.
        @satisfies REQ-050
        """
        from unittest.mock import patch

        from aibar.config import RuntimeConfig, resolve_currency_symbol

        fake_config = RuntimeConfig(currency_symbols={"copilot": "£"})
        with patch("aibar.config.load_runtime_config", return_value=fake_config):
            result = resolve_currency_symbol({}, "copilot")
        assert result == "£"

    def test_unknown_currency_value_falls_back_to_config_then_default(self) -> None:
        """
        @brief Verify unrecognised currency value in API raw falls back to default `"$"`.
        @return {None} Function return value.
        @satisfies REQ-050
        """
        result = resolve_currency_symbol({"currency": "UNKNOWN"}, "codex")
        assert result == "$"

    def test_none_raw_falls_back_to_default(self) -> None:
        """
        @brief Verify `None` raw dict falls back to default `"$"`.
        @return {None} Function return value.
        @satisfies REQ-050
        """
        result = resolve_currency_symbol(None, "claude")
        assert result == "$"


class TestCliPrintResultUsesCurrencySymbol:
    """
    @brief CLI _print_result currency symbol display tests.
    @satisfies REQ-051
    """

    def test_print_result_uses_metrics_currency_symbol(self, capsys) -> None:
        """
        @brief Verify `_print_result` renders cost with `metrics.currency_symbol`, not hardcoded `$`.
        @param capsys {pytest.CaptureFixture} Pytest stdout/stderr capture fixture.
        @return {None} Function return value.
        @satisfies REQ-051
        """
        from aibar.cli import _print_result
        from aibar.providers.base import ProviderName, ProviderResult, UsageMetrics, WindowPeriod

        metrics = UsageMetrics(cost=1.2345, currency_symbol="£")
        result = ProviderResult(
            provider=ProviderName.CLAUDE,
            window=WindowPeriod.DAY_7,
            is_error=False,
            metrics=metrics,
        )
        _print_result(ProviderName.CLAUDE, result)

        captured = capsys.readouterr()
        assert "£1.2345" in captured.out
        assert "$1.2345" not in captured.out

    def test_print_result_dollar_symbol_still_works(self, capsys) -> None:
        """
        @brief Verify `_print_result` renders cost with `$` when currency_symbol is `"$"`.
        @param capsys {pytest.CaptureFixture} Pytest stdout/stderr capture fixture.
        @return {None} Function return value.
        @satisfies REQ-051
        """
        from aibar.cli import _print_result
        from aibar.providers.base import ProviderName, ProviderResult, UsageMetrics, WindowPeriod

        metrics = UsageMetrics(cost=0.5000, currency_symbol="$")
        result = ProviderResult(
            provider=ProviderName.OPENAI,
            window=WindowPeriod.DAY_7,
            is_error=False,
            metrics=metrics,
        )
        _print_result(ProviderName.OPENAI, result)

        captured = capsys.readouterr()
        assert "$0.5000" in captured.out

    def test_print_result_uses_blue_panel_and_progress_bar(self, capsys) -> None:
        """
        @brief Verify `_print_result` renders panel borders and progress bar in text mode.
        @param capsys {pytest.CaptureFixture} Pytest stdout/stderr capture fixture.
        @return {None} Function return value.
        @satisfies REQ-067
        """
        from aibar.cli import _print_result
        from aibar.providers.base import ProviderName, ProviderResult, UsageMetrics, WindowPeriod

        metrics = UsageMetrics(limit=100.0, remaining=75.0, currency_symbol="$")
        result = ProviderResult(
            provider=ProviderName.CLAUDE,
            window=WindowPeriod.DAY_7,
            is_error=False,
            metrics=metrics,
        )
        _print_result(ProviderName.CLAUDE, result)
        captured = capsys.readouterr()

        assert "┌" in captured.out
        assert "└" in captured.out
        assert "Usage:" in captured.out
        assert "█" in captured.out
        assert "Updated at:" in captured.out
