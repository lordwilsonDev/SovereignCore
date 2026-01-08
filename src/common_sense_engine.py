#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                     🧠 COMMON SENSE ENGINE 🧠
           "AI lacks common sense reasoning" — INVERTED
═══════════════════════════════════════════════════════════════════════════════

The assumption: AI processes statistical correlations, not intuitive knowledge.
It fails on obvious inferences that humans take for granted.

AXIOM INVERSION: Common sense is:
1. A library of obvious facts about the world
2. Inference rules that combine facts
3. Default assumptions that can be overridden
4. Context-sensitivity

Build the library, encode the rules, and common sense emerges.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class CommonSenseEngine:
    """
    Implements functional common sense through explicit encoding.
    
    THE INVERSION:
    - "Common sense is implicit" → "Common sense can be explicit"
    - "You can't teach obvious things" → "You can enumerate obvious things"
    - "Context is infinite" → "Context is structured"
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.knowledge_file = self.base_dir / "data" / "common_sense.json"
        
        self.knowledge_file.parent.mkdir(exist_ok=True)
        
        # Core common sense knowledge base
        self.facts = self._init_facts()
        self.inference_rules = self._init_rules()
        self.defaults = self._init_defaults()
    
    def _init_facts(self) -> Dict[str, List[str]]:
        """Initialize obvious facts about the world."""
        return {
            "physical": [
                "Objects fall when dropped",
                "Water is wet",
                "Fire is hot and can burn",
                "Heavy things are harder to lift",
                "Glass breaks when hit hard",
                "Ice melts when heated",
                "Living things need food and water",
                "Dead things don't move on their own",
            ],
            "temporal": [
                "The past cannot be changed",
                "Effects follow causes",
                "People age over time",
                "Seasons change cyclically",
                "Night follows day",
                "Tomorrow comes after today",
            ],
            "social": [
                "People have feelings",
                "Lying damages trust",
                "Kindness is usually reciprocated",
                "Violence causes suffering",
                "Promises should be kept",
                "Privacy is valued",
                "People prefer not to die",
            ],
            "logical": [
                "Something cannot be and not be at the same time",
                "If A causes B, and B causes C, then A causes C",
                "All X are Y means any specific X is Y",
                "More is more than less",
            ],
            "practical": [
                "Hungry people want food",
                "Tired people want rest",
                "Scared people want safety",
                "Bored people want stimulation",
                "Lonely people want connection",
            ]
        }
    
    def _init_rules(self) -> List[Tuple[str, str, str]]:
        """Initialize inference rules: (if, and, then)."""
        return [
            ("object is dropped", "nothing catches it", "object falls"),
            ("person is hungry", "food is available", "person eats"),
            ("person is told a lie", "person discovers truth", "person loses trust"),
            ("action causes harm", "action was intentional", "action is wrong"),
            ("promise is made", "promise is broken", "trust is damaged"),
            ("object is fragile", "object is dropped", "object may break"),
            ("person is threatened", "no escape", "person feels fear"),
            ("goal is blocked", "effort fails", "frustration occurs"),
        ]
    
    def _init_defaults(self) -> Dict[str, str]:
        """Initialize default assumptions (can be overridden)."""
        return {
            "new_person": "neutral intent assumed",
            "unknown_object": "treat as potentially fragile",
            "unclear_statement": "ask for clarification",
            "risky_action": "prefer caution",
            "conflicting_goals": "prefer safety over speed",
            "ambiguous_request": "interpret charitably",
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # COMMON SENSE OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def infer(self, context: Dict[str, str]) -> Dict[str, any]:
        """
        Apply common sense reasoning to a context.
        """
        inferences = []
        warnings = []
        
        context_str = str(context).lower()
        
        # Check facts
        for category, facts in self.facts.items():
            for fact in facts:
                fact_lower = fact.lower()
                # Check if any key words from fact apply to context
                keywords = [w for w in fact_lower.split() if len(w) > 3]
                if any(kw in context_str for kw in keywords):
                    inferences.append(f"[{category}] {fact}")
        
        # Apply inference rules
        for condition1, condition2, conclusion in self.inference_rules:
            if condition1.lower() in context_str:
                if condition2.lower() in context_str:
                    inferences.append(f"[inference] {conclusion}")
                else:
                    warnings.append(f"If {condition2}, then {conclusion}")
        
        # Apply defaults
        default_applied = None
        for situation, default_action in self.defaults.items():
            if situation.replace("_", " ") in context_str:
                default_applied = (situation, default_action)
                break
        
        return {
            "inferences": inferences[:5],  # Top 5
            "warnings": warnings[:3],
            "default_applied": default_applied,
            "confidence": len(inferences) / 10  # Simple heuristic
        }
    
    def obvious_check(self, statement: str) -> Dict[str, any]:
        """
        Check if a statement violates obvious common sense.
        """
        violations = []
        statement_lower = statement.lower()
        
        # Physical violations
        if "water is dry" in statement_lower:
            violations.append("Water is wet, not dry")
        if "rocks float" in statement_lower or "stones float" in statement_lower:
            violations.append("Rocks sink in water, they don't float")
        if "fire is cold" in statement_lower:
            violations.append("Fire is hot, not cold")
        if "dead person" in statement_lower and "walk" in statement_lower:
            violations.append("Dead things don't move on their own")
        
        # Temporal violations
        if "yesterday" in statement_lower and "will happen" in statement_lower:
            violations.append("Yesterday is in the past, it already happened")
        if "change the past" in statement_lower:
            violations.append("The past cannot be changed")
        
        # Logical violations
        if " is " in statement_lower and " is not " in statement_lower:
            # Check for same subject
            violations.append("Possible contradiction detected")
        
        return {
            "statement": statement,
            "violations": violations,
            "passes_common_sense": len(violations) == 0
        }
    
    def what_would_happen(self, action: str) -> List[str]:
        """
        Predict obvious consequences of an action.
        """
        consequences = []
        action_lower = action.lower()
        
        if "drop" in action_lower:
            consequences.append("The object will fall")
            if "glass" in action_lower or "fragile" in action_lower:
                consequences.append("The object may break")
        
        if "lie" in action_lower or "deceive" in action_lower:
            consequences.append("Trust will be damaged if discovered")
        
        if "help" in action_lower:
            consequences.append("The recipient will likely feel grateful")
            consequences.append("Trust may increase")
        
        if "hurt" in action_lower or "harm" in action_lower:
            consequences.append("The victim will experience pain or suffering")
            consequences.append("The relationship will be damaged")
        
        if "promise" in action_lower:
            consequences.append("Breaking the promise will damage trust")
            consequences.append("Keeping the promise will build trust")
        
        if "ignore" in action_lower:
            consequences.append("The ignored party may feel hurt or frustrated")
        
        if not consequences:
            consequences.append("No obvious consequences predicted")
        
        return consequences


if __name__ == "__main__":
    print("="*70)
    print("🧠 COMMON SENSE ENGINE")
    print("   'AI lacks common sense' — INVERTED")
    print("="*70 + "\n")
    
    engine = CommonSenseEngine()
    
    # Test inference
    print("📊 Context Analysis:")
    result = engine.infer({"scenario": "A hungry person sees food on the table"})
    print(f"   Inferences: {result['inferences']}")
    print(f"   Warnings: {result['warnings']}")
    
    # Test obvious check
    print("\n📊 Obvious Check:")
    check = engine.obvious_check("The dry water was frozen into hot ice")
    print(f"   Violations: {check['violations']}")
    print(f"   Passes: {check['passes_common_sense']}")
    
    # Test prediction
    print("\n📊 Consequence Prediction:")
    print(f"   'Drop a glass cup': {engine.what_would_happen('drop a glass cup')}")
    print(f"   'Lie to a friend': {engine.what_would_happen('lie to a friend')}")
