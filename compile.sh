#!/bin/bash
# Quick compilation script

cd "$(dirname "$0")"

echo "Compiling Swift Bridge..."
swiftc SovereignBridge.swift -o sovereign_bridge -O \
    -framework Foundation \
    -framework Security \
    -framework IOKit

if [ $? -eq 0 ]; then
    echo "✅ Swift bridge compiled successfully"
    echo ""
    echo "Testing bridge..."
    ./sovereign_bridge keygen
    echo ""
    ./sovereign_bridge telemetry
else
    echo "❌ Compilation failed"
    exit 1
fi

echo ""
echo "Compiling Metal Scrubber..."
xcrun -sdk macosx metal -c scrubber.metal -o scrubber.air
xcrun -sdk macosx metallib scrubber.air -o scrubber.metallib

if [ $? -eq 0 ]; then
    echo "✅ Metal scrubber compiled successfully"
else
    echo "❌ Metal compilation failed"
    exit 1
fi

echo ""
echo "✅ All components compiled!"
echo ""
echo "Running system status..."
python3 sovereign_v4.py status
