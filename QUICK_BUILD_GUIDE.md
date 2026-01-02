# SovereignCore v4.0 - Quick Build Guide

## 🚀 Fast Track Build (5 minutes)

Open Terminal and run:

```bash
cd ~/SovereignCore
chmod +x BUILD_NOW.sh
./BUILD_NOW.sh
```

This will:
1. ✅ Clone BitNet repository
2. ✅ Compile Swift Hardware Bridge
3. ✅ Compile Metal GPU Scrubber
4. ⚠️ Ask if you want to compile BitNet engine (optional, takes 1-2 hours)

## 📋 What Gets Built

### Core Components (Required)
- **sovereign_bridge** - Swift binary for SEP signing and thermal monitoring
- **scrubber.metallib** - Metal GPU kernels for memory scrubbing
- **sovereign_v4.py** - Python orchestrator (already created)

### Optional Component
- **libbitnet.dylib** - BitNet 1.58b inference engine (1-2 hour compile)

## 🧪 Testing After Build

### Test Swift Bridge
```bash
./sovereign_bridge --test
```

### Test Metal Scrubber
```bash
python3 -c "import subprocess; subprocess.run(['ls', '-lh', 'scrubber.metallib'])"
```

### Run Full System (without BitNet)
```bash
python3 sovereign_v4.py
```

## 🔧 Manual Build Steps

If you prefer to build components individually:

### 1. Clone BitNet
```bash
git clone --recursive https://github.com/microsoft/BitNet
```

### 2. Compile Swift Bridge
```bash
swiftc SovereignBridge.swift \
    -o sovereign_bridge \
    -O \
    -framework Foundation \
    -framework Security \
    -framework IOKit
```

### 3. Compile Metal Scrubber
```bash
xcrun -sdk macosx metal -c scrubber.metal -o scrubber.air
xcrun -sdk macosx metallib scrubber.air -o scrubber.metallib
```

### 4. Compile BitNet Engine (Optional)
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

## ✅ Verification

Check that files exist:
```bash
ls -lh sovereign_bridge scrubber.metallib sovereign_v4.py
```

Expected output:
```
-rwxr-xr-x  1 user  staff   XXK  sovereign_bridge
-rw-r--r--  1 user  staff   XXK  scrubber.metallib
-rw-r--r--  1 user  staff   XXK  sovereign_v4.py
```

## 🐛 Troubleshooting

### Swift Compilation Fails
- Ensure Xcode Command Line Tools installed: `xcode-select --install`
- Check Swift version: `swift --version`

### Metal Compilation Fails
- Verify Xcode is installed
- Check Metal compiler: `xcrun -sdk macosx metal --version`

### BitNet Clone Fails
- Check internet connection
- Verify Git installed: `git --version`
- Try manual clone: `git clone --recursive https://github.com/microsoft/BitNet`

### CMake Not Found
- Install via Homebrew: `brew install cmake`
- Or download from: https://cmake.org/download/

## 📊 Build Time Estimates

| Component | Time | Required |
|-----------|------|----------|
| BitNet Clone | 2-5 min | Yes |
| Swift Bridge | 10-30 sec | Yes |
| Metal Scrubber | 5-10 sec | Yes |
| BitNet Engine | 1-2 hours | Optional |

## 🎯 Next Steps After Build

1. **Test Components**: Run individual tests to verify each component
2. **Download Model**: Place BitNet model in `models/` directory
3. **Run System**: Execute `python3 sovereign_v4.py`
4. **Monitor Thermals**: Watch system temperature during inference

## 📝 Notes

- The BitNet engine compilation is **optional** for initial testing
- You can test the Swift bridge and Metal scrubber independently
- The Python orchestrator will run even without the BitNet engine (with warnings)
- Full functionality requires all components + a BitNet model file
