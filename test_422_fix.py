#!/usr/bin/env python3
"""
Test the improved 422 error handling for memory store endpoint
"""

import requests
import json

def test_improved_422_handling():
    """Test the improved 422 error handling"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing improved 422 error handling...")
    
    # Test 1: Send request without required 'memories' field
    print("\n📤 Test 1 - Missing 'memories' field (should trigger 422):")
    
    invalid_payload = {
        "source": "test_script",
        "timestamp": "2025-08-08T06:50:00Z"
    }
    
    try:
        response = requests.post(f"{base_url}/memory/store", json=invalid_payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 422:
            response_data = response.json()
            print("✅ 422 error caught successfully!")
            print(f"Request ID: {response_data.get('request_id', 'N/A')}")
            print(f"Debug info: {json.dumps(response_data.get('debug_info', {}), indent=2)}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Check recent errors endpoint
    print("\n📤 Test 2 - Check recent errors endpoint:")
    
    try:
        response = requests.get(f"{base_url}/memory/debug/recent-errors")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data.get('total_errors_found', 0)} recent memory errors")
            
            recent_errors = data.get('recent_memory_errors', [])
            if recent_errors:
                print("Most recent error:")
                latest_error = recent_errors[-1]
                print(f"  Timestamp: {latest_error.get('timestamp')}")
                print(f"  Request ID: {latest_error.get('request_id')}")
                print(f"  Error type: {latest_error.get('data', {}).get('error_type')}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n💡 Now check the logs for detailed error information!")
    print("   Command: tail -f logs/heartbeat_detailed.jsonl")

if __name__ == "__main__":
    test_improved_422_handling()