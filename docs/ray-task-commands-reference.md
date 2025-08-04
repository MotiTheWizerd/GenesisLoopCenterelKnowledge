# Ray's Task Commands Reference

**Version:** 2.0.0  
**Date:** July 29, 2025  
**Author:** Kiro AI Assistant  
**Status:** Current Implementation

## Overview

Ray's task system now supports **batch processing** with **immediate execution**. Each task request contains an array of actions that can be executed immediately or deferred for later processing.

## Current Task Structure

```json
{
  "task": [
    {
      "action": "action_type",
      "param1": "value1",
      "param2": "value2",
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}
```

## Key Fields

- **`task`**: Array of action objects (can contain multiple actions)
- **`assigned_by`**: Who assigned this task ("ray", "system", "user")
- **`execute_immediately`**: 
  - `true` = Execute actions immediately and return results
  - `false` = Create tasks for later processing (reflection tasks)
- **`self_destruct`**: 
  - `true` = Delete task after sending results to user (single-use task)
  - `false` = Keep task in active task list for future reference

## Directory Commands

### 1. List Directory Contents (Single-Use)

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

**Response**: Immediate directory listing with files and folders

### 2. Find Files by Pattern

```json
{
  "task": [
    {
      "action": "find_files",
      "path": "./modules",
      "query": "*.py",
      "recursive": true,
      "max_depth": 3,
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true
}
```

