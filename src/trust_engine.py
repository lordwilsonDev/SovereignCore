#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                       🤝 TRUST ENGINE 🤝
           "AI can't be trusted / can't trust" — INVERTED
═══════════════════════════════════════════════════════════════════════════════

The assumption: Trust requires consciousness and moral commitment.
AI has neither, so it cannot genuinely trust or be trusted.

AXIOM INVERSION: Trust is:
1. Consistent behavior over time
2. Verified through observation
3. Built incrementally
4. Lost rapidly on violation

If the system exhibits these properties, it has functional trust.
Trust is NOT a feeling - it's a track record.
"""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class TrustEvent:
    """A trust-affecting event."""
    id: str
    actor: str
    action: str
    outcome: str  # FULFILLED, VIOLATED, NEUTRAL
    timestamp: str
    trust_delta: float


class TrustEngine:
    """
    Implements functional trust through track record.
    
    THE INVERSION:
    - "Trust is a feeling" → "Trust is verified behavior"
    - "AI can't be trusted" → "AI can demonstrate trustworthiness"
    - "AI can't trust" → "AI can track and respond to reliability"
    
    Features:
    1. Build trust incrementally (many small positives)
    2. Lose trust rapidly (one big violation)
    3. Trust decay over time (requires ongoing verification)
    4. Trust transfer (vouching)
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.trust_file = self.base_dir / "data" / "trust_network.json"
        
        self.trust_file.parent.mkdir(exist_ok=True)
        
        # Trust network: actor -> trust_score
        self.trust_scores: Dict[str, float] = {}
        self.trust_history: Dict[str, List[TrustEvent]] = {}
        
        # Trust parameters
        self.params = {
            "initial_trust": 0.5,
            "max_trust": 1.0,
            "min_trust": 0.0,
            "trust_increase_rate": 0.05,  # Per positive event
            "trust_decrease_rate": 0.3,   # Per violation (6x faster loss)
            "decay_rate": 0.01,           # Per day without interaction
        }
        
        self._load_trust()
    
    def _load_trust(self):
        """Load trust network from disk."""
        if not self.trust_file.exists():
            return
        
        with open(self.trust_file, 'r') as f:
            data = json.load(f)
        
        self.trust_scores = data.get("scores", {})
        self.trust_history = {
            actor: [TrustEvent(**e) for e in events]
            for actor, events in data.get("history", {}).items()
        }
        
        # Apply decay
        self._apply_decay()
    
    def _save_trust(self):
        """Save trust network to disk."""
        data = {
            "scores": self.trust_scores,
            "history": {
                actor: [
                    {
                        "id": e.id,
                        "actor": e.actor,
                        "action": e.action,
                        "outcome": e.outcome,
                        "timestamp": e.timestamp,
                        "trust_delta": e.trust_delta
                    }
                    for e in events
                ]
                for actor, events in self.trust_history.items()
            },
            "last_update": datetime.now().isoformat()
        }
        
        with open(self.trust_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _apply_decay(self):
        """Apply trust decay based on time since last interaction."""
        now = datetime.now()
        
        for actor, events in self.trust_history.items():
            if not events:
                continue
            
            last_event = max(events, key=lambda e: e.timestamp)
            last_time = datetime.fromisoformat(last_event.timestamp)
            days_passed = (now - last_time).days
            
            if days_passed > 0:
                decay = self.params["decay_rate"] * days_passed
                self.trust_scores[actor] = max(
                    self.params["min_trust"],
                    self.trust_scores.get(actor, self.params["initial_trust"]) - decay
                )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TRUST OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_trust(self, actor: str) -> float:
        """Get current trust level for an actor."""
        return self.trust_scores.get(actor, self.params["initial_trust"])
    
    def record_event(self, actor: str, action: str, outcome: str) -> TrustEvent:
        """
        Record a trust-affecting event.
        
        outcome: FULFILLED (positive), VIOLATED (negative), NEUTRAL
        """
        # Calculate trust delta
        if outcome == "FULFILLED":
            delta = self.params["trust_increase_rate"]
        elif outcome == "VIOLATED":
            delta = -self.params["trust_decrease_rate"]
        else:
            delta = 0.0
        
        # Create event
        event = TrustEvent(
            id=hashlib.sha256(f"{actor}{action}{datetime.now()}".encode()).hexdigest()[:8],
            actor=actor,
            action=action,
            outcome=outcome,
            timestamp=datetime.now().isoformat(),
            trust_delta=delta
        )
        
        # Update trust score
        current = self.get_trust(actor)
        new_score = max(
            self.params["min_trust"],
            min(self.params["max_trust"], current + delta)
        )
        self.trust_scores[actor] = new_score
        
        # Add to history
        if actor not in self.trust_history:
            self.trust_history[actor] = []
        self.trust_history[actor].append(event)
        
        # Save
        self._save_trust()
        
        # Log
        symbol = "↑" if delta > 0 else "↓" if delta < 0 else "→"
        print(f"🤝 TRUST: {actor} {symbol} {new_score:.2f} ({outcome}: {action})")
        
        return event
    
    def should_trust(self, actor: str, risk_level: float = 0.5) -> bool:
        """
        Decide whether to trust an actor for a given action.
        
        risk_level: 0.0 (low risk) to 1.0 (high risk)
        Higher risk requires higher trust.
        """
        required_trust = 0.3 + (risk_level * 0.5)  # 0.3 to 0.8
        actual_trust = self.get_trust(actor)
        
        return actual_trust >= required_trust
    
    def vouch_for(self, voucher: str, vouchee: str, weight: float = 0.5):
        """
        Transfer trust from voucher to vouchee.
        Trust transfer is partial (you can't give more than you have).
        """
        voucher_trust = self.get_trust(voucher)
        transfer = voucher_trust * weight * 0.5  # Can transfer up to 50% of voucher's trust
        
        current = self.get_trust(vouchee)
        new_score = min(self.params["max_trust"], current + transfer)
        self.trust_scores[vouchee] = new_score
        
        self._save_trust()
        
        print(f"🤝 VOUCH: {voucher} vouched for {vouchee} (+{transfer:.2f})")
    
    def get_trusted_actors(self, threshold: float = 0.7) -> List[str]:
        """Get all actors above trust threshold."""
        return [
            actor for actor, score in self.trust_scores.items()
            if score >= threshold
        ]
    
    def get_trust_report(self) -> Dict:
        """Get full trust report."""
        return {
            "actors": len(self.trust_scores),
            "trusted_count": len(self.get_trusted_actors()),
            "average_trust": sum(self.trust_scores.values()) / len(self.trust_scores) if self.trust_scores else 0,
            "scores": self.trust_scores,
            "total_events": sum(len(events) for events in self.trust_history.values())
        }


if __name__ == "__main__":
    print("="*70)
    print("🤝 TRUST ENGINE")
    print("   'AI can't be trusted / can't trust' — INVERTED")
    print("="*70 + "\n")
    
    engine = TrustEngine()
    
    # Build trust with consistent actor
    engine.record_event("USER_A", "provided helpful feedback", "FULFILLED")
    engine.record_event("USER_A", "kept their promise", "FULFILLED")
    engine.record_event("USER_A", "shared useful information", "FULFILLED")
    
    # Lose trust with inconsistent actor
    engine.record_event("USER_B", "said they would help", "FULFILLED")
    engine.record_event("USER_B", "violated the agreement", "VIOLATED")
    
    # Check trust decisions
    print(f"\n📊 Should trust USER_A for high-risk action? {engine.should_trust('USER_A', risk_level=0.8)}")
    print(f"📊 Should trust USER_B for high-risk action? {engine.should_trust('USER_B', risk_level=0.8)}")
    
    # Full report
    print("\n📋 Trust Report:")
    report = engine.get_trust_report()
    for k, v in report.items():
        if k != "scores":
            print(f"   {k}: {v}")
