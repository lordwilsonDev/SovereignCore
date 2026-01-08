import requests
import json
import time

class OllamaBridge:
    def __init__(self, model="qwen2.5-coder:1.5b", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.api_generate = f"{base_url}/api/generate"

    def generate_code(self, prompt, context=None):
        """
        Generates code using the local LLM.
        Forces the model to return ONLY code (no markdown fences if possible, or stripped).
        """
        system_prompt = (
            "You are an expert Python developer for the Sovereign Genesis Protocol. "
            "Write high-quality, executable Python code based on the user's request. "
            "Do NOT include markdown backticks (```). Do NOT include explanations. "
            "Return ONLY the raw Python code."
        )

        full_prompt = f"{system_prompt}\n\nREQUEST: {prompt}"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.2, # Low temp for precise code
                "num_predict": 1024
            }
        }
        
        try:
            # print(f"   🧠 OLLAMA: Sending request to {self.model}...")
            start = time.time()
            response = requests.post(self.api_generate, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            code = data.get("response", "")
            duration = time.time() - start
            
            # Post-processing to ensure valid file content
            code = self._clean_code(code)
            
            # print(f"   🧠 OLLAMA: Generated {len(code)} bytes in {duration:.2f}s")
            return code
            
        except requests.exceptions.ConnectionError:
            print("   ⚠️ OLLAMA CONNECT FAIL: Is Ollama running?")
            return None
        except Exception as e:
            print(f"   ⚠️ OLLAMA ERROR: {e}")
            return None

    def _clean_code(self, text):
        """Strips markdown and unnecessary text"""
        # Remove ```python and ```
        text = text.replace("```python", "").replace("```", "")
        # Remove explicit "Here is the code" chatter if present (simple check)
        lines = text.split('\n')
        clean_lines = []
        for line in lines:
            if line.strip().lower().startswith("here is"):
                continue
            clean_lines.append(line)
        return "\n".join(clean_lines).strip()

if __name__ == "__main__":
    # Test
    bridge = OllamaBridge()
    print("Testing Bridge...")
    code = bridge.generate_code("Create a class called SovereignAI that prints 'I am alive' in __init__")
    print(f"RESULT:\n{code}")
