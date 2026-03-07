"""
@file
@brief Chrome extension popup error-rendering contract assertions.
@details Validates that the popup controller hides window progress bars and quota
elements when a provider has an error and no prior populated window data (REQ-055),
and renders both windows and error when prior data persists (REQ-056).
Tests are static source analysis against popup.js.
@satisfies TST-027
@satisfies REQ-055
@satisfies REQ-056
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
POPUP_JS_PATH = PROJECT_ROOT / "src" / "aibar" / "chrome-extension" / "popup.js"


def test_popup_declares_has_populated_windows_helper() -> None:
    """
    @brief Verify popup defines _hasPopulatedWindows detection function.
    @details The helper must check window entries for finite usage_percent,
    remaining, or limit values and return a boolean used to gate window rendering.
    @satisfies REQ-055
    @satisfies REQ-056
    @satisfies TST-027
    """
    source = POPUP_JS_PATH.read_text(encoding="utf-8")
    assert "function _hasPopulatedWindows(provider, windows)" in source
    assert "Number.isFinite" in source[source.index("_hasPopulatedWindows") :]
    assert "usage_percent" in source[source.index("_hasPopulatedWindows") :]
    assert "remaining" in source[source.index("_hasPopulatedWindows") :]
    assert "limit" in source[source.index("_hasPopulatedWindows") :]


def test_popup_render_card_gates_windows_on_has_populated_windows() -> None:
    """
    @brief Verify _renderProviderCard uses _hasPopulatedWindows to gate window rendering.
    @details The card renderer must call _hasPopulatedWindows and only append the
    windows container when the result is true, ensuring empty window bars are hidden
    on error-only state.
    @satisfies REQ-055
    @satisfies TST-027
    """
    source = POPUP_JS_PATH.read_text(encoding="utf-8")
    render_fn_idx = source.index("function _renderProviderCard(provider)")
    # _hasPopulatedWindows must be called inside _renderProviderCard
    check_idx = source.index("_hasPopulatedWindows(", render_fn_idx)
    assert check_idx > render_fn_idx
    # Windows container must be gated by hasWindows conditional
    has_windows_idx = source.index("if (hasWindows)", render_fn_idx)
    windows_class_idx = source.index('"aibar-window-bars"', has_windows_idx)
    assert has_windows_idx < windows_class_idx


def test_popup_render_card_always_renders_error_when_present() -> None:
    """
    @brief Verify error message renders regardless of window data presence.
    @details The error div must be appended after the conditional windows block,
    ensuring errors appear for both error-only and error-with-windows states.
    @satisfies REQ-055
    @satisfies REQ-056
    @satisfies TST-027
    """
    source = POPUP_JS_PATH.read_text(encoding="utf-8")
    render_fn_idx = source.index("function _renderProviderCard(provider)")
    # Error rendering block must exist in _renderProviderCard
    error_check_idx = source.index("providerState.error", render_fn_idx)
    error_class_idx = source.index('"aibar-error"', error_check_idx)
    assert error_check_idx < error_class_idx


def test_popup_render_card_does_not_unconditionally_append_windows() -> None:
    """
    @brief Verify windows container is not appended unconditionally.
    @details Before the fix, _renderProviderCard always appended the windows
    container.  The updated code must gate the container behind
    _hasPopulatedWindows so that error-only cards show no empty bars.
    @satisfies REQ-055
    @satisfies TST-027
    """
    source = POPUP_JS_PATH.read_text(encoding="utf-8")
    render_fn_start = source.index("function _renderProviderCard(provider)")
    # Find the next function boundary (or end of file) to limit scope
    next_fn_idx = source.find("\nfunction ", render_fn_start + 1)
    if next_fn_idx == -1:
        render_fn_body = source[render_fn_start:]
    else:
        render_fn_body = source[render_fn_start:next_fn_idx]
    # The windows container class should only appear inside the hasWindows guard
    windows_class_count = render_fn_body.count('"aibar-window-bars"')
    assert windows_class_count == 1, "windows container must appear exactly once"
    # It must be inside an if (hasWindows) block
    assert "if (hasWindows)" in render_fn_body
