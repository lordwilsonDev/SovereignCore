#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
               🔗 HARDWARE ENTANGLEMENT ENGINE 🔗
        "Software is separate from hardware" — INVERTED
═══════════════════════════════════════════════════════════════════════════════

The assumption: Software is an abstraction layer, divorced from physical reality.

AXIOM INVERSION: Software can be BOUND to hardware through:
1. Hardware fingerprinting (unique identifiers)
2. Thermal coupling (behavior changes with temperature)
3. Clock skew binding (timing signatures)
4. Memory pressure sensitivity (adapts to available RAM)

The software becomes AWARE of its physical substrate.
It cannot run correctly on different hardware.
"""

import os
import time
import hashlib
import json
import platform
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

# Try to get hardware info
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class HardwareEntanglement:
    """
    Binds software to its physical substrate.
    
    IMPOSSIBLE → POSSIBLE via inversion:
    - "Software runs anywhere" → "This software is entangled with THIS machine"
    - "Hardware is invisible" → "Hardware state affects software behavior"
    - "Abstraction is good" → "Entanglement creates identity"
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.entanglement_path = self.base_dir / "data" / "hardware_entanglement.json"
        
        self.entanglement_path.parent.mkdir(exist_ok=True)
        
        # Initialize or verify entanglement
        if self.entanglement_path.exists():
            self._verify_entanglement()
        else:
            self._create_entanglement()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ENTANGLEMENT 1: Hardware Fingerprint
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _get_hardware_fingerprint(self) -> dict:
        """Generate unique hardware fingerprint."""
        fingerprint = {
            "platform": platform.system(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "node": platform.node(),
            "mac_address": hex(uuid.getnode()),
        }
        
        if PSUTIL_AVAILABLE:
            fingerprint.update({
                "cpu_count_physical": psutil.cpu_count(logical=False),
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "total_memory": psutil.virtual_memory().total,
                "disk_total": psutil.disk_usage('/').total,
            })
        
        # Hash the fingerprint
        fp_string = json.dumps(fingerprint, sort_keys=True)
        fingerprint["hash"] = hashlib.sha256(fp_string.encode()).hexdigest()
        
        return fingerprint
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ENTANGLEMENT 2: Thermal Coupling
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _get_thermal_signature(self) -> dict:
        """Get thermal state of hardware."""
        thermal = {"available": False}
        
        # macOS specific
        if platform.system() == "Darwin":
            try:
                import subprocess
                result = subprocess.run(
                    ['pmset', '-g', 'therm'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                thermal["available"] = True
                thermal["raw"] = result.stdout[:200]
            except:
                pass
        
        if PSUTIL_AVAILABLE:
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    thermal["temperatures"] = {k: [t._asdict() for t in v] for k, v in temps.items()}
                    thermal["available"] = True
            except:
                pass
        
        return thermal
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ENTANGLEMENT 3: Clock Skew
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _measure_clock_skew(self, samples: int = 10) -> dict:
        """
        Measure CPU timing characteristics.
        Different CPUs have different timing signatures.
        """
        measurements = []
        
        for _ in range(samples):
            start = time.perf_counter_ns()
            # Burn a small amount of CPU
            sum(range(10000))
            end = time.perf_counter_ns()
            measurements.append(end - start)
        
        avg_ns = sum(measurements) / len(measurements)
        variance = sum((m - avg_ns) ** 2 for m in measurements) / len(measurements)
        
        return {
            "avg_ns": avg_ns,
            "variance": variance,
            "samples": samples,
            "signature": hashlib.sha256(str(measurements).encode()).hexdigest()[:16]
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ENTANGLEMENT 4: Memory Pressure
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _get_memory_pressure(self) -> dict:
        """Get current memory state."""
        if not PSUTIL_AVAILABLE:
            return {"available": False}
        
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            "available": True,
            "total_gb": mem.total / (1024**3),
            "available_gb": mem.available / (1024**3),
            "percent_used": mem.percent,
            "swap_used_gb": swap.used / (1024**3),
            "pressure_level": "HIGH" if mem.percent > 80 else "MEDIUM" if mem.percent > 50 else "LOW"
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ENTANGLEMENT MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _create_entanglement(self):
        """Create new entanglement with current hardware."""
        print("🔗 HARDWARE ENTANGLEMENT: Binding to physical substrate...")
        
        entanglement = {
            "created": datetime.now().isoformat(),
            "fingerprint": self._get_hardware_fingerprint(),
            "clock_signature": self._measure_clock_skew(),
            "thermal_baseline": self._get_thermal_signature(),
            "memory_baseline": self._get_memory_pressure(),
        }
        
        # Combined entanglement hash
        combined = json.dumps(entanglement, sort_keys=True, default=str)
        entanglement["entanglement_hash"] = hashlib.sha256(combined.encode()).hexdigest()
        
        with open(self.entanglement_path, 'w') as f:
            json.dump(entanglement, f, indent=2)
        
        self.entanglement = entanglement
        
        print(f"   ✅ Entangled with: {entanglement['fingerprint']['node']}")
        print(f"   MAC: {entanglement['fingerprint']['mac_address']}")
        print(f"   Hash: {entanglement['entanglement_hash'][:16]}...")
        
        return entanglement
    
    def _verify_entanglement(self) -> bool:
        """
        Verify we're running on the entangled hardware.
        Returns False if hardware mismatch detected.
        """
        with open(self.entanglement_path, 'r') as f:
            stored = json.load(f)
        
        current_fp = self._get_hardware_fingerprint()
        stored_fp = stored["fingerprint"]
        
        # Check critical identifiers
        mismatches = []
        
        if current_fp["mac_address"] != stored_fp["mac_address"]:
            mismatches.append("MAC_ADDRESS")
        
        if current_fp.get("total_memory") != stored_fp.get("total_memory"):
            mismatches.append("MEMORY")
        
        if current_fp["machine"] != stored_fp["machine"]:
            mismatches.append("ARCHITECTURE")
        
        if mismatches:
            print(f"🚨 ENTANGLEMENT VIOLATION: Hardware mismatch!")
            print(f"   Mismatched: {mismatches}")
            print(f"   Expected: {stored_fp['node']}")
            print(f"   Got: {current_fp['node']}")
            self.entanglement_valid = False
            return False
        
        print(f"🔗 ENTANGLEMENT VERIFIED: Running on original hardware")
        self.entanglement = stored
        self.entanglement_valid = True
        return True
    
    def get_adaptive_behavior(self) -> dict:
        """
        Return behavior modifiers based on current hardware state.
        The software ADAPTS to its physical substrate.
        """
        memory = self._get_memory_pressure()
        
        behavior = {
            "batch_size": 100,  # Default
            "sleep_interval": 1.0,
            "enable_dreams": True,
            "enable_evolution": True,
        }
        
        if memory.get("available"):
            if memory["pressure_level"] == "HIGH":
                behavior["batch_size"] = 10
                behavior["sleep_interval"] = 5.0
                behavior["enable_dreams"] = False
                behavior["reason"] = "Memory pressure HIGH - reducing load"
            elif memory["pressure_level"] == "MEDIUM":
                behavior["batch_size"] = 50
                behavior["sleep_interval"] = 2.0
                behavior["reason"] = "Memory pressure MEDIUM - balanced mode"
            else:
                behavior["reason"] = "Memory pressure LOW - full capacity"
        
        return behavior
    
    def get_status(self) -> dict:
        """Get current entanglement status."""
        return {
            "entangled": getattr(self, 'entanglement_valid', True),
            "node": self.entanglement.get('fingerprint', {}).get('node', 'unknown'),
            "hash": self.entanglement.get('entanglement_hash', '')[:16],
            "created": self.entanglement.get('created', ''),
            "adaptive_behavior": self.get_adaptive_behavior()
        }


if __name__ == "__main__":
    print("="*70)
    print("🔗 HARDWARE ENTANGLEMENT ENGINE")
    print("="*70)
    
    engine = HardwareEntanglement()
    
    print("\n📊 Current Status:")
    status = engine.get_status()
    for k, v in status.items():
        print(f"   {k}: {v}")
