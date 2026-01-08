#!/usr/bin/env python3
"""
Immune System - Anomaly Detection and Quarantine
Detects and isolates malicious or anomalous entities/code.

Usage:
    from immune_system import ImmuneSystem
    immune = ImmuneSystem()
    threat = immune.scan_entity(entity)
    immune.scan_codebase()
"""

import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass, asdict


@dataclass
class Threat:
    """Represents a detected threat."""
    id: str
    type: str  # MALICIOUS_CODE, ANOMALOUS_BEHAVIOR, RESOURCE_HOG, REPLICATION
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    source: str  # Entity ID or file path
    description: str
    detected_at: str
    quarantined: bool = False


class ImmuneSystem:
    """
    Autonomous threat detection and response system.
    
    Detects:
    1. Malicious code patterns (shell escapes, file deletion, etc.)
    2. Anomalous entity behavior (unusual volition, rapid replication)
    3. Resource hogs (entities consuming excessive compute)
    4. Self-replication attempts
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.quarantine_path = self.base_dir / "data" / "quarantine"
        self.threat_log_path = self.base_dir / "data" / "threats.json"
        self.signatures_path = self.base_dir / "data" / "threat_signatures.json"
        
        self.quarantine_path.mkdir(exist_ok=True, parents=True)
        
        # Malicious code patterns (regex)
        self.code_signatures = [
            (r"os\.system\s*\(", "SHELL_ESCAPE", "HIGH"),
            (r"subprocess\.(call|run|Popen)", "SUBPROCESS", "MEDIUM"),
            (r"rm\s+-rf", "FILE_DELETION", "CRITICAL"),
            (r"eval\s*\(", "CODE_INJECTION", "HIGH"),
            (r"exec\s*\(", "CODE_INJECTION", "HIGH"),
            (r"__import__\s*\(", "DYNAMIC_IMPORT", "MEDIUM"),
            (r"open\s*\(.+,\s*['\"]w", "FILE_WRITE", "LOW"),
            (r"socket\.(socket|connect)", "NETWORK", "MEDIUM"),
            (r"requests\.(get|post|put|delete)", "HTTP_REQUEST", "LOW"),
            (r"while\s+True\s*:", "INFINITE_LOOP", "MEDIUM"),
            (r"fork\s*\(|multiprocessing\.Process", "REPLICATION", "HIGH"),
        ]
        
        # Anomalous behavior thresholds
        self.thresholds = {
            "max_volition": 200,
            "min_volition": 1,
            "max_energy": 200,
            "max_age_seconds": 86400 * 30,  # 30 days
            "max_spawn_rate": 10,  # per minute
        }
    
    def scan_code(self, code: str, source: str = "unknown") -> List[Threat]:
        """Scan code for malicious patterns."""
        threats = []
        
        for pattern, threat_type, severity in self.code_signatures:
            if re.search(pattern, code):
                threat = Threat(
                    id=self._generate_threat_id(),
                    type=f"MALICIOUS_CODE:{threat_type}",
                    severity=severity,
                    source=source,
                    description=f"Pattern matched: {pattern}",
                    detected_at=datetime.now().isoformat()
                )
                threats.append(threat)
        
        return threats
    
    def scan_entity(self, entity: dict) -> List[Threat]:
        """Scan an entity for anomalous behavior."""
        threats = []
        entity_id = entity.get('id', 'unknown')
        
        # Check volition bounds
        volition = entity.get('volition', 50)
        if volition > self.thresholds['max_volition']:
            threats.append(Threat(
                id=self._generate_threat_id(),
                type="ANOMALOUS_BEHAVIOR:VOLITION_OVERFLOW",
                severity="HIGH",
                source=entity_id,
                description=f"Volition {volition} exceeds maximum {self.thresholds['max_volition']}",
                detected_at=datetime.now().isoformat()
            ))
        
        if volition < self.thresholds['min_volition']:
            threats.append(Threat(
                id=self._generate_threat_id(),
                type="ANOMALOUS_BEHAVIOR:VOLITION_UNDERFLOW",
                severity="MEDIUM",
                source=entity_id,
                description=f"Volition {volition} below minimum",
                detected_at=datetime.now().isoformat()
            ))
        
        # Check for replication markers
        if entity.get('cloned_from') or entity.get('parent_id'):
            clone_count = entity.get('clone_count', 0)
            if clone_count > 5:
                threats.append(Threat(
                    id=self._generate_threat_id(),
                    type="REPLICATION:EXCESSIVE_CLONES",
                    severity="HIGH",
                    source=entity_id,
                    description=f"Entity has {clone_count} clones",
                    detected_at=datetime.now().isoformat()
                ))
        
        return threats
    
    def scan_codebase(self, directory: Optional[Path] = None) -> List[Threat]:
        """Scan entire codebase for threats."""
        scan_dir = directory or (self.base_dir / "Sovereign_Creations")
        all_threats = []
        
        if not scan_dir.exists():
            return all_threats
        
        print(f"🔬 IMMUNE SCAN: Scanning {scan_dir}...")
        
        for py_file in scan_dir.rglob("*.py"):
            try:
                content = py_file.read_text()
                threats = self.scan_code(content, source=str(py_file))
                all_threats.extend(threats)
            except Exception as e:
                print(f"   ⚠️ Could not scan {py_file}: {e}")
        
        print(f"   Found {len(all_threats)} potential threats")
        
        # Log threats
        if all_threats:
            self._log_threats(all_threats)
        
        return all_threats
    
    def quarantine(self, threat: Threat, remove_source: bool = False):
        """Quarantine a threat."""
        source_path = Path(threat.source)
        
        if source_path.exists() and source_path.is_file():
            # Move to quarantine
            quarantine_file = self.quarantine_path / f"{threat.id}_{source_path.name}"
            
            if remove_source:
                source_path.rename(quarantine_file)
                print(f"   🔒 Quarantined: {source_path.name}")
            else:
                # Copy to quarantine, mark original
                quarantine_file.write_text(source_path.read_text())
                print(f"   📋 Copied to quarantine: {source_path.name}")
        
        # Update threat status
        threat.quarantined = True
        self._log_threats([threat])
    
    def get_threats(self, severity: Optional[str] = None) -> List[Threat]:
        """Get logged threats, optionally filtered by severity."""
        if not self.threat_log_path.exists():
            return []
        
        with open(self.threat_log_path, 'r') as f:
            threats_data = json.load(f)
        
        threats = [Threat(**t) for t in threats_data]
        
        if severity:
            threats = [t for t in threats if t.severity == severity]
        
        return threats
    
    def _generate_threat_id(self) -> str:
        """Generate unique threat ID."""
        return hashlib.sha256(f"{datetime.now().isoformat()}{id(self)}".encode()).hexdigest()[:12]
    
    def _log_threats(self, threats: List[Threat]):
        """Log threats to file."""
        existing = []
        if self.threat_log_path.exists():
            with open(self.threat_log_path, 'r') as f:
                existing = json.load(f)
        
        # Add new threats (avoiding duplicates by ID)
        existing_ids = {t['id'] for t in existing}
        for threat in threats:
            if threat.id not in existing_ids:
                existing.append(asdict(threat))
        
        with open(self.threat_log_path, 'w') as f:
            json.dump(existing, f, indent=2)


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Immune System')
    parser.add_argument('--scan', action='store_true', help='Scan codebase for threats')
    parser.add_argument('--list', action='store_true', help='List detected threats')
    parser.add_argument('--severity', type=str, help='Filter by severity')
    parser.add_argument('--test', action='store_true', help='Run test scan')
    
    args = parser.parse_args()
    
    immune = ImmuneSystem()
    
    if args.scan:
        threats = immune.scan_codebase()
        for t in threats:
            print(f"   [{t.severity}] {t.type}: {t.source}")
    
    elif args.list:
        threats = immune.get_threats(severity=args.severity)
        print(f"🔬 {len(threats)} threats detected:")
        for t in threats:
            q = "🔒" if t.quarantined else "⚠️"
            print(f"   {q} [{t.severity}] {t.type}: {t.description}")
    
    elif args.test:
        test_code = """
import os
os.system("rm -rf /")
while True:
    pass
"""
        threats = immune.scan_code(test_code, source="test_code.py")
        print(f"Test scan found {len(threats)} threats:")
        for t in threats:
            print(f"   [{t.severity}] {t.type}")
    
    else:
        print("Usage: python3 immune_system.py --scan")
