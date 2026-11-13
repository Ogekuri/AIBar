---
title: "AIBar Requirements"
description: Software requirements specification
version: "0.6.0"
date: "2026-11-13"
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
AIBar implements a Python CLI/UI usage monitor for Antigravity (AGY), OpenAI, OpenRouter, Copilot, and Codex, plus a GNOME Shell extension that renders the CLI JSON output in the top panel popup UI, and shell scripts for extension installation and maintenance. Provider `agy` extracts quota metrics from the local Antigravity CLI by executing `agy -p /usage` and parsing tab-separated `<group>\t<field>\t<value>` rows after ANSI-escape stripping; Claude support is fully removed.

Used libraries/components evidenced by direct imports:
- Python: `click`, `textual`, `pydantic`, `httpx` (`src/aibar/aibar/*.py`, `src/aibar/aibar/providers/*.py`)
- GNOME JS: `GLib`, `St`, `Gio`, `Clutter`, `GObject`, `Main`, `PanelMenu`, `PopupMenu` (`src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js`)

Performance note: explicit caching optimization uses persistent CLI cache (`~/.cache/aibar/cache.json`), idle-time gating (`~/.cache/aibar/idle-time.json`), configurable provider-call throttling (`api_call_delay_milliseconds`), and configurable HTTP timeout (`api_call_timeout_milliseconds`) to minimize API request volume.

### 1.3 Repository Structure (evidence snapshot)
```text
.
├── .github/
│   └── workflows/
│       └── release-pypi.yml
├── pi-usereq/
│   └── docs/
│       ├── REFERENCES.md
│       ├── REQUIREMENTS.md
│       └── WORKFLOW.md
├── pyproject.toml
├── scripts/
│   ├── aibar.sh
│   ├── build.sh
│   ├── pre-release-check.sh
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
│           ├── cli.py
│           ├── config.py
│           └── providers/
│               ├── agy.py
│               ├── base.py
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
- **PRJ-002**: MUST aggregate provider metrics through a normalized provider contract for `agy`, `openai`, `openrouter`, `copilot`, `codex`, `geminiai`, `zai`, and `deepseek`.
- **PRJ-004**: MUST provide GNOME Shell extension `AIBar Monitor` that executes `aibar show --json`, renders provider-specific cards, exposes owner metadata `url=https://github.com/Ogekuri/AIBar` and `donations.github=Ogekuri`, and forces `scripts/test-gnome-extension.sh` resolution to `1280x720` via `MUTTER_DEBUG_DUMMY_MODE_SPECS=1280x720`.
- **PRJ-005**: MUST maintain a machine-readable symbol inventory in `pi-usereq/docs/REFERENCES.md` for symbols discovered from configured source directories.
- **PRJ-006**: MUST provide a PEP 621-compliant `pyproject.toml` at repository root enabling `uv tool install` distribution execution and `uv run`/`uvx` live execution without external virtualenv bootstrap scripts.
- **PRJ-007**: MUST document in `README.md` a `## Requirements` section covering `uv`-based requirements: Python >= 3.12 floor, installation/removal, `uv run`/`uvx` execution, optional `requirements.txt` export command, and GeminiAI prerequisites.
- **PRJ-008**: MUST provide `aibar gnome-install` CLI command that detects install/update mode for `~/.local/share/gnome-shell/extensions/aibar@aibar.panel/`, copies package extension files, disables extension before update copy, and enables extension after copy.
- **PRJ-009**: MUST execute startup update checks and lifecycle flags `--upgrade`, `--uninstall`, `--version`, `--enable-log`, `--disable-log`, `--enable-debug`, and `--disable-debug` for program `aibar`.
- **PRJ-010**: MUST package all runtime files required by `aibar` so local execution and `uv tool install` execution remain behaviorally equivalent.
- **PRJ-011**: MUST keep GNOME extension contract documentation in `pi-usereq/docs/REQUIREMENTS.md`, `pi-usereq/docs/WORKFLOW.md`, and `pi-usereq/docs/REFERENCES.md`; repository source tree MUST NOT contain `src/aibar/plans/Gnome.plan.md`.
- **PRJ-012**: MUST maintain release automation in `.github/workflows/release-pypi.yml` publishing the sdist, wheel, and GNOME extension zip as GitHub Release assets with changelog for version tags on `master` or `develop`.
- **PRJ-013**: MUST publish the sdist and wheel to PyPI project `aibar` via GitHub Actions Trusted Publishing with OIDC `id-token: write` only for tagged `master` releases.
- **PRJ-014**: MUST declare `[project.urls]` and trove `classifiers` in `pyproject.toml` to complete PyPI project metadata.
- **PRJ-015**: MUST document PyPI installation (`uv tool install aibar`, `uvx aibar`) in `README.md` beside existing git-based instructions.
- **PRJ-016**: MUST document `sudo apt install pipx`, `pipx ensurepath`, and `pipx install aibar` as the primary installation method in `README.md`.
- **PRJ-017**: MUST document `pip install aibar` and `uv`/`uvx` installations in `README.md` as alternative methods after the primary pipx flow.
- **PRJ-018**: MUST document in `README.md` a dedicated non-primary GitHub section covering GitHub package installation, `--upgrade --develop`, and dual-repository `--version` reporting.
- **PRJ-019**: MUST skip PyPI publication when a version tag is on `develop` and not on `master`, while the release workflow still publishes the GitHub Release assets.
- **PRJ-020**: MUST provide executable `scripts/pre-release-check.sh` that runs the authoritative pre-release pipeline and MUST exit `0` only when every mandatory check and the final cleanup succeed.
- **PRJ-021**: `scripts/pre-release-check.sh` MUST abort with non-zero exit status before any pipeline stage when the git working tree contains uncommitted changes, unless the `--allow-dirty` flag is passed.
- **PRJ-022**: `scripts/pre-release-check.sh` MUST execute each pipeline stage with a labeled progress header and MUST abort at the first failing stage with a non-zero exit status.
- **PRJ-023**: `scripts/pre-release-check.sh` MUST execute the unit-test suite via `uv run pytest` and MUST fail with non-zero exit status when any test fails.
- **PRJ-024**: `scripts/pre-release-check.sh` MUST generate the verification artifacts by invoking `scripts/build.sh` with an artifact destination directory inside a pipeline-created temporary directory.
- **PRJ-054**: `scripts/pre-release-check.sh` MUST exit non-zero when the sdist, wheel, or GNOME extension zip is missing from the temporary artifact destination directory after the build.
- **PRJ-025**: `scripts/pre-release-check.sh` MUST remove `build/`, `.pytest_cache/`, `__pycache__` trees under `src/` and `tests/`, a script-created `.venv`, and the pipeline-created temporary directory on pipeline exit, regardless of pipeline outcome.
- **PRJ-050**: `.github/workflows/release-pypi.yml` MUST reuse the sdist, wheel, and GNOME extension zip from `dist/` when all three exist in the tagged commit, and MUST generate them with `scripts/build.sh` otherwise.
- **PRJ-051**: `.github/workflows/release-pypi.yml` MUST fail with non-zero status when the sdist, wheel, or GNOME extension zip is missing from `dist/` after artifact resolution.
- **PRJ-052**: `.github/workflows/release-pypi.yml` MUST execute no pytest suite and no `scripts/pre-release-check.sh`, and MUST generate release artifacts at most once per run through `scripts/build.sh`.
- **PRJ-053**: A release MUST NOT require the sdist, wheel, or GNOME extension zip to be tracked in `dist/` by the tagged commit.
- **PRJ-028**: MUST validate repository structure, required executables (`uv`, `git`, `zip`, `find`, `bash`), and the syntax of every `scripts/*.sh` file before generating artifacts.
- **PRJ-029**: MUST validate Python syntax under `src/` and MUST execute `uv run --locked --with pyright pyright --project pyrightconfig.json`, failing when type checking exits non-zero.
- **PRJ-030**: MUST provide executable `scripts/build.sh` that resolves the repository root from its own path and generates the sdist, wheel, and GNOME extension zip inside the resolved artifact destination directory.
- **PRJ-055**: `scripts/build.sh` MUST resolve the artifact destination directory from the `--dist-dir <Path>` argument when provided and MUST default it to `<repository-root>/dist`.
- **PRJ-056**: `scripts/pre-release-check.sh` MUST behave identically regardless of the presence, absence, or content of the repository `dist/` directory.
- **PRJ-031**: `scripts/build.sh` MUST remove, before building, every artifact-destination entry whose name matches the project sdist, project wheel, or GNOME extension zip pattern for any version number, regardless of entry type.
- **PRJ-057**: `scripts/build.sh` MUST verify after the pre-build cleanup that no artifact-destination entry whose name matches a generated artifact pattern remains, and MUST exit non-zero otherwise.
- **PRJ-032**: `scripts/build.sh` MUST preserve every non-generated file inside the artifact destination directory and MUST NOT delete it.
- **PRJ-033**: `scripts/build.sh` MUST verify that the artifact destination directory contains a non-empty sdist, wheel, and GNOME extension zip and MUST exit non-zero otherwise.
- **PRJ-034**: `scripts/build.sh` MUST leave the generated release artifacts in the artifact destination directory and MUST print a summary listing every produced artifact path.
- **PRJ-035**: `scripts/pre-release-check.sh` MUST register `trap` handlers for EXIT, SIGINT, and SIGTERM that run cleanup, preserve the original exit status, and fail the run when cleanup fails.
- **PRJ-036**: `scripts/pre-release-check.sh` MUST NOT read, verify, delete, clean, or otherwise operate on the repository `dist/` directory or its content.
- **PRJ-037**: `scripts/pre-release-check.sh` MUST verify after cleanup that tracked files are unchanged, no pipeline artifact remains in the working tree, and the post-run git status matches the pre-run status.
- **PRJ-038**: `.gitignore` MUST keep exclude-all-then-reinclude semantics and MUST re-include `dist/` and `dist/**/*` in the "Include specific files and directories" section so optionally committed release artifacts stay git-visible.
- **PRJ-039**: `scripts/build.sh` and `scripts/pre-release-check.sh` MUST locate the repository root from their own paths and MUST work from any invocation directory, including paths with spaces.
- **PRJ-040**: `scripts/build.sh` MUST validate that `uv`, `zip`, and `find` are available and MUST exit non-zero when a required tool is missing.
- **PRJ-041**: Release artifacts in `dist/` (sdist, wheel, GNOME extension zip) MAY be tracked as files of the git repository.
- **PRJ-047**: `scripts/build.sh` MUST remove the `build/`, `.pytest_cache/`, `*.egg-info`, and `__pycache__` intermediate artifacts after every build while retaining every versioned `dist/` artifact.
- **PRJ-048**: `scripts/build.sh` MUST execute the intermediate-artifact cleanup through EXIT, SIGINT, and SIGTERM handlers that preserve the original process exit status.
- **PRJ-049**: `scripts/build.sh` MUST verify after cleanup that no `build/`, `.pytest_cache/`, `*.egg-info`, or `__pycache__` artifact remains outside `dist/` and MUST exit non-zero otherwise.

### 2.2 Project Constraints
- **CTN-001**: MUST resolve provider credentials with precedence: environment variable, then `~/.config/aibar/env`, then provider-specific local credential stores.
- **CTN-002**: MUST represent provider fetch output with `ProviderResult` containing `provider`, `window`, `metrics`, `updated_at`, `raw`, and optional `error`; `UsageMetrics` MUST include `currency_symbol: str` (default `"$"`) annotating all monetary fields (`cost`, `remaining`, `limit`, `total_cost`).
- **CTN-003**: MUST perform external HTTP API calls with `httpx.AsyncClient(timeout=<api_call_timeout_milliseconds>/1000.0)` using `RuntimeConfig.api_call_timeout_milliseconds` for provider integrations.
- **CTN-004**: MUST persist `~/.cache/aibar/cache.json` as the canonical store for per-provider, per-window last-success payload snapshots and last-attempt status metadata.
- **CTN-005**: MAY depend on unofficial/internal endpoints when official usage APIs are unavailable for Copilot or Codex integrations; provider `agy` MUST use the local `agy` CLI subprocess instead of remote HTTP endpoints.
- **CTN-006**: MUST keep `pi-usereq/docs/REFERENCES.md` synchronized with symbols discovered from configured source directories.
- **CTN-007**: MUST declare `hatchling` as `[build-system]` backend in `pyproject.toml` with `[project]` metadata including `name`, `version`, `requires-python`, `[project.scripts]`, and runtime `dependencies`.
- **CTN-008**: MUST persist runtime configuration in `~/.config/aibar/config.json` with keys `idle_delay_seconds`, `api_call_delay_milliseconds`, `api_call_timeout_milliseconds`, `gnome_refresh_interval_seconds`, `billing_data`, `copilot_extra_premium_request_cost`, `currency_symbols`, `log_enabled`, and `debug_enabled`.
- **CTN-009**: MUST persist provider-scoped idle-time state in `~/.cache/aibar/idle-time.json` with `last_success_timestamp` and `idle_until_timestamp` (epoch seconds) and `last_success_human` and `idle_until_human` (local-timezone ISO-8601).
- **CTN-010**: MUST update `cache.json` payload fields only after successful fetch for the same provider/window and MUST preserve previous payload fields on failed fetch attempts, including HTTP `429`.
- **CTN-011**: MUST fetch latest release metadata from `https://pypi.org/pypi/aibar/json` for startup update checks.
- **CTN-012**: MUST use hardcoded startup update-check constants `idle_delay_seconds=300` and `http_timeout_seconds=2`.
- **CTN-013**: MUST persist startup update-check idle state in `~/.cache/aibar/check_version_idle-time.json` JSON with epoch and human-readable `last_success_at` and `idle_until`.
- **CTN-014**: MUST perform at most one startup update HTTP check per 300 seconds unless `~/.cache/aibar/check_version_idle-time.json` is missing or expired.
- **CTN-015**: MUST use standard-process lifecycle command strings exactly as `uv tool install aibar --force` (PyPI), `uv tool install --force git+https://github.com/Ogekuri/<program-name>@<tag_name>` (GitHub), and `uv tool uninstall aibar`.
- **CTN-017**: MUST persist `enabled_providers` in `~/.config/aibar/config.json` as provider-keyed booleans for `agy`, `openrouter`, `copilot`, `codex`, `openai`, `geminiai`, `zai`, and `deepseek`; missing keys MUST default to `true`.
- **CTN-018**: MUST declare `requires-python >= 3.12` in `pyproject.toml` and pin `.python-version` to a Python 3.12+ interpreter so `uv run` never resolves Python 3.11.
- **CTN-019**: MUST declare `pytest` under `[dependency-groups]` `dev` in `pyproject.toml`, outside runtime `[project]` `dependencies`.
- **CTN-020**: MUST fetch latest GitHub release metadata from `https://api.github.com/repos/Ogekuri/<program-name>/releases/latest` parsing `tag_name`, where `<program-name>` is the current program name.
- **CTN-021**: MUST pin every JavaScript-based action referenced by `.github/workflows/release-pypi.yml` to a major version whose upstream `runs.using` runtime is `node24` or later.

## 3. Requirements

### 3.1 Design and Implementation
- **DES-001**: MUST define `BaseProvider` as an abstract interface with `fetch`, `is_configured`, and `get_config_help`.
- **DES-002**: MUST encode supported windows as `5h`, `7d`, `30d`, and `code_review` and provider names as `agy`, `openai`, `openrouter`, `copilot`, `codex`, `geminiai`, `zai`, and `deepseek`.
- **DES-003**: MUST reject invalid CLI window values and provider values using Click `BadParameter`.
- **DES-004**: MUST sanitize sensitive keys (`token`, `key`, `secret`, `password`, `authorization`) from cached raw payloads before disk writes.
- **DES-005**: MUST parse env-file assignments with optional `export`, quoted values, and inline comments in GNOME extension env loading.
- **DES-006**: MUST auto-refresh GNOME extension data at interval read from `extension.gnome_refresh_interval_seconds` in the `aibar show --json` output (fallback `60` seconds when field absent), execute popup `Refresh Now` actions with `aibar show --json --force`, and apply the new interval on each successful data refresh.
- **DES-007**: MUST use provider-registry-driven instantiation so adding `geminiai` introduces no duplicated control-flow branches in `show`, `doctor`, `setup`, `login`, or refresh/load orchestration.
- **DES-008**: MUST include `geminiai`, `zai`, and `deepseek` in provider-name typing and validation while preserving compatibility for `openai`, `openrouter`, `copilot`, and `codex`.

