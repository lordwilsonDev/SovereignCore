#!/bin/bash
# SovereignCore v4.0 - Dependency Installation Script

set -e  # Exit on error

echo "====================================="
echo "SovereignCore v4.0 Dependency Check"
echo "====================================="
echo ""

# Check for Xcode Command Line Tools
echo "[1/4] Checking Xcode Command Line Tools..."
if xcode-select -p &> /dev/null; then
    echo "✅ Xcode Command Line Tools installed"
else
    echo "❌ Xcode Command Line Tools not found"
    echo "Installing..."
    xcode-select --install
    echo "Please complete the installation and run this script again"
    exit 1
fi

# Check for Homebrew
echo ""
echo "[2/4] Checking Homebrew..."
if command -v brew &> /dev/null; then
    echo "✅ Homebrew installed at: $(which brew)"
else
    echo "❌ Homebrew not found"
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for Apple Silicon
    if [[ $(uname -m) == 'arm64' ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
fi

# Check for CMake
echo ""
echo "[3/4] Checking CMake..."
if command -v cmake &> /dev/null; then
    echo "✅ CMake installed: $(cmake --version | head -n1)"
else
    echo "❌ CMake not found"
    echo "Installing CMake via Homebrew..."
    brew install cmake
    echo "✅ CMake installed"
fi

# Check for Python 3
echo ""
echo "[4/4] Checking Python 3..."
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 installed: $(python3 --version)"
else
    echo "❌ Python 3 not found"
    echo "Installing Python 3 via Homebrew..."
    brew install python3
fi

echo ""
echo "====================================="
echo "✅ All dependencies installed!"
echo "====================================="
echo ""
echo "Next steps:"
echo "1. Run: cd ~/SovereignCore"
echo "2. Run: ./build_all.sh"
echo ""
