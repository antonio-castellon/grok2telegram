#!/bin/sh
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PIDFILE="$ROOT/data/pid"
if [ ! -f "$PIDFILE" ]; then
  echo "down (no pidfile)"
  exit 1
fi
PID="$(cat "$PIDFILE")"
if kill -0 "$PID" 2>/dev/null; then
  echo "up pid=$PID"
  exit 0
fi
echo "down (stale pid $PID)"
exit 1
