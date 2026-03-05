#!/usr/bin/env bash
# @file test-gnome-extension.sh
# @brief Launches a nested GNOME Shell session for extension testing.
# @details Invokes `install-gnome-extension.sh` to update extension files,
# then starts a nested GNOME Shell at 1024x800 resolution via
# `MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800 dbus-run-session -- gnome-shell --nested --wayland`.
# Accepts only the `start` subcommand.
# @satisfies PRJ-004, REQ-031, REQ-033

set -euo pipefail

## @brief Resolves the directory containing this script.
## @details Uses readlink -f to resolve symlinks, then extracts dirname.
## @return Absolute path to the script's parent directory.
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

readonly EXT_UUID="aibar@aibar.panel"
readonly INSTALL_SCRIPT="${SCRIPT_DIR}/install-gnome-extension.sh"

## @brief Runs the extension installer to update extension files.
## @details Invokes install-gnome-extension.sh from the same scripts/ directory.
## Exits with non-zero status if the installer fails.
## @return Exit 0 on success; propagates installer exit code on failure.
## @satisfies REQ-031
update_extension() {
    if [[ ! -x "${INSTALL_SCRIPT}" ]]; then
        echo "ERROR: install-gnome-extension.sh not found or not executable: ${INSTALL_SCRIPT}" >&2
        exit 1
    fi
    "${INSTALL_SCRIPT}"
}

case "${1:-}" in
    start)
        update_extension
        echo "Starting nested GNOME Shell at 1024x800..."
        env MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800 dbus-run-session -- gnome-shell --nested --wayland
        ;;
    *)
        echo "Usage: $0 {start}"
        exit 1
        ;;
esac
