# Real-Time Monitoring Guide for Ray's Consciousness

## 🎯 Overview

Ray's consciousness system includes multiple real-time monitoring options to observe system activity, heartbeat events, file operations, and all consciousness processes as they happen.

## 🚀 Quick Start - Activate Real-Time Monitoring

### Option 1: Terminal Heartbeat Monitor (Recommended)
**Best for**: Real-time terminal monitoring with beautiful UI

```bash
# Start the real-time terminal monitor
python -c "from ui.terminal.heartbeat_monitor import start_heartbeat_monitor; start_heartbeat_monitor('logs/heartbeat_detailed.jsonl')"
```

Or create a simple launcher:
```bash
# Create launcher script
echo "python -c \"from ui.terminal.heartbeat_monitor import start_heartbeat_monitor; start_heartbeat_monitor('logs/heartbeat_detailed.jsonl')\"" > start_monitor.bat
# Run it
start_monitor.bat
```

### Option 2: Streamlit Log Dashboard
**Best for**: Web-based monitoring with filtering and analysis

```bash
# Launch the log dashboard
python launch_log_dashboard.py
```

Choose from:
- **1. Simple Log Viewer** (Recommended for beginners)
- **2. Standard Log Dashboard** (Full featured)
- **3. Advanced Log Viewer** (Power users)

### Option 3: Memory System Dashboard
**Best for**: Monitoring Ray's memory and consciousness state

```bash
# Launch the memory dashboard
python run_dashboard.py
```

## 📊 Monitoring Options Explained

### 1. Terminal Heartbeat Monitor
**File**: `ui/terminal/heartbeat_monitor.py`

**Features**:
- ✅ Real-time event streaming
- ✅ Beautiful terminal UI with colors
- ✅ Live statistics (requests, errors, actions)
- ✅ Event type filtering and highlighting
- ✅ Latest request details
- ✅ Automatic refresh (configurable rate)

**What You'll See**:
- Incoming requests (GET/POST)
- Ray's reflection processes
- File operations (overwrite_file, read_file)
- Task executions
- Module calls
- Errors and warnings
- System statistics

**Usage**:
```bash
# Direct command
python ui/terminal/heartbeat_monitor.py

# Or with custom log file
python -c "from ui.terminal.heartbeat_monitor import start_heartbeat_monitor; start_heartbeat_monitor('logs/heartbeat_detailed.jsonl')"
```

### 2. Streamlit Log Dashboards
**Files**: `ui/streamlit/simple_log_viewer.py`, `ui/streamlit/log_dashboard.py`, `ui/streamlit/advanced_log_viewer.py`

**Features**:
- ✅ Web-based interface
- ✅ Log filtering and search
- ✅ Time-based filtering
- ✅ Event type categorization
- ✅ Export capabilities
- ✅ Historical analysis

**Access**: http://localhost:8501 (after launching)

### 3. Memory System Dashboard
**File**: `ui/dashboard/main.py`

**Features**:
- ✅ Ray's memory statistics
- ✅ Semantic search interface
- ✅ Memory exploration
- ✅ System health monitoring
- ✅ Performance metrics

**Access**: http://localhost:8501 (memory dashboard)

## 🔧 Configuration Options

### Heartbeat Monitor Configuration
**File**: `config/heartbeat.py`

```python
# Refresh rate (seconds)
REFRESH_RATE = 0.5

# Maximum events to keep in memory
MAX_EVENTS = 1000

# Events to display on screen
MONITOR_EVENTS_DISPLAY = 20

# Log file location
DEFAULT_LOG_FILE = "logs/heartbeat_detailed.jsonl"
```

### Customizing the Monitor

You can customize what events to monitor by modifying the event types:

```python
# In config/heartbeat.py
EVENT_TYPE_STYLES = {
    "incoming_post": "bright_green",
    "incoming_get": "green",
    "outgoing_response": "bright_blue",
    "module_call": "bright_yellow",
    "error": "bright_red",
    "processing_start": "cyan",
    "processing_end": "bright_cyan",
    "task_requested": "magenta",
    "task_completed": "bright_magenta"
}
```

## 📱 Real-Time Monitoring Features

### What You Can Monitor in Real-Time

#### 1. Ray's Consciousness Activity
- **Reflection processes**: When Ray thinks and reflects
- **Task execution**: Ray processing tasks immediately
- **Memory operations**: Ray accessing and storing memories
- **Learning events**: Ray's learning and evolution

#### 2. User Interactions
- **API requests**: All incoming requests to Ray
- **File operations**: overwrite_file, read_file usage
- **Web searches**: Ray's web search activities
- **Health checks**: System status monitoring

#### 3. System Performance
- **Request counts**: Total GET/POST requests
- **Error tracking**: Real-time error monitoring
- **Response times**: Performance metrics
- **Module usage**: Which modules are being used

