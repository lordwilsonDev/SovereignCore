#!/bin/bash
# Check for CMake installation

echo "Checking for CMake..."

if command -v cmake &> /dev/null; then
    echo "✅ CMake found:"
    which cmake
    cmake --version
    exit 0
else
    echo "❌ CMake not found"
    
    # Check for Homebrew
    if command -v brew &> /dev/null; then
        echo "📦 Homebrew found. Installing CMake..."
        brew install cmake
        exit $?
    else
        echo "⚠️  Homebrew not found"
        echo "Please install CMake using one of these methods:"
        echo "1. Install Homebrew first, then run: brew install cmake"
        echo "   Homebrew install: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        echo "2. Download CMake directly from: https://cmake.org/download/"
        exit 1
    fi
fi
