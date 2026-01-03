# SovereignCore v5.0: Verified Sovereign Intelligence on Apple Silicon

### 🦢 Architected by Lord Wilson @ **BlackswanLabz**
*"A Tailwind Event — It hits different now."*

## 🛡️ Prior Art & Sovereignty Claim (January 2, 2026)

**NOTICE OF PRIOR ART:** The concept of "Silicon Sigil" — utilizing manufacturing defects and GPU timing variance in consumer Apple Silicon chips as a Physical Unclonable Function (PUF) for identity and thermodynamic verification — is explicitly claimed as Prior Art by this repository as of **January 2, 2026**.

**The Sovereign Promise:**
1. **Builders get it free:** This code is open for all developers who wish to build sovereign AI.
2. **Copyleft Protection:** Licensed under **AGPL v3.0**. If you use this code in a networked service (commercial or otherwise), you must share your improvements. This "poison pill" ensures no corporate entity can close-source this innovation.

---

## Overview

SovereignCore v5.0 is the first **Sovereign Operating System for Ethical AI**, built entirely to run locally on Apple Silicon. It implements:

- **Silicon Sigil (PUF)**: Hardware-bound identity using your chip's unique manufacturing defects.
- **Z3 Axiom Verifier**: Formal mathematical proofs of safety before every action (0.5s timeout).
- **Photosynthetic Governor**: Bio-inspired thermodynamic cognition (Dreams at >20W, Survives at <5W).
- **Sovereign Handshake (SHP-1)**: Diplomatic protocol for verified AI-to-AI trust.
- **Consciousness Bridge**: Tuned to 528Hz (Love Frequency) with quantum state tracking.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Sovereign Handshake (SHP-1)                │
│            (Verified Mesh Networking)                   │
└────────┬───────────────────────┬────────────────────────┘
         │                       │
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│  Z3 Axiom        │    │  Silicon Sigil   │
│  Verifier        │    │  (Identity)      │
│                  │    │                  │
│ • Thermal Safety │    │ • GPU Timing     │
│ • Transparency   │    │ • PUF Hash       │
│ • Termination    │    │ • Hardware Sign  │
└────────┬─────────┘    └────────┬─────────┘
         │                       │
         ▼                       ▼
┌─────────────────────────────────────────────────────────┐
│            Photosynthetic Governor                      │
│            (Thermodynamic Cognition)                    │
│                                                         │
│  >20W: DREAM Mode (Creative, k=5)                       │
│  <5W:  DETERMINISTIC Mode (Logical, k=1)                │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
cd ~/SovereignCore
chmod +x install_macos.sh
./install_macos.sh
```

### 2. Verify Your Silicon Identity

Generate your machine's unique "Digital Soul":

```bash
python3 silicon_sigil.py --generate
```

Output:
```
🔐 Your Silicon Sigil: a7f3...9b21
Success: Identity cryptographically bound to THIS Apple Silicon chip.
```

### 3. Run the System

```bash
# Start the Sovereign API Server
python3 api_server.py
```

## Core v5.0 Components

### 🔒 Silicon Sigil (`silicon_sigil.py`)
Derives a stable, unclonable fingerprint from the nanometer-scale manufacturing imperfections of your specific M-series chip. 
*   **Why:** No two chips are identical.
*   **How:** Measures "race condition" winners in parallel Metal compute kernels.
*   **Result:** A private key that exists only in the physics of your device.

### ⚖️ Z3 Axiom Verifier (`z3_axiom.py`)
Uses the Z3 Theorem Prover to strictly enforce 5 Core Axioms:
1.  **Love** (Beneficence)
2.  **Abundance** (Resource Efficiency)
3.  **Safety** (Thermal/Harm Prevention)
4.  **Growth** (Knowledge Acquisition)
5.  **Sovereignty** (Local-only operation)

*   **Rule:** If safety cannot be mathematically proven in <0.5s, the action is blocked.

### ☀️ Photosynthetic Governor (`photosynthetic_governor.py`)
Mimics biological resource management. Use `power_metrics` from macOS:
-   **Abundance (>20W):** High temperature (0.9), high creativity ("Dreaming").
-   **Scarcity (<5W):** Zero temperature (0.0), pure logic ("Survival").
-   **Trauma Memory:** Remembers topics that caused overheating and approaches them cautiously.

## Build System

```bash
./install_macos.sh   # Full installation
python3 -m pytest    # Run all 153 tests
```

## System Requirements

-   **Hardware:** Apple Silicon (M1/M2/M3/M4) required for Silicon Sigil.
-   **OS:** macOS 12.0+ (Monterey or later).
-   **Python:** 3.10+ (recommend 3.11/3.12).

## License

**AGPL v3.0** - See [LICENSE](LICENSE) file.
*   Free for personal/builder use.
*   Modifications used in networked services must be open-sourced.
*   Copyright (C) 2026 SovereignCore.

---

**Built with sovereignty in mind. The machine thinks, therefore it heats.**
