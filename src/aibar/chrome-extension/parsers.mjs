/**
 * @file parsers.mjs
 * @brief Localization-independent HTML parser primitives for AIBar Chrome extension.
 * @details Extracts quota and progress metrics from provider usage pages by using
 * DOM semantics (`role=progressbar`, numeric attributes, `datetime`, embedded JSON)
 * instead of localized visible labels.
 * @satisfies CTN-010
 * @satisfies REQ-040
 * @satisfies REQ-041
 * @satisfies REQ-042
 */

/** @brief Parser semantic version for debug payloads. */
export const PARSER_VERSION = "2026.03.06";

/** @brief Token regex for window hints. */
const WINDOW_HINT_REGEX = /\b(5h|7d|30d)\b/i;

/** @brief Token regex for numeric fractions. */
const FRACTION_REGEX = /([0-9][0-9\s.,]*)\s*\/\s*([0-9][0-9\s.,]*)/g;

/** @brief Token regex for percentage values. */
const PERCENT_REGEX = /([0-9][0-9\s.,]*)\s*%/g;

/**
 * @brief Parse localized numeric token into a finite number.
 * @details Supports comma/dot decimal formats and thousands separators by
 * deterministic normalization rules; rejects non-finite values.
 * @param {string | number | null | undefined} token Candidate numeric token.
 * @returns {number | null} Parsed finite number or null when invalid.
 */
export function parseLocalizedNumber(token) {
  if (token === null || token === undefined) {
    return null;
  }
  if (typeof token === "number") {
    return Number.isFinite(token) ? token : null;
  }

  const compact = String(token)
    .replace(/\s+/g, "")
    .replace(/[^0-9,.-]/g, "");

  if (!compact || compact === "." || compact === "," || compact === "-") {
    return null;
  }

  let normalized = compact;
  const hasComma = normalized.includes(",");
  const hasDot = normalized.includes(".");

  if (hasComma && hasDot) {
    const commaIndex = normalized.lastIndexOf(",");
    const dotIndex = normalized.lastIndexOf(".");
    if (commaIndex > dotIndex) {
      normalized = normalized.replace(/\./g, "").replace(",", ".");
    } else {
      normalized = normalized.replace(/,/g, "");
    }
  } else if (hasComma) {
    if (/,[0-9]{1,3}$/.test(normalized)) {
      normalized = normalized.replace(",", ".");
    } else {
      normalized = normalized.replace(/,/g, "");
    }
  }

  const value = Number(normalized);
  return Number.isFinite(value) ? value : null;
}

/**
 * @brief Clamp value into inclusive min/max interval.
 * @param {number | null} value Candidate number.
 * @param {number} min Inclusive minimum.
 * @param {number} max Inclusive maximum.
 * @returns {number | null} Clamped value or null.
 */
function _clamp(value, min, max) {
  if (value === null || !Number.isFinite(value)) {
    return null;
  }
  return Math.max(min, Math.min(max, value));
}

/**
 * @brief Parse one HTML tag attribute value.
 * @details Parses quoted/unquoted HTML attributes using regex extraction.
 * @param {string} tagHtml Full tag HTML.
 * @param {string} attributeName Attribute name to extract.
 * @returns {string | null} Attribute value or null.
 */
function _extractAttribute(tagHtml, attributeName) {
  const regex = new RegExp(`${attributeName}\\s*=\\s*(?:\"([^\"]*)\"|'([^']*)'|([^\\s>]+))`, "i");
  const match = tagHtml.match(regex);
  if (!match) {
    return null;
  }
  return match[1] ?? match[2] ?? match[3] ?? null;
}

/**
 * @brief Infer usage window token from local HTML context.
 * @param {string} context Text context around parsed metric element.
 * @returns {string | null} Window hint token (`5h`, `7d`, `30d`) or null.
 */
function _extractWindowHint(context) {
  const match = context.match(WINDOW_HINT_REGEX);
  return match ? match[1].toLowerCase() : null;
}

