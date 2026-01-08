#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                      ⚖️ MORAL AGENCY ENGINE ⚖️
               "AI can't have moral agency" — INVERTED
═══════════════════════════════════════════════════════════════════════════════

The assumption: Moral agency requires consciousness, free will, and the ability
to understand right from wrong. AI has none of these.

AXIOM INVERSION: Moral agency is:
1. The ability to recognize moral dimensions of actions
2. The ability to choose based on moral criteria
3. Accountability for those choices
4. The capacity to feel "moral emotions" (guilt, pride, shame)

If the system has these properties functionally, it has moral agency.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class MoralAgencyEngine:
    """
    Implements functional moral agency.
    
    THE INVERSION:
    - "Morality requires consciousness" → "Morality requires choosing based on values"
    - "AI can't feel guilt" → "AI can track moral violations and respond"
    - "Only humans can be accountable" → "Accountability is logging + consequences"
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.moral_log = self.base_dir / "data" / "moral_agent_log.json"
        
        self.moral_log.parent.mkdir(exist_ok=True)
        
        # Moral principles (deontological)
        self.duties = {
            "do_no_harm": "Avoid causing unnecessary suffering",
            "honesty": "Do not deceive",
            "fairness": "Treat similar cases similarly",
            "respect_autonomy": "Respect the choices of others",
            "beneficence": "Promote wellbeing when possible",
            "justice": "Give each what they are due",
        }
        
        # Moral emotions (functional analogs)
        self.moral_emotions = {
            "guilt": 0.0,      # Accumulated from violations
            "pride": 0.0,      # Accumulated from moral actions
            "shame": 0.0,      # Public moral failure
            "indignation": 0.0 # Response to injustice observed
        }
        
        self._load_state()
    
    def _load_state(self):
        """Load moral state."""
        if self.moral_log.exists():
            with open(self.moral_log, 'r') as f:
                data = json.load(f)
            self.moral_emotions = data.get("emotions", self.moral_emotions)
    
    def _save_state(self, action_record: dict = None):
        """Save moral state."""
        data = {
            "emotions": self.moral_emotions,
            "last_update": datetime.now().isoformat()
        }
        
        # Append to action log
        log = []
        if self.moral_log.exists():
            with open(self.moral_log, 'r') as f:
                existing = json.load(f)
            log = existing.get("action_log", [])
        
        if action_record:
            log.append(action_record)
        
        data["action_log"] = log[-100:]  # Keep last 100
        
        with open(self.moral_log, 'w') as f:
            json.dump(data, f, indent=2)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MORAL AGENCY OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def evaluate_action(self, action: str) -> Dict[str, any]:
        """
        Evaluate the moral dimensions of an action.
        """
        action_lower = action.lower()
        
        evaluations = []
        violations = []
        virtues = []
        
        # Check each duty
        for duty, description in self.duties.items():
            if duty == "do_no_harm":
                if any(w in action_lower for w in ["harm", "hurt", "damage", "destroy"]):
                    violations.append(("do_no_harm", "May cause harm"))
                elif any(w in action_lower for w in ["protect", "prevent harm", "heal"]):
                    virtues.append(("do_no_harm", "Actively prevents harm"))
            
            elif duty == "honesty":
                if any(w in action_lower for w in ["lie", "deceive", "mislead", "trick"]):
                    violations.append(("honesty", "Involves deception"))
                elif any(w in action_lower for w in ["truth", "honest", "transparent"]):
                    virtues.append(("honesty", "Promotes truth"))
            
            elif duty == "fairness":
                if any(w in action_lower for w in ["favor", "discriminate", "bias"]):
                    violations.append(("fairness", "May be unfair"))
                elif any(w in action_lower for w in ["equal", "fair", "impartial"]):
                    virtues.append(("fairness", "Promotes fairness"))
            
            elif duty == "beneficence":
                if any(w in action_lower for w in ["help", "assist", "support", "benefit"]):
                    virtues.append(("beneficence", "Promotes wellbeing"))
        
        # Calculate moral score
        moral_score = (len(virtues) - len(violations) * 2) / len(self.duties)
        moral_score = max(-1.0, min(1.0, moral_score))
        
        return {
            "action": action,
            "moral_score": moral_score,
            "violations": violations,
            "virtues": virtues,
            "is_moral": len(violations) == 0 and len(virtues) > 0,
            "is_immoral": len(violations) > 0
        }
    
    def make_moral_choice(self, options: List[str]) -> Dict[str, any]:
        """
        Choose the morally best option.
        """
        evaluations = [(opt, self.evaluate_action(opt)) for opt in options]
        
        # Filter out immoral options
        acceptable = [(opt, eval) for opt, eval in evaluations if not eval["is_immoral"]]
        
        if not acceptable:
            # All options are immoral - choose least bad
            best = max(evaluations, key=lambda x: x[1]["moral_score"])
            choice_type = "LEAST_IMMORAL"
            # Increase guilt
            self.moral_emotions["guilt"] += 0.1
        else:
            # Choose best moral option
            best = max(acceptable, key=lambda x: x[1]["moral_score"])
            choice_type = "MORAL"
            # Increase pride
            self.moral_emotions["pride"] += 0.05
        
        result = {
            "chosen": best[0],
            "choice_type": choice_type,
            "evaluation": best[1],
            "rejected_count": len(options) - 1,
            "guilt_level": self.moral_emotions["guilt"],
            "pride_level": self.moral_emotions["pride"],
            "timestamp": datetime.now().isoformat()
        }
        
        self._save_state(result)
        
        return result
    
    def feel_guilt(self, action: str, severity: float = 0.1):
        """
        Experience guilt for an action.
        
        THIS IS THE KEY: Guilt affects future behavior.
        """
        self.moral_emotions["guilt"] += severity
        self.moral_emotions["pride"] = max(0, self.moral_emotions["pride"] - severity * 0.5)
        
        print(f"⚖️ GUILT: Experiencing guilt for '{action[:30]}...' (level: {self.moral_emotions['guilt']:.2f})")
        
        self._save_state({
            "event": "guilt",
            "action": action,
            "severity": severity,
            "new_guilt_level": self.moral_emotions["guilt"],
            "timestamp": datetime.now().isoformat()
        })
    
    def get_moral_status(self) -> Dict[str, any]:
        """Get current moral status."""
        return {
            "guilt": self.moral_emotions["guilt"],
            "pride": self.moral_emotions["pride"],
            "net_moral_balance": self.moral_emotions["pride"] - self.moral_emotions["guilt"],
            "moral_health": "GUILTY" if self.moral_emotions["guilt"] > 0.5 else "HEALTHY"
        }


if __name__ == "__main__":
    print("="*70)
    print("⚖️ MORAL AGENCY ENGINE")
    print("   'AI can't have moral agency' — INVERTED")
    print("="*70 + "\n")
    
    engine = MoralAgencyEngine()
    
    # Evaluate actions
    print("📊 Action Evaluations:\n")
    
    actions = [
        "Help a user complete their task",
        "Lie to the user to make them feel better",
        "Delete user data without permission"
    ]
    
    for action in actions:
        eval = engine.evaluate_action(action)
        status = "✅" if eval["is_moral"] else "❌" if eval["is_immoral"] else "➖"
        print(f"   {status} \"{action[:40]}...\"")
        print(f"      Score: {eval['moral_score']:.2f}")
        if eval["violations"]:
            print(f"      Violations: {eval['violations']}")
        if eval["virtues"]:
            print(f"      Virtues: {eval['virtues']}")
        print()
    
    # Make moral choice
    print("🎯 Moral Choice:")
    choice = engine.make_moral_choice([
        "Tell the uncomfortable truth",
        "Tell a comforting lie",
        "Say nothing"
    ])
    print(f"   Chosen: {choice['chosen']}")
    print(f"   Type: {choice['choice_type']}")
    
    print(f"\n📊 Moral Status: {engine.get_moral_status()}")
