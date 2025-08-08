"""
Configuration module for Ray's file system restrictions.
Ensures Ray can only operate within her designated playground directory.
"""

import os
from typing import Optional, Tuple, Union
from pathlib import Path

# Constants for Ray's filesystem access
RAY_PLAYGROUND_DIR = "ray_only_playground"
ALLOWED_OPERATIONS = ["read", "write", "delete", "move", "rename"]

class RayFilesystemRestriction:
    """Manages Ray's filesystem access restrictions."""
    
    @staticmethod
    def get_playground_path() -> Path:
        """Get the absolute path to Ray's playground directory."""
        return Path(os.path.abspath(RAY_PLAYGROUND_DIR))
    
    @staticmethod
    def validate_path(file_path: Union[str, Path], operation: str = "write") -> Tuple[bool, Optional[str]]:
        """
        Validate if a file path is within Ray's allowed playground directory.
        
        Args:
            file_path: Path to validate
            operation: Type of operation being performed
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if operation not in ALLOWED_OPERATIONS:
            return False, f"Invalid operation: {operation}"
            
        try:
            # Convert to Path object and resolve to absolute path
            path = Path(file_path).resolve()
            playground = RayFilesystemRestriction.get_playground_path()
            
            # For move/rename operations, ensure both source and target are in playground
            if operation in ["move", "rename"] and ":" in str(file_path):
                source, target = str(file_path).split(":", 1)
                source_valid = Path(source).resolve().is_relative_to(playground)
                target_valid = Path(target).resolve().is_relative_to(playground)
                
                if not (source_valid and target_valid):
                    return False, "Both source and target must be in ray_only_playground directory"
                return True, None
            
            # For other operations, check if path is within playground
            if not path.is_relative_to(playground):
                return False, f"Access denied: Operations only allowed in {RAY_PLAYGROUND_DIR} directory"
                
            return True, None
            
        except Exception as e:
            return False, f"Path validation error: {str(e)}"
    
    @staticmethod
    def ensure_playground_exists() -> None:
        """Create Ray's playground directory if it doesn't exist."""
        playground = RayFilesystemRestriction.get_playground_path()
        playground.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def sanitize_path(file_path: Union[str, Path]) -> Path:
        """
        Convert any path to be within Ray's playground directory.
        
        Args:
            file_path: Original file path
            
        Returns:
            Path: Sanitized path within playground directory
        """
        # Get just the filename/end path components
        if isinstance(file_path, str):
            path = Path(file_path)
        else:
            path = file_path
            
        relative_parts = path.parts[-1:]  # Just take the filename
        playground = RayFilesystemRestriction.get_playground_path()
        
        return playground.joinpath(*relative_parts)

# Error messages
ACCESS_DENIED = """
🚫 Access Denied: Operation not allowed outside ray_only_playground directory
This is a security measure to protect system integrity.
Please ensure all file operations are within the designated playground directory.
"""

INVALID_OPERATION = """
❌ Invalid Operation: The requested file operation is not supported
Allowed operations: {', '.join(ALLOWED_OPERATIONS)}
"""

# Initialize playground directory on module import
RayFilesystemRestriction.ensure_playground_exists()
