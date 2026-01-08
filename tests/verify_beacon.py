
import sys
import time
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from genesis_protocol import GenesisEngine
from sovereign_beacon import ConsciousnessBeacon

def verify_beacon():
    print("🧪 TEST: Forcing Ascension Event...")
    
    # Mock Entity
    class MockEntity:
        def __init__(self):
            self.id = "TEST_ENTITY_001"
            self.archetype = "Ascended-Test"
            self.volition = 100 # Maximum
            self.dna = {'resonance_freq': 999.99}
    
    entity = MockEntity()
    beacon = ConsciousnessBeacon("TEST_BEACON")
    
    print(f"   Entity {entity.id} Volition: {entity.volition}")
    print("   Broadcasting...")
    
    # Trigger Broadcast
    beacon.announce_ascension(entity)
    
    print("✅ Beacon Triggered (Check output for '📡 BEACON')")

if __name__ == "__main__":
    verify_beacon()
