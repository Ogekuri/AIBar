/**
 * @file popup.mjs
 * @brief Popup controller for rendering provider tabs and debug actions.
 * @details Consumes normalized state emitted by background service-worker and renders
 * GNOME-parity card/progress visuals for Claude, Copilot, and Codex providers.
 * @satisfies REQ-038
 * @satisfies REQ-039
 * @satisfies REQ-044
 */

import { createLogger } from "./debug.mjs";

/** @brief Popup logger instance. */
const logger = createLogger("popup");

/** @brief Supported provider tab order. */
const PROVIDER_TABS = ["claude", "copilot", "codex"];

/** @brief Window render ordering by provider. */
const PROVIDER_WINDOWS = {
  claude: ["5h", "7d"],
  copilot: ["30d"],
  codex: ["5h", "7d"],
};

/** @brief Last received runtime state snapshot. */
let currentState = null;

/** @brief Active provider tab name. */
let activeProvider = "claude";

/** @brief DOM cache for popup controls. */
const dom = {
  refreshButton: document.getElementById("refreshButton"),
  exportButton: document.getElementById("exportButton"),
  clearLogsButton: document.getElementById("clearLogsButton"),
  intervalInput: document.getElementById("intervalInput"),
  setIntervalButton: document.getElementById("setIntervalButton"),
  updatedLabel: document.getElementById("updatedLabel"),
  statusLabel: document.getElementById("statusLabel"),
  tabButtons: Array.from(document.querySelectorAll("[data-provider]")),
  cards: {
    claude: document.getElementById("card-claude"),
    copilot: document.getElementById("card-copilot"),
    codex: document.getElementById("card-codex"),
  },
};

/**
 * @brief Resolve CSS class for progress severity by percentage.
 * @param {number | null} usagePercent Usage percentage value.
 * @returns {string} CSS class name.
 */
function _progressClass(usagePercent) {
  if (usagePercent === null || !Number.isFinite(usagePercent)) {
    return "aibar-progress-none";
  }
  if (usagePercent < 50) {
    return "aibar-progress-ok";
  }
  if (usagePercent < 80) {
    return "aibar-progress-warning";
  }
  return "aibar-progress-danger";
}

/**
 * @brief Format percentage for UI display.
 * @param {number | null} value Percentage value.
 * @returns {string} UI label.
 */
function _formatPercent(value) {
  if (value === null || !Number.isFinite(value)) {
    return "n/a";
  }
  return `${value.toFixed(1)}%`;
}

/**
 * @brief Format numeric metric for UI display.
 * @param {number | null} value Numeric metric.
 * @returns {string} UI label.
 */
function _formatMetric(value) {
  if (value === null || !Number.isFinite(value)) {
    return "n/a";
  }
  return value.toFixed(1);
}

/**
 * @brief Format reset timestamp into compact relative text.
 * @param {string | null | undefined} resetAt ISO timestamp.
 * @returns {string} Relative-time display label.
 */
function _formatReset(resetAt) {
  if (!resetAt || typeof resetAt !== "string") {
    return "Reset in: n/a";
  }
  const target = new Date(resetAt);
  if (Number.isNaN(target.getTime())) {
    return "Reset in: n/a";
  }

  const deltaMs = target.getTime() - Date.now();
  if (deltaMs <= 0) {
    return "Reset in: now";
  }

  const totalMinutes = Math.floor(deltaMs / 60000);
  const days = Math.floor(totalMinutes / (60 * 24));
  const hours = Math.floor((totalMinutes % (60 * 24)) / 60);
  const minutes = totalMinutes % 60;

  if (days > 0) {
    return `Reset in: ${days}d ${hours}h ${minutes}m`;
  }
  return `Reset in: ${hours}h ${minutes}m`;
}

/**
 * @brief Build one window progress-bar row element.
 * @param {string} windowKey Window key (`5h`, `7d`, `30d`).
 * @param {Record<string, number | string | null> | null} windowData Window data object.
 * @returns {HTMLElement} Rendered row container.
 */
