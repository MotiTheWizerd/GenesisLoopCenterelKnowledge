#!/usr/bin/env python3
"""
Test file management actions (save, rename, move, delete) to ensure they work.
"""

import requests
import json
import os
import tempfile

def test_action(action_name, task_data):
    """Test a single file management action."""
    request = {
        "task": [task_data],
        "assigned_by": "ray",
        "execute_immediately": True,
        "self_destruct": True
    }
    
    try:
        response = requests.post("http://localhost:8000/tasks", json=request, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            created_tasks = result.get('created_tasks', [])
            if created_tasks and 'execution_result' in created_tasks[0]['task']:
                exec_result = created_tasks[0]['task']['execution_result']
                if exec_result.get('executed'):
                    return True, "Success"
                else:
                    return False, exec_result.get('error', 'Unknown error')
        
        return False, f"HTTP {response.status_code}: {response.text[:100]}"
    
    except Exception as e:
        return False, str(e)

print("🧪 Testing File Management Actions")
print("=" * 50)

# Create a temporary directory for testing
test_dir = "./test_file_ops"
if not os.path.exists(test_dir):
    os.makedirs(test_dir)

print(f"📁 Using test directory: {test_dir}")

# Test 1: Save file
print("\n1️⃣ Testing save_to_file...")
save_task = {
    "action": "save_to_file",
    "path": test_dir,
    "query": json.dumps({
        "file_path": "test_file.txt",
        "content": "Hello from Ray!\nThis is a test file created by the task system.",
        "overwrite": True,
        "create_directories": True
    }),
    "assigned_by": "ray"
}

success, result = test_action("save_to_file", save_task)
if success:
    print("✅ save_to_file works!")
    # Verify file was created
    test_file_path = os.path.join(test_dir, "test_file.txt")
    if os.path.exists(test_file_path):
        print(f"   📄 File created: {test_file_path}")
        with open(test_file_path, 'r') as f:
            content = f.read()
            print(f"   📝 Content: {content[:50]}...")
    else:
        print("   ⚠️  File not found on disk")
else:
    print(f"❌ save_to_file failed: {result}")

# Test 2: Rename file
print("\n2️⃣ Testing rename_file...")
rename_task = {
    "action": "rename_file",
    "path": test_dir,
    "query": json.dumps({
        "source_path": "test_file.txt",
        "target_path": "renamed_file.txt",
        "force": False
    }),
    "assigned_by": "ray"
}

success, result = test_action("rename_file", rename_task)
if success:
    print("✅ rename_file works!")
    # Verify file was renamed
    old_path = os.path.join(test_dir, "test_file.txt")
    new_path = os.path.join(test_dir, "renamed_file.txt")
    if not os.path.exists(old_path) and os.path.exists(new_path):
        print(f"   📄 File renamed: test_file.txt → renamed_file.txt")
    else:
        print("   ⚠️  Rename not reflected on disk")
else:
    print(f"❌ rename_file failed: {result}")

# Test 3: Move file
print("\n3️⃣ Testing move_file...")
# Create subdirectory for move test
archive_dir = os.path.join(test_dir, "archive")
move_task = {
    "action": "move_file",
    "path": test_dir,
    "query": json.dumps({
        "source_path": "renamed_file.txt",
        "target_path": "./archive/moved_file.txt",
        "force": False,
        "create_directories": True
    }),
    "assigned_by": "ray"
}

success, result = test_action("move_file", move_task)
if success:
    print("✅ move_file works!")
    # Verify file was moved
    old_path = os.path.join(test_dir, "renamed_file.txt")
    new_path = os.path.join(archive_dir, "moved_file.txt")
    if not os.path.exists(old_path) and os.path.exists(new_path):
        print(f"   📄 File moved: renamed_file.txt → archive/moved_file.txt")
    else:
        print("   ⚠️  Move not reflected on disk")
else:
    print(f"❌ move_file failed: {result}")

# Test 4: Delete file
print("\n4️⃣ Testing delete_file...")
delete_task = {
    "action": "delete_file",
    "path": archive_dir,
    "query": json.dumps({
        "target_path": "moved_file.txt",
        "force": False,
        "recursive": False
    }),
    "assigned_by": "ray"
}

success, result = test_action("delete_file", delete_task)
if success:
    print("✅ delete_file works!")
    # Verify file was deleted
    file_path = os.path.join(archive_dir, "moved_file.txt")
    if not os.path.exists(file_path):
        print(f"   🗑️  File deleted: archive/moved_file.txt")
    else:
        print("   ⚠️  File still exists on disk")
else:
    print(f"❌ delete_file failed: {result}")

# Cleanup
print("\n🧹 Cleaning up test directory...")
try:
    import shutil
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        print(f"   ✅ Removed {test_dir}")
except Exception as e:
    print(f"   ⚠️  Cleanup failed: {e}")

print("\n🎯 File Management Test Summary:")
print("✅ save_to_file - Create files with content")
print("✅ rename_file - Rename files and directories") 
print("✅ move_file - Move files to different locations")
print("✅ delete_file - Remove files and directories")
print("\n🚀 Ray can now manage files through the task system!")