### 3.2 Functions
- **REQ-001**: MUST skip unconfigured providers in `show` output and print missing environment-variable hints when text mode is used.
- **REQ-002**: MUST render default-window Codex as a single panel with `5h` and `7d` sections separated by one blank line; a shared `Remaining credits` line MUST follow `7d` `Resets in`, separated by one blank line and derived from `7d`.
- **REQ-003**: MUST emit pretty-printed JSON (`indent=2`) for `show --json` with top-level sections `payload`, `status`, `idle_time`, `freshness`, and `extension`; `freshness` MUST expose provider-keyed `last_success_timestamp`/`idle_until_timestamp` plus local-time `%Y-%m-%d %H:%M` strings, and `extension` MUST expose `gnome_refresh_interval_seconds`, `idle_delay_seconds`, `copilot_extra_premium_request_cost`, and provider-keyed `window_labels` values consumed by GNOME provider bars.
- **REQ-004**: MUST run provider health checks in `doctor` using the 5-hour window and report per-provider configuration and test status.
- **REQ-005**: MUST prompt `setup` for `idle_delay_seconds` (`300`) first, `api_call_delay_milliseconds` (`100`) second, `api_call_timeout_milliseconds` (`5000`) third, `default_retry_after_seconds` (`3600`) fourth, `gnome_refresh_interval_seconds` (`60`) fifth, and `billing_data` (`billing_data`) sixth, then persist values in `~/.config/aibar/config.json`.
- **REQ-123**: `setup` MUST present a dedicated provider activation section before all other setup sections and prompt toggleable `enable`/`disable` values for `agy`, `openrouter`, `copilot`, `codex`, `openai`, `geminiai`, `zai`, and `deepseek`.
- **REQ-007**: MUST execute GitHub device-flow login for Copilot and save the token in `~/.config/aibar/copilot.json`.
- **REQ-172**: `aibar login` without `--provider` MUST sequentially execute login flows for login-capable providers whose cached last-attempt status in `~/.cache/aibar/cache.json` contains `result=FAIL`.
- **REQ-173**: `aibar login` without `--provider` MUST NOT execute login flows for login-capable providers whose cached window statuses are all `OK` or absent.
- **REQ-174**: `aibar login` without `--provider` MUST print an informational message and exit with status 0 when no login-capable provider is in error state.
- **REQ-175**: `aibar login` without `--provider` MUST exit with non-zero status when at least one executed login flow fails.
- **REQ-176**: MUST expose global flag `--develop` with equivalent alias `--dev` that selects the GitHub package source only for `--upgrade` and has no effect on other invocations.
- **REQ-177**: MUST execute `uv tool install --force git+https://github.com/Ogekuri/<program-name>@<tag_name>` on Linux when `--upgrade` is provided with `--develop` or `--dev`, propagating subprocess exit status.
- **REQ-196**: MUST expose global flag `--force` that selects forced download and full reinstallation mode only for `--upgrade` invocations and has no effect on other invocations.
- **REQ-197**: MUST execute `uv tool install aibar --force --reinstall --refresh` (PyPI index) on Linux when `--upgrade` is provided with `--force` without `--develop`/`--dev`, propagating subprocess exit status.
- **REQ-198**: MUST execute `uv tool install --force --reinstall --refresh git+https://github.com/Ogekuri/<program-name>@<tag_name>` (GitHub) on Linux when `--upgrade` with `--develop`/`--dev` is provided with `--force`, propagating subprocess exit status.
- **REQ-189**: MUST resolve the `--develop`/`--dev` upgrade source tag by fetching `tag_name` from `https://api.github.com/repos/Ogekuri/<program-name>/releases/latest`, independent of the branch carrying the tag, before executing the GitHub lifecycle install.
- **REQ-190**: MUST exit `--upgrade` with `--develop`/`--dev` using non-zero status and a bright-red diagnostic, without executing `uv tool install`, when the latest GitHub release tag cannot be resolved.
- **REQ-191**: MUST define the GitHub program name once as the current program name `aibar` and compose all GitHub release and upgrade URLs from it without duplicated repository literals.
- **REQ-192**: MUST report the `--version` GitHub latest-release version from `https://api.github.com/repos/Ogekuri/<program-name>/releases/latest`, independent of the branch carrying the tag.
- **REQ-193**: MUST report under `--version` the GitHub release identical to the release installed by `--upgrade --develop`/`--dev`, sourced from the same releases/latest fetch.
- **REQ-194**: MUST resolve GitHub releases/latest HTTP failures, including HTTP 404, into failure responses carrying the HTTP status code and failure reason text.
- **REQ-195**: The `--version` GitHub latest-release report MUST render the aligned `Latest @ GitHub` line with failure value `unknown (<reason>)`, where `<reason>` is the GitHub fetch failure message, when the releases/latest check fails.
- **REQ-199**: The `--version`/`--ver` output MUST be exactly three stdout lines labeled `Current Installed`, `Latest @ PyPI`, and `Latest @ GitHub`, each label left-justified in one shared 18-character field followed by `: <version-value>`, so all colons align.
- **REQ-254**: MUST execute `gnome-install` of the newly installed version after the `--upgrade` install subprocess exits `0`, for every `--upgrade` invocation including `--develop`/`--dev` and `--force` variants.
- **REQ-255**: MUST execute the post-upgrade `gnome-install` by spawning the `aibar` console script re-resolved from `PATH` after the install subprocess completes, so the command runs the newly installed version.
- **REQ-256**: MUST propagate the post-upgrade `gnome-install` exit status as the `--upgrade` exit status and MUST NOT execute it when the install subprocess exits non-zero or on non-Linux runtimes.
- **REQ-009**: MUST execute provider retrieval for `show` in this order: force-flag handling, per-provider idle-time evaluation, per-provider conditional refresh to `~/.cache/aibar/cache.json`, then data load from `~/.cache/aibar/cache.json`.
- **REQ-124**: `show` refresh execution MUST exclude disabled providers from fetch scheduling and MUST NOT apply idle-time, API-delay, API-timeout, or retry-after handling to disabled providers.
- **REQ-125**: CLI text `show` MUST omit disabled providers and MUST NOT render panels or not-configured hints for providers whose `enabled_providers.<provider>` flag is `false`.
- **REQ-126**: `show --json` MUST emit top-level section `enabled_providers` and MUST omit disabled providers from `payload`, `status`, `idle_time`, `freshness`, and `extension.window_labels`.
- **REQ-010**: MUST ignore requested window for OpenAI fetch and return effective window `30d` in provider payload, CLI text output, and `show --json`.
- **REQ-011**: MUST ignore requested window for OpenRouter fetch and return effective window `30d` in provider payload, CLI text output, and `show --json`; OpenRouter cost MUST derive from `usage_monthly`.
- **REQ-148**: MUST set OpenRouter `metrics.limit` to API credit total `data.limit` and `metrics.remaining` to `limit - cost` (null when `data.limit` is absent or zero; negative when over-credit).
- **REQ-149**: MUST compute OpenRouter progress-bar percentage as `cost / (cost + remaining) * 100` in CLI text, `show --json`, and GNOME extension.
- **REQ-150**: MUST render OpenRouter over-credit progress bars (percentage > 100) with the same over-limit segment and 100% boundary marker as Copilot over-quota bars.
- **REQ-154**: MUST render OpenRouter usage-row and GNOME single-window bar labels with the effective-window label `30d`, because the OpenRouter key API exposes no explicit timeframe field (it returns `usage_daily`, `usage_weekly`, `usage_monthly`, and all-time `usage` basis values only) and the fixed `WindowPeriod.DAY_30` effective window matches the `usage_monthly` credit basis.
- **REQ-155**: OpenRouter `OK` CLI text blocks and GNOME provider cards MUST NOT render `Requests` or `Tokens` rows because the OpenRouter key API exposes no per-key request/token counters.
- **REQ-156**: OpenRouter provider fetch MUST normalize API all-time usage `data.usage` into `UsageMetrics.total_cost`, with `None` when the value is absent or non-finite.
- **REQ-157**: OpenRouter CLI text blocks and GNOME provider cards MUST render `Total cost: <currency_symbol><total_cost>` after the `Cost` row, and `show --json` MUST expose `metrics.total_cost`, when `total_cost` is finite.
- **REQ-012**: MUST ignore requested window for Copilot fetch, return effective window `30d`, and publish `premium_requests_extra_cost = max(premium_requests - premium_requests_included, 0) * copilot_extra_premium_request_cost` in payload, CLI text, and `show --json`.
- **REQ-013**: MUST select Codex rate-limit primary window for `5h` and secondary window for other requested windows.
- **REQ-014**: MUST attempt Codex token refresh when refresh token exists and `last_refresh` age is at least eight days.
- **REQ-015**: SHOULD continue Codex fetch with existing credentials when non-authentication refresh exceptions occur, leaving refresh failures non-fatal.
- **REQ-016**: MUST load `~/.config/aibar/env` into subprocess environment before GNOME extension executes `aibar show --json` and before popup `Refresh Now` executes `aibar show --json --force`.
- **REQ-017**: GNOME provider cards MUST render `FAIL` blocks as `Status: FAIL`, blank line, `Reason: <reason>`, blank line, and `Updated: <datetime>, Next: <datetime>`, and MUST NOT render `Window 5h:`, `Window 7d:`, or `Window 30d:` text.
- **REQ-018**: MUST set GNOME panel label to `Err` and truncate popup error text to 40 characters when command execution or JSON parsing fails.
- **REQ-019**: SHOULD order extension provider tabs/cards by `agy`, `openrouter`, `copilot`, `codex`, `openai`, `geminiai`, `zai`, `deepseek`, with providers not listed in ordering array appended alphabetically.
- **REQ-020**: MUST include each discovered configured-source symbol in `pi-usereq/docs/REFERENCES.md` with file path, symbol kind, line-range evidence, and parsed Doxygen fields (`@brief`, `@param`, `@return`, `@throws`) when present in source declarations.
- **REQ-021**: GNOME panel status labels MUST render `Err` only for providers whose `status.result=FAIL` category is OAuth or rate-limit, while providers without those failures MUST keep normal percentage/cost labels.
- **REQ-022**: MUST style GNOME panel tab and label fonts with provider classes and bright colors: Antigravity red, OpenRouter orange, Copilot yellow, Codex green, OpenAI blue, GeminiAI purple, Z.ai cyan, DeepSeek rose (`#FF375F`); cost labels MUST use the same font family, render when numeric value is `0`, and hide only when cost metric is unavailable.
- **REQ-023**: MUST declare a `[project.scripts]` entry `aibar = "aibar.cli:main"` in `pyproject.toml` so that `uv pip install` and `uvx` resolve the `aibar` console command.
- **REQ-024**: MUST provide `src/aibar/aibar/__main__.py` that delegates to `aibar.cli:main` to enable `python -m aibar` execution.
- **REQ-025**: MUST resolve GNOME extension source files from within the `aibar` Python package directory via module-relative path resolution (`Path(__file__).resolve().parent / "gnome-extension" / <UUID>`) in `gnome-install`, independent of git repository, working directory, or installation method (editable, wheel, `uv tool`).
- **REQ-083**: MUST place the GNOME extension source directory (`gnome-extension/aibar@aibar.panel/`) inside the `aibar` Python package subtree (`src/aibar/aibar/gnome-extension/`) so that wheel and sdist builds include extension files within the installed package at `<site-packages>/aibar/gnome-extension/aibar@aibar.panel/`.
- **REQ-026**: MUST create target directory `~/.local/share/gnome-shell/extensions/aibar@aibar.panel/` if it does not exist before copying extension files in `gnome-install`.
- **REQ-027**: MUST validate that the extension source directory is non-empty and contains `metadata.json` before copying in `gnome-install`.
- **REQ-028**: MUST produce colored, formatted terminal output via Click styling for status, success, error, and informational messages in `gnome-install` and `gnome-uninstall` commands.
- **REQ-029**: MUST copy all files from the package extension source directory to target directory, replacing any existing files, in `gnome-install`.
- **REQ-030**: MUST exit with non-zero status and descriptive error message when any prerequisite check fails in `gnome-install`.
- **REQ-031**: `scripts/test-gnome-extension.sh` MUST execute `scripts/aibar.sh gnome-install` before launching the nested Wayland GNOME Shell test session.
- **REQ-032**: `gnome-install` MUST execute install and update flows with colored status output: install flow copies extension files then enables `aibar@aibar.panel`; update flow disables `aibar@aibar.panel`, copies files, then enables `aibar@aibar.panel`.
- **REQ-099**: `gnome-install` update flow MUST mask non-zero disable outcomes caused by extension absence and continue copy/enable without exposing raw disable errors.
- **REQ-033**: `scripts/test-gnome-extension.sh` MUST NOT accept subcommand parameters and MUST execute its install-and-launch flow immediately on invocation without arguments.
- **REQ-034**: MUST render reset countdown as `Resets in: <d>d <h>h <m>m` for durations >= 24 hours in CLI text output.
- **REQ-035**: MUST print `Remaining credits: <remaining> / <limit>` for Codex and Copilot only when rendered status is `OK` and both values exist; line MUST follow `Resets in` after one blank line and `<remaining>` MUST be bold bright white.
- **REQ-036**: CLI text `show` MUST render `FAIL` provider/window blocks as `Status: FAIL`, blank line, `Reason: <reason>`, blank line, and `Updated: <datetime>, Next: <datetime>`, while `openai`, `codex`, `geminiai` `OK` blocks MUST normalize null API counters to `0`.
- **REQ-037**: CLI text `show` and GNOME provider-card error blocks MUST NOT append HTTP status or retry-after metadata in `FAIL` output blocks.
- **REQ-038**: MUST update only the refreshed provider idle-time entry after success by setting `last_success_at` to refresh completion time and `idle_until` to `last_success_at + idle_delay_seconds`, then persist epoch and human-readable values in `~/.cache/aibar/idle-time.json`.
- **REQ-039**: MUST support force-refresh handling that deletes `~/.cache/aibar/idle-time.json`, bypasses idle-time gating for the current execution, and executes a fresh provider refresh before loading `~/.cache/aibar/cache.json`.
- **REQ-040**: MUST enforce at least `api_call_delay_milliseconds` between consecutive provider API requests during refresh execution, with default `100` milliseconds when configuration is missing.
- **REQ-041**: MUST update idle-time for each provider refresh failure in `~/.cache/aibar/idle-time.json` using `idle_until = last_attempt_at + max(idle_delay_seconds, resolved_retry_after_seconds)`, where `resolved_retry_after_seconds` is parsed from API error metadata or `default_retry_after_seconds` when `retry_after_unavailable=true`.
- **REQ-042**: MUST minimize provider API requests and cache I/O by reusing in-memory cache and idle-time state within each refresh cycle and persisting `cache.json` or `idle-time.json` only when content changes.
- **REQ-043**: MUST centralize refresh and load logic for `~/.cache/aibar/cache.json` into shared internal functions reused by CLI `show` refresh and output workflows.
- **REQ-091**: `show` command MUST execute in this sequential order: (1) evaluate idle-time per provider to determine refresh need, (2) execute modular API calls only for providers with expired idle-time, collecting results in memory, (3) compute new idle-time values applying `idle_until = max(current_time + retry_after, current_time + idle_delay)` for errors, (4) write updated cache and idle-time under lock file, (5) read `cache.json` under lock file, (6) present results.
- **REQ-092**: MUST maintain exactly one code path for creating or updating `~/.cache/aibar/cache.json`; no other function MUST write to `cache.json`.
- **REQ-093**: MUST guard every read and write of `~/.cache/aibar/cache.json` with a blocking lock file `~/.cache/aibar/cache.json.lock`; lock MUST be created before write and released after write completes; reads MUST block while lock file exists.
- **REQ-094**: MUST perform at most one disk read of `~/.cache/aibar/cache.json` per `show` command execution when no refresh is needed, and at most one disk read after the single write when refresh occurs.
- **REQ-095**: MUST persist `api_call_timeout_milliseconds` (default `5000`) in `RuntimeConfig` and use it as the HTTP response timeout for all provider API calls via `httpx.AsyncClient(timeout=<value>/1000.0)`.
- **REQ-096**: MUST default `api_call_delay_milliseconds` to `100` when configuration is missing.
- **REQ-044**: MUST persist per-provider, per-window last-attempt status in `cache.json` with fields `result`, `error`, and `updated_at`, where `result` is `OK` or `FAIL`.
- **REQ-045**: MUST overwrite a provider/window payload in `cache.json` only when the current fetch for that provider/window succeeds.
- **REQ-046**: MUST preserve the previous provider/window payload in `cache.json` when the current fetch for that provider/window fails, including HTTP `429`.
- **REQ-047**: MUST store and load all last-success fallback payloads from `~/.cache/aibar/cache.json` and MUST NOT require legacy per-provider snapshot files.
- **REQ-049**: `setup` MUST prompt for per-provider default currency symbol (choices: `$`, `£`, `€`; default `$`) for providers `openai`, `openrouter`, `copilot`, `codex`, `geminiai`, `zai`, and `deepseek` in a dedicated section after timeout configuration, then persist selections in `~/.config/aibar/config.json` `currency_symbols`; provider `agy` MUST be excluded because it exposes no monetary metrics.
- **REQ-107**: MUST expose global flags `--enable-log`, `--disable-log`, `--enable-debug`, and `--disable-debug` that update `~/.config/aibar/config.json` and persist until reconfigured.
- **REQ-108**: `setup` MUST present a final logging section after all existing setup sections and MUST configure `log_enabled` and `debug_enabled` in `~/.config/aibar/config.json`.
- **REQ-109**: `--enable-log` and `--disable-log` MUST set `log_enabled` to `true` and `false` respectively without modifying `debug_enabled`.
- **REQ-110**: `--enable-debug` and `--disable-debug` MUST set `debug_enabled` to `true` and `false` respectively without modifying `log_enabled`.
- **REQ-111**: When `log_enabled` is `true`, CLI executions MUST append entries to `~/.cache/aibar/aibar.log`, and each non-empty entry line MUST start with timestamp `%Y-%m-%d %H:%M:%S`.
- **REQ-112**: Logging MUST record execution start, idle-time verification, idle-time-driven function branches, lock-acquisition timeout failures, error-handling branches, and every load/save operation targeting `~/.cache/aibar/cache.json`.
- **REQ-113**: Logging MUST record execution outcome and execution end time, then append one trailing empty line to separate the current execution block from the next execution block.
- **REQ-114**: API-call debug logging MUST append API metadata and debug response summaries only when both `log_enabled` and `debug_enabled` are `true`; for failed API calls, log `raw` as unmodified full JSON response payload.
- **REQ-115**: When `log_enabled` is `true`, runtime logging MUST append non-debug rows for provider `FAIL` attempts categorized as `oauth` or HTTP `429` `rate_limit`, including `retry_after_seconds` or `retry_after_unavailable=true` with extraction evidence; payload dump remains debug-only.
- **REQ-116**: `setup` MUST present a dedicated Copilot premium section after `billing_data` that prompts `copilot_extra_premium_request_cost` with default `0.04` USD per premium request and persists it in `~/.config/aibar/config.json`.
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
- **REQ-127**: GNOME extension MUST parse `enabled_providers` before provider extraction and MUST hide tabs, cards, and panel status labels for providers whose flag is `false`.
- **REQ-062**: GNOME tab/card labels MUST render `GEMINIAI`; machine-readable payload keys and CLI provider arguments MUST remain lowercase `geminiai`; CLI display title for provider `geminiai` MUST render `GEMINIAI`.
- **REQ-063**: Refresh scheduling MUST apply configured inter-provider call delay and provider-scoped idle-time lifecycle updates to GeminiAI fetches identically to existing providers, including `idle-time.json` updates after success and rate-limited failures.
- **REQ-064**: GeminiAI billing fetch MUST read `<project_id>` from `~/.config/aibar/geminiai_oauth_client.json`, discover `<table_id>` by listing tables in dataset `RuntimeConfig.billing_data` (default `billing_data`), and fail with structured error when billing export table is unavailable.
- **REQ-065**: GeminiAI billing fetch MUST query `<billing_dataset>.gcp_billing_export_v1_<table_id>` using explicit column projection and aggregate the latest available invoice month (`MAX(invoice.month)`); when invoice month is unavailable, implementation MUST fallback to `usage_start_time >= TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), MONTH)`.
- **REQ-066**: MUST guard every read/write of `~/.cache/aibar/cache.json` and `~/.cache/aibar/idle-time.json` with lock files under `~/.cache/aibar/`, polling every 250 milliseconds, and fail with explicit error after 5 seconds if lock acquisition remains blocked.
- **REQ-067**: CLI `show` text mode MUST render ANSI provider-colored bordered panels ordered `agy`, `openrouter`, `copilot`, `codex`, `openai`, `geminiai`, `zai`, `deepseek`, keep one shared panel width, and render `Status` first on `OK`.
- **REQ-128**: CLI `show` text mode MUST render `Usage: <window> <progress_bar> <percent>%` for `agy`, `copilot`, `codex`, and `zai`.
- **REQ-132**: CLI `show` text mode for `openrouter` MUST render `Usage: <window> <progress_bar> <percent>%` using the standard fixed-width CLI progress-bar format.
- **REQ-131**: CLI text `show` for `openai` and `geminiai` MUST render `Usage: <window> <percent>%` and MUST NOT print progress bars.
- **REQ-129**: CLI `show` text mode MUST render Copilot `Cost: <currency_symbol><value>` after one blank line following `Remaining credits` and MUST NOT render `Window <window>` heading text.
- **REQ-117**: GNOME Copilot card MUST render `Cost: <currency_symbol><value>` from `metrics.cost` (fallback `premium_requests_extra_cost`), including `0`, preserving existing Copilot typography and spacing.
- **REQ-118**: GNOME panel status bar MUST place Copilot `<currency_symbol><cost>` immediately after Copilot percentages and before Codex status labels when Copilot cost is available.
- **REQ-068**: Bare `aibar` and `aibar --help` MUST print human-readable usage text listing all commands and global or command-specific options, including `show --force`, `show --json`, `gnome-install`, `gnome-uninstall`, `--version`, `--upgrade` optionally combined with `--develop`/`--dev` and auxiliary `--force`, `--uninstall`, `--enable-log`/`--disable-log`, and `--enable-debug`/`--disable-debug` examples, without Doxygen tags.
- **REQ-069**: GNOME panel icon MUST be bright white when all percentages are <= 25, bright yellow when any percentage > 25, bright orange when any percentage > 50, bright red when any percentage > 75, and blinking bright-red/dim-red when any percentage > 90.
- **REQ-070**: MUST execute startup update-check preflight before CLI argument validation and command dispatch.
- **REQ-071**: MUST skip startup update HTTP calls while current epoch is lower than persisted `idle_until` in `~/.cache/aibar/check_version_idle-time.json`, except when invocation includes `--version`.
- **REQ-072**: MUST create missing `~/.cache/aibar/` and create or overwrite `check_version_idle-time.json` after successful startup update checks with epoch and human-readable `last_success_at=now` and `idle_until=now+300`.
- **REQ-073**: MUST print a bright-green message containing installed version and latest available version when the latest PyPI release is newer.
- **REQ-074**: MUST print bright-red error diagnostics when startup update checks fail, including HTTP status details such as `403`.
- **REQ-075**: MUST process startup update HTTP `429` responses by updating idle-time with `max(300, max_retry_after_seconds_observed)`.
- **REQ-076**: MUST execute `uv tool install aibar --force` (PyPI index) only on Linux when `--upgrade` is provided without `--develop`/`--dev` and MUST propagate subprocess exit status.
- **REQ-077**: MUST execute `uv tool uninstall aibar` only on Linux when `--uninstall` is provided, MUST propagate subprocess exit status, and MUST delete `~/.cache/aibar/check_version_idle-time.json` and `~/.cache/aibar/`.
- **REQ-088**: MUST NOT execute lifecycle `uv tool` subprocess commands for `--upgrade` or `--uninstall` on non-Linux operating systems.
- **REQ-089**: MUST print explicit manual command guidance for the current non-Linux operating system when `--upgrade` or `--uninstall` is provided.
- **REQ-078**: MUST print installed program version, then labeled latest-release versions for PyPI and GitHub, when `--version` is provided; startup release check MUST ignore `check_version_idle-time.json`.
- **REQ-079**: MUST include runtime files required by startup update-check behavior in `pyproject.toml` package configuration used by `.github/workflows/release-pypi.yml`.
- **REQ-080**: MUST disable the extension via `gnome-extensions disable aibar@aibar.panel` before removing files in `gnome-uninstall` with colored status output.
- **REQ-081**: MUST remove the extension directory `~/.local/share/gnome-shell/extensions/aibar@aibar.panel/` and all its contents in `gnome-uninstall`.
- **REQ-082**: MUST exit with non-zero status and descriptive error message when the extension directory does not exist in `gnome-uninstall`.
- **REQ-084**: CLI text `show` MUST render right-aligned `Updated: <datetime>, Next: <datetime>` freshness lines for both `OK` and `FAIL` provider/window blocks, and `show --json` MUST export provider freshness in local-time `%Y-%m-%d %H:%M`.
- **REQ-085**: CLI text `show` MUST render per-provider last-attempt authentication and refresh-rate-limit failures from cached status errors, including invalid or expired OAuth tokens and HTTP `429` refresh-limit diagnostics; when status is `FAIL`, statistics lines MUST remain suppressed.
- **REQ-090**: GNOME provider cards MUST render error category, HTTP status, and retry-after values from cached status entries using semantics equivalent to CLI `show` for the same provider/window.
- **REQ-119**: GNOME extension popup window MUST enforce a fixed standard width, word-wrap verbose error messages, and constrain tab content and status bars to prevent horizontal UI expansion.
- **REQ-120**: GNOME extension popup window MUST size the provider-card viewport to active content height up to a fixed maximum and MUST avoid persistent empty bottom space when content height is lower.
- **REQ-121**: GNOME provider-card progress bars for `agy`, `openrouter`, `copilot`, `codex`, and `zai` MUST render >100 with a visible over-limit segment and preserved 100% boundary marker.
- **REQ-130**: GNOME provider cards for `openai` and `geminiai` MUST render `Usage: <window> <percent>%` text and MUST NOT render progress bars.
- **REQ-122**: CLI text `show` progress bars for `agy`, `openrouter`, `copilot`, `codex`, and `zai` MUST render >100 with a visible over-limit segment and preserved 100% boundary marker.
- **REQ-086**: `scripts/aibar.sh` MUST execute CLI via `uv run python -m aibar.cli` and MUST NOT create, activate, or install dependencies into repository-local or system virtual environments.
- **REQ-087**: Repository root MUST track `uv.lock`, MUST NOT track `requirements.txt`, and MUST keep `README.md` instructions for optional export command `uv export --format requirements-txt > requirements.txt`.
- **REQ-133**: CLI `show` panels, GNOME tabs/cards, and GNOME panel status labels MUST preserve canonical order `agy`, `openrouter`, `copilot`, `codex`, `openai`, `geminiai`, `zai`, `deepseek` after disabled providers are filtered out.

