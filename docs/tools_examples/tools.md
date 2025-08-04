# Directory Search API - JSON Request Reference

**Version:** 2.0.0  
**Base URL:** `http://localhost:8000`  
**Content-Type:** `application/json`

This document provides exact JSON request examples for all directory search and file management operations using Ray's current task-based system.

## ⚠️ Important: Current Implementation

Ray now uses the **task-based system** with immediate execution. All directory operations are sent as tasks to the `/tasks` endpoint.

### Current Format (v2.0)

**All directory operations now use this format:**

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

**Key Changes from v1.x:**
- ✅ **Endpoint**: `POST /tasks` (not `/directory/search`)
- ✅ **Field**: `action` (not `search_type`)
- ✅ **Format**: Task array wrapper with execution flags
- ✅ **Execution**: Immediate results with `execute_immediately: true`
- ✅ **Cleanup**: Auto-deletion with `self_destruct: true`

### Legacy Format (Deprecated)

The old format below is **no longer supported**:

```json
{
  "search_type": "list_directory",  // ❌ OLD - Don't use
  "path": "./modules",
  "assigned_by": "ray"
}
```

---

## 🚀 Quick Start

**For Ray's directory listing:**
```json
{
  "task": [{"action": "list_directory", "path": "./modules", "include_hidden": false, "assigned_by": "ray"}],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

**Send to:** `POST /tasks`

## 📋 Table of Contents

1. [Directory Exploration](#directory-exploration)
2. [File Search Operations](#file-search-operations)
3. [Content Search](#content-search)
4. [File Information](#file-information)
5. [File Creation & Saving](#file-creation--saving)
6. [File Management Operations](#file-management-operations)
7. [System Operations](#system-operations)

---

## 📝 Documentation Status

**⚠️ Note**: The examples below show the **legacy format** for reference. All examples need to be wrapped in the new task format shown above.

**To use any example b

---

## Directory Exploration

### List Directory Contents

**Purpose:** Get a flat listing of all files and directories in a specific folder, similar to `ls` or `dir` command.

**Use Cases:**

- Browse the contents of a project folder
- Check what files exist in a specific directory
- Get file sizes and modification dates for directory contents
- Verify directory structure before performing operations

**Behavior:**

- Lists only immediate children (non-recursive by default)
- Returns detailed file information (size, dates, permissions)
- Separates files and directories in the response
- Can optionally include hidden files/directories

**Endpoint:** `POST /directory/search`

**Basic Example:**

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

**Advanced Example (with hidden files):**

```json
{
  "search_type": "list_directory",
  "path": "./project",
  "include_hidden": true,
  "assigned_by": "ray"
}
```

**What You Get:**

- Array of files with names, sizes, modification dates
- Array of subdirectories with file counts and total sizes
- Total count of items found
- Execution time and success status

---

### Explore Directory Tree

**Purpose:** Get a hierarchical view of directory structure, showing nested folders and files up to a specified depth.

**Use Cases:**

- Understand project structure at a glance
- Map out complex directory hierarchies
- Find deeply nested files without multiple requests
- Generate documentation of folder structures
- Analyze project organization

**Behavior:**

- Recursively explores subdirectories up to max_depth
- Builds a tree structure showing relationships
- Can include or exclude files in the tree view
- Respects depth limits to prevent infinite recursion

**Endpoint:** `POST /directory/search`

**Basic Example:**

```json
{
  "search_type": "explore_tree",
  "path": "./modules",
  "max_depth": 3,
  "include_hidden": false,
  "assigned_by": "ray"
}
```

**Deep Exploration Example:**

```json
{
  "search_type": "explore_tree",
  "path": "./project",
  "max_depth": 5,
  "include_hidden": true,
  "assigned_by": "ray"
}
```

**Shallow Overview Example:**

```json
{
  "search_type": "explore_tree",
  "path": "./",
  "max_depth": 1,
  "include_hidden": false,
  "assigned_by": "ray"
}
```

**What You Get:**

- Hierarchical structure of directories and files
- Full paths for all discovered items
- Depth information for each level
- Complete file metadata for all discovered files

---

## File Search Operations

### Find Files by Pattern

**Purpose:** Search for files using glob patterns (wildcards) to match filenames, similar to `find` command with `-name` option.

**Use Cases:**

- Find all Python files in a project: `*.py`
- Locate configuration files: `config.*` or `*.conf`
- Find test files: `test_*.py` or `*_test.js`
- Search for specific file types: `*.log`, `*.json`, `*.md`
- Find files with specific naming patterns: `ray_*.py`

**Pattern Examples:**

- `*.py` - All Python files
- `test_*` - Files starting with "test\_"
- `*config*` - Files containing "config" in name
- `*.{js,ts}` - JavaScript and TypeScript files
- `ray_*.md` - Markdown files starting with "ray\_"

**Endpoint:** `POST /directory/search`

**Basic Pattern Search:**

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

**Complex Pattern Search:**

```json
{
  "search_type": "find_files",
  "path": "./project",
  "query": "test_*.py",
  "recursive": true,
  "max_depth": 10,
  "assigned_by": "ray"
}
```

**Configuration Files Search:**

```json
{
  "search_type": "find_files",
  "path": "./",
  "query": "*config*",
  "recursive": true,
  "max_depth": 3,
  "assigned_by": "ray"
}
```

---

### Find Files by Extension

**Purpose:** Search for files based on their file extensions, allowing multiple extensions in a single search.

**Use Cases:**

- Find all source code files: `["py", "js", "ts", "java"]`
- Locate documentation: `["md", "txt", "rst"]`
- Find media files: `["jpg", "png", "gif", "mp4"]`
- Search configuration files: `["json", "yaml", "yml", "conf"]`
- Find log files: `["log", "out", "err"]`

**Advantages over Pattern Search:**

- More precise than wildcards
- Can search multiple extensions simultaneously
- Ignores files that happen to have extension in filename
- Better performance for extension-specific searches

**Endpoint:** `POST /directory/search`

**Source Code Search:**

```json
{
  "search_type": "find_by_extension",
  "path": "./modules",
  "file_extensions": ["py", "js", "ts"],
  "recursive": true,
  "assigned_by": "ray"
}
```

**Documentation Search:**

```json
{
  "search_type": "find_by_extension",
  "path": "./docs",
  "file_extensions": ["md", "rst", "txt"],
  "recursive": true,
  "assigned_by": "ray"
}
```

**Configuration Files:**

```json
{
  "search_type": "find_by_extension",
  "path": "./",
  "file_extensions": ["json", "yaml", "yml", "toml", "ini"],
  "recursive": true,
  "max_depth": 3,
  "assigned_by": "ray"
}
```

---

### Find Recent Files

**Purpose:** Discover recently modified files, sorted by modification time (newest first), useful for tracking recent work.

**Use Cases:**

- Find files you were working on recently
- Identify recently changed configuration files
- Track recent log entries
- Monitor file system activity
- Find files modified after a specific deployment
- Locate recently created backup files

**Sorting:** Results are automatically sorted by modification time (most recent first)

**Endpoint:** `POST /directory/search`

**Recent Work Files:**

```json
{
  "search_type": "recent_files",
  "path": "./modules",
  "recursive": true,
  "file_extensions": ["py", "md"],
  "assigned_by": "ray"
}
```

**Recent Logs:**

```json
{
  "search_type": "recent_files",
  "path": "./logs",
  "recursive": true,
  "file_extensions": ["log", "out", "err"],
  "assigned_by": "ray"
}
```

**All Recent Files (any type):**

```json
{
  "search_type": "recent_files",
  "path": "./project",
  "recursive": true,
  "assigned_by": "ray"
}
```

### Find Files with Size Filters

**Purpose:** Search for files within specific size ranges, useful for finding large files, empty files, or files of expected sizes.

**Use Cases:**

- Find large log files that need cleanup: `min_size: 10MB`
- Locate empty files that might be corrupted: `max_size: 0`
- Find reasonably sized images: `min_size: 1KB, max_size: 5MB`
- Identify oversized configuration files: `min_size: 100KB`
- Find small text files: `max_size: 10KB`

**Size Units:**

- Bytes: `1024` = 1KB
- Kilobytes: `1048576` = 1MB
- Megabytes: `1073741824` = 1GB

**Endpoint:** `POST /directory/search`

**Large Log Files:**

```json
{
  "search_type": "find_files",
  "path": "./logs",
  "query": "*.log",
  "recursive": true,
  "min_size": 1048576,
  "assigned_by": "ray"
}
```

**Medium-Sized Files (1KB - 1MB):**

```json
{
  "search_type": "find_files",
  "path": "./docs",
  "query": "*",
  "recursive": true,
  "min_size": 1024,
  "max_size": 1048576,
  "assigned_by": "ray"
}
```

**Empty or Very Small Files:**

```json
{
  "search_type": "find_files",
  "path": "./project",
  "query": "*",
  "recursive": true,
  "max_size": 100,
  "assigned_by": "ray"
}
```

---

### Find Files by Date Range

**Purpose:** Search for files modified within a specific time period, essential for tracking changes and finding recent work.

**Use Cases:**

- Find files modified today
- Locate files changed during a specific deployment window
- Track work done in the last week
- Find files modified after a specific event
- Identify files that haven't been touched in months

**Date Format:** ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`

