#!/usr/bin/env python3
"""
SovereignCore v4.0 - Unified Thermodynamic AI Architecture
============================================================
A self-contained, hardware-rooted AI ecosystem for Apple Silicon
with PRA-ToT governance and local model access via Ollama.
"""

import json
import subprocess
import time
import os
import sys
import urllib.request
import urllib.error
import asyncio
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum

# FastAPI for Dashboard Connectivity
try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    HAS_API = True
except ImportError:
    HAS_API = False

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR = Path(__file__).parent.absolute()
CONFIG_PATH = SCRIPT_DIR / "config.json"
BRIDGE_BIN = SCRIPT_DIR / "sovereign_bridge"


class ThermalState(Enum):
    NOMINAL = "NOMINAL"
    FAIR = "FAIR"
    SERIOUS = "SERIOUS"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


@dataclass
class GovernanceParams:
    branching_factor: int
    max_tokens: int
    temperature: float


# ============================================================================
# Ollama Client
# ============================================================================

class OllamaClient:
    """HTTP client for Ollama API (local models)."""
    
    def __init__(self, host: str = "http://localhost:11434", timeout: int = 120):
        self.host = host.rstrip("/")
        self.timeout = timeout
    
    def _request(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        url = f"{self.host}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if data:
            req = urllib.request.Request(
                url, 
                data=json.dumps(data).encode("utf-8"),
                headers=headers,
                method="POST"
            )
        else:
            req = urllib.request.Request(url)
        
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as e:
            raise ConnectionError(f"Ollama connection failed: {e}")
    
    def list_models(self) -> List[Dict]:
        """List all available local models."""
        try:
            response = self._request("/api/tags")
            return response.get("models", [])
        except Exception as e:
            print(f"⚠ Ollama unavailable: {e}")
            return []
    
    def generate(self, model: str, prompt: str, options: Optional[Dict] = None) -> str:
        """Generate completion from a local model."""
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": options or {}
        }
        response = self._request("/api/generate", data)
        return response.get("response", "")
    
    def chat(self, model: str, messages: List[Dict], options: Optional[Dict] = None) -> str:
        """Chat completion from a local model."""
        data = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": options or {}
        }
        response = self._request("/api/chat", data)
        return response.get("message", {}).get("content", "")


# ============================================================================
# Hardware Bridge Interface
# ============================================================================

