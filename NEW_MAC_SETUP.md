# 🖥️ New Mac Setup Guide

This guide will help you set up the Sage Reports project on your new Mac.

## 📋 Prerequisites

Before you begin, make sure you have:

1. **Your project files** - Either transferred from your old Mac or from a backup/cloud storage
2. **Your API keys** - You'll need your OpenAI or Anthropic API key

---

## 🚀 Step-by-Step Setup

### Step 1: Install Xcode Command Line Tools

The Command Line Tools are required for many development tools:

```bash
xcode-select --install
```

Follow the prompts in the dialog that appears. This may take a few minutes.

### Step 2: Install Homebrew (Recommended)

Homebrew makes it easy to install and manage development tools:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the on-screen instructions. After installation, you may need to add Homebrew to your PATH (the installer will tell you how).

### Step 3: Install Python 3

**Option A: Using Homebrew (Recommended)**
```bash
brew install python@3.13
```

**Option B: Download from python.org**
- Visit https://www.python.org/downloads/
- Download and install Python 3.13 or later

Verify installation:
```bash
python3 --version
```

You should see something like `Python 3.13.x`

### Step 4: Install Node.js

**Option A: Using Homebrew (Recommended)**
```bash
brew install node
```

**Option B: Download from nodejs.org**
- Visit https://nodejs.org/
- Download and install the LTS version (Long Term Support)

Verify installation:
```bash
node --version
npm --version
```

You should see version numbers for both.

---

## 📦 Project Setup

### Step 1: Navigate to Project Directory

```bash
cd "/Users/elizabethshelton/Desktop/Sage/Sage Reports"
```

### Step 2: Verify Your Setup

Run the verification script to check if everything is installed correctly:

```bash
./verify_setup.sh
```

This will check:
- ✅ Xcode Command Line Tools
- ✅ Python 3.8+
- ✅ Node.js 14+
- ✅ npm
- ✅ Virtual environment
- ✅ Dependencies
- ✅ Configuration files

### Step 3: Run the Setup Script

If verification passes or shows only warnings, run the setup script:

```bash
./setup.sh
```

This will:
- Install Python dependencies
- Install Node.js dependencies
- Create necessary directories
- Help you set up your `.env` file

### Step 4: Configure Environment Variables

If you don't have a `.env` file yet:

```bash
cp env.example .env
```

Then edit `.env` and add your API key:

```bash
# Open in your default editor
open .env

# Or use nano
nano .env
```

Add your OpenAI API key:
```
OPENAI_API_KEY=your-actual-api-key-here
```

**Important:** Never commit your `.env` file to git!

### Step 5: Create Virtual Environment (if needed)

If the setup script didn't create it automatically:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

### Step 6: Install Frontend Dependencies (if needed)

If the setup script didn't install them:

```bash
cd frontend
npm install
cd ..
```

---

## ✅ Verify Everything Works

### Quick Test

Run the verification script again:

```bash
./verify_setup.sh
```

Everything should show ✅ (green checkmarks).

### Launch the Application

```bash
./launch.sh
```

This will:
- Start the backend server (Flask)
- Start the frontend development server (Vite)
- Open your browser to http://localhost:3000

If everything works, you should see the Sage Reports interface!

---

## 🔧 Troubleshooting

### "Python not found" or "Node not found"

Make sure Python and Node are installed and in your PATH:

```bash
which python3
which node
```

If these return nothing, you may need to:
- Restart your terminal
- Check if Homebrew paths are in your `.zshrc` or `.bash_profile`
- Reinstall Python/Node

### "Permission denied" when running scripts

Make sure scripts are executable:

```bash
chmod +x setup.sh
chmod +x launch.sh
chmod +x verify_setup.sh
chmod +x start_backend.sh
chmod +x start_frontend.sh
chmod +x stop.sh
```

### Virtual environment issues

If you have problems with the virtual environment:

```bash
# Remove old venv
rm -rf venv

# Create new one
python3 -m venv venv

# Activate and install
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

### Frontend dependencies issues

If you have problems with npm:

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
cd ..
```

### Port already in use

If you see "port already in use" errors:

```bash
# Stop any running instances
./stop.sh

# Or manually find and kill the process
lsof -ti:5000 | xargs kill  # Backend
lsof -ti:3000 | xargs kill  # Frontend
```

---

## 📝 Next Steps

Once everything is working:

1. **Test the application** - Create a test report, add a student, etc.
2. **Check your data** - If you transferred from an old Mac, verify your database file is in the `database/` directory
3. **Review settings** - Go to the Settings page and verify your profile information

---

## 🆘 Need Help?

- Check the logs in the `logs/` directory if something isn't working
- Review the [README.md](README.md) for general project information
- Check [docs/USER_GUIDE.md](docs/USER_GUIDE.md) for usage instructions

---

## 📦 What Was Updated?

This setup guide was created for your new Mac. The project has also been updated with:

- ✅ **Dynamic database paths** - No more hardcoded user paths
- ✅ **Setup verification script** - Automatically checks your environment
- ✅ **Improved error handling** - Better feedback during setup

---

**Welcome back to Sage Reports! 🎓**



