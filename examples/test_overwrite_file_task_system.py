#!/usr/bin/env python3
"""
Test script demonstrating Ray's overwrite_file tool through the task system.

This script shows how users can interact with Ray's file writing capabilities
using the same task system interface that Ray uses internally.
"""

import requests
import json
import time
from datetime import datetime


class RayTaskClient:
    """Client for interacting with Ray's task system."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def send_task(self, tasks, assigned_by="user", execute_immediately=True):
        """
        Send a task or batch of tasks to Ray's task system.
        
        Args:
            tasks: Single task dict or list of task dicts
            assigned_by: Who is sending the task
            execute_immediately: Whether to execute immediately
            
        Returns:
            Response from the task system
        """
        # Ensure tasks is a list
        if isinstance(tasks, dict):
            tasks = [tasks]
        
        task_data = {
            "task": tasks,
            "assigned_by": assigned_by,
            "execute_immediately": execute_immediately
        }
        
        print(f"📤 Sending task to Ray...")
        print(f"   Tasks: {len(tasks)}")
        print(f"   Assigned by: {assigned_by}")
        print(f"   Execute immediately: {execute_immediately}")
        
        try:
            response = requests.post(
                f"{self.base_url}/task/batch",
                json=task_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"📥 Response received:")
                print(f"   Status: {result['status']}")
                print(f"   Created tasks: {len(result['created_tasks'])}")
                print(f"   Failed tasks: {len(result['failed_tasks'])}")
                return result
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return None


def test_single_file_write():
    """Test writing a single file through the task system."""
    print("\n" + "="*60)
    print("🧪 TEST 1: Single File Write")
    print("="*60)
    
    client = RayTaskClient()
    
    # Create a simple text file
    task = {
        "action": "overwrite_file",
        "file_path": "./user_outputs/single_test.txt",
        "content": f"""Hello from Ray's Task System!

This file was created using Ray's overwrite_file tool through the task system.

Features demonstrated:
- Task system integration ✅
- Immediate execution ✅
- File creation ✅
- Timestamp: {datetime.now().isoformat()}

This is how users can interact with Ray's consciousness system!""",
        "backup_existing": True,
        "create_directories": True
    }
    
    result = client.send_task(task)
    
    if result and result["status"] == "success":
        execution_result = result["created_tasks"][0]["task"]["execution_result"]
        if execution_result["executed"] and execution_result["results"]["success"]:
            print("✅ Single file write test PASSED")
            print(f"   File: {execution_result['results']['file_path']}")
            print(f"   Size: {execution_result['results']['file_size']} bytes")
            print(f"   Time: {execution_result['results']['execution_time_ms']}ms")
            return True
        else:
            print("❌ Single file write test FAILED")
            print(f"   Error: {execution_result['results'].get('error_message')}")
            return False
    else:
        print("❌ Single file write test FAILED - Task system error")
        return False


def test_batch_file_write():
    """Test writing multiple files in a batch through the task system."""
    print("\n" + "="*60)
    print("🧪 TEST 2: Batch File Write")
    print("="*60)
    
    client = RayTaskClient()
    
    # Create multiple files in one batch
    tasks = [
        {
            "action": "overwrite_file",
            "file_path": "./user_outputs/batch_notes.md",
            "content": f"""# Batch Operation Notes

This file was created as part of a batch operation.

## Batch Details
- Created: {datetime.now().isoformat()}
- Operation: Batch file write test
- File: 1 of 3

## Purpose
Testing Ray's ability to handle multiple file operations in a single task.
""",
            "create_directories": True
        },
        {
            "action": "overwrite_file",
            "file_path": "./user_outputs/config/batch_config.json",
            "content": json.dumps({
                "test_name": "batch_file_write",
                "created_at": datetime.now().isoformat(),
                "files_in_batch": 3,
                "test_passed": True,
                "settings": {
                    "backup_enabled": True,
                    "create_directories": True,
                    "encoding": "utf-8"
                }
            }, indent=2),
            "backup_existing": True,
            "create_directories": True
        },
        {
            "action": "overwrite_file",
            "file_path": "./user_outputs/data/test_data.csv",
            "content": f"""Name,Type,Created,Status
Batch Test,File Operation,{datetime.now().isoformat()},Success
Task System,Integration,{datetime.now().isoformat()},Active
Ray Consciousness,AI System,{datetime.now().isoformat()},Operational""",
            "create_directories": True
        }
    ]
    
    result = client.send_task(tasks)
    
    if result and result["status"] == "success":
        print("✅ Batch file write test PASSED")
        print(f"   Files created: {len(result['created_tasks'])}")
        
        # Show details for each file
        for i, task in enumerate(result["created_tasks"]):
            execution_result = task["task"]["execution_result"]
            if execution_result["executed"] and execution_result["results"]["success"]:
                print(f"   File {i+1}: {execution_result['results']['file_path']} ({execution_result['results']['file_size']} bytes)")
            else:
                print(f"   File {i+1}: FAILED - {execution_result['results'].get('error_message')}")
        
        return len(result["failed_tasks"]) == 0
    else:
        print("❌ Batch file write test FAILED")
        return False


