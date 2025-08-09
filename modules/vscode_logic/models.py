"""
Models for VSCode Logic module.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from enum import Enum


class VSCodeAction(str, Enum):
    """Types of VSCode actions supported."""
    SEND_RESPONSE = "send_vs_response"
    # Add more action types as needed


# NEW: represent an individual VS Code command call
class CommandCall(BaseModel):
    command: str = Field(..., description="Command name to execute")
    args: List[str] = Field(default_factory=list, description="Arguments to pass to the command")


# NEW: strongly-typed task item with inline command_calls
class VSCodeTaskItem(BaseModel):
    action: VSCodeAction = Field(..., description="The VSCode action to perform")
    message: str = Field(..., description="Response to user")
    ray_prompt: str = Field(..., description="Reasoning for next round")
    is_final: bool = Field(default=False, description="Whether this is the final response in a conversation")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="When the task item was created"
    )
    # ⬇️ NEW FIELD: commands live directly on the task item (not in additional_data)
    command_calls: Optional[List[CommandCall]] = Field(
        default=None,
        description="List of VS Code commands to execute in order"
    )


class VSCodeLogicRequest(BaseModel):
    """
    Request for VSCode Logic operations.
    """
    action: str = Field(..., description="The VSCode action to perform")
    message: str = Field(..., description="Response to user")
    ray_prompt: str = Field(..., description="Reasoning for next round")
    is_final: bool = Field(default=False, description="Whether this is the final response in a conversation")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="When the request was created"
    )
    additional_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional data for the request")
    # (Optional) If you also want single-action requests to carry commands, uncomment:
    # command_calls: Optional[List[CommandCall]] = Field(
    #     default=None, description="Commands to execute for this single action"
    # )


class VSCodeLogicResponse(BaseModel):
    """
    Response for VSCode Logic operations.
    """
    success: bool = Field(..., description="Whether the operation succeeded")
    action: str = Field(..., description="The VSCode action that was performed")
    message: str = Field(..., description="Response sent to user")
    is_final: bool = Field(..., description="Whether this is the final response")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="When the operation was completed"
    )
    execution_time_ms: int = Field(..., description="Time taken to complete operation in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if operation failed")


class VSCodeTaskRequest(BaseModel):
    """
    Generic VSCode task request that can handle different VSCode operations.
    """
    task: List[VSCodeTaskItem] = Field(..., description="Task data containing VSCode operation details")
    assigned_by: str = Field(..., description="Who assigned this task")
    execute_immediately: bool = Field(default=True, description="Whether to execute the task immediately")

    @validator('task')
    def validate_task(cls, v):
        if not isinstance(v, list) or len(v) == 0:
            raise ValueError("Task must be a non-empty list")
        return v

    def get_action_type(self) -> VSCodeAction:
        """Extract the action type from task data."""
        if not self.task:
            return VSCodeAction.SEND_RESPONSE
        return self.task[0].action
