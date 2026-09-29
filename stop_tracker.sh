#!/usr/bin/env bash
# ==============================================================================
# Stop SmartBMS Git Save Tracker
# ==============================================================================
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIDFILE="$DIR/tracker.pid"

if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Stopping Git Save Tracker (PID: $PID)..."
        kill "$PID"
        sleep 1
        if ps -p "$PID" > /dev/null 2>&1; then
            kill -9 "$PID"
        fi
        rm -f "$PIDFILE"
        echo "Git Save Tracker stopped."
    else
        echo "Tracker PID $PID was not running. Removing stale PID file."
        rm -f "$PIDFILE"
    fi
else
    # Fallback: check if git_tracker.py is running
    PID=$(pgrep -f "python3.*git_tracker.py")
    if [ -n "$PID" ]; then
        echo "Killing running tracker process PID $PID..."
        kill "$PID"
        echo "Stopped."
    else
        echo "Git Save Tracker is not running."
    fi
fi
