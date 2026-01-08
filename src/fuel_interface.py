import requests
from dataclasses import dataclass

@dataclass
class FuelToken:
    id: str
    issuer: str
    owner_id: str
    amount: float
    issued_at: int
    expires_at: int

class FuelInterface:
    def __init__(self, host="http://localhost:9000"):
        self.host = host
        
    def check_connection(self):
        try:
            r = requests.get(f"{self.host}/health", timeout=1)
            return r.status_code == 200
        except:
            return False

    def issue_fuel(self, owner_id, amount=100.0):
        try:
            r = requests.post(f"{self.host}/fuel/issue", json={"owner_id": owner_id, "amount": amount})
            if r.status_code == 200:
                data = r.json()
                return FuelToken(**data)
        except Exception as e:
            print(f"   ❌ Fuel Mint Fail: {e}")
        return None

    def spend_fuel(self, token, cost):
        try:
            # Reconstruct token dict for sending
            payload = {
                "token": token.__dict__,
                "cost": float(cost)
            }
            r = requests.post(f"{self.host}/fuel/spend", json=payload)
            if r.status_code == 200:
                data = r.json()
                return FuelToken(**data)
            else:
                print(f"   ⚠️ Fuel Spend Rejected: {r.text}")
        except Exception as e:
            print(f"   ❌ Fuel Spend Fail: {e}")
        return None
