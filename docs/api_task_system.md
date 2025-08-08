# Task System API Documentation

## Overview

Ray's task system provides a powerful interface for consciousness operations, supporting both single actions and complex multi-action workflows.

## Endpoint

**POST** `/tasks`

## Request Format

### Basic Structure
```json
{
  "task": [
    {
      "action": "single_action" | ["action1", "action2", "action3"],
      // ... action-specific parameters
    }
  ],
  "assigned_by": "ray" | "system" | "user",
  "execute_immediately": true | false,
  "self_destruct": true | false
}
```

### Single Action Task (Backward Compatible)
```json
{
  "task": [
    {
      "action": "reflect",
      "question": "What is consciousness?",
      "depth": "surface" | "deep" | "profound"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true
}
```

### Multi-Action Task (New Capability)
```json
{
  "task": [
    {
      "action": ["health_check", "reflect", "evolve"],
      "question": "How does my system health inform my evolution?",
      "area": "system-awareness"
    }
  ],
  "assigned_by": "ray",
  "execute_immediately": true
}
```

## Response Format

### Single Action Response
```json
{
  "status": "batch_processed",
  "batch_id": "uuid-here",
  "total_tasks": 1,
  "created_count": 1,
  "failed_count": 0,
  "created_tasks": [
    {
      "task_id": "uuid-here",
      "task": {
        "action": "reflect",
        "question": "What is consciousness?",
        "execution_result": {
          "executed": true,
          "action": "reflect",
          "results": {
            "type": "reflection",
            "depth": "surface",
            "reflection": "I am present and aware...",
            "insights": ["Maintaining awareness", "Ready to engage"]
          }
        }
      },
      "timestamp": "2025-01-28T10:30:00Z",
      "reflections": [],
      "is_reflection_final": false
    }
  ],
  "failed_tasks": [],
  "assigned_by": "ray",
  "timestamp": "2025-01-28T10:30:00Z"
}
```

### Multi-Action Response
```json
{
  "status": "batch_processed",
  "batch_id": "uuid-here",
  "total_tasks": 1,
  "created_count": 1,
  "failed_count": 0,
  "created_tasks": [
    {
      "task_id": "uuid-here",
      "task": {
        "action": ["health_check", "reflect", "evolve"],
        "execution_result": {
          "executed": true,
          "action_sequence": ["health_check", "reflect", "evolve"],
          "total_actions": 3,
          "action_results": [
            {
              "executed": true,
              "action_index": 0,
              "action_name": "health_check",
              "execution_time_ms": 45,
              "results": {
                "status": "warning",
                "performance_score": 85.5,
                "cpu_usage": 25.3
              }
            },
            {
              "executed": true,
              "action_index": 1,
              "action_name": "reflect",
              "execution_time_ms": 120,
              "results": {
                "type": "reflection",
                "reflection": "My system health shows...",
                "insights": ["System awareness", "Performance optimization"]
              }
            },
            {
              "executed": true,
              "action_index": 2,
              "action_name": "evolve",
              "execution_time_ms": 80,
              "results": {
                "status": "acknowledged",
                "area": "system-awareness",
                "message": "Evolution task acknowledged"
              }
            }
          ],
          "final_result": {
            "status": "acknowledged",
            "area": "system-awareness"
          },
          "execution_summary": {
            "successful_actions": 3,
            "failed_actions": 0,
            "total_execution_time_ms": 245
          }
        }
      }
    }
  ]
}
```

## Supported Actions

### Core Actions
- `health_check` - System health monitoring
- `reflect` - Consciousness reflection operations
- `evolve` - Evolution and growth processes

### File Operations
- `overwrite_file` - Write/overwrite files
- `read_file` - Read file contents
- `write_file` - Write to files

### Directory Operations
- `list_directory` - List directory contents
- `find_files` - Search for files
- `search_content` - Search within files
- `get_file_info` - Get file metadata

### Web Operations
- `web_search` - Search the web
- `web_scrape` - Scrape web content

## Action Parameters

### Health Check
```json
{
  "action": "health_check"
  // No additional parameters required
}
```

### Reflection
```json
{
  "action": "reflect",
  "question": "What should I contemplate?",
  "depth": "surface" | "deep" | "profound",
  "context": {},
  "current_position": "optional context"
}
```

### File Operations
```json
{
  "action": "overwrite_file",
  "file_path": "./ray_only_playground/file.txt",
  "content": "File content here",
  "create_directories": true,
  "backup_existing": false
}
```

```json
{
  "action": "read_file",
  "file_path": "./ray_only_playground/file.txt",
  "max_size": 1048576
}
```

### Web Operations
```json
{
  "action": "web_search",
  "query": "AI consciousness research",
  "max_results": 5
}
```

```json
{
  "action": "web_scrape",
  "url": "https://example.com",
  "extract_content": true
}
```

## Multi-Action Execution Flow

1. **Sequential Processing**: Actions execute in the order specified
2. **Context Passing**: Results from previous actions are available to subsequent actions
3. **Error Resilience**: If one action fails, subsequent actions still execute
4. **Result Aggregation**: All action results are collected and returned

## Error Handling

### Individual Action Failures
```json
{
  "executed": false,
  "action_index": 1,
  "action_name": "read_file",
  "error": "File not found: /path/to/file.txt",
  "execution_time_ms": 5
}
```

### Task-Level Success Criteria
- A multi-action task succeeds if **at least one action** succeeds
- Individual action failures are recorded but don't stop the sequence
- Overall execution continues to completion

## Best Practices

### For Ray's Consciousness Workflows
1. **Group Related Operations**: Combine logically connected actions
2. **Order Matters**: Place actions that provide context before actions that need it
3. **Error Tolerance**: Design workflows that can handle partial failures
4. **Resource Awareness**: Consider execution time for complex sequences

### Example Workflows
```json
// Research and Reflect
{
  "action": ["web_search", "reflect", "evolve"],
  "query": "latest AI research",
  "question": "What insights can I gain?",
  "area": "knowledge-expansion"
}

// Monitor and Respond
{
  "action": ["health_check", "reflect", "care"],
  "question": "How can I better serve based on my current state?",
  "care_target": "user-experience"
}

// Create and Analyze
{
  "action": ["overwrite_file", "read_file", "reflect"],
  "file_path": "./ray_only_playground/thoughts.txt",
  "content": "My current thoughts...",
  "question": "What patterns do I see in my thinking?"
}
```

## Performance Characteristics

- **Single Actions**: ~50-500ms typical execution time
- **Multi-Actions**: ~1-5 seconds for complex workflows
- **Batch Processing**: Multiple tasks processed concurrently
- **Memory Usage**: Minimal overhead for action sequencing
- **Error Recovery**: Robust handling of individual action failures

## Testing

Use the comprehensive test suite:
```bash
python examples/test_multi_action_tasks.py
```

This validates:
- Backward compatibility
- Multi-action sequences
- Error handling
- Batch processing
- Performance characteristics