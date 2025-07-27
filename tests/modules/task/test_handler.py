"""
Tests for task handler and TaskManager.
"""

import pytest
from unittest.mock import patch
from datetime import datetime, timezone

from modules.task.handler import TaskManager, task_manager
from modules.task.models import TaskRequestFromRay, TaskRequest, TaskStatus


class TestTaskManager:
    """Test TaskManager class."""
    
    def setup_method(self):
        """Set up test with fresh TaskManager instance."""
        self.manager = TaskManager()
    
    def test_initialization(self):
        """Test TaskManager initializes with empty lists."""
        assert len(self.manager.active_tasks) == 0
        assert len(self.manager.completed_tasks) == 0
    
    def test_create_task_basic(self):
        """Test creating a basic task."""
        ray_request = TaskRequestFromRay(
            task={"type": "reflect", "question": "test"},
            assigned_by="ray"
        )
        
        task = self.manager.create_task(ray_request)
        
        # Check task properties
        assert isinstance(task, TaskRequest)
        assert task.task == {"type": "reflect", "question": "test"}
        assert task.assigned_by == "ray"
        assert task.task_id is not None
        assert task.timestamp is not None
        
        # Check it was added to active tasks
        assert len(self.manager.active_tasks) == 1
        assert self.manager.active_tasks[0] == task
    
    def test_create_multiple_tasks(self):
        """Test creating multiple tasks."""
        ray_request1 = TaskRequestFromRay(task={"type": "reflect"}, assigned_by="ray")
        ray_request2 = TaskRequestFromRay(task={"type": "evolve"}, assigned_by="ray")
        
        task1 = self.manager.create_task(ray_request1)
        task2 = self.manager.create_task(ray_request2)
        
        # Check both tasks are in active list
        assert len(self.manager.active_tasks) == 2
        assert task1 in self.manager.active_tasks
        assert task2 in self.manager.active_tasks
        
        # Check unique IDs
        assert task1.task_id != task2.task_id
    
    def test_get_task_existing(self):
        """Test getting an existing task by ID."""
        ray_request = TaskRequestFromRay(task={}, assigned_by="ray")
        created_task = self.manager.create_task(ray_request)
        
        retrieved_task = self.manager.get_task(created_task.task_id)
        
        assert retrieved_task is not None
        assert retrieved_task == created_task
    
    def test_get_task_nonexistent(self):
        """Test getting a non-existent task returns None."""
        result = self.manager.get_task("nonexistent-id")
        assert result is None
    
    def test_get_all_active_tasks(self):
        """Test getting all active tasks."""
        # Create some tasks
        ray_request1 = TaskRequestFromRay(task={"type": "reflect"}, assigned_by="ray")
        ray_request2 = TaskRequestFromRay(task={"type": "evolve"}, assigned_by="system")
        
        task1 = self.manager.create_task(ray_request1)
        task2 = self.manager.create_task(ray_request2)
        
        all_tasks = self.manager.get_all_active_tasks()
        
        assert len(all_tasks) == 2
        assert task1 in all_tasks
        assert task2 in all_tasks
        
        # Should be a copy, not the original list
        assert all_tasks is not self.manager.active_tasks
    
    def test_get_tasks_by_assignee(self):
        """Test getting tasks filtered by assignee."""
        # Create tasks from different assignees
        ray_request = TaskRequestFromRay(task={"type": "reflect"}, assigned_by="ray")
        system_request = TaskRequestFromRay(task={"type": "evolve"}, assigned_by="system")
        
        ray_task = self.manager.create_task(ray_request)
        system_task = self.manager.create_task(system_request)
        
        # Get Ray's tasks
        ray_tasks = self.manager.get_tasks_by_assignee("ray")
        assert len(ray_tasks) == 1
        assert ray_tasks[0] == ray_task
        
        # Get system tasks
        system_tasks = self.manager.get_tasks_by_assignee("system")
        assert len(system_tasks) == 1
        assert system_tasks[0] == system_task
        
        # Get non-existent assignee
        empty_tasks = self.manager.get_tasks_by_assignee("nonexistent")
        assert len(empty_tasks) == 0
    
    def test_complete_task_existing(self):
        """Test completing an existing task."""
        ray_request = TaskRequestFromRay(task={"type": "reflect"}, assigned_by="ray")
        task = self.manager.create_task(ray_request)
        
        result = {"reflection": "completed successfully"}
        response = self.manager.complete_task(task.task_id, result)
        
        # Check response
        assert response is not None
        assert response.task_id == task.task_id
        assert response.status == TaskStatus.COMPLETED
        assert response.result == result
        assert response.assigned_by == "ray"
        
        # Check task moved from active to completed
        assert len(self.manager.active_tasks) == 0
        assert len(self.manager.completed_tasks) == 1
        assert self.manager.completed_tasks[0] == response
    
    def test_complete_task_nonexistent(self):
        """Test completing a non-existent task returns None."""
        response = self.manager.complete_task("nonexistent-id")
        assert response is None
    
    def test_get_status(self):
        """Test getting task manager status."""
        # Create some tasks
        ray_request1 = TaskRequestFromRay(task={}, assigned_by="ray")
        ray_request2 = TaskRequestFromRay(task={}, assigned_by="ray")
        
        task1 = self.manager.create_task(ray_request1)
        task2 = self.manager.create_task(ray_request2)
        
        # Complete one task
        self.manager.complete_task(task1.task_id)
        
        status = self.manager.get_status()
        
        assert status["active_tasks_count"] == 1
        assert status["completed_tasks_count"] == 1
        assert status["total_tasks_processed"] == 2


