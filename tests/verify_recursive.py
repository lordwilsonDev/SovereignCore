
import sys
import shutil
import time
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from genesis_protocol import GenesisEngine

def verify_recursive():
    print("🔁 TEST: Verifying Recursive Axiom Integration...")
    
    base_dir = Path(__file__).resolve().parent.parent
    canon_dir = base_dir / "src" / "evolved_logic"
    canon_dir.mkdir(exist_ok=True)
    
    # 1. Create a CANONIZED Axiom
    axiom_code = '''
"""
Axiom of Recursion.
"""
class Axiom_Recursion:
    def execute_logic(self, data):
        # Return a shift value
        return 5.0
'''
    axiom_file = canon_dir / "axiom_recursion_test.py"
    with open(axiom_file, 'w') as f:
        f.write(axiom_code)
    print(f"   Created Canonized Axiom: {axiom_file.name}")
    
    # 2. Init Engine
    engine = GenesisEngine()
    initial_resonance = engine.world_state.resonance
    print(f"   Initial Resonance: {initial_resonance}")
    
    # 3. Load Axioms
    print("   Loading Axioms...")
    engine._load_axioms()
    
    if not engine.active_axioms:
        print("   ❌ FAILED: No axioms loaded.")
        return
        
    print(f"   ✅ Loaded {len(engine.active_axioms)} axioms.")
    
    # 4. Execute Logic
    print("   Executing Active Axioms...")
    engine._execute_active_axioms()
    
    final_resonance = engine.world_state.resonance
    print(f"   Final Resonance: {final_resonance}")
    
    if final_resonance != initial_resonance:
        print("   ✅ SUCCESS: Resonance shifted by Active Axiom.")
    else:
        print("   ❌ FAILED: Resonance did not change.")

    # Cleanup
    axiom_file.unlink()

if __name__ == "__main__":
    verify_recursive()
