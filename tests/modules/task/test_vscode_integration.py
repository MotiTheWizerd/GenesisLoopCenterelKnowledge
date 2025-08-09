"""Tests for TaskManager integration with VSCode Logic module."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from modules.task.handler import TaskManager


class TestTaskManagerVSCodeIntegration:
    def setup_method(self):
        self.task_manager = TaskManager()
    
    @patch('modules.task.handler.vscode_logic_manager')
    def test_execute_vscode_logic_action(self, mock_vscode_manager):
        """Test that _execute_vscode_logic_action correctly handles VSCode Logic operations."""
        # Setup mock to return a successful response
        mock_response = MagicMock()
        mock_response.dict.return_value = {
            "success": True,
            "action": "send_vs_response",
            "message": "Hello, user!",
            "is_final": False,
            "execution_time_ms": 100,
            "error_message": None
        }
        
        # Setup the async run to return the mock response
        mock_vscode_manager.handle_task.return_value = mock_response
        
        # Create a sample task data
        task_data = {
            "action": "send_vs_response",
            "message": "Hello, user!",
            "ray_prompt": "This is reasoning for next round",
            "is_final": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "additional_data": {"nested": "structure", "works": True},
            "assigned_by": "ray"
        }
        
        # Call the method
        result = self.task_manager._execute_vscode_logic_action(task_data)
        
        # Verify the result
        assert result["executed"] == True
        assert result["action"] == "send_vs_response"
        assert "results" in result
        assert result["results"] == mock_response.dict.return_value
        
        # Verify that vscode_logic_manager.handle_task was called with the correct data
        mock_vscode_manager.handle_task.assert_called_once()
        call_args = mock_vscode_manager.handle_task.call_args[0][0]
        assert "task" in call_args
        assert len(call_args["task"]) == 1
        assert call_args["task"][0] == task_data
        assert call_args["assigned_by"] == "ray"
        assert call_args["execute_immediately"] == True
    
    @patch('modules.task.handler.vscode_logic_manager')
    def test_execute_vscode_logic_action_exception(self, mock_vscode_manager):
        """Test that _execute_vscode_logic_action correctly handles exceptions."""
        # Setup mock to raise an exception
        mock_vscode_manager.handle_task.side_effect = Exception("Test exception")
        
        # Create a sample task data
        task_data = {
            "action": "send_vs_response",
            "message": "Hello, user!",
            "ray_prompt": "This is reasoning for next round",
            "is_final": False
        }
        
        # Call the method
        result = self.task_manager._execute_vscode_logic_action(task_data)
        
        # Verify the result indicates failure
        assert result["executed"] == False
        assert "error" in result
        assert "Test exception" in result["error"]