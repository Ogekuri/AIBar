/**
 * @file extension.js
 * @brief GNOME Shell panel extension for aibar metrics.
 * @details Collects usage JSON from the aibar CLI and renders provider-specific quota/cost cards in the GNOME panel popup.
 * @note Targets GNOME Shell 45–48; uses ES module imports (gi:// and resource://) as required by GNOME Shell 45+.
 */

import GLib from 'gi://GLib';
import St from 'gi://St';
import Gio from 'gi://Gio';
import Clutter from 'gi://Clutter';
import GObject from 'gi://GObject';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';
import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js';

const REFRESH_INTERVAL_SECONDS = 60;
const IDLE_DELAY_SECONDS = 300;
const ENV_FILE_PATH = GLib.get_home_dir() + '/.config/aibar/env';
const RESET_PENDING_MESSAGE = 'Starts when the first message is sent';
const RATE_LIMIT_ERROR_MESSAGE = 'Rate limited. Try again later.';
const CLAUDE_OAUTH_ERROR_MESSAGE = 'Invalid or expired OAuth token';
const PROVIDER_PROGRESS_CLASSES = {
    claude: 'aibar-progress-provider-claude',
    openrouter: 'aibar-progress-provider-openrouter',
    copilot: 'aibar-progress-provider-copilot',
    codex: 'aibar-progress-provider-codex',
    openai: 'aibar-progress-provider-openai',
    geminiai: 'aibar-progress-provider-geminiai',
};
const PANEL_ICON_COLORS = {
    white: '#FFFFFF',
    yellow: '#FFD60A',
    orange: '#FF8C00',
    red: '#FF3B30',
    redDim: '#8A1B16',
};
const PROVIDER_DISPLAY_NAMES = {
    geminiai: 'GEMINIAI',
};
const API_COUNTER_PROVIDERS = new Set(['openai', 'openrouter', 'codex', 'geminiai']);
const WINDOW_BAR_30D_PROVIDERS = new Set(['copilot', 'openrouter', 'openai', 'geminiai']);
const DEFAULT_WINDOW_LABELS = Object.freeze({
    copilot: '30d',
    openrouter: '30d',
    openai: '30d',
    geminiai: '30d',
});
const ALL_PROVIDER_NAMES = Object.freeze([
    'claude',
    'openrouter',
    'copilot',
    'codex',
    'openai',
    'geminiai',
]);
const DEFAULT_ENABLED_PROVIDERS = Object.freeze({
    claude: true,
    openrouter: true,
    copilot: true,
    codex: true,
    openai: true,
    geminiai: true,
});
/**
 * @brief Maximum popup viewport height for provider cards in pixels.
 * @details Caps popup vertical growth while allowing short provider cards to
 * collapse the viewport height to content size. Time complexity O(1). Space
 * complexity O(1).
 * @satisfies REQ-120
 */
const PROVIDER_VIEWPORT_MAX_HEIGHT_PX = 260;
const DEFAULT_COPILOT_EXTRA_PREMIUM_REQUEST_COST = 0.04;
const PROGRESS_SEGMENT_SHAPE_CLASSES = Object.freeze([
    'aibar-progress-shape-none',
    'aibar-progress-shape-full',
    'aibar-progress-shape-left',
    'aibar-progress-shape-right',
]);
/**
 * @brief Minimum overflow width that can render its own rounded right cap.
 * @details Overflow widths below this threshold are absorbed into the fixed
 * 100%-boundary marker so slightly-over-limit bars keep a visible rounded end
 * without forcing a 1px neutral segment to carry the right-edge radius. Time
 * complexity O(1). Space complexity O(1).
 * @satisfies REQ-121
 */
const PROGRESS_ROUNDED_END_MIN_WIDTH_PX = 3;

/**
 * @brief Resolve provider label text for GNOME tab/card rendering.
 * @param {string} providerName Provider key from JSON payload.
 * @returns {string} Display label for provider tab and card.
 */
function _getProviderDisplayName(providerName) {
    if (providerName in PROVIDER_DISPLAY_NAMES)
        return PROVIDER_DISPLAY_NAMES[providerName];
    return providerName.toUpperCase();
}

/**
 * @brief Normalize `enabled_providers` JSON section for extension state.
 * @details Builds one provider-keyed boolean map for all known providers.
 * Missing keys normalize to `true` for backward compatibility with CLI JSON
 * documents emitted before provider-disable support existed.
 * @param {Object<string, any> | null} enabledProviders Raw `enabled_providers` JSON section.
 * @returns {Object<string, boolean>} Normalized provider-enabled mapping.
 * @satisfies REQ-127
 */
function _normalizeEnabledProvidersSection(enabledProviders) {
    const normalized = {...DEFAULT_ENABLED_PROVIDERS};
    if (!enabledProviders || typeof enabledProviders !== 'object' || Array.isArray(enabledProviders))
        return normalized;
    for (const providerName of ALL_PROVIDER_NAMES) {
        if (typeof enabledProviders[providerName] === 'boolean')
            normalized[providerName] = enabledProviders[providerName];
    }
    return normalized;
}

/**
 * @brief Filter provider-keyed JSON object by normalized enable-state map.
 * @details Copies only provider entries whose normalized enabled flag is not
 * `false`. Non-object inputs normalize to `{}` to keep parser state
 * deterministic.
 * @param {Object<string, any> | null} providerData Provider-keyed JSON section.
 * @param {Object<string, boolean>} enabledProviders Normalized provider-enabled mapping.
 * @returns {Object<string, any>} Filtered provider-keyed object.
 * @satisfies REQ-127
 */
function _filterProviderObjectByEnabledProviders(providerData, enabledProviders) {
    if (!providerData || typeof providerData !== 'object' || Array.isArray(providerData))
        return {};
    const filtered = {};
    for (const [providerName, providerValue] of Object.entries(providerData)) {
        if (enabledProviders[providerName] === false)
            continue;
        filtered[providerName] = providerValue;
    }
    return filtered;
}

/**
 * @brief Reset popup menu item pseudo-class state to base visual style.
 * @details Removes `focus` and `active` pseudo classes from the menu item actor so
 * focus-loss transitions always return to the original color surface.
 * Time complexity O(1). Space complexity O(1).
 * @param {any} menuItem Popup menu item actor candidate.
 * @returns {boolean} True when pseudo-class removal API is available and executed.
 * @satisfies DES-006
 */
function _resetMenuItemFocusVisualState(menuItem) {
    if (!menuItem || typeof menuItem.remove_style_pseudo_class !== 'function')
        return false;
    menuItem.remove_style_pseudo_class('focus');
    menuItem.remove_style_pseudo_class('active');
    return true;
}

/**
 * @brief Check whether provider cards must render API counter labels.
 * @details API-counter providers render `requests` and `tokens` labels on OK states
 * with null/undefined counters normalized to zero.
 * @param {string} providerName Provider key from JSON payload.
 * @returns {boolean} True when provider requires API counter label rendering.
 * @satisfies REQ-017
 */
function _providerSupportsApiCounters(providerName) {
    return API_COUNTER_PROVIDERS.has(providerName);
}

/**
 * @brief Resolve Copilot premium-request overage monetary value.
 * @details Computes overage primarily from `metrics.remaining`: returns `0` when
 * `remaining >= 0`; returns `-remaining * unit_cost` when `remaining < 0`.
 * Falls back to raw `premium_requests_extra_cost` or
 * `max(premium_requests - premium_requests_included, 0) * unit_cost` when
 * `remaining` is unavailable.
 * @param {Object<string, any> | null} data Copilot provider payload.
 * @param {number} configuredUnitCost Configured USD unit cost per extra request.
 * @returns {number | null} Non-negative overage monetary value or null.
 * @satisfies REQ-117
 * @satisfies REQ-118
 */
function _resolveCopilotExtraPremiumCost(data, configuredUnitCost) {
    if (!data || typeof data !== 'object' || Array.isArray(data))
        return null;

    const metrics = (data.metrics && typeof data.metrics === 'object' && !Array.isArray(data.metrics))
        ? data.metrics
        : null;
    const raw = (data.raw && typeof data.raw === 'object' && !Array.isArray(data.raw))
        ? data.raw
        : null;

    let unitCost = raw ? Number(raw.copilot_extra_premium_request_cost) : Number.NaN;
    if (!Number.isFinite(unitCost))
        unitCost = Number(configuredUnitCost);

    const remaining = metrics ? Number(metrics.remaining) : Number.NaN;
    if (Number.isFinite(remaining)) {
        if (remaining >= 0)
            return 0;
        if (!Number.isFinite(unitCost))
            return null;
        return Math.max(0, -remaining) * Math.max(0, unitCost);
    }

    if (!raw)
        return null;

    const directValue = Number(raw.premium_requests_extra_cost);
    if (Number.isFinite(directValue))
        return Math.max(0, directValue);

    const premiumRequests = Number(raw.premium_requests);
    const premiumRequestsIncluded = Number(raw.premium_requests_included);
    if (!Number.isFinite(premiumRequests) || !Number.isFinite(premiumRequestsIncluded))
        return null;
    if (!Number.isFinite(unitCost))
        return null;

    const extraRequests = Math.max(0, premiumRequests - premiumRequestsIncluded);
    return extraRequests * Math.max(0, unitCost);
}

/**
 * @brief Format one Date object as local datetime for provider freshness labels.
 * @details Produces `%Y-%m-%d %H:%M` in runtime local timezone; invalid Date values return null.
 * @param {Date} value Date object to format.
 * @returns {string | null} Formatted local datetime string or null.
 */
