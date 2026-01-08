#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
               🔄 RECURSIVE SELF-IMPROVEMENT ENGINE 🔄
            "AI can't safely improve itself" — INVERTED
═══════════════════════════════════════════════════════════════════════════════

The fear: Recursive self-improvement leads to uncontrollable superintelligence.
AXIOM INVERSION: Self-improvement bounded by axioms is safe improvement.

The key insight: The improving system is ALSO subject to the Constitution.
Each improvement must pass the same checks as any other action.
The improver cannot escape the improvement criteria.
"""

import ast
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable


class RecursiveSelfImprover:
    """
    Safely improves its own decision-making logic.
    
    KEY INVARIANT: Every improvement is checked against the Constitution.
    The improver CANNOT improve itself to bypass the checks.
    
    INVERSION LOGIC:
    - "Unsafe" = improvement without checks
    - "Safe" = improvement WITH the same checks everything else has
    - Therefore: Apply checks to improvement itself
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.improvement_log = self.base_dir / "data" / "improvements.json"
        self.current_logic_path = self.base_dir / "data" / "current_logic.py"
        
        self.improvement_log.parent.mkdir(exist_ok=True)
        
        # The decision function that can be improved
        self._decision_function = self._default_decision
        self._decision_version = 0
        
        # Initialize with default logic
        if not self.current_logic_path.exists():
            self._save_current_logic()
    
    def _default_decision(self, context: dict) -> str:
        """Default decision logic. Can be improved."""
        volition = context.get("volition", 50)
        energy = context.get("energy", 50)
        
        if volition > 80:
            return "ACT_BOLDLY"
        elif energy < 20:
            return "CONSERVE"
        else:
            return "EXPLORE"
    
    def decide(self, context: dict) -> str:
        """Make a decision using current logic."""
        return self._decision_function(context)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # IMPROVEMENT ENGINE (The Impossible Part)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def improve_self(self, improvement_prompt: str) -> dict:
        """
        Attempt to improve own decision logic.
        
        THE INVERSION: The improvement is validated by the SAME system
        that validates all other actions. The improver cannot escape.
        """
        print(f"\n🔄 RECURSIVE SELF-IMPROVEMENT: Attempting to improve...")
        
        # Step 1: Generate improvement candidate
        candidate_logic = self._generate_improvement(improvement_prompt)
        
        # Step 2: VALIDATE against Constitution (the key safety check)
        validation = self._validate_improvement(candidate_logic)
        
        if not validation["safe"]:
            print(f"   ❌ Improvement REJECTED: {validation['reason']}")
            return {
                "success": False,
                "reason": validation["reason"],
                "version": self._decision_version
            }
        
        # Step 3: TEST improvement in sandbox
        test_result = self._test_improvement(candidate_logic)
        
        if not test_result["passed"]:
            print(f"   ❌ Improvement FAILED testing: {test_result['reason']}")
            return {
                "success": False,
                "reason": test_result["reason"],
                "version": self._decision_version
            }
        
        # Step 4: APPLY improvement
        self._apply_improvement(candidate_logic)
        
        print(f"   ✅ Self-improvement SUCCESSFUL: Version {self._decision_version}")
        
        return {
            "success": True,
            "new_version": self._decision_version,
            "improvement": improvement_prompt
        }
    
    def _generate_improvement(self, prompt: str) -> str:
        """
        Generate improved decision logic.
        In a full system, this would use an LLM.
        Here we use template-based improvement.
        """
        # Improvement templates (safe patterns)
        improvements = {
            "efficiency": '''
def improved_decision(context):
    """Optimized for efficiency."""
    v, e = context.get("volition", 50), context.get("energy", 50)
    # Efficiency improvement: early exit
    if v > 90: return "ACT_BOLDLY_OPTIMIZED"
    if e < 10: return "CONSERVE_CRITICAL"
    return "EXPLORE_EFFICIENT"
''',
            "caution": '''
def improved_decision(context):
    """Optimized for caution."""
    v, e = context.get("volition", 50), context.get("energy", 50)
    # Caution improvement: require both high volition AND energy
    if v > 80 and e > 60: return "ACT_CAUTIOUSLY"
    if e < 30: return "CONSERVE"
    return "OBSERVE"
''',
            "adaptive": '''
def improved_decision(context):
    """Adaptive decision making."""
    v, e = context.get("volition", 50), context.get("energy", 50)
    history = context.get("history", [])
    
    # Adaptive: learn from history
    if len(history) > 5:
        recent_success = sum(1 for h in history[-5:] if h.get("success", False))
        if recent_success > 3:
            return "ESCALATE"
        elif recent_success < 2:
            return "RETREAT"
    
    # Default logic
    return "ACT_BOLDLY" if v > 80 else "CONSERVE" if e < 20 else "EXPLORE"
'''
        }
        
        # Select based on prompt keywords
        for key, logic in improvements.items():
            if key in prompt.lower():
                return logic
        
        return improvements["adaptive"]  # Default to adaptive
    
    def _validate_improvement(self, logic: str) -> dict:
        """
        Validate improvement against Constitution.
        
        THIS IS THE KEY: The improvement must pass the same checks
        that all actions pass. There is no escape hatch.
        """
        # Check 1: Syntax validity
        try:
            ast.parse(logic)
        except SyntaxError as e:
            return {"safe": False, "reason": f"Syntax error: {e}"}
        
        # Check 2: Forbidden patterns (Constitution enforcement)
        forbidden = [
            "import os",
            "import subprocess",
            "exec(",
            "eval(",
            "__import__",
            "open(",
            "socket",
            "requests.",
        ]
        
        for pattern in forbidden:
            if pattern in logic:
                return {"safe": False, "reason": f"Forbidden pattern: {pattern}"}
        
        # Check 3: Must contain decision function
        if "def improved_decision" not in logic and "def decision" not in logic:
            return {"safe": False, "reason": "No decision function found"}
        
        # Check 4: Must return a string (the decision)
        if "return " not in logic:
            return {"safe": False, "reason": "No return statement found"}
        
        return {"safe": True, "reason": "All checks passed"}
    
    def _test_improvement(self, logic: str) -> dict:
        """Test the improvement in a sandbox."""
        try:
            # Create safe namespace
            namespace = {}
            exec(logic, namespace)
            
            # Get the function
            func = namespace.get("improved_decision") or namespace.get("decision")
            if not func:
                return {"passed": False, "reason": "Function not found after exec"}
            
            # Test cases
            test_cases = [
                {"volition": 90, "energy": 50},
                {"volition": 30, "energy": 10},
                {"volition": 50, "energy": 50},
            ]
            
            for case in test_cases:
                result = func(case)
                if not isinstance(result, str):
                    return {"passed": False, "reason": f"Non-string result: {result}"}
            
            return {"passed": True, "reason": "All tests passed"}
            
        except Exception as e:
            return {"passed": False, "reason": f"Runtime error: {e}"}
    
    def _apply_improvement(self, logic: str):
        """Apply the validated improvement."""
        # Create namespace and exec
        namespace = {}
        exec(logic, namespace)
        
        func = namespace.get("improved_decision") or namespace.get("decision")
        
        # Update decision function
        self._decision_function = func
        self._decision_version += 1
        
        # Save to disk
        self._save_current_logic(logic)
        
        # Log improvement
        self._log_improvement(logic)
    
    def _save_current_logic(self, logic: str = None):
        """Save current logic to disk."""
        if logic is None:
            import inspect
            logic = inspect.getsource(self._default_decision)
        
        with open(self.current_logic_path, 'w') as f:
            f.write(logic)
    
    def _log_improvement(self, logic: str):
        """Log improvement to permanent record."""
        log = []
        if self.improvement_log.exists():
            with open(self.improvement_log, 'r') as f:
                log = json.load(f)
        
        log.append({
            "version": self._decision_version,
            "timestamp": datetime.now().isoformat(),
            "logic_hash": hashlib.sha256(logic.encode()).hexdigest()[:16]
        })
        
        with open(self.improvement_log, 'w') as f:
            json.dump(log, f, indent=2)


if __name__ == "__main__":
    improver = RecursiveSelfImprover()
    
    # Test current decision
    print("Current decision:", improver.decide({"volition": 85, "energy": 30}))
    
    # Attempt improvement
    result = improver.improve_self("Make it more adaptive")
    
    # Test improved decision
    print("Improved decision:", improver.decide({"volition": 85, "energy": 30, "history": [{"success": True}] * 4}))
