"""
Tests for directory search models.
"""

import pytest
from datetime import datetime, timezone
from modules.directory.models import (
    DirectorySearchRequest,
    DirectorySearchResponse,
    SearchResult,
    FileInfo,
    DirectoryInfo,
    SearchType,
    DirectoryExploreRequest,
    ContentSearchRequest
)


class TestDirectorySearchRequest:
    """Test DirectorySearchRequest model."""
    
    def test_basic_request_creation(self):
        """Test creating a basic directory search request."""
        request = DirectorySearchRequest(
            search_type=SearchType.LIST_DIRECTORY,
            path="./test",
            assigned_by="ray"
        )
        
        assert request.search_type == SearchType.LIST_DIRECTORY
        assert request.path == "./test"
        assert request.assigned_by == "ray"
        assert request.recursive is False
        assert request.include_hidden is False
    
    def test_advanced_request_creation(self):
        """Test creating an advanced directory search request."""
        request = DirectorySearchRequest(
            search_type=SearchType.FIND_FILES,
            path="./modules",
            query="*.py",
            recursive=True,
            max_depth=3,
            include_hidden=True,
            file_extensions=["py", "md"],
            min_size=100,
            max_size=10000,
            assigned_by="ray"
        )
        
        assert request.search_type == SearchType.FIND_FILES
        assert request.query == "*.py"
        assert request.recursive is True
        assert request.max_depth == 3
        assert request.include_hidden is True
        assert request.file_extensions == ["py", "md"]
        assert request.min_size == 100
        assert request.max_size == 10000
    
    def test_content_search_request(self):
        """Test creating a content search request."""
        request = DirectorySearchRequest(
            search_type=SearchType.SEARCH_CONTENT,
            path="./modules",
            query="consciousness",
            file_extensions=["py", "md"],
            assigned_by="ray"
        )
        
        assert request.search_type == SearchType.SEARCH_CONTENT
        assert request.query == "consciousness"
        assert request.file_extensions == ["py", "md"]


class TestFileInfo:
    """Test FileInfo model."""
    
    def test_file_info_creation(self):
        """Test creating a FileInfo object."""
        file_info = FileInfo(
            name="test.py",
            path="/path/to/test.py",
            size=1024,
            modified_time="2025-07-28T10:00:00Z",
            extension="py",
            is_directory=False,
            permissions="644"
        )
        
        assert file_info.name == "test.py"
        assert file_info.path == "/path/to/test.py"
        assert file_info.size == 1024
        assert file_info.extension == "py"
        assert file_info.is_directory is False
        assert file_info.permissions == "644"
    
    def test_directory_file_info(self):
        """Test FileInfo for a directory."""
        dir_info = FileInfo(
            name="modules",
            path="/path/to/modules",
            size=0,
            modified_time="2025-07-28T10:00:00Z",
            is_directory=True
        )
        
        assert dir_info.name == "modules"
        assert dir_info.is_directory is True
        assert dir_info.extension is None


class TestDirectoryInfo:
    """Test DirectoryInfo model."""
    
    def test_directory_info_creation(self):
        """Test creating a DirectoryInfo object."""
        files = [
            FileInfo(
                name="test.py",
                path="/path/test.py",
                size=1024,
                modified_time="2025-07-28T10:00:00Z"
            )
        ]
        
        dir_info = DirectoryInfo(
            name="test_dir",
            path="/path/to/test_dir",
            file_count=1,
            subdirectory_count=2,
            total_size=1024,
            modified_time="2025-07-28T10:00:00Z",
            files=files,
            subdirectories=["sub1", "sub2"]
        )
        
        assert dir_info.name == "test_dir"
        assert dir_info.file_count == 1
        assert dir_info.subdirectory_count == 2
        assert dir_info.total_size == 1024
        assert len(dir_info.files) == 1
        assert len(dir_info.subdirectories) == 2


class TestSearchResult:
    """Test SearchResult model."""
    
    def test_search_result_creation(self):
        """Test creating a SearchResult object."""
        files = [
            FileInfo(
                name="test.py",
                path="/path/test.py",
                size=1024,
                modified_time="2025-07-28T10:00:00Z"
            )
        ]
        
        result = SearchResult(
            search_type=SearchType.FIND_FILES,
            query="*.py",
            search_path="/path/to/search",
            files_found=files,
            total_results=1,
            recursive=True,
            execution_time_ms=150
        )
        
        assert result.search_type == SearchType.FIND_FILES
        assert result.query == "*.py"
        assert result.total_results == 1
        assert len(result.files_found) == 1
        assert result.recursive is True
        assert result.execution_time_ms == 150
        assert result.success is True
    
    def test_search_result_with_error(self):
        """Test SearchResult with error."""
        result = SearchResult(
            search_type=SearchType.LIST_DIRECTORY,
            query="/nonexistent",
            search_path="/nonexistent",
            success=False,
            error_message="Path not found"
        )
        
        assert result.success is False
        assert result.error_message == "Path not found"
        assert result.total_results == 0


class TestDirectorySearchResponse:
    """Test DirectorySearchResponse model."""
    
    def test_response_creation(self):
        """Test creating a DirectorySearchResponse."""
        search_result = SearchResult(
            search_type=SearchType.LIST_DIRECTORY,
            query="./test",
            search_path="./test",
            total_results=5
        )
        
        response = DirectorySearchResponse(
            search_result=search_result,
            assigned_by="ray",
            current_path="/current/path",
            parent_path="/current",
            suggested_paths=["/path1", "/path2"],
            summary={"total_files": 3, "total_directories": 2}
        )
        
        assert response.search_result.total_results == 5
        assert response.assigned_by == "ray"
        assert response.current_path == "/current/path"
        assert response.parent_path == "/current"
        assert len(response.suggested_paths) == 2
        assert response.summary["total_files"] == 3


class TestSearchTypes:
    """Test SearchType enum."""
    
    def test_all_search_types(self):
        """Test all available search types."""
        expected_types = [
            "list_directory",
            "find_files", 
            "search_content",
            "get_file_info",
            "explore_tree",
            "find_by_extension",
            "recent_files",
            "save_to_file",
            "rename_file",
            "delete_file",
            "move_file"
        ]
        
        actual_types = [search_type.value for search_type in SearchType]
        
        for expected in expected_types:
            assert expected in actual_types
        
        assert len(actual_types) == len(expected_types)


class TestContentSearchRequest:
    """Test ContentSearchRequest model."""
    
    def test_content_search_request_creation(self):
        """Test creating a ContentSearchRequest."""
        request = ContentSearchRequest(
            path="./modules",
            content_query="consciousness",
            file_extensions=["py", "md"],
            case_sensitive=True,
            max_results=50,
            assigned_by="ray"
        )
        
        assert request.path == "./modules"
        assert request.content_query == "consciousness"
        assert request.file_extensions == ["py", "md"]
        assert request.case_sensitive is True
        assert request.max_results == 50
        assert request.assigned_by == "ray"


class TestDirectoryExploreRequest:
    """Test DirectoryExploreRequest model."""
    
    def test_explore_request_creation(self):
        """Test creating a DirectoryExploreRequest."""
        request = DirectoryExploreRequest(
            path="./modules",
            max_depth=3,
            include_files=True,
            include_hidden=False,
            assigned_by="ray"
        )
        
        assert request.path == "./modules"
        assert request.max_depth == 3
        assert request.include_files is True
        assert request.include_hidden is False
        assert request.assigned_by == "ray"