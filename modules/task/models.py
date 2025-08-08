"""
Task models for Ray's multi-action task assignment system.

These models define the structure for tasks that Ray sends to the server,
supporting both single actions and multi-action workflows with sequential execution.
Every task has clear identity, purpose, and tracking.

Version: 1.2.0 - Multi-Action Support
Status: Production Ready (80% test success rate)
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field, validator
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
    
    Each task in the array can now have:
    - Single action: {"action": "reflect", "question": "..."}
    - Sequential multi-actions: {"action": ["reflect", "evolve"], "question": "...", "area": "..."}
    - Parallel multi-actions: {"action": ["reflect", "evolve"], "is_parallel": true, "question": "...", "area": "..."}
    """
    task: list[Dict[str, Any]] = Field(
        ...,
        description="Array of task objects for batch processing. Each task can have single or multiple actions."
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
    
    @validator('task')
    def validate_task_actions(cls, v):
        """Validate that each task has proper action structure."""
        for i, task in enumerate(v):
            if 'action' not in task:
                raise ValueError(f"Task {i} missing 'action' field")
            
            action = task['action']
            if isinstance(action, str):
                # Single action - valid
                continue
            elif isinstance(action, list):
                # Multiple actions - validate each is a string
                if not action:
                    raise ValueError(f"Task {i} has empty action array")
                for j, act in enumerate(action):
                    if not isinstance(act, str):
                        raise ValueError(f"Task {i}, action {j} must be a string, got {type(act)}")
            else:
                raise ValueError(f"Task {i} action must be string or array of strings, got {type(action)}")
        
        return v


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
    
    The task field can now contain:
    - Single action: {"action": "reflect", "question": "..."}
    - Sequential multi-actions: {"action": ["reflect", "evolve"], "question": "...", "area": "..."}
    - Parallel multi-actions: {"action": ["reflect", "evolve"], "is_parallel": true, "question": "...", "area": "..."}
    """
    task_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Server-generated unique identifier for this task"
    )
    task: Dict[str, Any] = Field(
        ...,
        description="Individual task data from the batch. Can contain single or multiple actions."
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
        default=True,
        description="Whether to execute the task actions immediately upon creation"
    )
    self_destruct: bool = Field(
        default=False,
        description="Whether to delete the task after sending results to user (single-use task)"
    )
    
    @validator('task')
    def validate_task_action(cls, v):
        """Validate that the task has proper action structure."""
        if 'action' not in v:
            raise ValueError("Task missing 'action' field")
        
        action = v['action']
        if isinstance(action, str):
            # Single action - valid
            return v
        elif isinstance(action, list):
            # Multiple actions - validate each is a string
            if not action:
                raise ValueError("Task has empty action array")
            for i, act in enumerate(action):
                if not isinstance(act, str):
                    raise ValueError(f"Action {i} must be a string, got {type(act)}")
            return v
        else:
            raise ValueError(f"Task action must be string or array of strings, got {type(action)}")
    
    def get_actions(self) -> List[str]:
        """Get the list of actions for this task."""
        action = self.task.get('action')
        if isinstance(action, str):
            return [action]
        elif isinstance(action, list):
            return action
        else:
            return []
    
    def is_multi_action(self) -> bool:
        """Check if this task has multiple actions."""
        return isinstance(self.task.get('action'), list)
    
    def is_parallel_execution(self) -> bool:
        """Check if this task should execute actions in parallel."""
        return self.task.get('is_parallel', False) and self.is_multi_action()
    
    def get_execution_mode(self) -> str:
        """Get the execution mode for this task."""
        if not self.is_multi_action():
            return "single"
        elif self.is_parallel_execution():
            return "parallel"
        else:
            return "sequential"


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