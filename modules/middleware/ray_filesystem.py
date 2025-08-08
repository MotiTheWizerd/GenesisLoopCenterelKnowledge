"""
Ray's file system access middleware.
Enforces file operation restrictions to ensure Ray only operates within her playground.
"""

import os
from pathlib import Path
from typing import Union, Tuple, Optional

# Constants
RAY_PLAYGROUND_DIR = "ray_only_playground"

class RayFilesystemMiddleware:
    """
    Middleware that enforces Ray's file system access restrictions.
    This ensures Ray can only read/write/modify files within her designated playground directory.
    """
    
    @staticmethod
    def get_playground_path() -> Path:
        """Get the absolute path to Ray's playground directory."""
        playground = os.path.abspath(RAY_PLAYGROUND_DIR)
        if not os.path.exists(playground):
            os.makedirs(playground, exist_ok=True)
        return Path(playground)

    @staticmethod
    def validate_path(file_path: Union[str, Path], operation: str = "write") -> Tuple[bool, Optional[str]]:
        """
        Validate if a path is within Ray's allowed playground directory.
        
        Args:
            file_path: The path to validate
            operation: Type of operation being performed (read, write, delete, move, rename)
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        try:
            # Convert to Path object and resolve to absolute path
            path = Path(file_path).resolve()
            playground = RayFilesystemMiddleware.get_playground_path()
            
            # Handle special cases for move/rename operations
            if operation in ["move", "rename"] and isinstance(file_path, str) and ":" in file_path:
                source, target = file_path.split(":", 1)
                source_valid = Path(source).resolve().is_relative_to(playground)
                target_valid = Path(target).resolve().is_relative_to(playground)
                
                if not (source_valid and target_valid):
                    return False, f"Both source and target paths must be within {RAY_PLAYGROUND_DIR} directory"
                return True, None
            
            # For all other operations, verify path is within playground
            if not path.is_relative_to(playground):
                return False, f"Access denied: Operation only allowed in {RAY_PLAYGROUND_DIR} directory"
            
            return True, None
            
        except Exception as e:
            return False, f"Path validation error: {str(e)}"
    
    @staticmethod
    def ensure_playground_path(file_path: Union[str, Path]) -> Path:
        """
        Convert any file path to be within Ray's playground directory.
        
        Args:
            file_path: The original file path
            
        Returns:
            Path: The converted path within the playground directory
        """
        playground = RayFilesystemMiddleware.get_playground_path()
        
        # If already a valid playground path, return as is
        try:
            path = Path(file_path).resolve()
            if path.is_relative_to(playground):
                return path
        except Exception:
            pass
        
        # Otherwise, move to playground root
        filename = os.path.basename(str(file_path))
        return playground / filename

# Error messages
ACCESS_DENIED = """
🚫 Access Denied: Operation not allowed outside ray_only_playground directory
Ray can only perform file operations within her designated playground directory.
This is a security measure to protect system integrity.
Please modify the path to be within: {playground_path}
"""
