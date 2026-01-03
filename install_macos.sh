#!/bin/bash
# Install SovereignCore as a macOS launchd service

set -e

echo "🚀 Installing SovereignCore as a macOS background service..."
echo ""

# Configuration
PLIST_NAME="com.sovereigncore.api.plist"
SOURCE_PLIST="/Users/lordwilson/SovereignCore/$PLIST_NAME"
TARGET_DIR="$HOME/Library/LaunchAgents"
TARGET_PLIST="$TARGET_DIR/$PLIST_NAME"

# Create logs directory
mkdir -p /Users/lordwilson/SovereignCore/logs

# Check if source exists
if [ ! -f "$SOURCE_PLIST" ]; then
    echo "❌ Error: $SOURCE_PLIST not found."
    exit 1
fi

# Copy plist to LaunchAgents
echo "Creating $TARGET_DIR if it doesn't exist..."
mkdir -p "$TARGET_DIR"

echo "Installing $PLIST_NAME to $TARGET_DIR..."
cp "$SOURCE_PLIST" "$TARGET_PLIST"

# Load the service
echo "Loading service via launchctl..."
launchctl unload "$TARGET_PLIST" 2>/dev/null || true
launchctl load "$TARGET_PLIST"

echo ""
echo "✅ SovereignCore has been installed as a background service!"
echo ""
echo "Commands to manage the service:"
echo "  Start:   launchctl load $TARGET_PLIST"
echo "  Stop:    launchctl unload $TARGET_PLIST"
echo "  Status:  launchctl list | grep sovereign"
echo "  Logs:    tail -f /Users/lordwilson/SovereignCore/logs/launchd_stdout.log"
echo ""
echo "The API is now running in the background."
echo "Verify at: http://localhost:8528/health"
echo ""
