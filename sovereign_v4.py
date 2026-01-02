#!/usr/bin/env python3
"""
SovereignCore v4.0: Unified Thermodynamic AI Architecture
==========================================================

The Python Orchestrator - Integrates:
- BitNet 1.58b inference engine (C++)
- Ollama local LLM bridge (Python)
- Secure Enclave signing (Swift)
- Metal GPU scrubber (Metal)
- PRA-ToT governance (Python)
"""

import ctypes
import subprocess
import json
import time
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Import Ollama bridge for fallback inference
try:
    from ollama_bridge import OllamaBridge, get_bridge
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Import Dual Purpose Engine for axiom inversion capabilities
try:
    from dual_purpose import DualPurposeEngine, CreativityMode
    DUAL_PURPOSE_AVAILABLE = True
except ImportError:
    DUAL_PURPOSE_AVAILABLE = False

# Import Knowledge Graph
try:
    from knowledge_graph import KnowledgeGraph
    KNOWLEDGE_GRAPH_AVAILABLE = True
except ImportError:
    KNOWLEDGE_GRAPH_AVAILABLE = False

# Configuration
PROJECT_ROOT = Path(__file__).parent
BITNET_LIB = PROJECT_ROOT / "build_sovereign" / "libbitnet.dylib"
BRIDGE_BIN = PROJECT_ROOT / "sovereign_bridge"
METAL_LIB = PROJECT_ROOT / "scrubber.metallib"
MODEL_PATH = PROJECT_ROOT / "models" / "bitnet_b1.58_3B.gguf"