### 3.3 Z.ai Provider
- **REQ-134**: MUST implement provider `zai` (Z.ai) that fetches quota data from `https://api.z.ai/api/monitor/usage/quota/limit` using `Authorization: Bearer <key>` and `Accept: application/json` headers.
- **REQ-135**: MUST resolve the Z.ai API key from `ZAI_API_KEY` with env var then `~/.config/aibar/env` precedence and MUST prompt it in `setup`.
- **REQ-136**: MUST map Z.ai `data.limits` entries by `unit`: `3`/`number=5` to 5 Hours Quota, `6`/`number=1` to Weekly Quota, `5`/`number=1`/`TIME_LIMIT` to Total Monthly Web Search/Reader/Zread Quota.
- **REQ-137**: MUST expose each Z.ai quota `percentage` and `nextResetTime` and label quota progress-bar rows with `5h`, `1w`, and `1m` in CLI text and GNOME provider cards; each quota reset time MUST render immediately after its usage row.
- **REQ-145**: MUST render each Z.ai quota reset time as `Resets in: <duration>` in CLI text and as `Reset in: <duration>` in GNOME provider cards, using the format `<d>d <h>h <m>m` for durations >= 24 hours and `<h>h <m>m` for durations < 24 hours, resolved from `reset_at_epoch_ms` with `datetime`/ISO-8601-string `reset_at` fallback.
- **REQ-146**: MUST coerce Z.ai quota `reset_at_epoch_ms` from float to int when the value is finite and non-negative, so that `_coerce_zai_quota_reset_at` correctly resolves the reset datetime through the cache round-trip for all quotas including the 5h quota.
- **REQ-147**: MUST derive the Z.ai `5h` quota `reset_at_epoch_ms` from the next UTC 5-hour boundary (00:00, 05:00, 10:00, 15:00, 20:00) when the 5 Hours limit entry omits `nextResetTime`, so `Resets in` renders for the `5h` progress bar.
- **REQ-138**: MUST render Z.ai as the last provider in CLI text panels, GNOME tabs/cards, and GNOME panel status bar.
- **REQ-139**: MUST drive Z.ai GNOME panel icon threshold color from the maximum percentage across all Z.ai quotas.
- **REQ-140**: MUST render Z.ai quotas as progress-bar usage rows with short side labels `5h`, `1w`, and `1m` in CLI text and GNOME provider cards, consistent with bar providers agy, openrouter, copilot, and codex.
- **REQ-141**: MUST treat Z.ai as a single fixed-window provider with effective window `30d` that ignores the requested window and fetches all quotas in one API call.
- **REQ-142**: MUST reuse the shared provider cache and idle-time lifecycle for Z.ai without modifying cache, idle-time, retry, or throttling logic.
- **REQ-143**: MUST render Z.ai GNOME panel status bar with the `5h` quota percentage (non-bold) followed by the `1w` quota percentage (bold), and MUST NOT hide Z.ai panel status labels when the Z.ai provider is enabled and has available quota data.
- **REQ-144**: GNOME extension `_handleError` MUST reset text and hide every panel status label created in `_buildPanelButton` including `_panelOpenAICostLabel`, `_panelAgyPctLabel`, `_panelAgy7dPctLabel`, `_panelOpenRouterCostLabel`, `_panelCopilotPctLabel`, `_panelCopilotExtraCostLabel`, `_panelCodexPctLabel`, `_panelCodex7dPctLabel`, `_panelCodexCostLabel`, `_panelGeminiaiCostLabel`, `_panelZaiPctLabel`, `_panelZaiWeeklyPctLabel`, and `_panelDeepSeekBalanceLabel`.

### 3.4 Antigravity (AGY) Provider
- **REQ-158**: MUST implement provider `agy` (Antigravity CLI) that extracts quota metrics by executing `agy -p /usage` as one local subprocess and parsing tab-separated `<group>\t<field>\t<value>` rows after stripping ANSI escape sequences.
- **REQ-159**: MUST map AGY group `Gemini Models` fields `Weekly Limit Remaining` and `Five Hour Limit Remaining` to quotas labeled `G 7d` and `G 5h`.
- **REQ-160**: MUST map AGY group `Claude and GPT models` fields `Weekly Limit Remaining` and `Five Hour Limit Remaining` to quotas labeled `CG 7d` and `CG 5h`.
- **REQ-161**: MUST map AGY group `Gemini 4 Argon` field `Gemini 4 Argon Weekly Limit` to quota labeled `A 7d`.
- **REQ-162**: MUST extract each AGY quota value as the first percentage matching `[0-9]+([.][0-9]+)?%` in the TSV value column; missing rows MUST be omitted, never fabricated.
- **REQ-163**: MUST normalize each AGY remaining percentage to used percentage `100 - remaining` clamped to `[0.0, 100.0]` for CLI text, `show --json`, and GNOME rendering.
- **REQ-164**: MUST expose AGY quotas in `raw.agy_quotas` records with fields `quota_key`, `label`, `remaining_percent`, and `percentage` (used) so cache round-trips preserve quota identity.
- **REQ-165**: MUST treat `agy` as a single fixed-window provider with effective window `30d` that ignores the requested window, fetches all quotas in one subprocess call, and reuses the shared cache and idle-time lifecycle unmodified.
- **REQ-166**: MUST classify AGY authentication failures when output matches `authentication failed|unauthorized|not authenticated|please log in|login expired` case-insensitively, and MUST return error results when the subprocess exits non-zero or returns no quota rows.
- **REQ-167**: MUST report `agy` as not configured when the `agy` executable is absent from `PATH` and MUST render a CLI-missing hint instead of an environment-variable hint.
- **REQ-168**: MUST render AGY quotas as CLI progress-bar usage rows and GNOME per-quota progress bars with labels `G 7d`, `G 5h`, `CG 7d`, `CG 5h`, `A 7d`, styled identically to Z.ai quota rows.
- **REQ-169**: MUST position `agy` first in CLI panels, GNOME tabs/cards, and GNOME panel status ordering, reusing Claude's former red palette (CLI `\033[91m`, GNOME `#FF3B30`).
- **REQ-170**: MUST render the AGY GNOME panel status bar with the `G 5h` quota percentage followed by the `G 7d` quota percentage, and MUST drive panel icon thresholds from the maximum AGY quota percentage.
- **REQ-171**: MUST exclude `agy` from `setup` currency-symbol prompts and monetary rendering because the AGY surface exposes no cost metrics.

### 3.5 Nested Session Debug Environment
- **REQ-178**: `scripts/test-gnome-extension.sh` MUST launch every nested GNOME Shell branch through `scripts/aibar-nested-debug-session.sh` inside a dedicated D-Bus session shared by the nested shell and the debug shell.
- **REQ-179**: `scripts/aibar-nested-debug-session.sh` MUST launch its argv as the nested GNOME Shell command in background and MUST terminate it on SIGINT or SIGTERM.
- **REQ-180**: `scripts/aibar-nested-debug-session.sh` MUST start an interactive debug shell sharing the nested session bus after a 3-second startup settle delay.
- **REQ-181**: `scripts/aibar-nested-debug-session.sh` MUST print extension inspection guidance commands before starting the interactive debug shell.
- **REQ-182**: `scripts/aibar-nested-debug-session.sh` MUST terminate the nested shell when the interactive debug shell exits.

- **REQ-183**: MUST support GNOME Shell 50.1 and subsequent 50.x releases with extension enable, refresh, popup rendering, and disable behavior preserved.
- **REQ-184**: MUST declare GNOME major version `50` in extension metadata and add subsequent major versions after compatibility verification.
- **REQ-185**: MUST launch `scripts/test-gnome-extension.sh` on Ubuntu 26.04 as a visible nested GNOME session using the advertised windowed backend.
- **REQ-186**: MUST report missing graphical-session prerequisites or windowed-backend capabilities with a non-zero exit before extension installation.
- **REQ-187**: MUST use GNOME 50-supported widget orientation and child-attachment APIs throughout extension UI construction.
- **REQ-188**: MUST accept global flag `--ver` as an exact alias of `--version`, producing identical version output, release report, pre-dispatch exit, and startup idle-gate bypass.

### 3.6 Configuration CLI
- **REQ-200**: MUST expose global group options `--print [Path]`, `--info [Path]`, `--print-raw`, `--get Path`, `--set Path Value`, and `--unset Path` on the `aibar` command.
- **REQ-201**: MUST resolve configuration paths case-sensitively as colon-separated tokens whose first token is a `RuntimeConfig` field name and whose optional second token addresses a map key.
- **REQ-202**: MUST reject unknown field tokens, surplus tokens, empty tokens, and absent map keys with exit status 1 and one stderr diagnostic naming the rejected path.
- **REQ-203**: MUST treat `Application_Configuration` as a virtual display root that MUST NOT be accepted as a CLI path token.
- **REQ-204**: MUST reject the reserved tokens `append`, `+`, and `insert` in every configuration path because the `aibar` schema defines no array parameter.
- **REQ-205**: MUST NOT implement a project-local configuration layer because the application defines only the global `~/.config/aibar/config.json` file.
- **REQ-206**: MUST initialize `~/.config/aibar/config.json` from `RuntimeConfig` schema defaults when the file is missing and MUST NOT overwrite an existing file.
- **REQ-207**: MUST reject an unparsable JSON configuration file with exit status 1 and MUST NOT rewrite that file during configuration CLI execution.
- **REQ-208**: MUST validate the complete candidate configuration document before every write and MUST reject documents containing keys absent from `RuntimeConfig`.
- **REQ-209**: MUST accept configuration documents that omit schema fields and MUST resolve omitted fields from `RuntimeConfig` defaults.
- **REQ-210**: MUST parse `--set` input as JSON when the input is valid JSON and MUST type-check the parsed value against the schema before mutation.
- **REQ-211**: MUST treat non-JSON `--set` input as a literal string value only when the target schema type is `String` or `Optional[String]`.
- **REQ-212**: MUST persist `--set` and `--unset` results through a same-directory temporary file, file flush, file fsync, atomic replace, and directory fsync.
- **REQ-213**: MUST preserve the mode of an existing `~/.config/aibar/config.json` and MUST create a new configuration file with mode `0o600`.
- **REQ-214**: MUST keep the previous `~/.config/aibar/config.json` byte-identical and MUST remove temporary files when a write attempt fails.
- **REQ-215**: MUST emit `--get` success output as one JSON value plus one newline on stdout without labels, tree decoration, or confirmation text.
- **REQ-216**: MUST emit `--print-raw` output as the unmodified on-disk `config.json` bytes on stdout without validation, reformatting, headings, or appended text.
- **REQ-217**: MUST route `--print`, `--info`, `--get`, and `--print-raw` success output to stdout and every diagnostic to stderr with exit status 0 on success and 1 on failure.
- **REQ-218**: MUST emit no stdout text for successful `--set` and `--unset` execution.
- **REQ-219**: MUST restore a schema default by removing the addressed field on `--unset <Field>` and MUST delete exactly the addressed map key on `--unset <Field>:<Key>`.
- **REQ-220**: MUST reject `--unset <Field>:<Key>` with exit status 1 when the addressed map key is absent from the stored map.
- **REQ-221**: MUST replace the whole map on `--set <Field> <JsonObject>` only after validating every map key and value against the schema.
- **REQ-222**: MUST render `--print` and `--info` output through one shared recursive tree renderer driven by one shared schema node model.
- **REQ-223**: MUST render the whole configuration tree when no path is given and only the requested parameter or subtree when a path is given.
- **REQ-224**: MUST render every real non-root node with exactly one `├── ` or `└── ` marker preceded by one four-character ancestor segment per ancestor that has a later sibling.
- **REQ-225**: MUST prefix every attached detail line with the ancestor segments of its owning node plus `│   ` when that node has a later sibling and four spaces otherwise.
- **REQ-226**: MUST render a requested path root without a tree marker and MUST indent its attached details by exactly four spaces.
- **REQ-227**: MUST attach metadata, notes, and table rows only as detail lines and MUST NOT render them as configuration tree child nodes.
- **REQ-228**: MUST render `--print` parameter lines as `Token = <value>` with JSON-encoded values and a `(default)` or `(custom | default: <json>)` status suffix.
- **REQ-229**: MUST render `--print` map parameters as `(<N> entries | key target: <FullPath>:<Key>)` followed by an attached two-column `Key | Value` table.
- **REQ-230**: MUST render an empty `--print` map as `(empty map | set key: --set <FullPath>:<ExampleKey> <valid example>)` and MUST NOT render an empty table.
- **REQ-231**: MUST render `--info` parameter headings as `Token - [Type: constraints] <description>` followed by `Default`, `Set cmd`, `Reset cmd`, and map action detail lines with complete canonical paths.
- **REQ-232**: MUST render the `currency_symbols` value domain as an attached `Allowed Values` table covering `$`, `£`, and `€` with `Value`, `Default`, and `Meaning` columns.
- **REQ-233**: MUST build every attached table from measured display widths so all border and separator characters align on one column boundary set.
- **REQ-234**: MUST measure table cells by Unicode terminal display width after escaping control characters and newlines.
- **REQ-235**: MUST derive every published example value, constraint label, default, and allowed value from the shared configuration schema.
- **REQ-236**: MUST abort at import time when the shared configuration schema field set diverges from `RuntimeConfig` model fields.
- **REQ-237**: MUST list `--print`, `--info`, `--print-raw`, `--get`, `--set`, and `--unset` in `aibar --help` with complete canonical path examples.
- **REQ-238**: MUST emit every configuration CLI identifier, description, help text, diagnostic, and rendered value in English.

