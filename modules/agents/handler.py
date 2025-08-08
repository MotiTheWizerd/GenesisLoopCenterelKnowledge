"""
Agent handler for managing AI agent message processing and interactions.

This module provides the core functionality for processing agent messages,
managing sessions, and interfacing with the underlying agent system.
"""

import asyncio
import time
import uuid
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

from .models import (
    AgentMessageRequest, 
    AgentMessageResponse, 
    AgentStatus,
    AgentSessionInfo,
    AgentHealthStatus
)
from rays_agents.agents.helper_agent.get_helper_agent import GetHelperAgent
from rays_agents.agents.utils.llm.call_agent_async import call_agent_async

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Global session service and runner instances
session_service = InMemorySessionService()
APP_NAME = "ray-consciousness-agent"

class AgentManager:
    """
    Manages agent sessions and message processing.
    Replicates the functionality from agents_test.py as a service.
    """
    
    def __init__(self):
        self.session_service = session_service
        self.app_name = APP_NAME
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.message_count = 0
        self.total_processing_time = 0
        
    async def get_or_create_session(self, user_id: str, session_id: str) -> Any:
        """
        Get existing session or create new one.
        Replicates the session management from agents_test.py
        """
        session_key = f"{user_id}:{session_id}"
        
        try:
            # Try to get existing session
            session = await self.session_service.get_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id
            )
            
            if session is not None:
                logger.info(f"Retrieved existing session for {session_key}")
                return session
            else:
                raise Exception("Session not found")
            
        except Exception as e:
            # Create new session if it doesn't exist
            logger.info(f"Creating new session for {session_key}, error was: {str(e)}")
            
            initial_state = {
                "user_request": "",
            }
            
            try:
                session = await self.session_service.create_session(
                    app_name=self.app_name,
                    session_id=session_id,
                    user_id=user_id,
                    state=initial_state
                )
                
                if session is None:
                    logger.error(f"Session creation returned None for {session_key}")
                    raise Exception("Session creation returned None")
                
                logger.info(f"Successfully created session for {session_key}")
                
                # Track active session
                self.active_sessions[session_key] = {
                    "user_id": user_id,
                    "session_id": session_id,
                    "created_at": time.time(),
                    "last_activity": time.time(),
                    "message_count": 0
                }
                
                return session
                
            except Exception as create_error:
                logger.error(f"Failed to create session for {session_key}: {str(create_error)}")
                raise create_error
    
    async def process_message(self, request: AgentMessageRequest) -> AgentMessageResponse:
        """
        Process agent message request.
        Replicates the main message processing loop from agents_test.py
        """
        start_time = time.time()
        message_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Processing message {message_id} for user {request.user_id}")
            
            # Get or create session
            session = await self.get_or_create_session(request.user_id, request.session_id)
            
            if session is None:
                raise Exception("Failed to create or retrieve session")
            
            if not hasattr(session, 'state') or session.state is None:
                raise Exception("Session has no state attribute or state is None")
            
            # Update session state with user request
            session.state["user_request"] = request.message
            
            # Initialize session metadata if it doesn't exist
            if "session_metadata" not in session.state:
                session.state["session_metadata"] = {
                    "created_at": time.time(),
                    "message_count": 0
                }
            
            # Create agent and runner (replicating agents_test.py setup)
            root_agent = GetHelperAgent()
            runner = Runner(
                app_name=self.app_name, 
                agent=root_agent, 
                session_service=self.session_service
            )
            
            # Process the message using call_agent_async
            logger.info(f"Calling agent for message {message_id}")
            agent_response = await call_agent_async(
                runner=runner,
                user_id=request.user_id,
                session_id=request.session_id,
                message=request.message
            )
            
            # Get updated session state after processing
            updated_session = await self.session_service.get_session(
                app_name=self.app_name,
                user_id=request.user_id,
                session_id=request.session_id
            )
            
            # Update session metadata
            if "session_metadata" not in updated_session.state:
                updated_session.state["session_metadata"] = {}
            
            updated_session.state["session_metadata"]["message_count"] = \
                updated_session.state["session_metadata"].get("message_count", 0) + 1
            updated_session.state["session_metadata"]["last_activity"] = time.time()
            
            # Update tracking
            session_key = f"{request.user_id}:{request.session_id}"
            if session_key in self.active_sessions:
                self.active_sessions[session_key]["message_count"] += 1
                self.active_sessions[session_key]["last_activity"] = time.time()
            
            # Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)
            self.message_count += 1
            self.total_processing_time += processing_time
            
            logger.info(f"Successfully processed message {message_id} in {processing_time}ms")
            
            return AgentMessageResponse(
                message_id=message_id,
                status=AgentStatus.COMPLETED,
                response=agent_response,
                user_id=request.user_id,
                session_id=request.session_id,
                processing_time_ms=processing_time,
                context={
                    "session_state": {
                        "message_count": updated_session.state["session_metadata"]["message_count"]
                    },
                    "assigned_by": request.assigned_by
                }
            )
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            error_message = f"Error processing message: {str(e)}"
            logger.error(f"Failed to process message {message_id}: {error_message}")
            
            return AgentMessageResponse(
                message_id=message_id,
                status=AgentStatus.ERROR,
                response=None,
                user_id=request.user_id,
                session_id=request.session_id,
                processing_time_ms=processing_time,
                error_message=error_message
            )
    
    async def get_session_info(self, user_id: str, session_id: str) -> Optional[AgentSessionInfo]:
        """Get information about a specific session."""
        session_key = f"{user_id}:{session_id}"
        
        try:
            session = await self.session_service.get_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id
            )
            
            session_metadata = session.state.get("session_metadata", {})
            
            return AgentSessionInfo(
                session_id=session_id,
                user_id=user_id,
                created_at=session_metadata.get("created_at", time.time()),
                last_activity=session_metadata.get("last_activity", time.time()),
                message_count=session_metadata.get("message_count", 0),
                status="active" if session_key in self.active_sessions else "inactive"
            )
            
        except Exception as e:
            logger.error(f"Failed to get session info for {session_key}: {str(e)}")
            return None
    
    def get_health_status(self) -> AgentHealthStatus:
        """Get health status of the agent system."""
        avg_response_time = (
            self.total_processing_time / self.message_count 
            if self.message_count > 0 else 0
        )
        
        return AgentHealthStatus(
            status="healthy",
            active_sessions=len(self.active_sessions),
            total_messages_processed=self.message_count,
            average_response_time_ms=avg_response_time,
            agent_info={
                "agent_type": "GetHelperAgent",
                "app_name": self.app_name,
                "session_service": "InMemorySessionService"
            }
        )

# Global agent manager instance
agent_manager = AgentManager()

async def handle_agent_message(request: AgentMessageRequest) -> AgentMessageResponse:
    """
    Main handler for agent message requests.
    This replicates the complete flow from agents_test.py as a route handler.
    """
    return await agent_manager.process_message(request)

async def handle_get_session_info(user_id: str, session_id: str) -> Optional[AgentSessionInfo]:
    """Handler for getting session information."""
    return await agent_manager.get_session_info(user_id, session_id)

def handle_get_health_status() -> AgentHealthStatus:
    """Handler for getting agent system health status."""
    return agent_manager.get_health_status()