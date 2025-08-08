#!/usr/bin/env python3
"""
Test that Ray's response format matches what her extension expects.
"""

import asyncio
import aiohttp
import json

async def test_ray_response_format():
    """Test that the response format matches Ray's expectations."""
    
    ray_request = {
        "task": [
            {
                "action": "agents/create",
                "name": "RayFormatTest",
                "prompt": "Test agent for format verification",
                "description": "Testing response format",
                "assigned_by": "ray"
            }
        ],
        "assigned_by": "ray",
        "execute_immediately": True
    }
    
    print("🧪 Testing Ray's response format expectations...")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8000/tasks",
            json=ray_request,
            headers={"Content-Type": "application/json"}
        ) as response:
            
            if response.status == 200:
                data = await response.json()
                
                # Check the response structure Ray expects
                if "created_tasks" in data and len(data["created_tasks"]) > 0:
                    task = data["created_tasks"][0]["task"]
                    
                    print("✅ Response structure analysis:")
                    print(f"   📋 Task action: {task.get('action')}")
                    print(f"   🏷️  Task name: {task.get('name')}")
                    print(f"   🆔 Direct agent_id: {task.get('agent_id')}")
                    
                    # Check if agent_id is directly accessible (like reflection)
                    if "agent_id" in task:
                        print("✅ SUCCESS: agent_id is directly accessible in task!")
                        print(f"   Ray can access: task.agent_id = '{task['agent_id']}'")
                        
                        # Verify it matches the nested one
                        nested_id = task.get("execution_result", {}).get("results", {}).get("agent_id")
                        if task["agent_id"] == nested_id:
                            print("✅ SUCCESS: Direct and nested agent_id match!")
                        else:
                            print("⚠️  WARNING: Direct and nested agent_id don't match")
                    else:
                        print("❌ FAILURE: agent_id is NOT directly accessible in task")
                        print("   Ray's extension won't be able to find it easily")
                    
                    # Show the exact path Ray's extension can use
                    print(f"\n📍 Ray's extension can access agent_id via:")
                    print(f"   response.created_tasks[0].task.agent_id")
                    
                else:
                    print("❌ No created tasks found in response")
            else:
                print(f"❌ Request failed with status: {response.status}")

if __name__ == "__main__":
    asyncio.run(test_ray_response_format())