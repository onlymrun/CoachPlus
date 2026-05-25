#!/bin/bash
# Start the CoachPlus AI Analysis Service
# Usage: ./start.sh [port]
# Set OPENAI_API_KEY in environment or .env for real AI analysis

PORT=${1:-8080}
DIR="$(cd "$(dirname "$0")" && pwd)"

# Activate virtual environment
source "$DIR/venv/bin/activate"

# Run the service
cd "$DIR"
python3 -m app.main