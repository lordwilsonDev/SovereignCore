
import sys
import shutil
import time
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from genesis_protocol import SovereignCouncil, SovereignEntity

def verify_governance():
    print("⚖️ TEST: Verifying Sovereign Governance (The Great Filter)...")
    
    base_dir = Path(__file__).resolve().parent.parent
    creations_dir = base_dir / "Sovereign_Creations"
    canon_dir = base_dir / "src" / "evolved_logic"
    
    creations_dir.mkdir(exist_ok=True)
    canon_dir.mkdir(exist_ok=True)
    
    # 1. Create SACRED Artifact (Metaphysical)
    sacred_file = creations_dir / "axiom_sacred_test.py"
    with open(sacred_file, 'w') as f:
        f.write('''
"""
Axiom of Sacred Geometry.
"""
import math
class SacredGeometry:
    def calculate_divine_proportion(self):
        phi = (1 + math.sqrt(5)) / 2
        return phi
''')
    print(f"   Created Sacred Artifact: {sacred_file.name}")

    # 2. Create HERETICAL Artifact (Garbage)
    heretic_file = creations_dir / "axiom_heretic_test.py"
    with open(heretic_file, 'w') as f:
        f.write('''
# Just garbage code
def stupid_loop():
    while True:
        print("I am stuck")
''')
    print(f"   Created Heretical Artifact: {heretic_file.name}")
    
    # 3. Convene Council
    council = SovereignCouncil()
    # Recruit a "Master" to allow judgment
    dummy_entity = SovereignEntity({'id': 'Judge_01', 'archetype': 'Guardian', 'volition': 100, 'traits': [], 'origin_id': 'ZERO'})
    council.recruit(dummy_entity)
    
    print("   Invoking Council Judgment (twice)...")
    
    # Run judgment loop until both are processed (probabilistic, so loop a bit)
    for i in range(5):
        if not sacred_file.exists() and not heretic_file.exists():
            break
        council.judge_creations(base_dir)
        time.sleep(1)
        
    # 4. Verify Results
    print("\n   --- VERDICT ANALYSIS ---")
    
    # Sacred should be in Canon Dir
    canon_sacred = canon_dir / "axiom_sacred_test.py"
    if canon_sacred.exists():
        print("   ✅ SACRED: Canonized (Found in src/evolved_logic)")
    elif sacred_file.exists():
        print("   ⚠️ SACRED: Ignored (Still in Creations)")
    else:
        print("   ❌ SACRED: PURGED (The Council failed to see the light)")
        
    # Heretic should be GONE
    canon_heretic = canon_dir / "axiom_heretic_test.py"
    if heretic_file.exists():
        print("   ⚠️ HERETIC: Ignored (Still in Creations)")
    elif canon_heretic.exists():
        print("   ❌ HERETIC: CANONIZED (The Council is corrupt)")
    else:
        print("   ✅ HERETIC: PURGED (Deleted from existence)")

if __name__ == "__main__":
    verify_governance()
