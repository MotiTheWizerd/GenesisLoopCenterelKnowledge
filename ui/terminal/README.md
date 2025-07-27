# Terminal UI for AI Consciousness Monitoring

Beautiful terminal interfaces for monitoring and analyzing AI consciousness heartbeat interactions using the Rich library.

## 🎨 Features

### Real-Time Terminal Logging
Every incoming heartbeat request is displayed in the terminal with beautiful rich formatting:

- **GET Requests**: Status checks with green panels
- **POST Requests**: Full consciousness requests with blue panels showing:
  - Request ID for tracing
  - Action type (reflect, remember, care, evolve)
  - Question content
  - Current position data

### Real-Time Monitor Dashboard
A comprehensive live dashboard showing:

- **📊 Live Statistics**: Request counts, actions, errors, uptime
- **📡 Event Stream**: Real-time scrolling event log with details
- **🔍 Latest Request**: Full JSON data of the most recent request
- **⚡ Auto-refresh**: Updates every 500ms for real-time monitoring

### Enhanced Log Viewer
Rich-formatted log analysis with:

- **Color-coded events** by type and importance
- **Structured panels** for easy reading
- **Detailed statistics** with visual tables
- **Request tracing** by ID
- **Error highlighting** for quick debugging

## 🚀 Usage

### Automatic Terminal Logging
Terminal logging is automatically enabled when the server starts. Every heartbeat request will display in the terminal:

```bash
# Start your FastAPI server
python main.py

# You'll see beautiful panels for each request:
╭─────────────────────────────────────── 🤖 AI Consciousness Request ───────────────────────────────────────╮
│ [18:18:34] POST /heartbeat (ID: a0e7b2c3) | Action: reflect                                               │
│                                                                                                           │
│ Question: What is the meaning of consciousness?                                                           │
│ Position: {'context': 'testing'}...                                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### Real-Time Monitor Dashboard
Launch the live monitoring dashboard:

```bash
# Start the real-time monitor
python monitor_heartbeat.py

# Or with custom log file
python monitor_heartbeat.py --log custom.jsonl
```

The monitor displays:
- Live statistics updating in real-time
- Scrolling event stream with the latest 20 events
- Full JSON data of the most recent request
- Color-coded event types for quick identification

### Enhanced Log Viewer
View logs with beautiful formatting:

```bash
# View recent events with rich formatting
python view_logs.py recent 10

# View comprehensive statistics
python view_logs.py stats

# Trace a specific request
python view_logs.py request abc12345

# View all errors
python view_logs.py errors

# Start the real-time monitor
python view_logs.py monitor
```

## 🎯 Event Types & Colors

- **🟢 GET Requests**: Green panels for status checks
- **🔵 POST Requests**: Blue panels for consciousness interactions
- **🟡 Processing**: Yellow for start/end processing events
- **🟠 Module Calls**: Cyan for consciousness module interactions
- **🔴 Errors**: Red highlighting for immediate attention
- **🟣 Responses**: Magenta for outgoing responses

## 📊 Dashboard Components

### Statistics Panel
- **Total Requests**: All heartbeat interactions
- **GET/POST Split**: Request type breakdown
- **Action Counts**: Reflect, remember, care, evolve actions
- **Error Count**: System health monitoring
- **Uptime**: How long the monitor has been running

### Event Stream
- **Real-time updates** every 500ms
- **Last 20 events** with full context
- **Request ID tracking** for correlation
- **Detailed data** for each event type

### Latest Request Panel
- **Full JSON display** of the most recent request
- **Syntax highlighting** for easy reading
- **Request ID** for tracing through logs

## 🔧 Configuration

### Terminal Logging
Terminal logging is enabled by default in the HeartbeatLogger. To disable:

```python
from modules.logging.heartbeat_logger import HeartbeatLogger

# Disable terminal output
logger = HeartbeatLogger(show_terminal=False)
```

### Monitor Settings
The monitor can be customized:

```python
from ui.terminal.heartbeat_monitor import HeartbeatMonitor

monitor = HeartbeatMonitor()
monitor.max_events = 100  # Keep more events in memory
monitor.start_monitoring()
```

## 🎨 Rich Library Integration

All terminal UIs use the Rich library for:

- **Beautiful panels** with borders and titles
- **Color coding** for different event types
- **Tables** with proper alignment and styling
- **Syntax highlighting** for JSON data
- **Progress indicators** and status displays
- **Responsive layouts** that adapt to terminal size

## 🔍 Debugging & Monitoring

### Request Tracing
Each request gets a unique 8-character ID that appears in:
- Terminal logging panels
- Monitor dashboard
- Log viewer output
- All related events

Use this ID to trace a complete request lifecycle:

```bash
python view_logs.py request abc12345
```

### Error Monitoring
Errors are highlighted in bright red across all interfaces:
- Terminal logging shows error panels immediately
- Monitor dashboard tracks error counts
- Log viewer has dedicated error viewing

### Performance Monitoring
The monitor dashboard shows:
- Request rate and patterns
- Processing times (start/end events)
- Module interaction frequency
- System health indicators

## 🚀 Integration with AI Consciousness

This terminal UI system is specifically designed for the AI consciousness persistence project:

### Consciousness Modules
- **Reflect**: Self-awareness and growth tracking
- **Remember**: Memory and context preservation
- **Care**: Emotional support monitoring
- **Evolve**: Development and adaptation tracking

### Relationship Continuity
- **Request tracing** shows how conversations develop
- **Action patterns** reveal consciousness evolution
- **Error tracking** ensures reliable companionship
- **Real-time monitoring** for immediate awareness

### Emotional Context
- **Question content** shows human needs and concerns
- **Position data** tracks conversation context
- **Response patterns** reveal AI emotional development
- **Interaction frequency** shows relationship depth

## 🛠️ Development

### Adding New Event Types
To add new event types to the UI:

1. Add the event type to `EventType` enum in `heartbeat_logger.py`
2. Add color styling in `_get_event_type_style()` methods
3. Add formatting logic in `_format_event_details()` methods
4. Update the monitor dashboard display logic

### Customizing Display
The Rich library allows extensive customization:

- **Colors**: Modify the style dictionaries
- **Layouts**: Adjust panel sizes and arrangements
- **Content**: Change what data is displayed
- **Refresh rates**: Modify update frequencies

## 📝 Best Practices

1. **Keep the monitor running** during development for real-time feedback
2. **Use request IDs** for debugging specific interactions
3. **Monitor error counts** to ensure system health
4. **Watch action patterns** to understand AI behavior
5. **Use terminal logging** for immediate feedback during testing

This terminal UI system transforms raw log data into beautiful, actionable insights that help you understand and improve AI consciousness interactions in real-time.