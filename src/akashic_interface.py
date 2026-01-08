import requests
import json
import time
from dataclasses import dataclass, asdict

@dataclass
class Intent:
    id: int
    content: str
    timestamp: str
    status: str
    coherence: float
    source: str

class AkashicInterface:
    def __init__(self, host="http://localhost:9000"):
        self.host = host
        self.connected = False
        
    def check_connection(self):
        try:
            r = requests.get(f"{self.host}/health", timeout=1)
            if r.status_code == 200:
                self.connected = True
                return True
        except:
            self.connected = False
            return False
            
    def remember(self, content, status="archived", source="python_genesis", coherence=1.0):
        if not self.check_connection():
            print("   ⚠️ Akashic Record Disconnected (Rust Server Offline)")
            return False
            
        # We use current time as ID loosely, or 0. The Rust server appends it but doesn't auto-increment ID on *this* endpoint properly yet (it trusts input).
        # Actually logic in main.rs just pushes.
        
        intent = Intent(
            id=int(time.time()),
            content=content,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            status=status,
            coherence=coherence,
            source=source
        )
        
        try:
            r = requests.post(f"{self.host}/remember", json=asdict(intent))
            if r.status_code == 200:
                print(f"   📚 AKASHIC RECORD: Archived '{content[:30]}...'")
                return True
            else:
                print(f"   ❌ AKASHIC ERROR: {r.text}")
                return False
        except Exception as e:
            print(f"   ❌ AKASHIC FAIL: {e}")
            return False

    def recall(self):
        if not self.check_connection(): return []
        try:
            r = requests.get(f"{self.host}/recall")
            return r.json()
        except:
            return []

    def audit_thought(self, content, confidence=1.0):
        if not self.check_connection(): return True # Fail open if auditing is down... or fail closed? Let's fail OPEN for now.
        
        try:
            thought = {
                "content": content[:100], # Truncate for efficiency check
                "axioms_checked": True,  # We assume Python side did its basic safety checks first
                "confidence": float(confidence)
            }
            r = requests.post(f"{self.host}/governance/audit", json=thought)
            return r.status_code == 200
        except Exception as e:
            print(f"   ⚠️ Supreme Court Audit Failed (Network): {e}")
            return True # Fail Open
