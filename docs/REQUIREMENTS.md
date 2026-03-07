---
title: "AIBar Requirements"
description: Software requirements specification
version: "0.3.14"
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

Performance note: explicit caching optimization uses persistent CLI cache (`~/.config/aibar/cache.json`), idle-time gating (`~/.config/aibar/idle-time.json`), and configurable provider-call throttling (`api_call_delay_seconds`) to minimize API request volume.

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

### 2.2 Project Constraints
- **CTN-001**: MUST resolve provider credentials with precedence: environment variable, then `~/.config/aibar/env`, then provider-specific local credential stores.
- **CTN-002**: MUST represent provider fetch output with `ProviderResult` containing `provider`, `window`, `metrics`, `updated_at`, `raw`, and optional `error`.
- **CTN-003**: MUST perform external HTTP API calls with `httpx.AsyncClient(timeout=30.0)` for provider integrations.
- **CTN-004**: MUST persist the latest successful multi-provider `show` dataset in `~/.config/aibar/cache.json` using exactly the same top-level and nested JSON schema emitted by `aibar show --json`.
- **CTN-005**: MAY depend on unofficial/internal endpoints when official usage APIs are unavailable for Claude, Copilot, or Codex integrations.
- **CTN-006**: MUST keep `docs/REFERENCES.md` synchronized with symbols defined under `src/` and `.github/workflows/`.
- **CTN-007**: MUST declare `hatchling` as `[build-system]` backend in `pyproject.toml` with `[project]` metadata including `name`, `version`, `requires-python`, `dependencies`, and `[project.scripts]` console entry point.
- **CTN-008**: MUST persist runtime throttling configuration in `~/.config/aibar/config.json` with keys `idle_delay_seconds` and `api_call_delay_seconds`.
- **CTN-009**: MUST persist idle-time state in `~/.config/aibar/idle-time.json` with epoch and human-readable fields for `last_success_at` and `idle_until`.

## 3. Requirements

### 3.1 Design and Implementation
- **DES-001**: MUST define `BaseProvider` as an abstract interface with `fetch`, `is_configured`, and `get_config_help`.
- **DES-002**: MUST encode supported windows as `5h`, `7d`, `30d`, and `code_review` and provider names as `claude`, `openai`, `openrouter`, `copilot`, and `codex`.
- **DES-003**: MUST reject invalid CLI window values and provider values using Click `BadParameter`.
- **DES-004**: MUST sanitize sensitive keys (`token`, `key`, `secret`, `password`, `authorization`) from cached raw payloads before disk writes.
- **DES-005**: MUST parse env-file assignments with optional `export`, quoted values, and inline comments in GNOME extension env loading.
- **DES-006**: MUST auto-refresh GNOME extension data every 300 seconds and also support manual refresh from the popup menu.

### 3.2 Functions
- **REQ-001**: MUST skip unconfigured providers in `show` output and print missing environment-variable hints when text mode is used.
- **REQ-002**: MUST print both 5-hour and 7-day outputs for Claude and Codex when `show` runs with default window and non-JSON mode.
- **REQ-003**: MUST emit pretty-printed JSON (`indent=2`) for `show --json` using either refreshed provider results or cache payloads without schema changes.
- **REQ-004**: MUST run provider health checks in `doctor` using the 5-hour window and report per-provider configuration and test status.
- **REQ-005**: MUST prompt `setup` for `idle_delay_seconds` (default `300`) first and `api_call_delay_seconds` (default `20`) second, then persist both values in `~/.config/aibar/config.json`.
- **REQ-006**: MUST fail Claude login when CLI credentials are missing or expired and MUST print `claude setup-token` remediation guidance.
- **REQ-007**: MUST execute GitHub device-flow login for Copilot and save the token in `~/.config/aibar/copilot.json`.
- **REQ-008**: MUST render Textual provider cards for all providers, support refresh, support 5h/7d switching, support JSON-tab toggling, suppress `Error: Rate limited. Try again later.`, and append `⚠️ Limit reached!` after `Resets in:` at displayed `100.0%`.
- **REQ-009**: MUST skip provider refresh when `idle_until` in `~/.config/aibar/idle-time.json` is in the future and MUST serve `show` data from `~/.config/aibar/cache.json`.
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
- **REQ-038**: MUST set `last_success_at` to refresh completion time and `idle_until` to `last_success_at + idle_delay_seconds` after every successful provider refresh, then persist epoch and human-readable values in `~/.config/aibar/idle-time.json`.
- **REQ-039**: MUST support `show --force` to delete `~/.config/aibar/idle-time.json`, bypass idle-time gating for the current run, and execute a fresh provider refresh.
- **REQ-040**: MUST enforce at least `api_call_delay_seconds` between consecutive provider API requests during refresh execution, with default `20` seconds when configuration is missing.
- **REQ-041**: MUST update idle-time on HTTP `429` using `max(retry_after_seconds, idle_delay_seconds)` and, when multiple `429` responses occur, MUST persist the largest computed `idle_until`.
- **REQ-042**: MUST minimize provider API requests during refresh by reusing already-fetched results within the run and by serving cached data whenever idle-time gating disables refresh.

