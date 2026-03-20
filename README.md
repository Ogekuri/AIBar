# AIBar/aibar (0.13.0)

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
- Human-readable output and JSON output (`--json`) for scripting/integration.
- Provider diagnostics (`doctor`) and interactive setup (`setup`) for credentials.
- Local cache of successful results under `~/.cache/aibar` to reduce repeated API calls.
- GNOME Shell extension

### Screenshot

[![Screenshot10](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot10.png)](https://raw.githubusercontent.com/Ogekuri/AIBar/refs/heads/master/images/Screenshot10.png)



## Quick Start

```bash
# 1) From the repository root, run the launcher
aibar --help

# 2) Configure credentials interactively
aibar setup

# 3) Verify provider configuration and connectivity
aibar doctor

# 4) Show usage
aibar show
aibar show --json
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

```bash
# Show all configured providers (default window: 7d)
aibar show

# Show one provider and select window
aibar show --provider claude --window 5h

# JSON output
aibar show --json

# Print required environment variables
aibar env

# Interactive setup wizard
aibar setup

# Provider login helpers
aibar login --provider claude
aibar login --provider copilot
aibar login --provider geminiai

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
