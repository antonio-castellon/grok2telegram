#!/bin/sh
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p data
if [ -f .venv/bin/activate ]; then
  . .venv/bin/activate
fi
# Clear a dead pid file so we never double-poll Telegram (409).
if [ -f data/pid ]; then
  OLD="$(cat data/pid)"
  if kill -0 "$OLD" 2>/dev/null; then
    echo "already up pid=$OLD"
    exit 0
  fi
  rm -f data/pid
fi
nohup python -m bridge >>data/bridge.log 2>&1 &
echo $! >data/pid
echo "started pid=$(cat data/pid)"
sleep 1
python -m bridge.inbox_flush || true
