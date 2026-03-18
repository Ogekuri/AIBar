"""
@file
@brief GNOME extension quota-label regressions.
@details Ensures quota-only provider cards use the required credit/reset wording format.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXTENSION_PATH = PROJECT_ROOT / "src" / "aibar" / "aibar" / "gnome-extension" / "aibar@aibar.panel" / "extension.js"
METADATA_PATH = PROJECT_ROOT / "src" / "aibar" / "aibar" / "gnome-extension" / "aibar@aibar.panel" / "metadata.json"
STYLESHEET_PATH = PROJECT_ROOT / "src" / "aibar" / "aibar" / "gnome-extension" / "aibar@aibar.panel" / "stylesheet.css"


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


def test_rate_limit_failures_render_error_banner_with_http_retry_metadata() -> None:
    """
    @brief Verify extension error rendering includes status and retry-after diagnostics.
    @satisfies REQ-017
    @satisfies REQ-037
    @satisfies REQ-090
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "function _buildHttpStatusRetryLabel(statusCodeRaw, retryAfterRaw)" in source
    assert "return `HTTP status: ${statusCode}, Retry after: ${retryAfter} sec.`;" in source
    assert "const isError = effectiveError !== null && effectiveError !== undefined;" in source
    assert "const statusRetryLabel = _buildHttpStatusRetryLabel(statusCode, retryAfterSeconds);" in source
    assert "'Status: FAIL'" in source
    assert "`Window: ${windowLabel}`" in source
    assert "`Error: ${effectiveError}`" in source
    assert "card.errorLabel.text = errorLines.join('\\n');" in source
    assert "const isRateLimitQuotaError = (" not in source


def test_limit_reached_suffix_is_appended_to_reset_labels_at_displayed_full_usage() -> None:
    """
    @brief Verify reset labels append `⚠️ Limit reached!` for displayed full usage.
    @satisfies REQ-017
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "function _isDisplayedFullPercent(pct)" in source
    assert "const shouldShowLimitReached = allowLimitReached && _isDisplayedFullPercent(pct);" in source
    assert "bar.resetLabel.text = `${baseText} ⚠️ Limit reached!`;" in source


def test_quota_providers_use_30d_window_bar_with_reset_before_credits() -> None:
    """
    @brief Verify quota providers use single 30d window bar and reset label placement.
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "const WINDOW_BAR_30D_PROVIDERS = new Set(['copilot', 'openrouter', 'openai', 'geminiai']);" in source
    assert "WINDOW_BAR_30D_PROVIDERS.has(providerName)" in source
    assert "card.fiveHourBar.label.text = '30d';" in source
    assert "const singleWindowReset = metrics.reset_at || fiveHourReset || sevenDayReset || null;" in source
    assert "updateWindowBar(card.fiveHourBar, usagePercent, singleWindowReset, true);" in source
    assert "card._barData.sevenDay = null;" in source
    assert "card.sevenDayBar.container.hide();" in source


def test_provider_card_cost_rows_use_costs_prefix_style_parity_and_no_empty_row() -> None:
    """
    @brief Verify extension card cost rows use `Costs:` style parity and hide empty spacer rows.
    @details Asserts provider-card costs render `Costs:` with non-bold values using the same
    `aibar-stat` label class style family as `Remaining credits`, and asserts empty `BYOK` rows
    are hidden so OpenRouter/OpenAI/GeminiAI cards do not leave a blank row after `Costs:`.
    @satisfies REQ-017
    @satisfies TST-004
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "let costLabel = new St.Label({style_class: 'aibar-stat'});" in source
    assert "`Costs: ${_escapeMarkup(costText)} / ${_escapeMarkup(limitText)}`" in source
    assert "`Costs: ${_escapeMarkup(costText)}`" in source
    assert "_boldWhiteMarkup(costText)" not in source
    assert "card.byokLabel.hide();" in source


def test_popup_labels_use_aibar_brand_casing() -> None:
    """
    @brief Verify popup label strings use AIBar casing.
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "text: 'AIBar'," in source
    assert "PopupMenu.PopupMenuItem('Open AIBar Report')" not in source
    assert "PopupMenu.PopupMenuItem('Open AIBar UI')" not in source
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