class SovereignCore:
    """
    The main orchestrator for SovereignCore v4.0.
    
    Implements:
    - Thermodynamic Locking
    - PRA-ToT Governance
    - Hardware-rooted identity
    - Axiom Inversion (dual-purpose capabilities)
    """
    
    def __init__(self):
        print("\n" + "="*60)
        print("SovereignCore v4.0 Initialization")
        print("="*60 + "\n")
        
        self.engine = None
        self.ollama = None
        self.dual_purpose = None
        self.identity_verified = False
        self.thermal_state = "UNKNOWN"
        self.thermal_pressure = 0.0
        
        # Initialize components
        self._verify_identity()
        self._load_engine()
        self._load_ollama()
        self._load_dual_purpose()
        self._load_memory()
        
    def _verify_identity(self):
        """Verify sovereign identity via Secure Enclave."""
        print("[1/3] Verifying Sovereign Identity (SEP)...")
        
        if not BRIDGE_BIN.exists():
            print("  ⚠️  Swift bridge not compiled. Run 'make bridge' first.")
            print("  Continuing without SEP verification...\n")
            return
        
        try:
            # Generate or retrieve key
            result = subprocess.run(
                [str(BRIDGE_BIN), "keygen"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data.get("status") == "success":
                    print("  ✅ Sovereign Identity Verified via SEP\n")
                    self.identity_verified = True
                else:
                    print(f"  ❌ Identity verification failed: {data.get('message')}\n")
            else:
                print(f"  ❌ Bridge error: {result.stderr}\n")
                
        except subprocess.TimeoutExpired:
            print("  ❌ Bridge timeout\n")
        except json.JSONDecodeError:
            print(f"  ❌ Invalid JSON from bridge: {result.stdout}\n")
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
    
    def _load_engine(self):
        """Load BitNet 1.58b inference engine."""
        print("[2/3] Loading BitNet 1.58b Engine...")
        
        if not BITNET_LIB.exists():
            print(f"  ⚠️  BitNet library not found at: {BITNET_LIB}")
            print("  Run 'make bitnet' to compile the engine.")
            print("  Continuing without inference capability...\n")
            return
        
        try:
            self.engine = ctypes.CDLL(str(BITNET_LIB))
            print(f"  ✅ BitNet Engine Loaded from {BITNET_LIB.name}\n")
        except Exception as e:
            print(f"  ❌ Failed to load engine: {e}\n")
    
    def _load_ollama(self):
        """Load Ollama bridge for fallback inference."""
        print("[2b/3] Loading Ollama Bridge...")
        
        if not OLLAMA_AVAILABLE:
            print("  ⚠️  Ollama bridge not available (import failed)")
            print("  Install with: pip install requests\n")
            return
        
        try:
            self.ollama = get_bridge()
            status = self.ollama.get_status()
            if status['connected']:
                print(f"  ✅ Ollama Bridge Connected")
                print(f"     Model: {status['model']}")
                print(f"     Available: {len(status['available_models'])} models\n")
            else:
                print("  ⚠️  Ollama server not running")
                print("     Start with: ollama serve\n")
        except Exception as e:
            print(f"  ❌ Ollama bridge error: {e}\n")
    
    def _load_dual_purpose(self):
        """Load Dual Purpose Engine for axiom inversion capabilities."""
        print("[2c/3] Loading Dual Purpose Engine...")
        
        if not DUAL_PURPOSE_AVAILABLE:
            print("  ⚠️  Dual Purpose Engine not available")
            print("  Missing: dual_purpose.py\n")
            return
        
        try:
            self.dual_purpose = DualPurposeEngine(self.ollama)
            print("  ✅ Axiom Inversion Enabled")
            print("     Features: SelfCritique, ScreenDiff, MacroRecorder")
            print("     Features: AuditLog, CreativityMode\n")
            
            # Log initialization to audit trail
            self.dual_purpose.audit.log(
                "sovereign_init", 
                {"version": "4.0", "components": ["ollama", "dual_purpose"]},
                requester="system"
            )
        except Exception as e:
            print(f"  ❌ Dual Purpose Engine error: {e}\n")
    
    def _load_memory(self):
        """Load persistent Knowledge Graph."""
        print("[2d/3] Loading Knowledge Graph...")
        
        if not KNOWLEDGE_GRAPH_AVAILABLE:
            print("  ⚠️  Knowledge Graph not available")
            print("  Missing: knowledge_graph.py\n")
            return
        
        try:
            self.memory = KnowledgeGraph()
            
            # Load stats
            stats = self.memory.get_stats()
            print(f"  ✅ Memory Layer Active")
            print(f"     Memories: {stats['total_memories']}")
            print(f"     Connections: {stats['total_connections']}\n")
            
        except Exception as e:
            print(f"  ❌ Memory Layer error: {e}\n")
    
    def get_thermodynamics(self) -> Dict[str, Any]:
        """Get thermal telemetry from hardware."""
        if not BRIDGE_BIN.exists():
            return {
                "state": "UNKNOWN",
                "cpu_temp": 40.0,
                "thermal_pressure": 0.0,
                "timestamp": time.time()
            }
        
        try:
            result = subprocess.run(
                [str(BRIDGE_BIN), "telemetry"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                self.thermal_state = data.get("state", "UNKNOWN")
                self.thermal_pressure = data.get("thermal_pressure", 0.0)
                return data
            else:
                return {"state": "ERROR", "cpu_temp": 0.0, "thermal_pressure": 0.0}
                
        except Exception as e:
            print(f"Telemetry error: {e}")
            return {"state": "ERROR", "cpu_temp": 0.0, "thermal_pressure": 0.0}
    
    def calculate_risk_score(self, telemetry: Dict[str, Any]) -> float:
        """
        Calculate Probabilistic Risk Assessment (PRA) score.
        
        R = f(T_smc, S_sep, C_load)
        
        Returns: 0.0 (low risk) to 1.0 (high risk)
        """
        # Thermal component (0.0 - 0.6)
        thermal_risk = telemetry.get("thermal_pressure", 0.0) * 0.6
        
        # Identity component (0.0 - 0.3)
        identity_risk = 0.0 if self.identity_verified else 0.3
        
        # Cognitive load component (0.0 - 0.1)
        # TODO: Track actual inference load
        cognitive_risk = 0.0
        
        total_risk = thermal_risk + identity_risk + cognitive_risk
        return min(total_risk, 1.0)
    
    def get_tot_branching_factor(self, risk_score: float) -> int:
        """
        Determine Tree of Thoughts branching factor based on risk.
        
        Low Risk (R < 0.2): k=5 (Deep exploration)
        Medium Risk (0.2 <= R < 0.6): k=3 (Balanced)
        High Risk (R >= 0.6): k=1 (Deterministic, energy-saving)
        """
        if risk_score < 0.2:
            return 5
        elif risk_score < 0.6:
            return 3
        else:
            return 1
    
    def run_inference(self, prompt: str):
        """
        Execute inference with PRA-ToT governance and thermodynamic locking.
        """
        print("\n" + "="*60)
        print("Inference Request")
        print("="*60)
        print(f"Prompt: {prompt}\n")
        
        # Step 1: Get thermal state
        print("[3/3] Checking Thermodynamic State...")
        telemetry = self.get_thermodynamics()
        print(f"  State: {telemetry.get('state')}")
        print(f"  CPU Temp: {telemetry.get('cpu_temp'):.1f}°C")
        print(f"  Thermal Pressure: {telemetry.get('thermal_pressure'):.2f}\n")
        
        # Step 2: Calculate risk and determine governance
        risk_score = self.calculate_risk_score(telemetry)
        k_branches = self.get_tot_branching_factor(risk_score)
        
        # Determine creativity mode via Dual Purpose Engine (Axiom Inversion)
        creativity_level = 0
        if self.dual_purpose:
            creativity_level = self.dual_purpose.creativity.calculate_creativity(
                risk_score, telemetry.get('state', 'UNKNOWN')
            )
            print(f"  🎨 Creativity Mode: Level {creativity_level}")
        
        # Step 3: Recall Memory (RAG)
        context = ""
        if hasattr(self, 'memory') and self.memory:
            print("[3b/3] Consulting Knowledge Graph...")
            memories = self.memory.recall(prompt, limit=3)
            
            if memories:
                context_lines = []
                print(f"  💡 Recalled {len(memories)} relevant memories:")
                for i, m in enumerate(memories):
                    mem = m['memory']
                    print(f"     {i+1}. {mem['content'][:60]}...")
                    context_lines.append(f"- {mem['content']}")
                
                context = "\nRELEVANT CONTEXT FROM MEMORY:\n" + "\n".join(context_lines) + "\n\n"
        
        full_prompt = context + prompt if context else prompt
        
        print("PRA-ToT Governance:")
        print(f"  Risk Score: {risk_score:.3f}")
        print(f"  Branching Factor: k={k_branches}")
        
        # Step 3: Thermodynamic Locking
        if telemetry.get('state') == 'CRITICAL':
            print("\n🔒 THERMODYNAMIC LOCK ENGAGED")
            print("   System thermal state is CRITICAL")
            print("   Inference blocked for hardware protection\n")
            return None
        
        # Step 4: Execute inference
        response = None
        
        if self.engine is not None:
            # Use BitNet engine (primary)
            print(f"\n🧠 Executing BitNet inference with k={k_branches} thought branches...")
            # TODO: Implement BitNet FFI calls
            print("   [BitNet FFI integration pending]")
            response = None
        
        if response is None and self.ollama is not None:
            # Fallback to Ollama
            print(f"\n🤖 Using Ollama fallback (model: {self.ollama.config.model})...")
            
            # Apply governance to Ollama
            self.ollama.apply_governance(risk_score, k_branches)
            
            # Execute inference with full context
            response = self.ollama.chat(full_prompt)
            print(f"\n📝 Response:\n{response}\n")
            
            # Save to memory if available
            if hasattr(self, 'memory') and self.memory and response:
                try:
                    self.memory.remember_conversation(prompt, response, 
                                                   context={"risk": risk_score})
                    print("  💾 Conversation saved to Knowledge Graph")
                except Exception as e:
                    print(f"  ⚠️  Failed to save memory: {e}")
        
        if response is None:
            print("\n⚠️  No inference engine available")
            print("   - BitNet: Not loaded (run 'make bitnet')")
            print("   - Ollama: Not connected (run 'ollama serve')\n")
            return None
        
        # Step 5: Sign response with SEP (if available)
        if self.identity_verified and BRIDGE_BIN.exists():
            try:
                result = subprocess.run(
                    [str(BRIDGE_BIN), "sign", response[:100]],  # Sign first 100 chars
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    print(f"🔐 Response signed by SEP: {data.get('signature', '')[:20]}...")
            except Exception:
                pass
        
        # Step 6: Post-inference memory scrubbing
        self._scrub_memory()
        
        print("="*60 + "\n")
        return response
    
    def _scrub_memory(self):
        """Engage Metal GPU scrubber for memory sanitization."""
        if not METAL_LIB.exists():
            print("⚠️  Metal scrubber not compiled. Skipping memory scrub.")
            return
        
        print("🧹 Engaging Metal GPU Scrubber...")
        print("   Sanitizing residual thought vectors")
        print("   [Metal dispatch pending - requires pyobjc integration]")
        # TODO: Implement Metal dispatch via pyobjc
        # This would load scrubber.metallib and execute the kernels
    
    def status(self):
        """Print system status."""
        print("\n" + "="*60)
        print("SovereignCore v4.0 Status")
        print("="*60 + "\n")
        
        print("Components:")
        print(f"  Swift Bridge: {'✅' if BRIDGE_BIN.exists() else '❌'} {BRIDGE_BIN}")
        print(f"  BitNet Engine: {'✅' if BITNET_LIB.exists() else '❌'} {BITNET_LIB}")
        print(f"  Metal Scrubber: {'✅' if METAL_LIB.exists() else '❌'} {METAL_LIB}")
        print(f"  Model File: {'✅' if MODEL_PATH.exists() else '❌'} {MODEL_PATH}")
        
        print("\nIdentity:")
        print(f"  SEP Verified: {'✅' if self.identity_verified else '❌'}")
        
        print("\nThermal State:")
        telemetry = self.get_thermodynamics()
        print(f"  State: {telemetry.get('state')}")
        print(f"  Temperature: {telemetry.get('cpu_temp'):.1f}°C")
        print(f"  Pressure: {telemetry.get('thermal_pressure'):.2f}")
        
        risk = self.calculate_risk_score(telemetry)
        k = self.get_tot_branching_factor(risk)
        print("\nGovernance:")
        print(f"  Risk Score: {risk:.3f}")
        print(f"  ToT Branching: k={k}")
        
        print("\n" + "="*60 + "\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="SovereignCore v4.0 - Thermodynamic AI Architecture"
    )
    parser.add_argument(
        "command",
        choices=["status", "infer"],
        help="Command to execute"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        help="Prompt for inference"
    )
    
    args = parser.parse_args()
    
    core = SovereignCore()
    
    if args.command == "status":
        core.status()
    elif args.command == "infer":
        if not args.prompt:
            print("Error: --prompt required for inference")
            sys.exit(1)
        core.run_inference(args.prompt)


if __name__ == "__main__":
    main()
