# 🖱️ Create a Desktop App - Super Simple!

You want to just **click something** to start Sage Reports? Here's how!

---

## ✅ Option 1: Double-Click File (Easiest!)

I've already created a file called **"Launch Sage Reports.command"** in your project folder.

### To Use It:

1. **Find the file** in your project folder:
   - It's called `Launch Sage Reports.command`
   - It has a terminal/script icon

2. **Double-click it!**
   - A terminal window will open
   - The app will start automatically
   - Your browser will open to the app

3. **That's it!** 🎉

### Make It Even Easier:

**Add to Desktop:**
- Right-click the file → "Make Alias"
- Drag the alias to your Desktop
- Now you can double-click it from Desktop!

**Add to Dock:**
- Drag the file to your Dock (the bar at the bottom)
- Now you can click it from your Dock anytime!

---

## ✅ Option 2: Create a Real App (Looks Professional!)

This creates an actual app icon you can click.

### Step-by-Step (Takes 2 minutes):

1. **Open Automator**
   - Press `Cmd + Space` (Spotlight search)
   - Type "Automator"
   - Press Enter

2. **Create New App**
   - Click "New Document"
   - Choose "Application"
   - Click "Choose"

3. **Add the Script**
   - In the left sidebar, search for "Run Shell Script"
   - Drag it to the right side (where it says "Drag actions or files here")

4. **Paste This Code:**
   ```bash
   cd "/Users/elizabethshelton/Desktop/Sage/Sage Reports"
   ./launch.sh
   ```

5. **Save the App**
   - Click "File" → "Save"
   - Name it: **"Sage Reports"**
   - Save it to your **Desktop**
   - Click "Save"

6. **Done!** 🎉
   - You now have a "Sage Reports" app on your Desktop
   - Just **double-click it** to start!

### Make It Even Better:

**Add to Dock:**
- Drag the "Sage Reports" app to your Dock
- Now it's always visible and one click away!

**Add Custom Icon (Optional):**
- Find an icon/image you like
- Right-click the app → "Get Info"
- Drag your icon image onto the small icon in the top-left
- Now it looks custom!

---

## ✅ Option 3: Bookmark (If App is Already Running)

If the app is already running, you can just bookmark it:

1. **Start the app** (using one of the methods above)
2. **Open your browser** to `http://localhost:3000`
3. **Bookmark it:**
   - Chrome: Click the star icon
   - Safari: Press `Cmd + D`
4. **Name it:** "Sage Reports"

**Now:** If the app is running, just click the bookmark!

---

## 🎯 Recommended Setup:

**Best for Daily Use:**

1. **Create the Automator app** (Option 2 above)
2. **Drag it to your Dock**
3. **Every morning:** Just click the Dock icon
4. **Browser opens automatically**
5. **Start working!**

---

## 🛑 To Stop the App:

**Easy Way:**
- Just close the terminal window that opened

**Or:**
- Open Terminal
- Type: `cd "/Users/elizabethshelton/Desktop/Sage/Sage Reports" && ./stop.sh`

---

## 💡 Pro Tip:

**Auto-start on Login (Optional):**

If you want it to start automatically when you turn on your Mac:

1. **System Settings** → **General** → **Login Items**
2. Click the **+** button
3. Find and add your "Sage Reports" app
4. Now it starts automatically when you log in!

---

## ✅ Quick Summary:

- **Easiest:** Double-click `Launch Sage Reports.command`
- **Best:** Create Automator app, add to Dock
- **Fastest:** Bookmark `http://localhost:3000` (if already running)

**You'll never need to open Cursor or Terminal again!** 🎉








