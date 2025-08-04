#!/usr/bin/env python3
"""
Test script to debug Ray's directory request issue.
"""

import requests
import json

# Test the exact request Ray is sending
ray_request = {
    "action": "list_directory",
    "search_type": "list_directory",  # This might be causing the issue
    "path": "./modules",
    "include_hidden": False
}

print("Testing Ray's directory request...")
print(f"Request payload: {json.dumps(ray_request, indent=2)}")

try:
    response = requests.post(
        "http://localhost:8000/directory/search",
        json=ray_request,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error: {e}")

# Test with correct format (without search_type)
correct_request = {
    "action": "list_directory",
    "path": "./modules", 
    "include_hidden": False,
    "assigned_by": "ray"
}

print("\n" + "="*50)
print("Testing corrected request...")
print(f"Request payload: {json.dumps(correct_request, indent=2)}")

try:
    response = requests.post(
        "http://localhost:8000/directory/search",
        json=correct_request,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Success! Found {result.get('search_result', {}).get('total_results', 0)} results")
        print(f"Response keys: {list(result.keys())}")
    else:
        print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error: {e}")