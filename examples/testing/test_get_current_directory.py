#!/usr/bin/env python3
"""
Test the new get_current_directory action.
"""

import requests
import json
import os

# Test Ray's get_current_directory request
ray_request = {
    "task": [
        {
            "action": "get_current_directory",
            "assigned_by": "ray"
        }
    ],
    "assigned_by": "ray",
    "execute_immediately": True,
    "self_destruct": True
}

print("🧪 Testing get_current_directory action...")
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
                    
                    # Show current directory info
                    if exec_result.get('response', {}).get('search_result', {}).get('directories_found'):
                        dirs = exec_result['response']['search_result']['directories_found']
                        if dirs:
                            current_dir = dirs[0]
                            print(f"\n📁 Current Directory Information:")
                            print(f"   Name: {current_dir['name']}")
                            print(f"   Path: {current_dir['path']}")
                            print(f"   Files: {current_dir['file_count']}")
                            print(f"   Subdirectories: {current_dir['subdirectory_count']}")
                            print(f"   Total Size: {current_dir['total_size']} bytes")
                            print(f"   Modified: {current_dir['modified_time']}")
                            
                            # Compare with Python's os.getcwd()
                            actual_cwd = os.getcwd()
                            print(f"\n🔍 Verification:")
                            print(f"   Python os.getcwd(): {actual_cwd}")
                            print(f"   Ray's result: {current_dir['path']}")
                            
                            if current_dir['path'] == actual_cwd:
                                print("   ✅ Paths match perfectly!")
                            else:
                                print("   ⚠️  Paths don't match")
                else:
                    print("❌ No results in execution_result")
                    if exec_result.get('error'):
                        print(f"   Error: {exec_result['error']}")
                    print(f"   Full exec_result: {exec_result}")
            else:
                print("❌ Task was created but NOT executed immediately")
                print("   Missing execution_result in task")
    else:
        print(f"❌ Error: {response.text}")
    
except Exception as e:
    print(f"❌ Request failed: {e}")

print("\n🎯 get_current_directory allows Ray to know where she is!")
print("📍 Perfect for navigation and understanding her current location in the file system.")