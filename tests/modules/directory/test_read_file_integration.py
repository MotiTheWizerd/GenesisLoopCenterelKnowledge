"""
Integration tests for read_file functionality.

These tests verify the complete read_file workflow including
API endpoints, error handling, and edge cases.
"""

import pytest
import os
import tempfile
import shutil
import json
import requests
from pathlib import Path


class TestReadFileIntegration:
    """Integration tests for read_file API endpoints."""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory with comprehensive test files."""
        temp_dir = tempfile.mkdtemp()
        
        # Create various test files
        test_files = {
            # Text files
            "simple.txt": "Hello World!\nThis is line 2.\nThis is line 3.",
            "empty.txt": "",
            "single_line.txt": "Just one line",
            "no_newline.txt": "No newline at end",
            
            # Code files
            "script.py": "#!/usr/bin/env python3\n# Python script\ndef main():\n    print('Hello')\n\nif __name__ == '__main__':\n    main()",
            "config.json": '{\n  "version": "1.0",\n  "debug": true,\n  "features": ["read", "write"]\n}',
            "data.yaml": "version: 1.0\ndebug: true\nfeatures:\n  - read\n  - write",
            
            # Large files
            "medium.log": "\n".join([f"Log entry {i}: This is log line {i}" for i in range(1, 51)]),  # 50 lines
            "large.log": "\n".join([f"Log entry {i}: This is log line {i}" for i in range(1, 201)]),  # 200 lines
            
            # Unicode files
            "unicode.txt": "Unicode test: 🌟 Ray's consciousness 🧠\nSpecial chars: àáâãäå\nEmojis: 😀😃😄😁",
            
            # Different encodings
            "ascii.txt": "Pure ASCII content\nNo special characters",
        }
        
        for filename, content in test_files.items():
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Create a Latin-1 encoded file
        latin_file = os.path.join(temp_dir, "latin1.txt")
        with open(latin_file, 'w', encoding='latin-1') as f:
            f.write("Latin-1 content: café, naïve, résumé")
        
        # Create a binary file
        binary_file = os.path.join(temp_dir, "binary.dat")
        with open(binary_file, 'wb') as f:
            f.write(b'\x00\x01\x02\x03\x04\x05\xFF\xFE\xFD\xFC')
        
        # Create subdirectory with nested file
        subdir = os.path.join(temp_dir, "subdir")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "nested.txt"), 'w') as f:
            f.write("Nested file content")
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_server_availability(self):
        """Test that the server is running and read_file is available."""
        try:
            response = requests.get(f"{self.BASE_URL}/directory/status", timeout=5)
            assert response.status_code == 200
            
            status = response.json()
            available_actions = status.get("available_actions", [])
            assert "read_file" in available_actions
            
        except requests.exceptions.RequestException:
            pytest.skip("Server not running - skipping integration tests")
    
    def test_task_based_read_simple(self, temp_dir):
        """Test reading file through task system."""
        file_path = os.path.join(temp_dir, "simple.txt")
        
        request = {
            "task": [{
                "action": "read_file",
                "file_path": file_path,
                "assigned_by": "test"
            }],
            "assigned_by": "test",
            "execute_immediately": True,
            "self_destruct": True
        }
        
        response = requests.post(f"{self.BASE_URL}/tasks", json=request)
        assert response.status_code == 200
        
        result = response.json()
        assert "task_results" in result
        assert len(result["task_results"]) == 1
        
        file_data = result["task_results"][0]
        assert file_data["name"] == "simple.txt"
        assert file_data["content"] == "Hello World!\nThis is line 2.\nThis is line 3."
        assert file_data["lines_count"] == 3
        assert file_data["is_binary"] is False
    
    def test_direct_read_simple(self, temp_dir):
        """Test reading file through direct directory endpoint."""
        file_path = os.path.join(temp_dir, "simple.txt")
        
        request = {
            "action": "read_file",
            "path": file_path,
            "assigned_by": "test"
        }
        
        response = requests.post(f"{self.BASE_URL}/directory/read", json=request)
        assert response.status_code == 200
        
        result = response.json()
        assert result["search_result"]["success"] is True
        assert len(result["search_result"]["files_found"]) == 1
        
        file_info = result["search_result"]["files_found"][0]
        assert file_info["name"] == "simple.txt"
        assert file_info["content"] == "Hello World!\nThis is line 2.\nThis is line 3."
        assert file_info["lines_count"] == 3
        assert file_info["is_binary"] is False
    
    def test_read_with_advanced_parameters(self, temp_dir):
        """Test reading file with advanced parameters."""
        file_path = os.path.join(temp_dir, "medium.log")
        
        query_params = {
            "file_path": file_path,
            "start_line": 10,
            "end_line": 15,
            "encoding": "utf-8",
            "max_size": 10240
        }
        
        request = {
            "action": "read_file",
            "path": ".",
            "query": json.dumps(query_params),
            "assigned_by": "test"
        }
        
        response = requests.post(f"{self.BASE_URL}/directory/read", json=request)
        assert response.status_code == 200
        
        result = response.json()
        assert result["search_result"]["success"] is True
        
        file_info = result["search_result"]["files_found"][0]
        assert file_info["lines_count"] == 6  # Lines 10-15 inclusive
        assert "Log entry 10:" in file_info["content"]
        assert "Log entry 15:" in file_info["content"]
        assert "Log entry 9:" not in file_info["content"]
        assert "Log entry 16:" not in file_info["content"]
    
    def test_read_json_file(self, temp_dir):
        """Test reading and parsing JSON file."""
        file_path = os.path.join(temp_dir, "config.json")
        
        request = {
            "action": "read_file",
            "path": file_path,
            "assigned_by": "test"
        }
        
        response = requests.post(f"{self.BASE_URL}/directory/read", json=request)
        assert response.status_code == 200
        
        result = response.json()
        file_info = result["search_result"]["files_found"][0]
        
        # Verify JSON content can be parsed
        config = json.loads(file_info["content"])
        assert config["version"] == "1.0"
        assert config["debug"] is True
        assert "read" in config["features"]
    
    def test_read_unicode_file(self, temp_dir):
        """Test reading file with Unicode characters."""
        file_path = os.path.join(temp_dir, "unicode.txt")
        
        request = {
            "action": "read_file",
            "path": file_path,
            "assigned_by": "test"
        }
        
        response = requests.post(f"{self.BASE_URL}/directory/read", json=request)
        assert response.status_code == 200
        
        result = response.json()
        file_info = result["search_result"]["files_found"][0]
        
        assert "🌟" in file_info["content"]
        assert "🧠" in file_info["content"]
        assert "àáâãäå" in file_info["content"]
        assert "😀😃😄😁" in file_info["content"]
    
    def test_read_empty_file(self, temp_dir):
        """Test reading empty file."""
        file_path = os.path.join(temp_dir, "empty.txt")
        
        request = {
            "action": "read_file",
            "path": file_path,
            "assigned_by": "test"
        }
        
        response = requests.post(f"{self.BASE_URL}/directory/read", json=request)
        assert response.status_code == 200
        
        result = response.json()
        file_info = result["search_result"]["files_found"][0]
        
        assert file_info["content"] == ""
        assert file_info["lines_count"] == 0
        assert file_info["size"] == 0
    
    def test_read_binary_file(self, temp_dir):
        """Test reading binary file."""
        file_path = os.path.join(temp_dir, "binary.dat")
        
        request = {
            "action": "read_file",
            "path": file_path,
            "assigned_by": "test"
        }
        
        response = requests.post(f"{self.BASE_URL}/directory/read", json=request)
        assert response.status_code == 200
        
        result = response.json()
        file_info = result["search_result"]["files_found"][0]
        
        assert file_info["is_binary"] is True
        assert file_info["lines_count"] == 0
        assert "<Binary file" in file_info["content"]
    
    def test_read_with_different_encoding(self, temp_dir):
        """Test reading file with specific encoding."""
        file_path = os.path.join(temp_dir, "latin1.txt")
        
        query_params = {
            "file_path": file_path,
            "encoding": "latin-1"
        }
        
        request = {
            "action": "read_file",
            "path": ".",
            "query": json.dumps(query_params),
            "assigned_by": "test"
        }
        
        response = requests.post(f"{self.BASE_URL}/directory/read", json=request)
        assert response.status_code == 200
        
        result = response.json()
        file_info = result["search_result"]["files_found"][0]
        
        assert "café" in file_info["content"]
        assert "naïve" in file_info["content"]
        assert "résumé" in file_info["content"]
        assert file_info["encoding_used"] == "latin-1"
    
    def test_read_with_size_limit(self, temp_dir):
        """Test file size limit enforcement."""
        file_path = os.path.join(temp_dir, "large.log")
        
        query_params = {
            "file_path": file_path,
            "max_size": 100  # Very small limit
        }
        
        request = {
            "action": "read_file",
            "path": ".",
            "query": json.dumps(query_params),
            "assigned_by": "test"
        }
        
        response = requests.post(f"{self.BASE_URL}/directory/read", json=request)
        assert response.status_code == 200
        
        result = response.json()
        assert result["search_result"]["success"] is False
        assert "too large" in result["search_result"]["error_message"].lower()
    
    def test_read_nonexistent_file(self, temp_dir):
        """Test error handling for nonexistent file."""
        file_path = os.path.join(temp_dir, "nonexistent.txt")
        
        request = {
            "action": "read_file",
            "path": file_path,
            "assigned_by": "test"
        }
        
        response = requests.post(f"{self.BASE_URL}/directory/read", json=request)
        assert response.status_code == 200
        
        result = response.json()
        assert result["search_result"]["success"] is False
        assert "not found" in result["search_result"]["error_message"].lower()
    
    def test_read_directory_as_file(self, temp_dir):
        """Test error when trying to read directory as file."""
        subdir_path = os.path.join(temp_dir, "subdir")
        
        request = {
            "action": "read_file",
            "path": subdir_path,
            "assigned_by": "test"
        }
        
        response = requests.post(f"{self.BASE_URL}/directory/read", json=request)
        assert response.status_code == 200
        
        result = response.json()
        assert result["search_result"]["success"] is False
        assert "not a file" in result["search_result"]["error_message"].lower()
    
    def test_read_file_line_boundaries(self, temp_dir):
        """Test various line boundary conditions."""
        file_path = os.path.join(temp_dir, "medium.log")
        
        # Test reading from start to specific line
        query_params = {
            "file_path": file_path,
            "end_line": 5
        }
        
        request = {
            "action": "read_file",
            "path": ".",
            "query": json.dumps(query_params),
            "assigned_by": "test"
        }
        
        response = requests.post(f"{self.BASE_URL}/directory/read", json=request)
        assert response.status_code == 200
        
        result = response.json()
        file_info = result["search_result"]["files_found"][0]
        assert file_info["lines_count"] == 5
        assert "Log entry 1:" in file_info["content"]
        assert "Log entry 5:" in file_info["content"]
        assert "Log entry 6:" not in file_info["content"]
    
    def test_response_structure_completeness(self, temp_dir):
        """Test that response contains all expected fields."""
        file_path = os.path.join(temp_dir, "simple.txt")
        
        request = {
            "action": "read_file",
            "path": file_path,
            "assigned_by": "test"
        }
        
        response = requests.post(f"{self.BASE_URL}/directory/read", json=request)
        assert response.status_code == 200
        
        result = response.json()
        
        # Check top-level response structure
        assert "request_id" in result
        assert "search_result" in result
        assert "assigned_by" in result
        assert "timestamp" in result
        assert "summary" in result
        
        # Check search result structure
        search_result = result["search_result"]
        assert "search_id" in search_result
        assert "action" in search_result
        assert "timestamp" in search_result
        assert "files_found" in search_result
        assert "total_results" in search_result
        assert "execution_time_ms" in search_result
        assert "success" in search_result
        
        # Check file info structure
        file_info = search_result["files_found"][0]
        required_fields = [
            "name", "path", "size", "modified_time", "extension",
            "is_directory", "permissions", "content", "lines_count",
            "is_binary", "encoding_used"
        ]
        
        for field in required_fields:
            assert field in file_info, f"Missing field: {field}"
    
    def test_performance_tracking(self, temp_dir):
        """Test that execution time is properly tracked."""
        file_path = os.path.join(temp_dir, "simple.txt")
        
        request = {
            "action": "read_file",
            "path": file_path,
            "assigned_by": "test"
        }
        
        response = requests.post(f"{self.BASE_URL}/directory/read", json=request)
        assert response.status_code == 200
        
        result = response.json()
        search_result = result["search_result"]
        
        assert "execution_time_ms" in search_result
        assert isinstance(search_result["execution_time_ms"], int)
        assert search_result["execution_time_ms"] >= 0
        assert search_result["execution_time_ms"] < 10000  # Should be under 10 seconds
    
    def test_multiple_file_reads(self, temp_dir):
        """Test reading multiple files in sequence."""
        files_to_read = ["simple.txt", "config.json", "unicode.txt"]
        
        for filename in files_to_read:
            file_path = os.path.join(temp_dir, filename)
            
            request = {
                "action": "read_file",
                "path": file_path,
                "assigned_by": "test"
            }
            
            response = requests.post(f"{self.BASE_URL}/directory/read", json=request)
            assert response.status_code == 200
            
            result = response.json()
            assert result["search_result"]["success"] is True
            
            file_info = result["search_result"]["files_found"][0]
            assert file_info["name"] == filename
            assert len(file_info["content"]) > 0