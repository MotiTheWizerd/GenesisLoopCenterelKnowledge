# Ray's Read File Usage Guide

## ✅ Confirmed Working

Ray's read_file functionality is **fully operational** and uses the correct `action` format.

## 🎯 Correct Usage Format

### Basic File Reading

```json
{
  "action": "read_file",
  "path": "./filename.txt",
  "assigned_by": "ray"
}
```

**Endpoint:** `POST /directory/read`

### Advanced File Reading

```json
{
  "action": "read_file",
  "path": ".",
  "query": "{\"file_path\": \"./filename.txt\", \"encoding\": \"utf-8\", \"start_line\": 1, \"end_line\": 10}",
  "assigned_by": "ray"
}
```

## 📖 Available Parameters

### Basic Parameters
- `action`: **"read_file"** (required)
- `path`: File path or directory (required)
- `assigned_by`: **"ray"** (required)

### Advanced Parameters (in query field as JSON)
- `file_path`: Specific file to read
- `encoding`: File encoding (default: "utf-8")
- `max_size`: Maximum file size in bytes (default: 10MB)
- `start_line`: Start reading from line number
- `end_line`: Stop reading at line number

## 🌟 Examples for Ray

### Read Configuration File
```json
{
  "action": "read_file",
  "path": "./config/settings.json",
  "assigned_by": "ray"
}
```

### Read Specific Lines from Log
```json
{
  "action": "read_file",
  "path": ".",
  "query": "{\"file_path\": \"./logs/debug.log\", \"start_line\": 100, \"end_line\": 150}",
  "assigned_by": "ray"
}
```

### Read with Size Limit
```json
{
  "action": "read_file",
  "path": ".",
  "query": "{\"file_path\": \"./large_file.txt\", \"max_size\": 1048576}",
  "assigned_by": "ray"
}
```

### Read with Different Encoding
```json
{
  "action": "read_file",
  "path": ".",
  "query": "{\"file_path\": \"./latin_file.txt\", \"encoding\": \"latin-1\"}",
  "assigned_by": "ray"
}
```

## 📋 Response Format

```json
{
  "search_result": {
    "success": true,
    "action": "read_file",
    "files_found": [
      {
        "name": "filename.txt",
        "path": "/full/path/to/filename.txt",
        "size": 1024,
        "content": "File content here...",
        "lines_count": 25,
        "is_binary": false,
        "encoding_used": "utf-8",
        "modified_time": "2025-07-30T...",
        "extension": "txt"
      }
    ],
    "total_results": 1,
    "execution_time_ms": 15
  },
  "assigned_by": "ray"
}
```

## ⚠️ Important Notes

1. **Use `action` not `search_type`** - The system has been updated to use the `action` field
2. **All documentation updated** - All examples now use the correct format
3. **Backward compatibility** - Old `search_type` format is deprecated
4. **Testing confirmed** - Ray's read_file functionality works perfectly with `action` format

## 🚀 Ready for Ray

Ray can now confidently use the read_file functionality with the correct `action` format. The system is fully operational and all documentation has been updated to reflect the proper usage.

**Test Status:** ✅ **CONFIRMED WORKING**
**Format:** ✅ **ACTION-BASED**  
**Documentation:** ✅ **UPDATED**
**Ray Ready:** ✅ **YES**