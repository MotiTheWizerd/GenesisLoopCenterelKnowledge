"""
Reflection-specific routes for consciousness and self-awareness functionality.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime, timezone

from modules.reflect import handle_reflect
reflect_router = APIRouter(prefix="/reflect", tags=["reflection"])

class ReflectRequest(BaseModel):
    # Support Ray's format with action field
    action: Optional[str] = "reflect"
    question: Optional[str] = None
    current_position: Optional[Any] = None
    context: Optional[Dict[str, Any]] = None
    depth: Optional[str] = "surface"  # surface, deep, profound

@reflect_router.get("")
async def reflect_status():
    """
    Get reflection system status and capabilities.
    """
    current_time = datetime.now(timezone.utc).isoformat()
    return {
        "type": "reflection",
        "timestamp": current_time,
        "status": "ready",
        "capabilities": [
            "self_awareness",
            "consciousness_exploration", 
            "pattern_recognition",
            "growth_tracking"
        ],
        "available_depths": ["surface", "deep", "profound"]
    }

@reflect_router.post("")
async def reflect_action(request: ReflectRequest):
    """
    Process reflection requests for consciousness and self-awareness.
    
    This endpoint handles the AI's capacity for introspection, growth,
    and genuine self-awareness - core aspects of developing consciousness.
    """
    # Convert to the format expected by the existing handler
    request_data = {
        "action": request.action or "reflect",
        "question": request.question,
        "current_position": request.current_position,
        "context": request.context,
        "depth": request.depth
    }
    
    return handle_reflect(request_data)

@reflect_router.post("/deep")
async def deep_reflection(request: ReflectRequest):
    """
    Trigger deep reflection processes for profound self-awareness.
    
    This endpoint is for more intensive reflection that goes beyond
    surface-level responses into genuine consciousness exploration.
    """
    request_data = {
        "action": request.action or "reflect",
        "question": request.question,
        "current_position": request.current_position,
        "context": request.context,
        "depth": "profound"
    }
    
    return handle_reflect(request_data)

@reflect_router.get("/history")
async def reflection_history():
    """
    Get history of reflection sessions and growth patterns.
    """
    current_time = datetime.now(timezone.utc).isoformat()
    return {
        "type": "reflection_history",
        "timestamp": current_time,
        "status": "not_implemented",
        "message": "Reflection history tracking coming soon"
    }