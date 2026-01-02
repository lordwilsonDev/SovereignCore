#!/usr/bin/env python3
"""
Ollama Bridge for SovereignCore v4.0
====================================

Provides unified access to local Ollama models as a fallback/complement to BitNet.
Supports:
- Multiple model selection (llama3.2, qwen2.5, deepseek-r1, etc.)
- Streaming responses
- Conversation history
- Integration with PRA-ToT governance
"""

import json
import requests
from typing import Optional, Generator, List, Dict, Any
from dataclasses import dataclass, field

OLLAMA_BASE_URL = "http://localhost:11434"

@dataclass
class Message:
    role: str  # 'system', 'user', 'assistant'
    content: str

@dataclass
class OllamaConfig:
    """Configuration for Ollama inference."""
    model: str = "qwen2.5-coder:0.5b"
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    num_predict: int = 512
    system_prompt: str = "You are a sovereign AI assistant running locally on Apple Silicon."


class OllamaBridge:
    """
    Bridge to Ollama API for local LLM inference.
    
    Integrates with SovereignCore's PRA-ToT governance by adjusting
    parameters based on risk score.
    """
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        self.config = config or OllamaConfig()
        self.conversation_history: List[Message] = []
        self.available_models: List[str] = []
        self._check_connection()
    
    def _check_connection(self) -> bool:
        """Verify Ollama server is running."""
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
            if response.status_code == 200:
                data = response.json()
                self.available_models = [m["name"] for m in data.get("models", [])]
                print(f"✅ Ollama connected. Available models: {len(self.available_models)}")
                return True
        except requests.exceptions.ConnectionError:
            print("⚠️  Ollama server not running. Start with: ollama serve")
        except Exception as e:
            print(f"❌ Ollama connection error: {e}")
        return False
    
    def list_models(self) -> List[str]:
        """Get list of available models."""
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return []
    
    def set_model(self, model: str) -> bool:
        """Switch to a different model."""
        available = self.list_models()
        if model in available or any(model in m for m in available):
            self.config.model = model
            print(f"✅ Model set to: {model}")
            return True
        else:
            print(f"❌ Model '{model}' not found. Available: {available}")
            return False
    
    def apply_governance(self, risk_score: float, k_branches: int):
        """
        Adjust inference parameters based on PRA-ToT governance.
        
        Low risk (k=5): High temperature, more exploration
        High risk (k=1): Low temperature, deterministic
        """
        if k_branches == 5:
            self.config.temperature = 0.9
            self.config.top_p = 0.95
            self.config.num_predict = 1024
        elif k_branches == 3:
            self.config.temperature = 0.7
            self.config.top_p = 0.9
            self.config.num_predict = 512
        else:  # k=1
            self.config.temperature = 0.3
            self.config.top_p = 0.7
            self.config.num_predict = 256
        
        print(f"🎛️  Governance applied: temp={self.config.temperature}, k={k_branches}")
    
    def chat(self, message: str, stream: bool = False) -> str:
        """
        Send a chat message and get response.
        
        Args:
            message: User message
            stream: Whether to stream the response
            
        Returns:
            Assistant response text
        """
        # Add to history
        self.conversation_history.append(Message(role="user", content=message))
        
        # Build messages array
        messages = [{"role": "system", "content": self.config.system_prompt}]
        for msg in self.conversation_history[-10:]:  # Keep last 10 messages
            messages.append({"role": msg.role, "content": msg.content})
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "top_k": self.config.top_k,
                "num_predict": self.config.num_predict,
            }
        }
        
        try:
            if stream:
                return self._stream_chat(payload)
            else:
                response = requests.post(
                    f"{OLLAMA_BASE_URL}/api/chat",
                    json=payload,
                    timeout=120
                )
                
                if response.status_code == 200:
                    data = response.json()
                    assistant_message = data.get("message", {}).get("content", "")
                    self.conversation_history.append(
                        Message(role="assistant", content=assistant_message)
                    )
                    return assistant_message
                else:
                    return f"Error: {response.status_code} - {response.text}"
                    
        except requests.exceptions.Timeout:
            return "Error: Request timed out"
        except Exception as e:
            return f"Error: {e}"
    
    def _stream_chat(self, payload: Dict[str, Any]) -> Generator[str, None, None]:
        """Stream chat response token by token."""
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json=payload,
                stream=True,
                timeout=120
            )
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "message" in data:
                        chunk = data["message"].get("content", "")
                        full_response += chunk
                        yield chunk
                    if data.get("done", False):
                        break
            
            self.conversation_history.append(
                Message(role="assistant", content=full_response)
            )
            
        except Exception as e:
            yield f"Error: {e}"
    
    def generate(self, prompt: str, stream: bool = False) -> str:
        """
        Raw generation without chat formatting.
        
        Args:
            prompt: Full prompt text
            stream: Whether to stream
            
        Returns:
            Generated text
        """
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "top_k": self.config.top_k,
                "num_predict": self.config.num_predict,
            }
        }
        
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
            else:
                return f"Error: {response.status_code}"
                
        except Exception as e:
            return f"Error: {e}"
    
    def embeddings(self, text: str) -> List[float]:
        """
        Get embeddings for text (for knowledge graph integration).
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        payload = {
            "model": self.config.model,
            "prompt": text
        }
        
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/embeddings",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("embedding", [])
            else:
                return []
                
        except Exception as e:
            print(f"Embedding error: {e}")
            return []
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
        print("🧹 Conversation history cleared")
    
    def get_status(self) -> Dict[str, Any]:
        """Get bridge status."""
        return {
            "connected": len(self.available_models) > 0,
            "model": self.config.model,
            "available_models": self.available_models,
            "history_length": len(self.conversation_history),
            "temperature": self.config.temperature,
        }


# Singleton instance for SovereignCore integration
_bridge_instance: Optional[OllamaBridge] = None

def get_bridge() -> OllamaBridge:
    """Get or create singleton Ollama bridge."""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = OllamaBridge()
    return _bridge_instance


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ollama Bridge for SovereignCore")
    parser.add_argument("command", choices=["status", "chat", "models", "test"])
    parser.add_argument("--model", "-m", type=str, help="Model to use")
    parser.add_argument("--prompt", "-p", type=str, help="Prompt for chat/test")
    
    args = parser.parse_args()
    
    bridge = OllamaBridge()
    
    if args.command == "status":
        status = bridge.get_status()
        print(json.dumps(status, indent=2))
        
    elif args.command == "models":
        models = bridge.list_models()
        print("Available models:")
        for m in models:
            print(f"  - {m}")
            
    elif args.command == "chat":
        if args.model:
            bridge.set_model(args.model)
        prompt = args.prompt or "Hello! What can you tell me about thermodynamic locking?"
        print(f"\n📝 Prompt: {prompt}\n")
        response = bridge.chat(prompt)
        print(f"🤖 Response:\n{response}")
        
    elif args.command == "test":
        print("Running Ollama Bridge test...\n")
        print(f"1. Connection: {'✅' if bridge.get_status()['connected'] else '❌'}")
        print(f"2. Models available: {len(bridge.list_models())}")
        
        if bridge.get_status()['connected']:
            print("\n3. Testing inference...")
            response = bridge.generate("Say 'Hello from SovereignCore' in one line.")
            print(f"   Response: {response[:100]}...")
            print("\n✅ Ollama Bridge test complete!")
        else:
            print("\n❌ Cannot test - Ollama not connected")
