# AIBar/aibar (0.32.0)

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/license-GPL--3.0-491?style=flat-square" alt="License: GPL-3.0">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-6A7EC2?style=flat-square&logo=terminal&logoColor=white" alt="Platforms">
  <img src="https://img.shields.io/badge/docs-live-b31b1b" alt="Docs">
<img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv">
</p>

<p align="center">
<strong>Monitor AI usage and quota in one CLI.</strong><br>
AIBar aggregates usage metrics for Claude, OpenAI, OpenRouter, GitHub Copilot, Codex, and GeminiAI, with terminal output and a GNOME panel extension.
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
⚠️ <strong>IMPORTANT NOTICE</strong>: Created with <a href="https://github.com/Ogekuri/useReq"><strong>useReq/req</strong></a> 🤖✨ ⚠️<br>
<br>
<p>


## Feature Highlights
- Unified `show` command for multiple providers (`claude`, `openai`, `openrouter`, `copilot`, `codex`, `geminiai`).
- Text output and machine output (`show --json`) with stable top-level sections (`payload`, `status`, `idle_time`, `freshness`, `extension`).
- Per-run refresh override with `show --force` (bypasses idle-time gating for that execution).
- Interactive setup (`setup`) for runtime controls, credentials, GeminiAI OAuth, provider currency symbols, and logging flags.
- Built-in lifecycle and observability flags: `--version|--ver`, `--upgrade`, `--uninstall`, `--enable-log`, `--disable-log`, `--enable-debug`, `--disable-debug`.
- GNOME Shell extension support via `gnome-install` / `gnome-uninstall` plus JSON-driven auto-refresh metadata.

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
# allowed values: claude, openai, openrouter, copilot, codex, geminiai, all
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

### `show` window behavior

- Allowed windows: `5h`, `7d`, `30d`.
- `claude` and `codex` support dual-window rendering (`5h` and `7d`) in default text output.
- For `copilot`, `openrouter`, `openai`, and `geminiai`, the effective window is fixed to `30d` even if another `--window` is provided.

### Repository helper scripts

```bash
# Repository launcher (delegates to uv run --project ... python -m aibar.cli)
scripts/aibar.sh --help

# Claude token refresh helper
scripts/claude_token_refresh.sh {start|stop|status|once|loop}

# GNOME nested-shell test helper
# runs gnome-install, then starts a nested Wayland GNOME Shell (1280x720)
scripts/test-gnome-extension.sh
```

## GeminiAI prerequisites

To enable GeminiAI features, configure Google Cloud before running `aibar setup`:

1. Create **Desktop Client OAuth 2.0** credentials in the target Google Cloud project.
2. In `aibar setup`, configure GeminiAI OAuth client JSON (`file` or `paste`) and authorize requested scopes:
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


### Claude

[![Screenshot04](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot04.png)](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot04.png)

### OpenRouter

[![Screenshot05](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot05.png)](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot05.png)

### GitHub Copilot

[![Screenshot06](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot06.png)](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot06.png)

### OpenAI Codex

[![Screenshot07](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot07.png)](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot07.png)

### Gemini AI API

[![Screenshot08](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot08.png)](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot07.png)

### OpenAI API

[![Screenshot09](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot09.png)](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot07.png)
