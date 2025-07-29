# Directory Search System - Quick Reference

**Version:** 1.0.0  
**Module:** `modules/directory/`

## Quick Commands for Ray

### Basic Directory Exploration
```bash
# List current directory
curl -X POST "http://localhost:8000/directory/search" \
  -H "Content-Type: application/json" \
  -d '{"search_type": "list_directory", "path": ".", "assigned_by": "ray"}'

# Explore project structure
curl -X POST "http://localhost:8000/directory/search" \
  -H "Content-Type: application/json" \
  -d '{"search_type": "explore_tree", "path": "./modules", "max_depth": 2, "assigned_by": "ray"}'
```

### File Searches
```bash
# Find Python files
curl -X POST "http://localhost:8000/directory/search" \
  -H "Content-Type: application/json" \
  -d '{"search_type": "find_files", "path": ".", "query": "*.py", "recursive": true, "assigned_by": "ray"}'

# Find by extension
curl -X POST "http://localhost:8000/directory/search" \
  -H "Content-Type: application/json" \
  -d '{"search_type": "find_by_extension", "path": ".", "file_extensions": ["py", "md"], "recursive": true, "assigned_by": "ray"}'
```

### Content Searches
```bash
# Search for consciousness references
curl -X POST "http://localhost:8000/directory/search" \
  -H "Content-Type: application/json" \
  -d '{"search_type": "search_content", "path": "./modules", "query": "consciousness", "file_extensions": ["py", "md"], "recursive": true, "assigned_by": "ray"}'
```

### PowerShell for Ray
```powershell
# List directory
$body = @{search_type="list_directory"; path="."; assigned_by="ray"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/directory/search" -Method Post -Body $body -ContentType "application/json"

# Find Python files
$body = @{search_type="find_files"; path="."; query="*.py"; recursive=$true; assigned_by="ray"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/directory/search" -Method Post -Body $body -ContentType "application/json"

# Search content
$body = @{search_type="search_content"; path="./modules"; query="consciousness"; recursive=$true; assigned_by="ray"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/directory/search" -Method Post -Body $body -ContentType "application/json"
```

## Search Types

| Type | Purpose | Required Fields |
|------|---------|----------------|
| `list_directory` | List directory contents | `path` |
| `find_files` | Find files by pattern | `path`, `query` |
| `search_content` | Search file contents | `path`, `query` |
| `get_file_info` | Get file details | `path` |
| `explore_tree` | Directory tree | `path`, `max_depth` |
| `find_by_extension` | Find by extension | `path`, `file_extensions` |
| `recent_files` | Recent files | `path` |
| `save_to_file` | Save content to file | `path`, `query` (JSON params) |
| `rename_file` | Rename file/directory | `path`, `query` (JSON params) |
| `delete_file` | Delete file/directory | `path`, `query` (JSON params) |
| `move_file` | Move file/directory | `path`, `query` (JSON params) |

## Quick GET Endpoints

```bash
# Quick directory list
curl "http://localhost:8000/directory/list?path=./modules"

# Find files by pattern
curl "http://localhost:8000/directory/find?pattern=*.py&path=./modules&recursive=true"

# Explore tree
curl "http://localhost:8000/directory/tree?path=./modules&max_depth=2"

# Get file info
curl "http://localhost:8000/directory/info?path=./main.py"

# Search history
curl "http://localhost:8000/directory/history"

# System status
curl "http://localhost:8000/directory/status"

# Save content to file
curl -X POST "http://localhost:8000/directory/save" \
  -H "Content-Type: application/json" \
  -d '{"search_type": "save_to_file", "path": ".", "query": "{\"file_path\": \"output.txt\", \"content\": \"Hello Ray!\"}", "assigned_by": "ray"}'

# Save search results
curl -X POST "http://localhost:8000/directory/save-search-results?search_id=uuid&file_path=results.json&format=markdown"

# Rename file
curl -X POST "http://localhost:8000/directory/rename" \
  -H "Content-Type: application/json" \
  -d '{"search_type": "rename_file", "path": ".", "query": "{\"source_path\": \"old.txt\", \"target_path\": \"new.txt\"}", "assigned_by": "ray"}'

# Move file
curl -X POST "http://localhost:8000/directory/move" \
  -H "Content-Type: application/json" \
  -d '{"search_type": "move_file", "path": ".", "query": "{\"source_path\": \"file.txt\", \"target_path\": \"./archive/file.txt\"}", "assigned_by": "ray"}'

# Delete file
curl -X POST "http://localhost:8000/directory/delete" \
  -H "Content-Type: application/json" \
  -d '{"search_type": "delete_file", "path": ".", "query": "{\"target_path\": \"unwanted.txt\"}", "assigned_by": "ray"}'
```

## Common Filters

```json
{
  "search_type": "find_files",
  "path": "./logs",
  "query": "*.log",
  "min_size": 1024,
  "max_size": 1048576,
  "modified_after": "2025-07-27T00:00:00Z",
  "recursive": true,
  "assigned_by": "ray"
}
```

## Response Structure

```json
{
  "search_result": {
    "search_id": "uuid",
    "search_type": "list_directory",
    "total_results": 15,
    "files_found": [...],
    "directories_found": [...],
    "execution_time_ms": 45,
    "success": true
  },
  "current_path": "/current/path",
  "suggested_paths": ["/path1", "/path2"],
  "summary": {
    "total_files": 10,
    "total_directories": 5
  }
}
```

## Error Handling

- **Path not found**: `success: false` with error message
- **Permission denied**: Skips inaccessible items
- **Invalid search type**: HTTP 422 validation error
- **Missing required fields**: HTTP 422 validation error

## Testing

```bash
# Run directory tests
python tests/run_directory_tests.py

# Run Ray's exploration example
python examples/directory-search/ray_project_exploration.py
```

---

**Ray's file system exploration made simple.** 🔍