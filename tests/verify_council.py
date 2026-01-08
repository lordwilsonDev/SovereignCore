
import sys
import time
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from genesis_protocol import GenesisEngine

def verify_council():
    print("🧪 TEST: Verifying Sovereign Council Governance...")
    
    engine = GenesisEngine()
    
    # Force add members to Council
    class MockEntity:
        def __init__(self, id, arch):
            self.id = id
            self.archetype = arch
            self.volition = 100
            self.dna = {'resonance_freq': 999}
            
    # Agenda: 2 Guardians (Order) vs 1 Void-Walker (Chaos)
    m1 = MockEntity("M_GUARD_1", "Guardian")
    m2 = MockEntity("M_GUARD_2", "Guardian")
    m3 = MockEntity("M_VOID_1", "Void-Walker")
    
    print("   Recruiting: 2 Guardians, 1 Void-Walker")
    engine.council.recruit(m1)
    engine.council.recruit(m2)
    engine.council.recruit(m3)
    
    # Run Analyze (Triggers Convene)
    print("   Convening Council...")
    engine._analyze_ancestors()
    
    print(f"   World State Age: {engine.world_state.age}")
    print(f"   Entropy Level: {engine.world_state.entropy_level}")
    
    if "Order" in engine.world_state.age:
        print("✅ Council Decree Successful (Order won)")
    else:
        print("❌ Council Decree Failed")

if __name__ == "__main__":
    verify_council()