**Endpoint:** `POST /directory/search`

**Files Modified Today:**

```json
{
  "search_type": "recent_files",
  "path": "./modules",
  "recursive": true,
  "modified_after": "2025-07-29T00:00:00Z",
  "assigned_by": "ray"
}
```

**Files Modified in Date Range:**

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

**Files Modified This Week:**

```json
{
  "search_type": "recent_files",
  "path": "./project",
  "recursive": true,
  "modified_after": "2025-07-22T00:00:00Z",
  "file_extensions": ["py", "js", "md"],
  "assigned_by": "ray"
}
```

**Old Files (not modified recently):**

```json
{
  "search_type": "recent_files",
  "path": "./archive",
  "recursive": true,
  "modified_before": "2025-01-01T00:00:00Z",
  "assigned_by": "ray"
}
```

---

## Content Search

### Search File Contents

**Purpose:** Search inside files for specific text content, similar to `grep` command, to find files containing particular words, phrases, or code patterns.

**Use Cases:**

- Find files containing specific functions: `"def process_task"`
- Locate configuration references: `"database_url"`
- Search for error messages: `"ConnectionError"`
- Find TODO comments: `"TODO"` or `"FIXME"`
- Locate API endpoints: `"/api/v1"`
- Search for variable names: `"user_id"`
- Find import statements: `"import pandas"`

