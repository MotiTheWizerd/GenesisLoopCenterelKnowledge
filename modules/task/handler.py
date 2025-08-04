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
                    batch_id=batch_id,
                    execute_immediately=ray_request.execute_immediately,
                    self_destruct=ray_request.self_destruct
                )
                
                # Add to global active tasks list
                self.active_tasks.append(task)
                created_tasks.append(task)
                
                # Execute immediately if requested
                if ray_request.execute_immediately:
                    execution_result = self._execute_task_immediately(task)
                    if execution_result:
                        # Update the task with execution results
                        task.task["execution_result"] = execution_result
                        print(f"   ⚡ Task {i+1}/{len(ray_request.task)} executed immediately: {task.task_id[:8]}")
                    else:
                        print(f"   ⚠️  Task {i+1}/{len(ray_request.task)} immediate execution failed: {task.task_id[:8]}")
                else:
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
        
        # Handle self-destruct tasks after response is prepared
        response = BatchTaskResponse(
            batch_id=batch_id,
            total_tasks=len(ray_request.task),
            created_tasks=created_tasks,
            failed_tasks=failed_tasks,
            assigned_by=ray_request.assigned_by,
            status=status
        )
        
        # Self-destruct tasks if requested (after response is created but before returning)
        if ray_request.self_destruct:
            self._self_destruct_tasks(created_tasks)
            print(f"💥 Self-destructed {len(created_tasks)} tasks after response preparation")
        
        return response

    @log_module_call("task_manager")
    def create_task(self, task_data: Dict[str, Any], assigned_by: str, batch_id: str = None, execute_immediately: bool = False, self_destruct: bool = False) -> TaskRequest:
        """
        Create a single task (used internally or for single task creation).
        
        Args:
            task_data: Individual task data
            assigned_by: Who assigned this task
            batch_id: Optional batch ID if part of a batch
            execute_immediately: Whether to execute the task immediately
            
        Returns:
            TaskRequest: Complete task object with server-generated ID and timestamp
        """
        # Create complete task object with server-generated fields
        task = TaskRequest(
            task_id=str(uuid4()),  # Server generates UUID
            task=task_data,
            assigned_by=assigned_by,
            timestamp=datetime.now(timezone.utc).isoformat(),  # Server generates timestamp
            batch_id=batch_id,
            execute_immediately=execute_immediately,
            self_destruct=self_destruct
        )
        
        # Add to global active tasks list
        self.active_tasks.append(task)
        
        # Execute immediately if requested
        if execute_immediately:
            execution_result = self._execute_task_immediately(task)
            if execution_result:
                task.task["execution_result"] = execution_result
                print(f"   ⚡ Task executed immediately")
        
        # Log task addition to global list
        log_heartbeat_event(
            EventType.MODULE_CALL,
            {
                "module": "task_manager",
                "function": "create_task",
                "task_id": task.task_id,
                "task_data": task.task,
                "assigned_by": task.assigned_by,
                "execute_immediately": execute_immediately,
                "active_tasks_count": len(self.active_tasks)
            },
            action="task_management",
            metadata={
                "task_id": task.task_id,
                "global_list_size": len(self.active_tasks),
                "immediate_execution": execute_immediately
            }
        )
        
        print(f"✨ Task created and added to global list:")
        print(f"   Task ID: {task.task_id}")
        print(f"   Assigned by: {task.assigned_by}")
        print(f"   Execute immediately: {execute_immediately}")
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

    def _execute_task_immediately(self, task: TaskRequest) -> Optional[Dict[str, Any]]:
        """
        Execute a task immediately based on its action type.
        
        Args:
            task: The task to execute
            
        Returns:
            Dict with execution results or None if execution failed
        """
        try:
            task_data = task.task
            action = task_data.get("action")
            
            print(f"⚡ Executing task immediately: {action}")
            
            # Reflection actions
            if action == "reflect":
                return self._execute_reflection_task(task_data)
            
            # Evolution actions
            elif action == "evolve":
                return self._execute_evolution_task(task_data)
            
            # Directory actions
            elif action in [
                "list_directory", 
                "find_files", 
                "search_content", 
                "get_file_info", 
                "explore_tree",
                "find_by_extension",
                "recent_files",
                "save_to_file",
                "rename_file",
                "delete_file",
                "move_file",
                "get_current_directory"
            ]:
                return self._execute_directory_action(task_data)
            
            # Web actions
            elif action in ["web_search", "web_scrape"]:
                return self._execute_web_action(task_data)
            
            # File operations
            elif action in ["overwrite_file", "write_file", "read_file"]:
                return self._execute_file_operation(task_data)
            
            # Health actions
            elif action in ["health_check", "system_status"]:
                return self._execute_health_action(task_data)
            
            # Other actions can be added here
            else:
                print(f"   ⚠️  Unknown action for immediate execution: {action}")
                return {"error": f"Unknown action: {action}", "executed": False}
                
        except Exception as e:
            print(f"   ❌ Immediate execution failed: {str(e)}")
            return {"error": str(e), "executed": False}
    
    def _execute_directory_action(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute directory-related actions immediately."""
        try:
            from modules.directory.handler import directory_manager
            from modules.directory.models import DirectorySearchRequest, ActionType
            
            # Convert task data to DirectorySearchRequest
            request = DirectorySearchRequest(
                action=ActionType(task_data.get("action")),
                path=task_data.get("path", "."),
                query=task_data.get("query"),
                recursive=task_data.get("recursive", False),
                max_depth=task_data.get("max_depth"),
                include_hidden=task_data.get("include_hidden", False),
                file_extensions=task_data.get("file_extensions"),
                assigned_by=task_data.get("assigned_by", "system")
            )
            
            # Execute the directory search
            response = directory_manager.search_directory(request)
            
            return {
                "executed": True,
                "action": task_data.get("action"),
                "results": {
                    "total_results": response.search_result.total_results,
                    "files_found": len(response.search_result.files_found),
                    "directories_found": len(response.search_result.directories_found),
                    "execution_time_ms": response.search_result.execution_time_ms,
                    "success": response.search_result.success
                },
                "response": response.dict()
            }
            
        except Exception as e:
            return {"executed": False, "error": str(e)}
    
    def _execute_web_action(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web-related actions immediately."""
        try:
            from modules.web.handler import web_manager
            
            action = task_data.get("action")
            if action == "web_search":
                # Execute web search
                result = web_manager.search(
                    query=task_data.get("query", ""),
                    max_results=task_data.get("max_results", 5)
                )
                return {"executed": True, "action": action, "results": result}
            elif action == "web_scrape":
                # Execute web scraping
                result = web_manager.scrape_url(
                    url=task_data.get("url", ""),
                    extract_content=task_data.get("extract_content", True)
                )
                return {"executed": True, "action": action, "results": result}
            else:
                return {"executed": False, "error": f"Unknown web action: {action}"}
                
        except Exception as e:
            return {"executed": False, "error": str(e)}
    
    def _execute_health_action(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute health-related actions immediately."""
        try:
            from modules.health.handler import health_manager
            
            action = task_data.get("action")
            if action == "health_check":
                result = health_manager.get_system_health()
                return {"executed": True, "action": action, "results": result}
            elif action == "system_status":
                result = health_manager.get_detailed_status()
                return {"executed": True, "action": action, "results": result}
            else:
                return {"executed": False, "error": f"Unknown health action: {action}"}
                
        except Exception as e:
            return {"executed": False, "error": str(e)}
    
    def _execute_reflection_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute reflection tasks immediately."""
        try:
            from modules.reflect.handler import reflect_manager
            
            question = task_data.get("question", "")
            if not question:
                return {"executed": False, "error": "No question provided for reflection"}
            
            # Execute reflection
            result = reflect_manager.process_reflection(question)
            
            return {
                "executed": True,
                "action": "reflect",
                "question": question,
                "results": result
            }
                
        except Exception as e:
            return {"executed": False, "error": str(e)}
    
    def _execute_evolution_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute evolution tasks immediately."""
        try:
            # For now, just acknowledge the evolution task
            # This can be expanded when evolution module is implemented
            area = task_data.get("area", "unknown")
            
            return {
                "executed": True,
                "action": "evolve",
                "area": area,
                "results": {
                    "status": "acknowledged",
                    "message": f"Evolution task for area '{area}' has been acknowledged",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
                
        except Exception as e:
            return {"executed": False, "error": str(e)}
    
    def _execute_file_operation(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file operations immediately."""
        try:
            from modules.file_ops.handler import file_ops_manager
            
            # Create task request for file operations
            file_task_data = {
                "task": task_data,
                "assigned_by": task_data.get("assigned_by", "system")
            }
            
            # Execute the file operation
            response = file_ops_manager.handle_task(file_task_data)
            
            return {
                "executed": True,
                "action": task_data.get("action"),
                "results": response.dict()
            }
                
        except Exception as e:
            return {"executed": False, "error": str(e)}

    def _self_destruct_tasks(self, tasks_to_destroy: List[TaskRequest]) -> None:
        """
        Remove self-destruct tasks from active task list.
        
        Args:
            tasks_to_destroy: List of tasks to remove from active tasks
        """
        task_ids_to_remove = {task.task_id for task in tasks_to_destroy}
        
        # Remove from active tasks
        original_count = len(self.active_tasks)
        self.active_tasks = [
            task for task in self.active_tasks 
            if task.task_id not in task_ids_to_remove
        ]
        
        removed_count = original_count - len(self.active_tasks)
        
        # Log self-destruction
        log_heartbeat_event(
            EventType.MODULE_CALL,
            {
                "module": "task_manager",
                "function": "_self_destruct_tasks",
                "removed_count": removed_count,
                "remaining_active_tasks": len(self.active_tasks),
                "destroyed_task_ids": list(task_ids_to_remove)
            },
            action="task_self_destruct",
            metadata={
                "self_destruct_count": removed_count,
                "remaining_tasks": len(self.active_tasks)
            }
        )
        
        print(f"💥 Self-destructed {removed_count} tasks")
        print(f"   Remaining active tasks: {len(self.active_tasks)}")

    def get_status(self) -> dict:
        """Get current status of the task manager."""
        return {
            "active_tasks_count": len(self.active_tasks),
            "completed_tasks_count": len(self.completed_tasks),
            "total_tasks_processed": len(self.active_tasks) + len(self.completed_tasks)
        }


# Global task manager instance - created when server loads
task_manager = TaskManager()