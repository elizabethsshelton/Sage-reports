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

# Create virtual environment if it doesn't exist
echo "📦 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "   Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Verify we're using the venv Python
VENV_PYTHON=$(which python3)
if [[ "$VENV_PYTHON" != *"venv"* ]]; then
    echo "⚠️  Warning: Virtual environment may not be activated correctly"
    echo "   Python path: $VENV_PYTHON"
fi

# Install Python packages INTO the virtual environment
echo "📦 Installing Python packages (into virtual environment)..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python packages"
    deactivate 2>/dev/null
    exit 1
fi
echo "✅ Python packages installed into virtual environment"
echo ""

# Deactivate virtual environment (we'll reactivate it when running the app)
deactivate
echo "   Virtual environment deactivated (will be activated automatically when you run the app)"
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

