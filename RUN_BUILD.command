#!/bin/bash
# Double-clickable build script for macOS
# This opens Terminal and runs the build

cd "$(dirname "$0")"

# Make BUILD_NOW.sh executable
chmod +x BUILD_NOW.sh

# Run the build script
./BUILD_NOW.sh

# Keep terminal open
echo ""
echo "Press any key to close..."
read -n 1
