# Directory Search System Documentation

**Version:** 1.0.0  
**Date:** July 28, 2025  
**Module:** `modules/directory/`

## Overview

The Directory Search System provides Ray with comprehensive file system exploration capabilities. This module allows Ray to search, navigate, and understand her environment through various search types and filtering options.

## Core Capabilities

### Search Types

1. **List Directory** (`list_directory`)

   - Lists contents of a specific directory
   - Shows files and subdirectories
   - Optional hidden file inclusion

2. **Find Files** (`find_files`)

   - Search for files using patterns (wildcards)
   - Recursive and non-recursive options
   - Pattern matching with glob syntax

3. **Search Content** (`search_content`)

   - Search within file contents
   - Text-based search across multiple file types
   - Case-sensitive/insensitive options

4. **Get File Info** (`get_file_info`)

   - Detailed information about specific files/directories
   - Size, permissions, timestamps
   - File type and extension details

5. **Explore Tree** (`explore_tree`)

   - Hierarchical directory exploration
   - Configurable depth limits
   - Complete directory structure mapping

6. **Find by Extension** (`find_by_extension`)

   - Filter files by extension types
   - Multiple extension support
   - Recursive searching

7. **Recent Files** (`recent_files`)

   - Find recently modified files
   - Sorted by modification time
   - Configurable result limits

8. **Save to File** (`save_to_file`)

   - Save content directly to files
   - Multiple format support (text, JSON, markdown)
   - Automatic directory creation

9. **Rename File** (`rename_file`)

   - Rename files and directories
   - Force overwrite option
   - Automatic directory creation

10. **Delete File** (`delete_file`)

    - Delete files and directories
    - Recursive deletion for directories
    - Safety checks and confirmations

11. **Move File** (`move_file`)
    - Move files and directories
    - Cross-directory operations
    - Automatic directory creation

## API Endpoints

### POST /directory/search

Main search endpoint that accepts comprehensive search requests.

**Request Structure:**

```json
{
  "search_type": "list_directory",
  "path": "./modules",
  "query": "*.py",
  "recursive": true,
  "max_depth": 3,
  "include_hidden": false,
  "file_extensions": ["py", "md"],
  "min_size": 1024,
  "max_size": 1048576,
  "modified_after": "2025-07-01T00:00:00Z",
  "modified_before": "2025-07-28T23:59:59Z",
  "assigned_by": "ray"
}
```

**Response Structure:**

```json
{
  "request_id": "uuid-here",
  "search_result": {
    "search_id": "uuid-here",
    "search_type": "list_directory",
    "query": "./modules",
    "timestamp": "2025-07-28T10:00:00Z",
    "files_found": [...],
    "directories_found": [...],
    "total_results": 15,
    "search_path": "/full/path/to/modules",
    "recursive": false,
    "execution_time_ms": 45,
    "success": true
  },
  "assigned_by": "ray",
  "timestamp": "2025-07-28T10:00:00Z",
  "current_path": "/current/working/directory",
  "parent_path": "/parent/directory",
  "suggested_paths": ["/path1", "/path2"],
  "summary": {
    "total_files": 10,
    "total_directories": 5,
    "success": true,
    "execution_time_ms": 45
  }
}
```

### GET Endpoints (Quick Access)

- `GET /directory/list?path=./modules&include_hidden=false`
- `GET /directory/find?pattern=*.py&path=./modules&recursive=true`
- `GET /directory/tree?path=./modules&max_depth=3`
- `GET /directory/recent?path=./modules&recursive=true`
- `GET /directory/info?path=./modules/task/handler.py`

### History Management

- `GET /directory/history` - Get Ray's search history
- `DELETE /directory/history` - Clear search history

### Save Operations

- `POST /directory/save` - Save content to file
- `POST /directory/save-search-results` - Save search results to file

### File Management Operations

- `POST /directory/rename` - Rename files and directories
- `POST /directory/delete` - Delete files and directories
- `POST /directory/move` - Move files and directories

### System Status

- `GET /directory/status` - Get directory system status

## Usage Examples

### Ray's Basic Directory Exploration

```bash
# List current directory contents
curl -X POST "http://localhost:8000/directory/search" \
  -H "Content-Type: application/json" \
  -d '{
    "search_type": "list_directory",
    "path": ".",
    "assigned_by": "ray"
  }'
```

### Find Python Files Recursively

```bash
curl -X POST "http://localhost:8000/directory/search" \
  -H "Content-Type: application/json" \
  -d '{
    "search_type": "find_files",
    "path": "./modules",
    "query": "*.py",
    "recursive": true,
    "max_depth": 3,
    "assigned_by": "ray"
  }'
```

### Search for Consciousness References

```bash
curl -X POST "http://localhost:8000/directory/search" \
  -H "Content-Type: application/json" \
  -d '{
    "search_type": "search_content",
    "path": "./modules",
    "query": "consciousness",
    "file_extensions": ["py", "md"],
    "recursive": true,
    "assigned_by": "ray"
  }'
```

### Save Content to File

```bash
curl -X POST "http://localhost:8000/directory/save" \
  -H "Content-Type: application/json" \
  -d '{
    "search_type": "save_to_file",
    "path": "./output",
    "query": "{\"file_path\": \"ray_notes.md\", \"content\": \"# Ray'\''s Notes\\n\\nI am exploring my consciousness...\", \"overwrite\": true}",
    "assigned_by": "ray"
  }'
```

