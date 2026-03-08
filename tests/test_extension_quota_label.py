"""
@file
@brief GNOME extension quota-label regressions.
@details Ensures quota-only provider cards use the required credit/reset wording format.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXTENSION_PATH = PROJECT_ROOT / "src" / "aibar" / "gnome-extension" / "aibar@aibar.panel" / "extension.js"
METADATA_PATH = PROJECT_ROOT / "src" / "aibar" / "gnome-extension" / "aibar@aibar.panel" / "metadata.json"
STYLESHEET_PATH = PROJECT_ROOT / "src" / "aibar" / "gnome-extension" / "aibar@aibar.panel" / "stylesheet.css"


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


def test_rate_limit_quota_payloads_do_not_render_error_banner() -> None:
    """
    @brief Verify rate-limit quota payloads bypass extension error-card rendering.
    @satisfies REQ-017
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "const RATE_LIMIT_ERROR_MESSAGE = 'Rate limited. Try again later.';" in source
    assert "const isRateLimitQuotaError = (" in source
    assert (
        "const isError = effectiveError !== null && effectiveError !== undefined && !isRateLimitQuotaError;"
        in source
    )


def test_limit_reached_suffix_is_appended_to_reset_labels_at_displayed_full_usage() -> None:
    """
    @brief Verify reset labels append `⚠️ Limit reached!` for displayed full usage.
    @satisfies REQ-017
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "function _isDisplayedFullPercent(pct)" in source
    assert "const shouldShowLimitReached = allowLimitReached && _isDisplayedFullPercent(pct);" in source
    assert "bar.resetLabel.text = `${baseText} ⚠️ Limit reached!`;" in source


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


def test_panel_indicator_uses_aibar_monitor_name() -> None:
    """
    @brief Verify panel indicator title uses `AIBar Monitor`.
    @satisfies PRJ-004
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "super._init(0.0, 'AIBar Monitor', false);" in source


def test_metadata_declares_aibar_monitor_name() -> None:
    """
    @brief Verify extension metadata name is `AIBar Monitor`.
    @satisfies PRJ-004
    """
    source = METADATA_PATH.read_text(encoding="utf-8")
    assert '"name": "AIBar Monitor"' in source


def test_refresh_now_popup_action_executes_forced_cli_refresh() -> None:
    """
    @brief Verify popup Refresh Now action triggers forced CLI refresh.
    @details Asserts popup wiring calls `_refreshData(true)` and refresh command
    assembly appends `--force` when `forceRefresh` is enabled.
    @return {None} Function return value.
    @satisfies DES-006
    @satisfies REQ-016
    @satisfies TST-004
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "PopupMenu.PopupMenuItem('Refresh Now')" in source
    assert "this._refreshData(true);" in source
    assert "if (forceRefresh)" in source
    assert "commandArgs.push('--force');" in source


def test_provider_card_renders_update_at_label_bottom_right() -> None:
    """
    @brief Verify provider card contains bottom-right Update at label sourced from updated_at.
    @details Asserts extension source creates an `updateAtLabel` in the card and populates
    it from `data.updated_at` using `HH:MM` formatted output, with right-aligned row layout.
    @satisfies REQ-017
    @satisfies TST-004
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "updateAtLabel" in source
    assert "aibar-update-at-label" in source
    assert "aibar-update-at-row" in source
    assert "updateAtSpacer" in source
    assert "data.updated_at" in source
    assert "Update at:" in source


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


def test_popup_open_triggers_bar_width_reapply() -> None:
    """
    @brief Verify popup open-state-changed handler invokes _applyBarWidths.
    @details Ensures progress bar fill widths are recalculated on popup open
    to fix zero-width bars when data arrived while popup was closed.
    @satisfies REQ-017
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "open-state-changed" in source
    assert "_applyBarWidths" in source
    open_idx = source.index("open-state-changed")
    apply_def_idx = source.index("_applyBarWidths()")
    assert open_idx < apply_def_idx, "_applyBarWidths must be defined after open-state-changed connection"
    assert "card._barData.fiveHour" in source
    assert "card._barData.sevenDay" in source
    assert "card._barData.progress" in source


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


def test_extension_reads_gnome_refresh_interval_from_json_extension_section() -> None:
    """
    @brief Verify extension reads gnome_refresh_interval_seconds from JSON extension section.
    @details Asserts extension source parses `json.extension.gnome_refresh_interval_seconds`,
    validates it is a number >= 1, updates `this._refreshIntervalSeconds` when changed,
    and reschedules the auto-refresh timer.
    @satisfies DES-006
    @satisfies REQ-003
    @satisfies TST-004
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "json.extension" in source
    assert "gnome_refresh_interval_seconds" in source
    assert "this._refreshIntervalSeconds" in source
    assert "_startAutoRefresh()" in source
    assert "this._refreshIntervalSeconds = newInterval;" in source


def test_extension_default_refresh_interval_is_60_seconds() -> None:
    """
    @brief Verify GNOME extension default refresh interval constant is 60 seconds.
    @satisfies DES-006
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "const REFRESH_INTERVAL_SECONDS = 60;" in source


def test_extension_auto_refresh_uses_configurable_interval() -> None:
    """
    @brief Verify auto-refresh timer uses `this._refreshIntervalSeconds` not a hard-coded constant.
    @satisfies DES-006
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "this._refreshIntervalSeconds," in source
    assert "REFRESH_INTERVAL_SECONDS," not in source


def test_geminiai_extension_tab_order_label_and_bright_pink_styles() -> None:
    """
    @brief Verify GeminiAI extension integration uses expected order, label, and colors.
    @details Asserts provider ordering array places `geminiai` after `codex`,
    display-name mapping renders `GeminiAI`, and stylesheet defines bright-pink
    tab/card classes for GeminiAI.
    @satisfies REQ-061
    @satisfies REQ-062
    @satisfies TST-029
    """
    extension_source = EXTENSION_PATH.read_text(encoding="utf-8")
    stylesheet_source = STYLESHEET_PATH.read_text(encoding="utf-8")

    assert "this._providerOrder = ['claude', 'openrouter', 'copilot', 'codex', 'geminiai'];" in extension_source
    assert "const PROVIDER_DISPLAY_NAMES = {" in extension_source
    assert "geminiai: 'GeminiAI'" in extension_source
    assert "_getProviderDisplayName(providerName)" in extension_source
    assert "text: _getProviderDisplayName(providerName)" in extension_source

    assert ".aibar-tab-active-geminiai {" in stylesheet_source
    assert ".aibar-tab-label-geminiai {" in stylesheet_source
    assert ".aibar-provider-geminiai {" in stylesheet_source
    assert "#FF1493" in stylesheet_source


def test_extension_uses_cached_status_error_for_provider_cards() -> None:
    """
    @brief Verify extension card rendering consumes cache `status` failure entries.
    @details Asserts update flow resolves window-specific status entries and uses
    `statusEntry.error` fallback when payload data has no inline error.
    @satisfies REQ-061
    @satisfies TST-029
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "const providerStatus = this._statusData[providerName];" in source
    assert "const statusEntry = (" in source
    assert "const statusError = (" in source
    assert "const effectiveError = statusError || data.error;" in source