def test_provider_card_renders_update_at_label_bottom_right_from_freshness() -> None:
    """
    @brief Verify provider card contains bottom-right Updated/Next label sourced from `freshness` timestamps.
    @details Asserts extension source creates an `updateAtLabel` in the card and populates
    it from `json.freshness.<provider>.last_success_timestamp` and
    `json.freshness.<provider>.idle_until_timestamp` using runtime local-time `%Y-%m-%d %H:%M`
    output as `Updated: <YYYY-MM-DD HH:MM>, Next: <YYYY-MM-DD HH:MM>`, with right-aligned row layout.
    @satisfies REQ-017
    @satisfies TST-004
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "updateAtLabel" in source
    assert "aibar-update-at-label" in source
    assert "aibar-update-at-row" in source
    assert "updateAtSpacer" not in source
    assert "json.freshness" in source
    assert "this._freshnessData" in source
    assert "last_success_timestamp" in source
    assert "idle_until_timestamp" in source
    assert "* 1000" in source
    assert "_formatLocalDateTime" in source
    assert "Updated:" in source
    assert "Next:" in source
    assert "getFullYear()" in source
    assert "getHours()" in source
    assert "if (freshnessState" in source
    assert source.index("if (freshnessState") < source.index("if (isError)")
    assert "style_class: 'aibar-reset-label aibar-update-at-label'" in source
    assert "x_align: Clutter.ActorAlign.END" in source
    assert "x_expand: true" in source
    assert "updateAtRow.add_child(updateAtLabel);" in source


def test_extension_builds_freshness_fallback_from_status_updated_at_when_freshness_missing() -> None:
    """
    @brief Verify extension derives `Updated/Next` fallback timestamps from status metadata.
    @details Asserts source defines a fallback helper that reads `statusEntry.updated_at`,
    converts it to epoch seconds, computes `idle_until_timestamp` using idle-delay seconds,
    and reuses fallback in provider-card refresh paths when `freshness` section is absent.
    @return {None} Function return value.
    @satisfies REQ-017
    @satisfies TST-004
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "function _buildFallbackFreshnessState(statusEntry, idleDelaySeconds)" in source
    assert "Date.parse(statusEntry.updated_at)" in source
    assert "const updatedTimestamp = Math.floor(parsedMilliseconds / 1000);" in source
    assert "const idleUntilTimestamp = updatedTimestamp + safeIntervalSeconds;" in source
    assert "const IDLE_DELAY_SECONDS = 300;" in source
    assert "last_success_timestamp: updatedTimestamp," in source
    assert "idle_until_timestamp: idleUntilTimestamp," in source
    assert "_resolveProviderFreshnessState(" in source
    assert "_buildFallbackFreshnessState(statusEntry, idleDelaySeconds);" in source


