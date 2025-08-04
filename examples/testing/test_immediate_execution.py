#!/usr/bin/env python3
"""
Test script to verify immediate task execution works.
"""

import requests
import json

# Test Ray's directory request with immediate execution
ray_request = {
    "task": [
        {
            "action": "list_directory",
            "path": "./modules",
            "include_hidden": False,
            "assigned_by": "ray"
        }
    ],
    "assigned_by": "ray",
    "execute_immediately": True
}

print("Testing Ray's directory request with immediate execution...")
print(f"Request payload: {json.dumps(ray_request, indent=2)}")

try:
    response = requests.post(
        "http://localhost:8000/tasks",
        json=ray_request,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Success!")
        print(f"Response keys: {list(result.keys())}")
        
        # Handle different response formats
        data = result.get('data', result)
        print(f"Batch ID: {data.get('batch_id', 'N/A')}")
        print(f"Created tasks: {data.get('created_count', len(data.get('created_tasks', [])))}")
        
        # Check if the task has execution results
        created_tasks = data.get('created_tasks', [])
        if created_tasks:
            task = created_tasks[0]
            if 'execution_result' in task['task']:
                print("⚡ Task was executed immediately!")
                exec_result = task['task']['execution_result']
                print(f"Execution success: {exec_result.get('executed', False)}")
                if exec_result.get('results'):
                    print(f"Results found: {exec_result['results'].get('total_results', 0)}")
            else:
                print("⚠️  Task was created but not executed immediately")
    else:
        print(f"❌ Error: {response.text}")
    
except Exception as e:
    print(f"❌ Request failed: {e}")

# Test without immediate execution for comparison
print("\n" + "="*50)
print("Testing without immediate execution...")

ray_request_no_exec = {
    "task": [
        {
            "action": "list_directory", 
            "path": "./modules",
            "include_hidden": False,
            "assigned_by": "ray"
        }
    ],
    "assigned_by": "ray",
    "execute_immediately": False
}

try:
    response = requests.post(
        "http://localhost:8000/tasks",
        json=ray_request_no_exec,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Success!")
        
        # Handle different response formats
        data = result.get('data', result)
        
        # Check if the task has execution results
        created_tasks = data.get('created_tasks', [])
        if created_tasks:
            task = created_tasks[0]
            if 'execution_result' in task['task']:
                print("⚠️  Task was executed immediately (unexpected)")
            else:
                print("✅ Task was created but not executed (as expected)")
    else:
        print(f"❌ Error: {response.text}")
    
except Exception as e:
    print(f"❌ Request failed: {e}")