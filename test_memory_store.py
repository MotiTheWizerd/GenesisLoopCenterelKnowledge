#!/usr/bin/env python3
"""
Test script to reproduce the 422 error with /memory/store endpoint
"""

import requests
import json

def test_memory_store():
    """Test the memory store endpoint with various payloads"""
    
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/memory/store"
    
    print("🧪 Testing /memory/store endpoint...")
    
    # Test 1: Valid payload according to StoreRequest model
    test_payload_1 = {
        "memories": [
            {
                "content": "This is a test memory",
                "type": "test",
                "importance": "low"
            }
        ],
        "source": "test_script",
        "timestamp": "2025-08-08T06:40:00Z"
    }
    
    print(f"\n📤 Test 1 - Valid payload:")
    print(f"Payload: {json.dumps(test_payload_1, indent=2)}")
    
    try:
        response = requests.post(endpoint, json=test_payload_1)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Minimal payload
    test_payload_2 = {
        "memories": [
            {"text": "Simple memory"}
        ]
    }
    
    print(f"\n📤 Test 2 - Minimal payload:")
    print(f"Payload: {json.dumps(test_payload_2, indent=2)}")
    
    try:
        response = requests.post(endpoint, json=test_payload_2)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Empty memories array
    test_payload_3 = {
        "memories": []
    }
    
    print(f"\n📤 Test 3 - Empty memories:")
    print(f"Payload: {json.dumps(test_payload_3, indent=2)}")
    
    try:
        response = requests.post(endpoint, json=test_payload_3)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Missing memories field
    test_payload_4 = {
        "source": "test"
    }
    
    print(f"\n📤 Test 4 - Missing memories field:")
    print(f"Payload: {json.dumps(test_payload_4, indent=2)}")
    
    try:
        response = requests.post(endpoint, json=test_payload_4)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_memory_store()