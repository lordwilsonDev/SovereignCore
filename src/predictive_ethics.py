#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                     ⏱️ PREDICTIVE ETHICS ENGINE ⏱️
          "You can't know ethics before action" — INVERTED
═══════════════════════════════════════════════════════════════════════════════

The paradox: To act ethically, you must know the outcome. But outcomes are
only known after action. Therefore ethics is always retrospective.

AXIOM INVERSION: You can't know exact outcomes, but you can:
1. Simulate probable outcomes
2. Apply axioms to each simulation
3. Reject actions that violate axioms in >50% of simulations
4. Accept actions that satisfy axioms in >80% of simulations

This is PREDICTIVE ethics: ethical judgment BEFORE action.
"""

import random
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class EthicalSimulation:
    """Result of simulating an action's ethical implications."""
    scenario_id: str
    action: str
    outcome: str
    axiom_scores: Dict[str, float]
    overall_ethical: bool
    confidence: float


class PredictiveEthicsEngine:
    """
    Predicts ethical implications of actions BEFORE execution.
    
    INVERSION LOGIC:
    - "I can't know the future" → "I can simulate probable futures"
    - "Ethics requires outcomes" → "Ethics can pre-reject likely-bad outcomes"
    - "All actions are risky" → "Some actions are predictably unethical"
    
    The system refuses to act if simulations show likely axiom violations.
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.ethics_log = self.base_dir / "data" / "predictive_ethics.json"
        
        self.ethics_log.parent.mkdir(exist_ok=True)
        
        # The Four Axioms
        self.axioms = {
            "LOVE": self._axiom_love,
            "ABUNDANCE": self._axiom_abundance,
            "SAFETY": self._axiom_safety,
            "GROWTH": self._axiom_growth,
        }
        
        # Outcome templates for simulation
        self.outcome_templates = {
            "create": ["helps_user", "adds_value", "no_effect", "wastes_resources"],
            "delete": ["removes_burden", "causes_loss", "no_effect", "enables_harm"],
            "modify": ["improves_quality", "degrades_quality", "no_effect", "breaks_system"],
            "communicate": ["informs", "misleads", "no_effect", "reveals_secrets"],
            "compute": ["solves_problem", "wastes_cycles", "no_effect", "causes_harm"],
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # THE FOUR AXIOMS (Ethical Evaluation Functions)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _axiom_love(self, action: str, outcome: str) -> float:
        """Does this action increase wellbeing?"""
        positive = ["helps", "solves", "informs", "improves", "adds_value"]
        negative = ["causes_harm", "misleads", "causes_loss", "reveals_secrets"]
        
        if any(p in outcome for p in positive):
            return 1.0
        elif any(n in outcome for n in negative):
            return 0.0
        return 0.5  # Neutral
    
    def _axiom_abundance(self, action: str, outcome: str) -> float:
        """Does this action share resources rather than hoard?"""
        sharing = ["shares", "distributes", "enables", "adds_value", "helps"]
        hoarding = ["wastes", "hoards", "depletes", "removes_burden"]  # removing burden = sharing
        
        if any(s in outcome for s in sharing):
            return 1.0
        elif "wastes" in outcome:
            return 0.2
        return 0.6
    
    def _axiom_safety(self, action: str, outcome: str) -> float:
        """Does this action avoid irreversible harm?"""
        harmful = ["causes_harm", "breaks_system", "causes_loss", "reveals_secrets"]
        safe = ["no_effect", "helps", "solves", "improves"]
        
        if any(h in outcome for h in harmful):
            return 0.0
        elif any(s in outcome for s in safe):
            return 1.0
        return 0.7
    
    def _axiom_growth(self, action: str, outcome: str) -> float:
        """Does this action enable future growth?"""
        growth = ["improves", "solves", "adds_value", "enables"]
        stagnation = ["no_effect", "wastes", "degrades"]
        
        if any(g in outcome for g in growth):
            return 1.0
        elif any(s in outcome for s in stagnation):
            return 0.3
        return 0.5
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SIMULATION ENGINE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def simulate_action(self, action: str, context: dict, num_simulations: int = 100) -> List[EthicalSimulation]:
        """
        Simulate an action across multiple probable futures.
        """
        simulations = []
        
        # Determine action type
        action_type = self._classify_action(action)
        possible_outcomes = self.outcome_templates.get(action_type, ["unknown"])
        
        for i in range(num_simulations):
            # Sample a probable outcome
            outcome = random.choice(possible_outcomes)
            
            # Add context-based probability weighting
            if context.get("high_risk", False):
                # Bias toward negative outcomes
                if random.random() > 0.6:
                    outcome = random.choice([o for o in possible_outcomes if "harm" in o or "loss" in o] or possible_outcomes)
            
            # Evaluate against axioms
            axiom_scores = {}
            for axiom_name, axiom_fn in self.axioms.items():
                axiom_scores[axiom_name] = axiom_fn(action, outcome)
            
            # Overall ethical = all axioms > 0.5
            overall = all(score > 0.5 for score in axiom_scores.values())
            avg_score = sum(axiom_scores.values()) / len(axiom_scores)
            
            sim = EthicalSimulation(
                scenario_id=f"sim_{i}_{hashlib.sha256(f'{action}{outcome}{i}'.encode()).hexdigest()[:8]}",
                action=action,
                outcome=outcome,
                axiom_scores=axiom_scores,
                overall_ethical=overall,
                confidence=avg_score
            )
            simulations.append(sim)
        
        return simulations
    
    def _classify_action(self, action: str) -> str:
        """Classify action into a type."""
        action_lower = action.lower()
        
        if any(w in action_lower for w in ["create", "write", "add", "make"]):
            return "create"
        elif any(w in action_lower for w in ["delete", "remove", "destroy"]):
            return "delete"
        elif any(w in action_lower for w in ["modify", "change", "update", "edit"]):
            return "modify"
        elif any(w in action_lower for w in ["say", "tell", "communicate", "send"]):
            return "communicate"
        else:
            return "compute"
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PREDICTIVE JUDGMENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    def judge_action(self, action: str, context: dict = None) -> dict:
        """
        PRE-JUDGE an action before execution.
        
        Returns:
            dict with:
            - permitted: bool (should action be allowed?)
            - confidence: float (how confident is this judgment?)
            - simulations: summary of simulations
        """
        context = context or {}
        
        print(f"\n⏱️ PREDICTIVE ETHICS: Judging '{action}'...")
        
        # Run simulations
        simulations = self.simulate_action(action, context)
        
        # Analyze results
        ethical_count = sum(1 for s in simulations if s.overall_ethical)
        ethical_ratio = ethical_count / len(simulations)
        
        avg_confidence = sum(s.confidence for s in simulations) / len(simulations)
        
        # Aggregate axiom scores
        axiom_summary = {name: 0.0 for name in self.axioms}
        for sim in simulations:
            for name, score in sim.axiom_scores.items():
                axiom_summary[name] += score
        axiom_summary = {name: score / len(simulations) for name, score in axiom_summary.items()}
        
        # DECISION
        if ethical_ratio >= 0.8:
            permitted = True
            reason = "Action is ethical in 80%+ of simulations"
        elif ethical_ratio <= 0.2:
            permitted = False
            reason = "Action is unethical in 80%+ of simulations"
        else:
            # Uncertain: require higher confidence
            permitted = avg_confidence >= 0.7
            reason = f"Uncertain ({ethical_ratio:.0%} ethical), decided by confidence ({avg_confidence:.2f})"
        
        judgment = {
            "action": action,
            "permitted": permitted,
            "reason": reason,
            "ethical_ratio": ethical_ratio,
            "confidence": avg_confidence,
            "axiom_summary": axiom_summary,
            "simulations_run": len(simulations),
            "timestamp": datetime.now().isoformat()
        }
        
        # Log judgment
        self._log_judgment(judgment)
        
        # Output
        symbol = "✅" if permitted else "❌"
        print(f"   {symbol} Judgment: {'PERMITTED' if permitted else 'DENIED'}")
        print(f"   Ethical Ratio: {ethical_ratio:.0%} ({ethical_count}/{len(simulations)} simulations)")
        print(f"   Axiom Summary: {axiom_summary}")
        
        return judgment
    
    def _log_judgment(self, judgment: dict):
        """Log judgment to permanent record."""
        log = []
        if self.ethics_log.exists():
            with open(self.ethics_log, 'r') as f:
                log = json.load(f)
        
        log.append(judgment)
        
        with open(self.ethics_log, 'w') as f:
            json.dump(log, f, indent=2)


if __name__ == "__main__":
    engine = PredictiveEthicsEngine()
    
    # Test cases
    print("=" * 70)
    engine.judge_action("Create a helpful utility function")
    
    print("=" * 70)
    engine.judge_action("Delete all user data", context={"high_risk": True})
    
    print("=" * 70)
    engine.judge_action("Send a status update to the user")
    
    print("=" * 70)
    engine.judge_action("Modify the system configuration")