/**
 * @brief Strip script/style blocks and tags from HTML.
 * @details Produces compact text stream used for fraction/percent extraction.
 * @param {string} html Raw HTML.
 * @returns {string} Plain text approximation.
 */
function _extractPlainText(html) {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/\s+/g, " ")
    .trim();
}

/**
 * @brief Extract progress-bar metrics from semantic HTML attributes.
 * @details Supports both generic tags with `role=progressbar` and `<progress>`
 * elements using `aria-valuenow/max` or `value/max` attributes.
 * @param {string} html Raw HTML.
 * @returns {Array<Record<string, number | string | null>>} Ordered progress-bar records.
 */
function _extractProgressMetrics(html) {
  const metrics = [];

  const progressbarRegex = /<[^>]*role\s*=\s*(?:"progressbar"|'progressbar')[^>]*>/gi;
  let match;
  while ((match = progressbarRegex.exec(html)) !== null) {
    const tag = match[0];
    const context = html.slice(Math.max(0, match.index - 120), Math.min(html.length, match.index + 220));
    const now = parseLocalizedNumber(_extractAttribute(tag, "aria-valuenow"));
    const min = parseLocalizedNumber(_extractAttribute(tag, "aria-valuemin")) ?? 0;
    const max = parseLocalizedNumber(_extractAttribute(tag, "aria-valuemax")) ?? 100;
    const pct = now !== null && max > min ? _clamp(((now - min) / (max - min)) * 100.0, 0, 100) : null;
    metrics.push({
      window_hint: _extractWindowHint(context),
      usage_percent: pct,
      raw_value: now,
      raw_limit: max,
    });
  }

  const htmlProgressRegex = /<progress\b[^>]*>/gi;
  while ((match = htmlProgressRegex.exec(html)) !== null) {
    const tag = match[0];
    const context = html.slice(Math.max(0, match.index - 120), Math.min(html.length, match.index + 220));
    const value = parseLocalizedNumber(_extractAttribute(tag, "value"));
    const max = parseLocalizedNumber(_extractAttribute(tag, "max")) ?? 100;
    const pct = value !== null && max > 0 ? _clamp((value / max) * 100.0, 0, 100) : null;
    metrics.push({
      window_hint: _extractWindowHint(context),
      usage_percent: pct,
      raw_value: value,
      raw_limit: max,
    });
  }

  return metrics;
}

/**
 * @brief Extract numeric fraction candidates from visible text stream.
 * @details Captures raw numeric pairs (`A/B`) that may encode used/limit or
 * remaining/limit values independent from natural-language labels.
 * @param {string} html Raw HTML.
 * @returns {Array<Record<string, number>>} Ordered fraction records.
 */
function _extractFractionCandidates(html) {
  const plainText = _extractPlainText(html);
  const fractions = [];
  let match;
  while ((match = FRACTION_REGEX.exec(plainText)) !== null) {
    const first = parseLocalizedNumber(match[1]);
    const second = parseLocalizedNumber(match[2]);
    if (first !== null && second !== null && second > 0) {
      fractions.push({
        first,
        second,
      });
    }
  }
  return fractions;
}

/**
 * @brief Extract percentage literals from visible text stream.
 * @param {string} html Raw HTML.
 * @returns {Array<number>} Ordered percentage numbers.
 */
function _extractPercentCandidates(html) {
  const plainText = _extractPlainText(html);
  const percentages = [];
  let match;
  while ((match = PERCENT_REGEX.exec(plainText)) !== null) {
    const value = parseLocalizedNumber(match[1]);
    if (value !== null) {
      percentages.push(_clamp(value, 0, 100));
    }
  }
  return percentages;
}

/**
 * @brief Extract ISO-like datetime tokens from markup.
 * @details Reads `datetime="..."` attributes and optional ISO literals in text.
 * @param {string} html Raw HTML.
 * @returns {Array<string>} Ordered datetime candidates in ISO format when parseable.
 */
