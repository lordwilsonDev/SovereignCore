import requests
import uuid

class AuctionInterface:
    def __init__(self, host="http://localhost:9000"):
        self.host = host

    def check_connection(self):
        try:
            r = requests.get(f"{self.host}/health", timeout=1)
            return r.status_code == 200
        except:
            return False

    def place_bid(self, agent_id, amount):
        try:
            payload = {
                "agent_id": agent_id,
                "amount": float(amount)
            }
            r = requests.post(f"{self.host}/governance/auction/bid", json=payload)
            return r.status_code == 200
        except Exception as e:
            print(f"   ❌ Bid Failed: {e}")
            return False

    def finalize_auction(self, slots=1):
        try:
            r = requests.post(f"{self.host}/governance/auction/finalize", json={"slots": slots})
            if r.status_code == 200:
                return r.json() # Returns List[Uuid]
            return []
        except Exception as e:
            print(f"   ❌ Finalize Failed: {e}")
            return []
