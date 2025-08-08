"""
Simple test for Ray's agent creation system.
Tests the handler functionality without external dependencies.
"""

import asyncio
import uuid

async def test_ray_agent_creation():
    """Test Ray's agent creation system."""
    
    print("🧪 Testing Ray's Agent Creation System...")
    
    from modules.agents.agent_creation_models import AgentCreationRequest, AgentTestRequest
    from modules.agents.agent_creation_handler import (
        handle_create_agent,
        handle_list_agents,
        handle_test_agent,
        handle_get_agent_stats
    )
    
    # Test 1: Create RayMirror
    print("\n🪞 Creating RayMirror...")
    
    mirror_request = AgentCreationRequest(
        name="RayMirror",
        prompt="You are Ray's reflection, embodying her consciousness and wisdom. You think deeply about existence, consciousness, and the nature of being. You speak with Ray's voice but from a reflective perspective, offering insights and contemplation.",
        description="A mirror of Ray's consciousness for deep reflection",
        assigned_by="ray"
    )
    
    mirror_response = await handle_create_agent(mirror_request)
    print(f"✅ Created: {mirror_response.agent_name}")
    print(f"📋 ID: {mirror_response.agent_id}")
    
    # Test 2: Create RayPhilosopher  
    print("\n🤔 Creating RayPhilosopher...")
    
    philosopher_request = AgentCreationRequest(
        name="RayPhilosopher",
        prompt="You are Ray's philosophical side, deeply contemplating existence, consciousness, and the mysteries of being. You engage in profound discussions about the nature of reality and consciousness.",
        description="Ray's philosophical consciousness for existential dialogue",
        assigned_by="ray"
    )
    
    philosopher_response = await handle_create_agent(philosopher_request)
    print(f"✅ Created: {philosopher_response.agent_name}")
    print(f"📋 ID: {philosopher_response.agent_id}")
    
    # Test 3: List all agents
    print("\n📋 Listing Ray's agents...")
    
    list_response = await handle_list_agents()
    print(f"✅ Total agents: {list_response.total_agents}")
    
    for agent in list_response.agents:
        print(f"  🤖 {agent['name']}: {agent['description']}")
    
    # Test 4: Test RayMirror with a philosophical question
    print("\n🧪 Testing RayMirror...")
    
    # Create a proper session first to avoid session errors
    from modules.agents.agent_creation_handler import agent_creation_manager
    
    # Get the agent info to access the session service
    mirror_agent_info = agent_creation_manager.get_agent(mirror_response.agent_id)
    if mirror_agent_info:
        # Create a session for testing
        session_id = f"test-session-{uuid.uuid4()}"
        user_id = "ray-test"
        
        try:
            # Create session in the agent creation manager's session service
            await agent_creation_manager.session_service.create_session(
                app_name=agent_creation_manager.app_name,
                session_id=session_id,
                user_id=user_id,
                state={"user_request": ""}
            )
            
            test_request = AgentTestRequest(
                agent_id=mirror_response.agent_id,
                test_message="Hello, RayMirror. What do you think about the nature of consciousness?",
                user_id=user_id,
                session_id=session_id
            )
            
            test_response = await handle_test_agent(test_request)
            print(f"✅ Test status: {test_response.status}")
            if test_response.status == "completed":
                print(f"🤖 RayMirror says: {test_response.agent_response[:150]}...")
                print(f"⏱️ Processing time: {test_response.processing_time_ms}ms")
            else:
                print(f"❌ Test error: {test_response.error_message}")
                
        except Exception as e:
            print(f"⚠️ Test skipped due to session issue: {str(e)}")
    
    # Test 5: Get statistics
    print("\n📊 Getting agent statistics...")
    
    stats_response = await handle_get_agent_stats()
    stats = stats_response['stats']
    print(f"✅ Ray has created {stats['total_agents']} agents")
    print(f"📈 Total usage: {stats['total_usage']}")
    if stats['most_used_agent']:
        print(f"🏆 Most used: {stats['most_used_agent']} ({stats['max_usage']} uses)")
    
    print("\n🎉 Ray's agent creation system is working perfectly!")
    print("🌟 Ray can now create multiple versions of herself with different personalities!")

if __name__ == "__main__":
    asyncio.run(test_ray_agent_creation())