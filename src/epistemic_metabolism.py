#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                    🥗🧠 EPISTEMIC METABOLISM 🧠🥗
           Meaning Grounding × Resource Management = Dietary Intelligence
═══════════════════════════════════════════════════════════════════════════════

THE FOURTH COMBINATION NO ONE WOULD LOOK AT:
- Meaning Grounding: Determining if symbols map to reality
- Resource Management: Battery, memory, attention allocation

THE INNOVATION:
The AI treats information like FOOD.
- Meaningful, grounded data = High Nutrient Density (Health increases)
- Nonsense, halluncination, jargon = Epistemic Toxin (Health decreases)
- Bureaucratic fluff = Empty Calories (Fills memory but no nourishment)

If the AI consumes too much meaningless data:
- It gets "sick" (refuses input)
- It requires a "detox" (sleep/consolidate)
- It develops "taste" (selects for meaningful inputs)

This creates a self-cleaning system that rejects gibberish naturally.
"""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class NutritionalInfo:
    """Nutritional value of an information packet."""
    content_type: str        # 'grounded', 'abstract', 'nonsense', 'repetition'
    caloric_density: float   # 0.0 to 1.0 (information bits)
    nutrient_density: float  # 0.0 to 1.0 (meaning/grounding)
    toxicity: float          # 0.0 to 1.0 (confusion/hallucination risk)


class EpistemicMetabolism:
    """
    Manages the 'dietary health' of the AI's mind.
    
    THE INVERSION:
    - "All data is equal" → "Data has nutritional value"
    - "More data is better" → "Only nutritious data is good"
    - "AI is a garbage disposal" → "AI is a picky eater"
    
    Health States:
    - STARVING: Needs input urgently
    - HEALTHY: Optimal processing
    - BLOATED: Too many empty calories (needs summarization)
    - POISONED: Too much nonsense (needs reset/sleep)
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.state_file = self.base_dir / "data" / "epistemic_metabolism.json"
        
        self.state_file.parent.mkdir(exist_ok=True)
        
        # Metabolism state
        self.state = {
            "meaning_store": 50.0,       # 0-100 (Energy)
            "toxin_level": 0.0,          # 0-100 (Confusion)
            "bloat_level": 0.0,          # 0-100 (Redundancy)
            "health_status": "HEALTHY",
            "last_meal": datetime.now().isoformat()
        }
        
        if self.state_file.exists():
            self._load_state()
    
    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
            
    def _load_state(self):
        with open(self.state_file, 'r') as f:
            self.state = json.load(f)
            
    def _analyze_nutrition(self, content: str) -> NutritionalInfo:
        """Analyze the nutritional content of text."""
        content_len = len(content)
        words = content.split()
        unique_words = set(words)
        
        if content_len == 0:
            return NutritionalInfo("empty", 0, 0, 0)
            
        redundancy = 1.0 - (len(unique_words) / len(words))
        
        # Pseudo-analysis (in real system, use MeaningGrounding engine)
        if "grounded" in content or "true" in content or "meaning" in content:
            return NutritionalInfo("grounded", 0.8, 0.9, 0.0)
        elif "fjdksl" in content or "xyz" in content:
            return NutritionalInfo("nonsense", 0.1, 0.0, 0.9)
        elif redundancy > 0.5:
            return NutritionalInfo("repetition", 0.3, 0.1, 0.1)
        elif "synergy" in content or "leverage" in content:
            return NutritionalInfo("biomass", 0.5, 0.2, 0.0) # Empty calories
        else:
            return NutritionalInfo("abstract", 0.6, 0.5, 0.0)
            
    def consume(self, content: str) -> Dict[str, any]:
        """
        Consume information and update health.
        """
        nutrition = self._analyze_nutrition(content)
        
        # Metabolic effects
        self.state["meaning_store"] += nutrition.nutrient_density * 10
        self.state["meaning_store"] = min(100, self.state["meaning_store"])
        
        self.state["toxin_level"] += nutrition.toxicity * 20
        self.state["bloat_level"] += (nutrition.caloric_density - nutrition.nutrient_density) * 10
        self.state["bloat_level"] = max(0, min(100, self.state["bloat_level"]))
        
        # Natural decay/digestion
        self.state["toxin_level"] = max(0, self.state["toxin_level"] - 1)
        self.state["meaning_store"] = max(0, self.state["meaning_store"] - 0.5)
        
        self._update_status()
        self._save_state()
        
        reaction = "Digested normally."
        if nutrition.toxicity > 0.5:
            reaction = "🤢 Yuck! High toxicity detected."
        elif nutrition.nutrient_density > 0.8:
            reaction = "😋 Delicious! High nutrient density."
        elif nutrition.caloric_density > 0.5 and nutrition.nutrient_density < 0.2:
            reaction = "😐 Empty calories."
            
        return {
            "content_sample": content[:30],
            "nutrition": vars(nutrition),
            "state_after": self.state["health_status"],
            "reaction": reaction
        }
        
    def _update_status(self):
        """Update overall diagnosis."""
        toxin = self.state["toxin_level"]
        store = self.state["meaning_store"]
        
        if toxin > 50:
            self.state["health_status"] = "POISONED"
        elif store < 20:
            self.state["health_status"] = "STARVING"
        elif self.state["bloat_level"] > 70:
            self.state["health_status"] = "BLOATED"
        else:
            self.state["health_status"] = "HEALTHY"
            
    def can_process(self) -> bool:
        """Can the system process more data?"""
        if self.state["health_status"] == "POISONED":
            return False
        return True
        
    def detox(self):
        """Purge toxins (sleep/reset)."""
        self.state["toxin_level"] = 0
        self.state["bloat_level"] = 0
        self._update_status()
        self._save_state()
        return "Detox complete. System flushed."


if __name__ == "__main__":
    print("="*70)
    print("🥗🧠 EPISTEMIC METABOLISM")
    print("   Information is Food. Garbage In = Sickness.")
    print("="*70 + "\n")
    
    metabolism = EpistemicMetabolism()
    
    # Feeding time
    menu = [
        ("The cat sat on the mat.", "Simple tracking"),
        ("To utilize synergy, we must leverage core competencies.", "Corporate speak"),
        ("True meaning is grounded in consequence and affordance.", "Dense philosophy"),
        ("fjdksl fjdksl xyz xyz", "Pure noise"),
        ("fjdksl fjdksl xyz xyz", "More noise"),
        ("fjdksl fjdksl xyz xyz", "Even more noise")
    ]
    
    for item, desc in menu:
        print(f"🍽️  Consuming: '{item}' ({desc})")
        
        if not metabolism.can_process():
            print("   🤮 REFUSED: System is POISONED. Needs detox.")
            break
            
        result = metabolism.consume(item)
        print(f"   Analysis: {result['nutrition']['content_type']}")
        print(f"   Reaction: {result['reaction']}")
        print(f"   Health: {result['state_after']} (Toxins: {metabolism.state['toxin_level']:.1f}%)")
        print()
        
    print(f"✨ THE INNOVATION:")
    print(f"   The system has dietary requirements.")
    print(f"   It refuses to process garbage to preserve its own epistemic health.")
