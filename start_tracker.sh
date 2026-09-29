#!/usr/bin/env bash
# ==============================================================================
# Start SmartBMS Git Save Tracker (via systemd user service with standalone fallback)
# ==============================================================================
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGFILE="$DIR/tracker.log"

if command -v systemctl >/dev/null 2>&1 && systemctl --user status >/dev/null 2>&1; then
    echo "Starting smartbms-tracker via systemd user service..."
    systemctl --user start smartbms-tracker.service
    sleep 1
    systemctl --user status smartbms-tracker.service --no-pager
else
    PIDFILE="$DIR/tracker.pid"
    if [ -f "$PIDFILE" ]; then
        PID=$(cat "$PIDFILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Git Save Tracker is already running with PID $PID."
            exit 0
        fi
    fi
    echo "Launching SmartBMS Git Save Tracker in standalone background mode..."
    nohup python3 -u "$DIR/git_tracker.py" </dev/null >> "$LOGFILE" 2>&1 &
    PID=$!
    echo "$PID" > "$PIDFILE"
    echo "Git Save Tracker started (PID: $PID)."
fi
echo "Live logs: tail -f $LOGFILE"
