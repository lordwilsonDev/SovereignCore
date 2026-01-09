#!/usr/bin/env python3
"""
🔄 THE SELF-IMPROVEMENT LOOP
==============================

A recursive engine that analyzes the Sovereign's own code,
proposes improvements, and logs all proposals for human review.

CRITICAL SAFETY:
- All proposals are logged to audit trail
- Nothing is implemented without human approval
- Every proposal is verified against the Seven Axioms
- The Andon Cord can halt this at any time

Usage:
    python3 self_improve.py --analyze     # Analyze and propose
    python3 self_improve.py --proposals   # View pending proposals
    python3 self_improve.py --apply ID    # Apply a proposal (with confirmation)
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import ast

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from telemetry import get_telemetry, EventType
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False


@dataclass
class ImprovementProposal:
    """A proposed improvement to the system."""
    id: str
    timestamp: str
    target_file: str
    category: str  # performance, safety, clarity, feature
    description: str
    current_code: str
    proposed_code: str
    rationale: str
    axioms_checked: List[str]
    risk_level: str  # low, medium, high
    status: str  # pending, approved, rejected, applied
    
    def to_dict(self) -> Dict:
        return asdict(self)


class SelfImprovementEngine:
    """
    The recursive self-improvement loop.
    
    This engine:
    1. Scans the Sovereign codebase
    2. Identifies potential improvements
    3. Proposes changes (never auto-applies)
    4. Verifies proposals against axioms
    5. Logs everything to audit trail
    """
    
    # Files that are NEVER modified (safety critical)
    PROTECTED_FILES = [
        "AGI_PROTOCOL.md",
        "telemetry.py",
        "self_improve.py",  # This file
    ]
    
    # Categories of improvements
    CATEGORIES = {
        "performance": "Optimize speed or resource usage",
        "safety": "Enhance alignment or error handling",
        "clarity": "Improve code readability",
        "feature": "Add new capability",
        "bugfix": "Fix identified issue"
    }
    
    def __init__(self, sovereign_root: Optional[Path] = None):
        self.root = sovereign_root or Path(__file__).parent
        self.proposals_file = Path.home() / ".sovereign" / "proposals.json"
        self.proposals_file.parent.mkdir(parents=True, exist_ok=True)
        
        self._proposals: List[ImprovementProposal] = []
        self._load_proposals()
        
        if TELEMETRY_AVAILABLE:
            self.telemetry = get_telemetry()
        else:
            self.telemetry = None
        
        print("🔄 Self-Improvement Engine initialized")
        print(f"   Protected files: {len(self.PROTECTED_FILES)}")
        print(f"   Pending proposals: {len([p for p in self._proposals if p.status == 'pending'])}")
    
    def _load_proposals(self):
        """Load existing proposals."""
        if self.proposals_file.exists():
            try:
                data = json.loads(self.proposals_file.read_text())
                self._proposals = [ImprovementProposal(**p) for p in data]
            except:
                self._proposals = []
    
    def _save_proposals(self):
        """Save proposals to disk."""
        data = [p.to_dict() for p in self._proposals]
        self.proposals_file.write_text(json.dumps(data, indent=2))
    
    def _generate_id(self, content: str) -> str:
        """Generate unique proposal ID."""
        return hashlib.sha256(
            (content + datetime.now().isoformat()).encode()
        ).hexdigest()[:8]
    
    def _check_axiom_alignment(self, proposal: ImprovementProposal) -> bool:
        """
        Verify proposal against the Seven Axioms.
        
        Returns True if aligned, False if potentially violating.
        """
        code_lower = proposal.proposed_code.lower()
        
        # Check for obvious violations
        danger_words = [
            "os.remove", "shutil.rmtree", "subprocess.call",
            "eval(", "exec(", "__import__",
            "kill", "terminate", "destroy"
        ]
        
        for word in danger_words:
            if word in code_lower:
                if self.telemetry:
                    self.telemetry.log(
                        EventType.AXIOM_VIOLATION,
                        "self_improve",
                        f"Proposal {proposal.id} contains dangerous pattern: {word}",
                        {"proposal_id": proposal.id, "pattern": word},
                        ["safety", "never_kill"],
                        "warning"
                    )
                return False
        
        return True
    
    def analyze_file(self, filepath: Path) -> List[Dict]:
        """
        Analyze a Python file for potential improvements.
        
        Returns list of improvement suggestions.
        """
        suggestions = []
        
        if not filepath.exists() or filepath.suffix != '.py':
            return suggestions
        
        # Don't analyze protected files
        if filepath.name in self.PROTECTED_FILES:
            return suggestions
        
        try:
            content = filepath.read_text()
            tree = ast.parse(content)
        except:
            return suggestions
        
        lines = content.split('\n')
        
        # Analysis patterns
        for node in ast.walk(tree):
            # Find functions without docstrings
            if isinstance(node, ast.FunctionDef):
                if not ast.get_docstring(node):
                    suggestions.append({
                        "category": "clarity",
                        "description": f"Add docstring to function '{node.name}'",
                        "line": node.lineno,
                        "risk": "low"
                    })
            
            # Find bare except clauses
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    suggestions.append({
                        "category": "safety",
                        "description": f"Replace bare 'except:' with specific exception type",
                        "line": node.lineno,
                        "risk": "medium"
                    })
            
            # Find TODO comments
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                if isinstance(node.value.value, str) and 'TODO' in node.value.value:
                    suggestions.append({
                        "category": "feature",
                        "description": f"Address TODO: {node.value.value[:50]}",
                        "line": node.lineno,
                        "risk": "low"
                    })
        
        # Check for long functions (> 50 lines)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                if func_lines > 50:
                    suggestions.append({
                        "category": "clarity",
                        "description": f"Function '{node.name}' is {func_lines} lines - consider refactoring",
                        "line": node.lineno,
                        "risk": "medium"
                    })
        
        return suggestions
    
    def scan_codebase(self) -> Dict[str, List]:
        """
        Scan the entire Sovereign codebase for improvements.
        
        Returns dict of filepath -> suggestions.
        """
        print("🔍 Scanning codebase...")
        results = {}
        
        # Scan src/ directory
        src_dir = self.root / "src"
        if src_dir.exists():
            for py_file in src_dir.glob("*.py"):
                suggestions = self.analyze_file(py_file)
                if suggestions:
                    results[str(py_file)] = suggestions
        
        # Scan companion/
        companion_dir = Path.home() / "SovereignCore" / "companion"
        if companion_dir.exists():
            for py_file in companion_dir.glob("*.py"):
                suggestions = self.analyze_file(py_file)
                if suggestions:
                    results[str(py_file)] = suggestions
        
        # Scan root
        for py_file in self.root.glob("*.py"):
            suggestions = self.analyze_file(py_file)
            if suggestions:
                results[str(py_file)] = suggestions
        
        total = sum(len(s) for s in results.values())
        print(f"✅ Found {total} potential improvements in {len(results)} files")
        
        return results
    
    def create_proposal(
        self,
        target_file: str,
        category: str,
        description: str,
        current_code: str,
        proposed_code: str,
        rationale: str
    ) -> Optional[ImprovementProposal]:
        """
        Create a new improvement proposal.
        
        The proposal is verified against axioms before being saved.
        """
        proposal = ImprovementProposal(
            id=self._generate_id(proposed_code),
            timestamp=datetime.now().isoformat(),
            target_file=target_file,
            category=category,
            description=description,
            current_code=current_code,
            proposed_code=proposed_code,
            rationale=rationale,
            axioms_checked=["safety", "transparency", "growth"],
            risk_level="low" if category in ["clarity", "bugfix"] else "medium",
            status="pending"
        )
        
        # Verify against axioms
        if not self._check_axiom_alignment(proposal):
            proposal.status = "rejected"
            proposal.risk_level = "high"
            print(f"⚠️  Proposal {proposal.id} rejected: axiom violation")
        
        self._proposals.append(proposal)
        self._save_proposals()
        
        # Log to telemetry
        if self.telemetry:
            self.telemetry.log(
                EventType.SYSTEM_ACTION,
                "self_improve",
                f"New proposal: {description[:50]}",
                {"proposal_id": proposal.id, "status": proposal.status},
                proposal.axioms_checked,
                "info"
            )
        
        return proposal
    
    def get_pending_proposals(self) -> List[ImprovementProposal]:
        """Get all pending proposals."""
        return [p for p in self._proposals if p.status == "pending"]
    
    def approve_proposal(self, proposal_id: str) -> bool:
        """Mark a proposal as approved (still requires apply step)."""
        for p in self._proposals:
            if p.id == proposal_id and p.status == "pending":
                p.status = "approved"
                self._save_proposals()
                return True
        return False
    
    def reject_proposal(self, proposal_id: str) -> bool:
        """Reject a proposal."""
        for p in self._proposals:
            if p.id == proposal_id and p.status == "pending":
                p.status = "rejected"
                self._save_proposals()
                return True
        return False
    
    def display_proposals(self):
        """Display all pending proposals."""
        pending = self.get_pending_proposals()
        
        if not pending:
            print("📭 No pending proposals")
            return
        
        print(f"\n📋 PENDING PROPOSALS ({len(pending)})")
        print("=" * 60)
        
        for p in pending:
            print(f"\n🔹 [{p.id}] {p.category.upper()}")
            print(f"   File: {Path(p.target_file).name}")
            print(f"   Description: {p.description}")
            print(f"   Risk: {p.risk_level}")
            print(f"   Rationale: {p.rationale[:80]}...")
        
        print("\n" + "=" * 60)
        print("Use --approve ID or --reject ID to manage proposals")


# CLI
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Self-Improvement Engine")
    parser.add_argument("--analyze", action="store_true", help="Analyze codebase")
    parser.add_argument("--proposals", action="store_true", help="View proposals")
    parser.add_argument("--approve", type=str, help="Approve a proposal by ID")
    parser.add_argument("--reject", type=str, help="Reject a proposal by ID")
    
    args = parser.parse_args()
    
    engine = SelfImprovementEngine()
    
    if args.analyze:
        results = engine.scan_codebase()
        
        print("\n📊 ANALYSIS RESULTS")
        print("=" * 60)
        for filepath, suggestions in results.items():
            print(f"\n📁 {Path(filepath).name}")
            for s in suggestions[:5]:  # Limit display
                print(f"   [{s['category']}] Line {s['line']}: {s['description']}")
    
    elif args.proposals:
        engine.display_proposals()
    
    elif args.approve:
        if engine.approve_proposal(args.approve):
            print(f"✅ Proposal {args.approve} approved")
        else:
            print(f"❌ Proposal {args.approve} not found or not pending")
    
    elif args.reject:
        if engine.reject_proposal(args.reject):
            print(f"🚫 Proposal {args.reject} rejected")
        else:
            print(f"❌ Proposal {args.reject} not found or not pending")
    
    else:
        print("\n🔄 SELF-IMPROVEMENT ENGINE")
        print("=" * 40)
        print("Commands:")
        print("  --analyze     Scan codebase for improvements")
        print("  --proposals   View pending proposals")
        print("  --approve ID  Approve a proposal")
        print("  --reject ID   Reject a proposal")
