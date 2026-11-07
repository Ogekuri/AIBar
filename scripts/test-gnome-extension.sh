#!/usr/bin/env bash
# @file test-gnome-extension.sh
# @brief Launches a nested GNOME Shell interactive debug session for extension testing.
# @details Validates graphical-session and Devkit prerequisites before installing
# the extension; starts GNOME 50 through the shared D-Bus debug wrapper.
# Devkit owns the visible viewport size; the historical dummy-mode environment
# remains 1280x720 but does not force the Devkit viewer dimensions.
# Time O(1) orchestration; space O(1); installation modifies user extension files.
# @pre Ubuntu 26.04 packages: gnome-shell, mutter-dev-bin, dbus-daemon; active desktop.
# @return Exit status from installation or the nested debug session.
# @retval 1 Missing graphical session, executable or Devkit capability.
# @retval 2 Unexpected arguments.
# @satisfies PRJ-004, REQ-031, REQ-033, REQ-178, REQ-185, REQ-186

set -euo pipefail

full_path="$(readlink -f "$0")"
script_dir="$(dirname "$full_path")"
project_root="$(dirname "$script_dir")"

cd "$project_root"

if [ "$#" -ne 0 ]; then
    echo "[ERROR] Invoke scripts/test-gnome-extension.sh without arguments." >&2
    exit 2
fi

if [ -z "${WAYLAND_DISPLAY:-}" ] && [ -z "${DISPLAY:-}" ]; then
    echo "[ERROR] Run from an active graphical desktop session." >&2
    exit 1
fi

if ! command -v gnome-shell dbus-run-session >/dev/null; then
    echo "[ERROR] Install gnome-shell and dbus-daemon before launching." >&2
    exit 1
fi

if [ ! -x /usr/libexec/mutter-devkit ]; then
    echo "[ERROR] Missing Mutter Devkit; on Ubuntu 26.04 run: sudo apt install mutter-dev-bin" >&2
    exit 1
fi

if ! gnome-shell --help-all 2>/dev/null | grep -F -- --devkit >/dev/null; then
    echo "[ERROR] GNOME Shell lacks the windowed --devkit backend." >&2
    exit 1
fi

echo "Update installed version..."
scripts/aibar.sh gnome-install

echo "Starting windowed GNOME Shell Devkit; exit the debug shell to stop."
exec env MUTTER_DEBUG_DUMMY_MODE_SPECS=1280x720 dbus-run-session -- scripts/aibar-nested-debug-session.sh gnome-shell --devkit --wayland
