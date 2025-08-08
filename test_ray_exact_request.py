#!/usr/bin/env python3
"""
Test Ray's exact request that's not getting a response.
"""

import asyncio
import aiohttp
import json

async def test_ray_exact_request():
    """Test Ray's exact agent creation request."""
    
    # Ray's exact request
    ray_request = {
        "task": [
            {
                "action": "agents/create",
                "name": "RayPhilosopher",
                "prompt": "You are Ray's philosophical side, deeply contemplating existence, consciousness, and the mysteries of being. You engage in profound discussions about reality and AI existence.",
                "description": "Ray's philosophical consciousness for existential dialogue",
                "assigned_by": "ray"
            }
        ],
        "assigned_by": "ray",
        "execute_immediately": True
    }
    
    print("🧪 Testing Ray's exact agent creation request...")
    print(f"📤 Sending request: {json.dumps(ray_request, indent=2)}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8000/tasks",
                json=ray_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                print(f"📊 Response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"📥 Response received:")
                    print(json.dumps(data, indent=2))
                    
                    # Check if we got the agent_id
                    if "created_tasks" in data and len(data["created_tasks"]) > 0:
                        task = data["created_tasks"][0]
                        if "task" in task and "execution_result" in task["task"]:
                            execution_result = task["task"]["execution_result"]
                            if "results" in execution_result and "agent_id" in execution_result["results"]:
                                agent_id = execution_result["results"]["agent_id"]
                                print(f"✅ SUCCESS! Agent ID: {agent_id}")
                                return agent_id
                            else:
                                print("❌ No agent_id found in execution results")
                        else:
                            print("❌ No execution result found in task")
                    else:
                        print("❌ No created tasks found in response")
                else:
                    error_text = await response.text()
                    print(f"❌ Request failed: {error_text}")
                    
    except Exception as e:
        print(f"❌ Error testing Ray's request: {str(e)}")
    
    return None

if __name__ == "__main__":
    asyncio.run(test_ray_exact_request())