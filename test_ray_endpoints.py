#!/usr/bin/env python3
"""
Test both /task and /tasks endpoints to see which one Ray is using
"""

import requests
import json

def test_both_endpoints():
    """Test both singular and plural task endpoints"""
    
    base_url = "http://localhost:8000"
    
    ray_task = {
        "task": [
            {
                "action": "reflect",
                "question": "Testing endpoint routing - which endpoint am I using?"
            }
        ],
        "assigned_by": "ray"
    }
    
    print("🧪 Testing Both Task Endpoints")
    print("=" * 50)
    
    # Test 1: /tasks (correct endpoint)
    print("\n📤 Test 1: Sending to /tasks (plural - correct)")
    try:
        response = requests.post(f"{base_url}/tasks", json=ray_task, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS - Task executed on /tasks")
            print(f"Batch ID: {result.get('batch_id')}")
            
            # Check for execution results
            created_tasks = result.get("created_tasks", [])
            for task in created_tasks:
                if 'execution_result' in task.get('task', {}):
                    print(f"✅ Execution result found!")
                else:
                    print(f"❌ No execution result")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: /task (incorrect endpoint - singular)
    print("\n📤 Test 2: Sending to /task (singular - incorrect)")
    try:
        response = requests.post(f"{base_url}/task", json=ray_task, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS - Task redirected from /task")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Check if it's a redirect response or actual execution
            if 'batch_id' in result:
                print(f"✅ Redirected and executed successfully!")
            else:
                print(f"⚠️ Got response but might not be executed")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Root endpoint (/)
    print("\n📤 Test 3: Sending to / (root)")
    try:
        response = requests.post(f"{base_url}/", json=ray_task, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_both_endpoints()
    
    print("\n" + "=" * 50)
    print("🎯 Summary:")
    print("   • /tasks (plural) = Correct endpoint")
    print("   • /task (singular) = Should redirect to /tasks")
    print("   • / (root) = Fallback handler")
    print("   • Ray should use: POST /tasks")