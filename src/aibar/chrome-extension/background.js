/**
 * @file background.js
 * @brief Chrome extension service-worker runtime for autonomous provider refresh.
 * @details Executes ordered provider page downloads, parser normalization, state
 * persistence, and debug instrumentation on a recurring alarm interval.
 * @satisfies PRJ-009
 * @satisfies PRJ-010
 * @satisfies CTN-008
 * @satisfies CTN-009
 * @satisfies CTN-012
 * @satisfies CTN-013
 * @satisfies CTN-014
 * @satisfies CTN-017
 * @satisfies CTN-016
 * @satisfies REQ-043
 * @satisfies REQ-044
 * @satisfies REQ-046
 * @satisfies REQ-047
 * @satisfies REQ-048
 * @satisfies REQ-049
 * @satisfies REQ-050
 * @satisfies REQ-051
 * @satisfies REQ-052
 * @satisfies REQ-045
 * @satisfies REQ-060
 * @satisfies REQ-061
 */

import {
  buildDebugBundle,
  clearDebugRecords,
  createLogger,
  readDebugRecords,
} from "./debug.js";
import {
  extractSignalDiagnostics,
  extractWindowAssignmentDiagnostics,
  mergeCopilotPayloads,
  parseClaudeUsageHtml,
  parseCodexUsageHtml,
  parseCopilotFeaturesHtml,
  parseCopilotPremiumHtml,
  providerPayloadHasUsableMetrics,
} from "./parsers.js";

/** @brief Default hardcoded refresh interval in seconds. */
export const REFRESH_INTERVAL_SECONDS = 180;

/** @brief Storage key for normalized runtime state. */
const STATE_STORAGE_KEY = "aibar.chrome.state";

/** @brief Storage key for optional refresh interval override. */
const INTERVAL_OVERRIDE_STORAGE_KEY = "aibar.chrome.refresh_interval_seconds";

/** @brief Session-scoped storage key for debug API enablement state. */
const DEBUG_API_ENABLED_SESSION_STORAGE_KEY = "aibar.chrome.debug_api_enabled";

/** @brief Alarm name used by service-worker scheduler. */
const REFRESH_ALARM_NAME = "aibar-refresh";

/** @brief Fixed provider download sequence required by requirements. */
const PROVIDER_FETCH_SEQUENCE = [
  "https://claude.ai/settings/usage",
  "https://chatgpt.com/codex/settings/usage",
  "https://github.com/settings/copilot/features",
  "https://github.com/settings/billing/premium_requests_usage",
];

/** @brief Canonical popup tab order represented by the primary API snapshot. */
const MAIN_API_TAB_ORDER = ["claude", "copilot", "codex"];

/** @brief Canonical window order by provider for popup progress-bar rendering. */
const MAIN_API_PROVIDER_WINDOWS = {
  claude: ["5h", "7d"],
  copilot: ["30d"],
  codex: ["5h", "7d", "code_review"],
};

/** @brief Debug API command identifiers exposed by runtime messaging. */
const DEBUG_API_SUPPORTED_COMMANDS = [
  "http.get",
  "parser.run",
  "provider.diagnose",
  "providers.diagnose",
  "providers.pages.get",
  "state.get",
  "refresh.run",
  "logs.get",
  "logs.clear",
  "interval.get",
  "interval.set",
];

/** @brief Allowed hostnames for debug HTTP retrieval command. */
const DEBUG_API_ALLOWED_HOSTS = new Set(["claude.ai", "chatgpt.com", "github.com"]);

/** @brief Default debug-body preview cap in characters. */
const DEBUG_API_DEFAULT_MAX_CHARS = 16000;

/** @brief Absolute debug-body preview cap in characters. */
const DEBUG_API_MAX_CHARS = 120000;

/** @brief Deterministic debug-disabled error returned by all debug API routes. */
const DEBUG_API_DISABLED_ERROR = "Debug API disabled: enable it in popup configuration for this runtime session.";

/** @brief Provider default URLs used by debug parser command. */
const DEBUG_API_PROVIDER_DEFAULT_URLS = {
  claude: "https://claude.ai/settings/usage",
  codex: "https://chatgpt.com/codex/settings/usage",
  copilot_features: "https://github.com/settings/copilot/features",
  copilot_premium: "https://github.com/settings/billing/premium_requests_usage",
};

/** @brief Default provider set used by aggregate diagnose command. */
const DEBUG_API_DEFAULT_PROVIDER_DIAGNOSE_SET = ["claude", "codex", "copilot_merged"];

/** @brief Required provider pages for one-call debug download diagnostics. */
const DEBUG_API_PROVIDER_PAGES = [
  { key: "claude", url: "https://claude.ai/settings/usage", parser: "claude" },
  { key: "copilot_features", url: "https://github.com/settings/copilot/features", parser: "copilot_features" },
  {
    key: "copilot_premium",
    url: "https://github.com/settings/billing/premium_requests_usage",
    parser: "copilot_premium",
  },
  { key: "codex", url: "https://chatgpt.com/codex/settings/usage", parser: "codex" },
];

/** @brief Default maximum same-origin related resources fetched per provider page. */
const DEBUG_API_PROVIDER_PAGES_DEFAULT_RELATED_LIMIT = 6;

/** @brief Localhost address used by external API listener. */
const LOCAL_API_LISTEN_HOST = "127.0.0.1";

/** @brief Default port used by external API listener. */
const LOCAL_API_DEFAULT_PORT = 32767;

/** @brief Minimum fallback port when probing in descending order. */
const LOCAL_API_MIN_PORT = 1024;

/** @brief TCP backlog used by localhost API listener. */
const LOCAL_API_BACKLOG = 10;

/** @brief Dedicated logger for background runtime events. */
const logger = createLogger("background");

/**
 * @brief Build empty provider state object.
 * @param {string} provider Provider identifier.
 * @returns {Record<string, unknown>} Empty provider state.
 */
function _emptyProviderState(provider) {
  return {
    provider,
    windows: {},
    parser: null,
    source_pages: [],
    extracted_at: null,
    error: null,
    last_success_at: null,
    last_failure_at: null,
  };
}

/**
 * @brief Build empty extension runtime state.
 * @returns {Record<string, unknown>} Empty state snapshot.
 */
function _emptyState() {
  return {
    refresh_interval_seconds: REFRESH_INTERVAL_SECONDS,
    last_cycle_status: "idle",
    updated_at: null,
    cycle_counter: 0,
    providers: {
      claude: _emptyProviderState("claude"),
      codex: _emptyProviderState("codex"),
      copilot: _emptyProviderState("copilot"),
    },
    provider_fetch_sequence: [...PROVIDER_FETCH_SEQUENCE],
    last_error: null,
  };
}

/** @brief In-memory mutable state snapshot. */
const runtimeState = _emptyState();

/** @brief Promise lock for concurrent refresh suppression. */
let refreshInFlight = null;

/** @brief In-memory non-persistent debug-access toggle. */
let debugApiEnabled = false;

/** @brief Current tcpServer socket id for localhost API listener. */
let localApiServerSocketId = null;

/** @brief Resolved localhost API port after successful bind. */
let localApiBoundPort = null;

/** @brief Flag preventing duplicate localhost accept loops. */
let localApiAcceptLoopRunning = false;

/**
 * @brief Deep clone state into message-safe payload.
 * @returns {Record<string, unknown>} Cloned state snapshot.
 */
function _cloneState() {
  return JSON.parse(JSON.stringify(runtimeState));
}

/**
 * @brief Convert optional metric token into finite number without null coercion.
 * @param {unknown} token Candidate token.
 * @returns {number | null} Finite number or null when token is empty/invalid.
 */
function _toFiniteMetricNumber(token) {
  if (token === null || token === undefined || token === "") {
    return null;
  }
  const parsed = Number(token);
  return Number.isFinite(parsed) ? parsed : null;
}

/**
 * @brief Normalize one window metric payload for primary API transport.
 * @details Restricts window payload shape to popup-rendered progress and quota
 * fields so API consumers can rebuild tab cards deterministically.
 * Time complexity: O(1).
 * Space complexity: O(1).
 * @param {Record<string, unknown> | null | undefined} windowData Candidate window payload.
 * @returns {{usage_percent: number | null, remaining: number | null, limit: number | null, reset_at: string | null}} Normalized window metrics.
 * @satisfies REQ-046
 */
function _normalizeMainApiWindow(windowData) {
  const usagePercent = _toFiniteMetricNumber(windowData?.usage_percent);
  const remaining = _toFiniteMetricNumber(windowData?.remaining);
  const limit = _toFiniteMetricNumber(windowData?.limit);
  const resetAt = typeof windowData?.reset_at === "string" ? windowData.reset_at : null;
  return {
    usage_percent: usagePercent,
    remaining,
    limit,
    reset_at: resetAt,
  };
}

/**
 * @brief Build machine-readable primary API snapshot payload.
 * @details Returns one-call popup/UI model with tab order plus per-provider
 * progress/quota windows, preserving runtime error and scheduler fields.
 * Time complexity: O(P*W), where P=provider count and W=window count.
 * Space complexity: O(P*W).
 * @returns {Record<string, unknown>} Primary API snapshot payload.
 * @satisfies REQ-046
 */