function _buildWindowRow(windowKey, windowData) {
  const usagePercent = Number(windowData?.usage_percent);
  const remaining = Number(windowData?.remaining);
  const limit = Number(windowData?.limit);
  const resetAt = typeof windowData?.reset_at === "string" ? windowData.reset_at : null;

  const row = document.createElement("div");
  row.className = "aibar-window-bar";

  const line = document.createElement("div");
  line.className = "aibar-window-row";

  const label = document.createElement("span");
  label.className = "aibar-window-label";
  label.textContent = windowKey;

  const bg = document.createElement("span");
  bg.className = "aibar-progress-bg";

  const fill = document.createElement("span");
  fill.className = `aibar-progress-fill ${_progressClass(Number.isFinite(usagePercent) ? usagePercent : null)}`;
  fill.style.width = Number.isFinite(usagePercent) ? `${Math.max(0, Math.min(100, usagePercent))}%` : "0%";
  bg.appendChild(fill);

  const pct = document.createElement("span");
  pct.className = "aibar-window-pct";
  pct.textContent = _formatPercent(Number.isFinite(usagePercent) ? usagePercent : null);

  line.append(label, bg, pct);
  row.appendChild(line);

  const resetLabel = document.createElement("div");
  resetLabel.className = "aibar-reset-label";
  resetLabel.textContent = _formatReset(resetAt);
  row.appendChild(resetLabel);

  const quotaLabel = document.createElement("div");
  quotaLabel.className = "aibar-stat";
  quotaLabel.textContent = `Remaining credits: ${_formatMetric(Number.isFinite(remaining) ? remaining : null)} / ${_formatMetric(
    Number.isFinite(limit) ? limit : null
  )}`;
  row.appendChild(quotaLabel);

  return row;
}

/**
 * @brief Render one provider card from current state.
 * @param {string} provider Provider key.
 * @returns {void}
 */
function _renderProviderCard(provider) {
  const card = dom.cards[provider];
  if (!card) {
    return;
  }

  const providerState = currentState?.providers?.[provider] ?? null;
  card.textContent = "";

  if (!providerState) {
    const empty = document.createElement("div");
    empty.className = "aibar-card-empty";
    empty.textContent = "No data available.";
    card.appendChild(empty);
    return;
  }

  const windowsContainer = document.createElement("div");
  windowsContainer.className = "aibar-window-bars";

  for (const windowKey of PROVIDER_WINDOWS[provider]) {
    const windowData = providerState.windows?.[windowKey] ?? null;
    windowsContainer.appendChild(_buildWindowRow(windowKey, windowData));
  }
  card.appendChild(windowsContainer);

  if (providerState.error) {
    const error = document.createElement("div");
    error.className = "aibar-error";
    error.textContent = `Error: ${providerState.error}`;
    card.appendChild(error);
  }
}

/**
 * @brief Render popup-wide status/footer labels and all provider cards.
 * @returns {void}
 */
function _renderState() {
  PROVIDER_TABS.forEach((provider) => _renderProviderCard(provider));

  const updatedAt = currentState?.updated_at;
  if (updatedAt) {
    const parsed = new Date(updatedAt);
    dom.updatedLabel.textContent = Number.isNaN(parsed.getTime())
      ? "Updated: n/a"
      : `Updated: ${parsed.toLocaleTimeString()}`;
  } else {
    dom.updatedLabel.textContent = "Updated: n/a";
  }

  dom.statusLabel.textContent = currentState?.last_cycle_status ?? "idle";
  dom.intervalInput.value = String(currentState?.refresh_interval_seconds ?? 180);
}

/**
 * @brief Apply active tab classes and card visibility state.
 * @param {string} provider Target provider.
 * @returns {void}
 */
