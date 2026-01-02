#!/bin/bash
# Clone Microsoft BitNet repository

cd "$(dirname "$0")"

echo "====================================="
echo "Cloning Microsoft BitNet Repository"
echo "====================================="
echo ""

if [ -d "BitNet" ]; then
    echo "⚠️  BitNet directory already exists"
    echo "Do you want to remove it and re-clone? (y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        echo "Removing existing BitNet directory..."
        rm -rf BitNet
    else
        echo "Keeping existing BitNet directory"
        exit 0
    fi
fi

echo "Cloning BitNet repository..."
echo "This may take a few minutes..."
echo ""

git clone --recursive https://github.com/microsoft/BitNet

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ BitNet repository cloned successfully"
    echo ""
    echo "Repository location: $(pwd)/BitNet"
    echo ""
    echo "Next steps:"
    echo "  1. Run: make bitnet"
    echo "  2. This will compile the BitNet engine"
    echo ""
else
    echo ""
    echo "❌ Failed to clone BitNet repository"
    echo ""
    echo "Please check:"
    echo "  1. Internet connection"
    echo "  2. Git is installed (run: git --version)"
    echo "  3. GitHub is accessible"
    echo ""
    exit 1
fi
