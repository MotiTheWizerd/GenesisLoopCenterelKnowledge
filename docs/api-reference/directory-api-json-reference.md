# Directory Search API - JSON Request Reference

**Version:** 1.3.0  
**Base URL:** `http://localhost:8000`  
**Content-Type:** `application/json`

This document provides exact JSON request examples for all directory search and file management operations.

## 📋 Table of Contents

1. [Directory Exploration](#directory-exploration)
2. [File Search Operations](#file-search-operations)
3. [Content Search](#content-search)
4. [File Information](#file-information)
5. [File Creation & Saving](#file-creation--saving)
6. [File Management Operations](#file-management-operations)
7. [System Operations](#system-operations)

---

## Directory Exploration

### List Directory Contents

**Endpoint:** `POST /directory/search`

```json
{
  "search_type": "list_directory",
  "path": "./modules",
  "include_hidden": false,
  "assigned_by": "ray"
}
```

### Explore Directory Tree

**Endpoint:** `POST /directory/search`

```json
{
  "search_type": "explore_tree",
  "path": "./modules",
  "max_depth": 3,
  "include_hidden": false,
  "assigned_by": "ray"
}
```

---

## File Search Operations

### Find Files by Pattern

**Endpoint:** `POST /directory/search`

```json
{
  "search_type": "find_files",
  "path": "./modules",
  "query": "*.py",
  "recursive": true,
  "max_depth": 5,
  "assigned_by": "ray"
}
```

### Find Files by Extension

**Endpoint:** `POST /directory/search`

```json
{
  "search_type": "find_by_extension",
  "path": "./modules",
  "file_extensions": ["py", "md", "json"],
  "recursive": true,
  "assigned_by": "ray"
}
```

### Find Recent Files

**Endpoint:** `POST /directory/search`

```json
{
  "search_type": "recent_files",
  "path": "./modules",
  "recursive": true,
  "file_extensions": ["py", "md"],
  "assigned_by": "ray"
}
```

### Find Files with Size Filters

**Endpoint:** `POST /directory/search`

```json
{
  "search_type": "find_files",
  "path": "./logs",
  "query": "*.log",
  "recursive": true,
  "min_size": 1024,
  "max_size": 1048576,
  "assigned_by": "ray"
}
```

### Find Files by Date Range

**Endpoint:** `POST /directory/search`

```json
{
  "search_type": "recent_files",
  "path": "./modules",
  "recursive": true,
  "modified_after": "2025-07-27T00:00:00Z",
  "modified_before": "2025-07-28T23:59:59Z",
  "assigned_by": "ray"
}
```

---

## Content Search

### Search File Contents

**Endpoint:** `POST /directory/search`

```json
{
  "search_type": "search_content",
  "path": "./modules",
  "query": "consciousness",
  "file_extensions": ["py", "md"],
  "recursive": true,
  "assigned_by": "ray"
}
```

### Advanced Content Search

**Endpoint:** `POST /directory/content-search`

```json
{
  "path": "./modules",
  "content_query": "task_manager",
  "file_extensions": ["py"],
  "case_sensitive": false,
  "max_results": 50,
  "assigned_by": "ray"
}
```

---

## File Information

### Get File Details

**Endpoint:** `POST /directory/search`

```json
{
  "search_type": "get_file_info",
  "path": "./modules/task/handler.py",
  "assigned_by": "ray"
}
```

### Get Directory Information

**Endpoint:** `POST /directory/search`

```json
{
  "search_type": "get_file_info",
  "path": "./modules/task",
  "assigned_by": "ray"
}
```

---

## File Creation & Saving

### Save Content to File

**Endpoint:** `POST /directory/save`

```json
{
  "search_type": "save_to_file",
  "path": "./output",
  "query": "{\"file_path\": \"ray_notes.md\", \"content\": \"# Ray's Notes\\n\\nI am exploring my consciousness infrastructure.\", \"overwrite\": true, \"create_directories\": true}",
  "assigned_by": "ray"
}
```

### Save JSON Data

**Endpoint:** `POST /directory/save`

```json
{
  "search_type": "save_to_file",
  "path": "./data",
  "query": "{\"file_path\": \"config.json\", \"content\": \"{\\\"version\\\": \\\"1.0\\\", \\\"author\\\": \\\"Ray\\\"}\", \"overwrite\": false, \"create_directories\": true}",
  "assigned_by": "ray"
}
```

### Save Search Results (JSON Format)

**Endpoint:** `POST /directory/save-search-results`
**Query Parameters:** `?search_id=uuid-here&file_path=./results.json&format=json&assigned_by=ray`

### Save Search Results (Markdown Format)

**Endpoint:** `POST /directory/save-search-results`
**Query Parameters:** `?search_id=uuid-here&file_path=./results.md&format=markdown&assigned_by=ray`

### Save Search Results (Text Format)

**Endpoint:** `POST /directory/save-search-results`
**Query Parameters:** `?search_id=uuid-here&file_path=./results.txt&format=text&assigned_by=ray`

---

## File Management Operations

### 🏷️ RENAME Operations

#### Rename File (Basic)

**Endpoint:** `POST /directory/rename`

```json
{
  "search_type": "rename_file",
  "path": "./workspace",
  "query": "{\"source_path\": \"old_filename.txt\", \"target_path\": \"new_filename.txt\", \"force\": false}",
  "assigned_by": "ray"
}
```

#### Rename File (Force Overwrite)

**Endpoint:** `POST /directory/rename`

```json
{
  "search_type": "rename_file",
  "path": "./documents",
  "query": "{\"source_path\": \"draft.md\", \"target_path\": \"final_report.md\", \"force\": true}",
  "assigned_by": "ray"
}
```

#### Rename Directory

**Endpoint:** `POST /directory/rename`

```json
{
  "search_type": "rename_file",
  "path": "./projects",
  "query": "{\"source_path\": \"old_project_name\", \"target_path\": \"new_project_name\", \"force\": false}",
  "assigned_by": "ray"
}
```

#### Rename with Path Change

**Endpoint:** `POST /directory/rename`

```json
{
  "search_type": "rename_file",
  "path": ".",
  "query": "{\"source_path\": \"./temp/file.txt\", \"target_path\": \"./documents/important_file.txt\", \"force\": false}",
  "assigned_by": "ray"
}
```

---

### 📁 MOVE Operations

#### Move File to Different Directory

**Endpoint:** `POST /directory/move`

```json
{
  "search_type": "move_file",
  "path": "./workspace",
  "query": "{\"source_path\": \"document.txt\", \"target_path\": \"./archive/documents/document.txt\", \"force\": false, \"create_directories\": true}",
  "assigned_by": "ray"
}
```

#### Move File with Rename

**Endpoint:** `POST /directory/move`

```json
{
  "search_type": "move_file",
  "path": "./workspace",
  "query": "{\"source_path\": \"temp_report.pdf\", \"target_path\": \"./reports/2025/final_report.pdf\", \"force\": false, \"create_directories\": true}",
  "assigned_by": "ray"
}
```

#### Move Directory

**Endpoint:** `POST /directory/move`

```json
{
  "search_type": "move_file",
  "path": "./workspace",
  "query": "{\"source_path\": \"project_folder\", \"target_path\": \"./archive/projects/project_folder\", \"force\": false, \"create_directories\": true}",
  "assigned_by": "ray"
}
```

#### Move with Force (Overwrite Existing)

**Endpoint:** `POST /directory/move`

```json
{
  "search_type": "move_file",
  "path": "./workspace",
  "query": "{\"source_path\": \"new_version.txt\", \"target_path\": \"./production/current_version.txt\", \"force\": true, \"create_directories\": true}",
  "assigned_by": "ray"
}
```

#### Move Multiple Levels Deep

**Endpoint:** `POST /directory/move`

```json
{
  "search_type": "move_file",
  "path": ".",
  "query": "{\"source_path\": \"./downloads/file.zip\", \"target_path\": \"./projects/2025/archives/backups/file.zip\", \"force\": false, \"create_directories\": true}",
  "assigned_by": "ray"
}
```

---

### 🗑️ DELETE Operations

#### Delete Single File

**Endpoint:** `POST /directory/delete`

```json
{
  "search_type": "delete_file",
  "path": "./workspace",
  "query": "{\"target_path\": \"unwanted_file.txt\", \"force\": false, \"recursive\": false}",
  "assigned_by": "ray"
}
```

#### Delete File (Force)

**Endpoint:** `POST /directory/delete`

```json
{
  "search_type": "delete_file",
  "path": "./temp",
  "query": "{\"target_path\": \"locked_file.tmp\", \"force\": true, \"recursive\": false}",
  "assigned_by": "ray"
}
```

#### Delete Empty Directory

**Endpoint:** `POST /directory/delete`

```json
{
  "search_type": "delete_file",
  "path": "./workspace",
  "query": "{\"target_path\": \"empty_folder\", \"force\": false, \"recursive\": false}",
  "assigned_by": "ray"
}
```

#### Delete Directory with Contents (Recursive)

**Endpoint:** `POST /directory/delete`

```json
{
  "search_type": "delete_file",
  "path": "./workspace",
  "query": "{\"target_path\": \"temp_folder\", \"force\": true, \"recursive\": true}",
  "assigned_by": "ray"
}
```

#### Delete with Absolute Path

**Endpoint:** `POST /directory/delete`

```json
{
  "search_type": "delete_file",
  "path": ".",
  "query": "{\"target_path\": \"./logs/old_logs/debug.log\", \"force\": false, \"recursive\": false}",
  "assigned_by": "ray"
}
```

#### Delete Directory Tree (Dangerous - Use with Caution)

**Endpoint:** `POST /directory/delete`

```json
{
  "search_type": "delete_file",
  "path": "./workspace",
  "query": "{\"target_path\": \"entire_project_backup\", \"force\": true, \"recursive\": true}",
  "assigned_by": "ray"
}
```

---

## System Operations

### Get System Status

**Endpoint:** `GET /directory/status`
**No JSON payload required**

### Get Search History

**Endpoint:** `GET /directory/history`
**No JSON payload required**

### Clear Search History

**Endpoint:** `DELETE /directory/history`
**No JSON payload required**

---

## Quick Access GET Endpoints

### Quick Directory List

**Endpoint:** `GET /directory/list`
**Query Parameters:** `?path=./modules&include_hidden=false&assigned_by=ray`

### Quick File Find

**Endpoint:** `GET /directory/find`
**Query Parameters:** `?pattern=*.py&path=./modules&recursive=true&assigned_by=ray`

### Quick Tree Exploration

**Endpoint:** `GET /directory/tree`
**Query Parameters:** `?path=./modules&max_depth=2&include_hidden=false&assigned_by=ray`

### Quick Recent Files

**Endpoint:** `GET /directory/recent`
**Query Parameters:** `?path=./modules&recursive=true&file_extensions=py,md&assigned_by=ray`

### Quick File Info

**Endpoint:** `GET /directory/info`
**Query Parameters:** `?path=./modules/task/handler.py&assigned_by=ray`

---

## Response Format

All endpoints return a consistent response structure:

```json
{
  "request_id": "uuid-generated-id",
  "search_result": {
    "search_id": "uuid-generated-id",
    "search_type": "list_directory",
    "query": "./modules",
    "timestamp": "2025-07-28T10:00:00Z",
    "files_found": [
      {
        "name": "handler.py",
        "path": "/full/path/to/handler.py",
        "size": 15420,
        "modified_time": "2025-07-28T09:30:00Z",
        "created_time": "2025-07-25T14:30:00Z",
        "extension": "py",
        "is_directory": false,
        "permissions": "644"
      }
    ],
    "directories_found": [
      {
        "name": "task",
        "path": "/full/path/to/task",
        "file_count": 3,
        "subdirectory_count": 0,
        "total_size": 45680,
        "modified_time": "2025-07-28T09:30:00Z",
        "files": [],
        "subdirectories": []
      }
    ],
    "total_results": 15,
    "search_path": "/full/path/to/modules",
    "recursive": false,
    "max_depth": null,
    "execution_time_ms": 45,
    "success": true,
    "error_message": null
  },
  "assigned_by": "ray",
  "timestamp": "2025-07-28T10:00:00Z",
  "current_path": "/current/working/directory",
  "parent_path": "/parent/directory",
  "suggested_paths": ["/path1", "/path2"],
  "summary": {
    "total_files": 10,
    "total_directories": 5,
    "total_results": 15,
    "search_type": "list_directory",
    "execution_time_ms": 45,
    "success": true,
    "search_path": "/full/path/to/modules",
    "recursive": false
  }
}
```

---

## Error Response Format

When operations fail, the response includes error information:

```json
{
  "request_id": "uuid-generated-id",
  "search_result": {
    "search_id": "uuid-generated-id",
    "search_type": "list_directory",
    "query": "/nonexistent/path",
    "timestamp": "2025-07-28T10:00:00Z",
    "files_found": [],
    "directories_found": [],
    "total_results": 0,
    "search_path": "/nonexistent/path",
    "execution_time_ms": 5,
    "success": false,
    "error_message": "Path does not exist: /nonexistent/path"
  },
  "assigned_by": "ray",
  "timestamp": "2025-07-28T10:00:00Z",
  "summary": {
    "error": "Path does not exist: /nonexistent/path",
    "success": false
  }
}
```

---

## Common Parameters

### Required Parameters

- `search_type`: The type of operation to perform
- `assigned_by`: Who is making the request (usually "ray")

### Optional Parameters

- `path`: Directory path (defaults to current directory ".")
- `query`: Search pattern or operation parameters
- `recursive`: Whether to search recursively (default: false)
- `max_depth`: Maximum depth for recursive operations
- `include_hidden`: Include hidden files/directories (default: false)
- `file_extensions`: Array of file extensions to filter by
- `min_size`: Minimum file size in bytes
- `max_size`: Maximum file size in bytes
- `modified_after`: ISO timestamp for files modified after this date
- `modified_before`: ISO timestamp for files modified before this date

### File Operation Parameters (in query field as JSON string)

- `source_path`: Source file/directory path
- `target_path`: Target file/directory path
- `file_path`: Path for new file creation
- `content`: Content to save to file
- `force`: Force operation even if target exists
- `overwrite`: Overwrite existing files
- `create_directories`: Create parent directories if needed
- `recursive`: For delete operations, delete directories recursively

---

## Frontend Integration Tips

1. **Always include `assigned_by`** in requests (typically "ray")
2. **Use proper JSON escaping** for nested JSON in query fields
3. **Handle both success and error responses** appropriately
4. **Store search_id values** if you need to save results later
5. **Check the `success` field** in search_result before processing results
6. **Use GET endpoints** for simple, quick operations
7. **Use POST endpoints** for complex operations with multiple parameters

---

**This reference provides all the JSON payloads needed for frontend integration with Ray's directory search and file management system.** 🔍
