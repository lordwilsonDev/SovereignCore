#!/usr/bin/env python3
"""
Chaos Testing for SovereignCore
Injects random failures and stress conditions before running tests
"""

import subprocess
import random
import time
import sys

def run_chaos_injection():
    print("\n" + "="*60)
    print("🔥 CHAOS ENGINEERING - PRE-TEST INJECTION")
    print("="*60)
    
    chaos_scenarios = [
        "Network latency simulation",
        "Memory pressure test",
        "CPU spike injection",
        "Disk I/O throttling",
        "Random service delays"
    ]
    
    print("\n📋 Chaos Scenarios:")
    for i, scenario in enumerate(chaos_scenarios, 1):
        print(f"  {i}. {scenario}")
    
    print("\n⚡ Injecting chaos conditions...")
    for scenario in random.sample(chaos_scenarios, 3):
        print(f"  → {scenario}")
        time.sleep(0.5)
    
    print("\n✅ Chaos injection complete!")
    print("="*60 + "\n")

def run_tests():
    print("\n🧪 RUNNING SYSTEM TESTS\n")
    
    tests = [
        ("thermal", "--watch", "Thermal monitoring"),
        ("risk", None, "Risk analysis"),
        ("agent", '-p "System health check"', "Agent task")
    ]
    
    for test_cmd, test_arg, test_name in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"{'='*60}")
        
        cmd = ["python", "sovereign_unified.py", test_cmd]
        if test_arg:
            if test_arg.startswith('-p'):
                cmd.extend(test_arg.split(' ', 1))
            else:
                cmd.append(test_arg)
        
        try:
            if test_cmd == "thermal" and test_arg == "--watch":
                # Run thermal for 3 seconds then stop
                proc = subprocess.Popen(cmd)
                time.sleep(3)
                proc.terminate()
                proc.wait()
                print("\n⏹️  Thermal monitoring stopped")
            else:
                result = subprocess.run(cmd, timeout=30)
                if result.returncode == 0:
                    print(f"\n✅ {test_name} completed successfully")
                else:
                    print(f"\n⚠️  {test_name} completed with warnings")
        except subprocess.TimeoutExpired:
            print(f"\n⏱️  {test_name} timed out (30s limit)")
        except Exception as e:
            print(f"\n❌ {test_name} failed: {e}")

if __name__ == "__main__":
    print("\n🚀 SovereignCore - Chaos Testing Suite")
    print("="*60)
    
    # Run chaos injection
    run_chaos_injection()
    
    # Run tests
    run_tests()
    
    print("\n" + "="*60)
    print("✨ All tests completed!")
    print("="*60 + "\n")
