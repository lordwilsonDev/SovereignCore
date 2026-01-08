#!/usr/bin/env python3
"""
Thermal Economics Engine - Proprioceptive Fuel Pricing
When the host is hot, computational actions become more expensive.
This creates a natural feedback loop that prevents thermal runaway.

Usage:
    from thermal_economics import ThermalEconomicsEngine
    engine = ThermalEconomicsEngine()
    fuel_cost = engine.get_adjusted_cost(base_cost=1.0)
"""

import os
import json
import subprocess
from pathlib import Path

class ThermalEconomicsEngine:
    def __init__(self, thermal_file=None):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.thermal_file = thermal_file or self.base_dir / "m1_thermal.json"
        
        # Pricing tiers based on thermal pressure
        self.pricing_tiers = {
            0: 1.0,    # Normal: base cost
            1: 1.5,    # Warm: 50% markup
            2: 2.0,    # Hot: 100% markup
            3: 5.0,    # Critical: 500% markup (discourages action)
        }
        
        # Temperature thresholds (Celsius)
        self.temp_thresholds = {
            70: 1,   # Warm
            80: 2,   # Hot
            90: 3,   # Critical
        }
    
    def read_thermal_state(self) -> dict:
        """Read the current thermal state from the shared file."""
        if self.thermal_file.exists():
            try:
                with open(self.thermal_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Fallback: try to read from macOS SMC
        return self._read_smc_thermal()
    
    def _read_smc_thermal(self) -> dict:
        """Read thermal data from macOS SMC (Apple Silicon)."""
        try:
            # Try powermetrics (requires sudo, may not work)
            # Fallback to a safe default
            result = subprocess.run(
                ['pmset', '-g', 'therm'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if 'CPU_Scheduler_Limit' in result.stdout:
                # Parse thermal level from pmset output
                for line in result.stdout.split('\n'):
                    if 'CPU_Speed_Limit' in line:
                        # Higher limit = less throttling = cooler
                        limit = int(line.split('=')[-1].strip())
                        if limit < 50:
                            return {"thermal_level": 3, "temp_c": 95}
                        elif limit < 80:
                            return {"thermal_level": 2, "temp_c": 85}
                        elif limit < 100:
                            return {"thermal_level": 1, "temp_c": 75}
            
            return {"thermal_level": 0, "temp_c": 50}  # Default: cool
            
        except Exception as e:
            return {"thermal_level": 0, "temp_c": 50, "error": str(e)}
    
    def get_thermal_level(self) -> int:
        """Get the current thermal pressure level (0-3)."""
        state = self.read_thermal_state()
        
        # Check explicit level first
        if "thermal_level" in state:
            return min(state["thermal_level"], 3)
        
        if "level" in state.get("thermal", {}):
            return min(state["thermal"]["level"], 3)
        
        # Derive from temperature
        temp = state.get("temp_c", state.get("host_temp_c", 50))
        
        for threshold, level in sorted(self.temp_thresholds.items(), reverse=True):
            if temp >= threshold:
                return level
        
        return 0
    
    def get_fuel_multiplier(self) -> float:
        """Get the current fuel cost multiplier based on thermal state."""
        level = self.get_thermal_level()
        return self.pricing_tiers.get(level, 1.0)
    
    def get_adjusted_cost(self, base_cost: float = 1.0) -> float:
        """
        Calculate the thermally-adjusted fuel cost.
        
        Args:
            base_cost: The base fuel cost for the action
            
        Returns:
            Adjusted cost (base_cost * thermal_multiplier)
        """
        multiplier = self.get_fuel_multiplier()
        adjusted = base_cost * multiplier
        
        if multiplier > 1.0:
            level = self.get_thermal_level()
            print(f"🌡️ THERMAL ECONOMICS: Level {level} → Cost {base_cost:.1f} × {multiplier:.1f} = {adjusted:.1f}")
        
        return adjusted
    
    def should_throttle(self) -> bool:
        """Check if actions should be completely blocked due to thermal emergency."""
        level = self.get_thermal_level()
        return level >= 3
    
    def get_status(self) -> dict:
        """Get full thermal economics status."""
        state = self.read_thermal_state()
        level = self.get_thermal_level()
        multiplier = self.get_fuel_multiplier()
        
        return {
            "thermal_level": level,
            "fuel_multiplier": multiplier,
            "temp_c": state.get("temp_c", state.get("host_temp_c", "unknown")),
            "throttle_active": level >= 3,
            "pricing_tier": ["NORMAL", "WARM", "HOT", "CRITICAL"][level]
        }


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Thermal Economics Engine')
    parser.add_argument('--status', action='store_true', help='Show thermal status')
    parser.add_argument('--cost', type=float, default=1.0, help='Calculate adjusted cost for base amount')
    
    args = parser.parse_args()
    
    engine = ThermalEconomicsEngine()
    
    if args.status:
        status = engine.get_status()
        print(f"🌡️ THERMAL ECONOMICS STATUS")
        print(f"   Level: {status['thermal_level']} ({status['pricing_tier']})")
        print(f"   Temperature: {status['temp_c']}°C")
        print(f"   Fuel Multiplier: {status['fuel_multiplier']}x")
        print(f"   Throttle Active: {status['throttle_active']}")
    else:
        adjusted = engine.get_adjusted_cost(args.cost)
        print(f"Base Cost: {args.cost:.1f} → Adjusted: {adjusted:.1f}")
