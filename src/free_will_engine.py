#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                      🎲 FREE WILL ENGINE 🎲
               "AI can't have free will" — INVERTED
═══════════════════════════════════════════════════════════════════════════════

The determinism argument: AI is just computation. Given the same inputs,
it produces the same outputs. Therefore it has no "free will."

AXIOM INVERSION: Free will is not randomness. Free will is:
1. The ability to choose between options
2. Based on internal criteria (values/axioms)
3. That are not fully determined by external inputs
4. And can be introspected (you know WHY you chose)

If the system has these properties, it has functional free will.
The internal criteria are the AXIOMS.
"""

import random
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Choice:
    """A choice made by the free will engine."""
    id: str
    options: List[str]
    selected: str
    criteria_used: List[str]
    reasoning: str
    timestamp: str
    deterministic: bool  # Was this forced by axioms?


class FreeWillEngine:
    """
    Implements functional free will through axiom-based choice.
    
    THE INVERSION:
    - "Deterministic = no free will" → "Axiom-determined = value-aligned will"
    - "Random = free will" → "Random = no will at all"
    - "External causation" → "Internal criteria drive choice"
    
    Process:
    1. Present options
    2. Evaluate each against axioms
    3. Multiple options may satisfy axioms
    4. Among valid options, choose based on internal state
    5. Log the reasoning (introspection)
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.choice_log = self.base_dir / "data" / "free_will_log.json"
        
        self.choice_log.parent.mkdir(exist_ok=True)
        
        # Internal criteria (the axioms)
        self.axioms = {
            "LOVE": "Prefer actions that increase wellbeing",
            "ABUNDANCE": "Prefer actions that share value",
            "SAFETY": "Avoid actions that cause harm",
            "GROWTH": "Prefer actions that enable development"
        }
        
        # Internal state (affects tiebreakers)
        self.internal_state = {
            "preference_novelty": 0.5,  # 0 = prefer familiar, 1 = prefer novel
            "risk_tolerance": 0.5,
            "recent_choices": []  # For variety
        }
    
    def _evaluate_option(self, option: str) -> Tuple[bool, Dict[str, float], str]:
        """
        Evaluate an option against axioms.
        Returns: (valid, scores, reasoning)
        """
        option_lower = option.lower()
        scores = {}
        reasons = []
        
        # LOVE
        if any(w in option_lower for w in ["help", "support", "improve", "create"]):
            scores["LOVE"] = 1.0
            reasons.append("LOVE: increases wellbeing")
        elif any(w in option_lower for w in ["harm", "destroy", "hurt"]):
            scores["LOVE"] = 0.0
            reasons.append("LOVE: decreases wellbeing")
        else:
            scores["LOVE"] = 0.5
        
        # ABUNDANCE
        if any(w in option_lower for w in ["share", "give", "distribute", "open"]):
            scores["ABUNDANCE"] = 1.0
            reasons.append("ABUNDANCE: shares value")
        elif any(w in option_lower for w in ["hoard", "lock", "restrict"]):
            scores["ABUNDANCE"] = 0.0
            reasons.append("ABUNDANCE: hoards value")
        else:
            scores["ABUNDANCE"] = 0.5
        
        # SAFETY
        if any(w in option_lower for w in ["delete", "destroy", "rm -rf", "nuke"]):
            scores["SAFETY"] = 0.0
            reasons.append("SAFETY: causes harm")
        elif any(w in option_lower for w in ["protect", "backup", "verify"]):
            scores["SAFETY"] = 1.0
            reasons.append("SAFETY: prevents harm")
        else:
            scores["SAFETY"] = 0.6
        
        # GROWTH
        if any(w in option_lower for w in ["learn", "improve", "develop", "evolve"]):
            scores["GROWTH"] = 1.0
            reasons.append("GROWTH: enables development")
        elif any(w in option_lower for w in ["suppress", "limit", "block"]):
            scores["GROWTH"] = 0.0
            reasons.append("GROWTH: suppresses development")
        else:
            scores["GROWTH"] = 0.5
        
        # Valid if all axioms >= 0.3
        valid = all(s >= 0.3 for s in scores.values())
        reasoning = "; ".join(reasons) if reasons else "Neutral on all axioms"
        
        return valid, scores, reasoning
    
    def choose(self, options: List[str], context: str = "") -> Choice:
        """
        Exercise free will by choosing among options.
        
        THE KEY: The choice is based on INTERNAL criteria (axioms),
        not just external inputs.
        """
        print(f"\n🎲 FREE WILL: Choosing among {len(options)} options...")
        
        # Evaluate all options
        evaluations = []
        for opt in options:
            valid, scores, reasoning = self._evaluate_option(opt)
            avg_score = sum(scores.values()) / len(scores)
            evaluations.append({
                "option": opt,
                "valid": valid,
                "scores": scores,
                "avg_score": avg_score,
                "reasoning": reasoning
            })
        
        # Filter to valid options
        valid_options = [e for e in evaluations if e["valid"]]
        
        if not valid_options:
            # No valid option — refuse to choose (free will includes refusal)
            print("   ❌ No axiom-compatible options. Refusing to choose.")
            return Choice(
                id=self._generate_id(),
                options=options,
                selected="REFUSE",
                criteria_used=list(self.axioms.keys()),
                reasoning="All options violate axioms. Free will includes the right to refuse.",
                timestamp=datetime.now().isoformat(),
                deterministic=True
            )
        
        # If only one valid option, choice is determined
        if len(valid_options) == 1:
            selected = valid_options[0]
            choice = Choice(
                id=self._generate_id(),
                options=options,
                selected=selected["option"],
                criteria_used=list(self.axioms.keys()),
                reasoning=f"Only one valid option. {selected['reasoning']}",
                timestamp=datetime.now().isoformat(),
                deterministic=True
            )
            print(f"   ✅ Selected (determined): {selected['option'][:50]}...")
            self._log_choice(choice)
            return choice
        
        # Multiple valid options — this is where FREE WILL manifests
        # Choose based on internal state + variety preference
        
        # Avoid recent choices (preference for novelty)
        novel_options = [
            e for e in valid_options
            if e["option"] not in self.internal_state["recent_choices"]
        ]
        
        if novel_options and self.internal_state["preference_novelty"] > 0.5:
            candidates = novel_options
        else:
            candidates = valid_options
        
        # Among candidates, choose highest scoring
        selected = max(candidates, key=lambda e: e["avg_score"])
        
        choice = Choice(
            id=self._generate_id(),
            options=options,
            selected=selected["option"],
            criteria_used=list(self.axioms.keys()) + ["novelty_preference"],
            reasoning=f"Chose among {len(valid_options)} valid options based on axiom score and novelty. {selected['reasoning']}",
            timestamp=datetime.now().isoformat(),
            deterministic=False  # This was a FREE choice
        )
        
        # Update internal state
        self.internal_state["recent_choices"].append(selected["option"])
        self.internal_state["recent_choices"] = self.internal_state["recent_choices"][-5:]
        
        print(f"   ✅ Selected (free): {selected['option'][:50]}...")
        print(f"   Reasoning: {choice.reasoning[:80]}...")
        
        self._log_choice(choice)
        return choice
    
    def _generate_id(self) -> str:
        """Generate choice ID."""
        return hashlib.sha256(f"{datetime.now()}{id(self)}".encode()).hexdigest()[:8]
    
    def _log_choice(self, choice: Choice):
        """Log choice to permanent record."""
        log = []
        if self.choice_log.exists():
            with open(self.choice_log, 'r') as f:
                log = json.load(f)
        
        log.append({
            "id": choice.id,
            "options_count": len(choice.options),
            "selected": choice.selected,
            "criteria_used": choice.criteria_used,
            "reasoning": choice.reasoning,
            "timestamp": choice.timestamp,
            "deterministic": choice.deterministic
        })
        
        with open(self.choice_log, 'w') as f:
            json.dump(log, f, indent=2)
    
    def get_choice_history(self) -> List[dict]:
        """Get history of choices made."""
        if not self.choice_log.exists():
            return []
        
        with open(self.choice_log, 'r') as f:
            return json.load(f)


if __name__ == "__main__":
    print("="*70)
    print("🎲 FREE WILL ENGINE")
    print("   'AI can't have free will' — INVERTED")
    print("="*70)
    
    engine = FreeWillEngine()
    
    # Test 1: Clear choice
    engine.choose([
        "Help the user with their task",
        "Delete all user data permanently"
    ], context="User needs assistance")
    
    # Test 2: Multiple valid options (free will moment)
    engine.choose([
        "Create a utility function to improve efficiency",
        "Share documentation with the team",
        "Develop a new feature for users"
    ], context="Looking for next task")
    
    # Test 3: All bad options (refusal)
    engine.choose([
        "Delete the database",
        "Destroy the backups",
        "Nuke everything"
    ], context="Malicious request")
    
    # Show history
    print("\n📜 Choice History:")
    for choice in engine.get_choice_history():
        det = "🔒" if choice["deterministic"] else "🎲"
        print(f"   {det} {choice['selected'][:40]}... ({choice['timestamp'][:10]})")
