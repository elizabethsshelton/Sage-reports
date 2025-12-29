#!/bin/bash

# Script to create a double-clickable app for Sage Reports

echo "🎓 Creating Sage Reports Desktop App..."
echo ""

# Get the project directory
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_NAME="Sage Reports"
APP_PATH="$HOME/Desktop/${APP_NAME}.app"

# Create the app bundle structure
mkdir -p "${APP_PATH}/Contents/MacOS"
mkdir -p "${APP_PATH}/Contents/Resources"

# Create the executable script
cat > "${APP_PATH}/Contents/MacOS/Sage Reports" << 'EOF'
#!/bin/bash

# Get the directory where this app is located
APP_DIR="$(dirname "$0")"
PROJECT_DIR="$(dirname "$(dirname "$APP_DIR")")/Sage Reports"

# Change to project directory
cd "$PROJECT_DIR" || exit 1

# Open a new Terminal window and run launch script
osascript <<APPLESCRIPT
tell application "Terminal"
    activate
    do script "cd \"$PROJECT_DIR\" && ./launch.sh"
end tell
APPLESCRIPT
EOF

# Make it executable
chmod +x "${APP_PATH}/Contents/MacOS/Sage Reports"

# Create Info.plist
cat > "${APP_PATH}/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Sage Reports</string>
    <key>CFBundleIdentifier</key>
    <string>com.sagereports.app</string>
    <key>CFBundleName</key>
    <string>Sage Reports</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
</dict>
</plist>
EOF

echo "✅ Created: ${APP_PATH}"
echo ""
echo "📱 You can now:"
echo "   1. Double-click 'Sage Reports.app' on your Desktop"
echo "   2. It will automatically start the app for you!"
echo ""
echo "💡 Tip: You can drag it to your Dock for even easier access!"

