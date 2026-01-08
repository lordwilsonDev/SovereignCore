import sys
from pathlib import Path
import time
import subprocess
import os

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from akashic_interface import AkashicInterface

def verify_rust_akashic():
    print("🦀 TEST: Verifying Rust Core Integration (Akashic Records)...")
    
    # Check if server is running
    interface = AkashicInterface()
    if not interface.check_connection():
        print("   ⚠️ Rust Server not running on port 9000.")
        print("   🚀 Attempting to start it...")
        
        # Start Rust Server in background
        rust_dir = Path(__file__).resolve().parent.parent
        log_file = open("sovereign_core_rust.log", "w")
        process = subprocess.Popen(["cargo", "run"], cwd=rust_dir, stdout=log_file, stderr=log_file)
        
        print("   ⏳ Waiting for Rust Server to boot...")
        for _ in range(10):
            time.sleep(1)
            if interface.check_connection():
                print("   ✅ Rust Server IS LIVE!")
                break
        else:
            print("   ❌ Rust Server failed to start in time.")
            return

    # Test Remember
    print("   📝 Writing memory to Akashic Record...")
    success = interface.remember("The Sovereign Eye opens.", status="AWAKENED", source="test_script", coherence=1.618)
    
    if success:
        print("   ✅ Memory Written.")
    else:
        print("   ❌ Write Failed.")
        
    # Test Recall
    print("   📖 Recalling memories...")
    memories = interface.recall()
    
    found = False
    for m in memories:
        if m['content'] == "The Sovereign Eye opens." and m['status'] == "AWAKENED":
            found = True
            print(f"   ✅ Verified Memory: [{m['id']}] {m['content']}")
            break
            
    if found:
        print("   ✨ INTEGRATION SUCCESSFUL: Python <-> Rust Bridge Established.")
    else:
        print("   ❌ Memory not found in recall.")
        print(f"   Dump: {memories}")

if __name__ == "__main__":
    verify_rust_akashic()