## 4. Test Requirements

Existing automated unit-test coverage under `tests/` is absent (`tests/.place-holder` only), so no behavioral assertions are currently enforced by repository tests.

- **TST-001**: MUST verify `show` rejects unsupported window/provider values with non-zero exit and Click `BadParameter` diagnostics.
- **TST-002**: MUST verify credential precedence by asserting env vars override env-file values and provider stores for at least one provider.
- **TST-003**: MUST verify successful refresh writes `~/.config/aibar/cache.json` with exact `show --json` schema and writes `last_success_at`/`idle_until` epoch plus human-readable fields in `~/.config/aibar/idle-time.json`.
- **TST-004**: MUST verify GNOME extension error path sets panel text `Err`, caps displayed error string length to 40 characters, renders quota-only card labels as `Remaining credits: <remaining>/<limit>` with bold `<remaining>`, renders reset labels with `Reset in:` prefix, suppresses `Error: Rate limited. Try again later.` for rate-limit quota payloads, appends `⚠️ Limit reached!` after reset countdown at displayed `100.0%`, renders Copilot `30d` bar/reset placement before remaining-credits text, renders popup labels `AIBar` and `Open AIBar UI`, and verifies `scripts/test-gnome-extension.sh` includes `MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800`.
- **TST-005**: MUST verify Copilot provider always returns `window=30d` regardless of requested window argument.
- **TST-006**: MUST verify `req --here --references` reproduces `docs/REFERENCES.md` without missing symbol entries and preserves Doxygen field extraction for documented symbols.
- **TST-007**: MUST verify GNOME panel percentage labels render in Claude 5h, Claude 7d, Copilot, Codex 5h, Codex 7d order between icon and summary label, enforce provider style classes, enforce bold primary percentages (Claude 5h/Copilot/Codex 5h), and omit labels when source metrics are unavailable.
- **TST-008**: MUST verify `pyproject.toml` declares `[build-system]` with `hatchling`, `[project.scripts]` entry `aibar = "aibar.cli:main"`, runtime `dependencies` list, and `requires-python` constraint.
- **TST-009**: MUST verify `scripts/install-gnome-extension.sh` is executable, passes `bash -n` syntax check, resolves git root correctly, validates source directory, and produces non-zero exit on missing source.
- **TST-010**: MUST verify `Remaining credits: <remaining> / <limit>` appears for Claude, Codex, and Copilot when both quota values exist.
- **TST-011**: MUST verify HTTP `429` handling persists idle-time using `max(retry_after_seconds, idle_delay_seconds)` and keeps the largest computed `idle_until` when multiple rate-limit responses occur in one refresh run.
- **TST-012**: MUST verify Textual provider cards suppress `Error: Rate limited. Try again later.` and append `⚠️ Limit reached!` after `Resets in:` when displayed usage is `100.0%`.
- **TST-013**: MUST verify `setup` prompts idle-delay first and API-call delay second, applies defaults `300` and `20`, and persists both values into `~/.config/aibar/config.json`.
- **TST-014**: MUST verify `show` skips provider API calls and serves `~/.config/aibar/cache.json` when `idle_until` is in the future, and refreshes providers when idle-time file is missing or expired.
- **TST-015**: MUST verify `show --force` removes `~/.config/aibar/idle-time.json`, bypasses idle-time gating for current execution, refreshes providers, and recreates idle-time metadata.
- **TST-016**: MUST verify refresh execution enforces configured inter-call delay between provider API requests, using `20` seconds when `api_call_delay_seconds` is absent.

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
| CTN-004 | `src/aibar/aibar/cache.py` + cache read/write helpers plus `src/aibar/aibar/cli.py` + CLI dataset persistence to `~/.config/aibar/cache.json` matching `show --json` schema. |
| CTN-005 | `src/aibar/aibar/config.py` + `PROVIDER_INFO` notes + entries describing unofficial/internal usage for Claude, Copilot, and Codex. |
| CTN-006 | `docs/REFERENCES.md` + full symbol index grouped by source file, regenerated from repository code. |
| CTN-007 | `pyproject.toml` + `[build-system] requires = ["hatchling"]` + `[project]` metadata fields `name`, `version`, `requires-python`, `dependencies`, `[project.scripts]`. |
| CTN-008 | `src/aibar/aibar/config.py` + runtime throttle config load/save helpers using `~/.config/aibar/config.json` keys `idle_delay_seconds` and `api_call_delay_seconds`. |
| CTN-009 | `src/aibar/aibar/cli.py` + idle-time load/save logic managing epoch and human-readable `last_success_at` and `idle_until` in `~/.config/aibar/idle-time.json`. |
| DES-001 | `src/aibar/aibar/providers/base.py` + `class BaseProvider(ABC)` + abstract methods `fetch`, `is_configured`, `get_config_help`. |
| DES-002 | `src/aibar/aibar/providers/base.py` + `WindowPeriod/ProviderName` + enum literals `5h/7d/30d/code_review` and provider names. |
| DES-003 | `src/aibar/aibar/cli.py` + `parse_window/parse_provider` + raises `click.BadParameter` for invalid inputs. |
| DES-004 | `src/aibar/aibar/cache.py` + `_sanitize_raw` + redacts keys in sensitive set before file write. |
| DES-005 | `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_loadEnvFromFile` + parses `export KEY=VALUE`, handles quotes/comments/semicolon cleanup. |
| DES-006 | `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `REFRESH_INTERVAL_SECONDS/_startAutoRefresh` + timeout 300 seconds; popup menu has `"Refresh Now"` action. |
| REQ-001 | `src/aibar/aibar/cli.py` + `show` loop + `if not prov.is_configured(): ... continue` and text hint `Set {config.ENV_VARS.get(name)}`. |
| REQ-002 | `src/aibar/aibar/cli.py` + `show` + default-window Claude/Codex dual fetch output rendering. |
| REQ-003 | `src/aibar/aibar/cli.py` + `show` JSON renderer emits `indent=2` from refreshed or cache-loaded payload without schema drift. |
| REQ-004 | `src/aibar/aibar/cli.py` + `doctor` + configuration status and `_fetch_result(provider, WindowPeriod.HOUR_5)` health check. |
| REQ-005 | `src/aibar/aibar/cli.py` + `setup` prompts `idle_delay_seconds` then `api_call_delay_seconds` with defaults `300` and `20`, then persists `~/.config/aibar/config.json`. |
| REQ-006 | `src/aibar/aibar/cli.py` + `_login_claude` + missing/expired flows print `claude setup-token` then `sys.exit(1)`. |
| REQ-007 | `src/aibar/aibar/providers/copilot.py` + `CopilotDeviceFlow` and `CopilotProvider.login` + device-code request/poll and `save_token`. |
| REQ-008 | `src/aibar/aibar/ui.py` + `AIBarUI.compose/BINDINGS` and `ProviderCard.watch_result` + provider cards, refresh/window/json controls, rate-limit error-string suppression, and `Resets in: ... ⚠️ Limit reached!` rendering at displayed `100.0%`. |
| REQ-009 | `src/aibar/aibar/cli.py` + `show` idle-time gate reads `~/.config/aibar/idle-time.json` and serves `~/.config/aibar/cache.json` without provider refresh while idle window is active. |
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
| REQ-038 | `src/aibar/aibar/cli.py` + successful refresh path computes `idle_until = last_success_at + idle_delay_seconds` and writes epoch/human-readable values to `~/.config/aibar/idle-time.json`. |
| REQ-039 | `src/aibar/aibar/cli.py` + `show --force` removes idle-time file and bypasses idle-time gate for current execution. |
| REQ-040 | `src/aibar/aibar/cli.py` + refresh scheduler enforces configured `api_call_delay_seconds` between consecutive provider API requests. |
| REQ-041 | `src/aibar/aibar/cli.py` + HTTP 429 handling uses `retry-after` and `idle_delay_seconds` to persist the largest computed `idle_until`. |
| REQ-042 | `src/aibar/aibar/cli.py` + refresh pipeline reuses in-run results and idle-time cache short-circuiting to minimize provider API calls. |
| TST-001 | `src/aibar/aibar/cli.py` + `parse_window/parse_provider` provide validation points for invalid input diagnostics. |
| TST-002 | `src/aibar/aibar/config.py` + `get_token` implements explicit precedence chain requiring regression coverage. |
| TST-003 | `tests/test_cli_idle_cache.py` + assertions for cache schema parity with `show --json` and idle-time epoch/human-readable field persistence after successful refresh. |
| TST-004 | `tests/test_extension_quota_label.py` + popup-label assertions (`AIBar`, `Open AIBar UI`), reset-prefix and `⚠️ Limit reached!` assertions, and rate-limit error-string suppression assertions; `tests/test_extension_dev_script.py` + `MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800`; `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_handleError/_populateProviderCard/_buildPopupMenu` coverage. |
| TST-005 | `src/aibar/aibar/providers/copilot.py` + `fetch` hard-codes `effective_window` to `WindowPeriod.DAY_30`. |
| TST-006 | `docs/REFERENCES.md` + generated symbol coverage for tracked `src/` files validates documentation inventory completeness. |
| TST-007 | `tests/test_extension_quota_label.py` + panel-segment assertions for five-label order, provider style classes, bold primary percentages, and missing-metric omission behavior. |
| TST-008 | `tests/test_pyproject_metadata.py` + assertions for `[build-system]` backend, `[project.scripts]` entry, `dependencies` list, and `requires-python` constraint in `pyproject.toml`. |
| TST-010 | `tests/test_reset_pending_message.py` and `src/aibar/aibar/cli.py` + verify remaining-credits rendering path in text output for quota providers. |
| TST-011 | `tests/test_cli_idle_time_429.py` + multi-429 scenarios verify `max(retry_after_seconds, idle_delay_seconds)` and largest `idle_until` persistence. |
| TST-012 | `tests/test_ui_rate_limit_rendering.py` and `src/aibar/aibar/ui.py` + verify Textual card suppresses rate-limit error string and appends `⚠️ Limit reached!` next to reset countdown at displayed `100.0%`. |
| TST-013 | `tests/test_setup_runtime_config.py` + setup prompt-order/default assertions and `~/.config/aibar/config.json` persistence checks for idle/API delays. |
| TST-014 | `tests/test_cli_idle_cache.py` + idle-time future/missing/expired branches verify cache-serving behavior and provider-call gating in `show`. |
| TST-015 | `tests/test_cli_idle_force.py` + `show --force` verifies idle-time file deletion, gate bypass, refresh invocation, and idle-time regeneration. |
| TST-016 | `tests/test_cli_provider_throttle.py` + refresh timing assertions verify configured inter-call delay and default `20`-second fallback. |
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
