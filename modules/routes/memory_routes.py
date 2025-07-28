"""
Memory routes for Ray to access her reflection history.

This module provides endpoints for Ray to retrieve and analyze her past reflections.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime, timezone
import json
from pathlib import Path

from modules.logging.heartbeat_logger import log_heartbeat_event, EventType, generate_request_id

memory_router = APIRouter(prefix="/memory", tags=["memory"])


class ReflectionMemory(BaseModel):
    """Structure for a single reflection memory."""
    task_id: str
    reflection: str
    timestamp: str
    is_final: bool


class TaskReflectionGroup(BaseModel):
    """Group of reflections for a specific task."""
    task_id: str
    task_data: Dict
    reflections: List[ReflectionMemory]
    reflection_count: int
    first_reflection: str
    last_reflection: str
    is_complete: bool


class MemoryResponse(BaseModel):
    """Response structure for memory retrieval."""
    status: str
    start_date: str
    end_date: str
    total_tasks: int
    total_reflections: int
    task_groups: List[TaskReflectionGroup]
    timestamp: str


def load_reflection_logs() -> List[Dict]:
    """Load reflection logs from the heartbeat detailed log file."""
    log_file = Path("logs/heartbeat_detailed.jsonl")
    
    if not log_file.exists():
        return []
    
    logs = []
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        log_entry = json.loads(line)
                        logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        print(f"❌ Error loading reflection logs: {e}")
    
    return logs


def filter_reflection_logs(logs: List[Dict], start_date: str, end_date: str) -> List[Dict]:
    """Filter logs for reflection updates within date range."""
    reflection_logs = []
    
    try:
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    
    for log in logs:
        # Look for task_updated events with reflection updates
        if (log.get('event_type') == 'task_updated' and 
            log.get('action') == 'update_task_reflection'):
            
            try:
                log_time = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
                if start_dt <= log_time <= end_dt:
                    reflection_logs.append(log)
            except (ValueError, KeyError):
                continue
    
    return reflection_logs


def group_reflections_by_task(reflection_logs: List[Dict]) -> Dict[str, TaskReflectionGroup]:
    """Group reflections by task_id."""
    task_groups = {}
    
    for log in reflection_logs:
        data = log.get('data', {})
        task_id = data.get('task_id')
        
        if not task_id:
            continue
        
        reflection = data.get('reflection', '')
        is_final = data.get('is_final', False)
        timestamp = log.get('timestamp', '')
        task_data = data.get('task_data', {})
        
        if task_id not in task_groups:
            task_groups[task_id] = TaskReflectionGroup(
                task_id=task_id,
                task_data=task_data,
                reflections=[],
                reflection_count=0,
                first_reflection='',
                last_reflection='',
                is_complete=False
            )
        
        # Add reflection to the group
        reflection_memory = ReflectionMemory(
            task_id=task_id,
            reflection=reflection,
            timestamp=timestamp,
            is_final=is_final
        )
        
        task_groups[task_id].reflections.append(reflection_memory)
        task_groups[task_id].reflection_count = len(task_groups[task_id].reflections)
        
        # Update first and last reflections
        if not task_groups[task_id].first_reflection:
            task_groups[task_id].first_reflection = reflection
        task_groups[task_id].last_reflection = reflection
        
        # Update completion status
        if is_final:
            task_groups[task_id].is_complete = True
    
    return task_groups


class RememberRequest(BaseModel):
    """Request structure for Ray to remember past reflections."""
    action: str = Field(..., description="Action type - should be 'remember_past_reflections'")
    from_: str = Field(..., alias="from", description="Start date in ISO format")
    to: str = Field(..., description="End date in ISO format")


@memory_router.post("/get_reflections_logs")
async def get_reflection_logs(request: RememberRequest):
    """
    Get Ray's reflection logs grouped by task ID within a date range.
    
    Ray sends:
    {
        "action": "remember_past_reflections",
        "from": "2025-07-27T00:00:00Z",
        "to": "2025-07-27T23:59:59Z"
    }
    
    Returns:
        MemoryResponse: Reflections grouped by task_id
    """
    print(f"🎯 DEBUGGING - Memory route reached! Request: {request}")
    print(f"🎯 DEBUGGING - Request action: {request.action}")
    print(f"🎯 DEBUGGING - Request from: {request.from_}")
    print(f"🎯 DEBUGGING - Request to: {request.to}")
    
    request_id = generate_request_id()
    
    try:
        # Extract dates from request
        start_date = request.from_
        end_date = request.to
        
        # Log incoming memory request
        log_heartbeat_event(
            EventType.INCOMING_POST,
            {
                "action": request.action,
                "start_date": start_date,
                "end_date": end_date,
                "endpoint": "POST /memory/get_reflections_logs"
            },
            request_id=request_id,
            action="get_reflection_logs",
            metadata={"route": "memory_retrieval", "date_range": f"{start_date} to {end_date}"}
        )
        
        # Load all logs
        all_logs = load_reflection_logs()
        
        # Filter for reflection logs in date range
        reflection_logs = filter_reflection_logs(all_logs, start_date, end_date)
        
        # Group reflections by task_id
        task_groups = group_reflections_by_task(reflection_logs)
        
        # Prepare response
        response = MemoryResponse(
            status="success",
            start_date=start_date,
            end_date=end_date,
            total_tasks=len(task_groups),
            total_reflections=sum(group.reflection_count for group in task_groups.values()),
            task_groups=list(task_groups.values()),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # Log successful memory retrieval
        log_heartbeat_event(
            EventType.OUTGOING_RESPONSE,
            {
                "status": "success",
                "total_tasks": response.total_tasks,
                "total_reflections": response.total_reflections,
                "date_range": f"{start_date} to {end_date}"
            },
            request_id=request_id,
            action="get_reflection_logs",
            metadata={"memory_retrieval": "success"}
        )
        
        print(f"🧠 Memory retrieval completed:")
        print(f"   Date range: {start_date} to {end_date}")
        print(f"   Tasks found: {response.total_tasks}")
        print(f"   Total reflections: {response.total_reflections}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        # Log memory retrieval error
        log_heartbeat_event(
            EventType.ERROR,
            {
                "error": str(e),
                "start_date": start_date,
                "end_date": end_date
            },
            request_id=request_id,
            action="get_reflection_logs",
            metadata={"error_type": "memory_retrieval_failed"}
        )
        
        print(f"❌ Error retrieving memory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve memory: {str(e)}")


@memory_router.get("/status")
async def get_memory_status():
    """Get memory system status and available log information."""
    print(f"🎯 DEBUGGING - Memory status route reached!")
    
    try:
        log_file = Path("logs/heartbeat_detailed.jsonl")
        
        if not log_file.exists():
            return {
                "status": "no_logs",
                "message": "No log file found",
                "log_file_exists": False,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Get basic file info
        file_size = log_file.stat().st_size
        
        # Count total logs quickly
        total_logs = 0
        reflection_logs = 0
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        total_logs += 1
                        if 'task_updated' in line and 'update_task_reflection' in line:
                            reflection_logs += 1
        except Exception:
            pass
        
        response = {
            "status": "operational",
            "log_file_exists": True,
            "log_file_size_bytes": file_size,
            "total_log_entries": total_logs,
            "reflection_log_entries": reflection_logs,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        print(f"🎯 DEBUGGING - Memory status response: {response}")
        return response
        
    except Exception as e:
        print(f"❌ Error getting memory status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get memory status: {str(e)}")


