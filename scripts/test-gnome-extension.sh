#!/usr/bin/env bash
# @file test-gnome-extension.sh
# @brief Development helper commands for aibar GNOME extension.
# @details Wraps nested-shell start, enable/disable/reload, and log tail commands
# for local extension workflows with fixed 1024x800 nested-shell resolution.
# Commands `start`, `enable`, and `reload` invoke `install-gnome-extension.sh`
# before execution to ensure extension files are up-to-date.
# @satisfies PRJ-004, REQ-031

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
    enable)
        update_extension
        gnome-extensions enable "$EXT_UUID"
        echo "Extension enabled"
        ;;
    disable)
        gnome-extensions disable "$EXT_UUID"
        echo "Extension disabled"
        ;;
    reload)
        update_extension
        gnome-extensions disable "$EXT_UUID"
        sleep 1
        gnome-extensions enable "$EXT_UUID"
        echo "Extension reloaded"
        ;;
    logs)
        journalctl -f -o cat /usr/bin/gnome-shell | grep -i "aibar"
        ;;
    *)
        echo "Usage: $0 {start|enable|disable|reload|logs}"
        exit 1
        ;;
esac
