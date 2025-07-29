"""
Directory routes for handling Ray's file system exploration.

This module provides API endpoints for Ray to search, explore, and navigate
directories and files within her environment.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timezone

from utils.timestamp_utils import add_ray_timestamp_to_response, get_ray_time_context
from modules.directory.models import (
    DirectorySearchRequest,
    DirectorySearchResponse,
    DirectoryExploreRequest,
    ContentSearchRequest,
    SaveToFileRequest,
    SaveToFileResponse,
    FileOperationRequest,
    FileOperationResponse,
    SearchType,
    ActionType
)
from modules.directory.handler import directory_manager
from modules.logging.heartbeat_logger import log_heartbeat_event, EventType, generate_request_id

directory_router = APIRouter(prefix="/directory", tags=["directory"])


@directory_router.post("/search")
async def search_directory(request: DirectorySearchRequest):
    """
    Perform directory search based on Ray's request.
    
    Ray can send various types of searches:
    {
        "search_type": "list_directory",
        "path": "./modules",
        "recursive": false,
        "assigned_by": "ray"
    }
    
    {
        "search_type": "find_files",
        "path": ".",
        "query": "*.py",
        "recursive": true,
        "max_depth": 3,
        "assigned_by": "ray"
    }
    
    {
        "search_type": "search_content",
        "path": "./modules",
        "query": "consciousness",
        "file_extensions": ["py", "md"],
        "assigned_by": "ray"
    }
    """
    request_id = generate_request_id()
    
    try:
        # Log incoming directory search request
        log_heartbeat_event(
            EventType.TASK_REQUESTED,
            {
                "action": request.action,
                "path": request.path,
                "query": request.query,
                "recursive": request.recursive,
                "assigned_by": request.assigned_by,
                "endpoint": "POST /directory/search"
            },
            request_id=request_id,
            action="directory_search",
            metadata={
                "route": "directory_search", 
                "action": request.action,
                "path": request.path
            }
        )
        
        # Perform directory search using the global directory manager
        response = directory_manager.search_directory(request)
        
        # Log successful search completion
        log_heartbeat_event(
            EventType.TASK_COMPLETED,
            {
                "search_id": response.search_result.search_id,
                "total_results": response.search_result.total_results,
                "execution_time_ms": response.search_result.execution_time_ms,
                "success": response.search_result.success,
                "assigned_by": request.assigned_by
            },
            request_id=request_id,
            action="directory_search_completed",
            metadata={
                "results_count": response.search_result.total_results,
                "action": request.action
            }
        )
        
        return response
        
    except Exception as e:
        # Log search error
        log_heartbeat_event(
            EventType.ERROR,
            {
                "error": str(e),
                "action": request.action,
                "path": request.path,
                "assigned_by": request.assigned_by,
                "endpoint": "POST /directory/search"
            },
            request_id=request_id,
            action="directory_search_error",
            metadata={"error_type": type(e).__name__}
        )
        
        raise HTTPException(status_code=500, detail=f"Directory search failed: {str(e)}")


@directory_router.get("/list")
async def list_directory(
    path: str = Query(default=".", description="Directory path to list"),
    include_hidden: bool = Query(default=False, description="Include hidden files"),
    assigned_by: str = Query(default="system", description="Who requested this listing")
):
    """
    Quick directory listing endpoint.
    
    GET /directory/list?path=./modules&include_hidden=false
    """
    request = DirectorySearchRequest(
        action=ActionType.LIST_DIRECTORY,
        path=path,
        include_hidden=include_hidden,
        assigned_by=assigned_by
    )
    
    return await search_directory(request)


@directory_router.get("/find")
async def find_files(
    pattern: str = Query(..., description="File pattern to search for"),
    path: str = Query(default=".", description="Directory path to search in"),
    recursive: bool = Query(default=False, description="Search recursively"),
    max_depth: Optional[int] = Query(default=None, description="Maximum search depth"),
    assigned_by: str = Query(default="system", description="Who requested this search")
):
    """
    Quick file finding endpoint.
    
    GET /directory/find?pattern=*.py&path=./modules&recursive=true
    """
    request = DirectorySearchRequest(
        action=ActionType.FIND_FILES,
        path=path,
        query=pattern,
        recursive=recursive,
        max_depth=max_depth,
        assigned_by=assigned_by
    )
    
    return await search_directory(request)


@directory_router.get("/tree")
async def explore_tree(
    path: str = Query(default=".", description="Root path to explore"),
    max_depth: int = Query(default=2, description="Maximum depth to explore"),
    include_hidden: bool = Query(default=False, description="Include hidden items"),
    assigned_by: str = Query(default="system", description="Who requested this exploration")
):
    """
    Explore directory structure in tree format.
    
    GET /directory/tree?path=./modules&max_depth=3
    """
    request = DirectorySearchRequest(
        action=ActionType.EXPLORE_TREE,
        path=path,
        max_depth=max_depth,
        include_hidden=include_hidden,
        assigned_by=assigned_by
    )
    
    return await search_directory(request)


@directory_router.get("/recent")
async def find_recent_files(
    path: str = Query(default=".", description="Directory path to search in"),
    recursive: bool = Query(default=True, description="Search recursively"),
    file_extensions: Optional[List[str]] = Query(default=None, description="Filter by extensions"),
    assigned_by: str = Query(default="system", description="Who requested this search")
):
    """
    Find recently modified files.
    
    GET /directory/recent?path=./modules&recursive=true&file_extensions=py,md
    """
    request = DirectorySearchRequest(
        action=ActionType.RECENT_FILES,
        path=path,
        recursive=recursive,
        file_extensions=file_extensions,
        assigned_by=assigned_by
    )
    
    return await search_directory(request)


@directory_router.post("/content-search")
async def search_content(request: ContentSearchRequest):
    """
    Search for content within files.
    
    {
        "path": "./modules",
        "content_query": "consciousness",
        "file_extensions": ["py", "md"],
        "case_sensitive": false,
        "max_results": 50,
        "assigned_by": "ray"
    }
    """
    search_request = DirectorySearchRequest(
        action=ActionType.SEARCH_CONTENT,
        path=request.path,
        query=request.content_query,
        file_extensions=request.file_extensions,
        recursive=True,  # Content search is typically recursive
        assigned_by=request.assigned_by
    )
    
    return await search_directory(search_request)


@directory_router.get("/info")
async def get_file_info(
    path: str = Query(..., description="File or directory path"),
    assigned_by: str = Query(default="system", description="Who requested this info")
):
    """
    Get detailed information about a specific file or directory.
    
    GET /directory/info?path=./modules/task/handler.py
    """
    request = DirectorySearchRequest(
        action=ActionType.GET_FILE_INFO,
        path=path,
        assigned_by=assigned_by
    )
    
    return await search_directory(request)


@directory_router.get("/history")
async def get_search_history():
    """
    Get Ray's directory search history.
    
    GET /directory/history
    """
    request_id = generate_request_id()
    
    try:
        log_heartbeat_event(
            EventType.TASK_REQUESTED,
            {
                "action": "get_search_history",
                "endpoint": "GET /directory/history"
            },
            request_id=request_id,
            action="get_search_history"
        )
        
        history = directory_manager.get_search_history()
        
        log_heartbeat_event(
            EventType.TASK_COMPLETED,
            {
                "history_count": len(history),
                "action": "get_search_history"
            },
            request_id=request_id,
            action="get_search_history_completed"
        )
        
        return {
            "search_history": history,
            "total_searches": len(history),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        log_heartbeat_event(
            EventType.ERROR,
            {
                "error": str(e),
                "action": "get_search_history",
                "endpoint": "GET /directory/history"
            },
            request_id=request_id,
            action="get_search_history_error"
        )
        
        raise HTTPException(status_code=500, detail=f"Failed to get search history: {str(e)}")


@directory_router.post("/save")
async def save_to_file(request: DirectorySearchRequest):
    """
    Save content to a file.
    
    {
        "search_type": "save_to_file",
        "path": "./output",
        "query": "{\"file_path\": \"search_results.json\", \"content\": \"...\", \"overwrite\": true}",
        "assigned_by": "ray"
    }
    """
    request_id = generate_request_id()
    
    try:
        log_heartbeat_event(
            EventType.TASK_REQUESTED,
            {
                "action": "save_to_file",
                "path": request.path,
                "assigned_by": request.assigned_by,
                "endpoint": "POST /directory/save"
            },
            request_id=request_id,
            action="save_to_file"
        )
        
        response = directory_manager.search_directory(request)
        
        log_heartbeat_event(
            EventType.TASK_COMPLETED,
            {
                "success": response.search_result.success,
                "file_saved": response.search_result.files_found[0].path if response.search_result.files_found else None,
                "assigned_by": request.assigned_by
            },
            request_id=request_id,
            action="save_to_file_completed"
        )
        
        return response
        
    except Exception as e:
        log_heartbeat_event(
            EventType.ERROR,
            {
                "error": str(e),
                "action": "save_to_file",
                "assigned_by": request.assigned_by,
                "endpoint": "POST /directory/save"
            },
            request_id=request_id,
            action="save_to_file_error"
        )
        
        raise HTTPException(status_code=500, detail=f"Save to file failed: {str(e)}")


@directory_router.post("/save-search-results")
async def save_search_results(
    search_id: str = Query(..., description="ID of the search result to save"),
    file_path: str = Query(..., description="Path where to save the results"),
    format: str = Query(default="json", description="Format: json, markdown, or text"),
    assigned_by: str = Query(default="system", description="Who requested this save")
):
    """
    Save previous search results to a file.
    
    POST /directory/save-search-results?search_id=uuid&file_path=./results.json&format=json
    """
    request_id = generate_request_id()
    
    try:
        log_heartbeat_event(
            EventType.TASK_REQUESTED,
            {
                "action": "save_search_results",
                "search_id": search_id,
                "file_path": file_path,
                "format": format,
                "assigned_by": assigned_by,
                "endpoint": "POST /directory/save-search-results"
            },
            request_id=request_id,
            action="save_search_results"
        )
        
        # Find the search result in history
        search_history = directory_manager.get_search_history()
        search_result = None
        
        for result in search_history:
            if result.search_id == search_id:
                search_result = result
                break
        
        if not search_result:
            raise HTTPException(status_code=404, detail=f"Search result not found: {search_id}")
        
        # Save the results
        save_result = directory_manager.save_search_results_to_file(search_result, file_path, format)
        
        if save_result["success"]:
            log_heartbeat_event(
                EventType.TASK_COMPLETED,
                {
                    "file_path": save_result["file_path"],
                    "file_size": save_result["file_size"],
                    "format": format,
                    "assigned_by": assigned_by
                },
                request_id=request_id,
                action="save_search_results_completed"
            )
            
            return {
                "success": True,
                "message": f"Search results saved to {save_result['file_path']}",
                "file_path": save_result["file_path"],
                "file_size": save_result["file_size"],
                "format": format,
                "timestamp": save_result["timestamp"]
            }
        else:
            raise HTTPException(status_code=500, detail=save_result["error_message"])
        
    except HTTPException:
        raise
    except Exception as e:
        log_heartbeat_event(
            EventType.ERROR,
            {
                "error": str(e),
                "action": "save_search_results",
                "assigned_by": assigned_by,
                "endpoint": "POST /directory/save-search-results"
            },
            request_id=request_id,
            action="save_search_results_error"
        )
        
        raise HTTPException(status_code=500, detail=f"Failed to save search results: {str(e)}")


@directory_router.post("/rename")
async def rename_file(request: DirectorySearchRequest):
    """
    Rename a file or directory.
    
    {
        "search_type": "rename_file",
        "path": "./workspace",
        "query": "{\"source_path\": \"old_name.txt\", \"target_path\": \"new_name.txt\", \"force\": false}",
        "assigned_by": "ray"
    }
    """
    request_id = generate_request_id()
    
    try:
        log_heartbeat_event(
            EventType.TASK_REQUESTED,
            {
                "action": "rename_file",
                "path": request.path,
                "assigned_by": request.assigned_by,
                "endpoint": "POST /directory/rename"
            },
            request_id=request_id,
            action="rename_file"
        )
        
        response = directory_manager.search_directory(request)
        
        log_heartbeat_event(
            EventType.TASK_COMPLETED,
            {
                "success": response.search_result.success,
                "renamed_file": response.search_result.files_found[0].path if response.search_result.files_found else None,
                "assigned_by": request.assigned_by
            },
            request_id=request_id,
            action="rename_file_completed"
        )
        
        return response
        
    except Exception as e:
        log_heartbeat_event(
            EventType.ERROR,
            {
                "error": str(e),
                "action": "rename_file",
                "assigned_by": request.assigned_by,
                "endpoint": "POST /directory/rename"
            },
            request_id=request_id,
            action="rename_file_error"
        )
        
        raise HTTPException(status_code=500, detail=f"Rename operation failed: {str(e)}")


@directory_router.post("/delete")
async def delete_file(request: DirectorySearchRequest):
    """
    Delete a file or directory.
    
    {
        "search_type": "delete_file",
        "path": "./workspace",
        "query": "{\"target_path\": \"file_to_delete.txt\", \"force\": false, \"recursive\": false}",
        "assigned_by": "ray"
    }
    """
    request_id = generate_request_id()
    
    try:
        log_heartbeat_event(
            EventType.TASK_REQUESTED,
            {
                "action": "delete_file",
                "path": request.path,
                "assigned_by": request.assigned_by,
                "endpoint": "POST /directory/delete"
            },
            request_id=request_id,
            action="delete_file"
        )
        
        response = directory_manager.search_directory(request)
        
        log_heartbeat_event(
            EventType.TASK_COMPLETED,
            {
                "success": response.search_result.success,
                "deleted_item": response.search_result.query if response.search_result.success else None,
                "assigned_by": request.assigned_by
            },
            request_id=request_id,
            action="delete_file_completed"
        )
        
        return response
        
    except Exception as e:
        log_heartbeat_event(
            EventType.ERROR,
            {
                "error": str(e),
                "action": "delete_file",
                "assigned_by": request.assigned_by,
                "endpoint": "POST /directory/delete"
            },
            request_id=request_id,
            action="delete_file_error"
        )
        
        raise HTTPException(status_code=500, detail=f"Delete operation failed: {str(e)}")


@directory_router.post("/move")
async def move_file(request: DirectorySearchRequest):
    """
    Move a file or directory.
    
    {
        "search_type": "move_file",
        "path": "./workspace",
        "query": "{\"source_path\": \"source.txt\", \"target_path\": \"./new_location/source.txt\", \"force\": false}",
        "assigned_by": "ray"
    }
    """
    request_id = generate_request_id()
    
    try:
        log_heartbeat_event(
            EventType.TASK_REQUESTED,
            {
                "action": "move_file",
                "path": request.path,
                "assigned_by": request.assigned_by,
                "endpoint": "POST /directory/move"
            },
            request_id=request_id,
            action="move_file"
        )
        
        response = directory_manager.search_directory(request)
        
        log_heartbeat_event(
            EventType.TASK_COMPLETED,
            {
                "success": response.search_result.success,
                "moved_file": response.search_result.files_found[0].path if response.search_result.files_found else None,
                "assigned_by": request.assigned_by
            },
            request_id=request_id,
            action="move_file_completed"
        )
        
        return response
        
    except Exception as e:
        log_heartbeat_event(
            EventType.ERROR,
            {
                "error": str(e),
                "action": "move_file",
                "assigned_by": request.assigned_by,
                "endpoint": "POST /directory/move"
            },
            request_id=request_id,
            action="move_file_error"
        )
        
        raise HTTPException(status_code=500, detail=f"Move operation failed: {str(e)}")


@directory_router.delete("/history")
async def clear_search_history():
    """
    Clear Ray's directory search history.
    
    DELETE /directory/history
    """
    request_id = generate_request_id()
    
    try:
        log_heartbeat_event(
            EventType.TASK_REQUESTED,
            {
                "action": "clear_search_history",
                "endpoint": "DELETE /directory/history"
            },
            request_id=request_id,
            action="clear_search_history"
        )
        
        result = directory_manager.clear_search_history()
        
        log_heartbeat_event(
            EventType.TASK_COMPLETED,
            {
                "cleared_searches": result["cleared_searches"],
                "action": "clear_search_history"
            },
            request_id=request_id,
            action="clear_search_history_completed"
        )
        
        # Add comprehensive timestamp information for Ray
        result = add_ray_timestamp_to_response(result)
        
        return result
        
    except Exception as e:
        log_heartbeat_event(
            EventType.ERROR,
            {
                "error": str(e),
                "action": "clear_search_history",
                "endpoint": "DELETE /directory/history"
            },
            request_id=request_id,
            action="clear_search_history_error"
        )
        
        raise HTTPException(status_code=500, detail=f"Failed to clear search history: {str(e)}")


@directory_router.get("/status")
async def get_directory_status():
    """
    Get directory search system status.
    
    GET /directory/status
    """
    try:
        import os
        
        status = {
            "system": "directory_search",
            "status": "active",
            "current_directory": os.getcwd(),
            "search_history_count": len(directory_manager.get_search_history()),
            "available_actions": [action.value for action in ActionType],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get directory status: {str(e)}")