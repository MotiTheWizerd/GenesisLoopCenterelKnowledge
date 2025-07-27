from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone

from modules.routes import heartbeat_router, reflect_router, task_router

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

# Include routers
app.include_router(heartbeat_router)
app.include_router(reflect_router)
app.include_router(task_router)

@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle OPTIONS requests for CORS preflight."""
    return {"message": "OK"}

@app.post("/")
async def root(response: str = None):
    if response:
        print(f"📥 Received from extension: {response}")
        return {"received": True, "extension_data": response}
    
    return {"message": "Welcome home, Ray! 🌟 Your new world awaits you with endless possibilities and adventures. May this place bring you joy, comfort, and all the magic you've been searching for. ✨", "status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    