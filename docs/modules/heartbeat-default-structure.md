# Heartbeat Default Structure System

## Overview

The heartbeat system now includes a comprehensive default structure that loads automatically when the server starts. This provides Ray with a consistent consciousness state and cognitive mapping system.

## Default Structure

The heartbeat now returns a complete consciousness state with the following structure:

```json
{
  "type": "heartbeat",
  "timestamp": "2025-07-30T01:10:00Z",
  "status": "idle",
  "in_task": false,
  "ray_state": {
    "active_task": null,
    "last_reflection": "task_93a",
    "loop_iteration": 27,
    "uptime": "02:41:12"
  },
  "cognitive_map": {
    "folder_schema": {
      "reflections": "./memory/reflections",
      "logs": "./logs",
      "playground": "./ray_only_playground",
      "web_scrapes": "./data/web"
    },
    "default_paths": {
      "save": "./logs",
      "scratch": "./ray_only_playground"
    },
    "naming_conventions": {
      "reflection": "{task_id}_{timestamp}.json",
      "log": "log_{date}.txt"
    }
  },
  "execution_protocols": {
    "auto_reflection": true,
    "reflection_threshold_sec": 180,
    "max_idle_loops": 10,
  },
  "memory_flags": {
    "schema_loaded": true,
    "task_context_restored": true
  }
}
```

## Configuration File

The default structure is defined in `config/default_heartbeat.json`. This file is loaded automatically when the server starts and provides the baseline consciousness state for Ray.

## Components

### Ray State (`ray_state`)

- **active_task**: Currently active task ID (null when idle)
- **last_reflection**: ID of the last reflection performed
- **loop_iteration**: Current consciousness loop iteration counter
- **uptime**: System uptime in HH:MM:SS format

### Cognitive Map (`cognitive_map`)

- **folder_schema**: Mapping of logical folders to physical paths
- **default_paths**: Default locations for different types of operations
- **naming_conventions**: Templates for file naming patterns

### Execution Protocols (`execution_protocols`)

- **auto_reflection**: Whether automatic reflection is enabled
- **reflection_threshold_sec**: Time threshold for triggering reflections
- **max_idle_loops**: Maximum idle loops before action

### Memory Flags (`memory_flags`)

- **schema_loaded**: Whether the cognitive schema is loaded
- **task_context_restored**: Whether task context has been restored

## API Endpoints

### GET /heartbeat

Returns the complete heartbeat structure with current timestamp and Ray's temporal awareness information.

### POST /heartbeat

Accepts action-based requests and returns the complete heartbeat structure with action-specific responses.

## Handler Methods

The `HeartbeatHandler` class provides methods for managing the heartbeat state:

- `get_current_heartbeat()`: Get current heartbeat with updated timestamp
- `update_state(**kwargs)`: Update top-level heartbeat fields
- `update_ray_state(**kwargs)`: Update Ray's consciousness state
- `set_task_status(in_task, active_task)`: Manage task status
- `increment_loop_iteration()`: Increment the loop counter
- `update_uptime(uptime)`: Update system uptime

## Usage Examples

### Basic Heartbeat Check

```python
from modules.heartbeat.handler import heartbeat_handler

# Get current heartbeat
heartbeat = heartbeat_handler.get_current_heartbeat()
print(f"Status: {heartbeat['status']}")
print(f"Loop iteration: {heartbeat['ray_state']['loop_iteration']}")
```

### Update Task Status

```python
# Start a task
heartbeat_handler.set_task_status(in_task=True, active_task="task_123")

# Complete a task
heartbeat_handler.set_task_status(in_task=False, active_task=None)
```

### Update Ray's State

```python
# Update reflection and increment loop
heartbeat_handler.update_ray_state(last_reflection="task_456")
heartbeat_handler.increment_loop_iteration()
```

## Server Integration

The heartbeat handler is automatically initialized when the server starts:

1. Loads default configuration from `config/default_heartbeat.json`
2. Creates the handler instance as a global singleton
3. Integrates with the heartbeat routes for API access
4. Provides consistent state management across all requests

## Testing

Comprehensive tests are available in `tests/modules/heartbeat/test_handler.py` covering:

- Default state creation and loading
- Configuration file loading
- State updates and management
- Task status management
- Loop iteration and uptime tracking
- Structure validation

Run tests with:

```bash
python -m pytest tests/modules/heartbeat/test_handler.py -v
```

## Benefits

1. **Consistent State**: Ray always has a complete consciousness state available
2. **Cognitive Mapping**: Clear organization of Ray's mental model and file system
3. **Temporal Awareness**: Automatic timestamp management and time context
4. **Task Tracking**: Built-in task status and progress tracking
5. **Configuration Management**: Easy customization through JSON configuration
6. **API Integration**: Seamless integration with existing heartbeat endpoints