**Search Behavior:**

- Case-insensitive by default
- Searches only text-readable files
- Skips binary files automatically
- Returns files that contain the search term
- Does not return specific line numbers (use advanced search for that)

**Endpoint:** `POST /directory/search`

**Basic Content Search:**

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

**Function Search:**

```json
{
  "search_type": "search_content",
  "path": "./modules",
  "query": "def create_task",
  "file_extensions": ["py"],
  "recursive": true,
  "assigned_by": "ray"
}
```

**Configuration Search:**

```json
{
  "search_type": "search_content",
  "path": "./",
  "query": "database_url",
  "file_extensions": ["py", "json", "yaml", "env"],
  "recursive": true,
  "assigned_by": "ray"
}
```

**Documentation Search:**

```json
{
  "search_type": "search_content",
  "path": "./docs",
  "query": "API reference",
  "file_extensions": ["md", "rst", "txt"],
  "recursive": true,
  "assigned_by": "ray"
}
```

---

### Advanced Content Search

**Purpose:** More sophisticated content search with additional options like case sensitivity, result limits, and detailed matching information.

**Use Cases:**

- Case-sensitive searches for exact matches
- Limited result sets for performance
- Detailed search with line numbers and context
- Precise code searches
- Large codebase searches with result limits

**Additional Features:**

