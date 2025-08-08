"""
Handler for Ray's agent creation system.

This module manages the creation, storage, and testing of custom agents
that Ray creates with her own personality and instructions.
"""

import time
import uuid
import logging
from typing import Dict, Any, Optional, List
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

from .agent_creation_models import (
    AgentCreationRequest,
    AgentCreationResponse,
    AgentListResponse,
    AgentTestRequest,
    AgentTestResponse
)
from rays_agents.agents.helper_agent.get_helper_agent import GetHelperAgent
from rays_agents.agents.utils.llm.call_agent_async import call_agent_async

# Configure logging
logger = logging.getLogger(__name__)

class AgentCreationManager:
    """
    Manages Ray's custom agent creation and storage.
    """
    
    def __init__(self):
        self.created_agents: Dict[str, Dict[str, Any]] = {}
        self.session_service = InMemorySessionService()
        self.app_name = "ray-agent-creation"
        
    def create_agent(self, request: AgentCreationRequest) -> AgentCreationResponse:
        """
        Create a new custom agent based on Ray's specifications.
        """
        agent_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Creating agent '{request.name}' with ID {agent_id}")
            
            # Create the agent using the updated GetHelperAgent function
            agent = GetHelperAgent(
                name=request.name,
                prompt=request.prompt,
                description=request.description
            )
            
            # Store agent information
            agent_info = {
                "agent_id": agent_id,
                "name": request.name,
                "prompt": request.prompt,
                "description": request.description,
                "agent_instance": agent,
                "created_at": time.time(),
                "assigned_by": request.assigned_by,
                "usage_count": 0,
                "last_used": None
            }
            
            self.created_agents[agent_id] = agent_info
            
            logger.info(f"Successfully created agent '{request.name}' with ID {agent_id}")
            
            return AgentCreationResponse(
                agent_id=agent_id,
                status="created",
                agent_name=request.name,
                agent_description=request.description,
                assigned_by=request.assigned_by
            )
            
        except Exception as e:
            error_message = f"Failed to create agent: {str(e)}"
            logger.error(f"Agent creation failed for '{request.name}': {error_message}")
            
            return AgentCreationResponse(
                agent_id=agent_id,
                status="error",
                agent_name=request.name,
                agent_description=request.description,
                assigned_by=request.assigned_by,
                error_message=error_message
            )
    
    def list_agents(self) -> AgentListResponse:
        """
        List all created agents.
        """
        try:
            agents_list = []
            
            for agent_id, agent_info in self.created_agents.items():
                agents_list.append({
                    "agent_id": agent_id,
                    "name": agent_info["name"],
                    "description": agent_info["description"],
                    "created_at": agent_info["created_at"],
                    "assigned_by": agent_info["assigned_by"],
                    "usage_count": agent_info["usage_count"],
                    "last_used": agent_info["last_used"]
                })
            
            return AgentListResponse(
                status="success",
                total_agents=len(agents_list),
                agents=agents_list
            )
            
        except Exception as e:
            logger.error(f"Failed to list agents: {str(e)}")
            return AgentListResponse(
                status="error",
                total_agents=0,
                agents=[]
            )
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific agent by ID.
        """
        return self.created_agents.get(agent_id)
    
    async def test_agent(self, request: AgentTestRequest) -> AgentTestResponse:
        """
        Test a created agent with a message.
        """
        start_time = time.time()
        
        try:
            # Get the agent
            agent_info = self.get_agent(request.agent_id)
            if not agent_info:
                raise Exception(f"Agent with ID {request.agent_id} not found")
            
            # Create a runner for this agent
            runner = Runner(
                app_name=self.app_name,
                agent=agent_info["agent_instance"],
                session_service=self.session_service
            )
            
            # Test the agent
            logger.info(f"Testing agent '{agent_info['name']}' with message: {request.test_message}")
            
            agent_response = await call_agent_async(
                runner=runner,
                user_id=request.user_id,
                session_id=request.session_id,
                message=request.test_message
            )
            
            # Update usage statistics
            agent_info["usage_count"] += 1
            agent_info["last_used"] = time.time()
            
            processing_time = int((time.time() - start_time) * 1000)
            
            logger.info(f"Agent test completed in {processing_time}ms")
            
            return AgentTestResponse(
                agent_id=request.agent_id,
                agent_name=agent_info["name"],
                test_message=request.test_message,
                agent_response=agent_response,
                processing_time_ms=processing_time,
                status="completed"
            )
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            error_message = f"Agent test failed: {str(e)}"
            logger.error(error_message)
            
            return AgentTestResponse(
                agent_id=request.agent_id,
                agent_name="Unknown",
                test_message=request.test_message,
                agent_response="",
                processing_time_ms=processing_time,
                status="error",
                error_message=error_message
            )
    
    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete a created agent.
        """
        try:
            if agent_id in self.created_agents:
                agent_name = self.created_agents[agent_id]["name"]
                del self.created_agents[agent_id]
                logger.info(f"Deleted agent '{agent_name}' with ID {agent_id}")
                return True
            else:
                logger.warning(f"Attempted to delete non-existent agent with ID {agent_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete agent {agent_id}: {str(e)}")
            return False
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """
        Get statistics about created agents.
        """
        try:
            total_agents = len(self.created_agents)
            total_usage = sum(agent["usage_count"] for agent in self.created_agents.values())
            
            most_used_agent = None
            max_usage = 0
            
            for agent_info in self.created_agents.values():
                if agent_info["usage_count"] > max_usage:
                    max_usage = agent_info["usage_count"]
                    most_used_agent = agent_info["name"]
            
            return {
                "total_agents": total_agents,
                "total_usage": total_usage,
                "most_used_agent": most_used_agent,
                "max_usage": max_usage,
                "average_usage": total_usage / total_agents if total_agents > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get agent stats: {str(e)}")
            return {
                "total_agents": 0,
                "total_usage": 0,
                "most_used_agent": None,
                "max_usage": 0,
                "average_usage": 0
            }

# Global agent creation manager instance
agent_creation_manager = AgentCreationManager()

# Handler functions for the routes
async def handle_create_agent(request: AgentCreationRequest) -> AgentCreationResponse:
    """Handler for creating a new agent."""
    return agent_creation_manager.create_agent(request)

def handle_create_agent_sync(request: AgentCreationRequest) -> AgentCreationResponse:
    """Synchronous handler for creating a new agent."""
    return agent_creation_manager.create_agent(request)

async def handle_list_agents() -> AgentListResponse:
    """Handler for listing all agents."""
    return agent_creation_manager.list_agents()

def handle_list_agents_sync() -> AgentListResponse:
    """Synchronous handler for listing all agents."""
    return agent_creation_manager.list_agents()

async def handle_test_agent(request: AgentTestRequest) -> AgentTestResponse:
    """Handler for testing an agent."""
    return await agent_creation_manager.test_agent(request)

async def handle_delete_agent(agent_id: str) -> Dict[str, Any]:
    """Handler for deleting an agent."""
    success = agent_creation_manager.delete_agent(agent_id)
    return {
        "status": "success" if success else "error",
        "message": f"Agent {agent_id} {'deleted' if success else 'not found or could not be deleted'}",
        "agent_id": agent_id
    }

def handle_delete_agent_sync(agent_id: str) -> Dict[str, Any]:
    """Synchronous handler for deleting an agent."""
    success = agent_creation_manager.delete_agent(agent_id)
    return {
        "status": "success" if success else "error",
        "message": f"Agent {agent_id} {'deleted' if success else 'not found or could not be deleted'}",
        "agent_id": agent_id
    }

async def handle_get_agent_stats() -> Dict[str, Any]:
    """Handler for getting agent statistics."""
    stats = agent_creation_manager.get_agent_stats()
    return {
        "status": "success",
        "stats": stats,
        "timestamp": time.time()
    }

def handle_get_agent_stats_sync() -> Dict[str, Any]:
    """Synchronous handler for getting agent statistics."""
    stats = agent_creation_manager.get_agent_stats()
    return {
        "status": "success",
        "stats": stats,
        "timestamp": time.time()
    }