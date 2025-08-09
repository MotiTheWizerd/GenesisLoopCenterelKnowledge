"""Tests for the coding_routes module."""

import pytest
from unittest.mock import patch, MagicMock
import json

from modules.routes.coding_routes import forward_vscode_response


@pytest.mark.asyncio
async def test_forward_vscode_response_success():
    """Test that forward_vscode_response correctly forwards data to the VSCode extension."""
    # Create a sample request data
    request_data = {
        "action": "send_vs_response",
        "message": "Hello, user!",
        "ray_prompt": "This is reasoning for next round",
        "is_final": False,
        "additional_data": {"nested": "structure", "works": True}
    }
    
    # Mock the httpx.AsyncClient
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    
    with patch('modules.routes.coding_routes.httpx.AsyncClient') as mock_client:
        # Setup the mock client
        mock_client_instance = MagicMock()
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        mock_client_instance.post.return_value = mock_response
        
        # Call the function
        result = await forward_vscode_response(request_data)
        
        # Verify the result
        assert result["status"] == "forwarded"
        assert result["external_status"] == 200
        
        # Verify that the client was called with the correct data
        mock_client_instance.post.assert_called_once_with(
            "http://localhost:3001/ray-response",
            json=request_data
        )


@pytest.mark.asyncio
async def test_forward_vscode_response_error():
    """Test that forward_vscode_response correctly handles errors."""
    # Create a sample request data
    request_data = {
        "action": "send_vs_response",
        "message": "Hello, user!",
        "ray_prompt": "This is reasoning for next round",
        "is_final": False
    }
    
    # Mock the httpx.AsyncClient to raise an exception
    with patch('modules.routes.coding_routes.httpx.AsyncClient') as mock_client:
        # Setup the mock client to raise an exception
        mock_client_instance = MagicMock()
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        mock_client_instance.post.side_effect = Exception("Connection error")
        
        # Call the function
        result = await forward_vscode_response(request_data)
        
        # Verify the result
        assert result["status"] == "error"
        assert "Connection error" in result["error"]


@pytest.mark.asyncio
async def test_forward_vscode_response_external_error():
    """Test that forward_vscode_response correctly handles external errors."""
    # Create a sample request data
    request_data = {
        "action": "send_vs_response",
        "message": "Hello, user!",
        "ray_prompt": "This is reasoning for next round",
        "is_final": False
    }
    
    # Mock the httpx.AsyncClient to return an error status code
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal server error"
    
    with patch('modules.routes.coding_routes.httpx.AsyncClient') as mock_client:
        # Setup the mock client
        mock_client_instance = MagicMock()
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        mock_client_instance.post.return_value = mock_response
        
        # Call the function
        result = await forward_vscode_response(request_data)
        
        # Verify the result
        assert result["status"] == "error"
        assert result["external_status"] == 500
        assert "Internal server error" in result["error"]