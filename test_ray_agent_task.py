#!/usr/bin/env python3
"""
Test Ray's agent creation task to verify the fix.
"""

import asyncio
import aiohttp
import json

async def test_ray_agent_task():
    """Test Ray's agent creation task that was failing."""
    
    # Ray's original task that wasn't getting a response with agent_id
    ray_task = {
        "task": [
            {
                "action": "agents/create/test",
                "agent_id": "PLACEHOLDER_AGENT_ID",
                "test_message": "What do you think about the nature of consciousness?",
                "user_id": "ray_user",
                "session_id": "session_001",
                "assigned_by": "ray"
            }
        ],
        "assigned_by": "ray",
        "execute_immediately": True
    }
    
    print("🧪 Testing Ray's agent creation task...")
    print(f"📤 Sending task: {json.dumps(ray_task, indent=2)}")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Send the task to the correct endpoint
            async with session.post(
                "http://localhost:8000/tasks",
                json=ray_task,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                print(f"📊 Response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"📥 Response received:")
                    print(json.dumps(data, indent=2))
                    
                    # Check if we got the expected response structure
                    if "created_tasks" in data and len(data["created_tasks"]) > 0:
                        task = data["created_tasks"][0]
                        if "task" in task and "execution_result" in task["task"]:
                            execution_result = task["task"]["execution_result"]
                            print(f"✅ Task executed successfully!")
                            print(f"🎯 Execution result: {execution_result}")
                            
                            # Check if agent_id is in the results
                            if "results" in execution_result and "agent_id" in execution_result["results"]:
                                agent_id = execution_result["results"]["agent_id"]
                                print(f"🆔 Agent ID found: {agent_id}")
                            else:
                                print("⚠️  No agent_id found in execution results")
                        else:
                            print("⚠️  No execution result found in task")
                    else:
                        print("⚠️  No created tasks found in response")
                else:
                    error_text = await response.text()
                    print(f"❌ Request failed: {error_text}")
                    
    except Exception as e:
        print(f"❌ Error testing Ray's task: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_ray_agent_task())