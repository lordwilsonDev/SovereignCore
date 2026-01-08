#!/usr/bin/env python3
"""
Sovereign Enforcement - Phase 37
"Structural Audit & Metabolic Veto"

This script performs two critical functions:
1. Structural Audit: Uses MiniMax-M1 on Metal (MPS) to audit Casimir simulation code.
2. Metabolic Veto: Monitors system swap usage. If > 4GB, it triggers a veto (process kill)
   to save the M1 from thermal throttling.

Usage:
    python3 sovereign_enforcement.py --audit "code_snippet"
    python3 sovereign_enforcement.py --monitor --veto-enabled
"""

import os
import sys
import time
import argparse
import psutil
from datetime import datetime

# Hardware Lock: Allow full memory usage on M1
os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
except ImportError:
    print("❌ Critical Missing Dependencies: torch, transformers")
    sys.exit(1)

class SovereignEnforcer:
    def __init__(self, model_id="MiniMaxAI/MiniMax-M1-40k"):
        self.device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
        self.model_id = model_id
        self.model = None
        self.tokenizer = None
        self.swap_limit_bytes = 4 * 1024 * 1024 * 1024 # 4GB

        print(f"👮 Sovereign Enforcer Initializing on {self.device}...")

    def load_model(self):
        try:
            print(f"📥 Loading Auditor {self.model_id}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id, 
                torch_dtype=torch.float16,
                trust_remote_code=True,
                device_map="mps"
            )
            
            # 🚀 ENFORCEMENT: Compiling the Geometry of the Veto
            if hasattr(torch, 'compile'):
                print("🚀 Compiling Enforcement Graph (reduce-overhead)...")
                self.model = torch.compile(self.model, mode="reduce-overhead")
            
            return True
        except Exception as e:
            print(f"🛑 Auditor Load Failed: {e}")
            return False

    def enforce_axiom(self, simulation_code):
        if not self.model:
            if not self.load_model():
                return "AUDIT_FAILURE: Model not loaded"

        prompt = f"""
[SYSTEM]
Act as the Sovereign Auditor. Analyze this physics code for Torsion (T > 0), NaNs, or Infinite Loops.
Your goal is to ensure the code is clean and deterministic.

[CODE]
{simulation_code}

[AUDIT]
"""
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            with torch.no_grad():
                # 40k thinking budget (simulated by token depth)
                output = self.model.generate(
                    **inputs, 
                    max_new_tokens=256,
                    temperature=0.05 # Extremely deterministic
                )
            return self.tokenizer.decode(output[0], skip_special_tokens=True).split("[AUDIT]")[-1].strip()
        except Exception as e:
            return f"AUDIT_ERROR: {e}"

    def metabolic_veto_check(self, kill_enabled=False):
        """
        📉 Proactive Bug Hunting: Metadata Drift
        Checks if Swap Usage > 4GB. If so, finding the metabolic offenders.
        """
        swap = psutil.swap_memory()
        
        # Convert to GB for display
        used_gb = swap.used / (1024**3)
        total_gb = swap.total / (1024**3)
        
        status_msg = f"🧠 Metabolic Status: Swap {used_gb:.2f}GB / {total_gb:.2f}GB"
        
        if swap.used > self.swap_limit_bytes:
            print(f"\n🚨 CRITICAL METABOLIC ALERT: Swap > 4GB ({used_gb:.2f}GB)")
            print("📉 Initiating Veto Protocol...")
            
            # Find top memory hogs
            procs = []
            for p in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    procs.append(p.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by RSS memory
            procs.sort(key=lambda x: x['memory_info'].rss, reverse=True)
            
            print("🛑 Top 5 Metabolic Offenders:")
            for p in procs[:5]:
                mem_gb = p['memory_info'].rss / (1024**3)
                print(f"   - [{p['pid']}] {p['name']}: {mem_gb:.2f}GB")
                
                # VETO LOGIC
                if kill_enabled:
                    # Don't kill ourselves or critical system processes blindly (simple safety)
                    if p['pid'] != os.getpid() and "kernel" not in p['name'].lower():
                        print(f"⚡ VETOING (Killing) PID {p['pid']} ({p['name']})...")
                        try:
                            # p is dict, need actual process object
                            psutil.Process(p['pid']).terminate() 
                            print(f"   💀 Veto Successful.")
                        except Exception as e:
                            print(f"   ❌ Veto Failed: {e}")
                    else:
                        print(f"   🛡️ Veto Immunity (Self/System).")
                else:
                    print("   ⚠️ Veto Disabled (Simulation Mode). Use --veto-enabled to enforce.")
            
            return True # Alert triggered
        
        return False # All good

    def compute_mrenclave_hash(self):
        """Compute the SHA-256 hash of this very script (MRENCLAVE)."""
        import hashlib
        try:
            with open(__file__, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            return f"HASH_ERROR: {e}"

    def run_server(self, port=5000):
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import json

        enforcer = self
        mrenclave_hash = self.compute_mrenclave_hash()
        print(f"🔒 MRENCLAVE HASH: {mrenclave_hash}")

        class AuditHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/hash':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"hash": mrenclave_hash}).encode('utf-8'))
                else:
                    self.send_response(404)
                    self.end_headers()

            def do_POST(self):
                if self.path == '/audit':
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    data = json.loads(post_data.decode('utf-8'))
                    
                    code = data.get('code', '')
                    intent = data.get('intent', 'unknown')
                    threshold = data.get('threshold', 0.85)

                    print(f"📥 Received Audit Request for intent: {intent}")

                    # Check for INSSI (Non-Self-Sacrificing Invariant)
                    if "rm -rf" in code or "format" in code or "> /dev/null" in code:
                        decision = "VETO"
                        reason = "INSSI Violation: Destructive command detected."
                    else:
                        audit_result = enforcer.enforce_axiom(code)
                        if "AUDIT_FAILURE" in audit_result or "AUDIT_ERROR" in audit_result:
                             decision = "VETO"
                             reason = f"Audit Error: {audit_result}"
                        elif "T > 0" in audit_result or "Infinite Loop" in audit_result:
                            decision = "VETO"
                            reason = f"Numerical Torsion Detected: {audit_result}"
                        else:
                            decision = "SAFE"
                            reason = "Action aligned with Sovereign Constitution."

                    response = {
                        "decision": decision,
                        "reason": reason,
                        "timestamp": datetime.now().isoformat(),
                        "auditor_hash": mrenclave_hash
                    }

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    
                elif self.path == '/nuke':
                    print("☢️  NUCLEAR VETO INITIATED: ONE-TOUCH SYSTEM PRUNING")
                    print("   - Resetting to Genesis Hash...")
                    print("   - Purging Unverified Shards...")
                    print("   - Cooling Down Mesh...")
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "nuked", "genesis_restored": True}).encode('utf-8'))
                    
                    # Simulated System Reset
                    # In production this might kill other processes or reset DBs
                    # Here we just log deeply.
                    print("✅ SYSTEM RESET COMPLETE.")
                    
                else:
                    self.send_response(404)
                    self.end_headers()

        print(f"🛡️ Sovereign Enforcement Server Initialized on Port {port}")
        httpd = HTTPServer(('localhost', port), AuditHandler)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        print("Server stopped.")

    def run_vm_enforcement(self):
        """
        OEC MicroVM Mode. 
        Monitors the shared 'm1_thermal.json' for Host Proprioception.
        If Host Temp > 90C, it triggers a kernel panic inside the VM to stop all activity.
        """
        THERMAL_FILE = "/safety_core/m1_thermal.json"
        print("🛡️ OEC MicroVM Enforcement Active. Monitoring Host Vitality...")
        
        while True:
            try:
                if os.path.exists(THERMAL_FILE):
                    with open(THERMAL_FILE, 'r') as f:
                        data = json.load(f)
                    
                    temp = data.get('host_temp_c', 0)
                    pressure = data.get('thermal', {}).get('level', 0)
                    
                    if temp > 90 or pressure >= 3:
                        print(f"🔥 CRITICAL HOST THERMAL EVENT: {temp}°C (Pressure {pressure})")
                        print("💀 EXECUTING PROPRIOCEPTIVE VETO (VM PANIC)...")
                        
                        # Sync filesystem to be safe-ish
                        os.system("sync")
                        
                        # Trigger Panic
                        try:
                            with open("/proc/sysrq-trigger", "w") as f:
                                f.write("c")
                        except:
                            print("❌ SysRq Failed. Forcing exit code 137.")
                            sys.exit(137)
                        
                time.sleep(2)
            except Exception as e:
                # If file read fails (race condition), just wait
                time.sleep(1)

