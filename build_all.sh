#!/bin/bash
# SovereignCore v4.0 - Complete Build Script

set -e  # Exit on error

echo ""
echo "====================================="
echo "SovereignCore v4.0 - Complete Build"
echo "====================================="
echo ""

# Check we're in the right directory
if [ ! -f "Makefile" ]; then
    echo "❌ Error: Makefile not found"
    echo "Please run this script from the SovereignCore directory"
    exit 1
fi

# Step 1: Build Swift Bridge
echo "[1/3] Building Swift Hardware Bridge..."
make bridge
if [ $? -ne 0 ]; then
    echo "❌ Swift bridge build failed"
    exit 1
fi

# Step 2: Build Metal Scrubber
echo "[2/3] Building Metal GPU Scrubber..."
make scrubber
if [ $? -ne 0 ]; then
    echo "❌ Metal scrubber build failed"
    exit 1
fi

# Step 3: Check for BitNet (optional)
echo "[3/3] Checking BitNet Engine..."
if [ -d "BitNet" ]; then
    echo "BitNet repository found. Building..."
    make bitnet
    if [ $? -ne 0 ]; then
        echo "⚠️  BitNet build failed (non-fatal)"
        echo "You can continue without BitNet for now"
    fi
else
    echo "⚠️  BitNet repository not found"
    echo "To build BitNet engine:"
    echo "  1. git clone --recursive https://github.com/microsoft/BitNet"
    echo "  2. make bitnet"
    echo ""
fi

echo ""
echo "====================================="
echo "✅ Build Complete!"
echo "====================================="
echo ""
echo "Testing system..."
echo ""

# Test the build
python3 sovereign_v4.py status

echo ""
echo "Next steps:"
echo "  1. Review status output above"
echo "  2. If BitNet is missing, clone and build it"
echo "  3. Download a BitNet model to models/"
echo "  4. Run: python3 sovereign_v4.py infer --prompt 'test'"
echo ""
