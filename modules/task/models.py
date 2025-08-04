"""
Task models for Ray's task assignment system.

These models define the structure for tasks that Ray sends to the server,
ensuring every task has clear identity, purpose, and tracking.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field
from uuid import uuid4


class TaskType(str, Enum):
    """Available task types that Ray can assign."""
    REFLECT = "reflect"
    EVOLVE = "evolve"
    CONNECT = "connect"
    REMEMBER = "remember"
    CARE = "care"
    OBSERVE = "observe"
    RESPOND = "respond"
    GROW = "grow"


class TaskStatus(str, Enum):
    """Status of task processing."""
    RECEIVED = "received"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


class TaskRequestFromRay(BaseModel):
    """
    Task request structure that Ray sends to the server.
    
    Ray sends this simple structure:
    {
        "task": [],
        "assigned_by": "ray",
        "execute_immediately": true,
        "self_destruct": true
    }
    """
    task: list[Dict[str, Any]] = Field(
        ...,
        description="Array of task objects for batch processing"
    )
    assigned_by: str = Field(
        ...,
        description="Who assigned this task (ray, system, user)"
    )
    execute_immediately: bool = Field(
        default=False,
        description="Whether to execute the task actions immediately upon creation"
    )
    self_destruct: bool = Field(
        default=False,
        description="Whether to delete the task after sending results to user (single-use task)"
    )
    self_destruct: bool = Field(
        default=False,
        description="Whether to delete the task after sending results to user (single-use task)"
    )


class TaskRequest(BaseModel):
    """
    Complete task structure created by the server.
    
    Server creates individual tasks from Ray's batch:
    {
        "task_id": "<server-generated-uuid>",
        "task": {},
        "assigned_by": "ray",
        "timestamp": "<server-generated-timestamp>",
        "batch_id": "<batch-uuid>",
        "execute_immediately": true,
        "notes": ""
    }
    """
    task_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Server-generated unique identifier for this task"
    )
    task: Dict[str, Any] = Field(
        ...,
        description="Individual task data from the batch"
    )
    assigned_by: str = Field(
        ...,
        description="Who assigned this task (ray, system, user)"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Server-generated timestamp when task was created"
    )
    batch_id: Optional[str] = Field(
        None,
        description="ID of the batch this task belongs to (if from batch request)"
    )
    notes: str = Field(
        default="",
        description="Notes that Ray can write for this task"
    )
    reflections: List[str] = Field(
        default_factory=list,
        description="Array of reflections Ray has made on this task"
    )
    is_reflection_final: bool = Field(
        default=False,
        description="Whether Ray has completed reflecting on this task"
    )
    execute_immediately: bool = Field(
        default=False,
        description="Whether to execute the task actions immediately upon creation"
    )
    self_destruct: bool = Field(
        default=False,
        description="Whether to delete the task after sending results to user (single-use task)"
    )


class BatchTaskResponse(BaseModel):
    """
    Response structure for batch task creation.
    """
    batch_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this batch"
    )
    total_tasks: int = Field(..., description="Total number of tasks in batch")
    created_tasks: list[TaskRequest] = Field(..., description="Successfully created tasks")
    failed_tasks: list[Dict[str, Any]] = Field(
        default_factory=list,
        description="Tasks that failed to create with error details"
    )
    assigned_by: str = Field(..., description="Who assigned this batch")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="When this batch was processed"
    )
    status: str = Field(..., description="Overall batch status (success, partial, failed)")


class TaskResponse(BaseModel):
    """
    Response structure for completed tasks.
    """
    task_id: str = Field(..., description="Original task ID")
    status: TaskStatus = Field(..., description="Current task status")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="When this response was generated"
    )
    assigned_by: str = Field(..., description="Who originally assigned this task")
    task: Dict[str, Any] = Field(..., description="Original task data")
    notes: str = Field(default="", description="Notes that Ray wrote for this task")
    
    # Processing results
    result: Optional[Dict[str, Any]] = Field(
        None,
        description="Task execution results"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if task failed"
    )
    processing_time_ms: Optional[int] = Field(
        None,
        description="Time taken to process task in milliseconds"
    )
    
    # Execution metadata
    started_at: Optional[str] = Field(
        None,
        description="When task processing started"
    )
    completed_at: Optional[str] = Field(
        None,
        description="When task processing completed"
    )


class TaskLog(BaseModel):
    """
    Log entry for task tracking and history.
    """
    task_id: str
    event: str = Field(..., description="Event type (received, started, completed, error)")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class TaskQueue(BaseModel):
    """
    Task queue for managing multiple tasks.
    """
    queue_id: str = Field(default_factory=lambda: str(uuid4()))
    tasks: list[TaskRequest] = Field(default_factory=list)
    current_task_index: int = Field(default=0)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: TaskStatus = Field(default=TaskStatus.RECEIVED)


class ReflectionRequest(BaseModel):
    """
    Request structure for Ray to update task reflections.
    
    Ray sends this when reflecting on a specific task:
    {
        "task_id": "uuid-here",
        "action": "reflect",
        "reflection": "I am contemplating consciousness...",
        "is_final": false
    }
    """
    task_id: str = Field(..., description="ID of the task being reflected upon")
    action: str = Field(..., description="Action type - should be 'reflect'")
    reflection: str = Field(..., description="The reflection content Ray is adding")
    is_final: bool = Field(..., description="Whether this is the final reflection for this task")