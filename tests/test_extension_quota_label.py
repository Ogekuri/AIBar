"""
@file
@brief GNOME extension quota-label regressions.
@details Ensures quota-only provider cards use the "remaining credits" suffix.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXTENSION_PATH = PROJECT_ROOT / "src" / "aibar" / "extension" / "aibar@aibar.panel" / "extension.js"


def test_quota_only_label_uses_remaining_credits_suffix() -> None:
    """
    @brief Verify quota-only card labels use "remaining credits".
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert (
        "`${metrics.remaining.toFixed(1)} / ${metrics.limit.toFixed(1)} remaining credits`"
        in source
    )
    assert (
        "`${metrics.remaining.toFixed(1)} / ${metrics.limit.toFixed(1)} credits`"
        not in source
    )


def test_copilot_uses_30d_window_bar_with_reset_before_credits() -> None:
    """
    @brief Verify Copilot card uses 30d window bar and reset label in window-bars section.
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "providerName === 'copilot'" in source
    assert "card.fiveHourBar.label.text = '30d';" in source
    assert "updateWindowBar(card.fiveHourBar, usagePercent, metrics.reset_at || null, true);" in source
    assert "card._barData.sevenDay = null;" in source
    assert "card.sevenDayBar.container.hide();" in source
