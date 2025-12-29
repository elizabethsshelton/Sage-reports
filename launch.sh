#!/bin/bash

# Sage Reports - One-Click Launcher
# Starts both backend and frontend, then opens the app in your browser

echo "🎓 Launching Sage Reports..."
echo ""

# Navigate to script directory
cd "$(dirname "$0")"

# Start backend in background
echo "🔧 Starting backend server..."
bash start_backend.sh > logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait a moment for backend to initialize
sleep 3

# Start frontend in background
echo "🎨 Starting frontend..."
bash start_frontend.sh > logs/frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
echo "⏳ Waiting for services to start..."
sleep 5

# Get local IP address for network access
LOCAL_IP=""
if command -v ipconfig &> /dev/null; then
    # macOS
    LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "")
elif command -v hostname &> /dev/null; then
    # Linux/Unix fallback
    LOCAL_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "")
fi

# Open browser
echo "🌐 Opening Sage Reports in your browser..."
open http://localhost:3000

echo ""
echo "✅ Sage Reports is running!"
echo ""
echo "   📱 Local access:"
echo "      🌐 Frontend: http://localhost:3000"
echo "      🔧 Backend:  http://127.0.0.1:5000"
echo ""

if [ ! -z "$LOCAL_IP" ]; then
    echo "   🌍 Network access (from other devices on your WiFi):"
    echo "      🌐 Frontend: http://$LOCAL_IP:3000"
    echo "      🔧 Backend:  http://$LOCAL_IP:5000"
    echo ""
    echo "   💡 To access from your phone/tablet:"
    echo "      1. Make sure your device is on the same WiFi network"
    echo "      2. Open a browser and go to: http://$LOCAL_IP:3000"
    echo ""
else
    echo "   💡 Network access enabled - check terminal output for your IP address"
    echo ""
fi

echo "   Backend PID:  $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "💡 To stop: Run './stop.sh' or close this terminal"
echo "   View logs: 'tail -f logs/backend.log' or 'tail -f logs/frontend.log'"
echo ""

# Save PIDs for stop script
echo $BACKEND_PID > logs/backend.pid
echo $FRONTEND_PID > logs/frontend.pid

# Keep script running (wait for user to Ctrl+C)
echo "Press Ctrl+C to stop all services..."
wait














