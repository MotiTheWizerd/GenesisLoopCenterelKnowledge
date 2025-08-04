#!/usr/bin/env python3
"""
Test all directory actions to ensure they work with the task system.
"""

import requests
import json

def test_action(action_name, task_data):
    """Test a single directory action."""
    request = {
        "task": [task_data],
        "assigned_by": "ray",
        "execute_immediately": True,
        "self_destruct": True
    }
    
    try:
        response = requests.post("http://localhost:8000/tasks", json=request, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            created_tasks = result.get('created_tasks', [])
            if created_tasks and 'execution_result' in created_tasks[0]['task']:
                exec_result = created_tasks[0]['task']['execution_result']
                if exec_result.get('executed'):
                    return True, exec_result.get('results', {}).get('total_results', 0)
                else:
                    return False, exec_result.get('error', 'Unknown error')
        
        return False, f"HTTP {response.status_code}: {response.text[:100]}"
    
    except Exception as e:
        return False, str(e)

print("🧪 Testing All Directory Actions")
print("=" * 50)

# Test cases for each action
test_cases = [
    ("list_directory", {
        "action": "list_directory",
        "path": "./modules",
        "include_hidden": False,
        "assigned_by": "ray"
    }),
    
    ("find_files", {
        "action": "find_files",
        "path": "./modules",
        "query": "*.py",
        "recursive": True,
        "assigned_by": "ray"
    }),
    
    ("search_content", {
        "action": "search_content",
        "path": "./modules",
        "query": "task",
        "file_extensions": ["py"],
        "recursive": True,
        "assigned_by": "ray"
    }),
    
    ("explore_tree", {
        "action": "explore_tree",
        "path": "./modules",
        "max_depth": 2,
        "include_hidden": False,
        "assigned_by": "ray"
    }),
    
    ("get_file_info", {
        "action": "get_file_info",
        "path": "./modules/task/handler.py",
        "assigned_by": "ray"
    }),
    
    ("find_by_extension", {
        "action": "find_by_extension",
        "path": "./modules",
        "file_extensions": ["py", "md"],
        "recursive": True,
        "assigned_by": "ray"
    }),
    
    ("recent_files", {
        "action": "recent_files",
        "path": "./modules",
        "recursive": True,
        "file_extensions": ["py"],
        "assigned_by": "ray"
    })
]

# Run tests
results = []
for action_name, task_data in test_cases:
    print(f"Testing {action_name}...", end=" ")
    success, result = test_action(action_name, task_data)
    
    if success:
        print(f"✅ SUCCESS ({result} results)")
        results.append((action_name, True, result))
    else:
        print(f"❌ FAILED: {result}")
        results.append((action_name, False, result))

# Summary
print("\n" + "=" * 50)
print("📊 Test Results Summary")
print("=" * 50)

passed = 0
failed = 0

for action_name, success, result in results:
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status:8} {action_name:20} {result}")
    if success:
        passed += 1
    else:
        failed += 1

print(f"\n🎯 Total: {passed} passed, {failed} failed")

if failed == 0:
    print("🎉 All directory actions are working perfectly!")
    print("Ray can now use all directory operations through the task system!")
else:
    print(f"⚠️  {failed} actions need attention")

print("\n📝 Ray can now use these working actions:")
for action_name, success, result in results:
    if success:
        print(f"  ✅ {action_name}")