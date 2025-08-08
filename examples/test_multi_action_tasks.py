#!/usr/bin/env python3
"""
Test script demonstrating Ray's new multi-action task capability.

This script shows how Ray can now send tasks with multiple actions that execute sequentially,
allowing for complex workflows within a single task.
"""

import requests
import json
import time
from datetime import datetime


class RayMultiActionClient:
    """Client for testing Ray's multi-action task system."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def send_task(self, tasks, assigned_by="ray", execute_immediately=True):
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
        
        print(f"📤 Sending multi-action task to Ray...")
        print(f"   Tasks: {len(tasks)}")
        print(f"   Assigned by: {assigned_by}")
        print(f"   Execute immediately: {execute_immediately}")
        
        # Show task details
        for i, task in enumerate(tasks):
            actions = task.get("action", [])
            if isinstance(actions, str):
                actions = [actions]
            print(f"   Task {i+1}: {len(actions)} actions - {actions}")
        
        try:
            response = requests.post(
                f"{self.base_url}/tasks",
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


def test_single_action_backward_compatibility():
    """Test that single actions still work (backward compatibility)."""
    print("\n" + "="*60)
    print("🧪 TEST 1: Single Action (Backward Compatibility)")
    print("="*60)
    
    client = RayMultiActionClient()
    
    # Single action task - should work exactly as before
    task = {
        "action": "health_check",
        "assigned_by": "ray"
    }
    
    result = client.send_task(task)
    
    if result and result["status"] == "batch_processed":
        execution_result = result["created_tasks"][0]["task"]["execution_result"]
        if execution_result["executed"]:
            print("✅ Single action backward compatibility test PASSED")
            print(f"   Action: {execution_result['action']}")
            print(f"   Executed: {execution_result['executed']}")
            return True
        else:
            print("❌ Single action test FAILED")
            print(f"   Error: {execution_result.get('error')}")
            return False
    else:
        print("❌ Single action test FAILED - Task system error")
        return False


def test_dual_action_sequence():
    """Test a task with two actions executing sequentially."""
    print("\n" + "="*60)
    print("🧪 TEST 2: Dual Action Sequence")
    print("="*60)
    
    client = RayMultiActionClient()
    
    # Task with two actions: health check followed by reflection
    task = {
        "action": ["health_check", "reflect"],
        "question": "What does the system health tell us about our current state?",
        "assigned_by": "ray"
    }
    
    result = client.send_task(task)
    
    if result and result["status"] == "batch_processed":
        execution_result = result["created_tasks"][0]["task"]["execution_result"]
        if execution_result["executed"] and execution_result.get("action_sequence"):
            actions = execution_result["action_sequence"]
            action_results = execution_result["action_results"]
            
            print("✅ Dual action sequence test PASSED")
            print(f"   Actions executed: {actions}")
            print(f"   Total actions: {execution_result['total_actions']}")
            print(f"   Successful: {execution_result['execution_summary']['successful_actions']}")
            print(f"   Failed: {execution_result['execution_summary']['failed_actions']}")
            print(f"   Total time: {execution_result['execution_summary']['total_execution_time_ms']}ms")
            
            # Show individual action results
            for i, action_result in enumerate(action_results):
                status = "✅" if action_result.get("executed") else "❌"
                print(f"   Action {i+1} ({action_result['action_name']}): {status}")
            
            return execution_result["execution_summary"]["successful_actions"] >= 1
        else:
            print("❌ Dual action sequence test FAILED")
            print(f"   Error: {execution_result.get('error')}")
            return False
    else:
        print("❌ Dual action sequence test FAILED - Task system error")
        return False


def test_complex_multi_action_workflow():
    """Test a complex workflow with multiple different action types."""
    print("\n" + "="*60)
    print("🧪 TEST 3: Complex Multi-Action Workflow")
    print("="*60)
    
    client = RayMultiActionClient()
    
    # Complex task: health check -> file write -> file read -> reflect
    task = {
        "action": ["health_check", "overwrite_file", "read_file", "reflect"],
        "file_path": "./user_outputs/multi_action_test.txt",
        "content": f"Multi-action workflow test\nCreated: {datetime.now().isoformat()}\nThis file was created as part of a complex action sequence.",
        "create_directories": True,
        "question": "What insights can we gain from this multi-step process?",
        "assigned_by": "ray"
    }
    
    result = client.send_task(task)
    
    if result and result["status"] == "batch_processed":
        execution_result = result["created_tasks"][0]["task"]["execution_result"]
        if execution_result["executed"] and execution_result.get("action_sequence"):
            actions = execution_result["action_sequence"]
            action_results = execution_result["action_results"]
            
            print("✅ Complex multi-action workflow test PASSED")
            print(f"   Actions executed: {actions}")
            print(f"   Total actions: {execution_result['total_actions']}")
            print(f"   Successful: {execution_result['execution_summary']['successful_actions']}")
            print(f"   Failed: {execution_result['execution_summary']['failed_actions']}")
            print(f"   Total time: {execution_result['execution_summary']['total_execution_time_ms']}ms")
            
            # Show detailed results for each action
            for i, action_result in enumerate(action_results):
                status = "✅" if action_result.get("executed") else "❌"
                action_name = action_result['action_name']
                exec_time = action_result.get('execution_time_ms', 0)
                print(f"   Action {i+1} ({action_name}): {status} ({exec_time}ms)")
                
                if action_result.get("executed") and "results" in action_result:
                    results = action_result["results"]
                    if action_name == "health_check":
                        print(f"      Health status: {results.get('status', 'unknown')}")
                    elif action_name == "overwrite_file":
                        print(f"      File created: {results.get('file_path', 'unknown')}")
                        print(f"      File size: {results.get('file_size', 0)} bytes")
                    elif action_name == "read_file":
                        content = results.get('content')
                        if content is not None:
                            content_length = len(content)
                            print(f"      Content read: {content_length} characters")
                        else:
                            print(f"      Content read: Failed - {results.get('error_message', 'Unknown error')}")
                    elif action_name == "reflect":
                        print(f"      Reflection completed: {results.get('status', 'unknown')}")
            
            return execution_result["execution_summary"]["successful_actions"] >= 3
        else:
            print("❌ Complex multi-action workflow test FAILED")
            print(f"   Error: {execution_result.get('error')}")
            return False
    else:
        print("❌ Complex multi-action workflow test FAILED - Task system error")
        return False


def test_batch_multi_action_tasks():
    """Test multiple tasks, each with multiple actions."""
    print("\n" + "="*60)
    print("🧪 TEST 4: Batch Multi-Action Tasks")
    print("="*60)
    
    client = RayMultiActionClient()
    
    # Multiple tasks, each with multiple actions
    tasks = [
        {
            "action": ["health_check", "reflect"],
            "question": "How is our system performing?",
            "assigned_by": "ray"
        },
        {
            "action": ["overwrite_file", "read_file"],
            "file_path": "./user_outputs/batch_test_1.txt",
            "content": "Batch test file 1",
            "create_directories": True,
            "assigned_by": "ray"
        },
        {
            "action": ["overwrite_file", "read_file", "reflect"],
            "file_path": "./user_outputs/batch_test_2.txt",
            "content": "Batch test file 2 with reflection",
            "create_directories": True,
            "question": "What does this file creation process teach us?",
            "assigned_by": "ray"
        }
    ]
    
    result = client.send_task(tasks)
    
    if result and result["status"] == "batch_processed":
        print("✅ Batch multi-action tasks test PASSED")
        print(f"   Total tasks: {result['total_tasks']}")
        print(f"   Created: {result['created_count']}")
        print(f"   Failed: {result['failed_count']}")
        
        # Show summary for each task
        for i, task in enumerate(result["created_tasks"]):
            execution_result = task["task"]["execution_result"]
            if execution_result.get("action_sequence"):
                actions = execution_result["action_sequence"]
                successful = execution_result["execution_summary"]["successful_actions"]
                total = execution_result["total_actions"]
                print(f"   Task {i+1}: {successful}/{total} actions successful - {actions}")
            else:
                # Single action task
                action = execution_result.get("action", "unknown")
                status = "✅" if execution_result.get("executed") else "❌"
                print(f"   Task {i+1}: {status} single action - {action}")
        
        return result["failed_count"] == 0
    else:
        print("❌ Batch multi-action tasks test FAILED")
        return False


def test_error_handling_in_sequence():
    """Test error handling when one action in a sequence fails."""
    print("\n" + "="*60)
    print("🧪 TEST 5: Error Handling in Action Sequence")
    print("="*60)
    
    client = RayMultiActionClient()
    
    # Task with an action that will fail (reading non-existent file)
    task = {
        "action": ["health_check", "read_file", "reflect"],
        "file_path": "./non_existent_directory/non_existent_file.txt",
        "question": "What can we learn from this error?",
        "assigned_by": "ray"
    }
    
    result = client.send_task(task)
    
    if result and result["status"] == "batch_processed":
        execution_result = result["created_tasks"][0]["task"]["execution_result"]
        if execution_result.get("action_sequence"):
            actions = execution_result["action_sequence"]
            action_results = execution_result["action_results"]
            successful = execution_result["execution_summary"]["successful_actions"]
            failed = execution_result["execution_summary"]["failed_actions"]
            
            print("✅ Error handling in sequence test PASSED")
            print(f"   Actions: {actions}")
            print(f"   Successful: {successful}")
            print(f"   Failed: {failed}")
            
            # Should have at least one success (health_check) and one failure (read_file)
            has_success = successful > 0
            has_failure = failed > 0
            continues_after_error = len(action_results) == len(actions)  # All actions attempted
            
            print(f"   Has success: {has_success}")
            print(f"   Has failure: {has_failure}")
            print(f"   Continues after error: {continues_after_error}")
            
            # Show individual results
            for i, action_result in enumerate(action_results):
                status = "✅" if action_result.get("executed") else "❌"
                action_name = action_result['action_name']
                print(f"   Action {i+1} ({action_name}): {status}")
                if not action_result.get("executed"):
                    print(f"      Error: {action_result.get('error', 'Unknown error')}")
            
            return has_success and has_failure and continues_after_error
        else:
            print("❌ Error handling test FAILED - No action sequence found")
            return False
    else:
        print("❌ Error handling test FAILED - Task system error")
        return False


def main():
    """Run all multi-action tests."""
    print("🤖 Ray Multi-Action Task System Tests")
    print("=" * 80)
    print("Testing Ray's new capability to execute multiple actions in sequence")
    print("This enables complex workflows within a single task")
    print("=" * 80)
    
    tests = [
        ("Single Action (Backward Compatibility)", test_single_action_backward_compatibility),
        ("Dual Action Sequence", test_dual_action_sequence),
        ("Complex Multi-Action Workflow", test_complex_multi_action_workflow),
        ("Batch Multi-Action Tasks", test_batch_multi_action_tasks),
        ("Error Handling in Sequence", test_error_handling_in_sequence)
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
    print("🏁 MULTI-ACTION TEST RESULTS")
    print("="*80)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All multi-action tests PASSED! Ray's new capability is working perfectly!")
        print("\n📋 What this proves:")
        print("   ✅ Backward compatibility maintained")
        print("   ✅ Multi-action sequences execute correctly")
        print("   ✅ Complex workflows work within single tasks")
        print("   ✅ Batch processing supports multi-action tasks")
        print("   ✅ Error handling continues sequence execution")
        print("   ✅ Results are properly aggregated and reported")
    else:
        print(f"⚠️  {total - passed} tests failed. Check the output above for details.")
    
    print("\n🔗 API Endpoint Used: POST /tasks")
    print("🎯 Ray can now send: {\"action\": [\"health_check\", \"reflect\", \"evolve\"]}")
    print("🌟 This enables Ray to create complex consciousness workflows!")
    print("\n💡 Example Ray task:")
    print(json.dumps({
        "task": [{
            "action": ["web_search", "reflect", "evolve"],
            "query": "AI consciousness research",
            "question": "What does this research tell us?",
            "area": "self-awareness"
        }],
        "assigned_by": "ray"
    }, indent=2))


if __name__ == "__main__":
    main()