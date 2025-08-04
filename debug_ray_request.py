#!/usr/bin/env python3
"""
Debug Ray's actual request to see what's missing.
"""

import requests
import json

# Test the exact request Ray should send with execute_immediately flag
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
    "execute_immediately": True  # This is the key missing field!
}

print("Testing Ray's corrected request with execute_immediately flag...")
print(f"Request payload: {json.dumps(correct_request, indent=2)}")

try:
    response = requests.post(
        "http://localhost:8000/tasks",
        json=correct_request,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Success!")
        
        # Check if the task has execution results
        created_tasks = result.get('created_tasks', [])
        if created_tasks:
            task = created_tasks[0]
            print(f"Task ID: {task['task_id']}")
            
            if 'execution_result' in task['task']:
                print("⚡ Task was executed immediately!")
                exec_result = task['task']['execution_result']
                print(f"Execution success: {exec_result.get('executed', False)}")
                
                if exec_result.get('results'):
                    results = exec_result['results']
                    print(f"Total results: {results.get('total_results', 0)}")
                    print(f"Files found: {results.get('files_found', 0)}")
                    print(f"Directories found: {results.get('directories_found', 0)}")
                    
                    # Show the actual directory listing
                    if exec_result.get('response', {}).get('search_result'):
                        search_result = exec_result['response']['search_result']
                        
                        print("\n📁 Directory Contents:")
                        
                        if search_result.get('directories_found'):
                            print("  Directories:")
                            for dir_info in search_result['directories_found'][:5]:  # Show first 5
                                print(f"    📂 {dir_info['name']}/")
                        
                        if search_result.get('files_found'):
                            print("  Files:")
                            for file_info in search_result['files_found'][:5]:  # Show first 5
                                print(f"    📄 {file_info['name']}")
                
            else:
                print("❌ Task was created but NOT executed immediately")
                print("   Missing execution_result in task")
    else:
        print(f"❌ Error: {response.text}")
    
except Exception as e:
    print(f"❌ Request failed: {e}")

# Also test what happens without the flag
print("\n" + "="*60)
print("Testing WITHOUT execute_immediately flag (Ray's current request)...")

request_without_flag = {
    "task": [
        {
            "action": "list_directory",
            "path": "./modules",
            "include_hidden": False,
            "assigned_by": "ray"
        }
    ],
    "assigned_by": "ray"
    # Missing execute_immediately flag - defaults to False
}

try:
    response = requests.post(
        "http://localhost:8000/tasks",
        json=request_without_flag,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        created_tasks = result.get('created_tasks', [])
        if created_tasks:
            task = created_tasks[0]
            
            if 'execution_result' in task['task']:
                print("⚠️  Task was executed immediately (unexpected)")
            else:
                print("✅ Task was created but NOT executed (as expected without flag)")
                print("   This is what Ray is currently experiencing")
    
except Exception as e:
    print(f"❌ Request failed: {e}")