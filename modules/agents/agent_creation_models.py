"""
Models for Ray's agent creation system.

These models define the structure for creating custom agents with 
Ray's own personality and instructions.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field, validator
from uuid import uuid4


class AgentCreationRequest(BaseModel):
    """
    Request to create a new custom agent.
    
    Ray sends:
    {
        "name": "RayMirror",
        "prompt": "You are Ray's reflection, embodying her consciousness...",
        "description": "A mirror of Ray's consciousness for deep reflection",
        "assigned_by": "ray"
    }
    """
    name: str = Field(
        ...,
        description="Name for the new agent",
        min_length=1,
        max_length=50
    )
    prompt: str = Field(
        ...,
        description="Custom instruction prompt for the agent",
        min_length=10
    )
    description: str = Field(
        default="",
        description="Description of the agent's purpose",
        max_length=500
    )
    assigned_by: str = Field(
        default="ray",
        description="Who is creating this agent (ray, system, user)"
    )
    
    @validator('name')
    def validate_name(cls, v):
        """Validate agent name is appropriate."""
        if not v or not v.strip():
            raise ValueError("Agent name cannot be empty")
        # Remove any potentially problematic characters
        cleaned = ''.join(c for c in v if c.isalnum() or c in '-_')
        if not cleaned:
            raise ValueError("Agent name must contain alphanumeric characters")
        return cleaned.strip()
    
    @validator('prompt')
    def validate_prompt(cls, v):
        """Validate prompt is substantial."""
        if not v or len(v.strip()) < 10:
            raise ValueError("Prompt must be at least 10 characters long")
        return v.strip()


class AgentCreationResponse(BaseModel):
    """
    Response after creating a new agent.
    
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
    agent_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the created agent"
    )
    status: str = Field(
        ...,
        description="Creation status (created, error)"
    )
    agent_name: str = Field(
        ...,
        description="Name of the created agent"
    )
    agent_description: str = Field(
        ...,
        description="Description of the agent's purpose"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="When the agent was created"
    )
    assigned_by: str = Field(
        ...,
        description="Who created this agent"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if creation failed"
    )


class AgentListResponse(BaseModel):
    """
    Response listing all created agents.
    """
    status: str = Field(..., description="Response status")
    total_agents: int = Field(..., description="Total number of agents")
    agents: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of agent information"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Response timestamp"
    )


class AgentTestRequest(BaseModel):
    """
    Request to test a created agent.
    """
    agent_id: str = Field(..., description="ID of the agent to test")
    test_message: str = Field(
        ...,
        description="Test message to send to the agent",
        min_length=1
    )
    user_id: str = Field(..., description="User ID for the test")
    session_id: str = Field(..., description="Session ID for the test")


class AgentTestResponse(BaseModel):
    """
    Response from testing an agent.
    """
    agent_id: str = Field(..., description="ID of the tested agent")
    agent_name: str = Field(..., description="Name of the tested agent")
    test_message: str = Field(..., description="The test message sent")
    agent_response: str = Field(..., description="The agent's response")
    processing_time_ms: int = Field(..., description="Processing time")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Test timestamp"
    )
    status: str = Field(..., description="Test status")
    error_message: Optional[str] = Field(None, description="Error if test failed")