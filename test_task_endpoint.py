#!/usr/bin/env python3
"""
Test the task endpoint to see if it's working properly
"""

import requests
import json
import time

def test_task_endpoint():
    """Test the task endpoint with Ray's example"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Task Endpoint")
    print("=" * 40)
    
    # Ray's example task
    ray_task = {
        "task": [
            {
                "action": "web_scrape",
                "url": "https://example.dev",
                "extract_text": True,
                "extract_links": True,
                "extract_images": False,
                "max_content_length": 50000,
                "timeout": 30,
                "follow_redirects": True
            },
            {
                "action": "reflect",
                "question": "Did this domain offer any signal, value, or pattern worth remembering?"
            }
        ],
        "assigned_by": "ray"
    }
    
    print("📤 Sending Ray's task to /tasks endpoint:")
    print(json.dumps(ray_task, indent=2))
    
    try:
        # Send to correct endpoint
        response = requests.post(f"{base_url}/tasks", json=ray_task, timeout=30)
        
        print(f"\n✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("📥 Response received:")
            print(json.dumps(result, indent=2))
            
            # Check if tasks were created
            if result.get("status") == "batch_processed":
                print(f"\n🎯 Task Processing Results:")
                print(f"   Batch ID: {result.get('batch_id')}")
                print(f"   Total tasks: {result.get('total_tasks')}")
                print(f"   Created: {result.get('created_count')}")
                print(f"   Failed: {result.get('failed_count')}")
                
                # Show created tasks
                created_tasks = result.get("created_tasks", [])
                for i, task in enumerate(created_tasks):
                    print(f"\n   Task {i+1}:")
                    print(f"     ID: {task.get('task_id')}")
                    print(f"     Action: {task.get('task', {}).get('action')}")
                    print(f"     Timestamp: {task.get('timestamp')}")
                
                return result.get('batch_id')
            else:
                print(f"❌ Unexpected status: {result.get('status')}")
        else:
            print(f"❌ Error response:")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out after 30 seconds")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def check_task_status():
    """Check the task manager status"""
    
    base_url = "http://localhost:8000"
    
    print("\n🔍 Checking Task Manager Status:")
    
    try:
        response = requests.get(f"{base_url}/tasks/status")
        
        if response.status_code == 200:
            status = response.json()
            print(json.dumps(status, indent=2))
        else:
            print(f"❌ Status check failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error checking status: {e}")

def check_active_tasks():
    """Check active tasks"""
    
    base_url = "http://localhost:8000"
    
    print("\n📋 Checking Active Tasks:")
    
    try:
        response = requests.get(f"{base_url}/tasks/list")
        
        if response.status_code == 200:
            tasks = response.json()
            active_count = tasks.get("active_tasks_count", 0)
            print(f"Active tasks count: {active_count}")
            
            if active_count > 0:
                print("Active tasks:")
                for task in tasks.get("active_tasks", []):
                    print(f"  - ID: {task.get('task_id')}")
                    print(f"    Action: {task.get('task', {}).get('action')}")
                    print(f"    Assigned by: {task.get('assigned_by')}")
                    print(f"    Timestamp: {task.get('timestamp')}")
                    print()
            else:
                print("No active tasks found")
                
        else:
            print(f"❌ Failed to get active tasks: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error checking active tasks: {e}")

def test_simple_task():
    """Test a simple task to see if the basic flow works"""
    
    base_url = "http://localhost:8000"
    
    print("\n🧪 Testing Simple Task:")
    
    simple_task = {
        "task": [
            {
                "action": "reflect",
                "question": "What is consciousness?"
            }
        ],
        "assigned_by": "test"
    }
    
    print("📤 Sending simple task:")
    print(json.dumps(simple_task, indent=2))
    
    try:
        response = requests.post(f"{base_url}/tasks", json=simple_task)
        
        print(f"\n✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("📥 Simple task response:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Error response:")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Test the task endpoint
    batch_id = test_task_endpoint()
    
    # Check task manager status
    check_task_status()
    
    # Check active tasks
    check_active_tasks()
    
    # Test simple task
    test_simple_task()
    
    print("\n" + "=" * 40)
    print("🎯 Key Findings:")
    print("   • Task endpoint is at /tasks (plural)")
    print("   • Check if tasks are being created and stored")
    print("   • Check if task execution is working")
    print("   • Monitor logs for task processing")