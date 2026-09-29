#!/usr/bin/env bash
# ==============================================================================
# Stop SmartBMS Git Save Tracker
# ==============================================================================
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIDFILE="$DIR/tracker.pid"

if command -v systemctl >/dev/null 2>&1 && systemctl --user status >/dev/null 2>&1; then
    echo "Stopping smartbms-tracker systemd service..."
    systemctl --user stop smartbms-tracker.service
fi

if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        kill "$PID" 2>/dev/null
    fi
    rm -f "$PIDFILE"
fi

pkill -f "python3.*git_tracker.py" 2>/dev/null

echo "SmartBMS Git Save Tracker stopped."