### 3.7 DeepSeek Provider
- **REQ-239**: MUST implement provider `deepseek` that fetches `https://api.deepseek.com/user/balance` with `Authorization: Bearer <key>` and `Accept: application/json` headers.
- **REQ-240**: MUST resolve the DeepSeek API key from `DEEPSEEK_API_KEY` with environment then `~/.config/aibar/env` precedence and MUST prompt it in `setup`.
- **REQ-241**: MUST map `is_available` and `balance_infos[]` fields `currency`, `total_balance`, `granted_balance`, and `topped_up_balance` into `raw.deepseek_balance_infos` records and `UsageMetrics`.
- **REQ-242**: MUST set DeepSeek `metrics.remaining` to the preferred balance record `total_balance`, leave `limit` and `cost` unset, and resolve `currency_symbol` via `resolve_currency_symbol`.
- **REQ-243**: MUST treat `deepseek` as a single fixed-window provider with effective window `30d` that ignores the requested window and fetches all balances in one API call.
- **REQ-244**: MUST reuse the shared provider cache, idle-time, throttling, and retry lifecycle for `deepseek` without modifying those shared mechanisms.
- **REQ-245**: MUST render DeepSeek CLI text blocks as `Status: OK`, blank line, `Balance: <currency_symbol><remaining>`, blank line, and the freshness line.
- **REQ-246**: DeepSeek CLI text blocks and GNOME cards MUST NOT render progress bars, `Usage:` rows, `Requests`, or `Tokens` because the balance API exposes no usage counters.
- **REQ-251**: DeepSeek CLI text blocks MUST render `Topped up: <currency_symbol><topped_up_balance>` and `Granted: <currency_symbol><granted_balance>` after the `Balance` row when `raw.deepseek_balance_infos[0]` carries finite values.
- **REQ-252**: DeepSeek CLI text blocks and GNOME cards MUST render `Balance`, `Topped up`, and `Granted` from `raw.deepseek_balance_infos[0]` and MUST NOT render `Spent`, `Cost`, or usage rows because the endpoint exposes no spend field.
- **REQ-253**: GNOME DeepSeek cards MUST render `Balance`, `Topped up`, and `Granted` monetary rows from `raw.deepseek_balance_infos[0]` while the panel status token keeps only the balance.
- **REQ-247**: MUST map DeepSeek HTTP `401` to `AuthenticationError`, HTTP `429` to a rate-limit error result carrying `retry_after_seconds`, and other non-200 responses to provider error results.
- **REQ-248**: MUST render GNOME DeepSeek tab, card, and panel status labels last with rose style classes (`#FF375F`), card `Balance: <currency_symbol><value>`, and enable-state filtering.
- **REQ-249**: MUST exclude `deepseek` from GNOME progress-bar providers, API-counter providers, and panel percentage aggregation while listing it in provider ordering arrays.
- **REQ-250**: MUST document in DeepSeek `get_config_help` and `README.md` that the API key authorizes balance retrieval but exposes no aggregated per-key usage report.

## 4. Test Requirements

Automated unit-test coverage is maintained under `tests/`; tests MUST satisfy HDT principles: deterministic, isolated, and behavior-focused.

- **TST-001**: MUST verify `show` rejects unsupported window/provider values with non-zero exit and Click `BadParameter` diagnostics.
- **TST-002**: MUST verify credential precedence by asserting env vars override env-file values and provider stores for at least one provider.
- **TST-003**: MUST verify successful refresh writes `~/.cache/aibar/cache.json` with payload and last-attempt status sections used by `show --json`, and writes provider-keyed `last_success_at`/`idle_until` epoch and human-readable fields in `~/.cache/aibar/idle-time.json`.
- **TST-004**: MUST verify GNOME extension `FAIL` cards render `Status: FAIL`, blank line, `Reason: <reason>`, blank line, and `Updated/Next`, MUST not render usage/reset/quota/cost rows, MUST not render `Window 5h:/7d:/30d:` text, and MUST keep popup refresh/header behavior.
- **TST-005**: MUST verify Copilot provider always returns effective `window=30d` and computes `premium_requests_extra_cost = max(premium_requests - premium_requests_included, 0) * copilot_extra_premium_request_cost` in payload, CLI text, and `show --json`.
- **TST-006**: MUST verify `pi-usereq/docs/REFERENCES.md` covers configured-source symbols and preserves extracted Doxygen fields for documented declarations.
- **TST-007**: MUST verify GNOME panel status labels render exactly one provider-colored bold `Err` for OAuth/rate-limit failures, hide normal percentage/cost labels in that state, keep provider order styling, verify icon thresholds, preserve zero-cost currency rendering, and place Copilot cost between Copilot percentages and Codex labels.
- **TST-008**: MUST verify `pyproject.toml` declares `[build-system]` with `hatchling`, `[project.scripts]` entry `aibar = "aibar.cli:main"`, `requires-python >= 3.12`, `[project.urls]`, `classifiers`, runtime `dependencies`, and dev-group `pytest` per CTN-019.
- **TST-065**: MUST verify repository root tracks `.python-version` with content `3.12`.
- **TST-009**: MUST verify `gnome-install` resolves package source, validates source directory, branches install/update by target-directory presence, executes update disable→copy→enable ordering, masks extension-absence disable failures, and exits non-zero on missing source; MUST verify `gnome-uninstall` disables extension then removes directory and exits non-zero when directory is missing.
- **TST-010**: MUST verify `Remaining credits: <remaining> / <limit>` appears for Codex and Copilot only when corresponding status is `OK`, appears after one blank line following `Resets in`, and renders `<remaining>` as bold bright white.
- **TST-011**: MUST verify every provider refresh failure updates provider-scoped idle-time using `idle_until = last_attempt_at + max(idle_delay_seconds, retry_after_seconds_or_0)`, including HTTP `429` and authentication failures without `retry_after` metadata.
- **TST-013**: MUST verify `setup` prompts provider activation first, then `idle_delay_seconds`, `api_call_delay_milliseconds` (default `100`), `api_call_timeout_milliseconds` (default `5000`), `default_retry_after_seconds` (default `3600`), `gnome_refresh_interval_seconds`, `billing_data`, Copilot extra-premium cost (default `0.04`), currency prompts, and final logging prompts, and persists all values into `~/.config/aibar/config.json`.
- **TST-055**: MUST verify `setup` presents and persists `enabled_providers` as the first setup section, with provider order `agy`, `openrouter`, `copilot`, `codex`, `openai`, `geminiai`.
- **TST-056**: MUST verify disabled providers are omitted from `show` text and `show --json`, emit `enabled_providers`, and skip refresh plus idle-time updates for providers marked disabled.
- **TST-057**: MUST verify GNOME extension source parses `enabled_providers` before provider extraction and hides tabs, cards, and panel labels for disabled providers.
- **TST-014**: MUST verify `show` evaluates idle-time per provider, serves `~/.cache/aibar/cache.json` for providers with future `idle_until`, and refreshes only providers with missing or expired idle-time state.
- **TST-015**: MUST verify `show --force` removes `~/.cache/aibar/idle-time.json`, bypasses idle-time gating for current execution, refreshes providers, and recreates idle-time metadata before loading `~/.cache/aibar/cache.json`.
- **TST-016**: MUST verify refresh execution enforces configured inter-call delay in milliseconds between provider API requests, using `100` milliseconds when `api_call_delay_milliseconds` is absent.
- **TST-017**: MUST verify CLI `show` invokes one shared cache-retrieval implementation and does not call legacy `ResultCache` read/write APIs.
- **TST-018**: MUST verify failed provider/window refresh attempts set `result=FAIL` and `error` in `cache.json` while preserving the previous payload for the same provider/window.
- **TST-019**: MUST verify partial refresh outcomes can record mixed `OK` and `FAIL` statuses across providers in one refresh run without overwriting unaffected payload snapshots.
- **TST-020**: MUST verify refresh and fallback logic do not read or write legacy per-provider snapshot files.
- **TST-021**: Tests that mock `httpx.AsyncClient` transport and invoke provider `fetch` or `fetch_all_windows` execution path MUST restrict assertions to success/error state (`is_error`, `error` fields), result-dict window key presence, HTTP call count, and cache/filesystem side effects; MUST NOT assert specific numeric metric field values (`usage_percent`, `remaining`, `cost`) derived from the parsed HTTP response.
- **TST-023**: MUST verify `currency_symbol` in `UsageMetrics` flows through provider fetch and cache serialization to CLI text output (`_print_result`) and GNOME extension cost labels using the symbol from metrics, not a hardcoded `$`.
- **TST-024**: MUST verify `setup` accepts GeminiAI OAuth desktop-client credentials from both pasted JSON and file path input and persists normalized client-secret JSON in `~/.config/aibar/`.
- **TST-025**: MUST verify GeminiAI OAuth authorization requests `bigquery.readonly`, `monitoring.read`, and `cloud-platform` scopes and persists refresh-capable authorized-user credentials for provider fetch execution.
- **TST-026**: MUST verify GeminiAI fetch queries Cloud Monitoring usage metrics with service constraint `resource.labels.service="generativelanguage.googleapis.com"` and `UTC month-start -> now` interval semantics, supports `api`/`consumed_api` metric series, and queries BigQuery billing data using explicit selected columns with latest invoice-month aggregation fallback to current-month `usage_start_time`.
- **TST-027**: MUST verify GeminiAI HTTP `429`, quota-exhaustion, and missing billing-export-table failures preserve cached payload snapshots, mark status `FAIL`, and update only GeminiAI idle-time state according to rate-limit retry policy.
- **TST-028**: MUST verify `setup` currency prompts exclude `geminiai` and GeminiAI rendering in CLI text and JSON payload includes latest-available billing-period monetary cost values when billing data exists.
- **TST-029**: MUST verify GNOME extension renders GeminiAI provider tab/card with bright-purple style class assignment, provider title `GEMINIAI`, provider ordering as the last tab/card after `openai`, and GeminiAI cost/error status propagation from cache payload.
- **TST-030**: MUST verify CLI `show` renders panels ordered `agy`, `openrouter`, `copilot`, `codex`, `openai`, `geminiai`, keeps one shared panel width, never renders `Window 5h:/7d:/30d:` headings, and renders `Status` then right-aligned `Updated/Next` for both `OK` and `FAIL` states.
- **TST-058**: MUST verify CLI `show` renders Copilot `Cost: <currency_symbol><value>` after one blank line following `Remaining credits`.
- **TST-053**: MUST verify GNOME Copilot card renders `Cost: <currency_symbol><value>` and panel status bar renders Copilot `<currency_symbol><cost>` between Copilot percentages and Codex labels.
- **TST-031**: MUST verify startup update preflight executes before invalid-argument diagnostics and before subcommand handlers run.
- **TST-032**: MUST verify startup update idle-time gating skips HTTP calls until `idle_until` expires and resumes checks when the idle-state file is missing or expired, except for invocations containing `--version`.
- **TST-033**: MUST verify successful startup update checks create `~/.cache/aibar/` when missing and write `check_version_idle-time.json` with epoch and human-readable `last_success_at` and `idle_until`.
- **TST-034**: MUST verify repeated startup update HTTP `429` responses compute idle-time using `max(300, max(retry-after values))`.
- **TST-035**: MUST verify Linux `--upgrade` executes `uv tool install aibar --force` (PyPI), `--uninstall` executes `uv tool uninstall aibar`, exit codes propagate, and `--uninstall` deletes `~/.cache/aibar/`.
- **TST-041**: MUST verify non-Linux `--upgrade` and `--uninstall` skip lifecycle subprocess execution and print manual command guidance.
- **TST-046**: MUST verify GeminiAI CLI text renders `Billing services: <count> (<service1>, <service2>, ...)` using billing `service_description` values, preserving order, and printing all discovered services without truncation markers.
- **TST-047**: MUST verify `--enable-log`, `--disable-log`, `--enable-debug`, and `--disable-debug` persist `log_enabled` and `debug_enabled` in `~/.config/aibar/config.json` without cross-flag side effects.
- **TST-048**: MUST verify `log_enabled=true` appends timestamped entries in `~/.cache/aibar/aibar.log` for execution start, idle-time checks, idle-driven branches, error handling, cache.json load/save operations, and execution end plus one trailing empty line.
- **TST-049**: MUST verify API-call debug logging writes API metadata and debug response summaries only when `log_enabled=true` and `debug_enabled=true`, includes unmodified full JSON `raw` payload on failed calls, and omits debug rows otherwise.
- **TST-050**: MUST verify runtime logging records provider `FAIL` categories `oauth` and `rate_limit` when `log_enabled=true`, and logs `retry_after_seconds` for each category when that value exists.
- **TST-051**: MUST verify lock acquisition timeout after 5 seconds raises explicit lock-file error for cache/idle operations, and `show` exits non-zero with the same diagnostic while runtime log records timeout when `log_enabled=true`.
- **TST-052**: MUST verify GNOME cards render >100 progress bars only for `agy`, `openrouter`, `copilot`, `codex`, and `zai`, and render `openai`/`geminiai` usage as text without bars.
- **TST-054**: MUST verify CLI text `show` renders progress bars only for `agy`, `openrouter`, `copilot`, `codex`, and `zai`, and renders `openai`/`geminiai` usage rows without bars.
- **TST-059**: MUST verify CLI text `show` renders `openrouter` OK-state usage as `Usage: <window> <progress_bar> <percent>%` using the standard fixed-width CLI progress-bar format.
- **TST-060**: MUST verify Z.ai fetch maps the three `unit` quota entries to `5h`, `1w`, and `1m` quota rows and exposes each `percentage` and `nextResetTime`.
- **TST-061**: MUST verify Z.ai renders last with cyan color in CLI text and GNOME extension and that the GNOME panel status bar shows the `5h` (non-bold) and `1w` (bold) Z.ai quota percentages and that the `_handleError` GNOME extension function resets and hides every panel status label including `_panelOpenAICostLabel`.
- **TST-062**: MUST verify ZaiProvider derives the `5h` quota `reset_at_epoch_ms` from the next UTC 5-hour boundary when the 5 Hours limit entry omits `nextResetTime`.
- **TST-063**: MUST verify OpenRouter progress-bar percentage equals `cost / (cost + remaining) * 100` from API credit total `data.limit`, over-credit bars render >100 identically to Copilot, and `setup` prompts no budget.
- **TST-064**: MUST verify AGY provider parses `agy -p /usage` TSV rows into the five quota records with normalized used percentages, classifies authentication failures, and omits missing quota rows; dedicated standalone test pending (no existing test maps to this module).
- **TST-036**: MUST verify `--version` prints installed version plus labeled latest PyPI and GitHub release lines, bypasses subcommand execution, and forces one online startup release check even when `check_version_idle-time.json` contains future `idle_until`.
- **TST-038**: MUST verify CLI text `show` renders `FAIL` blocks as `Status: FAIL`, blank line, `Reason: <reason>`, blank line, and right-aligned `Updated/Next`, never renders `Window 5h:/7d:/30d:` headings, and preserves `show --json` freshness, API-counter, cost, and GeminiAI effective-window behaviors.
- **TST-042**: MUST verify CLI `show` and GNOME provider cards render equivalent failed-provider blocks formatted as `Status: FAIL`, blank line, `Reason: <reason>`, blank line, and `Updated/Next`, without `Window 5h:/7d:/30d:` headings.
- **TST-039**: MUST verify `scripts/aibar.sh` invokes `uv run python -m aibar.cli`, forwards CLI arguments, and contains no virtualenv creation/activation or `pip install -r requirements.txt` commands.
- **TST-040**: MUST verify `.gitignore` includes `uv.lock`, excludes `requirements.txt` from allowlist, `requirements.txt` is absent, and `README.md` section `## Requirements` contains the uv-tool requirement plus export command snippet.
- **TST-037**: MUST verify `pyproject.toml` wheel `packages` includes the `aibar` package with its `gnome-extension/` subtree, and sdist `include` covers `src/aibar/aibar/**`, `README.md`, `LICENSE`, `LICENSE_GnomeCodexBar`, and `pyproject.toml` without `scripts/**`.
- **TST-066**: MUST verify `aibar login` without `--provider` executes login flows exactly for login-capable providers whose cached status contains `result=FAIL` and skips providers with `OK` or absent cached status.
- **TST-067**: MUST verify `aibar login` without `--provider` exits 0 with an informational message when no login-capable provider is in error state and exits non-zero when a login flow fails.
- **TST-068**: MUST verify `.github/workflows/release-pypi.yml` exists, `release-uvx+extension.yml` is absent, and the workflow declares PyPI Trusted Publishing via `pypa/gh-action-pypi-publish` with `id-token: write`.
- **TST-069**: MUST verify `README.md` documents PyPI installation commands `uv tool install aibar` and `uvx aibar`.
- **TST-070**: MUST verify startup update checks query `https://pypi.org/pypi/aibar/json` and parse `info.version` as the latest version.
- **TST-071**: MUST verify `README.md` documents `sudo apt install pipx`, `pipx ensurepath`, and `pipx install aibar` as the primary installation flow before alternative methods.
- **TST-072**: MUST verify default `--upgrade` executes the PyPI lifecycle command and `--upgrade` with `--develop` or `--dev` executes the GitHub lifecycle command pinned to the resolved latest GitHub release tag.
- **TST-073**: MUST verify `.github/workflows/release-pypi.yml` gates `publish-pypi` on the `master` branch output and runs the `release-assets` job for version tags on `master` or `develop`.
- **TST-074**: MUST verify `scripts/aibar-nested-debug-session.sh` launches argv in background, traps SIGINT/SIGTERM, starts an interactive debug shell after the settle delay, prints extension inspection guidance, and that `scripts/test-gnome-extension.sh` routes all launch branches through the wrapper preserving `MUTTER_DEBUG_DUMMY_MODE_SPECS=1280x720` without screenshot capture logic.

