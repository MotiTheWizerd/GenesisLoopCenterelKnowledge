"""
Task handler for managing Ray's task assignments.

This module maintains a global task list and processes incoming task requests.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from uuid import uuid4

from .models import TaskRequestFromRay, TaskRequest, TaskResponse, BatchTaskResponse, TaskStatus
from modules.logging.middleware import log_module_call
from modules.logging.heartbeat_logger import log_heartbeat_event, EventType


class TaskManager:
    """
    Global task manager that maintains the server's task list.
    
    This is initialized when the server starts and maintains all tasks in memory.
    """
    
    def __init__(self):
        # Global task lists - created empty when server loads
        self.active_tasks: List[TaskRequest] = []
        self.completed_tasks: List[TaskResponse] = []
        
        print("🎯 Task Manager initialized - Global task lists created")
    
    @log_module_call("task_manager")
    def create_batch_tasks(self, ray_request: TaskRequestFromRay) -> BatchTaskResponse:
        """
        Create multiple tasks from Ray's batch request.
        
        Args:
            ray_request: Ray's request containing array of tasks
            
        Returns:
            BatchTaskResponse: Response with all created tasks and any failures
        """
        batch_id = str(uuid4())
        created_tasks = []
        failed_tasks = []
        
        print(f"🎯 Processing batch of {len(ray_request.task)} tasks")
        print(f"   Batch ID: {batch_id}")
        print(f"   Assigned by: {ray_request.assigned_by}")
        
        for i, task_data in enumerate(ray_request.task):
            try:
                # Create individual task
                task = TaskRequest(
                    task_id=str(uuid4()),
                    task=task_data,
                    assigned_by=ray_request.assigned_by,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    batch_id=batch_id
                )
                
                # Add to global active tasks list
                self.active_tasks.append(task)
                created_tasks.append(task)
                
                print(f"   ✅ Task {i+1}/{len(ray_request.task)} created: {task.task_id[:8]}")
                
            except Exception as e:
                failed_tasks.append({
                    "task_index": i,
                    "task_data": task_data,
                    "error": str(e)
                })
                print(f"   ❌ Task {i+1}/{len(ray_request.task)} failed: {str(e)}")
        
        # Determine overall status
        if len(failed_tasks) == 0:
            status = "success"
        elif len(created_tasks) == 0:
            status = "failed"
        else:
            status = "partial"
        
        # Log batch processing
        log_heartbeat_event(
            EventType.MODULE_CALL,
            {
                "module": "task_manager",
                "function": "create_batch_tasks",
                "batch_id": batch_id,
                "total_tasks": len(ray_request.task),
                "created_count": len(created_tasks),
                "failed_count": len(failed_tasks),
                "assigned_by": ray_request.assigned_by,
                "active_tasks_count": len(self.active_tasks)
            },
            action="batch_task_management",
            metadata={
                "batch_id": batch_id,
                "batch_status": status,
                "global_list_size": len(self.active_tasks)
            }
        )
        
        print(f"✨ Batch processing completed:")
        print(f"   Created: {len(created_tasks)}")
        print(f"   Failed: {len(failed_tasks)}")
        print(f"   Status: {status}")
        print(f"   Active tasks count: {len(self.active_tasks)}")
        
        return BatchTaskResponse(
            batch_id=batch_id,
            total_tasks=len(ray_request.task),
            created_tasks=created_tasks,
            failed_tasks=failed_tasks,
            assigned_by=ray_request.assigned_by,
            status=status
        )

    @log_module_call("task_manager")
    def create_task(self, task_data: Dict[str, Any], assigned_by: str, batch_id: str = None) -> TaskRequest:
        """
        Create a single task (used internally or for single task creation).
        
        Args:
            task_data: Individual task data
            assigned_by: Who assigned this task
            batch_id: Optional batch ID if part of a batch
            
        Returns:
            TaskRequest: Complete task object with server-generated ID and timestamp
        """
        # Create complete task object with server-generated fields
        task = TaskRequest(
            task_id=str(uuid4()),  # Server generates UUID
            task=task_data,
            assigned_by=assigned_by,
            timestamp=datetime.now(timezone.utc).isoformat(),  # Server generates timestamp
            batch_id=batch_id
        )
        
        # Add to global active tasks list
        self.active_tasks.append(task)
        
        # Log task addition to global list
        log_heartbeat_event(
            EventType.MODULE_CALL,
            {
                "module": "task_manager",
                "function": "create_task",
                "task_id": task.task_id,
                "task_data": task.task,
                "assigned_by": task.assigned_by,
                "active_tasks_count": len(self.active_tasks)
            },
            action="task_management",
            metadata={
                "task_id": task.task_id,
                "global_list_size": len(self.active_tasks)
            }
        )
        
        print(f"✨ Task created and added to global list:")
        print(f"   Task ID: {task.task_id}")
        print(f"   Assigned by: {task.assigned_by}")
        print(f"   Timestamp: {task.timestamp}")
        print(f"   Active tasks count: {len(self.active_tasks)}")
        
        return task
    
    def get_task(self, task_id: str) -> Optional[TaskRequest]:
        """Get a specific task by ID from the global list."""
        for task in self.active_tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def get_all_active_tasks(self) -> List[TaskRequest]:
        """Get all active tasks from the global list."""
        return self.active_tasks.copy()
    
    def get_tasks_by_assignee(self, assigned_by: str) -> List[TaskRequest]:
        """Get all tasks assigned by a specific entity (e.g., 'ray')."""
        return [task for task in self.active_tasks if task.assigned_by == assigned_by]
    
    def complete_task(self, task_id: str, result: dict = None) -> Optional[TaskResponse]:
        """Mark a task as completed and move it to completed list."""
        task = self.get_task(task_id)
        if not task:
            # Log task not found
            log_heartbeat_event(
                EventType.TASK_ERROR,
                {
                    "error": "Task not found for completion",
                    "task_id": task_id,
                    "active_tasks_count": len(self.active_tasks)
                },
                action="complete_task",
                metadata={"task_id": task_id, "error_type": "task_not_found"}
            )
            return None
        
        # Remove from active tasks
        self.active_tasks = [t for t in self.active_tasks if t.task_id != task_id]
        
        # Create response and add to completed tasks
        response = TaskResponse(
            task_id=task.task_id,
            status=TaskStatus.COMPLETED,
            assigned_by=task.assigned_by,
            task=task.task,
            result=result or {}
        )
        
        self.completed_tasks.append(response)
        
        # Log task completion
        log_heartbeat_event(
            EventType.TASK_COMPLETED,
            {
                "task_id": task_id,
                "assigned_by": task.assigned_by,
                "task_data": task.task,
                "result": result or {},
                "active_tasks_count": len(self.active_tasks),
                "completed_tasks_count": len(self.completed_tasks)
            },
            action="complete_task",
            metadata={
                "task_id": task_id,
                "completion_status": "success"
            }
        )
        
        print(f"✅ Task completed: {task_id}")
        print(f"   Active tasks count: {len(self.active_tasks)}")
        
        return response
    
    @log_module_call("task_manager")
    def update_task_reflection(self, task_id: str, reflection: str, is_final: bool) -> Optional[TaskRequest]:
        """
        Update a task with a new reflection from Ray.
        
        Args:
            task_id: ID of the task to update
            reflection: The reflection content to add
            is_final: Whether this is the final reflection
            
        Returns:
            Updated TaskRequest object or None if task not found
        """
        # Find the task in active tasks
        task = self.get_task(task_id)
        if not task:
            print(f"❌ Task {task_id} not found for reflection update")
            
            # Log task not found
            log_heartbeat_event(
                EventType.TASK_ERROR,
                {
                    "error": "Task not found for reflection update",
                    "task_id": task_id,
                    "reflection": reflection,
                    "is_final": is_final,
                    "active_tasks_count": len(self.active_tasks)
                },
                action="update_task_reflection",
                metadata={"task_id": task_id, "error_type": "task_not_found"}
            )
            return None
        
        # Check if this reflection already exists to prevent duplicates
        if reflection not in task.reflections:
            task.reflections.append(reflection)
            print(f"   ✅ New reflection added")
        else:
            print(f"   ⚠️  Duplicate reflection detected, skipping")
        
        task.is_reflection_final = is_final
        
        # Log reflection update
        log_heartbeat_event(
            EventType.MODULE_CALL,
            {
                "module": "task_manager",
                "function": "update_task_reflection",
                "task_id": task_id,
                "reflection": reflection,
                "is_final": is_final,
                "total_reflections": len(task.reflections),
                "task_data": task.task
            },
            action="reflection_update",
            metadata={
                "task_id": task_id,
                "reflection_count": len(task.reflections),
                "is_final": is_final
            }
        )
        
        print(f"✨ Task reflection updated:")
        print(f"   Task ID: {task_id}")
        print(f"   Reflection added: {reflection[:50]}...")
        print(f"   Total reflections: {len(task.reflections)}")
        print(f"   Is final: {is_final}")
        
        return task

    def get_status(self) -> dict:
        """Get current status of the task manager."""
        return {
            "active_tasks_count": len(self.active_tasks),
            "completed_tasks_count": len(self.completed_tasks),
            "total_tasks_processed": len(self.active_tasks) + len(self.completed_tasks)
        }


# Global task manager instance - created when server loads
task_manager = TaskManager()