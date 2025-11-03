# Minimal AI Editing & Save Draft Features

## Overview
Two new features have been added to the report creation workflow to give you more control over AI-generated reports.

## 1. Minimal AI Editing Mode

### What It Does
When enabled, the AI will **preserve your wording and structure** and only make light edits for:
- Grammar errors
- Spelling mistakes
- Awkward phrasing
- Clarity improvements

### What It Doesn't Do
- ❌ Rewrite sentences
- ❌ Change structure
- ❌ Add content you didn't mention
- ❌ Significantly alter your tone

### How to Use
1. Go to **New Report** page
2. Fill in session details with your notes
3. Check the **"Minimal AI Editing"** checkbox
4. Click **"Generate Report with AI"**
5. The AI will return a lightly polished version of your text

### When to Use This
- You've already written most of the report yourself
- You want to maintain your exact phrasing and voice
- You just need a quick grammar/clarity check
- You prefer more control over the final content

---

## 2. Enhanced AI Wording Priority

### What Changed
Even in **normal AI mode** (without minimal editing), the AI now prioritizes your wording when you provide structured notes:

- If your notes contain **3+ bullet points** or **multiple lines**, the AI treats them as the primary content
- Your wording becomes the foundation - the AI expands naturally while maintaining your voice
- Better respect for your original phrasing throughout the report

### This Means
- You can write brief bullet points and the AI will expand them
- Or write fuller paragraphs and the AI will refine them
- The more structure you provide, the more the AI follows your lead

---

## 3. Save Draft Feature

### What It Does
Save your session notes **without generating an AI report** - perfect for:
- Sessions you're not ready to write about yet
- Jotting down quick notes to expand later
- Coming back to finish a report when you have more time

### How to Use
1. Start a **New Report**
2. Fill in basic info (student, date, duration)
3. Add any notes you have so far
4. Click **"Save Draft"** instead of "Generate Report"
5. Find your draft in the **Reports** page with `draft` status
6. Click to edit and generate the AI report when ready

### Benefits
- No pressure to complete reports immediately after sessions
- Capture important details while they're fresh
- Return later to generate the full report

---

## UI Changes

### New Report Page
- **Checkbox:** "Minimal AI Editing - Use my wording - just fix grammar and clarity"
- **New Button:** "Save Draft" (left side, next to Cancel)
- **Existing Button:** "Generate Report with AI" (now supports minimal editing mode)

---

## Technical Details

### Backend
- New endpoint: `POST /api/reports` - Creates draft without AI
- Updated: `POST /api/reports/generate` - Now accepts `minimal_editing` flag
- AI service updated to handle two generation modes

### Frontend
- `NewReport.jsx` - Added checkbox, save draft button, and handlers
- `api.js` - New `createReport()` function

---

## Example Workflow

### Workflow 1: Minimal Editing
```
1. Fill in: "We worked on solving quadratic equations. Student struggled 
   with factoring but improved by end of session. Recommend more practice."

2. Check "Minimal AI Editing"

3. AI returns: "We worked on solving quadratic equations. The student 
   struggled with factoring but showed improvement by the end of the 
   session. I recommend additional practice."
   
   → Just grammar/clarity fixes, same structure
```

### Workflow 2: Save & Continue Later
```
1. Right after session: Fill in quick notes
   • Student: John Doe
   • Date: Today
   • Notes: "Worked on chapter 5, struggled with problem 12"

2. Click "Save Draft"

3. Later: Open from Reports page, add more details, generate with AI
```

---

## Summary

These features give you **flexible control** over the report creation process:

- **Minimal Editing**: When you want to write it yourself
- **Enhanced Priority**: When you want AI help but with your voice
- **Save Draft**: When you need time to think

Choose the workflow that fits each session! 🎓






