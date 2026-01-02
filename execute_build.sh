#!/bin/bash
# SovereignCore v4.0 - Automated Execution Script
# This script executes the build without user interaction for core components

set -e

cd "$(dirname "$0")"

echo "=========================================="
echo "SovereignCore v4.0 - Automated Build"
echo "=========================================="
echo ""

# Step 1: Clone BitNet
echo "[1/3] Cloning BitNet Repository..."
if [ ! -d "BitNet" ]; then
    git clone --recursive https://github.com/microsoft/BitNet
    echo "✅ BitNet cloned"
else
    echo "✅ BitNet already exists"
fi
echo ""

# Step 2: Compile Swift Bridge
echo "[2/3] Compiling Swift Hardware Bridge..."
swiftc SovereignBridge.swift \
    -o sovereign_bridge \
    -O \
    -framework Foundation \
    -framework Security \
    -framework IOKit
echo "✅ Swift bridge compiled: sovereign_bridge"
echo ""

# Step 3: Compile Metal Scrubber
echo "[3/3] Compiling Metal GPU Scrubber..."
xcrun -sdk macosx metal -c scrubber.metal -o scrubber.air
xcrun -sdk macosx metallib scrubber.air -o scrubber.metallib
echo "✅ Metal scrubber compiled: scrubber.metallib"
echo ""

echo "=========================================="
echo "✅ BUILD COMPLETE!"
echo "=========================================="
echo ""
echo "Built components:"
ls -lh sovereign_bridge scrubber.metallib 2>/dev/null || echo "Checking files..."
echo ""
echo "Next steps:"
echo "  1. Test: ./sovereign_bridge --test"
echo "  2. Run: python3 sovereign_v4.py"
echo "  3. Optional: make bitnet (for full engine)"
echo ""