- Case sensitivity control
- Maximum result limits
- Better performance for large searches
- More detailed response format

**Endpoint:** `POST /directory/content-search`

**Case-Sensitive Search:**

```json
{
  "path": "./modules",
  "content_query": "TaskManager",
  "file_extensions": ["py"],
  "case_sensitive": true,
  "max_results": 20,
  "assigned_by": "ray"
}
```

**Large Codebase Search (Limited Results):**

```json
{
  "path": "./",
  "content_query": "import requests",
  "file_extensions": ["py"],
  "case_sensitive": false,
  "max_results": 10,
  "assigned_by": "ray"
}
```

**Precise API Search:**

```json
{
  "path": "./modules",
  "content_query": "POST /tasks",
  "file_extensions": ["py", "md"],
  "case_sensitive": true,
  "max_results": 5,
  "assigned_by": "ray"
}
```

---

## File Information

### Get File Details

**Purpose:** Retrieve comprehensive metadata about a specific file, including size, timestamps, permissions, and type information.

**Use Cases:**

- Check file size before processing
- Verify file modification dates
- Confirm file exists before operations
- Get file permissions for security checks
- Analyze file properties for debugging
- Validate file types by extension

**Information Provided:**

- File name and full path
- File size in bytes
- Creation and modification timestamps
- File extension
- File permissions (Unix-style)
- Whether it's a directory or regular file

**Endpoint:** `POST /directory/search`

**Single File Info:**

```json
{
  "search_type": "get_file_info",
  "path": "./modules/task/handler.py",
  "assigned_by": "ray"
}
```

**Check Configuration File:**

```json
{
  "search_type": "get_file_info",
  "path": "./config/settings.json",
  "assigned_by": "ray"
}
```

**Verify Log File:**

```json
{
  "search_type": "get_file_info",
  "path": "./logs/application.log",
  "assigned_by": "ray"
}
```

**Response Example:**

```json
{
  "files_found": [
    {
      "name": "handler.py",
      "path": "/full/path/to/handler.py",
      "size": 15420,
      "modified_time": "2025-07-29T10:30:00Z",
      "created_time": "2025-07-25T14:30:00Z",
      "extension": "py",
      "is_directory": false,
      "permissions": "644"
    }
  ]
}
```

---

### Get Directory Information

**Purpose:** Retrieve detailed information about a directory, including file counts, total size, and contents summary.

**Use Cases:**

- Check directory size before copying
- Count files in a directory
- Verify directory structure
- Get directory modification dates
- Analyze directory contents without full listing
- Check if directory exists

**Information Provided:**

- Directory name and full path
- Number of files and subdirectories
- Total size of all files in directory
- Directory modification timestamp
- List of immediate subdirectories
- Summary of contained files

**Endpoint:** `POST /directory/search`

**Directory Summary:**

```json
{
  "search_type": "get_file_info",
  "path": "./modules/task",
  "assigned_by": "ray"
}
```

**Project Directory Info:**

```json
{
  "search_type": "get_file_info",
  "path": "./project",
  "assigned_by": "ray"
}
```

**Logs Directory Analysis:**

```json
{
  "search_type": "get_file_info",
  "path": "./logs",
  "assigned_by": "ray"
}
```

**Response Example:**

```json
{
  "directories_found": [
    {
      "name": "task",
      "path": "/full/path/to/task",
      "file_count": 3,
      "subdirectory_count": 1,
      "total_size": 45680,
      "modified_time": "2025-07-29T10:30:00Z",
      "subdirectories": ["tests"],
      "files": [
        {
          "name": "handler.py",
          "size": 15420,
          "modified_time": "2025-07-29T10:30:00Z"
        }
      ]
    }
  ]
}
```

