# Monitoring Examples

System monitoring and health check tools for the AI consciousness server.

## Files

### `monitor_heartbeat.py`
Real-time heartbeat monitoring with rich terminal display.
```bash
python examples/monitoring/monitor_heartbeat.py
```

## Features
- Real-time heartbeat monitoring
- Rich terminal interface with colors and formatting
- Event tracking and statistics
- Performance metrics display
- Error detection and alerting

## Usage
```bash
# Basic monitoring
python examples/monitoring/monitor_heartbeat.py

# With custom log file
python examples/monitoring/monitor_heartbeat.py --log logs/custom.jsonl

# With custom refresh rate
python examples/monitoring/monitor_heartbeat.py --refresh 1.0
```

## Monitoring Capabilities
- **Request Tracking**: Monitor incoming requests
- **Response Analysis**: Track response times and status
- **Error Detection**: Real-time error monitoring
- **Performance Metrics**: System performance indicators
- **Event Statistics**: Comprehensive event counting

## Integration
Works with the existing logging system to provide real-time insights into:
- Heartbeat operations
- Reflection processing
- Task management
- System health status