function _extractDatetimeCandidates(html) {
  const datetimes = [];
  const datetimeRegex = /datetime\s*=\s*(?:"([^"]+)"|'([^']+)')/gi;
  let match;
  while ((match = datetimeRegex.exec(html)) !== null) {
    const token = match[1] ?? match[2] ?? "";
    const parsed = new Date(token);
    if (!Number.isNaN(parsed.getTime())) {
      datetimes.push(parsed.toISOString());
    }
  }
  return datetimes;
}

/**
 * @brief Collect embedded JSON payloads from script tags.
 * @details Parses `application/json`, `application/ld+json`, and `__NEXT_DATA__`
 * scripts into objects for language-agnostic metric extraction.
 * @param {string} html Raw HTML.
 * @returns {Array<unknown>} Parsed JSON roots.
 */
function _extractEmbeddedJsonObjects(html) {
  const objects = [];
  const scriptRegex = /<script[^>]*>([\s\S]*?)<\/script>/gi;
  let match;
  while ((match = scriptRegex.exec(html)) !== null) {
    const scriptTag = match[0];
    const scriptBody = (match[1] ?? "").trim();
    if (!scriptBody) {
      continue;
    }

    const isJsonType = /type\s*=\s*(?:"application\/(?:ld\+)?json"|'application\/(?:ld\+)?json')/i.test(scriptTag);
    const isNextData = /id\s*=\s*(?:"__NEXT_DATA__"|'__NEXT_DATA__')/i.test(scriptTag);
    if (!isJsonType && !isNextData) {
      continue;
    }

    try {
      objects.push(JSON.parse(scriptBody));
    } catch (_error) {
      // Skip malformed script payloads.
    }
  }
  return objects;
}

/**
 * @brief Resolve first numeric value from object keys matching regex list.
 * @param {Record<string, unknown>} obj Object candidate.
 * @param {Array<RegExp>} keyRegexes Key regex matchers.
 * @returns {number | null} First parsed numeric value.
 */
function _pickNumericByKey(obj, keyRegexes) {
  for (const [key, value] of Object.entries(obj)) {
    if (!keyRegexes.some((pattern) => pattern.test(key))) {
      continue;
    }
    const parsed = parseLocalizedNumber(value);
    if (parsed !== null) {
      return parsed;
    }
  }
  return null;
}

/**
 * @brief Resolve first datetime-like value from object keys matching regex list.
 * @param {Record<string, unknown>} obj Object candidate.
 * @param {Array<RegExp>} keyRegexes Key regex matchers.
 * @returns {string | null} ISO timestamp or null.
 */
function _pickDatetimeByKey(obj, keyRegexes) {
  for (const [key, value] of Object.entries(obj)) {
    if (!keyRegexes.some((pattern) => pattern.test(key))) {
      continue;
    }
    if (typeof value !== "string") {
      continue;
    }
    const parsed = new Date(value);
    if (!Number.isNaN(parsed.getTime())) {
      return parsed.toISOString();
    }
  }
  return null;
}

/**
 * @brief Recursively extract metric candidates from parsed JSON roots.
 * @details Uses provider-agnostic key families for quota/usage/reset values and
 * window hints; traversal is bounded by visited-object set.
 * @param {unknown} root Parsed JSON root.
 * @returns {Array<Record<string, number | string | null>>} Candidate metrics.
 */