def test_popup_scroll_view_uses_gnome_compatible_child_attachment() -> None:
    """
    @brief Verify popup scroll-view child wiring avoids runtime TypeError on GNOME Shell.
    @details Asserts `_buildPopupMenu` attaches the provider container through GNOME-compatible
    API checks (`set_child` preferred; guarded `add_actor` fallback) so extension startup does
    not crash on runtimes where `St.ScrollView.add_actor` is unavailable.
    @return {None} Function return value.
    @satisfies REQ-017
    @satisfies TST-004
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "this._providersScrollView = new St.ScrollView({" in source
    assert "style_class: 'aibar-providers-scroll'" in source
    assert "this._providersScrollView.set_policy(St.PolicyType.NEVER, St.PolicyType.AUTOMATIC);" in source
    assert "if (typeof this._providersScrollView.set_child === 'function')" in source
    assert "this._providersScrollView.set_child(this._providersContainer);" in source
    assert "else if (typeof this._providersScrollView.add_actor === 'function')" in source
    assert "this._providersScrollView.add_actor(this._providersContainer);" in source
    assert "providersItem.add_child(this._providersScrollView);" in source


def test_provider_cards_render_zero_api_counters_for_null_metrics() -> None:
    """
    @brief Verify extension cards normalize null API counter metrics to zero for supported providers.
    @details Asserts source defines provider gating for `openai/openrouter/codex/geminiai`
    and renders `requests`/`tokens` labels with explicit null-to-zero fallback logic.
    @return {None} Function return value.
    @satisfies REQ-017
    @satisfies TST-004
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "const API_COUNTER_PROVIDERS = new Set(['openai', 'openrouter', 'codex', 'geminiai']);" in source
    assert "function _providerSupportsApiCounters(providerName)" in source
    assert "const shouldRenderApiCounters = _providerSupportsApiCounters(providerName);" in source
    assert "const requestCount = (" in source
    assert "? metrics.requests" in source
    assert ": 0;" in source
    assert "const inputTokens = (" in source
    assert "const outputTokens = (" in source
    assert "const totalTokens = inputTokens + outputTokens;" in source
    assert "card.requestsLabel.text = `${requestCount.toLocaleString()} requests`;" in source
    assert "card.tokensLabel.text = (" in source
    assert "(${inputTokens.toLocaleString()} in / ${outputTokens.toLocaleString()} out)" in source


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
    claude_cost_idx = source.index("this._panelPercentages.add_child(this._panelClaudeCostLabel);")
    openrouter_cost_idx = source.index("this._panelPercentages.add_child(this._panelOpenRouterCostLabel);")
    copilot_idx = source.index("this._panelPercentages.add_child(this._panelCopilotPctLabel);")
    codex_5h_idx = source.index("this._panelPercentages.add_child(this._panelCodexPctLabel);")
    codex_7d_idx = source.index("this._panelPercentages.add_child(this._panelCodex7dPctLabel);")
    codex_cost_idx = source.index("this._panelPercentages.add_child(this._panelCodexCostLabel);")
    openai_cost_idx = source.index("this._panelPercentages.add_child(this._panelOpenAICostLabel);")
    geminiai_cost_idx = source.index("this._panelPercentages.add_child(this._panelGeminiaiCostLabel);")
    assert (
        claude_idx
        < claude_7d_idx
        < claude_cost_idx
        < openrouter_cost_idx
        < copilot_idx
        < codex_5h_idx
        < codex_7d_idx
        < codex_cost_idx
        < openai_cost_idx
        < geminiai_cost_idx
    )

    assert "style_class: 'aibar-panel-pct aibar-panel-pct-primary aibar-tab-label-claude'" in source
    assert "style_class: 'aibar-panel-pct aibar-panel-pct-secondary aibar-tab-label-claude'" in source
    assert "style_class: 'aibar-panel-pct aibar-panel-cost aibar-tab-label-claude'" in source
    assert "style_class: 'aibar-panel-pct aibar-panel-cost aibar-tab-label-openrouter'" in source
    assert "style_class: 'aibar-panel-pct aibar-panel-pct-primary aibar-tab-label-copilot'" in source
    assert "style_class: 'aibar-panel-pct aibar-panel-pct-primary aibar-tab-label-codex'" in source
    assert "style_class: 'aibar-panel-pct aibar-panel-pct-secondary aibar-tab-label-codex'" in source
    assert "style_class: 'aibar-panel-pct aibar-panel-cost aibar-tab-label-codex'" in source
    assert "style_class: 'aibar-panel-pct aibar-panel-cost aibar-tab-label-openai'" in source
    assert "style_class: 'aibar-panel-pct aibar-panel-cost aibar-tab-label-geminiai'" in source


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
    assert "this._panelClaudeCostLabel.hide();" in source
    assert "this._panelOpenRouterCostLabel.hide();" in source
    assert "this._panelCopilotPctLabel.hide();" in source
    assert "this._panelCodexPctLabel.hide();" in source
    assert "this._panelCodex7dPctLabel.hide();" in source
    assert "this._panelCodexCostLabel.hide();" in source
    assert "this._panelOpenAICostLabel.hide();" in source
    assert "this._panelGeminiaiCostLabel.hide();" in source


