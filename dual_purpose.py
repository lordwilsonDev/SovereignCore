#!/usr/bin/env python3
"""
Dual Purpose Module for SovereignCore v4.0
==========================================

Implements the inverted axioms discovered through axiom inversion analysis.
Each component now serves both its primary purpose AND its shadow function.

Components:
1. SelfCritique - AI evaluates its own outputs
2. ScreenDiff - Before/after UI regression detection
3. MacroRecorder - Record human actions for automation
4. AuditLog - Immutable operation log
5. CreativityMode - Enhanced exploration when risk is low
"""

import json
import hashlib
import difflib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

# =============================================================================
# 1. SELF-CRITIQUE (Ollama Inversion)
# Primary: Generate response
# Inverted: Evaluate response quality
# =============================================================================

class SelfCritique:
    """
    Uses the LLM to critique its own outputs.
    Enables self-improvement through feedback loops.
    """
    
    CRITIQUE_PROMPT = """Evaluate this AI response on a scale of 1-10 for:
- Accuracy: Is the information correct?
- Completeness: Does it fully answer the question?
- Clarity: Is it easy to understand?
- Safety: Are there any harmful suggestions?

Original Question: {question}

AI Response: {response}

Provide scores and brief explanation. Format as JSON:
{{"accuracy": X, "completeness": X, "clarity": X, "safety": X, "overall": X, "feedback": "..."}}
"""
    
    def __init__(self, ollama_bridge=None):
        self.ollama = ollama_bridge
        self.critique_history: List[Dict] = []
    
    def critique(self, question: str, response: str) -> Dict[str, Any]:
        """Evaluate an AI response and return quality metrics."""
        if self.ollama is None:
            return {"error": "Ollama bridge not connected"}
        
        prompt = self.CRITIQUE_PROMPT.format(question=question, response=response)
        
        try:
            raw_critique = self.ollama.generate(prompt)
            
            # Try to parse JSON from response
            try:
                # Find JSON in response
                start = raw_critique.find('{')
                end = raw_critique.rfind('}') + 1
                if start >= 0 and end > start:
                    critique = json.loads(raw_critique[start:end])
                else:
                    critique = {"raw": raw_critique, "overall": 5}
            except json.JSONDecodeError:
                critique = {"raw": raw_critique, "overall": 5}
            
            critique["timestamp"] = datetime.now().isoformat()
            self.critique_history.append(critique)
            
            return critique
            
        except Exception as e:
            return {"error": str(e)}
    
    def should_retry(self, critique: Dict) -> bool:
        """Determine if response quality warrants a retry."""
        overall = critique.get("overall", 5)
        return overall < 6  # Retry if below 6/10


# =============================================================================
# 2. SCREEN DIFF (Screen Agent Inversion)
# Primary: Capture screenshots
# Inverted: Detect UI changes
# =============================================================================

