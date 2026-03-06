/**
 * @file parsers.js
 * @brief Localization-independent HTML parser primitives for AIBar Chrome extension.
 * @details Extracts quota and progress metrics from provider usage pages by using
 * DOM semantics (`role=progressbar`, numeric attributes, `datetime`, embedded JSON)
 * plus script bootstrap payload extraction, instead of localized visible labels.
 * @satisfies CTN-010
 * @satisfies REQ-040
 * @satisfies REQ-041
 * @satisfies REQ-042
 */

/** @brief Parser semantic version for debug payloads. */
export const PARSER_VERSION = "2026.03.06.1";

/** @brief Token regex for window hints. */
const WINDOW_HINT_REGEX = /\b(5h|7d|30d)\b/i;

/** @brief Token regex for numeric fractions. */
const FRACTION_REGEX = /([0-9][0-9\s.,]*)\s*\/\s*([0-9][0-9\s.,]*)/g;

/** @brief Token regex for percentage values. */
const PERCENT_REGEX = /([0-9][0-9\s.,]*)\s*%/g;

/** @brief ISO datetime token regex for inline/script extraction. */
const ISO_DATETIME_REGEX = /\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})\b/g;

/** @brief Bootstrap variable names that frequently carry usage payloads. */
const JSON_BOOTSTRAP_KEYS = [
  "__NEXT_DATA__",
  "__remixContext",
  "__NUXT__",
  "__INITIAL_STATE__",
  "INITIAL_STATE",
  "__APOLLO_STATE__",
];

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
  const source = String(context ?? "");
  const compactMatch = source.match(WINDOW_HINT_REGEX);
  if (compactMatch) {
    return compactMatch[1].toLowerCase();
  }
  if (/\b(?:5\s*(?:h|hr|hour|hours)|hourly)\b/i.test(source)) {
    return "5h";
  }
  if (/\b(?:7\s*(?:d|day|days)|weekly|week)\b/i.test(source)) {
    return "7d";
  }
  if (/\b(?:30\s*(?:d|day|days)|monthly|month)\b/i.test(source)) {
    return "30d";
  }
  return null;
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
 * @brief Extract script-tag entries with full tag and body slices.
 * @param {string} html Raw HTML.
 * @returns {Array<Record<string, string>>} Script entries.
 */
function _extractScriptEntries(html) {
  const entries = [];
  const scriptRegex = /<script([^>]*)>([\s\S]*?)<\/script>/gi;
  let match;
  while ((match = scriptRegex.exec(html)) !== null) {
    entries.push({
      tag_attributes: match[1] ?? "",
      body: (match[2] ?? "").trim(),
      full_tag: match[0] ?? "",
    });
  }
  return entries;
}

/**
 * @brief Join all script bodies into one diagnostic text stream.
 * @param {string} html Raw HTML.
 * @returns {string} Concatenated script text.
 */
