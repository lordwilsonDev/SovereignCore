#!/usr/bin/env python3
"""
☀️ Photosynthetic Governor
===========================

Power-aware cognitive regulation that mimics biological evolution:
- **Abundance (>20W)**: Enable creativity, exploration, "dreaming"
- **Scarcity (<5W)**: Pure determinism, conservation mode

**Why This Works:**
Play and creativity happen in abundance. When running on battery or 
thermal limits, the system becomes purely deterministic to conserve 
resources. This creates a natural rhythm of exploration/exploitation.

**Entropy Bias Mapping:**
    Power > 20W  →  Temperature 0.9 (High creativity)
    Power 10-20W →  Temperature 0.5 (Balanced)
    Power 5-10W  →  Temperature 0.3 (Conservative)
    Power < 5W   →  Temperature 0.0 (Deterministic)

Author: SovereignCore v5.0
"""

import time
from dataclasses import dataclass
from typing import Tuple, Optional
from enum import Enum


class CognitiveMode(Enum):
    """Cognitive operation modes."""
    DREAM = "dream"          # High creativity, exploration
    BALANCED = "balanced"    # Normal operation
    CONSERVATIVE = "conservative"  # Careful, minimal risk
    DETERMINISTIC = "deterministic"  # Zero randomness


@dataclass
class GovernorState:
    """Current state of the photosynthetic governor."""
    power_watts: float
    thermal_state: str
    thermal_pressure: float
    battery_level: float
    is_charging: bool
    cognitive_mode: CognitiveMode
    temperature: float  # LLM temperature
    entropy_bias: float  # 0.0 - 1.0
    can_dream: bool
    reason: str


