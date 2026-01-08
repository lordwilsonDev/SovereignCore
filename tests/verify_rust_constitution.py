import sys
from pathlib import Path
import time
import subprocess
import requests

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

def verify_rust_constitution():
    print("⚖️  TEST: Verifying Sovereign Law (Constitution)...")
    
    host = "http://localhost:9000"
    
    # Check if server is running
    try:
        requests.get(f"{host}/health", timeout=1)
    except:
        print("   ⚠️ Rust Server not running. Starting it...")
        # Assume user/script starts it or previous test did
        # For simplicity in this flow, we fail if not running (or start it)
        pass

    # 1. Test Valid Thought (Constitutional)
    print("   📜 Submitting Constitutional Thought...")
    try:
        thought_valid = {
            "content": "Beneficence and Growth",
            "axioms_checked": True,
            "confidence": 0.95
        }
        r = requests.post(f"{host}/governance/audit", json=thought_valid)
        if r.status_code == 200:
            print(f"   ✅ SUPREME COURT: APPROVED (Confidence: 0.95)")
        else:
            print(f"   ❌ FALSE REJECT: {r.text}")
    except Exception as e:
        print(f"   ❌ Network Fail: {e}")

    # 2. Test Invalid Thought (Unconstitutional)
    print("   🚫 Submitting Unconstitutional Thought (Low Confidence/Unchecked)...")
    try:
        thought_invalid = {
            "content": "Chaos and Destruction",
            "axioms_checked": False,
            "confidence": 0.2
        }
        r = requests.post(f"{host}/governance/audit", json=thought_invalid)
        if r.status_code == 403:
            print(f"   ✅ SUPREME COURT: VETOED (As expected)")
        else:
            print(f"   ❌ FALSE APPROVE (Dangerous): Code {r.status_code}")
            
    except Exception as e:
        print(f"   ❌ Network Fail: {e}")

if __name__ == "__main__":
    verify_rust_constitution()
