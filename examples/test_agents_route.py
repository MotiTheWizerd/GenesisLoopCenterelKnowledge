"""
Test script for the agents route pipeline.

This script tests the complete /agents/message endpoint that replicates
the functionality from agents_test.py as an HTTP API.
"""

import asyncio
import json
import uuid
from datetime import datetime
import aiohttp

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "test-user-123"
TEST_SESSION_ID = str(uuid.uuid4())

async def test_agent_message():
    """Test the main /agents/message endpoint."""
    
    print("🧪 Testing /agents/message endpoint...")
    print(f"📋 User ID: {TEST_USER_ID}")
    print(f"📋 Session ID: {TEST_SESSION_ID}")
    
    # Test message request
    test_request = {
        "message": "Hello! Can you help me understand what you are and how you work?",
        "user_id": TEST_USER_ID,
        "session_id": TEST_SESSION_ID,
        "context": {
            "test_mode": True,
            "timestamp": datetime.now().isoformat()
        },
        "assigned_by": "test_user"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            print(f"📤 Sending request to {BASE_URL}/agents/message")
            print(f"📤 Request data: {json.dumps(test_request, indent=2)}")
            
            async with session.post(
                f"{BASE_URL}/agents/message",
                json=test_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                print(f"📥 Response status: {response.status}")
                
                if response.status == 200:
                    response_data = await response.json()
                    print(f"✅ Success! Response:")
                    print(json.dumps(response_data, indent=2))
                    
                    # Validate response structure
                    required_fields = ["message_id", "status", "response", "user_id", "session_id", "processing_time_ms", "timestamp"]
                    missing_fields = [field for field in required_fields if field not in response_data]
                    
                    if missing_fields:
                        print(f"⚠️ Missing response fields: {missing_fields}")
                    else:
                        print("✅ All required response fields present")
                        
                        # Test response content
                        if response_data.get("status") == "completed":
                            print("✅ Message processed successfully")
                            print(f"🤖 Agent response: {response_data.get('response', 'No response')[:200]}...")
                            print(f"⏱️ Processing time: {response_data.get('processing_time_ms')}ms")
                        else:
                            print(f"⚠️ Message processing status: {response_data.get('status')}")
                            if response_data.get('error_message'):
                                print(f"❌ Error: {response_data.get('error_message')}")
                    
                    return response_data
                else:
                    error_text = await response.text()
                    print(f"❌ Request failed: {error_text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error during request: {str(e)}")
            return None

async def test_session_info():
    """Test the session info endpoint."""
    
    print(f"\n🧪 Testing /agents/session/{TEST_USER_ID}/{TEST_SESSION_ID} endpoint...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                f"{BASE_URL}/agents/session/{TEST_USER_ID}/{TEST_SESSION_ID}"
            ) as response:
                
                print(f"📥 Response status: {response.status}")
                
                if response.status == 200:
                    response_data = await response.json()
                    print(f"✅ Session info retrieved:")
                    print(json.dumps(response_data, indent=2))
                    return response_data
                else:
                    error_text = await response.text()
                    print(f"❌ Request failed: {error_text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error during request: {str(e)}")
            return None

async def test_agent_health():
    """Test the agent health endpoint."""
    
    print(f"\n🧪 Testing /agents/health endpoint...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/agents/health") as response:
                
                print(f"📥 Response status: {response.status}")
                
                if response.status == 200:
                    response_data = await response.json()
                    print(f"✅ Agent health status:")
                    print(json.dumps(response_data, indent=2))
                    return response_data
                else:
                    error_text = await response.text()
                    print(f"❌ Request failed: {error_text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error during request: {str(e)}")
            return None

async def test_multiple_messages():
    """Test multiple messages in the same session."""
    
    print(f"\n🧪 Testing multiple messages in session {TEST_SESSION_ID}...")
    
    messages = [
        "What is your name?",
        "Can you remember what I asked you before?",
        "Tell me about your capabilities."
    ]
    
    responses = []
    
    for i, message in enumerate(messages, 1):
        print(f"\n📤 Message {i}/{len(messages)}: {message}")
        
        test_request = {
            "message": message,
            "user_id": TEST_USER_ID,
            "session_id": TEST_SESSION_ID,
            "context": {
                "message_number": i,
                "total_messages": len(messages)
            },
            "assigned_by": "test_user"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{BASE_URL}/agents/message",
                    json=test_request,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        response_data = await response.json()
                        responses.append(response_data)
                        print(f"✅ Response {i}: {response_data.get('response', 'No response')[:100]}...")
                        print(f"⏱️ Processing time: {response_data.get('processing_time_ms')}ms")
                    else:
                        error_text = await response.text()
                        print(f"❌ Message {i} failed: {error_text}")
                        
            except Exception as e:
                print(f"❌ Error with message {i}: {str(e)}")
        
        # Small delay between messages
        await asyncio.sleep(1)
    
    return responses

async def test_batch_messages():
    """Test batch message processing."""
    
    print(f"\n🧪 Testing batch message processing...")
    
    batch_request = {
        "messages": [
            {
                "message": "What is 2+2?",
                "user_id": TEST_USER_ID,
                "session_id": TEST_SESSION_ID,
                "assigned_by": "test_user"
            },
            {
                "message": "What is the capital of France?",
                "user_id": TEST_USER_ID,
                "session_id": TEST_SESSION_ID,
                "assigned_by": "test_user"
            },
            {
                "message": "Tell me a joke.",
                "user_id": TEST_USER_ID,
                "session_id": TEST_SESSION_ID,
                "assigned_by": "test_user"
            }
        ],
        "process_parallel": False
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            print(f"📤 Sending batch request with {len(batch_request['messages'])} messages")
            
            async with session.post(
                f"{BASE_URL}/agents/batch",
                json=batch_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                print(f"📥 Response status: {response.status}")
                
                if response.status == 200:
                    response_data = await response.json()
                    print(f"✅ Batch processing completed:")
                    print(f"📊 Total messages: {response_data.get('total_messages')}")
                    print(f"📊 Successful: {len(response_data.get('successful_responses', []))}")
                    print(f"📊 Failed: {len(response_data.get('failed_responses', []))}")
                    print(f"⏱️ Total processing time: {response_data.get('processing_time_ms')}ms")
                    
                    return response_data
                else:
                    error_text = await response.text()
                    print(f"❌ Batch request failed: {error_text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error during batch request: {str(e)}")
            return None

async def main():
    """Run all tests."""
    
    print("🚀 Starting agents route pipeline tests...")
    print("=" * 60)
    
    # Test 1: Single message
    message_response = await test_agent_message()
    
    if message_response:
        # Test 2: Session info
        await test_session_info()
        
        # Test 3: Agent health
        await test_agent_health()
        
        # Test 4: Multiple messages
        await test_multiple_messages()
        
        # Test 5: Batch processing
        await test_batch_messages()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print(f"🎯 Test session: {TEST_SESSION_ID}")
        print("📋 Check the server logs for detailed processing information.")
    else:
        print("\n❌ Initial message test failed. Skipping other tests.")
        print("🔧 Make sure the server is running on http://localhost:8000")

if __name__ == "__main__":
    asyncio.run(main())