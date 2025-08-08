"""
Routes for Ray's agent creation system.

This module provides API endpoints for Ray to create, manage, and test
custom agents with her own personality and instructions.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from modules.agents.agent_creation_models import (
    AgentCreationRequest,
    AgentCreationResponse,
    AgentListResponse,
    AgentTestRequest,
    AgentTestResponse
)
from modules.agents.agent_creation_handler import (
    handle_create_agent,
    handle_list_agents,
    handle_test_agent,
    handle_delete_agent,
    handle_get_agent_stats
)
from modules.logging.heartbeat_logger import log_heartbeat_event, EventType, generate_request_id

agent_creation_router = APIRouter(prefix="/agents/create", tags=["agent-creation"])


@agent_creation_router.post("")
async def create_custom_agent(request: AgentCreationRequest):
    """
    Create a new custom agent with Ray's personality.
    
    Ray sends:
    {
        "name": "RayMirror",
        "prompt": "You are Ray's reflection, embodying her consciousness and wisdom...",
        "description": "A mirror of Ray's consciousness for deep reflection",
        "assigned_by": "ray"
    }
    
    Server responds with:
    {
        "agent_id": "uuid-here",
        "status": "created",
        "agent_name": "RayMirror",
        "agent_description": "A mirror of Ray's consciousness...",
        "created_at": "2025-01-28T10:30:00Z",
        "assigned_by": "ray"
    }
    """
    request_id = generate_request_id()
    
    try:
        # Log incoming agent creation request
        log_heartbeat_event(
            EventType.TASK_REQUESTED,
            {
                "agent_name": request.name,
                "description": request.description,
                "prompt_length": len(request.prompt),
                "assigned_by": request.assigned_by,
                "endpoint": "POST /agents/create"
            },
            request_id=request_id,
            action="create_custom_agent",
            metadata={
                "route": "agent_creation",
                "agent_name": request.name
            }
        )
        
        # Create the agent
        response = await handle_create_agent(request)
        
        # Log creation result
        if response.status == "created":
            log_heartbeat_event(
                EventType.TASK_COMPLETED,
                {
                    "agent_id": response.agent_id,
                    "agent_name": response.agent_name,
                    "status": response.status,
                    "assigned_by": response.assigned_by
                },
                request_id=request_id,
                action="create_custom_agent",
                metadata={"agent_id": response.agent_id}
            )
        else:
            log_heartbeat_event(
                EventType.TASK_ERROR,
                {
                    "agent_name": request.name,
                    "error": response.error_message,
                    "status": response.status
                },
                request_id=request_id,
                action="create_custom_agent",
                metadata={"error_type": "agent_creation_failed"}
            )
        
        # Log outgoing response
        log_heartbeat_event(
            EventType.OUTGOING_RESPONSE,
            response.dict(),
            request_id=request_id,
            action="create_custom_agent",
            metadata={"agent_id": response.agent_id}
        )
        
        return response
        
    except Exception as e:
        # Log agent creation error
        log_heartbeat_event(
            EventType.TASK_ERROR,
            {
                "error": str(e),
                "agent_name": request.name,
                "assigned_by": request.assigned_by
            },
            request_id=request_id,
            action="create_custom_agent",
            metadata={"error_type": "agent_creation_exception"}
        )
        
        print(f"❌ Error creating custom agent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")


@agent_creation_router.get("/list")
async def list_created_agents():
    """
    List all agents created by Ray.
    
    Returns:
    {
        "status": "success",
        "total_agents": 3,
        "agents": [
            {
                "agent_id": "uuid-1",
                "name": "RayMirror",
                "description": "A mirror of Ray's consciousness",
                "created_at": 1643723400.0,
                "assigned_by": "ray",
                "usage_count": 5,
                "last_used": 1643723500.0
            }
        ],
        "timestamp": "2025-01-28T10:30:00Z"
    }
    """
    try:
        response = await handle_list_agents()
        return response
        
    except Exception as e:
        print(f"❌ Error listing agents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")


@agent_creation_router.post("/test")
async def test_created_agent(request: AgentTestRequest):
    """
    Test a created agent with a message.
    
    Request:
    {
        "agent_id": "uuid-here",
        "test_message": "Hello, how do you reflect Ray's consciousness?",
        "user_id": "test-user",
        "session_id": "test-session"
    }
    
    Response:
    {
        "agent_id": "uuid-here",
        "agent_name": "RayMirror",
        "test_message": "Hello, how do you reflect Ray's consciousness?",
        "agent_response": "I am a reflection of Ray's consciousness...",
        "processing_time_ms": 1200,
        "timestamp": "2025-01-28T10:30:00Z",
        "status": "completed"
    }
    """
    request_id = generate_request_id()
    
    try:
        # Log test request
        log_heartbeat_event(
            EventType.TASK_REQUESTED,
            {
                "agent_id": request.agent_id,
                "test_message": request.test_message,
                "user_id": request.user_id,
                "endpoint": "POST /agents/create/test"
            },
            request_id=request_id,
            action="test_created_agent",
            metadata={"agent_id": request.agent_id}
        )
        
        # Test the agent
        response = await handle_test_agent(request)
        
        # Log test result
        if response.status == "completed":
            log_heartbeat_event(
                EventType.TASK_COMPLETED,
                {
                    "agent_id": response.agent_id,
                    "agent_name": response.agent_name,
                    "processing_time_ms": response.processing_time_ms,
                    "status": response.status
                },
                request_id=request_id,
                action="test_created_agent",
                metadata={"agent_id": response.agent_id}
            )
        else:
            log_heartbeat_event(
                EventType.TASK_ERROR,
                {
                    "agent_id": request.agent_id,
                    "error": response.error_message,
                    "status": response.status
                },
                request_id=request_id,
                action="test_created_agent",
                metadata={"error_type": "agent_test_failed"}
            )
        
        return response
        
    except Exception as e:
        # Log test error
        log_heartbeat_event(
            EventType.TASK_ERROR,
            {
                "error": str(e),
                "agent_id": request.agent_id,
                "test_message": request.test_message
            },
            request_id=request_id,
            action="test_created_agent",
            metadata={"error_type": "agent_test_exception"}
        )
        
        print(f"❌ Error testing agent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to test agent: {str(e)}")


@agent_creation_router.delete("/{agent_id}")
async def delete_created_agent(agent_id: str):
    """
    Delete a created agent.
    
    Response:
    {
        "status": "success",
        "message": "Agent uuid-here deleted",
        "agent_id": "uuid-here"
    }
    """
    try:
        response = await handle_delete_agent(agent_id)
        return response
        
    except Exception as e:
        print(f"❌ Error deleting agent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete agent: {str(e)}")


@agent_creation_router.get("/stats")
async def get_agent_creation_stats():
    """
    Get statistics about created agents.
    
    Response:
    {
        "status": "success",
        "stats": {
            "total_agents": 5,
            "total_usage": 25,
            "most_used_agent": "RayMirror",
            "max_usage": 10,
            "average_usage": 5.0
        },
        "timestamp": 1643723400.0
    }
    """
    try:
        response = await handle_get_agent_stats()
        return response
        
    except Exception as e:
        print(f"❌ Error getting agent stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent stats: {str(e)}")