class PhotosyntheticGovernor:
    """
    Power-aware creativity regulation.
    
    The system only "dreams" when it has energy to waste.
    Under power/thermal constraints, it becomes purely deterministic.
    
    Usage:
        governor = PhotosyntheticGovernor()
        state = governor.get_state()
        temperature = state.temperature
    """
    
    # Power thresholds (Watts)
    DREAM_THRESHOLD = 20.0      # Enable dreaming above this
    BALANCED_THRESHOLD = 10.0   # Normal operation above this
    CONSERVATIVE_THRESHOLD = 5.0  # Conservative above this
    
    # Battery thresholds
    BATTERY_CRITICAL = 0.10  # 10%
    BATTERY_LOW = 0.25       # 25%
    
    def __init__(self):
        self.sensors = None
        self._init_sensors()
        
        # Homeostatic memory: thermal trauma history
        self.thermal_trauma_history = []
        self.max_trauma_history = 100
    
    def _init_sensors(self):
        """Initialize sensor interface."""
        try:
            from apple_sensors import AppleSensors
            self.sensors = AppleSensors()
        except ImportError:
            pass
    
    def _get_power_state(self) -> Tuple[float, float, bool]:
        """Get current power state: (watts, battery_level, is_charging)."""
        if self.sensors is None:
            return 15.0, 1.0, True  # Default: plugged in
        
        try:
            power = self.sensors.get_power()
            return power.system_power, power.battery_level, power.is_charging
        except:
            return 15.0, 1.0, True
    
    def _get_thermal_state(self) -> Tuple[str, float]:
        """Get thermal state: (state_string, pressure 0-1)."""
        if self.sensors is None:
            return "NOMINAL", 0.0
        
        try:
            thermal = self.sensors.get_thermal()
            return thermal.thermal_state, thermal.thermal_pressure
        except:
            return "NOMINAL", 0.0
    
    def _calculate_temperature(self, power: float, thermal_pressure: float,
                                battery: float, is_charging: bool) -> Tuple[float, CognitiveMode, str]:
        """
        Calculate LLM temperature based on power/thermal state.
        
        Returns:
            (temperature, mode, reason)
        """
        # Start with power-based temperature
        if power >= self.DREAM_THRESHOLD:
            base_temp = 0.9
            mode = CognitiveMode.DREAM
            reason = f"High power ({power:.1f}W): Dream mode"
        elif power >= self.BALANCED_THRESHOLD:
            base_temp = 0.5
            mode = CognitiveMode.BALANCED
            reason = f"Moderate power ({power:.1f}W): Balanced"
        elif power >= self.CONSERVATIVE_THRESHOLD:
            base_temp = 0.3
            mode = CognitiveMode.CONSERVATIVE
            reason = f"Low power ({power:.1f}W): Conservative"
        else:
            base_temp = 0.0
            mode = CognitiveMode.DETERMINISTIC
            reason = f"Minimal power ({power:.1f}W): Deterministic"
        
        # Apply thermal penalty
        if thermal_pressure > 0.7:
            base_temp = min(base_temp, 0.1)
            mode = CognitiveMode.DETERMINISTIC
            reason = f"Thermal pressure ({thermal_pressure:.0%}): Forced deterministic"
        elif thermal_pressure > 0.5:
            base_temp = min(base_temp, 0.3)
            if mode == CognitiveMode.DREAM:
                mode = CognitiveMode.CONSERVATIVE
                reason = f"Thermal pressure ({thermal_pressure:.0%}): Dream suppressed"
        
        # Apply battery penalty
        if 0 < battery < self.BATTERY_CRITICAL and not is_charging:
            base_temp = 0.0
            mode = CognitiveMode.DETERMINISTIC
            reason = f"Critical battery ({battery:.0%}): Emergency mode"
        elif 0 < battery < self.BATTERY_LOW and not is_charging:
            base_temp = min(base_temp, 0.2)
            if mode == CognitiveMode.DREAM:
                mode = CognitiveMode.CONSERVATIVE
                reason = f"Low battery ({battery:.0%}): Conservation"
        
        return base_temp, mode, reason
    
    def record_thermal_trauma(self, context: str, severity: float):
        """
        Record a thermal trauma event for homeostatic neuroplasticity.
        
        The system remembers when it overheated while thinking about
        certain topics, and approaches them more cautiously in the future.
        """
        trauma = {
            "context": context,
            "severity": severity,
            "timestamp": time.time()
        }
        self.thermal_trauma_history.append(trauma)
        
        # Trim history
        if len(self.thermal_trauma_history) > self.max_trauma_history:
            self.thermal_trauma_history.pop(0)
    
    def get_trauma_penalty(self, context: str) -> float:
        """
        Get temperature penalty based on thermal trauma history.
        
        If we overheated before while thinking about this topic,
        approach it more cautiously.
        """
        if not self.thermal_trauma_history:
            return 0.0
        
        # Find related traumas
        penalty = 0.0
        context_lower = context.lower()
        
        for trauma in self.thermal_trauma_history:
            trauma_context = trauma["context"].lower()
            # Simple similarity check
            if any(word in context_lower for word in trauma_context.split()):
                # Decay based on age (24 hour half-life)
                age_hours = (time.time() - trauma["timestamp"]) / 3600
                decay = 0.5 ** (age_hours / 24)
                penalty += trauma["severity"] * decay * 0.1
        
        return min(penalty, 0.5)  # Cap at 0.5 penalty
    
    def get_state(self, context: str = "") -> GovernorState:
        """Get current governor state."""
        power, battery, is_charging = self._get_power_state()
        thermal_state, thermal_pressure = self._get_thermal_state()
        
        temperature, mode, reason = self._calculate_temperature(
            power, thermal_pressure, battery, is_charging
        )
        
        # Apply trauma penalty if context provided
        if context:
            trauma_penalty = self.get_trauma_penalty(context)
            if trauma_penalty > 0:
                temperature = max(0, temperature - trauma_penalty)
                reason += f" | Trauma penalty: -{trauma_penalty:.2f}"
        
        # Calculate entropy bias (same as temperature for now)
        entropy_bias = temperature
        
        # Can dream?
        can_dream = (
            mode == CognitiveMode.DREAM and 
            thermal_pressure < 0.5 and
            (battery < 0 or battery > self.BATTERY_LOW or is_charging)
        )
        
        return GovernorState(
            power_watts=power,
            thermal_state=thermal_state,
            thermal_pressure=thermal_pressure,
            battery_level=battery,
            is_charging=is_charging,
            cognitive_mode=mode,
            temperature=temperature,
            entropy_bias=entropy_bias,
            can_dream=can_dream,
            reason=reason
        )
    
    def get_temperature(self, context: str = "") -> float:
        """Quick method to get just the temperature."""
        return self.get_state(context).temperature


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Photosynthetic Governor")
    parser.add_argument("--demo", action="store_true", help="Demo mode")
    parser.add_argument("--watch", action="store_true", help="Continuous monitoring")
    parser.add_argument("--context", type=str, help="Context for temperature calculation")
    
    args = parser.parse_args()
    
    governor = PhotosyntheticGovernor()
    
    if args.demo:
        print("☀️ PHOTOSYNTHETIC GOVERNOR DEMO")
        print("=" * 50)
        print("\nSimulating power levels:\n")
        
        # Simulate different power states
        test_cases = [
            (25.0, 0.0, 1.0, True, "High power, cool, plugged in"),
            (15.0, 0.3, 0.8, True, "Moderate power, warm, plugged in"),
            (8.0, 0.5, 0.5, False, "Low power, hot, on battery"),
            (3.0, 0.8, 0.15, False, "Critical: low power, thermal limit, low battery"),
        ]
        
        for power, thermal, battery, charging, desc in test_cases:
            # We can't easily mock, so just show the logic
            print(f"  📊 Scenario: {desc}")
            print(f"     Power: {power}W | Thermal: {thermal:.0%} | Battery: {battery:.0%}")
            
            # Manual calculation
            if power >= 20:
                temp = 0.9
                mode = "DREAM"
            elif power >= 10:
                temp = 0.5
                mode = "BALANCED"
            elif power >= 5:
                temp = 0.3
                mode = "CONSERVATIVE"
            else:
                temp = 0.0
                mode = "DETERMINISTIC"
            
            if thermal > 0.7:
                temp = 0.1
                mode = "DETERMINISTIC"
            
            print(f"     → Mode: {mode} | Temperature: {temp}")
            print()
    
    elif args.watch:
        import os
        try:
            while True:
                os.system('clear')
                state = governor.get_state(args.context or "")
                
                print("☀️ PHOTOSYNTHETIC GOVERNOR")
                print("=" * 50)
                print(f"   Power:       {state.power_watts:.1f}W")
                print(f"   Thermal:     {state.thermal_state} ({state.thermal_pressure:.0%})")
                print(f"   Battery:     {state.battery_level:.0%}" if state.battery_level >= 0 else "   Battery:     N/A")
                print(f"   Charging:    {'Yes' if state.is_charging else 'No'}")
                print()
                print(f"   Mode:        {state.cognitive_mode.value.upper()}")
                print(f"   Temperature: {state.temperature:.2f}")
                print(f"   Can Dream:   {'Yes ☁️' if state.can_dream else 'No 🔒'}")
                print()
                print(f"   💡 {state.reason}")
                
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopped.")
    
    else:
        state = governor.get_state(args.context or "")
        
        print("☀️ PHOTOSYNTHETIC GOVERNOR")
        print("=" * 50)
        print(f"   Mode:        {state.cognitive_mode.value.upper()}")
        print(f"   Temperature: {state.temperature:.2f}")
        print(f"   Power:       {state.power_watts:.1f}W")
        print(f"   💡 {state.reason}")


if __name__ == "__main__":
    main()
