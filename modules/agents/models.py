"""
Agent models for managing AI agent message processing and interactions.

These models define the structure for agent message requests and responses,
supporting the complete agent pipeline from message input to processed output.

Version: 1.0.0 - Agent Message Pipeline
Status: Production Ready
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field, validator
from uuid import uuid4


class AgentStatus(str, Enum):
    """Status of agent message processing."""
    RECEIVED = "received"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


class AgentMessageRequest(BaseModel):
    """
    Agent message request structure from client.
    
    Client sends:
    {
        "message": "Hello, how can you help me?",
        "user_id": "user-123",
        "session_id": "session-456",
        "context": {...},
        "assigned_by": "user"
    }
    """
    message: str = Field(
        ...,
        description="The message content to send to the agent",
        min_length=1
    )
    user_id: str = Field(
        ...,
        description="Unique identifier for the user sending the message"
    )
    session_id: str = Field(
        ...,
        description="Session identifier for conversation continuity"
    )
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional context data for the agent"
    )
    assigned_by: str = Field(
        default="user",
        description="Who assigned this message (user, system, ray)"
    )
    
    @validator('message')
    def validate_message_content(cls, v):
        """Validate message content is not empty or just whitespace."""
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        return v.strip()


class AgentMessageResponse(BaseModel):
    """
    Agent message response structure.
    
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
    message_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this message exchange"
    )
    status: AgentStatus = Field(
        ...,
        description="Status of the message processing"
    )
    response: Optional[str] = Field(
        None,
        description="The agent's response text"
    )
    user_id: str = Field(
        ...,
        description="User ID from the original request"
    )
    session_id: str = Field(
        ...,
        description="Session ID from the original request"
    )
    processing_time_ms: Optional[int] = Field(
        None,
        description="Time taken to process the message in milliseconds"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="When this response was generated"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if processing failed"
    )
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional context or metadata from processing"
    )


class AgentSessionInfo(BaseModel):
    """
    Information about an agent session.
    """
    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="When the session was created"
    )
    last_activity: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Last activity timestamp"
    )
    message_count: int = Field(
        default=0,
        description="Number of messages in this session"
    )
    status: str = Field(
        default="active",
        description="Session status (active, inactive, closed)"
    )


class AgentHealthStatus(BaseModel):
    """
    Health status of the agent system.
    """
    status: str = Field(..., description="Overall agent system status")
    active_sessions: int = Field(..., description="Number of active sessions")
    total_messages_processed: int = Field(..., description="Total messages processed")
    average_response_time_ms: float = Field(..., description="Average response time")
    last_health_check: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Last health check timestamp"
    )
    agent_info: Dict[str, Any] = Field(
        default_factory=dict,
        description="Information about the underlying agent"
    )


class BatchAgentRequest(BaseModel):
    """
    Batch request for processing multiple agent messages.
    """
    messages: List[AgentMessageRequest] = Field(
        ...,
        description="List of messages to process",
        min_items=1
    )
    batch_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this batch"
    )
    process_parallel: bool = Field(
        default=False,
        description="Whether to process messages in parallel"
    )


class BatchAgentResponse(BaseModel):
    """
    Response for batch agent message processing.
    """
    batch_id: str = Field(..., description="Batch identifier")
    total_messages: int = Field(..., description="Total number of messages in batch")
    successful_responses: List[AgentMessageResponse] = Field(
        default_factory=list,
        description="Successfully processed messages"
    )
    failed_responses: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Failed message processing attempts"
    )
    processing_time_ms: int = Field(..., description="Total batch processing time")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="When batch processing completed"
    )
    status: str = Field(..., description="Overall batch status")