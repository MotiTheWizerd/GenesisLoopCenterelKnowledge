"""
Agent routes for handling AI agent message processing and interactions.

This module provides the API endpoints for processing agent messages,
managing sessions, and interfacing with the underlying agent system.
Replicates the functionality from agents_test.py as HTTP endpoints.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from modules.agents.models import (
    AgentMessageRequest, 
    AgentMessageResponse, 
    AgentSessionInfo,
    AgentHealthStatus,
    BatchAgentRequest,
    BatchAgentResponse
)
from modules.agents.handler import (
    handle_agent_message,
    handle_get_session_info,
    handle_get_health_status,
    agent_manager
)
from modules.logging.heartbeat_logger import log_heartbeat_event, EventType, generate_request_id

agents_router = APIRouter(prefix="/agents", tags=["agents"])


@agents_router.post("/message")
async def process_agent_message(request: AgentMessageRequest):
    """
    Process a single agent message.
    
    This endpoint replicates the complete functionality from agents_test.py:
    - Creates or retrieves session
    - Processes message through GetHelperAgent
    - Updates conversation history
    - Returns agent response
    
    Client sends:
    {
        "message": "Hello, how can you help me?",
        "user_id": "user-123",
        "session_id": "session-456",
        "context": {...},
        "assigned_by": "user"
    }
    
    Server responds with:
    {
        "message_id": "uuid-here",
        "status": "completed",
        "response": "Agent response text",
        "user_id": "user-123",
        "session_id": "session-456",
        "processing_time_ms": 1500,
        "timestamp": "2025-01-01T00:00:00Z"
    }
    """
    request_id = generate_request_id()
    
    try:
        # Log incoming agent message request
        log_heartbeat_event(
            EventType.TASK_REQUESTED,
            {
                "message": request.message,
                "user_id": request.user_id,
                "session_id": request.session_id,
                "assigned_by": request.assigned_by,
                "endpoint": "POST /agents/message"
            },
            request_id=request_id,
            action="process_agent_message",
            metadata={
                "route": "agent_message_processing", 
                "user_id": request.user_id,
                "session_id": request.session_id
            }
        )
        
        # Process the message using the agent handler
        response = await handle_agent_message(request)
        
        # Log successful message processing
        log_heartbeat_event(
            EventType.TASK_COMPLETED if response.status.value == "completed" else EventType.TASK_ERROR,
            {
                "message_id": response.message_id,
                "status": response.status.value,
                "user_id": response.user_id,
                "session_id": response.session_id,
                "processing_time_ms": response.processing_time_ms,
                "response_length": len(response.response) if response.response else 0,
                "error_message": response.error_message
            },
            request_id=request_id,
            action="process_agent_message",
            metadata={
                "message_id": response.message_id,
                "status": response.status.value
            }
        )
        
        # Log outgoing response
        log_heartbeat_event(
            EventType.OUTGOING_RESPONSE,
            response.dict(),
            request_id=request_id,
            action="process_agent_message",
            metadata={"message_id": response.message_id}
        )
        
        return response
        
    except Exception as e:
        # Log agent message processing error
        log_heartbeat_event(
            EventType.TASK_ERROR,
            {
                "error": str(e),
                "user_id": request.user_id,
                "session_id": request.session_id,
                "message": request.message[:100] + "..." if len(request.message) > 100 else request.message
            },
            request_id=request_id,
            action="process_agent_message",
            metadata={"error_type": "agent_message_processing_failed"}
        )
        
        print(f"❌ Error processing agent message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process agent message: {str(e)}")


@agents_router.post("/batch")
async def process_batch_agent_messages(request: BatchAgentRequest):
    """
    Process multiple agent messages in batch.
    
    Client sends:
    {
        "messages": [
            {"message": "Hello", "user_id": "user-1", "session_id": "session-1"},
            {"message": "How are you?", "user_id": "user-1", "session_id": "session-1"}
        ],
        "batch_id": "batch-uuid",
        "process_parallel": false
    }
    """
    request_id = generate_request_id()
    
    try:
        # Log incoming batch request
        log_heartbeat_event(
            EventType.TASK_REQUESTED,
            {
                "batch_id": request.batch_id,
                "message_count": len(request.messages),
                "process_parallel": request.process_parallel,
                "endpoint": "POST /agents/batch"
            },
            request_id=request_id,
            action="process_batch_agent_messages",
            metadata={
                "route": "batch_agent_processing",
                "batch_id": request.batch_id,
                "message_count": len(request.messages)
            }
        )
        
        successful_responses = []
        failed_responses = []
        start_time = datetime.now()
        
        if request.process_parallel:
            # Process messages in parallel
            import asyncio
            tasks = [handle_agent_message(msg) for msg in request.messages]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_responses.append({
                        "message_index": i,
                        "error": str(result),
                        "message": request.messages[i].dict()
                    })
                else:
                    successful_responses.append(result)
        else:
            # Process messages sequentially
            for i, message_request in enumerate(request.messages):
                try:
                    response = await handle_agent_message(message_request)
                    successful_responses.append(response)
                except Exception as e:
                    failed_responses.append({
                        "message_index": i,
                        "error": str(e),
                        "message": message_request.dict()
                    })
        
        # Calculate total processing time
        processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Create batch response
        batch_response = BatchAgentResponse(
            batch_id=request.batch_id,
            total_messages=len(request.messages),
            successful_responses=successful_responses,
            failed_responses=failed_responses,
            processing_time_ms=processing_time_ms,
            status="completed" if not failed_responses else "partial_failure"
        )
        
        # Log batch completion
        log_heartbeat_event(
            EventType.TASK_COMPLETED,
            {
                "batch_id": batch_response.batch_id,
                "total_messages": batch_response.total_messages,
                "successful_count": len(successful_responses),
                "failed_count": len(failed_responses),
                "processing_time_ms": processing_time_ms,
                "status": batch_response.status
            },
            request_id=request_id,
            action="process_batch_agent_messages",
            metadata={"batch_id": batch_response.batch_id}
        )
        
        return batch_response
        
    except Exception as e:
        # Log batch processing error
        log_heartbeat_event(
            EventType.TASK_ERROR,
            {
                "error": str(e),
                "batch_id": request.batch_id,
                "message_count": len(request.messages)
            },
            request_id=request_id,
            action="process_batch_agent_messages",
            metadata={"error_type": "batch_processing_failed"}
        )
        
        print(f"❌ Error processing batch agent messages: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process batch messages: {str(e)}")


@agents_router.get("/session/{user_id}/{session_id}")
async def get_session_info(user_id: str, session_id: str):
    """
    Get information about a specific agent session.
    
    Returns session metadata including:
    - Session creation time
    - Last activity
    - Message count
    - Session status
    """
    try:
        session_info = await handle_get_session_info(user_id, session_id)
        
        if not session_info:
            raise HTTPException(
                status_code=404, 
                detail=f"Session not found for user {user_id}, session {session_id}"
            )
        
        return {
            "status": "success",
            "session_info": session_info.dict(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting session info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session info: {str(e)}")


@agents_router.get("/health")
async def get_agent_health():
    """
    Get health status of the agent system.
    
    Returns:
    - System status
    - Active session count
    - Total messages processed
    - Average response time
    - Agent information
    """
    try:
        health_status = handle_get_health_status()
        
        return {
            "status": "success",
            "health": health_status.dict(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error getting agent health: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent health: {str(e)}")


@agents_router.get("/sessions")
async def list_active_sessions():
    """
    List all active agent sessions.
    
    Returns summary of all currently active sessions.
    """
    try:
        active_sessions = []
        
        for session_key, session_data in agent_manager.active_sessions.items():
            user_id, session_id = session_key.split(":", 1)
            session_info = await handle_get_session_info(user_id, session_id)
            
            if session_info:
                active_sessions.append(session_info.dict())
        
        return {
            "status": "success",
            "active_session_count": len(active_sessions),
            "active_sessions": active_sessions,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error listing active sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list active sessions: {str(e)}")


@agents_router.delete("/session/{user_id}/{session_id}")
async def close_session(user_id: str, session_id: str):
    """
    Close/cleanup a specific agent session.
    
    Removes session from active tracking and cleans up resources.
    """
    try:
        session_key = f"{user_id}:{session_id}"
        
        if session_key in agent_manager.active_sessions:
            del agent_manager.active_sessions[session_key]
            
            return {
                "status": "success",
                "message": f"Session {session_id} for user {user_id} has been closed",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Active session not found for user {user_id}, session {session_id}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error closing session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to close session: {str(e)}")