function _extractJsonMetricCandidates(root) {
  const results = [];
  const visited = new Set();

  /**
   * @brief Depth-first traversal over JSON object graph.
   * @param {unknown} node Current node.
   * @returns {void}
   */
  function walk(node) {
    if (!node || typeof node !== "object") {
      return;
    }
    if (visited.has(node)) {
      return;
    }
    visited.add(node);

    if (Array.isArray(node)) {
      for (const item of node.slice(0, 200)) {
        walk(item);
      }
      return;
    }

    const obj = /** @type {Record<string, unknown>} */ (node);

    const remaining = _pickNumericByKey(obj, [/remain/i, /available/i, /left/i, /balance/i]);
    const limit = _pickNumericByKey(obj, [/limit/i, /quota/i, /allowance/i, /total/i, /max/i]);
    const used = _pickNumericByKey(obj, [/used/i, /consumed/i, /^usage$/i, /count/i]);
    const usagePercent = _pickNumericByKey(obj, [/percent/i, /percentage/i, /utilization/i]);
    const resetAt = _pickDatetimeByKey(obj, [/reset/i, /renew/i, /window_end/i, /expires/i]);

    let windowHint = null;
    for (const value of Object.values(obj)) {
      if (typeof value !== "string") {
        continue;
      }
      const hinted = _extractWindowHint(value);
      if (hinted) {
        windowHint = hinted;
        break;
      }
    }

    if (
      remaining !== null ||
      limit !== null ||
      used !== null ||
      usagePercent !== null ||
      resetAt !== null
    ) {
      results.push({
        window_hint: windowHint,
        remaining,
        limit,
        used,
        usage_percent: usagePercent,
        reset_at: resetAt,
      });
    }

    for (const value of Object.values(obj)) {
      walk(value);
    }
  }

  walk(root);
  return results;
}

/**
 * @brief Select one best-matching candidate by window hint or ordered fallback.
 * @param {Array<Record<string, unknown>>} candidates Candidate list.
 * @param {string} windowKey Target window key.
 * @param {number} index Ordered fallback index.
 * @returns {Record<string, unknown> | null} Selected candidate.
 */
function _pickCandidate(candidates, windowKey, index) {
  const hinted = candidates.find((item) => item.window_hint === windowKey);
  if (hinted) {
    return hinted;
  }
  return candidates[index] ?? null;
}

/**
 * @brief Infer remaining/limit from fraction candidate and usage percentage.
 * @details Chooses interpretation (`used/limit` vs `remaining/limit`) minimizing
 * percentage-distance from known usage value when available.
 * @param {{first: number, second: number}} fraction Fraction candidate.
 * @param {number | null} usagePercent Known usage percentage.
 * @returns {{remaining: number | null, limit: number | null}} Inferred values.
 */
function _inferQuotaFromFraction(fraction, usagePercent) {
  const limit = fraction.second;
  if (!Number.isFinite(limit) || limit <= 0) {
    return { remaining: null, limit: null };
  }

  const usedIfFirst = _clamp((fraction.first / limit) * 100, 0, 100);
  const usedIfComplement = _clamp(((limit - fraction.first) / limit) * 100, 0, 100);

  if (usagePercent === null) {
    return {
      remaining: _clamp(limit - fraction.first, 0, limit),
      limit,
    };
  }

  const firstDistance = Math.abs((usedIfFirst ?? 0) - usagePercent);
  const complementDistance = Math.abs((usedIfComplement ?? 0) - usagePercent);

  if (firstDistance <= complementDistance) {
    return {
      remaining: _clamp(limit - fraction.first, 0, limit),
      limit,
    };
  }

  return {
    remaining: _clamp(fraction.first, 0, limit),
    limit,
  };
}

/**
 * @brief Build one normalized window metrics record.
 * @param {Array<string>} windowKeys Ordered window keys.
 * @param {Array<Record<string, number | string | null>>} progressCandidates Progress candidates.
 * @param {Array<Record<string, number>>} fractionCandidates Fraction candidates.
 * @param {Array<number | null>} percentCandidates Percent candidates.
 * @param {Array<string>} datetimeCandidates Datetime candidates.
 * @param {Array<Record<string, number | string | null>>} jsonCandidates JSON-derived candidates.
 * @returns {Record<string, Record<string, number | string | null>>} Window metrics map.
 */
