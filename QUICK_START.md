# 🚀 Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

You need:
- Python 3.8 or higher ([Download here](https://www.python.org/downloads/))
- Node.js 14 or higher ([Download here](https://nodejs.org/))

Check if installed:
```bash
python3 --version
node --version
```

## Step 1: Install Dependencies (One Time)

Open Terminal and run:

```bash
cd "/Users/ellizabethshelton/Desktop/Sage/sat_tex/Sage Reports"

# Install Python packages
pip3 install -r requirements.txt

# Install frontend packages
cd frontend
npm install
cd ..
```

## Step 2: Set Up AI (One Time)

### Get an API Key

**Option A - OpenAI (Easiest):**
1. Go to https://platform.openai.com/api-keys
2. Sign up/login and create a new key
3. Copy the key (starts with `sk-...`)

**Option B - Anthropic (Best Quality):**
1. Go to https://console.anthropic.com/
2. Sign up and create an API key
3. Copy the key

### Add Your Key

1. Copy `.env.example` and rename to `.env`
2. Open `.env` in a text editor
3. Paste your key:

```
# For OpenAI:
OPENAI_API_KEY=sk-your-key-here
AI_PROVIDER=openai

# OR for Anthropic:
ANTHROPIC_API_KEY=your-key-here
AI_PROVIDER=anthropic
```

4. Save and close

## Step 3: Start the App (Every Time)

### Terminal Window 1 - Backend:
```bash
cd "/Users/ellizabethshelton/Desktop/Sage/Sage Reports"
python3 backend/app.py
```

Keep this running! ✅

### Terminal Window 2 - Frontend:
```bash
cd "/Users/ellizabethshelton/Desktop/Sage/Sage Reports/frontend"
npm start
```

The app opens automatically at http://localhost:3000 🎉

## Step 4: First Time Setup in the App

1. **Upload Sample Reports**
   - Click "Settings"
   - Upload as many past reports as you have (10-20+ recommended)
   - **No limit!** The more samples, the better the AI learns your style
   - The AI uses ALL your uploaded samples

2. **Add Students**
   - Click "Students" → "Add Student"
   - Fill in student details
   - **Important:** Add "Recurring Schedule" (e.g., "Mondays 4pm, Thursdays 6pm")

3. **Check Your Calendar**
   - Click "Calendar" to see your weekly schedule
   - Sessions automatically appear based on student schedules
   - Green = report done, Yellow = upcoming, Red = missing report

4. **Write Your First Report**
   - Click "New Report" OR click "Write Report" from the Calendar
   - Fill in session details
   - Click "Generate Report with AI"
   - Edit and save!

## That's It! 🎓

You're ready to start writing reports.

### Quick Tips

- Keep both Terminal windows open while using the app
- To stop: Press `Ctrl + C` in each Terminal window
- Your data is saved in the `database/` folder
- Back up your database regularly

### Need Help?

See the complete [USER_GUIDE.md](USER_GUIDE.md) for detailed instructions and troubleshooting.

---

## Common Issues

**"AI Not Connected"**
- Check your `.env` file has the right API key
- Restart the backend server

**"Module not found" errors**
- Run `pip3 install -r requirements.txt` again
- Or in frontend: `npm install`

**Port already in use**
- Close any other apps using port 5000 or 3000
- Or restart your computer

---

**Happy Report Writing! 🎉**

