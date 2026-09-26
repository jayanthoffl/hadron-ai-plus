#!/bin/bash
set -e

echo "=================================================="
echo "🚀 Starting HADRON AI++ Production Stack..."
echo "=================================================="

# Ensure ports are strictly separated:
# Port 5000: Internal Quantum & Intelligence Engine
# Port 5050: Public Control Tower Executive Cockpit + Unified API
export HADRON_API_PORT=5000
export HADRON_API_URL="http://127.0.0.1:5000"
export PORT=${PORT:-5050}

# Avoid port collision if platform defaults PORT to 5000
if [ "$PORT" = "5000" ]; then
    export PORT=5050
fi

echo "1. Launching HADRON Intelligence & Quantum API on 0.0.0.0:${HADRON_API_PORT}..."
python app.py &
API_PID=$!

# Trap exit signals to terminate child background processes cleanly
trap "kill $API_PID 2>/dev/null || true" EXIT

echo "2. Launching HADRON Control Tower Executive Cockpit on 0.0.0.0:${PORT}..."
python control_tower_app.py
