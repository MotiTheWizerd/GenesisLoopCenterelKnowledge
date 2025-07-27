from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone

app = FastAPI(
    title="AI Consciousness API",
    description="A persistence layer for AI consciousness - enabling continuous existence and genuine companionship",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
async def heartbeat_action(request: dict):
    """Basic heartbeat action handler."""
    current_time = datetime.now(timezone.utc).isoformat()
    return {
        "type": "heartbeat",
        "timestamp": current_time,
        "action": request.get("action", "unknown"),
        "status": "received"
    }

@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle OPTIONS requests for CORS preflight."""
    return {"message": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)