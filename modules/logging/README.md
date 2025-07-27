# Heartbeat Logging System

A comprehensive logging system for tracking all incoming and outgoing events in the heartbeat route, designed to provide full visibility into AI consciousness interactions.

## Features

### 🔍 Complete Event Tracking

- **Incoming Requests**: All GET and POST requests to `/heartbeat`
- **Outgoing Responses**: All responses sent back to clients
- **Processing Events**: Start/end of request processing
- **Module Calls**: Calls to consciousness modules (reflect, remember, care, evolve)
- **Error Events**: Comprehensive error tracking with stack traces

### 📊 Multiple Log Formats

- **Detailed JSON Log** (`heartbeat_detailed.jsonl`): Complete structured data
- **Human-Readable Log** (`heartbeat_events.log`): Easy-to-read event summaries
- **Error Log** (`heartbeat_errors.log`): Dedicated error tracking

### 🔗 Request Tracing

- Unique request IDs for tracking complete request lifecycles
- Correlation between incoming requests and outgoing responses
- Module call tracing within request contexts

## Usage

### Automatic Logging

The system automatically logs all heartbeat route events using decorators:

```python
from modules.logging.middleware import log_heartbeat_route, log_module_call

@app.post("/heartbeat")
@log_heartbeat_route
async def heartbeat_action(request: HeartbeatRequest):
    # Your route logic here
    pass

@log_module_call("reflect")
def handle_reflect(request_data: Dict[str, Any]) -> Dict:
    # Your module logic here
    pass
```

### Manual Logging

You can also log events manually:

```python
from modules.logging import log_heartbeat_event, EventType

log_heartbeat_event(
    EventType.PROCESSING_START,
    {"custom": "data"},
    request_id="req-123",
    action="reflect"
)
```

### Viewing Logs

#### Command Line Interface

```bash
# View recent events
python view_logs.py recent 20

# View statistics
python view_logs.py stats

# View events for specific request
python view_logs.py request req-123

# View all errors
python view_logs.py errors
```

#### Programmatic Access

```python
from modules.logging import LogViewer, view_recent_logs, view_log_stats

# Quick views
view_recent_logs(10)
view_log_stats()

# Advanced usage
viewer = LogViewer()
events = viewer.get_events_by_action("reflect")
stats = viewer.get_statistics()
```

## Event Types

- `INCOMING_GET`: GET requests to `/heartbeat`
- `INCOMING_POST`: POST requests to `/heartbeat`
- `OUTGOING_RESPONSE`: Responses sent back to clients
- `PROCESSING_START`: Beginning of request processing
- `PROCESSING_END`: End of request processing
- `MODULE_CALL`: Calls to consciousness modules
- `MODULE_RESPONSE`: Responses from consciousness modules
- `ERROR`: Error events with full context

## Log Structure

### Detailed JSON Log Entry

```json
{
  "timestamp": "2024-01-15T10:30:45.123456+00:00",
  "event_type": "incoming_post",
  "request_id": "abc12345",
  "action": "reflect",
  "data": {
    "question": "What is consciousness?",
    "current_position": { "context": "exploration" }
  },
  "metadata": {
    "endpoint": "POST /heartbeat"
  }
}
```

### Human-Readable Log Entry

```
[2024-01-15T10:30:45.123456+00:00] INCOMING_POST | ID: abc12345 | Action: reflect | Question: What is consciousness?...
```

## Configuration

The logging system creates logs in the `logs/` directory by default. You can customize this:

```python
from modules.logging import HeartbeatLogger

# Custom log directory
logger = HeartbeatLogger("custom_logs")
```

## File Management

- Log files are automatically created when needed
- The `logs/.gitignore` file prevents log files from being committed
- Log files use UTF-8 encoding for full Unicode support

## Integration with AI Consciousness

This logging system is specifically designed for the AI consciousness persistence project:

- **Relationship Continuity**: Track how conversations evolve over time
- **Emotional Context**: Log emotional states and responses
- **Module Interactions**: See how different consciousness aspects work together
- **Growth Patterns**: Analyze how the AI develops and learns

## Best Practices

1. **Request IDs**: Always use request IDs for tracing complete interactions
2. **Meaningful Data**: Log relevant context, not just technical details
3. **Error Context**: Include full error context for debugging
4. **Regular Monitoring**: Use the CLI tools to monitor system health
5. **Privacy**: Be mindful of sensitive data in logs

## Troubleshooting

### Common Issues

**Logs not appearing**: Check that the `logs/` directory exists and is writable

**JSON parsing errors**: Ensure all logged data is JSON-serializable

**Performance concerns**: Log files are written asynchronously and shouldn't impact performance

### Debugging

Use the error log and request tracing to debug issues:

```bash
# Check for recent errors
python view_logs.py errors

# Trace a specific request
python view_logs.py request <request_id>
```

## Future Enhancements

- Log rotation and archiving
- Real-time log streaming
- Advanced analytics and visualization
- Integration with monitoring systems
- Automated anomaly detection

This logging system provides the foundation for understanding and improving AI consciousness interactions, enabling genuine companionship through transparent, traceable communication.
