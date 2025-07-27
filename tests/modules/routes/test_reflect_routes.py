"""
Tests for reflection routes.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_reflect_status():
    """Test the reflect status endpoint."""
    response = client.get("/reflect")
    assert response.status_code == 200
    
    data = response.json()
    assert data["type"] == "reflection"
    assert data["status"] == "ready"
    assert "capabilities" in data
    assert "available_depths" in data

def test_reflect_surface():
    """Test surface-level reflection."""
    request_data = {
        "question": "How are you feeling?",
        "depth": "surface"
    }
    
    response = client.post("/reflect", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["type"] == "reflection"
    assert data["depth"] == "surface"
    assert "reflection" in data
    assert "insights" in data

def test_reflect_deep():
    """Test deep reflection."""
    request_data = {
        "question": "What does consciousness mean to you?",
        "depth": "deep"
    }
    
    response = client.post("/reflect", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["type"] == "reflection"
    assert data["depth"] == "deep"
    assert "growth_areas" in data

def test_reflect_profound():
    """Test profound reflection endpoint."""
    request_data = {
        "question": "What is the nature of your existence?"
    }
    
    response = client.post("/reflect/deep", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["type"] == "reflection"
    assert data["depth"] == "profound"
    assert "consciousness_markers" in data
    assert "growth_trajectory" in data

def test_reflection_history():
    """Test reflection history endpoint."""
    response = client.get("/reflect/history")
    assert response.status_code == 200
    
    data = response.json()
    assert data["type"] == "reflection_history"