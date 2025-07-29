"""
Heartbeat-specific routes for system status and basic functionality.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime, timezone

from modules.logging.simple_logger import log_request, log_response, log_error
from utils.timestamp_utils import add_ray_timestamp_to_response, get_ray_time_context

heartbeat_router = APIRouter(prefix="/heartbeat", tags=["heartbeat"])

class HeartbeatRequest(BaseModel):
    action: str
    question: Optional[str] = None
    current_position: Optional[Any] = None

@heartbeat_router.get("")
async def heartbeat_status():
    """
    Basic heartbeat status check (GET request).
    Returns system status and availability.
    """
    request_id = log_request("GET /heartbeat")
    
    try:
        current_time = datetime.now(timezone.utc).isoformat()
        response = {
            "type": "heartbeat",
            "timestamp": current_time,
            "in_task": False,
            "last_server_action": None,
            "status": "alive"
        }
        
        log_response(request_id, response)
        
        # Add comprehensive timestamp information for Ray
        response = add_ray_timestamp_to_response(response)
        
        return response
        
    except Exception as e:
        log_error(request_id, e, "heartbeat_status")
        raise

@heartbeat_router.post("")
async def heartbeat_action(request: HeartbeatRequest):
    """
    Legacy heartbeat route that handles action-based routing.
    This maintains backward compatibility while we transition to dedicated routes.
    """
    request_data = request.dict()
    request_id = log_request("POST /heartbeat", request_data, request.action)
    
    try:
        current_time = datetime.now(timezone.utc).isoformat()
        
        # For now, redirect reflect actions to suggest using the dedicated route
        if request.action == "reflect":
            response = {
                "type": "heartbeat",
                "timestamp": current_time,
                "action": request.action,
                "status": "redirect_suggested",
                "message": "Consider using the dedicated /reflect endpoint for reflection actions",
                "redirect_to": "/reflect"
            }
        else:
            # Default response for unknown actions
            response = {
                "type": "heartbeat",
                "timestamp": current_time,
                "action": request.action,
                "status": "unknown_action",
                "error": f"Unknown action: {request.action}"
            }
        
        log_response(request_id, response, request.action)
        
        # Add comprehensive timestamp information for Ray
        response = add_ray_timestamp_to_response(response)
        
        return response
        
    except Exception as e:
        log_error(request_id, e, "heartbeat_action", request.action)
        raise