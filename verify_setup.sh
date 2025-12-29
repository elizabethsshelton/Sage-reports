#!/bin/bash

# Sage Reports - New Mac Setup Verification Script
# This script checks if your new Mac is properly set up to run the project

echo "================================================"
echo "🎓 Sage Reports - Setup Verification"
echo "================================================"
echo ""
echo "This script will verify your new Mac setup..."
echo ""

# Navigate to script directory
cd "$(dirname "$0")"
PROJECT_ROOT="$(pwd)"

# Track issues
ISSUES=0
WARNINGS=0

# ============================================
# CHECK XCODE COMMAND LINE TOOLS
# ============================================
echo "📋 Checking Xcode Command Line Tools..."
if xcode-select -p &> /dev/null; then
    echo "✅ Xcode Command Line Tools installed"
else
    echo "❌ Xcode Command Line Tools NOT found"
    echo "   Install by running: xcode-select --install"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# ============================================
# CHECK PYTHON
# ============================================
echo "📋 Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        echo "✅ Python found: $(python3 --version)"
    else
        echo "⚠️  Python version $PYTHON_VERSION found, but 3.8+ is required"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo "❌ Python 3 not found"
    echo "   Install from: https://www.python.org/downloads/"
    echo "   Or use Homebrew: brew install python@3.13"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# ============================================
# CHECK NODE.JS
# ============================================
echo "📋 Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version 2>&1 | sed 's/v//')
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)
    
    if [ "$NODE_MAJOR" -ge 14 ]; then
        echo "✅ Node.js found: $(node --version)"
    else
        echo "⚠️  Node.js version $NODE_VERSION found, but 14+ is required"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo "❌ Node.js not found"
    echo "   Install from: https://nodejs.org/"
    echo "   Or use Homebrew: brew install node"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# ============================================
# CHECK NPM
# ============================================
echo "📋 Checking npm..."
if command -v npm &> /dev/null; then
    echo "✅ npm found: $(npm --version)"
else
    echo "❌ npm not found (usually comes with Node.js)"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# ============================================
# CHECK PYTHON VIRTUAL ENVIRONMENT
# ============================================
echo "📋 Checking Python virtual environment..."
if [ -d "venv" ]; then
    if [ -f "venv/bin/activate" ]; then
        echo "✅ Virtual environment exists"
    else
        echo "⚠️  venv directory exists but appears incomplete"
        echo "   Recreate with: python3 -m venv venv"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo "⚠️  Virtual environment not found"
    echo "   Create with: python3 -m venv venv"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# ============================================
# CHECK PYTHON DEPENDENCIES
# ============================================
echo "📋 Checking Python dependencies..."
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    if pip list | grep -q flask; then
        echo "✅ Python dependencies appear to be installed"
    else
        echo "⚠️  Python dependencies not installed in venv"
        echo "   Install with: pip install -r requirements.txt"
        WARNINGS=$((WARNINGS + 1))
    fi
    deactivate 2>/dev/null
else
    echo "⚠️  Cannot check Python dependencies (venv not found)"
fi
echo ""

# ============================================
# CHECK NODE DEPENDENCIES
# ============================================
echo "📋 Checking Node.js dependencies..."
if [ -d "frontend/node_modules" ]; then
    echo "✅ Frontend dependencies appear to be installed"
else
    echo "⚠️  Frontend dependencies not installed"
    echo "   Install with: cd frontend && npm install"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# ============================================
# CHECK ENVIRONMENT FILE
# ============================================
echo "📋 Checking environment configuration..."
if [ -f ".env" ]; then
    if grep -q "OPENAI_API_KEY" .env && ! grep -q "your-openai-api-key-here" .env; then
        echo "✅ .env file exists and appears configured"
    else
        echo "⚠️  .env file exists but may need API key configuration"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo "⚠️  .env file not found"
    echo "   Create from template: cp env.example .env"
    echo "   Then edit .env and add your OpenAI API key"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# ============================================
# CHECK DATABASE DIRECTORY
# ============================================
echo "📋 Checking database directory..."
if [ -d "database" ]; then
    echo "✅ Database directory exists"
else
    echo "⚠️  Database directory not found (will be created automatically)"
fi
echo ""

# ============================================
# CHECK PROJECT STRUCTURE
# ============================================
echo "📋 Checking project structure..."
MISSING_FILES=0
for file in "backend/app.py" "frontend/package.json" "requirements.txt"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing file: $file"
        MISSING_FILES=$((MISSING_FILES + 1))
    fi
done

if [ $MISSING_FILES -eq 0 ]; then
    echo "✅ Project structure looks good"
else
    ISSUES=$((ISSUES + MISSING_FILES))
fi
echo ""

# ============================================
# SUMMARY
# ============================================
echo "================================================"
echo "📊 Verification Summary"
echo "================================================"

if [ $ISSUES -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ Everything looks good! Your Mac is ready to run Sage Reports."
    echo ""
    echo "Next steps:"
    echo "1. Make sure your API key is in .env"
    echo "2. Run: ./launch.sh"
    echo ""
    exit 0
elif [ $ISSUES -eq 0 ]; then
    echo "⚠️  Setup mostly complete, but there are $WARNINGS warning(s) above"
    echo "   Review the warnings and address them if needed"
    echo ""
    echo "To complete setup, run:"
    echo "  ./setup.sh"
    echo ""
    exit 0
else
    echo "❌ Found $ISSUES critical issue(s) that must be fixed"
    if [ $WARNINGS -gt 0 ]; then
        echo "⚠️  Also found $WARNINGS warning(s)"
    fi
    echo ""
    echo "Please fix the issues above and run this script again."
    echo ""
    
    # Provide installation guidance
    if ! command -v python3 &> /dev/null || ! command -v node &> /dev/null; then
        echo "Quick setup instructions:"
        echo ""
        echo "1. Install Homebrew (if not installed):"
        echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        echo ""
        echo "2. Install Python and Node.js:"
        echo "   brew install python@3.13 node"
        echo ""
        echo "3. Install Xcode Command Line Tools:"
        echo "   xcode-select --install"
        echo ""
        echo "4. Run setup script:"
        echo "   ./setup.sh"
        echo ""
    fi
    
    exit 1
fi



