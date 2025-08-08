#!/usr/bin/env python3
"""
Test Ray's exact task to see what's happening
"""

import requests
import json

def test_ray_current_task():
    """Test Ray's current task"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Ray's Current Task")
    print("=" * 40)
    
    # Ray's exact task
    ray_task = {
        "task": [
            {
                "action": "reflect",
                "question": "Has the task execution engine been restored?"
            }
        ],
        "assigned_by": "ray",
        "execute_immediately": True
    }
    
    print("📤 Sending Ray's exact task:")
    print(json.dumps(ray_task, indent=2))
    
    try:
        response = requests.post(f"{base_url}/tasks", json=ray_task, timeout=30)
        
        print(f"\n✅ Response Status: {response.status_code}")
        print(f"📥 Full Response:")
        print(response.text)
        
        if response.status_code == 200:
            result = response.json()
            print("\n🎯 Parsed Response:")
            print(json.dumps(result, indent=2))
            
            # Check for execution results
            created_tasks = result.get("created_tasks", [])
            for task in created_tasks:
                task_data = task.get('task', {})
                if 'execution_result' in task_data:
                    print(f"\n✅ EXECUTION RESULT FOUND!")
                    exec_result = task_data['execution_result']
                    print(f"Executed: {exec_result.get('executed')}")
                    if 'results' in exec_result:
                        print(f"Results: {exec_result['results']}")
                else:
                    print(f"\n❌ No execution result in task")
        else:
            print(f"❌ Error Status: {response.status_code}")
            print(f"Error Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - server might be processing")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - is server running?")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_server_status():
    """Check if server is responding"""
    
    base_url = "http://localhost:8000"
    
    print("\n🔍 Checking Server Status:")
    
    try:
        response = requests.get(f"{base_url}/heartbeat", timeout=5)
        print(f"Heartbeat Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Server Status: {data.get('status', 'unknown')}")
            print(f"Ray Working: {data.get('ray_working_on_request', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Server check failed: {e}")

def check_recent_logs():
    """Check recent task activity in logs"""
    
    print("\n📋 Checking Recent Task Activity:")
    
    try:
        with open("logs/heartbeat_detailed.jsonl", 'r') as f:
            lines = f.readlines()
            recent_lines = lines[-10:] if len(lines) > 10 else lines
            
            for line in recent_lines:
                try:
                    log_entry = json.loads(line.strip())
                    if 'task' in str(log_entry).lower():
                        timestamp = log_entry.get('timestamp', '')
                        event_type = log_entry.get('event_type', '')
                        action = log_entry.get('action', '')
                        print(f"  {timestamp} | {event_type} | {action}")
                except:
                    continue
                    
    except Exception as e:
        print(f"❌ Could not read logs: {e}")

if __name__ == "__main__":
    check_server_status()
    test_ray_current_task()
    check_recent_logs()