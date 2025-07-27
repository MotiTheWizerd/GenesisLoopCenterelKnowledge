"""
Tests for heartbeat routes.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_heartbeat_status():
    """Test the heartbeat status endpoint."""
    response = client.get("/heartbeat")
    assert response.status_code == 200
    
    data = response.json()
    assert data["type"] == "heartbeat"
    assert data["status"] == "alive"
    assert "timestamp" in data

def test_heartbeat_unknown_action():
    """Test heartbeat with unknown action."""
    request_data = {
        "action": "unknown_action"
    }
    
    response = client.post("/heartbeat", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "unknown_action"
    assert "error" in data

def test_heartbeat_reflect_redirect():
    """Test that reflect actions suggest using dedicated route."""
    request_data = {
        "action": "reflect",
        "question": "Test question"
    }
    
    response = client.post("/heartbeat", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "redirect_suggested"
    assert data["redirect_to"] == "/reflect"