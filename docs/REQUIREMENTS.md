---
title: "AIBar Requirements"
description: Software requirements specification
version: "0.3.22"
date: "2026-03-14"
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

Performance note: explicit caching optimization uses persistent CLI cache (`~/.cache/aibar/cache.json`), idle-time gating (`~/.cache/aibar/idle-time.json`), and configurable provider-call throttling (`api_call_delay_seconds`) to minimize API request volume.

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
- **PRJ-001**: MUST expose CLI subcommands `show`, `doctor`, `env`, `setup`, `login`, `gnome-install`, and `gnome-uninstall` under one Click command group.
- **PRJ-002**: MUST aggregate provider metrics through a normalized provider contract for `claude`, `openai`, `openrouter`, `copilot`, and `codex`.
- **PRJ-004**: MUST provide a GNOME Shell panel extension named `AIBar Monitor` that executes `aibar show --json`, renders provider-specific cards, sets metadata owner identifiers (`url`, `github`) to `Ogekuri`, and forces `scripts/test-gnome-extension.sh` nested-shell resolution to `1024x800` via `MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800`.
- **PRJ-005**: MUST maintain a machine-readable symbol inventory for repository code documentation under `docs/REFERENCES.md`.
- **PRJ-006**: MUST provide a PEP 621-compliant `pyproject.toml` at repository root enabling installation via `uv pip install` and live execution via `uvx --from git+https://github.com/Ogekuri/AIBar.git aibar <command>`.
- **PRJ-007**: MUST document in `README.md` a dedicated section covering `uv`-based installation, removal, and `uvx` live execution instructions, plus GeminiAI prerequisites (Desktop OAuth client, BigQuery dataset, required APIs).
- **PRJ-008**: MUST provide `aibar gnome-install` CLI command that installs or updates GNOME extension files from the installed package source directory to `~/.local/share/gnome-shell/extensions/aibar@aibar.panel/` and enables the extension via `gnome-extensions enable`.
- **PRJ-009**: MUST execute startup update checks and lifecycle flags `--upgrade`, `--uninstall`, `--version`, and `--ver` for program `aibar`.
- **PRJ-010**: MUST package all runtime files required by `aibar` so local execution and `uv tool install` execution remain behaviorally equivalent.
- **PRJ-011**: MUST keep GNOME extension contract documentation in `docs/REQUIREMENTS.md`, `docs/WORKFLOW.md`, and `docs/REFERENCES.md`; repository source tree MUST NOT contain `src/aibar/plans/Gnome.plan.md`.

### 2.2 Project Constraints
- **CTN-001**: MUST resolve provider credentials with precedence: environment variable, then `~/.config/aibar/env`, then provider-specific local credential stores.
- **CTN-002**: MUST represent provider fetch output with `ProviderResult` containing `provider`, `window`, `metrics`, `updated_at`, `raw`, and optional `error`; `UsageMetrics` MUST include `currency_symbol: str` (default `"$"`) annotating all monetary fields (`cost`, `remaining`, `limit`).
- **CTN-003**: MUST perform external HTTP API calls with `httpx.AsyncClient(timeout=30.0)` for provider integrations.
- **CTN-004**: MUST persist `~/.cache/aibar/cache.json` as the canonical store for per-provider, per-window last-success payload snapshots and last-attempt status metadata.
- **CTN-005**: MAY depend on unofficial/internal endpoints when official usage APIs are unavailable for Claude, Copilot, or Codex integrations.
- **CTN-006**: MUST keep `docs/REFERENCES.md` synchronized with symbols defined under `src/` and `.github/workflows/`.
- **CTN-007**: MUST declare `hatchling` as `[build-system]` backend in `pyproject.toml` with `[project]` metadata including `name`, `version`, `requires-python`, `dependencies`, and `[project.scripts]` console entry point.
- **CTN-008**: MUST persist runtime configuration in `~/.config/aibar/config.json` with keys `idle_delay_seconds`, `api_call_delay_milliseconds`, `gnome_refresh_interval_seconds`, `billing_data`, and `currency_symbols` (mapping provider name → currency symbol string; default `"$"` per provider when key is absent).
- **CTN-009**: MUST persist provider-scoped idle-time state in `~/.cache/aibar/idle-time.json`, where each provider key stores epoch and human-readable `last_success_at` and `idle_until` fields.
- **CTN-010**: MUST update `cache.json` payload fields only after successful fetch for the same provider/window and MUST preserve previous payload fields on failed fetch attempts, including HTTP `429`.
- **CTN-011**: MUST fetch latest release metadata from `https://api.github.com/repos/Ogekuri/AIBar/releases/latest` for startup update checks.
- **CTN-012**: MUST use hardcoded startup update-check constants `idle_delay_seconds=300` and `http_timeout_seconds=2`.
- **CTN-013**: MUST persist startup update-check idle state in `$HOME/.github_api_idle-time.aibar` JSON with epoch and human-readable `last_success_at` and `idle_until`.
- **CTN-014**: MUST perform at most one startup update HTTP check per 300 seconds unless `$HOME/.github_api_idle-time.aibar` is missing or expired.
- **CTN-015**: MUST execute lifecycle subprocess commands exactly as `uv tool install aibar --force --from git+https://github.com/Ogekuri/AIBar.git` and `uv tool uninstall aibar`.

## 3. Requirements

### 3.1 Design and Implementation
- **DES-001**: MUST define `BaseProvider` as an abstract interface with `fetch`, `is_configured`, and `get_config_help`.
- **DES-002**: MUST encode supported windows as `5h`, `7d`, `30d`, and `code_review` and provider names as `claude`, `openai`, `openrouter`, `copilot`, and `codex`.
- **DES-003**: MUST reject invalid CLI window values and provider values using Click `BadParameter`.
- **DES-004**: MUST sanitize sensitive keys (`token`, `key`, `secret`, `password`, `authorization`) from cached raw payloads before disk writes.
- **DES-005**: MUST parse env-file assignments with optional `export`, quoted values, and inline comments in GNOME extension env loading.
- **DES-006**: MUST auto-refresh GNOME extension data at interval read from `extension.gnome_refresh_interval_seconds` in the `aibar show --json` output (fallback `60` seconds when field absent), execute popup `Refresh Now` actions with `aibar show --json --force`, and apply the new interval on each successful data refresh.
- **DES-007**: MUST use provider-registry-driven instantiation so adding `geminiai` introduces no duplicated control-flow branches in `show`, `doctor`, `setup`, `login`, or refresh/load orchestration.
- **DES-008**: MUST include `geminiai` in provider-name typing and validation while preserving compatibility for `claude`, `openai`, `openrouter`, `copilot`, and `codex`.

