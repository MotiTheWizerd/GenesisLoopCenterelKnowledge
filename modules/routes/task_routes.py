"""
Task routes for handling Ray's task assignments.

This module provides the API endpoint for Ray to send task commands.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from modules.task.models import TaskRequestFromRay, TaskRequest, BatchTaskResponse
from modules.task.handler import task_manager
from modules.logging.heartbeat_logger import log_heartbeat_event, EventType, generate_request_id

task_router = APIRouter(prefix="/task", tags=["task"])


@task_router.post("")
async def create_batch_tasks(request: TaskRequestFromRay):
    """
    Create batch tasks from Ray's command.
    
    Ray sends:
    {
        "task": [
            {"type": "reflect", "question": "What is consciousness?"},
            {"type": "evolve", "area": "self-awareness"}
        ],
        "assigned_by": "ray"
    }
    
    Server creates individual task objects and adds to global list.
    """
    request_id = generate_request_id()
    
    try:
        # Log incoming batch task request
        log_heartbeat_event(
            EventType.TASK_REQUESTED,
            {
                "task_count": len(request.task),
                "task_data": request.task,
                "assigned_by": request.assigned_by,
                "endpoint": "POST /task"
            },
            request_id=request_id,
            action="create_batch_tasks",
            metadata={"route": "batch_task_creation", "batch_size": len(request.task)}
        )
        
        # Create batch tasks using the global task manager
        batch_response = task_manager.create_batch_tasks(request)
        
        # Log successful batch creation
        log_heartbeat_event(
            EventType.TASK_CREATED,
            {
                "batch_id": batch_response.batch_id,
                "total_tasks": batch_response.total_tasks,
                "created_count": len(batch_response.created_tasks),
                "failed_count": len(batch_response.failed_tasks),
                "assigned_by": batch_response.assigned_by,
                "status": batch_response.status
            },
            request_id=request_id,
            action="create_batch_tasks",
            metadata={"batch_id": batch_response.batch_id, "batch_status": batch_response.status}
        )
        
        # Prepare response
        response = {
            "status": "batch_processed",
            "batch_id": batch_response.batch_id,
            "total_tasks": batch_response.total_tasks,
            "created_count": len(batch_response.created_tasks),
            "failed_count": len(batch_response.failed_tasks),
            "created_tasks": [
                {
                    "task_id": task.task_id,
                    "task": task.task,
                    "timestamp": task.timestamp
                } for task in batch_response.created_tasks
            ],
            "failed_tasks": batch_response.failed_tasks,
            "assigned_by": batch_response.assigned_by,
            "timestamp": batch_response.timestamp,
            "message": f"Batch {batch_response.batch_id} processed: {len(batch_response.created_tasks)} created, {len(batch_response.failed_tasks)} failed"
        }
        
        # Log outgoing response
        log_heartbeat_event(
            EventType.OUTGOING_RESPONSE,
            response,
            request_id=request_id,
            action="create_batch_tasks",
            metadata={"batch_id": batch_response.batch_id}
        )
        
        return response
        
    except Exception as e:
        # Log batch creation error
        log_heartbeat_event(
            EventType.TASK_ERROR,
            {
                "error": str(e),
                "task_count": len(request.task) if hasattr(request, 'task') else 0,
                "assigned_by": request.assigned_by if hasattr(request, 'assigned_by') else "unknown"
            },
            request_id=request_id,
            action="create_batch_tasks",
            metadata={"error_type": "batch_creation_failed"}
        )
        
        print(f"❌ Error creating batch tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create batch tasks: {str(e)}")


@task_router.get("/list")
async def get_active_tasks():
    """
    Get all active tasks from the global task list.
    """
    try:
        active_tasks = task_manager.get_all_active_tasks()
        
        return {
            "status": "success",
            "active_tasks_count": len(active_tasks),
            "active_tasks": [task.dict() for task in active_tasks],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error getting task list: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get task list: {str(e)}")


@task_router.get("/{task_id}")
async def get_task(task_id: str):
    """
    Get a specific task by ID from the global task list.
    """
    try:
        task = task_manager.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        return {
            "status": "success",
            "task": task.dict(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get task: {str(e)}")


@task_router.get("/status")
async def get_task_manager_status():
    """
    Get current status of the task manager and global task lists.
    """
    try:
        status = task_manager.get_status()
        
        return {
            "status": "operational",
            "task_manager": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error getting task manager status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")