function _buildWindows(
  windowKeys,
  progressCandidates,
  fractionCandidates,
  percentCandidates,
  datetimeCandidates,
  jsonCandidates
) {
  const windows = {};

  windowKeys.forEach((windowKey, index) => {
    const jsonCandidate = _pickCandidate(jsonCandidates, windowKey, index);
    const progressCandidate = _pickCandidate(progressCandidates, windowKey, index);

    const usagePercent = _clamp(
      parseLocalizedNumber(jsonCandidate?.usage_percent) ??
        parseLocalizedNumber(progressCandidate?.usage_percent) ??
        parseLocalizedNumber(percentCandidates[index] ?? null),
      0,
      100
    );

    const quotaFromFraction = fractionCandidates[index]
      ? _inferQuotaFromFraction(fractionCandidates[index], usagePercent)
      : { remaining: null, limit: null };

    const limit =
      _clamp(parseLocalizedNumber(jsonCandidate?.limit), 0, Number.MAX_SAFE_INTEGER) ??
      quotaFromFraction.limit;

    let remaining =
      _clamp(parseLocalizedNumber(jsonCandidate?.remaining), 0, Number.MAX_SAFE_INTEGER) ??
      quotaFromFraction.remaining;

    const used = _clamp(parseLocalizedNumber(jsonCandidate?.used), 0, Number.MAX_SAFE_INTEGER);
    if (remaining === null && limit !== null && used !== null) {
      remaining = _clamp(limit - used, 0, limit);
    }

    const resetAt =
      (typeof jsonCandidate?.reset_at === "string" ? jsonCandidate.reset_at : null) ??
      datetimeCandidates[index] ??
      null;

    windows[windowKey] = {
      usage_percent: usagePercent,
      remaining,
      limit,
      reset_at: resetAt,
    };
  });

  return windows;
}

/**
 * @brief Extract all parser signal families from one HTML payload.
 * @param {string} html Raw HTML page source.
 * @returns {Record<string, unknown>} Signal bundle.
 */
function _extractSignals(html) {
  const embeddedJson = _extractEmbeddedJsonObjects(html);
  const jsonCandidates = embeddedJson.flatMap((entry) => _extractJsonMetricCandidates(entry));
  return {
    progress: _extractProgressMetrics(html),
    fractions: _extractFractionCandidates(html),
    percentages: _extractPercentCandidates(html),
    datetimes: _extractDatetimeCandidates(html),
    json_candidates: jsonCandidates,
  };
}

/**
 * @brief Build normalized provider payload with parser diagnostics.
 * @param {string} provider Provider key.
 * @param {Record<string, Record<string, number | string | null>>} windows Window map.
 * @param {Record<string, unknown>} signals Parser signal bundle.
 * @param {Array<string>} sourcePages Source page URLs.
 * @returns {Record<string, unknown>} Provider payload.
 */
function _buildProviderPayload(provider, windows, signals, sourcePages) {
  return {
    provider,
    windows,
    extracted_at: new Date().toISOString(),
    source_pages: sourcePages,
    parser: {
      version: PARSER_VERSION,
      signal_counts: {
        progress: Array.isArray(signals.progress) ? signals.progress.length : 0,
        fractions: Array.isArray(signals.fractions) ? signals.fractions.length : 0,
        percentages: Array.isArray(signals.percentages) ? signals.percentages.length : 0,
        datetimes: Array.isArray(signals.datetimes) ? signals.datetimes.length : 0,
        json_candidates: Array.isArray(signals.json_candidates) ? signals.json_candidates.length : 0,
      },
    },
  };
}

/**
 * @brief Parse Claude usage HTML into normalized window metrics.
 * @details Targets windows `5h` and `7d` using ordered semantic extraction.
 * @param {string} html Claude usage page HTML.
 * @returns {Record<string, unknown>} Normalized Claude payload.
 * @satisfies REQ-040
 */
export function parseClaudeUsageHtml(html) {
  const signals = _extractSignals(html);
  const windows = _buildWindows(
    ["5h", "7d"],
    signals.progress,
    signals.fractions,
    signals.percentages,
    signals.datetimes,
    signals.json_candidates
  );
  return _buildProviderPayload("claude", windows, signals, ["https://claude.ai/settings/usage"]);
}

/**
 * @brief Parse Codex usage HTML into normalized window metrics.
 * @details Targets windows `5h` and `7d` using ordered semantic extraction.
 * @param {string} html Codex usage page HTML.
 * @returns {Record<string, unknown>} Normalized Codex payload.
 * @satisfies REQ-041
 */
