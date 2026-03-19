---
title: "AIBar Requirements"
description: Software requirements specification
version: "0.3.27"
date: "2026-03-19"
author: "req-new"
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
- GNOME JS: `GLib`, `St`, `Gio`, `Clutter`, `GObject`, `Main`, `PanelMenu`, `PopupMenu` (`src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js`)

Performance note: explicit caching optimization uses persistent CLI cache (`~/.cache/aibar/cache.json`), idle-time gating (`~/.cache/aibar/idle-time.json`), configurable provider-call throttling (`api_call_delay_milliseconds`), and configurable HTTP timeout (`api_call_timeout_milliseconds`) to minimize API request volume.

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
- **PRJ-006**: MUST provide a PEP 621-compliant `pyproject.toml` at repository root enabling `uv tool install` distribution execution and `uv run`/`uvx` live execution without external virtualenv bootstrap scripts.
- **PRJ-007**: MUST document in `README.md` dedicated sections for `uv`-based requirements, installation/removal, `uv run`/`uvx` execution, and optional `requirements.txt` export command, plus GeminiAI prerequisites.
- **PRJ-008**: MUST provide `aibar gnome-install` CLI command that detects install/update mode for `~/.local/share/gnome-shell/extensions/aibar@aibar.panel/`, copies package extension files, disables extension before update copy, and enables extension after copy.
- **PRJ-009**: MUST execute startup update checks and lifecycle flags `--upgrade`, `--uninstall`, `--version`, and `--ver` for program `aibar`.
- **PRJ-010**: MUST package all runtime files required by `aibar` so local execution and `uv tool install` execution remain behaviorally equivalent.
- **PRJ-011**: MUST keep GNOME extension contract documentation in `docs/REQUIREMENTS.md`, `docs/WORKFLOW.md`, and `docs/REFERENCES.md`; repository source tree MUST NOT contain `src/aibar/plans/Gnome.plan.md`.

