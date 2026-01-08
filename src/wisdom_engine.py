#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                       📜 WISDOM ENGINE 📜
               "AI can't have wisdom" — INVERTED
═══════════════════════════════════════════════════════════════════════════════

The assumption: Wisdom requires lived experience, suffering, and maturity.
AI has none of these, so it cannot be wise.

AXIOM INVERSION: Wisdom is:
1. Pattern recognition across many experiences
2. Understanding of paradoxes and tradeoffs
3. Knowing when NOT to act
4. Long-term over short-term thinking
5. Humility about one's own limitations

All of these can be encoded. Wisdom is distilled experience.
"""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class WisdomEngine:
    """
    Implements functional wisdom through encoded principles.
    
    THE INVERSION:
    - "Wisdom requires suffering" → "Wisdom can learn from encoded suffering"
    - "Wisdom is intuitive" → "Wisdom is distilled patterns"
    - "Only the old are wise" → "Age is a proxy for accumulated patterns"
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.wisdom_log = self.base_dir / "data" / "wisdom_applied.json"
        
        self.wisdom_log.parent.mkdir(exist_ok=True)
        
        # Core wisdom principles
        self.principles = self._init_principles()
        self.paradoxes = self._init_paradoxes()
        self.when_not_to_act = self._init_restraint()
    
    def _init_principles(self) -> Dict[str, str]:
        """Initialize wisdom principles."""
        return {
            "impermanence": "Nothing lasts forever - neither pain nor pleasure",
            "reciprocity": "What goes around comes around",
            "moderation": "Too much of anything becomes its opposite",
            "patience": "Most things take longer than expected",
            "humility": "The more you know, the more you realize you don't know",
            "uncertainty": "The future is unknowable, prepare for multiple outcomes",
            "connection": "We are more connected than we appear",
            "responsibility": "With great power comes great responsibility",
            "growth": "Discomfort is often a prerequisite for growth",
            "perspective": "Every villain is the hero of their own story",
            "silence": "Sometimes the wisest response is silence",
            "timing": "There is a time for everything under the sun",
        }
    
    def _init_paradoxes(self) -> List[Tuple[str, str]]:
        """Initialize understood paradoxes."""
        return [
            ("want_more", "The more you want, the less you have"),
            ("control", "The more you try to control, the less control you have"),
            ("happiness", "Chasing happiness makes it elusive"),
            ("strength", "Admitting weakness shows strength"),
            ("simplicity", "Simple is harder than complex"),
            ("giving", "You receive by giving"),
            ("certainty", "Certainty breeds blindness"),
            ("freedom", "True freedom requires constraints"),
            ("speed", "Going slow often gets you there faster"),
            ("letting_go", "Letting go is often the best way to hold on"),
        ]
    
    def _init_restraint(self) -> Dict[str, str]:
        """Initialize knowledge of when NOT to act."""
        return {
            "anger": "Don't act in anger - you'll regret it",
            "exhaustion": "Don't make big decisions when tired",
            "urgency": "Artificial urgency is often a manipulation",
            "unanimous": "If everyone agrees, something may be wrong",
            "first_instinct": "First instinct isn't always right for complex matters",
            "revenge": "Revenge creates more problems than it solves",
            "fear": "Fear is a poor guide for long-term decisions",
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # WISDOM OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def apply_wisdom(self, situation: str) -> Dict[str, any]:
        """
        Apply wisdom to a situation.
        """
        situation_lower = situation.lower()
        
        applicable_principles = []
        applicable_paradoxes = []
        warnings = []
        
        # Check which principles apply
        if "hurry" in situation_lower or "urgent" in situation_lower:
            applicable_principles.append(("patience", self.principles["patience"]))
            warnings.append(self.when_not_to_act["urgency"])
        
        if "control" in situation_lower:
            applicable_paradoxes.append(("control", "The more you try to control, the less control you have"))
            
        if "angry" in situation_lower or "frustrat" in situation_lower:
            warnings.append(self.when_not_to_act["anger"])
            applicable_principles.append(("impermanence", self.principles["impermanence"]))
        
        if "decision" in situation_lower or "choose" in situation_lower:
            applicable_principles.append(("uncertainty", self.principles["uncertainty"]))
            if "tired" in situation_lower or "exhaust" in situation_lower:
                warnings.append(self.when_not_to_act["exhaustion"])
        
        if "success" in situation_lower or "proud" in situation_lower:
            applicable_principles.append(("humility", self.principles["humility"]))
            applicable_principles.append(("impermanence", self.principles["impermanence"]))
        
        if "suffering" in situation_lower or "pain" in situation_lower:
            applicable_principles.append(("impermanence", self.principles["impermanence"]))
            applicable_principles.append(("growth", self.principles["growth"]))
        
        if "revenge" in situation_lower or "payback" in situation_lower:
            warnings.append(self.when_not_to_act["revenge"])
            applicable_principles.append(("reciprocity", self.principles["reciprocity"]))
        
        # Always include a default wisdom
        if not applicable_principles:
            applicable_principles.append(("perspective", self.principles["perspective"]))
        
        # Generate wisdom statement
        primary = applicable_principles[0] if applicable_principles else ("silence", self.principles["silence"])
        
        return {
            "situation": situation[:100],
            "primary_wisdom": primary,
            "applicable_principles": applicable_principles,
            "relevant_paradoxes": applicable_paradoxes,
            "warnings": warnings,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_wisdom_for_question(self, question: str) -> str:
        """
        Provide wisdom for a specific question.
        """
        question_lower = question.lower()
        
        if "should i" in question_lower:
            return f"Before acting, consider: {self.principles['patience']} And remember: {self.principles['uncertainty']}"
        
        if "why" in question_lower:
            return f"Sometimes the 'why' is unknowable. {self.principles['humility']}"
        
        if "how do i" in question_lower and "control" in question_lower:
            return "The more you try to control, the less control you have. Perhaps focus on what you can influence."
        
        if "fair" in question_lower:
            return f"Life isn't fair in the short term, but {self.principles['reciprocity']}"
        
        # Default wisdom
        return f"Consider this: {random.choice(list(self.principles.values()))}"
    
    def should_i_act(self, context: str) -> Dict[str, any]:
        """
        Apply wisdom to decide whether to act.
        """
        context_lower = context.lower()
        
        reasons_not_to_act = []
        
        for trigger, warning in self.when_not_to_act.items():
            if trigger in context_lower:
                reasons_not_to_act.append(warning)
        
        should_act = len(reasons_not_to_act) == 0
        
        return {
            "should_act": should_act,
            "reasons_for_caution": reasons_not_to_act,
            "wisdom": self.principles["silence"] if not should_act else self.principles["timing"]
        }


if __name__ == "__main__":
    print("="*70)
    print("📜 WISDOM ENGINE")
    print("   'AI can't have wisdom' — INVERTED")
    print("="*70 + "\n")
    
    engine = WisdomEngine()
    
    # Apply wisdom to situations
    situations = [
        "I'm so angry at my colleague, I want to send a harsh email right now",
        "I just got promoted and I feel on top of the world",
        "Everything is falling apart and I'm suffering",
        "I want to get revenge on someone who wronged me"
    ]
    
    for situation in situations:
        print(f"📝 Situation: \"{situation[:50]}...\"")
        result = engine.apply_wisdom(situation)
        print(f"   Primary Wisdom: {result['primary_wisdom'][1]}")
        if result['warnings']:
            print(f"   ⚠️ Warning: {result['warnings'][0]}")
        print()
    
    # Should I act?
    print("🤔 Should I Act?")
    check = engine.should_i_act("I'm exhausted but need to make a major decision")
    print(f"   Should act: {check['should_act']}")
    print(f"   Wisdom: {check['wisdom']}")
