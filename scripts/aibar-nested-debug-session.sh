#!/usr/bin/env bash
# @file aibar-nested-debug-session.sh
# @brief Runs the nested GNOME Shell command and opens an interactive debug shell on its session bus.
# @details Launches the argv as the nested GNOME Shell command in background inside
# the dedicated D-Bus session created by `dbus-run-session`, waits a startup settle
# delay, prints extension inspection guidance, then starts an interactive debug
# shell sharing `DBUS_SESSION_BUS_ADDRESS` so inspection commands target the nested
# shell. When the debug shell exits or SIGINT/SIGTERM arrives, the nested shell and
# the dedicated session are terminated. No screenshots are captured.
# @param[in] ... GNOME Shell command with arguments to launch as the nested shell.
# @env AIBAR_NESTED_SETTLE_SECONDS Delay before the debug shell starts (default: 3).
# @satisfies REQ-178, REQ-179, REQ-180, REQ-181, REQ-182

set -u

SETTLE_SECONDS="${AIBAR_NESTED_SETTLE_SECONDS:-3}"

if [ "$#" -eq 0 ]; then
    echo "[ERROR] No nested shell command provided." >&2
    exit 1
fi

"$@" &
shell_pid=$!

cleanup() {
    kill "$shell_pid" 2>/dev/null || true
    wait "$shell_pid" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

sleep "$SETTLE_SECONDS"

echo "[INFO] Nested GNOME Shell running (pid: $shell_pid); interactive debug shell attached to the nested session bus."
echo "[INFO] Debug commands:"
echo "  gnome-extensions info aibar@aibar.panel"
echo "  gnome-extensions list --enabled"
echo "  aibar show --json --force"
echo "  aibar doctor"
echo "[INFO] Type 'exit' or press Ctrl+D to stop the nested debug session."

bash --noprofile --norc -i
debug_status=$?

cleanup
trap - INT TERM EXIT
exit "$debug_status"
