"""
Tests for the heartbeat handler functionality.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

from modules.heartbeat.handler import HeartbeatHandler, heartbeat_handler


class TestHeartbeatHandler:
    """Test cases for HeartbeatHandler class."""
    
    def test_default_state_creation(self):
        """Test that default state is created correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_heartbeat.json"
            handler = HeartbeatHandler(str(config_path))
            
            heartbeat = handler.get_current_heartbeat()
            
            # Verify basic structure
            assert heartbeat["type"] == "heartbeat"
            assert heartbeat["status"] == "idle"
            assert heartbeat["in_task"] is False
            
            # Verify ray_state
            ray_state = heartbeat["ray_state"]
            assert ray_state["active_task"] is None
            assert ray_state["last_reflection"] == "task_93a"
            assert ray_state["loop_iteration"] == 27
            assert ray_state["uptime"] == "02:41:12"
            
            # Verify cognitive_map
            cognitive_map = heartbeat["cognitive_map"]
            assert "folder_schema" in cognitive_map
            assert "default_paths" in cognitive_map
            assert "naming_conventions" in cognitive_map
            
            # Verify execution_protocols
            execution_protocols = heartbeat["execution_protocols"]
            assert execution_protocols["auto_reflection"] is True
            assert execution_protocols["reflection_threshold_sec"] == 180
            assert execution_protocols["max_idle_loops"] == 10
            
            # Verify memory_flags
            memory_flags = heartbeat["memory_flags"]
            assert memory_flags["schema_loaded"] is True
            assert memory_flags["task_context_restored"] is True
    
    def test_load_from_config_file(self):
        """Test loading heartbeat state from configuration file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_heartbeat.json"
            
            # Create test config
            test_config = {
                "type": "heartbeat",
                "timestamp": "2025-07-30T01:10:00Z",
                "status": "testing",
                "in_task": True,
                "ray_state": {
                    "active_task": "test_task",
                    "last_reflection": "task_test",
                    "loop_iteration": 100,
                    "uptime": "10:00:00"
                },
                "cognitive_map": {
                    "folder_schema": {
                        "test": "./test"
                    },
                    "default_paths": {
                        "test": "./test"
                    },
                    "naming_conventions": {
                        "test": "test_{id}.json"
                    }
                },
                "execution_protocols": {
                    "auto_reflection": False,
                    "reflection_threshold_sec": 300,
                    "max_idle_loops": 5
                },
                "memory_flags": {
                    "schema_loaded": False,
                    "task_context_restored": False
                }
            }
            
            with open(config_path, 'w') as f:
                json.dump(test_config, f)
            
            # Load handler with config
            handler = HeartbeatHandler(str(config_path))
            heartbeat = handler.get_current_heartbeat()
            
            # Verify loaded values (timestamp should be updated to current)
            assert heartbeat["type"] == "heartbeat"
            assert heartbeat["status"] == "testing"
            assert heartbeat["in_task"] is True
            
            ray_state = heartbeat["ray_state"]
            assert ray_state["active_task"] == "test_task"
            assert ray_state["last_reflection"] == "task_test"
            assert ray_state["loop_iteration"] == 100
            assert ray_state["uptime"] == "10:00:00"
    
    def test_state_updates(self):
        """Test updating heartbeat state."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_heartbeat.json"
            handler = HeartbeatHandler(str(config_path))
            
            # Test basic state update
            handler.update_state(status="active", in_task=True)
            heartbeat = handler.get_current_heartbeat()
            
            assert heartbeat["status"] == "active"
            assert heartbeat["in_task"] is True
            
            # Test ray_state update
            handler.update_ray_state(active_task="new_task", loop_iteration=50)
            heartbeat = handler.get_current_heartbeat()
            
            ray_state = heartbeat["ray_state"]
            assert ray_state["active_task"] == "new_task"
            assert ray_state["loop_iteration"] == 50
    
    def test_task_status_management(self):
        """Test task status management methods."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_heartbeat.json"
            handler = HeartbeatHandler(str(config_path))
            
            # Set task status
            handler.set_task_status(in_task=True, active_task="task_123")
            heartbeat = handler.get_current_heartbeat()
            
            assert heartbeat["in_task"] is True
            assert heartbeat["ray_state"]["active_task"] == "task_123"
            
            # Clear task status
            handler.set_task_status(in_task=False, active_task=None)
            heartbeat = handler.get_current_heartbeat()
            
            assert heartbeat["in_task"] is False
            assert heartbeat["ray_state"]["active_task"] is None
    
    def test_loop_iteration_increment(self):
        """Test loop iteration increment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_heartbeat.json"
            handler = HeartbeatHandler(str(config_path))
            
            # Get initial iteration
            initial_heartbeat = handler.get_current_heartbeat()
            initial_iteration = initial_heartbeat["ray_state"]["loop_iteration"]
            
            # Increment
            handler.increment_loop_iteration()
            updated_heartbeat = handler.get_current_heartbeat()
            new_iteration = updated_heartbeat["ray_state"]["loop_iteration"]
            
            assert new_iteration == initial_iteration + 1
    
    def test_uptime_update(self):
        """Test uptime update."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_heartbeat.json"
            handler = HeartbeatHandler(str(config_path))
            
            # Update uptime
            new_uptime = "05:30:45"
            handler.update_uptime(new_uptime)
            heartbeat = handler.get_current_heartbeat()
            
            assert heartbeat["ray_state"]["uptime"] == new_uptime
    
    def test_timestamp_updates(self):
        """Test that timestamps are updated correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_heartbeat.json"
            handler = HeartbeatHandler(str(config_path))
            
            # Get initial timestamp
            heartbeat1 = handler.get_current_heartbeat()
            timestamp1 = heartbeat1["timestamp"]
            
            # Wait a moment and get another heartbeat
            import time
            time.sleep(0.01)
            
            heartbeat2 = handler.get_current_heartbeat()
            timestamp2 = heartbeat2["timestamp"]
            
            # Timestamps should be different
            assert timestamp1 != timestamp2
    
    def test_global_handler_instance(self):
        """Test that the global handler instance works correctly."""
        # This tests the actual global instance
        heartbeat = heartbeat_handler.get_current_heartbeat()
        
        # Verify basic structure
        assert heartbeat["type"] == "heartbeat"
        assert "ray_state" in heartbeat
        assert "cognitive_map" in heartbeat
        assert "execution_protocols" in heartbeat
        assert "memory_flags" in heartbeat
        
        # Test that it can be updated
        original_iteration = heartbeat["ray_state"]["loop_iteration"]
        heartbeat_handler.increment_loop_iteration()
        
        updated_heartbeat = heartbeat_handler.get_current_heartbeat()
        new_iteration = updated_heartbeat["ray_state"]["loop_iteration"]
        
        assert new_iteration == original_iteration + 1


