# 📅 Calendar Session Management - Implementation Plan

## 🎯 Goal
Make the calendar work like typical scheduling software: cancel sessions, reschedule/move sessions, add one-time sessions.

## ✅ What I've Built So Far

### **Backend (Complete):**
- ✅ Created `CalendarSession` model in database
- ✅ Table fields: student_id, session_date, duration, status, notes, is_one_time
- ✅ API endpoints:
  - `GET /api/calendar-sessions` - Get sessions for date range
  - `POST /api/calendar-sessions` - Add new session
  - `PUT /api/calendar-sessions/<id>` - Update session (reschedule, cancel)
  - `DELETE /api/calendar-sessions/<id>` - Delete session
- ✅ Database table created and ready

### **Frontend API (Complete):**
- ✅ Added API service methods
- ✅ Calendar component loads calendar sessions
- ✅ Handler functions for cancel/reschedule/add

## 🚧 What's Left To Build

### **Calendar UI Updates Needed:**

**1. Session Context Menu** (3-dot menu on each session)
Options:
- ✏️ Write Report
- 🔄 Reschedule
- ❌ Cancel Session
- 🗑️ Delete (for one-time sessions)

**2. "+ Add Session" Button** (on each day card)
- Click to add a one-time session for that day
- Opens modal with student/time selection

**3. Cancelled Sessions Display**
- Show cancelled sessions with strikethrough
- Gray background
- "Cancelled" badge

**4. Rescheduled Sessions**
- Show new date/time
- "Rescheduled" badge
- Link to original date

**5. Add Session Modal**
Fields:
- Student (dropdown)
- Time (time picker)
- Duration (dropdown: 0.5h - 3h)
- Notes (optional)

**6. Reschedule Modal**
Fields:
- New Date (date picker)
- New Time (time picker)
- Reason (optional notes)

## 🔄 How It Will Work

### **Current System:**
- Calendar shows recurring sessions from Student.recurring_schedule
- Just a visual display
- No actual session management

### **Enhanced System:**

**Recurring Schedule** (Student.recurring_schedule)
- "Mondays 4pm, Thursdays 6pm"
- Generates expected sessions for calendar view

**+**

**Calendar Sessions** (calendar_sessions table)
- Actual session records
- Can override recurring schedule
- Statuses: scheduled, cancelled, rescheduled

**=**

**Smart Calendar View:**
```
Monday, Oct 21
  Sarah - 4:00 PM (Geometry)
    [recurring, scheduled]
    [⋮ Menu: Write Report | Reschedule | Cancel]
  
  Mike - 5:00 PM (SAT Math) - CANCELLED
    [recurring, cancelled]
    [⋮ Menu: Uncancel | Delete]

Tuesday, Oct 22
  Jenny - 3:00 PM (Calculus) - ONE-TIME SESSION
    [one-time, scheduled]
    [⋮ Menu: Write Report | Reschedule | Delete]
    
  [+ Add Session]
```

## 📊 Session Priority Logic

For each day/time slot:

1. Check calendar_sessions table for specific date
   - If status='cancelled' → Show as cancelled
   - If status='rescheduled' → Don't show (moved to new date)
   - If is_one_time=true → Show as one-time session

2. Check recurring_schedule
   - If no override in calendar_sessions → Show as scheduled
   - If has override → Use override status

3. Merge and display

## 🎨 UI Design

### **Session Card:**
```
┌─────────────────────────────────┐
│ Sarah Smith         [⋮]         │
│ 🕐 4:00 PM                      │
│ Geometry                        │
│ ✓ Done / ! Missing / Pending    │
│ [Write Report]                  │
└─────────────────────────────────┘
```

### **Session Card with Menu Open:**
```
┌─────────────────────────────────┐
│ Sarah Smith         [⋮]         │
│ 🕐 4:00 PM      ┌──────────────┐│
│ Geometry        │✏️ Write Report││
│ ! Missing       │🔄 Reschedule  ││
│                 │❌ Cancel      ││
│                 └──────────────┘│
└─────────────────────────────────┘
```

### **Cancelled Session:**
```
┌─────────────────────────────────┐
│ Sarah Smith - CANCELLED    [⋮]  │
│ 🕐 4:00 PM (struck through)     │
│ Geometry                        │
│ [Uncancel]  [Delete Override]   │
└─────────────────────────────────┘
```

## 💾 Database Examples

### **Example 1: Cancel a recurring session**
```
Student: Sarah (recurring_schedule: "Mondays 4pm")
Action: Cancel Oct 21 session

calendar_sessions table:
  student_id: sarah_id
  session_date: 2025-10-21 16:00:00
  status: 'cancelled'
  is_one_time: false

Result: Oct 21 session shows as cancelled, 
        Oct 28 session still shows (recurring)
```

### **Example 2: Reschedule**
```
Action: Move Sarah's Monday 4pm to Tuesday 3pm

Step 1: Mark original as rescheduled
  status: 'rescheduled'
  session_date: 2025-10-21 16:00:00

Step 2: Create new session
  status: 'scheduled'
  session_date: 2025-10-22 15:00:00
  is_one_time: true

Result: Monday shows no session, 
        Tuesday shows rescheduled session
```

### **Example 3: Add one-time session**
```
Action: Add Jenny for Wednesday 2pm (not recurring)

calendar_sessions table:
  student_id: jenny_id
  session_date: 2025-10-23 14:00:00
  status: 'scheduled'
  is_one_time: true

Result: Wednesday shows one-time session
```

## 🚀 Next Steps

I've built the backend infrastructure. To complete the UI, I need to:

1. Update calendar rendering logic to merge recurring + actual sessions
2. Add 3-dot menu to each session card
3. Add "+ Add Session" button to each day
4. Create Add Session modal
5. Create Reschedule modal
6. Handle cancelled session display

**This is about 30-45 minutes of work. Should I continue implementing the full calendar management UI?**

Or would you prefer a simpler approach where you just add notes about cancellations to the recurring schedule?


