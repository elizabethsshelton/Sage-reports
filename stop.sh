#!/bin/bash

# Sage Reports - Stop Script
# Stops both backend and frontend servers

echo "🛑 Stopping Sage Reports..."
echo ""

# Navigate to script directory
cd "$(dirname "$0")"

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if PID files exist
if [ -f logs/backend.pid ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    echo "Stopping backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || echo "  Backend already stopped"
    rm logs/backend.pid
else
    # Try to find and kill Flask process
    pkill -f "python backend/app.py" && echo "  Stopped backend" || echo "  No backend running"
fi

if [ -f logs/frontend.pid ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    echo "Stopping frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null || echo "  Frontend already stopped"
    rm logs/frontend.pid
else
    # Try to find and kill npm/vite process
    pkill -f "vite.*frontend" && echo "  Stopped frontend" || echo "  No frontend running"
fi

echo ""
echo "✅ Sage Reports stopped!"
echo ""