function _extractScriptText(html) {
  return _extractScriptEntries(html)
    .map((entry) => entry.body)
    .filter((entry) => Boolean(entry))
    .join(" ");
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
 * @brief Extract numeric fraction candidates from one generic text stream.
 * @details Captures raw numeric pairs (`A/B`) that may encode used/limit or
 * remaining/limit values independent from natural-language labels.
 * @param {string} text Generic text stream.
 * @returns {Array<Record<string, number>>} Ordered fraction records.
 */
function _extractFractionCandidatesFromText(text) {
  const fractions = [];
  FRACTION_REGEX.lastIndex = 0;
  let match;
  while ((match = FRACTION_REGEX.exec(text)) !== null) {
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
 * @brief Extract percentage literals from one generic text stream.
 * @param {string} text Generic text stream.
 * @returns {Array<number>} Ordered percentage numbers.
 */
function _extractPercentCandidatesFromText(text) {
  const percentages = [];
  PERCENT_REGEX.lastIndex = 0;
  let match;
  while ((match = PERCENT_REGEX.exec(text)) !== null) {
    const value = parseLocalizedNumber(match[1]);
    if (value !== null) {
      percentages.push(_clamp(value, 0, 100));
    }
  }
  return percentages;
}

/**
 * @brief Extract ISO-like datetime tokens from one generic text stream.
 * @param {string} text Generic text stream.
 * @returns {Array<string>} Ordered datetime candidates in ISO format.
 */
function _extractDatetimeCandidatesFromText(text) {
  const datetimes = [];
  ISO_DATETIME_REGEX.lastIndex = 0;
  let match;
  while ((match = ISO_DATETIME_REGEX.exec(text)) !== null) {
    const parsed = new Date(match[0]);
    if (!Number.isNaN(parsed.getTime())) {
      datetimes.push(parsed.toISOString());
    }
  }
  return datetimes;
}

/**
 * @brief Deduplicate array values while preserving original ordering.
 * @template T
 * @param {Array<T>} values Candidate values.
 * @param {(entry: T) => string} keySelector Unique-key selector.
 * @returns {Array<T>} Deduplicated values.
 */
function _dedupeByKey(values, keySelector) {
  const output = [];
  const seen = new Set();
  for (const value of values) {
    const key = keySelector(value);
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    output.push(value);
  }
  return output;
}

/**
 * @brief Extract numeric fraction candidates from visible and script text streams.
 * @param {string} html Raw HTML.
 * @returns {Array<Record<string, number>>} Ordered fraction records.
 */
function _extractFractionCandidates(html) {
  const visible = _extractFractionCandidatesFromText(_extractPlainText(html));
  const script = _extractFractionCandidatesFromText(_extractScriptText(html));
  return _dedupeByKey([...visible, ...script], (entry) => `${entry.first}|${entry.second}`);
}

/**
 * @brief Extract percentage literals from visible and script text streams.
 * @param {string} html Raw HTML.
 * @returns {Array<number>} Ordered percentage numbers.
 */
function _extractPercentCandidates(html) {
  const visible = _extractPercentCandidatesFromText(_extractPlainText(html));
  const script = _extractPercentCandidatesFromText(_extractScriptText(html));
  return _dedupeByKey([...visible, ...script], (entry) => String(entry));
}

/**
 * @brief Extract ISO-like datetime tokens from markup and script content.
 * @details Reads `datetime="..."` attributes and optional ISO literals in script.
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
  const scriptDatetimes = _extractDatetimeCandidatesFromText(_extractScriptText(html));
  return _dedupeByKey([...datetimes, ...scriptDatetimes], (entry) => entry);
}

/**
 * @brief Extract balanced JSON slice starting at object/array token.
 * @param {string} source Source text.
 * @param {number} startIndex Start index for `{` or `[` token.
 * @returns {string | null} Balanced JSON slice or null.
 */
function _extractBalancedJsonSlice(source, startIndex) {
  const opener = source[startIndex];
  const closer = opener === "{" ? "}" : opener === "[" ? "]" : null;
  if (!closer) {
    return null;
  }

  let depth = 0;
  let inString = false;
  let quote = "";
  let escaped = false;

  for (let index = startIndex; index < source.length; index += 1) {
    const token = source[index];
    if (inString) {
      if (escaped) {
        escaped = false;
        continue;
      }
      if (token === "\\") {
        escaped = true;
        continue;
      }
      if (token === quote) {
        inString = false;
      }
      continue;
    }

    if (token === "\"" || token === "'") {
      inString = true;
      quote = token;
      continue;
    }

    if (token === opener) {
      depth += 1;
      continue;
    }
    if (token === closer) {
      depth -= 1;
      if (depth === 0) {
        return source.slice(startIndex, index + 1);
      }
    }
  }

  return null;
}

/**
 * @brief Decode quoted JSON payload and parse into object when possible.
 * @param {string} quotedToken Quoted JS/JSON token.
 * @returns {unknown | null} Parsed payload or null.
 */
function _decodeQuotedJsonPayload(quotedToken) {
  try {
    const decoded = JSON.parse(quotedToken);
    if (typeof decoded === "string") {
      const compact = decoded.trim();
      if (compact.startsWith("{") || compact.startsWith("[")) {
        return JSON.parse(compact);
      }
    }
  } catch (_error) {
    // Ignore malformed quoted payloads.
  }
  return null;
}

/**
 * @brief Extract bootstrap JSON objects from script assignment statements.
 * @param {string} scriptBody Script body text.
 * @returns {Array<unknown>} Parsed JSON roots.
 */
function _extractBootstrapJsonFromScriptBody(scriptBody) {
  const objects = [];
  const assignmentRegex = new RegExp(
    `(?:window\\.)?(?:${JSON_BOOTSTRAP_KEYS.join("|")})\\s*=`,
    "gi"
  );
  let match;
  while ((match = assignmentRegex.exec(scriptBody)) !== null) {
    const tokenStart = assignmentRegex.lastIndex;
    const trailing = scriptBody.slice(tokenStart).trimStart();

    const parseMatch = trailing.match(/^JSON\.parse\(\s*("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')\s*\)/);
    if (parseMatch) {
      const parsed = _decodeQuotedJsonPayload(parseMatch[1]);
      if (parsed !== null) {
        objects.push(parsed);
      }
      continue;
    }

    const firstObjectIndex = scriptBody.indexOf("{", tokenStart);
    const firstArrayIndex = scriptBody.indexOf("[", tokenStart);
    const candidates = [firstObjectIndex, firstArrayIndex].filter((value) => value >= 0);
    const jsonStart = candidates.length > 0 ? Math.min(...candidates) : -1;
    if (jsonStart < 0) {
      continue;
    }
    const jsonSlice = _extractBalancedJsonSlice(scriptBody, jsonStart);
    if (!jsonSlice) {
      continue;
    }
    try {
      objects.push(JSON.parse(jsonSlice));
    } catch (_error) {
      // Ignore malformed bootstrap objects.
    }
  }

  return objects;
}

/**
 * @brief Collect embedded JSON payloads from script tags.
 * @details Parses `application/json`, `application/ld+json`, and `__NEXT_DATA__`
 * scripts plus bootstrap assignment payloads into objects for language-agnostic
 * metric extraction.
 * @param {string} html Raw HTML.
 * @returns {Array<unknown>} Parsed JSON roots.
 */
function _extractEmbeddedJsonObjects(html) {
  const objects = [];
  for (const scriptEntry of _extractScriptEntries(html)) {
    const scriptTag = scriptEntry.full_tag;
    const scriptBody = scriptEntry.body;
    if (!scriptBody) {
      continue;
    }

    const isJsonType = /type\s*=\s*(?:"application\/(?:ld\+)?json"|'application\/(?:ld\+)?json')/i.test(scriptTag);
    const isNextData = /id\s*=\s*(?:"__NEXT_DATA__"|'__NEXT_DATA__')/i.test(scriptTag);
    if (isJsonType || isNextData) {
      try {
        objects.push(JSON.parse(scriptBody));
      } catch (_error) {
        // Skip malformed script payloads.
      }
    }

    objects.push(..._extractBootstrapJsonFromScriptBody(scriptBody));
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
    const windowHintCandidateText = Object.entries(obj)
      .flatMap(([key, value]) => [key, typeof value === "string" ? value : ""])
      .join(" ");
    const hinted = _extractWindowHint(windowHintCandidateText);
    if (hinted) {
      windowHint = hinted;
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
 * @brief Compute normalized candidate score for window assignment.
 * @param {Record<string, unknown>} candidate Candidate payload.
 * @param {string} windowKey Target window key.
 * @returns {number} Descending score; negative values indicate poor fit.
 */
function _candidateScore(candidate, windowKey) {
  let score = 0;
  const hasUsage = parseLocalizedNumber(candidate?.usage_percent) !== null;
  const hasLimit = parseLocalizedNumber(candidate?.limit) !== null;
  const hasRemaining = parseLocalizedNumber(candidate?.remaining) !== null;
  const hasUsed = parseLocalizedNumber(candidate?.used) !== null;
  const hasReset = typeof candidate?.reset_at === "string";

  if (candidate?.window_hint === windowKey) {
    score += 4;
  }
  if (hasUsage) {
    score += 3;
  }
  if (hasLimit) {
    score += 2;
  }
  if (hasRemaining || hasUsed) {
    score += 2;
  }
  if (hasReset) {
    score += 1;
  }
  if (!hasUsage && !hasLimit && !hasRemaining && !hasUsed) {
    score -= 5;
  }

  return score;
}

/**
 * @brief Select one best-matching candidate by score and index proximity.
 * @param {Array<Record<string, unknown>>} candidates Candidate list.
 * @param {string} windowKey Target window key.
 * @param {number} index Ordered fallback index.
 * @returns {Record<string, unknown> | null} Selected candidate.
 */
function _pickCandidate(candidates, windowKey, index) {
  const ranked = candidates
    .map((item, itemIndex) => ({
      item,
      score: _candidateScore(item, windowKey),
      distance: Math.abs(itemIndex - index),
    }))
    .sort((left, right) => right.score - left.score || left.distance - right.distance);

  const best = ranked[0];
  if (!best || best.score < 2) {
    return null;
  }
  return best.item;
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
    const usagePercentFromSignals = _clamp(
      parseLocalizedNumber(jsonCandidate?.usage_percent) ??
        parseLocalizedNumber(progressCandidate?.usage_percent) ??
        parseLocalizedNumber(percentCandidates[index] ?? null),
      0,
      100
    );

    const quotaFromFraction = fractionCandidates[index]
      ? _inferQuotaFromFraction(fractionCandidates[index], usagePercentFromSignals)
      : { remaining: null, limit: null };

    const limit = _clamp(
      parseLocalizedNumber(jsonCandidate?.limit) ?? quotaFromFraction.limit,
      0,
      Number.MAX_SAFE_INTEGER
    );

    const used = _clamp(parseLocalizedNumber(jsonCandidate?.used), 0, Number.MAX_SAFE_INTEGER);

    let remaining = _clamp(
      parseLocalizedNumber(jsonCandidate?.remaining) ?? quotaFromFraction.remaining,
      0,
      Number.MAX_SAFE_INTEGER
    );
    if (remaining === null && limit !== null && used !== null) {
      remaining = _clamp(limit - used, 0, limit);
    }

    let usagePercent = usagePercentFromSignals;
    if (usagePercent === null && limit !== null && used !== null && limit > 0) {
      usagePercent = _clamp((used / limit) * 100, 0, 100);
    }
    if (usagePercent === null && limit !== null && remaining !== null && limit > 0) {
      usagePercent = _clamp(((limit - remaining) / limit) * 100, 0, 100);
    }

    if (remaining === null && limit !== null && usagePercent !== null) {
      remaining = _clamp(limit * (1 - usagePercent / 100), 0, limit);
    }

    const hasQuotaOrUsageSignal =
      usagePercent !== null || limit !== null || remaining !== null || used !== null;

    const resetAtCandidate =
      typeof jsonCandidate?.reset_at === "string" ? jsonCandidate.reset_at : null;
    const resetAt =
      resetAtCandidate ??
      (hasQuotaOrUsageSignal ? datetimeCandidates[index] ?? null : null);

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
 * @brief Determine whether payload contains usable quota/usage metrics.
 * @details Rejects payloads that contain only reset timestamps without
 * quota/progress numbers to avoid false-positive parser success states.
 * @param {Record<string, unknown> | null | undefined} payload Parsed payload.
 * @returns {boolean} True when at least one window has quota or usage metrics.
 */
export function providerPayloadHasUsableMetrics(payload) {
  const windows = payload?.windows;
  if (!windows || typeof windows !== "object") {
    return false;
  }

  return Object.values(windows).some((windowData) => {
    const usage = parseLocalizedNumber(windowData?.usage_percent);
    const remaining = parseLocalizedNumber(windowData?.remaining);
    const limit = parseLocalizedNumber(windowData?.limit);
    return usage !== null || remaining !== null || limit !== null;
  });
}

/**
 * @brief Build compact signal sample payload for debug API responses.
 * @param {Array<unknown>} values Candidate values.
 * @param {number} maxItems Maximum number of sample entries.
 * @returns {Array<unknown>} Bounded sample array.
 */
function _sample(values, maxItems) {
  return values.slice(0, maxItems);
}

/**
 * @brief Extract parser signal counts and bounded samples for diagnostics.
 * @param {string} html Raw HTML page source.
 * @returns {Record<string, unknown>} Signal diagnostics.
 */
export function extractSignalDiagnostics(html) {
  const signals = _extractSignals(html);
  return {
    parser_version: PARSER_VERSION,
    signal_counts: {
      progress: signals.progress.length,
      fractions: signals.fractions.length,
      percentages: signals.percentages.length,
      datetimes: signals.datetimes.length,
      json_candidates: signals.json_candidates.length,
    },
    signal_samples: {
      progress: _sample(signals.progress, 3),
      fractions: _sample(signals.fractions, 3),
      percentages: _sample(signals.percentages, 5),
      datetimes: _sample(signals.datetimes, 3),
      json_candidate_window_hints: _sample(
        signals.json_candidates.map((candidate) => candidate.window_hint ?? null),
        5
      ),
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
