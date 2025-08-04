"""
Tests for directory search routes.
"""

import pytest
import os
import tempfile
import shutil
from modules.directory.models import SearchType, DirectorySearchRequest
from modules.directory.handler import directory_manager

class TestDirectoryRoutes:
    """Test directory search API routes."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        
        # Create test structure
        os.makedirs(os.path.join(temp_dir, "subdir1"))
        os.makedirs(os.path.join(temp_dir, "subdir2"))
        
        # Create test files
        test_files = [
            "test1.py",
            "test2.txt", 
            "test3.md",
            "subdir1/nested_file.py",
            "subdir2/another_file.md"
        ]
        
        for file_path in test_files:
            full_path = os.path.join(temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(f"Content of {file_path}\nThis contains consciousness keyword.")
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_directory_search_request_processing(self, temp_dir):
        """Test directory search request processing through handler."""
        request = DirectorySearchRequest(
            search_type=SearchType.LIST_DIRECTORY,
            path=temp_dir,
            assigned_by="ray"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        assert response.search_result.search_type == SearchType.LIST_DIRECTORY
        assert response.search_result.total_results > 0
        assert response.assigned_by == "ray"
    
    def test_find_files_request_processing(self, temp_dir):
        """Test finding files through handler."""
        request = DirectorySearchRequest(
            search_type=SearchType.FIND_FILES,
            path=temp_dir,
            query="*.py",
            recursive=True,
            assigned_by="ray"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        assert len(response.search_result.files_found) >= 2  # test1.py and nested_file.py
        
        for file_info in response.search_result.files_found:
            assert file_info.name.endswith('.py')
    
    def test_content_search_request_processing(self, temp_dir):
        """Test content search through handler."""
        request = DirectorySearchRequest(
            search_type=SearchType.SEARCH_CONTENT,
            path=temp_dir,
            query="consciousness",
            recursive=True,
            assigned_by="ray"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        assert len(response.search_result.files_found) >= 3  # All test files contain the keyword
    
    def test_search_history_functionality(self, temp_dir):
        """Test search history tracking."""
        initial_count = len(directory_manager.get_search_history())
        
        request = DirectorySearchRequest(
            search_type=SearchType.LIST_DIRECTORY,
            path=temp_dir,
            assigned_by="ray"
        )
        
        directory_manager.search_directory(request)
        
        history = directory_manager.get_search_history()
        assert len(history) == initial_count + 1
        assert history[-1].search_type == SearchType.LIST_DIRECTORY
    
    def test_error_handling(self):
        """Test error handling for invalid paths."""
        request = DirectorySearchRequest(
            search_type=SearchType.LIST_DIRECTORY,
            path="/nonexistent/path",
            assigned_by="ray"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is False
        assert response.search_result.error_message is not None
        assert "not exist" in response.search_result.error_message.lower()
    
    def test_response_structure_completeness(self, temp_dir):
        """Test that response contains all expected fields."""
        request = DirectorySearchRequest(
            search_type=SearchType.LIST_DIRECTORY,
            path=temp_dir,
            assigned_by="ray"
        )
        
        response = directory_manager.search_directory(request)
        
        # Check response structure
        assert hasattr(response, 'search_result')
        assert hasattr(response, 'assigned_by')
        assert hasattr(response, 'current_path')
        assert hasattr(response, 'summary')
        assert hasattr(response, 'suggested_paths')
        
        # Check search result structure
        result = response.search_result
        assert hasattr(result, 'search_id')
        assert hasattr(result, 'search_type')
        assert hasattr(result, 'timestamp')
        assert hasattr(result, 'execution_time_ms')
        
        # Check summary content
        summary = response.summary
        assert 'total_files' in summary
        assert 'total_directories' in summary
        assert 'success' in summary
        assert 'execution_time_ms' in summary


class TestReadFileRoutes:
    """Test read_file API route functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory with test files for reading."""
        temp_dir = tempfile.mkdtemp()
        
        # Create test files
        test_files = {
            "simple.txt": "Hello World!\nThis is a test file.\nLine 3 content.",
            "config.json": '{\n  "version": "1.0",\n  "debug": true\n}',
            "empty.txt": "",
            "unicode.txt": "Unicode: 🌟 Ray's test 🧠"
        }
        
        for filename, content in test_files.items():
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_read_file_request_processing(self, temp_dir):
        """Test read_file request processing through handler."""
        from modules.directory.models import DirectorySearchRequest, ActionType
        
        file_path = os.path.join(temp_dir, "simple.txt")
        request = DirectorySearchRequest(
            action=ActionType.READ_FILE,
            path=file_path,
            assigned_by="ray"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        assert response.search_result.action == ActionType.READ_FILE
        assert len(response.search_result.files_found) == 1
        
        file_info = response.search_result.files_found[0]
        assert file_info.name == "simple.txt"
        assert file_info.content == "Hello World!\nThis is a test file.\nLine 3 content."
        assert file_info.lines_count == 3
        assert file_info.is_binary is False
    
    def test_read_file_with_query_parameters(self, temp_dir):
        """Test read_file with JSON query parameters."""
        from modules.directory.models import DirectorySearchRequest, ActionType
        import json
        
        query_params = {
            "file_path": os.path.join(temp_dir, "config.json"),
            "encoding": "utf-8",
            "max_size": 1024
        }
        
        request = DirectorySearchRequest(
            action=ActionType.READ_FILE,
            path=".",
            query=json.dumps(query_params),
            assigned_by="ray"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        file_info = response.search_result.files_found[0]
        assert file_info.name == "config.json"
        assert '"version": "1.0"' in file_info.content
        assert file_info.encoding_used == "utf-8"
    
    def test_read_file_error_handling(self, temp_dir):
        """Test read_file error handling for invalid files."""
        from modules.directory.models import DirectorySearchRequest, ActionType
        
        # Test nonexistent file
        nonexistent_path = os.path.join(temp_dir, "nonexistent.txt")
        request = DirectorySearchRequest(
            action=ActionType.READ_FILE,
            path=nonexistent_path,
            assigned_by="ray"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is False
        assert "does not exist" in response.search_result.error_message.lower()
    
    def test_read_file_response_structure(self, temp_dir):
        """Test that read_file response has correct structure."""
        from modules.directory.models import DirectorySearchRequest, ActionType
        
        file_path = os.path.join(temp_dir, "simple.txt")
        request = DirectorySearchRequest(
            action=ActionType.READ_FILE,
            path=file_path,
            assigned_by="ray"
        )
        
        response = directory_manager.search_directory(request)
        
        # Check response structure
        assert hasattr(response, 'search_result')
        assert hasattr(response, 'assigned_by')
        assert response.assigned_by == "ray"
        
        # Check search result structure
        result = response.search_result
        assert hasattr(result, 'search_id')
        assert hasattr(result, 'action')
        assert hasattr(result, 'timestamp')
        assert hasattr(result, 'execution_time_ms')
        assert hasattr(result, 'success')
        assert result.action == ActionType.READ_FILE
        
        # Check file info structure
        file_info = result.files_found[0]
        assert hasattr(file_info, 'content')
        assert hasattr(file_info, 'lines_count')
        assert hasattr(file_info, 'is_binary')
        assert hasattr(file_info, 'encoding_used')
    
    def test_read_empty_file_handling(self, temp_dir):
        """Test reading empty files."""
        from modules.directory.models import DirectorySearchRequest, ActionType
        
        file_path = os.path.join(temp_dir, "empty.txt")
        request = DirectorySearchRequest(
            action=ActionType.READ_FILE,
            path=file_path,
            assigned_by="ray"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        file_info = response.search_result.files_found[0]
        assert file_info.content == ""
        assert file_info.lines_count == 0
        assert file_info.size == 0
    
    def test_read_unicode_file_handling(self, temp_dir):
        """Test reading files with Unicode content."""
        from modules.directory.models import DirectorySearchRequest, ActionType
        
        file_path = os.path.join(temp_dir, "unicode.txt")
        request = DirectorySearchRequest(
            action=ActionType.READ_FILE,
            path=file_path,
            assigned_by="ray"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        file_info = response.search_result.files_found[0]
        assert "🌟" in file_info.content
        assert "🧠" in file_info.content
        assert file_info.is_binary is False