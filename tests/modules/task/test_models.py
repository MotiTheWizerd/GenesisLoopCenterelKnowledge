"""
Tests for task models.
"""

import pytest
from datetime import datetime, timezone
from uuid import UUID

from modules.task.models import (
    TaskRequestFromRay,
    TaskRequest,
    TaskResponse,
    TaskStatus,
    TaskType,
    TaskLog,
    TaskQueue
)


class TestTaskRequestFromRay:
    """Test TaskRequestFromRay model."""
    
    def test_create_basic_request(self):
        """Test creating a basic task request from Ray."""
        request = TaskRequestFromRay(
            task={"type": "reflect", "question": "test"},
            assigned_by="ray"
        )
        
        assert request.task == {"type": "reflect", "question": "test"}
        assert request.assigned_by == "ray"
    
    def test_create_empty_task(self):
        """Test creating request with empty task object."""
        request = TaskRequestFromRay(
            task={},
            assigned_by="ray"
        )
        
        assert request.task == {}
        assert request.assigned_by == "ray"
    
    def test_validation_missing_fields(self):
        """Test validation fails when required fields are missing."""
        with pytest.raises(ValueError):
            TaskRequestFromRay(task={})  # Missing assigned_by
        
        with pytest.raises(ValueError):
            TaskRequestFromRay(assigned_by="ray")  # Missing task


class TestTaskRequest:
    """Test TaskRequest model."""
    
    def test_create_complete_task(self):
        """Test creating a complete task with all fields."""
        task = TaskRequest(
            task={"type": "reflect", "question": "test"},
            assigned_by="ray"
        )
        
        # Check required fields
        assert task.task == {"type": "reflect", "question": "test"}
        assert task.assigned_by == "ray"
        
        # Check auto-generated fields
        assert task.task_id is not None
        assert len(task.task_id) > 0
        assert UUID(task.task_id)  # Should be valid UUID
        
        assert task.timestamp is not None
        assert len(task.timestamp) > 0
        # Should be valid ISO timestamp
        datetime.fromisoformat(task.timestamp.replace('Z', '+00:00'))
    
    def test_task_id_uniqueness(self):
        """Test that each task gets a unique ID."""
        task1 = TaskRequest(task={}, assigned_by="ray")
        task2 = TaskRequest(task={}, assigned_by="ray")
        
        assert task1.task_id != task2.task_id
    
    def test_timestamp_format(self):
        """Test that timestamp is in correct ISO format."""
        task = TaskRequest(task={}, assigned_by="ray")
        
        # Should be parseable as datetime
        parsed_time = datetime.fromisoformat(task.timestamp.replace('Z', '+00:00'))
        assert isinstance(parsed_time, datetime)
        assert parsed_time.tzinfo is not None


class TestTaskResponse:
    """Test TaskResponse model."""
    
    def test_create_basic_response(self):
        """Test creating a basic task response."""
        response = TaskResponse(
            task_id="test-id",
            status=TaskStatus.COMPLETED,
            assigned_by="ray",
            task={"type": "reflect"}
        )
        
        assert response.task_id == "test-id"
        assert response.status == TaskStatus.COMPLETED
        assert response.assigned_by == "ray"
        assert response.task == {"type": "reflect"}
        assert response.timestamp is not None
    
    def test_response_with_result(self):
        """Test response with execution results."""
        response = TaskResponse(
            task_id="test-id",
            status=TaskStatus.COMPLETED,
            assigned_by="ray",
            task={},
            result={"reflection": "test result"},
            processing_time_ms=150
        )
        
        assert response.result == {"reflection": "test result"}
        assert response.processing_time_ms == 150
    
    def test_response_with_error(self):
        """Test response with error information."""
        response = TaskResponse(
            task_id="test-id",
            status=TaskStatus.ERROR,
            assigned_by="ray",
            task={},
            error_message="Test error occurred"
        )
        
        assert response.status == TaskStatus.ERROR
        assert response.error_message == "Test error occurred"


class TestTaskStatus:
    """Test TaskStatus enum."""
    
    def test_all_status_values(self):
        """Test all status enum values."""
        assert TaskStatus.RECEIVED == "received"
        assert TaskStatus.PROCESSING == "processing"
        assert TaskStatus.COMPLETED == "completed"
        assert TaskStatus.ERROR == "error"
        assert TaskStatus.CANCELLED == "cancelled"


class TestTaskType:
    """Test TaskType enum."""
    
    def test_all_task_types(self):
        """Test all task type enum values."""
        assert TaskType.REFLECT == "reflect"
        assert TaskType.EVOLVE == "evolve"
        assert TaskType.CONNECT == "connect"
        assert TaskType.REMEMBER == "remember"
        assert TaskType.CARE == "care"
        assert TaskType.OBSERVE == "observe"
        assert TaskType.RESPOND == "respond"
        assert TaskType.GROW == "grow"


class TestTaskLog:
    """Test TaskLog model."""
    
    def test_create_log_entry(self):
        """Test creating a task log entry."""
        log = TaskLog(
            task_id="test-id",
            event="task_created",
            message="Task was created successfully"
        )
        
        assert log.task_id == "test-id"
        assert log.event == "task_created"
        assert log.message == "Task was created successfully"
        assert log.timestamp is not None
    
    def test_log_with_details(self):
        """Test log entry with additional details."""
        log = TaskLog(
            task_id="test-id",
            event="task_processed",
            details={"processing_time": 100, "result_size": 256}
        )
        
        assert log.details == {"processing_time": 100, "result_size": 256}


class TestTaskQueue:
    """Test TaskQueue model."""
    
    def test_create_empty_queue(self):
        """Test creating an empty task queue."""
        queue = TaskQueue()
        
        assert len(queue.tasks) == 0
        assert queue.current_task_index == 0
        assert queue.status == TaskStatus.RECEIVED
        assert queue.queue_id is not None
        assert queue.created_at is not None
    
    def test_queue_with_tasks(self):
        """Test queue with initial tasks."""
        task1 = TaskRequest(task={"type": "reflect"}, assigned_by="ray")
        task2 = TaskRequest(task={"type": "evolve"}, assigned_by="ray")
        
        queue = TaskQueue(tasks=[task1, task2])
        
        assert len(queue.tasks) == 2
        assert queue.tasks[0] == task1
        assert queue.tasks[1] == task2