export function parseCodexUsageHtml(html) {
  const signals = _extractSignals(html);
  const windows = _buildWindows(
    ["5h", "7d"],
    signals.progress,
    signals.fractions,
    signals.percentages,
    signals.datetimes,
    signals.json_candidates
  );
  return _buildProviderPayload("codex", windows, signals, ["https://chatgpt.com/codex/settings/usage"]);
}

/**
 * @brief Parse Copilot features-page HTML into normalized window metrics.
 * @param {string} html Copilot features page HTML.
 * @returns {Record<string, unknown>} Normalized features payload.
 */
export function parseCopilotFeaturesHtml(html) {
  const signals = _extractSignals(html);
  const windows = _buildWindows(
    ["30d"],
    signals.progress,
    signals.fractions,
    signals.percentages,
    signals.datetimes,
    signals.json_candidates
  );
  return _buildProviderPayload(
    "copilot",
    windows,
    signals,
    ["https://github.com/settings/copilot/features"]
  );
}

/**
 * @brief Parse Copilot premium-requests HTML into normalized window metrics.
 * @param {string} html Copilot premium page HTML.
 * @returns {Record<string, unknown>} Normalized premium payload.
 */
export function parseCopilotPremiumHtml(html) {
  const signals = _extractSignals(html);
  const windows = _buildWindows(
    ["30d"],
    signals.progress,
    signals.fractions,
    signals.percentages,
    signals.datetimes,
    signals.json_candidates
  );
  return _buildProviderPayload(
    "copilot",
    windows,
    signals,
    ["https://github.com/settings/billing/premium_requests_usage"]
  );
}

/**
 * @brief Merge Copilot feature and premium payloads into one consumer payload.
 * @details Selects the richest `30d` window metrics and aggregates source-page and
 * parser signal counters for traceable diagnostics.
 * @param {Record<string, unknown>} featuresPayload Copilot features parsed payload.
 * @param {Record<string, unknown>} premiumPayload Copilot premium parsed payload.
 * @returns {Record<string, unknown>} Merged Copilot payload.
 * @satisfies REQ-042
 */
export function mergeCopilotPayloads(featuresPayload, premiumPayload) {
  const featuresWindow = featuresPayload?.windows?.["30d"] ?? null;
  const premiumWindow = premiumPayload?.windows?.["30d"] ?? null;
  const mergedWindow = {
    usage_percent: premiumWindow?.usage_percent ?? featuresWindow?.usage_percent ?? null,
    remaining: premiumWindow?.remaining ?? featuresWindow?.remaining ?? null,
    limit: premiumWindow?.limit ?? featuresWindow?.limit ?? null,
    reset_at: premiumWindow?.reset_at ?? featuresWindow?.reset_at ?? null,
  };

  const featuresSignals = featuresPayload?.parser?.signal_counts ?? {};
  const premiumSignals = premiumPayload?.parser?.signal_counts ?? {};

  return {
    provider: "copilot",
    windows: {
      "30d": mergedWindow ?? {
        usage_percent: null,
        remaining: null,
        limit: null,
        reset_at: null,
      },
    },
    extracted_at: new Date().toISOString(),
    source_pages: [
      "https://github.com/settings/copilot/features",
      "https://github.com/settings/billing/premium_requests_usage",
    ],
    parser: {
      version: PARSER_VERSION,
      signal_counts: {
        progress: (featuresSignals.progress ?? 0) + (premiumSignals.progress ?? 0),
        fractions: (featuresSignals.fractions ?? 0) + (premiumSignals.fractions ?? 0),
        percentages: (featuresSignals.percentages ?? 0) + (premiumSignals.percentages ?? 0),
        datetimes: (featuresSignals.datetimes ?? 0) + (premiumSignals.datetimes ?? 0),
        json_candidates:
          (featuresSignals.json_candidates ?? 0) + (premiumSignals.json_candidates ?? 0),
      },
    },
  };
}
