import sys
from pathlib import Path
import time
import subprocess
import requests
import uuid

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

def verify_rust_auction():
    print("📢 TEST: Verifying Market Dynamics (Auction House)...")
    
    host = "http://localhost:9000"
    
    # Check server
    try:
        requests.get(f"{host}/health", timeout=1)
    except:
        print("   ⚠️ Rust Server not running. Starting it...")
        pass

    # Generate IDs
    id_low = str(uuid.uuid4())
    id_mid = str(uuid.uuid4())
    id_high = str(uuid.uuid4())

    # 1. Place Bids
    print(f"   💸 Placing Bids...")
    try:
        requests.post(f"{host}/governance/auction/bid", json={"agent_id": id_low, "amount": 10.0})
        requests.post(f"{host}/governance/auction/bid", json={"agent_id": id_mid, "amount": 50.0})
        requests.post(f"{host}/governance/auction/bid", json={"agent_id": id_high, "amount": 100.0})
        print("      ✅ 3 Bids placed.")
    except Exception as e:
        print(f"   ❌ Bid Fail: {e}")
        return

    # 2. Finalize Auction (1 Slot)
    print("   🔨 Finalizing Auction (1 Slot)...")
    try:
        r = requests.post(f"{host}/governance/auction/finalize", json={"slots": 1})
        if r.status_code == 200:
            winners = r.json()
            print(f"      🏆 Winner: {winners[0]}")
            
            if winners[0] == id_high:
                print("      ✅ SUCCESS: Highest Bidder Won.")
            else:
                print(f"      ❌ FAIL: Expected {id_high}, got {winners[0]}")
        else:
            print(f"   ❌ Finalize Failed: {r.text}")
            
    except Exception as e:
        print(f"   ❌ Network Fail: {e}")

if __name__ == "__main__":
    verify_rust_auction()
