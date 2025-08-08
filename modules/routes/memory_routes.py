"""
Memory routes for Ray to access her reflection history.

This module provides endpoints for Ray to retrieve and analyze her past reflections.
"""

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, List, Optional
from datetime import datetime, timezone
import json
from pathlib import Path

from modules.logging.heartbeat_logger import log_heartbeat_event, EventType, generate_request_id
from utils.timestamp_utils import add_ray_timestamp_to_response, get_ray_time_context

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


class EmbedRequest(BaseModel):
    """Request structure for memory embedding."""
    text: str = Field(..., description="The text to embed in memory")
    metadata: Optional[Dict] = Field(default=None, description="Optional metadata to store with the embedding")
    timestamp: Optional[str] = Field(default=None, description="Optional timestamp for the memory")
    tags: Optional[List[str]] = Field(default=None, description="Optional tags for categorizing the memory")


class StoreRequest(BaseModel):
    """Request structure for storing memories."""
    memories: List[Dict] = Field(..., description="List of memories to store")
    source: Optional[str] = Field(default="system", description="Source of the memories")
    timestamp: Optional[str] = Field(default=None, description="Optional timestamp for all memories")
    metadata: Optional[Dict] = Field(default=None, description="Optional metadata for all memories")


class RememberRequest(BaseModel):
    """Request structure for Ray to remember past reflections."""
    action: str = Field(..., description="Action type - should be 'remember_past_reflections'")
    from_: str = Field(..., alias="from", description="Start date in ISO format")
    to: str = Field(..., description="End date in ISO format")


@memory_router.post("/store")
async def store_memory(raw_request: Request):
    """
    Store multiple memories in Ray's memory system.
    
    This endpoint handles storing structured memories in batch,
    making them available for future analysis and recall.
    """
    request_id = generate_request_id()
    
    try:
        # Get raw request body for debugging
        body = await raw_request.body()
        raw_data = json.loads(body.decode()) if body else {}
        
        print(f"🎯 DEBUGGING - Memory store raw request: {raw_data}")
        
        # Validate the request manually to provide better error messages
        if not isinstance(raw_data, dict):
            error_details = {
                "error_type": "invalid_request_format",
                "received_type": type(raw_data).__name__,
                "expected": "dictionary/object",
                "raw_data": str(raw_data)[:500]  # Limit size for logging
            }
            
            log_heartbeat_event(
                EventType.ERROR,
                error_details,
                request_id=request_id,
                action="memory_store_validation_error",
                metadata={"error_type": "invalid_format"}
            )
            
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Request must be a JSON object",
                    "received_type": type(raw_data).__name__,
                    "request_id": request_id
                }
            )
        
        # Check for required 'memories' field
        if 'memories' not in raw_data:
            error_details = {
                "error_type": "missing_required_field",
                "missing_field": "memories",
                "received_fields": list(raw_data.keys()),
                "raw_data": raw_data
            }
            
            log_heartbeat_event(
                EventType.ERROR,
                error_details,
                request_id=request_id,
                action="memory_store_validation_error",
                metadata={"error_type": "missing_memories_field"}
            )
            
            print(f"🚨 MEMORY STORE ERROR - Missing 'memories' field")
            print(f"   Request ID: {request_id}")
            print(f"   Received fields: {list(raw_data.keys())}")
            print(f"   Raw data: {raw_data}")
            
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Missing required field 'memories'",
                    "received_fields": list(raw_data.keys()),
                    "expected_format": {
                        "memories": [{"content": "example memory"}],
                        "source": "optional_source",
                        "timestamp": "optional_timestamp"
                    },
                    "request_id": request_id
                }
            )
        
        # Validate memories field
        memories = raw_data.get('memories')
        if not isinstance(memories, list):
            error_details = {
                "error_type": "invalid_memories_type",
                "memories_type": type(memories).__name__,
                "expected": "list",
                "memories_value": str(memories)[:200]
            }
            
            log_heartbeat_event(
                EventType.ERROR,
                error_details,
                request_id=request_id,
                action="memory_store_validation_error",
                metadata={"error_type": "invalid_memories_type"}
            )
            
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Field 'memories' must be a list",
                    "received_type": type(memories).__name__,
                    "request_id": request_id
                }
            )
        
        # Now create the validated request object
        try:
            request = StoreRequest(**raw_data)
        except ValidationError as e:
            error_details = {
                "error_type": "pydantic_validation_error",
                "validation_errors": e.errors(),
                "raw_data": raw_data
            }
            
            log_heartbeat_event(
                EventType.ERROR,
                error_details,
                request_id=request_id,
                action="memory_store_validation_error",
                metadata={"error_type": "pydantic_validation"}
            )
            
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Request validation failed",
                    "validation_errors": e.errors(),
                    "request_id": request_id
                }
            )
        
        print(f"🎯 DEBUGGING - Memory store validated request: {request}")
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        error_details = {
            "error_type": "request_parsing_error",
            "error_message": str(e),
            "error_type_name": type(e).__name__
        }
        
        log_heartbeat_event(
            EventType.ERROR,
            error_details,
            request_id=request_id,
            action="memory_store_parsing_error",
            metadata={"error_type": "request_parsing"}
        )
        
        print(f"🚨 MEMORY STORE PARSING ERROR: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Failed to parse request",
                "error_message": str(e),
                "request_id": request_id
            }
        )
    
    # Continue with the original logic
    try:
        # Log incoming store request
        log_heartbeat_event(
            EventType.INCOMING_POST,
            {
                "memory_count": len(request.memories),
                "source": request.source,
                "endpoint": "POST /memory/store"
            },
            request_id=request_id,
            action="store_memory",
            metadata={"route": "memory_store"}
        )
        
        # Default timestamp for all memories if not individually specified
        batch_timestamp = request.timestamp or datetime.now(timezone.utc).isoformat()
        stored_memories = []
        
        # Write to memory storage file
        log_file = Path("logs/memory_storage.jsonl")
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                for memory in request.memories:
                    memory_id = generate_request_id()
                    memory_entry = {
                        "id": memory_id,
                        "timestamp": memory.get('timestamp', batch_timestamp),
                        "source": request.source,
                        **memory,  # Include all provided memory fields
                        "metadata": {**(request.metadata or {}), **(memory.get('metadata', {}))}  # Merge metadata
                    }
                    f.write(json.dumps(memory_entry) + "\n")
                    stored_memories.append({
                        "id": memory_id,
                        "timestamp": memory_entry["timestamp"]
                    })
                    
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to store memories: {str(e)}")
        
        # Prepare response
        response = {
            "status": "success",
            "batch_id": request_id,
            "timestamp": batch_timestamp,
            "memories_stored": len(stored_memories),
            "stored_memory_ids": stored_memories,
            "source": request.source
        }
        
        # Log successful storage
        log_heartbeat_event(
            EventType.OUTGOING_RESPONSE,
            {
                "status": "success",
                "batch_id": request_id,
                "memories_stored": len(stored_memories)
            },
            request_id=request_id,
            action="store_memory",
            metadata={"memories_stored": True}
        )
        
        # Add comprehensive timestamp information for Ray
        response = add_ray_timestamp_to_response(response)
        
        return response
        
    except Exception as e:
        # Log storage error
        log_heartbeat_event(
            EventType.ERROR,
            {
                "error": str(e),
                "memory_count": len(request.memories)
            },
            request_id=request_id,
            action="store_memory",
            metadata={"error_type": "memory_store_failed"}
        )
        
        print(f"❌ Error storing memories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to store memories: {str(e)}")


