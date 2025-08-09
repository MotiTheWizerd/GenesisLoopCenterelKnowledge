#!/usr/bin/env python3
"""
Test script to send 3 messages to the ray-response endpoint
"""

import requests
import json
from datetime import datetime
import time

def send_test_messages():
    """Send 3 test messages to the /api/vscode/response endpoint"""
    
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/vscode/response"
    
    # First check if server is running
    try:
        health_check = requests.get(f"{base_url}/heartbeat", timeout=5)
        print(f"✅ Server is running (status: {health_check.status_code})")
    except requests.exceptions.ConnectionError:
        print(f"❌ Server is not running at {base_url}")
        print("   Please start the server with: python main.py")
        return
    except Exception as e:
        print(f"⚠️  Server health check failed: {e}")
        print("   Continuing with test anyway...")
    
    # Test messages
    messages = [

{
"message": "Probe index with multiple known symbols from index.json",
"is_final": "true",
"command_calls": [
{ "command": "findSymbolFromIndex", "args": ["initialize"] },
{ "command": "findSymbolFromIndex", "args": ["handleSystemToggle"] },
{ "command": "findSymbolFromIndex", "args": ["getSystemStates"] },
{ "command": "findSymbolFromIndex", "args": ["enableAllSystemsViaControlPanel"] },
{ "command": "findSymbolFromIndex", "args": ["checkActivityMonitorStatus"] }
]
}


    ]
    
    print("🚀 Sending 3 test messages to ray-response endpoint...\n")
    
    for i, message in enumerate(messages, 1):
        print(f"📤 Sending message {i}/3:")
        print(f"   Content: {message['message']}")
        
        try:
            response = requests.post(
                endpoint,
                json=message,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            print(f"📥 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"✅ Message {i} forwarded successfully!")
                print(f"   Status: {response_data.get('status', 'unknown')}")
            else:
                print(f"❌ Message {i} failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                    
        except requests.exceptions.ConnectionError:
            print(f"❌ Could not connect to server at {base_url}")
            print("   Make sure the server is running on localhost:8000")
            break
        except requests.exceptions.Timeout:
            print(f"❌ Message {i} timed out")
        except Exception as e:
            print(f"❌ Error sending message {i}: {e}")
        
        print()  # Empty line for readability
        
        # Small delay between messages
        if i < len(messages):
            time.sleep(0.5)
    
    print("✨ Test completed!")

if __name__ == "__main__":
    send_test_messages()