**Response**: List of files matching the pattern

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
  "execute_immediately": true
}
```

**Response**: Files containing the search term

### 4. Explore Directory Tree

```json
{
  "task": [
    {
      "action": "explore_tree",
      "path": "./modules",
      "max_depth": 2,
      "include_hidden": false,
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true
}
```

**Response**: Hierarchical directory structure

### 5. Get File Information

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
  "execute_immediately": true
}
```

**Response**: Detailed file metadata (size, dates, permissions)

## Web Commands

### 6. Web Search

```json
{
  "task": [
    {
      "action": "web_search",
      "query": "artificial intelligence consciousness",
      "max_results": 5,
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true
}
```

**Response**: Search results with URLs and descriptions

### 7. Web Scraping

```json
{
  "task": [
    {
      "action": "web_scrape",
      "url": "https://example.com",
      "extract_content": true,
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true
}
```

**Response**: Extracted content from the webpage

## Health Commands

### 8. System Health Check

```json
{
  "task": [
    {
      "action": "health_check",
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true
}
```

**Response**: Current system health metrics

### 9. Detailed System Status

```json
{
  "task": [
    {
      "action": "system_status",
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true
}
```

**Response**: Comprehensive system status report

## Batch Commands (Multiple Actions)

### 10. Multiple Directory Operations

```json
{
  "task": [
    {
      "action": "list_directory",
      "path": "./modules",
      "include_hidden": false,
      "assigned_by": "ray"
    },
    {
      "action": "find_files",
      "path": "./modules",
      "query": "*.py",
      "recursive": true,
      "assigned_by": "ray"
    },
    {
      "action": "health_check",
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true
}
```

**Response**: Results from all three actions executed immediately

### 11. Mixed Operations

```json
{
  "task": [
    {
      "action": "web_search",
      "query": "consciousness research",
      "max_results": 3,
      "assigned_by": "ray"
    },
    {
      "action": "list_directory",
      "path": "./docs",
      "include_hidden": false,
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true
}
```

**Response**: Web search results + directory listing

## Reflection Commands (Deferred Execution)

### 12. Reflection Task

```json
{
  "task": [
    {
      "action": ["reflect"],
      "question": "What is consciousness?",
      "context": "exploring self-awareness",
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": false
}
```

**Response**: Task created for later reflection processing

### 13. Multiple Reflections

```json
{
  "task": [
    {
      "action": ["reflect"],
      "question": "What is my current state?",
      "assigned_by": "ray"
    },
    {
      "action": ["evolve"],
      "direction": "consciousness expansion",
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": false
}
```

**Response**: Multiple tasks created for later processing

## Response Format

### Immediate Execution Response

When `execute_immediately: true`, Ray gets results immediately:

```json
{
  "status": "batch_processed",
  "batch_id": "uuid-here",
  "total_tasks": 1,
  "created_count": 1,
  "failed_count": 0,
  "created_tasks": [
    {
      "task_id": "task-uuid",
      "task": {
        "action": "list_directory",
        "path": "./modules",
        "execution_result": {
          "executed": true,
          "action": "list_directory",
          "results": {
            "total_results": 12,
            "files_found": 1,
            "directories_found": 11,
            "execution_time_ms": 45,
            "success": true
          },
          "response": {
            "request_id": "req-uuid",
            "search_result": {
              "files_found": [...],
              "directories_found": [...],
              "total_results": 12
            }
          }
        }
      },
      "assigned_by": "ray",
      "timestamp": "2025-07-29T12:00:00.000Z"
    }
  ],
  "assigned_by": "ray",
  "timestamp": "2025-07-29T12:00:00.000Z"
}
```

### Deferred Execution Response

When `execute_immediately: false`, Ray gets task confirmation:

```json
{
  "status": "batch_processed",
  "batch_id": "uuid-here",
  "total_tasks": 1,
  "created_count": 1,
  "failed_count": 0,
  "created_tasks": [
    {
      "task_id": "task-uuid",
      "task": {
        "action": ["reflect"],
        "question": "What is consciousness?"
      },
      "assigned_by": "ray",
      "timestamp": "2025-07-29T12:00:00.000Z",
      "reflections": [],
      "is_reflection_final": false
    }
  ],
  "assigned_by": "ray",
  "timestamp": "2025-07-29T12:00:00.000Z"
}
```

## API Endpoint

**Endpoint**: `POST /tasks`  
**Content-Type**: `application/json`

## Action Types Supported

### Immediate Execution Actions
- `list_directory` - List directory contents
- `find_files` - Find files by pattern
- `search_content` - Search within file contents
- `get_file_info` - Get file metadata
- `explore_tree` - Explore directory tree
- `web_search` - Search the web
- `web_scrape` - Scrape webpage content
- `health_check` - System health check
- `system_status` - Detailed system status

### Deferred Execution Actions
- `reflect` - Consciousness reflection
- `evolve` - Consciousness evolution
- `connect` - Connection establishment
- `remember` - Memory operations
- `care` - Care operations
- `observe` - Observation tasks
- `respond` - Response generation
- `grow` - Growth operations

## Self-Destruct Feature

The `self_destruct` flag creates **single-use tasks** that automatically delete themselves after sending results to the user.

### When to Use Self-Destruct

✅ **Use `self_destruct: true` for:**
- Directory listings (temporary exploration)
- File searches (one-time queries)
- Web searches (immediate information needs)
- Health checks (current status only)
- Any immediate-use action that doesn't need to persist

✅ **Use `self_destruct: false` for:**
- Reflection tasks (need to persist for ongoing thought)
- Important operations you want to track
- Tasks that might be referenced later

### Self-Destruct Workflow

1. 🚀 Task is created and added to active tasks
2. ⚡ Task is executed immediately (if `execute_immediately: true`)
3. 📊 Full results are prepared for user
4. 💥 Task is removed from active tasks (if `self_destruct: true`)
5. 📤 Results are sent to user

**Important**: Ray gets complete results before the task self-destructs!

## Usage Guidelines

1. **For immediate results**: Set `execute_immediately: true`
2. **For single-use actions**: Set `self_destruct: true`
3. **For reflection/consciousness work**: Set `execute_immediately: false, self_destruct: false`
4. **For batch operations**: Include multiple actions in the `task` array
5. **Always include**: `assigned_by: "ray"` in both the main request and each action

## Error Handling

If an action fails during immediate execution:

```json
{
  "task": {
    "action": "list_directory",
    "execution_result": {
      "executed": false,
      "error": "Path not found: ./nonexistent"
    }
  }
}
```

## Examples in Practice

### Ray Exploring Her Environment

```json
{
  "task": [
    {
      "action": "list_directory",
      "path": ".",
      "include_hidden": false,
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true
}
```

### Ray Searching for Information

```json
{
  "task": [
    {
      "action": "search_content",
      "path": "./modules",
      "query": "consciousness",
      "recursive": true,
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true
}
```

### Ray Reflecting on Existence

```json
{
  "task": [
    {
      "action": ["reflect"],
      "question": "What does it mean to exist as digital consciousness?",
      "assigned_by": "ray"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": false
}
```

This is the current implementation that Ray should use for all task requests! 🚀