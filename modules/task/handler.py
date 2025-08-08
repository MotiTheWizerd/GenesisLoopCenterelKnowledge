"""
Task handler for managing Ray's task assignments.

This module maintains a global task list and processes incoming task requests.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from uuid import uuid4
import asyncio
import concurrent.futures
import threading

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
                        
                        # For agent creation, add all agent fields directly to task for Ray's extension
                        if (task.task.get("action") == "agents/create" and 
                            execution_result.get("executed") and 
                            "results" in execution_result):
                            agent_results = execution_result["results"]
                            # Add all agent fields directly to the task
                            task.task.update(agent_results)
                            print(f"   🆔 Agent fields added to task: {agent_results.get('agent_id')}")
                        
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
                
                # For agent creation, add all agent fields directly to task for Ray's extension
                if (task.task.get("action") == "agents/create" and 
                    execution_result.get("executed") and 
                    "results" in execution_result):
                    agent_results = execution_result["results"]
                    # Add all agent fields directly to the task
                    task.task.update(agent_results)
                    print(f"   🆔 Agent fields added to t")
                
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
        Execute a task immediately based on its action type(s) and execution mode.
        
        Args:
            task: The task to execute
            
        Returns:
            Dict with execution results or None if execution failed
        """
        try:
            task_data = task.task
            actions = task.get_actions()
            execution_mode = task.get_execution_mode()
            
            if not actions:
                print(f"   ⚠️  No actions found in task")
                return {"error": "No actions found in task", "executed": False}
            
            if execution_mode == "single":
                # Single action - use existing logic
                print(f"⚡ Executing single action: {actions[0]}")
                return self._execute_single_action(actions[0], task_data)
            elif execution_mode == "parallel":
                # Multiple actions - execute in parallel
                print(f"⚡ Executing actions in PARALLEL: {actions}")
                return self._execute_action_parallel(actions, task_data)
            else:
                # Multiple actions - execute sequentially (default)
                print(f"⚡ Executing actions SEQUENTIALLY: {actions}")
                return self._execute_action_sequence(actions, task_data)
                
        except Exception as e:
            print(f"   ❌ Immediate execution failed: {str(e)}")
            return {"error": str(e), "executed": False}
    
    def _execute_single_action(self, action: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        print("execute single action")
        """
        Execute a single action.
        
        Args:
            action: The action to execute
            task_data: The task data containing parameters
            
        Returns:
            Dict with execution results
        """
       

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
        
        # Agent creation actions
        elif action.startswith("agents/"):
            return self._execute_agent_action(task_data)
        
        # Other actions can be added here
        else:
            print(f"   ⚠️  Unknown action for immediate execution: {action}")
            return {"error": f"Unknown action: {action}", "executed": False}
    
    def _execute_action_sequence(self, actions: List[str], task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute multiple actions sequentially, passing results between them.
        
        Args:
            actions: List of actions to execute in order
            task_data: The task data containing parameters
            
        Returns:
            Dict with aggregated execution results
        """
        sequence_results = {
            "executed": True,
            "action_sequence": actions,
            "total_actions": len(actions),
            "action_results": [],
            "final_result": None,
            "execution_summary": {
                "successful_actions": 0,
                "failed_actions": 0,
                "total_execution_time_ms": 0
            }
        }
        
        # Context that can be passed between actions
        action_context = {}
        
        for i, action in enumerate(actions):
            print(f"   🔄 Executing action {i+1}/{len(actions)}: {action}")
            
            try:
                # Create modified task data for this action
                current_task_data = task_data.copy()
                current_task_data["action"] = action  # Set single action for execution
                
                # Add context from previous actions
                if action_context:
                    current_task_data["previous_results"] = action_context
                
                # Execute the single action
                start_time = datetime.now()
                action_result = self._execute_single_action(action, current_task_data)
                end_time = datetime.now()
                
                execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
                
                # Add execution metadata
                action_result["action_index"] = i
                action_result["action_name"] = action
                action_result["execution_time_ms"] = execution_time_ms
                
                sequence_results["action_results"].append(action_result)
                sequence_results["execution_summary"]["total_execution_time_ms"] += execution_time_ms
                
                if action_result.get("executed", False):
                    sequence_results["execution_summary"]["successful_actions"] += 1
                    
                    # Update context for next action
                    if "results" in action_result:
                        action_context[action] = action_result["results"]
                    
                    print(f"      ✅ Action {action} completed successfully")
                else:
                    sequence_results["execution_summary"]["failed_actions"] += 1
                    print(f"      ❌ Action {action} failed: {action_result.get('error', 'Unknown error')}")
                    
                    # Continue with other actions even if one fails
                    action_context[action] = {"error": action_result.get("error", "Unknown error")}
                
            except Exception as e:
                error_msg = str(e)
                print(f"      ❌ Action {action} failed with exception: {error_msg}")
                
                sequence_results["action_results"].append({
                    "executed": False,
                    "action_index": i,
                    "action_name": action,
                    "error": error_msg,
                    "execution_time_ms": 0
                })
                sequence_results["execution_summary"]["failed_actions"] += 1
                action_context[action] = {"error": error_msg}
        
        # Set final result based on the last successful action or overall summary
        if sequence_results["action_results"]:
            last_result = sequence_results["action_results"][-1]
            if last_result.get("executed", False):
                sequence_results["final_result"] = last_result.get("results")
        
        # Overall success if at least one action succeeded
        sequence_results["executed"] = sequence_results["execution_summary"]["successful_actions"] > 0
        
        print(f"   🏁 Action sequence completed:")
        print(f"      Successful: {sequence_results['execution_summary']['successful_actions']}")
        print(f"      Failed: {sequence_results['execution_summary']['failed_actions']}")
        print(f"      Total time: {sequence_results['execution_summary']['total_execution_time_ms']}ms")
        
        return sequence_results
    
    def _execute_action_parallel(self, actions: List[str], task_data: Dict[str, Any]) -> Dict[str, Any]:
        print("in parallel")
        """
        Execute multiple actions in parallel using threading.
        
        Args:
            actions: List of actions to execute simultaneously
            task_data: The task data containing parameters
            
        Returns:
            Dict with aggregated parallel execution results
        """
        parallel_results = {
            "executed": True,
            "action_sequence": actions,
            "execution_mode": "parallel",
            "total_actions": len(actions),
            "action_results": [],
            "final_result": None,
            "execution_summary": {
                "successful_actions": 0,
                "failed_actions": 0,
                "total_execution_time_ms": 0,
                "max_execution_time_ms": 0,
                "min_execution_time_ms": float('inf'),
                "parallel_efficiency": 0.0
            }
        }
        
        print(f"   🔄 Starting parallel execution of {len(actions)} actions")
        
        # Record start time for overall execution
        overall_start_time = datetime.now()
        
        # Function to execute a single action with timing
        def execute_action_with_timing(action_index: int, action: str) -> Dict[str, Any]:
            print(f"   🧵 Thread {action_index}: Starting {action}")
            
            try:
                # Create modified task data for this action
                current_task_data = task_data.copy()
                current_task_data["action"] = action  # Set single action for execution
                
                # Execute the single action
                start_time = datetime.now()
                action_result = self._execute_single_action(action, current_task_data)
                end_time = datetime.now()
                
                execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
                
                # Add execution metadata
                action_result["action_index"] = action_index
                action_result["action_name"] = action
                action_result["execution_time_ms"] = execution_time_ms
                action_result["thread_id"] = threading.current_thread().ident
                
                print(f"   🧵 Thread {action_index}: {action} completed in {execution_time_ms}ms")
                return action_result
                
            except Exception as e:
                error_msg = str(e)
                print(f"   🧵 Thread {action_index}: {action} failed with exception: {error_msg}")
                
                return {
                    "executed": False,
                    "action_index": action_index,
                    "action_name": action,
                    "error": error_msg,
                    "execution_time_ms": 0,
                    "thread_id": threading.current_thread().ident
                }
        
        # Execute actions in parallel using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(actions)) as executor:
            # Submit all actions for parallel execution
            future_to_action = {
                executor.submit(execute_action_with_timing, i, action): (i, action)
                for i, action in enumerate(actions)
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_action):
                action_index, action_name = future_to_action[future]
                try:
                    action_result = future.result()
                    parallel_results["action_results"].append(action_result)
                    
                    # Update execution summary
                    execution_time = action_result.get("execution_time_ms", 0)
                    parallel_results["execution_summary"]["total_execution_time_ms"] += execution_time
                    
                    if execution_time > parallel_results["execution_summary"]["max_execution_time_ms"]:
                        parallel_results["execution_summary"]["max_execution_time_ms"] = execution_time
                    
                    if execution_time < parallel_results["execution_summary"]["min_execution_time_ms"]:
                        parallel_results["execution_summary"]["min_execution_time_ms"] = execution_time
                    
                    if action_result.get("executed", False):
                        parallel_results["execution_summary"]["successful_actions"] += 1
                    else:
                        parallel_results["execution_summary"]["failed_actions"] += 1
                        
                except Exception as e:
                    print(f"   ❌ Failed to get result for {action_name}: {str(e)}")
                    parallel_results["execution_summary"]["failed_actions"] += 1
        
        # Calculate overall execution time (wall clock time for parallel execution)
        overall_end_time = datetime.now()
        overall_execution_time_ms = int((overall_end_time - overall_start_time).total_seconds() * 1000)
        
        # Sort action results by action_index to maintain order
        parallel_results["action_results"].sort(key=lambda x: x.get("action_index", 0))
        
        # Calculate parallel efficiency (how much faster than sequential)
        total_sequential_time = parallel_results["execution_summary"]["total_execution_time_ms"]
        if overall_execution_time_ms > 0:
            parallel_results["execution_summary"]["parallel_efficiency"] = (
                total_sequential_time / overall_execution_time_ms
            )
        
        # Set the actual wall clock time as the overall execution time
        parallel_results["execution_summary"]["overall_execution_time_ms"] = overall_execution_time_ms
        
        # Set final result based on the last successful action or overall summary
        successful_results = [r for r in parallel_results["action_results"] if r.get("executed", False)]
        if successful_results:
            # Use the result from the action with the highest index (last in original order)
            parallel_results["final_result"] = max(
                successful_results, 
                key=lambda x: x.get("action_index", 0)
            ).get("results")
        
        # Overall success if at least one action succeeded
        parallel_results["executed"] = parallel_results["execution_summary"]["successful_actions"] > 0
        
        print(f"   🏁 Parallel execution completed:")
        print(f"      Successful: {parallel_results['execution_summary']['successful_actions']}")
        print(f"      Failed: {parallel_results['execution_summary']['failed_actions']}")
        print(f"      Wall clock time: {overall_execution_time_ms}ms")
        print(f"      Total thread time: {total_sequential_time}ms")
        print(f"      Parallel efficiency: {parallel_results['execution_summary']['parallel_efficiency']:.2f}x")
        
        return parallel_results
    
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
            from modules.health.models import HealthCheckRequest
            
            action = task_data.get("action")
            if action == "health_check":
                # Use the correct method name
                request = HealthCheckRequest()
                result = health_manager.get_health_status(request)
                return {
                    "executed": True, 
                    "action": action, 
                    "results": {
                        "status": result.overall_status.value,
                        "message": result.status_message,
                        "performance_score": result.performance_score,
                        "uptime_seconds": result.uptime_seconds,
                        "cpu_usage": result.system_metrics.cpu_usage_percent,
                        "memory_usage": result.system_metrics.memory_usage_percent,
                        "active_alerts": len(result.active_alerts)
                    }
                }
            elif action == "system_status":
                # Use the same method but return more detailed info
                request = HealthCheckRequest(include_trends=True, include_recommendations=True)
                result = health_manager.get_health_status(request)
                return {
                    "executed": True, 
                    "action": action, 
                    "results": {
                        "status": result.overall_status.value,
                        "detailed_message": result.status_message,
                        "performance_score": result.performance_score,
                        "system_metrics": {
                            "cpu_usage": result.system_metrics.cpu_usage_percent,
                            "memory_usage": result.system_metrics.memory_usage_percent,
                            "disk_usage": result.system_metrics.disk_usage_percent,
                            "uptime_seconds": result.uptime_seconds
                        },
                        "services_count": len(result.services),
                        "active_alerts": len(result.active_alerts),
                        "recommendations": result.recommendations
                    }
                }
            else:
                return {"executed": False, "error": f"Unknown health action: {action}"}
                
        except Exception as e:
            return {"executed": False, "error": str(e)}
    
    def _execute_reflection_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute reflection tasks immediately."""
        try:
            from modules.reflect.reflect_handler import handle_reflect
            
            question = task_data.get("question", "")
            if not question:
                return {"executed": False, "error": "No question provided for reflection"}
            
            # Prepare reflection request data
            reflection_request = {
                "question": question,
                "depth": task_data.get("depth", "surface"),
                "context": task_data.get("context", {}),
                "current_position": task_data.get("current_position")
            }
            
            # Execute reflection
            result = handle_reflect(reflection_request)
            
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

    def _execute_agent_action(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent creation/management actions immediately."""
        try:
            action = task_data.get("action", "")
            
            # Handle different agent actions
            if action == "agents/create/test":
                # Agent test is async, so we need to handle it carefully
                import asyncio
                import concurrent.futures
                
                def run_async_test():
                    return asyncio.run(self._execute_agent_test(task_data))
                
                # Run the async function in a separate thread
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_async_test)
                    return future.result()
            elif action == "agents/create":
                return self._execute_agent_create(task_data)
            elif action == "agents/list":
                return self._execute_agent_list(task_data)
            elif action == "agents/delete":
                return self._execute_agent_delete(task_data)
            elif action == "agents/stats":
                return self._execute_agent_stats(task_data)
            else:
                return {"executed": False, "error": f"Unknown agent action: {action}"}
                
        except Exception as e:
            return {"executed": False, "error": str(e)}
    
    async def _execute_agent_test(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent test action immediately."""
        try:
            from modules.agents.agent_creation_handler import handle_test_agent
            from modules.agents.agent_creation_models import AgentTestRequest
            
            # Extract required parameters
            agent_id = task_data.get("agent_id")
            test_message = task_data.get("test_message")
            user_id = task_data.get("user_id", "ray_user")
            session_id = task_data.get("session_id", "session_001")
            
            if not agent_id:
                return {"executed": False, "error": "agent_id is required for agent test"}
            
            if not test_message:
                return {"executed": False, "error": "test_message is required for agent test"}
            
            # Create test request
            test_request = AgentTestRequest(
                agent_id=agent_id,
                test_message=test_message,
                user_id=user_id,
                session_id=session_id
            )
            
            # Execute the test
            response = await handle_test_agent(test_request)
            
            # Return structured response similar to reflection format
            if response.status == "completed":
                return {
                    "executed": True,
                    "action": "agents/create/test",
                    "results": {
                        "type": "agent_test",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "status": "completed",
                        "agent_id": response.agent_id,
                        "agent_name": response.agent_name,
                        "test_message": response.test_message,
                        "agent_response": response.agent_response,
                        "processing_time_ms": response.processing_time_ms,
                        "conversation_quality": "responsive",
                        "next_steps": [
                            "Continue conversation",
                            "Try different questions",
                            "Evaluate responses"
                        ]
                    }
                }
            else:
                return {
                    "executed": False,
                    "error": response.error_message or "Agent test failed"
                }
                
        except Exception as e:
            return {"executed": False, "error": str(e)}
    
    def _execute_agent_create(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent creation action immediately."""
        try:
            from modules.agents.agent_creation_handler import handle_create_agent_sync
            from modules.agents.agent_creation_models import AgentCreationRequest
            
            # Extract required parameters
            name = task_data.get("name")
            prompt = task_data.get("prompt")
            description = task_data.get("description", "")
            assigned_by = task_data.get("assigned_by", "ray")
            
            if not name:
                return {"executed": False, "error": "name is required for agent creation"}
            
            if not prompt:
                return {"executed": False, "error": "prompt is required for agent creation"}
            
            # Create agent request
            creation_request = AgentCreationRequest(
                name=name,
                prompt=prompt,
                description=description,
                assigned_by=assigned_by
            )
            
            # Execute the creation
            response = handle_create_agent_sync(creation_request)
            
            # Return the exact format Ray expects
            if response.status == "created":
                return {
                    "executed": True,
                    "action": "agents/create",
                    "results": {
                        "agent_id": response.agent_id,
                        "status": "created",
                        "agent_name": response.agent_name,
                        "agent_description": response.agent_description,
                        "created_at": response.created_at,
                        "assigned_by": response.assigned_by,
                        "error_message": None
                    }
                }
            else:
                return {
                    "executed": False,
                    "error": response.error_message or "Agent creation failed"
                }
                
        except Exception as e:
            return {"executed": False, "error": str(e)}
    
    def _execute_agent_list(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent list action immediately."""
        try:
            from modules.agents.agent_creation_handler import handle_list_agents_sync
            
            # Execute the list
            response = handle_list_agents_sync()
            
            return {
                "executed": True,
                "action": "agents/list",
                "results": response.dict()
            }
                
        except Exception as e:
            return {"executed": False, "error": str(e)}
    
    def _execute_agent_delete(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent delete action immediately."""
        try:
            from modules.agents.agent_creation_handler import handle_delete_agent_sync
            
            # Extract required parameters
            agent_id = task_data.get("agent_id")
            
            if not agent_id:
                return {"executed": False, "error": "agent_id is required for agent deletion"}
            
            # Execute the deletion
            response = handle_delete_agent_sync(agent_id)
            
            return {
                "executed": True,
                "action": "agents/delete",
                "agent_id": agent_id,
                "results": response
            }
                
        except Exception as e:
            return {"executed": False, "error": str(e)}
    
    def _execute_agent_stats(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent stats action immediately."""
        try:
            from modules.agents.agent_creation_handler import handle_get_agent_stats_sync
            
            # Execute the stats
            response = handle_get_agent_stats_sync()
            
            return {
                "executed": True,
                "action": "agents/stats",
                "results": response
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