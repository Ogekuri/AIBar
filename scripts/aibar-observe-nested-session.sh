#!/usr/bin/env bash
# @file aibar-observe-nested-session.sh
# @brief Launches a nested GNOME Shell command and captures observation snapshots.
# @details Executes the argv as the nested GNOME Shell command inside the current
# D-Bus session, captures periodic whole-screen PNG snapshots through the nested
# session `org.gnome.Shell.Screenshot.Screenshot` D-Bus API, prints each snapshot
# path, and terminates the shell on SIGINT or SIGTERM.
# @param[in] ... GNOME Shell command with arguments to launch as the nested shell.
# @env AIBAR_NESTED_SNAPSHOT_INTERVAL Seconds between snapshots (default: 5).
# @env AIBAR_NESTED_SETTLE_SECONDS Delay before the first snapshot (default: 3).
# @satisfies REQ-178, REQ-179, REQ-180, REQ-181, REQ-182

set -u

SNAPSHOT_DIR="${HOME}/.cache/aibar/nested-shell"
SNAPSHOT_FILE="${SNAPSHOT_DIR}/nested-shell-snapshot.png"
SNAPSHOT_INTERVAL="${AIBAR_NESTED_SNAPSHOT_INTERVAL:-5}"
SETTLE_SECONDS="${AIBAR_NESTED_SETTLE_SECONDS:-3}"

if [ "$#" -eq 0 ]; then
    echo "[ERROR] No nested shell command provided." >&2
    exit 1
fi

mkdir -p "$SNAPSHOT_DIR"

"$@" &
shell_pid=$!

cleanup() {
    kill "$shell_pid" 2>/dev/null || true
    wait "$shell_pid" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

echo "[INFO] Observation snapshots: $SNAPSHOT_FILE (interval: ${SNAPSHOT_INTERVAL}s)"
sleep "$SETTLE_SECONDS"

while kill -0 "$shell_pid" 2>/dev/null; do
    gdbus call \
        --session \
        --dest org.gnome.Shell \
        --object-path /org/gnome/Shell \
        --method org.gnome.Shell.Screenshot.Screenshot \
        true false "$SNAPSHOT_FILE" "" >/dev/null 2>&1 || true
    echo "[INFO] Observation snapshot saved: $SNAPSHOT_FILE"
    sleep "$SNAPSHOT_INTERVAL" 2>/dev/null || sleep 1
done

cleanup
trap - INT TERM EXIT
