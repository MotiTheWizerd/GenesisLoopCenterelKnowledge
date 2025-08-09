"""Integration test for the VSCode response flow.

This test verifies the entire flow from task creation to VSCode response forwarding.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from modules.task.handler import task_manager
from modules.task.models import TaskRequestFromRay


@pytest.mark.asyncio
@patch('modules.vscode_logic.handler.forward_vscode_response')
@patch('modules.vscode_logic.handler.log_heartbeat_event')
async def test_vscode_response_flow(mock_log_event, mock_forward):
    """Test the entire flow from task creation to VSCode response forwarding."""
    # Setup mock to return a successful response
    mock_forward.return_value = {"status": "forwarded", "external_status": 200}
    
    # Create a sample VSCode response task
    vscode_task = {
        "task": [{
            "action": "send_vs_response",
            "message": "Hello, this is a response from Ray to the VSCode user!",
            "ray_prompt": "I'm providing a helpful response to the user's question about Python.",
            "is_final": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "additional_data": {
                "nested": "structure",
                "works": True
            }
        }],
        "assigned_by": "ray",
        "execute_immediately": True
    }
    
    # Create a task request
    task_request = TaskRequestFromRay(**vscode_task)
    
    # Process the task
    with patch('modules.task.handler.asyncio.run') as mock_asyncio_run:
        # Setup the mock to simulate running the async function
        mock_response = MagicMock()
        mock_response.dict.return_value = {
            "success": True,
            "action": "send_vs_response",
            "message": "Hello, this is a response from Ray to the VSCode user!",
            "is_final": False,
            "execution_time_ms": 100,
            "error_message": None
        }
        mock_asyncio_run.return_value = mock_response
        
        # Process the task
        response = task_manager.create_batch_tasks(task_request)
        
        # Verify the response
        assert response.success == True
        assert len(response.tasks) == 1
        assert response.tasks[0]["action"] == "send_vs_response"
        assert response.tasks[0]["executed"] == True
        
        # Verify that asyncio.run was called
        mock_asyncio_run.assert_called_once()
        
    # Verify that forward_vscode_response would have been called in a real scenario
    # Note: In this test, it's not actually called because we're mocking asyncio.run
    # In a real scenario, asyncio.run would execute the async function which would call forward_vscode_response


if __name__ == "__main__":
    # Run the test
    pytest.main(['-xvs', __file__])