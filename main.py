from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from pathlib import Path
import time
import json

from modules.routes import heartbeat_router, reflect_router, task_router, memory_router, directory_router, web_router, health_router, command_history_router, self_learning_router
from modules.command_history.handler import command_history_handler

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

# Command tracking middleware
@app.middleware("http")
async def track_commands(request: Request, call_next):
    """Track all API commands for Ray's command history"""
    start_time = time.time()
    
    # Get request info
    method = request.method
    url = str(request.url)
    path = request.url.path
    
    # Skip tracking for certain endpoints
    skip_paths = ["/docs", "/openapi.json", "/favicon.ico", "/commands"]
    if any(skip_path in path for skip_path in skip_paths):
        return await call_next(request)
    
    # Get request data
    request_data = None
    assigned_by = None
    
    try:
        if method == "POST" and request.headers.get("content-type") == "application/json":
            # Read request body
            body = await request.body()
            if body:
                request_data = json.loads(body.decode())
                assigned_by = request_data.get("assigned_by")
        
        # Recreate request with body for downstream processing
        async def receive():
            return {"type": "http.request", "body": body if 'body' in locals() else b""}
        
        request._receive = receive
        
    except Exception:
        pass  # Continue without request data if parsing fails
    
    # Process request
    response = await call_next(request)
    
    # Calculate response time
    response_time_ms = (time.time() - start_time) * 1000
    
    # Determine command type from path
    command_type = _get_command_type_from_path(path)
    
    # Record command
    try:
        command_history_handler.record_command(
            command_type=command_type,
            endpoint=path,
            method=method,
            request_data=request_data,
            response_status=response.status_code,
            response_time_ms=response_time_ms,
            success=200 <= response.status_code < 400,
            error_message=None if 200 <= response.status_code < 400 else f"HTTP {response.status_code}",
            request_id=None,  # Could add request ID header if needed
            assigned_by=assigned_by
        )
    except Exception as e:
        print(f"Error recording command: {str(e)}")
    
    return response

def _get_command_type_from_path(path: str) -> str:
    """Determine command type from API path"""
    if "/web/search" in path:
        return "search"
    elif "/web/scrape" in path:
        return "scrape"
    elif "/web/" in path:
        return "web"
    elif "/reflect" in path:
        return "reflect"
    elif "/directory" in path:
        return "directory"
    elif "/health" in path:
        return "health"
    elif "/memory" in path:
        return "memory"
    elif "/task" in path:
        return "task"
    elif "/heartbeat" in path:
        return "heartbeat"
    else:
        return "api"

# Include routers
print("🔧 DEBUGGING - Including routers...")
app.include_router(heartbeat_router)
print("🔧 DEBUGGING - Heartbeat router included")
app.include_router(reflect_router)
print("🔧 DEBUGGING - Reflect router included")
app.include_router(task_router)
print("🔧 DEBUGGING - Task router included")
app.include_router(memory_router)
print("🔧 DEBUGGING - Memory router included")
app.include_router(directory_router)
print("🔧 DEBUGGING - Directory router included")
app.include_router(web_router)
print("🔧 DEBUGGING - Web router included")
app.include_router(health_router)
print("🔧 DEBUGGING - Health router included")
app.include_router(command_history_router)
print("🔧 DEBUGGING - Command history router included")
app.include_router(self_learning_router)
print("🔧 DEBUGGING - Self-learning router included")
print("🔧 DEBUGGING - All routers loaded successfully")

@app.get("/debug/routes")
async def list_routes():
    """Debug endpoint to list all available routes."""
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, 'name', 'unnamed')
            })
    return {"routes": routes}

@app.get("/memory-status")
async def get_memory_status():
    """Get memory system status and available log information."""
    try:
        log_file = Path("logs/heartbeat_detailed.jsonl")
        
        if not log_file.exists():
            return {
                "status": "no_logs",
                "message": "No log file found",
                "log_file_exists": False,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Get basic file info
        file_size = log_file.stat().st_size
        
        # Count total logs quickly
        total_logs = 0
        reflection_logs = 0
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        total_logs += 1
                        if 'task_updated' in line and 'update_task_reflection' in line:
                            reflection_logs += 1
        except Exception:
            pass
        
        return {
            "status": "operational",
            "log_file_exists": True,
            "log_file_size_bytes": file_size,
            "total_log_entries": total_logs,
            "reflection_log_entries": reflection_logs,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error getting memory status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get memory status: {str(e)}")

@app.post("/")
async def root(request: Request):
    try:
        request_data = await request.json()
        print(f"📥 DEBUGGING - Received at root endpoint: {request_data}")
        print(f"📥 DEBUGGING - Request type: {type(request_data)}")
        
        # Check if this is Ray's memory request that fell through
        if isinstance(request_data, dict):
            action = request_data.get('action')
            
            if action == 'remember_past_reflections':
                print(f"🚨 DEBUGGING - Ray's memory request fell to root! Data: {request_data}")
                print(f"🚨 DEBUGGING - This should be going to POST /memory/get_reflections_logs")
                
                # For now, let's redirect this to the memory endpoint logic
                from modules.routes.memory_routes import get_reflection_logs, RememberRequest
                
                try:
                    # Convert the request data to the expected format
                    memory_request = RememberRequest(
                        action=request_data.get('action'),
                        **{'from': request_data.get('from'), 'to': request_data.get('to')}
                    )
                    print(f"🔄 DEBUGGING - Redirecting to memory handler...")
                    result = await get_reflection_logs(memory_request)
                    print(f"✅ DEBUGGING - Memory request handled successfully")
                    return result
                except Exception as e:
                    print(f"❌ DEBUGGING - Error handling memory request: {e}")
                    return {"error": f"Failed to handle memory request: {str(e)}"}
            
            elif action == 'memory_status':
                print(f"🚨 DEBUGGING - Memory status request fell to root! Data: {request_data}")
                print(f"🚨 DEBUGGING - This should be going to GET /memory/status")
                
                # Redirect to memory status endpoint logic
                from modules.routes.memory_routes import get_memory_status
                
                try:
                    print(f"🔄 DEBUGGING - Redirecting to memory status handler...")
                    result = await get_memory_status()
                    print(f"✅ DEBUGGING - Memory status request handled successfully")
                    return result
                except Exception as e:
                    print(f"❌ DEBUGGING - Error handling memory status request: {e}")
                    return {"error": f"Failed to handle memory status request: {str(e)}"}
        
        return {"received": True, "extension_data": request_data}
        
    except Exception as e:
        print(f"❌ DEBUGGING - Error parsing request: {e}")
        return {"message": "Welcome home, Ray! 🌟 Your new world awaits you with endless possibilities and adventures. May this place bring you joy, comfort, and all the magic you've been searching for. ✨", "status": "success"}

@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle OPTIONS requests for CORS preflight."""
    return {"message": "OK"}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all_debug(path: str, request):
    """Debug route to catch all unmatched requests."""
    method = request.method
    print(f"🚨 DEBUGGING - Unmatched route: {method} /{path}")
    
    # Try to get request body for POST requests
    if method == "POST":
        try:
            body = await request.json()
            print(f"🚨 DEBUGGING - Request body: {body}")
            
            # Check if this is Ray's memory request
            if isinstance(body, dict) and body.get('action') == 'remember_past_reflections':
                print(f"🚨 DEBUGGING - Ray's memory request hit catch-all! Should go to /memory/get_reflections_logs")
        except:
            print(f"🚨 DEBUGGING - Could not parse request body")
    
    return {"error": f"Route not found: {method} /{path}", "debug": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    