function _buildMainApiSnapshot() {
  const snapshot = _cloneState();
  const providers = {};

  for (const provider of MAIN_API_TAB_ORDER) {
    const providerState = snapshot.providers?.[provider] ?? _emptyProviderState(provider);
    const orderedWindows = {};
    for (const windowKey of MAIN_API_PROVIDER_WINDOWS[provider]) {
      orderedWindows[windowKey] = _normalizeMainApiWindow(providerState.windows?.[windowKey]);
    }
    providers[provider] = {
      provider,
      windows: orderedWindows,
      error: providerState?.error ?? null,
      parser: providerState?.parser ?? null,
      source_pages: Array.isArray(providerState?.source_pages) ? [...providerState.source_pages] : [],
      extracted_at: providerState?.extracted_at ?? null,
      last_success_at: providerState?.last_success_at ?? null,
      last_failure_at: providerState?.last_failure_at ?? null,
    };
  }

  return {
    endpoint: "api.main.snapshot",
    tab_order: [...MAIN_API_TAB_ORDER],
    tab_windows: JSON.parse(JSON.stringify(MAIN_API_PROVIDER_WINDOWS)),
    refresh_interval_seconds: snapshot.refresh_interval_seconds,
    last_cycle_status: snapshot.last_cycle_status,
    updated_at: snapshot.updated_at,
    cycle_counter: snapshot.cycle_counter,
    last_error: snapshot.last_error,
    provider_fetch_sequence: [...PROVIDER_FETCH_SEQUENCE],
    providers,
  };
}

/**
 * @brief Enforce runtime debug-access gate before serving debug routes.
 * @details Uses runtime debug-access flag restored from browser-session storage
 * and throws deterministic error to ensure all debug message routes fail
 * uniformly when disabled.
 * Time complexity: O(1).
 * Space complexity: O(1).
 * @returns {void}
 * @throws {Error} If debug access is disabled.
 * @satisfies CTN-014
 * @satisfies REQ-051
 */
function _ensureDebugAccessEnabled() {
  if (debugApiEnabled) {
    return;
  }
  const error = new Error(DEBUG_API_DISABLED_ERROR);
  error.code = "DEBUG_API_DISABLED";
  throw error;
}

/**
 * @brief Merge persisted state into in-memory runtime state.
 * @details Preserves last successful provider payloads across service-worker restarts
 * to satisfy failure fallback requirements.
 * @returns {Promise<void>} Completion promise.
 */
async function _loadPersistedState() {
  const stored = await chrome.storage.local.get(STATE_STORAGE_KEY);
  const previous = stored[STATE_STORAGE_KEY];
  if (!previous || typeof previous !== "object") {
    return;
  }

  const previousProviders = previous.providers ?? {};

  runtimeState.refresh_interval_seconds =
    Number(previous.refresh_interval_seconds) || runtimeState.refresh_interval_seconds;
  runtimeState.updated_at = previous.updated_at ?? runtimeState.updated_at;
  runtimeState.cycle_counter = Number(previous.cycle_counter) || runtimeState.cycle_counter;
  runtimeState.last_cycle_status = previous.last_cycle_status ?? runtimeState.last_cycle_status;
  runtimeState.last_error = previous.last_error ?? runtimeState.last_error;

  for (const provider of ["claude", "codex", "copilot"]) {
    if (previousProviders[provider] && typeof previousProviders[provider] === "object") {
      runtimeState.providers[provider] = {
        ...runtimeState.providers[provider],
        ...previousProviders[provider],
      };
    }
  }
}

/**
 * @brief Resolve optional browser-session storage area used for debug-flag persistence.
 * @details Returns `chrome.storage.session` when available in current runtime.
 * Falls back to `null` when session storage APIs are unavailable so callers can
 * preserve deterministic in-memory behavior.
 * Time complexity: O(1).
 * Space complexity: O(1).
 * @returns {chrome.storage.StorageArea | null} Session storage area or null.
 * @satisfies CTN-017
 */
function _getSessionStorageArea() {
  const sessionArea = chrome?.storage?.session;
  if (
    sessionArea
    && typeof sessionArea.get === "function"
    && typeof sessionArea.set === "function"
  ) {
    return sessionArea;
  }
  return null;
}

/**
 * @brief Load debug API enablement from browser-session storage.
 * @details Initializes `debugApiEnabled` using session-scoped persistence so the
 * flag survives service-worker restarts while resetting on browser termination.
 * Defaults to `false` when no persisted value exists.
 * Time complexity: O(1).
 * Space complexity: O(1).
 * @returns {Promise<boolean>} True when state was loaded from session storage.
 * @throws {Error} If session storage access throws.
 * @satisfies CTN-014
 * @satisfies CTN-017
 * @satisfies REQ-052
 */
async function _loadDebugAccessState() {
  debugApiEnabled = false;
  const sessionStorage = _getSessionStorageArea();
  if (!sessionStorage) {
    return false;
  }
  const stored = await sessionStorage.get(DEBUG_API_ENABLED_SESSION_STORAGE_KEY);
  debugApiEnabled = stored?.[DEBUG_API_ENABLED_SESSION_STORAGE_KEY] === true;
  return true;
}

/**
 * @brief Persist debug API enablement into browser-session storage.
 * @details Writes session-scoped debug-access value so explicit enablement
 * survives service-worker restarts but is dropped on browser shutdown.
 * Time complexity: O(1).
 * Space complexity: O(1).
 * @param {boolean} enabled Debug-access target state.
 * @returns {Promise<boolean>} True when session storage persistence is available.
 * @throws {Error} If session storage write fails.
 * @satisfies CTN-017
 * @satisfies REQ-052
 */
async function _persistDebugAccessState(enabled) {
  const sessionStorage = _getSessionStorageArea();
  if (!sessionStorage) {
    return false;
  }
  await sessionStorage.set({ [DEBUG_API_ENABLED_SESSION_STORAGE_KEY]: enabled });
  return true;
}

/**
 * @brief Persist current runtime state to extension storage.
 * @returns {Promise<void>} Completion promise.
 */
async function _persistState() {
  await chrome.storage.local.set({ [STATE_STORAGE_KEY]: _cloneState() });
}

/**
 * @brief Read configured refresh interval with persistence support.
 * @details Uses hardcoded default REFRESH_INTERVAL_SECONDS and allows optional
 * storage override persisted in `chrome.storage.local` that survives browser
 * restarts.  The interval value is restored on service-worker startup.
 * @returns {Promise<number>} Effective interval in seconds.
 * @satisfies CTN-008
 * @satisfies CTN-016
 */
async function _getRefreshIntervalSeconds() {
  const stored = await chrome.storage.local.get(INTERVAL_OVERRIDE_STORAGE_KEY);
  const override = Number(stored[INTERVAL_OVERRIDE_STORAGE_KEY]);
  if (Number.isFinite(override) && override >= 60) {
    return Math.round(override);
  }
  return REFRESH_INTERVAL_SECONDS;
}

/**
 * @brief Configure periodic refresh alarm.
 * @returns {Promise<void>} Completion promise.
 */
async function _scheduleRefreshAlarm() {
  const intervalSeconds = await _getRefreshIntervalSeconds();
  runtimeState.refresh_interval_seconds = intervalSeconds;

  await chrome.alarms.clear(REFRESH_ALARM_NAME);
  await chrome.alarms.create(REFRESH_ALARM_NAME, {
    delayInMinutes: Math.max(1, intervalSeconds / 60),
    periodInMinutes: Math.max(1, intervalSeconds / 60),
  });

  logger.info("scheduler-configured", {
    refresh_interval_seconds: intervalSeconds,
  });
}

/**
 * @brief Download one provider page using authenticated extension fetch.
 * @param {string} url Target page URL.
 * @returns {Promise<string>} Downloaded HTML content.
 * @throws {Error} When HTTP status is not OK.
 */
async function _fetchHtml(url) {
  const response = await fetch(url, {
    credentials: "include",
    cache: "no-store",
    redirect: "follow",
  });

  if (!response.ok) {
    throw new Error(`Fetch failed for ${url}: HTTP ${response.status}`);
  }

  return response.text();
}

/**
 * @brief Normalize debug-body preview length with hard bounds.
 * @details Converts caller-provided `max_chars` tokens into bounded integers to
 * avoid oversized responses in debug API payloads.
 * Time complexity: O(1).
 * Space complexity: O(1).
 * @param {unknown} token Requested max preview characters.
 * @returns {number} Bounded preview length.
 * @satisfies CTN-013
 */
function _normalizeDebugMaxChars(token) {
  const parsed = Number(token);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return DEBUG_API_DEFAULT_MAX_CHARS;
  }
  return Math.min(DEBUG_API_MAX_CHARS, Math.round(parsed));
}

/**
 * @brief Normalize and validate debug URL token.
 * @details Enforces `https` scheme and allowlisted hosts for debug retrieval
 * commands to reduce abuse surface.
 * Time complexity: O(1).
 * Space complexity: O(1).
 * @param {unknown} token Candidate URL.
 * @returns {string} Normalized URL string.
 * @throws {Error} If URL is invalid, non-HTTPS, or host is not allowed.
 * @satisfies CTN-012
 */
