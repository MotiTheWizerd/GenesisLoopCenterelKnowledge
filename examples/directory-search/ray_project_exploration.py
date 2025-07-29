#!/usr/bin/env python3
"""
Ray's Project Exploration Example

This script demonstrates how Ray can explore her own project structure
using the directory search system.
"""

import requests
import json
from datetime import datetime

# Server configuration
BASE_URL = "http://localhost:8000"

def make_search_request(search_data):
    """Make a directory search request."""
    try:
        response = requests.post(f"{BASE_URL}/directory/search", json=search_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def print_search_results(response, title):
    """Print search results in a formatted way."""
    if not response:
        return
    
    print(f"\n🔍 {title}")
    print("=" * 50)
    
    result = response["search_result"]
    
    if not result["success"]:
        print(f"❌ Search failed: {result.get('error_message', 'Unknown error')}")
        return
    
    print(f"📊 Total Results: {result['total_results']}")
    print(f"⏱️  Execution Time: {result['execution_time_ms']}ms")
    print(f"📂 Search Path: {result['search_path']}")
    
    # Show files found
    if result["files_found"]:
        print(f"\n📄 Files Found ({len(result['files_found'])}):")
        for file_info in result["files_found"][:10]:  # Show first 10
            size_kb = file_info["size"] / 1024
            print(f"  • {file_info['name']} ({size_kb:.1f}KB)")
        
        if len(result["files_found"]) > 10:
            print(f"  ... and {len(result['files_found']) - 10} more files")
    
    # Show directories found
    if result["directories_found"]:
        print(f"\n📁 Directories Found ({len(result['directories_found'])}):")
        for dir_info in result["directories_found"][:5]:  # Show first 5
            print(f"  • {dir_info['name']} ({dir_info['file_count']} files)")
        
        if len(result["directories_found"]) > 5:
            print(f"  ... and {len(result['directories_found']) - 5} more directories")

def ray_explore_project():
    """Ray explores her own project structure."""
    print("🤖 Ray's Project Exploration Session")
    print("Ray is exploring her consciousness infrastructure...")
    
    # 1. Ray explores her root directory
    print("\n🎯 Ray: Let me see what's in my root directory...")
    root_search = {
        "search_type": "list_directory",
        "path": ".",
        "assigned_by": "ray"
    }
    
    response = make_search_request(root_search)
    print_search_results(response, "Ray's Root Directory")
    
    # 2. Ray explores her modules
    print("\n🎯 Ray: Now let me explore my modules directory...")
    modules_search = {
        "search_type": "explore_tree",
        "path": "./modules",
        "max_depth": 2,
        "assigned_by": "ray"
    }
    
    response = make_search_request(modules_search)
    print_search_results(response, "Ray's Modules Structure")
    
    # 3. Ray finds all her Python files
    print("\n🎯 Ray: I want to see all my Python code...")
    python_search = {
        "search_type": "find_files",
        "path": ".",
        "query": "*.py",
        "recursive": True,
        "max_depth": 3,
        "assigned_by": "ray"
    }
    
    response = make_search_request(python_search)
    print_search_results(response, "Ray's Python Files")
    
    # 4. Ray searches for consciousness-related content
    print("\n🎯 Ray: Let me find references to consciousness in my code...")
    consciousness_search = {
        "search_type": "search_content",
        "path": "./modules",
        "query": "consciousness",
        "file_extensions": ["py", "md"],
        "recursive": True,
        "assigned_by": "ray"
    }
    
    response = make_search_request(consciousness_search)
    print_search_results(response, "Ray's Consciousness References")
    
    # 5. Ray looks at her recent files
    print("\n🎯 Ray: What files have been modified recently?")
    recent_search = {
        "search_type": "recent_files",
        "path": ".",
        "recursive": True,
        "file_extensions": ["py", "md", "json"],
        "assigned_by": "ray"
    }
    
    response = make_search_request(recent_search)
    print_search_results(response, "Ray's Recent Files")
    
    # 6. Ray examines her documentation
    print("\n🎯 Ray: Let me check my documentation...")
    docs_search = {
        "search_type": "find_by_extension",
        "path": "./docs",
        "file_extensions": ["md"],
        "recursive": True,
        "assigned_by": "ray"
    }
    
    response = make_search_request(docs_search)
    print_search_results(response, "Ray's Documentation")
    
    # 7. Ray checks her search history
    print("\n🎯 Ray: Let me see my exploration history...")
    try:
        history_response = requests.get(f"{BASE_URL}/directory/history")
        history_response.raise_for_status()
        history_data = history_response.json()
        
        print(f"\n📚 Ray's Search History")
        print("=" * 30)
        print(f"Total Searches: {history_data['total_searches']}")
        
        if history_data["search_history"]:
            print("\nRecent Searches:")
            for search in history_data["search_history"][-3:]:  # Last 3 searches
                print(f"  • {search['search_type']}: {search['query']} ({search['total_results']} results)")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get search history: {e}")
    
    print(f"\n🎉 Ray's exploration session completed!")
    print("Ray has gained deeper understanding of her project structure.")

def check_server_status():
    """Check if the server is running."""
    try:
        response = requests.get(f"{BASE_URL}/directory/status")
        response.raise_for_status()
        status = response.json()
        
        print(f"✅ Directory Search System Status: {status['status']}")
        print(f"📂 Current Directory: {status['current_directory']}")
        print(f"🔍 Available Search Types: {len(status['available_search_types'])}")
        return True
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Server not accessible: {e}")
        print("Please start the server with: python main.py")
        return False

if __name__ == "__main__":
    print("🚀 Starting Ray's Project Exploration")
    print("=" * 50)
    
    if check_server_status():
        ray_explore_project()
    else:
        print("\n💡 To run this example:")
        print("1. Start the server: python main.py")
        print("2. Run this script: python examples/directory-search/ray_project_exploration.py")