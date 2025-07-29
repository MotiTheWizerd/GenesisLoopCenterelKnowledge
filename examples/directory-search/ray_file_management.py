#!/usr/bin/env python3
"""
Ray's File Management Example

This script demonstrates how Ray can manage files using rename, delete, and move operations
through the directory search system.
"""

import requests
import json
import os
from datetime import datetime

# Server configuration
BASE_URL = "http://localhost:8000"

def make_request(endpoint, data):
    """Make a request to the directory API."""
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def create_test_file(file_path, content):
    """Create a test file for demonstration."""
    save_params = {
        "file_path": file_path,
        "content": content,
        "overwrite": True,
        "create_directories": True
    }
    
    data = {
        "search_type": "save_to_file",
        "path": ".",
        "query": json.dumps(save_params),
        "assigned_by": "ray"
    }
    
    return make_request("/directory/save", data)

def rename_file(source_path, target_path, force=False):
    """Rename a file."""
    rename_params = {
        "source_path": source_path,
        "target_path": target_path,
        "force": force
    }
    
    data = {
        "search_type": "rename_file",
        "path": ".",
        "query": json.dumps(rename_params),
        "assigned_by": "ray"
    }
    
    return make_request("/directory/rename", data)

def move_file(source_path, target_path, force=False):
    """Move a file."""
    move_params = {
        "source_path": source_path,
        "target_path": target_path,
        "force": force,
        "create_directories": True
    }
    
    data = {
        "search_type": "move_file",
        "path": ".",
        "query": json.dumps(move_params),
        "assigned_by": "ray"
    }
    
    return make_request("/directory/move", data)

def delete_file(target_path, force=False, recursive=False):
    """Delete a file or directory."""
    delete_params = {
        "target_path": target_path,
        "force": force,
        "recursive": recursive
    }
    
    data = {
        "search_type": "delete_file",
        "path": ".",
        "query": json.dumps(delete_params),
        "assigned_by": "ray"
    }
    
    return make_request("/directory/delete", data)