function _normalizeDebugUrl(token) {
  if (typeof token !== "string" || !token.trim()) {
    throw new Error("URL must be a non-empty string");
  }

  let parsed;
  try {
    parsed = new URL(token);
  } catch (_error) {
    throw new Error("URL is not valid");
  }

  if (parsed.protocol !== "https:") {
    throw new Error("URL must use https protocol for debug command");
  }

  if (!DEBUG_API_ALLOWED_HOSTS.has(parsed.hostname)) {
    throw new Error(`URL host not allowed for debug command: ${parsed.hostname}`);
  }

  return parsed.toString();
}

/**
 * @brief Convert response headers into bounded JSON-safe object.
 * @details Serializes at most 30 headers to constrain debug response footprint.
 * @param {Headers} headers Response headers object.
 * @returns {Record<string, string>} Serialized headers map.
 */
function _serializeHeaders(headers) {
  const output = {};
  let count = 0;
  for (const [key, value] of headers.entries()) {
    output[key] = value;
    count += 1;
    if (count >= 30) {
      break;
    }
  }
  return output;
}

/**
 * @brief Build deterministic HTML probe metadata for parser diagnostics.
 * @param {string} html Raw HTML text.
 * @returns {Record<string, unknown>} Probe metadata object.
 */
function _buildHtmlProbe(html) {
  const titleMatch = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  const title = titleMatch ? titleMatch[1].replace(/\s+/g, " ").trim() : null;
  const compactHtml = html.toLowerCase();
  return {
    html_length: html.length,
    title,
    has_progressbar_role: html.includes("progressbar"),
    has_next_data: html.includes("__NEXT_DATA__"),
    has_window_tokens: /\b(?:5h|7d|30d|code_review)\b/i.test(html),
    has_cloudflare_challenge: /just a moment|cf_chl|challenge-platform|cf-mitigated/i.test(compactHtml),
    has_login_marker: /sign in|log in|login|enable javascript and cookies to continue/i.test(compactHtml),
    script_tag_count: (html.match(/<script\b/gi) || []).length,
  };
}

/**
 * @brief Compute SHA-256 hash for deterministic body identity checks.
 * @param {string} text Input text payload.
 * @returns {Promise<string>} Hex-encoded digest.
 */
async function _sha256Hex(text) {
  const bytes = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

/**
 * @brief Build payload-quality summary for parsed provider windows.
 * @param {Record<string, unknown>} payload Parsed provider payload.
 * @returns {Record<string, unknown>} Quality summary object.
 */
function _buildPayloadQuality(payload) {
  const quality = {
    payload_usable: providerPayloadHasUsableMetrics(payload),
    usable_windows: 0,
    windows: {},
  };
  const windows = payload?.windows && typeof payload.windows === "object" ? payload.windows : {};
  for (const [windowKey, windowData] of Object.entries(windows)) {
    const usage = _toFiniteMetricNumber(windowData?.usage_percent);
    const remaining = _toFiniteMetricNumber(windowData?.remaining);
    const limit = _toFiniteMetricNumber(windowData?.limit);
    const hasUsage = usage !== null;
    const hasRemaining = remaining !== null;
    const hasLimit = limit !== null;
    const hasQuota = hasRemaining || hasLimit;
    const usable = hasUsage || hasQuota;
    if (usable) {
      quality.usable_windows += 1;
    }
    quality.windows[windowKey] = {
      has_usage_percent: hasUsage,
      has_quota: hasQuota,
      usage_percent: hasUsage ? usage : null,
      remaining: hasRemaining ? remaining : null,
      limit: hasLimit ? limit : null,
      reset_at: typeof windowData?.reset_at === "string" ? windowData.reset_at : null,
      usable,
    };
  }
  return quality;
}

/**
 * @brief Build parser failure error when payload has no usable metrics.
 * @param {string} provider Provider key.
 * @param {Record<string, unknown>} payload Parsed payload.
 * @returns {void}
 * @throws {Error} If payload is missing quota/progress metrics.
 */
function _assertProviderPayloadUsable(provider, payload) {
  if (providerPayloadHasUsableMetrics(payload)) {
    return;
  }
  const signalCounts = payload?.parser?.signal_counts ?? {};
  throw new Error(
    `Parser produced no usable ${provider} metrics (signals=${JSON.stringify(signalCounts)})`
  );
}

/**
 * @brief Download one debug URL and capture response metadata.
 * @param {string} urlToken Debug URL token.
 * @returns {Promise<Record<string, unknown>>} Download result with full body.
 * @satisfies REQ-047
 */
async function _downloadDebugUrl(urlToken) {
  const normalizedUrl = _normalizeDebugUrl(urlToken);
  const response = await fetch(normalizedUrl, {
    credentials: "include",
    cache: "no-store",
    redirect: "follow",
  });
  const bodyText = await response.text();
  return {
    requested_url: normalizedUrl,
    final_url: response.url,
    status: response.status,
    ok: response.ok,
    redirected: response.redirected,
    content_type: response.headers.get("content-type"),
    headers: _serializeHeaders(response.headers),
    body_text: bodyText,
  };
}

/**
 * @brief Build debug HTTP response payload with bounded preview and hash metadata.
 * @param {Record<string, unknown>} download Raw download payload.
 * @param {number} maxChars Bounded preview size.
 * @returns {Promise<Record<string, unknown>>} HTTP response payload.
 */
async function _buildDebugHttpResponse(download, maxChars) {
  const bodyPreview = download.body_text.slice(0, maxChars);
  const tailPreview = download.body_text.slice(Math.max(0, download.body_text.length - maxChars));
  return {
    final_url: download.final_url,
    status: download.status,
    ok: download.ok,
    redirected: download.redirected,
    content_type: download.content_type,
    headers: download.headers,
    body_length: download.body_text.length,
    body_sha256: await _sha256Hex(download.body_text),
    body_preview: bodyPreview,
    body_preview_tail: tailPreview,
    body_truncated: download.body_text.length > bodyPreview.length,
    html_probe: _buildHtmlProbe(download.body_text),
  };
}

/**
 * @brief Normalize max related-resource downloads for providers.pages.get.
 * @details Applies deterministic hard bounds to prevent unbounded secondary page
 * downloads during debug diagnostics runs.
 * Time complexity: O(1).
 * Space complexity: O(1).
 * @param {unknown} token Candidate limit value.
 * @returns {number} Bounded related-resource limit.
 * @satisfies REQ-048
 */
function _normalizeDebugRelatedLimit(token) {
  const parsed = Number(token);
  if (!Number.isFinite(parsed) || parsed < 0) {
    return DEBUG_API_PROVIDER_PAGES_DEFAULT_RELATED_LIMIT;
  }
  return Math.min(20, Math.max(0, Math.round(parsed)));
}

/**
 * @brief Extract same-origin related resource URLs from one HTML page.
 * @details Parses script/link resource attributes and keeps only `https`
 * same-origin URLs so follow-up debug downloads remain within current host scope.
 * Time complexity: O(N) on HTML length.
 * Space complexity: O(M) on extracted URLs.
 * @param {string} html Source HTML.
 * @param {string} pageUrl Base page URL used for URL resolution.
 * @returns {Array<string>} Ordered unique same-origin resource URLs.
 * @satisfies REQ-048
 */
function _extractRelatedResourceUrls(html, pageUrl) {
  let baseUrl;
  try {
    baseUrl = new URL(pageUrl);
  } catch (_error) {
    return [];
  }

  const matches = [];
  const attrRegex = /<(?:script|link)\b[^>]*\b(?:src|href)\s*=\s*(?:"([^"]+)"|'([^']+)')/gi;
  let attrMatch;
  while ((attrMatch = attrRegex.exec(html)) !== null) {
    const raw = attrMatch[1] ?? attrMatch[2] ?? "";
    if (!raw || raw.startsWith("data:") || raw.startsWith("javascript:")) {
      continue;
    }
    try {
      const resolved = new URL(raw, baseUrl);
      if (resolved.protocol !== "https:" || resolved.hostname !== baseUrl.hostname) {
        continue;
      }
      matches.push(resolved.toString());
    } catch (_error) {
      // Ignore malformed related URLs.
    }
  }

  return Array.from(new Set(matches));
}

/**
 * @brief Build parser-centric quality summary for one provider payload.
 * @param {string} provider Provider token.
 * @param {Record<string, unknown>} payload Parsed payload.
 * @returns {Record<string, unknown>} Structured quality summary.
 * @satisfies REQ-048
 */
function _buildProviderPayloadAnalysis(provider, payload) {
  const quality = _buildPayloadQuality(payload);
  return {
    provider,
    payload_usable: quality.payload_usable,
    usable_windows: quality.usable_windows,
    windows: quality.windows,
    payload_assertion: _buildPayloadAssertion(provider, payload),
  };
}

