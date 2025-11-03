#!/bin/bash

# Sage Reports - Frontend Startup Script

echo "🎓 Starting Sage Reports Frontend..."
echo ""

# Navigate to script directory
cd "$(dirname "$0")/frontend"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 14 or higher."
    exit 1
fi

echo "✅ Node.js found: $(node --version)"

# Check if node_modules exists
if [ ! -d node_modules ]; then
    echo "📦 Installing frontend packages (this may take a minute)..."
    npm install
fi

echo ""
echo "🚀 Starting frontend..."
echo "   App will open at: http://localhost:3000"
echo "   Press Ctrl+C to stop"
echo ""

# Start the frontend
npm start

