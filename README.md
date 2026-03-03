# AIBar/aibar (0.0.0)

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/license-GPL--3.0-491?style=flat-square" alt="License: GPL-3.0">
  <img src="https://img.shields.io/badge/platform-Linux-6A7EC2?style=flat-square&logo=terminal&logoColor=white" alt="Platforms">
  <img src="https://img.shields.io/badge/docs-live-b31b1b" alt="Docs">
<img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv">
</p>

<p align="center">
<strong>Monitor AI usage and quota in one CLI/TUI.</strong><br>
AIBar aggregates usage metrics for Claude, OpenAI, OpenRouter, GitHub Copilot, and Codex, with both terminal output and a GNOME panel extension.
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> |
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
- Interactive Textual UI (`ui`) with refresh controls and 5h/7d window switching.
- Provider diagnostics (`doctor`) and interactive setup (`setup`) for credentials.
- Local cache of successful results under `~/.cache/aibar` to reduce repeated API calls.
- GNOME Shell extension support via `aibar show --json`.


## Quick Start

```bash
# 1) From the repository root, run the launcher (creates .venv on first run)
./aibar.sh --help

# 2) Configure credentials interactively
./aibar.sh setup

# 3) Verify provider configuration and connectivity
./aibar.sh doctor

# 4) Show usage
./aibar.sh show
./aibar.sh show --json
```


## Usage

```bash
# Show all configured providers (default window: 7d)
./aibar.sh show

# Show one provider and select window
./aibar.sh show --provider claude --window 5h

# JSON output
./aibar.sh show --json

# Print required environment variables
./aibar.sh env

# Interactive setup wizard
./aibar.sh setup

# Provider login helpers
./aibar.sh login --provider claude
./aibar.sh login --provider copilot

# Launch terminal UI
./aibar.sh ui
```



## Acknowledgments

- Thanks to **Shobhit Narayanan** for creating [GnomeCodexBar](https://github.com/shenron0101/GnomeCodexBar).



## License

- This program is licensed under the terms in [`LICENSE`](./LICENSE).
- This project includes modified files from **GnomeCodexBar**; those files are covered by the license provided in `LICENSE_GnomeCodexBar`, as required by the original license terms.
