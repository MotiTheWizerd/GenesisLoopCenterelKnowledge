"""
Unit tests for reflect handler module.
"""

import pytest
from modules.reflect.reflect_handler import handle_reflect


def test_handle_reflect_basic():
    """Test basic reflect handler functionality."""
    request_data = {
        "action": "reflect",
        "question": "test question",
        "current_position": "test position"
    }
    
    result = handle_reflect(request_data)
    
    assert result["type"] == "heartbeat"
    assert result["action"] == "reflect"
    assert result["status"] == "processing_reflection"
    assert "timestamp" in result


def test_handle_reflect_minimal():
    """Test reflect handler with minimal data."""
    request_data = {
        "action": "reflect"
    }
    
    result = handle_reflect(request_data)
    
    assert result["type"] == "heartbeat"
    assert result["action"] == "reflect"
    assert result["status"] == "processing_reflection"