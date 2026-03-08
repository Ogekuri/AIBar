# AIBar/aibar (0.1.0)

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/license-GPL--3.0-491?style=flat-square" alt="License: GPL-3.0">
  <img src="https://img.shields.io/badge/platform-Linux-6A7EC2?style=flat-square&logo=terminal&logoColor=white" alt="Platforms">
  <img src="https://img.shields.io/badge/docs-live-b31b1b" alt="Docs">
<img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv">
</p>

<p align="center">
<strong>Monitor AI usage and quota in one CLI.</strong><br>
AIBar aggregates usage metrics for Claude, OpenAI, OpenRouter, GitHub Copilot, Codex, and GeminiAI, with terminal output and a GNOME panel extension.
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> |
  <a href="#installation-uv">Installation (uv)</a> |
  <a href="#feature-highlights">Feature Highlights</a> |
  <a href="#usage">Usage</a> |
  <a href="#acknowledgments">Acknowledgments</a>
</p>

<p align="center">
<br>
🚧 <strong>DRAFT:</strong>Preliminary Version 📝 - Work in Progress 🏗️ 🚧<br>
⚠️ <strong>IMPORTANT NOTICE</strong>: Created with <a href="https://github.com/Ogekuri/useReq"><strong>useReq/req</strong></a> 🤖✨ ⚠️<br>
<br>
<p>


## Feature Highlights
- Unified `show` command for multiple providers (`claude`, `openai`, `openrouter`, `copilot`, `codex`).
- Human-readable output and JSON output (`--json`) for scripting/integration.
- Provider diagnostics (`doctor`) and interactive setup (`setup`) for credentials.
- Local cache of successful results under `~/.cache/aibar` to reduce repeated API calls.
- GNOME Shell extension support via `aibar show --json`.


## Screenshots

### Claude

[![Screenshot1](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot1.png)](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot1.png)


### GitHub Copilot


[![Screenshot2](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot2.png)](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot2.png)


### OpenAI Codex

[![Screenshot3](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot3.png)](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot3.png)


## Quick Start

```bash
# 1) From the repository root, run the launcher (creates .venv on first run)
./aibar --help

# 2) Configure credentials interactively
./aibar setup

# 3) Verify provider configuration and connectivity
./aibar doctor

# 4) Show usage
./aibar show
./aibar show --json
```


## Installation (uv)

[uv](https://docs.astral.sh/uv/) is the recommended tool for installing and running AIBar.

### Install from Git

```bash
uv pip install "aibar @ git+https://github.com/Ogekuri/AIBar.git"
```

After installation the `aibar` command is available system-wide (or in the active virtual environment):

```bash
aibar --help
aibar show
aibar doctor
```

### Live Execution (no install)

Run AIBar directly from the repository without a local clone using `uvx`:

```bash
uvx --from "git+https://github.com/Ogekuri/AIBar.git" aibar --help
uvx --from "git+https://github.com/Ogekuri/AIBar.git" aibar show --json
uvx --from "git+https://github.com/Ogekuri/AIBar.git" aibar doctor
```

### Uninstall

```bash
uv pip uninstall aibar
```


## Usage

```bash
# Show all configured providers (default window: 7d)
./aibar show

# Show one provider and select window
./aibar show --provider claude --window 5h

# JSON output
./aibar show --json

# Print required environment variables
./aibar env

# Interactive setup wizard
./aibar setup

# Provider login helpers
./aibar login --provider claude
./aibar login --provider copilot

```

## GeminiAI prerequisites

To enable GeminiAI features, configure Google Cloud before running `aibar setup`:

1. Enable **Desktop Client OAuth 2.0** credentials in the target Google Cloud application.
2. Create a BigQuery dataset in Google Cloud Console and provide its name in setup prompt `billing_data` (default: `billing_data`).
3. Enable API access for the OAuth client project:
   - Cloud Monitoring API
   - Dataform API
   - Generative Language API
   - Cloud Dataplex API
   - BigQuery API



## Acknowledgments

- Thanks to **Shobhit Narayanan** for creating [GnomeCodexBar](https://github.com/shenron0101/GnomeCodexBar).



## License

- This program is licensed under the terms in [`LICENSE`](./LICENSE).
- This project includes modified files from **GnomeCodexBar**; those files are covered by the license provided in `LICENSE_GnomeCodexBar`, as required by the original license terms.
