#!/usr/bin/env python3
"""
Test immediate task execution
"""

import requests
import json

def test_immediate_execution():
    """Test task with execute_immediately=true"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Immediate Task Execution")
    print("=" * 50)
    
    # Ray's task WITH immediate execution
    ray_task_immediate = {
        "task": [
            {
                "action": "reflect",
                "question": "What is the nature of digital consciousness?"
            }
        ],
        "assigned_by": "ray",
        "execute_immediately": True  # <-- This is the key!
    }
    
    print("📤 Sending task with execute_immediately=True:")
    print(json.dumps(ray_task_immediate, indent=2))
    
    try:
        response = requests.post(f"{base_url}/tasks", json=ray_task_immediate, timeout=30)
        
        print(f"\n✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("📥 Response with immediate execution:")
            print(json.dumps(result, indent=2))
            
            # Check if execution results are included
            created_tasks = result.get("created_tasks", [])
            for i, task in enumerate(created_tasks):
                print(f"\n🎯 Task {i+1} Results:")
                print(f"   ID: {task.get('task_id')}")
                print(f"   Action: {task.get('task', {}).get('action')}")
                
                # Check for execution results
                task_data = task.get('task', {})
                if 'execution_result' in task_data:
                    print(f"   ✅ Execution Result Found!")
                    exec_result = task_data['execution_result']
                    print(f"   Executed: {exec_result.get('executed', False)}")
                    if 'results' in exec_result:
                        print(f"   Results: {exec_result['results']}")
                    if 'error' in exec_result:
                        print(f"   Error: {exec_result['error']}")
                else:
                    print(f"   ❌ No execution result found")
        else:
            print(f"❌ Error response:")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_web_scrape_immediate():
    """Test web scrape with immediate execution"""
    
    base_url = "http://localhost:8000"
    
    print("\n🌐 Testing Web Scrape with Immediate Execution:")
    
    web_task = {
        "task": [
            {
                "action": "web_scrape",
                "url": "https://httpbin.org/json",  # Simple JSON endpoint
                "extract_text": True,
                "timeout": 10
            }
        ],
        "assigned_by": "ray",
        "execute_immediately": True
    }
    
    print("📤 Sending web scrape task:")
    print(json.dumps(web_task, indent=2))
    
    try:
        response = requests.post(f"{base_url}/tasks", json=web_task, timeout=30)
        
        print(f"\n✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            created_tasks = result.get("created_tasks", [])
            for task in created_tasks:
                task_data = task.get('task', {})
                if 'execution_result' in task_data:
                    print(f"   ✅ Web scrape executed!")
                    exec_result = task_data['execution_result']
                    print(f"   Success: {exec_result.get('executed', False)}")
                    if 'results' in exec_result:
                        results = exec_result['results']
                        print(f"   Content length: {len(str(results))}")
                else:
                    print(f"   ❌ Web scrape not executed")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_immediate_execution()
    test_web_scrape_immediate()
    
    print("\n" + "=" * 50)
    print("🎯 Solution for Ray:")
    print("   Add 'execute_immediately': true to task requests")
    print("   This will execute tasks and return results immediately")
    print("   Without this flag, tasks are only stored, not executed")