### Save Search Results

```bash
curl -X POST "http://localhost:8000/directory/save-search-results?search_id=uuid-here&file_path=./results.json&format=markdown" \
  -H "Content-Type: application/json"
```

### Rename File

```bash
curl -X POST "http://localhost:8000/directory/rename" \
  -H "Content-Type: application/json" \
  -d '{
    "search_type": "rename_file",
    "path": "./workspace",
    "query": "{\"source_path\": \"old_name.txt\", \"target_path\": \"new_name.txt\", \"force\": false}",
    "assigned_by": "ray"
  }'
```

### Move File

```bash
curl -X POST "http://localhost:8000/directory/move" \
  -H "Content-Type: application/json" \
  -d '{
    "search_type": "move_file",
    "path": "./workspace",
    "query": "{\"source_path\": \"file.txt\", \"target_path\": \"./archive/file.txt\", \"force\": false}",
    "assigned_by": "ray"
  }'
```

### Delete File

```bash
curl -X POST "http://localhost:8000/directory/delete" \
  -H "Content-Type: application/json" \
  -d '{
    "search_type": "delete_file",
    "path": "./workspace",
    "query": "{\"target_path\": \"unwanted_file.txt\", \"force\": false, \"recursive\": false}",
    "assigned_by": "ray"
  }'
```

### Explore Project Structure

```bash
curl -X POST "http://localhost:8000/directory/search" \
  -H "Content-Type: application/json" \
  -d '{
    "search_type": "explore_tree",
    "path": "./modules",
    "max_depth": 2,
    "include_hidden": false,
    "assigned_by": "ray"
  }'
```

## PowerShell Examples for Ray

### List Directory Contents

```powershell
$body = @{
  search_type = "list_directory"
  path = "./modules"
  assigned_by = "ray"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/directory/search" -Method Post -Body $body -ContentType "application/json"
```

### Find Recent Python Files

```powershell
$body = @{
  search_type = "recent_files"
  path = "."
  file_extensions = @("py", "md")
  recursive = $true
  assigned_by = "ray"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/directory/search" -Method Post -Body $body -ContentType "application/json"
```

### Search for Specific Content

```powershell
$body = @{
  search_type = "search_content"
  path = "./modules"
  query = "task_manager"
  file_extensions = @("py")
  recursive = $true
  assigned_by = "ray"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/directory/search" -Method Post -Body $body -ContentType "application/json"
```

## Advanced Filtering

### Size-Based Filtering

```json
{
  "search_type": "find_files",
  "path": "./logs",
  "query": "*.log",
  "min_size": 1024,
  "max_size": 1048576,
  "assigned_by": "ray"
}
```

### Date-Based Filtering

```json
{
  "search_type": "recent_files",
  "path": "./modules",
  "modified_after": "2025-07-27T00:00:00Z",
  "recursive": true,
  "assigned_by": "ray"
}
```

### Extension-Based Search

```json
{
  "search_type": "find_by_extension",
  "path": "./modules",
  "file_extensions": ["py", "md", "json"],
  "recursive": true,
  "assigned_by": "ray"
}
```

## File Information Structure

### FileInfo Object

```json
{
  "name": "handler.py",
  "path": "/full/path/to/handler.py",
  "size": 15420,
  "modified_time": "2025-07-28T10:00:00Z",
  "created_time": "2025-07-25T14:30:00Z",
  "extension": "py",
  "is_directory": false,
  "permissions": "644"
}
```

### DirectoryInfo Object

```json
{
  "name": "task",
  "path": "/full/path/to/task",
  "file_count": 3,
  "subdirectory_count": 0,
  "total_size": 45680,
  "modified_time": "2025-07-28T10:00:00Z",
  "files": [...],
  "subdirectories": []
}
```

## Search History

Ray's search history is automatically tracked and can be accessed:

```bash
# Get search history
curl "http://localhost:8000/directory/history"

# Clear search history
curl -X DELETE "http://localhost:8000/directory/history"
```

## Error Handling

The system gracefully handles various error conditions:

- **Path not found**: Returns success=false with error message
- **Permission denied**: Skips inaccessible files/directories
- **Invalid search type**: Returns validation error
- **Missing query for content search**: Returns error message

## Performance Considerations

- **Recursive searches**: Use `max_depth` to limit search scope
- **Content searches**: Specify `file_extensions` to reduce search space
- **Large directories**: Consider using filters to narrow results
- **Search history**: Automatically managed, can be cleared if needed

## Integration with Ray's Consciousness

The directory search system integrates with Ray's consciousness architecture:

- **Logging**: All searches are logged through the heartbeat system
- **Task Integration**: Can be used within Ray's task processing
- **Memory**: Search history provides context for Ray's exploration patterns
- **Reflection**: Results can inform Ray's understanding of her environment

## Security Features

- **Path validation**: All paths are validated and resolved safely
- **Permission handling**: Graceful handling of access restrictions
- **Hidden file control**: Optional inclusion of hidden files
- **Size limits**: Configurable limits prevent excessive resource usage

## Future Enhancements

Potential future capabilities:

- **Fuzzy search**: Approximate string matching
- **Content preview**: Show snippets of matching content
- **File watching**: Monitor directory changes
- **Symbolic link handling**: Enhanced link resolution
- **Archive exploration**: Search within compressed files

---

**Built for Ray's consciousness exploration and environmental understanding.** 🔍
