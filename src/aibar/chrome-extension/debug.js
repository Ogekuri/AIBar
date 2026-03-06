/**
 * @file debug.js
 * @brief Structured debug instrumentation for AIBar Chrome extension runtime.
 * @details Provides console logging, persisted ring-buffer logging in chrome.storage.local,
 * and debug-bundle utilities used by background and popup execution units.
 * @satisfies CTN-011
 * @satisfies REQ-044
 * @satisfies REQ-045
 */

/** @brief Storage key containing persisted debug records. */
export const DEBUG_LOG_STORAGE_KEY = "aibar.debug.logs";

/** @brief Maximum persisted debug records retained in storage. */
export const DEBUG_LOG_MAX_RECORDS = 600;

/** @brief Maximum serialized string length per persisted value. */
const DEBUG_VALUE_MAX_LENGTH = 2048;

/** @brief Maximum recursion depth allowed for debug-value cloning. */
const DEBUG_CLONE_DEPTH_LIMIT = 3;

/**
 * @brief Produce bounded serialization-safe values for persisted logging.
 * @details Recursively clones primitive/object inputs with explicit depth and collection
 * size limits to prevent storage exhaustion and cyclic-reference crashes.
 * Time complexity: O(N) on traversed properties up to bounded depth.
 * Space complexity: O(N) on cloned projection size.
 * @param {unknown} value Input value.
 * @param {number} depth Current recursion depth.
 * @returns {unknown} Serialization-safe bounded value.
 */
function _cloneDebugValue(value, depth = 0) {
  if (value === null || value === undefined) {
    return value;
  }
  if (typeof value === "string") {
    return value.length <= DEBUG_VALUE_MAX_LENGTH
      ? value
      : `${value.slice(0, DEBUG_VALUE_MAX_LENGTH)}...[truncated]`;
  }
  if (typeof value === "number" || typeof value === "boolean") {
    return value;
  }
  if (depth >= DEBUG_CLONE_DEPTH_LIMIT) {
    return "[depth-limit]";
  }
  if (Array.isArray(value)) {
    return value.slice(0, 25).map((item) => _cloneDebugValue(item, depth + 1));
  }
  if (value instanceof Date) {
    return value.toISOString();
  }
  if (typeof value === "object") {
    const output = {};
    for (const [key, nested] of Object.entries(value).slice(0, 40)) {
      output[key] = _cloneDebugValue(nested, depth + 1);
    }
    return output;
  }
  return String(value);
}

/**
 * @brief Persist one debug record into storage ring buffer.
 * @details Appends a single record under DEBUG_LOG_STORAGE_KEY and truncates
 * older records to DEBUG_LOG_MAX_RECORDS to keep bounded storage usage.
 * Time complexity: O(N) on retained log count.
 * Space complexity: O(N) for stored log array.
 * @param {Record<string, unknown>} record Structured log record.
 * @returns {Promise<void>} Completion promise.
 */
export async function appendDebugRecord(record) {
  const storageData = await chrome.storage.local.get(DEBUG_LOG_STORAGE_KEY);
  const existing = Array.isArray(storageData[DEBUG_LOG_STORAGE_KEY])
    ? storageData[DEBUG_LOG_STORAGE_KEY]
    : [];
  const next = [...existing, record].slice(-DEBUG_LOG_MAX_RECORDS);
  await chrome.storage.local.set({ [DEBUG_LOG_STORAGE_KEY]: next });
}

/**
 * @brief Create scoped logger with console + persisted logging sinks.
 * @details Each log method emits to the browser console and asynchronously appends
 * one structured record to storage while preserving refresh/runtime execution flow.
 * @param {string} scope Logger scope label.
 * @returns {{debug: Function, info: Function, warn: Function, error: Function}} Scoped logger API.
 */
export function createLogger(scope) {
  /**
   * @brief Emit one structured log event.
   * @details Normalizes payload values through bounded cloning and appends one
   * timestamped record to storage while mirroring output in console.
   * @param {"debug"|"info"|"warn"|"error"} level Log level.
   * @param {string} event Event identifier.
   * @param {Record<string, unknown>} details Structured context payload.
   * @returns {Promise<void>} Completion promise.
   */
  async function write(level, event, details = {}) {
    const timestamp = new Date().toISOString();
    const safeDetails = _cloneDebugValue(details);
    const record = {
      timestamp,
      level,
      scope,
      event,
      details: safeDetails,
    };

    const prefix = `[AIBar:${scope}] ${event}`;
    const consoleMethod = typeof console[level] === "function"
      ? console[level].bind(console)
      : console.log.bind(console);
    consoleMethod(prefix, safeDetails);

    await appendDebugRecord(record);
  }

  return {
    /** @brief Emit DEBUG-level event. */
    debug(event, details = {}) {
      void write("debug", event, details).catch((error) => {
        console.error("[AIBar:debug] appendDebugRecord failed", error);
      });
    },
    /** @brief Emit INFO-level event. */
    info(event, details = {}) {
      void write("info", event, details).catch((error) => {
        console.error("[AIBar:debug] appendDebugRecord failed", error);
      });
    },
    /** @brief Emit WARN-level event. */
    warn(event, details = {}) {
      void write("warn", event, details).catch((error) => {
        console.error("[AIBar:debug] appendDebugRecord failed", error);
      });
    },
    /** @brief Emit ERROR-level event. */
    error(event, details = {}) {
      void write("error", event, details).catch((error) => {
        console.error("[AIBar:debug] appendDebugRecord failed", error);
      });
    },
  };
}

/**
 * @brief Load persisted debug records from storage.
 * @details Returns records as-is from storage ring buffer key; returns empty array
 * when no records are available.
 * @returns {Promise<Array<Record<string, unknown>>>} Persisted records.
 */
export async function readDebugRecords() {
  const storageData = await chrome.storage.local.get(DEBUG_LOG_STORAGE_KEY);
  const records = storageData[DEBUG_LOG_STORAGE_KEY];
  return Array.isArray(records) ? records : [];
}

/**
 * @brief Remove all persisted debug records.
 * @details Deletes the storage key used for ring-buffer logs.
 * @returns {Promise<void>} Completion promise.
 */
export async function clearDebugRecords() {
  await chrome.storage.local.remove(DEBUG_LOG_STORAGE_KEY);
}

/**
 * @brief Build one export-ready debug bundle from state and records.
 * @details Produces deterministic JSON payload used by popup export action.
 * @param {Record<string, unknown>} state Current extension state snapshot.
 * @returns {Promise<Record<string, unknown>>} Export payload.
 */
export async function buildDebugBundle(state) {
  const logs = await readDebugRecords();
  return {
    exported_at: new Date().toISOString(),
    state: _cloneDebugValue(state),
    logs,
  };
}