class TestGlobalTaskManager:
    """Test the global task manager instance."""
    
    def test_global_instance_exists(self):
        """Test that global task_manager instance exists."""
        assert task_manager is not None
        assert isinstance(task_manager, TaskManager)
    
    def test_global_instance_initialized(self):
        """Test that global instance is properly initialized."""
        # Note: This test might be affected by other tests that use the global instance
        assert hasattr(task_manager, 'active_tasks')
        assert hasattr(task_manager, 'completed_tasks')
        assert isinstance(task_manager.active_tasks, list)
        assert isinstance(task_manager.completed_tasks, list)


class TestTaskManagerIntegration:
    """Integration tests for TaskManager."""
    
    def setup_method(self):
        """Set up test with fresh TaskManager instance."""
        self.manager = TaskManager()
    
    def test_full_task_lifecycle(self):
        """Test complete task lifecycle from creation to completion."""
        # Create task
        ray_request = TaskRequestFromRay(
            task={"type": "reflect", "question": "What is consciousness?"},
            assigned_by="ray"
        )
        
        task = self.manager.create_task(ray_request)
        
        # Verify task is active
        assert len(self.manager.active_tasks) == 1
        assert len(self.manager.completed_tasks) == 0
        
        # Get task by ID
        retrieved_task = self.manager.get_task(task.task_id)
        assert retrieved_task == task
        
        # Complete task
        result = {"reflection": "Consciousness is the state of being aware"}
        response = self.manager.complete_task(task.task_id, result)
        
        # Verify task is completed
        assert len(self.manager.active_tasks) == 0
        assert len(self.manager.completed_tasks) == 1
        assert response.result == result
        
        # Verify task no longer retrievable from active tasks
        assert self.manager.get_task(task.task_id) is None
    
    def test_multiple_assignees_workflow(self):
        """Test workflow with multiple task assignees."""
        # Create tasks from different assignees
        ray_request = TaskRequestFromRay(task={"type": "reflect"}, assigned_by="ray")
        system_request = TaskRequestFromRay(task={"type": "monitor"}, assigned_by="system")
        user_request = TaskRequestFromRay(task={"type": "respond"}, assigned_by="user")
        
        ray_task = self.manager.create_task(ray_request)
        system_task = self.manager.create_task(system_request)
        user_task = self.manager.create_task(user_request)
        
        # Verify all tasks are active
        assert len(self.manager.active_tasks) == 3
        
        # Get tasks by assignee
        ray_tasks = self.manager.get_tasks_by_assignee("ray")
        system_tasks = self.manager.get_tasks_by_assignee("system")
        user_tasks = self.manager.get_tasks_by_assignee("user")
        
        assert len(ray_tasks) == 1
        assert len(system_tasks) == 1
        assert len(user_tasks) == 1
        
        # Complete Ray's task
        self.manager.complete_task(ray_task.task_id)
        
        # Verify counts
        assert len(self.manager.active_tasks) == 2
        assert len(self.manager.completed_tasks) == 1
        
        # Verify remaining active tasks
        remaining_ray_tasks = self.manager.get_tasks_by_assignee("ray")
        remaining_system_tasks = self.manager.get_tasks_by_assignee("system")
        remaining_user_tasks = self.manager.get_tasks_by_assignee("user")
        
        assert len(remaining_ray_tasks) == 0
        assert len(remaining_system_tasks) == 1
        assert len(remaining_user_tasks) == 1