def test_panel_cost_text_keeps_zero_values_visible_with_currency_symbol() -> None:
    """
    @brief Verify panel cost formatter returns currency-prefixed text for numeric zero.
    @satisfies TST-007
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "if (metrics.cost === null || metrics.cost === undefined)" in source
    assert "return `${currencySymbol}${numeric.toFixed(2)}`;" in source


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
    assert "idle_delay_seconds" in source
    assert "this._idleDelaySeconds = Math.floor(extensionData.idle_delay_seconds);" in source


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
    @details Asserts provider ordering array places `openai` before `geminiai` with GeminiAI last,
    display-name mapping renders `GEMINIAI`, and stylesheet defines bright-purple
    tab/card classes for GeminiAI.
    @satisfies REQ-061
    @satisfies REQ-062
    @satisfies TST-029
    """
    extension_source = EXTENSION_PATH.read_text(encoding="utf-8")
    stylesheet_source = STYLESHEET_PATH.read_text(encoding="utf-8")

    assert "this._providerOrder = ['claude', 'openrouter', 'copilot', 'codex', 'openai', 'geminiai'];" in extension_source
    assert "const PROVIDER_DISPLAY_NAMES = {" in extension_source
    assert "geminiai: 'GEMINIAI'" in extension_source
    assert "_getProviderDisplayName(providerName)" in extension_source
    assert "text: _getProviderDisplayName(providerName)" in extension_source

    assert ".aibar-tab-active-geminiai {" in stylesheet_source
    assert ".aibar-tab-label-geminiai {" in stylesheet_source
    assert ".aibar-provider-geminiai {" in stylesheet_source
    assert "#BF5AF2" in stylesheet_source


def test_panel_icon_color_thresholds_and_blink_logic_are_defined() -> None:
    """
    @brief Verify panel icon threshold and blink behavior is implemented in source.
    @satisfies REQ-069
    @satisfies TST-007
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "const PANEL_ICON_COLORS = {" in source
    assert "if (safePercent > 75)" in source
    assert "else if (safePercent > 50)" in source
    assert "else if (safePercent > 25)" in source
    assert "const shouldBlink = safePercent > 90;" in source
    assert "GLib.timeout_add_seconds(" in source
    assert "PANEL_ICON_COLORS.redDim" in source


def test_provider_color_palette_is_applied_to_tabs_cards_and_progress_fills() -> None:
    """
    @brief Verify provider bright color palette is applied consistently in stylesheet.
    @satisfies REQ-022
    @satisfies REQ-067
    """
    stylesheet_source = STYLESHEET_PATH.read_text(encoding="utf-8")
    assert ".aibar-tab-label-claude {" in stylesheet_source and "#FF3B30" in stylesheet_source
    assert ".aibar-tab-label-openrouter {" in stylesheet_source and "#FF8C00" in stylesheet_source
    assert ".aibar-tab-label-copilot {" in stylesheet_source and "#FFD60A" in stylesheet_source
    assert ".aibar-tab-label-codex {" in stylesheet_source and "#32D74B" in stylesheet_source
    assert ".aibar-tab-label-openai {" in stylesheet_source and "#0A84FF" in stylesheet_source
    assert ".aibar-tab-label-geminiai {" in stylesheet_source and "#BF5AF2" in stylesheet_source
    assert ".aibar-progress-provider-claude {" in stylesheet_source
    assert ".aibar-progress-provider-openrouter {" in stylesheet_source
    assert ".aibar-progress-provider-copilot {" in stylesheet_source
    assert ".aibar-progress-provider-codex {" in stylesheet_source
    assert ".aibar-progress-provider-openai {" in stylesheet_source
    assert ".aibar-progress-provider-geminiai {" in stylesheet_source


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
    assert "statusEntry.retry_after_seconds" in source
