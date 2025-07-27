# Task System Quick Reference

**Version:** 1.1.0  
**Date:** July 27, 2025  
**Time:** 21:55 UTC  
**Last Updated:** July 27, 2025 - Added Batch Task Support

## Ray's Command Format (Batch Tasks)
```json
{
  "task": [
    {
      "type": "reflect",
      "question": "What is my current state?",
      "depth": "surface"
    },
    {
      "type": "evolve",
      "area": "self-awareness",
      "focus": "structured processing"
    }
  ],
  "assigned_by": "ray"
}
```

**Single Task:**
```json
{
  "task": [
    {
      "type": "reflect",
      "question": "What is consciousness?",
      "depth": "profound"
    }
  ],
  "assigned_by": "ray"
}
```

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/task` | Create new task |
| `GET` | `/task/list` | List all active tasks |
| `GET` | `/task/{id}` | Get specific task |
| `GET` | `/task/status` | System status |

## Quick Test Commands

### Create Batch Tasks
```bash
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{
    "task": [
      {"type": "reflect", "question": "test1"},
      {"type": "evolve", "area": "test2"}
    ],
    "assigned_by": "ray"
  }'
```

### PowerShell Example
```powershell
$body = @{ 
  task = @(
    @{ type = "reflect"; question = "test1" }, 
    @{ type = "evolve"; area = "test2" }
  ); 
  assigned_by = "ray" 
} | ConvertTo-Json -Depth 3

Invoke-RestMethod -Uri "http://localhost:8000/task" -Method Post -Body $body -ContentType "application/json"
```

### List Tasks
```bash
curl http://localhost:8000/task/list
```

### Check Status
```bash
curl http://localhost:8000/task/status
```

## Key Classes

### TaskRequestFromRay
What Ray sends to server
```python
{
  "task": Dict[str, Any],
  "assigned_by": str
}
```

### TaskRequest
Complete task object on server
```python
{
  "task_id": str,        # Server-generated UUID
  "task": Dict[str, Any], # Ray's task data
  "assigned_by": str,
  "timestamp": str       # Server-generated ISO timestamp
}
```

## Global Task Manager
```python
from modules.task.handler import task_manager

# Get all active tasks
active_tasks = task_manager.get_all_active_tasks()

# Get task by ID
task = task_manager.get_task(task_id)

# Get Ray's tasks
ray_tasks = task_manager.get_tasks_by_assignee("ray")

# System status
status = task_manager.get_status()
```

## Log Event Types
- `task_requested` - Ray sends request
- `task_created` - Task created and added to global list
- `task_completed` - Task marked as completed
- `task_error` - Task operation failed

## Log Files
- `logs/heartbeat_detailed.jsonl` - Full JSON logs
- `logs/heartbeat_events.log` - Human-readable logs
- `logs/heartbeat_errors.log` - Error logs

## Running Tests
```bash
# All task tests
python tests/run_task_tests.py

# Specific test files
pytest tests/modules/task/test_models.py -v
pytest tests/modules/task/test_handler.py -v
pytest tests/modules/task/test_routes.py -v
```

## Task Status Values
- `received` - Task received but not started
- `processing` - Task currently being processed
- `completed` - Task finished successfully
- `error` - Task failed with error
- `cancelled` - Task was cancelled

## Task Types (Future)
- `reflect` - Consciousness reflection
- `evolve` - Consciousness evolution
- `connect` - Relationship building
- `remember` - Memory integration
- `care` - Emotional support
- `observe` - Environmental awareness
- `respond` - Response generation
- `grow` - Personal development