/**
 * @brief Download same-origin related resources for one provider page.
 * @param {string} html Page HTML.
 * @param {string} pageUrl Source page URL.
 * @param {number} maxChars Preview size limit.
 * @param {number} maxRelated Resource download limit.
 * @returns {Promise<Record<string, unknown>>} Related-resource diagnostics payload.
 * @satisfies REQ-048
 */
async function _downloadRelatedResources(html, pageUrl, maxChars, maxRelated) {
  const candidates = _extractRelatedResourceUrls(html, pageUrl);
  const selected = candidates.slice(0, maxRelated);
  const resources = [];
  for (const resourceUrl of selected) {
    try {
      const download = await _downloadDebugUrl(resourceUrl);
      resources.push({
        url: resourceUrl,
        ok: true,
        response: await _buildDebugHttpResponse(download, maxChars),
      });
    } catch (error) {
      resources.push({
        url: resourceUrl,
        ok: false,
        error: String(error?.message ?? error),
      });
    }
  }

  return {
    discovered_total: candidates.length,
    fetched_total: resources.length,
    resources,
  };
}

/**
 * @brief Execute one provider-page download diagnostic entry.
 * @param {{key: string, url: string, parser: string}} descriptor Provider page descriptor.
 * @param {number} maxChars Preview-size limit.
 * @param {number} maxRelated Related-resource download limit.
 * @returns {Promise<Record<string, unknown>>} Page diagnostics payload.
 * @satisfies REQ-048
 */
async function _executeProviderPageDownload(descriptor, maxChars, maxRelated) {
  const download = await _downloadDebugUrl(descriptor.url);
  const parser = _resolveDebugParser(descriptor.parser);
  const parserPayload = parser(download.body_text);
  const payloadAnalysis = _buildProviderPayloadAnalysis(descriptor.parser, parserPayload);
  const related = await _downloadRelatedResources(
    download.body_text,
    descriptor.url,
    Math.min(maxChars, 8000),
    maxRelated
  );

  return {
    key: descriptor.key,
    provider: descriptor.parser,
    request: {
      url: download.requested_url,
      max_chars: maxChars,
      related_limit: maxRelated,
    },
    response: await _buildDebugHttpResponse(download, maxChars),
    parser_signal_diagnostics: extractSignalDiagnostics(download.body_text),
    window_assignment_diagnostics: _buildWindowAssignmentDiagnostics(download.body_text, descriptor.parser),
    parser_payload: parserPayload,
    payload_analysis: payloadAnalysis,
    related_content: related,
  };
}

/**
 * @brief Execute providers.pages.get debug command.
 * @details Downloads required provider pages and same-origin related resources,
 * runs provider-specific parsers, and returns one aggregate diagnostics payload.
 * @param {Record<string, unknown>} args Debug command arguments.
 * @returns {Promise<Record<string, unknown>>} Aggregate page diagnostics payload.
 * @satisfies REQ-048
 */
async function _executeProvidersPagesGetCommand(args) {
  const maxChars = _normalizeDebugMaxChars(args?.max_chars);
  const maxRelated = _normalizeDebugRelatedLimit(args?.max_related_resources);
  const providers = {};

  for (const descriptor of DEBUG_API_PROVIDER_PAGES) {
    try {
      providers[descriptor.key] = {
        ok: true,
        diagnostics: await _executeProviderPageDownload(descriptor, maxChars, maxRelated),
      };
    } catch (error) {
      providers[descriptor.key] = {
        ok: false,
        error: String(error?.message ?? error),
      };
    }
  }

  const summary = {
    total: DEBUG_API_PROVIDER_PAGES.length,
    ok: Object.values(providers).filter((entry) => entry?.ok).length,
  };
  summary.fail = summary.total - summary.ok;

  return {
    command: "providers.pages.get",
    request: {
      urls: DEBUG_API_PROVIDER_PAGES.map((entry) => entry.url),
      max_chars: maxChars,
      max_related_resources: maxRelated,
    },
    summary,
    providers,
  };
}

/**
 * @brief Build payload-usability assertion status for diagnostics commands.
 * @details Reuses runtime parser-usability gate and returns structured pass/fail
 * metadata without throwing to simplify field-debug report consumption.
 * @param {string} provider Provider key.
 * @param {Record<string, unknown>} payload Parsed payload.
 * @returns {{ok: boolean, error: string | null}} Assertion status payload.
 */
function _buildPayloadAssertion(provider, payload) {
  try {
    _assertProviderPayloadUsable(provider, payload);
    return {
      ok: true,
      error: null,
    };
  } catch (error) {
    return {
      ok: false,
      error: String(error?.message ?? error),
    };
  }
}

/**
 * @brief Build window-assignment diagnostics for one parser HTML source.
 * @details Wraps parser trace extraction in non-throwing envelope to keep debug
 * API responses stable even when trace generation fails.
 * @param {string} html Raw HTML payload.
 * @param {string} provider Provider token for window-key selection.
 * @returns {Record<string, unknown>} Window-trace payload or structured error.
 */
function _buildWindowAssignmentDiagnostics(html, provider) {
  try {
    return extractWindowAssignmentDiagnostics(html, { provider });
  } catch (error) {
    return {
      provider,
      error: String(error?.message ?? error),
    };
  }
}

/**
 * @brief Execute provider-level diagnose routine for one provider token.
 * @details Downloads provider pages, executes parser flows, and returns combined
 * response probes, parser payloads, usability checks, and window traces.
 * @param {string} provider Provider token.
 * @param {Record<string, unknown>} args Debug command arguments.
 * @param {number} maxChars Bounded response preview size.
 * @returns {Promise<Record<string, unknown>>} Diagnose payload.
 */
async function _executeProviderDiagnoseCommand(provider, args, maxChars) {
  if (provider === "copilot_merged") {
    const featuresDownload = await _downloadDebugUrl(
      args?.url_features ?? DEBUG_API_PROVIDER_DEFAULT_URLS.copilot_features
    );
    const premiumDownload = await _downloadDebugUrl(
      args?.url_premium ?? DEBUG_API_PROVIDER_DEFAULT_URLS.copilot_premium
    );
    const featuresPayload = parseCopilotFeaturesHtml(featuresDownload.body_text);
    const premiumPayload = parseCopilotPremiumHtml(premiumDownload.body_text);
    const mergedPayload = mergeCopilotPayloads(featuresPayload, premiumPayload);
    const mergedQuality = _buildPayloadQuality(mergedPayload);

    return {
      sources: {
        features: {
          request_url: featuresDownload.requested_url,
          response: await _buildDebugHttpResponse(featuresDownload, maxChars),
          parser_signal_diagnostics: extractSignalDiagnostics(featuresDownload.body_text),
          window_assignment_diagnostics: _buildWindowAssignmentDiagnostics(
            featuresDownload.body_text,
            "copilot_features"
          ),
          parser_payload: featuresPayload,
          payload_quality: _buildPayloadQuality(featuresPayload),
          payload_assertion: _buildPayloadAssertion("copilot_features", featuresPayload),
        },
        premium: {
          request_url: premiumDownload.requested_url,
          response: await _buildDebugHttpResponse(premiumDownload, maxChars),
          parser_signal_diagnostics: extractSignalDiagnostics(premiumDownload.body_text),
          window_assignment_diagnostics: _buildWindowAssignmentDiagnostics(
            premiumDownload.body_text,
            "copilot_premium"
          ),
          parser_payload: premiumPayload,
          payload_quality: _buildPayloadQuality(premiumPayload),
          payload_assertion: _buildPayloadAssertion("copilot_premium", premiumPayload),
        },
      },
      parser_payload: mergedPayload,
      payload_quality: mergedQuality,
      payload_usable: mergedQuality.payload_usable,
      payload_assertion: _buildPayloadAssertion("copilot", mergedPayload),
    };
  }

  const parser = _resolveDebugParser(provider);
  const download = await _downloadDebugUrl(args?.url ?? DEBUG_API_PROVIDER_DEFAULT_URLS[provider]);
  const parserPayload = parser(download.body_text);
  const payloadQuality = _buildPayloadQuality(parserPayload);

  return {
    request: {
      url: download.requested_url,
      max_chars: maxChars,
    },
    response: await _buildDebugHttpResponse(download, maxChars),
    parser_signal_diagnostics: extractSignalDiagnostics(download.body_text),
    window_assignment_diagnostics: _buildWindowAssignmentDiagnostics(download.body_text, provider),
    parser_payload: parserPayload,
    payload_quality: payloadQuality,
    payload_usable: payloadQuality.payload_usable,
    payload_assertion: _buildPayloadAssertion(provider, parserPayload),
  };
}

/**
 * @brief Resolve parser function by debug provider key.
 * @param {string} provider Provider key token.
 * @returns {(html: string) => Record<string, unknown>} Parser function.
 * @throws {Error} If provider key is unsupported.
 */
function _resolveDebugParser(provider) {
  switch (provider) {
    case "claude":
      return parseClaudeUsageHtml;
    case "codex":
      return parseCodexUsageHtml;
    case "copilot_features":
      return parseCopilotFeaturesHtml;
    case "copilot_premium":
      return parseCopilotPremiumHtml;
    default:
      throw new Error(`Unsupported parser provider: ${provider}`);
  }
}

