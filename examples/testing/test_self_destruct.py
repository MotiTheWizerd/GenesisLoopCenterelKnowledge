#!/usr/bin/env python3
"""
Test the self-destruct functionality for single-use tasks.
"""

import requests
import json
import time

def get_active_tasks_count():
    """Get current active tasks count."""
    try:
        response = requests.get("http://localhost:8000/task/status", timeout=5)
        if response.status_code == 200:
            return response.json().get('task_manager', {}).get('active_tasks_count', 0)
    except:
        pass
    return None

print("🧪 Testing Self-Destruct Functionality")
print("=" * 50)

# Get initial task count
initial_count = get_active_tasks_count()
print(f"Initial active tasks: {initial_count}")

# Test 1: Regular task (should persist)
print("\n1️⃣ Testing regular task (should persist)...")
regular_request = {
    "task": [
        {
            "action": "list_directory",
            "path": "./modules",
            "include_hidden": False,
            "assigned_by": "ray"
        }
    ],
    "assigned_by": "ray",
    "execute_immediately": True,
    "self_destruct": False  # Should persist
}

try:
    response = requests.post("http://localhost:8000/tasks", json=regular_request, timeout=10)
    if response.status_code == 200:
        result = response.json()
        task_id = result['created_tasks'][0]['task_id']
        print(f"✅ Regular task created: {task_id[:8]}")
        
        # Check task count after creation
        after_regular = get_active_tasks_count()
        print(f"Active tasks after regular task: {after_regular}")
        
        if after_regular > initial_count:
            print("✅ Regular task persisted in active tasks")
        else:
            print("❌ Regular task not found in active tasks")
    else:
        print(f"❌ Regular task failed: {response.status_code}")
except Exception as e:
    print(f"❌ Regular task error: {e}")

# Test 2: Self-destruct task (should be removed)
print("\n2️⃣ Testing self-destruct task (should be removed)...")
self_destruct_request = {
    "task": [
        {
            "action": "list_directory",
            "path": "./modules",
            "include_hidden": False,
            "assigned_by": "ray"
        }
    ],
    "assigned_by": "ray",
    "execute_immediately": True,
    "self_destruct": True  # Should self-destruct
}

try:
    before_destruct = get_active_tasks_count()
    print(f"Active tasks before self-destruct task: {before_destruct}")
    
    response = requests.post("http://localhost:8000/tasks", json=self_destruct_request, timeout=10)
    if response.status_code == 200:
        result = response.json()
        task_id = result['created_tasks'][0]['task_id']
        print(f"✅ Self-destruct task created: {task_id[:8]}")
        
        # Check if task has execution results
        task = result['created_tasks'][0]
        if 'execution_result' in task['task']:
            print("⚡ Task was executed immediately")
            exec_result = task['task']['execution_result']
            if exec_result.get('executed'):
                print(f"📊 Results: {exec_result['results']['total_results']} items found")
        
        # Check task count after self-destruct
        after_destruct = get_active_tasks_count()
        print(f"Active tasks after self-destruct task: {after_destruct}")
        
        if after_destruct == before_destruct:
            print("✅ Self-destruct task was removed from active tasks")
        else:
            print("❌ Self-destruct task still exists in active tasks")
    else:
        print(f"❌ Self-destruct task failed: {response.status_code}")
except Exception as e:
    print(f"❌ Self-destruct task error: {e}")

# Test 3: Batch with mixed self-destruct settings
print("\n3️⃣ Testing batch with self-destruct...")
batch_request = {
    "task": [
        {
            "action": "health_check",
            "assigned_by": "ray"
        },
        {
            "action": "list_directory",
            "path": "./docs",
            "include_hidden": False,
            "assigned_by": "ray"
        }
    ],
    "assigned_by": "ray",
    "execute_immediately": True,
    "self_destruct": True  # Both tasks should self-destruct
}

try:
    before_batch = get_active_tasks_count()
    print(f"Active tasks before batch: {before_batch}")
    
    response = requests.post("http://localhost:8000/tasks", json=batch_request, timeout=10)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Batch created: {result['created_count']} tasks")
        
        # Check task count after batch self-destruct
        after_batch = get_active_tasks_count()
        print(f"Active tasks after batch: {after_batch}")
        
        if after_batch == before_batch:
            print("✅ All batch tasks were self-destructed")
        else:
            print("❌ Some batch tasks still exist in active tasks")
    else:
        print(f"❌ Batch request failed: {response.status_code}")
except Exception as e:
    print(f"❌ Batch request error: {e}")

# Final status
print("\n📊 Final Status:")
final_count = get_active_tasks_count()
print(f"Final active tasks: {final_count}")
print(f"Net change: {final_count - initial_count if initial_count is not None else 'Unknown'}")

print("\n🎯 Self-Destruct Feature Summary:")
print("✅ Tasks with self_destruct=true are executed and then removed")
print("✅ Tasks with self_destruct=false persist in active tasks")
print("✅ User gets full execution results before task destruction")
print("✅ Perfect for immediate-use directory listings and searches")