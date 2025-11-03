# 🎓 Start Here - Sage Tutoring Reports

Welcome! Your AI-assisted tutoring report system is ready to set up.

## ⚡ Quick Setup (10 minutes)

### Step 1: Get an API Key

Choose one AI provider:

**OpenAI (GPT-4)** - Easiest to set up
- Go to: https://platform.openai.com/api-keys
- Create account and generate key

**OR**

**Anthropic (Claude)** - Best quality reports
- Go to: https://console.anthropic.com/
- Create account and generate key

### Step 2: Configure Your API Key

1. In this folder, find the file `.env.example`
2. Copy it and rename the copy to `.env`
3. Open `.env` in TextEdit or any text editor
4. Paste your API key:
   ```
   OPENAI_API_KEY=your-key-here
   AI_PROVIDER=openai
   ```
5. Save the file

### Step 3: Install & Run

Open Terminal and run these commands:

```bash
# Navigate to folder
cd "/Users/ellizabethshelton/Desktop/Sage/Sage Reports"

# Run setup (one time only)
./setup.sh

# Start backend (Terminal window 1)
./start_backend.sh

# In a NEW Terminal window, start frontend
./start_frontend.sh
```

The app will open automatically at http://localhost:3000

## 📚 What Next?

1. **Upload Sample Reports** (Settings page)
   - Upload as many past reports as you have (10-20+ recommended!)
   - **No limit** - the AI uses ALL of them to learn your style
   - More samples = better accuracy

2. **Add Students** (Students page)
   - Add student names, subjects, notes
   - **Important:** Add recurring schedules (e.g., "Mondays 4pm, Thursdays 6pm")

3. **Check Your Calendar** (Calendar page)
   - See your weekly schedule
   - Track which sessions need reports
   - Green = done, Yellow = upcoming, Red = missing

4. **Write Your First Report** (Dashboard → New Report)
   - Or click "Write Report" directly from Calendar
   - Fill in session details
   - Let AI generate the draft
   - Edit and save!

## 📖 Documentation

- `START_HERE.md` - You are here!
- `QUICK_START.md` - 5-minute setup guide
- `USER_GUIDE.md` - Complete manual with all features
- `CALENDAR_GUIDE.md` - How to use the calendar feature
- `README.md` - Technical overview

## ⚠️ Troubleshooting

**"Permission denied" when running scripts?**
```bash
chmod +x setup.sh start_backend.sh start_frontend.sh
```

**"AI Not Connected" in the app?**
- Check your `.env` file has the correct API key
- Restart the backend server

**Need Python or Node.js?**
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/

## 💡 Tips

- Keep both Terminal windows open while using the app
- Your data is saved in the `database/` folder
- Back up your database regularly
- The more sample reports you upload, the better the AI matches your style

---

**Ready to start? Run `./setup.sh` in Terminal!** 🚀

