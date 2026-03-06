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
  codex: ["5h", "7d"],
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
 * @details Uses non-persistent in-memory flag and throws deterministic error to
 * ensure all debug message routes fail uniformly when disabled.
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
 * @brief Persist current runtime state to extension storage.
 * @returns {Promise<void>} Completion promise.
 */
async function _persistState() {
  await chrome.storage.local.set({ [STATE_STORAGE_KEY]: _cloneState() });
}

/**
 * @brief Read configured refresh interval with override support.
 * @details Uses hardcoded default REFRESH_INTERVAL_SECONDS and allows optional
 * storage override to support field debugging with shorter/longer cycles.
 * @returns {Promise<number>} Effective interval in seconds.
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
    has_window_tokens: /\b(?:5h|7d|30d)\b/i.test(html),
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
 * @param {string} trigger Initialization trigger label.
 * @returns {Promise<void>} Completion promise.
 */
async function _initializeRuntime(trigger) {
  debugApiEnabled = false;
  await _loadPersistedState();
  await _scheduleRefreshAlarm();
  await _refreshAllProviders(trigger);
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
    sendResponse({
      ok: true,
      debug_api_enabled: debugApiEnabled,
      persisted: false,
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
    logger.info("debug-access-updated", {
      enabled: debugApiEnabled,
      persisted: false,
    });
    sendResponse({
      ok: true,
      debug_api_enabled: debugApiEnabled,
      persisted: false,
    });
    return;
  }

  if (typeof message.type === "string" && message.type.startsWith("debug.")) {
    try {
      _ensureDebugAccessEnabled();
    } catch (error) {
      sendResponse({
        ok: false,
        code: "DEBUG_API_DISABLED",
        error: String(error?.message ?? error),
      });
      return;
    }
  }

  if (message.type === "debug.api.describe") {
    sendResponse({
      ok: true,
      debug_api_enabled: debugApiEnabled,
      api: _describeDebugApi(),
    });
    return;
  }

  if (message.type === "debug.api.execute") {
    const command = typeof message.command === "string" ? message.command.trim() : "";
    if (!command) {
      sendResponse({ ok: false, error: "debug.api.execute requires command string" });
      return;
    }

    const args = message.args && typeof message.args === "object" ? message.args : {};
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
      sendResponse({
        ok: true,
        command,
        debug_api_enabled: debugApiEnabled,
        duration_ms: durationMs,
        result,
      });
    } catch (error) {
      const durationMs = Date.now() - startedAt;
      const messageText = String(error?.message ?? error);
      logger.error("debug-api-command-failure", {
        command,
        duration_ms: durationMs,
        error: messageText,
      });
      sendResponse({
        ok: false,
        command,
        debug_api_enabled: debugApiEnabled,
        duration_ms: durationMs,
        error: messageText,
      });
    }
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