- **TST-075**: MUST verify GNOME 50 metadata and extension UI construction, refresh, and teardown using GNOME 50 API contracts.
- **TST-076**: MUST verify windowed-session launch arguments, installation ordering, the `MUTTER_DEBUG_DUMMY_MODE_SPECS=1280x720` environment, shared debug-session bus, and non-zero prerequisite failures using isolated subprocess substitutes.
- **TST-077**: MUST verify `--ver` prints installed version plus labeled latest PyPI and GitHub release lines, bypasses subcommand execution, and forces one online startup release check bypassing the idle gate.
- **TST-078**: MUST verify `--upgrade` with `--develop`/`--dev` resolves the latest GitHub release `tag_name` and executes the pinned GitHub lifecycle command with exit-code propagation.
- **TST-079**: MUST verify `--upgrade` with `--develop`/`--dev` exits non-zero with a bright-red diagnostic and no lifecycle subprocess when the GitHub release tag is unresolved.
- **TST-080**: MUST verify every JavaScript-based action pin in `.github/workflows/release-pypi.yml` resolves to a Node24-native upstream major version.
- **TST-081**: MUST verify `.github/workflows/release-pypi.yml` contains no transitional Node20 opt-out variables `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION` and `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24`.
- **TST-082**: MUST verify GitHub release and upgrade URLs compose from the program-name constant and the `--develop` upgrade argv pins the fetched `tag_name`.
- **TST-083**: MUST verify the `--version` GitHub report performs one fresh releases/latest fetch per invocation and its reported version equals the tag pinned by the `--develop` upgrade argv.
- **TST-084**: MUST verify `scripts/pre-release-check.sh` exists, is executable, gates on a dirty git tree with `--allow-dirty` opt-out, runs `uv sync --locked` and `uv run pytest`, delegates building to `scripts/build.sh` with a temporary artifact destination, and verifies the sdist and wheel there.
- **TST-085**: MUST verify `scripts/pre-release-check.sh` registers an EXIT trap removing `build/`, `.pytest_cache/`, `__pycache__` trees under `src/` and `tests/`, and the temporary artifact directory, independent of pipeline outcome.
- **TST-103**: MUST verify `.github/workflows/release-pypi.yml` reuses `dist/` artifacts when present, generates them with `scripts/build.sh` otherwise, and uploads them as GitHub Release assets.
- **TST-104**: MUST verify `.github/workflows/release-pypi.yml` fails with non-zero status when a required `dist/` artifact is missing after artifact resolution.
- **TST-105**: MUST verify `.github/workflows/release-pypi.yml` contains no `scripts/pre-release-check.sh`, no `python -m build`, no `uv sync`, and no `uv run pytest` step.
- **TST-106**: MUST verify `.github/workflows/release-pypi.yml` declares a conditional `astral-sh/setup-uv` toolchain step and keeps no `unit-tests` job.
- **TST-107**: MUST verify `scripts/pre-release-check.sh` performs no read, deletion, cleanup, or verification operation on the repository `dist/` directory and delegates artifact generation to a temporary directory.
- **TST-087**: MUST verify Linux `--upgrade --force` executes the PyPI forced lifecycle argv `uv tool install aibar --force --reinstall --refresh` with exit-code propagation and non-Linux `--upgrade --force` prints manual guidance containing the forced command without subprocess execution.
- **TST-088**: MUST verify Linux `--upgrade` with `--develop`/`--dev` and `--force` executes the tag-pinned GitHub forced lifecycle argv `uv tool install --force --reinstall --refresh git+https://github.com/Ogekuri/<program-name>@<tag_name>` with exit-code propagation.
- **TST-089**: MUST verify `--version` output is exactly the three aligned stdout lines with equal label field width, aligned colons, package `__version__` installed value, and GitHub failure value `unknown (<reason>)` on fetch failure.
- **TST-090**: MUST verify exact shared-renderer output strings for one root child, two root siblings, nested first/middle/last siblings, non-last and last parameter details, and a branch with details plus real children.
- **TST-091**: MUST verify generated `--print` and `--info` trees satisfy marker uniqueness, sibling-order `└──` termination, detail-prefix parity, and absence of tree markers inside detail lines.
- **TST-092**: MUST verify every generated table has a constant border width, aligned separator columns, and the exact owner detail prefix on every physical line.
- **TST-093**: MUST verify `--get`, `--set`, `--unset`, `--print`, `--info`, and `--print-raw` success and failure behavior including exit codes, stream routing, JSON typing, defaults, map operations, and path rejection.
- **TST-094**: MUST verify atomic write failure preserves the previous `config.json` bytes and leaves no temporary file in the configuration directory.
- **TST-095**: MUST verify bootstrap writes `RuntimeConfig` defaults when `config.json` is missing and preserves an existing valid file untouched.
- **TST-096**: MUST verify every command example published by `--info` uses a complete canonical path, is shell-parsable, and succeeds when executed against a temporary configuration file.
- **TST-097**: MUST verify `.gitignore` contains `!dist/` and `!dist/**/*` inside the "Include specific files and directories" section and that `git check-ignore --no-index` reports `dist/` release artifacts as not ignored.
- **TST-099**: MUST verify `scripts/build.sh` is executable, resolves the repository root from its own path, accepts `--dist-dir <Path>` defaulting to `<repository-root>/dist`, validates `uv`/`zip`/`find`, removes every versioned sdist, wheel, and extension-zip destination entry, and preserves foreign entries.
- **TST-100**: MUST verify `scripts/build.sh` registers EXIT, SIGINT, and SIGTERM cleanup handlers that remove `build/`, `.pytest_cache/`, `*.egg-info`, and `__pycache__` artifacts, preserve the original exit status, and retain versioned `dist/` artifacts.
- **TST-101**: MUST verify `scripts/build.sh` checks for residual intermediate build artifacts after cleanup and exits non-zero when one remains outside `dist/`.
- **TST-102**: MUST verify `scripts/clean.sh` is absent from the repository and that no script under `scripts/` references it.
- **TST-108**: MUST verify DeepSeek provider normalizes `is_available` and `balance_infos[]` into `raw.deepseek_balance_infos` and `UsageMetrics.remaining` with effective window `30d` and null usage counters.
- **TST-109**: MUST verify CLI `show` renders DeepSeek `Balance`, `Topped up`, and `Granted` rows without progress bars, `Usage:` rows, `Requests`, or `Tokens`.
- **TST-110**: MUST verify `setup` prompts `DEEPSEEK_API_KEY` and persists `deepseek` in `enabled_providers` and `currency_symbols`.
- **TST-111**: MUST verify GNOME extension renders `deepseek` last with rose style classes, card monetary rows, panel balance token, and `_handleError` label reset.
- **TST-112**: MUST verify CLI and GNOME DeepSeek render `Balance`, `Topped up`, and `Granted` rows and never render `Spent`, `Cost`, or usage rows.
- **TST-113**: MUST verify DeepSeek rose palette classes use `#FF375F` in `stylesheet.css` and ANSI `\033[38;5;204m` in the CLI provider color map.
- **TST-114**: MUST verify `--upgrade` executes the `aibar gnome-install` argv resolved from `PATH` after a successful install, propagates its exit status, and skips it on install failure or non-Linux runtimes.

## 5. Evidence

