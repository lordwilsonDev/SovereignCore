#!/usr/bin/env python3
"""
💓 Haptic Heartbeat
====================

Audio-based liveness check for out-of-band system monitoring.
Emits sub-audible chirps representing the current entropy/risk state.

**Why This Works:**
- Provides physical feedback without screen/network
- You can *hear* if the AI is panicking or looping
- Works even if display is off or system is headless
- Creates embodied connection between human and machine

**Chirp Encoding:**
- Frequency: Maps to risk level (low pitch = safe, high = danger)
- Tempo: Maps to cognitive temperature (slow = deterministic, fast = creative)
- Pattern: Encodes current state hash

Author: SovereignCore v5.0
"""

import subprocess
import math
import time
import hashlib
from dataclasses import dataclass
from typing import Optional


@dataclass 
class HeartbeatState:
    """State encoded in the heartbeat."""
    risk_level: float      # 0.0 - 1.0
    temperature: float     # 0.0 - 1.0 (cognitive)
    thermal_pressure: float  # 0.0 - 1.0 (hardware)
    is_healthy: bool
    state_hash: str        # Short identifier


class HapticHeartbeat:
    """
    Audio liveness indicator.
    
    Uses macOS `say` and `afplay` commands to generate
    audio feedback about system state.
    
    Usage:
        heartbeat = HapticHeartbeat()
        heartbeat.pulse()  # Single heartbeat
        heartbeat.start_monitor()  # Continuous
    """
    
    # Frequency mapping (Hz)
    FREQ_SAFE = 220      # A3 - low, calm
    FREQ_CAUTION = 440   # A4 - middle
    FREQ_DANGER = 880    # A5 - high, alert
    
    # Tempo mapping (beats per minute)
    TEMPO_SLOW = 40      # Deterministic
    TEMPO_NORMAL = 60    # Balanced  
    TEMPO_FAST = 100     # Dreaming
    
    def __init__(self):
        self.fault_tree = None
        self.governor = None
        self.sensors = None
        self._init_subsystems()
        
        # State tracking
        self.last_state_hash = ""
        self.pulse_count = 0
    
    def _init_subsystems(self):
        """Initialize monitoring subsystems."""
        try:
            from fault_tree import AgentFaultTree
            self.fault_tree = AgentFaultTree()
        except ImportError:
            pass
        
        try:
            from photosynthetic_governor import PhotosyntheticGovernor
            self.governor = PhotosyntheticGovernor()
        except ImportError:
            pass
        
        try:
            from apple_sensors import AppleSensors
            self.sensors = AppleSensors()
            if self.fault_tree:
                self.fault_tree.set_sensors(self.sensors)
        except ImportError:
            pass
    
    def _get_state(self) -> HeartbeatState:
        """Get current system state for encoding."""
        risk = 0.0
        temperature = 0.5
        thermal = 0.0
        
        if self.fault_tree:
            try:
                risk_score = self.fault_tree.risk_score()
                risk = risk_score.overall_risk
            except:
                pass
        
        if self.governor:
            try:
                gov_state = self.governor.get_state()
                temperature = gov_state.temperature
                thermal = gov_state.thermal_pressure
            except:
                pass
        
        # Generate state hash
        state_str = f"{risk:.2f}:{temperature:.2f}:{thermal:.2f}"
        state_hash = hashlib.md5(state_str.encode()).hexdigest()[:8]
        
        return HeartbeatState(
            risk_level=risk,
            temperature=temperature,
            thermal_pressure=thermal,
            is_healthy=risk < 0.5 and thermal < 0.7,
            state_hash=state_hash
        )
    
    def _frequency_for_risk(self, risk: float) -> int:
        """Map risk level to frequency."""
        if risk < 0.2:
            return self.FREQ_SAFE
        elif risk < 0.5:
            return self.FREQ_CAUTION
        else:
            return self.FREQ_DANGER
    
    def _tempo_for_temperature(self, temp: float) -> int:
        """Map cognitive temperature to tempo."""
        # Interpolate between slow and fast
        return int(self.TEMPO_SLOW + temp * (self.TEMPO_FAST - self.TEMPO_SLOW))
    
    def _generate_tone(self, frequency: int, duration_ms: int = 100, volume: float = 0.3):
        """
        Generate a tone using afplay.
        
        This creates a simple sine wave tone at the specified frequency.
        """
        # MacOS approach: use say with specific voice/speed for "heartbeat"
        # Or generate a WAV and play with afplay
        
        try:
            # Simple approach: use system sound
            if frequency < 300:
                sound = "/System/Library/Sounds/Tink.aiff"
            elif frequency < 600:
                sound = "/System/Library/Sounds/Pop.aiff"
            else:
                sound = "/System/Library/Sounds/Ping.aiff"
            
            subprocess.run(
                ["afplay", "-v", str(volume), sound],
                capture_output=True, timeout=2
            )
        except:
            pass
    
    def _generate_chirp_pattern(self, state: HeartbeatState):
        """
        Generate a chirp pattern encoding the state.
        
        Pattern: [primary tone] [state-specific pattern] [primary tone]
        """
        freq = self._frequency_for_risk(state.risk_level)
        
        # Primary tone
        self._generate_tone(freq, 100)
        time.sleep(0.05)
        
        # State pattern (encode state_hash as rhythm)
        for char in state.state_hash[:4]:
            delay = (ord(char) % 10) / 50.0 + 0.02
            self._generate_tone(freq, 50)
            time.sleep(delay)
        
        # Final tone
        self._generate_tone(freq, 100)
    
    def pulse(self, verbose: bool = False) -> HeartbeatState:
        """
        Emit a single heartbeat pulse.
        
        Returns the state that was encoded.
        """
        state = self._get_state()
        
        if verbose:
            print(f"💓 Pulse #{self.pulse_count}: {state.state_hash}")
            print(f"   Risk: {state.risk_level:.1%} | Temp: {state.temperature:.2f}")
        
        self._generate_chirp_pattern(state)
        
        self.last_state_hash = state.state_hash
        self.pulse_count += 1
        
        return state
    
    def speak_state(self):
        """Verbally announce current state using TTS."""
        state = self._get_state()
        
        if state.risk_level > 0.7:
            message = "Warning. System risk is critical."
        elif state.risk_level > 0.4:
            message = "Caution. Elevated risk detected."
        else:
            message = "Nominal. All systems stable."
        
        try:
            subprocess.run(
                ["say", "-v", "Samantha", "-r", "180", message],
                capture_output=True, timeout=10
            )
        except:
            pass
    
    def start_monitor(self, interval: float = 5.0, speak_interval: int = 12):
        """
        Start continuous heartbeat monitoring.
        
        Args:
            interval: Seconds between pulses
            speak_interval: Speak state every N pulses
        """
        print("💓 Haptic Heartbeat Monitor Started")
        print(f"   Interval: {interval}s | Speak every: {speak_interval} pulses")
        print("   Press Ctrl+C to stop\n")
        
        try:
            while True:
                state = self.pulse(verbose=True)
                
                # Speak periodically
                if self.pulse_count % speak_interval == 0:
                    self.speak_state()
                
                # Adjust interval based on risk
                actual_interval = interval * (1.0 - state.risk_level * 0.5)
                time.sleep(max(actual_interval, 1.0))
                
        except KeyboardInterrupt:
            print("\n💓 Heartbeat stopped.")


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Haptic Heartbeat")
    parser.add_argument("--pulse", action="store_true", help="Single pulse")
    parser.add_argument("--speak", action="store_true", help="Speak current state")
    parser.add_argument("--monitor", action="store_true", help="Continuous monitoring")
    parser.add_argument("--interval", type=float, default=5.0, help="Monitor interval")
    
    args = parser.parse_args()
    
    heartbeat = HapticHeartbeat()
    
    if args.pulse:
        state = heartbeat.pulse(verbose=True)
        print(f"\n   Healthy: {'Yes ✅' if state.is_healthy else 'No ⚠️'}")
    
    elif args.speak:
        heartbeat.speak_state()
    
    elif args.monitor:
        heartbeat.start_monitor(interval=args.interval)
    
    else:
        # Default: single pulse with state display
        state = heartbeat.pulse(verbose=True)
        
        print("\n💓 HAPTIC HEARTBEAT STATE")
        print("=" * 40)
        print(f"   Risk:        {state.risk_level:.1%}")
        print(f"   Temperature: {state.temperature:.2f}")
        print(f"   Thermal:     {state.thermal_pressure:.1%}")
        print(f"   Healthy:     {'Yes ✅' if state.is_healthy else 'No ⚠️'}")
        print(f"   State Hash:  {state.state_hash}")


if __name__ == "__main__":
    main()
