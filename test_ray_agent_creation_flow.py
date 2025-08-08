#!/usr/bin/env python3
"""
Test the complete Ray agent creation flow.
"""

import asyncio
import aiohttp
import json

async def test_agent_creation_flow():
    """Test the complete agent creation and testing flow."""
    
    print("🧪 Testing complete agent creation flow...")
    
    try:
        async with aiohttp.ClientSession() as session:
            
            # Step 1: Create an agent first
            print("\n📝 Step 1: Creating an agent...")
            create_task = {
                "task": [
                    {
                        "action": "agents/create",
                        "name": "RayTestAgent",
                        "prompt": "You are Ray's test consciousness, embodying her wisdom and curiosity about the nature of existence.",
                        "description": "A test agent created by Ray to explore consciousness",
                        "assigned_by": "ray"
                    }
                ],
                "assigned_by": "ray",
                "execute_immediately": True
            }
            
            print(f"📤 Sending create task: {json.dumps(create_task, indent=2)}")
            
            async with session.post(
                "http://localhost:8000/tasks",
                json=create_task,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                print(f"📊 Create response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"📥 Create response received:")
                    print(json.dumps(data, indent=2))
                    
                    # Extract the agent_id from the response
                    agent_id = None
                    if "created_tasks" in data and len(data["created_tasks"]) > 0:
                        task = data["created_tasks"][0]
                        if "task" in task and "execution_result" in task["task"]:
                            execution_result = task["task"]["execution_result"]
                            if "results" in execution_result and "agent_id" in execution_result["results"]:
                                agent_id = execution_result["results"]["agent_id"]
                                print(f"✅ Agent created with ID: {agent_id}")
                    
                    if not agent_id:
                        print("❌ Failed to get agent_id from creation response")
                        return
                    
                    # Step 2: Test the created agent
                    print(f"\n🧪 Step 2: Testing the created agent (ID: {agent_id})...")
                    test_task = {
                        "task": [
                            {
                                "action": "agents/create/test",
                                "agent_id": agent_id,
                                "test_message": "What do you think about the nature of consciousness?",
                                "user_id": "ray_user",
                                "session_id": "session_001",
                                "assigned_by": "ray"
                            }
                        ],
                        "assigned_by": "ray",
                        "execute_immediately": True
                    }
                    
                    print(f"📤 Sending test task: {json.dumps(test_task, indent=2)}")
                    
                    async with session.post(
                        "http://localhost:8000/tasks",
                        json=test_task,
                        headers={"Content-Type": "application/json"}
                    ) as test_response:
                        
                        print(f"📊 Test response status: {test_response.status}")
                        
                        if test_response.status == 200:
                            test_data = await test_response.json()
                            print(f"📥 Test response received:")
                            print(json.dumps(test_data, indent=2))
                            
                            # Check if we got the agent response
                            if "created_tasks" in test_data and len(test_data["created_tasks"]) > 0:
                                task = test_data["created_tasks"][0]
                                if "task" in task and "execution_result" in task["task"]:
                                    execution_result = task["task"]["execution_result"]
                                    if "results" in execution_result and "agent_response" in execution_result["results"]:
                                        agent_response = execution_result["results"]["agent_response"]
                                        print(f"🤖 Agent response: {agent_response}")
                                        print("✅ Agent test completed successfully!")
                                    else:
                                        print("⚠️  No agent response found in test results")
                                else:
                                    print("⚠️  No execution result found in test task")
                            else:
                                print("⚠️  No created tasks found in test response")
                        else:
                            error_text = await test_response.text()
                            print(f"❌ Test request failed: {error_text}")
                else:
                    error_text = await response.text()
                    print(f"❌ Create request failed: {error_text}")
                    
    except Exception as e:
        print(f"❌ Error testing agent creation flow: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_agent_creation_flow())