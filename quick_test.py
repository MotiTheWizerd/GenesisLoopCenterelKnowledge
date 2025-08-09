#!/usr/bin/env python3
import requests
import json

# Test task without execute_immediately flag
task = {
    "task": [{"action": "reflect", "question": "Testing default execution"}],
    "assigned_by": "ray"
}

try:
    response = requests.post("http://localhost:8000/tasks", json=task, timeout=10)
    if response.status_code == 200:
        result = response.json()
        created_tasks = result.get("created_tasks", [])
        if created_tasks and 'execution_result' in created_tasks[0].get('task', {}):
            print("✅ DEFAULT EXECUTION WORKING!")
        else:
            print("❌ Default execution not working - server restart needed")
    else:
        print(f"❌ Request failed: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")