#!/usr/bin/env bash
# @file test-gnome-extension.sh
# @brief Launches a nested GNOME Shell session for extension testing.
# @details Starts a nested GNOME Shell at 1024x800 resolution via
# `MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800 dbus-run-session -- gnome-shell --nested --wayland`.
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
env MUTTER_DEBUG_DUMMY_MODE_SPECS=1280x720 dbus-run-session -- gnome-shell --nested --wayland
