# SovereignCore v4.0 - Installation Guide

## Step-by-Step Installation

### Step 1: Navigate to Project Directory

```bash
cd ~/SovereignCore
```

### Step 2: Make Scripts Executable

```bash
chmod +x *.sh
chmod +x sovereign_v4.py
```

### Step 3: Install Dependencies

```bash
./install_dependencies.sh
```

This will install:
- Xcode Command Line Tools
- Homebrew (if not already installed)
- CMake
- Python 3

### Step 4: Clone BitNet Repository

```bash
./clone_bitnet.sh
```

Or manually:
```bash
git clone --recursive https://github.com/microsoft/BitNet
```

### Step 5: Build All Components

```bash
make all
```

This builds:
- Swift Hardware Bridge
- Metal GPU Scrubber

### Step 6: Build BitNet Engine (Optional but Recommended)

```bash
make bitnet
```

**Note**: This takes 1-2 hours and requires ~5GB disk space.

### Step 7: Test the System

```bash
python3 sovereign_v4.py status
```

You should see:
- ✅ Swift Bridge compiled
- ✅ Metal Scrubber compiled
- ✅ SEP Verified
- Thermal state information

### Step 8: Run Test Inference

```bash
python3 sovereign_v4.py infer --prompt "Test the system"
```

## Quick Build (All-in-One)

If you want to build everything at once:

```bash
cd ~/SovereignCore
chmod +x *.sh sovereign_v4.py
./build_all.sh
```

## Manual Compilation

If you prefer to compile components individually:

### Swift Bridge
```bash
swiftc SovereignBridge.swift -o sovereign_bridge -O \
    -framework Foundation \
    -framework Security \
    -framework IOKit
```

### Metal Scrubber
```bash
xcrun -sdk macosx metal -c scrubber.metal -o scrubber.air
xcrun -sdk macosx metallib scrubber.air -o scrubber.metallib
```

### BitNet Engine
```bash
mkdir -p build_sovereign
cd build_sovereign
cmake ../BitNet \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_OSX_ARCHITECTURES=arm64 \
    -DBITNET_BUILD_SHARED_LIB=ON \
    -DACCELERATE=ON \
    -DCMAKE_C_FLAGS="-mcpu=apple-m1" \
    -DCMAKE_CXX_FLAGS="-mcpu=apple-m1"
make -j$(sysctl -n hw.logicalcpu)
cd ..
```

## Troubleshooting

### "Permission Denied" Errors

```bash
chmod +x *.sh sovereign_v4.py
```

### "Command Not Found: git"

```bash
xcode-select --install
```

### "Command Not Found: cmake"

```bash
brew install cmake
```

### "Command Not Found: brew"

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Swift Compilation Fails

Make sure Xcode Command Line Tools are installed:
```bash
xcode-select -p
```

If not installed:
```bash
xcode-select --install
```

### BitNet Clone Fails

Check internet connection and try:
```bash
git clone https://github.com/microsoft/BitNet
cd BitNet
git submodule update --init --recursive
```

## Verification

After installation, verify all components:

```bash
# Check files exist
ls -lh sovereign_bridge
ls -lh scrubber.metallib
ls -lh build_sovereign/libbitnet.dylib

# Test Swift bridge
./sovereign_bridge keygen
./sovereign_bridge telemetry

# Test Python orchestrator
python3 sovereign_v4.py status
```

## Next Steps

Once installed:

1. **Download a BitNet model** (if you want inference capability)
2. **Place model in** `models/` directory
3. **Run inference**: `python3 sovereign_v4.py infer --prompt "your prompt"`

## Getting Models

BitNet models are not yet widely available. You may need to:

1. Convert existing models to BitNet format
2. Wait for official BitNet model releases
3. Train your own BitNet model

For now, the system will work without models - it demonstrates the governance and security layers.
