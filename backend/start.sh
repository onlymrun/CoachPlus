#!/bin/bash
# CoachPlus Backend Start Script
# Usage: ./start.sh [port]
# PORT env var from Render takes precedence, fallback to 8000
PORT="${PORT:-${1:-8000}}"
cd "$(dirname "$0")"
echo "Starting CoachPlus Backend on http://0.0.0.0:$PORT"
echo "API Docs: http://localhost:$PORT/docs"
echo ""
./venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port "$PORT"