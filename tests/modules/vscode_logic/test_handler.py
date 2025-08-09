"""Tests for VSCode Logic module handler."""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from modules.vscode_logic.handler import VSCodeLogicHandler
from modules.vscode_logic.models import VSCodeLogicResponse


class TestVSCodeLogicHandler:
    def setup_method(self):
        self.handler = VSCodeLogicHandler()
    
    @pytest.mark.asyncio
    @patch('modules.vscode_logic.handler.forward_vscode_response')
    @patch('modules.vscode_logic.handler.log_heartbeat_event')
    async def test_handle_send_response(self, mock_log_event, mock_forward):
        """Test handling a send_vs_response action."""
        # Setup mock to return a successful response
        mock_forward.return_value = {"status": "forwarded", "external_status": 200}
        
        # Create a sample task request
        task_data = {
            "task": [{
                "action": "send_vs_response",
                "message": "Hello, user!",
                "ray_prompt": "This is reasoning for next round",
                "is_final": False,
                "additional_data": {"nested": "structure", "works": True}
            }],
            "assigned_by": "ray",
            "execute_immediately": True
        }
        
        # Call the handler
        response = await self.handler.handle_task(task_data)
        
        # Verify the response
        assert isinstance(response, VSCodeLogicResponse)
        assert response.success == True
        assert response.action == "send_vs_response"
        assert response.message == "Hello, user!"
        assert response.is_final == False
        assert response.execution_time_ms > 0
        assert response.error_message is None
        
        # Verify that log_heartbeat_event was called
        mock_log_event.assert_called_once()
        
        # Verify that forward_vscode_response was called
        mock_forward.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_invalid_task(self):
        """Test handling an invalid task."""
        # Create an invalid task request (missing required fields)
        task_data = {
            "task": [{
                "action": "send_vs_response"
                # Missing required fields
            }],
            "assigned_by": "ray"
        }
        
        # Call the handler
        response = await self.handler.handle_task(task_data)
        
        # Verify the response indicates failure
        assert isinstance(response, VSCodeLogicResponse)
        assert response.success == False
        assert response.action == "send_vs_response"
        assert response.message == ""
        assert response.is_final == False
        assert response.error_message is not None
    
    @pytest.mark.asyncio
    @patch('modules.vscode_logic.handler.log_heartbeat_event')
    async def test_handle_exception(self, mock_log_event):
        """Test handling an exception during processing."""
        # Create a task request that will cause an exception
        task_data = {
            # Missing 'task' field will cause an exception
            "assigned_by": "ray"
        }
        
        # Call the handler
        response = await self.handler.handle_task(task_data)
        
        # Verify the response indicates failure
        assert isinstance(response, VSCodeLogicResponse)
        assert response.success == False
        assert response.action == "unknown"
        assert response.message == ""
        assert response.is_final == False
        assert response.error_message is not None
        
        # Verify that log_heartbeat_event was called for the error
        mock_log_event.assert_called_once()