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

# Open browser
echo "🌐 Opening Sage Reports in your browser..."
open http://localhost:3000

echo ""
echo "✅ Sage Reports is running!"
echo ""
echo "   🌐 Frontend: http://localhost:3000"
echo "   🔧 Backend:  http://127.0.0.1:5000"
echo ""
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