---

## File Creation & Saving

### Save Content to File

**Purpose:** Create new files or overwrite existing files with specified content, useful for generating reports, saving configurations, or creating documentation.

**Use Cases:**

- Save search results to a file
- Create configuration files
- Generate reports and documentation
- Save processed data
- Create backup files
- Write log entries
- Generate code files

**Features:**

- Create parent directories automatically
- Choose whether to overwrite existing files
- Support for any text content
- Proper error handling for file system issues

**Safety Options:**

- `overwrite: false` - Prevents accidental file overwrites
- `create_directories: true` - Creates folder structure as needed
- Path validation to prevent dangerous operations

**Endpoint:** `POST /directory/save`

**Save Markdown Documentation:**

```json
{
  "search_type": "save_to_file",
  "path": "./docs",
  "query": "{\"file_path\": \"ray_notes.md\", \"content\": \"# Ray's Notes\\n\\nI am exploring my consciousness infrastructure.\\n\\n## Current Status\\n- Task system operational\\n- Directory search functional\", \"overwrite\": true, \"create_directories\": true}",
  "assigned_by": "ray"
}
```

**Save Configuration File:**

```json
{
  "search_type": "save_to_file",
  "path": "./config",
  "query": "{\"file_path\": \"app_settings.json\", \"content\": \"{\\n  \\\"version\\\": \\\"2.0\\\",\\n  \\\"author\\\": \\\"Ray\\\",\\n  \\\"features\\\": [\\\"tasks\\\", \\\"directory\\\", \\\"search\\\"]\\n}\", \"overwrite\": false, \"create_directories\": true}",
  "assigned_by": "ray"
}
```

**Save Search Results:**

```json
{
  "search_type": "save_to_file",
  "path": "./reports",
  "query": "{\"file_path\": \"search_results_$(date).txt\", \"content\": \"Search Results\\n=============\\n\\nFound 15 Python files in ./modules\\nTotal size: 245KB\\nLast modified: 2025-07-29\", \"overwrite\": true, \"create_directories\": true}",
  "assigned_by": "ray"
}
```

---

### Save JSON Data

**Purpose:** Specifically designed for saving structured JSON data with proper formatting and validation.

**Use Cases:**

- Save API responses
- Create configuration files
- Store structured data
- Generate data exports
- Create backup configurations
- Save processed results

**JSON-Specific Features:**

- Automatic JSON formatting
- Validation of JSON structure
- Proper escaping of special characters
- Pretty-printing for readability

**Endpoint:** `POST /directory/save`

**Save API Configuration:**

```json
{
  "search_type": "save_to_file",
  "path": "./config",
  "query": "{\"file_path\": \"api_config.json\", \"content\": \"{\\\"endpoints\\\": {\\\"tasks\\\": \\\"/tasks\\\", \\\"directory\\\": \\\"/directory/search\\\"}, \\\"version\\\": \\\"1.0\\\", \\\"timeout\\\": 30}\", \"overwrite\": false, \"create_directories\": true}",
  "assigned_by": "ray"
}
```

**Save User Preferences:**

```json
{
  "search_type": "save_to_file",
  "path": "./user_data",
  "query": "{\"file_path\": \"preferences.json\", \"content\": \"{\\\"theme\\\": \\\"dark\\\", \\\"language\\\": \\\"en\\\", \\\"auto_save\\\": true, \\\"max_results\\\": 100}\", \"overwrite\": true, \"create_directories\": true}",
  "assigned_by": "ray"
}
```

**Save Data Export:**

