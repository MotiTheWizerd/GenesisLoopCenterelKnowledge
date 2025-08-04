"""
Heartbeat-specific routes for system status and basic functionality.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime, timezone

from modules.logging.simple_logger import log_request, log_response, log_error
from modules.heartbeat.handler import heartbeat_handler
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
    Returns system status and availability with Ray's full consciousness state.
    """
    request_id = log_request("GET /heartbeat")
    
    try:
        # Get the current heartbeat state from the handler
        response = heartbeat_handler.get_current_heartbeat()
        
        # Ensure status is set to "alive" for GET requests
        response["status"] = "alive"
        
        log_response(request_id, response)
        
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
        # Get the current heartbeat state from the handler
        response = heartbeat_handler.get_current_heartbeat()
        
        # Add action-specific information
        response["action"] = request.action
        
        # For now, redirect reflect actions to suggest using the dedicated route
        if request.action == "reflect":
            response["status"] = "redirect_suggested"
            response["message"] = "Consider using the dedicated /reflect endpoint for reflection actions"
            response["redirect_to"] = "/reflect"
        else:
            # Default response for unknown actions
            response["status"] = "unknown_action"
            response["error"] = f"Unknown action: {request.action}"
        
        log_response(request_id, response, request.action)
        
        return response
        
    except Exception as e:
        log_error(request_id, e, "heartbeat_action", request.action)
        raise