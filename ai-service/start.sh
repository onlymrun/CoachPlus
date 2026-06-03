#!/bin/bash
# Start the CoachPlus AI Analysis Service
# Usage: ./start.sh [port]
# PORT env var from Render takes precedence, fallback to 8080
# Set OPENAI_API_KEY in environment or .env for real AI analysis
PORT="${PORT:-${1:-8080}}"
DIR="$(cd "$(dirname "$0")" && pwd)"
# Activate virtual environment
source "$DIR/venv/bin/activate"
# Run the service
cd "$DIR"
python3 -m app.main