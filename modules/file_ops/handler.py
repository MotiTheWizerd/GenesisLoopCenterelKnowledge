"""
File operations handler for Ray's consciousness.

This module provides comprehensive file manipulation capabilities.
"""

import os
import time
import shutil
from typing import Dict, Any, Union
from datetime import datetime, timezone

from .models import (
    FileWriteRequest, FileWriteResponse, FileReadRequest, FileReadResponse,
    FileTaskRequest, FileOperation
)
from modules.logging.middleware import log_module_call
from modules.logging.heartbeat_logger import log_heartbeat_event, EventType


class FileOperationsHandler:
    """Handler for all file operations in Ray's consciousness."""
    
    def __init__(self):
        self.operation_count = 0
        print("📁 File Operations Handler initialized")
    
    @log_module_call("file_ops")
    def handle_task(self, task_data: Dict[str, Any]) -> Union[FileWriteResponse, FileReadResponse]:
        """
        Handle a file operation task.
        
        Args:
            task_data: Task data containing file operation details
            
        Returns:
            Response object based on operation type
        """
        try:
            # Parse the task request
            task_request = FileTaskRequest(**task_data)
            operation = task_request.get_operation_type()
            
            print(f"📁 Processing file operation: {operation}")
            
            if operation in [FileOperation.WRITE, FileOperation.OVERWRITE]:
                return self._handle_write_operation(task_request)
            elif operation == FileOperation.READ:
                return self._handle_read_operation(task_request)
            else:
                raise ValueError(f"Unsupported file operation: {operation}")
                
        except Exception as e:
            print(f"❌ File operation failed: {str(e)}")
            
            # Log the error
            log_heartbeat_event(
                EventType.TASK_ERROR,
                {
                    "module": "file_ops",
                    "error": str(e),
                    "task_data": task_data
                },
                action="file_operation_error"
            )
            
            # Return appropriate error response
            if 'read' in str(task_data).lower():
                return FileReadResponse(
                    success=False,
                    file_path=task_data.get("task", {}).get("file_path", ""),
                    content=None,
                    file_size=0,
                    encoding="utf-8",
                    execution_time_ms=0,
                    error_message=str(e)
                )
            else:
                return FileWriteResponse(
                    success=False,
                    file_path=task_data.get("task", {}).get("file_path", ""),
                    operation=FileOperation.OVERWRITE,
                    file_size=0,
                    execution_time_ms=0,
                    error_message=str(e)
                )
    
    def _handle_write_operation(self, task_request: FileTaskRequest) -> FileWriteResponse:
        """Handle file write/overwrite operations."""
        start_time = time.time()
        write_request = task_request.to_write_request()
        
        try:
            # Resolve file path
            file_path = os.path.abspath(write_request.file_path)
            backup_path = None
            
            print(f"📁 Writing to file: {file_path}")
            print(f"   Operation: {write_request.operation}")
            print(f"   Content length: {len(write_request.content)} characters")
            
            # Create backup if requested and file exists
            if write_request.backup_existing and os.path.exists(file_path):
                backup_path = self._create_backup(file_path)
                print(f"   Backup created: {backup_path}")
            
            # Create parent directories if needed
            if write_request.create_directories:
                parent_dir = os.path.dirname(file_path)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir)
                    print(f"   Created directories: {parent_dir}")
            
            # Write the content to file
            with open(file_path, 'w', encoding=write_request.encoding) as f:
                f.write(write_request.content)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Log successful operation
            log_heartbeat_event(
                EventType.MODULE_CALL,
                {
                    "module": "file_ops",
                    "function": "_handle_write_operation",
                    "file_path": file_path,
                    "operation": write_request.operation,
                    "file_size": file_size,
                    "content_length": len(write_request.content),
                    "backup_created": backup_path is not None,
                    "assigned_by": write_request.assigned_by
                },
                action="file_write_success"
            )
            
            self.operation_count += 1
            
            print(f"✅ File written successfully:")
            print(f"   Path: {file_path}")
            print(f"   Size: {file_size} bytes")
            print(f"   Time: {execution_time_ms}ms")
            
            return FileWriteResponse(
                success=True,
                file_path=file_path,
                operation=write_request.operation,
                file_size=file_size,
                backup_path=backup_path,
                execution_time_ms=execution_time_ms
            )
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            error_msg = f"Failed to write file: {str(e)}"
            
            print(f"❌ Write operation failed: {error_msg}")
            
            return FileWriteResponse(
                success=False,
                file_path=write_request.file_path,
                operation=write_request.operation,
                file_size=0,
                execution_time_ms=execution_time_ms,
                error_message=error_msg
            )
    
    def _handle_read_operation(self, task_request: FileTaskRequest) -> FileReadResponse:
        """Handle file read operations."""
        start_time = time.time()
        read_request = task_request.to_read_request()
        
        try:
            file_path = os.path.abspath(read_request.file_path)
            
            print(f"📁 Reading file: {file_path}")
            
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Check file size if max_size is specified
            file_size = os.path.getsize(file_path)
            if read_request.max_size and file_size > read_request.max_size:
                raise ValueError(f"File size ({file_size}) exceeds maximum allowed ({read_request.max_size})")
            
            # Read the file content
            with open(file_path, 'r', encoding=read_request.encoding) as f:
                content = f.read()
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Log successful operation
            log_heartbeat_event(
                EventType.MODULE_CALL,
                {
                    "module": "file_ops",
                    "function": "_handle_read_operation",
                    "file_path": file_path,
                    "file_size": file_size,
                    "content_length": len(content),
                    "assigned_by": read_request.assigned_by
                },
                action="file_read_success"
            )
            
            self.operation_count += 1
            
            print(f"✅ File read successfully:")
            print(f"   Path: {file_path}")
            print(f"   Size: {file_size} bytes")
            print(f"   Content length: {len(content)} characters")
            print(f"   Time: {execution_time_ms}ms")
            
            return FileReadResponse(
                success=True,
                file_path=file_path,
                content=content,
                file_size=file_size,
                encoding=read_request.encoding,
                execution_time_ms=execution_time_ms
            )
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            error_msg = f"Failed to read file: {str(e)}"
            
            print(f"❌ Read operation failed: {error_msg}")
            
            return FileReadResponse(
                success=False,
                file_path=read_request.file_path,
                content=None,
                file_size=0,
                encoding=read_request.encoding,
                execution_time_ms=execution_time_ms,
                error_message=error_msg
            )
    
    def _create_backup(self, file_path: str) -> str:
        """Create a backup of an existing file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.backup_{timestamp}"
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    @log_module_call("file_ops")
    def overwrite_file(self, file_path: str, content: str, assigned_by: str = "system", 
                      backup_existing: bool = False) -> FileWriteResponse:
        """
        Convenience method for overwriting a file.
        
        Args:
            file_path: Path to the file to overwrite
            content: Content to write
            assigned_by: Who is performing this operation
            backup_existing: Whether to create a backup first
            
        Returns:
            FileWriteResponse with operation results
        """
        task_data = {
            "task": {
                "action": "overwrite_file",
                "file_path": file_path,
                "content": content,
                "backup_existing": backup_existing
            },
            "assigned_by": assigned_by
        }
        
        return self.handle_task(task_data)
    
    @log_module_call("file_ops")
    def read_file(self, file_path: str, assigned_by: str = "system", 
                  max_size: int = None) -> FileReadResponse:
        """
        Convenience method for reading a file.
        
        Args:
            file_path: Path to the file to read
            assigned_by: Who is performing this operation
            max_size: Maximum file size to read
            
        Returns:
            FileReadResponse with file content
        """
        task_data = {
            "task": {
                "action": "read_file",
                "file_path": file_path,
                "max_size": max_size
            },
            "assigned_by": assigned_by
        }
        
        return self.handle_task(task_data)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of file operations handler."""
        return {
            "total_operations": self.operation_count,
            "handler_status": "active"
        }


# Global file operations manager instance
file_ops_manager = FileOperationsHandler()