function _setActiveProvider(provider) {
  activeProvider = provider;

  for (const button of dom.tabButtons) {
    const candidate = button.dataset.provider;
    const isActive = candidate === provider;
    button.className = isActive ? `aibar-tab-active aibar-tab-active-${candidate}` : "aibar-tab";
  }

  for (const candidate of PROVIDER_TABS) {
    const card = dom.cards[candidate];
    if (!card) {
      continue;
    }
    card.classList.toggle("aibar-card-visible", candidate === provider);
  }
}

/**
 * @brief Request latest state from background service worker.
 * @returns {Promise<void>} Completion promise.
 */
async function _requestState() {
  const response = await chrome.runtime.sendMessage({ type: "usage.get_state" });
  if (!response?.ok) {
    throw new Error(response?.error ?? "usage.get_state failed");
  }
  currentState = response.state;
  _renderState();
}

/**
 * @brief Trigger manual refresh request.
 * @returns {Promise<void>} Completion promise.
 */
async function _refreshNow() {
  const response = await chrome.runtime.sendMessage({ type: "usage.refresh_now" });
  if (!response?.ok) {
    throw new Error(response?.error ?? "usage.refresh_now failed");
  }
  currentState = response.state;
  _renderState();
}

/**
 * @brief Export debug bundle as downloadable JSON file.
 * @returns {Promise<void>} Completion promise.
 */
async function _exportDebugBundle() {
  const response = await chrome.runtime.sendMessage({ type: "debug.export_bundle" });
  if (!response?.ok) {
    throw new Error(response?.error ?? "debug.export_bundle failed");
  }

  const payload = JSON.stringify(response.bundle, null, 2);
  const blob = new Blob([payload], { type: "application/json" });
  const blobUrl = URL.createObjectURL(blob);

  const anchor = document.createElement("a");
  anchor.href = blobUrl;
  anchor.download = `aibar-debug-${Date.now()}.json`;
  anchor.click();

  URL.revokeObjectURL(blobUrl);
}

/**
 * @brief Clear persisted debug logs.
 * @returns {Promise<void>} Completion promise.
 */
async function _clearLogs() {
  const response = await chrome.runtime.sendMessage({ type: "debug.clear_logs" });
  if (!response?.ok) {
    throw new Error(response?.error ?? "debug.clear_logs failed");
  }
}

/**
 * @brief Apply refresh interval override from popup input.
 * @returns {Promise<void>} Completion promise.
 */
async function _setIntervalOverride() {
  const seconds = Number(dom.intervalInput.value);
  const response = await chrome.runtime.sendMessage({
    type: "debug.set_refresh_interval",
    seconds,
  });
  if (!response?.ok) {
    throw new Error(response?.error ?? "debug.set_refresh_interval failed");
  }
  await _requestState();
}

/**
 * @brief Register popup event handlers.
 * @returns {void}
 */
function _wireUiEvents() {
  dom.refreshButton.addEventListener("click", () => {
    void _refreshNow().catch((error) => {
      logger.error("manual-refresh-failure", { error: String(error) });
    });
  });

  dom.exportButton.addEventListener("click", () => {
    void _exportDebugBundle().catch((error) => {
      logger.error("export-debug-failure", { error: String(error) });
    });
  });

  dom.clearLogsButton.addEventListener("click", () => {
    void _clearLogs().catch((error) => {
      logger.error("clear-logs-failure", { error: String(error) });
    });
  });

  dom.setIntervalButton.addEventListener("click", () => {
    void _setIntervalOverride().catch((error) => {
      logger.error("set-interval-failure", { error: String(error) });
    });
  });

  for (const button of dom.tabButtons) {
    button.addEventListener("click", () => {
      const provider = button.dataset.provider;
      if (provider && PROVIDER_TABS.includes(provider)) {
        _setActiveProvider(provider);
      }
    });
  }
}

chrome.runtime.onMessage.addListener((message) => {
  if (message?.type !== "usage.updated") {
    return;
  }
  currentState = message.state;
  _renderState();
});

_wireUiEvents();
_setActiveProvider(activeProvider);
void _requestState().catch((error) => {
  logger.error("initial-state-load-failure", { error: String(error) });
});
