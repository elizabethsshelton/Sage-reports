#!/bin/bash

# Sage Reports - Backend Startup Script

echo "🎓 Starting Sage Reports Backend..."
echo ""

# Navigate to script directory
cd "$(dirname "$0")"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please copy .env.example to .env and add your API key"
    echo ""
    read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
fi

# Check if database directory exists
if [ ! -d database ]; then
    echo "📁 Creating database directory..."
    mkdir database
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo ""
echo "🚀 Starting backend server..."
echo "   Server will run at: http://127.0.0.1:5000"
echo "   Press Ctrl+C to stop"
echo ""

# Start the backend
python3 backend/app.py
