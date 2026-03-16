#!/usr/bin/env bash
# @file test-gnome-extension.sh
# @brief Launches a nested GNOME Shell session for extension testing.
# @details Invokes `aibar gnome-install` to update and enable extension files,
# then starts a nested GNOME Shell at 1024x800 resolution via
# `MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800 dbus-run-session -- gnome-shell --nested --wayland`.
# No subcommand parameter required; executes directly on invocation.
# @satisfies PRJ-004, REQ-031, REQ-033

set -euo pipefail

## @brief Runs the extension installer CLI command to update extension files.
## @details Invokes `aibar gnome-install` to copy extension files and enable the extension.
## Exits with non-zero status if the command fails.
## @return Exit 0 on success; propagates CLI exit code on failure.
## @satisfies REQ-031
update_extension() {
    if ! command -v aibar >/dev/null 2>&1; then
        echo "ERROR: aibar CLI not found in PATH." >&2
        exit 1
    fi
    aibar gnome-install
}

update_extension
echo "Starting nested GNOME Shell at 1024x800..."
env MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800 dbus-run-session -- gnome-shell --nested --wayland