/**
 * @brief Build summary-safe command args for debug logging.
 * @details Redacts large inline HTML fields by replacing them with length metadata.
 * @param {Record<string, unknown>} args Debug command args.
 * @returns {Record<string, unknown>} Sanitized argument summary.
 */
function _summarizeDebugArgs(args) {
  const summary = { ...args };
  if (typeof summary.html === "string") {
    summary.html_chars = summary.html.length;
    delete summary.html;
  }
  if (typeof summary.html_features === "string") {
    summary.html_features_chars = summary.html_features.length;
    delete summary.html_features;
  }
  if (typeof summary.html_premium === "string") {
    summary.html_premium_chars = summary.html_premium.length;
    delete summary.html_premium;
  }
  return summary;
}

/**
 * @brief Build debug API command catalog payload.
 * @returns {Record<string, unknown>} Supported command catalog.
 * @satisfies REQ-046
 */
function _describeDebugApi() {
  return {
    endpoint: "debug.api.execute",
    commands: [...DEBUG_API_SUPPORTED_COMMANDS],
    defaults: {
      http_get_max_chars: DEBUG_API_DEFAULT_MAX_CHARS,
      max_allowed_chars: DEBUG_API_MAX_CHARS,
      parser_default_urls: { ...DEBUG_API_PROVIDER_DEFAULT_URLS },
      provider_diagnose_supported: [
        "claude",
        "codex",
        "copilot_features",
        "copilot_premium",
        "copilot_merged",
      ],
      providers_diagnose_default: [...DEBUG_API_DEFAULT_PROVIDER_DIAGNOSE_SET],
      providers_pages_get_urls: DEBUG_API_PROVIDER_PAGES.map((entry) => entry.url),
      providers_pages_get_default_related_limit: DEBUG_API_PROVIDER_PAGES_DEFAULT_RELATED_LIMIT,
    },
  };
}

/**
 * @brief Build deterministic debug-disabled response envelope.
 * @details Centralizes disabled-debug rejection payload shape so runtime and
 * localhost external routes preserve identical contract semantics.
 * Time complexity: O(1).
 * Space complexity: O(1).
 * @param {unknown} errorSource Candidate error instance/value.
 * @returns {{ok: false, code: string, error: string}} Deterministic disabled-debug payload.
 * @satisfies REQ-051
 */
function _buildDebugDisabledResponse(errorSource) {
  return {
    ok: false,
    code: "DEBUG_API_DISABLED",
    error: String(errorSource?.message ?? errorSource),
  };
}

/**
 * @brief Execute debug API command with structured lifecycle logging.
 * @details Reuses command-dispatch implementation and emits deterministic
 * start/success/failure log records used by runtime and localhost API calls.
 * Time complexity: O(C), where C is command-specific execution complexity.
 * Space complexity: O(C), where C is command-specific response payload size.
 * @param {string} command Debug command identifier.
 * @param {Record<string, unknown>} args Debug command arguments.
 * @returns {Promise<Record<string, unknown>>} Standardized command response envelope.
 * @satisfies REQ-048
 * @satisfies REQ-050
 */
async function _runDebugApiExecute(command, args) {
  const startedAt = Date.now();
  logger.info("debug-api-command-start", {
    command,
    args: _summarizeDebugArgs(args),
  });

  try {
    const result = await _executeDebugApiCommand(command, args);
    const durationMs = Date.now() - startedAt;
    logger.info("debug-api-command-success", {
      command,
      duration_ms: durationMs,
    });
    return {
      ok: true,
      command,
      debug_api_enabled: debugApiEnabled,
      duration_ms: durationMs,
      result,
    };
  } catch (error) {
    const durationMs = Date.now() - startedAt;
    const messageText = String(error?.message ?? error);
    logger.error("debug-api-command-failure", {
      command,
      duration_ms: durationMs,
      error: messageText,
    });
    return {
      ok: false,
      command,
      debug_api_enabled: debugApiEnabled,
      duration_ms: durationMs,
      error: messageText,
    };
  }
}

/**
 * @brief Evaluate debug access gate and return deterministic failure payload.
 * @details Runs debug gate once and returns null for enabled state; otherwise
 * returns REQ-051-compliant disabled-debug response.
 * Time complexity: O(1).
 * Space complexity: O(1).
 * @returns {{ok: false, code: string, error: string} | null} Disabled-debug response or null.
 * @satisfies REQ-051
 */
function _getDebugGateFailure() {
  try {
    _ensureDebugAccessEnabled();
    return null;
  } catch (error) {
    return _buildDebugDisabledResponse(error);
  }
}

/**
 * @brief Resolve structured payload for `debug.api.describe`.
 * @details Applies debug-access gate before returning command-catalog metadata.
 * Time complexity: O(1).
 * Space complexity: O(1).
 * @returns {Record<string, unknown>} Describe response envelope.
 * @satisfies REQ-048
 * @satisfies REQ-051
 */
function _buildDebugDescribeResponse() {
  const gateFailure = _getDebugGateFailure();
  if (gateFailure) {
    return gateFailure;
  }
  return {
    ok: true,
    debug_api_enabled: debugApiEnabled,
    api: _describeDebugApi(),
  };
}

/**
 * @brief Resolve structured payload for `debug.api.execute`.
 * @details Validates command token, enforces debug gate, and dispatches to
 * lifecycle-logged command execution helper.
 * Time complexity: O(C), where C is command-specific complexity.
 * Space complexity: O(C), where C is command payload size.
 * @param {Record<string, unknown>} request Candidate execute request payload.
 * @returns {Promise<Record<string, unknown>>} Execute response envelope.
 * @satisfies REQ-048
 * @satisfies REQ-050
 * @satisfies REQ-051
 */
async function _buildDebugExecuteResponse(request) {
  const gateFailure = _getDebugGateFailure();
  if (gateFailure) {
    return gateFailure;
  }
  const command = typeof request?.command === "string" ? request.command.trim() : "";
  if (!command) {
    return { ok: false, error: "debug.api.execute requires command string" };
  }
  const args = request?.args && typeof request.args === "object" ? request.args : {};
  return await _runDebugApiExecute(command, args);
}

/**
 * @brief Execute one debug API command.
 * @details Dispatches debug commands for HTTP retrieval, parser execution, and
 * standard runtime operations with deterministic structured responses.
 * @param {string} command Debug command identifier.
 * @param {Record<string, unknown>} args Debug command arguments.
 * @returns {Promise<Record<string, unknown>>} Command execution payload.
 * @throws {Error} If command or arguments are invalid.
 * @satisfies REQ-047
 * @satisfies REQ-048
 * @satisfies REQ-049
 */
