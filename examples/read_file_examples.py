#!/usr/bin/env python3
"""
Examples of how Ray can use the read_file functionality.

This demonstrates various ways Ray can read files through the API.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def example_1_simple_read():
    """Example 1: Simple file reading"""
    print("📖 Example 1: Simple file reading")
    
    request = {
        "action": "read_file",
        "path": "./README.md",  # File path directly in path field
        "assigned_by": "ray"
    }
    
    response = requests.post(f"{BASE_URL}/directory/read", json=request)
    
    if response.status_code == 200:
        result = response.json()
        file_info = result["search_result"]["files_found"][0]
        
        print(f"✅ Read {file_info['name']}")
        print(f"   Size: {file_info['size']} bytes")
        print(f"   Lines: {file_info['lines_count']}")
        print(f"   Content preview: {file_info['content'][:100]}...")
    else:
        print(f"❌ Failed: {response.status_code}")

def example_2_advanced_read():
    """Example 2: Advanced file reading with parameters"""
    print("\n📖 Example 2: Advanced file reading")
    
    # Read specific lines from a file
    query_params = {
        "file_path": "./main.py",
        "start_line": 1,
        "end_line": 20,
        "encoding": "utf-8",
        "max_size": 1048576  # 1MB limit
    }
    
    request = {
        "action": "read_file",
        "path": ".",
        "query": json.dumps(query_params),
        "assigned_by": "ray"
    }
    
    response = requests.post(f"{BASE_URL}/directory/read", json=request)
    
    if response.status_code == 200:
        result = response.json()
        file_info = result["search_result"]["files_found"][0]
        
        print(f"✅ Read lines 1-20 from {file_info['name']}")
        print(f"   Lines read: {file_info['lines_count']}")
        print(f"   Content:\n{file_info['content']}")
    else:
        print(f"❌ Failed: {response.status_code}")

def example_3_simple_post():
    """Example 3: Using simple POST request"""
    print("\n📖 Example 3: Simple POST request")
    
    request = {
        "action": "read_file",
        "path": "./pyproject.toml",
        "assigned_by": "ray"
    }
    
    response = requests.post(f"{BASE_URL}/directory/read", json=request)
    
    if response.status_code == 200:
        result = response.json()
        file_info = result["search_result"]["files_found"][0]
        
        print(f"✅ Read {file_info['name']} via simple POST")
        print(f"   Size: {file_info['size']} bytes")
        print(f"   Content preview: {file_info['content'][:200]}...")
    else:
        print(f"❌ Failed: {response.status_code}")

def example_4_error_handling():
    """Example 4: Error handling"""
    print("\n📖 Example 4: Error handling")
    
    # Try to read a non-existent file
    request = {
        "action": "read_file",
        "path": "./non_existent_file.txt",
        "assigned_by": "ray"
    }
    
    response = requests.post(f"{BASE_URL}/directory/read", json=request)
    
    if response.status_code == 200:
        result = response.json()
        search_result = result["search_result"]
        
        if not search_result["success"]:
            print(f"✅ Error handled correctly: {search_result['error_message']}")
        else:
            print(f"❌ Expected error but got success")
    else:
        print(f"❌ HTTP Error: {response.status_code}")

def example_5_ray_task_format():
    """Example 5: Ray's task format integration"""
    print("\n📖 Example 5: Ray's task format")
    
    # This is how Ray would typically send the request
    ray_task = {
        "task": [
            {
                "type": "read_file",
                "file_path": "./docs/PROJECT_STRUCTURE.md",
                "max_lines": 50
            }
        ],
        "assigned_by": "ray"
    }
    
    # Convert to directory API format
    directory_request = {
        "action": "read_file",
        "path": ".",
        "query": json.dumps({
            "file_path": ray_task["task"][0]["file_path"],
            "end_line": ray_task["task"][0].get("max_lines", None)
        }),
        "assigned_by": ray_task["assigned_by"]
    }
    
    response = requests.post(f"{BASE_URL}/directory/read", json=directory_request)
    
    if response.status_code == 200:
        result = response.json()
        file_info = result["search_result"]["files_found"][0]
        
        print(f"✅ Ray's task processed successfully")
        print(f"   File: {file_info['name']}")
        print(f"   Lines: {file_info['lines_count']}")
        print(f"   Binary: {file_info['is_binary']}")
    else:
        print(f"❌ Failed: {response.status_code}")

def main():
    """Run all examples"""
    print("🎯 Ray's Read File Examples")
    print("=" * 50)
    
    try:
        example_1_simple_read()
        example_2_advanced_read()
        example_3_simple_post()
        example_4_error_handling()
        example_5_ray_task_format()
        
        print("\n🎉 All examples completed!")
        print("\nRay can now read files using these patterns:")
        print("1. Simple path-based reading")
        print("2. Advanced parameter control")
        print("3. Simple POST requests")
        print("4. Proper error handling")
        print("5. Integration with task format")
        
    except Exception as e:
        print(f"❌ Example error: {str(e)}")

if __name__ == "__main__":
    main()