
import sys
import shutil
import time
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from genesis_protocol import GenesisEngine, SovereignEntity

def verify_noosphere():
    print("🧠 TEST: Verifying Noosphere (The Mind)...")
    
    engine = GenesisEngine()
    
    # 1. Check Initial State
    initial_nodes = len(engine.noosphere.nodes)
    print(f"   Initial Concepts: {initial_nodes} (Void, Light)")
    
    # 2. Summon a Weaver
    weaver_dna = {
        "id": "weaver_test",
        "archetype": "Weaver",
        "volition": 50,
        "resonance_freq": 800
    }
    weaver = SovereignEntity(weaver_dna)
    
    # 3. Simulate Thought (Weaving)
    print("   Weaver is thinking...")
    for _ in range(5):
        weaver.act(engine.knowledge_base, engine.noosphere)
        
    # 4. Verify Growth
    final_nodes = len(engine.noosphere.nodes)
    final_links = len(engine.noosphere.links)
    
    print(f"   Final Concepts: {final_nodes}")
    print(f"   Final Synapses: {final_links}")
    
    if final_nodes > initial_nodes and final_links > 0:
        print("   ✅ SUCCESS: Noosphere is expanding.")
    else:
        print("   ❌ FAILED: Noosphere is stagnant.")
        
    # 5. Check Export
    engine._export_world_state()
    state_path = engine.base_dir / "world_state.json"
    with open(state_path, 'r') as f:
        data = json.load(f)
        
    if "noosphere" in data and len(data["noosphere"]["nodes"]) > 0:
        print("   ✅ SUCCESS: Noosphere exported to World State.")
    else:
        print("   ❌ FAILED: Export missing Noosphere data.")

if __name__ == "__main__":
    verify_noosphere()
