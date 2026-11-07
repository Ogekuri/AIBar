#!/usr/bin/env bash
# @file aibar-nested-debug-session.sh
# @brief Runs the nested GNOME Shell command and opens an interactive debug shell on its session bus.
# @details Launches the argv as the nested GNOME Shell command in background inside
# the dedicated D-Bus session created by `dbus-run-session`, waits a startup settle
# delay, prints extension inspection guidance, then starts an interactive debug
# shell sharing `DBUS_SESSION_BUS_ADDRESS` so inspection commands target the nested
# shell. On normal debug-shell exit the nested shell is terminated and the debug
# status is propagated. On SIGINT/SIGTERM the wrapper SIGKILLs every background job
# (debug shell and nested shell) and exits immediately, so control returns to the
# invoking terminal instead of a residual intermediate shell. When the nested
# GNOME Shell exits first (Devkit window closed via its X button), the wrapper
# reaps the first terminated job with `wait -n`, SIGKILLs the still-running
# debug shell, and exits with the nested-shell status so no interactive shell
# outlives the session. The debug shell runs
# in background with job control disabled (`+m`) so it stays in the wrapper's
# foreground process group and keyboard interrupts reach the wrapper for
# whole-session termination. Because bash assigns /dev/null as stdin to
# background commands when job control is off, the wrapper duplicates its own
# stdin onto file descriptor 3 and launches the debug shell with an explicit
# `<&3` redirection so terminal input reaches the interactive debug shell
# (fixes the instant-session-exit regression introduced by 260b3f0). No
# screenshots are captured.
# Time O(1) orchestration; space O(1); mutates child processes only.
# @param[in] ... GNOME Shell command with arguments to launch as the nested shell.
# @env AIBAR_NESTED_SETTLE_SECONDS Delay before the debug shell starts (default: 3).
# @return Exit status of the first terminated session job: debug-shell status on normal debug exit; nested-shell status when the Devkit window closes; 130 after SIGINT; 143 after SIGTERM.
# @retval 130 Session terminated by SIGINT (debug shell and nested shell killed).
# @retval 143 Session terminated by SIGTERM (debug shell and nested shell killed).
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

terminate_session() {
    trap - INT TERM
    for job_pid in $(jobs -p); do
        kill -KILL "$job_pid" 2>/dev/null || true
    done
    wait 2>/dev/null || true
    exit "$1"
}

trap 'terminate_session 130' INT
trap 'terminate_session 143' TERM
trap cleanup EXIT

sleep "$SETTLE_SECONDS"

echo "[INFO] Nested GNOME Shell running (pid: $shell_pid); interactive debug shell attached to the nested session bus."
echo "[INFO] Debug commands:"
echo "  gnome-extensions info aibar@aibar.panel"
echo "  gnome-extensions list --enabled"
echo "  aibar show --json --force"
echo "  aibar doctor"
echo "[INFO] Type 'exit' or press Ctrl+D or Ctrl+C to stop the nested debug session."

exec 3<&0
bash --noprofile --norc -i +m <&3 &
debug_pid=$!

wait -n
reaped_status=$?

exec 3<&-

if kill -0 "$debug_pid" 2>/dev/null && ! kill -0 "$shell_pid" 2>/dev/null; then
    kill -KILL "$debug_pid" 2>/dev/null || true
    wait "$debug_pid" 2>/dev/null || true
fi

debug_pid=""
cleanup
trap - INT TERM EXIT
exit "$reaped_status"
