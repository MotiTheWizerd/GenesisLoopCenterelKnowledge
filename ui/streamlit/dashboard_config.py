#!/usr/bin/env python3
"""
Dashboard configuration for Ray's Streamlit interface.
"""

from pathlib import Path
import os

class DashboardConfig:
    """Configuration settings for the dashboard."""
    
    def __init__(self):
        # Calculate project root from this file's location
        # This file is in ui/streamlit/, so go up 2 levels to reach project root
        self.project_root = Path(__file__).parent.parent.parent
        
        # Ensure we have the correct path
        self._validate_project_root()
    
    def _validate_project_root(self):
        """Validate that we found the correct project root."""
        expected_files = [
            "extract/memory_metadata.json",
            "pyproject.toml",
            "main.py"
        ]
        
        for file_path in expected_files:
            if (self.project_root / file_path).exists():
                return  # Found at least one expected file
        
        # If validation fails, try alternative paths
        alternative_roots = [
            Path.cwd(),  # Current working directory
            Path(__file__).parent.parent,  # Go up 1 level
            Path(__file__).parent.parent.parent.parent,  # Go up 3 levels
        ]
        
        for alt_root in alternative_roots:
            if (alt_root / "extract/memory_metadata.json").exists():
                self.project_root = alt_root
                return
    
    @property
    def extract_dir(self):
        """Path to extract directory."""
        return self.project_root / "extract"
    
    @property
    def logs_dir(self):
        """Path to logs directory."""
        return self.project_root / "logs"
    
    @property
    def rays_memory_room(self):
        """Path to Ray's memory room."""
        return self.project_root / "RaysHome" / "MemoryRoom"
    
    @property
    def ray_workspace(self):
        """Path to Ray's workspace."""
        return self.project_root / "ray_workspace"
    
    @property
    def memories_dir(self):
        """Path to memories directory (for backward compatibility)."""
        return self.project_root / "memories"
    
    @property
    def backups_dir(self):
        """Path to backups directory."""
        return self.project_root / "backups"
    
    def get_api_ports(self):
        """Get list of common API server ports to try."""
        return [8000, 8001, 8080, 3000, 8500]
    
    def get_memory_files(self):
        """Get list of all memory files."""
        memory_files = []
        
        # Key memory files
        key_files = [
            self.extract_dir / "memory_metadata.json",
            self.extract_dir / "agent_memories.json",
            self.extract_dir / "chats.json",
            self.logs_dir / "memory_entries.jsonl",
            self.logs_dir / "heartbeat_detailed.jsonl",
            self.logs_dir / "command_history.jsonl"
        ]
        
        for file_path in key_files:
            if file_path.exists():
                memory_files.append(str(file_path))
        
        # Scan directories for additional files
        directories = [
            self.extract_dir,
            self.logs_dir,
            self.rays_memory_room,
            self.ray_workspace,
            self.memories_dir
        ]
        
        for directory in directories:
            if directory.exists():
                # Add JSON files
                for file_path in directory.rglob("*.json"):
                    if str(file_path) not in memory_files:
                        memory_files.append(str(file_path))
                
                # Add JSONL files
                for file_path in directory.rglob("*.jsonl"):
                    if str(file_path) not in memory_files:
                        memory_files.append(str(file_path))
                
                # Add markdown files from memory directories
                if "memory" in directory.name.lower() or "rays" in directory.name.lower():
                    for file_path in directory.rglob("*.md"):
                        if str(file_path) not in memory_files:
                            memory_files.append(str(file_path))
        
        return sorted(memory_files)
    
    def get_debug_info(self):
        """Get debug information about paths."""
        debug_info = {
            "project_root": str(self.project_root),
            "current_working_dir": str(Path.cwd()),
            "config_file_location": str(Path(__file__)),
            "paths_exist": {}
        }
        
        paths_to_check = [
            ("extract_dir", self.extract_dir),
            ("logs_dir", self.logs_dir),
            ("rays_memory_room", self.rays_memory_room),
            ("ray_workspace", self.ray_workspace),
            ("memory_metadata", self.extract_dir / "memory_metadata.json"),
            ("agent_memories", self.extract_dir / "agent_memories.json"),
            ("chats", self.extract_dir / "chats.json")
        ]
        
        for name, path in paths_to_check:
            debug_info["paths_exist"][name] = {
                "path": str(path),
                "exists": path.exists()
            }
        
        return debug_info

# Global config instance
config = DashboardConfig()