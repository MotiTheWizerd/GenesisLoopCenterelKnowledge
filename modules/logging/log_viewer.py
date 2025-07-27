"""
Utilities for viewing and analyzing heartbeat logs.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict


class LogViewer:
    """
    Utility class for viewing and analyzing heartbeat logs.
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize the log viewer.
        
        Args:
            log_dir: Directory containing log files
        """
        self.log_dir = Path(log_dir)
        self.detailed_log = self.log_dir / "heartbeat_detailed.jsonl"
        self.readable_log = self.log_dir / "heartbeat_events.log"
        self.error_log = self.log_dir / "heartbeat_errors.log"
    
    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get the most recent events from the detailed log.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent log events
        """
        events = []
        
        if not self.detailed_log.exists():
            return events
        
        try:
            with open(self.detailed_log, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            # Get the last 'limit' lines
            recent_lines = lines[-limit:] if len(lines) > limit else lines
            
            for line in recent_lines:
                try:
                    event = json.loads(line.strip())
                    events.append(event)
                except json.JSONDecodeError:
                    continue
                    
        except Exception as e:
            print(f"Error reading log file: {e}")
        
        return events
    
    def get_events_by_request_id(self, request_id: str) -> List[Dict[str, Any]]:
        """
        Get all events for a specific request ID.
        
        Args:
            request_id: The request ID to filter by
            
        Returns:
            List of events for the request
        """
        events = []
        
        if not self.detailed_log.exists():
            return events
        
        try:
            with open(self.detailed_log, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        if event.get("request_id") == request_id:
                            events.append(event)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"Error reading log file: {e}")
        
        return events
    
    def get_events_by_action(self, action: str) -> List[Dict[str, Any]]:
        """
        Get all events for a specific action.
        
        Args:
            action: The action to filter by (e.g., "reflect")
            
        Returns:
            List of events for the action
        """
        events = []
        
        if not self.detailed_log.exists():
            return events
        
        try:
            with open(self.detailed_log, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        if event.get("action") == action:
                            events.append(event)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"Error reading log file: {e}")
        
        return events
    
    def get_error_events(self) -> List[Dict[str, Any]]:
        """
        Get all error events.
        
        Returns:
            List of error events
        """
        events = []
        
        if not self.detailed_log.exists():
            return events
        
        try:
            with open(self.detailed_log, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        if event.get("event_type") == "error":
                            events.append(event)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"Error reading log file: {e}")
        
        return events
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about logged events.
        
        Returns:
            Dictionary containing various statistics
        """
        stats = {
            "total_events": 0,
            "events_by_type": defaultdict(int),
            "events_by_action": defaultdict(int),
            "unique_request_ids": set(),
            "error_count": 0,
            "time_range": {"start": None, "end": None}
        }
        
        if not self.detailed_log.exists():
            return dict(stats)
        
        try:
            with open(self.detailed_log, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        stats["total_events"] += 1
                        
                        # Count by event type
                        event_type = event.get("event_type", "unknown")
                        stats["events_by_type"][event_type] += 1
                        
                        # Count by action
                        action = event.get("action")
                        if action:
                            stats["events_by_action"][action] += 1
                        
                        # Track unique request IDs
                        request_id = event.get("request_id")
                        if request_id:
                            stats["unique_request_ids"].add(request_id)
                        
                        # Count errors
                        if event_type == "error":
                            stats["error_count"] += 1
                        
                        # Track time range
                        timestamp = event.get("timestamp")
                        if timestamp:
                            if stats["time_range"]["start"] is None:
                                stats["time_range"]["start"] = timestamp
                            stats["time_range"]["end"] = timestamp
                            
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"Error reading log file: {e}")
        
        # Convert sets to counts
        stats["unique_request_count"] = len(stats["unique_request_ids"])
        del stats["unique_request_ids"]
        
        # Convert defaultdicts to regular dicts
        stats["events_by_type"] = dict(stats["events_by_type"])
        stats["events_by_action"] = dict(stats["events_by_action"])
        
        return stats
    
    def print_recent_events(self, limit: int = 10) -> None:
        """
        Print recent events in a readable format.
        
        Args:
            limit: Number of recent events to print
        """
        events = self.get_recent_events(limit)
        
        print(f"\n=== Recent {len(events)} Events ===")
        for event in events:
            timestamp = event.get("timestamp", "N/A")
            event_type = event.get("event_type", "N/A")
            request_id = event.get("request_id", "N/A")
            action = event.get("action", "N/A")
            
            print(f"[{timestamp}] {event_type.upper()} | ID: {request_id} | Action: {action}")
            
            # Show relevant data based on event type
            data = event.get("data", {})
            if event_type == "incoming_post" and "question" in data:
                question = data["question"][:100] + "..." if len(data.get("question", "")) > 100 else data.get("question", "")
                print(f"  Question: {question}")
            elif event_type == "outgoing_response" and "status" in data:
                print(f"  Status: {data['status']}")
            elif event_type == "error":
                print(f"  Error: {data.get('error', 'N/A')}")
            
            print()
    
    def print_statistics(self) -> None:
        """Print statistics about logged events."""
        stats = self.get_statistics()
        
        print("\n=== Heartbeat Log Statistics ===")
        print(f"Total Events: {stats['total_events']}")
        print(f"Unique Requests: {stats['unique_request_count']}")
        print(f"Error Count: {stats['error_count']}")
        
        if stats['time_range']['start'] and stats['time_range']['end']:
            print(f"Time Range: {stats['time_range']['start']} to {stats['time_range']['end']}")
        
        print("\nEvents by Type:")
        for event_type, count in stats['events_by_type'].items():
            print(f"  {event_type}: {count}")
        
        if stats['events_by_action']:
            print("\nEvents by Action:")
            for action, count in stats['events_by_action'].items():
                print(f"  {action}: {count}")


# Convenience functions
def view_recent_logs(limit: int = 10) -> None:
    """View recent log events."""
    viewer = LogViewer()
    viewer.print_recent_events(limit)


def view_log_stats() -> None:
    """View log statistics."""
    viewer = LogViewer()
    viewer.print_statistics()


def view_request_logs(request_id: str) -> None:
    """View all logs for a specific request ID."""
    viewer = LogViewer()
    events = viewer.get_events_by_request_id(request_id)
    
    print(f"\n=== Events for Request ID: {request_id} ===")
    for event in events:
        timestamp = event.get("timestamp", "N/A")
        event_type = event.get("event_type", "N/A")
        print(f"[{timestamp}] {event_type.upper()}")
        
        data = event.get("data", {})
        if data:
            print(f"  Data: {json.dumps(data, indent=2)}")
        print()


def view_error_logs() -> None:
    """View all error events."""
    viewer = LogViewer()
    errors = viewer.get_error_events()
    
    print(f"\n=== Error Events ({len(errors)} total) ===")
    for error in errors:
        timestamp = error.get("timestamp", "N/A")
        data = error.get("data", {})
        print(f"[{timestamp}] ERROR")
        print(f"  Error: {data.get('error', 'N/A')}")
        if "traceback" in data:
            print(f"  Traceback: {data['traceback']}")
        print()