#!/usr/bin/env python3
"""
Test script to check if the API server is running and responding correctly.
"""

import requests
import json

def test_api_server():
    """Test the API server endpoints."""
    
    print("🧪 Testing API Server")
    print("=" * 50)
    
    ports_to_test = [8000, 8001, 8080, 3000, 8500]
    
    for port in ports_to_test:
        print(f"\n🔍 Testing port {port}:")
        
        try:
            # Test basic connection
            response = requests.get(f"http://localhost:{port}", timeout=2)
            print(f"  ✅ Port {port} is responding")
            print(f"  📄 Status Code: {response.status_code}")
            print(f"  📋 Content-Type: {response.headers.get('content-type', 'Unknown')}")
            
            # Check if it looks like FastAPI
            if 'application/json' in response.headers.get('content-type', ''):
                print(f"  🎯 Looks like an API server (JSON response)")
            elif 'text/html' in response.headers.get('content-type', ''):
                if 'streamlit' in response.text.lower():
                    print(f"  🌊 This is a Streamlit server")
                elif 'fastapi' in response.text.lower() or 'swagger' in response.text.lower():
                    print(f"  🚀 This might be FastAPI docs page")
                else:
                    print(f"  🌐 This is some other web server")
            
            # Test health endpoints if it might be an API
            if port != 8500:  # Skip Streamlit port
                try:
                    health_response = requests.get(f"http://localhost:{port}/health/status", timeout=2)
                    print(f"  🏥 /health/status: {health_response.status_code}")
                    if health_response.status_code == 200:
                        content_type = health_response.headers.get('content-type', '')
                        if 'application/json' in content_type:
                            print(f"  ✅ Health endpoint returns JSON!")
                            try:
                                data = health_response.json()
                                print(f"  📊 Health data keys: {list(data.keys())[:5]}")
                            except:
                                print(f"  ❌ JSON parsing failed")
                        else:
                            print(f"  ⚠️ Health endpoint returns: {content_type}")
                except requests.exceptions.RequestException:
                    print(f"  ❌ /health/status not available")
        
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Port {port} is not responding")
        except requests.exceptions.Timeout:
            print(f"  ⏱️ Port {port} timed out")
        except Exception as e:
            print(f"  ❌ Error testing port {port}: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 API Server test complete!")

if __name__ == "__main__":
    test_api_server()