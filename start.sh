#!/bin/bash
set -e

echo "=================================================="
echo "🚀 Starting HADRON AI++ Production Stack..."
echo "=================================================="

# Set ports
API_PORT=${HADRON_API_PORT:-5000}
PORT=${PORT:-5050}

echo "1. Launching HADRON Intelligence & Quantum API on port $API_PORT..."
python app.py &
API_PID=$!

echo "2. Launching HADRON Control Tower Executive Dashboard on port $PORT..."
export HADRON_API_URL="http://127.0.0.1:$API_PORT"

# Trap exit signals to kill background API cleanly
trap "kill $API_PID 2>/dev/null || true" EXIT

python control_tower_app.py