class TestHeartbeatStructure:
    """Test cases for heartbeat structure validation."""
    
    def test_required_fields_present(self):
        """Test that all required fields are present in heartbeat."""
        heartbeat = heartbeat_handler.get_current_heartbeat()
        
        required_fields = [
            "type", "timestamp", "status", "in_task",
            "ray_state", "cognitive_map", "execution_protocols", "memory_flags"
        ]
        
        for field in required_fields:
            assert field in heartbeat, f"Required field '{field}' missing from heartbeat"
    
    def test_ray_state_structure(self):
        """Test ray_state structure."""
        heartbeat = heartbeat_handler.get_current_heartbeat()
        ray_state = heartbeat["ray_state"]
        
        required_ray_fields = ["active_task", "last_reflection", "loop_iteration", "uptime"]
        
        for field in required_ray_fields:
            assert field in ray_state, f"Required ray_state field '{field}' missing"
    
    def test_cognitive_map_structure(self):
        """Test cognitive_map structure."""
        heartbeat = heartbeat_handler.get_current_heartbeat()
        cognitive_map = heartbeat["cognitive_map"]
        
        required_cognitive_fields = ["folder_schema", "default_paths", "naming_conventions"]
        
        for field in required_cognitive_fields:
            assert field in cognitive_map, f"Required cognitive_map field '{field}' missing"
    
    def test_execution_protocols_structure(self):
        """Test execution_protocols structure."""
        heartbeat = heartbeat_handler.get_current_heartbeat()
        execution_protocols = heartbeat["execution_protocols"]
        
        required_protocol_fields = ["auto_reflection", "reflection_threshold_sec", "max_idle_loops"]
        
        for field in required_protocol_fields:
            assert field in execution_protocols, f"Required execution_protocols field '{field}' missing"
    
    def test_memory_flags_structure(self):
        """Test memory_flags structure."""
        heartbeat = heartbeat_handler.get_current_heartbeat()
        memory_flags = heartbeat["memory_flags"]
        
        required_memory_fields = ["schema_loaded", "task_context_restored"]
        
        for field in required_memory_fields:
            assert field in memory_flags, f"Required memory_flags field '{field}' missing"