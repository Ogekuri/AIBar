#!/usr/bin/env bash
#
# claude_token_refresh.sh - Background helper to refresh Claude tokens
#
# Usage: ./claude_token_refresh.sh {start|stop|status|once|loop}
#
#   start  - Daemonize and run refresh loop in background
#   stop   - Stop the running daemon
#   status - Check if daemon is running
#   once   - Run a single refresh immediately
#   loop   - Run refresh loop forever (foreground)
#
# Environment:
#   XDG_CONFIG_HOME - Config directory (default: ~/.config)
#   AIBAR_CLAUDE_REFRESH_INTERVAL_SECONDS - Interval in seconds (default: 1800)

set -euo pipefail

# Configuration
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/aibar"
PID_FILE="$CONFIG_DIR/claude_token_refresh.pid"
LOG_FILE="$CONFIG_DIR/claude_token_refresh.log"
INTERVAL="${AIBAR_CLAUDE_REFRESH_INTERVAL_SECONDS:-1800}"
# Captures the selected subcommand (`once|loop|start|stop|status`) for mode-gated logic.
REFRESH_COMMAND="${1:-}"

# Ensure config directory exists
mkdir -p "$CONFIG_DIR"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Run a single refresh cycle
##
# @brief Execute a single token refresh cycle.
# @details Truncates LOG_FILE to zero bytes before writing any log entries, ensuring each
#   invocation (once mode) and each daemon iteration (loop mode) produces a standalone log
#   containing only entries from that cycle. Invokes `claude /usage` and `aibar login --provider
#   claude` when the respective commands are available on PATH. In `once` mode only, if
#   `claude /usage` fails with canonical OAuth-expired text (`Invalid or expired OAuth token`),
#   executes `claude setup-token` and retries `claude /usage` once before continuing.
# @retval 0 Always; individual command failures are logged as warnings, not fatal errors.
# @satisfies REQ-048
##
do_refresh() {
    > "$LOG_FILE"
    log "Starting token refresh cycle"
    
    if command -v claude >/dev/null 2>&1; then
        log "Running: claude /usage"
        local usage_output=""
        local usage_status=0
        usage_output="$(claude /usage 2>&1)" || usage_status=$?
        if [[ -n "$usage_output" ]]; then
            printf '%s\n' "$usage_output" >>"$LOG_FILE"
        fi
        if [[ "$usage_status" -ne 0 ]]; then
            log "Warning: claude /usage failed (exit_code=$usage_status)"
            if [[ "$REFRESH_COMMAND" == "once" ]] && [[ "$usage_output" == *"Invalid or expired OAuth token"* ]]; then
                log "Detected expired OAuth token in once mode"
                log "Running: claude setup-token"
                local setup_output=""
                local setup_status=0
                setup_output="$(claude setup-token 2>&1)" || setup_status=$?
                if [[ -n "$setup_output" ]]; then
                    printf '%s\n' "$setup_output" >>"$LOG_FILE"
                fi
                if [[ "$setup_status" -ne 0 ]]; then
                    log "Warning: claude setup-token failed (exit_code=$setup_status)"
                else
                    log "Running: claude /usage"
                    local retry_output=""
                    local retry_status=0
                    retry_output="$(claude /usage 2>&1)" || retry_status=$?
                    if [[ -n "$retry_output" ]]; then
                        printf '%s\n' "$retry_output" >>"$LOG_FILE"
                    fi
                    if [[ "$retry_status" -ne 0 ]]; then
                        log "Warning: claude /usage failed after setup-token (exit_code=$retry_status)"
                    fi
                fi
            fi
        fi
    else
        log "Warning: claude command not found"
    fi
    
    if command -v aibar >/dev/null 2>&1; then
        log "Running: aibar login --provider claude"
        aibar login --provider claude >>"$LOG_FILE" 2>&1 || log "Warning: aibar login failed"
    else
        log "Warning: aibar command not found"
    fi
    
    log "Token refresh cycle complete"
}

# Run refresh loop forever
run_loop() {
    log "Starting refresh loop (interval: ${INTERVAL}s)"
    while true; do
        do_refresh
        log "Sleeping for ${INTERVAL}s"
        sleep "$INTERVAL"
    done
}

# Check if process is running
is_running() {
    if [[ -f "$PID_FILE" ]]; then
        local pid
        pid=$(cat "$PID_FILE" 2>/dev/null) || return 1
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

# Start daemon
start_daemon() {
    if is_running; then
        log "Daemon already running (PID: $(cat "$PID_FILE"))"
        return 0
    fi
    
    log "Starting daemon"
    nohup "$0" loop >>"$LOG_FILE" 2>&1 &
    local pid=$!
    echo "$pid" >"$PID_FILE"
    log "Daemon started (PID: $pid)"
}

# Stop daemon
stop_daemon() {
    if ! is_running; then
        log "Daemon not running"
        rm -f "$PID_FILE"
        return 0
    fi
    
    local pid
    pid=$(cat "$PID_FILE")
    log "Stopping daemon (PID: $pid)"
    
    if kill "$pid" 2>/dev/null; then
        rm -f "$PID_FILE"
        log "Daemon stopped"
    else
        log "Failed to stop daemon"
        return 1
    fi
}

# Show status
show_status() {
    if is_running; then
        echo "Daemon is running (PID: $(cat "$PID_FILE"))"
        echo "Config directory: $CONFIG_DIR"
        echo "Log file: $LOG_FILE"
        echo "Refresh interval: ${INTERVAL}s"
    else
        echo "Daemon is not running"
        echo "Config directory: $CONFIG_DIR"
        echo "Log file: $LOG_FILE"
    fi
}

# Show usage
show_usage() {
    cat <<'EOF'
Usage: ./claude_token_refresh.sh {start|stop|status|once|loop}

Commands:
  start  - Daemonize and run refresh loop in background
  stop   - Stop the running daemon
  status - Check if daemon is running
  once   - Run a single refresh immediately
  loop   - Run refresh loop forever (foreground)

Environment Variables:
  XDG_CONFIG_HOME                           Config directory (default: ~/.config)
  AIBAR_CLAUDE_REFRESH_INTERVAL_SECONDS Interval in seconds (default: 1800)
EOF
}

# Main command dispatch
case "${1:-}" in
    start)
        start_daemon
        ;;
    stop)
        stop_daemon
        ;;
    status)
        show_status
        ;;
    once)
        do_refresh
        ;;
    loop)
        run_loop
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
