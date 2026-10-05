# AIBar/aibar (0.48.0)

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/license-GPL--3.0-491?style=flat-square" alt="License: GPL-3.0">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-6A7EC2?style=flat-square&logo=terminal&logoColor=white" alt="Platforms">
  <img src="https://img.shields.io/badge/docs-live-b31b1b" alt="Docs">
<img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv">
</p>

<p align="center">
<strong>Monitor AI usage and quota in one CLI.</strong><br>
AIBar aggregates usage metrics for Claude, OpenAI, OpenRouter, GitHub Copilot, Codex, GeminiAI, and Z.ai, with terminal output and a GNOME panel extension.
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> |
  <a href="#requirements-uv">Requirements (uv)</a> |
  <a href="#installation-uv">Installation (uv)</a> |
  <a href="#feature-highlights">Feature Highlights</a> |
  <a href="#usage">Usage</a> |
  <a href="#acknowledgments">Acknowledgments</a>
</p>

<p align="center">
<br>
🚧 <strong>DRAFT</strong>: 👾 Alpha Development 👾 - Work in Progress 🏗️ 🚧<br>
⚠️ <strong>IMPORTANT NOTICE</strong>: Created with <a href="https://github.com/Ogekuri/PI-useReq"><strong>PI-useReq/pi-usereq</strong></a> 🤖✨ ⚠️<br>
<br>
<p>


## Feature Highlights
- Unified `show` command for multiple providers (`claude`, `openai`, `openrouter`, `copilot`, `codex`, `geminiai`, `zai`).
- Text output and machine output (`show --json`) with stable top-level sections (`payload`, `status`, `idle_time`, `freshness`, `extension`, `enabled_providers`).
- Per-run refresh override with `show --force` (bypasses idle-time gating for that execution).
- Interactive `setup` for provider enable/disable state, runtime throttling, Copilot overage pricing, provider currency symbols, GeminiAI OAuth/project settings, and logging flags.
- Built-in lifecycle and observability flags: `--version|--ver`, `--upgrade`, `--uninstall`, `--enable-log`, `--disable-log`, `--enable-debug`, `--disable-debug`.
- Startup release preflight that can emit update notices or fetch diagnostics before normal command output.
- GNOME Shell extension support via `gnome-install` / `gnome-uninstall`, popup `Refresh Now`, and JSON-driven refresh/window metadata.

### Screenshot

[![Screenshot10](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot10.png)](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot10.png)



## Quick Start

```bash
# 1) From the repository root, run the repository launcher
scripts/aibar.sh --help

# 2) Configure credentials and runtime settings
scripts/aibar.sh setup

# 3) Verify provider configuration and connectivity
scripts/aibar.sh doctor

# 4) Show usage
scripts/aibar.sh show
scripts/aibar.sh show --json
```

## Requirements (uv)

