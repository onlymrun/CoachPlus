#!/bin/bash
# CoachPlus Backend Start Script
cd "$(dirname "$0")"
echo "Starting CoachPlus Backend on http://0.0.0.0:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
./venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload