#!/usr/bin/env python3
"""
Test available endpoints to help debug Ray's issue.
"""

import asyncio
import aiohttp
import json

async def test_endpoints():
    """Test various endpoints to see which ones work."""
    
    ray_request = {
        "task": [
            {
                "action": "agents/create",
                "name": "RayTest",
                "prompt": "Test agent",
                "description": "Test",
                "assigned_by": "ray"
            }
        ],
        "assigned_by": "ray",
        "execute_immediately": True
    }
    
    endpoints_to_test = [
        "http://localhost:8000/tasks",
        "http://localhost:8000/task",
        "http://localhost:8000/agents/create",
        "http://localhost:8000/"
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints_to_test:
            print(f"\n🧪 Testing endpoint: {endpoint}")
            try:
                async with session.post(
                    endpoint,
                    json=ray_request,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    print(f"📊 Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        # Check if agent_id is in response
                        response_str = json.dumps(data)
                        if "agent_id" in response_str:
                            print("✅ Contains agent_id!")
                        else:
                            print("❌ No agent_id found")
                        
                        # Show first 200 chars of response
                        print(f"📥 Response preview: {response_str[:200]}...")
                    else:
                        error_text = await response.text()
                        print(f"❌ Error: {error_text[:100]}...")
                        
            except Exception as e:
                print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_endpoints())