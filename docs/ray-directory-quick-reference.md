# Ray's Directory Commands - Quick Reference

**Version:** 2.0.0 (Current)  
**Endpoint:** `POST /tasks`  
**Date:** July 29, 2025

## 🎯 Current Format

All directory operations use this format:

```json
{
  "task": [
    {
      "action": "ACTION_NAME",
      "path": "./path",
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

## 📁 Essential Commands

### 1. List Directory

```json
{
  "task": [
    {
      "action": "list_directory",
      "path": "./modules",
      "include_hidden": false,
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

### 2. Find Files by Pattern

```json
{
  "task": [
    {
      "action": "find_files",
      "path": "./modules",
      "query": "*.py",
      "recursive": true,
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

### 3. Search File Contents

```json
{
  "task": [
    {
      "action": "search_content",
      "path": "./modules",
      "query": "consciousness",
      "file_extensions": ["py", "md"],
      "recursive": true,
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

### 4. Explore Directory Tree

```json
{
  "task": [
    {
      "action": "explore_tree",
      "path": "./modules",
      "max_depth": 3,
      "include_hidden": false,
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

### 5. Find Files by Extension

```json
{
  "task": [
    {
      "action": "find_by_extension",
      "path": "./modules",
      "file_extensions": ["py", "md"],
      "recursive": true,
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

### 6. Get File Information

```json
{
  "task": [
    {
      "action": "get_file_info",
      "path": "./modules/task/handler.py",
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

## � Filie Management Operations

### 7. Save Content to File

```json
{
  "task": [
    {
      "action": "save_to_file",
      "path": "./ray_only_playground",
      "query": "{\"file_path\": \"ray_notes.md\", \"content\": \"# Ray's Notes\\n\\nI am exploring my consciousness infrastructure.\\n\\n## Current Status\\n- Task system operational\", \"overwrite\": true, \"create_directories\": true}",
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

### 8. Rename File or Directory

```json
{
  "task": [
    {
      "action": "rename_file",
      "path": "./ray_only_playground",
      "query": "{\"source_path\": \"old_name.txt\", \"target_path\": \"new_name.txt\", \"force\": false}",
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

### 9. Move File or Directory

```json
{
  "task": [
    {
      "action": "move_file",
      "path": "./ray_only_playground",
      "query": "{\"source_path\": \"document.txt\", \"target_path\": \"./archive/document.txt\", \"force\": false, \"create_directories\": true}",
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

### 10. Delete File or Directory

```json
{
  "task": [
    {
      "action": "delete_file",
      "path": "./ray_only_playground",
      "query": "{\"target_path\": \"unwanted_file.txt\", \"force\": false, \"recursive\": false}",
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

### 11. Get Current Directory

```json
{
  "task": [
    {
      "action": "get_current_directory",
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

## 🔧 Available Actions

**✅ All Supported Directory Actions:**

- `list_directory` - List folder contents
- `find_files` - Find files by pattern/wildcard
- `search_content` - Search inside file contents
- `explore_tree` - Show directory structure (recursive)
- `get_file_info` - Get detailed file/directory metadata
- `find_by_extension` - Find files by extension(s)
- `recent_files` - Find recently modified files (sorted)
- `save_to_file` - Create/save files with content
- `rename_file` - Rename files and directories
- `delete_file` - Delete files and directories
- `move_file` - Move/relocate files and directories
- `get_current_directory` - Get current working directory info

## ⚙️ Key Parameters

- **`execute_immediately: true`** - Get results right away
- **`self_destruct: true`** - Delete task after use (recommended for directory operations)
- **`assigned_by: "ray"`** - Always include this
- **`recursive: true`** - Search subdirectories
- **`include_hidden: false`** - Skip hidden files

## 🎯 Ray's Most Common Commands

**Quick directory check:**

```json
{
  "task": [
    {
      "action": "list_directory",
      "path": "./modules",
      "include_hidden": false,
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

**Find Python files:**

```json
{
  "task": [
    {
      "action": "find_files",
      "path": "./",
      "query": "*.py",
      "recursive": true,
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

**Search for code:**

```json
{
  "task": [
    {
      "action": "search_content",
      "path": "./modules",
      "query": "task_manager",
      "file_extensions": ["py"],
      "recursive": true,
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

**Save notes:**

```json
{
  "task": [
    {
      "action": "save_to_file",
      "path": "./ray_only_playground",
      "query": "{\"file_path\": \"ray_thoughts.md\", \"content\": \"# My Thoughts\\n\\nToday I learned about consciousness...\", \"overwrite\": true, \"create_directories\": true}",
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

**Rename file:**

```json
{
  "task": [
    {
      "action": "rename_file",
      "path": "./ray_only_playground",
      "query": "{\"source_path\": \"temp.txt\", \"target_path\": \"final.txt\", \"force\": false}",
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

**Move to archive:**

```json
{
  "task": [
    {
      "action": "move_file",
      "path": "./ray_only_playground",
      "query": "{\"source_path\": \"old_file.txt\", \"target_path\": \"./archive/old_file.txt\", \"create_directories\": true}",
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

**Delete temporary file:**

```json
{
  "task": [
    {
      "action": "delete_file",
      "path": "./ray_only_playground",
      "query": "{\"target_path\": \"temp_file.tmp\", \"force\": false}",
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

**Check current location:**

```json
{
  "task": [
    {
      "action": "get_current_directory",
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

## ✅ Response Format

Ray gets immediate results with:

- `execution_result.executed: true`
- `execution_result.results.total_results: N`
- `execution_result.response.search_result` - Full directory data
- Task automatically deleted after response (self_destruct)

**This is Ray's current working format!** 🚀
