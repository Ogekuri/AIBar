/**
 * @file background.mjs
 * @brief Chrome extension service-worker runtime for autonomous provider refresh.
 * @details Executes ordered provider page downloads, parser normalization, state
 * persistence, and debug instrumentation on a recurring alarm interval.
 * @satisfies PRJ-009
 * @satisfies PRJ-010
 * @satisfies CTN-008
 * @satisfies CTN-009
 * @satisfies REQ-043
 * @satisfies REQ-045
 */

import {
  buildDebugBundle,
  clearDebugRecords,
  createLogger,
  readDebugRecords,
} from "./debug.mjs";
import {
  mergeCopilotPayloads,
  parseClaudeUsageHtml,
  parseCodexUsageHtml,
  parseCopilotFeaturesHtml,
  parseCopilotPremiumHtml,
} from "./parsers.mjs";

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

/**
 * @brief Deep clone state into message-safe payload.
 * @returns {Record<string, unknown>} Cloned state snapshot.
 */
function _cloneState() {
  return JSON.parse(JSON.stringify(runtimeState));
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
      state: _cloneState(),
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

  if (message.type === "usage.get_state") {
    sendResponse({ ok: true, state: _cloneState() });
    return;
  }

  if (message.type === "usage.refresh_now") {
    await _refreshAllProviders("manual");
    sendResponse({ ok: true, state: _cloneState() });
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
    sendResponse({ ok: true, refresh_interval_seconds: runtimeState.refresh_interval_seconds });
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