### 2.2 Project Constraints
- **CTN-001**: MUST resolve provider credentials with precedence: environment variable, then `~/.config/aibar/env`, then provider-specific local credential stores.
- **CTN-002**: MUST represent provider fetch output with `ProviderResult` containing `provider`, `window`, `metrics`, `updated_at`, `raw`, and optional `error`; `UsageMetrics` MUST include `currency_symbol: str` (default `"$"`) annotating all monetary fields (`cost`, `remaining`, `limit`).
- **CTN-003**: MUST perform external HTTP API calls with `httpx.AsyncClient(timeout=<api_call_timeout_milliseconds>/1000.0)` using `RuntimeConfig.api_call_timeout_milliseconds` for provider integrations.
- **CTN-004**: MUST persist `~/.cache/aibar/cache.json` as the canonical store for per-provider, per-window last-success payload snapshots and last-attempt status metadata.
- **CTN-005**: MAY depend on unofficial/internal endpoints when official usage APIs are unavailable for Claude, Copilot, or Codex integrations.
- **CTN-006**: MUST keep `docs/REFERENCES.md` synchronized with symbols defined under `src/` and `.github/workflows/`.
- **CTN-007**: MUST declare `hatchling` as `[build-system]` backend in `pyproject.toml` with `[project]` metadata including `name`, `version`, `requires-python`, `[project.scripts]`, and `dependencies` containing `pytest`.
- **CTN-008**: MUST persist runtime configuration in `~/.config/aibar/config.json` with keys `idle_delay_seconds`, `api_call_delay_milliseconds`, `api_call_timeout_milliseconds`, `gnome_refresh_interval_seconds`, `billing_data`, and `currency_symbols` (mapping provider name → currency symbol string; default `"$"` per provider when key is absent).
- **CTN-009**: MUST persist provider-scoped idle-time state in `~/.cache/aibar/idle-time.json` with `last_success_timestamp` and `idle_until_timestamp` (epoch seconds) and `last_success_human` and `idle_until_human` (local-timezone ISO-8601).
- **CTN-010**: MUST update `cache.json` payload fields only after successful fetch for the same provider/window and MUST preserve previous payload fields on failed fetch attempts, including HTTP `429`.
- **CTN-011**: MUST fetch latest release metadata from `https://api.github.com/repos/Ogekuri/AIBar/releases/latest` for startup update checks.
- **CTN-012**: MUST use hardcoded startup update-check constants `idle_delay_seconds=300` and `http_timeout_seconds=2`.
- **CTN-013**: MUST persist startup update-check idle state in `~/.cache/aibar/check_version_idle-time.json` JSON with epoch and human-readable `last_success_at` and `idle_until`.
- **CTN-014**: MUST perform at most one startup update HTTP check per 300 seconds unless `~/.cache/aibar/check_version_idle-time.json` is missing or expired.
- **CTN-015**: MUST use lifecycle command strings exactly as `uv tool install aibar --force --from git+https://github.com/Ogekuri/AIBar.git` and `uv tool uninstall aibar`.
- **CTN-016**: MUST allow `~/.cache/aibar/idle-time.json` provider entries to include optional boolean field `oauth_refresh_blocked` for Claude authentication-retry suppression state.

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
- **REQ-002**: MUST render default-window Claude and Codex as single panels with `5h` and `7d` sections separated by one blank line; a shared `Remaining credits` line MUST follow `7d` `Resets in`, separated by one blank line and derived from `7d`.
- **REQ-003**: MUST emit pretty-printed JSON (`indent=2`) for `show --json` with top-level sections `payload`, `status`, `idle_time`, `freshness`, and `extension`; `freshness` MUST expose provider-keyed `last_success_timestamp`/`idle_until_timestamp` plus local-time `%Y-%m-%d %H:%M` strings, and `extension` MUST expose `gnome_refresh_interval_seconds`, `idle_delay_seconds`, and provider-keyed `window_labels` values consumed by GNOME provider bars.
- **REQ-004**: MUST run provider health checks in `doctor` using the 5-hour window and report per-provider configuration and test status.
- **REQ-005**: MUST prompt `setup` for `idle_delay_seconds` (default `300`) first, `api_call_delay_milliseconds` (default `100`) second, `api_call_timeout_milliseconds` (default `3000`) third, `gnome_refresh_interval_seconds` (default `60`) fourth, and `billing_data` (default `billing_data`) fifth, then persist values in `~/.config/aibar/config.json`.
- **REQ-006**: MUST fail Claude login when CLI credentials are missing or expired and MUST print `claude setup-token` remediation guidance.
- **REQ-007**: MUST execute GitHub device-flow login for Copilot and save the token in `~/.config/aibar/copilot.json`.
- **REQ-009**: MUST execute provider retrieval for `show` in this order: force-flag handling, per-provider idle-time evaluation, per-provider conditional refresh to `~/.cache/aibar/cache.json`, then data load from `~/.cache/aibar/cache.json`.
- **REQ-010**: MUST ignore requested window for OpenAI fetch and return effective window `30d` in provider payload, CLI text output, and `show --json`.
- **REQ-011**: MUST ignore requested window for OpenRouter fetch and return effective window `30d` in provider payload, CLI text output, and `show --json`; OpenRouter cost MUST derive from `usage_monthly` and include `limit` and `limit_remaining`.
- **REQ-012**: MUST ignore requested window for Copilot fetch and return effective window `30d` in provider payload, CLI text output, and `show --json`.
- **REQ-013**: MUST select Codex rate-limit primary window for `5h` and secondary window for other requested windows.
- **REQ-014**: MUST attempt Codex token refresh when refresh token exists and `last_refresh` age is at least eight days.
- **REQ-015**: SHOULD continue Codex fetch with existing credentials when non-authentication refresh exceptions occur, leaving refresh failures non-fatal.
- **REQ-016**: MUST load `~/.config/aibar/env` into subprocess environment before GNOME extension executes `aibar show --json` and before popup `Refresh Now` executes `aibar show --json --force`.
- **REQ-017**: GNOME provider cards MUST render only `Error: <reason>` on `FAIL`, MUST hide status/window/freshness/usage/reset/quota/cost rows on `FAIL`, and MUST NOT render any window label text (`5h`, `7d`, `30d`) inside provider-card content.
- **REQ-018**: MUST set GNOME panel label to `Err` and truncate popup error text to 40 characters when command execution or JSON parsing fails.
- **REQ-019**: SHOULD order extension provider tabs/cards by `claude`, `openrouter`, `copilot`, `codex`, `openai`, `geminiai`, with providers not listed in ordering array appended alphabetically.
- **REQ-020**: MUST include each discovered source symbol in `docs/REFERENCES.md` with file path, symbol kind, line-range evidence, and parsed Doxygen fields (`@brief`, `@param`, `@return`, `@raises`) when present in source declarations.
- **REQ-021**: MUST render GNOME panel status labels after the icon in this order: Claude 5h percentage, Claude 7d percentage, Claude cost, OpenRouter cost, Copilot 30d percentage, Codex 5h percentage, Codex 7d percentage, Codex cost, OpenAI cost, GeminiAI cost.
- **REQ-022**: MUST style GNOME panel tab and label fonts with provider classes and bright colors: Claude red, OpenRouter orange, Copilot yellow, Codex green, OpenAI blue, GeminiAI purple; cost labels MUST use the same font family, render when numeric value is `0`, and hide only when cost metric is unavailable.
- **REQ-023**: MUST declare a `[project.scripts]` entry `aibar = "aibar.cli:main"` in `pyproject.toml` so that `uv pip install` and `uvx` resolve the `aibar` console command.
- **REQ-024**: MUST provide `src/aibar/aibar/__main__.py` that delegates to `aibar.cli:main` to enable `python -m aibar` execution.
- **REQ-025**: MUST resolve GNOME extension source files from within the `aibar` Python package directory via module-relative path resolution (`Path(__file__).resolve().parent / "gnome-extension" / <UUID>`) in `gnome-install`, independent of git repository, working directory, or installation method (editable, wheel, `uv tool`).
- **REQ-083**: MUST place the GNOME extension source directory (`gnome-extension/aibar@aibar.panel/`) inside the `aibar` Python package subtree (`src/aibar/aibar/gnome-extension/`) so that wheel and sdist builds include extension files within the installed package at `<site-packages>/aibar/gnome-extension/aibar@aibar.panel/`.
- **REQ-026**: MUST create target directory `~/.local/share/gnome-shell/extensions/aibar@aibar.panel/` if it does not exist before copying extension files in `gnome-install`.
- **REQ-027**: MUST validate that the extension source directory is non-empty and contains `metadata.json` before copying in `gnome-install`.
- **REQ-028**: MUST produce colored, formatted terminal output via Click styling for status, success, error, and informational messages in `gnome-install` and `gnome-uninstall` commands.
- **REQ-029**: MUST copy all files from the package extension source directory to target directory, replacing any existing files, in `gnome-install`.
- **REQ-030**: MUST exit with non-zero status and descriptive error message when any prerequisite check fails in `gnome-install`.
- **REQ-031**: `scripts/test-gnome-extension.sh` MUST launch only the nested GNOME Shell interface and MUST NOT invoke `aibar gnome-install` or any extension-update command.
- **REQ-032**: `gnome-install` MUST execute install and update flows with colored status output: install flow copies extension files then enables `aibar@aibar.panel`; update flow disables `aibar@aibar.panel`, copies files, then enables `aibar@aibar.panel`.
- **REQ-099**: `gnome-install` update flow MUST mask non-zero disable outcomes caused by extension absence and continue copy/enable without exposing raw disable errors.
- **REQ-033**: `scripts/test-gnome-extension.sh` MUST NOT accept any subcommand parameter; it MUST execute the nested-shell launch directly on invocation without arguments.
- **REQ-034**: MUST render reset countdown as `Resets in: <d>d <h>h <m>m` for durations >= 24 hours in CLI text output.
- **REQ-035**: MUST print `Remaining credits: <remaining> / <limit>` for Claude, Codex, and Copilot only when rendered status is `OK` and both values exist; line MUST follow `Resets in` after one blank line and `<remaining>` MUST be bold bright white.
- **REQ-036**: CLI text `show` MUST print only `Error: <reason>` for `FAIL` provider/window states, and on `OK` states for `openai`, `openrouter`, `codex`, `geminiai` MUST render `Requests` and `Tokens` lines with null counters normalized to `0`.
- **REQ-037**: CLI text `show` and GNOME provider-card error blocks MUST NOT append HTTP status or retry-after metadata in `FAIL` output blocks.
- **REQ-038**: MUST update only the refreshed provider idle-time entry after success by setting `last_success_at` to refresh completion time and `idle_until` to `last_success_at + idle_delay_seconds`, then persist epoch and human-readable values in `~/.cache/aibar/idle-time.json`.
- **REQ-039**: MUST support force-refresh handling that deletes `~/.cache/aibar/idle-time.json`, bypasses idle-time gating for the current execution, and executes a fresh provider refresh before loading `~/.cache/aibar/cache.json`.
- **REQ-040**: MUST enforce at least `api_call_delay_milliseconds` between consecutive provider API requests during refresh execution, with default `100` milliseconds when configuration is missing.
- **REQ-041**: MUST update idle-time for each provider refresh failure in `~/.cache/aibar/idle-time.json` using `idle_until = last_attempt_at + max(idle_delay_seconds, retry_after_seconds_or_0)`, where `retry_after_seconds_or_0` is parsed from API error metadata when available.
- **REQ-042**: MUST minimize provider API requests and cache I/O by reusing in-memory cache and idle-time state within each refresh cycle and persisting `cache.json` or `idle-time.json` only when content changes.
- **REQ-043**: MUST centralize refresh and load logic for `~/.cache/aibar/cache.json` into shared internal functions reused by CLI `show` refresh and output workflows.
- **REQ-091**: `show` command MUST execute in this sequential order: (1) evaluate idle-time per provider to determine refresh need, (2) execute modular API calls only for providers with expired idle-time, collecting results in memory, (3) compute new idle-time values applying `idle_until = max(current_time + retry_after, current_time + idle_delay)` for errors, (4) write updated cache and idle-time under lock file, (5) read `cache.json` under lock file, (6) present results.
- **REQ-092**: MUST maintain exactly one code path for creating or updating `~/.cache/aibar/cache.json`; no other function MUST write to `cache.json`.
- **REQ-093**: MUST guard every read and write of `~/.cache/aibar/cache.json` with a blocking lock file `~/.cache/aibar/cache.json.lock`; lock MUST be created before write and released after write completes; reads MUST block while lock file exists.
- **REQ-094**: MUST perform at most one disk read of `~/.cache/aibar/cache.json` per `show` command execution when no refresh is needed, and at most one disk read after the single write when refresh occurs.
- **REQ-095**: MUST persist `api_call_timeout_milliseconds` (default `3000`) in `RuntimeConfig` and use it as the HTTP response timeout for all provider API calls via `httpx.AsyncClient(timeout=<value>/1000.0)`.
- **REQ-096**: MUST default `api_call_delay_milliseconds` to `100` when configuration is missing.
- **REQ-044**: MUST persist per-provider, per-window last-attempt status in `cache.json` with fields `result`, `error`, and `updated_at`, where `result` is `OK` or `FAIL`.
- **REQ-045**: MUST overwrite a provider/window payload in `cache.json` only when the current fetch for that provider/window succeeds.
- **REQ-046**: MUST preserve the previous provider/window payload in `cache.json` when the current fetch for that provider/window fails, including HTTP `429`.
- **REQ-047**: MUST store and load all last-success fallback payloads from `~/.cache/aibar/cache.json` and MUST NOT require `~/.cache/aibar/claude_dual_last_success.json`.
- **REQ-048**: `scripts/claude_token_refresh.sh` `do_refresh()` MUST truncate `LOG_FILE` to zero bytes before writing any log entries, so each `once` invocation and each daemon refresh cycle produces a standalone log containing only entries from that cycle.
- **REQ-049**: `setup` MUST prompt for per-provider default currency symbol (choices: `$`, `£`, `€`; default `$`) for providers `claude`, `openai`, `openrouter`, `copilot`, `codex`, `geminiai` in a dedicated section after timeout configuration, then persist selections in `~/.config/aibar/config.json` `currency_symbols`.
- **REQ-050**: Provider `fetch` MUST attempt to extract `currency_symbol` from the raw API JSON response (field `currency`); when absent, MUST resolve `currency_symbol` from `RuntimeConfig.currency_symbols[provider_name]` with fallback `"$"`.
- **REQ-051**: CLI `show` text output MUST render cost as `Cost: <currency_symbol><value>` where `<currency_symbol><value>` uses `metrics.currency_symbol`, is bold bright white, and MUST NOT use hardcoded `$`.
- **REQ-053**: GNOME extension MUST NOT render aggregated total panel cost; panel and provider-card cost labels MUST use per-provider `metrics.currency_symbol` and display provider-local monetary values.
- **REQ-054**: MUST support provider key `geminiai` across `aibar`, `aibar setup`, `aibar show`, `aibar show --json`, and GNOME extension payload pipelines.
- **REQ-055**: `setup` MUST accept GeminiAI OAuth source choices `skip`, `file`, `paste`, and `login`; `file`/`paste` inputs MUST validate required fields and persist normalized client JSON under `~/.config/aibar/`.
- **REQ-056**: `setup` and `login --provider geminiai` MUST execute OAuth installed-app authorization with scopes `https://www.googleapis.com/auth/bigquery.readonly`, `https://www.googleapis.com/auth/monitoring.read`, and `https://www.googleapis.com/auth/cloud-platform`, then persist refresh-capable authorized-user credentials.
- **REQ-057**: GeminiAI provider `fetch` MUST query Cloud Monitoring using service constraint `resource.labels.service="generativelanguage.googleapis.com"` and MUST extract request/token metrics when Monitoring emits either `resource.type="api"` or `resource.type="consumed_api"` series, then map usage metrics (`request_count`, latency, errors, token usage) into `UsageMetrics`.
- **REQ-058**: GeminiAI provider failures for HTTP `429`, Google quota exhaustion, or missing billing-export table MUST mark attempt status `FAIL`, preserve prior payload snapshots, and apply existing idle-time retry policy for rate-limited refreshes.
- **REQ-059**: `setup` MUST include `geminiai` in `currency_symbols` prompts, and GeminiAI rendering MUST resolve `RuntimeConfig.currency_symbols.geminiai` with fallback `"$"` when missing.
- **REQ-060**: CLI text `show` and JSON `show --json` MUST expose GeminiAI monitoring usage fields, latest-available billing-period cost values, and cached `result/error` status for billing table discovery or query failures.
- **REQ-106**: CLI text GeminiAI `Billing services: <count>` MUST append parenthesized service names from billing data in display order, comma-separated, including all available services without truncation markers.
- **REQ-097**: GeminiAI effective window MUST always be `30d` in CLI text and JSON output, and GeminiAI fetch logic MUST ignore requested window arguments.
- **REQ-098**: GeminiAI monitoring queries MUST use interval `[UTC month start, current UTC time]` so `30d` behavior represents current-month usage scope.
- **REQ-061**: GNOME extension MUST render GeminiAI provider tab/card using bright-purple style classes, include GeminiAI payload and status in panel aggregation logic, and order `geminiai` as the last provider tab/card.
- **REQ-062**: GNOME tab/card labels MUST render `GEMINIAI`; machine-readable payload keys and CLI provider arguments MUST remain lowercase `geminiai`; CLI display title for provider `geminiai` MUST render `GEMINIAI`.
- **REQ-063**: Refresh scheduling MUST apply configured inter-provider call delay and provider-scoped idle-time lifecycle updates to GeminiAI fetches identically to existing providers, including `idle-time.json` updates after success and rate-limited failures.
- **REQ-064**: GeminiAI billing fetch MUST read `<project_id>` from `~/.config/aibar/geminiai_oauth_client.json`, discover `<table_id>` by listing tables in dataset `RuntimeConfig.billing_data` (default `billing_data`), and fail with structured error when billing export table is unavailable.
- **REQ-065**: GeminiAI billing fetch MUST query `<billing_dataset>.gcp_billing_export_v1_<table_id>` using explicit column projection and aggregate the latest available invoice month (`MAX(invoice.month)`); when invoice month is unavailable, implementation MUST fallback to `usage_start_time >= TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), MONTH)`.
- **REQ-066**: MUST guard every read/write of `~/.cache/aibar/cache.json` and `~/.cache/aibar/idle-time.json` with blocking lock files in `~/.cache/aibar/`, polling lock release every 250 milliseconds before continuing.
- **REQ-067**: CLI `show` text mode MUST render ANSI provider-colored bordered panels ordered `claude`, `openrouter`, `copilot`, `codex`, `openai`, `geminiai`, MUST render `Status` first on `OK`, and MUST NOT render any `Window <window>` heading text.
- **REQ-068**: Bare `aibar` and `aibar --help` MUST print human-readable usage text listing all commands and global or command-specific options, including `show --force`, `show --json`, `gnome-install`, `gnome-uninstall`, `--version`/`--ver`, `--upgrade`, and `--uninstall` examples, without Doxygen tags.
- **REQ-069**: GNOME panel icon MUST be bright white when all percentages are <= 25, bright yellow when any percentage > 25, bright orange when any percentage > 50, bright red when any percentage > 75, and blinking bright-red/dim-red when any percentage > 90.
- **REQ-070**: MUST execute startup update-check preflight before CLI argument validation and command dispatch.
- **REQ-071**: MUST skip startup update HTTP calls while current epoch is lower than persisted `idle_until` in `~/.cache/aibar/check_version_idle-time.json`.
- **REQ-072**: MUST create missing `~/.cache/aibar/` and create or overwrite `check_version_idle-time.json` after successful startup update checks with epoch and human-readable `last_success_at=now` and `idle_until=now+300`.
- **REQ-073**: MUST print a bright-green message containing installed version and latest available version when the latest GitHub release is newer.
- **REQ-074**: MUST print bright-red error diagnostics when startup update checks fail, including HTTP status details such as `403`.
- **REQ-075**: MUST process startup update HTTP `429` responses by updating idle-time with `max(300, max_retry_after_seconds_observed)`.
- **REQ-076**: MUST execute `uv tool install aibar --force --from git+https://github.com/Ogekuri/AIBar.git` only on Linux when `--upgrade` is provided and MUST propagate subprocess exit status.
- **REQ-077**: MUST execute `uv tool uninstall aibar` only on Linux when `--uninstall` is provided, MUST propagate subprocess exit status, and MUST delete `~/.cache/aibar/check_version_idle-time.json` and `~/.cache/aibar/`.
- **REQ-088**: MUST NOT execute lifecycle `uv tool` subprocess commands for `--upgrade` or `--uninstall` on non-Linux operating systems.
- **REQ-089**: MUST print explicit manual command guidance for the current non-Linux operating system when `--upgrade` or `--uninstall` is provided.
- **REQ-078**: MUST print installed program version and exit when `--version` or `--ver` is provided.
- **REQ-079**: MUST include runtime files required by startup update-check behavior in `pyproject.toml` package configuration used by `.github/workflows/release-uvx+extension.yml`.
- **REQ-080**: MUST disable the extension via `gnome-extensions disable aibar@aibar.panel` before removing files in `gnome-uninstall` with colored status output.
- **REQ-081**: MUST remove the extension directory `~/.local/share/gnome-shell/extensions/aibar@aibar.panel/` and all its contents in `gnome-uninstall`.
- **REQ-082**: MUST exit with non-zero status and descriptive error message when the extension directory does not exist in `gnome-uninstall`.
- **REQ-084**: CLI text `show` MUST render the right-aligned `Updated: <datetime>, Next: <datetime>` freshness line only for `OK` provider/window states; `show --json` MUST still export provider freshness in `freshness` formatted in local timezone `%Y-%m-%d %H:%M`.
- **REQ-085**: CLI text `show` MUST render per-provider last-attempt authentication and refresh-rate-limit failures from cached status errors, including invalid or expired OAuth tokens and HTTP `429` refresh-limit diagnostics; when status is `FAIL`, statistics lines MUST remain suppressed.
- **REQ-090**: GNOME provider cards MUST render error category, HTTP status, and retry-after values from cached status entries using semantics equivalent to CLI `show` for the same provider/window.
- **REQ-100**: MUST implement one internal Claude OAuth renewal routine that truncates `~/.config/aibar/claude_token_refresh.log` before each execution and then runs `claude /usage` plus `aibar login --provider claude` with command-availability checks.
- **REQ-101**: MUST execute each Claude OAuth renewal command with runtime `api_call_delay_milliseconds` spacing and runtime `api_call_timeout_milliseconds` timeout enforcement.
- **REQ-102**: MUST classify Claude authentication failure when API execution yields `Invalid or expired OAuth token` and MUST preserve canonical surface text `Error: Invalid or expired OAuth token` for failed Claude outputs.
- **REQ-103**: MUST execute exactly one Claude OAuth renewal attempt and exactly one Claude API retry when Claude fetch raises authentication error `Invalid or expired OAuth token`.
- **REQ-104**: MUST set `~/.cache/aibar/idle-time.json` field `claude.oauth_refresh_blocked=true` when Claude retry after renewal still fails with `Invalid or expired OAuth token`, and MUST skip further renewal attempts while the flag remains active.
- **REQ-105**: MUST clear `claude.oauth_refresh_blocked` when `show --force` is used and MUST auto-clear it when current epoch exceeds `last_success_timestamp + 86400`.
- **REQ-086**: `scripts/aibar.sh` MUST execute CLI via `uv run python -m aibar.cli` and MUST NOT create, activate, or install dependencies into repository-local or system virtual environments.
- **REQ-087**: Repository root MUST track `uv.lock`, MUST NOT track `requirements.txt`, and MUST keep `README.md` instructions for optional export command `uv export --format requirements-txt > requirements.txt`.

