# SovereignCore v4.0 - Quick Start Guide

## 🚀 Fast Track Installation

Open Terminal and run these commands:

```bash
# 1. Go to project directory
cd ~/SovereignCore

# 2. Make scripts executable
chmod +x *.sh *.py

# 3. Clone BitNet (required for inference)
git clone --recursive https://github.com/microsoft/BitNet

# 4. Build everything
make all

# 5. Test the system
python3 sovereign_v4.py status
```

## What Gets Built

### ✅ Swift Hardware Bridge
- Secure Enclave integration
- Thermal monitoring
- Hardware-rooted identity

### ✅ Metal GPU Scrubber  
- Memory sanitization
- Thermodynamic load generation
- "Proof of Heat" mechanism

### ✅ Python Orchestrator
- PRA-ToT governance
- Thermodynamic locking
- Component coordination

### ⏳ BitNet Engine (Optional)
- Requires: `make bitnet` (1-2 hours)
- Enables: AI inference capability

## Testing

### Test 1: Swift Bridge
```bash
./sovereign_bridge keygen
./sovereign_bridge telemetry
```

**Expected output:**
```json
{"status":"success","message":"Key generated or retrieved from SEP"}
{"state":"NOMINAL","cpu_temp":45.0,"thermal_pressure":0.0,"timestamp":...}
```

### Test 2: System Status
```bash
python3 sovereign_v4.py status
```

**Expected output:**
```
============================================================
SovereignCore v4.0 Status
============================================================

Components:
  Swift Bridge: ✅ .../sovereign_bridge
  BitNet Engine: ❌ .../libbitnet.dylib
  Metal Scrubber: ✅ .../scrubber.metallib
  Model File: ❌ .../bitnet_b1.58_3B.gguf

Identity:
  SEP Verified: ✅

Thermal State:
  State: NOMINAL
  Temperature: 45.0°C
  Pressure: 0.00

Governance:
  Risk Score: 0.000
  ToT Branching: k=5
```

### Test 3: Inference (Demo Mode)
```bash
python3 sovereign_v4.py infer --prompt "Analyze system security"
```

**Expected output:**
```
============================================================
Inference Request
============================================================
Prompt: Analyze system security

[3/3] Checking Thermodynamic State...
  State: NOMINAL
  CPU Temp: 45.0°C
  Thermal Pressure: 0.00

PRA-ToT Governance:
  Risk Score: 0.000
  Branching Factor: k=5

🧠 Executing inference with k=5 thought branches...
   [BitNet engine integration pending - requires model file]

🧹 Engaging Metal GPU Scrubber...
   Sanitizing residual thought vectors
   [Metal dispatch pending - requires pyobjc integration]
============================================================
```

## Build Times

| Component | Time | Disk Space |
|-----------|------|------------|
| Swift Bridge | 5 sec | 1 MB |
| Metal Scrubber | 3 sec | <1 MB |
| BitNet Engine | 1-2 hours | 5 GB |

## Minimum vs Full Installation

### Minimum (5 minutes)
```bash
make all
```
- Swift Bridge ✅
- Metal Scrubber ✅
- Python Orchestrator ✅
- Demonstrates governance without inference

### Full (2 hours)
```bash
make all
make bitnet
```
- Everything from minimum +
- BitNet inference engine ✅
- Requires model file for actual inference

## Common Issues

### Issue: "swiftc: command not found"
**Solution:**
```bash
xcode-select --install
```

### Issue: "xcrun: error: unable to find utility 'metal'"
**Solution:** Install Xcode Command Line Tools (same as above)

### Issue: "cmake: command not found"
**Solution:**
```bash
brew install cmake
```

### Issue: "brew: command not found"
**Solution:**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Issue: Git clone fails
**Solution:** Check internet connection, or clone without submodules:
```bash
git clone https://github.com/microsoft/BitNet
cd BitNet
git submodule update --init --recursive
```

## File Permissions

If you get "Permission denied" errors:

```bash
cd ~/SovereignCore
chmod +x *.sh
chmod +x sovereign_v4.py
```

## What's Next?

1. **System works without BitNet** - Demonstrates governance layer
2. **Build BitNet for inference** - Run `make bitnet`
3. **Get a model** - Place in `models/` directory
4. **Run full inference** - With all components active

## Architecture Overview

```
         Python Orchestrator (sovereign_v4.py)
                      |
        +-------------+-------------+
        |             |             |
   Swift Bridge   BitNet       Metal
   (Hardware)    (Inference)  (Security)
        |
   Secure Enclave
   Thermal Sensors
```

## Key Features

✅ **Thermodynamic Locking** - Uses heat as proof of computation  
✅ **PRA-ToT Governance** - Risk-based intelligence throttling  
✅ **Hardware Identity** - SEP-rooted cryptographic signing  
✅ **Memory Scrubbing** - GPU-based sanitization  
✅ **Local-First** - No cloud, no telemetry  

## Support

If something doesn't work:

1. Check `README.md` for detailed docs
2. Check `INSTALL.md` for troubleshooting
3. Run `make help` for build options
4. Review error messages carefully

---

**Ready to build? Run:**

```bash
cd ~/SovereignCore && chmod +x *.sh *.py && make all
```
