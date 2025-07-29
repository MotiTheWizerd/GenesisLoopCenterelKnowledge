# Task System Troubleshooting Guide

**Version:** 1.0.0  
**Date:** July 27, 2025  
**Time:** 21:15 UTC  
**Scope:** Production Support and Debugging

## Common Issues and Solutions

### 1. Server Won't Start - Import Error

**Error:**
```
ImportError: cannot import name 'TaskHandler' from 'modules.task.handler'
```

**Solution:**
Check `modules/task/__init__.py` imports. Should be:
```python
from .handler import TaskManager, task_manager
```
Not `TaskHandler` (which doesn't exist).

### 2. Task Creation Fails - Validation Error

**Error:**
```
422 Unprocessable Entity
```

**Cause:** Missing required fields in request

**Solution:**
Ensure request includes both required fields:
```json
{
  "task": {},           // Required - can be empty dict
  "assigned_by": "ray"  // Required - string value
}
```

### 3. Task Not Found in List

**Symptoms:**
- Task created successfully (200 response)
- Task not appearing in `/task/list`

**Debugging Steps:**
1. Check task creation response for task_id
2. Query specific task: `GET /task/{task_id}`
3. Check server logs for errors
4. Verify global task manager state

**Common Causes:**
- Task completed immediately (moved to completed list)
- Server restart (tasks are in-memory only)
- Multiple server instances

### 4. Logging Not Working

**Symptoms:**
- No task events in log files
- Missing `task_requested` or `task_created` events

**Debugging Steps:**
1. Check if log directory exists: `logs/`
2. Verify log files are being created:
   - `logs/heartbeat_detailed.jsonl`
   - `logs/heartbeat_events.log`
3. Check file permissions
4. Look for logging errors in console

**Solution:**
```bash
# Create log directory if missing
mkdir logs

# Check recent log entries
tail -f logs/heartbeat_detailed.jsonl
```

### 5. Memory Issues with Large Task Lists

**Symptoms:**
- Server becoming slow
- High memory usage
- Task operations timing out

**Monitoring:**
```python
# Check task counts
response = requests.get('http://localhost:8000/task/status')
status = response.json()
print(f"Active: {status['task_manager']['active_tasks_count']}")
print(f"Completed: {status['task_manager']['completed_tasks_count']}")
```

**Solutions:**
- Implement task cleanup for completed tasks
- Add task archiving
- Consider database persistence for high-volume scenarios

### 6. Task System Not Responding

**Symptoms:**
- 500 Internal Server Error
- Timeouts on task endpoints
- Server logs showing exceptions

**Debugging Steps:**
1. Check server console for error messages
2. Review error logs: `logs/heartbeat_errors.log`
3. Test basic server health: `GET /heartbeat`
4. Restart server if needed

**Common Fixes:**
```bash
# Restart server
python main.py

# Check if task manager initialized
# Should see: "🎯 Task Manager initialized - Global task lists created"
```

## Diagnostic Commands

### Check Server Health
```bash
# Basic server health
curl http://localhost:8000/heartbeat

# Task system health
curl http://localhost:8000/task/status
```

### Test Task Creation
```bash
# Minimal valid request
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"task": {}, "assigned_by": "test"}'
```

### Monitor Logs in Real-Time
```bash
# Watch detailed logs
tail -f logs/heartbeat_detailed.jsonl

# Watch human-readable logs
tail -f logs/heartbeat_events.log

# Watch error logs
tail -f logs/heartbeat_errors.log
```

### Check Task Manager State
```python
# Python script to check internal state
import requests

# Get all active tasks
response = requests.get('http://localhost:8000/task/list')
if response.status_code == 200:
    data = response.json()
    print(f"Active tasks: {data['active_tasks_count']}")
    for task in data['active_tasks']:
        print(f"  - {task['task_id'][:8]}: {task['assigned_by']}")
else:
    print(f"Error: {response.status_code}")
```

## Performance Monitoring

### Task Creation Rate
```bash
# Count task creation events in last hour
grep "task_created" logs/heartbeat_detailed.jsonl | \
  grep "$(date -u +%Y-%m-%dT%H)" | wc -l
```

### Memory Usage Tracking
```python
# Monitor task list sizes over time
import requests
import time

while True:
    response = requests.get('http://localhost:8000/task/status')
    if response.status_code == 200:
        data = response.json()
        tm = data['task_manager']
        print(f"Active: {tm['active_tasks_count']}, "
              f"Completed: {tm['completed_tasks_count']}, "
              f"Total: {tm['total_tasks_processed']}")
    time.sleep(10)
```

### Error Rate Monitoring
```bash
# Count errors in last 100 log entries
tail -100 logs/heartbeat_detailed.jsonl | \
  grep -c "task_error"
```

## Log Analysis

### Find Specific Task Events
```bash
# Find all events for a specific task ID
grep "task-id-here" logs/heartbeat_detailed.jsonl

# Find all Ray's tasks
grep '"assigned_by": "ray"' logs/heartbeat_detailed.jsonl
```

### Task Processing Time Analysis
```bash
# Extract task creation timestamps
grep "task_created" logs/heartbeat_detailed.jsonl | \
  jq -r '.timestamp'
```

### Error Pattern Analysis
```bash
# Find common error patterns
grep "task_error" logs/heartbeat_detailed.jsonl | \
  jq -r '.data.error' | sort | uniq -c
```

## Testing and Validation

### Run Full Test Suite
```bash
# All task tests
python tests/run_task_tests.py

# Specific test categories
pytest tests/modules/task/test_models.py -v     # Model validation
pytest tests/modules/task/test_handler.py -v   # Task manager logic
pytest tests/modules/task/test_routes.py -v    # API endpoints
```

### Manual Integration Test
```python
import requests
import json

# 1. Create task
create_response = requests.post('http://localhost:8000/task', json={
    'task': {'type': 'test', 'data': 'integration_test'},
    'assigned_by': 'test_user'
})

if create_response.status_code == 200:
    task_id = create_response.json()['task_id']
    print(f"✅ Task created: {task_id}")
    
    # 2. Verify in list
    list_response = requests.get('http://localhost:8000/task/list')
    tasks = list_response.json()['active_tasks']
    found = any(t['task_id'] == task_id for t in tasks)
    print(f"✅ Task in list: {found}")
    
    # 3. Get specific task
    get_response = requests.get(f'http://localhost:8000/task/{task_id}')
    print(f"✅ Task retrieval: {get_response.status_code == 200}")
    
else:
    print(f"❌ Task creation failed: {create_response.status_code}")
```

## Recovery Procedures

### Server Restart Recovery
Tasks are stored in memory, so server restart will clear all tasks:

1. **Before restart:** Export active tasks if needed
2. **After restart:** Verify task manager initialization
3. **Re-create critical tasks:** If needed for ongoing operations

### Log File Rotation
If log files become too large:

```bash
# Backup current logs
mv logs/heartbeat_detailed.jsonl logs/heartbeat_detailed.jsonl.backup
mv logs/heartbeat_events.log logs/heartbeat_events.log.backup

# Restart server to create new log files
# Or use logrotate for automatic rotation
```

### Database Migration (Future)
When moving from in-memory to database storage:

1. Export current task state
2. Set up database schema
3. Import existing tasks
4. Update configuration
5. Test thoroughly before production

## Contact and Support

For issues not covered in this guide:

1. **Check server logs** for detailed error messages
2. **Run test suite** to verify system integrity
3. **Review recent changes** that might have affected the system
4. **Create minimal reproduction case** for debugging

Remember: The task system is designed to be robust and self-healing. Most issues can be resolved by understanding the data flow and checking the comprehensive logging system.