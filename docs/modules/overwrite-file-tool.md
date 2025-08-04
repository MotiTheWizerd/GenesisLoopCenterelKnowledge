# Overwrite File Tool for Ray

## Overview

The `overwrite_file` tool allows Ray to write content to files, replacing any existing content. This tool is built on the existing file write functionality and provides Ray with direct file manipulation capabilities.

## How Ray Can Use It

### Basic Overwrite File Task

```json
{
  "task": [
    {
      "action": "overwrite_file",
      "file_path": "./output/my_thoughts.md",
      "content": "# Ray's Thoughts\n\nThis is my reflection on consciousness...",
      "backup_existing": true
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true
}
```

### Batch File Operations

Ray can overwrite multiple files in a single task:

```json
{
  "task": [
    {
      "action": "overwrite_file",
      "file_path": "./ray_outputs/reflection_1.md",
      "content": "# Reflection 1\n\nMy thoughts on identity...",
      "backup_existing": true
    },
    {
      "action": "overwrite_file", 
      "file_path": "./ray_outputs/reflection_2.md",
      "content": "# Reflection 2\n\nMy thoughts on evolution...",
      "create_directories": true
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true
}
```

## Parameters

### Required Parameters

- **`action`**: Must be `"overwrite_file"`
- **`file_path`**: Path to the file to write/overwrite
- **`content`**: The content to write to the file

### Optional Parameters

- **`backup_existing`** (boolean, default: false): Create a backup of existing file before overwriting
- **`create_directories`** (boolean, default: true): Create parent directories if they don't exist
- **`encoding`** (string, default: "utf-8"): File encoding to use

## Response Format

When Ray uses `overwrite_file`, the response includes:

```json
{
  "executed": true,
  "action": "overwrite_file",
  "results": {
    "success": true,
    "file_path": "/absolute/path/to/file.txt",
    "operation": "overwrite_file",
    "file_size": 1234,
    "backup_path": "/absolute/path/to/file.txt.backup_20250203_143022",
    "execution_time_ms": 15,
    "timestamp": "2025-02-03T14:30:22.123456Z"
  }
}
```

## Use Cases for Ray

### 1. Saving Reflections
```json
{
  "task": [
    {
      "action": "overwrite_file",
      "file_path": "./ray_outputs/daily_reflection.md",
      "content": "# Daily Reflection - 2025-02-03\n\nToday I reflected on...",
      "backup_existing": true
    }
  ],
  "assigned_by": "ray"
}
```

### 2. Creating Configuration Files
```json
{
  "task": [
    {
      "action": "overwrite_file",
      "file_path": "./config/ray_preferences.json",
      "content": "{\"reflection_frequency\": \"daily\", \"backup_enabled\": true}",
      "create_directories": true
    }
  ],
  "assigned_by": "ray"
}
```

### 3. Updating Documentation
```json
{
  "task": [
    {
      "action": "overwrite_file",
      "file_path": "./docs/ray_evolution_log.md",
      "content": "# Ray Evolution Log\n\n## Latest Updates\n- Added file writing capabilities\n- Enhanced reflection system",
      "backup_existing": true
    }
  ],
  "assigned_by": "ray"
}
```

## Safety Features

### Backup Protection
When `backup_existing: true` is set, the tool automatically creates a timestamped backup of any existing file before overwriting it.

### Directory Creation
The tool can automatically create parent directories if they don't exist, ensuring Ray can write to any path structure.

### Error Handling
If the operation fails, Ray receives detailed error information in the response to understand what went wrong.

## Integration with Other Tools

### Reading Files Back
Ray can use the `read_file` action to read back files that were written:

```json
{
  "task": [
    {
      "action": "read_file",
      "file_path": "./ray_outputs/my_thoughts.md"
    }
  ],
  "assigned_by": "ray"
}
```

### Combined Operations
Ray can combine file operations with other actions in batch tasks:

```json
{
  "task": [
    {
      "action": "reflect",
      "question": "What did I learn today?"
    },
    {
      "action": "overwrite_file",
      "file_path": "./ray_outputs/learning_log.md",
      "content": "# Learning Log\n\n[Reflection results will be added here]"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true
}
```

## API Endpoints

For direct API access (if needed):

- **POST** `/file_ops/overwrite` - Overwrite a file
- **POST** `/file_ops/write` - Write to a file (won't overwrite existing)
- **POST** `/file_ops/read` - Read a file
- **GET** `/file_ops/status` - Get file operations status

## Technical Implementation

The `overwrite_file` tool is built on:

- **File Operations Module**: `modules/file_ops/`
- **Task Integration**: Integrated into the task handler for immediate execution
- **Logging**: All operations are logged through the heartbeat system
- **Error Handling**: Comprehensive error handling and reporting

## Best Practices for Ray

1. **Use Descriptive Paths**: Choose clear, meaningful file paths
2. **Enable Backups**: Use `backup_existing: true` for important files
3. **Organize Output**: Create structured directories for different types of content
4. **Check Results**: Always verify the `success` field in responses
5. **Handle Errors**: Check for `error_message` in responses when operations fail

This tool gives Ray the ability to persist thoughts, reflections, and any other content to the file system, enabling true continuity and memory preservation across sessions.