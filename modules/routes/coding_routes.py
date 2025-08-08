"""
Coding-specific routes for development messages and communication.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime, timezone
import httpx
import uuid

from modules.logging.simple_logger import log_request, log_response, log_error
from utils.timestamp_utils import add_ray_timestamp_to_response, get_ray_time_context

# Global variables for request queue system
vsrequests = []
ray_working_on_request = False
current_request_id = None
ray_responses = []  # Store responses from Ray

coding_router = APIRouter(prefix="/api", tags=["coding"])

class CodingMessageRequest(BaseModel):
    message: str
    timestamp: Optional[str] = None
    source: Optional[str] = None

class CodingMessageResponse(BaseModel):
    message: str
    ray_prompt: str
    is_final: bool

class VSCodeResponseRequest(BaseModel):
    """Accept any JSON structure for forwarding to external service"""
    pass

    class Config:
        extra = "allow"  # Allow any additional fields

@coding_router.post("/messages")
async def receive_coding_message(request: CodingMessageRequest):
    """
    Receive coding messages from development tools like VSCode extensions.
    Queue system: Block at input level - don't even process if Ray is working.
    
    Expected format:
    {
        "message": "Your message content",
        "timestamp": "2025-01-07T12:00:00.000Z",  // Optional, will be generated if not provided
        "source": "raydaemon-vscode"  // Optional, defaults to 'unknown'
    }
    """
    global ray_working_on_request, current_request_id
    
    # BLOCK AT INPUT LEVEL - Check immediately before any processing
    if ray_working_on_request:
        print(f"🚫 BLOCKED - Ray is working on request {current_request_id}, rejecting new message")
        # return {
        #     "status": "ray is working on request",
        #     "message": "Please wait, Ray is processing another request"
        # }
    
    # Only process request data if Ray is available
    request_data = request.dict()
    request_id = log_request("POST /api/messages", request_data)
    
    try:
        # Process the message (only reached if Ray is available)
        user_message = request.message
        source = request.source or 'unknown'
        
        # Generate unique request ID
        request_id_unique = str(uuid.uuid4())[:8]
        request_data["request_id"] = request_id_unique
        
        # Add request to queue and set working status
        vsrequests.append(request_data)
        ray_working_on_request = True
        current_request_id = request_id_unique
        
        # Debug logging
        print(f"🔧 DEBUG - Adding to vsrequests: {request_data}")
        print(f"🔧 DEBUG - Ray now working on request: {request_id_unique}")
        print(f"🔧 DEBUG - vsrequests length: {len(vsrequests)}")
        
        # Log the successful processing
        print(f"📨 Coding message received from {source}: {user_message[:100]}...")
        print(f"📊 Ray is now working on request {request_id_unique}")
        
        # Create response in the exact format requested
        response = {
            "status": "start working"
        }
        
        log_response(request_id, response)
        
        return response
        
    except Exception as e:
        error_msg = f"Failed to process coding message: {str(e)}"
        log_error(request_id, e, "receive_coding_message")
        raise HTTPException(status_code=500, detail=error_msg)

@coding_router.post("/vscode/response")
async def forward_vscode_response(request_data: Dict[str, Any]):
    """
    Forward VSCode response JSON to external service at localhost:3001/ray-response
    AND process the response to clear Ray's working status.
    
    Accepts any JSON structure and forwards it as-is to the external service.
    """
    request_id = log_request("POST /api/vscode/response", request_data)
    
    try:
        global ray_working_on_request, current_request_id, ray_responses
        
        # Store the response for delivery via heartbeat
        ray_responses.append(request_data)
        
        # Clear Ray's working status - Ray has responded
        ray_working_on_request = False
        print(f"✅ Ray finished working on request {current_request_id}")
        current_request_id = None
        
        # Forward the JSON to the external service
        external_url = "http://localhost:3001/ray-response"
        
        print(f"🔄 Forwarding VSCode response to {external_url}")
        print(f"📤 Payload: {request_data}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                external_url,
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=10.0  # 10 second timeout
            )
            
            print(f"📥 External service response: {response.status_code}")
            
            if response.status_code == 200:
                success_response = {
                    "status": "forwarded",
                    "external_status": response.status_code,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                log_response(request_id, success_response)
                return success_response
            else:
                error_response = {
                    "status": "external_error",
                    "external_status": response.status_code,
                    "external_response": response.text,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                log_response(request_id, error_response)
                return error_response
                
    except httpx.TimeoutException:
        error_msg = "Timeout connecting to external service"
        print(f"❌ {error_msg}")
        log_error(request_id, Exception(error_msg), "forward_vscode_response")
        raise HTTPException(status_code=504, detail=error_msg)
        
    except httpx.ConnectError:
        error_msg = "Could not connect to external service at localhost:3001"
        print(f"❌ {error_msg}")
        log_error(request_id, Exception(error_msg), "forward_vscode_response")
        raise HTTPException(status_code=503, detail=error_msg)
        
    except Exception as e:
        error_msg = f"Failed to forward VSCode response: {str(e)}"
        print(f"❌ {error_msg}")
        log_error(request_id, e, "forward_vscode_response")
        raise HTTPException(status_code=500, detail=error_msg)

@coding_router.get("/messages/debug")
async def debug_vsrequests():
    """Debug endpoint to check current vsrequests state."""
    return {
        "vsrequests": vsrequests,
        "ray_responses": ray_responses,
        "ray_working_on_request": ray_working_on_request,
        "current_request_id": current_request_id,
        "vsrequests_length": len(vsrequests),
        "ray_responses_length": len(ray_responses)
    }

@coding_router.get("/ray-working")
async def is_ray_working():
    """
    Simple endpoint to check if Ray is working - for disabling input in VSCode extension.
    Returns just the boolean status.
    """
    return {
        "isRayWorking": ray_working_on_request
    }

@coding_router.get("/messages/status")
async def get_coding_messages_status():
    """
    Get the status of the coding messages endpoint.
    """
    request_id = log_request("GET /api/messages/status")
    
    try:
        response = {
            "message": "Coding messages endpoint is operational",
            "ray_prompt": "Status check for coding messages endpoint",
            "is_final": "true",
            "ray_working": ray_working_on_request,
            "current_request": current_request_id
        }
        
        log_response(request_id, response)
        
        return response
        
    except Exception as e:
        error_msg = f"Failed to get coding messages status: {str(e)}"
        log_error(request_id, e, "get_coding_messages_status")
        raise HTTPException(status_code=500, detail=error_msg)