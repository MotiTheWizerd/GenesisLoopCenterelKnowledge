#!/usr/bin/env python3
"""
Log viewer utility for filtering and displaying specific log types.
"""

import json
import sys
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

def load_logs(log_file: str = "logs/heartbeat_detailed.jsonl") -> List[Dict]:
    """Load logs from JSONL file."""
    logs = []
    try:
        with open(log_file, 'r') as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))
    except FileNotFoundError:
        print(f"Log file {log_file} not found")
        return []
    return logs

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