## 4. Test Requirements

Automated unit-test coverage is maintained under `tests/`; tests MUST satisfy HDT principles: deterministic, isolated, and behavior-focused.

- **TST-001**: MUST verify `show` rejects unsupported window/provider values with non-zero exit and Click `BadParameter` diagnostics.
- **TST-002**: MUST verify credential precedence by asserting env vars override env-file values and provider stores for at least one provider.
- **TST-003**: MUST verify successful refresh writes `~/.cache/aibar/cache.json` with payload and last-attempt status sections used by `show --json`, and writes provider-keyed `last_success_at`/`idle_until` epoch and human-readable fields in `~/.cache/aibar/idle-time.json`.
- **TST-004**: MUST verify GNOME extension `FAIL` cards render only `Error: <reason>`, hide status/window/freshness/usage/reset/quota/cost rows, never render window-label text (`5h`, `7d`, `30d`) in card content, and keep existing popup refresh/header behavior.
- **TST-005**: MUST verify Copilot provider always returns and displays effective `window=30d` in payload, CLI text, and `show --json` regardless of requested window argument.
- **TST-006**: MUST verify `req --here --references` reproduces `docs/REFERENCES.md` without missing symbol entries and preserves Doxygen field extraction for documented symbols.
- **TST-007**: MUST verify GNOME panel status labels render in the REQ-021 order (including OpenAI cost), enforce provider style classes and color mapping, verify dynamic icon color/blink thresholds, render zero-cost labels with provider currency symbol, and omit unavailable labels when source metrics are unavailable.
- **TST-008**: MUST verify `pyproject.toml` declares `[build-system]` with `hatchling`, `[project.scripts]` entry `aibar = "aibar.cli:main"`, `requires-python`, and `dependencies` list containing `pytest`.
- **TST-009**: MUST verify `gnome-install` resolves package source, validates source directory, branches install/update by target-directory presence, executes update disable→copy→enable ordering, masks extension-absence disable failures, and exits non-zero on missing source; MUST verify `gnome-uninstall` disables extension then removes directory and exits non-zero when directory is missing.
- **TST-010**: MUST verify `Remaining credits: <remaining> / <limit>` appears for Claude, Codex, and Copilot only when corresponding status is `OK`, appears after one blank line following `Resets in`, and renders `<remaining>` as bold bright white.
- **TST-011**: MUST verify every provider refresh failure updates provider-scoped idle-time using `idle_until = last_attempt_at + max(idle_delay_seconds, retry_after_seconds_or_0)`, including HTTP `429` and authentication failures without `retry_after` metadata.
- **TST-013**: MUST verify `setup` prompts idle-delay first, API-call delay milliseconds second (default `100`), API-call timeout milliseconds third (default `3000`), `gnome_refresh_interval_seconds` fourth, `billing_data` fifth (default `billing_data`), then per-provider currency symbol prompts, and persists all values into `~/.config/aibar/config.json`.
- **TST-014**: MUST verify `show` evaluates idle-time per provider, serves `~/.cache/aibar/cache.json` for providers with future `idle_until`, and refreshes only providers with missing or expired idle-time state.
- **TST-015**: MUST verify `show --force` removes `~/.cache/aibar/idle-time.json`, bypasses idle-time gating for current execution, refreshes providers, and recreates idle-time metadata before loading `~/.cache/aibar/cache.json`.
- **TST-016**: MUST verify refresh execution enforces configured inter-call delay in milliseconds between provider API requests, using `100` milliseconds when `api_call_delay_milliseconds` is absent.
- **TST-017**: MUST verify CLI `show` invokes one shared cache-retrieval implementation and does not call legacy `ResultCache` read/write APIs.
- **TST-018**: MUST verify failed provider/window refresh attempts set `result=FAIL` and `error` in `cache.json` while preserving the previous payload for the same provider/window.
- **TST-019**: MUST verify partial refresh outcomes can record mixed `OK` and `FAIL` statuses across windows of the same provider without overwriting unaffected payload snapshots.
- **TST-020**: MUST verify refresh and fallback logic do not read or write `~/.cache/aibar/claude_dual_last_success.json`.
- **TST-021**: Tests that mock `httpx.AsyncClient` transport and invoke provider `fetch` or `fetch_all_windows` execution path MUST restrict assertions to success/error state (`is_error`, `error` fields), result-dict window key presence, HTTP call count, and cache/filesystem side effects; MUST NOT assert specific numeric metric field values (`usage_percent`, `remaining`, `cost`) derived from the parsed HTTP response.
- **TST-022**: MUST verify `scripts/claude_token_refresh.sh` `do_refresh()` truncates `LOG_FILE` before writing any log entries (source-level pattern assertion).
- **TST-023**: MUST verify `currency_symbol` in `UsageMetrics` flows through provider fetch and cache serialization to CLI text output (`_print_result`) and GNOME extension cost labels using the symbol from metrics, not a hardcoded `$`.
- **TST-024**: MUST verify `setup` accepts GeminiAI OAuth desktop-client credentials from both pasted JSON and file path input and persists normalized client-secret JSON in `~/.config/aibar/`.
- **TST-025**: MUST verify GeminiAI OAuth authorization requests `bigquery.readonly`, `monitoring.read`, and `cloud-platform` scopes and persists refresh-capable authorized-user credentials for provider fetch execution.
- **TST-026**: MUST verify GeminiAI fetch queries Cloud Monitoring usage metrics with service constraint `resource.labels.service="generativelanguage.googleapis.com"` and `UTC month-start -> now` interval semantics, supports `api`/`consumed_api` metric series, and queries BigQuery billing data using explicit selected columns with latest invoice-month aggregation fallback to current-month `usage_start_time`.
- **TST-027**: MUST verify GeminiAI HTTP `429`, quota-exhaustion, and missing billing-export-table failures preserve cached payload snapshots, mark status `FAIL`, and update only GeminiAI idle-time state according to rate-limit retry policy.
- **TST-028**: MUST verify `setup` currency prompts exclude `geminiai` and GeminiAI rendering in CLI text and JSON payload includes latest-available billing-period monetary cost values when billing data exists.
- **TST-029**: MUST verify GNOME extension renders GeminiAI provider tab/card with bright-purple style class assignment, provider title `GEMINIAI`, provider ordering as the last tab/card after `openai`, and GeminiAI cost/error status propagation from cache payload.
- **TST-030**: MUST verify CLI `show` renders panels ordered `claude`, `openrouter`, `copilot`, `codex`, `openai`, `geminiai`, keeps one shared panel width, never renders `Window <window>` headings, and renders `Status` then right-aligned `Updated/Next` only for `OK` states.
- **TST-031**: MUST verify startup update preflight executes before invalid-argument diagnostics and before subcommand handlers run.
- **TST-032**: MUST verify startup update idle-time gating skips HTTP calls until `idle_until` expires and resumes checks when the idle-state file is missing or expired.
- **TST-033**: MUST verify successful startup update checks create `~/.cache/aibar/` when missing and write `check_version_idle-time.json` with epoch and human-readable `last_success_at` and `idle_until`.
- **TST-034**: MUST verify repeated startup update HTTP `429` responses compute idle-time using `max(300, max(retry-after values))`.
- **TST-035**: MUST verify Linux `--upgrade` and `--uninstall` invoke required `uv tool` subprocess commands, propagate subprocess exit codes, and during `--uninstall` delete `~/.cache/aibar/check_version_idle-time.json` and `~/.cache/aibar/`.
- **TST-041**: MUST verify non-Linux `--upgrade` and `--uninstall` skip lifecycle subprocess execution and print manual command guidance.
- **TST-043**: MUST verify Claude OAuth renewal routine truncates `~/.config/aibar/claude_token_refresh.log`, executes `claude /usage` and `aibar login --provider claude`, and records command-availability failures without aborting execution.
- **TST-044**: MUST verify Claude authentication error `Invalid or expired OAuth token` triggers one renewal attempt and one retry, then persists `claude.oauth_refresh_blocked=true` when retry authentication fails again.
- **TST-045**: MUST verify `claude.oauth_refresh_blocked` suppresses repeated renewal attempts, auto-clears at `last_success_timestamp + 86400`, and is removed on `show --force`.
- **TST-046**: MUST verify GeminiAI CLI text renders `Billing services: <count> (<service1>, <service2>, ...)` using billing `service_description` values, preserving order, and printing all discovered services without truncation markers.
- **TST-036**: MUST verify `--version` and `--ver` print installed version and bypass subcommand execution.
- **TST-038**: MUST verify CLI text `show` prints `Error: <reason>` only on `FAIL`, never renders `Window <window>` headings, renders right-aligned `Updated/Next` only on `OK`, and keeps `show --json` freshness, API-counter, cost, and GeminiAI effective-window behaviors.
- **TST-042**: MUST verify CLI `show` and GNOME provider cards render equivalent `Error: <reason>` output for failed provider/window status without status/window/retry/freshness lines.
- **TST-039**: MUST verify `scripts/aibar.sh` invokes `uv run python -m aibar.cli`, forwards CLI arguments, and contains no virtualenv creation/activation or `pip install -r requirements.txt` commands.
- **TST-040**: MUST verify `.gitignore` includes `uv.lock` and excludes `requirements.txt` from allowlist, repository file `requirements.txt` is absent, and README contains uv-tool requirement plus export command snippet.
- **TST-037**: MUST verify `pyproject.toml` wheel `packages` setting includes the `aibar` package containing `gnome-extension/` subtree, and sdist `include` covers `src/aibar/aibar/gnome-extension/**` and `scripts/**` for `.github/workflows/release-uvx+extension.yml` builds.