async function _executeDebugApiCommand(command, args) {
  switch (command) {
    case "http.get": {
      const maxChars = _normalizeDebugMaxChars(args?.max_chars);
      const download = await _downloadDebugUrl(args?.url);
      return {
        command: "http.get",
        request: {
          url: download.requested_url,
          max_chars: maxChars,
        },
        response: await _buildDebugHttpResponse(download, maxChars),
      };
    }
    case "parser.run": {
      const provider = String(args?.provider ?? "").trim();
      if (!provider) {
        throw new Error("parser.run requires provider argument");
      }

      if (provider === "copilot_merged") {
        const featuresHtml = typeof args?.html_features === "string"
          ? args.html_features
          : (await _downloadDebugUrl(args?.url_features ?? DEBUG_API_PROVIDER_DEFAULT_URLS.copilot_features)).body_text;
        const premiumHtml = typeof args?.html_premium === "string"
          ? args.html_premium
          : (await _downloadDebugUrl(args?.url_premium ?? DEBUG_API_PROVIDER_DEFAULT_URLS.copilot_premium)).body_text;
        const mergedPayload = mergeCopilotPayloads(
          parseCopilotFeaturesHtml(featuresHtml),
          parseCopilotPremiumHtml(premiumHtml)
        );
        const payloadQuality = _buildPayloadQuality(mergedPayload);
        return {
          command: "parser.run",
          provider: "copilot_merged",
          html_probe: {
            features: _buildHtmlProbe(featuresHtml),
            premium: _buildHtmlProbe(premiumHtml),
          },
          parser_signal_diagnostics: {
            features: extractSignalDiagnostics(featuresHtml),
            premium: extractSignalDiagnostics(premiumHtml),
          },
          window_assignment_diagnostics: {
            features: _buildWindowAssignmentDiagnostics(featuresHtml, "copilot_features"),
            premium: _buildWindowAssignmentDiagnostics(premiumHtml, "copilot_premium"),
          },
          parser_payload: mergedPayload,
          payload_quality: payloadQuality,
          payload_usable: payloadQuality.payload_usable,
          payload_assertion: _buildPayloadAssertion("copilot", mergedPayload),
        };
      }

      const parser = _resolveDebugParser(provider);
      const html = typeof args?.html === "string"
        ? args.html
        : (await _downloadDebugUrl(args?.url ?? DEBUG_API_PROVIDER_DEFAULT_URLS[provider])).body_text;
      const parserPayload = parser(html);
      const payloadQuality = _buildPayloadQuality(parserPayload);
      return {
        command: "parser.run",
        provider,
        html_probe: _buildHtmlProbe(html),
        parser_signal_diagnostics: extractSignalDiagnostics(html),
        window_assignment_diagnostics: _buildWindowAssignmentDiagnostics(html, provider),
        parser_payload: parserPayload,
        payload_quality: payloadQuality,
        payload_usable: payloadQuality.payload_usable,
        payload_assertion: _buildPayloadAssertion(provider, parserPayload),
      };
    }
    case "provider.diagnose": {
      const provider = String(args?.provider ?? "").trim();
      if (!provider) {
        throw new Error("provider.diagnose requires provider argument");
      }
      const maxChars = _normalizeDebugMaxChars(args?.max_chars);
      return {
        command: "provider.diagnose",
        provider,
        ...(await _executeProviderDiagnoseCommand(provider, args, maxChars)),
      };
    }
    case "providers.diagnose": {
      const maxChars = _normalizeDebugMaxChars(args?.max_chars);
      const providerTokens = Array.isArray(args?.providers)
        ? args.providers.map((token) => String(token).trim()).filter((token) => Boolean(token))
        : [...DEBUG_API_DEFAULT_PROVIDER_DIAGNOSE_SET];
      const dedupedProviders = Array.from(new Set(providerTokens));
      if (dedupedProviders.length === 0) {
        throw new Error("providers.diagnose requires at least one provider token");
      }

      const providers = {};
      for (const provider of dedupedProviders) {
        try {
          providers[provider] = {
            ok: true,
            diagnostics: await _executeProviderDiagnoseCommand(provider, args, maxChars),
          };
        } catch (error) {
          providers[provider] = {
            ok: false,
            error: String(error?.message ?? error),
          };
        }
      }

      const summary = {
        total: dedupedProviders.length,
        ok: Object.values(providers).filter((entry) => entry?.ok).length,
      };
      summary.fail = summary.total - summary.ok;

      return {
        command: "providers.diagnose",
        request: {
          providers: dedupedProviders,
          max_chars: maxChars,
        },
        summary,
        provider_fetch_sequence: [...PROVIDER_FETCH_SEQUENCE],
        providers,
      };
    }
    case "providers.pages.get":
      return await _executeProvidersPagesGetCommand(args);
    case "state.get":
      return {
        command: "state.get",
        state: _cloneState(),
      };
    case "refresh.run":
      await _refreshAllProviders("debug_api");
      return {
        command: "refresh.run",
        state: _cloneState(),
      };
    case "logs.get":
      return {
        command: "logs.get",
        logs: await readDebugRecords(),
      };
    case "logs.clear":
      await clearDebugRecords();
      return {
        command: "logs.clear",
        cleared: true,
      };
    case "interval.get":
      return {
        command: "interval.get",
        refresh_interval_seconds: runtimeState.refresh_interval_seconds,
      };
    case "interval.set": {
      const seconds = Number(args?.seconds);
      if (!Number.isFinite(seconds) || seconds < 60) {
        throw new Error("interval.set requires seconds >= 60");
      }
      await chrome.storage.local.set({ [INTERVAL_OVERRIDE_STORAGE_KEY]: Math.round(seconds) });
      await _scheduleRefreshAlarm();
      return {
        command: "interval.set",
        refresh_interval_seconds: runtimeState.refresh_interval_seconds,
      };
    }
    default:
      throw new Error(`Unsupported debug command: ${command}`);
  }
}

/**
 * @brief Check whether sockets transport exists for localhost API listener.
 * @details Validates MV3 runtime support for tcpServer/tcp socket namespaces.
 * Time complexity: O(1).
 * Space complexity: O(1).
 * @returns {boolean} True when sockets transport APIs are available.
 * @satisfies REQ-060
 */
function _localApiTransportSupported() {
  return Boolean(chrome?.sockets?.tcpServer && chrome?.sockets?.tcp);
}

/**
 * @brief Create one TCP server socket through callback-based Chrome API.
 * @details Wraps callback API into Promise envelope for deterministic async flow.
 * Time complexity: O(1).
 * Space complexity: O(1).
 * @returns {Promise<number>} Created server socket identifier.
 * @throws {Error} If server socket creation fails.
 * @satisfies REQ-060
 */
function _createTcpServerSocket() {
  return new Promise((resolve, reject) => {
    chrome.sockets.tcpServer.create({}, (createInfo) => {
      if (!createInfo || !Number.isInteger(createInfo.socketId)) {
        reject(new Error("Failed to create localhost API server socket"));
        return;
      }
      resolve(createInfo.socketId);
    });
  });
}

/**
 * @brief Listen on candidate localhost port for external API bridge.
 * @details Attempts tcpServer listen call and returns Chrome result code.
 * Time complexity: O(1).
 * Space complexity: O(1).
 * @param {number} socketId Server socket id.
 * @param {number} port Candidate localhost port.
 * @returns {Promise<number>} Listen result code; >=0 indicates success.
 * @satisfies REQ-060
 */
function _listenTcpServerSocket(socketId, port) {
  return new Promise((resolve) => {
    chrome.sockets.tcpServer.listen(
      socketId,
      LOCAL_API_LISTEN_HOST,
      port,
      LOCAL_API_BACKLOG,
      (resultCode) => {
        resolve(resultCode);
      }
    );
  });
}

/**
 * @brief Close TCP server socket best-effort.
 * @details Swallows close-time errors because socket may already be closed.
 * Time complexity: O(1).
 * Space complexity: O(1).
 * @param {number} socketId Server socket id.
 * @returns {void}
 */
function _closeTcpServerSocket(socketId) {
  try {
    chrome.sockets.tcpServer.close(socketId);
  } catch (error) {
    logger.warn("localhost-api-server-close-failure", {
      socket_id: socketId,
      error: String(error?.message ?? error),
    });
  }
}

/**
 * @brief Accept one pending client connection on localhost API listener.
 * @details Wraps callback API into Promise to keep accept-loop sequential.
 * Time complexity: O(1) excluding socket wait time.
 * Space complexity: O(1).
 * @param {number} socketId Server socket id.
 * @returns {Promise<{resultCode: number, clientSocketId: number}>} Accepted client metadata.
 * @satisfies REQ-060
 */
function _acceptTcpClient(socketId) {
  return new Promise((resolve) => {
    chrome.sockets.tcpServer.accept(socketId, (acceptInfo) => {
      resolve({
        resultCode: Number(acceptInfo?.resultCode ?? -1),
        clientSocketId: Number(acceptInfo?.clientSocketId ?? -1),
      });
    });
  });
}

/**
 * @brief Read request bytes from accepted client socket.
 * @details Reads one request chunk for compact HTTP request parsing.
 * Time complexity: O(N), where N is received byte count.
 * Space complexity: O(N).
 * @param {number} clientSocketId Accepted client socket id.
 * @returns {Promise<{resultCode: number, data: ArrayBuffer | null}>} Read result metadata.
 * @satisfies REQ-061
 */
function _readTcpClientChunk(clientSocketId) {
  return new Promise((resolve) => {
    chrome.sockets.tcp.recv(clientSocketId, (recvInfo) => {
      resolve({
        resultCode: Number(recvInfo?.resultCode ?? -1),
        data: recvInfo?.data ?? null,
      });
    });
  });
}

/**
 * @brief Write one HTTP response payload to accepted client socket.
 * @details Serializes response text via UTF-8 encoder and forwards bytes via tcp.send.
 * Time complexity: O(N), where N is response byte count.
 * Space complexity: O(N).
 * @param {number} clientSocketId Accepted client socket id.
 * @param {string} payload HTTP response payload.
 * @returns {Promise<void>} Completion promise.
 * @satisfies REQ-061
 */
function _writeTcpClientPayload(clientSocketId, payload) {
  return new Promise((resolve) => {
    const bytes = new TextEncoder().encode(payload);
    chrome.sockets.tcp.send(clientSocketId, bytes.buffer, () => {
      resolve();
    });
  });
}

/**
 * @brief Close accepted client socket best-effort.
 * @details Executes disconnect and close without propagating close-time failures.
 * Time complexity: O(1).
 * Space complexity: O(1).
 * @param {number} clientSocketId Accepted client socket id.
 * @returns {void}
 */
function _closeTcpClientSocket(clientSocketId) {
  try {
    chrome.sockets.tcp.disconnect(clientSocketId);
  } catch (error) {
    logger.warn("localhost-api-client-disconnect-failure", {
      socket_id: clientSocketId,
      error: String(error?.message ?? error),
    });
  }
  try {
    chrome.sockets.tcp.close(clientSocketId);
  } catch (error) {
    logger.warn("localhost-api-client-close-failure", {
      socket_id: clientSocketId,
      error: String(error?.message ?? error),
    });
  }
}

/**
 * @brief Build canonical HTTP JSON response payload.
 * @details Converts body object into HTTP/1.1 JSON response with content length.
 * Time complexity: O(N), where N is serialized JSON length.
 * Space complexity: O(N).
 * @param {number} statusCode HTTP status code.
 * @param {Record<string, unknown>} body Response payload object.
 * @returns {string} Serialized HTTP response text.
 * @satisfies REQ-061
 */
