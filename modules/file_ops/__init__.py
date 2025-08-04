"""
File operations module for Ray's consciousness.

This module provides file manipulation capabilities including:
- Writing/overwriting files
- Reading files
- File management operations
"""

from .handler import file_ops_manager
from .models import FileWriteRequest, FileWriteResponse, FileReadRequest, FileReadResponse

__all__ = [
    'file_ops_manager',
    'FileWriteRequest',
    'FileWriteResponse', 
    'FileReadRequest',
    'FileReadResponse'
]