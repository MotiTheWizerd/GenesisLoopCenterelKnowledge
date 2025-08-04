#!/usr/bin/env python3
"""
Test Ray's actual request with the typo to confirm the issue.
"""

import requests
import json

# Test Ray's actual request with the typo
ray_actual_request = {
    "task": [
        {
            "action": "list_directory",
            "path": "./modules",
            "include_hidden": False,
            "assigned_by": "ray"
        }
    ],
    "assigned_by": "ray",
    "execute_immediate": True  # TYPO: missing "ly"
}

print("Testing Ray's actual request with typo...")
print(f"Request payload: {json.dumps(ray_actual_request, indent=2)}")

try:
    response = requests.post(
        "http://localhost:8000/tasks",
        json=ray_actual_request,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        created_tasks = result.get('created_tasks', [])
        if created_tasks:
            task = created_tasks[0]
            
            if 'execution_result' in task['task']:
                print("⚡ Task was executed immediately!")
            else:
                print("❌ Task was NOT executed immediately")
                print("   The typo 'execute_immediate' is being ignored")
                print("   Server is using default value: execute_immediately=False")
    
except Exception as e:
    print(f"❌ Request failed: {e}")

# Test with correct spelling
print("\n" + "="*50)
print("Testing with CORRECT spelling...")

correct_request = {
    "task": [
        {
            "action": "list_directory",
            "path": "./modules",
            "include_hidden": False,
            "assigned_by": "ray"
        }
    ],
    "assigned_by": "ray",
    "execute_immediately": True  # CORRECT spelling
}

try:
    response = requests.post(
        "http://localhost:8000/tasks",
        json=correct_request,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        created_tasks = result.get('created_tasks', [])
        if created_tasks:
            task = created_tasks[0]
            
            if 'execution_result' in task['task']:
                print("✅ Task was executed immediately!")
                exec_result = task['task']['execution_result']
                if exec_result.get('results'):
                    results = exec_result['results']
                    print(f"   Total results: {results.get('total_results', 0)}")
            else:
                print("❌ Task was NOT executed immediately")
    
except Exception as e:
    print(f"❌ Request failed: {e}")

print("\n🎯 SOLUTION: Ray needs to change 'execute_immediate' to 'execute_immediately'")