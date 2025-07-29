"""
Tests for directory search handler.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from modules.directory.handler import DirectoryManager
from modules.directory.models import (
    DirectorySearchRequest,
    SearchType
)


class TestDirectoryManager:
    """Test DirectoryManager functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        
        # Create test structure
        os.makedirs(os.path.join(temp_dir, "subdir1"))
        os.makedirs(os.path.join(temp_dir, "subdir2"))
        os.makedirs(os.path.join(temp_dir, "subdir1", "nested"))
        
        # Create test files
        test_files = [
            "test1.py",
            "test2.txt", 
            "test3.md",
            "subdir1/nested_file.py",
            "subdir1/nested/deep_file.txt",
            "subdir2/another_file.md"
        ]
        
        for file_path in test_files:
            full_path = os.path.join(temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(f"Content of {file_path}\nThis contains consciousness keyword for testing.")
        
        # Create hidden file
        with open(os.path.join(temp_dir, ".hidden_file"), 'w') as f:
            f.write("Hidden content")
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def directory_manager(self):
        """Create a DirectoryManager instance."""
        return DirectoryManager()
    
    def test_manager_initialization(self, directory_manager):
        """Test DirectoryManager initialization."""
        assert directory_manager.search_history == []
        assert directory_manager.current_directory == os.getcwd()
    
    def test_list_directory(self, directory_manager, temp_dir):
        """Test listing directory contents."""
        request = DirectorySearchRequest(
            search_type=SearchType.LIST_DIRECTORY,
            path=temp_dir,
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        assert response.search_result.total_results > 0
        assert len(response.search_result.files_found) >= 3  # test1.py, test2.txt, test3.md
        assert len(response.search_result.directories_found) >= 2  # subdir1, subdir2
    
    def test_list_directory_with_hidden(self, directory_manager, temp_dir):
        """Test listing directory with hidden files."""
        request = DirectorySearchRequest(
            search_type=SearchType.LIST_DIRECTORY,
            path=temp_dir,
            include_hidden=True,
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        # Should include the .hidden_file
        hidden_files = [f for f in response.search_result.files_found if f.name.startswith('.')]
        assert len(hidden_files) >= 1
    
    def test_find_files_by_pattern(self, directory_manager, temp_dir):
        """Test finding files by pattern."""
        request = DirectorySearchRequest(
            search_type=SearchType.FIND_FILES,
            path=temp_dir,
            query="*.py",
            recursive=True,
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        python_files = response.search_result.files_found
        assert len(python_files) >= 2  # test1.py and nested_file.py
        
        for file_info in python_files:
            assert file_info.name.endswith('.py')
    
    def test_find_files_non_recursive(self, directory_manager, temp_dir):
        """Test finding files non-recursively."""
        request = DirectorySearchRequest(
            search_type=SearchType.FIND_FILES,
            path=temp_dir,
            query="*.py",
            recursive=False,
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        # Should only find test1.py in root, not nested files
        python_files = response.search_result.files_found
        assert len(python_files) == 1
        assert python_files[0].name == "test1.py"
    
    def test_search_content(self, directory_manager, temp_dir):
        """Test searching file contents."""
        request = DirectorySearchRequest(
            search_type=SearchType.SEARCH_CONTENT,
            path=temp_dir,
            query="consciousness",
            recursive=True,
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        # All test files contain "consciousness" keyword
        assert len(response.search_result.files_found) >= 3
    
    def test_get_file_info(self, directory_manager, temp_dir):
        """Test getting file information."""
        test_file = os.path.join(temp_dir, "test1.py")
        
        request = DirectorySearchRequest(
            search_type=SearchType.GET_FILE_INFO,
            path=test_file,
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        assert len(response.search_result.files_found) == 1
        
        file_info = response.search_result.files_found[0]
        assert file_info.name == "test1.py"
        assert file_info.extension == "py"
        assert file_info.size > 0
    
    def test_explore_tree(self, directory_manager, temp_dir):
        """Test exploring directory tree."""
        request = DirectorySearchRequest(
            search_type=SearchType.EXPLORE_TREE,
            path=temp_dir,
            max_depth=2,
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        assert response.search_result.total_results > 0
        
        # Should find files at multiple levels
        files_found = response.search_result.files_found
        directories_found = response.search_result.directories_found
        
        assert len(files_found) >= 4  # Files at root and one level deep
        assert len(directories_found) >= 2  # subdir1, subdir2
    
    def test_find_by_extension(self, directory_manager, temp_dir):
        """Test finding files by extension."""
        request = DirectorySearchRequest(
            search_type=SearchType.FIND_BY_EXTENSION,
            path=temp_dir,
            file_extensions=["py", "md"],
            recursive=True,
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        files_found = response.search_result.files_found
        
        # Should find .py and .md files
        extensions = [f.extension for f in files_found]
        assert "py" in extensions
        assert "md" in extensions
        assert "txt" not in extensions  # Should not find .txt files
    
    def test_find_recent_files(self, directory_manager, temp_dir):
        """Test finding recent files."""
        request = DirectorySearchRequest(
            search_type=SearchType.RECENT_FILES,
            path=temp_dir,
            recursive=True,
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        files_found = response.search_result.files_found
        
        # Files should be sorted by modification time (most recent first)
        if len(files_found) > 1:
            for i in range(len(files_found) - 1):
                current_time = files_found[i].modified_time
                next_time = files_found[i + 1].modified_time
                assert current_time >= next_time
    
    def test_file_size_filters(self, directory_manager, temp_dir):
        """Test file size filtering."""
        # Create a large file
        large_file = os.path.join(temp_dir, "large_file.txt")
        with open(large_file, 'w') as f:
            f.write("x" * 10000)  # 10KB file
        
        request = DirectorySearchRequest(
            search_type=SearchType.FIND_FILES,
            path=temp_dir,
            query="*.txt",
            min_size=5000,  # 5KB minimum
            recursive=False,
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        # Should only find the large file
        files_found = response.search_result.files_found
        assert len(files_found) == 1
        assert files_found[0].name == "large_file.txt"
        assert files_found[0].size >= 5000
    
    def test_search_history(self, directory_manager, temp_dir):
        """Test search history tracking."""
        initial_count = len(directory_manager.get_search_history())
        
        request = DirectorySearchRequest(
            search_type=SearchType.LIST_DIRECTORY,
            path=temp_dir,
            assigned_by="test"
        )
        
        directory_manager.search_directory(request)
        
        history = directory_manager.get_search_history()
        assert len(history) == initial_count + 1
        assert history[-1].search_type == SearchType.LIST_DIRECTORY
    
    def test_clear_search_history(self, directory_manager, temp_dir):
        """Test clearing search history."""
        # Perform a search to add to history
        request = DirectorySearchRequest(
            search_type=SearchType.LIST_DIRECTORY,
            path=temp_dir,
            assigned_by="test"
        )
        
        directory_manager.search_directory(request)
        assert len(directory_manager.get_search_history()) > 0
        
        # Clear history
        result = directory_manager.clear_search_history()
        assert result["cleared_searches"] > 0
        assert len(directory_manager.get_search_history()) == 0
    
    def test_invalid_path_error(self, directory_manager):
        """Test error handling for invalid paths."""
        request = DirectorySearchRequest(
            search_type=SearchType.LIST_DIRECTORY,
            path="/nonexistent/path",
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is False
        assert response.search_result.error_message is not None
        assert "not exist" in response.search_result.error_message.lower()
    
    def test_content_search_without_query(self, directory_manager, temp_dir):
        """Test content search without query raises error."""
        request = DirectorySearchRequest(
            search_type=SearchType.SEARCH_CONTENT,
            path=temp_dir,
            query=None,  # No query provided
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is False
        assert "requires a query" in response.search_result.error_message
    
    def test_response_structure(self, directory_manager, temp_dir):
        """Test response structure completeness."""
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