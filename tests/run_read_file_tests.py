#!/usr/bin/env python3
"""
Test runner for read_file functionality.

This script runs comprehensive tests for Ray's read_file feature,
including handler tests, route tests, and integration tests.
"""

import sys
import os
import pytest
import tempfile
import shutil
import requests
import json
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_unit_tests():
    """Run unit tests for read_file functionality."""
    print("🧪 Running read_file unit tests...")
    
    # Run specific test classes
    test_files = [
        "tests/modules/directory/test_handler.py::TestReadFileHandler",
        "tests/modules/directory/test_routes.py::TestReadFileRoutes"
    ]
    
    for test_file in test_files:
        print(f"\n📋 Running {test_file}...")
        result = pytest.main(["-v", test_file])
        if result != 0:
            print(f"❌ Tests failed in {test_file}")
            return False
        else:
            print(f"✅ Tests passed in {test_file}")
    
    return True

def test_server_integration():
    """Test read_file functionality with running server."""
    print("\n🌐 Testing server integration...")
    
    BASE_URL = "http://localhost:8000"
    
    # Create test file
    test_content = "Hello from integration test!\nLine 2 content.\nLine 3 content."
    test_file = "test_integration_file.txt"
    
    try:
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        # Test 1: Task-based read
        print("📖 Testing task-based read...")
        task_request = {
            "task": [{
                "action": "read_file",
                "file_path": f"./{test_file}",
                "assigned_by": "test"
            }],
            "assigned_by": "test",
            "execute_immediately": True,
            "self_destruct": True
        }
        
        try:
            response = requests.post(f"{BASE_URL}/tasks", json=task_request, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get("task_results") and result["task_results"][0]:
                    file_data = result["task_results"][0]
                    if file_data.get("content") == test_content:
                        print("✅ Task-based read successful")
                    else:
                        print("❌ Task-based read content mismatch")
                        return False
                else:
                    print("❌ Task-based read no results")
                    return False
            else:
                print(f"❌ Task-based read HTTP error: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Task-based read connection error: {e}")
            return False
        
        # Test 2: Direct directory read
        print("📖 Testing direct directory read...")
        direct_request = {
            "action": "read_file",
            "path": f"./{test_file}",
            "assigned_by": "test"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/directory/read", json=direct_request, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if (result.get("search_result", {}).get("success") and 
                    result["search_result"].get("files_found")):
                    file_info = result["search_result"]["files_found"][0]
                    if file_info.get("content") == test_content:
                        print("✅ Direct directory read successful")
                    else:
                        print("❌ Direct directory read content mismatch")
                        return False
                else:
                    print("❌ Direct directory read failed")
                    return False
            else:
                print(f"❌ Direct directory read HTTP error: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Direct directory read connection error: {e}")
            return False
        
        # Test 3: Advanced parameters
        print("📖 Testing advanced parameters...")
        advanced_request = {
            "action": "read_file",
            "path": ".",
            "query": json.dumps({
                "file_path": f"./{test_file}",
                "start_line": 2,
                "end_line": 3,
                "encoding": "utf-8"
            }),
            "assigned_by": "test"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/directory/read", json=advanced_request, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if (result.get("search_result", {}).get("success") and 
                    result["search_result"].get("files_found")):
                    file_info = result["search_result"]["files_found"][0]
                    expected_content = "Line 2 content.\nLine 3 content.\n"
                    if file_info.get("content") == expected_content:
                        print("✅ Advanced parameters successful")
                    else:
                        print("❌ Advanced parameters content mismatch")
                        print(f"Expected: {repr(expected_content)}")
                        print(f"Got: {repr(file_info.get('content'))}")
                        return False
                else:
                    print("❌ Advanced parameters failed")
                    return False
            else:
                print(f"❌ Advanced parameters HTTP error: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Advanced parameters connection error: {e}")
            return False
        
        # Test 4: Error handling
        print("📖 Testing error handling...")
        error_request = {
            "action": "read_file",
            "path": "./nonexistent_file.txt",
            "assigned_by": "test"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/directory/read", json=error_request, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if (result.get("search_result", {}).get("success") is False and
                    "not found" in result["search_result"].get("error_message", "").lower()):
                    print("✅ Error handling successful")
                else:
                    print("❌ Error handling failed - should have failed")
                    return False
            else:
                print(f"❌ Error handling HTTP error: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Error handling connection error: {e}")
            return False
        
        return True
        
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)

