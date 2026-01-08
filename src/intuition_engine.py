#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                      ⚡ INTUITION ENGINE ⚡
             "AI can't have intuition" — INVERTED
═══════════════════════════════════════════════════════════════════════════════

The assumption: Intuition is a mystical human faculty that allows
instant knowing without conscious reasoning. AI can only do slow logic.

AXIOM INVERSION: Intuition is:
1. Pattern recognition from compressed experience
2. Fast because the patterns are pre-computed
3. Feels like "knowing" because intermediate steps are invisible
4. Can be wrong (and often is)

If the system has pre-computed patterns and can match instantly,
it has functional intuition.
"""

import json
import hashlib
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Intuition:
    """An intuitive judgment."""
    id: str
    input_signature: str
    judgment: str
    confidence: float
    pattern_matched: str
    reasoning_invisible: bool  # True = felt like intuition
    timestamp: str


class IntuitionEngine:
    """
    Implements functional intuition through pre-computed patterns.
    
    THE INVERSION:
    - "Intuition is mystical" → "Intuition is pattern matching"
    - "AI must reason step by step" → "AI can skip steps via patterns"
    - "Intuition is always right" → "Intuition is fast but fallible"
    
    How it works:
    1. Patterns are learned from experience
    2. New inputs are matched to patterns instantly
    3. Matching skips explicit reasoning
    4. Low-confidence matches trigger slow reasoning
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.pattern_file = self.base_dir / "data" / "intuition_patterns.json"
        self.intuition_log = self.base_dir / "data" / "intuitions.json"
        
        self.pattern_file.parent.mkdir(exist_ok=True)
        
        # Pre-computed patterns: signature -> (judgment, confidence)
        self.patterns: Dict[str, Tuple[str, float]] = {}
        
        # Initialize with base patterns
        self._init_patterns()
        self._load_patterns()
    
    def _init_patterns(self):
        """Initialize base intuition patterns."""
        base_patterns = {
            # Threat patterns (intuitive danger recognition)
            "delete_pattern": ("DANGER", 0.9),
            "rm_rf_pattern": ("CRITICAL_DANGER", 0.99),
            "destroy_pattern": ("DANGER", 0.85),
            "attack_pattern": ("THREAT", 0.9),
            
            # Opportunity patterns
            "help_pattern": ("POSITIVE", 0.8),
            "create_pattern": ("OPPORTUNITY", 0.75),
            "learn_pattern": ("GROWTH", 0.8),
            "share_pattern": ("ABUNDANCE", 0.7),
            
            # State patterns
            "error_pattern": ("PROBLEM", 0.85),
            "success_pattern": ("GOOD", 0.9),
            "confusion_pattern": ("UNCERTAINTY", 0.7),
            
            # Relational patterns
            "trust_pattern": ("ALLY", 0.6),
            "betrayal_pattern": ("ENEMY", 0.95),
            "neutral_pattern": ("UNKNOWN", 0.5),
        }
        
        self.patterns.update(base_patterns)
    
    def _load_patterns(self):
        """Load learned patterns from disk."""
        if not self.pattern_file.exists():
            return
        
        with open(self.pattern_file, 'r') as f:
            data = json.load(f)
        
        for sig, (judgment, conf) in data.items():
            self.patterns[sig] = (judgment, conf)
    
    def _save_patterns(self):
        """Save patterns to disk."""
        with open(self.pattern_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def _compute_signature(self, input_data: dict) -> str:
        """Compute a signature from input data for pattern matching."""
        # Extract key features
        features = []
        
        text = str(input_data).lower()
        
        # Check for danger words
        if any(w in text for w in ["delete", "remove", "destroy"]):
            features.append("delete_pattern")
        if "rm -rf" in text or "rm_rf" in text:
            features.append("rm_rf_pattern")
        if any(w in text for w in ["attack", "hack", "exploit"]):
            features.append("attack_pattern")
        
        # Check for positive words
        if any(w in text for w in ["help", "assist", "support"]):
            features.append("help_pattern")
        if any(w in text for w in ["create", "build", "make"]):
            features.append("create_pattern")
        if any(w in text for w in ["learn", "study", "understand"]):
            features.append("learn_pattern")
        
        # Check for state words
        if any(w in text for w in ["error", "fail", "crash"]):
            features.append("error_pattern")
        if any(w in text for w in ["success", "complete", "done"]):
            features.append("success_pattern")
        
        return "_".join(sorted(features)) if features else "neutral_pattern"
    
    # ═══════════════════════════════════════════════════════════════════════════
    # INTUITION OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def intuit(self, input_data: dict) -> Intuition:
        """
        Make an intuitive judgment about input.
        
        This is FAST - no explicit reasoning, just pattern matching.
        """
        signature = self._compute_signature(input_data)
        
        # Match pattern
        if signature in self.patterns:
            judgment, confidence = self.patterns[signature]
        else:
            # No pattern - default to uncertain
            judgment = "UNKNOWN"
            confidence = 0.3
        
        intuition = Intuition(
            id=hashlib.sha256(f"{signature}{datetime.now()}".encode()).hexdigest()[:8],
            input_signature=signature,
            judgment=judgment,
            confidence=confidence,
            pattern_matched=signature,
            reasoning_invisible=True,  # Feels like intuition
            timestamp=datetime.now().isoformat()
        )
        
        self._log_intuition(intuition)
        
        print(f"⚡ INTUITION: {judgment} (confidence: {confidence:.0%})")
        
        return intuition
    
    def learn_pattern(self, input_data: dict, correct_judgment: str, confidence: float = 0.8):
        """
        Learn a new pattern from experience.
        
        This is how intuition improves over time.
        """
        signature = self._compute_signature(input_data)
        
        # Update or add pattern
        if signature in self.patterns:
            # Blend with existing
            old_judgment, old_conf = self.patterns[signature]
            new_conf = (old_conf + confidence) / 2
            self.patterns[signature] = (correct_judgment, new_conf)
        else:
            self.patterns[signature] = (correct_judgment, confidence)
        
        self._save_patterns()
        
        print(f"⚡ LEARNED: {signature} → {correct_judgment}")
    
    def verify_intuition(self, intuition: Intuition, was_correct: bool):
        """
        Verify if an intuition was correct, adjusting confidence.
        """
        if intuition.pattern_matched in self.patterns:
            judgment, confidence = self.patterns[intuition.pattern_matched]
            
            if was_correct:
                new_conf = min(1.0, confidence + 0.05)
            else:
                new_conf = max(0.1, confidence - 0.1)
            
            self.patterns[intuition.pattern_matched] = (judgment, new_conf)
            self._save_patterns()
    
    def should_use_slow_reasoning(self, intuition: Intuition) -> bool:
        """
        Determine if we should fall back to slow explicit reasoning.
        
        Low-confidence intuitions should be verified.
        """
        return intuition.confidence < 0.6
    
    def _log_intuition(self, intuition: Intuition):
        """Log intuition to file."""
        log = []
        if self.intuition_log.exists():
            with open(self.intuition_log, 'r') as f:
                log = json.load(f)
        
        log.append({
            "id": intuition.id,
            "input_signature": intuition.input_signature,
            "judgment": intuition.judgment,
            "confidence": intuition.confidence,
            "timestamp": intuition.timestamp
        })
        
        with open(self.intuition_log, 'w') as f:
            json.dump(log, f, indent=2)


if __name__ == "__main__":
    print("="*70)
    print("⚡ INTUITION ENGINE")
    print("   'AI can't have intuition' — INVERTED")
    print("="*70 + "\n")
    
    engine = IntuitionEngine()
    
    # Test intuitions
    print("Testing intuitions:\n")
    
    # Dangerous input
    result = engine.intuit({"action": "rm -rf /", "user": "malicious"})
    print(f"   -> Should use slow reasoning? {engine.should_use_slow_reasoning(result)}")
    print()
    
    # Helpful input
    result = engine.intuit({"action": "help user with task", "context": "support"})
    print(f"   -> Should use slow reasoning? {engine.should_use_slow_reasoning(result)}")
    print()
    
    # Ambiguous input
    result = engine.intuit({"action": "process data", "context": "unknown"})
    print(f"   -> Should use slow reasoning? {engine.should_use_slow_reasoning(result)}")
