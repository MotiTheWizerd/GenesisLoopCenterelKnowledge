"""
Simple test for the agents route pipeline.
Tests the basic functionality without external dependencies.
"""

import asyncio
import uuid
from modules.agents.models import AgentMessageRequest
from modules.agents.handler import handle_agent_message

async def test_basic_agent_functionality():
    """Test the basic agent message handling without HTTP."""
    
    print("🧪 Testing basic agent functionality...")
    
    # Create test request
    test_request = AgentMessageRequest(
        message="Hello! Can you tell me what you are?",
        user_id="test-user-123",
        session_id=str(uuid.uuid4()),
        context={"test_mode": True},
        assigned_by="test_user"
    )
    
    print(f"📤 Processing message: {test_request.message}")
    print(f"👤 User ID: {test_request.user_id}")
    print(f"🔗 Session ID: {test_request.session_id}")
    
    try:
        # Process the message
        response = await handle_agent_message(test_request)
        
        print(f"✅ Message processed successfully!")
        print(f"📋 Message ID: {response.message_id}")
        print(f"📊 Status: {response.status}")
        print(f"⏱️ Processing time: {response.processing_time_ms}ms")
        print(f"🤖 Response: {response.response[:200] if response.response else 'No response'}...")
        
        if response.error_message:
            print(f"⚠️ Error message: {response.error_message}")
        
        return response
        
    except Exception as e:
        print(f"❌ Error processing message: {str(e)}")
        return None

if __name__ == "__main__":
    asyncio.run(test_basic_agent_functionality())