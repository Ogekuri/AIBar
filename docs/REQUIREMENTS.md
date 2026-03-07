---
title: "AIBar Requirements"
description: Software requirements specification
version: "0.3.13"
date: "2026-03-07"
author: "req-change"
scope:
  paths:
    - "src/**/*.py"
    - "src/**/*.js"
    - "src/**/*.json"
    - "src/**/*.css"
    - "scripts/**/*.sh"
    - ".github/workflows/**/*"
  excludes:
    - ".*/**"
visibility: "draft"
tags: ["requirements", "srs", "llm-ready"]
---

# AIBar Requirements

## 1. Introduction

### 1.1 Document Rules
This document MUST follow these authoring rules (LLM-first, normative SRS):
- This document MUST be written and maintained in English.
- Use RFC 2119 keywords exclusively (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY); do not use "shall".
- In requirements sections, every bullet MUST start with a unique, stable Requirement ID.
- Requirement ID prefixes in this document are PRJ, CTN, DES, REQ, and TST.
- Each requirement MUST be atomic, single-sentence, and testable; target <= 35 words.
- Requirement IDs MUST remain stable across updates; IDs MUST NOT be reused.

### 1.2 Project Scope
AIBar implements a Python CLI/UI usage monitor for Claude, OpenAI, OpenRouter, Copilot, and Codex, plus a GNOME Shell extension that renders the CLI JSON output in the top panel popup UI, and shell scripts for extension installation and maintenance.

Used libraries/components evidenced by direct imports:
- Python: `click`, `textual`, `pydantic`, `httpx` (`src/aibar/aibar/*.py`, `src/aibar/aibar/providers/*.py`)
- GNOME JS: `GLib`, `St`, `Gio`, `Clutter`, `GObject`, `Main`, `PanelMenu`, `PopupMenu` (`src/aibar/gnome-extension/aibar@aibar.panel/extension.js`)

Performance note: explicit caching optimization is implemented via in-memory + disk TTL cache for non-Claude providers (`ResultCache` in `src/aibar/aibar/cache.py`); no other explicit performance optimizations were identified.

### 1.3 Repository Structure (evidence snapshot)
```text
.
├── .github/
│   └── workflows/
│       └── .place-holder
├── docs/
│   ├── .place-holder
│   └── REQUIREMENTS.md
├── pyproject.toml
├── scripts/
│   ├── aibar.sh
│   ├── claude_token_refresh.sh
│   ├── install-gnome-extension.sh
│   └── test-gnome-extension.sh
├── src/
│   └── aibar/
│       ├── gnome-extension/
│       │   └── aibar@aibar.panel/
│       │       ├── extension.js
│       │       ├── metadata.json
│       │       └── stylesheet.css
│       └── aibar/
│           ├── __main__.py
│           ├── cache.py
│           ├── claude_cli_auth.py
│           ├── cli.py
│           ├── config.py
│           ├── ui.py
│           └── providers/
│               ├── base.py
│               ├── claude_oauth.py
│               ├── codex.py
│               ├── copilot.py
│               ├── openai_usage.py
│               └── openrouter.py
└── tests/
    └── .place-holder
```

## 2. Project Requirements

### 2.1 Project Functions
- **PRJ-001**: MUST expose CLI subcommands `show`, `doctor`, `ui`, `env`, `setup`, and `login` under one Click command group.
- **PRJ-002**: MUST aggregate provider metrics through a normalized provider contract for `claude`, `openai`, `openrouter`, `copilot`, and `codex`.
- **PRJ-003**: MUST provide an interactive Textual UI with an Overview tab and a Raw JSON tab.
- **PRJ-004**: MUST provide a GNOME Shell panel extension named `IABar Monitor` that executes `aibar show --json`, renders provider-specific cards, sets metadata owner identifiers (`url`, `github`) to `Ogekuri`, and forces `scripts/test-gnome-extension.sh` nested-shell resolution to `1024x800` via `MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800`.
- **PRJ-005**: MUST maintain a machine-readable symbol inventory for repository code documentation under `docs/REFERENCES.md`.
- **PRJ-006**: MUST provide a PEP 621-compliant `pyproject.toml` at repository root enabling installation via `uv pip install` and live execution via `uvx --from git+https://github.com/Ogekuri/AIBar.git aibar <command>`.
- **PRJ-007**: MUST document in `README.md` a dedicated section covering `uv`-based installation, removal, and `uvx` live execution instructions.
- **PRJ-008**: MUST provide `scripts/install-gnome-extension.sh` that copies GNOME extension files from `src/aibar/gnome-extension/aibar@aibar.panel/` to `~/.local/share/gnome-shell/extensions/aibar@aibar.panel/` and enables the extension via `gnome-extensions enable`.
- **PRJ-009**: MUST provide a Chrome extension in `src/aibar/chrome-extension` exposing an AIBar toolbar popup with `claude`, `copilot`, and `codex` provider tabs.
- **PRJ-010**: MUST collect Chrome extension provider metrics through autonomous website download/parsing flows without invoking the `aibar` executable.
- **PRJ-011**: MUST expose Chrome-extension runtime message APIs with one primary snapshot endpoint and one debug-command surface for deterministic field diagnostics without source-code edits.
- **PRJ-012**: MUST maintain `guidelines/Google_Extension_API_Reference.md` as a machine-readable Chrome-extension API contract synchronized to current implementation and sufficient for complete client-side API integration.

