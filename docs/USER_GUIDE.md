# Sage Tutoring Reports - Complete User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Setting Up the AI](#setting-up-the-ai)
3. [Managing Students](#managing-students)
4. [Writing Reports](#writing-reports)
5. [Uploading Sample Reports](#uploading-sample-reports)
6. [Tips & Best Practices](#tips--best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### First-Time Setup

#### Step 1: Install Python
1. Check if Python is installed by opening Terminal and typing:
   ```bash
   python3 --version
   ```
2. If not installed, download from [python.org](https://www.python.org/downloads/)
3. Install Python 3.8 or higher

#### Step 2: Install Node.js
1. Check if Node.js is installed:
   ```bash
   node --version
   ```
2. If not installed, download from [nodejs.org](https://nodejs.org/)
3. Install the LTS (Long Term Support) version

#### Step 3: Install Dependencies

Open Terminal and navigate to your project folder:
```bash
cd "/Users/ellizabethshelton/Desktop/Sage/Sage Reports"
```

Install Python packages:
```bash
pip3 install -r requirements.txt
```

Install frontend packages:
```bash
cd frontend
npm install
cd ..
```

---

## Setting Up the AI

### Getting an API Key

You have two options for AI providers:

#### Option 1: OpenAI (GPT-4) - Recommended for beginners
1. Go to [https://platform.openai.com/signup](https://platform.openai.com/signup)
2. Create an account or sign in
3. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
4. Click "Create new secret key"
5. Copy the key (it starts with `sk-`)

#### Option 2: Anthropic (Claude) - Recommended for best quality
1. Go to [https://console.anthropic.com/](https://console.anthropic.com/)
2. Create an account
3. Navigate to API Keys
4. Create a new key
5. Copy the key

### Adding Your API Key

1. In your project folder, find the file called `.env.example`
2. Copy it and rename the copy to `.env` (just `.env`, no `.example`)
3. Open `.env` in any text editor
4. Add your API key:

For OpenAI:
```
OPENAI_API_KEY=sk-your-actual-key-here
AI_PROVIDER=openai
```

For Anthropic:
```
ANTHROPIC_API_KEY=your-actual-key-here
AI_PROVIDER=anthropic
```

5. Save the file

---

## Running the Application

### Starting the Backend Server

Open Terminal in your project folder:
```bash
cd "/Users/ellizabethshelton/Desktop/Sage/Sage Reports"
python3 backend/app.py
```

You should see:
```
🎓 Sage Tutoring Report System
📊 Server running at http://127.0.0.1:5000
🤖 AI Provider: openai
```

**Keep this Terminal window open!**

### Starting the Frontend

Open a **NEW** Terminal window:
```bash
cd "/Users/ellizabethshelton/Desktop/Sage/Sage Reports/frontend"
npm start
```

The app will automatically open in your browser at `http://localhost:3000`

---

## Managing Students

### Adding a New Student

1. Click **"Students"** in the navigation menu
2. Click **"Add Student"** button
3. Fill in the form:
   - **Name** (required): Student's full name
   - **Subject/Class**: e.g., "SAT Math", "AP Biology", "Algebra 2"
   - **Grade Level**: e.g., "11th Grade", "Junior"
   - **Parent Email**: For your records (not currently used for sending)
   - **Recurring Schedule**: e.g., "Mondays 4pm, Thursdays 6pm"
   - **Notes**: Important information to remember (learning style, goals, challenges, etc.)
4. Click **"Add Student"**

### Editing a Student

1. Go to the Students page
2. Find the student card
3. Click the pencil (Edit) icon
4. Update any information
5. Click **"Save Changes"**

### Marking a Student as Inactive

Instead of deleting students, you can mark them inactive:
1. Edit the student
2. Uncheck **"Active student"**
3. Save changes

Inactive students won't show up in the main list but their data is preserved.

---

## Writing Reports

### Creating a New Report

1. Click **"Reports"** → **"New Report"** (or the big button on the Dashboard)
2. Fill in the session details:

   **Student Information:**
   - Select the student from the dropdown
   - Choose the session date

   **Session Details:**
   - **Topics Covered** (required): List the main topics
     - Example: "Quadratic equations, completing the square, vertex form"
   
   - **What We Did** (required): Describe the activities
     - Example: "Reviewed homework problems from chapter 5, practiced 10 quadratic equations, worked through 3 sample test questions, discussed strategies for identifying equation type"
   
   - **Additional Notes** (optional): Observations, recommendations, areas to elaborate
     - Example: "Student showed improvement with factoring but still struggles with word problems. Very engaged today. Recommend reviewing chapter 6 before next session."

3. Click **"Generate Report with AI"**

The AI will:
- Use your sample reports to match your writing style
- Reference previous sessions with this student
- Create a professional, detailed report
- Include specific recommendations and next steps

### Editing the Generated Report

After generation, you'll be taken to the Edit page where you can:

1. **Review** the AI-generated content
2. **Edit** the report in the text area (the whole report is editable)
3. **Add** personal touches or specific details
4. **Compare** with the original AI version (shown on the left)
5. **Copy** the report to clipboard (Copy icon)
6. **Download** as a text file (Download icon)
7. **Save** your changes

### Report Status

Track your workflow with status labels:
- **Draft**: Report is being worked on
- **Reviewed**: Report is finalized and ready
- **Sent**: Report has been sent to parents

Change the status using the dropdown in the top-right when editing.

---

## Uploading Sample Reports

**This is the most important step for quality results!**

### Why Sample Reports Matter

The AI learns from your examples to:
- Match your tone and writing style
- Use similar structure and format
- Include the types of details you typically mention
- Write in a way that sounds like you

### How to Upload

1. Go to **"Settings"**
2. In the "Sample Reports" section:
   - Click **"Upload Files"** to upload text files
   - Click **"Paste Text"** to paste report text directly

### What to Upload

**Best practices:**
- Upload **as many reports as you have!** There's no limit - 10, 20, 50+ reports all help
- The AI uses **ALL** your samples to learn (not just a few)
- More samples = more accurate style matching
- Include different types of sessions (strong, challenging, different subjects)
- Include reports for different students to capture variety in your writing
- Use complete reports (not fragments)

**File formats:**
- Plain text (.txt) works best
- Word documents (.doc, .docx) are supported
- You can also paste text directly

**Recommended:**
- Start with 10-20 reports minimum
- Add more over time as you write new ones
- The system automatically uses all samples when generating

### Example of a Good Sample Report

```
Session Report for Sarah Johnson
Date: March 15, 2024

Today's session focused on quadratic equations and graphing parabolas. We started by reviewing Sarah's homework from last week, where she had some excellent work on basic factoring problems. 

We then moved into more complex quadratic equations, particularly those requiring the quadratic formula. Sarah initially found the formula intimidating, but after working through several examples together, she began to see the pattern and gained confidence. By the end of the session, she was able to solve problems independently with minimal guidance.

For graphing, we covered how to identify the vertex, axis of symmetry, and direction of opening. Sarah did particularly well with vertex form equations and converting between forms.

Areas of strength:
- Quick to spot factoring opportunities
- Strong algebraic manipulation skills
- Asks clarifying questions when unsure

Areas for continued practice:
- Word problems involving quadratic equations
- Identifying which method to use (factoring vs. quadratic formula)
- Speed with calculations

Homework recommendation: Complete problems 15-25 in Chapter 8, focusing on the word problems. We'll review these at the start of our next session.

Sarah is making great progress and showing increased confidence with each session. Looking forward to continuing our work next week!
```

---

## Tips & Best Practices

### For Best AI Results

1. **Be Specific with Topics**
   - ❌ "Math stuff"
   - ✅ "Quadratic equations: factoring, completing the square, quadratic formula"

2. **Describe Activities in Detail**
   - ❌ "Did problems"
   - ✅ "Worked through 10 practice problems from the textbook, focusing on word problems. Reviewed homework corrections and discussed common mistakes."

3. **Include Observations in Notes**
   - Mention if the student struggled or excelled
   - Note engagement level
   - Include recommendations for practice
   - Reference upcoming tests or assignments

4. **Upload Quality Sample Reports**
   - Your actual reports work better than "idealized" examples
   - More samples = better style matching (but 3-5 is enough)

### Workflow Suggestions

**Weekly Routine:**
1. Keep brief notes during each session
2. At the end of the day/week, batch write reports
3. For each session:
   - Fill in the form (5 minutes)
   - Let AI generate the draft (30 seconds)
   - Review and edit (2-3 minutes)
   - Save and mark as "Reviewed"

**Monthly Maintenance:**
1. Review inactive students
2. Update student notes with ongoing observations
3. Check that sample reports still represent your style
4. Back up your database (copy the `database/` folder)

---

## Troubleshooting

### "AI Not Connected" Error

**Problem:** Red "AI Offline" indicator in the header

**Solutions:**
1. Check your `.env` file exists (not `.env.example`)
2. Verify your API key is correct (no extra spaces)
3. Make sure you set `AI_PROVIDER=openai` or `AI_PROVIDER=anthropic`
4. Restart the backend server
5. Check your OpenAI/Anthropic account has credits

### App Won't Start

**Problem:** Error messages when running `python3 backend/app.py`

**Solutions:**
1. Make sure you're in the correct directory
2. Reinstall dependencies: `pip3 install -r requirements.txt`
3. Check Python version: `python3 --version` (need 3.8+)
4. Try: `python backend/app.py` instead of `python3`

**Problem:** Error messages when running `npm start`

**Solutions:**
1. Make sure you're in the `frontend` directory
2. Delete `node_modules` and reinstall: 
   ```bash
   rm -rf node_modules
   npm install
   ```
3. Check Node version: `node --version` (need 14+)

### Database Issues

**Problem:** Data disappeared or database errors

**Solutions:**
1. Check that `database/sage_reports.db` exists
2. Don't delete or move the database file
3. To start fresh, rename the database file (it will create a new one)
4. To restore, copy your backup database file back

### Report Generation is Slow

**Normal:** First request can take 5-10 seconds
**If longer:** Check your internet connection (AI calls require internet)

### Generated Reports Don't Match My Style

**Solutions:**
1. Upload more sample reports (minimum 3, ideally 5)
2. Make sure sample reports are complete and representative
3. In the Edit page, compare with your samples and adjust
4. After a few edits, the AI learns your preferences

---

## Keyboard Shortcuts

### General
- `Cmd + Click` on any link: Open in new tab

### In Report Editor
- `Cmd + A`: Select all text
- `Cmd + C`: Copy selected text
- `Cmd + V`: Paste
- `Cmd + Z`: Undo
- `Cmd + Shift + Z`: Redo

---

## Data and Privacy

### Where is Data Stored?

- **Locally**: All student and report data is stored in `database/sage_reports.db` on your computer
- **AI Provider**: Report content is sent to OpenAI/Anthropic for generation (per their privacy policies)
- **Not stored elsewhere**: No data is sent to any other servers

### Backing Up Your Data

**Recommended:** Back up weekly

```bash
# Copy the database file
cp database/sage_reports.db database/backup_sage_reports_2024_01_15.db
```

Or simply copy the entire `database/` folder to another location.

### Exporting Reports

1. Open any report in Edit mode
2. Click the Download icon
3. Save the `.txt` file anywhere you want

---

## Getting Help

### Common Questions

**Q: Can I use this without internet?**
A: The app runs locally, but report generation requires internet (for AI API calls).

**Q: How much do API calls cost?**
A: OpenAI GPT-4: ~$0.01-0.03 per report. Anthropic Claude: ~$0.01-0.02 per report. Most users spend < $5/month.

**Q: Can I send reports directly to parents?**
A: Not currently. Copy the report and paste into your email client.

**Q: Can multiple people use this?**
A: Yes, but you'll need to share the database file or set up on a shared computer.

**Q: What if I want different writing styles for different types of reports?**
A: Use the Notes field to guide the AI (e.g., "Write this more formally" or "Keep this brief").

---

## Advanced Features (Coming Soon)

- Email integration to send reports directly
- Calendar sync to automatically create report templates
- Report templates for different session types
- Progress tracking and student analytics
- Export to PDF with formatting

---

## Support

For issues or questions:
1. Check this guide first
2. Review the Troubleshooting section
3. Check your console for error messages
4. Verify your .env file is configured correctly

---

**Happy Report Writing! 🎓**