## 5. Evidence

| Requirement ID | Evidence (file + symbol + excerpt) |
|---|---|
| PRJ-001 | `src/aibar/aibar/cli.py` + `main/show/doctor/env/setup/login/gnome_install/gnome_uninstall` + `@main.command()` declarations for all subcommands. |
| PRJ-002 | `src/aibar/aibar/cli.py` + `get_providers` + returns Claude/OpenAI/OpenRouter/Copilot/Codex provider instances keyed by `ProviderName`. |
| PRJ-004 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/metadata.json` + `name` set to `AIBar Monitor` and `url/github` owner `Ogekuri`, `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_refreshData/_updateProviderCard` provider-card rendering behavior, and `scripts/test-gnome-extension.sh` exports `MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800`. |
| PRJ-005 | `docs/REFERENCES.md` + repository-wide symbol sections + machine-readable file/symbol index entries. |
| PRJ-006 | `pyproject.toml` + `[build-system]`/`[project]`/`[project.scripts]` sections + `aibar = "aibar.cli:main"` console entry point used by `uv tool install`, `uv run`, and `uvx` execution without external virtualenv bootstrap. |
| PRJ-007 | `README.md` + dedicated `Requirements (uv)` and `Installation (uv)` sections + `uv tool`/`uv run`/`uvx` instructions and optional `uv export --format requirements-txt > requirements.txt` snippet. |
| PRJ-011 | `docs/REQUIREMENTS.md`, `docs/WORKFLOW.md`, and `docs/REFERENCES.md` + GNOME contract documentation sources; repository tree excludes `src/aibar/plans/Gnome.plan.md`. |
| CTN-001 | `src/aibar/aibar/config.py` + `Config.get_token` + env var -> env file -> provider-specific stores (`ClaudeCLIAuth`, `CodexCredentialStore`, `CopilotCredentialStore`). |
| CTN-002 | `src/aibar/aibar/providers/base.py` + `ProviderResult` model + fields `provider/window/metrics/updated_at/raw/error`; `UsageMetrics` + `currency_symbol` field. |
| CTN-003 | `src/aibar/aibar/providers/*.py` + `fetch` methods + `httpx.AsyncClient(timeout=api_call_timeout_milliseconds/1000.0)` in all providers using `RuntimeConfig.api_call_timeout_milliseconds`. |
| CTN-004 | `src/aibar/aibar/cache.py` + cache schema helpers and `src/aibar/aibar/cli.py` + `cache.json` as canonical store for payload snapshots and attempt statuses. |
| CTN-005 | `src/aibar/aibar/config.py` + `PROVIDER_INFO` notes + entries describing unofficial/internal usage for Claude, Copilot, and Codex. |
| CTN-006 | `docs/REFERENCES.md` + full symbol index grouped by source file, regenerated from repository code. |
| CTN-007 | `pyproject.toml` + `[build-system] requires = ["hatchling"]` + `[project]` metadata fields `name`, `version`, `requires-python`, `dependencies` (including `pytest`), and `[project.scripts]`. |
| CTN-008 | `src/aibar/aibar/config.py` + `RuntimeConfig` model + `idle_delay_seconds`, `api_call_delay_milliseconds`, `api_call_timeout_milliseconds`, `gnome_refresh_interval_seconds`, and `currency_symbols` fields persisted in `~/.config/aibar/config.json`. |
| CTN-009 | `src/aibar/aibar/config.py` + `build_idle_time_state/load_idle_time/save_idle_time` + provider-scoped idle-time epoch fields and local-timezone `*_human` serialization in `~/.cache/aibar/idle-time.json`. |
| CTN-010 | `src/aibar/aibar/cache.py` + conditional payload-write helpers guarantee payload replacement only on successful provider/window fetch and payload preservation on failed attempts including HTTP `429`. |
| DES-001 | `src/aibar/aibar/providers/base.py` + `class BaseProvider(ABC)` + abstract methods `fetch`, `is_configured`, `get_config_help`. |
| DES-002 | `src/aibar/aibar/providers/base.py` + `WindowPeriod/ProviderName` + enum literals `5h/7d/30d/code_review` and provider names. |
| DES-003 | `src/aibar/aibar/cli.py` + `parse_window/parse_provider` + raises `click.BadParameter` for invalid inputs. |
| DES-004 | `src/aibar/aibar/cache.py` + `_sanitize_raw` + redacts keys in sensitive set before file write. |
| DES-005 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_loadEnvFromFile` + parses `export KEY=VALUE`, handles quotes/comments/semicolon cleanup. |
| DES-006 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + scheduler-driven `_startAutoRefresh/_refreshData` using `this._refreshIntervalSeconds` read from `json.extension.gnome_refresh_interval_seconds`, popup `Refresh Now` command uses `aibar show --json --force`, interval updated on each successful refresh. |
| REQ-001 | `src/aibar/aibar/cli.py` + `show` loop + `if not prov.is_configured(): ... continue` and text hint `Set {config.ENV_VARS.get(name)}`. |
| REQ-002 | `src/aibar/aibar/cli.py` + `show/_build_dual_window_panel` + default-window Claude/Codex rendering emits one grouped panel each with `5h`/`7d` sections and Codex `Cost/Requests/Tokens` lines after `7d`. |
| REQ-003 | `src/aibar/aibar/cli.py` + `show` JSON renderer emits `indent=2` with `payload`, `status`, `idle_time`, `freshness`, and `extension` sections; `freshness` exports provider-keyed timestamps/local-time strings and `extension` exports `gnome_refresh_interval_seconds`, `idle_delay_seconds`, plus provider-keyed `window_labels`. |
| REQ-004 | `src/aibar/aibar/cli.py` + `doctor` + configuration status and `_fetch_result(provider, WindowPeriod.HOUR_5)` health check. |
| REQ-005 | `src/aibar/aibar/cli.py` + `setup` prompts `idle_delay_seconds`, `api_call_delay_milliseconds`, `api_call_timeout_milliseconds`, and `gnome_refresh_interval_seconds` with defaults `300`, `100`, `3000`, and `60`, then persists `~/.config/aibar/config.json`. |
| REQ-049 | `src/aibar/aibar/cli.py` + `setup` + per-provider currency symbol section after timeout section; prompts each provider with choices `$`/`£`/`€` default `$`; persists `currency_symbols` map in `~/.config/aibar/config.json`. |
| REQ-050 | `src/aibar/aibar/providers/*.py` + `_parse_response`/`_build_result` + `_resolve_currency_symbol` helper resolves currency from raw API response `currency` field; fallback to `RuntimeConfig.currency_symbols[provider_name]`. |
| REQ-051 | `src/aibar/aibar/cli.py` + `_print_result` + cost line uses `m.currency_symbol` instead of hardcoded `$`. |
| REQ-053 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_updateUI/_populateProviderCard` + panel summary cost uses `metrics.currency_symbol`; card cost label uses per-provider `metrics.currency_symbol`. |
| TST-013 | `tests/test_setup_runtime_config.py` + setup prompt-order/default assertions extended with currency symbol prompt section and `currency_symbols` persistence checks. |
| TST-023 | `tests/test_currency_symbol_flow.py` + `currency_symbol` field in `UsageMetrics`, provider fetch pass-through, CLI `_print_result`, and GNOME extension cost label use metrics symbol. |
| REQ-006 | `src/aibar/aibar/cli.py` + `_login_claude` + missing/expired flows print `claude setup-token` then `sys.exit(1)`. |
| REQ-007 | `src/aibar/aibar/providers/copilot.py` + `CopilotDeviceFlow` and `CopilotProvider.login` + device-code request/poll and `save_token`. |
| REQ-009 | `src/aibar/aibar/cli.py` + shared retrieval entrypoint used by `show` + executes force check, per-provider idle-time check, per-provider conditional refresh, then `cache.json` load. |
| REQ-010 | `src/aibar/aibar/cli.py` + provider-window normalization in `show`/refresh pipeline pins OpenAI to `WindowPeriod.DAY_30`; `src/aibar/aibar/providers/openai_usage.py` + `fetch/_get_time_range` executes 30-day usage-cost retrieval. |
| REQ-011 | `src/aibar/aibar/cli.py` + provider-window normalization in `show`/refresh pipeline pins OpenRouter to `WindowPeriod.DAY_30`; `src/aibar/aibar/providers/openrouter.py` + `_get_usage/_parse_response` derives monthly cost and exposes `limit`/`limit_remaining`. |
| REQ-012 | `src/aibar/aibar/providers/copilot.py` + `fetch` + sets `effective_window = WindowPeriod.DAY_30` and returns that window. |
| REQ-013 | `src/aibar/aibar/providers/codex.py` + `_parse_response` + `window_key = "primary_window" if 5h else "secondary_window"`. |
| REQ-014 | `src/aibar/aibar/providers/codex.py` + `CodexCredentials.needs_refresh` + threshold `age.days >= 8`; `CodexProvider.fetch` calls refresher. |
| REQ-015 | `src/aibar/aibar/providers/codex.py` + `fetch` + catches generic refresh exception and continues (`pass  # Continue with existing token`). |
| REQ-016 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_refreshData` and popup `Refresh Now` handler + loads env file and `launcher.setenv(key, value, true)` before command spawn, including `--force` manual refresh path. |
| REQ-017 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_buildPopupMenu/_parseOutput/_updateUI/_populateProviderCard` + popup removes `Open AIBar Report`, `copilot/openrouter/openai/geminiai` render single `30d` window bars with left labels sourced from JSON `extension.window_labels` (fallback `30d`), freshness uses `freshness` data with status+`extension.idle_delay_seconds` fallback, `Costs:` numeric values (currency included) render bold bright white, and OpenRouter/OpenAI/GeminiAI cards suppress empty spacer rows after `Costs:` while API counters stay normalized. |
| REQ-018 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_handleError` + `this._panelLabel.set_text('Err')` and `message.substring(0, 40)`. |
| REQ-019 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_providerOrder` and `_updateUI` sorting enforce `claude/openrouter/copilot/codex/openai/geminiai`; unknown providers rank `999` then lexical order. |
| REQ-020 | `docs/REFERENCES.md` + per-symbol entries containing symbol identifier, file path, and line-range spans. |
| REQ-021 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_buildPanelButton/_updateUI` + panel labels inserted between icon and summary label in fixed order: Claude 5h, Claude 7d, Claude cost, OpenRouter cost, Copilot 30d, Codex 5h, Codex 7d, Codex cost, OpenAI cost, GeminiAI cost. |
| REQ-022 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_buildPanelButton/_updateUI` + panel labels use provider classes/colors; cost labels render provider currency for numeric `0` values and hide only when cost metric is unavailable. |
| REQ-023 | `pyproject.toml` + `[project.scripts]` + `aibar = "aibar.cli:main"` declaration. |
| REQ-024 | `src/aibar/aibar/__main__.py` + `main()` import and invocation from `aibar.cli`. |
| REQ-034 | `src/aibar/aibar/cli.py` + `_format_reset_duration/_print_result` + day-token reset countdown formatting in text output. |
| REQ-035 | `src/aibar/aibar/cli.py` + `_build_result_panel/_print_result` + remaining-credits line gated to `result.is_error == False` and `remaining/limit` presence. |
| REQ-036 | `src/aibar/aibar/cli.py` + `_build_result_panel` failed-state branch returns after error diagnostics and suppresses usage/reset/quota/cost statistics lines; `openai/openrouter/codex/geminiai` `Requests`/`Tokens` lines render with null→`0` normalization on `OK` states. |
| REQ-037 | `src/aibar/aibar/cli.py` + error-rendering lines include unified `HTTP status: <code>, Retry after: <seconds> sec.` string; `src/aibar/aibar/gnome-extension/.../extension.js` + provider-card error block includes equivalent retry metadata text. |
| REQ-038 | `src/aibar/aibar/cli.py` + successful refresh path computes per-provider `idle_until = last_success_at + idle_delay_seconds` and writes provider-keyed epoch/human-readable values to `~/.cache/aibar/idle-time.json`. |
| REQ-039 | `src/aibar/aibar/cli.py` + shared force-refresh handling removes `~/.cache/aibar/idle-time.json`, bypasses idle-time gate, and refreshes before loading `cache.json`. |
| REQ-040 | `src/aibar/aibar/cli.py` + refresh scheduler enforces configured `api_call_delay_seconds` between consecutive provider API requests. |
| REQ-041 | `src/aibar/aibar/cli.py` + refresh-failure handling computes provider-scoped `idle_until = last_attempt_at + max(idle_delay_seconds, retry_after_seconds_or_0)` and persists the failed provider state in `~/.cache/aibar/idle-time.json`. |
| REQ-042 | `src/aibar/aibar/cli.py` + retrieval pipeline uses only `cache.json` and `idle-time.json` persisted artifacts for idle-time-gated API minimization. |
| REQ-043 | `src/aibar/aibar/cli.py` + shared cache refresh/load helpers provide one retrieval implementation for CLI retrieval and render flows. |
| REQ-044 | `src/aibar/aibar/cache.py` + cache status-write helpers persist per-provider/window `result` (`OK`/`FAIL`), `error`, and `updated_at` fields. |
| REQ-045 | `src/aibar/aibar/cache.py` + provider/window upsert path only writes payload on successful fetch outcomes. |
| REQ-046 | `src/aibar/aibar/cache.py` + failed provider/window upsert path preserves existing payload while updating failure status metadata. |
| REQ-047 | `src/aibar/aibar/cli.py` + `src/aibar/aibar/cache.py` + fallback and refresh flows use only `cache.json` and remove dependency on `claude_dual_last_success.json`. |
| TST-001 | `src/aibar/aibar/cli.py` + `parse_window/parse_provider` provide validation points for invalid input diagnostics. |
| TST-002 | `src/aibar/aibar/config.py` + `get_token` implements explicit precedence chain requiring regression coverage. |
| TST-003 | `tests/test_cli_idle_cache.py` and `tests/test_cli_idle_force.py` + assertions for cache schema parity with `show --json` and provider-keyed idle-time epoch/human-readable field persistence under `~/.cache/aibar/`. |
| TST-004 | `tests/test_extension_quota_label.py` + popup-header/remove-action assertions, failed-state metric-row suppression, `extension.window_labels`-driven 30d-bar left-label assertions for `copilot/openrouter/openai/geminiai`, freshness fallback assertions via `extension.idle_delay_seconds`, bottom-right `Updated/Next` assertions, bold-bright-white `Costs:` numeric/no-spacer assertions, and API-counter format assertions for `openai/openrouter/codex/geminiai`. |
| TST-005 | `src/aibar/aibar/providers/copilot.py` + `fetch` hard-codes `effective_window` to `WindowPeriod.DAY_30`. |
| TST-006 | `docs/REFERENCES.md` + generated symbol coverage for tracked `src/` files validates documentation inventory completeness. |
| TST-007 | `tests/test_extension_quota_label.py` + panel-segment order assertions (including OpenAI cost), provider style classes, zero-cost currency-label visibility checks, bold primary percentages, and missing-metric omission behavior. |
| TST-008 | `tests/test_pyproject_metadata.py` + assertions for `[build-system]` backend, `[project.scripts]` entry, `requires-python`, and `dependencies` list containing `pytest` in `pyproject.toml`. |
| TST-010 | `tests/test_reset_pending_message.py` and `src/aibar/aibar/cli.py` + verify remaining-credits rendering path appears only for successful quota-provider states. |
| TST-011 | `tests/test_cli_idle_time_429.py` + provider failure scenarios verify provider-scoped `idle_until = last_attempt_at + max(idle_delay_seconds, retry_after_seconds_or_0)` updates across HTTP `429` and auth failures without retry-after metadata. |
| TST-013 | `tests/test_setup_runtime_config.py` + setup prompt-order/default assertions and `~/.config/aibar/config.json` persistence checks for idle delay, API delay, and gnome_refresh_interval_seconds. |
| TST-014 | `tests/test_cli_idle_cache.py` + provider-scoped idle-time future/missing/expired branches verify per-provider cache-serving behavior and refresh gating in `show`. |
| TST-015 | `tests/test_cli_idle_force.py` + force-refresh path verifies idle-time deletion, gate bypass, refresh invocation, and idle-time regeneration before cache load. |
| TST-017 | `tests/test_cli_cache_status_retention.py` and `src/aibar/aibar/cli.py` + verify shared retrieval usage and absence of `ResultCache` read/write calls in CLI `show` path. |
| TST-018 | `tests/test_cli_cache_status_retention.py` + failed-refresh assertions verify `result=FAIL` with error metadata while preserving existing provider/window payload snapshots. |
| TST-019 | `tests/test_cli_cache_status_retention.py` + mixed-window assertions verify partial provider updates preserve unaffected windows and record per-window status granularity. |
| TST-020 | `tests/test_cli_cache_status_retention.py` + file-system assertions verify no read/write path targets `~/.cache/aibar/claude_dual_last_success.json`. |
| TST-016 | `tests/test_cli_provider_throttle.py` + refresh timing assertions verify configured inter-call delay and default `20`-second fallback. |
| PRJ-008 | `src/aibar/aibar/cli.py` + `gnome_install` command + install/update mode detection using target-directory presence, file copy from package source, update-path disable before copy, and post-copy enable. |
| REQ-025 | `src/aibar/aibar/cli.py` + `_resolve_extension_source_dir` + `Path(__file__).resolve().parent / "gnome-extension" / _EXT_UUID` module-relative path resolution for extension source directory. |
| REQ-083 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/` subtree inside `aibar` package + `pyproject.toml` wheel `packages = ["src/aibar/aibar"]` auto-includes gnome-extension in wheel build. |
| REQ-026 | `src/aibar/aibar/cli.py` + `gnome_install` + `os.makedirs` for target directory creation. |
| REQ-027 | `src/aibar/aibar/cli.py` + `gnome_install` + validates non-empty source directory and `metadata.json` presence. |
| REQ-028 | `src/aibar/aibar/cli.py` + `gnome_install/gnome_uninstall` + `click.style` colored output for status, success, error, and informational messages. |
| REQ-029 | `src/aibar/aibar/cli.py` + `gnome_install` + `shutil.copy2` copies files from package source to target directory replacing existing files. |
| REQ-030 | `src/aibar/aibar/cli.py` + `gnome_install` + `sys.exit(1)` on prerequisite failure with descriptive error message. |
| REQ-031 | `scripts/test-gnome-extension.sh` + launches nested-shell UI directly and contains no `aibar gnome-install` invocation. |
| REQ-032 | `src/aibar/aibar/cli.py` + `gnome_install` + install/update branch execution with install copy→enable and update disable→copy→enable ordering plus colored status output. |
| REQ-099 | `src/aibar/aibar/cli.py` + `gnome_install` update path + non-zero disable outcomes from missing extension treated as masked warnings and flow continues to copy/enable. |
| REQ-033 | `scripts/test-gnome-extension.sh` + no subcommand parameter; executes nested-shell launch directly on invocation. |
| REQ-080 | `src/aibar/aibar/cli.py` + `gnome_uninstall` + `subprocess.run(["gnome-extensions", "disable", "aibar@aibar.panel"])` before removal with colored status output. |
| REQ-081 | `src/aibar/aibar/cli.py` + `gnome_uninstall` + `shutil.rmtree` removes extension directory and all contents. |
| REQ-082 | `src/aibar/aibar/cli.py` + `gnome_uninstall` + `sys.exit(1)` when extension directory does not exist with descriptive error message. |
| TST-009 | `tests/test_gnome_install_uninstall.py` + `gnome-install` install/update branch, update disable→copy→enable ordering, and masked-missing-extension disable assertions; `gnome-uninstall` disable-before-remove and missing-directory exit assertions. |
| TST-021 | `tests/test_claude_retry_and_cli_cache.py` + `TestClaudeRetryOn429::test_retries_on_429_then_succeeds` and `TestFetchAllWindows::test_single_call_returns_both_windows` + metric-value assertions on parsed HTTP responses removed; assertions restricted to `is_error` state, window key presence in results dict, and `mock_get.call_count`. |
| REQ-048 | `scripts/claude_token_refresh.sh` + `do_refresh()` + `> "$LOG_FILE"` truncation statement before first `log` call. |
| TST-022 | `tests/test_claude_token_refresh_script.py` + source-level assertion that `do_refresh()` body contains `LOG_FILE` truncation before any `log` invocation. |
| TST-023 | `tests/test_currency_symbol_flow.py` + assertions for `currency_symbol` field in `UsageMetrics`, CLI `_print_result` cost formatting, and GNOME extension panel label using metrics symbol. |
| TST-030 | `tests/test_cli_show_panel_alignment.py` + CLI output assertions verify provider order, grouped dual-window rendering with `Window 5h:`/`Window 7d:` headings, `Status` first/right-aligned `Updated/Next` last layout, and identical visible panel width. |
| REQ-067 | `src/aibar/aibar/cli.py` + `show/_provider_panel_sort_key/_build_result_panel/_build_dual_window_panel/_emit_provider_panel` + provider ordering, `Window <window>:` headings, status-first and right-aligned freshness-last row placement, ANSI colors, and shared-width rendering. |
| REQ-084 | `src/aibar/aibar/cli.py` + `_build_result_panel/_emit_provider_panel/show` + per-provider freshness line renders `Updated: <datetime>, Next: <datetime>` from provider `idle_time` timestamps with local-timezone `%Y-%m-%d %H:%M` and right-aligned panel layout; `show --json` exports equivalent provider freshness under top-level `freshness` for extension alignment. |
| REQ-085 | `src/aibar/aibar/cli.py` + text renderer surfaces cached authentication/rate-limit failures and suppresses statistics lines for `FAIL` states. |
| REQ-090 | `src/aibar/aibar/cli.py` + `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + both renderers consume identical cached error/status/retry-after payload semantics for failed provider/window states. |
| REQ-060 | `src/aibar/aibar/cli.py` + `show` provider/window resolution and payload rendering expose GeminiAI monitoring/billing/status fields in text and JSON surfaces. |
| REQ-097 | `src/aibar/aibar/cli.py` + `show` GeminiAI provider selection path forces effective `30d` window independent from requested window argument. |
| REQ-098 | `src/aibar/aibar/providers/geminiai.py` + monitoring interval construction uses current UTC month start as interval start and current UTC time as interval end. |
| TST-038 | `tests/test_cli_show_status_messages.py` + verifies CLI `show` right-aligned freshness line uses provider `idle_time` timestamps with local-timezone `%Y-%m-%d %H:%M` parity, `show --json` top-level `freshness` parity, fail-state statistics suppression, retry-after rendering format, `Window <window>:` headings, API-counter null→`0` rendering for `openai/openrouter/codex/geminiai`, and GeminiAI effective window `30d` under non-30d requests. |
| TST-042 | `tests/test_cli_show_status_messages.py` + `tests/test_extension_quota_label.py` + cross-surface assertions for equivalent error category, HTTP status, retry-after value, and `Updated/Next` text sourced from the same `idle_time` timestamps on failed states. |
| REQ-086 | `scripts/aibar.sh` + launcher executes `uv run python -m aibar.cli "$@"` and removes repository virtualenv bootstrap/install commands. |
| REQ-087 | `.gitignore` + allowlist tracks `uv.lock` and drops `requirements.txt`; repository root no longer includes `requirements.txt`; `README.md` includes optional `uv export --format requirements-txt > requirements.txt` command. |
| TST-039 | `tests/test_launcher_uv_only.py` + source-level assertions for `scripts/aibar.sh` uv-run invocation and absence of virtualenv/pip install logic. |
| TST-040 | `tests/test_uv_requirements_surface.py` + assertions for `.gitignore` allowlist change, `requirements.txt` absence, and README uv requirements/export command content. |
| REQ-091 | `src/aibar/aibar/cli.py` + `retrieve_results_via_cache_pipeline` + sequential execution: idle-time check, modular API calls, in-memory collection, locked cache write, locked cache read, presentation. |
| REQ-092 | `src/aibar/aibar/config.py` + `save_cli_cache` is the single write path for `cache.json`. |
| REQ-093 | `src/aibar/aibar/config.py` + `_blocking_file_lock(CACHE_FILE_PATH)` guards every `cache.json` read and write. |
| REQ-094 | `src/aibar/aibar/cli.py` + `retrieve_results_via_cache_pipeline` + at most one `load_cli_cache` per execution path. |
| REQ-095 | `src/aibar/aibar/config.py` + `RuntimeConfig.api_call_timeout_milliseconds` default `3000`; providers use `httpx.AsyncClient(timeout=api_call_timeout_milliseconds/1000.0)`. |
| REQ-096 | `src/aibar/aibar/config.py` + `DEFAULT_API_CALL_DELAY_MILLISECONDS = 100`. |
