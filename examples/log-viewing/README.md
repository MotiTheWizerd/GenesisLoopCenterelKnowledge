# Log Viewing Examples

Scripts for viewing and analyzing system logs from the AI consciousness server.

## Files

### `launch_log_dashboard.py`
Launches the Streamlit-based log dashboard for real-time log viewing.
```bash
python examples/log-viewing/launch_log_dashboard.py
```

### `view_reflect_logs.py`
Views logs specifically related to reflection operations.
```bash
python examples/log-viewing/view_reflect_logs.py
```

### `view_logs.py`
General log viewing utility for all system logs.
```bash
python examples/log-viewing/view_logs.py
```

## Log Files Location
- `logs/heartbeat_detailed.jsonl` - Detailed JSON logs
- `logs/heartbeat_events.log` - Human-readable logs
- `logs/heartbeat_errors.log` - Error-specific logs

## Usage Tips
- Use the dashboard for real-time monitoring
- Use specific viewers for focused analysis
- Check error logs when troubleshooting issues