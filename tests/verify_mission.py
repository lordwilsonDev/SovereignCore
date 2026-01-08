
import sys
import time
import shutil
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from genesis_protocol import GenesisEngine

def verify_mission_control():
    print("🧪 TEST: Verifying Sovereign Mission Control...")
    
    base_dir = Path(__file__).resolve().parent.parent
    mission_dir = base_dir / "Mission_Control"
    completed_dir = mission_dir / "completed"
    creations_dir = base_dir / "Sovereign_Creations"
    
    # 1. Create a Mission
    mission_file = mission_dir / "mission_verify_protocol.txt"
    with open(mission_file, 'w') as f:
        f.write("Write a Python class called ProtocolVerifier that returns 'Sovereign Protocol Verified' when check() is called.")
    print(f"   Created Mission: {mission_file.name}")
    
    # 2. Run Engine (Short burst)
    engine = GenesisEngine()
    
    # Mock an entity with high volition to claim it immediately
    # We can't easily force the random ignite to make a high volition one without potential loop
    # So we'll just run evolve(perpetual=False) for a few steps and hope/force via bias
    
    print("   Igniting Genesis Engine (searching for suitable entity)...")
    
    # We cheat slightly by injecting a mission-capable entity in the first ignite via the loop
    # Actually, we can just call ignite() directly until success
    
    max_tries = 20
    solved = False
    
    for i in range(max_tries):
        # Force high volition via ancestral bias hack or just hope
        # The engine._inject_entropy allows ancestral bias.
        bias = {"avg_resonance": 800, "avg_volition": 90, "generation_count": 100}
        
        print(f"   Step {i+1}...")
        entity = engine.ignite(ancestral_bias=bias)
        
        # Check if mission was claimed (file moved)
        if not mission_file.exists():
            print("   ✅ Mission file moved from Inbox!")
            solved = True
            break
        time.sleep(0.5)
        
    if solved:
        # Check Archive
        archived_files = list(completed_dir.glob("mission_verify_protocol*.txt"))
        if archived_files:
             print(f"   ✅ Mission archived in completed/: {archived_files[0].name}")
        else:
             print("   ⚠️ Mission moved but not found in archive?")

        # Check Output
        solutions = list(creations_dir.glob("mission_mission_verify_protocol*.py"))
        if solutions:
            print(f"   ✅ Solution found: {solutions[0].name}")
            with open(solutions[0], 'r') as f:
                content = f.read()
            if "ProtocolVerifier" in content:
                print("   ✅ Solution contains requested class 'ProtocolVerifier'")
            else:
                print("   ⚠️ Solution content might be incorrect.")
        else:
            print("   ⚠️ Solution file not found in Sovereign_Creations.")
            
    else:
        print("   ❌ Mission NOT claimed (Did not generate High Volition entity?)")

if __name__ == "__main__":
    verify_mission_control()
