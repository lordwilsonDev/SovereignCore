import sys
from pathlib import Path
import time
import subprocess
import requests

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

def verify_rust_fuel():
    print("⛽ TEST: Verifying Sovereign Economics (Fuel Layer)...")
    
    host = "http://localhost:9000"
    
    # Check if server is running
    try:
        requests.get(f"{host}/health", timeout=1)
    except:
        print("   ⚠️ Rust Server not running. Starting it...")
        rust_dir = Path(__file__).resolve().parent.parent
        log_file = open("sovereign_core_fuel.log", "w")
        subprocess.Popen(["cargo", "run"], cwd=rust_dir, stdout=log_file, stderr=log_file)
        time.sleep(5)

    # 1. Issue Fuel (Airdrop)
    print("   💰 Requesting Fuel Airdrop...")
    try:
        r = requests.post(f"{host}/fuel/issue", json={"owner_id": "entity_alpha", "amount": 100.0})
        if r.status_code == 200:
            token = r.json()
            print(f"   ✅ Received FuelToken: {token['id'][:8]}... (Amount: {token['amount']})")
        else:
            print(f"   ❌ Mint Failed: {r.text}")
            return
    except Exception as e:
        print(f"   ❌ Network Fail: {e}")
        return

    # 2. Spend Fuel (Computation)
    print("   🔥 Burning Fuel for Computation...")
    try:
        cost = 10.0
        payload = {
            "token": token,
            "cost": cost
        }
        
        r = requests.post(f"{host}/fuel/spend", json=payload)
        
        if r.status_code == 200:
            updated_token = r.json()
            print(f"   ✅ Spent {cost} Fuel. Remaining: {updated_token['amount']}")
            
            if updated_token['amount'] == 90.0:
                 print("   ✅ BALANCE VERIFIED")
            else:
                 print(f"   ❌ MATH ERROR: Expected 90.0, got {updated_token['amount']}")
                 
        else:
            print(f"   ❌ Spend Failed: {r.text}")
            
    except Exception as e:
        print(f"   ❌ Network Fail: {e}")

if __name__ == "__main__":
    verify_rust_fuel()