function _buildLocalApiHttpResponse(statusCode, body) {
  const jsonPayload = JSON.stringify(body);
  const bodyBytes = new TextEncoder().encode(jsonPayload);
  return [
    `HTTP/1.1 ${statusCode} ${statusCode === 200 ? "OK" : "ERROR"}`,
    "Content-Type: application/json; charset=utf-8",
    `Content-Length: ${bodyBytes.length}`,
    "Connection: close",
    "",
    jsonPayload,
  ].join("\r\n");
}

/**
 * @brief Parse one HTTP request line/body pair from raw socket text.
 * @details Extracts method, path, and optional JSON body from first read chunk.
 * Time complexity: O(N), where N is request text length.
 * Space complexity: O(N).
 * @param {string} requestText Decoded HTTP request text.
 * @returns {{method: string, path: string, body: Record<string, unknown> | null}} Parsed request envelope.
 * @throws {Error} If method/path/body cannot be parsed.
 * @satisfies REQ-061
 */
function _parseLocalApiHttpRequest(requestText) {
  const [head, bodyText] = requestText.split("\r\n\r\n", 2);
  const lines = head.split("\r\n");
  const requestLine = lines[0] ?? "";
  const match = requestLine.match(/^([A-Z]+)\s+([^\s]+)\s+HTTP\/1\.[01]$/);
  if (!match) {
    throw new Error("Invalid HTTP request line");
  }
  const method = match[1];
  const path = match[2];
  let body = null;
  if (bodyText && bodyText.trim()) {
    body = JSON.parse(bodyText);
  }
  return {
    method,
    path,
    body,
  };
}

/**
 * @brief Dispatch localhost HTTP request to primary/debug API handlers.
 * @details Maps route path/method to existing internal API builders and preserves
 * debug gate semantics for debug endpoints.
 * Time complexity: O(C), where C is selected handler complexity.
 * Space complexity: O(C), where C is handler payload size.
 * @param {string} method HTTP method token.
 * @param {string} path HTTP path token.
 * @param {Record<string, unknown> | null} body Parsed request body.
 * @returns {Promise<{statusCode: number, body: Record<string, unknown>}>} Response envelope.
 * @satisfies REQ-061
 */
async function _dispatchLocalApiHttpRequest(method, path, body) {
  if (method === "GET" && path === "/api/main/snapshot") {
    return {
      statusCode: 200,
      body: {
        ok: true,
        snapshot: _buildMainApiSnapshot(),
      },
    };
  }

  if (method === "GET" && path === "/debug/api/describe") {
    const response = _buildDebugDescribeResponse();
    return {
      statusCode: response.ok ? 200 : 403,
      body: response,
    };
  }

  if (method === "POST" && path === "/debug/api/execute") {
    const response = await _buildDebugExecuteResponse(body ?? {});
    return {
      statusCode: response.ok ? 200 : (response.code === "DEBUG_API_DISABLED" ? 403 : 400),
      body: response,
    };
  }

  return {
    statusCode: 404,
    body: {
      ok: false,
      error: "Unsupported localhost API route",
    },
  };
}

/**
 * @brief Process one accepted localhost TCP client request.
 * @details Reads one HTTP request chunk, dispatches API response, writes JSON
 * envelope, and closes client socket.
 * Time complexity: O(N + C), where N=request bytes and C=handler complexity.
 * Space complexity: O(N + C).
 * @param {number} clientSocketId Accepted client socket id.
 * @returns {Promise<void>} Completion promise.
 * @satisfies REQ-061
 */
async function _handleLocalApiClient(clientSocketId) {
  try {
    const recvInfo = await _readTcpClientChunk(clientSocketId);
    if (recvInfo.resultCode <= 0 || !recvInfo.data) {
      return;
    }
    const requestText = new TextDecoder().decode(new Uint8Array(recvInfo.data));
    const request = _parseLocalApiHttpRequest(requestText);
    const response = await _dispatchLocalApiHttpRequest(request.method, request.path, request.body);
    await _writeTcpClientPayload(
      clientSocketId,
      _buildLocalApiHttpResponse(response.statusCode, response.body)
    );
  } catch (error) {
    await _writeTcpClientPayload(
      clientSocketId,
      _buildLocalApiHttpResponse(400, { ok: false, error: String(error?.message ?? error) })
    );
  } finally {
    _closeTcpClientSocket(clientSocketId);
  }
}

/**
 * @brief Run accept loop for localhost API listener.
 * @details Continuously accepts client sockets and dispatches request handlers
 * until listener socket is closed or replaced.
 * Time complexity: O(K), where K is accepted connection count.
 * Space complexity: O(1) plus per-request handler memory.
 * @returns {Promise<void>} Completion promise.
 * @satisfies REQ-060
 * @satisfies REQ-061
 */
async function _runLocalApiAcceptLoop() {
  if (localApiAcceptLoopRunning || !Number.isInteger(localApiServerSocketId)) {
    return;
  }
  localApiAcceptLoopRunning = true;
  try {
    while (Number.isInteger(localApiServerSocketId)) {
      const acceptInfo = await _acceptTcpClient(localApiServerSocketId);
      if (acceptInfo.resultCode < 0 || acceptInfo.clientSocketId < 0) {
        if (!Number.isInteger(localApiServerSocketId)) {
          break;
        }
        continue;
      }
      void _handleLocalApiClient(acceptInfo.clientSocketId).catch((error) => {
        logger.error("localhost-api-client-failure", {
          error: String(error?.message ?? error),
        });
      });
    }
  } finally {
    localApiAcceptLoopRunning = false;
  }
}

/**
 * @brief Start localhost API listener on default or descending fallback port.
 * @details Probes port `32767` first, then decrements port one-by-one until
 * first successful bind to `127.0.0.1`.
 * Time complexity: O(P), where P is attempted port count.
 * Space complexity: O(1).
 * @returns {Promise<void>} Completion promise.
 * @throws {Error} If no candidate port can be bound.
 * @satisfies REQ-060
 */
async function _startLocalApiListener() {
  if (Number.isInteger(localApiServerSocketId)) {
    return;
  }
  if (!_localApiTransportSupported()) {
    logger.error("localhost-api-transport-unsupported", {
      host: LOCAL_API_LISTEN_HOST,
      default_port: LOCAL_API_DEFAULT_PORT,
    });
    return;
  }

  for (let port = LOCAL_API_DEFAULT_PORT; port >= LOCAL_API_MIN_PORT; port -= 1) {
    const socketId = await _createTcpServerSocket();
    const resultCode = await _listenTcpServerSocket(socketId, port);
    if (resultCode >= 0) {
      localApiServerSocketId = socketId;
      localApiBoundPort = port;
      logger.info("localhost-api-listening", {
        host: LOCAL_API_LISTEN_HOST,
        port: localApiBoundPort,
      });
      void _runLocalApiAcceptLoop().catch((error) => {
        logger.error("localhost-api-accept-loop-failure", {
          error: String(error?.message ?? error),
        });
      });
      return;
    }
    _closeTcpServerSocket(socketId);
  }

  throw new Error("Failed to bind localhost API listener on descending fallback range");
}

/**
 * @brief Apply successful provider refresh payload.
 * @param {string} provider Provider key.
 * @param {Record<string, unknown>} payload Parsed provider payload.
 * @returns {void}
 */
function _applyProviderSuccess(provider, payload) {
  runtimeState.providers[provider] = {
    ...runtimeState.providers[provider],
    ...payload,
    error: null,
    last_success_at: new Date().toISOString(),
  };
}

/**
 * @brief Apply provider refresh failure while preserving last successful windows.
 * @param {string} provider Provider key.
 * @param {Error} error Failure object.
 * @returns {void}
 */
function _applyProviderFailure(provider, error) {
  runtimeState.providers[provider] = {
    ...runtimeState.providers[provider],
    error: String(error?.message ?? error),
    last_failure_at: new Date().toISOString(),
  };
}

/**
 * @brief Execute one ordered refresh cycle across all provider pages.
 * @details Preserves successful state on errors and emits debug logs for each step.
 * @param {string} trigger Refresh trigger source.
 * @returns {Promise<void>} Completion promise.
 */
