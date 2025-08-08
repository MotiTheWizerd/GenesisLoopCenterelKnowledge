#!/usr/bin/env python3
"""
Log viewer utility for filtering and displaying specific log types.
"""

import json
import sys
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

def find_project_root():
    """Find the project root directory by looking for known files."""
    current = Path.cwd()
    
    # Look for project indicators
    indicators = ["pyproject.toml", "main.py", "extract/memory_metadata.json"]
    
    # Check current directory and parents
    for path in [current] + list(current.parents):
        for indicator in indicators:
            if (path / indicator).exists():
                return path
    
    # Fallback: assume current directory
    return current

def resolve_log_path(log_file: str) -> Path:
    """Resolve log file path relative to project root."""
    if Path(log_file).is_absolute():
        return Path(log_file)
    
    # Try relative to current directory first
    if Path(log_file).exists():
        return Path(log_file)
    
    # Try relative to project root
    project_root = find_project_root()
    project_log_path = project_root / log_file
    if project_log_path.exists():
        return project_log_path
    
    # Return original path (will fail later with clear error)
    return Path(log_file)

def load_logs(log_file: str = "logs/heartbeat_detailed.jsonl") -> List[Dict]:
    """Load logs from JSONL file with robust error handling for problematic encodings."""
    logs = []
    
    # Resolve the correct path
    log_path = resolve_log_path(log_file)
    
    print(f"Attempting to load log file: {log_path.absolute()}")
    
    # First, check if file exists and is accessible
    if not log_path.exists():
        print(f"Error: Log file not found at {log_path.absolute()}")
        print(f"Current working directory: {Path.cwd()}")
        print(f"Project root detected as: {find_project_root()}")
        return []
    
    # Try reading with different approaches
    try:
        # Approach 1: Try reading with error handler for problematic bytes
        try:
            with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        logs.append(json.loads(line))
            print(f"Successfully read {len(logs)} log entries using utf-8 with error replacement")
            return logs
        except (UnicodeDecodeError, json.JSONDecodeError):
            logs = []  # Reset for next attempt
        
        # Approach 2: Try reading in binary and decoding with error handling
        with open(log_path, 'rb') as f:
            content = f.read()
            
            # Try different encodings with error handling
            encodings = [
                ('utf-8', 'strict'),
                ('utf-8-sig', 'strict'),
                ('latin-1', 'strict'),
                ('cp1252', 'strict'),
                ('utf-8', 'replace'),  # Replace problematic bytes
                ('utf-8-sig', 'replace'),
                ('latin-1', 'replace'),
                ('cp1252', 'replace')
            ]
            
            for encoding, errors in encodings:
                try:
                    decoded = content.decode(encoding, errors=errors)
                    logs = []
                    for line in decoded.splitlines():
                        line = line.strip()
                        if line:
                            logs.append(json.loads(line))
                    print(f"Successfully read {len(logs)} log entries using {encoding} encoding with {errors} error handling")
                    return logs
                except (UnicodeDecodeError, json.JSONDecodeError) as e:
                    print(f"Failed with {encoding} encoding: {str(e)[:200]}...")
                    continue
        
        # If we get here, all attempts failed
        print(f"Failed to read {log_path.absolute()} with any encoding method")
        return []
        
    except Exception as e:
        print(f"Unexpected error reading {log_path.absolute()}: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def filter_reflect_logs(logs: List[Dict]) -> List[Dict]:
    """Filter logs to show only reflect-related events."""
    reflect_logs = []
    for log in logs:
        # Check if it's a reflect-related log
        if (log.get('action') == 'reflect' or 
            'reflect' in str(log.get('data', {})) or
            log.get('data', {}).get('function') in ['reflect_action', 'deep_reflection'] or
            log.get('data', {}).get('module') == 'reflect'):
            reflect_logs.append(log)
    return reflect_logs

def format_log_entry(log: Dict) -> str:
    """Format a log entry for display."""
    timestamp = log.get('timestamp', '')
    event_type = log.get('event_type', '')
    request_id = log.get('request_id', '')[:8]  # Short ID
    action = log.get('action', 'N/A')
    
    # Extract relevant data based on event type
    data = log.get('data', {})
    
    if event_type == 'module_call':
        question = data.get('input_data', {}).get('question', 'N/A')
        depth = data.get('input_data', {}).get('depth', 'surface')
        current_pos = data.get('input_data', {}).get('current_position')
        pos_preview = (current_pos[:50] + '...') if current_pos else 'None'
        return f"[{timestamp}] 📥 REFLECT CALL ({request_id}) - Q: {question} | Depth: {depth} | Pos: {pos_preview}"
    
    elif event_type == 'module_response':
        output = data.get('output_data', {})
        reflection = output.get('reflection', '')
        reflection_preview = (reflection[:80] + '...') if reflection else 'N/A'
        insights = len(output.get('insights', []))
        return f"[{timestamp}] 📤 REFLECT RESPONSE ({request_id}) - {reflection_preview} | Insights: {insights}"
    
    elif event_type == 'processing_start':
        function = data.get('function', 'unknown')
        return f"[{timestamp}] 🔄 PROCESSING START ({request_id}) - {function}"
    
    elif event_type == 'processing_end':
        function = data.get('function', 'unknown')
        success = data.get('success', False)
        status = '✅' if success else '❌'
        return f"[{timestamp}] {status} PROCESSING END ({request_id}) - {function}"
    
    elif event_type == 'outgoing_response':
        response_type = data.get('type', 'unknown')
        depth = data.get('depth', 'N/A')
        question = data.get('question', 'N/A')
        return f"[{timestamp}] 🚀 FINAL RESPONSE ({request_id}) - Type: {response_type} | Depth: {depth} | Q: {question}"
    
    else:
        return f"[{timestamp}] {event_type.upper()} ({request_id}) - {action}"

def view_reflect_logs(limit: Optional[int] = None):
    """View reflect logs with formatting."""
    logs = load_logs()
    reflect_logs = filter_reflect_logs(logs)
    
    if not reflect_logs:
        print("No reflect logs found.")
        return
    
    print(f"Found {len(reflect_logs)} reflect log entries:")
    print("=" * 100)
    
    # Show most recent first
    reflect_logs.reverse()
    
    if limit:
        reflect_logs = reflect_logs[:limit]
    
    for log in reflect_logs:
        print(format_log_entry(log))
    
    print("=" * 100)

def view_latest_reflect_session():
    """View the most recent reflect session (all events with same request_id)."""
    logs = load_logs()
    reflect_logs = filter_reflect_logs(logs)
    
    if not reflect_logs:
        print("No reflect logs found.")
        return
    
    # Get the most recent request_id
    latest_log = reflect_logs[-1]
    latest_request_id = latest_log.get('request_id')
    
    # Find all logs with this request_id
    session_logs = [log for log in logs if log.get('request_id') == latest_request_id]
    
    print(f"Latest reflect session (Request ID: {latest_request_id}):")
    print("=" * 100)
    
    for log in session_logs:
        print(format_log_entry(log))
    
    print("=" * 100)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "latest":
            view_latest_reflect_session()
        elif sys.argv[1] == "all":
            view_reflect_logs()
        elif sys.argv[1].isdigit():
            view_reflect_logs(int(sys.argv[1]))
        else:
            print("Usage: python log_viewer.py [latest|all|<number>]")
    else:
        view_reflect_logs(10)  # Default: show last 10 entries