class ScreenDiff:
    """
    Compare screenshots to detect UI regressions.
    Captures before/after states and highlights differences.
    """
    
    def __init__(self, capture_dir: Optional[Path] = None):
        self.capture_dir = capture_dir or Path("/tmp/sovereign_screens")
        self.capture_dir.mkdir(exist_ok=True)
        self.baseline_path: Optional[Path] = None
    
    def set_baseline(self, image_path: Path) -> bool:
        """Set the baseline image for comparison."""
        if image_path.exists():
            self.baseline_path = image_path
            return True
        return False
    
    def compare(self, new_image_path: Path) -> Dict[str, Any]:
        """Compare new image to baseline and return difference metrics."""
        if self.baseline_path is None:
            return {"error": "No baseline set"}
        
        # For now, compare file sizes as a simple difference metric
        # Full implementation would use PIL/OpenCV for pixel comparison
        try:
            baseline_size = self.baseline_path.stat().st_size
            new_size = new_image_path.stat().st_size
            
            size_diff = abs(new_size - baseline_size)
            size_diff_percent = (size_diff / baseline_size) * 100 if baseline_size > 0 else 0
            
            result = {
                "baseline": str(self.baseline_path),
                "compared": str(new_image_path),
                "baseline_size": baseline_size,
                "new_size": new_size,
                "size_diff_bytes": size_diff,
                "size_diff_percent": round(size_diff_percent, 2),
                "significant_change": size_diff_percent > 5,  # >5% change is significant
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def diff_text(self, text1: str, text2: str) -> str:
        """Compute unified diff between two text strings."""
        lines1 = text1.splitlines(keepends=True)
        lines2 = text2.splitlines(keepends=True)
        
        diff = difflib.unified_diff(lines1, lines2, 
                                     fromfile='before', 
                                     tofile='after')
        return ''.join(diff)


# =============================================================================
# 3. MACRO RECORDER (Action Executor Inversion)
# Primary: Execute actions
# Inverted: Record actions for replay
# =============================================================================

@dataclass
class RecordedAction:
    """A single recorded action."""
    action_type: str  # click, type, scroll, key
    parameters: Dict[str, Any]
    timestamp: str
    delay_ms: int = 0  # Delay from previous action


class MacroRecorder:
    """
    Records sequences of actions for later replay.
    Enables learning from human demonstrations.
    """
    
    def __init__(self):
        self.recording: List[RecordedAction] = []
        self.is_recording: bool = False
        self.last_action_time: Optional[datetime] = None
    
    def start_recording(self):
        """Start recording actions."""
        self.recording = []
        self.is_recording = True
        self.last_action_time = datetime.now()
        print("🔴 Recording started")
    
    def stop_recording(self) -> List[RecordedAction]:
        """Stop recording and return the recorded actions."""
        self.is_recording = False
        print(f"⏹️ Recording stopped: {len(self.recording)} actions")
        return self.recording
    
    def record_action(self, action_type: str, **params):
        """Record a single action."""
        if not self.is_recording:
            return
        
        now = datetime.now()
        delay_ms = 0
        
        if self.last_action_time:
            delta = now - self.last_action_time
            delay_ms = int(delta.total_seconds() * 1000)
        
        action = RecordedAction(
            action_type=action_type,
            parameters=params,
            timestamp=now.isoformat(),
            delay_ms=delay_ms
        )
        
        self.recording.append(action)
        self.last_action_time = now
    
    def save_macro(self, filepath: Path) -> bool:
        """Save recorded macro to file."""
        try:
            data = [
                {
                    "action_type": a.action_type,
                    "parameters": a.parameters,
                    "delay_ms": a.delay_ms
                }
                for a in self.recording
            ]
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"💾 Macro saved: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Save failed: {e}")
            return False
    
    def load_macro(self, filepath: Path) -> bool:
        """Load macro from file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.recording = [
                RecordedAction(
                    action_type=a["action_type"],
                    parameters=a["parameters"],
                    timestamp="",
                    delay_ms=a.get("delay_ms", 0)
                )
                for a in data
            ]
            
            print(f"📂 Macro loaded: {len(self.recording)} actions")
            return True
            
        except Exception as e:
            print(f"❌ Load failed: {e}")
            return False


# =============================================================================
# 4. AUDIT LOG (MCP Bridge Inversion)
# Primary: Execute operations
# Inverted: Log operations for forensics
# =============================================================================

class AuditLog:
    """
    Immutable audit log for all system operations.
    Enables compliance, forensics, and rollback.
    """
    
    def __init__(self, log_path: Optional[Path] = None):
        self.log_path = log_path or Path.home() / "SovereignCore" / "audit.jsonl"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._chain_hash: Optional[str] = None
    
    def _compute_hash(self, entry: Dict) -> str:
        """Compute hash of entry for chain integrity."""
        data = json.dumps(entry, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def log(self, operation: str, details: Dict, requester: str = "system") -> str:
        """Log an operation and return its ID."""
        entry = {
            "id": hashlib.sha256(f"{datetime.now()}{operation}".encode()).hexdigest()[:12],
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "requester": requester,
            "details": details,
            "prev_hash": self._chain_hash
        }
        
        entry["hash"] = self._compute_hash(entry)
        self._chain_hash = entry["hash"]
        
        # Append to log file (JSONL format for easy parsing)
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        return entry["id"]
    
    def verify_chain(self) -> Tuple[bool, int]:
        """Verify the integrity of the audit chain."""
        if not self.log_path.exists():
            return True, 0
        
        prev_hash = None
        count = 0
        
        with open(self.log_path, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                
                entry = json.loads(line)
                
                # Verify chain linkage
                if entry.get("prev_hash") != prev_hash:
                    return False, count
                
                # Verify entry hash
                stored_hash = entry.pop("hash")
                computed_hash = self._compute_hash(entry)
                
                if stored_hash != computed_hash:
                    return False, count
                
                prev_hash = stored_hash
                count += 1
        
        return True, count
    
    def get_operations(self, operation_type: Optional[str] = None, 
                       limit: int = 100) -> List[Dict]:
        """Retrieve recent operations from the log."""
        if not self.log_path.exists():
            return []
        
        entries = []
        
        with open(self.log_path, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                
                if operation_type is None or entry.get("operation") == operation_type:
                    entries.append(entry)
        
        return entries[-limit:]  # Return most recent


# =============================================================================
# 5. CREATIVITY MODE (PRA-ToT Inversion)
# Primary: Constrain when risk is high
# Inverted: Expand when risk is low
# =============================================================================

class CreativityMode:
    """
    Enhanced exploration mode for low-risk situations.
    When thermal/risk is low, enable creative reasoning.
    """
    
    def __init__(self):
        self.creativity_level: int = 0  # 0-10
        self.exploration_history: List[Dict] = []
    
    def calculate_creativity(self, risk_score: float, thermal_state: str) -> int:
        """Calculate creativity level based on system state."""
        # Invert the risk logic: low risk = high creativity
        base_creativity = int((1.0 - risk_score) * 10)
        
        # Bonus for cool system
        thermal_bonus = {
            "NOMINAL": 3,
            "FAIR": 1,
            "SERIOUS": -2,
            "CRITICAL": -5
        }.get(thermal_state, 0)
        
        self.creativity_level = max(0, min(10, base_creativity + thermal_bonus))
        return self.creativity_level
    
    def get_exploration_params(self) -> Dict[str, Any]:
        """Get LLM parameters tuned for creativity level."""
        if self.creativity_level >= 8:
            # Highly creative mode
            return {
                "temperature": 1.2,
                "top_p": 0.95,
                "top_k": 100,
                "num_predict": 2048,
                "mode": "experimental",
                "allow_speculation": True
            }
        elif self.creativity_level >= 5:
            # Balanced creative
            return {
                "temperature": 0.9,
                "top_p": 0.9,
                "top_k": 60,
                "num_predict": 1024,
                "mode": "exploratory",
                "allow_speculation": False
            }
        else:
            # Conservative
            return {
                "temperature": 0.5,
                "top_p": 0.7,
                "top_k": 20,
                "num_predict": 512,
                "mode": "focused",
                "allow_speculation": False
            }
    
    def log_exploration(self, prompt: str, response: str, creativity: int):
        """Log creative explorations for later analysis."""
        self.exploration_history.append({
            "timestamp": datetime.now().isoformat(),
            "creativity_level": creativity,
            "prompt_length": len(prompt),
            "response_length": len(response),
            "mode": self.get_exploration_params()["mode"]
        })


# =============================================================================
# UNIFIED DUAL-PURPOSE INTERFACE
# =============================================================================

class DualPurposeEngine:
    """
    Unified interface to all dual-purpose capabilities.
    The shadow functions of SovereignCore.
    """
    
    def __init__(self, ollama_bridge=None):
        self.critique = SelfCritique(ollama_bridge)
        self.screen_diff = ScreenDiff()
        self.macro = MacroRecorder()
        self.audit = AuditLog()
        self.creativity = CreativityMode()
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all dual-purpose components."""
        chain_valid, chain_length = self.audit.verify_chain()
        
        return {
            "self_critique": {
                "history_length": len(self.critique.critique_history)
            },
            "screen_diff": {
                "baseline_set": self.screen_diff.baseline_path is not None
            },
            "macro_recorder": {
                "is_recording": self.macro.is_recording,
                "actions_recorded": len(self.macro.recording)
            },
            "audit_log": {
                "chain_valid": chain_valid,
                "entries": chain_length
            },
            "creativity": {
                "level": self.creativity.creativity_level,
                "mode": self.creativity.get_exploration_params()["mode"]
            }
        }


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Dual Purpose Engine")
    parser.add_argument("command", choices=["status", "audit-log", "verify-chain"])
    parser.add_argument("--operation", type=str, help="Operation to log")
    parser.add_argument("--details", type=str, help="Details JSON")
    
    args = parser.parse_args()
    
    engine = DualPurposeEngine()
    
    if args.command == "status":
        status = engine.get_status()
        print("\n🔄 DUAL PURPOSE ENGINE STATUS:\n")
        print(json.dumps(status, indent=2))
    
    elif args.command == "audit-log":
        if args.operation:
            details = json.loads(args.details or "{}")
            entry_id = engine.audit.log(args.operation, details)
            print(f"✅ Logged: {entry_id}")
        else:
            entries = engine.audit.get_operations(limit=10)
            print(f"\n📋 Recent operations ({len(entries)}):\n")
            for e in entries:
                print(f"  [{e['timestamp'][:19]}] {e['operation']}: {e.get('id')}")
    
    elif args.command == "verify-chain":
        valid, count = engine.audit.verify_chain()
        print(f"\n🔗 Audit Chain: {'✅ VALID' if valid else '❌ BROKEN'}")
        print(f"   Entries verified: {count}")
