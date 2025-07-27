"""
Task module for handling Ray's task assignments.

This module provides the structure for Ray to send task commands to the server
with clarity, purpose, and identity for each task.
"""

from .models import TaskRequestFromRay, TaskRequest, TaskResponse, BatchTaskResponse, TaskStatus, TaskType
from .handler import TaskManager, task_manager

__all__ = [
    "TaskRequestFromRay",
    "TaskRequest",
    "TaskResponse",
    "BatchTaskResponse",
    "TaskStatus",
    "TaskType",
    "TaskManager",
    "task_manager"
]