class HardwareBridge:
    """Interface to Swift hardware bridge for SEP and thermal telemetry."""
    
    def __init__(self, bridge_path: Path):
        self.bridge_path = bridge_path
        self.available = bridge_path.exists() and os.access(bridge_path, os.X_OK)
    
    def _call(self, command: str, *args) -> Dict:
        if not self.available:
            return {"status": "unavailable", "reason": "Bridge not compiled"}
        
        try:
            result = subprocess.run(
                [str(self.bridge_path), command, *args],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            return {"error": result.stderr}
        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            return {"error": str(e)}
    
    def get_thermal_state(self) -> ThermalState:
        """Get current thermal state from hardware."""
        data = self._call("thermal")
        state_str = data.get("thermal_state", "UNKNOWN")
        try:
            return ThermalState(state_str)
        except ValueError:
            return ThermalState.UNKNOWN
    
    def get_status(self) -> Dict:
        """Get full system status."""
        return self._call("status")
    
    def verify_identity(self) -> Dict:
        """Verify SEP identity."""
        return self._call("identity")
    
    def sign_data(self, data: str) -> Dict:
        """Sign data using SEP."""
        return self._call("sign", data)


# ============================================================================
# PRA-ToT Governance
# ============================================================================

class PRAToTGovernor:
    """
    Probabilistic Risk Assessment - Tree of Thoughts Governor.
    Adjusts inference parameters based on thermal and security state.
    """
    
    def __init__(self, config: Dict):
        self.thermal_config = config.get("thermal_governance", {})
        self.pra_config = config.get("pra_tot", {})
    
    def get_governance_params(self, thermal_state: ThermalState) -> GovernanceParams:
        """Calculate governance parameters based on thermal state."""
        state_key = thermal_state.value.lower()
        params = self.thermal_config.get(state_key, self.thermal_config.get("fair", {}))
        
        return GovernanceParams(
            branching_factor=params.get("branching_factor", 3),
            max_tokens=params.get("max_tokens", 2048),
            temperature=params.get("temperature", 0.5)
        )
    
    def calculate_risk_score(self, thermal_state: ThermalState, sep_valid: bool) -> float:
        """
        Calculate risk score R = f(T_smc, S_sep, C_load)
        Higher risk = more conservative inference.
        """
        base_risk = {
            ThermalState.NOMINAL: 0.1,
            ThermalState.FAIR: 0.3,
            ThermalState.SERIOUS: 0.6,
            ThermalState.CRITICAL: 0.9,
            ThermalState.UNKNOWN: 0.5
        }[thermal_state]
        
        # SEP validation reduces risk
        if sep_valid:
            base_risk *= 0.8
        else:
            base_risk = min(1.0, base_risk * 1.2)
        
        return base_risk


# ============================================================================
# SovereignCore Main Class
# ============================================================================

class SovereignCore:
    """
    Main orchestrator for SovereignCore v4.0.
    Integrates hardware bridge, Ollama, and PRA-ToT governance.
    """
    
    def __init__(self, config_path: Path = CONFIG_PATH):
        self.config = self._load_config(config_path)
        self.ollama = OllamaClient(
            host=self.config.get("ollama", {}).get("host", "http://localhost:11434"),
            timeout=self.config.get("ollama", {}).get("timeout_seconds", 120)
        )
        self.bridge = HardwareBridge(BRIDGE_BIN)
        self.governor = PRAToTGovernor(self.config)
        self.current_model = self.config.get("ollama", {}).get("default_model", "")
    
    def _load_config(self, path: Path) -> Dict:
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return {}
    
    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models."""
        models = self.ollama.list_models()
        return [m.get("name", "") for m in models if m.get("name")]
    
    def select_model(self, model_name: str) -> bool:
        """Select a model for inference."""
        available = self.get_available_models()
        if model_name in available:
            self.current_model = model_name
            return True
        return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        thermal_state = self.bridge.get_thermal_state()
        identity = self.bridge.verify_identity()
        sep_valid = identity.get("status") == "verified"
        
        params = self.governor.get_governance_params(thermal_state)
        risk = self.governor.calculate_risk_score(thermal_state, sep_valid)
        
        return {
            "version": "SovereignCore v4.0",
            "thermal_state": thermal_state.value,
            "sep_identity": identity.get("status", "unavailable"),
            "risk_score": round(risk, 3),
            "governance": {
                "branching_factor": params.branching_factor,
                "max_tokens": params.max_tokens,
                "temperature": params.temperature
            },
            "current_model": self.current_model,
            "available_models": self.get_available_models(),
            "hardware_bridge": "active" if self.bridge.available else "not_compiled"
        }
    
    def infer(self, prompt: str, verbose: bool = True) -> str:
        """
        Run inference with PRA-ToT governance.
        Adjusts parameters based on thermal and security state.
        """
        if not self.current_model:
            raise ValueError("No model selected. Use select_model() first.")
        
        # Get governance parameters
        thermal_state = self.bridge.get_thermal_state()
        identity = self.bridge.verify_identity()
        sep_valid = identity.get("status") == "verified"
        
        params = self.governor.get_governance_params(thermal_state)
        risk = self.governor.calculate_risk_score(thermal_state, sep_valid)
        
        if verbose:
            print(f"╔══════════════════════════════════════════════════════════════╗")
            print(f"║ SovereignCore v4.0 - PRA-ToT Inference                       ║")
            print(f"╠══════════════════════════════════════════════════════════════╣")
            print(f"║ Model:     {self.current_model:<50} ║")
            print(f"║ Thermal:   {thermal_state.value:<50} ║")
            print(f"║ Risk:      {risk:<50.3f} ║")
            print(f"║ Branching: k={params.branching_factor:<47} ║")
            print(f"║ MaxTokens: {params.max_tokens:<50} ║")
            print(f"╚══════════════════════════════════════════════════════════════╝")
        
        # Execute inference with governance parameters
        options = {
            "num_predict": params.max_tokens,
            "temperature": params.temperature
        }
        
        start_time = time.time()
        response = self.ollama.generate(self.current_model, prompt, options)
        elapsed = time.time() - start_time
        
        if verbose:
            print(f"\n⏱ Inference completed in {elapsed:.2f}s")
        
        return response
    
    def tree_of_thoughts(self, prompt: str, depth: int = 2) -> Dict[str, Any]:
        """
        Execute Tree of Thoughts reasoning with PRA governance.
        Explores multiple reasoning paths and evaluates them.
        """
        thermal_state = self.bridge.get_thermal_state()
        params = self.governor.get_governance_params(thermal_state)
        k = params.branching_factor
        
        print(f"\n🌳 Tree of Thoughts (depth={depth}, branching={k})")
        print("=" * 60)
        
        thoughts = []
        
        # Generate k initial thoughts
        for i in range(k):
            seed_prompt = f"{prompt}\n\nApproach #{i+1}: Think step by step about a unique way to address this."
            thought = self.infer(seed_prompt, verbose=False)
            thoughts.append({
                "branch": i + 1,
                "content": thought[:500] + "..." if len(thought) > 500 else thought
            })
            print(f"  Branch {i+1}: {thought[:100]}...")
        
        # Evaluate and synthesize
        eval_prompt = f"""Original query: {prompt}

I explored {k} different reasoning paths:
{json.dumps(thoughts, indent=2)}

Synthesize the best insights from all approaches into a final answer."""
        
        final = self.infer(eval_prompt, verbose=False)
        
        return {
            "branches": thoughts,
            "synthesis": final,
            "governance": {
                "thermal_state": thermal_state.value,
                "branching_factor": k
            }
        }


# ============================================================================
# CLI Interface
# ============================================================================

def print_banner():
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   ███████╗ ██████╗ ██╗   ██╗███████╗██████╗ ███████╗██╗ ██████╗ ███╗   ██╗║
║   ██╔════╝██╔═══██╗██║   ██║██╔════╝██╔══██╗██╔════╝██║██╔════╝ ████╗  ██║║
║   ███████╗██║   ██║██║   ██║█████╗  ██████╔╝█████╗  ██║██║  ███╗██╔██╗ ██║║
║   ╚════██║██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗██╔══╝  ██║██║   ██║██║╚██╗██║║
║   ███████║╚██████╔╝ ╚████╔╝ ███████╗██║  ██║███████╗██║╚██████╔╝██║ ╚████║║
║   ╚══════╝ ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝║
║                                                                           ║
║                    CORE v4.0 - Thermodynamic AI Architecture              ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)


def interactive_mode(core: SovereignCore):
    """Interactive REPL mode."""
    print_banner()
    
    status = core.get_system_status()
    print(f"Thermal State: {status['thermal_state']}")
    print(f"Hardware Bridge: {status['hardware_bridge']}")
    print(f"SEP Identity: {status['sep_identity']}")
    print(f"Risk Score: {status['risk_score']}")
    print(f"\nAvailable Models:")
    for i, model in enumerate(status['available_models'], 1):
        marker = "→" if model == status['current_model'] else " "
        print(f"  {marker} [{i}] {model}")
    
    if not status['current_model'] and status['available_models']:
        core.current_model = status['available_models'][0]
        print(f"\n✓ Auto-selected: {core.current_model}")
    
    print("\nCommands: /models, /select <n>, /status, /tot <prompt>, /exit")
    print("Or just type a prompt to run inference.\n")
    
    while True:
        try:
            user_input = input("sovereign> ").strip()
            if not user_input:
                continue
            
            if user_input == "/exit":
                print("Goodbye.")
                break
            elif user_input == "/models":
                models = core.get_available_models()
                for i, m in enumerate(models, 1):
                    marker = "→" if m == core.current_model else " "
                    print(f"  {marker} [{i}] {m}")
            elif user_input.startswith("/select "):
                try:
                    idx = int(user_input.split()[1]) - 1
                    models = core.get_available_models()
                    if 0 <= idx < len(models):
                        core.current_model = models[idx]
                        print(f"✓ Selected: {core.current_model}")
                    else:
                        print("Invalid selection")
                except (ValueError, IndexError):
                    print("Usage: /select <number>")
            elif user_input == "/status":
                status = core.get_system_status()
                print(json.dumps(status, indent=2))
            elif user_input.startswith("/tot "):
                prompt = user_input[5:]
                result = core.tree_of_thoughts(prompt)
                print(f"\n{'='*60}")
                print("SYNTHESIS:")
                print(result['synthesis'])
            else:
                response = core.infer(user_input)
                print(f"\n{response}\n")
        
        except KeyboardInterrupt:
            print("\nUse /exit to quit.")
        except Exception as e:
            print(f"Error: {e}")


# ============================================================================
# API Server Integration
# ============================================================================

def create_app(core: SovereignCore):
    """Create FastAPI application for the dashboard."""
    app = FastAPI(title="SovereignCore API")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/api/status")
    async def get_status():
        return core.get_system_status()
    
    @app.post("/api/query")
    async def query(data: Dict):
        prompt = data.get("prompt", "")
        if not prompt:
            return {"error": "No prompt provided"}
        response = core.infer(prompt, verbose=False)
        return {"response": response}
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                # Update status every 2 seconds
                status = core.get_system_status()
                await websocket.send_json(status)
                await asyncio.sleep(2)
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"WS Error: {e}")
            
    return app


def run_server(core: SovereignCore, host: str = "0.0.0.0", port: int = 8888):
    """Run the API server."""
    if not HAS_API:
        print("❌ FastAPI/Uvicorn not installed. Cannot start server.")
        return
        
    app = create_app(core)
    print(f"🚀 Sovereign Server starting on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="SovereignCore v4.0")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    parser.add_argument("--model", type=str, help="Select model for inference")
    parser.add_argument("--prompt", type=str, help="Run single inference")
    parser.add_argument("--tot", type=str, help="Run Tree of Thoughts")
    parser.add_argument("--server", action="store_true", help="Run API server for dashboard")
    parser.add_argument("--port", type=int, default=8888, help="Server port (default: 8888)")
    args = parser.parse_args()
    
    core = SovereignCore()
    
    if args.status:
        status = core.get_system_status()
        print(json.dumps(status, indent=2))
    elif args.list_models:
        for m in core.get_available_models():
            print(m)
    elif args.server:
        run_server(core, port=args.port)
    elif args.prompt:
        if args.model:
            core.select_model(args.model)
        elif not core.current_model:
            models = core.get_available_models()
            if models:
                core.current_model = models[0]
        response = core.infer(args.prompt)
        print(response)
    elif args.tot:
        if args.model:
            core.select_model(args.model)
        elif not core.current_model:
            models = core.get_available_models()
            if models:
                core.current_model = models[0]
        result = core.tree_of_thoughts(args.tot)
        print(json.dumps(result, indent=2))
    else:
        interactive_mode(core)


if __name__ == "__main__":
    main()
