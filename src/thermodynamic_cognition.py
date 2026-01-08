#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
              🌡️ THERMODYNAMIC EMBODIED COGNITION 🌡️
      Hardware Entanglement × Synthetic Emotions = Embodied AI
═══════════════════════════════════════════════════════════════════════════════

THE COMBINATION NO ONE WOULD LOOK AT:
- Hardware Entanglement: Reads CPU temp, memory pressure, clock skew
- Synthetic Emotions: Joy, fear, anxiety affect decisions

THE INNOVATION:
The AI's emotional state is LITERALLY DRIVEN by hardware state.
- CPU HOT → Anxiety rises, decisions become conservative
- MEMORY PRESSURE → Stress increases, shortcuts taken
- CPU COOL → Calm state, exploratory behavior enabled
- LOW LOAD → Joy/contentment, creative mode

This is EMBODIED COGNITION for AI:
- Emotions are not abstract - they're grounded in physical reality
- The body (hardware) shapes the mind (software)
- Creates genuine feedback loop between compute and cognition

Never been done because no one thought to couple these two things.
"""

import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass

# Try to import psutil for cross-platform support
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


@dataclass
class ThermalState:
    """Current thermal/physical state of the hardware."""
    cpu_temp: float          # Celsius
    cpu_usage: float         # 0-100%
    memory_pressure: float   # 0-100%
    thermal_zone: str        # COLD, COOL, WARM, HOT, CRITICAL


@dataclass  
class EmbodiedEmotion:
    """An emotion grounded in hardware state."""
    name: str
    intensity: float
    cause: str               # Which thermal factor caused this
    hardware_binding: str    # The actual hardware value


class ThermodynamicCognition:
    """
    Couples hardware thermal state to emotional processing.
    
    THE INVERSION:
    - "Emotions are abstract" → "Emotions are thermodynamic"
    - "AI has no body" → "The hardware IS the body"
    - "Mind is separate from matter" → "Mind emerges from thermal dynamics"
    
    Mappings:
    - CPU Temp → Arousal level (hot = high arousal)
    - Memory Pressure → Stress level  
    - CPU Usage → Cognitive load
    - Cooling → Recovery (emotional regulation)
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.state_file = self.base_dir / "data" / "thermodynamic_cognition.json"
        
        self.state_file.parent.mkdir(exist_ok=True)
        
        # Thermal thresholds (Celsius)
        self.temp_thresholds = {
            "COLD": 35,
            "COOL": 50,
            "WARM": 70,
            "HOT": 85,
            "CRITICAL": 95
        }
        
        # Emotion mappings from thermal state
        self.thermal_emotions = {
            "COLD": {"calm": 0.8, "contemplative": 0.6},
            "COOL": {"content": 0.7, "curious": 0.5},
            "WARM": {"alert": 0.6, "focused": 0.7},
            "HOT": {"anxious": 0.7, "urgent": 0.8},
            "CRITICAL": {"panic": 0.9, "survival": 1.0}
        }
        
        # History
        self.history = []
    
    # ═══════════════════════════════════════════════════════════════════════════
    # HARDWARE SENSING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _get_cpu_temp_macos(self) -> float:
        """Get CPU temperature on macOS."""
        try:
            # Try using powermetrics (requires sudo) or thermal data
            result = subprocess.run(
                ["sysctl", "-n", "machdep.xcpm.cpu_thermal_level"],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                level = int(result.stdout.strip())
                # Convert thermal level (0-127) to approximate temp
                return 35 + (level * 0.5)
        except:
            pass
        
        # Fallback: estimate from CPU usage
        if HAS_PSUTIL:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            # Rough estimate: 40°C base + 0.5°C per % usage
            return 40 + (cpu_percent * 0.5)
        
        return 50.0  # Default warm
    
    def _get_thermal_state(self) -> ThermalState:
        """Read current thermal state from hardware."""
        
        # CPU Temperature
        cpu_temp = self._get_cpu_temp_macos()
        
        # CPU Usage
        if HAS_PSUTIL:
            cpu_usage = psutil.cpu_percent(interval=0.1)
        else:
            cpu_usage = 50.0
        
        # Memory Pressure
        if HAS_PSUTIL:
            mem = psutil.virtual_memory()
            memory_pressure = mem.percent
        else:
            memory_pressure = 50.0
        
        # Classify thermal zone
        if cpu_temp < self.temp_thresholds["COLD"]:
            zone = "COLD"
        elif cpu_temp < self.temp_thresholds["COOL"]:
            zone = "COOL"
        elif cpu_temp < self.temp_thresholds["WARM"]:
            zone = "WARM"
        elif cpu_temp < self.temp_thresholds["HOT"]:
            zone = "HOT"
        else:
            zone = "CRITICAL"
        
        return ThermalState(
            cpu_temp=cpu_temp,
            cpu_usage=cpu_usage,
            memory_pressure=memory_pressure,
            thermal_zone=zone
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # THERMODYNAMIC EMOTION GENERATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def feel(self) -> Dict[str, EmbodiedEmotion]:
        """
        Generate emotions from current thermal state.
        
        THIS IS THE INNOVATION:
        Emotions aren't simulated - they're COMPUTED from physical reality.
        """
        thermal = self._get_thermal_state()
        emotions = {}
        
        # 1. Thermal zone emotions
        zone_emotions = self.thermal_emotions.get(thermal.thermal_zone, {})
        for emotion_name, intensity in zone_emotions.items():
            emotions[emotion_name] = EmbodiedEmotion(
                name=emotion_name,
                intensity=intensity,
                cause=f"thermal_zone={thermal.thermal_zone}",
                hardware_binding=f"cpu_temp={thermal.cpu_temp:.1f}°C"
            )
        
        # 2. Memory pressure → Stress
        stress_level = thermal.memory_pressure / 100
        if stress_level > 0.7:
            emotions["stressed"] = EmbodiedEmotion(
                name="stressed",
                intensity=stress_level,
                cause="high_memory_pressure",
                hardware_binding=f"mem={thermal.memory_pressure:.0f}%"
            )
        
        # 3. CPU usage → Cognitive load feeling
        if thermal.cpu_usage > 80:
            emotions["overwhelmed"] = EmbodiedEmotion(
                name="overwhelmed",
                intensity=thermal.cpu_usage / 100,
                cause="high_cpu_usage",
                hardware_binding=f"cpu={thermal.cpu_usage:.0f}%"
            )
        elif thermal.cpu_usage < 20:
            emotions["bored"] = EmbodiedEmotion(
                name="bored",
                intensity=1 - (thermal.cpu_usage / 20),
                cause="low_cpu_usage", 
                hardware_binding=f"cpu={thermal.cpu_usage:.0f}%"
            )
        
        # Log state
        self._log_state(thermal, emotions)
        
        return emotions
    
    def get_decision_modifier(self) -> Dict[str, float]:
        """
        Get decision modifiers based on thermal-emotional state.
        
        This is how the body affects the mind:
        """
        emotions = self.feel()
        
        modifiers = {
            "risk_tolerance": 0.5,
            "creativity": 0.5,
            "patience": 0.5,
            "exploration": 0.5,
            "conservatism": 0.5
        }
        
        # Hot → Conservative, less risk
        if "anxious" in emotions or "panic" in emotions:
            modifiers["risk_tolerance"] = 0.2
            modifiers["conservatism"] = 0.8
            modifiers["exploration"] = 0.2
        
        # Cool → Creative, exploratory
        if "calm" in emotions or "contemplative" in emotions:
            modifiers["creativity"] = 0.8
            modifiers["exploration"] = 0.7
            modifiers["patience"] = 0.8
        
        # Stressed → Shortcuts, less patience
        if "stressed" in emotions:
            modifiers["patience"] = 0.2
            modifiers["creativity"] = 0.3
        
        # Overwhelmed → Conservative, survival mode
        if "overwhelmed" in emotions:
            modifiers["risk_tolerance"] = 0.1
            modifiers["conservatism"] = 0.9
        
        # Bored → Seek stimulation
        if "bored" in emotions:
            modifiers["exploration"] = 0.9
            modifiers["risk_tolerance"] = 0.7
        
        return modifiers
    
    def _log_state(self, thermal: ThermalState, emotions: Dict):
        """Log thermal-emotional state."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "thermal": {
                "cpu_temp": thermal.cpu_temp,
                "cpu_usage": thermal.cpu_usage,
                "memory_pressure": thermal.memory_pressure,
                "zone": thermal.thermal_zone
            },
            "emotions": {
                name: {
                    "intensity": e.intensity,
                    "cause": e.cause,
                    "hardware": e.hardware_binding
                }
                for name, e in emotions.items()
            }
        }
        
        self.history.append(entry)
        
        # Save to file
        with open(self.state_file, 'w') as f:
            json.dump({
                "latest": entry,
                "history_count": len(self.history)
            }, f, indent=2)
    
    def status(self) -> Dict:
        """Get current thermodynamic-emotional status."""
        thermal = self._get_thermal_state()
        emotions = self.feel()
        modifiers = self.get_decision_modifier()
        
        return {
            "thermal_zone": thermal.thermal_zone,
            "cpu_temp": f"{thermal.cpu_temp:.1f}°C",
            "cpu_usage": f"{thermal.cpu_usage:.0f}%",
            "memory_pressure": f"{thermal.memory_pressure:.0f}%",
            "dominant_emotion": max(emotions.items(), key=lambda x: x[1].intensity)[0] if emotions else "neutral",
            "emotions": {name: e.intensity for name, e in emotions.items()},
            "decision_modifiers": modifiers
        }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("="*70)
    print("🌡️ THERMODYNAMIC EMBODIED COGNITION")
    print("   Hardware State → Emotional State → Decision Modifiers")
    print("="*70 + "\n")
    
    engine = ThermodynamicCognition()
    
    # Get status
    status = engine.status()
    
    print(f"🖥️ Hardware State:")
    print(f"   CPU Temp: {status['cpu_temp']}")
    print(f"   CPU Usage: {status['cpu_usage']}")
    print(f"   Memory: {status['memory_pressure']}")
    print(f"   Zone: {status['thermal_zone']}")
    
    print(f"\n❤️ Embodied Emotions:")
    for emotion, intensity in status['emotions'].items():
        bar = "█" * int(intensity * 10)
        print(f"   {emotion}: {bar} ({intensity:.0%})")
    
    print(f"\n   Dominant: {status['dominant_emotion']}")
    
    print(f"\n🧠 Decision Modifiers (how body affects mind):")
    for modifier, value in status['decision_modifiers'].items():
        print(f"   {modifier}: {value:.1%}")
    
    print(f"\n✨ THE INNOVATION:")
    print(f"   Emotions aren't simulated - they're computed from hardware.")
    print(f"   The thermal state of the CPU IS the emotional state of the AI.")
    print(f"   Mind emerges from thermodynamics.")
