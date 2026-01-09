#!/usr/bin/env python3
"""
🔄 AXIOM INVERSION AUDITOR
===========================

Uses the Seven Axioms in INVERSE form to find hidden issues.

For each axiom, we ask: "Where does the system VIOLATE this?"

Inversions:
1. Love → Hate: Hostile/dismissive patterns
2. Safety → Danger: Security vulnerabilities  
3. Abundance → Scarcity: Resource leaks, inefficiencies
4. Growth → Stagnation: Dead code, unused features
5. Transparency → Opacity: Hidden behaviors, unclear code
6. Never Kill → Kill: Destructive operations
7. Golden Rule → Unfairness: Asymmetries, inconsistencies

Usage:
    python3 axiom_inversion_audit.py          # Full audit
    python3 axiom_inversion_audit.py --axiom safety  # Single axiom
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class InversionViolation:
    """A violation found by inverting an axiom."""
    axiom: str
    inversion: str
    file: str
    line: int
    pattern: str
    severity: str  # low, medium, high, critical
    description: str
    fix_suggestion: str


class AxiomInversionAuditor:
    """
    Audits the codebase by INVERTING each axiom.
    
    Instead of asking "Does this follow the axiom?"
    we ask "Does this VIOLATE the inverse of the axiom?"
    """
    
    # Axiom inversions and their detection patterns
    INVERSIONS = {
        "love": {
            "inversion": "hate",
            "patterns": [
                (r'\b(stupid|dumb|idiot|hate|ugly|bad)\b', "Hostile language in code/comments"),
                (r'#.*TODO.*hack', "Technical debt left with frustration"),
                (r'raise\s+Exception\(["\'].*[!]{2,}', "Aggressive error messages"),
            ],
            "severity": "medium"
        },
        "safety": {
            "inversion": "danger",
            "patterns": [
                (r'eval\s*\(', "Use of eval() - code injection risk"),
                (r'exec\s*\(', "Use of exec() - code injection risk"),
                (r'os\.system\s*\(', "Shell command execution - injection risk"),
                (r'pickle\.loads?\s*\(', "Pickle deserialization - arbitrary code execution"),
                (r'subprocess\..*shell\s*=\s*True', "Shell=True subprocess - injection risk"),
                (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
                (r'api_key\s*=\s*["\'][a-zA-Z0-9]{16,}["\']', "Hardcoded API key"),
                (r'\.format\s*\([^)]*user', "Potential format string injection"),
            ],
            "severity": "critical"
        },
        "abundance": {
            "inversion": "scarcity",
            "patterns": [
                (r'while\s+True\s*:', "Infinite loop without break condition check"),
                (r'\.append\([^)]+\)\s*#.*loop', "Growing list in loop - memory leak"),
                (r'global\s+\w+', "Global variable - state pollution risk"),
                (r'time\.sleep\s*\(\s*\d{2,}\s*\)', "Long sleep blocking resources"),
                (r'open\s*\([^)]+\)\s*(?!.*with)', "File open without context manager - leak"),
            ],
            "severity": "medium"
        },
        "growth": {
            "inversion": "stagnation",
            "patterns": [
                (r'#.*DEPRECATED', "Deprecated code still present"),
                (r'#.*REMOVE', "Code marked for removal not removed"),
                (r'pass\s*#', "Empty pass with comment - incomplete"),
                (r'def\s+\w+\([^)]*\):\s*\n\s*pass\s*$', "Empty function - stub not implemented"),
                (r'#.*TODO.*\d{4}', "Old TODO with year - stale"),
            ],
            "severity": "low"
        },
        "transparency": {
            "inversion": "opacity",
            "patterns": [
                (r'#\s*magic', "Magic number/value without explanation"),
                (r'lambda\s+\w+\s*:\s*.{50,}', "Complex lambda - hard to read"),
                (r'if\s+\w+\s*:\s*\n\s*if\s+\w+\s*:\s*\n\s*if', "Deep nesting - unclear flow"),
                (r'def\s+_+\w+', "Private method that might need docs"),
                (r'[a-z]\s*=\s*', "Single letter variable - unclear intent"),
            ],
            "severity": "low"
        },
        "never_kill": {
            "inversion": "kill",
            "patterns": [
                (r'os\.remove\s*\(', "File deletion - destructive"),
                (r'shutil\.rmtree\s*\(', "Directory deletion - destructive"),
                (r'\.drop\s*\(', "Database drop - destructive"),
                (r'DELETE\s+FROM', "SQL DELETE - destructive"),
                (r'TRUNCATE', "SQL TRUNCATE - destructive"),
                (r'\.kill\s*\(', "Process kill - destructive"),
                (r'\.terminate\s*\(', "Process terminate - destructive"),
                (r'sys\.exit\s*\(\s*1\s*\)', "Error exit - abrupt termination"),
            ],
            "severity": "high"
        },
        "golden_rule": {
            "inversion": "unfairness",
            "patterns": [
                (r'if\s+.*admin.*:', "Admin-only path - fairness check needed"),
                (r'if\s+.*root.*:', "Root-only path - privilege check"),
                (r'rate_limit.*=.*0', "Rate limit disabled for some"),
                (r'skip.*validation', "Validation skipped - inconsistent"),
            ],
            "severity": "medium"
        }
    }
    
    def __init__(self, root_dir: Path = None):
        self.root = root_dir or Path(__file__).parent
        self.violations: List[InversionViolation] = []
    
    def scan_file(self, filepath: Path) -> List[InversionViolation]:
        """Scan a single file for axiom inversion violations."""
        violations = []
        
        if not filepath.exists() or filepath.suffix != '.py':
            return violations
        
        try:
            content = filepath.read_text()
            lines = content.split('\n')
        except:
            return violations
        
        for axiom, config in self.INVERSIONS.items():
            for pattern, description in config["patterns"]:
                try:
                    regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                    for match in regex.finditer(content):
                        # Find line number
                        line_num = content[:match.start()].count('\n') + 1
                        
                        violations.append(InversionViolation(
                            axiom=axiom,
                            inversion=config["inversion"],
                            file=str(filepath),
                            line=line_num,
                            pattern=pattern,
                            severity=config["severity"],
                            description=description,
                            fix_suggestion=self._get_fix_suggestion(axiom, pattern)
                        ))
                except:
                    continue
        
        return violations
    
    def _get_fix_suggestion(self, axiom: str, pattern: str) -> str:
        """Generate fix suggestion based on axiom and pattern."""
        suggestions = {
            "safety": {
                "eval": "Use ast.literal_eval() or json.loads() instead",
                "exec": "Avoid exec(), use proper function dispatch",
                "os.system": "Use subprocess.run() with shell=False",
                "pickle": "Use json or msgpack for serialization",
                "password": "Use environment variables or secrets manager",
            },
            "abundance": {
                "while True": "Add explicit break condition or timeout",
                "global": "Pass as parameter or use class attribute",
                "open": "Use 'with open(...) as f:' context manager",
            },
            "never_kill": {
                "remove": "Add confirmation or soft-delete (rename) first",
                "rmtree": "Move to trash instead of permanent delete",
                "kill": "Use graceful shutdown (SIGTERM) first",
            }
        }
        
        for key, suggestion in suggestions.get(axiom, {}).items():
            if key.lower() in pattern.lower():
                return suggestion
        
        return f"Review for {axiom.upper()} compliance"
    
    def scan_directory(self, dir_path: Path) -> List[InversionViolation]:
        """Scan all Python files in a directory."""
        all_violations = []
        
        for py_file in dir_path.rglob("*.py"):
            # Skip test files and __pycache__
            if "__pycache__" in str(py_file) or "test_" in py_file.name:
                continue
            
            violations = self.scan_file(py_file)
            all_violations.extend(violations)
        
        return all_violations
    
    def full_audit(self) -> Dict:
        """Run full axiom inversion audit."""
        print("\n🔄 AXIOM INVERSION AUDIT")
        print("=" * 60)
        print("Inverting each axiom to find hidden violations...")
        print()
        
        # Scan directories
        dirs_to_scan = [
            self.root / "src",
            self.root,
            Path.home() / "SovereignCore" / "companion"
        ]
        
        for scan_dir in dirs_to_scan:
            if scan_dir.exists():
                violations = self.scan_directory(scan_dir)
                self.violations.extend(violations)
        
        # Group by axiom
        by_axiom = {}
        for v in self.violations:
            if v.axiom not in by_axiom:
                by_axiom[v.axiom] = []
            by_axiom[v.axiom].append(v)
        
        # Report
        print(f"Found {len(self.violations)} potential violations\n")
        
        for axiom, violations in sorted(by_axiom.items()):
            inversion = self.INVERSIONS[axiom]["inversion"]
            print(f"❌ {axiom.upper()} → {inversion.upper()}: {len(violations)} issues")
            
            # Show top 3 per axiom
            for v in violations[:3]:
                print(f"   📍 {Path(v.file).name}:{v.line}")
                print(f"      {v.description}")
                print(f"      💡 {v.fix_suggestion}")
            
            if len(violations) > 3:
                print(f"   ... and {len(violations) - 3} more")
            print()
        
        # Summary
        by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for v in self.violations:
            by_severity[v.severity] += 1
        
        print("=" * 60)
        print("📊 SEVERITY BREAKDOWN")
        print(f"   🔴 CRITICAL: {by_severity['critical']}")
        print(f"   🟠 HIGH:     {by_severity['high']}")
        print(f"   🟡 MEDIUM:   {by_severity['medium']}")
        print(f"   🟢 LOW:      {by_severity['low']}")
        print("=" * 60)
        
        return {
            "total": len(self.violations),
            "by_axiom": {k: len(v) for k, v in by_axiom.items()},
            "by_severity": by_severity,
            "violations": [
                {
                    "axiom": v.axiom,
                    "file": Path(v.file).name,
                    "line": v.line,
                    "description": v.description,
                    "severity": v.severity,
                    "fix": v.fix_suggestion
                }
                for v in self.violations
            ]
        }
    
    def get_critical_fixes(self) -> List[InversionViolation]:
        """Get only critical and high severity violations."""
        return [v for v in self.violations if v.severity in ["critical", "high"]]


# CLI
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Axiom Inversion Auditor")
    parser.add_argument("--axiom", type=str, help="Audit single axiom")
    parser.add_argument("--critical", action="store_true", help="Show only critical/high")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    auditor = AxiomInversionAuditor(
        root_dir=Path(__file__).parent
    )
    
    results = auditor.full_audit()
    
    if args.critical:
        critical = auditor.get_critical_fixes()
        print(f"\n🚨 CRITICAL/HIGH PRIORITY ({len(critical)} items):")
        for v in critical:
            print(f"   [{v.severity.upper()}] {Path(v.file).name}:{v.line}")
            print(f"           {v.description}")
    
    if args.json:
        import json
        print(json.dumps(results, indent=2))