def test_performance():
    """Test read_file performance with various file sizes."""
    print("\n⚡ Testing read_file performance...")
    
    BASE_URL = "http://localhost:8000"
    
    # Create test files of different sizes
    test_files = {
        "small.txt": "Small file content",
        "medium.txt": "\n".join([f"Line {i}: Medium file content" for i in range(100)]),
        "large.txt": "\n".join([f"Line {i}: Large file content with more text" for i in range(1000)])
    }
    
    try:
        # Create test files
        for filename, content in test_files.items():
            with open(filename, 'w') as f:
                f.write(content)
        
        for filename in test_files.keys():
            print(f"📊 Testing {filename}...")
            
            start_time = time.time()
            
            request = {
                "action": "read_file",
                "path": f"./{filename}",
                "assigned_by": "test"
            }
            
            try:
                response = requests.post(f"{BASE_URL}/directory/read", json=request, timeout=30)
                
                end_time = time.time()
                duration = (end_time - start_time) * 1000  # Convert to ms
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("search_result", {}).get("success"):
                        file_info = result["search_result"]["files_found"][0]
                        file_size = file_info.get("size", 0)
                        lines = file_info.get("lines_count", 0)
                        
                        print(f"   ✅ {filename}: {file_size} bytes, {lines} lines, {duration:.1f}ms")
                    else:
                        print(f"   ❌ {filename}: Read failed")
                        return False
                else:
                    print(f"   ❌ {filename}: HTTP {response.status_code}")
                    return False
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ {filename}: Connection error - {e}")
                return False
        
        return True
        
    finally:
        # Cleanup
        for filename in test_files.keys():
            if os.path.exists(filename):
                os.remove(filename)

def check_server_status():
    """Check if the server is running and read_file is available."""
    print("🔍 Checking server status...")
    
    try:
        response = requests.get("http://localhost:8000/directory/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            available_actions = status.get("available_actions", [])
            if "read_file" in available_actions:
                print("✅ Server is running and read_file is available")
                return True
            else:
                print("❌ Server is running but read_file is not available")
                print(f"Available actions: {available_actions}")
                return False
        else:
            print(f"❌ Server status check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Server connection failed: {e}")
        print("   Please start the server with: python main.py")
        return False

def main():
    """Run all read_file tests."""
    print("🚀 Ray's Read File Test Suite")
    print("=" * 50)
    
    # Run unit tests first
    unit_tests_passed = run_unit_tests()
    
    if not unit_tests_passed:
        print("\n❌ Unit tests failed. Skipping integration tests.")
        return False
    
    print("\n✅ All unit tests passed!")
    
    # Check if server is running for integration tests
    server_running = check_server_status()
    
    if server_running:
        print("\n🌐 Running integration tests...")
        
        integration_passed = test_server_integration()
        performance_passed = test_performance()
        
        if integration_passed and performance_passed:
            print("\n🎉 All tests passed!")
            print("\nRay's read_file functionality is working perfectly:")
            print("✅ Unit tests: Handler and route logic")
            print("✅ Integration tests: API endpoints")
            print("✅ Performance tests: Various file sizes")
            print("✅ Error handling: Invalid files and parameters")
            return True
        else:
            print("\n❌ Some integration tests failed.")
            return False
    else:
        print("\n⚠️ Server not running - skipping integration tests")
        print("Unit tests passed, but integration tests require a running server.")
        return unit_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)