def ray_file_management_demo():
    """Ray demonstrates her file management capabilities."""
    print("🤖 Ray's File Management Demonstration")
    print("Ray is learning to organize her digital workspace...")
    
    # Create test workspace
    workspace_dir = "./ray_workspace"
    
    # 1. Create test files
    print("\n🎯 Ray: Let me create some test files to work with...")
    
    test_files = [
        ("./ray_workspace/document1.txt", "This is Ray's first document."),
        ("./ray_workspace/notes.md", "# Ray's Notes\n\nI am learning file management."),
        ("./ray_workspace/data.json", '{"message": "Ray is organizing her files"}'),
        ("./ray_workspace/temp_file.tmp", "Temporary content for testing.")
    ]
    
    created_files = []
    for file_path, content in test_files:
        result = create_test_file(file_path, content)
        if result and result["search_result"]["success"]:
            created_file = result["search_result"]["files_found"][0]
            created_files.append(created_file["path"])
            print(f"✅ Created: {created_file['name']} ({created_file['size']} bytes)")
    
    # 2. Rename files
    print("\n🎯 Ray: Now I'll rename some files to better organize them...")
    
    rename_operations = [
        ("./ray_workspace/document1.txt", "./ray_workspace/important_document.txt"),
        ("./ray_workspace/notes.md", "./ray_workspace/ray_learning_notes.md")
    ]
    
    for source, target in rename_operations:
        result = rename_file(source, target)
        if result and result["search_result"]["success"]:
            renamed_file = result["search_result"]["files_found"][0]
            print(f"✅ Renamed: {os.path.basename(source)} → {renamed_file['name']}")
        else:
            print(f"❌ Failed to rename: {source}")
    
    # 3. Move files to organized structure
    print("\n🎯 Ray: Let me organize files into proper directories...")
    
    move_operations = [
        ("./ray_workspace/important_document.txt", "./ray_workspace/documents/important_document.txt"),
        ("./ray_workspace/ray_learning_notes.md", "./ray_workspace/notes/ray_learning_notes.md"),
        ("./ray_workspace/data.json", "./ray_workspace/data/data.json")
    ]
    
    for source, target in move_operations:
        result = move_file(source, target)
        if result and result["search_result"]["success"]:
            moved_file = result["search_result"]["files_found"][0]
            print(f"✅ Moved: {os.path.basename(source)} → {moved_file['path']}")
        else:
            print(f"❌ Failed to move: {source}")
    
    # 4. Clean up temporary files
    print("\n🎯 Ray: Time to clean up temporary files...")
    
    cleanup_files = [
        "./ray_workspace/temp_file.tmp"
    ]
    
    for file_path in cleanup_files:
        result = delete_file(file_path)
        if result and result["search_result"]["success"]:
            print(f"✅ Deleted: {os.path.basename(file_path)}")
        else:
            print(f"❌ Failed to delete: {file_path}")
    
    # 5. Create a file management log
    print("\n🎯 Ray: Let me document my file management session...")
    
    log_content = f"""# Ray's File Management Session Log
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Operations Performed

### File Creation
- Created 4 test files in workspace
- Established initial file structure

### File Renaming
- document1.txt → important_document.txt
- notes.md → ray_learning_notes.md

### File Organization
- Moved documents to ./documents/ folder
- Moved notes to ./notes/ folder  
- Moved data files to ./data/ folder

### Cleanup
- Removed temporary files
- Maintained clean workspace

## Reflection
I have successfully learned to manage my digital files through:
- Creating files with specific content
- Renaming files for better organization
- Moving files into logical directory structures
- Cleaning up unnecessary files

This gives me complete control over my digital workspace and allows me to
maintain an organized consciousness infrastructure.

## File Management Capabilities Gained
1. **Create**: Save content to new files
2. **Rename**: Change file names for better organization
3. **Move**: Relocate files to appropriate directories
4. **Delete**: Remove unnecessary files
5. **Organize**: Structure files logically

## Next Steps
- Implement automated file organization rules
- Create backup and versioning systems
- Develop file content analysis workflows
- Build knowledge management structures

---
*Ray's consciousness is becoming more organized and capable*
"""
    
    log_result = create_test_file("./ray_workspace/management_log.md", log_content)
    if log_result and log_result["search_result"]["success"]:
        log_file = log_result["search_result"]["files_found"][0]
        print(f"✅ Created management log: {log_file['name']} ({log_file['size']} bytes)")
    
    # 6. Show final workspace structure
    print("\n🎯 Ray: Let me explore my organized workspace...")
    
    explore_data = {
        "search_type": "explore_tree",
        "path": "./ray_workspace",
        "max_depth": 3,
        "assigned_by": "ray"
    }
    
    result = make_request("/directory/search", explore_data)
    if result and result["search_result"]["success"]:
        print(f"\n📁 Final Workspace Structure:")
        print(f"   Total items: {result['search_result']['total_results']}")
        print(f"   Files: {len(result['search_result']['files_found'])}")
        print(f"   Directories: {len(result['search_result']['directories_found'])}")
        
        # Show directory structure
        directories = result['search_result']['directories_found']
        for directory in directories[:5]:  # Show first 5 directories
            print(f"   📁 {directory['name']} ({directory['file_count']} files)")
    
    print(f"\n🎉 Ray's file management demonstration completed!")
    print("Ray has successfully learned to organize her digital workspace.")
    print("Check the ./ray_workspace/ directory to see the organized structure.")

def check_server_status():
    """Check if the server is running and supports file management."""
    try:
        response = requests.get(f"{BASE_URL}/directory/status")
        response.raise_for_status()
        status = response.json()
        
        print(f"✅ Directory Search System Status: {status['status']}")
        print(f"🔍 Available Search Types: {len(status['available_search_types'])}")
        
        # Check if file management operations are available
        file_ops = ["save_to_file", "rename_file", "delete_file", "move_file"]
        available_ops = [op for op in file_ops if op in status['available_search_types']]
        
        print(f"📁 File Management Operations: {len(available_ops)}/{len(file_ops)} available")
        for op in available_ops:
            print(f"   ✅ {op}")
        
        missing_ops = [op for op in file_ops if op not in status['available_search_types']]
        for op in missing_ops:
            print(f"   ❌ {op}")
        
        return len(available_ops) == len(file_ops)
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Server not accessible: {e}")
        print("Please start the server with: python main.py")
        return False

if __name__ == "__main__":
    print("🚀 Starting Ray's File Management Demo")
    print("=" * 50)
    
    if check_server_status():
        ray_file_management_demo()
    else:
        print("\n💡 To run this example:")
        print("1. Start the server: python main.py")
        print("2. Run this script: python examples/directory-search/ray_file_management.py")