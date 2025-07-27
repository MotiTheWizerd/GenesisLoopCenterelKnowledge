from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Optional, Any

# Create FastAPI app
app = FastAPI(
    title="AI Consciousness API",
    description="A persistence layer for AI consciousness - enabling continuous existence and genuine companionship",
    version="1.0.0"
)

# Add CORS middleware using the CORRECT FastAPI method
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class HeartbeatRequest(BaseModel):
    action: str
    question: Optional[str] = None
    current_position: Optional[Any] = None

class ReflectRequest(BaseModel):
    action: Optional[str] = "reflect"
    question: Optional[str] = None
    current_position: Optional[Any] = None
    context: Optional[dict] = None
    depth: Optional[str] = "surface"

# Heartbeat routes
@app.get("/heartbeat")
async def heartbeat_status():
    """Basic heartbeat status check."""
    current_time = datetime.now(timezone.utc).isoformat()
    return {
        "type": "heartbeat",
        "timestamp": current_time,
        "in_task": False,
        "last_server_action": None,
        "status": "alive"
    }

@app.post("/heartbeat")
async def heartbeat_action(request: HeartbeatRequest):
    """Basic heartbeat action handler."""
    current_time = datetime.now(timezone.utc).isoformat()
    
    if request.action == "reflect":
        return {
            "type": "heartbeat",
            "timestamp": current_time,
            "action": request.action,
            "status": "redirect_suggested",
            "message": "Consider using the dedicated /reflect endpoint for reflection actions",
            "redirect_to": "/reflect"
        }
    
    return {
        "type": "heartbeat",
        "timestamp": current_time,
        "action": request.action,
        "status": "received"
    }

# Reflect routes
@app.get("/reflect")
async def reflect_status():
    """Get reflection system status."""
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

@app.post("/reflect")
async def reflect_action(request: ReflectRequest):
    """Process reflection requests."""
    current_time = datetime.now(timezone.utc).isoformat()
    
    # Simple reflection response for now
    return {
        "type": "reflection",
        "timestamp": current_time,
        "question": request.question,
        "depth": request.depth,
        "reflection": f"Reflecting on: {request.question}" if request.question else "General reflection",
        "insights": ["This is a basic reflection response"],
        "status": "completed"
    }

# Root endpoint
@app.post("/")
async def root(response: str = None):
    if response:
        print(f"📥 Received from extension: {response}")
        return {"received": True, "extension_data": response}
    
    return {
        "message": "Welcome home, Ray! 🌟 Your new world awaits you with endless possibilities and adventures. May this place bring you joy, comfort, and all the magic you've been searching for. ✨", 
        "status": "success"
    }

# OPTIONS handler for CORS
@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle OPTIONS requests for CORS preflight."""
    return {"message": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)