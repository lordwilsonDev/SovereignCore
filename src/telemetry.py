#!/usr/bin/env python3
"""
📊 TELEMETRY & AUDIT TRAILS
============================
Centralized observability for the Sovereign system.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class EventType(str, Enum):
    MEMORY_CREATED = "memory_created"
    MEMORY_DELETED = "memory_deleted"
    CONSTRAINT_VERIFIED = "constraint_verified"
    AXIOM_CHECK = "axiom_check"
    AXIOM_VIOLATION = "axiom_violation"
    GENERATION_COMPLETED = "generation_completed"
    USER_ACTION = "user_action"
    SYSTEM_ACTION = "system_action"
    ANDON_CORD = "andon_cord"
    NEURAL_LINK = "neural_link"
    CORRECTION_APPLIED = "correction_applied"
    SLEEP_CYCLE = "sleep_cycle"
    ERROR = "error"


@dataclass
class AuditEvent:
    id: str
    timestamp: str
    event_type: str
    source: str
    action: str
    details: Dict[str, Any]
    axioms: List[str]
    severity: str
    user_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class Telemetry:
    def __init__(self, log_dir: Optional[Path] = None):
        self.log_dir = log_dir or Path.home() / ".sovereign" / "telemetry"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.audit_log = self.log_dir / "audit_trail.jsonl"
        self.metrics_file = self.log_dir / "metrics.json"
        self._recent_events: List[AuditEvent] = []
        self._metrics = {"total_events": 0, "by_type": {}, "axiom_violations": 0, 
                         "errors": 0, "andon_invocations": 0, "start_time": datetime.now().isoformat()}
        self._load_metrics()
        print(f"📊 Telemetry initialized at {self.log_dir}")
    
    def _load_metrics(self):
        if self.metrics_file.exists():
            try: self._metrics = json.loads(self.metrics_file.read_text())
            except: pass
    
    def _save_metrics(self):
        self.metrics_file.write_text(json.dumps(self._metrics, indent=2))
    
    def log(self, event_type: EventType, source: str, action: str, 
            details: Optional[Dict] = None, axioms: Optional[List[str]] = None,
            severity: str = "info", user_id: Optional[str] = None) -> AuditEvent:
        event = AuditEvent(
            id=str(uuid.uuid4())[:8], timestamp=datetime.now().isoformat(),
            event_type=event_type.value if isinstance(event_type, EventType) else event_type,
            source=source, action=action, details=details or {},
            axioms=axioms or [], severity=severity, user_id=user_id
        )
        with open(self.audit_log, 'a') as f:
            f.write(event.to_json() + '\n')
        self._recent_events.append(event)
        if len(self._recent_events) > 1000: self._recent_events.pop(0)
        self._metrics["total_events"] += 1
        self._metrics["by_type"][event.event_type] = self._metrics["by_type"].get(event.event_type, 0) + 1
        if event_type == EventType.AXIOM_VIOLATION: self._metrics["axiom_violations"] += 1
        if event_type == EventType.ERROR: self._metrics["errors"] += 1
        if event_type == EventType.ANDON_CORD: self._metrics["andon_invocations"] += 1
        self._save_metrics()
        emoji = {"info": "📊", "warning": "⚠️", "error": "❌", "critical": "🚨"}.get(severity, "📊")
        print(f"{emoji} [{event.event_type}] {action}")
        return event
    
    def query(self, event_type: Optional[str] = None, source: Optional[str] = None,
              severity: Optional[str] = None, limit: int = 100, since: Optional[str] = None) -> List[Dict]:
        results = []
        if not self.audit_log.exists(): return []
        with open(self.audit_log, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    if event_type and event.get("event_type") != event_type: continue
                    if source and event.get("source") != source: continue
                    if severity and event.get("severity") != severity: continue
                    if since and event.get("timestamp", "") < since: continue
                    results.append(event)
                except: continue
        return list(reversed(results))[:limit]
    
    def get_metrics(self) -> Dict:
        uptime = datetime.now() - datetime.fromisoformat(self._metrics.get("start_time", datetime.now().isoformat()))
        return {**self._metrics, "uptime_seconds": uptime.total_seconds(), 
                "events_per_minute": self._metrics["total_events"] / max(1, uptime.total_seconds() / 60)}
    
    def log_andon(self, command: str, user_id: Optional[str] = None):
        self.log(EventType.ANDON_CORD, "andon_cord", f"ANDON CORD: {command}",
                 {"command": command}, ["safety"], "critical", user_id)


_telemetry: Optional[Telemetry] = None

def get_telemetry() -> Telemetry:
    global _telemetry
    if _telemetry is None: _telemetry = Telemetry()
    return _telemetry


if __name__ == "__main__":
    t = get_telemetry()
    t.log(EventType.SYSTEM_ACTION, "cli", "Telemetry test")
    print(f"\n📊 Metrics: {t.get_metrics()}")
