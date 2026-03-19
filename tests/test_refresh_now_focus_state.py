"""
@file
@brief Refresh Now focus-state regression tests.
@details Verifies GNOME extension source restores the base visual state for the
Refresh Now popup menu item after focus loss.
"""

from pathlib import Path


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


def test_refresh_now_button_restores_original_color_after_focus_loss() -> None:
    """
    @brief Verify Refresh Now popup item resets visual state after losing focus.
    @details Asserts source includes focus-loss wiring and pseudo-class cleanup
    so the button returns to its original color state.
    @return {None} Function return value.
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "function _resetMenuItemFocusVisualState(menuItem)" in source
    assert "refreshItem.connect('key-focus-out', () => {" in source
    assert "_resetMenuItemFocusVisualState(refreshItem);" in source
    assert "menuItem.remove_style_pseudo_class('focus');" in source
    assert "menuItem.remove_style_pseudo_class('active');" in source