### 2.2 Project Constraints
- **CTN-001**: MUST resolve provider credentials with precedence: environment variable, then `~/.config/aibar/env`, then provider-specific local credential stores.
- **CTN-002**: MUST represent provider fetch output with `ProviderResult` containing `provider`, `window`, `metrics`, `updated_at`, `raw`, and optional `error`.
- **CTN-003**: MUST perform external HTTP API calls with `httpx.AsyncClient(timeout=30.0)` for provider integrations.
- **CTN-004**: MUST cache successful non-Claude provider results with per-provider TTL and disk persistence under `~/.cache/aibar`, and MUST persist latest successful Claude dual-window payload for HTTP 429 fallback rendering.
- **CTN-005**: MAY depend on unofficial/internal endpoints when official usage APIs are unavailable for Claude, Copilot, or Codex integrations.
- **CTN-006**: MUST keep `docs/REFERENCES.md` synchronized with symbols defined under `src/` and `.github/workflows/`.
- **CTN-007**: MUST declare `hatchling` as `[build-system]` backend in `pyproject.toml` with `[project]` metadata including `name`, `version`, `requires-python`, `dependencies`, and `[project.scripts]` console entry point.
- **CTN-008**: MUST execute Chrome extension provider updates every 180 seconds by default through a persisted interval value that the user MAY override and that MUST survive browser restarts via `chrome.storage.local`.
- **CTN-009**: MUST process Chrome extension source pages in fixed order: Claude usage, Codex usage, Copilot features usage, Copilot premium usage.
- **CTN-010**: MUST extract Chrome extension usage values from localization-independent DOM semantics, bootstrap-script payloads, and escaped script key-value artifacts, and MUST NOT rely on localized visible-label strings.
- **CTN-011**: MUST expose Chrome extension runtime debugging through console-safe structured logs, optional persisted extension-local log records, and API-retrievable parser/window diagnostic traces for fetched provider pages.
- **CTN-012**: MUST restrict debug HTTP retrieval commands to `https` URLs and allowed hosts `claude.ai`, `chatgpt.com`, and `github.com`.
- **CTN-013**: MUST cap debug HTTP response body previews through bounded `max_chars` truncation to prevent unbounded payload growth.
- **CTN-014**: MUST default debug API enablement to disabled and MUST allow debug API commands only after explicit user enablement.
- **CTN-015**: MUST declare `host_permissions` in Chrome extension manifest for all provider domains so that service-worker `fetch()` includes browser session credentials via `credentials: "include"`.
- **CTN-016**: MUST persist user-configured refresh interval in `chrome.storage.local` under a deterministic key and MUST restore it on service-worker startup before scheduling the first alarm.
- **CTN-017**: MUST persist debug API enablement for the current browser session across service-worker restarts and MUST clear it when the browser process terminates.

## 3. Requirements

### 3.1 Design and Implementation
- **DES-001**: MUST define `BaseProvider` as an abstract interface with `fetch`, `is_configured`, and `get_config_help`.
- **DES-002**: MUST encode supported windows as `5h`, `7d`, `30d`, and `code_review` and provider names as `claude`, `openai`, `openrouter`, `copilot`, and `codex`.
- **DES-003**: MUST reject invalid CLI window values and provider values using Click `BadParameter`.
- **DES-004**: MUST sanitize sensitive keys (`token`, `key`, `secret`, `password`, `authorization`) from cached raw payloads before disk writes.
- **DES-005**: MUST parse env-file assignments with optional `export`, quoted values, and inline comments in GNOME extension env loading.
- **DES-006**: MUST auto-refresh GNOME extension data every 300 seconds and also support manual refresh from the popup menu.
- **DES-007**: MUST reuse GNOME extension icon assets for Chrome extension toolbar icons and popup branding assets.
- **DES-008**: MUST implement Chrome extension popup tabs with GNOME-parity card layout semantics while restricting visible providers to `claude`, `copilot`, and `codex`.
- **DES-009**: MUST run Chrome extension refresh scheduling in a dedicated background execution unit that updates shared provider state for popup rendering.
- **DES-010**: MUST remove repository directory `src/aibar/chrome-extension/temp/` after parser extraction logic is implemented and validated.
- **DES-011**: MUST implement a background API dispatcher with `api.main.snapshot`, `debug.api.describe`, and `debug.api.execute` routes and a centralized debug-access guard controlled by runtime configuration state.
- **DES-012**: MUST expose popup configuration controls limited to refresh-now, interval input, debug-enable checkbox, and debug status label; debug export, log-clear, and page-fetch actions MUST be accessible only through debug API commands.

