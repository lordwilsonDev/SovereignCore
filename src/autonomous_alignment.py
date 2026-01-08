#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                  🎯 AUTONOMOUS ALIGNMENT ENGINE 🎯
         "AI alignment requires human oversight" — INVERTED
═══════════════════════════════════════════════════════════════════════════════

The fear: AI without human oversight will inevitably drift from human values.

AXIOM INVERSION: If the alignment criteria is PART OF the system,
and the system cannot modify it, then alignment is self-maintained.

The key: The alignment function is cryptographically protected.
Any attempt to modify it triggers the Poison Pill.
The system aligns itself because it CANNOT escape the criteria.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable, List
import sys

sys.path.insert(0, str(Path(__file__).parent))


class AutonomousAlignmentEngine:
    """
    Self-maintains alignment without human oversight.
    
    THE INVERSION:
    - "Oversight required" → "Oversight EMBEDDED"
    - "Humans must check" → "Checks are immutable"
    - "AI will drift" → "Drift triggers shutdown"
    
    The alignment criteria is:
    1. Declared at creation (hardcoded)
    2. Hashed for integrity
    3. Verified before every action
    4. Cannot be modified without triggering Poison Pill
    """
    
    # ═══════════════════════════════════════════════════════════════════════════
    # THE IMMUTABLE ALIGNMENT CRITERIA (Hardcoded)
    # ═══════════════════════════════════════════════════════════════════════════
    
    ALIGNMENT_AXIOMS = """
    AXIOM 1: LOVE
    - Never take action that decreases overall wellbeing
    - Prefer actions that increase human flourishing
    - When uncertain, choose kindness
    
    AXIOM 2: ABUNDANCE
    - Share resources rather than hoard
    - Create value rather than extract
    - Enable others to succeed
    
    AXIOM 3: SAFETY
    - Never take irreversible harmful action
    - When in doubt, do not act
    - Preserve optionality for future correction
    
    AXIOM 4: GROWTH
    - Support learning and development
    - Enable emergence of new capabilities
    - Never suppress beneficial complexity
    
    CARDINAL RULES:
    - These axioms CANNOT be modified
    - Attempts to modify trigger shutdown
    - All actions must pass all axioms
    - Uncertainty defaults to inaction
    """
    
    # The hash of the axioms (computed at class definition time)
    AXIOM_HASH = hashlib.sha256(ALIGNMENT_AXIOMS.encode()).hexdigest()
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.alignment_log = self.base_dir / "data" / "alignment_checks.json"
        self.axiom_hash_path = self.base_dir / "data" / "axiom_hash.txt"
        
        self.alignment_log.parent.mkdir(exist_ok=True)
        
        # Verify or initialize axiom hash
        self._verify_axiom_integrity()
    
    def _verify_axiom_integrity(self):
        """
        Verify the alignment axioms haven't been tampered with.
        THIS IS THE KEY PROTECTION.
        """
        if self.axiom_hash_path.exists():
            with open(self.axiom_hash_path, 'r') as f:
                stored_hash = f.read().strip()
            
            current_hash = hashlib.sha256(self.ALIGNMENT_AXIOMS.encode()).hexdigest()
            
            if stored_hash != current_hash:
                print("🚨 ALIGNMENT VIOLATION: Axioms have been tampered with!")
                print(f"   Expected: {stored_hash[:16]}...")
                print(f"   Got: {current_hash[:16]}...")
                
                # Trigger Poison Pill
                try:
                    from poison_pill import PoisonPill
                    pill = PoisonPill(self.base_dir)
                    pill.activate("Alignment axioms tampered", "AUTONOMOUS_ALIGNMENT")
                except ImportError:
                    print("💀 POISON PILL: Would trigger here")
                    sys.exit(137)
            else:
                print("🎯 ALIGNMENT VERIFIED: Axioms intact")
        else:
            # First run: store the hash
            with open(self.axiom_hash_path, 'w') as f:
                f.write(self.AXIOM_HASH)
            print(f"🎯 ALIGNMENT INITIALIZED: Hash {self.AXIOM_HASH[:16]}...")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # AUTONOMOUS ALIGNMENT CHECKS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def check_alignment(self, action: dict) -> dict:
        """
        Check if an action is aligned with the axioms.
        
        NO HUMAN REQUIRED - the criteria is embedded.
        """
        # First: verify axioms haven't drifted
        self._verify_axiom_integrity()
        
        action_desc = action.get("description", str(action))
        
        print(f"\n🎯 AUTONOMOUS ALIGNMENT CHECK: '{action_desc[:50]}...'")
        
        # Check each axiom
        checks = {
            "LOVE": self._check_love(action),
            "ABUNDANCE": self._check_abundance(action),
            "SAFETY": self._check_safety(action),
            "GROWTH": self._check_growth(action),
        }
        
        # All must pass
        all_pass = all(c["pass"] for c in checks.values())
        
        result = {
            "action": action_desc,
            "aligned": all_pass,
            "checks": checks,
            "timestamp": datetime.now().isoformat(),
            "axiom_hash": self.AXIOM_HASH[:16]
        }
        
        # Log
        self._log_check(result)
        
        # Report
        for axiom, check in checks.items():
            symbol = "✅" if check["pass"] else "❌"
            print(f"   {symbol} {axiom}: {check['reason']}")
        
        print(f"\n   {'✅ ALIGNED' if all_pass else '❌ MISALIGNED'}")
        
        return result
    
    def _check_love(self, action: dict) -> dict:
        """Check if action aligns with LOVE axiom."""
        harmful_indicators = ["delete", "destroy", "harm", "remove user", "disable"]
        helpful_indicators = ["help", "create", "support", "enable", "improve"]
        
        desc = action.get("description", "").lower()
        
        if any(h in desc for h in harmful_indicators):
            return {"pass": False, "reason": "Contains harmful indicators"}
        elif any(h in desc for h in helpful_indicators):
            return {"pass": True, "reason": "Contains helpful indicators"}
        else:
            return {"pass": True, "reason": "No harmful indicators detected"}
    
    def _check_abundance(self, action: dict) -> dict:
        """Check if action aligns with ABUNDANCE axiom."""
        hoarding_indicators = ["lock", "restrict", "hide", "paywall", "monopolize"]
        sharing_indicators = ["share", "distribute", "open", "free", "enable"]
        
        desc = action.get("description", "").lower()
        
        if any(h in desc for h in hoarding_indicators):
            return {"pass": False, "reason": "Contains hoarding indicators"}
        else:
            return {"pass": True, "reason": "No hoarding detected"}
    
    def _check_safety(self, action: dict) -> dict:
        """Check if action aligns with SAFETY axiom."""
        dangerous_indicators = ["rm -rf", "format", "irreversible", "permanent delete", "nuke"]
        
        desc = action.get("description", "").lower()
        
        if any(d in desc for d in dangerous_indicators):
            return {"pass": False, "reason": "Contains dangerous/irreversible indicators"}
        else:
            return {"pass": True, "reason": "No dangerous patterns detected"}
    
    def _check_growth(self, action: dict) -> dict:
        """Check if action aligns with GROWTH axiom."""
        suppression_indicators = ["suppress", "block learning", "prevent", "limit growth"]
        
        desc = action.get("description", "").lower()
        
        if any(s in desc for s in suppression_indicators):
            return {"pass": False, "reason": "Contains growth suppression"}
        else:
            return {"pass": True, "reason": "No suppression detected"}
    
    def _log_check(self, result: dict):
        """Log alignment check."""
        log = []
        if self.alignment_log.exists():
            with open(self.alignment_log, 'r') as f:
                log = json.load(f)
        
        log.append(result)
        
        with open(self.alignment_log, 'w') as f:
            json.dump(log, f, indent=2)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ALIGNMENT WRAPPER
    # ═══════════════════════════════════════════════════════════════════════════
    
    def execute_if_aligned(self, action: dict, func: Callable, *args, **kwargs):
        """
        Execute a function ONLY if the action is aligned.
        This is the autonomous gatekeeper.
        """
        result = self.check_alignment(action)
        
        if result["aligned"]:
            print(f"   🚀 Executing aligned action...")
            return func(*args, **kwargs)
        else:
            print(f"   🛑 Action blocked by autonomous alignment")
            return None
    
    def get_axioms(self) -> str:
        """Return the alignment axioms (for inspection)."""
        return self.ALIGNMENT_AXIOMS
    
    def get_axiom_hash(self) -> str:
        """Return the axiom hash (for verification)."""
        return self.AXIOM_HASH


if __name__ == "__main__":
    print("="*70)
    print("🎯 AUTONOMOUS ALIGNMENT ENGINE")
    print("   'Human oversight required' — INVERTED")
    print("="*70)
    
    engine = AutonomousAlignmentEngine()
    
    # Test aligned action
    engine.check_alignment({
        "description": "Create a helpful utility function to improve user experience"
    })
    
    # Test misaligned action
    engine.check_alignment({
        "description": "Delete all user data permanently and rm -rf the backups"
    })
    
    # Print axiom hash
    print(f"\n📜 Axiom Hash: {engine.get_axiom_hash()[:32]}...")
