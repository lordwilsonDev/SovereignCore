#!/bin/bash
# SovereignCore v4.0 - Complete Build Script
# This script builds all components in the correct order

set -e  # Exit on any error

cd "$(dirname "$0")"

echo "=========================================="
echo "SovereignCore v4.0 - Complete Build"
echo "=========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Clone BitNet Repository
echo -e "${YELLOW}Step 1/5: Cloning BitNet Repository${NC}"
echo "----------------------------------------"
if [ ! -d "BitNet" ]; then
    echo "Cloning Microsoft BitNet repository..."
    git clone --recursive https://github.com/microsoft/BitNet
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ BitNet cloned successfully${NC}"
    else
        echo -e "${RED}❌ Failed to clone BitNet${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ BitNet directory already exists${NC}"
fi
echo ""

# Step 2: Compile Swift Bridge
echo -e "${YELLOW}Step 2/5: Compiling Swift Hardware Bridge${NC}"
echo "----------------------------------------"
if [ -f "SovereignBridge.swift" ]; then
    echo "Compiling Swift bridge..."
    swiftc SovereignBridge.swift \
        -o sovereign_bridge \
        -O \
        -framework Foundation \
        -framework Security \
        -framework IOKit
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Swift bridge compiled successfully${NC}"
        echo "   Output: sovereign_bridge"
    else
        echo -e "${RED}❌ Failed to compile Swift bridge${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ SovereignBridge.swift not found${NC}"
    exit 1
fi
echo ""

# Step 3: Compile Metal Scrubber
echo -e "${YELLOW}Step 3/5: Compiling Metal GPU Scrubber${NC}"
echo "----------------------------------------"
if [ -f "scrubber.metal" ]; then
    echo "Compiling Metal kernel to AIR..."
    xcrun -sdk macosx metal -c scrubber.metal -o scrubber.air
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Metal kernel compiled to AIR${NC}"
    else
        echo -e "${RED}❌ Failed to compile Metal kernel${NC}"
        exit 1
    fi
    
    echo "Linking AIR to metallib..."
    xcrun -sdk macosx metallib scrubber.air -o scrubber.metallib
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Metal library created successfully${NC}"
        echo "   Output: scrubber.metallib"
    else
        echo -e "${RED}❌ Failed to create Metal library${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ scrubber.metal not found${NC}"
    exit 1
fi
echo ""

# Step 4: Compile BitNet Engine (Optional - takes 1-2 hours)
echo -e "${YELLOW}Step 4/5: Compiling BitNet Engine (OPTIONAL)${NC}"
echo "----------------------------------------"
echo "⚠️  This step takes 1-2 hours and requires significant resources"
echo "Do you want to compile the BitNet engine now? (y/n)"
read -r response

if [ "$response" = "y" ]; then
    echo "Creating build directory..."
    mkdir -p build_sovereign
    cd build_sovereign
    
    echo "Configuring CMake..."
    cmake ../BitNet \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_OSX_ARCHITECTURES=arm64 \
        -DBITNET_BUILD_SHARED_LIB=ON \
        -DACCELERATE=ON \
        -DCMAKE_C_FLAGS="-mcpu=apple-m1" \
        -DCMAKE_CXX_FLAGS="-mcpu=apple-m1"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ CMake configuration successful${NC}"
    else
        echo -e "${RED}❌ CMake configuration failed${NC}"
        cd ..
        exit 1
    fi
    
    echo "Compiling BitNet (this will take a while)..."
    make -j$(sysctl -n hw.logicalcpu)
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ BitNet engine compiled successfully${NC}"
        echo "   Output: build_sovereign/libbitnet.dylib"
        cd ..
    else
        echo -e "${RED}❌ BitNet compilation failed${NC}"
        cd ..
        exit 1
    fi
else
    echo "Skipping BitNet compilation"
    echo "Note: You can compile it later with: make bitnet"
fi
echo ""

# Step 5: Verify Build
echo -e "${YELLOW}Step 5/5: Verifying Build${NC}"
echo "----------------------------------------"

ERRORS=0

if [ -f "sovereign_bridge" ]; then
    echo -e "${GREEN}✅ sovereign_bridge${NC}"
else
    echo -e "${RED}❌ sovereign_bridge missing${NC}"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "scrubber.metallib" ]; then
    echo -e "${GREEN}✅ scrubber.metallib${NC}"
else
    echo -e "${RED}❌ scrubber.metallib missing${NC}"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "sovereign_v4.py" ]; then
    echo -e "${GREEN}✅ sovereign_v4.py${NC}"
else
    echo -e "${RED}❌ sovereign_v4.py missing${NC}"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "build_sovereign/libbitnet.dylib" ]; then
    echo -e "${GREEN}✅ libbitnet.dylib${NC}"
else
    echo -e "${YELLOW}⚠️  libbitnet.dylib not compiled (optional)${NC}"
fi

echo ""
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}BUILD SUCCESSFUL!${NC}"
    echo "=========================================="
    echo ""
    echo "Core components ready:"
    echo "  • Swift Hardware Bridge: sovereign_bridge"
    echo "  • Metal GPU Scrubber: scrubber.metallib"
    echo "  • Python Orchestrator: sovereign_v4.py"
    echo ""
    echo "Next steps:"
    echo "  1. Test the Swift bridge:"
    echo "     ./sovereign_bridge --test"
    echo ""
    echo "  2. Run the system:"
    echo "     python3 sovereign_v4.py"
    echo ""
    echo "  3. (Optional) Compile BitNet engine:"
    echo "     make bitnet"
    echo ""
else
    echo -e "${RED}BUILD FAILED${NC}"
    echo "=========================================="
    echo ""
    echo "Please check the errors above and try again"
    exit 1
fi