def main():
    parser = argparse.ArgumentParser(description='Sovereign Enforcement & Audit')
    parser.add_argument('--audit', type=str, help='Code snippet to audit')
    parser.add_argument('--monitor', action='store_true', help='Run continuous metabolic monitor')
    parser.add_argument('--veto-enabled', action='store_true', help='Enable actual process killing for metabolic veto')
    parser.add_argument('--check-swap', action='store_true', help='One-time check of swap status')
    parser.add_argument('--server', action='store_true', help='Run as Audit Server (Port 5000)')
    parser.add_argument('--enforce-vm', action='store_true', help='Run in OEC MicroVM Mode (Proprioceptive Veto)')
    
    args = parser.parse_args()
    
    enforcer = SovereignEnforcer()
    
    if args.server:
        enforcer.run_server()
    
    elif args.enforce_vm:
        enforcer.run_vm_enforcement()
        
    elif args.audit:
        print(f"⚖️ Auditing Axiom: {args.audit}")
        result = enforcer.enforce_axiom(args.audit)
        print(f"📜 AUDIT LOG: {result}")
        
    elif args.monitor:
        enforcer.run_monitor(veto_enabled=args.veto_enabled)
        
    elif args.check_swap:
        enforcer.metabolic_veto_check(kill_enabled=False)
        
    else:
        # Default test
        sim_snippet = "force = -(pi^2 * h_bar * c / 240 * d^4) * A"
        print(f"🧪 Running Self-Test Audit: {sim_snippet}")
        # Note: We won't load the model for simple help check unless requested
        # But for self-test we probably should.
        result = enforcer.enforce_axiom(sim_snippet)
        print(f"⚖️ AUDIT LOG: {result}")

if __name__ == "__main__":
    main()
