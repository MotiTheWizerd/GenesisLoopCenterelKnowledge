"""
Tests for file operations handler.
"""

import os
import tempfile
import pytest
from unittest.mock import patch

from modules.file_ops.handler import FileOperationsHandler
from modules.file_ops.models import FileOperation


class TestFileOperationsHandler:
    """Test cases for FileOperationsHandler."""
    
    def setup_method(self):
        """Set up test environment."""
        self.handler = FileOperationsHandler()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_overwrite_file_new_file(self):
        """Test overwriting a file that doesn't exist (creates new file)."""
        test_file = os.path.join(self.temp_dir, "test_new.txt")
        test_content = "This is new content for testing"
        
        task_data = {
            "task": {
                "action": "overwrite_file",
                "file_path": test_file,
                "content": test_content
            },
            "assigned_by": "test"
        }
        
        response = self.handler.handle_task(task_data)
        
        assert response.success is True
        assert response.operation == FileOperation.OVERWRITE
        assert response.file_path == test_file
        assert response.file_size == len(test_content)
        assert os.path.exists(test_file)
        
        # Verify content
        with open(test_file, 'r') as f:
            assert f.read() == test_content
    
    def test_overwrite_file_existing_file(self):
        """Test overwriting an existing file."""
        test_file = os.path.join(self.temp_dir, "test_existing.txt")
        original_content = "Original content"
        new_content = "New overwritten content"
        
        # Create original file
        with open(test_file, 'w') as f:
            f.write(original_content)
        
        task_data = {
            "task": {
                "action": "overwrite_file",
                "file_path": test_file,
                "content": new_content
            },
            "assigned_by": "test"
        }
        
        response = self.handler.handle_task(task_data)
        
        assert response.success is True
        assert response.operation == FileOperation.OVERWRITE
        assert response.file_size == len(new_content)
        
        # Verify content was overwritten
        with open(test_file, 'r') as f:
            assert f.read() == new_content
    
    def test_overwrite_file_with_backup(self):
        """Test overwriting a file with backup creation."""
        test_file = os.path.join(self.temp_dir, "test_backup.txt")
        original_content = "Original content to backup"
        new_content = "New content after backup"
        
        # Create original file
        with open(test_file, 'w') as f:
            f.write(original_content)
        
        task_data = {
            "task": {
                "action": "overwrite_file",
                "file_path": test_file,
                "content": new_content,
                "backup_existing": True
            },
            "assigned_by": "test"
        }
        
        response = self.handler.handle_task(task_data)
        
        assert response.success is True
        assert response.backup_path is not None
        assert os.path.exists(response.backup_path)
        
        # Verify original content is in backup
        with open(response.backup_path, 'r') as f:
            assert f.read() == original_content
        
        # Verify new content is in main file
        with open(test_file, 'r') as f:
            assert f.read() == new_content
    
    def test_overwrite_file_create_directories(self):
        """Test overwriting a file with directory creation."""
        nested_dir = os.path.join(self.temp_dir, "nested", "deep", "path")
        test_file = os.path.join(nested_dir, "test.txt")
        test_content = "Content in nested directory"
        
        task_data = {
            "task": {
                "action": "overwrite_file",
                "file_path": test_file,
                "content": test_content,
                "create_directories": True
            },
            "assigned_by": "test"
        }
        
        response = self.handler.handle_task(task_data)
        
        assert response.success is True
        assert os.path.exists(nested_dir)
        assert os.path.exists(test_file)
        
        # Verify content
        with open(test_file, 'r') as f:
            assert f.read() == test_content
    
    def test_read_file_success(self):
        """Test reading a file successfully."""
        test_file = os.path.join(self.temp_dir, "test_read.txt")
        test_content = "Content to read from file"
        
        # Create test file
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        task_data = {
            "task": {
                "action": "read_file",
                "file_path": test_file
            },
            "assigned_by": "test"
        }
        
        response = self.handler.handle_task(task_data)
        
        assert response.success is True
        assert response.content == test_content
        assert response.file_size == len(test_content)
        assert response.file_path == test_file
    
    def test_read_file_not_found(self):
        """Test reading a file that doesn't exist."""
        test_file = os.path.join(self.temp_dir, "nonexistent.txt")
        
        task_data = {
            "task": {
                "action": "read_file",
                "file_path": test_file
            },
            "assigned_by": "test"
        }
        
        response = self.handler.handle_task(task_data)
        
        assert response.success is False
        assert response.content is None
        assert "File not found" in response.error_message
    
    def test_convenience_methods(self):
        """Test convenience methods for file operations."""
        test_file = os.path.join(self.temp_dir, "convenience_test.txt")
        test_content = "Content via convenience method"
        
        # Test overwrite_file convenience method
        response = self.handler.overwrite_file(
            file_path=test_file,
            content=test_content,
            assigned_by="test"
        )
        
        assert response.success is True
        assert os.path.exists(test_file)
        
        # Test read_file convenience method
        read_response = self.handler.read_file(
            file_path=test_file,
            assigned_by="test"
        )
        
        assert read_response.success is True
        assert read_response.content == test_content
    
    def test_handler_status(self):
        """Test getting handler status."""
        status = self.handler.get_status()
        
        assert "total_operations" in status
        assert "handler_status" in status
        assert status["handler_status"] == "active"
    
    @patch('modules.file_ops.handler.log_heartbeat_event')
    def test_logging_integration(self, mock_log):
        """Test that operations are properly logged."""
        test_file = os.path.join(self.temp_dir, "log_test.txt")
        test_content = "Content for logging test"
        
        task_data = {
            "task": {
                "action": "overwrite_file",
                "file_path": test_file,
                "content": test_content
            },
            "assigned_by": "test"
        }
        
        response = self.handler.handle_task(task_data)
        
        assert response.success is True
        # Verify logging was called
        assert mock_log.called