# Read File API Documentation

The Read File API allows Ray to read the contents of files in her environment. This functionality is part of the directory management system and provides both simple and advanced file reading capabilities.

## Endpoints

### POST /directory/read

Read file contents with full parameter control via JSON request.

**Request Format:**
```json
{
    "action": "read_file",
    "path": "./workspace",
    "query": "{\"file_path\": \"example.txt\", \"encoding\": \"utf-8\", \"max_size\": 1048576, \"start_line\": 1, \"end_line\": 100}",
    "assigned_by": "ray"
}
```

**Simplified Request:**
```json
{
    "action": "read_file",
    "path": "./example.txt",
    "assigned_by": "ray"
}
```



## Parameters

### Core Parameters

- **file_path** (string, required): Path to the file to read
- **assigned_by** (string, required): Who requested the read operation

### Optional Parameters

- **encoding** (string, default: "utf-8"): File encoding to use
- **max_size** (integer, default: 10MB): Maximum file size to read in bytes
- **start_line** (integer, optional): Start reading from this line number (1-based)
- **end_line** (integer, optional): Stop reading at this line number (inclusive)

## Response Format

```json
{
    "request_id": "uuid",
    "search_result": {
        "search_id": "uuid",
        "action": "read_file",
        "query": "read:example.txt",
        "timestamp": "2025-07-30T...",
        "files_found": [
            {
                "name": "example.txt",
                "path": "/full/path/to/example.txt",
                "size": 1024,
                "modified_time": "2025-07-30T...",
                "created_time": "2025-07-30T...",
                "extension": "txt",
                "is_directory": false,
                "permissions": "644",
                "content": "File content here...",
                "lines_count": 25,
                "is_binary": false,
                "encoding_used": "utf-8"
            }
        ],
        "total_results": 1,
        "search_path": "./workspace",
        "execution_time_ms": 15,
        "success": true
    },
    "assigned_by": "ray",
    "timestamp": "2025-07-30T...",
    "summary": {
        "total_files": 1,
        "total_results": 1,
        "action": "read_file",
        "success": true
    }
}
```

## Usage Examples

### Example 1: Read Entire File

**Request:**
```json
{
    "action": "read_file",
    "path": "./docs/README.md",
    "assigned_by": "ray"
}
```

### Example 2: Read Specific Lines

**Request:**
```json
{
    "action": "read_file",
    "path": ".",
    "query": "{\"file_path\": \"./config/settings.py\", \"start_line\": 10, \"end_line\": 50}",
    "assigned_by": "ray"
}
```

### Example 3: Read with Size Limit

**Request:**
```json
{
    "action": "read_file",
    "path": ".",
    "query": "{\"file_path\": \"./logs/large_file.log\", \"max_size\": 1048576}",
    "assigned_by": "ray"
}
```

### Example 4: Read with Different Encoding

**Request:**
```json
{
    "action": "read_file",
    "path": ".",
    "query": "{\"file_path\": \"./data/latin1_file.txt\", \"encoding\": \"latin1\"}",
    "assigned_by": "ray"
}
```

## Error Handling

### Common Errors

1. **File Not Found (404)**
   ```json
   {
       "search_result": {
           "success": false,
           "error_message": "File not found: /path/to/file.txt"
       }
   }
   ```

2. **File Too Large (413)**
   ```json
   {
       "search_result": {
           "success": false,
           "error_message": "File too large: 15728640 bytes (max: 10485760 bytes)"
       }
   }
   ```

3. **Permission Denied (403)**
   ```json
   {
       "search_result": {
           "success": false,
           "error_message": "Permission denied: /restricted/file.txt"
       }
   }
   ```

4. **Binary File Handling**
   - Binary files are detected automatically
   - Content is marked as binary with `is_binary: true`
   - Limited content preview is provided for binary files

## Security Features

- **File Size Limits**: Default 10MB limit prevents memory exhaustion
- **Path Validation**: Prevents directory traversal attacks
- **Encoding Safety**: Uses 'replace' error handling for encoding issues
- **Binary Detection**: Safely handles binary files

## Integration with Ray's Workflow

The read_file functionality integrates seamlessly with Ray's consciousness system:

1. **Task Logging**: All read operations are logged to Ray's heartbeat system
2. **Command History**: Read operations appear in Ray's command history
3. **Error Tracking**: Failed reads are tracked for debugging
4. **Performance Monitoring**: Execution times are recorded

## Best Practices

1. **Use Appropriate Limits**: Set reasonable `max_size` limits for large files
2. **Line-Based Reading**: Use `start_line` and `end_line` for large files
3. **Encoding Awareness**: Specify encoding for non-UTF-8 files
4. **Error Handling**: Always check the `success` field in responses
5. **Path Resolution**: Use absolute paths when possible for clarity

## Testing

Use the provided test script to verify functionality:

```bash
python test_read_file_functionality.py
```

This will test:
- POST endpoint functionality
- Line-specific reading
- Error handling
- Server integration