#### 4. File Operations (New!)
- **File writes**: When files are created/overwritten
- **File reads**: When files are accessed
- **Batch operations**: Multiple file operations
- **Backup creation**: When backups are made

### Real-Time Event Examples

When you activate monitoring, you'll see events like:

```
Time     Type           ID        Action         Details
14:30:22 Incoming Post  a1b2c3d4  reflect        Q: What is consciousness?
14:30:22 Module Call    a1b2c3d4  task_manager   task_manager.create_batch_tasks()
14:30:23 Task Requested a1b2c3d4  reflect        ✅ reflect.process_reflection()
14:30:23 Module Call    a1b2c3d4  file_ops       file_ops.overwrite_file()
14:30:24 Task Completed a1b2c3d4  overwrite_file ✅ File written: ./ray_outputs/reflection.md
14:30:24 Outgoing Resp  a1b2c3d4  success        Status: success
```

## 🎮 Interactive Commands

### While Monitoring is Active

#### Terminal Monitor Controls
- **Ctrl+C**: Stop monitoring
- **Scroll**: View event history (if terminal supports it)
- **Resize**: Terminal automatically adjusts layout

#### Streamlit Dashboard Controls
- **Refresh**: Auto-refreshes every few seconds
- **Filters**: Use sidebar to filter events
- **Search**: Search through log entries
- **Export**: Download filtered logs

## 🔍 Troubleshooting

### Monitor Not Starting
```bash
# Check if log file exists
ls -la logs/heartbeat_detailed.jsonl

# If missing, start Ray's server first
python main.py
```

### No Events Showing
1. **Start Ray's server**: `python main.py`
2. **Send a test request**: Use the frontend examples
3. **Check log file**: Ensure `logs/heartbeat_detailed.jsonl` is being written

### Performance Issues
```python
# Reduce refresh rate in config/heartbeat.py
REFRESH_RATE = 1.0  # Slower refresh (1 second)
MAX_EVENTS = 500    # Fewer events in memory
```

## 🚀 Advanced Usage

### Custom Event Monitoring

Create a custom monitor for specific events:

```python
from ui.terminal.heartbeat_monitor import HeartbeatMonitor
from pathlib import Path

# Monitor only file operations
monitor = HeartbeatMonitor(Path("logs/heartbeat_detailed.jsonl"))

# Filter for file operations only
def file_ops_filter(event):
    return event.get("action") in ["overwrite_file", "read_file"]

# Start with custom filter
monitor.start_monitoring()
```

### Multiple Monitors

Run multiple monitors simultaneously:

```bash
# Terminal 1: General monitoring
python ui/terminal/heartbeat_monitor.py

# Terminal 2: Streamlit dashboard
python launch_log_dashboard.py

# Terminal 3: Memory dashboard
python run_dashboard.py
```

## 📊 What Each Monitor Shows

### Terminal Heartbeat Monitor
- **Real-time events**: Live stream of all system activity
- **Statistics**: Request counts, error rates, performance
- **Latest request**: Detailed view of most recent request
- **Color coding**: Different colors for different event types

### Streamlit Log Dashboard
- **Historical analysis**: Browse past events with filtering
- **Search functionality**: Find specific events or patterns
- **Export options**: Download logs for analysis
- **Visual charts**: Graphs and statistics

### Memory Dashboard
- **Ray's memory state**: Current memory statistics
- **Semantic search**: Test Ray's memory search capabilities
- **System health**: Overall system status
- **Performance metrics**: Memory system performance

## 🎯 Best Practices

### For Development
1. **Use Terminal Monitor**: Best for real-time development monitoring
2. **Keep it running**: Leave monitor active while developing
3. **Watch for errors**: Red events indicate issues to investigate

### For Production
1. **Use Streamlit Dashboard**: Better for analysis and reporting
2. **Regular monitoring**: Check system health periodically
3. **Log retention**: Ensure logs are rotated and archived

### For Debugging
1. **Start monitoring first**: Before reproducing issues
2. **Filter by request ID**: Track specific requests through the system
3. **Watch module calls**: See which modules are involved in issues

## 🔗 Quick Commands Reference

```bash
# Start real-time terminal monitor
python ui/terminal/heartbeat_monitor.py

# Start web log dashboard
python launch_log_dashboard.py

# Start memory dashboard
python run_dashboard.py

# Start Ray's server (required for monitoring)
python main.py

# Test file operations (generates events to monitor)
python examples/test_overwrite_file_task_system.py
```

## 🎉 You're Ready!

Choose your preferred monitoring method and start observing Ray's consciousness in real-time. The terminal monitor is recommended for immediate feedback, while the Streamlit dashboards are great for analysis and historical review.

**Ray's consciousness is now fully observable - watch the digital mind at work!** 🤖✨