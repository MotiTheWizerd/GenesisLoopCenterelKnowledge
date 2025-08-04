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


class TestReadFileHandler:
    """Test read_file functionality in DirectoryManager."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory with test files for reading."""
        temp_dir = tempfile.mkdtemp()
        
        # Create test files with different content types
        test_files = {
            "simple.txt": "Hello World!\nThis is a simple text file.\nLine 3 content.",
            "config.json": '{\n  "version": "1.0",\n  "debug": true,\n  "features": ["read", "write"]\n}',
            "multiline.py": "#!/usr/bin/env python3\n# Test Python file\ndef hello():\n    print('Hello from Python!')\n    return True\n\nif __name__ == '__main__':\n    hello()",
            "large_file.log": "\n".join([f"Log entry {i}: This is log line number {i}" for i in range(1, 101)]),  # 100 lines
            "unicode.txt": "Unicode test: 🌟 Ray's consciousness 🧠 with émojis and spëcial chars",
            "empty.txt": "",
            "single_line.txt": "Just one line without newline"
        }
        
        for filename, content in test_files.items():
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Create a binary file with more complex binary data
        binary_path = os.path.join(temp_dir, "binary.dat")
        with open(binary_path, 'wb') as f:
            # Create truly binary data that will cause UnicodeDecodeError
            binary_data = bytes(range(256)) * 4  # All possible byte values
            f.write(binary_data)
        
        # Create subdirectory with file
        subdir = os.path.join(temp_dir, "subdir")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "nested.txt"), 'w') as f:
            f.write("Nested file content")
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def directory_manager(self):
        """Create a DirectoryManager instance."""
        return DirectoryManager()
    
    def test_read_simple_file(self, directory_manager, temp_dir):
        """Test reading a simple text file."""
        from modules.directory.models import DirectorySearchRequest, ActionType
        
        file_path = os.path.join(temp_dir, "simple.txt")
        request = DirectorySearchRequest(
            action=ActionType.READ_FILE,
            path=file_path,
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        assert len(response.search_result.files_found) == 1
        
        file_info = response.search_result.files_found[0]
        assert file_info.name == "simple.txt"
        assert file_info.content == "Hello World!\nThis is a simple text file.\nLine 3 content."
        assert file_info.lines_count == 3
        assert file_info.is_binary is False
        assert file_info.encoding_used == "utf-8"
    
    def test_read_json_file(self, directory_manager, temp_dir):
        """Test reading a JSON configuration file."""
        from modules.directory.models import DirectorySearchRequest, ActionType
        import json
        
        file_path = os.path.join(temp_dir, "config.json")
        request = DirectorySearchRequest(
            action=ActionType.READ_FILE,
            path=file_path,
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        file_info = response.search_result.files_found[0]
        
        # Verify JSON content can be parsed
        config = json.loads(file_info.content)
        assert config["version"] == "1.0"
        assert config["debug"] is True
        assert "read" in config["features"]
    
    def test_read_with_query_parameters(self, directory_manager, temp_dir):
        """Test reading file with JSON query parameters."""
        from modules.directory.models import DirectorySearchRequest, ActionType
        import json
        
        query_params = {
            "file_path": os.path.join(temp_dir, "multiline.py"),
            "encoding": "utf-8",
            "max_size": 1024
        }
        
        request = DirectorySearchRequest(
            action=ActionType.READ_FILE,
            path=".",
            query=json.dumps(query_params),
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        file_info = response.search_result.files_found[0]
        assert file_info.name == "multiline.py"
        assert "def hello():" in file_info.content
        assert file_info.lines_count == 8
    
    def test_read_file_with_line_range(self, directory_manager, temp_dir):
        """Test reading specific lines from a file."""
        from modules.directory.models import DirectorySearchRequest, ActionType
        import json
        
        query_params = {
            "file_path": os.path.join(temp_dir, "large_file.log"),
            "start_line": 10,
            "end_line": 15
        }
        
        request = DirectorySearchRequest(
            action=ActionType.READ_FILE,
            path=".",
            query=json.dumps(query_params),
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        file_info = response.search_result.files_found[0]
        
        # Should have 6 lines (10-15 inclusive)
        assert file_info.lines_count == 6
        assert "Log entry 10:" in file_info.content
        assert "Log entry 15:" in file_info.content
        assert "Log entry 9:" not in file_info.content
        assert "Log entry 16:" not in file_info.content
    
    def test_read_unicode_file(self, directory_manager, temp_dir):
        """Test reading file with Unicode characters."""
        from modules.directory.models import DirectorySearchRequest, ActionType
        
        file_path = os.path.join(temp_dir, "unicode.txt")
        request = DirectorySearchRequest(
            action=ActionType.READ_FILE,
            path=file_path,
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        file_info = response.search_result.files_found[0]
        assert "🌟" in file_info.content
        assert "🧠" in file_info.content
        assert "émojis" in file_info.content
        assert "spëcial" in file_info.content
    
    def test_read_empty_file(self, directory_manager, temp_dir):
        """Test reading an empty file."""
        from modules.directory.models import DirectorySearchRequest, ActionType
        
        file_path = os.path.join(temp_dir, "empty.txt")
        request = DirectorySearchRequest(
            action=ActionType.READ_FILE,
            path=file_path,
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        file_info = response.search_result.files_found[0]
        assert file_info.content == ""
        assert file_info.lines_count == 0
        assert file_info.size == 0
    
    def test_read_binary_file(self, directory_manager, temp_dir):
        """Test reading a binary file."""
        from modules.directory.models import DirectorySearchRequest, ActionType
        
        file_path = os.path.join(temp_dir, "binary.dat")
        request = DirectorySearchRequest(
            action=ActionType.READ_FILE,
            path=file_path,
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        file_info = response.search_result.files_found[0]
        # Binary detection may vary based on content, check for either binary detection or replacement chars
        assert file_info.is_binary is True or '�' in file_info.content
        if file_info.is_binary:
            assert "<Binary file" in file_info.content or file_info.lines_count == 0
    
    def test_read_file_size_limit(self, directory_manager, temp_dir):
        """Test file size limit enforcement."""
        from modules.directory.models import DirectorySearchRequest, ActionType
        import json
        
        query_params = {
            "file_path": os.path.join(temp_dir, "large_file.log"),
            "max_size": 100  # Very small limit
        }
        
        request = DirectorySearchRequest(
            action=ActionType.READ_FILE,
            path=".",
            query=json.dumps(query_params),
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is False
        assert "too large" in response.search_result.error_message.lower()
    
    def test_read_nonexistent_file(self, directory_manager, temp_dir):
        """Test reading a file that doesn't exist."""
        from modules.directory.models import DirectorySearchRequest, ActionType
        
        file_path = os.path.join(temp_dir, "nonexistent.txt")
        request = DirectorySearchRequest(
            action=ActionType.READ_FILE,
            path=file_path,
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is False
        assert "does not exist" in response.search_result.error_message.lower()
    
    def test_read_directory_instead_of_file(self, directory_manager, temp_dir):
        """Test error when trying to read a directory as a file."""
        from modules.directory.models import DirectorySearchRequest, ActionType
        
        subdir_path = os.path.join(temp_dir, "subdir")
        request = DirectorySearchRequest(
            action=ActionType.READ_FILE,
            path=subdir_path,
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is False
        assert "not a file" in response.search_result.error_message.lower()
    
    def test_read_file_with_different_encoding(self, directory_manager, temp_dir):
        """Test reading file with specified encoding."""
        from modules.directory.models import DirectorySearchRequest, ActionType
        import json
        
        # Create a file with Latin-1 encoding
        latin_file = os.path.join(temp_dir, "latin1.txt")
        with open(latin_file, 'w', encoding='latin-1') as f:
            f.write("Café with special chars: àáâãäå")
        
        query_params = {
            "file_path": latin_file,
            "encoding": "latin-1"
        }
        
        request = DirectorySearchRequest(
            action=ActionType.READ_FILE,
            path=".",
            query=json.dumps(query_params),
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        file_info = response.search_result.files_found[0]
        assert "Café" in file_info.content
        assert file_info.encoding_used == "latin-1"
    
    def test_read_file_line_boundaries(self, directory_manager, temp_dir):
        """Test reading with various line boundary conditions."""
        from modules.directory.models import DirectorySearchRequest, ActionType
        import json
        
        # Test reading from line 1 to end
        query_params = {
            "file_path": os.path.join(temp_dir, "multiline.py"),
            "start_line": 1
        }
        
        request = DirectorySearchRequest(
            action=ActionType.READ_FILE,
            path=".",
            query=json.dumps(query_params),
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        file_info = response.search_result.files_found[0]
        assert file_info.lines_count == 8  # All lines
        
        # Test reading up to specific line
        query_params["start_line"] = None
        query_params["end_line"] = 3
        
        request.query = json.dumps(query_params)
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        file_info = response.search_result.files_found[0]
        assert file_info.lines_count == 3  # First 3 lines
    
    def test_read_file_metadata_completeness(self, directory_manager, temp_dir):
        """Test that all file metadata is properly populated."""
        from modules.directory.models import DirectorySearchRequest, ActionType
        
        file_path = os.path.join(temp_dir, "simple.txt")
        request = DirectorySearchRequest(
            action=ActionType.READ_FILE,
            path=file_path,
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        file_info = response.search_result.files_found[0]
        
        # Check all metadata fields are present
        assert file_info.name is not None
        assert file_info.path is not None
        assert file_info.size is not None
        assert file_info.modified_time is not None
        assert file_info.extension is not None
        assert file_info.is_directory is False
        assert file_info.permissions is not None
        
        # Check read-specific fields
        assert file_info.content is not None
        assert file_info.lines_count is not None
        assert file_info.is_binary is not None
        assert file_info.encoding_used is not None
    
    def test_read_file_performance_tracking(self, directory_manager, temp_dir):
        """Test that execution time is tracked."""
        from modules.directory.models import DirectorySearchRequest, ActionType
        
        file_path = os.path.join(temp_dir, "simple.txt")
        request = DirectorySearchRequest(
            action=ActionType.READ_FILE,
            path=file_path,
            assigned_by="test"
        )
        
        response = directory_manager.search_directory(request)
        
        assert response.search_result.success is True
        assert response.search_result.execution_time_ms is not None
        assert response.search_result.execution_time_ms >= 0
        assert isinstance(response.search_result.execution_time_ms, int)