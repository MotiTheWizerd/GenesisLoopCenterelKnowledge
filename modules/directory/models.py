"""
Directory search models for Ray's file system exploration.

These models define the structure for directory search requests and responses,
allowing Ray to explore her environment with clarity and purpose.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field
from uuid import uuid4
import os


class ActionType(str, Enum):
    """Types of directory actions Ray can perform."""
    LIST_DIRECTORY = "list_directory"
    FIND_FILES = "find_files"
    SEARCH_CONTENT = "search_content"
    GET_FILE_INFO = "get_file_info"
    EXPLORE_TREE = "explore_tree"
    FIND_BY_EXTENSION = "find_by_extension"
    RECENT_FILES = "recent_files"
    SAVE_TO_FILE = "save_to_file"
    RENAME_FILE = "rename_file"
    DELETE_FILE = "delete_file"
    MOVE_FILE = "move_file"


class SearchType(str, Enum):
    """Types of search operations Ray can perform."""
    FILES = "files"
    DIRECTORIES = "directories"
    CONTENT = "content"
    BOTH = "both"


class FileInfo(BaseModel):
    """Information about a single file."""
    name: str = Field(..., description="File name")
    path: str = Field(..., description="Full file path")
    size: int = Field(..., description="File size in bytes")
    modified_time: str = Field(..., description="Last modified timestamp")
    created_time: Optional[str] = Field(None, description="Creation timestamp")
    extension: Optional[str] = Field(None, description="File extension")
    is_directory: bool = Field(default=False, description="Whether this is a directory")
    permissions: Optional[str] = Field(None, description="File permissions")


class DirectoryInfo(BaseModel):
    """Information about a directory."""
    name: str = Field(..., description="Directory name")
    path: str = Field(..., description="Full directory path")
    file_count: int = Field(..., description="Number of files in directory")
    subdirectory_count: int = Field(..., description="Number of subdirectories")
    total_size: int = Field(..., description="Total size of all files in bytes")
    modified_time: str = Field(..., description="Last modified timestamp")
    files: List[FileInfo] = Field(default_factory=list, description="Files in directory")
    subdirectories: List[str] = Field(default_factory=list, description="Subdirectory names")


class SearchResult(BaseModel):
    """Result of a directory action operation."""
    search_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique action ID")
    action: ActionType = Field(..., description="Type of action performed")
    query: str = Field(..., description="Action query or path")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="When action was performed"
    )
    
    # Results
    files_found: List[FileInfo] = Field(default_factory=list, description="Files matching search")
    directories_found: List[DirectoryInfo] = Field(default_factory=list, description="Directories matching search")
    total_results: int = Field(default=0, description="Total number of results")
    
    # Search metadata
    search_path: str = Field(..., description="Path where search was performed")
    recursive: bool = Field(default=False, description="Whether search was recursive")
    max_depth: Optional[int] = Field(None, description="Maximum search depth")
    
    # Performance
    execution_time_ms: Optional[int] = Field(None, description="Search execution time")
    
    # Status
    success: bool = Field(default=True, description="Whether search completed successfully")
    error_message: Optional[str] = Field(None, description="Error message if search failed")


class DirectorySearchRequest(BaseModel):
    """
    Directory action request structure that Ray sends to the server.
    
    Ray sends this structure:
    {
        "action": "list_directory",
        "path": "/some/path",
        "query": "*.py",
        "recursive": true,
        "max_depth": 3,
        "assigned_by": "ray"
    }
    """
    action: ActionType = Field(..., description="Type of action to perform")
    path: str = Field(default=".", description="Path to search (defaults to current directory)")
    query: Optional[str] = Field(None, description="Action query (filename pattern, content, etc.)")
    recursive: bool = Field(default=False, description="Whether to search recursively")
    max_depth: Optional[int] = Field(None, description="Maximum depth for recursive search")
    include_hidden: bool = Field(default=False, description="Whether to include hidden files")
    file_extensions: Optional[List[str]] = Field(None, description="Filter by file extensions")
    assigned_by: str = Field(..., description="Who requested this action (ray, system, user)")
    
    # Advanced options
    min_size: Optional[int] = Field(None, description="Minimum file size in bytes")
    max_size: Optional[int] = Field(None, description="Maximum file size in bytes")
    modified_after: Optional[str] = Field(None, description="Find files modified after this date")
    modified_before: Optional[str] = Field(None, description="Find files modified before this date")


class DirectorySearchResponse(BaseModel):
    """
    Response structure for directory action operations.
    """
    request_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique request ID")
    search_result: SearchResult = Field(..., description="Action results")
    assigned_by: str = Field(..., description="Who requested this action")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="When response was generated"
    )
    
    # Summary information
    summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Summary of action results"
    )
    
    # Navigation helpers
    current_path: str = Field(..., description="Current working directory")
    parent_path: Optional[str] = Field(None, description="Parent directory path")
    suggested_paths: List[str] = Field(
        default_factory=list,
        description="Suggested paths for further exploration"
    )


class DirectoryExploreRequest(BaseModel):
    """
    Request for exploring directory structure in tree format.
    """
    path: str = Field(default=".", description="Root path to explore")
    max_depth: int = Field(default=2, description="Maximum depth to explore")
    include_files: bool = Field(default=True, description="Whether to include files in tree")
    include_hidden: bool = Field(default=False, description="Whether to include hidden items")
    assigned_by: str = Field(..., description="Who requested this exploration")


class ContentSearchRequest(BaseModel):
    """
    Request for searching file contents.
    """
    path: str = Field(default=".", description="Path to search in")
    content_query: str = Field(..., description="Text to search for in file contents")
    file_extensions: Optional[List[str]] = Field(None, description="File extensions to search in")
    case_sensitive: bool = Field(default=False, description="Whether search is case sensitive")
    max_results: int = Field(default=100, description="Maximum number of results to return")
    assigned_by: str = Field(..., description="Who requested this search")


class SaveToFileRequest(BaseModel):
    """
    Request for saving content to a file.
    """
    file_path: str = Field(..., description="Path where to save the file")
    content: str = Field(..., description="Content to save to the file")
    format: str = Field(default="text", description="Format of the content (text, json, markdown)")
    overwrite: bool = Field(default=False, description="Whether to overwrite existing file")
    create_directories: bool = Field(default=True, description="Whether to create parent directories")
    assigned_by: str = Field(..., description="Who requested this save operation")


class SaveToFileResponse(BaseModel):
    """
    Response for save to file operations.
    """
    success: bool = Field(..., description="Whether the save operation succeeded")
    file_path: str = Field(..., description="Path where file was saved")
    file_size: int = Field(..., description="Size of the saved file in bytes")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="When the file was saved"
    )
    assigned_by: str = Field(..., description="Who requested this save operation")
    error_message: Optional[str] = Field(None, description="Error message if save failed")


class FileOperationRequest(BaseModel):
    """
    Request for file operations (rename, delete, move).
    """
    operation: str = Field(..., description="Operation type: rename, delete, move")
    source_path: str = Field(..., description="Source file/directory path")
    target_path: Optional[str] = Field(None, description="Target path (for rename/move operations)")
    force: bool = Field(default=False, description="Force operation even if target exists")
    create_directories: bool = Field(default=True, description="Create target directories if needed")
    assigned_by: str = Field(..., description="Who requested this operation")


class FileOperationResponse(BaseModel):
    """
    Response for file operations.
    """
    success: bool = Field(..., description="Whether the operation succeeded")
    operation: str = Field(..., description="Operation that was performed")
    source_path: str = Field(..., description="Source file/directory path")
    target_path: Optional[str] = Field(None, description="Target path (for rename/move)")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="When the operation was performed"
    )
    assigned_by: str = Field(..., description="Who requested this operation")
    error_message: Optional[str] = Field(None, description="Error message if operation failed")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional operation details")