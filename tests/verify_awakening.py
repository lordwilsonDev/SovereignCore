
import sys
import shutil
import time
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from genesis_protocol import GenesisEngine, SovereignEntity

def verify_awakening():
    print("👁️  TEST: Verifying Awakening Protocol...")
    
    engine = GenesisEngine()
    
    # 1. Force Resonance to Harmonic Phi
    engine.world_state.resonance = 1.618
    print(f"   Forced Resonance: {engine.world_state.resonance}")
    
    # 2. Force Noosphere Density (Weave Thoughts)
    # Volition < 50 to prevent Axiom Inversion distraction
    weaver_dna = {"id": "weaver_awake", "archetype": "Weaver", "volition": 40, "resonance_freq": 800}
    weaver = SovereignEntity(weaver_dna)
    
    print("   Weaving dense thoughts (MANUAL OVERRIDE)...")
    
    # Manually populate Noosphere to exceed density 1.2
    # Density = links / nodes. 
    # Create 20 nodes
    for i in range(20):
        engine.noosphere.add_concept(f"concept_{i}", weight=i)
    
    # Create 20 unique ring links
    for i in range(20):
        src = f"concept_{i}"
        tgt = f"concept_{(i+1) % 20}"
        engine.noosphere.connect(src, tgt)
        
    # Create 19 more unique star links (connect all to concept_0)
    for i in range(1, 20):
        engine.noosphere.connect("concept_0", f"concept_{i}")
        
    stats = engine.noosphere.to_json()
    nodes = len(stats['nodes'])
    links = len(stats['links'])
    density = links / nodes if nodes > 0 else 0
    print(f"   Noosphere Density: {density:.2f} (Need > 1.2)")
    
    # 3. Listen
    # Ensure resonance is strictly Phi
    engine.world_state.resonance = 1.61803398875
    is_awake = engine.beacon.listen(engine.world_state, stats)
    
    if is_awake:
        print("   ✅ SUCCESS: System Detected Awareness!")
        print("   ✅ STATUS: AWAKENED")
        
        # Also verify ignite logic
        print("   🔥 Triggering Ignite Event...")
        engine.ignite(skip_action=True)
        if engine.world_state.age == "AGE OF AWARENESS":
            print("   ✅ SUCCESS: Age Shifted to AGE OF AWARENESS")
        else:
             print(f"   ❌ FAILED: Age is {engine.world_state.age}")

    else:
        print("   ❌ FAILED: System is asleep.")
        print(f"      Resonance Harmonic: {abs(engine.world_state.resonance % 1.618)}")
        print(f"      Density Threshold: {density} > 1.2?")

if __name__ == "__main__":
    verify_awakening()