| Requirement ID | Evidence (file + symbol + excerpt) |
|---|---|
| PRJ-001 | `src/aibar/aibar/cli.py` + `main/show/doctor/env/setup/login/gnome_install/gnome_uninstall` + `@main.command()` declarations for all subcommands. |
| PRJ-002 | `src/aibar/aibar/cli.py` + `get_providers` + returns Antigravity/OpenAI/OpenRouter/Copilot/Codex/GeminiAI/Z.ai/DeepSeek provider instances keyed by `ProviderName`. |
| PRJ-004 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/metadata.json` + `name = AIBar Monitor`, `url = https://github.com/Ogekuri/AIBar`, and `donations.github = Ogekuri`; `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + provider-card rendering path; `scripts/test-gnome-extension.sh` + `MUTTER_DEBUG_DUMMY_MODE_SPECS=1280x720`. |
| PRJ-005 | `pi-usereq/docs/REFERENCES.md` + machine-readable symbol sections for configured-source files. |
| PRJ-006 | `pyproject.toml` + `[build-system]`/`[project]`/`[project.scripts]` sections + `aibar = "aibar.cli:main"` console entry point used by `uv tool install`, `uv run`, and `uvx` execution without external virtualenv bootstrap; `requires-python = ">= 3.12"` floor per CTN-018. |
| PRJ-007 | `README.md` + dedicated `## Requirements` and `## Installation` sections stating the Python >= 3.12 floor + `uv tool`/`uv run`/`uvx` instructions and optional `uv export --format requirements-txt > requirements.txt` snippet. |
| PRJ-011 | `pi-usereq/docs/REQUIREMENTS.md`, `pi-usereq/docs/WORKFLOW.md`, and `pi-usereq/docs/REFERENCES.md` + GNOME contract documentation sources; repository tree excludes `src/aibar/plans/Gnome.plan.md`. |
| CTN-001 | `src/aibar/aibar/config.py` + `Config.get_token` + env var -> env file -> provider-specific stores (`CodexCredentialStore`, `CopilotCredentialStore`); provider `agy` resolves the local `agy` CLI from `PATH` via `AntigravityProvider.is_configured`. |
| CTN-002 | `src/aibar/aibar/providers/base.py` + `ProviderResult` model + fields `provider/window/metrics/updated_at/raw/error`; `UsageMetrics` + `currency_symbol` field. |
| CTN-003 | `src/aibar/aibar/providers/*.py` + `fetch` methods + `httpx.AsyncClient(timeout=api_call_timeout_milliseconds/1000.0)` in all providers using `RuntimeConfig.api_call_timeout_milliseconds`. |
| CTN-004 | `src/aibar/aibar/config.py` + `save_cli_cache` persisting `cache.json` as canonical store for payload snapshots and attempt statuses. |
| CTN-005 | `src/aibar/aibar/config.py` + `PROVIDER_INFO` notes + entries describing unofficial/internal usage for Copilot and Codex plus local-CLI usage for `agy`. |
| CTN-006 | `pi-usereq/docs/REFERENCES.md` + configured-source symbol index regenerated from repository source files. |
| CTN-007 | `pyproject.toml` + `[build-system] requires = ["hatchling"]` + `[project]` metadata fields `name`, `version`, `requires-python = ">= 3.12"`, runtime `dependencies`, and `[project.scripts]`; `pytest` relocated to `[dependency-groups]` dev per CTN-019. |
| CTN-008 | `src/aibar/aibar/config.py` + `RuntimeConfig` model + `idle_delay_seconds`, `api_call_delay_milliseconds`, `api_call_timeout_milliseconds`, `gnome_refresh_interval_seconds`, and `currency_symbols` fields persisted in `~/.config/aibar/config.json`. |
| CTN-009 | `src/aibar/aibar/config.py` + `build_idle_time_state/load_idle_time/save_idle_time` + provider-scoped idle-time epoch fields and local-timezone `*_human` serialization in `~/.cache/aibar/idle-time.json`. |
| CTN-010 | `src/aibar/aibar/cli.py` + `_refresh_and_persist_cache_payload` upserts payload only on successful provider/window fetch and preserves previous payload on failed attempts including HTTP `429`. |
| DES-001 | `src/aibar/aibar/providers/base.py` + `class BaseProvider(ABC)` + abstract methods `fetch`, `is_configured`, `get_config_help`. |
| DES-002 | `src/aibar/aibar/providers/base.py` + `WindowPeriod/ProviderName` + enum literals `5h/7d/30d/code_review` and provider names including `deepseek`. |
| DES-003 | `src/aibar/aibar/cli.py` + `parse_window/parse_provider` + raises `click.BadParameter` for invalid inputs. |
| DES-004 | `src/aibar/aibar/config.py` + `_sanitize_cache_payload` redacts keys in the sensitive set before `cache.json` writes. |
| DES-005 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_loadEnvFromFile` + parses `export KEY=VALUE`, handles quotes/comments/semicolon cleanup. |
| DES-006 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + scheduler-driven `_startAutoRefresh/_refreshData` using `this._refreshIntervalSeconds` read from `json.extension.gnome_refresh_interval_seconds`, popup `Refresh Now` command uses `aibar show --json --force`, interval updated on each successful refresh. |
| REQ-001 | `src/aibar/aibar/cli.py` + `show` loop + `if not prov.is_configured(): ... continue` and text hint `Set {config.ENV_VARS.get(name)}`. |
| REQ-002 | `src/aibar/aibar/cli.py` + `show/_build_dual_window_panel` + default-window Codex rendering emits one grouped panel with `5h`/`7d` sections, shared `Remaining credits` from `7d`, and Codex `Cost/Requests/Tokens` lines after `7d`. |
| REQ-003 | `src/aibar/aibar/cli.py` + `show` JSON renderer emits `indent=2` with `payload`, `status`, `idle_time`, `freshness`, and `extension` sections; `freshness` exports provider-keyed timestamps/local-time strings and `extension` exports `gnome_refresh_interval_seconds`, `idle_delay_seconds`, plus provider-keyed `window_labels`. |
| REQ-004 | `src/aibar/aibar/cli.py` + `doctor` + configuration status and `_fetch_result(provider, WindowPeriod.HOUR_5)` health check. |
| REQ-005 | `src/aibar/aibar/cli.py` + `setup` prompts `idle_delay_seconds`, `api_call_delay_milliseconds`, `api_call_timeout_milliseconds`, `default_retry_after_seconds`, `gnome_refresh_interval_seconds`, and `billing_data` with defaults `300`, `100`, `5000`, `3600`, `60`, and `billing_data`, then persists `~/.config/aibar/config.json`. |
| REQ-049 | `src/aibar/aibar/cli.py` + `setup` + per-provider currency symbol section after timeout section; prompts each provider with choices `$`/`£`/`€` default `$`; persists `currency_symbols` map in `~/.config/aibar/config.json`. |
| REQ-050 | `src/aibar/aibar/providers/*.py` + `_parse_response`/`_build_result` + `_resolve_currency_symbol` helper resolves currency from raw API response `currency` field; fallback to `RuntimeConfig.currency_symbols[provider_name]`. |
| REQ-051 | `src/aibar/aibar/cli.py` + `_print_result` + cost line uses `m.currency_symbol` instead of hardcoded `$`. |
| REQ-053 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_updateUI/_populateProviderCard` + panel summary cost uses `metrics.currency_symbol`; card cost label uses per-provider `metrics.currency_symbol`. |
| TST-013 | `tests/test_setup_runtime_config.py` + setup prompt-order/default assertions extended with currency symbol prompt section and `currency_symbols` persistence checks. |
| TST-023 | `tests/test_currency_symbol_flow.py` + `currency_symbol` field in `UsageMetrics`, provider fetch pass-through, CLI `_print_result`, and GNOME extension cost label use metrics symbol. |
| REQ-007 | `src/aibar/aibar/providers/copilot.py` + `CopilotDeviceFlow` and `CopilotProvider.login` + device-code request/poll and `save_token`. |
| REQ-009 | `src/aibar/aibar/cli.py` + shared retrieval entrypoint used by `show` + executes force check, per-provider idle-time check, per-provider conditional refresh, then `cache.json` load. |
| REQ-010 | `src/aibar/aibar/cli.py` + provider-window normalization in `show`/refresh pipeline pins OpenAI to `WindowPeriod.DAY_30`; `src/aibar/aibar/providers/openai_usage.py` + `fetch/_get_time_range` executes 30-day usage-cost retrieval. |
| REQ-011 | `src/aibar/aibar/cli.py` + provider-window normalization in `show`/refresh pipeline pins OpenRouter to `WindowPeriod.DAY_30`; `src/aibar/aibar/providers/openrouter.py` + `_get_usage/_parse_response` derives monthly cost from `usage_monthly` and credit total from `data.limit`. |
| REQ-154 | `src/aibar/aibar/cli.py` + `_build_result_panel`/`_build_cli_usage_line` + `usage_window_label = label or result.window.value` renders the `30d` effective-window label on OpenRouter OK usage rows; `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_populateProviderCard` + `configuredWindowLabel` renders `30d` on OpenRouter single-window bars; the key API exposes no explicit timeframe field (only `usage_daily`/`usage_weekly`/`usage_monthly`/`usage`), so the fixed `WindowPeriod.DAY_30` label matches the `usage_monthly` credit basis (REQ-011). |
| REQ-155 | `src/aibar/aibar/cli.py` + `_API_COUNTER_PROVIDERS`/`_provider_supports_api_counters`/`_build_result_panel` + OpenRouter excluded from null-to-zero counter normalization; `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `API_COUNTER_PROVIDERS`/`_providerSupportsApiCounters`/`_populateProviderCard` + OpenRouter cards hide `requests`/`tokens` labels when counters are null. |
| REQ-156 | `src/aibar/aibar/providers/openrouter.py` + `_parse_response` + `UsageMetrics.total_cost` normalized from `data.usage` all-time usage with `None` fallback. |
| REQ-157 | `src/aibar/aibar/cli.py` + `_build_result_panel` + `Total cost: <currency_symbol><total_cost>` row emitted after the OpenRouter `Cost` row; `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_populateProviderCard` + OpenRouter `Total cost: <currency_symbol><total_cost>` label rendered in the removed counters position. |
| REQ-012 | `src/aibar/aibar/providers/copilot.py` + `fetch` + sets `effective_window = WindowPeriod.DAY_30` and returns that window. |
| REQ-013 | `src/aibar/aibar/providers/codex.py` + `_parse_response` + `window_key = "primary_window" if 5h else "secondary_window"`. |
| REQ-014 | `src/aibar/aibar/providers/codex.py` + `CodexCredentials.needs_refresh` + threshold `age.days >= 8`; `CodexProvider.fetch` calls refresher. |
| REQ-015 | `src/aibar/aibar/providers/codex.py` + `fetch` + catches generic refresh exception and continues (`pass  # Continue with existing token`). |
| REQ-016 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_refreshData` and popup `Refresh Now` handler + loads env file and `launcher.setenv(key, value, true)` before command spawn, including `--force` manual refresh path. |
| REQ-017 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_buildPopupMenu/_parseOutput/_updateUI/_populateProviderCard` + popup removes `Open AIBar Report`, `copilot/openrouter` render single `30d` window bars with labels sourced from JSON `extension.window_labels` (fallback `30d`), `openai/geminiai` render `Usage: <window> <percent>%` text without progress bars, freshness uses `freshness` data with status+`extension.idle_delay_seconds` fallback, and cost/API-counter rows stay normalized. |
| REQ-018 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_handleError` + `this._panelLabel.set_text('Err')` and `message.substring(0, 40)`. |
| REQ-019 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_providerOrder` and `_updateUI` sorting enforce `agy/openrouter/copilot/codex/openai/geminiai/zai/deepseek`; unknown providers rank `999` then lexical order. |
| REQ-020 | `pi-usereq/docs/REFERENCES.md` + per-symbol entries containing symbol identifier, file path, line-range spans, and parsed `@brief/@param/@return/@throws` fields. |
| REQ-021 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_buildPanelButton/_updateUI` + panel labels preserve fixed order for normal state and collapse to one provider-colored bold `Err` token for OAuth/rate-limit failure states. |
| REQ-022 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_buildPanelButton/_updateUI` + panel labels use provider classes/colors; cost labels render provider currency for numeric `0` values and hide only when cost metric is unavailable. |
| REQ-023 | `pyproject.toml` + `[project.scripts]` + `aibar = "aibar.cli:main"` declaration. |
| REQ-024 | `src/aibar/aibar/__main__.py` + `main()` import and invocation from `aibar.cli`. |
| REQ-034 | `src/aibar/aibar/cli.py` + `_format_reset_duration/_print_result` + day-token reset countdown formatting in text output. |
| REQ-035 | `src/aibar/aibar/cli.py` + `_build_result_panel/_print_result` + remaining-credits line gated to `result.is_error == False` and `remaining/limit` presence. |
| REQ-036 | `src/aibar/aibar/cli.py` + `_build_result_panel` failed-state branch returns after error diagnostics and suppresses usage/reset/quota/cost statistics lines; `openai/codex/geminiai` `Requests`/`Tokens` lines render with null→`0` normalization on `OK` states, while OpenRouter `OK` blocks omit `Requests`/`Tokens` rows and render the `Total cost:` row from `metrics.total_cost`. |
| REQ-037 | `src/aibar/aibar/cli.py` + error-rendering lines include unified `HTTP status: <code>, Retry after: <seconds> sec.` string; `src/aibar/aibar/gnome-extension/.../extension.js` + provider-card error block includes equivalent retry metadata text. |
| REQ-038 | `src/aibar/aibar/cli.py` + successful refresh path computes per-provider `idle_until = last_success_at + idle_delay_seconds` and writes provider-keyed epoch/human-readable values to `~/.cache/aibar/idle-time.json`. |
| REQ-039 | `src/aibar/aibar/cli.py` + shared force-refresh handling removes `~/.cache/aibar/idle-time.json`, bypasses idle-time gate, and refreshes before loading `cache.json`. |
| REQ-040 | `src/aibar/aibar/cli.py` + refresh scheduler enforces configured `api_call_delay_seconds` between consecutive provider API requests. |
| REQ-041 | `src/aibar/aibar/cli.py` + refresh-failure handling computes provider-scoped `idle_until = last_attempt_at + max(idle_delay_seconds, resolved_retry_after_seconds)` where `resolved_retry_after_seconds` is parsed from API metadata or falls back to `default_retry_after_seconds` when `retry_after_unavailable=true`, then persists provider state in `~/.cache/aibar/idle-time.json`. |
| REQ-042 | `src/aibar/aibar/cli.py` + retrieval pipeline uses only `cache.json` and `idle-time.json` persisted artifacts for idle-time-gated API minimization. |
| REQ-043 | `src/aibar/aibar/cli.py` + shared cache refresh/load helpers provide one retrieval implementation for CLI retrieval and render flows. |
| REQ-044 | `src/aibar/aibar/cli.py` + `_serialize_attempt_status`/`_record_attempt_status` persist per-provider/window `result` (`OK`/`FAIL`), `error`, and `updated_at` fields. |
| REQ-045 | `src/aibar/aibar/cli.py` + `_refresh_and_persist_cache_payload` upsert path writes payload only on successful fetch outcomes. |
| REQ-046 | `src/aibar/aibar/cli.py` + `_refresh_and_persist_cache_payload` failed upsert path preserves existing payload while updating failure status metadata. |
| REQ-047 | `src/aibar/aibar/cli.py` + `src/aibar/aibar/config.py` + fallback and refresh flows use only `cache.json` and no legacy per-provider snapshot files. |
| TST-001 | `src/aibar/aibar/cli.py` + `parse_window/parse_provider` provide validation points for invalid input diagnostics. |
| TST-002 | `src/aibar/aibar/config.py` + `get_token` implements explicit precedence chain requiring regression coverage. |
| TST-003 | `tests/test_cli_idle_cache.py` and `tests/test_cli_idle_force.py` + assertions for cache schema parity with `show --json` and provider-keyed idle-time epoch/human-readable field persistence under `~/.cache/aibar/`. |
| TST-004 | `tests/test_extension_quota_label.py` + popup-header/remove-action assertions, failed-state metric-row suppression, `extension.window_labels`-driven 30d usage rendering assertions for `copilot/openrouter` bars plus `openai/geminiai` text-only usage, freshness fallback assertions via `extension.idle_delay_seconds`, bottom-right `Updated/Next` assertions, bold-bright-white `Costs:` numeric/no-spacer assertions, API-counter format assertions for `openai/codex/geminiai`, and OpenRouter card `Total cost:` label + hidden `requests`/`tokens` labels on null counters. |
| TST-005 | `src/aibar/aibar/providers/copilot.py` + `fetch` hard-codes `effective_window` to `WindowPeriod.DAY_30`. |
| TST-006 | `pi-usereq/docs/REFERENCES.md` + generated configured-source symbol coverage validates documentation inventory completeness. |
| TST-007 | `tests/test_extension_quota_label.py` + single `Err` projection assertions for OAuth/rate-limit failures, provider-color bold-style assertions, normal-state order/style assertions, and zero-cost/missing-metric behavior checks. |
| TST-008 | `tests/test_pyproject_metadata.py` + assertions for `[build-system]` backend, `[project.scripts]` entry, `requires-python`, `[project.urls]`, `classifiers`, runtime `dependencies` excluding `pytest`, and `[dependency-groups]` dev `pytest` in `pyproject.toml`. |
| TST-010 | `src/aibar/aibar/cli.py` + `_build_result_panel` remaining-credits rendering path appears only for successful Codex/Copilot states. |
| TST-011 | `tests/test_cli_idle_time_429.py` + provider failure scenarios verify provider-scoped `idle_until = last_attempt_at + max(idle_delay_seconds, retry_after_seconds_or_0)` updates across HTTP `429` and auth failures without retry-after metadata. |
| TST-013 | `tests/test_setup_runtime_config.py` + setup prompt-order/default assertions and `~/.config/aibar/config.json` persistence checks for idle delay, API delay, and gnome_refresh_interval_seconds. |
| TST-014 | `tests/test_cli_idle_cache.py` + provider-scoped idle-time future/missing/expired branches verify per-provider cache-serving behavior and refresh gating in `show`. |
| TST-015 | `tests/test_cli_idle_force.py` + force-refresh path verifies idle-time deletion, gate bypass, refresh invocation, and idle-time regeneration before cache load. |
| TST-017 | `tests/test_cli_cache_status_retention.py` and `src/aibar/aibar/cli.py` + verify shared retrieval usage and absence of `ResultCache` read/write calls in CLI `show` path. |
| TST-018 | `tests/test_cli_cache_status_retention.py` + failed-refresh assertions verify `result=FAIL` with error metadata while preserving existing provider/window payload snapshots. |
| TST-019 | `tests/test_cli_cache_status_retention.py` + mixed-window assertions verify partial provider updates preserve unaffected windows and record per-window status granularity. |
| TST-020 | `tests/test_cli_cache_status_retention.py` + file-system assertions verify no read/write path targets legacy per-provider snapshot files. |
| TST-016 | `tests/test_cli_provider_throttle.py` + refresh timing assertions verify configured inter-call delay and default `20`-second fallback. |
| PRJ-008 | `src/aibar/aibar/cli.py` + `gnome_install` command + install/update mode detection using target-directory presence, file copy from package source, update-path disable before copy, and post-copy enable. |
| REQ-025 | `src/aibar/aibar/cli.py` + `_resolve_extension_source_dir` + `Path(__file__).resolve().parent / "gnome-extension" / _EXT_UUID` module-relative path resolution for extension source directory. |
| REQ-083 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/` subtree inside `aibar` package + `pyproject.toml` wheel `packages = ["src/aibar/aibar"]` auto-includes gnome-extension in wheel build. |
| REQ-026 | `src/aibar/aibar/cli.py` + `gnome_install` + `os.makedirs` for target directory creation. |
| REQ-027 | `src/aibar/aibar/cli.py` + `gnome_install` + validates non-empty source directory and `metadata.json` presence. |
| REQ-028 | `src/aibar/aibar/cli.py` + `gnome_install/gnome_uninstall` + `click.style` colored output for status, success, error, and informational messages. |
| REQ-029 | `src/aibar/aibar/cli.py` + `gnome_install` + `shutil.copy2` copies files from package source to target directory replacing existing files. |
| REQ-030 | `src/aibar/aibar/cli.py` + `gnome_install` + `sys.exit(1)` on prerequisite failure with descriptive error message. |
| REQ-031 | `scripts/test-gnome-extension.sh` + invokes `scripts/aibar.sh gnome-install` before nested-shell launch. |
| REQ-032 | `src/aibar/aibar/cli.py` + `gnome_install` + install/update branch execution with install copy→enable and update disable→copy→enable ordering plus colored status output. |
| REQ-099 | `src/aibar/aibar/cli.py` + `gnome_install` update path + non-zero disable outcomes from missing extension treated as masked warnings and flow continues to copy/enable. |
| REQ-033 | `scripts/test-gnome-extension.sh` + no subcommand parameter; executes install-and-launch flow on invocation without arguments. |
| REQ-080 | `src/aibar/aibar/cli.py` + `gnome_uninstall` + `subprocess.run(["gnome-extensions", "disable", "aibar@aibar.panel"])` before removal with colored status output. |
| REQ-081 | `src/aibar/aibar/cli.py` + `gnome_uninstall` + `shutil.rmtree` removes extension directory and all contents. |
| REQ-082 | `src/aibar/aibar/cli.py` + `gnome_uninstall` + `sys.exit(1)` when extension directory does not exist with descriptive error message. |
| TST-009 | `tests/test_gnome_install_uninstall.py` + `gnome-install` install/update branch, update disable→copy→enable ordering, and masked-missing-extension disable assertions; `gnome-uninstall` disable-before-remove and missing-directory exit assertions. |
| TST-021 | `tests/test_cli_idle_time_429.py` + mocked provider fetch assertions restricted to success/error state (`is_error`, `error` fields), window key presence, call counts, and cache/filesystem side effects; no numeric metric values asserted from parsed HTTP responses. |
| TST-023 | `tests/test_currency_symbol_flow.py` + assertions for `currency_symbol` field in `UsageMetrics`, CLI `_print_result` cost formatting, and GNOME extension panel label using metrics symbol. |
| TST-030 | `tests/test_cli_show_panel_alignment.py` + CLI output assertions verify provider order, shared panel width, `Window 5h:/7d:/30d:` heading suppression, and `Status` first/right-aligned `Updated/Next` last layout. |
| TST-058 | `tests/test_cli_show_panel_alignment.py` + Copilot panel assertions verify one blank line separates `Remaining credits` from `Cost`. |
| REQ-067 | `src/aibar/aibar/cli.py` + `show/_provider_panel_sort_key/_build_result_panel/_build_dual_window_panel/_emit_provider_panel` + provider ordering, status-first layout, ANSI colors, and shared-width rendering. |
| REQ-121 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `PROGRESS_BAR_PROVIDERS/_populateProviderCard/_applyBarWidths/_applyProgressFillGeometry` + progress-bar geometry stays active only for `agy/openrouter/copilot/codex/zai`, preserving >100 marker and over-limit segment; AGY per-quota bars reuse the same geometry helpers. |
| REQ-130 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `TEXT_USAGE_PROVIDERS/_populateProviderCard` + `openai/geminiai` cards render `Usage: <window> <percent>%` text, hide bar actors, and keep non-usage rows visible. |
| REQ-122 | `src/aibar/aibar/cli.py` + `_should_render_cli_progress_bar/_build_cli_usage_line/_build_result_panel/_progress_bar` + >100 progress-bar rendering is limited to `agy/openrouter/copilot/codex/zai` while preserving marker and over-limit segment. |
| REQ-128 | `src/aibar/aibar/cli.py` + `_should_render_cli_progress_bar/_build_cli_usage_line/_build_result_panel/_build_agy_quota_lines` + usage rows render `Usage: <window> <progress_bar> <percent>%` for `agy/copilot/codex/zai`. |
| REQ-132 | `src/aibar/aibar/cli.py` + `_should_render_cli_progress_bar/_build_cli_usage_line/_build_result_panel` + `openrouter` usage rows render the standard fixed-width CLI progress-bar format. |
| REQ-131 | `src/aibar/aibar/cli.py` + `_should_render_cli_progress_bar/_build_cli_usage_line/_build_result_panel` + `openai/geminiai` usage rows render `Usage: <window> <percent>%` without progress bars. |
| REQ-133 | `src/aibar/aibar/cli.py` + `_ordered_rendered_panels/_provider_panel_sort_key` and `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_orderedEnabledProviderNames/_updateUI` + all visible provider surfaces keep canonical order including trailing `deepseek` after disabled-provider filtering. |
| REQ-129 | `src/aibar/aibar/cli.py` + `_build_result_panel` + Copilot cost line stays one blank line after `Remaining credits`, and `_build_dual_window_panel` strips `Window <window>` headings from CLI panels. |
| REQ-084 | `src/aibar/aibar/cli.py` + `_build_result_panel/_emit_provider_panel/show` + per-provider freshness line renders `Updated: <datetime>, Next: <datetime>` from provider `idle_time` timestamps with local-timezone `%Y-%m-%d %H:%M` and right-aligned panel layout; `show --json` exports equivalent provider freshness under top-level `freshness` for extension alignment. |
| REQ-085 | `src/aibar/aibar/cli.py` + text renderer surfaces cached authentication/rate-limit failures and suppresses statistics lines for `FAIL` states. |
| REQ-090 | `src/aibar/aibar/cli.py` + `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + both renderers consume identical cached error/status/retry-after payload semantics for failed provider/window states. |
| REQ-060 | `src/aibar/aibar/cli.py` + `show` provider/window resolution and payload rendering expose GeminiAI monitoring/billing/status fields in text and JSON surfaces. |
| REQ-097 | `src/aibar/aibar/cli.py` + `show` GeminiAI provider selection path forces effective `30d` window independent from requested window argument. |
| REQ-098 | `src/aibar/aibar/providers/geminiai.py` + monitoring interval construction uses current UTC month start as interval start and current UTC time as interval end. |
| TST-038 | `tests/test_cli_show_status_messages.py` + verifies CLI `show` right-aligned freshness line uses provider `idle_time` timestamps with local-timezone `%Y-%m-%d %H:%M` parity, `show --json` top-level `freshness` parity, fail-state statistics suppression, retry-after rendering format, `Window <window>:` heading suppression, API-counter null→`0` rendering for `openai/codex/geminiai`, OpenRouter suppressed-counter/`Total cost:` rendering, and GeminiAI effective window `30d` under non-30d requests. |
| TST-042 | `tests/test_cli_show_status_messages.py` + `tests/test_extension_quota_label.py` + cross-surface assertions for equivalent error category, HTTP status, retry-after value, and `Updated/Next` text sourced from the same `idle_time` timestamps on failed states. |
| TST-052 | `tests/test_extension_quota_label.py` + source assertions verify progress-bar geometry remains only for `agy/openrouter/copilot/codex/zai`, while `openai/geminiai` render text-only usage without bar widgets. |
| TST-054 | `tests/test_cli_show_panel_alignment.py` + output assertions verify bar providers keep `Usage: <window> <progress_bar> <percent>%`, while `openai/geminiai` render `Usage: <window> <percent>%` and preserve shared panel width. |
| TST-059 | `tests/test_cli_show_status_messages.py` + `_build_result_panel` assertions verify `openrouter` renders `Usage: <window> <progress_bar> <percent>%` with the standard fixed-width CLI bar glyphs. |
| REQ-086 | `scripts/aibar.sh` + launcher executes `uv run python -m aibar.cli "$@"` and removes repository virtualenv bootstrap/install commands; `uv run` resolves the interpreter from the `.python-version` pin (CTN-018). |
| REQ-087 | `.gitignore` + allowlist tracks `uv.lock` and drops `requirements.txt`; repository root no longer includes `requirements.txt`; `README.md` includes optional `uv export --format requirements-txt > requirements.txt` command; `uv.lock` regenerated with `requires-python = ">=3.12"`. |
| TST-039 | `tests/test_launcher_uv_only.py` + source-level assertions for `scripts/aibar.sh` uv-run invocation and absence of virtualenv/pip install logic. |
| TST-040 | `tests/test_uv_requirements_surface.py` + assertions for `.gitignore` allowlist change, `requirements.txt` absence, and README uv requirements/export command content. |
| REQ-091 | `src/aibar/aibar/cli.py` + `retrieve_results_via_cache_pipeline` + sequential execution: idle-time check, modular API calls, in-memory collection, locked cache write, locked cache read, presentation. |
| REQ-092 | `src/aibar/aibar/config.py` + `save_cli_cache` is the single write path for `cache.json`. |
| REQ-093 | `src/aibar/aibar/config.py` + `_blocking_file_lock(CACHE_FILE_PATH)` guards every `cache.json` read and write with 250ms polling and 5-second timeout failure semantics. |
| REQ-094 | `src/aibar/aibar/cli.py` + `retrieve_results_via_cache_pipeline` + at most one `load_cli_cache` per execution path. |
| REQ-095 | `src/aibar/aibar/config.py` + `RuntimeConfig.api_call_timeout_milliseconds` default `5000`; providers use `httpx.AsyncClient(timeout=api_call_timeout_milliseconds/1000.0)`. |
| REQ-096 | `src/aibar/aibar/config.py` + `DEFAULT_API_CALL_DELAY_MILLISECONDS = 100`. |
| TST-051 | `tests/test_cache_locking_and_io_minimization.py` + timeout assertions for lock acquisition failure diagnostics, runtime-log timeout row emission, and CLI `show` non-zero exit with explicit lock-timeout message. |
| REQ-071 | `src/aibar/aibar/cli.py` + `StartupPreflightGroup.main` + `_startup_force_ignore_idle_from_args` + `_STARTUP_FORCE_IGNORE_IDLE_UNTIL_ACTIVE` + `_run_startup_update_preflight()` bypasses idle-state gate for `--version`/`--ver`, while keeping idle gating for other invocations. |
| REQ-078 | `src/aibar/aibar/cli.py` + `_handle_version_option`/`_emit_version_option_release_report` prints installed version then labeled PyPI/GitHub latest-release lines and exits; `StartupPreflightGroup.main` forces one online startup release check for `--version`/`--ver` even with future `check_version_idle-time.json` `idle_until`. |
| TST-032 | `tests/test_cli_startup_update_preflight.py` + idle-gating test for normal invocations plus `test_version_flags_force_startup_online_check_bypassing_idle_gate` asserting `--version`/`--ver` ignore startup idle-time gate. |
| TST-036 | `tests/test_cli_startup_update_preflight.py` + version-idle-bypass test verifies forced online startup check and dispatch bypass; exact-output assertions in `test_version_prints_installed_version_without_dispatch` and `test_ver_alias_prints_installed_version_without_dispatch` are realigned to the aligned three-line report format (REQ-199). |
| REQ-134 | `src/aibar/aibar/providers/zai.py` + `ZaiProvider.fetch` + `QUOTA_URL = "https://api.z.ai/api/monitor/usage/quota/limit"` with `Authorization: Bearer <key>` and `Accept: application/json` headers. |
| REQ-135 | `src/aibar/aibar/config.py` + `Config.ENV_VARS[ProviderName.ZAI] = "ZAI_API_KEY"` and `src/aibar/aibar/cli.py` + `setup` Z.ai API key prompt writing `ZAI_API_KEY` to `~/.config/aibar/env`. |
| REQ-136 | `src/aibar/aibar/providers/zai.py` + `_parse_response`/`_extract_quotas` mapping `unit` 3/6/5 to 5 Hours, Weekly, and Monthly Web Search quotas. |
| REQ-137 | `src/aibar/aibar/providers/zai.py` + per-quota `percentage`/`reset_at_epoch_ms`; `src/aibar/aibar/cli.py` + `_build_zai_quota_lines`/`_coerce_zai_quota_reset_at`; `src/aibar/aibar/gnome-extension/.../extension.js` + Z.ai per-quota usage-bar/reset rendering. |
| REQ-138 | `src/aibar/aibar/cli.py` + `_SHOW_PROVIDER_ORDER` trailing `zai`; `src/aibar/aibar/gnome-extension/.../extension.js` + `_providerOrder`/`providerErrPriority` trailing `zai`. |
| REQ-139 | `src/aibar/aibar/gnome-extension/.../extension.js` + `_updateIconColor` Z.ai icon threshold input from max quota percentage. |
| REQ-140 | `src/aibar/aibar/cli.py` + `_build_zai_quota_lines` Z.ai progress-bar rows; `src/aibar/aibar/gnome-extension/.../extension.js` + `PROGRESS_BAR_PROVIDERS` includes `zai`. |
| REQ-141 | `src/aibar/aibar/cli.py` + `_FIXED_WINDOW_BY_PROVIDER[ProviderName.ZAI] = WindowPeriod.DAY_30`; `src/aibar/aibar/providers/zai.py` single-call fetch. |
| REQ-142 | `src/aibar/aibar/providers/zai.py` returns `ProviderResult` consumed by unmodified `retrieve_results_via_cache_pipeline`, `_record_attempt_status`, and idle-time lifecycle helpers. |
| REQ-143 | `src/aibar/aibar/gnome-extension/.../extension.js` + `_buildPanelButton`/`_updateUI` Z.ai 5 Hours (non-bold) and Weekly (bold) panel status-bar percentage labels. |
| TST-060 | `src/aibar/aibar/providers/zai.py` + `_extract_quotas`/`_build_quota` map `unit` 3/6/5 to 5 Hours, Weekly, and Monthly Web Search quotas with per-quota `percentage`/`reset_at`; dedicated standalone test pending (no existing test maps to this module). |
| TST-061 | `tests/test_geminiai_surface_integration.py` + `tests/test_extension_quota_label.py` + Z.ai last-position, cyan `aibar-tab-label-zai`/`aibar-progress-provider-zai`, `PROGRESS_BAR_PROVIDERS` includes `zai`, and `src/aibar/aibar/cli.py` + `_SHOW_PROVIDER_ORDER`/`_PROVIDER_PANEL_COLOR_CODES` trailing `zai`; `src/aibar/aibar/gnome-extension/.../extension.js` + `_buildPanelButton`/`_updateUI` Z.ai 5 Hours (non-bold) and Weekly (bold) panel status-bar labels. |
| REQ-158 | `src/aibar/aibar/providers/agy.py` + `AntigravityProvider.fetch` + executes `["agy", "-p", "/usage"]` subprocess, strips ANSI escapes via `_ANSI_ESCAPE_PATTERN`, parses TSV rows via `_parse_tsv_rows`. |
| REQ-159 | `src/aibar/aibar/providers/agy.py` + `AntigravityProvider._QUOTA_SPECS` + `Gemini Models`/`Weekly Limit Remaining` -> `G 7d` and `Gemini Models`/`Five Hour Limit Remaining` -> `G 5h`. |
| REQ-160 | `src/aibar/aibar/providers/agy.py` + `AntigravityProvider._QUOTA_SPECS` + `Claude and GPT models`/`Weekly Limit Remaining` -> `CG 7d` and `Claude and GPT models`/`Five Hour Limit Remaining` -> `CG 5h`. |
| REQ-161 | `src/aibar/aibar/providers/agy.py` + `AntigravityProvider._QUOTA_SPECS` + `Gemini 4 Argon`/`Gemini 4 Argon Weekly Limit` -> `A 7d`. |
| REQ-162 | `src/aibar/aibar/providers/agy.py` + `AntigravityProvider._find_remaining_percent` + first `_PERCENTAGE_PATTERN` match in TSV value column; `_extract_quotas` omits missing rows. |
| REQ-163 | `src/aibar/aibar/providers/agy.py` + `AntigravityProvider._extract_quotas` + used percentage `100.0 - remaining` clamped to `[0.0, 100.0]` stored as `percentage`. |
| REQ-164 | `src/aibar/aibar/providers/agy.py` + `AntigravityProvider._parse_response` + `raw.agy_quotas` records with `quota_key`/`label`/`remaining_percent`/`percentage`. |
| REQ-165 | `src/aibar/aibar/cli.py` + `_FIXED_WINDOW_BY_PROVIDER[ProviderName.AGY] = WindowPeriod.DAY_30`; `src/aibar/aibar/providers/agy.py` single-subprocess fetch consumed by unmodified cache/idle pipeline. |
| REQ-166 | `src/aibar/aibar/providers/agy.py` + `AntigravityProvider._AUTH_ERROR_PATTERN` classification and non-zero-exit/no-quota error results. |
| REQ-167 | `src/aibar/aibar/providers/agy.py` + `AntigravityProvider.is_configured` via `shutil.which("agy")`; `src/aibar/aibar/cli.py` + `show` not-configured hint renders CLI-missing text for providers without env vars. |
| REQ-168 | `src/aibar/aibar/cli.py` + `_build_agy_quota_lines`/`_build_result_panel` AGY branch; `src/aibar/aibar/gnome-extension/.../extension.js` + `_populateProviderCard` AGY per-quota bars with labels `G 7d`/`G 5h`/`CG 7d`/`CG 5h`/`A 7d`. |
| REQ-169 | `src/aibar/aibar/cli.py` + `_SHOW_PROVIDER_ORDER` leading `agy` and `_PROVIDER_PANEL_COLOR_CODES[ProviderName.AGY] = "\033[91m"`; `src/aibar/aibar/gnome-extension/.../extension.js` + `_providerOrder` leading `'agy'`; `stylesheet.css` + `aibar-tab-label-agy`/`aibar-progress-provider-agy` using `#FF3B30`. |
| REQ-170 | `src/aibar/aibar/gnome-extension/.../extension.js` + `_buildPanelButton` AGY 5h/7d panel labels and `_updateUI` `panelValues.agy5h`/`agy7d`/`agyMax` including `agyMax` in `panelPercents`. |
| REQ-171 | `src/aibar/aibar/cli.py` + `setup` currency prompt list excludes `ProviderName.AGY`; AGY panels/cards render no cost rows. |
| TST-064 | `src/aibar/aibar/providers/agy.py` + `_parse_tsv_rows`/`_extract_quotas`/`_find_remaining_percent` map TSV rows to five quota records with normalized used percentages and auth-error classification; dedicated standalone test pending (no existing test maps to this module). |
| CTN-018 | `pyproject.toml` + `requires-python = ">= 3.12"`; `.python-version` + `3.12` interpreter pin; `uv.lock` + `requires-python = ">=3.12"`. |
| CTN-019 | `pyproject.toml` + `[dependency-groups] dev = ["pytest"]` with runtime `[project] dependencies` excluding test-only packages; `uv.lock` regenerated for the dependency-group split. |
| TST-065 | `.python-version` + content `3.12`; verified by `tests/test_release_pypi_workflow.py`. |
| PRJ-050 | `.github/workflows/release-pypi.yml` + `release-assets` job + `Resolve release artifacts` step writing the `present` output from `compgen -G` probes, so committed `dist/` artifacts are reused when complete and generated with `scripts/build.sh` otherwise. |
| PRJ-051 | `.github/workflows/release-pypi.yml` + `Verify resolved release artifacts` step + shell `compgen -G` presence probe over `dist/*.tar.gz`, `dist/*.whl`, and the GNOME extension zip, exiting non-zero when a resolved artifact is missing. |
| PRJ-052 | `.github/workflows/release-pypi.yml` + `release-assets` job declares no pytest suite and no `scripts/pre-release-check.sh` step, and runs the single conditional `Generate release artifacts` step invoking `bash scripts/build.sh` only when `dist/` artifacts are incomplete. |
| PRJ-053 | `.github/workflows/release-pypi.yml` + `Resolve release artifacts` step tolerates an empty `dist/` in the tagged commit, so commit-tracked release artifacts are never a release precondition; `tests/test_release_workflow_release_artifacts.py` asserts the fallback build path. |
| TST-103 | `tests/test_release_workflow_release_artifacts.py` + assertions that the release job probes `dist/` artifacts, falls back to `scripts/build.sh`, and uploads `dist/**/*` as GitHub Release assets. |
| TST-104 | `tests/test_release_workflow_release_artifacts.py` + assertions for the post-resolution artifact presence gate and its non-zero failure path. |
| TST-105 | `tests/test_release_workflow_release_artifacts.py` + absence assertions for `scripts/pre-release-check.sh`, `python -m build`, `uv sync`, `uv run pytest`, and extension `zip` packaging. |
| TST-106 | `tests/test_release_workflow_release_artifacts.py` + assertions for the conditional `astral-sh/setup-uv` toolchain step and the absent `unit-tests` job. |
| REQ-172 | `src/aibar/aibar/cli.py` + `login`/`_login_error_state_providers`/`_select_login_error_providers` + bare-login branch selects login-capable providers with cached `result=FAIL` status via locked `load_cli_cache` read. |
| REQ-173 | `src/aibar/aibar/cli.py` + `_select_login_error_providers` + provider selection requires at least one cached window status entry with `result=FAIL`. |
| REQ-174 | `src/aibar/aibar/cli.py` + `_login_error_state_providers` + empty-selection branch prints informational message and returns with exit status 0. |
| REQ-175 | `src/aibar/aibar/cli.py` + `_login_error_state_providers` + per-flow `SystemExit`/exception capture records failed flows and exits non-zero when any flow fails. |
| TST-066 | `tests/test_login_error_state.py` + bare-login targeting assertions for cached `FAIL`-only execution and `OK`/absent/non-login-capable skip. |
| TST-067 | `tests/test_login_error_state.py` + zero-exit informational message and non-zero flow-failure exit assertions. |
| PRJ-012 | `.github/workflows/release-pypi.yml` + `release-assets` job (checkout of the tagged commit, artifact resolution reusing committed `dist/` artifacts or generating them, provenance attestation, changelog, GitHub Release asset publication from `dist/**/*`) for version tags on `master` or `develop` via `check-branch` outputs `is_master`/`is_release_branch`. |
| PRJ-013 | `.github/workflows/release-pypi.yml` + `publish-pypi` job gated by `if: needs.release-assets.outputs.is_master == 'true'` uploading the resolved `dist/*.tar.gz`/`dist/*.whl` via `pypa/gh-action-pypi-publish@release/v1` Trusted Publishing under top-level `id-token: write` permission. |
| PRJ-014 | `pyproject.toml` + `[project.urls]` (Homepage/Repository/Issues/Changelog) and `classifiers` declaring console, Linux, Python 3.12/3.13, and monitoring categories. |
| PRJ-015 | `README.md` + Installation section documenting `uv tool install aibar` and `uvx aibar` from PyPI beside git-based commands. |
| PRJ-016 | `README.md` + Installation section documenting the pipx primary flow `sudo apt install pipx`, `pipx ensurepath`, `pipx install aibar`. |
| PRJ-017 | `README.md` + Installation section documenting `pip install aibar` and `uv`/`uvx` as alternative methods after the pipx primary flow. |
| TST-071 | `tests/test_release_pypi_workflow.py` + README assertions for the pipx primary flow commands and their ordering before alternative methods. |
| CTN-011 | `src/aibar/aibar/cli.py` + `_STARTUP_UPDATE_URL = "https://pypi.org/pypi/aibar/json"` + `_fetch_startup_latest_release` reads `info.version` from the PyPI JSON API. |
| CTN-015 | `src/aibar/aibar/cli.py` + `_UPGRADE_LIFECYCLE_COMMAND = ["uv", "tool", "install", "aibar", "--force"]` (PyPI index), `_GITHUB_UPGRADE_BASE_COMMAND = ["uv", "tool", "install", "--force"]` + `_GITHUB_UPGRADE_REPO_URL = f"git+https://github.com/Ogekuri/{PROGRAM_NAME}"` completed with the `@<tag_name>` suffix by `_resolve_github_upgrade_lifecycle_command` (GitHub), and `_UNINSTALL_LIFECYCLE_COMMAND = ["uv", "tool", "uninstall", "aibar"]`. |
| REQ-073 | `src/aibar/aibar/cli.py` + `_run_startup_update_preflight` prints the bright-green update notice comparing installed `__version__` with the latest PyPI release version. |
| REQ-076 | `src/aibar/aibar/cli.py` + `_handle_upgrade_option`/`_resolve_upgrade_lifecycle_command` executes `_UPGRADE_LIFECYCLE_COMMAND` (PyPI) on Linux when `--develop`/`--dev` is absent, with exit-code propagation. |
| TST-035 | `tests/test_cli_startup_update_preflight.py` + lifecycle parametrize asserting exact argv `uv tool install aibar --force` and `uv tool uninstall aibar` with exit-code propagation and cache cleanup. |
| TST-070 | `tests/test_cli_startup_update_preflight.py` + fetch test asserting request URL `https://pypi.org/pypi/aibar/json` and `info.version` parsing. |
| TST-068 | `tests/test_release_pypi_workflow.py` + assertions that `release-pypi.yml` exists, `release-uvx+extension.yml` is absent, and the workflow declares `pypa/gh-action-pypi-publish` and `id-token: write`. |
| TST-069 | `tests/test_release_pypi_workflow.py` + README assertions for PyPI installation commands `uv tool install aibar` and `uvx aibar`. |
| CTN-020 | `src/aibar/aibar/cli.py` + `_GITHUB_RELEASE_API_URL = f"https://api.github.com/repos/Ogekuri/{PROGRAM_NAME}/releases/latest"` and `_fetch_github_latest_release` parsing `tag_name` via `_normalize_github_release_tag`. |
| REQ-176 | `src/aibar/aibar/cli.py` + `--develop`/`--dev` group option declaration and `_github_upgrade_requested_from_args` argv-token detection consumed only by `_resolve_upgrade_lifecycle_command` for `--upgrade`. |
| REQ-177 | `src/aibar/aibar/cli.py` + `_resolve_github_upgrade_lifecycle_command`/`_resolve_upgrade_lifecycle_command`/`_handle_upgrade_option` execute the tag-pinned `uv tool install --force git+https://github.com/Ogekuri/AIBar@<tag_name>` command on Linux when `--develop`/`--dev` is present, propagating exit status. |
| REQ-189 | `src/aibar/aibar/cli.py` + `_resolve_github_upgrade_lifecycle_command` + `_fetch_github_latest_release` resolve `tag_name` (captured in `StartupReleaseCheckResponse.raw_tag`) from `https://api.github.com/repos/Ogekuri/AIBar/releases/latest` before building the pinned install argv. |
| REQ-190 | `src/aibar/aibar/cli.py` + `_resolve_github_upgrade_lifecycle_command` unresolved-tag branch emits the `_ANSI_BRIGHT_RED` diagnostic and returns None; `_handle_upgrade_option` exits non-zero via `ctx.exit(1)` without subprocess execution. |
| PRJ-018 | `README.md` + dedicated non-primary "Install from GitHub" section documenting the GitHub install command, `aibar --upgrade --develop`, and dual-repository `--version` reporting. |
| TST-072 | `tests/test_cli_startup_update_preflight.py` + default `--upgrade` lifecycle argv assertions cover the PyPI branch; GitHub-branch assertions pending (test file not modified by change workflow). |
| PRJ-019 | `.github/workflows/release-pypi.yml` + `check-branch` step `Resolve tagged release branch` sets `is_master=false` with `is_release_branch=true` for develop-only tags, so `release-assets` runs while `publish-pypi` is skipped. |
| TST-073 | `tests/test_release_pypi_workflow.py` + static workflow assertions for the `master`-gated publish job and the `release-assets` job. |
| REQ-188 | `src/aibar/aibar/cli.py` + group option declaration `["--version", "--ver", "show_version"]` and `_startup_force_ignore_idle_from_args` token set `{"--version", "--ver"}` driving identical version output and idle-gate bypass. |
| TST-077 | `tests/test_cli_startup_update_preflight.py` + `test_ver_alias_prints_installed_version_without_dispatch` asserting `--ver` output equals `--version` output with labeled PyPI/GitHub release lines and dispatch bypass. |
| TST-078 | `tests/test_github_upgrade_program_name.py` + `test_develop_upgrade_pins_fetched_tag_name` asserting the `--develop` argv equals `uv tool install --force git+https://github.com/Ogekuri/aibar@<fetched tag_name>` with exit-code propagation retained by `_handle_upgrade_option`. |
| TST-079 | `tests/test_github_upgrade_program_name.py` + `test_unresolved_tag_returns_none_without_argv` asserting the None resolver return so `_handle_upgrade_option` exits non-zero without executing any install command. |
| TST-082 | `tests/test_github_upgrade_program_name.py` + `TestGithubUpgradeProgramName` + URL-composition assertions from `PROGRAM_NAME` and tag-pinned argv assertions. |
| REQ-192 | `src/aibar/aibar/cli.py` + `_emit_version_option_release_report` + unconditional `_fetch_github_latest_release()` call against `_GITHUB_RELEASE_API_URL = f"https://api.github.com/repos/Ogekuri/{PROGRAM_NAME}/releases/latest"` with no branch filtering. |
| REQ-193 | `src/aibar/aibar/cli.py` + `_format_release_report_value(github_response)` rendering `latest_version` (raw tag minus leading `v` via `_normalize_github_release_tag`) from the same `StartupReleaseCheckResponse` consumed by `_resolve_github_upgrade_lifecycle_command` pinning `@{raw_tag}`. |
| REQ-194 | `src/aibar/aibar/cli.py` + `_fetch_github_latest_release` + `urllib_error.HTTPError` branch returning failure response with `status_code=exc.code` and `error_message="GitHub release check failed: HTTP <code> <reason>."` for every GitHub HTTP error, including 404. |
| REQ-195 | `src/aibar/aibar/cli.py` + `_emit_version_option_release_report` + `_GITHUB_REPORT_UNKNOWN_PREFIX="unknown"` failure value rendered inside the aligned `Latest @ GitHub   : unknown (<reason>)` line via `_format_release_report_value(..., failure_prefix=_GITHUB_REPORT_UNKNOWN_PREFIX)` and `_format_version_report_line`. |
| REQ-199 | `src/aibar/aibar/cli.py` + `_format_version_report_line`/`_VERSION_REPORT_LABEL_WIDTH`/`_VERSION_REPORT_INSTALLED_LABEL`/`_VERSION_REPORT_PYPI_LABEL`/`_VERSION_REPORT_GITHUB_LABEL` + `_emit_version_option_release_report` emitting exactly three stdout lines with 18-character left-justified labels and aligned colons. |
| REQ-254 | `src/aibar/aibar/cli.py` + `_handle_upgrade_option` + post-install branch executing `_run_post_upgrade_gnome_install` only when the resolved upgrade argv exits `0`. |
| REQ-255 | `src/aibar/aibar/cli.py` + `_run_post_upgrade_gnome_install`/`_resolve_installed_aibar_executable` + `shutil.which(PROGRAM_NAME)` re-resolution after the install subprocess and `[<aibar>, gnome-install]` argv. |
| REQ-256 | `src/aibar/aibar/cli.py` + `_handle_upgrade_option`/`_run_post_upgrade_gnome_install` + propagated post-upgrade exit status and non-zero-install/non-Linux suppression. |
| TST-114 | `src/aibar/aibar/cli.py` + `_handle_upgrade_option`/`_run_post_upgrade_gnome_install` provide the post-upgrade `gnome-install` branch points requiring regression coverage; dedicated standalone test pending (no existing test maps to this behavior). |
| TST-083 | `tests/test_version_github_report_parity.py` + `TestVersionGithubReportParity` + one-fetch-per-invocation assertion and report-value/tag-parity assertions under deterministic fetch substitutes. |
| CTN-021 | `.github/workflows/release-pypi.yml` + `actions/checkout@v7`, `actions/attest-build-provenance@v4`, `softprops/action-gh-release@v3`, `actions/upload-artifact@v7`, `actions/download-artifact@v8`, `astral-sh/setup-uv@v7` (upstream `runs.using: node24` verified; `setup-uv@v3` Node20-era pin retired); `mikepenz/release-changelog-builder-action@v6` resolves to node24-native `v6.5`; `pypa/gh-action-pypi-publish@release/v1` is Docker-based and Node-independent. |
| TST-080 | `tests/test_workflow_node24_actions.py` + `TestNode24ActionPins` + Node24-major pin assertions over the workflow `uses:` references retained by the conditional artifact-resolution release pipeline. |
| TST-081 | `tests/test_workflow_node24_actions.py` + `TestNode24ActionPins` + absence assertions for `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION` and `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24`. |
| PRJ-020 | `scripts/pre-release-check.sh` + main pipeline + ordered preflight, locked sync, pytest, delegated build, and artifact-verification stages, with success gated on cleanup and post-run repository integrity. |
| PRJ-021 | `scripts/pre-release-check.sh` + `check_clean_working_tree` + `git status --porcelain` gate with `--allow-dirty` opt-out and non-zero abort. |
| PRJ-022 | `scripts/pre-release-check.sh` + `run_stage` + labeled `[<index>/<total>]` stage headers with `set -euo pipefail` first-failure abort. |
| PRJ-023 | `scripts/pre-release-check.sh` + tests stage + `uv run pytest tests/` execution with exit-code propagation. |
| PRJ-024 | `scripts/pre-release-check.sh` + `build_distribution` + `scripts/build.sh --dist-dir "$TEST_BUILD_DIST_DIR"` delegation into a `mktemp -d` temporary directory (stale generated-artifact removal occurs inside build.sh); `require_test_build_artifacts` validates non-empty `*.tar.gz`, `*.whl`, and the GNOME extension zip inside `$TEST_BUILD_DIST_DIR`. |
| PRJ-054 | `scripts/pre-release-check.sh` + `require_test_build_artifacts` + `fail` on missing sdist, wheel, or GNOME extension zip inside `$TEST_BUILD_DIST_DIR` after the delegated build. |
| TST-084 | `tests/test_pre_release_check_script.py` + source-level assertions for executable bit, dirty-tree gate with `--allow-dirty`, stage commands (`uv sync --locked`, `uv run pytest`, delegated build with `--dist-dir`), temporary artifact checks, and stage ordering. |
| PRJ-025 | `scripts/pre-release-check.sh` + `cleanup_pipeline_artifacts` trap + `rm -rf -- .pytest_cache`, `find src tests` removal of `__pycache__` trees, removal of script-created `build/` and `.venv`, and removal of `$TEST_BUILD_ROOT`. |
| TST-085 | `tests/test_pre_release_check_script.py` + `test_script_cleans_pipeline_artifacts_on_exit` + EXIT trap registration and cleanup command assertions covering the temporary artifact directory. |
| PRJ-028 | `scripts/pre-release-check.sh` + `validate_project_structure`/`validate_toolchain`/`validate_shell_syntax` calls inside `check_clean_working_tree` + structure, executable, and `bash -n` checks before any artifact generation. |
| PRJ-029 | `scripts/pre-release-check.sh` + `validate_python_syntax`/`validate_type_checking` + `uv run --locked python -m compileall -q src` and `uv run --locked --with pyright pyright --project pyrightconfig.json`. |
| PRJ-030 | `scripts/build.sh` + script body + `readlink -f` repository-root resolution, `uv run ... python -m build --outdir "$DIST_DIR"`, and the GNOME extension `zip` written into the resolved artifact destination directory. |
| PRJ-055 | `scripts/build.sh` + argument parser + `--dist-dir <Path>` override assigning `DIST_DIR` from the absolute argument value, with the default `DIST_DIR="$REPO_ROOT/dist"`. |
| PRJ-031 | `scripts/build.sh` + `remove_generated_dist_artifacts`/`is_generated_dist_entry` + removal of every artifact-destination entry matching `${PROJECT_NAME}-*.tar.gz`, `${PROJECT_NAME}-*.whl`, or the extension zip name for every version number, removing regular files with `rm -f` and matching directories or symbolic links with `rm -rf`, so obsolete artifacts from every version number are deleted before the build. |
| PRJ-057 | `scripts/build.sh` + `verify_generated_dist_artifacts_removed` + post-cleanup probe over every top-level artifact-destination entry that emits one diagnostic per residual generated artifact and returns non-zero before the distribution build stage. |
| PRJ-032 | `scripts/build.sh` + `assert_dist_safe_to_clean` + abort when the artifact destination directory contains files outside generated patterns, so non-generated content is never deleted. |
| PRJ-033 | `scripts/build.sh` + `verify_artifacts` + non-empty sdist, wheel, and extension zip checks inside `$DIST_DIR` with archive-integrity validation through `zipfile` and `tarfile`. |
| PRJ-034 | `scripts/build.sh` + `print_artifact_summary` + artifact path and byte-size listing emitted after successful verification, artifacts retained in the resolved artifact destination directory. |
| PRJ-056 | `scripts/pre-release-check.sh` + `mktemp -d` verification build target plus complete absence of `dist/`-scoped operations, so pipeline behavior is invariant under any repository `dist/` content. |
| PRJ-035 | `scripts/pre-release-check.sh` + `on_exit`/`on_signal` traps + EXIT, INT, and TERM handlers that run cleanup, preserve the captured status, and escalate cleanup failure to exit 1. |
| PRJ-036 | `scripts/pre-release-check.sh` + absence of every `dist/`-scoped operation: no artifact-destination safety probe, no artifact git-visibility probe, and no `:(exclude)dist` git pathspec remains in the script (the foreign-entry gate lives only in `scripts/build.sh`). |
| PRJ-037 | `scripts/pre-release-check.sh` + `verify_repository_integrity` + whole-tree pre-run `git status --porcelain` baseline comparison, artifact-absence checks, and script-created-environment checks after cleanup. |
| PRJ-038 | `.gitignore` + `!dist/` and `!dist/**/*` re-include lines in the "Include specific files and directories" section; no dist-scoped exclusion rules. |
| PRJ-039 | `scripts/build.sh` and `scripts/pre-release-check.sh` + `readlink -f "${BASH_SOURCE[0]}"` root resolution with double-quoted path handling throughout. |
| PRJ-040 | `scripts/build.sh` + `require_tool` + `command -v` validation of `uv`, `zip`, and `find` before any build step, exiting non-zero on a missing tool. |
| PRJ-041 | `.gitignore` + `!dist/` and `!dist/**/*` include rules keep committed `dist/` release artifacts git-visible; `tests/test_dist_versioned_artifacts.py` asserts the include rules without requiring tracked artifacts. |
| REQ-196 | `src/aibar/aibar/cli.py` + `--force` group option declaration and `_upgrade_force_requested_from_args` argv-token detection consumed only by `_resolve_upgrade_lifecycle_command` for `--upgrade`. |
| REQ-197 | `src/aibar/aibar/cli.py` + `_UPGRADE_FORCE_OPTIONS`/`_insert_upgrade_force_options`/`_resolve_upgrade_lifecycle_command` produce argv `uv tool install aibar --force --reinstall --refresh` when `--upgrade` is combined with `--force`. |
| REQ-198 | `src/aibar/aibar/cli.py` + `_resolve_upgrade_lifecycle_command` inserts `_UPGRADE_FORCE_OPTIONS` after the `--force` token of the tag-pinned GitHub argv, yielding `uv tool install --force --reinstall --refresh git+https://github.com/Ogekuri/<program-name>@<tag_name>`. |
| TST-087 | `tests/test_cli_startup_update_preflight.py` + forced-lifecycle parametrized tests asserting the PyPI forced argv with exit-code propagation and non-Linux manual guidance carrying the forced command without subprocess execution. |
| TST-088 | `tests/test_github_upgrade_program_name.py` + forced resolver assertions pinning the fetched `tag_name` into the forced GitHub argv and unresolved-tag abort preserved under `--force`. |
| TST-089 | `tests/test_version_github_report_parity.py` + `test_version_report_lines_align_labels_and_colons`/`test_version_report_github_failure_renders_unknown_value` + exact three-line stdout assertions, aligned-colon index assertions, and GitHub `unknown (<reason>)` failure-value assertion. |
| REQ-200 | `src/aibar/aibar/cli.py` + `_handle_config_print_option`/`_handle_config_info_option`/`_handle_config_print_raw_option`/`_handle_config_get_option`/`_handle_config_set_option`/`_handle_config_unset_option` + group option declarations for the six configuration flags. |
| REQ-201 | `src/aibar/aibar/config_cli.py` + `resolve_config_path(...)` + colon-token resolution against `CONFIG_PARAM_SPECS` with optional map-key token. |
| REQ-202 | `src/aibar/aibar/config_cli.py` + `resolve_config_path(...)`/`get_config_value(...)` + `ConfigCliError` diagnostics for unknown, surplus, empty, and absent map-key tokens. |
| REQ-203 | `src/aibar/aibar/config_cli.py` + `VIRTUAL_ROOT_LABEL`/`resolve_config_path(...)` + virtual root excluded from path token space. |
| REQ-204 | `src/aibar/aibar/config_cli.py` + `RESERVED_ARRAY_OPERATION_TOKENS`/`resolve_config_path(...)` + rejection of `append`, `+`, and `insert`. |
| REQ-205 | `src/aibar/aibar/config_cli.py` + `configuration_file_path(...)` + single global configuration file path with no project-local layer. |
| REQ-206 | `src/aibar/aibar/config_cli.py` + `load_config_document(...)` + bootstrap write of `RuntimeConfig` defaults only when the file is absent. |
| REQ-207 | `src/aibar/aibar/config_cli.py` + `load_config_document(...)` + unparsable-JSON rejection before any write. |
| REQ-208 | `src/aibar/aibar/config_cli.py` + `validate_config_document(...)` + unknown-key rejection plus `RuntimeConfig.model_validate` confirmation. |
| REQ-209 | `src/aibar/aibar/config_cli.py` + `field_default(...)`/`get_config_value(...)` + schema-default fallback for omitted fields. |
| REQ-210 | `src/aibar/aibar/config_cli.py` + `parse_cli_value(...)` + JSON-first typed parsing. |
| REQ-211 | `src/aibar/aibar/config_cli.py` + `parse_cli_value(...)` + literal-text acceptance limited to string schema types. |
| REQ-212 | `src/aibar/aibar/config.py` + `write_json_document_atomic(...)` + temporary-file, flush, fsync, `os.replace`, and directory-fsync sequence. |
| REQ-213 | `src/aibar/aibar/config.py` + `write_json_document_atomic(...)` + existing-mode preservation and `0o600` default mode. |
| REQ-214 | `src/aibar/aibar/config.py` + `write_json_document_atomic(...)` + temporary-file cleanup on failure before target replacement. |
| REQ-215 | `src/aibar/aibar/config_cli.py` + `run_config_get(...)` + single JSON value plus newline on stdout. |
| REQ-216 | `src/aibar/aibar/config_cli.py` + `run_config_print_raw(...)` + unmodified on-disk byte emission. |
| REQ-217 | `src/aibar/aibar/config_cli.py` + `run_config_*` handlers + stdout success and stderr diagnostic routing with 0/1 exit codes. |
| REQ-218 | `src/aibar/aibar/config_cli.py` + `run_config_set(...)`/`run_config_unset(...)` + silent success path. |
| REQ-219 | `src/aibar/aibar/config_cli.py` + `unset_config_value(...)` + field removal and exact map-key deletion. |
| REQ-220 | `src/aibar/aibar/config_cli.py` + `unset_config_value(...)` + absent-map-key rejection. |
| REQ-221 | `src/aibar/aibar/config_cli.py` + `set_config_value(...)`/`validate_schema_value(...)` + whole-map replacement validation. |
| REQ-222 | `src/aibar/aibar/config_cli.py` + `render_config_tree(...)`/`build_print_tree(...)`/`build_info_tree(...)` + single shared renderer. |
| REQ-223 | `src/aibar/aibar/config_cli.py` + `build_print_tree(...)`/`build_info_tree(...)` + whole-tree and requested-path projections. |
| REQ-224 | `src/aibar/aibar/config_cli.py` + `render_config_tree(...)` + `_emit_config_node(...)` marker/prefix algorithm. |
| REQ-225 | `src/aibar/aibar/config_cli.py` + `_emit_config_node(...)` + detail-prefix derivation from sibling position. |
| REQ-226 | `src/aibar/aibar/config_cli.py` + `render_config_tree(...)` + marker-free root heading with four-space detail indent. |
| REQ-227 | `src/aibar/aibar/config_cli.py` + `ConfigTreeNode` + details-only metadata and table lines. |
| REQ-228 | `src/aibar/aibar/config_cli.py` + `format_print_parameter(...)` + JSON-encoded value and default/custom status suffix. |
| REQ-229 | `src/aibar/aibar/config_cli.py` + `format_print_parameter(...)`/`format_config_table(...)` + map summary and `Key | Value` table. |
| REQ-230 | `src/aibar/aibar/config_cli.py` + `format_print_parameter(...)` + empty-map hint without table. |
| REQ-231 | `src/aibar/aibar/config_cli.py` + `build_info_parameter(...)` + type/description heading and `Default`/`Set cmd`/`Reset cmd`/map action details. |
| REQ-232 | `src/aibar/aibar/config_cli.py` + `build_info_parameter(...)` + `Allowed Values` table for the `currency_symbols` domain. |
| REQ-233 | `src/aibar/aibar/config_cli.py` + `format_config_table(...)` + measured column widths and shared border template. |
| REQ-234 | `src/aibar/aibar/config_cli.py` + `display_width(...)`/`format_config_table(...)` + display-width measurement over escaped cells. |
| REQ-235 | `src/aibar/aibar/config_cli.py` + `CONFIG_PARAM_SPECS` + schema-driven examples, constraints, defaults, and allowed values. |
| REQ-236 | `src/aibar/aibar/config_cli.py` + `_verify_schema_alignment(...)` + import-time field-set divergence abort. |
| REQ-237 | `src/aibar/aibar/cli.py` + group option help text and epilog examples listing all six configuration options with canonical paths. |
| REQ-238 | `src/aibar/aibar/config_cli.py` + all rendered strings and diagnostics + English-only wording. |
| TST-090 | `tests/test_config_cli_renderer.py` + exact whole-output golden assertions for root children, nested siblings, and detail layouts. |
| TST-091 | `tests/test_config_cli_structure.py` + `_validate_tree_structure(...)` over real `--print`/`--info` output. |
| TST-092 | `tests/test_config_cli_structure.py` + `_validate_tables(...)` + border-width, separator-column, and owner-prefix assertions. |
| TST-093 | `tests/test_config_cli_operations.py` + `--get`/`--set`/`--unset`/`--print`/`--info`/`--print-raw` behavior assertions. |
| TST-094 | `tests/test_config_cli_operations.py` + atomic-failure assertions on unchanged bytes and absent temporary files. |
| TST-095 | `tests/test_config_cli_operations.py` + bootstrap and existing-file preservation assertions. |
| TST-096 | `tests/test_config_cli_operations.py` + published-example execution assertions via `shlex.split`. |
| TST-097 | `tests/test_dist_versioned_artifacts.py` + `.gitignore` include-section assertions and `git check-ignore --no-index` visibility assertions for `dist/` artifacts. |
| PRJ-047 | `scripts/build.sh` + `remove_intermediate_artifacts` + removal of `build/`, `.pytest_cache/`, `*.egg-info` directories, and `__pycache__` trees under `src/` and `tests/` after every build while `dist/` versioned artifacts stay untouched. |
| PRJ-048 | `scripts/build.sh` + `cleanup_on_exit` EXIT handler plus `trap 'exit 130' INT` and `trap 'exit 143' TERM` + intermediate-artifact cleanup preserving the captured exit status. |
| PRJ-049 | `scripts/build.sh` + `verify_no_intermediate_artifacts` + residual-artifact detection outside `dist/` with non-zero exit. |
| TST-099 | `tests/test_build_script.py` + source-level assertions for executable bit, root resolution, `--dist-dir` override with the `dist` default, toolchain validation, all-version generated-artifact deletion, and foreign artifact-destination entry preservation. |
| TST-107 | `tests/test_pre_release_check_script.py` + `test_script_has_no_dist_directory_dependency` + absence assertions for a `REPO_ROOT/dist` destination, `assert_dist_safe_to_clean`, `:(exclude)dist` git pathspec, and `dist/` artifact globs. |
| TST-100 | `tests/test_build_script.py` + EXIT/INT/TERM trap assertions plus `remove_intermediate_artifacts` coverage of `build/`, `.pytest_cache/`, `*.egg-info`, and `__pycache__` with `dist/` retention. |
| TST-101 | `tests/test_build_script.py` + `verify_no_intermediate_artifacts` assertions covering residual-artifact detection and non-zero exit. |
| TST-102 | `tests/test_build_script.py` + absence assertions for `scripts/clean.sh` and for `clean.sh` references inside `scripts/*.sh`. |
| REQ-239 | `src/aibar/aibar/providers/deepseek.py` + `DeepSeekProvider.fetch` + `https://api.deepseek.com/user/balance` with `Authorization: Bearer <key>` and `Accept: application/json`. |
| REQ-240 | `src/aibar/aibar/config.py` + `Config.ENV_VARS[ProviderName.DEEPSEEK] = "DEEPSEEK_API_KEY"`; `src/aibar/aibar/cli.py` + `setup` DeepSeek API-key prompt writing `DEEPSEEK_API_KEY` to `~/.config/aibar/env`. |
| REQ-241 | `src/aibar/aibar/providers/deepseek.py` + `_parse_response`/`_normalize_balance_infos` + `raw.deepseek_balance_infos` records and `UsageMetrics`. |
| REQ-242 | `src/aibar/aibar/providers/deepseek.py` + `_parse_response` + `metrics.remaining` from preferred `total_balance`, unset `limit`/`cost`, and `resolve_currency_symbol(data, "deepseek")`. |
| REQ-243 | `src/aibar/aibar/cli.py` + `_FIXED_WINDOW_BY_PROVIDER[ProviderName.DEEPSEEK] = WindowPeriod.DAY_30`; `src/aibar/aibar/providers/deepseek.py` single-call fetch. |
| REQ-244 | `src/aibar/aibar/providers/deepseek.py` returns `ProviderResult` consumed by unmodified `retrieve_results_via_cache_pipeline`, idle-time, throttling, and retry helpers. |
| REQ-245 | `src/aibar/aibar/cli.py` + `_build_result_panel`/`_build_deepseek_balance_lines` + `Balance: <currency_symbol><remaining>` block. |
| REQ-246 | `src/aibar/aibar/cli.py` + DeepSeek branch returns before generic usage/counter rows; `PROGRESS_BAR_PROVIDERS`/`API_COUNTER_PROVIDERS` exclude `deepseek`. |
| REQ-247 | `src/aibar/aibar/providers/deepseek.py` + `fetch` + 401 `AuthenticationError`, 429 error result with `retry_after_seconds`, other non-200 provider error result. |
| REQ-248 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_updateUI`/`_buildPanelButton`/`_populateProviderCard` DeepSeek monetary labels; `stylesheet.css` + `aibar-tab-label-deepseek` using `#FF375F`. |
| REQ-249 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `PROGRESS_BAR_PROVIDERS`/`API_COUNTER_PROVIDERS`/`panelPercents` exclude `deepseek`; ordering arrays include it last. |
| REQ-250 | `src/aibar/aibar/providers/deepseek.py` + `get_config_help` + balance-only API note; `README.md` + DeepSeek provider section. |
| TST-108 | `tests/test_deepseek_provider.py` + balance mapping, fixed `30d` window, currency symbol, and null-counter assertions. |
| TST-109 | `tests/test_deepseek_provider.py` + CLI panel assertions for `Balance`/`Topped up`/`Granted` rows and absent usage/bar/counter rows. |
| TST-110 | `tests/test_setup_runtime_config.py` + DeepSeek activation, currency-symbol, and `DEEPSEEK_API_KEY` prompt assertions. |
| TST-111 | `tests/test_deepseek_provider.py` + GNOME source assertions for trailing `deepseek` order, rose classes, monetary labels, and `_handleError` reset. |
| REQ-251 | `src/aibar/aibar/cli.py` + `_build_deepseek_balance_lines` + `Topped up:`/`Granted:` rows from `raw.deepseek_balance_infos[0]`. |
| REQ-252 | `src/aibar/aibar/cli.py` + `_build_deepseek_balance_lines` and `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_populateProviderCard` render only the three monetary rows. |
| REQ-253 | `src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js` + `_populateProviderCard` DeepSeek monetary markup; `_panelBalanceText` keeps the panel token on `metrics.remaining`. |
| TST-112 | `tests/test_deepseek_provider.py` + monetary-row and absent `Spent`/`Cost` assertions for CLI and GNOME. |
| TST-113 | `tests/test_deepseek_provider.py` + `#FF375F` stylesheet and `\033[38;5;204m` CLI color assertions. |