async function _refreshAllProviders(trigger) {
  if (refreshInFlight) {
    logger.debug("refresh-skipped-lock", { trigger });
    return refreshInFlight;
  }

  refreshInFlight = (async () => {
    const startedAt = Date.now();
    runtimeState.last_cycle_status = "running";
    runtimeState.last_error = null;

    logger.info("refresh-cycle-start", {
      trigger,
      provider_fetch_sequence: PROVIDER_FETCH_SEQUENCE,
    });

    try {
      const claudeHtml = await _fetchHtml(PROVIDER_FETCH_SEQUENCE[0]);
      const claudePayload = parseClaudeUsageHtml(claudeHtml);
      _assertProviderPayloadUsable("claude", claudePayload);
      _applyProviderSuccess("claude", claudePayload);
      logger.debug("provider-refresh-success", {
        provider: "claude",
        parser_signal_counts: claudePayload?.parser?.signal_counts ?? {},
      });
    } catch (error) {
      _applyProviderFailure("claude", error);
      logger.error("provider-refresh-failure", {
        provider: "claude",
        error: String(error?.message ?? error),
      });
    }

    try {
      const codexHtml = await _fetchHtml(PROVIDER_FETCH_SEQUENCE[1]);
      const codexPayload = parseCodexUsageHtml(codexHtml);
      _assertProviderPayloadUsable("codex", codexPayload);
      _applyProviderSuccess("codex", codexPayload);
      logger.debug("provider-refresh-success", {
        provider: "codex",
        parser_signal_counts: codexPayload?.parser?.signal_counts ?? {},
      });
    } catch (error) {
      _applyProviderFailure("codex", error);
      logger.error("provider-refresh-failure", {
        provider: "codex",
        error: String(error?.message ?? error),
      });
    }

    try {
      const copilotFeaturesHtml = await _fetchHtml(PROVIDER_FETCH_SEQUENCE[2]);
      const copilotPremiumHtml = await _fetchHtml(PROVIDER_FETCH_SEQUENCE[3]);
      const copilotFeaturesPayload = parseCopilotFeaturesHtml(copilotFeaturesHtml);
      const copilotPremiumPayload = parseCopilotPremiumHtml(copilotPremiumHtml);
      const mergedCopilotPayload = mergeCopilotPayloads(copilotFeaturesPayload, copilotPremiumPayload);
      _assertProviderPayloadUsable("copilot", mergedCopilotPayload);
      _applyProviderSuccess("copilot", mergedCopilotPayload);
      logger.debug("provider-refresh-success", {
        provider: "copilot",
        parser_signal_counts: mergedCopilotPayload?.parser?.signal_counts ?? {},
      });
    } catch (error) {
      _applyProviderFailure("copilot", error);
      logger.error("provider-refresh-failure", {
        provider: "copilot",
        error: String(error?.message ?? error),
      });
    }

    runtimeState.updated_at = new Date().toISOString();
    runtimeState.cycle_counter += 1;

    const providerErrors = ["claude", "codex", "copilot"]
      .map((provider) => runtimeState.providers[provider]?.error)
      .filter((value) => Boolean(value));

    if (providerErrors.length > 0) {
      runtimeState.last_cycle_status = "partial_error";
      runtimeState.last_error = providerErrors.join(" | ");
    } else {
      runtimeState.last_cycle_status = "ok";
      runtimeState.last_error = null;
    }

    await _persistState();

    logger.info("refresh-cycle-finished", {
      trigger,
      duration_ms: Date.now() - startedAt,
      status: runtimeState.last_cycle_status,
      cycle_counter: runtimeState.cycle_counter,
    });

    await chrome.runtime.sendMessage({
      type: "usage.updated",
      snapshot: _buildMainApiSnapshot(),
    }).catch(() => {
      // No popup listeners available.
    });
  })();

  try {
    await refreshInFlight;
  } finally {
    refreshInFlight = null;
  }
}

/**
 * @brief Initialize scheduler and persisted state for service-worker lifecycle.
 * @details Restores persisted runtime/debug state, executes one immediate refresh
 * cycle, starts localhost API listener, and then schedules recurring refresh alarms.
 * @param {string} trigger Initialization trigger label.
 * @returns {Promise<void>} Completion promise.
 * @satisfies REQ-043
 * @satisfies REQ-060
 */
async function _initializeRuntime(trigger) {
  await _loadPersistedState();
  await _loadDebugAccessState();
  await _startLocalApiListener();
  await _refreshAllProviders(trigger);
  await _scheduleRefreshAlarm();
}

/**
 * @brief Handle incoming runtime messages from popup/UI contexts.
 * @details Supports state retrieval, manual refresh, debug log operations, and
 * refresh-interval override updates.
 * @param {Record<string, unknown>} message Message payload.
 * @param {(response: Record<string, unknown>) => void} sendResponse Response callback.
 * @returns {Promise<void>} Completion promise.
 */
async function _handleMessage(message, sendResponse) {
  if (!message || typeof message !== "object") {
    sendResponse({ ok: false, error: "Invalid message payload" });
    return;
  }

  if (message.type === "api.main.snapshot") {
    sendResponse({
      ok: true,
      snapshot: _buildMainApiSnapshot(),
    });
    return;
  }

  if (message.type === "usage.get_state") {
    sendResponse({
      ok: true,
      state: _cloneState(),
      snapshot: _buildMainApiSnapshot(),
    });
    return;
  }

  if (message.type === "usage.refresh_now") {
    await _refreshAllProviders("manual");
    sendResponse({
      ok: true,
      state: _cloneState(),
      snapshot: _buildMainApiSnapshot(),
    });
    return;
  }

  if (message.type === "config.debug_api.get") {
    const persisted = _getSessionStorageArea() !== null;
    sendResponse({
      ok: true,
      debug_api_enabled: debugApiEnabled,
      persisted,
    });
    return;
  }

  if (message.type === "config.debug_api.set") {
    if (typeof message.enabled !== "boolean") {
      sendResponse({
        ok: false,
        error: "config.debug_api.set requires boolean enabled",
      });
      return;
    }
    debugApiEnabled = message.enabled;
    const persisted = await _persistDebugAccessState(debugApiEnabled);
    logger.info("debug-access-updated", {
      enabled: debugApiEnabled,
      persisted,
    });
    sendResponse({
      ok: true,
      debug_api_enabled: debugApiEnabled,
      persisted,
    });
    return;
  }

  /**
   * @brief Set refresh interval override (always available, not debug-gated).
   * @satisfies REQ-057
   * @satisfies CTN-008
   * @satisfies CTN-016
   */
  if (message.type === "config.refresh_interval.set") {
    const value = Number(message.seconds);
    if (!Number.isFinite(value) || value < 60) {
      sendResponse({ ok: false, error: "Refresh interval must be >= 60 seconds" });
      return;
    }
    await chrome.storage.local.set({ [INTERVAL_OVERRIDE_STORAGE_KEY]: Math.round(value) });
    await _scheduleRefreshAlarm();
    logger.info("refresh-interval-updated", {
      source: "config.refresh_interval.set",
      refresh_interval_seconds: runtimeState.refresh_interval_seconds,
    });
    sendResponse({
      ok: true,
      refresh_interval_seconds: runtimeState.refresh_interval_seconds,
    });
    return;
  }

  if (typeof message.type === "string" && message.type.startsWith("debug.")) {
    const gateFailure = _getDebugGateFailure();
    if (gateFailure) {
      sendResponse(gateFailure);
      return;
    }
  }

  if (message.type === "debug.api.describe") {
    sendResponse(_buildDebugDescribeResponse());
    return;
  }

  if (message.type === "debug.api.execute") {
    sendResponse(await _buildDebugExecuteResponse(message));
    return;
  }

  if (message.type === "debug.get_logs") {
    const logs = await readDebugRecords();
    sendResponse({ ok: true, logs });
    return;
  }

  if (message.type === "debug.clear_logs") {
    await clearDebugRecords();
    sendResponse({ ok: true });
    return;
  }

  if (message.type === "debug.export_bundle") {
    const bundle = await buildDebugBundle(_cloneState());
    sendResponse({ ok: true, bundle });
    return;
  }

  if (message.type === "debug.set_refresh_interval") {
    const value = Number(message.seconds);
    if (!Number.isFinite(value) || value < 60) {
      sendResponse({ ok: false, error: "Refresh interval must be >= 60 seconds" });
      return;
    }
    await chrome.storage.local.set({ [INTERVAL_OVERRIDE_STORAGE_KEY]: Math.round(value) });
    await _scheduleRefreshAlarm();
    sendResponse({
      ok: true,
      refresh_interval_seconds: runtimeState.refresh_interval_seconds,
    });
    return;
  }

  sendResponse({ ok: false, error: "Unsupported message type" });
}

if (typeof chrome !== "undefined" && chrome?.runtime && chrome?.alarms) {
  chrome.runtime.onInstalled.addListener(() => {
    void _initializeRuntime("install").catch((error) => {
      logger.error("runtime-init-failure", { trigger: "install", error: String(error) });
    });
  });

  chrome.runtime.onStartup.addListener(() => {
    void _initializeRuntime("startup").catch((error) => {
      logger.error("runtime-init-failure", { trigger: "startup", error: String(error) });
    });
  });

  chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name !== REFRESH_ALARM_NAME) {
      return;
    }
    void _refreshAllProviders("alarm").catch((error) => {
      logger.error("refresh-alarm-failure", { error: String(error) });
    });
  });

  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    void _handleMessage(message, sendResponse).catch((error) => {
      logger.error("message-handler-failure", {
        type: message?.type ?? null,
        error: String(error?.message ?? error),
      });
      sendResponse({ ok: false, error: String(error?.message ?? error) });
    });
    return true;
  });

  void _initializeRuntime("service_worker_bootstrap").catch((error) => {
    logger.error("runtime-init-failure", { trigger: "service_worker_bootstrap", error: String(error) });
  });
}
