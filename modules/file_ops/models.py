"""
Models for file operations module.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum


class FileOperation(str, Enum):
    """Types of file operations supported."""
    WRITE = "write"
    OVERWRITE = "overwrite_file"
    READ = "read"
    APPEND = "append"
    DELETE = "delete"


class FileWriteRequest(BaseModel):
    """
    Request for writing/overwriting a file.
    """
    file_path: str = Field(..., description="Path to the file to write/overwrite")
    content: str = Field(..., description="Content to write to the file")
    operation: FileOperation = Field(default=FileOperation.OVERWRITE, description="Type of file operation")
    encoding: str = Field(default="utf-8", description="File encoding")
    create_directories: bool = Field(default=True, description="Whether to create parent directories")
    backup_existing: bool = Field(default=False, description="Whether to create backup of existing file")
    assigned_by: str = Field(..., description="Who requested this operation")


class FileWriteResponse(BaseModel):
    """
    Response for file write operations.
    """
    success: bool = Field(..., description="Whether the operation succeeded")
    file_path: str = Field(..., description="Path of the file that was written")
    operation: FileOperation = Field(..., description="Operation that was performed")
    file_size: int = Field(..., description="Size of the written file in bytes")
    backup_path: Optional[str] = Field(None, description="Path to backup file if created")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="When the operation was completed"
    )
    execution_time_ms: int = Field(..., description="Time taken to complete operation in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if operation failed")


class FileReadRequest(BaseModel):
    """
    Request for reading a file.
    """
    file_path: str = Field(..., description="Path to the file to read")
    encoding: str = Field(default="utf-8", description="File encoding")
    max_size: Optional[int] = Field(None, description="Maximum file size to read in bytes")
    assigned_by: str = Field(..., description="Who requested this operation")


class FileReadResponse(BaseModel):
    """
    Response for file read operations.
    """
    success: bool = Field(..., description="Whether the read operation succeeded")
    file_path: str = Field(..., description="Path of the file that was read")
    content: Optional[str] = Field(None, description="Content of the file")
    file_size: int = Field(..., description="Size of the file in bytes")
    encoding: str = Field(..., description="Encoding used to read the file")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="When the file was read"
    )
    execution_time_ms: int = Field(..., description="Time taken to read file in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if read failed")


class FileTaskRequest(BaseModel):
    """
    Generic file task request that can handle different file operations.
    """
    task: Dict[str, Any] = Field(..., description="Task data containing file operation details")
    assigned_by: str = Field(..., description="Who assigned this task")
    
    def get_operation_type(self) -> FileOperation:
        """Extract the operation type from task data."""
        action = self.task.get("action", "").lower()
        
        if action in ["write", "write_file"]:
            return FileOperation.WRITE
        elif action in ["overwrite", "overwrite_file"]:
            return FileOperation.OVERWRITE
        elif action in ["read", "read_file"]:
            return FileOperation.READ
        elif action in ["append", "append_file"]:
            return FileOperation.APPEND
        elif action in ["delete", "delete_file"]:
            return FileOperation.DELETE
        else:
            return FileOperation.OVERWRITE  # Default to overwrite
    
    def to_write_request(self) -> FileWriteRequest:
        """Convert to FileWriteRequest."""
        return FileWriteRequest(
            file_path=self.task.get("file_path", ""),
            content=self.task.get("content", ""),
            operation=self.get_operation_type(),
            encoding=self.task.get("encoding", "utf-8"),
            create_directories=self.task.get("create_directories", True),
            backup_existing=self.task.get("backup_existing", False),
            assigned_by=self.assigned_by
        )
    
    def to_read_request(self) -> FileReadRequest:
        """Convert to FileReadRequest."""
        return FileReadRequest(
            file_path=self.task.get("file_path", ""),
            encoding=self.task.get("encoding", "utf-8"),
            max_size=self.task.get("max_size"),
            assigned_by=self.assigned_by
        )