### 3.2 Functions
- **REQ-001**: MUST skip unconfigured providers in `show` output and print missing environment-variable hints when text mode is used.
- **REQ-002**: MUST print both 5-hour and 7-day outputs for Claude and Codex when `show` runs with default window and non-JSON mode.
- **REQ-003**: MUST emit pretty-printed JSON (`indent=2`) for fetched providers when `show --json` is requested.
- **REQ-004**: MUST run provider health checks in `doctor` using the 5-hour window and report per-provider configuration and test status.
- **REQ-005**: MUST prompt for OpenRouter and OpenAI keys and optional GitHub token in `setup`, then persist provided keys to `~/.config/aibar/env`.
- **REQ-006**: MUST fail Claude login when CLI credentials are missing or expired and MUST print `claude setup-token` remediation guidance.
- **REQ-007**: MUST execute GitHub device-flow login for Copilot and save the token in `~/.config/aibar/copilot.json`.
- **REQ-008**: MUST render Textual provider cards for all providers, support refresh, support 5h/7d switching, support JSON-tab toggling, suppress `Error: Rate limited. Try again later.`, and append `⚠️ Limit reached!` after `Resets in:` at displayed `100.0%`.
- **REQ-009**: MUST use cache hits before API fetches only for non-Claude providers in Textual refresh flow and invalidate cache when window selection changes.
- **REQ-010**: MUST map OpenAI `5h` requests to a one-day API range before requesting usage and costs.
- **REQ-011**: MUST derive OpenRouter `cost` from window-specific usage fields (`usage_daily`, `usage_weekly`, `usage_monthly`) and include `limit` and `limit_remaining`.
- **REQ-012**: MUST ignore requested window for Copilot fetch and return results with effective window `30d`.
- **REQ-013**: MUST select Codex rate-limit primary window for `5h` and secondary window for other requested windows.
- **REQ-014**: MUST attempt Codex token refresh when refresh token exists and `last_refresh` age is at least eight days.
- **REQ-015**: SHOULD continue Codex fetch with existing credentials when non-authentication refresh exceptions occur, leaving refresh failures non-fatal.
- **REQ-016**: MUST load `~/.config/aibar/env` into subprocess environment before GNOME extension executes `aibar show --json`.
- **REQ-017**: MUST set GNOME panel label to total cost when cost metrics exist, otherwise configured-provider count when quota metrics exist, otherwise `N/A`; quota-only cards MUST render `Remaining credits: <remaining>/<limit>` with `<remaining>` in bold; reset labels in extension cards MUST start with `Reset in:` and append `⚠️ Limit reached!` at displayed `100.0%`; rate-limit quota payloads MUST NOT render `Error: Rate limited. Try again later.`; Copilot cards MUST render a `30d` window bar with reset text directly below that bar and before remaining-credits text; popup header/action labels MUST render `AIBar` branding (`AIBar`, `Open AIBar UI`).
- **REQ-018**: MUST set GNOME panel label to `Err` and truncate popup error text to 40 characters when command execution or JSON parsing fails.
- **REQ-019**: SHOULD order extension provider tabs/cards by `claude`, `openrouter`, `copilot`, `codex`, with providers not listed in ordering array appended alphabetically.
- **REQ-020**: MUST include each discovered source symbol in `docs/REFERENCES.md` with file path, symbol kind, line-range evidence, and parsed Doxygen fields (`@brief`, `@param`, `@return`, `@raises`) when present in source declarations.
- **REQ-021**: MUST render GNOME panel percentage labels between the icon and panel summary label in fixed order: Claude 5h usage, Claude 7d usage, Copilot usage, Codex 5h usage, Codex 7d usage.
- **REQ-022**: MUST style Claude 5h/7d labels with `aibar-tab-label-claude`, Copilot label with `aibar-tab-label-copilot`, and Codex 5h/7d labels with `aibar-tab-label-codex`; MUST render Claude 5h, Copilot, and Codex 5h percentages in bold; MUST omit unavailable percentage metrics.
- **REQ-023**: MUST declare a `[project.scripts]` entry `aibar = "aibar.cli:main"` in `pyproject.toml` so that `uv pip install` and `uvx` resolve the `aibar` console command.
- **REQ-024**: MUST provide `src/aibar/aibar/__main__.py` that delegates to `aibar.cli:main` to enable `python -m aibar` execution.
- **REQ-025**: MUST resolve the git project root via `git rev-parse --show-toplevel` in `scripts/install-gnome-extension.sh` so the script is invocable from any working directory.
- **REQ-026**: MUST create target directory `~/.local/share/gnome-shell/extensions/aibar@aibar.panel/` if it does not exist before copying extension files.
- **REQ-027**: MUST validate prerequisites before copying: git availability, project root resolution, non-empty source directory, and presence of `metadata.json` in source.
- **REQ-028**: MUST produce colored, formatted terminal output using ANSI escape sequences for status, success, error, and informational messages in `scripts/install-gnome-extension.sh`.
- **REQ-029**: MUST copy all files from `src/aibar/gnome-extension/aibar@aibar.panel/` to target directory preserving file attributes via `cp -a`.
- **REQ-030**: MUST exit with non-zero status and descriptive error message when any prerequisite check fails in `scripts/install-gnome-extension.sh`.
- **REQ-031**: MUST invoke `scripts/install-gnome-extension.sh` before launching the nested shell in `scripts/test-gnome-extension.sh` to update extension files.
- **REQ-032**: MUST enable the extension via `gnome-extensions enable aibar@aibar.panel` after successful file copy in `scripts/install-gnome-extension.sh` with colored status output.
- **REQ-033**: `scripts/test-gnome-extension.sh` MUST NOT accept any subcommand parameter; it MUST execute the nested-shell launch directly on invocation without arguments.
- **REQ-034**: MUST render reset countdown as `Resets in: <d>d <h>h <m>m` for durations >= 24 hours in CLI text output.
- **REQ-035**: MUST print `Remaining credits: <remaining> / <limit>` for Claude, Codex, and Copilot when both values exist in CLI text output.
- **REQ-036**: MUST render Claude HTTP 429 as partial-window output: 5h shows `Error: Rate limited. Try again later.` and `Usage: ... 100.0%`; 5h reset and all 7d usage/reset values MUST use persisted Claude payload when available.
- **REQ-037**: MUST use synthetic Claude partial-window fallback values when persisted Claude payload is unavailable during HTTP 429 rendering.
- **REQ-038**: MUST open the Chrome extension popup panel on toolbar icon click and render tab navigation with exactly `claude`, `copilot`, and `codex` entries.
- **REQ-039**: MUST render Chrome popup tab visual hierarchy, progress bars, and metric card structure equivalent to GNOME extension semantics for corresponding providers.
- **REQ-040**: MUST parse Claude `5h` and `7d` usage windows from `https://claude.ai/settings/usage` with deterministic window assignment and MUST fail refresh when no usable quota/progress metrics are extracted.
- **REQ-041**: MUST parse Codex `5h`, `7d`, and `code_review` windows from `https://chatgpt.com/codex/settings/usage`, including remaining-percentage-to-usage normalization and non-window artifact rejection, and MUST fail refresh when usable metrics are absent.
- **REQ-042**: MUST combine Copilot data from `https://github.com/settings/copilot/features` and `https://github.com/settings/billing/premium_requests_usage`, including consumed-of-included quota fractions and monthly reset extraction for merged `30d` payload.
- **REQ-043**: MUST start provider refresh on service-worker startup before first alarm scheduling and MUST continue recurring updates every configured interval independently of popup lifecycle and debug API enablement.
- **REQ-044**: MUST support manual debug dump export containing raw extraction traces, normalized provider payloads, and timestamped refresh diagnostics when debug access is enabled.
- **REQ-045**: MUST continue rendering the latest successful provider state when network fetch or parser-usable-metric validation fails and MUST surface failure diagnostics through debug instrumentation.
- **REQ-046**: MUST serve runtime message type `api.main.snapshot` regardless of debug API enablement and return latest background-downloaded Claude, Copilot, and Codex percentages, credits, and reset times.
- **REQ-047**: MUST execute debug command `http.get` when debug access is enabled by downloading requested URL and returning HTTP metadata, bounded previews, deterministic body hash, and HTML probe markers.
- **REQ-048**: MUST execute debug diagnostics commands (`parser.run`, `provider.diagnose`, `providers.diagnose`, `providers.pages.get`) when debug access is enabled and return parser payloads, probes, signal traces, payload-usability summaries, and page-blockage diagnostics.
- **REQ-049**: MUST execute debug standard commands `state.get`, `refresh.run`, `logs.get`, `logs.clear`, `interval.get`, and `interval.set` only when debug access is enabled.
- **REQ-050**: MUST emit structured debug log records for debug API command start/completion including command identifier, duration, and success/failure status, and MUST keep logger sinks non-throwing when console or storage writes fail.
- **REQ-051**: MUST return deterministic error responses for all runtime message types prefixed with `debug.` when debug access is disabled, while non-debug APIs continue to operate.
- **REQ-052**: MUST expose runtime configuration messages `config.debug_api.get` and `config.debug_api.set` to read and mutate debug-access enablement with browser-session persistence.
- **REQ-053**: MUST expose popup debug UI controls limited to debug-enable checkbox and status badge, and MUST NOT render export-debug, clear-logs, or fetch-pages buttons in the popup HTML.
- **REQ-054**: MUST keep `guidelines/Google_Extension_API_Reference.md` updated on every Chrome-extension API change and include complete request/response schemas for `api.main.snapshot`, `debug.api.describe`, and `debug.api.execute`.
- **REQ-055**: MUST hide Chrome extension popup window progress bars and quota elements for a provider when that provider has an error and no populated window data, showing only the error message in the card.
- **REQ-056**: MUST render Chrome extension popup window progress bars alongside the error message when a provider has an error but prior successful window data is still present in state.
- **REQ-057**: MUST render Chrome extension popup controls section with only refresh-now button, interval input with set button, debug-enable checkbox, and debug status badge — without export-debug, clear-logs, or fetch-pages buttons.
- **REQ-058**: MUST render popup cards from latest background provider state immediately on popup open without requiring manual refresh, debug API activation, or popup-triggered provider download.
- **REQ-059**: MUST render popup layout with provider tab bar above provider cards and configuration controls below provider cards.

