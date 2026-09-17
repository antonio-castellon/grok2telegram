#!/bin/sh
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p data
if [ -f .venv/bin/activate ]; then
  . .venv/bin/activate
fi
nohup python -m bridge >>data/bridge.log 2>&1 &
echo $! >data/pid
echo "started pid=$(cat data/pid)"
# Bridge also flushes on boot; this second pass catches anything still queued
# if the process is slow to enter the poll loop.
sleep 1
python -m bridge.inbox_flush || true
