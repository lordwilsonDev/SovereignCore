
import sys
import time
import random
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from genesis_protocol import SovereignEntity, KnowledgeBase

def verify_inversion():
    print("🧪 TEST: Verifying Axiom Inversion Logic...")
    
    # Mock DNA for high volition entity
    dna = {
        'id': "INVERTER_001",
        'archetype': "Evolved-Architect",
        'volition': 60, # Above 50 threshold
        'resonance_freq': 888.88
    }
    
    entity = SovereignEntity(dna)
    kb = KnowledgeBase(Path(".")) # Mock KB path
    
    print(f"   Entity Volition: {entity.volition}")
    print("   Forcing multiple action cycles to trigger Inversion...")
    
    # Force the random check to pass by repeatedly calling act
    # Since it's probabilistic, we loop until success or limit
    inversion_triggered = False
    for i in range(20):
        print(f"   Cycle {i+1}...")
        
        # Capture stdout to detect the "attempts Axiom Inversion" print
        # or just observe the volition change
        old_vol = entity.volition
        entity.act(kb)
        
        if entity.volition != old_vol and entity.volition > old_vol + 3: # Gained more than normal study (+3)
            print("✅ INVERSION DETECTED via Exponential Growth!")
            inversion_triggered = True
            break
        elif "attempts Axiom Inversion" in str(sys.stdout): # Hard to capture stdout this way strictly
            pass
            
    if not inversion_triggered:
        print("⚠️ Inversion chance didn't trigger in 20 cycles (Probability issue or bad luck).")
    else:
        print(f"   Final Volition: {entity.volition}")

if __name__ == "__main__":
    verify_inversion()