## 4. Test Requirements

Existing automated unit-test coverage under `tests/` is absent (`tests/.place-holder` only), so no behavioral assertions are currently enforced by repository tests.

- **TST-001**: MUST verify `show` rejects unsupported window/provider values with non-zero exit and Click `BadParameter` diagnostics.
- **TST-002**: MUST verify credential precedence by asserting env vars override env-file values and provider stores for at least one provider.
- **TST-003**: MUST verify cache persistence writes only successful non-Claude results, redacts sensitive raw keys before disk serialization, bypasses TTL cache reuse for Claude fetch paths, and persists Claude dual-window snapshot data for HTTP 429 fallback.
- **TST-004**: MUST verify GNOME extension error path sets panel text `Err`, caps displayed error string length to 40 characters, renders quota-only card labels as `Remaining credits: <remaining>/<limit>` with bold `<remaining>`, renders reset labels with `Reset in:` prefix, suppresses `Error: Rate limited. Try again later.` for rate-limit quota payloads, appends `⚠️ Limit reached!` after reset countdown at displayed `100.0%`, renders Copilot `30d` bar/reset placement before remaining-credits text, renders popup labels `AIBar` and `Open AIBar UI`, and verifies `scripts/test-gnome-extension.sh` includes `MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800`.
- **TST-005**: MUST verify Copilot provider always returns `window=30d` regardless of requested window argument.
- **TST-006**: MUST verify `req --here --references` reproduces `docs/REFERENCES.md` without missing symbol entries and preserves Doxygen field extraction for documented symbols.
- **TST-007**: MUST verify GNOME panel percentage labels render in Claude 5h, Claude 7d, Copilot, Codex 5h, Codex 7d order between icon and summary label, enforce provider style classes, enforce bold primary percentages (Claude 5h/Copilot/Codex 5h), and omit labels when source metrics are unavailable.
- **TST-008**: MUST verify `pyproject.toml` declares `[build-system]` with `hatchling`, `[project.scripts]` entry `aibar = "aibar.cli:main"`, runtime `dependencies` list, and `requires-python` constraint.
- **TST-009**: MUST verify `scripts/install-gnome-extension.sh` is executable, passes `bash -n` syntax check, resolves git root correctly, validates source directory, and produces non-zero exit on missing source.
- **TST-010**: MUST verify `Remaining credits: <remaining> / <limit>` appears for Claude, Codex, and Copilot when both quota values exist.
- **TST-011**: MUST verify Claude dual-window text output on HTTP 429 prints rate-limit error only in 5h, keeps 5h usage at `100.0%`, and renders 7d usage/reset values from persisted Claude payload.
- **TST-012**: MUST verify Textual provider cards suppress `Error: Rate limited. Try again later.` and append `⚠️ Limit reached!` after `Resets in:` when displayed usage is `100.0%`.
- **TST-013**: MUST verify Chrome extension manifest wiring opens popup UI with only `claude`, `copilot`, and `codex` tabs and toolbar icon assets resolved from GNOME icon sources.
- **TST-014**: MUST verify Chrome background scheduler performs startup refresh before first alarm, executes provider refresh in required source-page order, and preserves default `180`-second interval with configurable persisted override.
- **TST-015**: MUST verify provider parsers extract required quota/progress fields from localized, bootstrap-script, and escaped-script fixtures, ignore reset-only artifacts, and remain independent from translated display strings.
- **TST-016**: MUST verify Copilot parser merges features and premium pages into one normalized payload consumed by popup `copilot` tab rendering.
- **TST-017**: MUST verify refresh failures preserve last successful tab payloads and emit structured debug records to console and persisted log storage.
- **TST-018**: MUST verify repository no longer contains `src/aibar/chrome-extension/temp/` after implementation changes are completed.
- **TST-019**: MUST verify runtime message handler exposes `api.main.snapshot`, `debug.api.describe`, and `debug.api.execute`, and MUST verify `api.main.snapshot` remains callable while debug is disabled with percentages, credits, and reset values.
- **TST-020**: MUST verify `debug.api.execute` commands `http.get` and `providers.pages.get` enforce URL safety constraints and return bounded previews, deterministic hashes, and per-provider download diagnostics when debug access is enabled.
- **TST-021**: MUST verify debug parser-diagnostics dispatch maps provider keys to parser flows and returns probes, signal diagnostics, parser payloads, window-assignment traces, payload-usability summaries, and metric-key evidence when debug access is enabled.
- **TST-022**: MUST verify debug standard commands route to state/refresh/log/interval handlers with interval constraints and verify logger implementation remains non-throwing on console/storage sink failures.
- **TST-023**: MUST verify all `debug.*` runtime message calls return errors while debug access is disabled, and verify `config.debug_api.set` persists debug enablement across service-worker restarts but resets on browser restart.
- **TST-024**: MUST verify `guidelines/Google_Extension_API_Reference.md` documents `api.main.snapshot`, `debug.api.describe`, `debug.api.execute`, `providers.pages.get`, configuration routes, and disabled-debug error semantics.
- **TST-025**: MUST verify parser fixtures matching current Claude/Copilot/Codex usage-page structures produce correct normalized usage, quota, and reset fields for popup progress-bar rendering.
- **TST-026**: MUST verify Chrome extension manifest declares `host_permissions` entries for `claude.ai`, `chatgpt.com`, and `github.com` enabling authenticated session-credential fetch.
- **TST-027**: MUST verify Chrome extension popup hides window progress bars and quota for an errored provider when no prior window data exists, and renders both windows and error when prior window data is present.
- **TST-028**: MUST verify Chrome extension popup HTML does not contain export-debug, clear-logs, or fetch-pages buttons, and contains only refresh-now, interval input, debug-enable checkbox, and debug status controls.
- **TST-029**: MUST verify Chrome extension persisted refresh interval is restored on service-worker startup and survives simulated browser restart.
- **TST-030**: MUST verify popup initial render consumes existing background snapshot data and displays provider cards without requiring a mandatory foreground refresh.
- **TST-031**: MUST verify popup HTML places provider tab bar before provider cards and places configuration controls after provider cards.

