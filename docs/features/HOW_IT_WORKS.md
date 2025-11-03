# 🎓 How Sage Reports Works - Simple Guide

## 📊 Two Types of Reports

### **1. Regular Reports** (`/reports` page)
- All your tutoring session reports
- **Draft** = Still working on it, NOT used for training
- **Reviewed/Sent** = Finalized, USED for AI training ✅
- **All editable and deletable** - even finalized ones

### **2. Manual Sample Uploads** (Settings page)
- Historical reports you upload manually
- From LearnSpeed or past records
- Always used for AI training ✅
- View-only (not editable in main Reports view)

---

## ✅ **Key Point: NO DUPLICATES!**

**One report = One database record**

When you finalize a report:
- ❌ Does NOT create a copy
- ✅ Same report stays in `reports` table
- ✅ Status changes to "sent"
- ✅ AI now uses it for training

**Two separate tables:**
- `reports` table = Your active session reports (all statuses)
- `sample_reports` table = Manual uploads ONLY (external historical reports)

---

## 🧠 How AI Learns

### **AI Training Data Comes From:**

1. **Finalized reports** (from `reports` table)
   - Where status = "sent" or "reviewed"
   - ✅ Used for training
   
2. **Manual sample uploads** (from `sample_reports` table)
   - All manual uploads
   - ✅ Always used for training

3. **Draft reports** (from `reports` table)
   - Where status = "draft"
   - ❌ NOT used for training

### **Two Ways It Learns:**

**1. Writing Style** (from ALL training data)
- Your tone, voice, patterns
- How you structure reports
- Common phrases you use

**2. Student-Specific Context** (prioritized)
When generating for Student X:
- Looks for finalized reports for Student X (up to 3)
- Looks for manual uploads for Student X (up to 2)  
- Adds general reports for overall style (up to 5)
- = Smart mix of student-specific + your general style

---

## 🔄 Complete Workflow

### **Scenario: Generate Report for Sarah**

1. **Generate** (`/reports/new`)
   - Select Sarah + date
   - AI looks for Sarah's finalized reports + manual uploads
   - Creates draft

2. **Edit** (Edit page)
   - Review and refine
   - Make it perfect
   - Click "Save Changes" (still draft, not training yet)

3. **Finalize** (Edit page)
   - Click **"Finalize & Use for Training"** button
   - ✅ Saves
   - ✅ Changes status to "sent"
   - ✅ **NOW used for AI training!**
   - ✅ Still only ONE copy in database

4. **View Timeline** (Reports page)
   - See Sarah's draft reports (yellow "draft" badge)
   - See Sarah's finalized reports (green "sent" badge + blue "🎓 Used for Training")
   - See Sarah's manual uploads (orange "📚 Manual Sample")
   - **All merged in chronological order!**

5. **Next Report for Sarah**
   - AI uses the finalized report from step 3
   - Much smarter!

---

## 📋 Reports Page View

### **What You'll See:**

```
Sarah Smith  🟡 draft
   Oct 16, 2025 • Geometry • 1h
   Topics: Quadratic equations
   [Edit] [Delete]

Sarah Smith  🟢 sent  🎓 Used for Training
   Oct 15, 2025 • Geometry • 1h  
   Topics: Systems of equations
   [Edit] [Delete]

Sarah Smith  📚 Manual Sample  ✍️ Manual Upload
   Sep 10, 2025 • Geometry • 1h
   First session - angles and notation...
   [View-only]
```

**Filters:**
- **All Reports** - Everything merged (default)
- **Active Reports Only** - Just from `reports` table
- **Training Samples Only** - Just manual uploads
- **By Student** - One student's complete timeline
- **By Status** - Draft, Reviewed, Sent

---

## 📊 Database Tables Explained

### **`reports` Table**
```
Contains: ALL your session reports
Columns:
  - id, student_id, session_date
  - topics_covered, activities, notes
  - ai_generated_report, final_report
  - status (draft/reviewed/sent) ← Determines if used for training
  - created_at, updated_at

Training usage:
  - status = 'draft' → ❌ Not used
  - status = 'sent' or 'reviewed' → ✅ Used for training
```

### **`sample_reports` Table**
```
Contains: ONLY manual uploads (external historical reports)
Columns:
  - id, filename, content
  - student_name, session_date, subject
  - duration_hours, attendance_status
  - source (manual/file_upload)
  - uploaded_at

Training usage:
  - ✅ Always used (all records)
```

---

## 💡 Benefits

### **1. No Duplication**
- One report = one database record
- Clean, efficient database
- No confusion about which version is "real"

### **2. Everything Editable**
- Edit finalized reports if you need to fix something
- Delete any report
- Full control

### **3. Smart Training**
- AI learns from finalized reports only
- Quality control built-in
- Bad drafts don't pollute training data

### **4. Clear Visual Timeline**
- Reports page shows everything together
- Draft vs. Finalized clearly marked
- Manual samples distinguished
- Complete student history in one view

---

## 🎯 Quick Reference

| Action | Where | Result | Used for Training? |
|--------|-------|--------|-------------------|
| Generate new report | /reports/new | Draft in `reports` table | ❌ No (draft) |
| Save changes | Edit page | Still draft | ❌ No (draft) |
| Finalize report | Edit page (green button) | Status → "sent" | ✅ Yes! |
| Upload manual sample | Settings modal | Added to `sample_reports` | ✅ Yes! |
| Edit finalized report | Reports → Edit | Can change anytime | ✅ Still used |
| Delete any report | Reports → Delete | Removes from database | ❌ Gone |

---

## ✅ Summary

**Simple Architecture:**
- `reports` table = Your active work (editable, deletable)
  - Draft = not for training
  - Sent/Reviewed = used for training
- `sample_reports` table = Manual uploads only (external historical)
  - Always for training

**No Duplication:**
- One report = one record
- Status field determines if used for training
- Clean and simple!

**Visual Timeline:**
- Reports page merges both tables
- Shows complete student history
- Clear badges for draft/finalized/manual

**AI Gets Smarter:**
- Learns from finalized + manual samples
- Prioritizes student-specific reports
- Improves with every finalized report!

---

**That's it! Refresh your browser and check the Reports page - the duplicate is gone!** 🎉


