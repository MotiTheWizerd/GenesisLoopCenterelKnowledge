#!/usr/bin/env python3
"""
Quick test for the coding routes
"""

import requests
import json
from datetime import datetime

def test_coding_messages_route():
    """Test the coding messages route with the expected format"""
    
    base_url = "http://localhost:8000"
    
    # Test data matching the requested format
    test_message = {
        "message": "Test message from VSCode extension",
        "timestamp": datetime.now().isoformat(),
        "source": "raydaemon-vscode"
    }
    
    print("🧪 Testing /api/messages route...")
    print(f"📤 Sending: {json.dumps(test_message, indent=2)}")
    
    try:
        # Test POST request
        response = requests.post(
            f"{base_url}/api/messages",
            json=test_message,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Messages route working correctly!")
        else:
            print("❌ Messages route returned error")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"❌ Error testing messages route: {e}")

def test_vscode_response_route():
    """Test the VSCode response forwarding route"""
    
    base_url = "http://localhost:8000"
    
    # Test data - any JSON structure
    test_response = {
        "message": "Here's my response to the user",
        "ray_prompt": "Here is the context I needed, let's check the code",
        "is_final": "false",
        "timestamp": datetime.now().isoformat(),
        "additional_data": {
            "nested": "structure",
            "works": True
        }
    }
    
    print("\n🧪 Testing /api/vscode/response route...")
    print(f"📤 Sending: {json.dumps(test_response, indent=2)}")
    
    try:
        # Test POST request
        response = requests.post(
            f"{base_url}/api/vscode/response",
            json=test_response,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ VSCode response route working correctly!")
        elif response.status_code == 503:
            print("⚠️  External service not available (expected if localhost:3001 not running)")
        elif response.status_code == 504:
            print("⚠️  External service timeout (expected if localhost:3001 not responding)")
        else:
            print("❌ VSCode response route returned unexpected error")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"❌ Error testing VSCode response route: {e}")

def test_debug_endpoint():
    """Test the debug endpoint to check vsrequests state"""
    
    base_url = "http://localhost:8000"
    
    print("\n🧪 Testing /api/messages/debug route...")
    
    try:
        response = requests.get(f"{base_url}/api/messages/debug")
        print(f"📥 Debug Response: {response.status_code}")
        print(f"📥 Debug Data: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Debug endpoint working correctly!")
        else:
            print("❌ Debug endpoint returned error")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server for debug check")
    except Exception as e:
        print(f"❌ Error testing debug endpoint: {e}")

def test_status_endpoint():
    """Test the status endpoint"""
    
    base_url = "http://localhost:8000"
    
    print("\n🧪 Testing /api/messages/status route...")
    
    try:
        response = requests.get(f"{base_url}/api/messages/status")
        print(f"📥 Status Response: {response.status_code}")
        print(f"📥 Status Data: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Status endpoint working correctly!")
        else:
            print("❌ Status endpoint returned error")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server for status check")
    except Exception as e:
        print(f"❌ Error testing status endpoint: {e}")

if __name__ == "__main__":
    print("🚀 Running coding routes tests...\n")
    
    test_coding_messages_route()
    test_vscode_response_route()
    test_debug_endpoint()
    test_status_endpoint()
    
    print("\n✨ All tests completed!")