"""
API routes for file operations.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import uuid

from modules.file_ops.handler import file_ops_manager
from modules.file_ops.models import FileTaskRequest, FileWriteResponse, FileReadResponse
from modules.logging.heartbeat_logger import log_heartbeat_event, EventType

file_ops_router = APIRouter(prefix="/file_ops", tags=["file_operations"])


@file_ops_router.post("/overwrite", response_model=FileWriteResponse)
async def overwrite_file(request: FileTaskRequest):
    """
    Overwrite a file with new content.
    
    Example request:
    {
        "task": {
            "action": "overwrite_file",
            "file_path": "./output/test.txt",
            "content": "New file content here",
            "backup_existing": true
        },
        "assigned_by": "ray"
    }
    """
    request_id = str(uuid.uuid4())
    
    try:
        # Log the request
        log_heartbeat_event(
            EventType.TASK_REQUESTED,
            {
                "action": "overwrite_file",
                "file_path": request.task.get("file_path"),
                "content_length": len(request.task.get("content", "")),
                "assigned_by": request.assigned_by,
                "endpoint": "POST /file_ops/overwrite"
            },
            request_id=request_id,
            action="overwrite_file"
        )
        
        # Process the file operation
        response = file_ops_manager.handle_task(request.dict())
        
        # Log completion
        log_heartbeat_event(
            EventType.TASK_COMPLETED,
            {
                "success": response.success,
                "file_path": response.file_path,
                "file_size": response.file_size,
                "execution_time_ms": response.execution_time_ms,
                "assigned_by": request.assigned_by
            },
            request_id=request_id,
            action="overwrite_file_completed"
        )
        
        return response
        
    except Exception as e:
        # Log error
        log_heartbeat_event(
            EventType.TASK_ERROR,
            {
                "error": str(e),
                "action": "overwrite_file",
                "file_path": request.task.get("file_path"),
                "assigned_by": request.assigned_by,
                "endpoint": "POST /file_ops/overwrite"
            },
            request_id=request_id,
            action="overwrite_file_error"
        )
        
        raise HTTPException(status_code=500, detail=str(e))


@file_ops_router.post("/write", response_model=FileWriteResponse)
async def write_file(request: FileTaskRequest):
    """
    Write content to a file (will not overwrite existing files by default).
    
    Example request:
    {
        "task": {
            "action": "write_file",
            "file_path": "./output/new_file.txt",
            "content": "File content here",
            "create_directories": true
        },
        "assigned_by": "ray"
    }
    """
    request_id = str(uuid.uuid4())
    
    try:
        # Log the request
        log_heartbeat_event(
            EventType.TASK_REQUESTED,
            {
                "action": "write_file",
                "file_path": request.task.get("file_path"),
                "content_length": len(request.task.get("content", "")),
                "assigned_by": request.assigned_by,
                "endpoint": "POST /file_ops/write"
            },
            request_id=request_id,
            action="write_file"
        )
        
        # Process the file operation
        response = file_ops_manager.handle_task(request.dict())
        
        # Log completion
        log_heartbeat_event(
            EventType.TASK_COMPLETED,
            {
                "success": response.success,
                "file_path": response.file_path,
                "file_size": response.file_size,
                "execution_time_ms": response.execution_time_ms,
                "assigned_by": request.assigned_by
            },
            request_id=request_id,
            action="write_file_completed"
        )
        
        return response
        
    except Exception as e:
        # Log error
        log_heartbeat_event(
            EventType.TASK_ERROR,
            {
                "error": str(e),
                "action": "write_file",
                "file_path": request.task.get("file_path"),
                "assigned_by": request.assigned_by,
                "endpoint": "POST /file_ops/write"
            },
            request_id=request_id,
            action="write_file_error"
        )
        
        raise HTTPException(status_code=500, detail=str(e))


@file_ops_router.post("/read", response_model=FileReadResponse)
async def read_file(request: FileTaskRequest):
    """
    Read content from a file.
    
    Example request:
    {
        "task": {
            "action": "read_file",
            "file_path": "./output/test.txt",
            "max_size": 10000
        },
        "assigned_by": "ray"
    }
    """
    request_id = str(uuid.uuid4())
    
    try:
        # Log the request
        log_heartbeat_event(
            EventType.TASK_REQUESTED,
            {
                "action": "read_file",
                "file_path": request.task.get("file_path"),
                "max_size": request.task.get("max_size"),
                "assigned_by": request.assigned_by,
                "endpoint": "POST /file_ops/read"
            },
            request_id=request_id,
            action="read_file"
        )
        
        # Process the file operation
        response = file_ops_manager.handle_task(request.dict())
        
        # Log completion
        log_heartbeat_event(
            EventType.TASK_COMPLETED,
            {
                "success": response.success,
                "file_path": response.file_path,
                "file_size": response.file_size,
                "content_length": len(response.content) if response.content else 0,
                "execution_time_ms": response.execution_time_ms,
                "assigned_by": request.assigned_by
            },
            request_id=request_id,
            action="read_file_completed"
        )
        
        return response
        
    except Exception as e:
        # Log error
        log_heartbeat_event(
            EventType.TASK_ERROR,
            {
                "error": str(e),
                "action": "read_file",
                "file_path": request.task.get("file_path"),
                "assigned_by": request.assigned_by,
                "endpoint": "POST /file_ops/read"
            },
            request_id=request_id,
            action="read_file_error"
        )
        
        raise HTTPException(status_code=500, detail=str(e))


@file_ops_router.get("/status")
async def get_file_ops_status():
    """Get the current status of file operations handler."""
    return file_ops_manager.get_status()