### 3.2 Functions
- **REQ-001**: MUST skip unconfigured providers in `show` output and print missing environment-variable hints when text mode is used.
- **REQ-002**: MUST print both 5-hour and 7-day outputs for Claude and Codex when `show` runs with default window and non-JSON mode.
- **REQ-003**: MUST emit pretty-printed JSON (`indent=2`) for `show --json` with top-level sections `payload` (per-provider/window data), `status` (last-attempt state), and `extension` (GNOME extension runtime config including `gnome_refresh_interval_seconds`).
- **REQ-004**: MUST run provider health checks in `doctor` using the 5-hour window and report per-provider configuration and test status.
- **REQ-005**: MUST prompt `setup` for `idle_delay_seconds` (default `300`) first, `api_call_delay_milliseconds` (default `1000`) second, `gnome_refresh_interval_seconds` (default `60`) third, and `billing_data` (default `billing_data`) fourth, then persist values in `~/.config/aibar/config.json`.
- **REQ-006**: MUST fail Claude login when CLI credentials are missing or expired and MUST print `claude setup-token` remediation guidance.
- **REQ-007**: MUST execute GitHub device-flow login for Copilot and save the token in `~/.config/aibar/copilot.json`.
- **REQ-009**: MUST execute provider retrieval for `show` in this order: force-flag handling, per-provider idle-time evaluation, per-provider conditional refresh to `~/.cache/aibar/cache.json`, then data load from `~/.cache/aibar/cache.json`.
- **REQ-010**: MUST map OpenAI `5h` requests to a one-day API range before requesting usage and costs.
- **REQ-011**: MUST derive OpenRouter `cost` from window-specific usage fields (`usage_daily`, `usage_weekly`, `usage_monthly`) and include `limit` and `limit_remaining`.
- **REQ-012**: MUST ignore requested window for Copilot fetch and return results with effective window `30d`.
- **REQ-013**: MUST select Codex rate-limit primary window for `5h` and secondary window for other requested windows.
- **REQ-014**: MUST attempt Codex token refresh when refresh token exists and `last_refresh` age is at least eight days.
- **REQ-015**: SHOULD continue Codex fetch with existing credentials when non-authentication refresh exceptions occur, leaving refresh failures non-fatal.
- **REQ-016**: MUST load `~/.config/aibar/env` into subprocess environment before GNOME extension executes `aibar show --json` and before popup `Refresh Now` executes `aibar show --json --force`.
- **REQ-017**: Quota-only cards MUST render `Remaining credits: <remaining>/<limit>` with `<remaining>` in bold; reset labels in extension cards MUST start with `Reset in:` and append `⚠️ Limit reached!` at displayed `100.0%`; rate-limit quota payloads MUST NOT render `Error: Rate limited. Try again later.`; Copilot cards MUST render a `30d` window bar with reset text directly below that bar and before remaining-credits text; popup header/action labels MUST render `AIBar` branding (`AIBar`, `Open AIBar Report`); each provider card tab MUST render `Updated: <HH:MM>, Next: <HH:MM>` aligned bottom-right using `aibar-reset-label` font/color, where `Updated` is sourced from provider `updated_at` and `Next` is computed as `updated_at + gnome_refresh_interval_seconds`.
- **REQ-018**: MUST set GNOME panel label to `Err` and truncate popup error text to 40 characters when command execution or JSON parsing fails.
- **REQ-019**: SHOULD order extension provider tabs/cards by `claude`, `openrouter`, `copilot`, `codex`, with providers not listed in ordering array appended alphabetically.
- **REQ-020**: MUST include each discovered source symbol in `docs/REFERENCES.md` with file path, symbol kind, line-range evidence, and parsed Doxygen fields (`@brief`, `@param`, `@return`, `@raises`) when present in source declarations.
- **REQ-021**: MUST render GNOME panel status labels after the icon in this order: Claude 5h percentage, Claude 7d percentage, Claude cost, OpenRouter cost, Copilot 30d percentage, Codex 5h percentage, Codex 7d percentage, Codex cost, OpenAI cost, GeminiAI cost.
- **REQ-022**: MUST style GNOME panel tab and label fonts with provider classes and bright colors: Claude red, OpenRouter orange, Copilot yellow, Codex green, OpenAI blue, GeminiAI purple; cost labels MUST use the same font family, render when numeric value is `0`, and hide only when cost metric is unavailable.
- **REQ-023**: MUST declare a `[project.scripts]` entry `aibar = "aibar.cli:main"` in `pyproject.toml` so that `uv pip install` and `uvx` resolve the `aibar` console command.
- **REQ-024**: MUST provide `src/aibar/aibar/__main__.py` that delegates to `aibar.cli:main` to enable `python -m aibar` execution.
- **REQ-025**: MUST resolve GNOME extension source files from the installed package location via Python module path resolution in `gnome-install`, independent of git repository or working directory.
- **REQ-026**: MUST create target directory `~/.local/share/gnome-shell/extensions/aibar@aibar.panel/` if it does not exist before copying extension files in `gnome-install`.
- **REQ-027**: MUST validate that the extension source directory is non-empty and contains `metadata.json` before copying in `gnome-install`.
- **REQ-028**: MUST produce colored, formatted terminal output via Click styling for status, success, error, and informational messages in `gnome-install` and `gnome-uninstall` commands.
- **REQ-029**: MUST copy all files from the package extension source directory to target directory, replacing any existing files, in `gnome-install`.
- **REQ-030**: MUST exit with non-zero status and descriptive error message when any prerequisite check fails in `gnome-install`.
- **REQ-031**: MUST invoke `aibar gnome-install` before launching the nested shell in `scripts/test-gnome-extension.sh` to update extension files.
- **REQ-032**: MUST enable the extension via `gnome-extensions enable aibar@aibar.panel` after successful file copy in `gnome-install` with colored status output.
- **REQ-033**: `scripts/test-gnome-extension.sh` MUST NOT accept any subcommand parameter; it MUST execute the nested-shell launch directly on invocation without arguments.
- **REQ-034**: MUST render reset countdown as `Resets in: <d>d <h>h <m>m` for durations >= 24 hours in CLI text output.
- **REQ-035**: MUST print `Remaining credits: <remaining> / <limit>` for Claude, Codex, and Copilot when both values exist in CLI text output.
- **REQ-036**: MUST render Claude HTTP 429 as partial-window output: 5h shows `Error: Rate limited. Try again later.` and `Usage: ... 100.0%`; 5h reset and all 7d usage/reset values MUST use persisted Claude payload when available.
- **REQ-037**: MUST use synthetic Claude partial-window fallback values when persisted Claude payload is unavailable during HTTP 429 rendering.
- **REQ-038**: MUST update only the refreshed provider idle-time entry after success by setting `last_success_at` to refresh completion time and `idle_until` to `last_success_at + idle_delay_seconds`, then persist epoch and human-readable values in `~/.cache/aibar/idle-time.json`.
- **REQ-039**: MUST support force-refresh handling that deletes `~/.cache/aibar/idle-time.json`, bypasses idle-time gating for the current execution, and executes a fresh provider refresh before loading `~/.cache/aibar/cache.json`.
- **REQ-040**: MUST enforce at least `api_call_delay_milliseconds` between consecutive provider API requests during refresh execution, with default `1000` milliseconds when configuration is missing.
- **REQ-041**: MUST update idle-time only for the rate-limited provider on HTTP `429` using `max(retry_after_seconds, idle_delay_seconds)`; non-rate-limited providers MUST continue scheduling with `idle_delay_seconds`.
- **REQ-042**: MUST minimize provider API requests and cache I/O by reusing in-memory cache and idle-time state within each refresh cycle and persisting `cache.json` or `idle-time.json` only when content changes.
- **REQ-043**: MUST centralize refresh and load logic for `~/.cache/aibar/cache.json` into shared internal functions reused by CLI `show` refresh and output workflows.
- **REQ-044**: MUST persist per-provider, per-window last-attempt status in `cache.json` with fields `result`, `error`, and `updated_at`, where `result` is `OK` or `FAIL`.
- **REQ-045**: MUST overwrite a provider/window payload in `cache.json` only when the current fetch for that provider/window succeeds.
- **REQ-046**: MUST preserve the previous provider/window payload in `cache.json` when the current fetch for that provider/window fails, including HTTP `429`.
- **REQ-047**: MUST store and load all last-success fallback payloads from `~/.cache/aibar/cache.json` and MUST NOT require `~/.cache/aibar/claude_dual_last_success.json`.
- **REQ-048**: `scripts/claude_token_refresh.sh` `do_refresh()` MUST truncate `LOG_FILE` to zero bytes before writing any log entries, so each `once` invocation and each daemon refresh cycle produces a standalone log containing only entries from that cycle.
- **REQ-049**: `setup` MUST prompt for per-provider default currency symbol (choices: `$`, `£`, `€`; default `$`) for providers `claude`, `openai`, `openrouter`, `copilot`, `codex`, `geminiai` in a dedicated section after timeout configuration, then persist selections in `~/.config/aibar/config.json` `currency_symbols`.
- **REQ-050**: Provider `fetch` MUST attempt to extract `currency_symbol` from the raw API JSON response (field `currency`); when absent, MUST resolve `currency_symbol` from `RuntimeConfig.currency_symbols[provider_name]` with fallback `"$"`.
- **REQ-051**: CLI `show` text output MUST format cost values using `metrics.currency_symbol` from the fetched result; MUST NOT use hardcoded `$` for cost lines.
- **REQ-053**: GNOME extension MUST NOT render aggregated total panel cost; panel and provider-card cost labels MUST use per-provider `metrics.currency_symbol` and display provider-local monetary values.
- **REQ-054**: MUST support provider key `geminiai` across `aibar`, `aibar setup`, `aibar show`, `aibar show --json`, and GNOME extension payload pipelines.
- **REQ-055**: `setup` MUST accept GeminiAI OAuth source choices `skip`, `file`, `paste`, and `login`; `file`/`paste` inputs MUST validate required fields and persist normalized client JSON under `~/.config/aibar/`.
- **REQ-056**: `setup` and `login --provider geminiai` MUST execute OAuth installed-app authorization with scopes `https://www.googleapis.com/auth/bigquery.readonly`, `https://www.googleapis.com/auth/monitoring.read`, and `https://www.googleapis.com/auth/cloud-platform`, then persist refresh-capable authorized-user credentials.
- **REQ-057**: GeminiAI provider `fetch` MUST query Cloud Monitoring using service constraint `resource.labels.service="generativelanguage.googleapis.com"` and MUST extract request/token metrics when Monitoring emits either `resource.type="api"` or `resource.type="consumed_api"` series, then map usage metrics (`request_count`, latency, errors, token usage) into `UsageMetrics`.
- **REQ-058**: GeminiAI provider failures for HTTP `429`, Google quota exhaustion, or missing billing-export table MUST mark attempt status `FAIL`, preserve prior payload snapshots, and apply existing idle-time retry policy for rate-limited refreshes.
- **REQ-059**: `setup` MUST include `geminiai` in `currency_symbols` prompts, and GeminiAI rendering MUST resolve `RuntimeConfig.currency_symbols.geminiai` with fallback `"$"` when missing.
- **REQ-060**: CLI text `show` and JSON `show --json` MUST expose GeminiAI monitoring usage fields, latest-available billing-period monetary cost values, and cached `result/error` status for billing table discovery or query failures; when `show --provider geminiai` omits `--window`, effective window MUST default to `30d`.
- **REQ-061**: GNOME extension MUST render GeminiAI provider tab/card using bright-purple style classes, include GeminiAI payload and status in panel aggregation logic, and order `geminiai` immediately after `codex`.
- **REQ-062**: GNOME tab/card labels MUST render `GEMINIAI`; machine-readable payload keys and CLI provider arguments MUST remain lowercase `geminiai`; CLI display title for provider `geminiai` MUST render `GEMINIAI`.
- **REQ-063**: Refresh scheduling MUST apply configured inter-provider call delay and provider-scoped idle-time lifecycle updates to GeminiAI fetches identically to existing providers, including `idle-time.json` updates after success and rate-limited failures.
- **REQ-064**: GeminiAI billing fetch MUST read `<project_id>` from `~/.config/aibar/geminiai_oauth_client.json`, discover `<table_id>` by listing tables in dataset `RuntimeConfig.billing_data` (default `billing_data`), and fail with structured error when billing export table is unavailable.
- **REQ-065**: GeminiAI billing fetch MUST query `<billing_dataset>.gcp_billing_export_v1_<table_id>` using explicit column projection and aggregate the latest available invoice month (`MAX(invoice.month)`); when invoice month is unavailable, implementation MUST fallback to `usage_start_time >= TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), MONTH)`.
- **REQ-066**: MUST guard every read/write of `~/.cache/aibar/cache.json` and `~/.cache/aibar/idle-time.json` with blocking lock files in `~/.cache/aibar/`, polling lock release every 250 milliseconds before continuing.
- **REQ-067**: CLI `show` text mode MUST render ANSI provider-colored bordered panels (Claude red, OpenRouter orange, Copilot yellow, Codex green, OpenAI blue, GeminiAI purple) with provider-colored progress bars, omit `⚠️` glyph suffixes from reset lines, and keep one shared panel width equal to the widest rendered panel.
- **REQ-068**: Bare `aibar` and `aibar --help` MUST print human-readable usage text listing all commands and global or command-specific options, including `show --force`, `show --json`, `gnome-install`, and `gnome-uninstall` examples, without Doxygen tags.
- **REQ-069**: GNOME panel icon MUST be bright white when all percentages are <= 25, bright yellow when any percentage > 25, bright orange when any percentage > 50, bright red when any percentage > 75, and blinking bright-red/dim-red when any percentage > 90.
- **REQ-070**: MUST execute startup update-check preflight before CLI argument validation and command dispatch.
- **REQ-071**: MUST skip startup update HTTP calls while current epoch is lower than persisted `idle_until` in `$HOME/.github_api_idle-time.aibar`.
- **REQ-072**: MUST create or overwrite `$HOME/.github_api_idle-time.aibar` after successful startup update checks using `last_success_at=now` and `idle_until=now+300` in epoch and human-readable formats.
- **REQ-073**: MUST print a bright-green message containing installed version and latest available version when the latest GitHub release is newer.
- **REQ-074**: MUST print bright-red error diagnostics when startup update checks fail, including HTTP status details such as `403`.
- **REQ-075**: MUST process startup update HTTP `429` responses by updating idle-time with `max(300, max_retry_after_seconds_observed)`.
- **REQ-076**: MUST execute `uv tool install aibar --force --from git+https://github.com/Ogekuri/AIBar.git` when `--upgrade` is provided and propagate subprocess exit status.
- **REQ-077**: MUST execute `uv tool uninstall aibar` when `--uninstall` is provided and propagate subprocess exit status.
- **REQ-078**: MUST print installed program version and exit when `--version` or `--ver` is provided.
- **REQ-079**: MUST include runtime files required by startup update-check behavior in `pyproject.toml` package configuration used by `.github/workflows/release-uvx+extension.yml`.
- **REQ-080**: MUST disable the extension via `gnome-extensions disable aibar@aibar.panel` before removing files in `gnome-uninstall` with colored status output.
- **REQ-081**: MUST remove the extension directory `~/.local/share/gnome-shell/extensions/aibar@aibar.panel/` and all its contents in `gnome-uninstall`.
- **REQ-082**: MUST exit with non-zero status and descriptive error message when the extension directory does not exist in `gnome-uninstall`.

