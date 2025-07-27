"""
Tests for task routes.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from main import app
from modules.task.models import TaskRequestFromRay, TaskRequest, TaskStatus
from modules.task.handler import TaskManager


client = TestClient(app)


class TestTaskRoutes:
    """Test task API routes."""
    
    def setup_method(self):
        """Set up test with fresh task manager."""
        # Create a fresh task manager for each test
        self.mock_manager = TaskManager()
        
    @patch('modules.routes.task_routes.task_manager')
    def test_create_task_success(self, mock_task_manager):
        """Test successful task creation."""
        # Mock the task manager
        mock_task_manager.create_task.return_value = TaskRequest(
            task_id="test-task-id",
            task={"type": "reflect", "question": "test"},
            assigned_by="ray",
            timestamp="2024-01-01T00:00:00Z"
        )
        
        # Make request
        response = client.post("/task", json={
            "task": {"type": "reflect", "question": "test"},
            "assigned_by": "ray"
        })
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "task_created"
        assert data["task_id"] == "test-task-id"
        assert data["assigned_by"] == "ray"
        assert data["task"] == {"type": "reflect", "question": "test"}
        assert "timestamp" in data
        assert "message" in data
        
        # Verify task manager was called
        mock_task_manager.create_task.assert_called_once()
    
    def test_create_task_invalid_data(self):
        """Test task creation with invalid data."""
        # Missing required field
        response = client.post("/task", json={
            "task": {"type": "reflect"}
            # Missing assigned_by
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_create_task_empty_request(self):
        """Test task creation with empty request."""
        response = client.post("/task", json={})
        
        assert response.status_code == 422  # Validation error
    
    @patch('modules.routes.task_routes.task_manager')
    def test_create_task_server_error(self, mock_task_manager):
        """Test task creation with server error."""
        # Mock task manager to raise exception
        mock_task_manager.create_task.side_effect = Exception("Database error")
        
        response = client.post("/task", json={
            "task": {},
            "assigned_by": "ray"
        })
        
        assert response.status_code == 500
        data = response.json()
        assert "Failed to create task" in data["detail"]
    
    @patch('modules.routes.task_routes.task_manager')
    def test_get_active_tasks_success(self, mock_task_manager):
        """Test getting active tasks list."""
        # Mock active tasks
        mock_tasks = [
            TaskRequest(
                task_id="task-1",
                task={"type": "reflect"},
                assigned_by="ray",
                timestamp="2024-01-01T00:00:00Z"
            ),
            TaskRequest(
                task_id="task-2", 
                task={"type": "evolve"},
                assigned_by="system",
                timestamp="2024-01-01T00:01:00Z"
            )
        ]
        mock_task_manager.get_all_active_tasks.return_value = mock_tasks
        
        response = client.get("/task/list")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["active_tasks_count"] == 2
        assert len(data["active_tasks"]) == 2
        assert "timestamp" in data
        
        # Check task data
        task1 = data["active_tasks"][0]
        assert task1["task_id"] == "task-1"
        assert task1["assigned_by"] == "ray"
    
    @patch('modules.routes.task_routes.task_manager')
    def test_get_active_tasks_empty(self, mock_task_manager):
        """Test getting active tasks when list is empty."""
        mock_task_manager.get_all_active_tasks.return_value = []
        
        response = client.get("/task/list")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["active_tasks_count"] == 0
        assert len(data["active_tasks"]) == 0
    
    @patch('modules.routes.task_routes.task_manager')
    def test_get_active_tasks_error(self, mock_task_manager):
        """Test getting active tasks with server error."""
        mock_task_manager.get_all_active_tasks.side_effect = Exception("Database error")
        
        response = client.get("/task/list")
        
        assert response.status_code == 500
        data = response.json()
        assert "Failed to get task list" in data["detail"]
    
    @patch('modules.routes.task_routes.task_manager')
    def test_get_task_by_id_success(self, mock_task_manager):
        """Test getting a specific task by ID."""
        mock_task = TaskRequest(
            task_id="test-task-id",
            task={"type": "reflect", "question": "test"},
            assigned_by="ray",
            timestamp="2024-01-01T00:00:00Z"
        )
        mock_task_manager.get_task.return_value = mock_task
        
        response = client.get("/task/test-task-id")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["task"]["task_id"] == "test-task-id"
        assert data["task"]["assigned_by"] == "ray"
        assert "timestamp" in data
    
    @patch('modules.routes.task_routes.task_manager')
    def test_get_task_by_id_not_found(self, mock_task_manager):
        """Test getting a non-existent task."""
        mock_task_manager.get_task.return_value = None
        
        response = client.get("/task/nonexistent-id")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    @patch('modules.routes.task_routes.task_manager')
    def test_get_task_by_id_error(self, mock_task_manager):
        """Test getting task with server error."""
        mock_task_manager.get_task.side_effect = Exception("Database error")
        
        response = client.get("/task/test-id")
        
        assert response.status_code == 500
        data = response.json()
        assert "Failed to get task" in data["detail"]
    
    @patch('modules.routes.task_routes.task_manager')
    def test_get_task_manager_status_success(self, mock_task_manager):
        """Test getting task manager status."""
        mock_status = {
            "active_tasks_count": 3,
            "completed_tasks_count": 7,
            "total_tasks_processed": 10
        }
        mock_task_manager.get_status.return_value = mock_status
        
        response = client.get("/task/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "operational"
        assert data["task_manager"] == mock_status
        assert "timestamp" in data
    
    @patch('modules.routes.task_routes.task_manager')
    def test_get_task_manager_status_error(self, mock_task_manager):
        """Test getting task manager status with error."""
        mock_task_manager.get_status.side_effect = Exception("Status error")
        
        response = client.get("/task/status")
        
        assert response.status_code == 500
        data = response.json()
        assert "Failed to get status" in data["detail"]


class TestTaskRoutesIntegration:
    """Integration tests for task routes."""
    
    def test_create_and_retrieve_task_flow(self):
        """Test complete flow of creating and retrieving a task."""
        # Create a task
        create_response = client.post("/task", json={
            "task": {"type": "reflect", "question": "What is consciousness?"},
            "assigned_by": "ray"
        })
        
        assert create_response.status_code == 200
        create_data = create_response.json()
        task_id = create_data["task_id"]
        
        # Retrieve the task
        get_response = client.get(f"/task/{task_id}")
        
        assert get_response.status_code == 200
        get_data = get_response.json()
        
        assert get_data["task"]["task_id"] == task_id
        assert get_data["task"]["assigned_by"] == "ray"
        assert get_data["task"]["task"]["type"] == "reflect"
        assert get_data["task"]["task"]["question"] == "What is consciousness?"
    
    def test_create_multiple_tasks_and_list(self):
        """Test creating multiple tasks and listing them."""
        # Create first task
        response1 = client.post("/task", json={
            "task": {"type": "reflect"},
            "assigned_by": "ray"
        })
        assert response1.status_code == 200
        
        # Create second task
        response2 = client.post("/task", json={
            "task": {"type": "evolve"},
            "assigned_by": "system"
        })
        assert response2.status_code == 200
        
        # List all tasks
        list_response = client.get("/task/list")
        assert list_response.status_code == 200
        
        list_data = list_response.json()
        assert list_data["active_tasks_count"] >= 2  # May have tasks from other tests
        
        # Check that our tasks are in the list
        task_types = [task["task"]["type"] for task in list_data["active_tasks"]]
        assert "reflect" in task_types
        assert "evolve" in task_types
    
    def test_task_manager_status_reflects_operations(self):
        """Test that task manager status reflects actual operations."""
        # Get initial status
        initial_response = client.get("/task/status")
        assert initial_response.status_code == 200
        initial_data = initial_response.json()
        initial_count = initial_data["task_manager"]["active_tasks_count"]
        
        # Create a task
        create_response = client.post("/task", json={
            "task": {"type": "test"},
            "assigned_by": "ray"
        })
        assert create_response.status_code == 200
        
        # Check status again
        final_response = client.get("/task/status")
        assert final_response.status_code == 200
        final_data = final_response.json()
        final_count = final_data["task_manager"]["active_tasks_count"]
        
        # Should have one more active task
        assert final_count == initial_count + 1