## 5. Evidence

| Requirement ID | Evidence (file + symbol + excerpt) |
|---|---|
| PRJ-001 | `src/aibar/aibar/cli.py` + `main/show/doctor/ui/env/setup/login` + `@main.command()` declarations for all subcommands. |
| PRJ-002 | `src/aibar/aibar/cli.py` + `get_providers` + returns Claude/OpenAI/OpenRouter/Copilot/Codex provider instances keyed by `ProviderName`. |
| PRJ-003 | `src/aibar/aibar/ui.py` + `AIBarUI.compose` + defines `TabPane("Overview")` and `TabPane("Raw JSON")`. |
| PRJ-004 | `src/aibar/gnome-extension/aibar@aibar.panel/metadata.json` + `name/url/github` with owner `Ogekuri`, `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_refreshData/_updateProviderCard` provider-card rendering behavior, and `scripts/test-gnome-extension.sh` exports `MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800`. |
| PRJ-005 | `docs/REFERENCES.md` + repository-wide symbol sections + machine-readable file/symbol index entries. |
| PRJ-006 | `pyproject.toml` + `[build-system]`/`[project]`/`[project.scripts]` sections + `aibar = "aibar.cli:main"` console entry point enabling `uv pip install` and `uvx` execution. |
| PRJ-007 | `README.md` + `## Installation (uv)` section + `uv pip install`, `uv pip uninstall`, `uvx --from` commands. |
| CTN-001 | `src/aibar/aibar/config.py` + `Config.get_token` + env var -> env file -> provider-specific stores (`ClaudeCLIAuth`, `CodexCredentialStore`, `CopilotCredentialStore`). |
| CTN-002 | `src/aibar/aibar/providers/base.py` + `ProviderResult` model + fields `provider/window/metrics/updated_at/raw/error`. |
| CTN-003 | `src/aibar/aibar/providers/*.py` + `fetch` methods + `httpx.AsyncClient(timeout=30.0)` in Claude/OpenAI/OpenRouter/Copilot/Codex providers. |
| CTN-004 | `src/aibar/aibar/cache.py` + `ResultCache` + non-Claude TTL+disk cache plus `src/aibar/aibar/cli.py` + Claude dual-window snapshot persistence for HTTP 429 fallback rendering. |
| CTN-005 | `src/aibar/aibar/config.py` + `PROVIDER_INFO` notes + entries describing unofficial/internal usage for Claude, Copilot, and Codex. |
| CTN-006 | `docs/REFERENCES.md` + full symbol index grouped by source file, regenerated from repository code. |
| CTN-007 | `pyproject.toml` + `[build-system] requires = ["hatchling"]` + `[project]` metadata fields `name`, `version`, `requires-python`, `dependencies`, `[project.scripts]`. |
| DES-001 | `src/aibar/aibar/providers/base.py` + `class BaseProvider(ABC)` + abstract methods `fetch`, `is_configured`, `get_config_help`. |
| DES-002 | `src/aibar/aibar/providers/base.py` + `WindowPeriod/ProviderName` + enum literals `5h/7d/30d/code_review` and provider names; `src/aibar/chrome-extension/parsers.js` + `WINDOW_HINT_REGEX` + `_extractWindowHint` token set. |
| DES-003 | `src/aibar/aibar/cli.py` + `parse_window/parse_provider` + raises `click.BadParameter` for invalid inputs. |
| DES-004 | `src/aibar/aibar/cache.py` + `_sanitize_raw` + redacts keys in sensitive set before file write. |
| DES-005 | `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_loadEnvFromFile` + parses `export KEY=VALUE`, handles quotes/comments/semicolon cleanup. |
| DES-006 | `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `REFRESH_INTERVAL_SECONDS/_startAutoRefresh` + timeout 300 seconds; popup menu has `"Refresh Now"` action. |
| REQ-001 | `src/aibar/aibar/cli.py` + `show` loop + `if not prov.is_configured(): ... continue` and text hint `Set {config.ENV_VARS.get(name)}`. |
| REQ-002 | `src/aibar/aibar/cli.py` + `show` + default-window Claude/Codex dual fetch output rendering. |
| REQ-003 | `src/aibar/aibar/cli.py` + `show` + `json.dumps(output, indent=2)` from `result.model_dump(mode="json")`. |
| REQ-004 | `src/aibar/aibar/cli.py` + `doctor` + configuration status and `_fetch_result(provider, WindowPeriod.HOUR_5)` health check. |
| REQ-005 | `src/aibar/aibar/cli.py` + `setup` + prompts for keys then `write_env_file(updates)` to `ENV_FILE_PATH`. |
| REQ-006 | `src/aibar/aibar/cli.py` + `_login_claude` + missing/expired flows print `claude setup-token` then `sys.exit(1)`. |
| REQ-007 | `src/aibar/aibar/providers/copilot.py` + `CopilotDeviceFlow` and `CopilotProvider.login` + device-code request/poll and `save_token`. |
| REQ-008 | `src/aibar/aibar/ui.py` + `AIBarUI.compose/BINDINGS` and `ProviderCard.watch_result` + provider cards, refresh/window/json controls, rate-limit error-string suppression, and `Resets in: ... ⚠️ Limit reached!` rendering at displayed `100.0%`. |
| REQ-009 | `src/aibar/aibar/ui.py` + `action_refresh/action_window_5h/action_window_7d` + cache `get`/`set` path gated to non-Claude providers, with cache invalidation on window switch. |
| REQ-010 | `src/aibar/aibar/providers/openai_usage.py` + `_get_time_range` + dict maps `"5h"` to `1` day. |
| REQ-011 | `src/aibar/aibar/providers/openrouter.py` + `_get_usage/_parse_response` + cost from usage field and limit metrics from payload. |
| REQ-012 | `src/aibar/aibar/providers/copilot.py` + `fetch` + sets `effective_window = WindowPeriod.DAY_30` and returns that window. |
| REQ-013 | `src/aibar/aibar/providers/codex.py` + `_parse_response` + `window_key = "primary_window" if 5h else "secondary_window"`. |
| REQ-014 | `src/aibar/aibar/providers/codex.py` + `CodexCredentials.needs_refresh` + threshold `age.days >= 8`; `CodexProvider.fetch` calls refresher. |
| REQ-015 | `src/aibar/aibar/providers/codex.py` + `fetch` + catches generic refresh exception and continues (`pass  # Continue with existing token`). |
| REQ-016 | `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_refreshData` + loads env file and `launcher.setenv(key, value, true)` before spawn. |
| REQ-017 | `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_updateUI/_populateProviderCard/_buildPopupMenu` + panel label fallback chain; quota-only cards with bold remaining credits; `Reset in:` prefix; `⚠️ Limit reached!` suffix at displayed `100.0%`; suppression of `Error: Rate limited. Try again later.` for rate-limit quota payloads; Copilot `30d` reset placement; popup labels `AIBar` and `Open AIBar UI`. |
| REQ-018 | `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_handleError` + `this._panelLabel.set_text('Err')` and `message.substring(0, 40)`. |
| REQ-019 | `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_providerOrder` and `_updateUI` sorting + unknown providers rank `999` then lexical order. |
| REQ-020 | `docs/REFERENCES.md` + per-symbol entries containing symbol identifier, file path, and line-range spans. |
| REQ-021 | `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_buildPanelButton/_updateUI` + panel percentage labels inserted between icon and summary label in fixed Claude 5h, Claude 7d, Copilot, Codex 5h, Codex 7d order. |
| REQ-022 | `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_buildPanelButton/_updateUI` + panel labels use provider color classes, primary percentages (Claude 5h/Copilot/Codex 5h) are bold, and labels hide when required metrics are unavailable. |
| REQ-023 | `pyproject.toml` + `[project.scripts]` + `aibar = "aibar.cli:main"` declaration. |
| REQ-024 | `src/aibar/aibar/__main__.py` + `main()` import and invocation from `aibar.cli`. |
| REQ-034 | `src/aibar/aibar/cli.py` + `_format_reset_duration/_print_result` + day-token reset countdown formatting in text output. |
| REQ-035 | `src/aibar/aibar/cli.py` + `_print_result` + remaining-credits line for Claude/Codex/Copilot when `remaining` and `limit` are present. |
| REQ-036 | `src/aibar/aibar/cli.py` + `_fetch_claude_dual/_print_result` + Claude HTTP 429 output keeps 5h error+100% while 7d usage/reset are restored from persisted Claude payload. |
| REQ-037 | `src/aibar/aibar/cli.py` + Claude HTTP 429 fallback path synthesizes deterministic values when no persisted Claude payload is available. |
| TST-001 | `src/aibar/aibar/cli.py` + `parse_window/parse_provider` provide validation points for invalid input diagnostics. |
| TST-002 | `src/aibar/aibar/config.py` + `get_token` implements explicit precedence chain requiring regression coverage. |
| TST-003 | `tests/test_claude_retry_and_cli_cache.py`, `tests/test_claude_dual_cooldown_symmetry.py`, `tests/test_ui_claude_cache_bypass.py`, and `src/aibar/aibar/cache.py` + validate non-Claude cache persistence/redaction, Claude TTL-cache bypass, and Claude dual-window snapshot persistence. |
| TST-004 | `tests/test_extension_quota_label.py` + popup-label assertions (`AIBar`, `Open AIBar UI`), reset-prefix and `⚠️ Limit reached!` assertions, and rate-limit error-string suppression assertions; `tests/test_extension_dev_script.py` + `MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800`; `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_handleError/_populateProviderCard/_buildPopupMenu` coverage. |
| TST-005 | `src/aibar/aibar/providers/copilot.py` + `fetch` hard-codes `effective_window` to `WindowPeriod.DAY_30`. |
| TST-006 | `docs/REFERENCES.md` + generated symbol coverage for tracked `src/` files validates documentation inventory completeness. |
| TST-007 | `tests/test_extension_quota_label.py` + panel-segment assertions for five-label order, provider style classes, bold primary percentages, and missing-metric omission behavior. |
| TST-008 | `tests/test_pyproject_metadata.py` + assertions for `[build-system]` backend, `[project.scripts]` entry, `dependencies` list, and `requires-python` constraint in `pyproject.toml`. |
| TST-010 | `tests/test_reset_pending_message.py` and `src/aibar/aibar/cli.py` + verify remaining-credits rendering path in text output for quota providers. |
| TST-011 | `tests/test_claude_rate_limit_partial_window.py` and `src/aibar/aibar/cli.py` + verify Claude HTTP 429 renders error only in 5h, keeps 5h at 100%, and restores 7d usage/reset from persisted payload. |
| TST-012 | `tests/test_ui_rate_limit_rendering.py` and `src/aibar/aibar/ui.py` + verify Textual card suppresses rate-limit error string and appends `⚠️ Limit reached!` next to reset countdown at displayed `100.0%`. |
| PRJ-008 | `scripts/install-gnome-extension.sh` + copies extension files from `src/aibar/gnome-extension/aibar@aibar.panel/` to `~/.local/share/gnome-shell/extensions/aibar@aibar.panel/` + enables extension via `gnome-extensions enable`. |
| REQ-025 | `scripts/install-gnome-extension.sh` + `git rev-parse --show-toplevel` for project root resolution. |
| REQ-026 | `scripts/install-gnome-extension.sh` + `mkdir -p` for target directory creation. |
| REQ-027 | `scripts/install-gnome-extension.sh` + prerequisite checks for git, project root, source directory, and `metadata.json`. |
| REQ-028 | `scripts/install-gnome-extension.sh` + ANSI color escape sequences for formatted output. |
| REQ-029 | `scripts/install-gnome-extension.sh` + `cp -a` preserving file attributes. |
| REQ-030 | `scripts/install-gnome-extension.sh` + `exit 1` on prerequisite failure with error message. |
| REQ-031 | `scripts/test-gnome-extension.sh` + calls `install-gnome-extension.sh` before nested-shell launch. |
| REQ-032 | `scripts/install-gnome-extension.sh` + `gnome-extensions enable aibar@aibar.panel` after file copy with colored status output. |
| REQ-033 | `scripts/test-gnome-extension.sh` + no subcommand parameter; executes nested-shell launch directly on invocation. |
| TST-009 | `tests/test_install_gnome_extension.py` + executable check, syntax check, git root resolution, source validation, and missing-source exit code assertions. |
| PRJ-009 | `src/aibar/chrome-extension/manifest.json` + popup/action wiring and `src/aibar/chrome-extension/popup.html` + provider-tab set `claude`, `copilot`, `codex`. |
| PRJ-010 | `src/aibar/chrome-extension/background.js` + `_fetchHtml` website downloads and parser pipeline without subprocess `aibar` invocation. |
| CTN-008 | `src/aibar/chrome-extension/background.js` + `REFRESH_INTERVAL_SECONDS = 180`, `INTERVAL_OVERRIDE_STORAGE_KEY`, `_getRefreshIntervalSeconds`, and `_loadPersistedState` interval restoration path. |
| CTN-009 | `src/aibar/chrome-extension/background.js` + `PROVIDER_FETCH_SEQUENCE` and ordered fetch execution in `_refreshAllProviders`. |
| CTN-010 | `src/aibar/chrome-extension/parsers.js` + `_extractProgressMetrics`, `_extractEmbeddedJsonObjects`, `_extractBootstrapJsonFromScriptBody`, and `_extractEscapedScriptMetricCandidates` extraction path without localized UI labels. |
| CTN-011 | `src/aibar/chrome-extension/debug.js` + bound-safe console logger + storage-backed records, `src/aibar/chrome-extension/background.js` + parser/window diagnostic command responses, and `src/aibar/chrome-extension/popup.js` + debug export/clear actions. |
| DES-007 | `src/aibar/chrome-extension/icons/icon16.png`, `icon32.png`, `icon48.png`, `icon128.png` referenced by `manifest.json` icon entries. |
| DES-008 | `src/aibar/chrome-extension/popup.html` + tab/card skeleton and `src/aibar/chrome-extension/popup.css` + GNOME-parity class taxonomy. |
| DES-009 | `src/aibar/chrome-extension/background.js` + service-worker execution unit with alarm-triggered periodic refresh and state publish. |
| DES-010 | `tests/test_chrome_extension_temp_removed.py` + asserts repository absence of `src/aibar/chrome-extension/temp/`. |
| REQ-038 | `src/aibar/chrome-extension/popup.html` + toolbar popup layout with exact `claude`, `copilot`, `codex` tab entries. |
| REQ-039 | `src/aibar/chrome-extension/popup.js` + `_buildWindowRow/_renderProviderCard` progress-card rendering and `popup.css` provider color semantics. |
| REQ-040 | `src/aibar/chrome-extension/background.js` + Claude fetch with `_assertProviderPayloadUsable`, and `src/aibar/chrome-extension/parsers.js` + deterministic `5h/7d` assignment in `parseClaudeUsageHtml`/`_buildWindows`. |
| REQ-041 | `src/aibar/chrome-extension/background.js` + Codex fetch with `_assertProviderPayloadUsable`, and `src/aibar/chrome-extension/parsers.js` + remaining-percent normalization + artifact rejection + `code_review` window in `parseCodexUsageHtml`/`_buildWindows`. |
| REQ-042 | `src/aibar/chrome-extension/background.js` + dual Copilot fetch and `src/aibar/chrome-extension/parsers.js` + `mergeCopilotPayloads` preferring features percentage with premium fraction/reset merge. |
| REQ-043 | `src/aibar/chrome-extension/background.js` + startup refresh in `_loadPersistedState`/`_initialize`, recurring scheduler in `_scheduleRefreshAlarm`, and `usage.updated` publication after refresh completion. |
| REQ-044 | `src/aibar/chrome-extension/debug.js` + `buildDebugBundle` and `src/aibar/chrome-extension/popup.js` + `_exportDebugBundle` JSON dump flow. |
| REQ-045 | `src/aibar/chrome-extension/background.js` + `_assertProviderPayloadUsable` + `_applyProviderFailure` preserving prior payload when parser/network validation fails. |
| TST-013 | `tests/test_chrome_extension_manifest.py` + manifest/popup tab/icon assertions for Chrome extension wiring. |
| TST-014 | `tests/test_chrome_extension_background.py` + startup refresh, alarm interval, and provider-order assertions. |
| TST-015 | `tests/test_chrome_extension_parser.py` + localized + bootstrap + escaped-script fixtures and reset-only artifact rejection assertions. |
| TST-016 | `tests/test_chrome_extension_parser.py` + Copilot features+premium merge assertion for normalized `30d` payload. |
| TST-017 | `tests/test_chrome_extension_background.py` and `tests/test_chrome_extension_debug.py` + fallback state and debug instrumentation assertions. |
| TST-018 | `tests/test_chrome_extension_temp_removed.py` + temp-directory absence assertion. |
| PRJ-011 | `src/aibar/chrome-extension/background.js` + `_handleMessage` routes for `api.main.snapshot`, `debug.api.describe`, and `debug.api.execute` APIs. |
| PRJ-012 | `guidelines/Google_Extension_API_Reference.md` + API contract sections for primary/debug endpoints and configuration routes kept synchronized with implementation. |
| CTN-012 | `src/aibar/chrome-extension/background.js` + `_normalizeDebugUrl` enforces `https` protocol and host allowlist set (`claude.ai`, `chatgpt.com`, `github.com`). |
| CTN-013 | `src/aibar/chrome-extension/background.js` + `_normalizeDebugMaxChars` with bounded preview caps and `http.get` truncation metadata. |
| CTN-014 | `src/aibar/chrome-extension/background.js` + default disabled debug gate (`debugApiEnabled=false`) and command guard in `_ensureDebugAccessEnabled`. |
| CTN-017 | `src/aibar/chrome-extension/background.js` + debug-session persistence load/save hooks backed by browser-session-scoped storage and restore during service-worker initialization. |
| DES-011 | `src/aibar/chrome-extension/background.js` + `_buildMainApiSnapshot`, `_describeDebugApi`, `_executeDebugApiCommand`, and centralized debug guard in `_handleMessage`. |
| DES-012 | `src/aibar/chrome-extension/popup.html` + debug-enable checkbox and `src/aibar/chrome-extension/popup.js` + config route wiring; export/clear-logs/fetch-pages buttons removed from popup, accessible only via debug API. |
| REQ-046 | `src/aibar/chrome-extension/background.js` + unconditional `api.main.snapshot` route in `_handleMessage` and snapshot payload builder exposing percentages/credits/reset fields from latest background state. |
| REQ-047 | `src/aibar/chrome-extension/background.js` + `http.get` command route returning bounded previews, hash, and HTML probe metadata when debug access is enabled. |
| REQ-048 | `src/aibar/chrome-extension/background.js` + `parser.run`/`provider.diagnose`/`providers.diagnose`/`providers.pages.get` command dispatch with parser diagnostics, payload assertions, and per-page related-content diagnostics behind debug-access guard. |
| REQ-049 | `src/aibar/chrome-extension/background.js` + debug standard command routes `state.get`, `refresh.run`, `logs.get`, `logs.clear`, `interval.get`, and `interval.set` behind debug-access guard. |
| REQ-050 | `src/aibar/chrome-extension/background.js` + structured debug command lifecycle logging and `src/aibar/chrome-extension/debug.js` + non-throwing sink wrappers (`_resolveConsoleMethod`, `_emitConsoleSafe`, guarded `appendDebugRecord`). |
| REQ-051 | `src/aibar/chrome-extension/background.js` + `_ensureDebugAccessEnabled` deterministic rejection path for all `debug.*` message types when debug access is disabled. |
| REQ-052 | `src/aibar/chrome-extension/background.js` + `config.debug_api.get`/`config.debug_api.set` handlers with browser-session persistence for debug-enable state. |
| REQ-058 | `src/aibar/chrome-extension/popup.js` + initial snapshot fetch path that renders cards from shared background state before any manual refresh action. |
| REQ-059 | `src/aibar/chrome-extension/popup.html` + DOM order places provider tab bar before cards and configuration controls after cards. |
| REQ-053 | `src/aibar/chrome-extension/popup.html` + debug-enable checkbox and status badge only; `src/aibar/chrome-extension/popup.js` + runtime enablement wiring without export/clear-logs/fetch-pages buttons. |
| REQ-054 | `guidelines/Google_Extension_API_Reference.md` + complete request/response schemas and disabled-debug error semantics for primary/debug extension APIs. |
| TST-019 | `tests/test_chrome_extension_debug_api.py` + route assertions for `api.main.snapshot`/debug endpoints and snapshot availability while debug is disabled. |
| TST-020 | `tests/test_chrome_extension_debug_api.py` + HTTPS allowlist validation, `http.get` preview/hash/probe assertions, and `providers.pages.get` aggregate provider-page diagnostics assertions. |
| TST-021 | `tests/test_chrome_extension_debug_api.py` + parser/provider/providers-diagnose dispatch assertions plus `providers.pages.get` parser/window-analysis payload checks. |
| TST-022 | `tests/test_chrome_extension_debug_api.py` + debug standard-command/lifecycle assertions and `tests/test_chrome_extension_debug.py` + logger non-throwing sink-wrapper assertions. |
| TST-023 | `tests/test_chrome_extension_debug_api.py` + disabled-debug rejection assertions and session-persistent debug-enable lifecycle assertions across service-worker restart simulation. |
| TST-024 | `tests/test_chrome_extension_api_reference.py` + API-reference coverage assertions for primary/debug/configuration routes including `providers.pages.get` and disabled-debug error semantics. |
| TST-025 | `tests/test_chrome_extension_parser.py` + fixtures `claude_usage_current_signals.html`, `copilot_features_current_signals.html`, `copilot_premium_current_signals.html`, `codex_usage_current_signals.html`, and `codex_usage_noise_fractions.html` validating current usage normalization and noise-artifact rejection. |
| CTN-015 | `src/aibar/chrome-extension/manifest.json` + `host_permissions` entries for `https://claude.ai/*`, `https://chatgpt.com/*`, `https://github.com/*` enabling `credentials: "include"` in service-worker `fetch()`. |
| REQ-055 | `src/aibar/chrome-extension/popup.js` + `_renderProviderCard` + error-only rendering path hides window container when provider state has error and no populated windows. |
| REQ-056 | `src/aibar/chrome-extension/popup.js` + `_renderProviderCard` + renders window progress bars alongside error when prior successful window data persists in provider state. |
| TST-026 | `tests/test_chrome_extension_manifest.py` + `host_permissions` assertions for `claude.ai`, `chatgpt.com`, and `github.com` domains. |
| TST-027 | `tests/test_chrome_extension_popup.py` + popup error-rendering assertions for hidden windows on error-only state and visible windows when prior data exists. |
| CTN-016 | `src/aibar/chrome-extension/background.js` + `INTERVAL_OVERRIDE_STORAGE_KEY` persistence in `_getRefreshIntervalSeconds` and restoration in `_loadPersistedState` before first alarm scheduling. |
| REQ-057 | `src/aibar/chrome-extension/popup.html` + controls section containing only refresh-now, interval input/set, debug-enable checkbox, and debug status badge. |
| TST-030 | `tests/test_chrome_extension_popup.py` + popup boot render assertions using preloaded background snapshot state without forced foreground refresh. |
| TST-031 | `tests/test_chrome_extension_popup.py` + popup HTML structure assertions for tab-before-cards and controls-after-cards ordering. |
