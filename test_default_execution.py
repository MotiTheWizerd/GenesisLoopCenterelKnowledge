#!/usr/bin/env python3
"""
Test that execute_immediately defaults to True
"""

import requests
import json

def test_default_execution():
    """Test task without explicit execute_immediately flag"""
    
    base_url = "http://localhost:8000"
    
    # Task WITHOUT execute_immediately flag - should default to True now
    ray_task = {
        "task": [
            {
                "action": "reflect",
                "question": "Testing default execution - am I being executed immediately?"
            }
        ],
        "assigned_by": "ray"
        # Note: NO execute_immediately field - should default to True
    }
    
    print("🧪 Testing Default Execution Behavior")
    print("=" * 50)
    print("📤 Sending task WITHOUT execute_immediately flag:")
    print(json.dumps(ray_task, indent=2))
    
    try:
        response = requests.post(f"{base_url}/tasks", json=ray_task, timeout=15)
        
        print(f"\n✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("📥 Response received:")
            
            # Check if tasks were executed
            created_tasks = result.get("created_tasks", [])
            for i, task in enumerate(created_tasks):
                print(f"\n🎯 Task {i+1}:")
                print(f"   ID: {task.get('task_id')}")
                
                task_data = task.get('task', {})
                if 'execution_result' in task_data:
                    print(f"   ✅ EXECUTED BY DEFAULT!")
                    exec_result = task_data['execution_result']
                    print(f"   Success: {exec_result.get('executed', False)}")
                    if 'results' in exec_result:
                        results = exec_result['results']
                        reflection = results.get('reflection', 'No reflection')
                        print(f"   Reflection: {reflection}")
                else:
                    print(f"   ❌ NOT EXECUTED - Default didn't work")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_default_execution()
    
    print("\n" + "=" * 50)
    print("🎯 Expected Result:")
    print("   • Task should execute immediately by default")
    print("   • No need for Ray to specify execute_immediately: true")
    print("   • Should see execution_result in response")