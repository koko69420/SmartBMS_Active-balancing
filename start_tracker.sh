#!/usr/bin/env bash
# ==============================================================================
# Start SmartBMS Git Save Tracker in Background
# ==============================================================================
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIDFILE="$DIR/tracker.pid"
LOGFILE="$DIR/tracker.log"

if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Git Save Tracker is already running with PID $PID."
        exit 0
    else
        rm -f "$PIDFILE"
    fi
fi

echo "Launching SmartBMS Git Save Tracker..."
nohup python3 "$DIR/git_tracker.py" > "$LOGFILE" 2>&1 &
PID=$!
echo "$PID" > "$PIDFILE"

sleep 1
if ps -p "$PID" > /dev/null 2>&1; then
    echo "Git Save Tracker started successfully (PID: $PID)."
    echo "Logs: tail -f $LOGFILE"
else
    echo "Failed to start tracker. Check $LOGFILE for errors."
    exit 1
fi
