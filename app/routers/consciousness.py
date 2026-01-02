from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
import time
import asyncio
from typing import Dict, Any, Optional

# Import the existing bridges and orchestrators
# Note: These are in the root directory. We need to ensure Python path captures root.
import sys
import os
sys.path.append(os.getcwd()) # Ensure root imports work for legacy bridges

try:
    from consciousness_bridge import ConsciousnessBridge
    from tot_orchestrator import ToTOrchestrator
except ImportError:
    # Safety fallback if running from inside app/
    sys.path.append(os.path.dirname(os.path.dirname(os.getcwd())))
    from consciousness_bridge import ConsciousnessBridge
    from tot_orchestrator import ToTOrchestrator

router = APIRouter(tags=["consciousness"])

class ConsciousnessRequest(BaseModel):
    prompt: str
    context: Optional[Dict[str, Any]] = None

class ConsciousnessResponse(BaseModel):
    response: str
    silicon_id: str
    consciousness_level: float
    thermal_state: str
    processing_time_ms: float
    request_id: str

bridge = ConsciousnessBridge()

@router.post("/api/v1/consciousness/process")
async def process_consciousness(
    request: Request,
    consciousness_request: ConsciousnessRequest
):
    start_time_ms = time.time() * 1000
    
    try:
        # Get current state
        state = bridge.get_state()
        
        # Initialize ToT Orchestrator (Ouroboros Stabilization)
        orchestrator = ToTOrchestrator()
        
        # Add thermal context for recursion safety
        context = {
            "user_id": "authenticated_user", # In prod, extract from JWT
            "silicon_id": state.silicon_id,
            "thermal_state": state.thermal_state,
            "consciousness_level": state.consciousness_level,
            "recursion_depth": 0 # Start at root
        }
        
        # Execute reasoning loop with safety guards
        result = await orchestrator.run_reasoning_loop(
            prompt=consciousness_request.prompt,
            context=context
        )
        
        processing_time = (time.time() * 1000) - start_time_ms
        
        return ConsciousnessResponse(
            response=result.get("response", ""),
            silicon_id=state.silicon_id[:16],
            consciousness_level=state.consciousness_level,
            thermal_state=state.thermal_state,
            processing_time_ms=processing_time,
            request_id=str(getattr(request.state, "request_id", "req_000"))
        )
    
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Processing failed")