@memory_router.post("/embed")
async def embed_memory(request: EmbedRequest):
    """
    Embed text into Ray's memory with optional metadata.
    
    The endpoint stores text with associated metadata in Ray's memory system,
    making it available for future recall and analysis.
    """
    print(f"🎯 DEBUGGING - Memory embed route reached! Request: {request}")
    request_id = generate_request_id()
    
    try:
        # Log incoming embed request
        log_heartbeat_event(
            EventType.INCOMING_POST,
            {
                "text_length": len(request.text),
                "has_metadata": request.metadata is not None,
                "has_tags": request.tags is not None,
                "endpoint": "POST /memory/embed"
            },
            request_id=request_id,
            action="embed_memory",
            metadata={"route": "memory_embed"}
        )
        
        # Prepare memory entry
        timestamp = request.timestamp or datetime.now(timezone.utc).isoformat()
        memory_entry = {
            "text": request.text,
            "metadata": request.metadata or {},
            "timestamp": timestamp,
            "tags": request.tags or [],
            "request_id": request_id
        }
        
        # Write to memory log file
        log_file = Path("logs/memory_entries.jsonl")
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(memory_entry) + "\n")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to write memory: {str(e)}")
        
        # Prepare response
        response = {
            "status": "success",
            "memory_id": request_id,
            "timestamp": timestamp,
            "text_length": len(request.text),
            "has_metadata": request.metadata is not None,
            "has_tags": request.tags is not None
        }
        
        # Log successful embedding
        log_heartbeat_event(
            EventType.OUTGOING_RESPONSE,
            {
                "status": "success",
                "memory_id": request_id,
                "text_length": len(request.text)
            },
            request_id=request_id,
            action="embed_memory",
            metadata={"memory_stored": True}
        )
        
        # Add comprehensive timestamp information for Ray
        response = add_ray_timestamp_to_response(response)
        
        return response
        
    except Exception as e:
        # Log embedding error
        log_heartbeat_event(
            EventType.ERROR,
            {
                "error": str(e),
                "text_length": len(request.text)
            },
            request_id=request_id,
            action="embed_memory",
            metadata={"error_type": "memory_embed_failed"}
        )
        
        print(f"❌ Error embedding memory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to embed memory: {str(e)}")


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
        
        # Add comprehensive timestamp information for Ray
        response_dict = response.dict()
        response_dict = add_ray_timestamp_to_response(response_dict)
        
        return response_dict
        
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
        
        # Add comprehensive timestamp information for Ray
        response = add_ray_timestamp_to_response(response)
        
        return response
        
    except Exception as e:
        print(f"❌ Error getting memory status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get memory status: {str(e)}")


@memory_router.get("/debug/recent-errors")
async def get_recent_memory_errors():
    """Debug endpoint to show recent memory-related errors"""
    try:
        log_file = Path("logs/heartbeat_detailed.jsonl")
        
        if not log_file.exists():
            return {"errors": [], "message": "No log file found"}
        
        recent_errors = []
        
        # Read last 100 lines to find recent errors
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            recent_lines = lines[-100:] if len(lines) > 100 else lines
            
            for line in recent_lines:
                try:
                    log_entry = json.loads(line.strip())
                    
                    # Look for memory-related errors
                    if (log_entry.get('event_type') == 'error' and 
                        ('memory' in str(log_entry).lower() or 
                         'validation_error' in str(log_entry).lower())):
                        recent_errors.append(log_entry)
                        
                except json.JSONDecodeError:
                    continue
        
        return {
            "recent_memory_errors": recent_errors[-10:],  # Last 10 errors
            "total_errors_found": len(recent_errors),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error getting recent memory errors: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent errors: {str(e)}")