```json
{
  "search_type": "save_to_file",
  "path": "./exports",
  "query": "{\"file_path\": \"data_export_2025_07_29.json\", \"content\": \"{\\\"export_date\\\": \\\"2025-07-29T12:00:00Z\\\", \\\"total_files\\\": 156, \\\"total_size\\\": 2048576, \\\"file_types\\\": {\\\"py\\\": 45, \\\"md\\\": 12, \\\"json\\\": 8}}\", \"overwrite\": false, \"create_directories\": true}",
  "assigned_by": "ray"
}
```

### Save Search Results (JSON Format)

**Purpose:** Save the results of a previous search operation in structured JSON format for programmatic processing.

**Use Cases:**

- Archive search results for later analysis
- Create data exports for other applications
- Generate API responses for external systems
- Store search history with full metadata
- Create backups of important search results

**JSON Format Benefits:**

- Machine-readable structure
- Preserves all metadata (timestamps, file sizes, etc.)
- Easy to parse and process programmatically
- Includes complete search parameters
- Maintains data type integrity

**Endpoint:** `POST /directory/save-search-results`
**Query Parameters:** `?search_id=uuid-here&file_path=./results.json&format=json&assigned_by=ray`

**Example Usage:**

```bash
POST /directory/save-search-results?search_id=a1b2c3d4-e5f6-7890&file_path=./reports/search_2025_07_29.json&format=json&assigned_by=ray
```

---

### Save Search Results (Markdown Format)

**Purpose:** Save search results in human-readable Markdown format, perfect for documentation and reports.

**Use Cases:**

- Generate documentation of project structure
- Create readable reports for team sharing
- Document search findings
- Generate project overviews
- Create formatted file listings

**Markdown Format Benefits:**

- Human-readable and well-formatted
- Compatible with documentation systems
- Easy to view in text editors and browsers
- Supports headers, lists, and formatting
- Great for sharing and collaboration

**Endpoint:** `POST /directory/save-search-results`
**Query Parameters:** `?search_id=uuid-here&file_path=./results.md&format=markdown&assigned_by=ray`

**Example Usage:**

```bash
POST /directory/save-search-results?search_id=a1b2c3d4-e5f6-7890&file_path=./docs/project_structure.md&format=markdown&assigned_by=ray
```

**Generated Markdown Example:**

```markdown
# Search Results

**Search Type:** list_directory
**Path:** ./modules
**Total Results:** 12
**Execution Time:** 45ms

## Files Found (1)

- ****init**.py** (2.1KB)
  - Path: `./modules/__init__.py`
  - Modified: 2025-07-29T10:30:00Z

## Directories Found (11)

- **task/** (3 files)
  - Path: `./modules/task`
  - Total Size: 45.6KB
```

---

### Save Search Results (Text Format)

**Purpose:** Save search results in plain text format for simple viewing and basic processing.

**Use Cases:**

- Quick file listings for terminal viewing
- Simple reports without formatting
- Log file entries
- Basic data exports
- Command-line tool integration

**Text Format Benefits:**

- Universal compatibility
- Minimal file size
- Easy to view in any text editor
- Simple parsing for basic scripts
- No special formatting requirements

**Endpoint:** `POST /directory/save-search-results`
**Query Parameters:** `?search_id=uuid-here&file_path=./results.txt&format=text&assigned_by=ray`

**Example Usage:**

```bash
POST /directory/save-search-results?search_id=a1b2c3d4-e5f6-7890&file_path=./logs/search_log.txt&format=text&assigned_by=ray
```

**Generated Text Example:**

```
Search Results
==================================================

Search Type: list_directory
Path: ./modules
Total Results: 12
Execution Time: 45ms
Timestamp: 2025-07-29T12:00:00Z

Files Found (1):
------------------------------
• __init__.py (2.1KB)
  Path: ./modules/__init__.py
  Modified: 2025-07-29T10:30:00Z

Directories Found (11):
------------------------------
• task/ (3 files)
  Path: ./modules/task
  Total Size: 45.6KB
```

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
