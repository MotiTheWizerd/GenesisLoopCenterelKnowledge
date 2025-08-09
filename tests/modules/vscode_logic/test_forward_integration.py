"""Tests for VSCode Logic module integration with forward_vscode_response function."""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from modules.vscode_logic.handler import VSCodeLogicHandler
from modules.vscode_logic.models import VSCodeLogicResponse, VSCodeTaskRequest


class TestVSCodeForwardIntegration:
    def setup_method(self):
        self.handler = VSCodeLogicHandler()
    
    @pytest.mark.asyncio
    @patch('modules.vscode_logic.handler.forward_vscode_response')
    @patch('modules.vscode_logic.handler.log_heartbeat_event')
    async def test_forward_vscode_response_integration(self, mock_log_event, mock_forward):
        """Test that the handler correctly calls forward_vscode_response."""
        # Setup mock to return a successful response
        mock_forward.return_value = {"status": "forwarded", "external_status": 200}
        
        # Create a sample task request
        task_data = {
            "task": [{
                "action": "send_vs_response",
                "message": "Hello, user!",
                "ray_prompt": "This is reasoning for next round",
                "is_final": False,
                "timestamp": datetime.now(timezone.utc).isoformat(),
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
        
        # Verify that forward_vscode_response was called with the correct data
        mock_forward.assert_called_once()
        call_args = mock_forward.call_args[0][0]
        assert call_args["message"] == "Hello, user!"
        assert call_args["ray_prompt"] == "This is reasoning for next round"
        assert call_args["is_final"] == False
        assert "timestamp" in call_args
        assert call_args["additional_data"] == {"nested": "structure", "works": True}
        
        # Verify that log_heartbeat_event was called
        mock_log_event.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('modules.vscode_logic.handler.forward_vscode_response')
    async def test_forward_vscode_response_exception(self, mock_forward):
        """Test handling an exception during forward_vscode_response."""
        # Setup mock to raise an exception
        mock_forward.side_effect = Exception("Connection error")
        
        # Create a sample task request
        task_data = {
            "task": [{
                "action": "send_vs_response",
                "message": "Hello, user!",
                "ray_prompt": "This is reasoning for next round",
                "is_final": False
            }],
            "assigned_by": "ray",
            "execute_immediately": True
        }
        
        # Call the handler
        response = await self.handler.handle_task(task_data)
        
        # Verify the response indicates failure
        assert isinstance(response, VSCodeLogicResponse)
        assert response.success == False
        assert response.action == "send_vs_response"
        assert response.message == ""
        assert response.is_final == False
        assert "Connection error" in response.error_message
        
        # Verify that forward_vscode_response was called
        mock_forward.assert_called_once()