#!/bin/bash

# Sage Reports - Double-Click Launcher
# This file can be double-clicked to launch the app

# Get the directory where this script is located
cd "$(dirname "$0")"
PROJECT_DIR="$(pwd)"

# Open a new Terminal window and run the launch script
# This keeps the window open so servers keep running
osascript <<EOF
tell application "Terminal"
    activate
    do script "cd '$PROJECT_DIR' && echo '🎓 Starting Sage Reports...' && ./launch.sh"
end tell
EOF

# Wait longer for servers to start (they need time)
echo "⏳ Waiting for servers to start (this may take 20-30 seconds)..."
sleep 20

# Check if servers are running before opening browser
for i in {1..10}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend is ready!"
        open http://localhost:3000
        exit 0
    fi
    echo "Still waiting... ($i/10)"
    sleep 2
done

# If we get here, servers might not be ready
echo "⚠️  Servers may still be starting. Please wait a bit longer, then open:"
echo "   http://localhost:3000"
open http://localhost:3000 2>/dev/null || echo "Please open http://localhost:3000 in your browser manually"
