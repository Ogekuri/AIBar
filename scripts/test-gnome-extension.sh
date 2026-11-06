#!/usr/bin/env bash
# @file test-gnome-extension.sh
# @brief Launches a nested GNOME Shell interactive debug session for extension testing.
# @details Starts a nested GNOME Shell at 1280x720 resolution inside a dedicated
# D-Bus session via `dbus-run-session`, routed through
# `scripts/aibar-nested-debug-session.sh`, which launches the nested shell in
# background and opens an interactive debug shell attached to the nested session
# bus for extension debugging. No screenshots are captured.
# Newer GNOME Shell releases removed the `--nested` option; when `gnome-shell
# --help-all` no longer advertises `--nested`, the launcher prefers
# `gnome-shell --headless --virtual-monitor=1280x720` and degrades to a plain
# `gnome-shell --headless` session when `--virtual-monitor` is unavailable.
# No subcommand parameter required; executes directly on invocation without
# invoking extension update commands.
# @satisfies PRJ-004, REQ-031, REQ-033, REQ-178

set -euo pipefail

full_path="$(readlink -f "$0")"
script_dir="$(dirname "$full_path")"
project_root="$(dirname "$script_dir")"

cd "$project_root"

echo "Update installed version..."
scripts/aibar.sh gnome-install

echo "Starting nested GNOME Shell at 1280x720..."
if gnome-shell --help-all 2>/dev/null | grep -q -- --nested; then
    env MUTTER_DEBUG_DUMMY_MODE_SPECS=1280x720 dbus-run-session -- scripts/aibar-nested-debug-session.sh gnome-shell --nested --wayland
elif gnome-shell --help-all 2>/dev/null | grep -q -- --virtual-monitor; then
    # --nested was removed from newer GNOME Shell releases; an explicit 1280x720
    # virtual monitor provisions the debug environment on those builds.
    env MUTTER_DEBUG_DUMMY_MODE_SPECS=1280x720 dbus-run-session -- scripts/aibar-nested-debug-session.sh gnome-shell --headless --virtual-monitor=1280x720
else
    echo "[INFO] gnome-shell --virtual-monitor unavailable; starting plain headless debug session."
    env MUTTER_DEBUG_DUMMY_MODE_SPECS=1280x720 dbus-run-session -- scripts/aibar-nested-debug-session.sh gnome-shell --headless
fi