## 4. Test Requirements

Automated unit-test coverage is maintained under `tests/`; tests MUST satisfy HDT principles: deterministic, isolated, and behavior-focused.

- **TST-001**: MUST verify `show` rejects unsupported window/provider values with non-zero exit and Click `BadParameter` diagnostics.
- **TST-002**: MUST verify credential precedence by asserting env vars override env-file values and provider stores for at least one provider.
- **TST-003**: MUST verify successful refresh writes `~/.cache/aibar/cache.json` with payload and last-attempt status sections used by `show --json`, and writes provider-keyed `last_success_at`/`idle_until` epoch and human-readable fields in `~/.cache/aibar/idle-time.json`.
- **TST-004**: MUST verify GNOME extension error path sets panel text `Err`, caps displayed error string length to 40 characters, renders quota-only card labels as `Remaining credits: <remaining>/<limit>` with bold `<remaining>`, renders reset labels with `Reset in:` prefix, suppresses `Error: Rate limited. Try again later.` for rate-limit quota payloads, appends `⚠️ Limit reached!` after reset countdown at displayed `100.0%`, renders Copilot `30d` bar/reset placement before remaining-credits text, renders popup labels `AIBar` and `Open AIBar Report`, verifies popup `Refresh Now` executes with `--force`, verifies `scripts/test-gnome-extension.sh` includes `MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800`, and verifies each provider card renders `Updated: <HH:MM>, Next: <HH:MM>` label bottom-right sourced from `updated_at` and `gnome_refresh_interval_seconds`.
- **TST-005**: MUST verify Copilot provider always returns `window=30d` regardless of requested window argument.
- **TST-006**: MUST verify `req --here --references` reproduces `docs/REFERENCES.md` without missing symbol entries and preserves Doxygen field extraction for documented symbols.
- **TST-007**: MUST verify GNOME panel status labels render in the REQ-021 order (including OpenAI cost), enforce provider style classes and color mapping, verify dynamic icon color/blink thresholds, render zero-cost labels with provider currency symbol, and omit unavailable labels when source metrics are unavailable.
- **TST-008**: MUST verify `pyproject.toml` declares `[build-system]` with `hatchling`, `[project.scripts]` entry `aibar = "aibar.cli:main"`, runtime `dependencies` list, and `requires-python` constraint.
- **TST-009**: MUST verify `gnome-install` resolves extension source from package location, validates source directory, copies files to target, enables the extension, and exits non-zero on missing source; MUST verify `gnome-uninstall` removes extension directory, disables the extension, and exits non-zero when extension directory does not exist.
- **TST-010**: MUST verify `Remaining credits: <remaining> / <limit>` appears for Claude, Codex, and Copilot when both quota values exist.
- **TST-011**: MUST verify HTTP `429` handling updates idle-time only for rate-limited providers using `max(retry_after_seconds, idle_delay_seconds)` while non-rate-limited providers keep `idle_until = last_success_at + idle_delay_seconds`.
- **TST-013**: MUST verify `setup` prompts idle-delay first, API-call delay milliseconds second (default `1000`), `gnome_refresh_interval_seconds` third, `billing_data` fourth (default `billing_data`), then per-provider currency symbol prompts, and persists all values into `~/.config/aibar/config.json`.
- **TST-014**: MUST verify `show` evaluates idle-time per provider, serves `~/.cache/aibar/cache.json` for providers with future `idle_until`, and refreshes only providers with missing or expired idle-time state.
- **TST-015**: MUST verify `show --force` removes `~/.cache/aibar/idle-time.json`, bypasses idle-time gating for current execution, refreshes providers, and recreates idle-time metadata before loading `~/.cache/aibar/cache.json`.
- **TST-016**: MUST verify refresh execution enforces configured inter-call delay in milliseconds between provider API requests, using `1000` milliseconds when `api_call_delay_milliseconds` is absent.
- **TST-017**: MUST verify CLI `show` invokes one shared cache-retrieval implementation and does not call legacy `ResultCache` read/write APIs.
- **TST-018**: MUST verify failed provider/window refresh attempts set `result=FAIL` and `error` in `cache.json` while preserving the previous payload for the same provider/window.
- **TST-019**: MUST verify partial refresh outcomes can record mixed `OK` and `FAIL` statuses across windows of the same provider without overwriting unaffected payload snapshots.
- **TST-020**: MUST verify refresh and fallback logic do not read or write `~/.cache/aibar/claude_dual_last_success.json`.
- **TST-021**: Tests that mock `httpx.AsyncClient` transport and invoke provider `fetch` or `fetch_all_windows` execution path MUST restrict assertions to success/error state (`is_error`, `error` fields), result-dict window key presence, HTTP call count, and cache/filesystem side effects; MUST NOT assert specific numeric metric field values (`usage_percent`, `remaining`, `cost`) derived from the parsed HTTP response.
- **TST-022**: MUST verify `scripts/claude_token_refresh.sh` `do_refresh()` truncates `LOG_FILE` before writing any log entries (source-level pattern assertion).
- **TST-023**: MUST verify `currency_symbol` in `UsageMetrics` flows through provider fetch and cache serialization to CLI text output (`_print_result`) and GNOME extension cost labels using the symbol from metrics, not a hardcoded `$`.
- **TST-024**: MUST verify `setup` accepts GeminiAI OAuth desktop-client credentials from both pasted JSON and file path input and persists normalized client-secret JSON in `~/.config/aibar/`.
- **TST-025**: MUST verify GeminiAI OAuth authorization requests `bigquery.readonly`, `monitoring.read`, and `cloud-platform` scopes and persists refresh-capable authorized-user credentials for provider fetch execution.
- **TST-026**: MUST verify GeminiAI fetch queries Cloud Monitoring usage metrics with service constraint `resource.labels.service="generativelanguage.googleapis.com"` and supports `api`/`consumed_api` metric series, and queries BigQuery billing data using explicit selected columns with latest invoice-month aggregation fallback to current-month `usage_start_time`.
- **TST-027**: MUST verify GeminiAI HTTP `429`, quota-exhaustion, and missing billing-export-table failures preserve cached payload snapshots, mark status `FAIL`, and update only GeminiAI idle-time state according to rate-limit retry policy.
- **TST-028**: MUST verify `setup` currency prompts exclude `geminiai` and GeminiAI rendering in CLI text and JSON payload includes latest-available billing-period monetary cost values when billing data exists.
- **TST-029**: MUST verify GNOME extension renders GeminiAI provider tab/card with bright-purple style class assignment, provider title `GEMINIAI`, provider ordering immediately after `codex`, and GeminiAI cost/error status propagation from cache payload.
- **TST-030**: MUST verify CLI `show` renders all provider panels with identical visible width in one execution, where the shared width equals the widest rendered panel content width, and reset lines contain no `⚠️` glyph suffix.
- **TST-031**: MUST verify startup update preflight executes before invalid-argument diagnostics and before subcommand handlers run.
- **TST-032**: MUST verify startup update idle-time gating skips HTTP calls until `idle_until` expires and resumes checks when the idle-state file is missing or expired.
- **TST-033**: MUST verify successful startup update checks write `$HOME/.github_api_idle-time.aibar` with epoch and human-readable `last_success_at` and `idle_until`.
- **TST-034**: MUST verify repeated startup update HTTP `429` responses compute idle-time using `max(300, max(retry-after values))`.
- **TST-035**: MUST verify `--upgrade` and `--uninstall` invoke required `uv tool` commands and propagate subprocess exit codes.
- **TST-036**: MUST verify `--version` and `--ver` print installed version and bypass subcommand execution.
- **TST-037**: MUST verify `pyproject.toml` include/package-data settings cover files needed for startup update-check runtime behavior in `.github/workflows/release-uvx+extension.yml` builds.

