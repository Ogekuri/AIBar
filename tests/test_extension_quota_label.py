"""
@file
@brief GNOME extension quota-label regressions.
@details Ensures quota-only provider cards use the required credit/reset wording format.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXTENSION_PATH = PROJECT_ROOT / "src" / "aibar" / "extension" / "aibar@aibar.panel" / "extension.js"


def test_quota_only_label_uses_remaining_credits_prefix_and_bold_remaining() -> None:
    """
    @brief Verify quota-only card labels use required prefix and bold remaining value.
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert (
        "Remaining credits: <b>${metrics.remaining.toFixed(1)}</b>/${metrics.limit.toFixed(1)}"
        in source
    )
    assert "remaining credits" not in source


def test_reset_labels_use_reset_in_prefix_with_colon() -> None:
    """
    @brief Verify extension reset labels use the 'Reset in:' prefix.
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "Reset in:" in source
    assert "Resets in " not in source


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


def test_popup_labels_use_aibar_brand_casing() -> None:
    """
    @brief Verify popup label strings use AIBar casing.
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "text: 'AIBar'," in source
    assert "PopupMenu.PopupMenuItem('Open AIBar UI')" in source
    assert "PopupMenu.PopupMenuItem('Open aibar UI')" not in source


def test_panel_percentage_labels_use_fixed_order_provider_styles_and_primary_bold() -> None:
    """
    @brief Verify panel percentage label order, provider styles, and primary bold classes.
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "this._panelBox.add_child(this._icon);" in source
    assert "this._panelBox.add_child(this._panelPercentages);" in source
    assert "this._panelBox.add_child(this._panelLabel);" in source

    claude_idx = source.index("this._panelPercentages.add_child(this._panelClaudePctLabel);")
    claude_7d_idx = source.index("this._panelPercentages.add_child(this._panelClaude7dPctLabel);")
    copilot_idx = source.index("this._panelPercentages.add_child(this._panelCopilotPctLabel);")
    codex_5h_idx = source.index("this._panelPercentages.add_child(this._panelCodexPctLabel);")
    codex_7d_idx = source.index("this._panelPercentages.add_child(this._panelCodex7dPctLabel);")
    assert claude_idx < claude_7d_idx < copilot_idx < codex_5h_idx < codex_7d_idx

    assert "style_class: 'aibar-panel-pct aibar-panel-pct-primary aibar-tab-label-claude'" in source
    assert "style_class: 'aibar-panel-pct aibar-panel-pct-secondary aibar-tab-label-claude'" in source
    assert "style_class: 'aibar-panel-pct aibar-panel-pct-primary aibar-tab-label-copilot'" in source
    assert "style_class: 'aibar-panel-pct aibar-panel-pct-primary aibar-tab-label-codex'" in source
    assert "style_class: 'aibar-panel-pct aibar-panel-pct-secondary aibar-tab-label-codex'" in source


def test_panel_percentage_labels_hide_when_metrics_are_unavailable() -> None:
    """
    @brief Verify panel percentage labels are omitted when usage metrics are unavailable.
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "label.set_text('');" in source
    assert "label.hide();" in source
    assert "this._panelClaudePctLabel.hide();" in source
    assert "this._panelClaude7dPctLabel.hide();" in source
    assert "this._panelCopilotPctLabel.hide();" in source
    assert "this._panelCodexPctLabel.hide();" in source
    assert "this._panelCodex7dPctLabel.hide();" in source
