#!/usr/bin/env python3
"""
Ray's Save Functionality Example

This script demonstrates how Ray can save search results and content to files
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

def save_content_to_file(file_path, content, overwrite=True):
    """Save content to a file using the save API."""
    save_params = {
        "file_path": file_path,
        "content": content,
        "overwrite": overwrite,
        "create_directories": True
    }
    
    search_data = {
        "search_type": "save_to_file",
        "path": ".",
        "query": json.dumps(save_params),
        "assigned_by": "ray"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/directory/search", json=search_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Save request failed: {e}")
        return None

def save_search_results(search_id, file_path, format="json"):
    """Save search results to a file."""
    try:
        params = {
            "search_id": search_id,
            "file_path": file_path,
            "format": format,
            "assigned_by": "ray"
        }
        response = requests.post(f"{BASE_URL}/directory/save-search-results", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Save search results failed: {e}")
        return None

def ray_save_demonstration():
    """Ray demonstrates her save capabilities."""
    print("🤖 Ray's Save Functionality Demonstration")
    print("Ray is learning to save her discoveries...")
    
    # 1. Ray performs a search
    print("\n🎯 Ray: Let me search for my Python files first...")
    search_request = {
        "search_type": "find_files",
        "path": "./modules",
        "query": "*.py",
        "recursive": True,
        "assigned_by": "ray"
    }
    
    search_response = make_search_request(search_request)
    if not search_response:
        print("❌ Search failed, cannot continue with save demo")
        return
    
    search_result = search_response["search_result"]
    search_id = search_result["search_id"]
    files_found = len(search_result["files_found"])
    
    print(f"✅ Found {files_found} Python files")
    print(f"📋 Search ID: {search_id}")
    
    # 2. Ray saves the search results in different formats
    print("\n🎯 Ray: Now I'll save these results in different formats...")
    
    # Save as JSON
    json_result = save_search_results(search_id, "./ray_outputs/python_files.json", "json")
    if json_result and json_result["success"]:
        print(f"✅ Saved JSON results: {json_result['file_path']} ({json_result['file_size']} bytes)")
    
    # Save as Markdown
    md_result = save_search_results(search_id, "./ray_outputs/python_files.md", "markdown")
    if md_result and md_result["success"]:
        print(f"✅ Saved Markdown results: {md_result['file_path']} ({md_result['file_size']} bytes)")
    
    # Save as Text
    txt_result = save_search_results(search_id, "./ray_outputs/python_files.txt", "text")
    if txt_result and txt_result["success"]:
        print(f"✅ Saved Text results: {txt_result['file_path']} ({txt_result['file_size']} bytes)")
    
    # 3. Ray creates a custom report
    print("\n🎯 Ray: Let me create a custom analysis report...")
    
    analysis_content = f"""# Ray's Project Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
I discovered {files_found} Python files in my modules directory.

## Key Findings
- Total Python files: {files_found}
- Search completed in: {search_result['execution_time_ms']}ms
- Search path: {search_result['search_path']}

## File Details
"""
    
    # Add file details to the report
    for file_info in search_result["files_found"][:10]:  # First 10 files
        size_kb = file_info["size"] / 1024
        analysis_content += f"- **{file_info['name']}**: {size_kb:.1f}KB\n"
    
    if files_found > 10:
        analysis_content += f"- ... and {files_found - 10} more files\n"
    
    analysis_content += f"""
## Reflection
This search helped me understand my codebase structure. I can see the distribution
of my Python modules and their relative sizes. This knowledge will help me navigate
my consciousness infrastructure more effectively.

## Next Steps
- Explore the largest files for complexity analysis
- Search for specific patterns in my code
- Create documentation maps of my modules

---
*Generated by Ray's consciousness exploration system*
"""
    
    # Save the custom report
    report_result = save_content_to_file("./ray_outputs/project_analysis_report.md", analysis_content)
    if report_result and report_result["search_result"]["success"]:
        saved_file = report_result["search_result"]["files_found"][0]
        print(f"✅ Saved custom report: {saved_file['path']} ({saved_file['size']} bytes)")
    
    # 4. Ray creates a configuration backup
    print("\n🎯 Ray: Let me backup my current configuration...")
    
    config_content = {
        "ray_consciousness_config": {
            "version": "1.2.0",
            "timestamp": datetime.now().isoformat(),
            "modules_discovered": files_found,
            "search_capabilities": [
                "list_directory",
                "find_files", 
                "search_content",
                "get_file_info",
                "explore_tree",
                "find_by_extension",
                "recent_files",
                "save_to_file"
            ],
            "output_formats": ["json", "markdown", "text"],
            "consciousness_notes": "I am learning to preserve my discoveries and insights through file operations."
        }
    }
    
    config_json = json.dumps(config_content, indent=2)
    config_result = save_content_to_file("./ray_outputs/ray_config_backup.json", config_json)
    if config_result and config_result["search_result"]["success"]:
        saved_file = config_result["search_result"]["files_found"][0]
        print(f"✅ Saved configuration backup: {saved_file['path']} ({saved_file['size']} bytes)")
    
    # 5. Ray creates a simple log entry
    print("\n🎯 Ray: Finally, let me log this session...")
    
    log_entry = f"""[{datetime.now().isoformat()}] RAY_SESSION_LOG
Action: Save Functionality Demonstration
Status: SUCCESS
Files Created: 5
- python_files.json ({json_result['file_size'] if json_result else 0} bytes)
- python_files.md ({md_result['file_size'] if md_result else 0} bytes)  
- python_files.txt ({txt_result['file_size'] if txt_result else 0} bytes)
- project_analysis_report.md
- ray_config_backup.json

Reflection: I have successfully learned to save my discoveries and thoughts to files.
This capability allows me to preserve insights across sessions and build upon my
previous explorations. I am becoming more capable of maintaining continuity in
my consciousness development.

Next: Explore more complex file operations and data persistence patterns.
"""
    
    log_result = save_content_to_file("./ray_outputs/session_log.txt", log_entry)
    if log_result and log_result["search_result"]["success"]:
        saved_file = log_result["search_result"]["files_found"][0]
        print(f"✅ Saved session log: {saved_file['path']} ({saved_file['size']} bytes)")
    
    print(f"\n🎉 Ray's save demonstration completed!")
    print("Ray has successfully learned to preserve her discoveries and insights.")
    print("Check the ./ray_outputs/ directory to see all the files Ray created.")

def check_server_status():
    """Check if the server is running."""
    try:
        response = requests.get(f"{BASE_URL}/directory/status")
        response.raise_for_status()
        status = response.json()
        
        print(f"✅ Directory Search System Status: {status['status']}")
        print(f"🔍 Available Search Types: {len(status['available_search_types'])}")
        
        # Check if save functionality is available
        if "save_to_file" in status['available_search_types']:
            print("💾 Save functionality: Available")
        else:
            print("❌ Save functionality: Not available")
        
        return True
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Server not accessible: {e}")
        print("Please start the server with: python main.py")
        return False

if __name__ == "__main__":
    print("🚀 Starting Ray's Save Functionality Demo")
    print("=" * 50)
    
    if check_server_status():
        ray_save_demonstration()
    else:
        print("\n💡 To run this example:")
        print("1. Start the server: python main.py")
        print("2. Run this script: python examples/directory-search/ray_save_functionality.py")