# 🌐 Network Access Guide

Your Sage Reports application can now be accessed from other devices on your network!

## 🎯 What This Means

**Before:** Only accessible from your Mac at `localhost:3000`

**Now:** Accessible from:
- ✅ Your Mac (localhost)
- ✅ Your iPhone/iPad (on same WiFi)
- ✅ Your other computers (on same WiFi)
- ✅ Any device on your local network

---

## 🚀 How to Use

### Step 1: Start the Application

Run the launch script as usual:

```bash
./launch.sh
```

### Step 2: Find Your Network IP Address

When the app starts, you'll see output like this:

```
✅ Sage Reports is running!

   📱 Local access:
      🌐 Frontend: http://localhost:3000
      🔧 Backend:  http://127.0.0.1:5000

   🌍 Network access (from other devices on your WiFi):
      🌐 Frontend: http://192.168.1.100:3000
      🔧 Backend:  http://192.168.1.100:5000

   💡 To access from your phone/tablet:
      1. Make sure your device is on the same WiFi network
      2. Open a browser and go to: http://192.168.1.100:3000
```

**Note:** Your IP address will be different (something like `192.168.1.xxx` or `10.0.0.xxx`)

### Step 3: Access from Other Devices

1. **Make sure your device is on the same WiFi network** as your Mac
2. **Open a web browser** on your device (Safari, Chrome, etc.)
3. **Type the network URL** shown in the terminal (e.g., `http://192.168.1.100:3000`)
4. **That's it!** The app should load

---

## 📱 Accessing from Your Phone

### iPhone/iPad

1. Make sure your iPhone is on the same WiFi as your Mac
2. Open Safari (or any browser)
3. Type the network URL (e.g., `http://192.168.1.100:3000`)
4. The app will load just like on your computer!

**Tip:** You can bookmark it for easy access later.

### Android

Same process:
1. Connect to the same WiFi network
2. Open Chrome or any browser
3. Type the network URL
4. Use the app!

---

## 🔍 Finding Your IP Address Manually

If you need to find your Mac's IP address manually:

### Method 1: Terminal Command

```bash
ipconfig getifaddr en0
```

Or try:
```bash
ipconfig getifaddr en1
```

### Method 2: System Settings

1. Open **System Settings** (or System Preferences on older macOS)
2. Go to **Network**
3. Select your WiFi connection
4. Your IP address will be shown (usually something like `192.168.1.xxx`)

---

## ⚠️ Important Notes

### Security

- **Local Network Only:** The app is only accessible on your local WiFi network
- **Not Public:** It's NOT accessible from the internet (only devices on your WiFi)
- **Same Network Required:** All devices must be on the same WiFi network

### Firewall

If you can't access from other devices:

1. **Check macOS Firewall:**
   - System Settings → Network → Firewall
   - Make sure it's not blocking the connections

2. **Allow Python/Node in Firewall:**
   - If prompted, allow Python and Node.js through the firewall

### IP Address Changes

- Your Mac's IP address might change if you:
  - Disconnect and reconnect to WiFi
  - Restart your router
  - Connect to a different WiFi network

- **Solution:** Just check the terminal output again for the new IP address

---

## 🛠️ Troubleshooting

### "Can't connect" from phone

**Check:**
1. ✅ Are both devices on the same WiFi network?
2. ✅ Is the app running on your Mac?
3. ✅ Did you use the correct IP address?
4. ✅ Is your Mac's firewall blocking connections?

**Try:**
- Restart the app: `./stop.sh` then `./launch.sh`
- Check the IP address again
- Make sure your phone's WiFi is connected (not using cellular data)

### IP address not showing

The launch script tries to detect your IP automatically. If it doesn't show:

1. Find it manually (see "Finding Your IP Address Manually" above)
2. Use that IP address with port 3000: `http://YOUR_IP:3000`

### App works on Mac but not on phone

**Common causes:**
- Different WiFi networks
- Firewall blocking connections
- Wrong IP address

**Solution:**
1. Verify both devices are on the same WiFi
2. Check macOS Firewall settings
3. Double-check the IP address in terminal output

---

## 🌍 Making It Accessible from Internet (Advanced)

**Current setup:** Only accessible on your local network (WiFi)

**If you want internet access** (access from anywhere):
- You'll need to deploy to a cloud service (Heroku, Railway, Render, etc.)
- This requires additional setup and may have costs
- Contact me if you want help with cloud deployment

---

## ✅ Quick Reference

**Local access (on your Mac):**
- Frontend: `http://localhost:3000`
- Backend: `http://127.0.0.1:5000`

**Network access (from other devices):**
- Frontend: `http://YOUR_IP:3000`
- Backend: `http://YOUR_IP:5000`

**To find YOUR_IP:**
```bash
ipconfig getifaddr en0
```

---

**Enjoy accessing your Sage Reports from any device on your network! 🎉**








