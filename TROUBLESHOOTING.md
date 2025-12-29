# 🔧 Troubleshooting Guide

## ❌ "This site can't be reached" or "ERR_CONNECTION_REFUSED"

This means the servers aren't running yet. Here's how to fix it:

### ✅ Solution 1: Wait a Bit Longer

When you double-click "Launch Sage Reports.command":
1. A terminal window will open
2. **Wait 10-15 seconds** for servers to start
3. Then try opening `http://localhost:3000` in your browser

The servers need time to start up!

### ✅ Solution 2: Check if Servers Are Running

**Check if backend is running:**
- Look at the terminal window that opened
- You should see messages like "Starting backend server..."
- If you see errors, let me know what they say

**Check if frontend is running:**
- You should see "Starting frontend..." in the terminal
- Wait until you see "Sage Reports is running!"

### ✅ Solution 3: Manual Start (If Double-Click Doesn't Work)

1. **Open Terminal** (Cmd + Space, type "Terminal")
2. **Type this:**
   ```bash
   cd "/Users/elizabethshelton/Desktop/Sage/Sage Reports"
   ./launch.sh
   ```
3. **Wait** until you see "✅ Sage Reports is running!"
4. **Open your browser** to `http://localhost:3000`

### ✅ Solution 4: Check What's Running

**See if something is already running:**
```bash
cd "/Users/elizabethshelton/Desktop/Sage/Sage Reports"
./stop.sh
```
This stops any old servers that might be stuck.

Then try starting again:
```bash
./launch.sh
```

---

## ❓ Other Common Issues

### "Permission denied"

**Fix:**
```bash
cd "/Users/elizabethshelton/Desktop/Sage/Sage Reports"
chmod +x launch.sh
chmod +x "Launch Sage Reports.command"
```

### "Port already in use"

**Fix:**
```bash
cd "/Users/elizabethshelton/Desktop/Sage/Sage Reports"
./stop.sh
```
Then try starting again.

### Browser opens but page is blank

**Wait longer!** The servers need 10-15 seconds to fully start.

**Or manually go to:**
- `http://localhost:3000`

### Terminal window closes immediately

**This shouldn't happen**, but if it does:
- Use Solution 3 (Manual Start) above
- The terminal window needs to stay open for servers to run

---

## ✅ Quick Fix Checklist

1. ✅ Double-click "Launch Sage Reports.command"
2. ✅ Wait 10-15 seconds
3. ✅ Check terminal window - do you see "Sage Reports is running!"?
4. ✅ Open browser to `http://localhost:3000`
5. ✅ If still not working, try Manual Start (Solution 3)

---

## 💡 Pro Tip

**The terminal window MUST stay open!**
- Don't close the terminal window
- That's what keeps the servers running
- You can minimize it, but don't close it

**To stop the app:**
- Close the terminal window
- Or run: `./stop.sh`

---

## 🆘 Still Not Working?

If nothing works, try this step-by-step:

1. **Stop everything:**
   ```bash
   cd "/Users/elizabethshelton/Desktop/Sage/Sage Reports"
   ./stop.sh
   ```

2. **Start manually:**
   ```bash
   ./launch.sh
   ```

3. **Watch the terminal** - what messages do you see?
4. **Wait 15 seconds**
5. **Try browser:** `http://localhost:3000`

**If you see error messages**, copy them and let me know what they say!






