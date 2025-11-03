#!/bin/bash

# Sage Reports - One-Time Setup Script

echo "================================================"
echo "🎓 Sage Tutoring Reports - Setup"
echo "================================================"
echo ""

# Navigate to script directory
cd "$(dirname "$0")"

# Check Python
echo "📋 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found."
    echo "   Please install Python 3.8+ from https://www.python.org/downloads/"
    exit 1
fi
echo "✅ Python found: $(python3 --version)"
echo ""

# Check Node.js
echo "📋 Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found."
    echo "   Please install Node.js 14+ from https://nodejs.org/"
    exit 1
fi
echo "✅ Node.js found: $(node --version)"
echo ""

# Install Python packages
echo "📦 Installing Python packages..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python packages"
    exit 1
fi
echo "✅ Python packages installed"
echo ""

# Install frontend packages
echo "📦 Installing frontend packages (this may take a minute)..."
cd frontend
npm install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install frontend packages"
    exit 1
fi
cd ..
echo "✅ Frontend packages installed"
echo ""

# Create database directory
if [ ! -d database ]; then
    echo "📁 Creating database directory..."
    mkdir database
fi

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  No .env file found"
    echo ""
    echo "Next steps:"
    echo "1. Copy .env.example to .env"
    echo "2. Add your OpenAI or Anthropic API key to .env"
    echo "3. Run ./start_backend.sh and ./start_frontend.sh"
    echo ""
    read -p "Would you like to create .env now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo "✅ Created .env file"
        echo "   Please edit .env and add your API key"
        echo ""
        read -p "Press Enter to open .env in default editor..."
        open .env
    fi
else
    echo "✅ .env file exists"
fi

echo ""
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Make sure your API key is in the .env file"
echo "2. Open TWO Terminal windows:"
echo "   Window 1: ./start_backend.sh"
echo "   Window 2: ./start_frontend.sh"
echo "3. The app will open at http://localhost:3000"
echo ""
echo "See QUICK_START.md for more details."
echo "================================================"

