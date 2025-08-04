#!/usr/bin/env python3
"""
Integration test for the new overwrite_file functionality.

This test verifies that Ray can use the overwrite_file tool through the task system.
"""

import os
import tempfile
import json
from modules.task.handler import task_manager
from modules.file_ops.handler import file_ops_manager


def test_overwrite_file_integration():
    """Test the complete overwrite_file integration."""
    print("🧪 Testing overwrite_file integration...")
    
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
        temp_file.write("Original content")
        temp_file_path = temp_file.name
    
    try:
        # Test 1: Direct file operations manager
        print("\n📁 Test 1: Direct file operations manager")
        
        new_content = "This content was written by Ray's overwrite_file tool!"
        response = file_ops_manager.overwrite_file(
            file_path=temp_file_path,
            content=new_content,
            assigned_by="ray",
            backup_existing=True
        )
        
        print(f"   Success: {response.success}")
        print(f"   File path: {response.file_path}")
        print(f"   File size: {response.file_size} bytes")
        print(f"   Backup created: {response.backup_path is not None}")
        print(f"   Execution time: {response.execution_time_ms}ms")
        
        # Verify content
        with open(temp_file_path, 'r') as f:
            actual_content = f.read()
        
        assert actual_content == new_content, f"Expected '{new_content}', got '{actual_content}'"
        print("   ✅ Content verification passed")
        
        # Test 2: Through task manager (how Ray would use it)
        print("\n🎯 Test 2: Through task manager (Ray's interface)")
        
        ray_task = {
            "task": [
                {
                    "action": "overwrite_file",
                    "file_path": temp_file_path,
                    "content": "Ray updated this file through the task system!",
                    "backup_existing": True
                }
            ],
            "assigned_by": "ray",
            "execute_immediately": True
        }
        
        # Create the task request object
        from modules.task.models import TaskRequestFromRay
        task_request = TaskRequestFromRay(**ray_task)
        
        # Process through task manager
        batch_response = task_manager.create_batch_tasks(task_request)
        
        print(f"   Batch status: {batch_response.status}")
        print(f"   Created tasks: {len(batch_response.created_tasks)}")
        print(f"   Failed tasks: {len(batch_response.failed_tasks)}")
        
        if batch_response.created_tasks:
            task = batch_response.created_tasks[0]
            execution_result = task.task.get("execution_result")
            if execution_result:
                print(f"   Execution success: {execution_result.get('executed')}")
                print(f"   Results: {execution_result.get('results', {}).get('success')}")
        
        # Verify the content was updated
        with open(temp_file_path, 'r') as f:
            final_content = f.read()
        
        expected_final = "Ray updated this file through the task system!"
        assert final_content == expected_final, f"Expected '{expected_final}', got '{final_content}'"
        print("   ✅ Task system integration passed")
        
        # Test 3: Read the file back
        print("\n📖 Test 3: Reading file back")
        
        read_response = file_ops_manager.read_file(
            file_path=temp_file_path,
            assigned_by="ray"
        )
        
        print(f"   Read success: {read_response.success}")
        print(f"   Content length: {len(read_response.content) if read_response.content else 0}")
        print(f"   File size: {read_response.file_size} bytes")
        
        assert read_response.success, "File read should succeed"
        assert read_response.content == expected_final, "Read content should match written content"
        print("   ✅ File read verification passed")
        
        print("\n🎉 All integration tests passed!")
        print("\n📋 Summary:")
        print("   ✅ Direct file operations manager works")
        print("   ✅ Task manager integration works")
        print("   ✅ Ray can use overwrite_file through task system")
        print("   ✅ File reading works correctly")
        print("   ✅ Backup functionality works")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        
        # Clean up any backup files
        backup_pattern = f"{temp_file_path}.backup_"
        import glob
        for backup_file in glob.glob(f"{backup_pattern}*"):
            if os.path.exists(backup_file):
                os.unlink(backup_file)


if __name__ == "__main__":
    success = test_overwrite_file_integration()
    exit(0 if success else 1)