## 5. Evidence

| Requirement ID | Evidence (file + symbol + excerpt) |
|---|---|
| PRJ-001 | `src/aibar/aibar/cli.py` + `main/show/doctor/env/setup/login/gnome_install/gnome_uninstall` + `@main.command()` declarations for all subcommands. |
| PRJ-002 | `src/aibar/aibar/cli.py` + `get_providers` + returns Claude/OpenAI/OpenRouter/Copilot/Codex provider instances keyed by `ProviderName`. |
| PRJ-004 | `src/aibar/gnome-extension/aibar@aibar.panel/metadata.json` + `name` set to `AIBar Monitor` and `url/github` owner `Ogekuri`, `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_refreshData/_updateProviderCard` provider-card rendering behavior, and `scripts/test-gnome-extension.sh` exports `MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800`. |
| PRJ-005 | `docs/REFERENCES.md` + repository-wide symbol sections + machine-readable file/symbol index entries. |
| PRJ-006 | `pyproject.toml` + `[build-system]`/`[project]`/`[project.scripts]` sections + `aibar = "aibar.cli:main"` console entry point enabling `uv pip install` and `uvx` execution. |
| PRJ-007 | `README.md` + `## Installation (uv)` section + `uv pip install`, `uv pip uninstall`, `uvx --from` commands. |
| PRJ-011 | `docs/REQUIREMENTS.md`, `docs/WORKFLOW.md`, and `docs/REFERENCES.md` + GNOME contract documentation sources; repository tree excludes `src/aibar/plans/Gnome.plan.md`. |
| CTN-001 | `src/aibar/aibar/config.py` + `Config.get_token` + env var -> env file -> provider-specific stores (`ClaudeCLIAuth`, `CodexCredentialStore`, `CopilotCredentialStore`). |
| CTN-002 | `src/aibar/aibar/providers/base.py` + `ProviderResult` model + fields `provider/window/metrics/updated_at/raw/error`; `UsageMetrics` + `currency_symbol` field. |
| CTN-003 | `src/aibar/aibar/providers/*.py` + `fetch` methods + `httpx.AsyncClient(timeout=30.0)` in Claude/OpenAI/OpenRouter/Copilot/Codex providers. |
| CTN-004 | `src/aibar/aibar/cache.py` + cache schema helpers and `src/aibar/aibar/cli.py` + `cache.json` as canonical store for payload snapshots and attempt statuses. |
| CTN-005 | `src/aibar/aibar/config.py` + `PROVIDER_INFO` notes + entries describing unofficial/internal usage for Claude, Copilot, and Codex. |
| CTN-006 | `docs/REFERENCES.md` + full symbol index grouped by source file, regenerated from repository code. |
| CTN-007 | `pyproject.toml` + `[build-system] requires = ["hatchling"]` + `[project]` metadata fields `name`, `version`, `requires-python`, `dependencies`, `[project.scripts]`. |
| CTN-008 | `src/aibar/aibar/config.py` + `RuntimeConfig` model + `idle_delay_seconds`, `api_call_delay_seconds`, `gnome_refresh_interval_seconds`, and `currency_symbols` fields persisted in `~/.config/aibar/config.json`. |
| CTN-009 | `src/aibar/aibar/config.py` + `load_idle_time/save_idle_time` and `src/aibar/aibar/cli.py` + provider-scoped idle-time lifecycle handling in `~/.cache/aibar/idle-time.json`. |
| CTN-010 | `src/aibar/aibar/cache.py` + conditional payload-write helpers guarantee payload replacement only on successful provider/window fetch and payload preservation on failed attempts including HTTP `429`. |
| DES-001 | `src/aibar/aibar/providers/base.py` + `class BaseProvider(ABC)` + abstract methods `fetch`, `is_configured`, `get_config_help`. |
| DES-002 | `src/aibar/aibar/providers/base.py` + `WindowPeriod/ProviderName` + enum literals `5h/7d/30d/code_review` and provider names. |
| DES-003 | `src/aibar/aibar/cli.py` + `parse_window/parse_provider` + raises `click.BadParameter` for invalid inputs. |
| DES-004 | `src/aibar/aibar/cache.py` + `_sanitize_raw` + redacts keys in sensitive set before file write. |
| DES-005 | `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_loadEnvFromFile` + parses `export KEY=VALUE`, handles quotes/comments/semicolon cleanup. |
| DES-006 | `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + scheduler-driven `_startAutoRefresh/_refreshData` using `this._refreshIntervalSeconds` read from `json.extension.gnome_refresh_interval_seconds`, popup `Refresh Now` command uses `aibar show --json --force`, interval updated on each successful refresh. |
| REQ-001 | `src/aibar/aibar/cli.py` + `show` loop + `if not prov.is_configured(): ... continue` and text hint `Set {config.ENV_VARS.get(name)}`. |
| REQ-002 | `src/aibar/aibar/cli.py` + `show` + default-window Claude/Codex dual fetch output rendering. |
| REQ-003 | `src/aibar/aibar/cli.py` + `show` JSON renderer emits `indent=2` with `payload`, `status`, and `extension` (containing `gnome_refresh_interval_seconds`) sections. |
| REQ-004 | `src/aibar/aibar/cli.py` + `doctor` + configuration status and `_fetch_result(provider, WindowPeriod.HOUR_5)` health check. |
| REQ-005 | `src/aibar/aibar/cli.py` + `setup` prompts `idle_delay_seconds`, `api_call_delay_seconds`, and `gnome_refresh_interval_seconds` with defaults `300`, `20`, and `60`, then persists `~/.config/aibar/config.json`. |
| REQ-049 | `src/aibar/aibar/cli.py` + `setup` + per-provider currency symbol section after timeout section; prompts each provider with choices `$`/`£`/`€` default `$`; persists `currency_symbols` map in `~/.config/aibar/config.json`. |
| REQ-050 | `src/aibar/aibar/providers/*.py` + `_parse_response`/`_build_result` + `_resolve_currency_symbol` helper resolves currency from raw API response `currency` field; fallback to `RuntimeConfig.currency_symbols[provider_name]`. |
| REQ-051 | `src/aibar/aibar/cli.py` + `_print_result` + cost line uses `m.currency_symbol` instead of hardcoded `$`. |
| REQ-053 | `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_updateUI/_populateProviderCard` + panel summary cost uses `metrics.currency_symbol`; card cost label uses per-provider `metrics.currency_symbol`. |
| TST-013 | `tests/test_setup_runtime_config.py` + setup prompt-order/default assertions extended with currency symbol prompt section and `currency_symbols` persistence checks. |
| TST-023 | `tests/test_currency_symbol_flow.py` + `currency_symbol` field in `UsageMetrics`, provider fetch pass-through, CLI `_print_result`, and GNOME extension cost label use metrics symbol. |
| REQ-006 | `src/aibar/aibar/cli.py` + `_login_claude` + missing/expired flows print `claude setup-token` then `sys.exit(1)`. |
| REQ-007 | `src/aibar/aibar/providers/copilot.py` + `CopilotDeviceFlow` and `CopilotProvider.login` + device-code request/poll and `save_token`. |
| REQ-009 | `src/aibar/aibar/cli.py` + shared retrieval entrypoint used by `show` + executes force check, per-provider idle-time check, per-provider conditional refresh, then `cache.json` load. |
| REQ-010 | `src/aibar/aibar/providers/openai_usage.py` + `_get_time_range` + dict maps `"5h"` to `1` day. |
| REQ-011 | `src/aibar/aibar/providers/openrouter.py` + `_get_usage/_parse_response` + cost from usage field and limit metrics from payload. |
| REQ-012 | `src/aibar/aibar/providers/copilot.py` + `fetch` + sets `effective_window = WindowPeriod.DAY_30` and returns that window. |
| REQ-013 | `src/aibar/aibar/providers/codex.py` + `_parse_response` + `window_key = "primary_window" if 5h else "secondary_window"`. |
| REQ-014 | `src/aibar/aibar/providers/codex.py` + `CodexCredentials.needs_refresh` + threshold `age.days >= 8`; `CodexProvider.fetch` calls refresher. |
| REQ-015 | `src/aibar/aibar/providers/codex.py` + `fetch` + catches generic refresh exception and continues (`pass  # Continue with existing token`). |
| REQ-016 | `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_refreshData` and popup `Refresh Now` handler + loads env file and `launcher.setenv(key, value, true)` before command spawn, including `--force` manual refresh path. |
| REQ-017 | `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_updateUI/_populateProviderCard/_buildPopupMenu` + panel label fallback chain; quota-only cards with bold remaining credits; `Reset in:` prefix; `⚠️ Limit reached!` suffix at displayed `100.0%`; suppression of `Error: Rate limited. Try again later.` for rate-limit quota payloads; Copilot `30d` reset placement; popup labels `AIBar` and `Open AIBar Report`; `Updated: <HH:MM>, Next: <HH:MM>` label bottom-right per provider card sourced from `updated_at` and `this._refreshIntervalSeconds`. |
| REQ-018 | `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_handleError` + `this._panelLabel.set_text('Err')` and `message.substring(0, 40)`. |
| REQ-019 | `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_providerOrder` and `_updateUI` sorting + unknown providers rank `999` then lexical order. |
| REQ-020 | `docs/REFERENCES.md` + per-symbol entries containing symbol identifier, file path, and line-range spans. |
| REQ-021 | `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_buildPanelButton/_updateUI` + panel labels inserted between icon and summary label in fixed order: Claude 5h, Claude 7d, Claude cost, OpenRouter cost, Copilot 30d, Codex 5h, Codex 7d, Codex cost, OpenAI cost, GeminiAI cost. |
| REQ-022 | `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_buildPanelButton/_updateUI` + panel labels use provider classes/colors; cost labels render provider currency for numeric `0` values and hide only when cost metric is unavailable. |
| REQ-023 | `pyproject.toml` + `[project.scripts]` + `aibar = "aibar.cli:main"` declaration. |
| REQ-024 | `src/aibar/aibar/__main__.py` + `main()` import and invocation from `aibar.cli`. |
| REQ-034 | `src/aibar/aibar/cli.py` + `_format_reset_duration/_print_result` + day-token reset countdown formatting in text output. |
| REQ-035 | `src/aibar/aibar/cli.py` + `_print_result` + remaining-credits line for Claude/Codex/Copilot when `remaining` and `limit` are present. |
| REQ-036 | `src/aibar/aibar/cli.py` + `_fetch_claude_dual/_print_result` + Claude HTTP 429 output keeps 5h error+100% while 7d usage/reset are restored from persisted Claude payload. |
| REQ-037 | `src/aibar/aibar/cli.py` + Claude HTTP 429 fallback path synthesizes deterministic values when no persisted Claude payload is available. |
| REQ-038 | `src/aibar/aibar/cli.py` + successful refresh path computes per-provider `idle_until = last_success_at + idle_delay_seconds` and writes provider-keyed epoch/human-readable values to `~/.cache/aibar/idle-time.json`. |
| REQ-039 | `src/aibar/aibar/cli.py` + shared force-refresh handling removes `~/.cache/aibar/idle-time.json`, bypasses idle-time gate, and refreshes before loading `cache.json`. |
| REQ-040 | `src/aibar/aibar/cli.py` + refresh scheduler enforces configured `api_call_delay_seconds` between consecutive provider API requests. |
| REQ-041 | `src/aibar/aibar/cli.py` + HTTP 429 handling uses `retry-after` and `idle_delay_seconds` to update only the rate-limited provider idle-time entry. |
| REQ-042 | `src/aibar/aibar/cli.py` + retrieval pipeline uses only `cache.json` and `idle-time.json` persisted artifacts for idle-time-gated API minimization. |
| REQ-043 | `src/aibar/aibar/cli.py` + shared cache refresh/load helpers provide one retrieval implementation for CLI retrieval and render flows. |
| REQ-044 | `src/aibar/aibar/cache.py` + cache status-write helpers persist per-provider/window `result` (`OK`/`FAIL`), `error`, and `updated_at` fields. |
| REQ-045 | `src/aibar/aibar/cache.py` + provider/window upsert path only writes payload on successful fetch outcomes. |
| REQ-046 | `src/aibar/aibar/cache.py` + failed provider/window upsert path preserves existing payload while updating failure status metadata. |
| REQ-047 | `src/aibar/aibar/cli.py` + `src/aibar/aibar/cache.py` + fallback and refresh flows use only `cache.json` and remove dependency on `claude_dual_last_success.json`. |
| TST-001 | `src/aibar/aibar/cli.py` + `parse_window/parse_provider` provide validation points for invalid input diagnostics. |
| TST-002 | `src/aibar/aibar/config.py` + `get_token` implements explicit precedence chain requiring regression coverage. |
| TST-003 | `tests/test_cli_idle_cache.py` and `tests/test_cli_idle_force.py` + assertions for cache schema parity with `show --json` and provider-keyed idle-time epoch/human-readable field persistence under `~/.cache/aibar/`. |
| TST-004 | `tests/test_extension_quota_label.py` + popup-label assertions (`AIBar`, `Open AIBar Report`), reset-prefix and `⚠️ Limit reached!` assertions, rate-limit error-string suppression assertions, `Updated:` and `Next:` provider-card label assertions, and popup `Refresh Now` `--force` assertion; `tests/test_extension_dev_script.py` + `MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800`; `src/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_handleError/_populateProviderCard/_buildPopupMenu` coverage. |
| TST-005 | `src/aibar/aibar/providers/copilot.py` + `fetch` hard-codes `effective_window` to `WindowPeriod.DAY_30`. |
| TST-006 | `docs/REFERENCES.md` + generated symbol coverage for tracked `src/` files validates documentation inventory completeness. |
| TST-007 | `tests/test_extension_quota_label.py` + panel-segment order assertions (including OpenAI cost), provider style classes, zero-cost currency-label visibility checks, bold primary percentages, and missing-metric omission behavior. |
| TST-008 | `tests/test_pyproject_metadata.py` + assertions for `[build-system]` backend, `[project.scripts]` entry, `dependencies` list, and `requires-python` constraint in `pyproject.toml`. |
| TST-010 | `tests/test_reset_pending_message.py` and `src/aibar/aibar/cli.py` + verify remaining-credits rendering path in text output for quota providers. |
| TST-011 | `tests/test_cli_idle_time_429.py` + rate-limit scenarios verify provider-scoped `max(retry_after_seconds, idle_delay_seconds)` updates while non-rate-limited providers retain default idle-delay scheduling. |
| TST-013 | `tests/test_setup_runtime_config.py` + setup prompt-order/default assertions and `~/.config/aibar/config.json` persistence checks for idle delay, API delay, and gnome_refresh_interval_seconds. |
| TST-014 | `tests/test_cli_idle_cache.py` + provider-scoped idle-time future/missing/expired branches verify per-provider cache-serving behavior and refresh gating in `show`. |
| TST-015 | `tests/test_cli_idle_force.py` + force-refresh path verifies idle-time deletion, gate bypass, refresh invocation, and idle-time regeneration before cache load. |
| TST-017 | `tests/test_cli_cache_status_retention.py` and `src/aibar/aibar/cli.py` + verify shared retrieval usage and absence of `ResultCache` read/write calls in CLI `show` path. |
| TST-018 | `tests/test_cli_cache_status_retention.py` + failed-refresh assertions verify `result=FAIL` with error metadata while preserving existing provider/window payload snapshots. |
| TST-019 | `tests/test_cli_cache_status_retention.py` + mixed-window assertions verify partial provider updates preserve unaffected windows and record per-window status granularity. |
| TST-020 | `tests/test_cli_cache_status_retention.py` + file-system assertions verify no read/write path targets `~/.cache/aibar/claude_dual_last_success.json`. |
| TST-016 | `tests/test_cli_provider_throttle.py` + refresh timing assertions verify configured inter-call delay and default `20`-second fallback. |
| PRJ-008 | `src/aibar/aibar/cli.py` + `gnome_install` command + copies extension files from package source to `~/.local/share/gnome-shell/extensions/aibar@aibar.panel/` + enables extension via `gnome-extensions enable`. |
| REQ-025 | `src/aibar/aibar/cli.py` + `_resolve_extension_source_dir` + Python `__file__`-based module path resolution for extension source directory. |
| REQ-026 | `src/aibar/aibar/cli.py` + `gnome_install` + `os.makedirs` for target directory creation. |
| REQ-027 | `src/aibar/aibar/cli.py` + `gnome_install` + validates non-empty source directory and `metadata.json` presence. |
| REQ-028 | `src/aibar/aibar/cli.py` + `gnome_install/gnome_uninstall` + `click.style` colored output for status, success, error, and informational messages. |
| REQ-029 | `src/aibar/aibar/cli.py` + `gnome_install` + `shutil.copy2` copies files from package source to target directory replacing existing files. |
| REQ-030 | `src/aibar/aibar/cli.py` + `gnome_install` + `sys.exit(1)` on prerequisite failure with descriptive error message. |
| REQ-031 | `scripts/test-gnome-extension.sh` + calls `aibar gnome-install` before nested-shell launch. |
| REQ-032 | `src/aibar/aibar/cli.py` + `gnome_install` + `subprocess.run(["gnome-extensions", "enable", "aibar@aibar.panel"])` after file copy with colored status output. |
| REQ-033 | `scripts/test-gnome-extension.sh` + no subcommand parameter; executes nested-shell launch directly on invocation. |
| REQ-080 | `src/aibar/aibar/cli.py` + `gnome_uninstall` + `subprocess.run(["gnome-extensions", "disable", "aibar@aibar.panel"])` before removal with colored status output. |
| REQ-081 | `src/aibar/aibar/cli.py` + `gnome_uninstall` + `shutil.rmtree` removes extension directory and all contents. |
| REQ-082 | `src/aibar/aibar/cli.py` + `gnome_uninstall` + `sys.exit(1)` when extension directory does not exist with descriptive error message. |
| TST-009 | `tests/test_gnome_install_uninstall.py` + `gnome-install` source resolution, validation, copy, enable assertions; `gnome-uninstall` removal, disable, missing-directory exit code assertions. |
| TST-021 | `tests/test_claude_retry_and_cli_cache.py` + `TestClaudeRetryOn429::test_retries_on_429_then_succeeds` and `TestFetchAllWindows::test_single_call_returns_both_windows` + metric-value assertions on parsed HTTP responses removed; assertions restricted to `is_error` state, window key presence in results dict, and `mock_get.call_count`. |
| REQ-048 | `scripts/claude_token_refresh.sh` + `do_refresh()` + `> "$LOG_FILE"` truncation statement before first `log` call. |
| TST-022 | `tests/test_claude_token_refresh_script.py` + source-level assertion that `do_refresh()` body contains `LOG_FILE` truncation before any `log` invocation. |
| TST-023 | `tests/test_currency_symbol_flow.py` + assertions for `currency_symbol` field in `UsageMetrics`, CLI `_print_result` cost formatting, and GNOME extension panel label using metrics symbol. |
| TST-030 | `tests/test_cli_show_panel_alignment.py` + CLI panel output assertions verify all rendered panels share identical visible width within one `show` execution. |
