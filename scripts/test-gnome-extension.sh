#!/usr/bin/env bash
# @file test-gnome-extension.sh
# @brief Launches a nested GNOME Shell session for extension testing.
# @details Starts a nested GNOME Shell at 1280x720 resolution via
# `MUTTER_DEBUG_DUMMY_MODE_SPECS=1280x720 dbus-run-session -- gnome-shell --nested --wayland`.
# Newer GNOME Shell releases removed the `--nested` option; when `gnome-shell
# --help-all` no longer advertises `--nested`, the launcher falls back to
# `gnome-shell --headless`, which starts the equivalent nested Wayland session
# whose dummy monitors honor `MUTTER_DEBUG_DUMMY_MODE_SPECS`.
# No subcommand parameter required; executes directly on invocation without
# invoking extension update commands.
# @satisfies PRJ-004, REQ-031, REQ-033

set -euo pipefail

full_path="$(readlink -f "$0")"
script_dir="$(dirname "$full_path")"
project_root="$(dirname "$script_dir")"

cd "$project_root"

echo "Update installed version..."
scripts/aibar.sh gnome-install

echo "Starting nested GNOME Shell at 1280x720..."
if gnome-shell --help-all 2>/dev/null | grep -q -- --nested; then
    env MUTTER_DEBUG_DUMMY_MODE_SPECS=1280x720 dbus-run-session -- gnome-shell --nested --wayland
else
    # --nested was removed from newer GNOME Shell releases; --headless starts
    # the equivalent Wayland session with dummy monitors at 1280x720.
    env MUTTER_DEBUG_DUMMY_MODE_SPECS=1280x720 dbus-run-session -- gnome-shell --headless
fi