AIBar requires [Astral uv](https://docs.astral.sh/uv/) for all local launcher/runtime workflows.
Do not create or manage external virtual environments for repository execution.


## Installation (uv)

[uv](https://docs.astral.sh/uv/) is the recommended tool for installing and running AIBar.

### Install from Git

```bash
uv tool install aibar --force --from git+https://github.com/Ogekuri/AIBar.git
```

After installation the `aibar` command is available system-wide:

```bash
aibar --help
aibar setup
aibar show
```

### Live Execution (no install)

Run AIBar directly from the repository without a local clone using `uvx`:

```bash
uvx --from "git+https://github.com/Ogekuri/AIBar.git" aibar --help
uvx --from "git+https://github.com/Ogekuri/AIBar.git" aibar show --json
uvx --from "git+https://github.com/Ogekuri/AIBar.git" aibar doctor
```

### Export requirements.txt (optional)

```bash
uv export --format requirements-txt > requirements.txt
```

### Uninstall

```bash
uv tool uninstall aibar
```


## Usage

### Core commands

```bash
# Show all configured providers
# (default flow renders dual windows for claude/codex when --window is not set)
aibar show

# Provider selection
# allowed values: claude, openai, openrouter, copilot, codex, geminiai, zai, all
aibar show --provider claude --window 5h

# JSON output for scripts/integrations
aibar show --json

# Force refresh for current execution (ignore idle-time gate)
aibar show --force

# Diagnostics and configuration
aibar doctor
aibar env
aibar setup

# Provider login helpers
aibar login --provider claude
aibar login --provider copilot
aibar login --provider geminiai

# GNOME extension lifecycle
aibar gnome-install
aibar gnome-uninstall
```

Providers disabled during `aibar setup` (stored under `enabled_providers`) are skipped by refresh/idle-time handling and omitted from `show` text and `show --json` output.

### Global lifecycle and logging options

```bash
# Version
# aibar --version and aibar --ver are equivalent
aibar --version

# Package lifecycle helpers (Linux: executed directly; non-Linux: prints manual command)
aibar --upgrade
aibar --uninstall

# Runtime logging flags
# execution log path: ~/.cache/aibar/aibar.log
aibar --enable-log
aibar --disable-log
aibar --enable-debug
aibar --disable-debug
```

- Startup behavior: every CLI invocation runs a latest-release preflight before command parsing. Notices and fetch diagnostics are idle-cached for about `300` seconds; `aibar --version` and `aibar --ver` still force one online check.
- `--upgrade` and `--uninstall` execute only on Linux. On non-Linux platforms, AIBar prints the equivalent manual `uv` command.
- Debug rows are emitted only when execution logging is enabled. For verbose API diagnostics, enable both `--enable-log` and `--enable-debug`.

### `show` window behavior

- Allowed windows: `5h`, `7d`, `30d`.
- `claude` and `codex` support dual-window rendering (`5h` and `7d`) in default text output when `--window` is not explicitly set.
- For `copilot`, `openrouter`, `openai`, `geminiai`, and `zai`, the effective window is fixed to `30d` even if another `--window` is provided.

### Text output layout

- Each provider renders one colored panel in the canonical order `claude`, `openrouter`, `copilot`, `codex`, `openai`, `geminiai`, `zai`; all panels share the same width.
- `Status` is the first line on successful panels, and every panel ends with a right-aligned `Updated: <datetime>, Next: <datetime>` freshness line.
- Usage rows use `Usage: <window> <progress_bar> <percent>%` for `claude`, `openrouter`, `copilot`, `codex`, and `zai`; `openai` and `geminiai` render `Usage: <window> <percent>%` without a bar.
- `Remaining credits: <remaining> / <limit>` is printed for `claude`, `codex`, and `copilot` when the status is `OK`.
- Percentages above 100% render the over-limit segment with the 100% boundary marker.
- Failed providers render `Status: FAIL`, the failure `Reason:`, and the `Updated/Next` freshness line instead of usage statistics.

### OpenRouter

- The OpenRouter usage view is driven by the **API key credit total** returned by OpenRouter: `100%` on the progress bar corresponds to the total credits on the key (current spend + remaining credit), and the bar shows current spend relative to that total.
- No monthly budget needs to be configured. Spending beyond purchased credits renders the over-credit bar (`>100%`) with the same over-limit marker used by other quota providers.
- `aibar setup` does not prompt for an OpenRouter budget, and no budget key is stored in `config.json`.
- CLI and GNOME views also render `Total cost: <currency_symbol><total_cost>` from the all-time API usage reported for the key (exposed as `metrics.total_cost` in `show --json`).
- `Requests` and `Tokens` rows are not rendered for OpenRouter: the key API exposes no per-key request/token counters.

### Z.ai

- Provider key `zai`; the API key is read from `ZAI_API_KEY` (environment variable or `~/.config/aibar/env`) and can be entered during `aibar setup`.
- One quota request returns all quotas; the effective window is fixed to `30d`.
- Text output renders one progress bar per quota with the short labels `5h`, `1w`, and `1m` (5-hour quota, weekly quota, and total monthly Web Search/Reader quota), each followed by its own `Resets in: <duration>` countdown.
- Usage above 100% on any quota renders the shared over-limit bar segment with the 100% boundary marker.
- In the GNOME extension, Z.ai renders as the last provider tab/card (cyan accent): one progress bar per quota with `Reset in: <duration>`, and the panel status bar shows the `5h` quota percentage followed by the bold `1w` quota percentage.

### `show --json` contract

Top-level keys:
- `payload`: normalized provider results keyed by provider id.
- `status`: per-provider, per-window fetch outcomes (`OK` / `FAIL`) and cached error metadata.
- `idle_time`: provider idle-time timestamps used for refresh gating.
- `freshness`: provider `Updated` / `Next` timestamps used by CLI and GNOME views.
- `extension`: GNOME-facing metadata (`gnome_refresh_interval_seconds`, `idle_delay_seconds`, `copilot_extra_premium_request_cost`, `window_labels`).
- `enabled_providers`: normalized provider enable/disable map consumed by CLI and GNOME surfaces.

### Setup persistence and config schema

`aibar setup` writes:
- `~/.config/aibar/env`: credentials entered during setup.
- `~/.config/aibar/config.json`: runtime settings.

User-editable `config.json` keys surfaced by setup:
- `idle_delay_seconds` (default `300`)
- `api_call_delay_milliseconds` (default `100`)
- `api_call_timeout_milliseconds` (default `5000`)
- `default_retry_after_seconds` (default `3600`)
- `gnome_refresh_interval_seconds` (default `60`)
- `billing_data` (default `billing_data`)
- `enabled_providers` (missing provider keys default to enabled)
- `copilot_extra_premium_request_cost` (default `0.04`)
- `currency_symbols` (per-provider display symbol; setup choices `$`, `£`, `€`, default `$`)
- `log_enabled`
- `debug_enabled`
- `geminiai_project_id`

### GNOME extension behavior

- Installed path: `~/.local/share/gnome-shell/extensions/aibar@aibar.panel/`.
- Supported GNOME Shell versions: `45`, `46`, `47`, `48`.
- Scheduled refreshes run `aibar show --json`.
- Popup `Refresh Now` runs `aibar show --json --force`.
- Disabled providers from `aibar setup` are hidden from panel labels, tabs, and cards.
- Provider cards show `Updated: ..., Next: ...` freshness labels.
- Auto-refresh interval follows `gnome_refresh_interval_seconds` from `aibar setup` / `config.json`.

### Repository helper scripts

```bash
# Repository launcher (delegates to uv run --project ... python -m aibar.cli)
scripts/aibar.sh --help

# Claude token refresh helper
scripts/claude_token_refresh.sh {start|stop|status|once|loop}

# Override refresh interval (seconds; default: 1800)
AIBAR_CLAUDE_REFRESH_INTERVAL_SECONDS=900 scripts/claude_token_refresh.sh start

# Helper state files
# log: ~/.config/aibar/claude_token_refresh.log
# pid: ~/.config/aibar/claude_token_refresh.pid

# GNOME nested-shell test helper
# runs gnome-install, then starts a nested Wayland GNOME Shell (1280x720)
scripts/test-gnome-extension.sh
```

## GeminiAI prerequisites

To enable GeminiAI features, configure Google Cloud before running `aibar setup`:

1. Create **Desktop Client OAuth 2.0** credentials in the target Google Cloud project.
2. In `aibar setup`, configure GeminiAI OAuth client JSON (`file` or `paste`) or re-authorize with `login`, then authorize requested scopes:
   - `https://www.googleapis.com/auth/bigquery.readonly`
   - `https://www.googleapis.com/auth/monitoring.read`
   - `https://www.googleapis.com/auth/cloud-platform`
3. Configure the Gemini project id in setup (`geminiai project id`) or via `GEMINIAI_PROJECT_ID`.
4. Set setup field `billing_data` to the BigQuery dataset containing billing export tables (`gcp_billing_export_v1_*`, default dataset name: `billing_data`).
5. Ensure required Google APIs are enabled for the project used by OAuth credentials:
   - Cloud Monitoring API
   - BigQuery API



## Acknowledgments

- Thanks to **Shobhit Narayanan** for creating [GnomeCodexBar](https://github.com/shenron0101/GnomeCodexBar).



## License

- This program is licensed under the terms in [`LICENSE`](./LICENSE).
- This project includes modified files from **GnomeCodexBar**; those files are covered by the license provided in `LICENSE_GnomeCodexBar`, as required by the original license terms.


## Screenshots

### Claude

[![Screenshot01](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot01.png)](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot01.png)
[![Screenshot02](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot02.png)](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot02.png)
[![Screenshot03](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot03.png)](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot03.png)


### Claude (7d window)

[![Screenshot04](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot04.png)](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot04.png)

### OpenRouter

[![Screenshot05](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot05.png)](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot05.png)

### GitHub Copilot

[![Screenshot06](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot06.png)](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot06.png)

### OpenAI Codex

[![Screenshot07](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot07.png)](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot07.png)

### Gemini AI API

[![Screenshot08](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot08.png)](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot08.png)

### OpenAI API

[![Screenshot09](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot09.png)](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot09.png)
