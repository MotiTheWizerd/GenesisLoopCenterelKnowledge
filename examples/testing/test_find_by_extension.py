#!/usr/bin/env python3
"""
Test the find_by_extension action to make sure it works now.
"""

import requests
import json

# Test Ray's find_by_extension request
ray_request = {
    "task": [
        {
            "action": "find_by_extension",
            "path": "./modules",
            "file_extensions": ["py", "md"],
            "recursive": True,
            "assigned_by": "ray"
        }
    ],
    "assigned_by": "ray",
    "execute_immediately": True,
    "self_destruct": True
}

print("🧪 Testing find_by_extension action...")
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
                    
                    # Show some file examples
                    if exec_result.get('response', {}).get('search_result', {}).get('files_found'):
                        files = exec_result['response']['search_result']['files_found']
                        print(f"\n📄 First few files found:")
                        for file_info in files[:5]:
                            print(f"  - {file_info['name']} ({file_info.get('extension', 'no ext')})")
                else:
                    print("❌ No results in execution_result")
            else:
                print("❌ Task was created but NOT executed immediately")
                print("   Missing execution_result in task")
    else:
        print(f"❌ Error: {response.text}")
    
except Exception as e:
    print(f"❌ Request failed: {e}")

# Also test recent_files
print("\n" + "="*50)
print("🧪 Testing recent_files action...")

recent_request = {
    "task": [
        {
            "action": "recent_files",
            "path": "./modules",
            "recursive": True,
            "file_extensions": ["py"],
            "assigned_by": "ray"
        }
    ],
    "assigned_by": "ray",
    "execute_immediately": True,
    "self_destruct": True
}

try:
    response = requests.post(
        "http://localhost:8000/tasks",
        json=recent_request,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        created_tasks = result.get('created_tasks', [])
        if created_tasks:
            task = created_tasks[0]
            
            if 'execution_result' in task['task']:
                print("✅ recent_files action works!")
                exec_result = task['task']['execution_result']
                if exec_result.get('results'):
                    print(f"Found {exec_result['results'].get('total_results', 0)} recent files")
            else:
                print("❌ recent_files action failed")
    
except Exception as e:
    print(f"❌ recent_files test failed: {e}")

print("\n🎯 Both actions should now work for Ray!")