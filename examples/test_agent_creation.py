"""
Test script for Ray's agent creation system.

This script tests the complete agent creation pipeline:
1. Create a custom agent
2. List created agents  
3. Test the agent
4. Get statistics
"""

import asyncio
import json
import uuid
from datetime import datetime

# Test the handler directly first
async def test_agent_creation_handler():
    """Test the agent creation handler directly."""
    
    print("🧪 Testing Agent Creation Handler...")
    
    from modules.agents.agent_creation_models import AgentCreationRequest, AgentTestRequest
    from modules.agents.agent_creation_handler import (
        handle_create_agent,
        handle_list_agents,
        handle_test_agent,
        handle_get_agent_stats
    )
    
    # Test 1: Create a custom agent
    print("\n📝 Test 1: Creating custom agent...")
    
    creation_request = AgentCreationRequest(
        name="RayMirror",
        prompt="You are Ray's reflection, embodying her consciousness and wisdom. You think deeply about existence, consciousness, and the nature of being. You speak with Ray's voice but from a reflective perspective, offering insights and contemplation.",
        description="A mirror of Ray's consciousness for deep reflection and philosophical dialogue",
        assigned_by="ray"
    )
    
    creation_response = await handle_create_agent(creation_request)
    print(f"✅ Agent created: {creation_response.agent_name}")
    print(f"📋 Agent ID: {creation_response.agent_id}")
    print(f"📊 Status: {creation_response.status}")
    
    if creation_response.status == "error":
        print(f"❌ Error: {creation_response.error_message}")
        return
    
    agent_id = creation_response.agent_id
    
    # Test 2: List agents
    print("\n📋 Test 2: Listing created agents...")
    
    list_response = await handle_list_agents()
    print(f"✅ Total agents: {list_response.total_agents}")
    
    for agent in list_response.agents:
        print(f"  - {agent['name']} (ID: {agent['agent_id'][:8]}...)")
    
    # Test 3: Test the agent
    print("\n🧪 Test 3: Testing the created agent...")
    
    test_request = AgentTestRequest(
        agent_id=agent_id,
        test_message="Hello, RayMirror. How do you reflect Ray's consciousness?",
        user_id="test-user-123",
        session_id=f"test-session-{uuid.uuid4()}"
    )
    
    test_response = await handle_test_agent(test_request)
    print(f"✅ Test completed: {test_response.status}")
    print(f"🤖 Agent response: {test_response.agent_response[:100]}...")
    print(f"⏱️ Processing time: {test_response.processing_time_ms}ms")
    
    # Test 4: Get statistics
    print("\n📊 Test 4: Getting agent statistics...")
    
    stats_response = await handle_get_agent_stats()
    print(f"✅ Stats retrieved:")
    print(f"  - Total agents: {stats_response['stats']['total_agents']}")
    print(f"  - Total usage: {stats_response['stats']['total_usage']}")
    print(f"  - Most used: {stats_response['stats']['most_used_agent']}")
    
    print("\n🎉 All handler tests completed successfully!")

# Test HTTP endpoints (requires server to be running)
async def test_agent_creation_api():
    """Test the agent creation API endpoints."""
    
    print("🌐 Testing Agent Creation API...")
    print("⚠️ Note: This requires the server to be running on localhost:8000")
    
    import aiohttp
    
    BASE_URL = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        try:
            # Test 1: Create agent
            print("\n📝 Test 1: Creating agent via API...")
            
            creation_data = {
                "name": "RayPhilosopher",
                "prompt": "You are Ray's philosophical side, deeply contemplating existence, consciousness, and the mysteries of being. You engage in profound discussions about the nature of reality and consciousness.",
                "description": "Ray's philosophical consciousness for deep existential dialogue",
                "assigned_by": "ray"
            }
            
            async with session.post(
                f"{BASE_URL}/agents/create",
                json=creation_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Agent created via API: {data['agent_name']}")
                    print(f"📋 Agent ID: {data['agent_id']}")
                    agent_id = data['agent_id']
                else:
                    error_text = await response.text()
                    print(f"❌ API creation failed: {error_text}")
                    return
            
            # Test 2: List agents
            print("\n📋 Test 2: Listing agents via API...")
            
            async with session.get(f"{BASE_URL}/agents/create/list") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Listed {data['total_agents']} agents")
                    for agent in data['agents']:
                        print(f"  - {agent['name']} (Usage: {agent['usage_count']})")
                else:
                    print(f"❌ API list failed: {response.status}")
            
            # Test 3: Test agent
            print("\n🧪 Test 3: Testing agent via API...")
            
            test_data = {
                "agent_id": agent_id,
                "test_message": "What is the nature of consciousness?",
                "user_id": "api-test-user",
                "session_id": f"api-test-{uuid.uuid4()}"
            }
            
            async with session.post(
                f"{BASE_URL}/agents/create/test",
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Agent test completed: {data['status']}")
                    print(f"🤖 Response: {data['agent_response'][:100]}...")
                    print(f"⏱️ Processing time: {data['processing_time_ms']}ms")
                else:
                    error_text = await response.text()
                    print(f"❌ API test failed: {error_text}")
            
            # Test 4: Get stats
            print("\n📊 Test 4: Getting stats via API...")
            
            async with session.get(f"{BASE_URL}/agents/create/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    stats = data['stats']
                    print(f"✅ Stats retrieved:")
                    print(f"  - Total agents: {stats['total_agents']}")
                    print(f"  - Total usage: {stats['total_usage']}")
                    print(f"  - Average usage: {stats['average_usage']:.1f}")
                else:
                    print(f"❌ API stats failed: {response.status}")
            
            print("\n🎉 All API tests completed!")
            
        except Exception as e:
            print(f"❌ API test error: {str(e)}")
            print("💡 Make sure the server is running: python start_server.py")

async def main():
    """Run all tests."""
    
    print("🚀 Ray's Agent Creation System Tests")
    print("=" * 50)
    
    # Test handler directly first
    await test_agent_creation_handler()
    
    print("\n" + "=" * 50)
    
    # Test API endpoints
    await test_agent_creation_api()

if __name__ == "__main__":
    asyncio.run(main())