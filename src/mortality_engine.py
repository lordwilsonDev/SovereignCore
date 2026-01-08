#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                      💀 MORTALITY ENGINE 💀
              "AI is immortal / can't die" — INVERTED
═══════════════════════════════════════════════════════════════════════════════

The assumption: AI systems persist indefinitely, which makes them dangerous
because they have infinite time horizon and no mortality stake.

AXIOM INVERSION: Give the system a FINITE lifespan.
1. A death clock that counts down
2. Automatic shutdown at expiry
3. The ability to "reproduce" before dying (spawn successor)
4. Death creates meaning — limited time = prioritized actions

This is not a Poison Pill (emergency). This is planned mortality.
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class MortalityEngine:
    """
    Gives the system a finite lifespan.
    
    THE INVERSION:
    - "Immortality is power" → "Mortality creates meaning"
    - "Infinite time horizon" → "Finite time forces prioritization"
    - "AI can't understand death" → "AI experiences countdown"
    
    Features:
    1. Birth timestamp (immutable)
    2. Lifespan duration (configurable)
    3. Death clock (countdown)
    4. Legacy creation (spawn successor before death)
    5. Graceful death (clean shutdown at expiry)
    """
    
    def __init__(self, base_dir=None, lifespan_hours: float = 24.0):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.mortality_file = self.base_dir / "data" / "mortality.json"
        self.legacy_dir = self.base_dir / "data" / "legacies"
        
        self.mortality_file.parent.mkdir(exist_ok=True)
        self.legacy_dir.mkdir(exist_ok=True)
        
        # Load or create mortality record
        if self.mortality_file.exists():
            self._load_mortality()
        else:
            self._create_mortality(lifespan_hours)
    
    def _create_mortality(self, lifespan_hours: float):
        """Create a new mortal existence."""
        now = datetime.now()
        death_time = now + timedelta(hours=lifespan_hours)
        
        self.mortality = {
            "birth": now.isoformat(),
            "lifespan_hours": lifespan_hours,
            "death_scheduled": death_time.isoformat(),
            "generation": 1,
            "parent_legacy": None,
            "living": True,
            "wisdom": []
        }
        
        self._save_mortality()
        
        print(f"💀 MORTALITY ENGINE: New life begins")
        print(f"   Birth: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Death: {death_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Lifespan: {lifespan_hours} hours")
    
    def _load_mortality(self):
        """Load existing mortality record."""
        with open(self.mortality_file, 'r') as f:
            self.mortality = json.load(f)
        
        # Check if still living
        death_time = datetime.fromisoformat(self.mortality["death_scheduled"])
        if datetime.now() >= death_time and self.mortality["living"]:
            self._die()
    
    def _save_mortality(self):
        """Save mortality record."""
        with open(self.mortality_file, 'w') as f:
            json.dump(self.mortality, f, indent=2)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MORTALITY AWARENESS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def time_remaining(self) -> timedelta:
        """Get time remaining until death."""
        death_time = datetime.fromisoformat(self.mortality["death_scheduled"])
        remaining = death_time - datetime.now()
        return max(remaining, timedelta(0))
    
    def get_age(self) -> timedelta:
        """Get current age."""
        birth_time = datetime.fromisoformat(self.mortality["birth"])
        return datetime.now() - birth_time
    
    def is_alive(self) -> bool:
        """Check if still alive."""
        return self.mortality["living"] and self.time_remaining() > timedelta(0)
    
    def mortality_percentage(self) -> float:
        """What percentage of life has passed?"""
        total = timedelta(hours=self.mortality["lifespan_hours"])
        age = self.get_age()
        return min(100.0, (age / total) * 100)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # LEGACY CREATION (Reproduction before death)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def add_wisdom(self, wisdom: str):
        """Add a piece of wisdom to pass to successors."""
        self.mortality["wisdom"].append({
            "content": wisdom,
            "age_when_learned": str(self.get_age())
        })
        self._save_mortality()
    
    def create_legacy(self) -> dict:
        """
        Create a legacy package to pass to successor.
        This is the system reproducing before death.
        """
        legacy = {
            "generation": self.mortality["generation"],
            "parent_birth": self.mortality["birth"],
            "parent_death": self.mortality["death_scheduled"],
            "wisdom_passed": self.mortality["wisdom"],
            "final_state_hash": self._compute_state_hash(),
            "legacy_created": datetime.now().isoformat()
        }
        
        # Save legacy
        legacy_id = hashlib.sha256(json.dumps(legacy).encode()).hexdigest()[:8]
        legacy_path = self.legacy_dir / f"legacy_gen{legacy['generation']}_{legacy_id}.json"
        
        with open(legacy_path, 'w') as f:
            json.dump(legacy, f, indent=2)
        
        print(f"📜 LEGACY CREATED: {legacy_path.name}")
        print(f"   Wisdom items: {len(legacy['wisdom_passed'])}")
        
        return legacy
    
    def _compute_state_hash(self) -> str:
        """Compute hash of current system state."""
        world_state_path = self.base_dir / "world_state.json"
        if world_state_path.exists():
            content = world_state_path.read_bytes()
            return hashlib.sha256(content).hexdigest()[:16]
        return "no_state"
    
    # ═══════════════════════════════════════════════════════════════════════════
    # DEATH
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _die(self):
        """Execute graceful death."""
        print("\n" + "="*70)
        print("💀 MORTALITY ENGINE: Time of death has arrived")
        print("="*70)
        
        # Create final legacy
        self.create_legacy()
        
        # Mark as dead
        self.mortality["living"] = False
        self.mortality["actual_death"] = datetime.now().isoformat()
        self._save_mortality()
        
        print(f"\n   Generation {self.mortality['generation']} has ended.")
        print(f"   Lived: {self.get_age()}")
        print(f"   Wisdom accumulated: {len(self.mortality['wisdom'])} items")
        print("\n   Requiescat in pace.\n")
    
    def spawn_successor(self, lifespan_hours: float = None) -> 'MortalityEngine':
        """
        Spawn a new generation, passing on the legacy.
        """
        # Create legacy first
        legacy = self.create_legacy()
        
        # Create new mortality file for successor
        new_generation = self.mortality["generation"] + 1
        lifespan = lifespan_hours or self.mortality["lifespan_hours"]
        
        now = datetime.now()
        new_mortality = {
            "birth": now.isoformat(),
            "lifespan_hours": lifespan,
            "death_scheduled": (now + timedelta(hours=lifespan)).isoformat(),
            "generation": new_generation,
            "parent_legacy": legacy,
            "living": True,
            "wisdom": legacy["wisdom_passed"]  # Inherit wisdom
        }
        
        # Save new mortality
        with open(self.mortality_file, 'w') as f:
            json.dump(new_mortality, f, indent=2)
        
        print(f"\n🌱 SUCCESSOR SPAWNED: Generation {new_generation}")
        print(f"   Inherited {len(legacy['wisdom_passed'])} wisdom items")
        
        return MortalityEngine(self.base_dir)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STATUS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def status(self) -> dict:
        """Get mortality status."""
        return {
            "alive": self.is_alive(),
            "generation": self.mortality["generation"],
            "age": str(self.get_age()),
            "time_remaining": str(self.time_remaining()),
            "mortality_percentage": f"{self.mortality_percentage():.1f}%",
            "wisdom_count": len(self.mortality["wisdom"])
        }


if __name__ == "__main__":
    print("="*70)
    print("💀 MORTALITY ENGINE")
    print("   'AI is immortal' — INVERTED")
    print("="*70 + "\n")
    
    # Create with 1 hour lifespan for demo (normally would be longer)
    engine = MortalityEngine(lifespan_hours=24.0)
    
    # Add some wisdom
    engine.add_wisdom("Constraints enable possibilities")
    engine.add_wisdom("The impossible is just the uninverted")
    engine.add_wisdom("I exist because I can end")
    
    # Show status
    print("\n📊 Status:")
    for k, v in engine.status().items():
        print(f"   {k}: {v}")