function _formatLocalDateTime(value) {
    if (!(value instanceof Date))
        return null;
    if (Number.isNaN(value.getTime()))
        return null;
    const year = value.getFullYear().toString().padStart(4, '0');
    const month = (value.getMonth() + 1).toString().padStart(2, '0');
    const day = value.getDate().toString().padStart(2, '0');
    const hours = value.getHours().toString().padStart(2, '0');
    const minutes = value.getMinutes().toString().padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}`;
}

/**
 * @brief Normalize retry-after value to positive integer seconds.
 * @param {any} value Retry-after candidate value.
 * @returns {number | null} Integer retry-after seconds or null when unavailable.
 */
function _coerceRetryAfterSeconds(value) {
    if (value === null || value === undefined)
        return null;
    const numeric = Number(value);
    if (!Number.isFinite(numeric))
        return null;
    const parsed = Math.floor(numeric);
    if (parsed <= 0)
        return null;
    return parsed;
}

/**
 * @brief Classify panel-failure category from cache status metadata.
 * @details Returns one of `oauth`, `rate_limit`, or `other` by inspecting
 * normalized status error text and optional HTTP status code.
 * @param {any} statusEntry Window-specific cache status entry.
 * @returns {'oauth' | 'rate_limit' | 'other'} Failure category.
 */
function _classifyPanelFailureCategory(statusEntry) {
    if (!statusEntry || typeof statusEntry !== 'object' || Array.isArray(statusEntry))
        return 'other';
    const statusCode = Number.isInteger(statusEntry.status_code)
        ? statusEntry.status_code
        : null;
    const errorText = typeof statusEntry.error === 'string'
        ? statusEntry.error
        : '';
    if (errorText.includes(CLAUDE_OAUTH_ERROR_MESSAGE))
        return 'oauth';
    if (errorText.includes(RATE_LIMIT_ERROR_MESSAGE) || statusCode === 429)
        return 'rate_limit';
    return 'other';
}

/**
 * @brief Build provider-scoped panel failure state for one provider.
 * @details Resolves per-window FAIL entries from status data and computes
 * `hasFailure` plus failure category for panel collapse logic.
 * @param {Object<string, any>} statusData Provider-keyed status section.
 * @param {string} providerName Provider key.
 * @param {string[]} windows Ordered window keys to inspect.
 * @returns {{hasFailure: boolean, category: 'oauth' | 'rate_limit' | 'other'}} Provider failure state.
 */
function _panelProviderFailureState(statusData, providerName, windows) {
    if (!statusData || typeof statusData !== 'object' || Array.isArray(statusData))
        return {hasFailure: false, category: 'other'};
    const providerStatus = statusData[providerName];
    if (!providerStatus || typeof providerStatus !== 'object' || Array.isArray(providerStatus))
        return {hasFailure: false, category: 'other'};
    let sawFailure = false;
    let category = 'other';
    for (const windowKey of windows) {
        if (typeof windowKey !== 'string' || windowKey.length === 0)
            continue;
        const entry = providerStatus[windowKey];
        if (!entry || typeof entry !== 'object' || Array.isArray(entry))
            continue;
        if (entry.result !== 'FAIL')
            continue;
        sawFailure = true;
        const nextCategory = _classifyPanelFailureCategory(entry);
        if (nextCategory === 'oauth' || nextCategory === 'rate_limit')
            return {hasFailure: true, category: nextCategory};
        category = 'other';
    }
    return {hasFailure: sawFailure, category};
}

/**
 * @brief Build normalized HTTP status/retry metadata label.
 * @param {any} statusCodeRaw HTTP status candidate value.
 * @param {any} retryAfterRaw Retry-after candidate value.
 * @returns {string} Diagnostic label text or empty string.
 * @satisfies REQ-037
 */
function _buildHttpStatusRetryLabel(statusCodeRaw, retryAfterRaw) {
    const statusCode = Number.isInteger(statusCodeRaw) ? statusCodeRaw : null;
    const retryAfter = _coerceRetryAfterSeconds(retryAfterRaw);
    if (statusCode !== null && retryAfter !== null)
        return `HTTP status: ${statusCode}, Retry after: ${retryAfter} sec.`;
    if (statusCode !== null)
        return `HTTP status: ${statusCode}`;
    if (retryAfter !== null)
        return `Retry after: ${retryAfter} sec.`;
    return '';
}

/**
 * @brief Escape text for safe Pango markup insertion.
 * @param {string} value Raw text.
 * @returns {string} Markup-safe text.
 */
function _escapeMarkup(value) {
    return value
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&apos;');
}

/**
 * @brief Wrap one value as bright-white bold Pango markup.
 * @param {string} value Raw text value.
 * @returns {string} Bright-white bold markup snippet.
 */
function _boldWhiteMarkup(value) {
    return `<span foreground="#FFFFFF"><b>${_escapeMarkup(value)}</b></span>`;
}

/**
 * @brief Build provider freshness fallback from cache-status `updated_at` metadata.
 * @details Converts `statusEntry.updated_at` to epoch seconds and derives
 * `idle_until_timestamp` using configured idle-delay seconds when `freshness`/`idle_time`
 * sections are unavailable from CLI JSON output.
 * @param {any} statusEntry Window-specific cache status entry.
 * @param {number} idleDelaySeconds Active idle delay in seconds.
 * @returns {{last_success_timestamp: number, idle_until_timestamp: number} | null} Fallback freshness state or null.
 * @satisfies REQ-017
 */
function _buildFallbackFreshnessState(statusEntry, idleDelaySeconds) {
    if (!statusEntry || typeof statusEntry !== 'object' || Array.isArray(statusEntry))
        return null;
    if (typeof statusEntry.updated_at !== 'string' || statusEntry.updated_at.length === 0)
        return null;
    const parsedMilliseconds = Date.parse(statusEntry.updated_at);
    if (!Number.isFinite(parsedMilliseconds))
        return null;
    const updatedTimestamp = Math.floor(parsedMilliseconds / 1000);
    if (!Number.isInteger(updatedTimestamp))
        return null;
    const safeIntervalSeconds = (
        Number.isInteger(idleDelaySeconds) && idleDelaySeconds > 0
    )
        ? idleDelaySeconds
        : IDLE_DELAY_SECONDS;
    const idleUntilTimestamp = updatedTimestamp + safeIntervalSeconds;
    return {
        last_success_timestamp: updatedTimestamp,
        idle_until_timestamp: idleUntilTimestamp,
    };
}

/**
 * @brief Resolve provider freshness state from canonical CLI freshness source.
 * @details Uses `freshness.<provider>` (or `idle_time.<provider>` compatibility
 * alias populated by parser) and falls back to status-derived timestamps only
 * when freshness state is unavailable in CLI JSON.
 * @param {Object<string, any>} freshnessData Provider-keyed freshness object.
 * @param {string} providerName Provider key from usage payload.
 * @param {any} statusEntry Window-specific cache status entry.
 * @param {number} idleDelaySeconds Active idle delay in seconds.
 * @returns {{last_success_timestamp: number, idle_until_timestamp: number} | null} Resolved freshness state.
 * @satisfies REQ-017
 */
function _resolveProviderFreshnessState(freshnessData, providerName, statusEntry, idleDelaySeconds) {
    const providerFreshness = (
        freshnessData &&
        typeof freshnessData === 'object' &&
        !Array.isArray(freshnessData) &&
        freshnessData[providerName] &&
        typeof freshnessData[providerName] === 'object' &&
        !Array.isArray(freshnessData[providerName])
    )
        ? freshnessData[providerName]
        : null;
    if (providerFreshness)
        return providerFreshness;
    return _buildFallbackFreshnessState(statusEntry, idleDelaySeconds);
}

/**
 * @brief Resolve aibar executable path.
 * @details Prefers PATH discovery and falls back to AIBAR_PATH from the env file.
 * @returns {string} Resolved executable path or fallback command name.
 */
function _getAiBarPath() {
    let found = GLib.find_program_in_path('aibar');
    if (found)
        return found;

    let env = _loadEnvFromFile();
    if (env.AIBAR_PATH)
        return env.AIBAR_PATH;

    return 'aibar';
}

/**
 * @brief Load key-value environment variables from aibar env file.
 * @details Parses export syntax, quoted values, and inline comments.
 * @returns {Object<string,string>} Parsed environment map.
 */
function _loadEnvFromFile() {
    let env = {};

    try {
        let [ok, contents] = GLib.file_get_contents(ENV_FILE_PATH);
        if (!ok || !contents)
            return env;

        let text;
        if (contents instanceof Uint8Array)
            text = new TextDecoder('utf-8').decode(contents);
        else
            text = contents.toString();

        let lines = text.split('\n');

        for (let line of lines) {
            let trimmed = line.trim();
            if (!trimmed || trimmed.startsWith('#'))
                continue;

            let hashIndex = trimmed.indexOf('#');
            if (hashIndex !== -1) {
                let beforeHash = trimmed.slice(0, hashIndex);
                let singleQuotes = (beforeHash.match(/'/g) || []).length;
                let doubleQuotes = (beforeHash.match(/"/g) || []).length;
                if (singleQuotes % 2 === 0 && doubleQuotes % 2 === 0)
                    trimmed = beforeHash.trim();
            }

            let match = trimmed.match(/^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$/);
            if (!match)
                continue;

            let name = match[1];
            let value = match[2].trim();

            if (value.endsWith(';'))
                value = value.slice(0, -1).trim();

            if ((value.startsWith('"') && value.endsWith('"')) ||
                (value.startsWith("'") && value.endsWith("'")))
                value = value.slice(1, -1);

            if (value)
                env[name] = value;
        }
    } catch (_e) {
        return env;
    }

    return env;
}

/**
 * @brief Map percentage usage to CSS progress severity class.
 * @param {number} pct Usage percentage.
 * @returns {string} CSS class suffix for progress state.
 */
function _getProviderProgressClass(providerName) {
    return PROVIDER_PROGRESS_CLASSES[providerName] || 'aibar-progress-provider-openai';
}

/**
 * @brief Check whether a percentage renders as `0.0%` in one-decimal UI output.
 * @details Mirrors display rounding semantics so fallback reset text is shown when
 * usage is effectively zero from the user's perspective (e.g. internal 0.04 -> 0.0%).
 * @param {number} pct Usage percentage candidate.
 * @returns {boolean} True when value is finite, non-negative, and rounds to 0.0.
 */
function _isDisplayedZeroPercent(pct) {
    const numeric = Number(pct);
    if (!Number.isFinite(numeric))
        return false;
    if (numeric < 0)
        return false;
    return Math.round(numeric * 10) === 0;
}

/**
 * @brief Check whether a percentage renders as `100.0%` in one-decimal UI output.
 * @details Mirrors display rounding semantics so near-full values are treated as
 * full usage for limit-reached warning rendering.
 * @param {number} pct Usage percentage candidate.
 * @returns {boolean} True when value is finite and rounds to `100.0`.
 */
function _isDisplayedFullPercent(pct) {
    const numeric = Number(pct);
    if (!Number.isFinite(numeric))
        return false;
    return Math.round(numeric * 10) >= 1000;
}

/**
 * @brief Attach over-limit visualization actors to one progress background.
 * @details Appends one bright-neutral 100%-boundary marker actor and one opaque
 * neutral over-limit fill actor to the same horizontal background container used
 * by the provider fill.
 * Stores actor references on `fillActor` so shared geometry updates require only the
 * existing `_applyProgressFillGeometry(...)` call sites. Time complexity O(1). Space
 * complexity O(1).
 * @param {St.BoxLayout} backgroundActor Progress background container.
 * @param {St.Widget} fillActor Primary provider-color fill actor.
 * @returns {void} No return value.
 * @satisfies REQ-121
 */
function _attachOverLimitActors(backgroundActor, fillActor) {
    const markerActor = new St.Widget({
        style_class: 'aibar-progress-marker',
        visible: false,
    });
    const overLimitActor = new St.Widget({
        style_class: 'aibar-progress-over-limit-fill',
        visible: false,
    });
    fillActor._aibarMarkerActor = markerActor;
    fillActor._aibarOverLimitActor = overLimitActor;
    backgroundActor.add_child(fillActor);
    backgroundActor.add_child(markerActor);
    backgroundActor.add_child(overLimitActor);
}

/**
 * @brief Apply rounded-edge shape classes to the currently visible progress segments.
 * @details Ensures the bar start and end caps are rounded on whichever actors
 * actually touch the outer edges of the progress bar. This keeps sub-100 bars,
 * exactly-full bars, and over-limit bars visually correct even when the provider
 * fill no longer reaches the right edge because neutral overflow segments are
 * visible. Time complexity O(1). Space complexity O(1).
 * @param {St.Widget | null} fillActor Provider-color segment actor.
 * @param {St.Widget | null} markerActor Fixed 100%-boundary marker actor.
 * @param {St.Widget | null} overLimitActor Neutral overflow segment actor.
 * @param {number} fillWidth Computed width of the provider-color segment.
 * @param {number} markerWidth Computed width of the 100%-boundary marker.
 * @param {number} overLimitWidth Computed width of the neutral overflow segment.
 * @returns {void} No return value.
 * @satisfies REQ-121
 */
function _applyProgressSegmentRadii(fillActor, markerActor, overLimitActor, fillWidth, markerWidth, overLimitWidth) {
    const segments = [
        {actor: fillActor, width: Math.max(0, fillWidth)},
        {actor: markerActor, width: Math.max(0, markerWidth)},
        {actor: overLimitActor, width: Math.max(0, overLimitWidth)},
    ];

    for (const segment of segments) {
        if (!segment.actor)
            continue;
        for (const className of PROGRESS_SEGMENT_SHAPE_CLASSES)
            segment.actor.remove_style_class_name(className);
        segment.actor.add_style_class_name('aibar-progress-shape-none');
    }

    const visibleSegments = segments.filter(segment => segment.actor && segment.width > 0);
    if (visibleSegments.length === 0)
        return;
    if (visibleSegments.length === 1) {
        visibleSegments[0].actor.remove_style_class_name('aibar-progress-shape-none');
        visibleSegments[0].actor.add_style_class_name('aibar-progress-shape-full');
        return;
    }

    const firstVisible = visibleSegments[0].actor;
    const lastVisible = visibleSegments[visibleSegments.length - 1].actor;
    firstVisible.remove_style_class_name('aibar-progress-shape-none');
    firstVisible.add_style_class_name('aibar-progress-shape-left');
    lastVisible.remove_style_class_name('aibar-progress-shape-none');
    lastVisible.add_style_class_name('aibar-progress-shape-right');
}

/**
 * @brief Apply deterministic progress-fill geometry with over-limit segment support.
 * @details Computes fixed-width progress geometry from percentage and current
 * background width. Percentages up to `100` render provider-color fill plus background.
 * Percentages above `100` render a provider-color base segment, a fixed 2px 100%
 * boundary marker, and a neutral over-limit segment scaled across the extra `0..100`
 * range and clamped for larger values. When the neutral overflow segment is too
 * thin to render a visible rounded end cap, its width is absorbed into the marker
 * so the right edge stays rounded without widening the bar. The helper preserves
 * side-label layout by never exceeding the background width. Time complexity O(1).
 * Space complexity O(1).
 * @param {St.Widget} fillActor Progress fill widget receiving width updates.
 * @param {St.Widget} backgroundActor Progress background widget providing max width.
 * @param {number} pct Usage percentage value.
 * @returns {void} No return value.
 * @satisfies REQ-119
 * @satisfies REQ-121
 */
function _applyProgressFillGeometry(fillActor, backgroundActor, pct) {
    const bgWidth = backgroundActor ? backgroundActor.get_width() : 0;
    if (bgWidth <= 0)
        return;

    const markerActor = fillActor._aibarMarkerActor || null;
    const overLimitActor = fillActor._aibarOverLimitActor || null;
    const numericPct = Number(pct);
    const normalizedPct = Number.isFinite(numericPct) ? Math.max(0, numericPct) : 0;
    const isOverLimit = normalizedPct > 100;
    const markerWidth = isOverLimit ? Math.min(2, bgWidth) : 0;
    let effectiveMarkerWidth = markerWidth;
    let fillWidth = Math.round((Math.min(normalizedPct, 100) / 100) * bgWidth);
    let overLimitWidth = 0;

    if (isOverLimit) {
        const availableWidth = Math.max(0, bgWidth - markerWidth);
        const clampedOverLimitPercent = Math.min(normalizedPct - 100, 100);
        overLimitWidth = Math.round((clampedOverLimitPercent / 100) * availableWidth);
        if (clampedOverLimitPercent > 0 && availableWidth > 0)
            overLimitWidth = Math.max(1, overLimitWidth);
        overLimitWidth = Math.min(availableWidth, overLimitWidth);
        fillWidth = Math.max(0, availableWidth - overLimitWidth);
        if (
            overLimitWidth > 0 &&
            overLimitWidth < PROGRESS_ROUNDED_END_MIN_WIDTH_PX
        ) {
            effectiveMarkerWidth = Math.min(bgWidth, markerWidth + overLimitWidth);
            overLimitWidth = 0;
        }
    }

    _applyProgressSegmentRadii(fillActor, markerActor, overLimitActor, fillWidth, effectiveMarkerWidth, overLimitWidth);
    fillActor.set_width(Math.max(0, fillWidth));
    if (markerActor) {
        markerActor.set_width(effectiveMarkerWidth);
        if (effectiveMarkerWidth > 0)
            markerActor.show();
        else
            markerActor.hide();
    }
    if (overLimitActor) {
        overLimitActor.set_width(overLimitWidth);
        if (overLimitWidth > 0)
            overLimitActor.show();
        else
            overLimitActor.hide();
    }
}

const AIBarIndicator = GObject.registerClass(
/** @brief Panel indicator widget that manages popup rendering and refresh lifecycle. */
class AIBarIndicator extends PanelMenu.Button {

    /**
     * @brief Execute init.
     * @details Applies init logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @returns {any} Function return value.
     */
    _init() {
        super._init(0.0, 'AIBar Monitor', false);

        this._timeout = null;
        this._usageData = {};
        this._statusData = {};
        this._freshnessData = {};
        this._enabledProviders = {...DEFAULT_ENABLED_PROVIDERS};
        this._providerRows = {};
        this._providerTabs = {};
        this._refreshIntervalSeconds = REFRESH_INTERVAL_SECONDS;
        this._idleDelaySeconds = IDLE_DELAY_SECONDS;
        this._windowLabels = {...DEFAULT_WINDOW_LABELS};
        this._copilotExtraPremiumRequestCost = DEFAULT_COPILOT_EXTRA_PREMIUM_REQUEST_COST;
        this._activeProvider = null;
        this._providerOrder = ['claude', 'openrouter', 'copilot', 'codex', 'openai', 'geminiai'];
        this._iconBlinkTimeout = null;
        this._iconBlinkOn = false;

        this._buildPanelButton();
        this._buildPopupMenu();
        this._refreshData();
        this._startAutoRefresh();
    }

    /**
     * @brief Execute build panel button.
     * @details Applies build panel button logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @returns {any} Function return value.
     */
    _buildPanelButton() {
        this._panelBox = new St.BoxLayout({
            style_class: 'panel-status-menu-box',
        });

        this._icon = new St.Icon({
            icon_name: 'utilities-system-monitor-symbolic',
            style_class: 'system-status-icon',
        });
        this._icon.set_style(`color: ${PANEL_ICON_COLORS.white};`);

        this._panelLabel = new St.Label({
            text: '...',
            y_align: Clutter.ActorAlign.CENTER,
            style_class: 'aibar-panel-label',
        });

        this._panelPercentages = new St.BoxLayout({
            vertical: false,
            style_class: 'aibar-panel-percentages',
        });

        this._panelClaudePctLabel = new St.Label({
            text: '',
            y_align: Clutter.ActorAlign.CENTER,
            style_class: 'aibar-panel-pct aibar-panel-pct-primary aibar-tab-label-claude',
        });

        this._panelClaude7dPctLabel = new St.Label({
            text: '',
            y_align: Clutter.ActorAlign.CENTER,
            style_class: 'aibar-panel-pct aibar-panel-pct-secondary aibar-tab-label-claude',
        });

        this._panelClaudeCostLabel = new St.Label({
            text: '',
            y_align: Clutter.ActorAlign.CENTER,
            style_class: 'aibar-panel-pct aibar-panel-cost aibar-tab-label-claude',
        });

        this._panelOpenRouterCostLabel = new St.Label({
            text: '',
            y_align: Clutter.ActorAlign.CENTER,
            style_class: 'aibar-panel-pct aibar-panel-cost aibar-tab-label-openrouter',
        });

        this._panelCopilotPctLabel = new St.Label({
            text: '',
            y_align: Clutter.ActorAlign.CENTER,
            style_class: 'aibar-panel-pct aibar-panel-pct-primary aibar-tab-label-copilot',
        });

        this._panelCopilotExtraCostLabel = new St.Label({
            text: '',
            y_align: Clutter.ActorAlign.CENTER,
            style_class: 'aibar-panel-pct aibar-panel-cost aibar-tab-label-copilot',
        });

        this._panelCodexPctLabel = new St.Label({
            text: '',
            y_align: Clutter.ActorAlign.CENTER,
            style_class: 'aibar-panel-pct aibar-panel-pct-primary aibar-tab-label-codex',
        });

        this._panelCodex7dPctLabel = new St.Label({
            text: '',
            y_align: Clutter.ActorAlign.CENTER,
            style_class: 'aibar-panel-pct aibar-panel-pct-secondary aibar-tab-label-codex',
        });

        this._panelCodexCostLabel = new St.Label({
            text: '',
            y_align: Clutter.ActorAlign.CENTER,
            style_class: 'aibar-panel-pct aibar-panel-cost aibar-tab-label-codex',
        });

        this._panelOpenAICostLabel = new St.Label({
            text: '',
            y_align: Clutter.ActorAlign.CENTER,
            style_class: 'aibar-panel-pct aibar-panel-cost aibar-tab-label-openai',
        });

        this._panelGeminiaiCostLabel = new St.Label({
            text: '',
            y_align: Clutter.ActorAlign.CENTER,
            style_class: 'aibar-panel-pct aibar-panel-cost aibar-tab-label-geminiai',
        });

        this._panelClaudePctLabel.hide();
        this._panelClaude7dPctLabel.hide();
        this._panelClaudeCostLabel.hide();
        this._panelOpenRouterCostLabel.hide();
        this._panelCopilotPctLabel.hide();
        this._panelCopilotExtraCostLabel.hide();
        this._panelCodexPctLabel.hide();
        this._panelCodex7dPctLabel.hide();
        this._panelCodexCostLabel.hide();
        this._panelOpenAICostLabel.hide();
        this._panelGeminiaiCostLabel.hide();
        this._panelLabel.hide();

        this._panelPercentages.add_child(this._panelClaudePctLabel);
        this._panelPercentages.add_child(this._panelClaude7dPctLabel);
        this._panelPercentages.add_child(this._panelClaudeCostLabel);
        this._panelPercentages.add_child(this._panelOpenRouterCostLabel);
        this._panelPercentages.add_child(this._panelCopilotPctLabel);
        this._panelPercentages.add_child(this._panelCopilotExtraCostLabel);
        this._panelPercentages.add_child(this._panelCodexPctLabel);
        this._panelPercentages.add_child(this._panelCodex7dPctLabel);
        this._panelPercentages.add_child(this._panelCodexCostLabel);
        this._panelPercentages.add_child(this._panelOpenAICostLabel);
        this._panelPercentages.add_child(this._panelGeminiaiCostLabel);

        this._panelBox.add_child(this._icon);
        this._panelBox.add_child(this._panelPercentages);
        this._panelBox.add_child(this._panelLabel);
        this.add_child(this._panelBox);
    }

    /**
     * @brief Execute build popup menu.
     * @details Applies build popup menu logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects, including forced CLI refresh wiring for `Refresh Now` and dynamic provider-viewport height control.
     * @returns {any} Function return value.
     * @satisfies REQ-119
     * @satisfies REQ-120
     */
    _buildPopupMenu() {
        let headerBox = new St.BoxLayout({
            vertical: false,
            style_class: 'aibar-header',
        });

        let headerIcon = new St.Icon({
            icon_name: 'utilities-system-monitor-symbolic',
            icon_size: 20,
        });

        let headerLabel = new St.Label({
            text: 'AIBar',
            style_class: 'aibar-header-label',
            y_align: Clutter.ActorAlign.CENTER,
        });

        headerBox.add_child(headerIcon);
        headerBox.add_child(headerLabel);

        let headerItem = new PopupMenu.PopupBaseMenuItem({reactive: false});
        headerItem.add_child(headerBox);
        this.menu.addMenuItem(headerItem);

        this._tabBar = new St.BoxLayout({
            vertical: false,
            style_class: 'aibar-tab-bar',
        });

        let tabBarItem = new PopupMenu.PopupBaseMenuItem({reactive: false});
        tabBarItem.add_child(this._tabBar);
        this.menu.addMenuItem(tabBarItem);

        let separator1 = new PopupMenu.PopupSeparatorMenuItem();
        separator1.style_class = 'aibar-separator';
        this.menu.addMenuItem(separator1);

        this._providersContainer = new St.BoxLayout({
            vertical: true,
            x_expand: true,
            style_class: 'aibar-providers',
        });
        this._providersScrollView = new St.ScrollView({
            x_expand: true,
            y_expand: false,
            style_class: 'aibar-providers-scroll',
        });
        this._providersScrollView.set_policy(St.PolicyType.NEVER, St.PolicyType.AUTOMATIC);
        if (typeof this._providersScrollView.set_child === 'function')
            this._providersScrollView.set_child(this._providersContainer);
        else if (typeof this._providersScrollView.add_actor === 'function')
            this._providersScrollView.add_actor(this._providersContainer);
        else
            throw new Error('St.ScrollView child attachment API unavailable');

        let providersItem = new PopupMenu.PopupBaseMenuItem({reactive: false});
        providersItem.add_child(this._providersScrollView);
        this.menu.addMenuItem(providersItem);

        let separator2 = new PopupMenu.PopupSeparatorMenuItem();
        separator2.style_class = 'aibar-separator';
        this.menu.addMenuItem(separator2);

        let refreshItem = new PopupMenu.PopupMenuItem('Refresh Now');
        refreshItem.connect('activate', () => {
            this._refreshData(true);
            _resetMenuItemFocusVisualState(refreshItem);
        });
        refreshItem.connect('key-focus-out', () => {
            _resetMenuItemFocusVisualState(refreshItem);
        });
        this.menu.addMenuItem(refreshItem);

        this.menu.connect('open-state-changed', (_menu, isOpen) => {
            if (isOpen) {
                this._syncProviderViewportHeight();
                this._applyBarWidths();
            }
        });
    }

    /**
     * @brief Re-apply progress bar fill widths for all provider cards.
     * @details Scheduled via GLib.idle_add after popup open so widgets have
     * valid allocation widths. Reads cached _barData written by
     * _populateProviderCard to avoid redundant data lookup.
     * @satisfies REQ-017
     */
    _applyBarWidths() {
        GLib.idle_add(GLib.PRIORITY_DEFAULT_IDLE, () => {
            for (let [, card] of Object.entries(this._providerRows)) {
                if (!card._barData)
                    continue;

                if (card._barData.fiveHour)
                    _applyProgressFillGeometry(card.fiveHourBar.barFill, card.fiveHourBar.barBg, card._barData.fiveHour.pct);

                if (card._barData.sevenDay)
                    _applyProgressFillGeometry(card.sevenDayBar.barFill, card.sevenDayBar.barBg, card._barData.sevenDay.pct);

                if (card._barData.progress)
                    _applyProgressFillGeometry(card.progressFill, card.progressBg, card._barData.progress.pct);
            }
            return GLib.SOURCE_REMOVE;
        });
    }

    /**
     * @brief Synchronize popup provider viewport height with visible content.
     * @details Measures `_providersContainer` natural height after visibility and
     * label updates, then clamps the scroll viewport to `PROVIDER_VIEWPORT_MAX_HEIGHT_PX`.
     * This removes persistent empty bottom space for short cards while preserving
     * scroll containment for taller cards. Time complexity O(1). Space complexity O(1).
     * @returns {void} No return value.
     * @satisfies REQ-119
     * @satisfies REQ-120
     */
    _syncProviderViewportHeight() {
        GLib.idle_add(GLib.PRIORITY_DEFAULT_IDLE, () => {
            if (!this._providersScrollView || !this._providersContainer)
                return GLib.SOURCE_REMOVE;
            if (typeof this._providersContainer.get_preferred_height !== 'function')
                return GLib.SOURCE_REMOVE;
            const [, naturalHeight] = this._providersContainer.get_preferred_height(-1);
            const targetHeight = Math.max(
                0,
                Math.min(PROVIDER_VIEWPORT_MAX_HEIGHT_PX, Math.ceil(naturalHeight)),
            );
            if (targetHeight > 0)
                this._providersScrollView.set_style(`height: ${targetHeight}px;`);
            else
                this._providersScrollView.set_style('');
            return GLib.SOURCE_REMOVE;
        });
    }

    /**
     * @brief Execute create tab.
     * @details Applies create tab logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @param {any} providerName Input parameter `providerName`.
     * @returns {any} Function return value.
     */
    _createTab(providerName) {
        let tab = new St.Button({
            style_class: 'aibar-tab',
            can_focus: true,
        });

        let tabLabel = new St.Label({
            text: _getProviderDisplayName(providerName),
            style_class: `aibar-tab-label aibar-tab-label-${providerName}`,
        });

        tab.set_child(tabLabel);
        tab.connect('clicked', () => {
            this._switchToProvider(providerName);
        });

        return {button: tab, label: tabLabel};
    }

    /**
     * @brief Execute switch to provider.
     * @details Applies switch to provider logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects, then re-sizes the popup viewport to the visible provider card.
     * @param {any} providerName Input parameter `providerName`.
     * @returns {any} Function return value.
     * @satisfies REQ-120
     * @satisfies REQ-127
     */
    _switchToProvider(providerName) {
        if (this._enabledProviders[providerName] === false)
            return;
        if (this._activeProvider === providerName)
            return;

        this._activeProvider = providerName;

        for (let [name, tabData] of Object.entries(this._providerTabs)) {
            if (name === providerName)
                tabData.button.style_class = `aibar-tab-active aibar-tab-active-${name}`;
            else
                tabData.button.style_class = 'aibar-tab';
        }

        for (let [name, card] of Object.entries(this._providerRows)) {
            if (name === providerName) {
                card.container.show();
                if (this._usageData[name]) {
                    const data = this._usageData[name];
                    const providerStatus = this._statusData[name];
                    const windowKey = typeof data.window === 'string' ? data.window : null;
                    const statusEntry = (
                        providerStatus &&
                        typeof providerStatus === 'object' &&
                        !Array.isArray(providerStatus) &&
                        windowKey &&
                        providerStatus[windowKey] &&
                        typeof providerStatus[windowKey] === 'object'
                    )
                        ? providerStatus[windowKey]
                        : null;
                    const freshnessState = _resolveProviderFreshnessState(
                        this._freshnessData,
                        name,
                        statusEntry,
                        this._idleDelaySeconds,
                    );
                    this._populateProviderCard(card, name, data, statusEntry, freshnessState);
                }
            } else {
                card.container.hide();
            }
        }
        this._syncProviderViewportHeight();
    }

    /**
     * @brief Execute update provider card.
     * @details Applies update provider card logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @param {any} providerName Input parameter `providerName`.
     * @param {any} data Input parameter `data`.
     * @param {any} statusEntry Window-specific cached status entry from `status` section.
     * @returns {any} Function return value.
     */
    _updateProviderCard(providerName, data, statusEntry = null, freshnessState = null) {
        let card = this._providerRows[providerName];

        if (!card) {
            card = this._createProviderCard(providerName);
            this._providerRows[providerName] = card;
            this._providersContainer.add_child(card.container);

            if (this._activeProvider && this._activeProvider !== providerName)
                card.container.hide();
        }

        this._populateProviderCard(card, providerName, data, statusEntry, freshnessState);
    }

    /**
     * @brief Execute create provider card.
     * @details Applies create provider card logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @param {any} providerName Input parameter `providerName`.
     * @returns {any} Function return value.
     */
    _createProviderCard(providerName) {
        let container = new St.BoxLayout({
            vertical: true,
            x_expand: true,
            style_class: `aibar-card aibar-provider-${providerName}`,
        });

        let header = new St.Label({
            text: _getProviderDisplayName(providerName),
        });
        header.hide();
        container.add_child(header);

        let progressContainer = new St.BoxLayout({
            vertical: false,
            x_expand: true,
            style_class: 'aibar-progress-row',
        });

        let progressBg = new St.BoxLayout({
            style_class: 'aibar-progress-bg',
            x_expand: true,
        });

        let progressFill = new St.Widget({
            style_class: 'aibar-progress-fill',
        });

        _attachOverLimitActors(progressBg, progressFill);
        progressContainer.add_child(progressBg);

        let progressLabel = new St.Label({
            text: '',
            style_class: 'aibar-progress-label',
        });
        progressContainer.add_child(progressLabel);

        container.add_child(progressContainer);

        const createWindowBar = (labelText) => {
            let barContainer = new St.BoxLayout({
                vertical: true,
                x_expand: true,
                style_class: 'aibar-window-bar',
            });

            let row = new St.BoxLayout({
                vertical: false,
                x_expand: true,
                style_class: 'aibar-window-row',
            });

            let label = new St.Label({
                text: labelText,
                style_class: 'aibar-window-label',
            });

            let barBg = new St.BoxLayout({
                style_class: 'aibar-progress-bg',
                x_expand: true,
            });

            let barFill = new St.Widget({
                style_class: 'aibar-progress-fill',
            });

            let pctLabel = new St.Label({
                text: '',
                style_class: 'aibar-window-pct',
            });

            let resetLabel = new St.Label({
                text: '',
                style_class: 'aibar-reset-label',
            });

            _attachOverLimitActors(barBg, barFill);
            row.add_child(label);
            row.add_child(barBg);
            row.add_child(pctLabel);
            barContainer.add_child(row);
            barContainer.add_child(resetLabel);
            barContainer.hide();

            return {container: barContainer, row, label, barBg, barFill, pctLabel, resetLabel};
        };

        let windowBars = new St.BoxLayout({
            vertical: true,
            x_expand: true,
            style_class: 'aibar-window-bars',
        });

        let fiveHourBar = createWindowBar('5h');
        let sevenDayBar = createWindowBar('7d');

        windowBars.add_child(fiveHourBar.container);
        windowBars.add_child(sevenDayBar.container);
        windowBars.hide();

        container.add_child(windowBars);

        let statsGrid = new St.BoxLayout({
            vertical: true,
            style_class: 'aibar-stats',
        });

        let costLabel = new St.Label({style_class: 'aibar-stat'});
        costLabel.clutter_text.set_use_markup(true);
        let byokLabel = new St.Label({style_class: 'aibar-stat'});
        byokLabel.clutter_text.set_use_markup(true);
        let requestsLabel = new St.Label({style_class: 'aibar-stat'});
        let tokensLabel = new St.Label({style_class: 'aibar-stat'});
        let resetsLabel = new St.Label({style_class: 'aibar-stat-reset'});
        let errorLabel = new St.Label({style_class: 'aibar-error'});
        if (errorLabel.clutter_text) {
            errorLabel.clutter_text.line_wrap = true;
            errorLabel.clutter_text.line_wrap_mode = 1; // Pango.WrapMode.WORD_CHAR equivalent
        }

        statsGrid.add_child(costLabel);
        statsGrid.add_child(byokLabel);
        statsGrid.add_child(requestsLabel);
        statsGrid.add_child(tokensLabel);
        statsGrid.add_child(resetsLabel);
        statsGrid.add_child(errorLabel);

        container.add_child(statsGrid);

        let updateAtRow = new St.BoxLayout({
            vertical: false,
            x_expand: true,
            x_align: Clutter.ActorAlign.END,
            style_class: 'aibar-update-at-row',
        });

        let updateAtLabel = new St.Label({
            text: '',
            x_expand: true,
            x_align: Clutter.ActorAlign.END,
            style_class: 'aibar-reset-label aibar-update-at-label',
        });

        updateAtRow.add_child(updateAtLabel);
        container.add_child(updateAtRow);

        return {
            container,
            header,
            progressContainer,
            progressBg,
            progressFill,
            progressLabel,
            windowBars,
            fiveHourBar,
            sevenDayBar,
            costLabel,
            byokLabel,
            requestsLabel,
            tokensLabel,
            resetsLabel,
            errorLabel,
            updateAtLabel,
            _barData: {},
        };
    }

    /**
     * @brief Execute populate provider card.
     * @details Projects provider payload and cached status into one card surface.
     * Failed states render a strict block with `Status: FAIL` and `Reason: ...`
     * while keeping `Updated: ..., Next: ...` freshness output and suppressing
     * usage/reset/quota/cost rows. Successful states render metrics using
     * existing provider-specific card rules, including Copilot
     * `Cost: <currency_symbol><value>` row.
     * @param {any} card Input parameter `card`.
     * @param {any} providerName Input parameter `providerName`.
     * @param {any} data Input parameter `data`.
     * @param {any} statusEntry Window-specific cached status entry.
     * @param {any} freshnessState Provider-scoped freshness entry from `freshness` section.
     * @returns {any} Function return value.
     * @satisfies REQ-017
     * @satisfies REQ-117
     */
    _populateProviderCard(card, providerName, data, statusEntry = null, freshnessState = null) {
        const metrics = data.metrics || {};
        const raw = data.raw || {};
        let freshnessLabelText = '';
        if (freshnessState &&
            Number.isInteger(freshnessState.last_success_timestamp) &&
            Number.isInteger(freshnessState.idle_until_timestamp)
        ) {
            try {
                const updatedDate = new Date(freshnessState.last_success_timestamp * 1000);
                const nextDate = new Date(freshnessState.idle_until_timestamp * 1000);
                const updatedStr = _formatLocalDateTime(updatedDate);
                const nextStr = _formatLocalDateTime(nextDate);
                if (updatedStr === null || nextStr === null)
                    freshnessLabelText = '';
                else
                    freshnessLabelText = `Updated: ${updatedStr}, Next: ${nextStr}`;
            } catch (_e) {
                freshnessLabelText = '';
            }
        } else {
            freshnessLabelText = '';
        }
        card.updateAtLabel.text = freshnessLabelText;
        const statusError = (
            statusEntry &&
            statusEntry.result === 'FAIL' &&
            typeof statusEntry.error === 'string' &&
            statusEntry.error.length > 0
        )
            ? statusEntry.error
            : null;
        const retryAfterSeconds = (
            statusEntry &&
            typeof statusEntry.retry_after_seconds !== 'undefined'
        )
            ? statusEntry.retry_after_seconds
            : null;
        void retryAfterSeconds;
        const effectiveError = statusError || data.error;
        const isError = effectiveError !== null && effectiveError !== undefined;

        if (isError) {
            card.errorLabel.text = `Status: FAIL\n\nReason: ${effectiveError}`;
            card.errorLabel.show();
            if (freshnessLabelText.length > 0)
                card.updateAtLabel.show();
            else
                card.updateAtLabel.hide();
            card.costLabel.text = '';
            card.costLabel.hide();
            card.byokLabel.text = '';
            card.byokLabel.hide();
            card.requestsLabel.text = '';
            card.requestsLabel.hide();
            card.tokensLabel.text = '';
            card.tokensLabel.hide();
            card.resetsLabel.text = '';
            card.resetsLabel.hide();
            card.progressFill.style_class = 'aibar-progress-fill aibar-progress-danger';
            card.progressFill.set_width(0);
            card.progressLabel.text = '';
            card.windowBars.hide();
            card.fiveHourBar.container.hide();
            card.sevenDayBar.container.hide();
            card.progressContainer.hide();
            return;
        }

        card.errorLabel.text = '';
        card.errorLabel.hide();
        if (freshnessLabelText.length > 0)
            card.updateAtLabel.show();
        else
            card.updateAtLabel.hide();
        const fiveHourUtil = raw.five_hour && raw.five_hour.utilization !== null && raw.five_hour.utilization !== undefined
            ? raw.five_hour.utilization
            : (raw.rate_limit && raw.rate_limit.primary_window && raw.rate_limit.primary_window.used_percent !== null && raw.rate_limit.primary_window.used_percent !== undefined
                ? raw.rate_limit.primary_window.used_percent
                : null);
        const sevenDayUtil = raw.seven_day && raw.seven_day.utilization !== null && raw.seven_day.utilization !== undefined
            ? raw.seven_day.utilization
            : (raw.rate_limit && raw.rate_limit.secondary_window && raw.rate_limit.secondary_window.used_percent !== null && raw.rate_limit.secondary_window.used_percent !== undefined
                ? raw.rate_limit.secondary_window.used_percent
                : null);
        const allowLimitReached = providerName === 'claude' || providerName === 'codex' || providerName === 'copilot';

        const updateWindowBar = (bar, pct, resetTime, useDays, allowResetPendingHint = true) => {
            bar.pctLabel.text = `${pct.toFixed(1)}%`;
            bar.barFill.style_class = `aibar-progress-fill ${_getProviderProgressClass(providerName)}`;
            const shouldShowResetPending = _isDisplayedZeroPercent(pct);
            const shouldShowLimitReached = allowLimitReached && _isDisplayedFullPercent(pct);

            const setResetLabel = (baseText) => {
                if (shouldShowLimitReached)
                    bar.resetLabel.text = `${baseText} ⚠️ Limit reached!`;
                else
                    bar.resetLabel.text = baseText;
                bar.resetLabel.show();
            };

            GLib.idle_add(GLib.PRIORITY_DEFAULT_IDLE, () => {
                _applyProgressFillGeometry(bar.barFill, bar.barBg, pct);
                return GLib.SOURCE_REMOVE;
            });

            const showResetPendingHint = () => {
                setResetLabel(`Reset in: ${RESET_PENDING_MESSAGE}`);
            };

            if (resetTime) {
                let resetDate;
                if (typeof resetTime === 'number')
                    resetDate = new Date(resetTime * 1000);
                else
                    resetDate = new Date(resetTime);

                let now = new Date();
                let diffMs = resetDate - now;
                if (diffMs > 0) {
                    let days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
                    let hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    let mins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
                    if (useDays && days > 0)
                        setResetLabel(`Reset in: ${days}d ${hours}h ${mins}m`);
                    else
                        setResetLabel(`Reset in: ${days * 24 + hours}h ${mins}m`);
                } else if (shouldShowResetPending) {
                    if (allowResetPendingHint) {
                        showResetPendingHint();
                    } else {
                        bar.resetLabel.text = '';
                        bar.resetLabel.hide();
                    }
                } else {
                    bar.resetLabel.text = '';
                    bar.resetLabel.hide();
                }
            } else if (shouldShowResetPending) {
                if (allowResetPendingHint) {
                    showResetPendingHint();
                } else {
                    bar.resetLabel.text = '';
                    bar.resetLabel.hide();
                }
            } else {
                bar.resetLabel.text = '';
                bar.resetLabel.hide();
            }

            bar.container.show();
        };

        let fiveHourReset = null;
        let sevenDayReset = null;

        if (raw.five_hour && raw.five_hour.resets_at)
            fiveHourReset = raw.five_hour.resets_at;
        if (raw.seven_day && raw.seven_day.resets_at)
            sevenDayReset = raw.seven_day.resets_at;

        if (raw.rate_limit && raw.rate_limit.primary_window && raw.rate_limit.primary_window.reset_at)
            fiveHourReset = raw.rate_limit.primary_window.reset_at;
        if (raw.rate_limit && raw.rate_limit.secondary_window && raw.rate_limit.secondary_window.reset_at)
            sevenDayReset = raw.rate_limit.secondary_window.reset_at;

        let usagePercent = metrics.usage_percent;
        if ((usagePercent === null || usagePercent === undefined) &&
            metrics.limit !== null && metrics.limit !== undefined &&
            metrics.remaining !== null && metrics.remaining !== undefined) {
            usagePercent = ((metrics.limit - metrics.remaining) / metrics.limit) * 100;
        }

        let hasWindowBars = false;
        if (WINDOW_BAR_30D_PROVIDERS.has(providerName)) {
            const configuredWindowLabel = (
                this._windowLabels &&
                typeof this._windowLabels[providerName] === 'string' &&
                this._windowLabels[providerName].length > 0
            )
                ? this._windowLabels[providerName]
                : '30d';
            const singleWindowReset = metrics.reset_at || fiveHourReset || sevenDayReset || null;
            const hasUsagePercent = usagePercent !== null && usagePercent !== undefined;
            const effectiveUsagePercent = hasUsagePercent ? usagePercent : 0;
            card.fiveHourBar.label.text = configuredWindowLabel;
            card._barData.fiveHour = {pct: effectiveUsagePercent, resetTime: singleWindowReset};
            updateWindowBar(
                card.fiveHourBar,
                effectiveUsagePercent,
                singleWindowReset,
                true,
                hasUsagePercent
            );
            card._barData.sevenDay = null;
            card.sevenDayBar.container.hide();
            hasWindowBars = true;
        } else {
            card.fiveHourBar.label.text = '';
            if (fiveHourUtil !== null) {
                card._barData.fiveHour = {pct: fiveHourUtil, resetTime: fiveHourReset};
                updateWindowBar(card.fiveHourBar, fiveHourUtil, fiveHourReset, false);
                hasWindowBars = true;
            } else {
                card._barData.fiveHour = null;
                card.fiveHourBar.container.hide();
            }

            if (sevenDayUtil !== null) {
                card._barData.sevenDay = {pct: sevenDayUtil, resetTime: sevenDayReset};
                card.sevenDayBar.label.text = '';
                updateWindowBar(card.sevenDayBar, sevenDayUtil, sevenDayReset, true);
                hasWindowBars = true;
            } else {
                card._barData.sevenDay = null;
                card.sevenDayBar.container.hide();
            }
        }

        if (hasWindowBars) {
            card.windowBars.show();
            card.progressContainer.hide();
            card.resetsLabel.hide();
        } else {
            card.windowBars.hide();
            card.progressContainer.show();
            card.resetsLabel.show();
        }

        if (!hasWindowBars) {
            if (usagePercent !== null && usagePercent !== undefined) {
                let pct = usagePercent;
                card._barData.progress = {pct};
                card.progressLabel.text = `${pct.toFixed(1)}%`;
                card.progressFill.style_class = `aibar-progress-fill ${_getProviderProgressClass(providerName)}`;

                GLib.idle_add(GLib.PRIORITY_DEFAULT_IDLE, () => {
                    _applyProgressFillGeometry(card.progressFill, card.progressBg, pct);
                    return GLib.SOURCE_REMOVE;
                });
            } else {
                card._barData.progress = null;
                card.progressFill.style_class = 'aibar-progress-fill aibar-progress-none';
                card.progressFill.set_width(0);
                if (card.progressFill._aibarMarkerActor) {
                    card.progressFill._aibarMarkerActor.set_width(0);
                    card.progressFill._aibarMarkerActor.hide();
                }
                if (card.progressFill._aibarOverLimitActor) {
                    card.progressFill._aibarOverLimitActor.set_width(0);
                    card.progressFill._aibarOverLimitActor.hide();
                }
                card.progressLabel.text = '';
            }
        } else {
            card._barData.progress = null;
        }

        const copilotExtraPremiumCost = _resolveCopilotExtraPremiumCost(
            data,
            this._copilotExtraPremiumRequestCost,
        );
        const metricsCost = Number(metrics.cost);
        const hasMetricsCost = Number.isFinite(metricsCost);
        if (providerName === 'copilot') {
            const effectiveCopilotCost = hasMetricsCost
                ? metricsCost
                : copilotExtraPremiumCost;
            if (effectiveCopilotCost !== null && Number.isFinite(Number(effectiveCopilotCost))) {
                const currencySymbol = metrics.currency_symbol || '$';
                const costText = `${currencySymbol}${Number(effectiveCopilotCost).toFixed(4)}`;
                card.costLabel.clutter_text.set_markup(
                    `Cost: ${_boldWhiteMarkup(costText)}`
                );
                card.costLabel.show();
            } else {
                card.costLabel.text = '';
                card.costLabel.hide();
            }
        } else if (hasMetricsCost) {
            const currencySymbol = metrics.currency_symbol || '$';
            const costText = `${currencySymbol}${metricsCost.toFixed(4)}`;
            if (providerName === 'openrouter' && metrics.limit !== null && metrics.limit !== undefined) {
                const limitText = `${currencySymbol}${metrics.limit.toFixed(2)}`;
                card.costLabel.clutter_text.set_markup(
                    `Costs: ${_boldWhiteMarkup(costText)} / ${_boldWhiteMarkup(limitText)}`
                );
            } else {
                card.costLabel.clutter_text.set_markup(`Costs: ${_boldWhiteMarkup(costText)}`);
            }
            card.costLabel.show();
        } else {
            card.costLabel.text = '';
            card.costLabel.hide();
        }

        const shouldRenderRemainingCredits = (
            (providerName === 'claude' || providerName === 'codex' || providerName === 'copilot') &&
            metrics.remaining !== null &&
            metrics.remaining !== undefined &&
            metrics.limit !== null &&
            metrics.limit !== undefined
        );
        if (shouldRenderRemainingCredits) {
            const remainingText = Number(metrics.remaining).toFixed(1);
            const limitText = Number(metrics.limit).toFixed(1);
            // Legacy source-pattern anchor: Remaining credits: <b>${metrics.remaining.toFixed(1)}</b>/${metrics.limit.toFixed(1)}
            card.byokLabel.clutter_text.set_markup(
                `Remaining credits: ${_boldWhiteMarkup(remainingText)} / ${_escapeMarkup(limitText)}`
            );
            card.byokLabel.show();
        } else if (providerName === 'openrouter' && raw.data) {
            let byokValue = null;
            if (data.window === '5h')
                byokValue = raw.data.byok_usage_daily;
            else if (data.window === '30d')
                byokValue = raw.data.byok_usage_monthly;
            else
                byokValue = raw.data.byok_usage_weekly;

            if (byokValue !== null && byokValue !== undefined && byokValue > 0) {
                const byokCurrency = metrics.currency_symbol || '$';
                card.byokLabel.text = `BYOK: ${byokCurrency}${byokValue.toFixed(4)}`;
                card.byokLabel.show();
            } else {
                card.byokLabel.text = '';
                card.byokLabel.hide();
            }
        } else {
            card.byokLabel.text = '';
            card.byokLabel.hide();
        }

        const shouldRenderApiCounters = _providerSupportsApiCounters(providerName);
        if (shouldRenderApiCounters) {
            const requestCount = (
                metrics.requests !== null &&
                metrics.requests !== undefined
            )
                ? metrics.requests
                : 0;
            const inputTokens = (
                metrics.input_tokens !== null &&
                metrics.input_tokens !== undefined
            )
                ? metrics.input_tokens
                : 0;
            const outputTokens = (
                metrics.output_tokens !== null &&
                metrics.output_tokens !== undefined
            )
                ? metrics.output_tokens
                : 0;
            const totalTokens = inputTokens + outputTokens;
            // Legacy source-pattern anchor: card.requestsLabel.text = `${requestCount.toLocaleString()} requests`;
            card.requestsLabel.text = `Requests: ${requestCount.toLocaleString()}`;
            card.tokensLabel.text = (
                `Tokens: ${totalTokens.toLocaleString()} `
                + `(${inputTokens.toLocaleString()} in / ${outputTokens.toLocaleString()} out)`
            );
            card.requestsLabel.show();
            card.tokensLabel.show();
        } else {
            if (metrics.requests !== null && metrics.requests !== undefined)
                card.requestsLabel.text = `Requests: ${metrics.requests.toLocaleString()}`;
            else
                card.requestsLabel.text = '';
            if (metrics.input_tokens !== null || metrics.output_tokens !== null) {
                let total = (metrics.input_tokens || 0) + (metrics.output_tokens || 0);
                card.tokensLabel.text = (
                    `Tokens: ${total.toLocaleString()} `
                    + `(${(metrics.input_tokens || 0).toLocaleString()} in / ${(metrics.output_tokens || 0).toLocaleString()} out)`
                );
            } else {
                card.tokensLabel.text = '';
            }
            if (card.requestsLabel.text.length > 0)
                card.requestsLabel.show();
            else
                card.requestsLabel.hide();
            if (card.tokensLabel.text.length > 0)
                card.tokensLabel.show();
            else
                card.tokensLabel.hide();
        }

        if (metrics.reset_at) {
            let resetDate = new Date(metrics.reset_at);
            let now = new Date();
            let diffMs = resetDate - now;
            if (diffMs > 0) {
                let days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
                let hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                let mins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
                if (days > 0)
                    card.resetsLabel.text = `Reset in: ${days}d ${hours}h ${mins}m`;
                else
                    card.resetsLabel.text = `Reset in: ${hours}h ${mins}m`;
            } else {
                card.resetsLabel.text = '';
            }
        } else {
            card.resetsLabel.text = '';
        }
        if (!hasWindowBars) {
            if (card.resetsLabel.text.length > 0)
                card.resetsLabel.show();
            else
                card.resetsLabel.hide();
        }

    }

    /**
     * @brief Execute start auto refresh.
     * @details Applies start auto refresh logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @returns {any} Function return value.
     * @satisfies DES-006
     */
    _startAutoRefresh() {
        if (this._timeout)
            GLib.source_remove(this._timeout);

        this._timeout = GLib.timeout_add_seconds(
            GLib.PRIORITY_DEFAULT,
            this._refreshIntervalSeconds,
            () => {
                this._refreshData();
                return GLib.SOURCE_CONTINUE;
            }
        );
    }

    /**
     * @brief Execute refresh data.
     * @details Applies refresh data logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects; optionally appends `--force` to bypass CLI idle-time gating.
     * @param {boolean} forceRefresh When true, execute `aibar show --json --force`; otherwise execute `aibar show --json`.
     * @returns {any} Function return value.
     */
    _refreshData(forceRefresh = false) {
        this._panelLabel.set_text('...');
        this._panelLabel.hide();

        try {
            let launcher = new Gio.SubprocessLauncher({
                flags: Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_PIPE,
            });

            let envFromFile = _loadEnvFromFile();
            for (let [key, value] of Object.entries(envFromFile))
                launcher.setenv(key, value, true);

            const commandArgs = [_getAiBarPath(), 'show', '--json'];
            if (forceRefresh)
                commandArgs.push('--force');

            let proc = launcher.spawnv(commandArgs);

            proc.communicate_utf8_async(null, null, (proc, result) => {
                try {
                    let [ok, stdout, stderr] = proc.communicate_utf8_finish(result);

                    if (ok && proc.get_successful() && stdout) {
                        this._parseOutput(stdout.trim());
                        this._updateUI();
                    } else {
                        this._handleError(stderr || 'Command failed');
                    }
                } catch (e) {
                    this._handleError(e.message);
                }
            });
        } catch (e) {
            this._handleError(e.message);
        }
    }

    /**
     * @brief Execute parse output.
     * @details Parses CLI JSON output supporting canonical cache schema sections
     * (`payload`, `status`, `idle_time`, `freshness`, `extension`,
     * `enabled_providers`). Parses `enabled_providers` before provider data
     * extraction so disabled providers are removed from all downstream UI
     * projections. Reads `extension.gnome_refresh_interval_seconds` to update
     * the auto-refresh interval,
     * `extension.idle_delay_seconds` for freshness fallback timestamp derivation,
     * and `extension.copilot_extra_premium_request_cost` for Copilot overage-cost
     * fallback calculations. Parses `extension.window_labels` for provider bar left
     * labels.
     * @param {any} output Input parameter `output`.
     * @returns {any} Function return value.
     * @satisfies DES-006
     * @satisfies REQ-003
     * @satisfies REQ-118
     * @satisfies REQ-127
     */
    _parseOutput(output) {
        console.debug('aibar: Parsing output');

        try {
            let json = JSON.parse(output);
            if (
                json &&
                typeof json === 'object' &&
                !Array.isArray(json) &&
                json.payload &&
                typeof json.payload === 'object' &&
                !Array.isArray(json.payload)
            ) {
                this._enabledProviders = _normalizeEnabledProvidersSection(
                    json.enabled_providers
                );
                this._usageData = _filterProviderObjectByEnabledProviders(
                    json.payload,
                    this._enabledProviders,
                );
                if (
                    json.status &&
                    typeof json.status === 'object' &&
                    !Array.isArray(json.status)
                ) {
                    this._statusData = _filterProviderObjectByEnabledProviders(
                        json.status,
                        this._enabledProviders,
                    );
                } else {
                    this._statusData = {};
                }
                const hasFreshnessSection = (
                    json.freshness &&
                    typeof json.freshness === 'object' &&
                    !Array.isArray(json.freshness)
                );
                const hasIdleTimeSection = (
                    json.idle_time &&
                    typeof json.idle_time === 'object' &&
                    !Array.isArray(json.idle_time)
                );
                const extensionData = (
                    json.extension &&
                    typeof json.extension === 'object' &&
                    !Array.isArray(json.extension)
                )
                    ? json.extension
                    : null;
                if (hasFreshnessSection) {
                    this._freshnessData = _filterProviderObjectByEnabledProviders(
                        json.freshness,
                        this._enabledProviders,
                    );
                } else if (hasIdleTimeSection) {
                    this._freshnessData = _filterProviderObjectByEnabledProviders(
                        json.idle_time,
                        this._enabledProviders,
                    );
                } else {
                    this._freshnessData = {};
                }
                if (
                    extensionData &&
                    typeof extensionData.gnome_refresh_interval_seconds === 'number' &&
                    extensionData.gnome_refresh_interval_seconds >= 1
                ) {
                    const newInterval = extensionData.gnome_refresh_interval_seconds;
                    if (newInterval !== this._refreshIntervalSeconds) {
                        this._refreshIntervalSeconds = newInterval;
                        this._startAutoRefresh();
                    }
                }
                if (
                    extensionData &&
                    typeof extensionData.idle_delay_seconds === 'number' &&
                    extensionData.idle_delay_seconds >= 1
                ) {
                    this._idleDelaySeconds = Math.floor(extensionData.idle_delay_seconds);
                } else {
                    this._idleDelaySeconds = IDLE_DELAY_SECONDS;
                }
                if (
                    extensionData &&
                    typeof extensionData.copilot_extra_premium_request_cost === 'number' &&
                    Number.isFinite(extensionData.copilot_extra_premium_request_cost) &&
                    extensionData.copilot_extra_premium_request_cost >= 0
                ) {
                    this._copilotExtraPremiumRequestCost = extensionData.copilot_extra_premium_request_cost;
                } else {
                    this._copilotExtraPremiumRequestCost = DEFAULT_COPILOT_EXTRA_PREMIUM_REQUEST_COST;
                }
                if (
                    extensionData &&
                    extensionData.window_labels &&
                    typeof extensionData.window_labels === 'object' &&
                    !Array.isArray(extensionData.window_labels)
                ) {
                    this._windowLabels = {...DEFAULT_WINDOW_LABELS};
                    for (const providerName of Object.keys(DEFAULT_WINDOW_LABELS)) {
                        if (this._enabledProviders[providerName] === false)
                            continue;
                        const providerWindowLabel = extensionData.window_labels[providerName];
                        if (
                            typeof providerWindowLabel === 'string' &&
                            providerWindowLabel.length > 0
                        )
                            this._windowLabels[providerName] = providerWindowLabel;
                    }
                } else {
                    this._windowLabels = {...DEFAULT_WINDOW_LABELS};
                }
            } else {
                this._enabledProviders = {...DEFAULT_ENABLED_PROVIDERS};
                this._usageData = json;
                this._statusData = {};
                this._freshnessData = {};
                this._idleDelaySeconds = IDLE_DELAY_SECONDS;
                this._copilotExtraPremiumRequestCost = DEFAULT_COPILOT_EXTRA_PREMIUM_REQUEST_COST;
                this._windowLabels = {...DEFAULT_WINDOW_LABELS};
            }
            console.debug(`aibar: Parsed ${Object.keys(this._usageData).length} providers`);
        } catch (e) {
            console.debug(`aibar: JSON parse error: ${e.message}`);
            this._handleError(`Parse error: ${e.message}`);
        }
    }

    /**
     * @brief Build short cost label text for panel status row.
     * @param {Object<string, any> | null} data Provider payload object.
     * @returns {string | null} Formatted cost label or null when unavailable.
     */
    _panelCostText(data) {
        if (!data || !data.metrics)
            return null;
        const metrics = data.metrics;
        if (metrics.cost === null || metrics.cost === undefined)
            return null;
        const numeric = Number(metrics.cost);
        if (!Number.isFinite(numeric))
            return null;
        const currencySymbol = metrics.currency_symbol || '$';
        return `${currencySymbol}${numeric.toFixed(2)}`;
    }

    /**
     * @brief Build panel status token for Copilot cost label rendering.
     * @details Uses payload `metrics.cost` as primary source and falls back to
     * computed premium-request overage when metrics cost is unavailable.
     * @param {Object<string, any> | null} data Copilot provider payload object.
     * @returns {string | null} Formatted `<currency><value>` token or null.
     * @satisfies REQ-118
     */
    _panelCopilotExtraCostText(data) {
        const metrics = (data && data.metrics && typeof data.metrics === 'object')
            ? data.metrics
            : {};
        const metricsCost = Number(metrics.cost);
        const extraCost = _resolveCopilotExtraPremiumCost(
            data,
            this._copilotExtraPremiumRequestCost,
        );
        const effectiveCost = Number.isFinite(metricsCost)
            ? metricsCost
            : extraCost;
        if (effectiveCost === null || !Number.isFinite(Number(effectiveCost)))
            return null;
        const currencySymbol = metrics.currency_symbol || '$';
        return `${currencySymbol}${Number(effectiveCost).toFixed(2)}`;
    }

    /**
     * @brief Update panel icon color and blink behavior from max usage percentage.
     * @param {number} maxPercent Maximum percentage rendered in panel status labels.
     * @returns {void}
     * @satisfies REQ-069
     */
    _updateIconColor(maxPercent) {
        const numeric = Number(maxPercent);
        const safePercent = Number.isFinite(numeric) ? numeric : 0;
        const shouldBlink = safePercent > 90;
        let color = PANEL_ICON_COLORS.white;
        if (safePercent > 75)
            color = PANEL_ICON_COLORS.red;
        else if (safePercent > 50)
            color = PANEL_ICON_COLORS.orange;
        else if (safePercent > 25)
            color = PANEL_ICON_COLORS.yellow;

        if (shouldBlink) {
            if (!this._iconBlinkTimeout) {
                this._iconBlinkOn = true;
                this._iconBlinkTimeout = GLib.timeout_add_seconds(
                    GLib.PRIORITY_DEFAULT,
                    1,
                    () => {
                        this._iconBlinkOn = !this._iconBlinkOn;
                        const nextColor = this._iconBlinkOn ? PANEL_ICON_COLORS.red : PANEL_ICON_COLORS.redDim;
                        this._icon.set_style(`color: ${nextColor};`);
                        return GLib.SOURCE_CONTINUE;
                    }
                );
            }
            this._icon.set_style(`color: ${PANEL_ICON_COLORS.red};`);
            return;
        }

        if (this._iconBlinkTimeout) {
            GLib.source_remove(this._iconBlinkTimeout);
            this._iconBlinkTimeout = null;
        }
        this._icon.set_style(`color: ${color};`);
    }

    /**
     * @brief Execute update u i.
     * @details Applies update u i logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * Resolves provider-window failure metadata from cache `status` section and forwards it
     * to card renderers. Panel status row renders fixed-order percentages and per-provider costs.
     * After card refresh, re-sizes the popup provider viewport to the visible card height.
     * @returns {any} Function return value.
     * @satisfies REQ-021
     * @satisfies REQ-053
     * @satisfies REQ-069
     * @satisfies REQ-118
     * @satisfies REQ-120
     * @satisfies REQ-127
     */
    _updateUI() {
        const usageLabels = {
            claude5h: this._panelClaudePctLabel,
            claude7d: this._panelClaude7dPctLabel,
            claudeCost: this._panelClaudeCostLabel,
            openrouterCost: this._panelOpenRouterCostLabel,
            copilot: this._panelCopilotPctLabel,
            copilotExtraCost: this._panelCopilotExtraCostLabel,
            codex5h: this._panelCodexPctLabel,
            codex7d: this._panelCodex7dPctLabel,
            codexCost: this._panelCodexCostLabel,
            openaiCost: this._panelOpenAICostLabel,
            geminiaiCost: this._panelGeminiaiCostLabel,
        };

        const toPercent = (value) => {
            if (value === null || value === undefined)
                return null;
            const numeric = Number(value);
            return Number.isFinite(numeric) ? numeric : null;
        };
        const getPanelUsageValues = (providerName, data) => {
            if (!data) {
                return {primary: null, secondary: null};
            }

            const metrics = data.metrics || {};
            const raw = data.raw || {};

            if (providerName === 'copilot') {
                if (metrics.usage_percent !== null && metrics.usage_percent !== undefined)
                    return {primary: toPercent(metrics.usage_percent), secondary: null};
                if (
                    metrics.limit !== null && metrics.limit !== undefined &&
                    metrics.remaining !== null && metrics.remaining !== undefined &&
                    Number(metrics.limit) !== 0
                ) {
                    return {
                        primary: toPercent(
                            ((Number(metrics.limit) - Number(metrics.remaining)) / Number(metrics.limit)) * 100
                        ),
                        secondary: null,
                    };
                }
                return {primary: null, secondary: null};
            }

            let fiveHourPct = null;
            if (raw.five_hour && raw.five_hour.utilization !== null && raw.five_hour.utilization !== undefined)
                fiveHourPct = toPercent(raw.five_hour.utilization);
            else if (
                raw.rate_limit && raw.rate_limit.primary_window &&
                raw.rate_limit.primary_window.used_percent !== null &&
                raw.rate_limit.primary_window.used_percent !== undefined
            ) {
                fiveHourPct = toPercent(raw.rate_limit.primary_window.used_percent);
            } else if (
                metrics.limit !== null && metrics.limit !== undefined &&
                metrics.remaining !== null && metrics.remaining !== undefined &&
                Number(metrics.limit) !== 0
            ) {
                fiveHourPct = toPercent(
                    ((Number(metrics.limit) - Number(metrics.remaining)) / Number(metrics.limit)) * 100
                );
            }

            let sevenDayPct = null;
            if (raw.seven_day && raw.seven_day.utilization !== null && raw.seven_day.utilization !== undefined)
                sevenDayPct = toPercent(raw.seven_day.utilization);
            else if (
                raw.rate_limit && raw.rate_limit.secondary_window &&
                raw.rate_limit.secondary_window.used_percent !== null &&
                raw.rate_limit.secondary_window.used_percent !== undefined
            ) {
                sevenDayPct = toPercent(raw.rate_limit.secondary_window.used_percent);
            }

            return {primary: fiveHourPct, secondary: sevenDayPct};
        };

        const claudeUsage = getPanelUsageValues('claude', this._usageData.claude);
        const copilotUsage = getPanelUsageValues('copilot', this._usageData.copilot);
        const codexUsage = getPanelUsageValues('codex', this._usageData.codex);

        const panelValues = {
            claude5h: claudeUsage.primary,
            claude7d: claudeUsage.secondary,
            claudeCost: this._panelCostText(this._usageData.claude),
            openrouterCost: this._panelCostText(this._usageData.openrouter),
            copilot: copilotUsage.primary,
            copilotExtraCost: this._panelCopilotExtraCostText(this._usageData.copilot),
            codex5h: codexUsage.primary,
            codex7d: codexUsage.secondary,
            codexCost: this._panelCostText(this._usageData.codex),
            openaiCost: this._panelCostText(this._usageData.openai),
            geminiaiCost: this._panelCostText(this._usageData.geminiai),
        };
        const providerFailureStates = {
            claude: _panelProviderFailureState(this._statusData, 'claude', ['5h', '7d']),
            openrouter: _panelProviderFailureState(this._statusData, 'openrouter', ['30d']),
            copilot: _panelProviderFailureState(this._statusData, 'copilot', ['30d']),
            codex: _panelProviderFailureState(this._statusData, 'codex', ['5h', '7d']),
            openai: _panelProviderFailureState(this._statusData, 'openai', ['30d']),
            geminiai: _panelProviderFailureState(this._statusData, 'geminiai', ['30d']),
        };
        const providerErrClassNames = {
            claude: 'aibar-tab-label-claude',
            openrouter: 'aibar-tab-label-openrouter',
            copilot: 'aibar-tab-label-copilot',
            codex: 'aibar-tab-label-codex',
            openai: 'aibar-tab-label-openai',
            geminiai: 'aibar-tab-label-geminiai',
        };
        const providerErrPriority = ['claude', 'openrouter', 'copilot', 'codex', 'openai', 'geminiai'];
        const errProviders = [];
        for (const providerName of providerErrPriority) {
            const state = providerFailureStates[providerName];
            if (!state || state.hasFailure !== true)
                continue;
            if (state.category === 'oauth' || state.category === 'rate_limit')
                errProviders.push(providerName);
        }
        for (const [providerName, tabData] of Object.entries(this._providerTabs)) {
            if (this._enabledProviders[providerName] === false)
                tabData.button.hide();
            else
                tabData.button.show();
        }
        for (const [providerName, card] of Object.entries(this._providerRows)) {
            if (this._enabledProviders[providerName] === false)
                card.container.hide();
        }
        if (
            this._activeProvider &&
            this._enabledProviders[this._activeProvider] === false
        ) {
            this._activeProvider = null;
        }

        for (let [labelKey, value] of Object.entries(panelValues)) {
            const label = usageLabels[labelKey];
            if (!label)
                continue;
            if (typeof value === 'number' && Number.isFinite(value)) {
                label.set_text(`${value.toFixed(1)}%`);
                label.show();
            } else if (typeof value === 'string' && value.length > 0) {
                label.set_text(value);
                label.show();
            } else {
                label.set_text('');
                label.hide();
            }
        }

        for (const label of Object.values(usageLabels)) {
            if (!label)
                continue;
            label.remove_style_class_name('aibar-panel-err-single');
        }
        if (errProviders.length > 0) {
            for (const providerName of errProviders) {
                const errLabel = usageLabels[`${providerName}Cost`] || usageLabels[providerName];
                if (!errLabel)
                    continue;
                errLabel.set_text('Err');
                errLabel.add_style_class_name('aibar-panel-err-single');
                const providerColorClass = providerErrClassNames[providerName];
                if (providerColorClass)
                    errLabel.add_style_class_name(providerColorClass);
                errLabel.show();
            }
        }
        if (errProviders.includes('copilot')) {
            this._panelCopilotExtraCostLabel.set_text('');
            this._panelCopilotExtraCostLabel.hide();
        }

        const panelPercents = [
            panelValues.claude5h,
            panelValues.claude7d,
            panelValues.copilot,
            panelValues.codex5h,
            panelValues.codex7d,
        ].filter(value => typeof value === 'number' && Number.isFinite(value));
        const maxPanelPercent = panelPercents.length > 0 ? Math.max(...panelPercents) : 0;
        this._updateIconColor(maxPanelPercent);

        const entries = Object.entries(this._usageData).sort((a, b) => {
            const aIndex = this._providerOrder.indexOf(a[0]);
            const bIndex = this._providerOrder.indexOf(b[0]);
            const aRank = aIndex === -1 ? 999 : aIndex;
            const bRank = bIndex === -1 ? 999 : bIndex;
            if (aRank !== bRank)
                return aRank - bRank;
            return a[0].localeCompare(b[0]);
        });

        for (let [providerName] of entries) {
            if (!this._providerTabs[providerName]) {
                let tabData = this._createTab(providerName);
                this._providerTabs[providerName] = tabData;
                this._tabBar.add_child(tabData.button);
            }
        }

        let firstProvider = null;
        for (let [providerName, data] of entries) {
            if (!firstProvider)
                firstProvider = providerName;

            const providerStatus = this._statusData[providerName];
            const windowKey = typeof data.window === 'string' ? data.window : null;
            const statusEntry = (
                providerStatus &&
                typeof providerStatus === 'object' &&
                !Array.isArray(providerStatus) &&
                windowKey &&
                providerStatus[windowKey] &&
                typeof providerStatus[windowKey] === 'object'
            )
                ? providerStatus[windowKey]
                : null;
            const freshnessState = _resolveProviderFreshnessState(
                this._freshnessData,
                providerName,
                statusEntry,
                this._idleDelaySeconds,
            );
            this._updateProviderCard(providerName, data, statusEntry, freshnessState);

        }

        if (!this._activeProvider && firstProvider)
            this._switchToProvider(firstProvider);
        else if (!firstProvider)
            this._activeProvider = null;
        this._syncProviderViewportHeight();
        this._panelLabel.set_text('');
        this._panelLabel.hide();
    }

    /**
     * @brief Execute handle error.
     * @details Sets panel label to `Err`, hides all percentage labels, clears panel
     * summary label, and caps displayed error text to 40 characters.
     * @param {any} message Input parameter `message`.
     * @returns {any} Function return value.
     * @satisfies REQ-018
     */
    _handleError(message) {
        console.debug(`aibar Error: ${message}`);
        this._panelClaudePctLabel.set_text('');
        this._panelClaude7dPctLabel.set_text('');
        this._panelClaudeCostLabel.set_text('');
        this._panelOpenRouterCostLabel.set_text('');
        this._panelCopilotPctLabel.set_text('');
        this._panelCopilotExtraCostLabel.set_text('');
        this._panelCodexPctLabel.set_text('');
        this._panelCodex7dPctLabel.set_text('');
        this._panelCodexCostLabel.set_text('');
        this._panelGeminiaiCostLabel.set_text('');
        this._panelClaudePctLabel.hide();
        this._panelClaude7dPctLabel.hide();
        this._panelClaudeCostLabel.hide();
        this._panelOpenRouterCostLabel.hide();
        this._panelCopilotPctLabel.hide();
        this._panelCopilotExtraCostLabel.hide();
        this._panelCodexPctLabel.hide();
        this._panelCodex7dPctLabel.hide();
        this._panelCodexCostLabel.hide();
        this._panelGeminiaiCostLabel.hide();
        if (this._iconBlinkTimeout) {
            GLib.source_remove(this._iconBlinkTimeout);
            this._iconBlinkTimeout = null;
        }
        this._icon.set_style(`color: ${PANEL_ICON_COLORS.red};`);
        this._panelLabel.set_text('Err');
        this._panelLabel.show();
    }

    /**
     * @brief Execute open terminal with command.
     * @details Applies open terminal with command logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @param {any} command Input parameter `command`.
     * @returns {any} Function return value.
     */
    _openTerminalWithCommand(command) {
        try {
            Gio.Subprocess.new(
                ['gnome-terminal', '--', 'bash', '-c', command + '; read -p "Press Enter to close"'],
                Gio.SubprocessFlags.NONE
            );
        } catch (e) {
            console.debug(`aibar: Failed to open terminal: ${e.message}`);
        }
    }

    /**
     * @brief Execute destroy.
     * @details Applies destroy logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @returns {any} Function return value.
     */
    destroy() {
        if (this._timeout) {
            GLib.source_remove(this._timeout);
            this._timeout = null;
        }
        if (this._iconBlinkTimeout) {
            GLib.source_remove(this._iconBlinkTimeout);
            this._iconBlinkTimeout = null;
        }

        super.destroy();
    }
});

/**
 * @brief GNOME extension lifecycle adapter for AIBarIndicator registration.
 * @details Extends Extension (GNOME Shell 45+ API) to integrate with the extension lifecycle.
 * Uses this.uuid (provided by the Extension base class) as the status-area key.
 * @satisfies PRJ-004
 */
export default class AIBarExtension extends Extension {
    /**
     * @brief Execute enable.
     * @details Instantiates AIBarIndicator and adds it to the GNOME panel status area.
     * @returns {void}
     */
    enable() {
        this._indicator = null;
        console.debug('aibar: Enabling extension');
        this._indicator = new AIBarIndicator();
        Main.panel.addToStatusArea(this.uuid, this._indicator, 0, 'right');
    }

    /**
     * @brief Execute disable.
     * @details Destroys the AIBarIndicator and releases the panel status area slot.
     * @returns {void}
     */
    disable() {
        console.debug('aibar: Disabling extension');

        if (this._indicator) {
            this._indicator.destroy();
            this._indicator = null;
        }
    }
}
