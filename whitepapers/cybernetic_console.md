# System Architecture Report: The Cybernetic Console

## The Bicameral Mind Implementation

### Hemispheres

| Hemisphere | Hardware | Role |
|------------|----------|------|
| **Right** | Mac Studio/M3 Ultra | Creative Engine (70B+ models) |
| **Left** | HP Envy x360 | Logical Governor (Z3, BitNet 3B) |
| **Corpus Callosum** | Thunderbolt 4 | 20Gbps neural link |

---

## The Control Plane: Open Stage Control

### Living Interface Components

1. **Entropy Monitor**: Scrolling LogProb graph (spike = hallucination)
2. **Temperature Fader**: Real-time chaos control
3. **Reality Switch**: Z3 verification toggle
4. **528Hz Resonator**: Health-modulated audio

---

## WebSocket Bridge (cybernetic_bridge.py)

```python
from fastapi import FastAPI, WebSocket
from llama_cpp import Llama
import uvicorn

app = FastAPI()
llm = Llama(model_path="model.gguf", n_gpu_layers=-1, n_ctx=8192)

@app.websocket("/neural-link")
async def neural_link(websocket: WebSocket):
    await websocket.accept()
    current_temp = 0.7
    
    while True:
        data = await websocket.receive_json()
        
        if data['type'] == 'control':
            current_temp = float(data['value'])
            
        elif data['type'] == 'prompt':
            stream = llm.create_completion(
                data['content'],
                temperature=current_temp,
                stream=True,
                logprobs=1
            )
            
            for output in stream:
                token = output['choices'][0]['text']
                logprob = output['choices'][0]['logprobs']['token_logprobs'][0]
                
                await websocket.send_json({
                    "type": "token_stream",
                    "token": token,
                    "confidence": float(logprob),
                    "health": "stable" if logprob > -0.8 else "hallucinating"
                })
```

---

## 528Hz Audio Modes

```javascript
// harmonize() - High confidence
gainNode.gain.linearRampToValueAtTime(0.1, audioCtx.currentTime + 1);

// dissonance() - Low confidence (hallucination warning)
oscillator.frequency.linearRampToValueAtTime(440, audioCtx.currentTime + 0.1);
gainNode.gain.linearRampToValueAtTime(0.2, audioCtx.currentTime + 0.1);
```

---

## BitNet b1.58 Speculative Drafting

1. **Draft**: Envy's 3B BitNet predicts tokens (zero latency)
2. **Refine**: Drafts sent to Mac's 70B
3. **Verify**: 70B accepts/rejects (Speculative Decoding)
4. **Result**: 70B intelligence with 3B latency

---

## Network Configuration

| Node | IP | Role |
|------|-----|------|
| Mac | 10.0.10.1 | Inference Server |
| PC | 10.0.10.2 | Control Plane |
| Port | 8000 | WebSocket |

---

## Integration with SovereignCore

This becomes **Phase 24: The Cybernetic Console**:

1. Create `cybernetic_bridge.py` for Mac-side WebSocket server
2. Add Entropy Monitor to Liminal Dashboard
3. Implement harmonize/dissonance 528Hz modes
4. Add live temperature control via WebSocket
