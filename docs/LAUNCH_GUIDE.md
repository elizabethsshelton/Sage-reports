# 🚀 How to Launch Sage Reports Daily

## **Option 1: One-Click Launch (Recommended!)** ⭐

### **Step 1: Test the Launcher**
Open Terminal and run:
```bash
cd "/Users/ellizabethshelton/Desktop/Sage/Sage Reports"
./launch.sh
```

This will:
- ✅ Start backend server
- ✅ Start frontend server
- ✅ Open browser to http://localhost:3000
- ✅ Show you the PIDs and logs

### **Step 2: Create Desktop Shortcut (macOS)**

**Method A: Create App Launcher (Double-Click to Open)**

1. Open **Automator** (search in Spotlight)
2. Click **"New Document"**
3. Select **"Application"**
4. Search for **"Run Shell Script"** and drag it to the workflow
5. Paste this script:
   ```bash
   cd "/Users/ellizabethshelton/Desktop/Sage/Sage Reports"
   ./launch.sh
   ```
6. **File → Save** as **"Launch Sage Reports"**
7. Save to Desktop or Applications folder
8. **Double-click the app** to launch!

**Method B: Create Alias in Terminal**

Add to your `~/.zshrc` file:
```bash
alias sage='cd "/Users/ellizabethshelton/Desktop/Sage/Sage Reports" && ./launch.sh'
```

Then just type `sage` in any terminal window!

---

## **Option 2: Terminal Commands**

### **Start Everything:**
```bash
cd "/Users/ellizabethshelton/Desktop/Sage/Sage Reports"
./launch.sh
```

### **Stop Everything:**
```bash
cd "/Users/ellizabethshelton/Desktop/Sage/Sage Reports"
./stop.sh
```

### **View Logs:**
```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log
```

---

## **Option 3: Manual Start (If Needed)**

### **Terminal 1 - Backend:**
```bash
cd "/Users/ellizabethshelton/Desktop/Sage/Sage Reports"
bash start_backend.sh
```

### **Terminal 2 - Frontend:**
```bash
cd "/Users/ellizabethshelton/Desktop/Sage/Sage Reports"
bash start_frontend.sh
```

### **Open Browser:**
Visit: http://localhost:3000

---

## **Daily Workflow (Super Easy!)**

### **Morning:**
1. **Double-click** "Launch Sage Reports" app on Desktop
   - OR type `sage` in Terminal
   - OR run `./launch.sh`
2. Browser opens automatically
3. Start working! 🎓

### **End of Day:**
1. Run `./stop.sh` in Terminal
   - OR just close the terminal window
   - OR press Ctrl+C in the launch window

---

## **Troubleshooting**

### **If app doesn't start:**
```bash
# Check if already running
lsof -i :5000  # Backend
lsof -i :3000  # Frontend

# Kill if needed
./stop.sh
```

### **If browser doesn't open:**
Manually visit: http://localhost:3000

### **View what's happening:**
```bash
tail -f logs/backend.log
tail -f logs/frontend.log
```

---

## **Files Created:**

- ✅ `launch.sh` - Starts everything, opens browser
- ✅ `stop.sh` - Stops everything cleanly
- ✅ `logs/` directory - Stores log files
- ✅ Scripts are executable (chmod +x already applied)

---

## **Recommended Setup for Daily Use:**

### **Create Desktop App (5 minutes):**

1. Open **Automator**
2. New → **Application**
3. Add **Run Shell Script**
4. Paste:
   ```bash
   cd "/Users/ellizabethshelton/Desktop/Sage/Sage Reports"
   ./launch.sh
   
   # Keep terminal open
   echo ""
   echo "Sage Reports is running!"
   echo "Close this window to stop the servers."
   read -p "Press Enter to stop..."
   ./stop.sh
   ```
5. Save as **"Sage Reports"** on Desktop
6. (Optional) Right-click → Get Info → drag custom icon

**Now you can:** Just double-click "Sage Reports" on your Desktop! 🎉

---

## **Alternative: Dock Shortcut**

Drag the "Sage Reports" app to your Dock for even easier access!

---

## **What Happens When You Launch:**

```
🎓 Launching Sage Reports...

🔧 Starting backend server...
🎨 Starting frontend...
⏳ Waiting for services to start...
🌐 Opening Sage Reports in your browser...

✅ Sage Reports is running!

   🌐 Frontend: http://localhost:3000
   🔧 Backend:  http://127.0.0.1:5000

💡 To stop: Run './stop.sh' or close this terminal
```

Browser opens automatically to your dashboard!

---

## **Super Quick Reference:**

**Start:** `./launch.sh` or double-click Desktop app  
**Stop:** `./stop.sh` or close terminal  
**URL:** http://localhost:3000  

**That's it!** 🚀






