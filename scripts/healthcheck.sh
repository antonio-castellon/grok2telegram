#!/bin/sh
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PIDFILE="$ROOT/data/pid"
need_start=0
if [ ! -f "$PIDFILE" ]; then
  need_start=1
else
  PID="$(cat "$PIDFILE")"
  if ! kill -0 "$PID" 2>/dev/null; then
    echo "down (stale pid $PID) — restarting"
    rm -f "$PIDFILE"
    need_start=1
  fi
fi
if [ "$need_start" -eq 1 ]; then
  "$ROOT/scripts/start.sh" || exit 1
  sleep 1
  if [ ! -f "$PIDFILE" ]; then
    echo "down (start failed)"
    exit 1
  fi
  PID="$(cat "$PIDFILE")"
  if ! kill -0 "$PID" 2>/dev/null; then
    echo "down (died after start)"
    exit 1
  fi
  echo "up pid=$PID (restarted)"
  exit 0
fi
echo "up pid=$(cat "$PIDFILE")"
exit 0