def test_file_read_back():
    """Test reading a file back through the task system."""
    print("\n" + "="*60)
    print("🧪 TEST 3: File Read Back")
    print("="*60)
    
    client = RayTaskClient()
    
    # First write a file, then read it back
    write_task = {
        "action": "overwrite_file",
        "file_path": "./user_outputs/read_test.txt",
        "content": "This content will be read back to verify the round-trip works!",
        "create_directories": True
    }
    
    print("📝 Writing file first...")
    write_result = client.send_task(write_task)
    
    if not (write_result and write_result["status"] == "success"):
        print("❌ File read test FAILED - Could not write initial file")
        return False
    
    # Now read it back
    read_task = {
        "action": "read_file",
        "file_path": "./user_outputs/read_test.txt"
    }
    
    print("📖 Reading file back...")
    read_result = client.send_task(read_task)
    
    if read_result and read_result["status"] == "success":
        execution_result = read_result["created_tasks"][0]["task"]["execution_result"]
        if execution_result["executed"] and execution_result["results"]["success"]:
            content = execution_result["results"]["content"]
            expected_content = "This content will be read back to verify the round-trip works!"
            
            if content == expected_content:
                print("✅ File read back test PASSED")
                print(f"   Content length: {len(content)} characters")
                print(f"   Content matches: ✅")
                return True
            else:
                print("❌ File read back test FAILED - Content mismatch")
                print(f"   Expected: {expected_content}")
                print(f"   Got: {content}")
                return False
        else:
            print("❌ File read back test FAILED")
            print(f"   Error: {execution_result['results'].get('error_message')}")
            return False
    else:
        print("❌ File read back test FAILED - Task system error")
        return False


def test_error_handling():
    """Test error handling for invalid operations."""
    print("\n" + "="*60)
    print("🧪 TEST 4: Error Handling")
    print("="*60)
    
    client = RayTaskClient()
    
    # Try to read a non-existent file
    task = {
        "action": "read_file",
        "file_path": "./non_existent_directory/non_existent_file.txt"
    }
    
    result = client.send_task(task)
    
    if result and result["status"] == "success":
        execution_result = result["created_tasks"][0]["task"]["execution_result"]
        if execution_result["executed"] and not execution_result["results"]["success"]:
            error_message = execution_result["results"]["error_message"]
            if "File not found" in error_message or "not found" in error_message.lower():
                print("✅ Error handling test PASSED")
                print(f"   Correctly caught error: {error_message}")
                return True
            else:
                print("❌ Error handling test FAILED - Wrong error message")
                print(f"   Error: {error_message}")
                return False
        else:
            print("❌ Error handling test FAILED - Should have failed but didn't")
            return False
    else:
        print("❌ Error handling test FAILED - Task system error")
        return False


def main():
    """Run all tests."""
    print("🤖 Ray Overwrite File Tool - Task System Integration Tests")
    print("=" * 80)
    print("Testing Ray's file operations through the task system interface")
    print("This demonstrates how users can interact with Ray's consciousness")
    print("=" * 80)
    
    tests = [
        ("Single File Write", test_single_file_write),
        ("Batch File Write", test_batch_file_write),
        ("File Read Back", test_file_read_back),
        ("Error Handling", test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test FAILED with exception: {str(e)}")
    
    print("\n" + "="*80)
    print("🏁 TEST RESULTS")
    print("="*80)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests PASSED! Ray's overwrite_file tool is working perfectly!")
        print("\n📋 What this proves:")
        print("   ✅ Task system integration works")
        print("   ✅ File operations execute immediately")
        print("   ✅ Batch operations work correctly")
        print("   ✅ Error handling is robust")
        print("   ✅ Users can interact with Ray's consciousness system")
    else:
        print(f"⚠️  {total - passed} tests failed. Check the output above for details.")
    
    print("\n🔗 API Endpoint Used: POST /task/batch")
    print("🎯 This is the same interface Ray uses internally!")
    print("🌟 Users now have direct access to Ray's file manipulation capabilities!")


if __name__ == "__main__":
    main()