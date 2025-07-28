"""
Comprehensive logging system for heartbeat route events.
Tracks all incoming and outgoing events with detailed metadata.
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union
from pathlib import Path
from enum import Enum

# Optional rich import for terminal display
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.columns import Columns
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class EventType(Enum):
    """Types of events to log."""
    INCOMING_GET = "incoming_get"
    INCOMING_POST = "incoming_post"
    OUTGOING_RESPONSE = "outgoing_response"
    PROCESSING_START = "processing_start"
    PROCESSING_END = "processing_end"
    ERROR = "error"
    MODULE_CALL = "module_call"
    MODULE_RESPONSE = "module_response"
    # Task-specific events
    TASK_REQUESTED = "task_requested"
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_COMPLETED = "task_completed"
    TASK_ERROR = "task_error"


class HeartbeatLogger:
    """
    Comprehensive logger for heartbeat route events.
    Creates separate log files and provides structured logging.
    """
    
    def __init__(self, log_dir: str = "logs", show_terminal: bool = True):
        """
        Initialize the heartbeat logger.
        
        Args:
            log_dir: Directory to store log files
            show_terminal: Whether to show events in terminal (requires rich)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create separate log files for different types
        self.heartbeat_log = self.log_dir / "heartbeat_events.log"
        self.detailed_log = self.log_dir / "heartbeat_detailed.jsonl"
        self.error_log = self.log_dir / "heartbeat_errors.log"
        
        # Terminal display setup
        self.show_terminal = show_terminal and RICH_AVAILABLE
        if self.show_terminal:
            self.console = Console()
        else:
            self.console = None
    
    def log_event(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        request_id: Optional[str] = None,
        action: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a heartbeat event with full context.
        
        Args:
            event_type: Type of event being logged
            data: The actual data being logged
            request_id: Unique identifier for the request
            action: The action being performed (reflect, etc.)
            metadata: Additional metadata about the event
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Create the log entry
        log_entry = {
            "timestamp": timestamp,
            "event_type": event_type.value,
            "request_id": request_id,
            "action": action,
            "data": data,
            "metadata": metadata or {}
        }
        
        # Write to detailed JSON log
        self._write_detailed_log(log_entry)
        
        # Write to human-readable log
        self._write_readable_log(log_entry)
        
        # Write errors to separate error log
        if event_type == EventType.ERROR:
            self._write_error_log(log_entry)
        
        # Display in terminal if enabled
        if self.show_terminal and self.console:
            self._display_terminal_event(log_entry)
    
    def _write_detailed_log(self, log_entry: Dict[str, Any]) -> None:
        """Write detailed JSON log entry."""
        try:
            with open(self.detailed_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"Failed to write detailed log: {e}")
    
    def _write_readable_log(self, log_entry: Dict[str, Any]) -> None:
        """Write human-readable log entry."""
        try:
            timestamp = log_entry["timestamp"]
            event_type = log_entry["event_type"]
            request_id = log_entry.get("request_id", "N/A")
            action = log_entry.get("action", "N/A")
            
            readable_line = f"[{timestamp}] {event_type.upper()} | ID: {request_id} | Action: {action}"
            
            # Add data summary based on event type
            if event_type == "incoming_post":
                data = log_entry.get("data", {})
                readable_line += f" | Question: {data.get('question', 'N/A')[:50]}..."
            elif event_type == "outgoing_response":
                data = log_entry.get("data", {})
                readable_line += f" | Status: {data.get('status', 'N/A')}"
            elif event_type == "error":
                data = log_entry.get("data", {})
                readable_line += f" | Error: {data.get('error', 'N/A')}"
            
            with open(self.heartbeat_log, "a", encoding="utf-8") as f:
                f.write(readable_line + "\n")
        except Exception as e:
            print(f"Failed to write readable log: {e}")
    
    def _write_error_log(self, log_entry: Dict[str, Any]) -> None:
        """Write error-specific log entry."""
        try:
            timestamp = log_entry["timestamp"]
            data = log_entry.get("data", {})
            error_info = f"[{timestamp}] ERROR: {data.get('error', 'Unknown error')}"
            
            if "traceback" in data:
                error_info += f"\nTraceback: {data['traceback']}"
            
            with open(self.error_log, "a", encoding="utf-8") as f:
                f.write(error_info + "\n" + "="*80 + "\n")
        except Exception as e:
            print(f"Failed to write error log: {e}")
    
    def _display_terminal_event(self, log_entry: Dict[str, Any]) -> None:
        """Display event in terminal with rich formatting."""
        if not self.console:
            return
        
        try:
            event_type = log_entry.get("event_type", "")
            timestamp = log_entry.get("timestamp", "")
            request_id = log_entry.get("request_id", "N/A")
            action = log_entry.get("action", "N/A")
            data = log_entry.get("data", {})
            
            # Only show incoming requests for terminal display
            if event_type not in ["incoming_get", "incoming_post"]:
                return
            
            # Format timestamp
            time_str = timestamp.split("T")[1][:8] if "T" in timestamp else timestamp[:8]
            
            # Create event display
            event_text = Text()
            event_text.append(f"[{time_str}] ", style="dim")
            
            if event_type == "incoming_get":
                event_text.append("GET ", style="bright_green bold")
                event_text.append("/heartbeat ", style="cyan")
                event_text.append(f"(ID: {request_id[:8]})", style="yellow")
                
                panel = Panel(
                    event_text,
                    title="🔍 Status Check",
                    style="green",
                    padding=(0, 1)
                )
                
            elif event_type == "incoming_post":
                event_text.append("POST ", style="bright_blue bold")
                event_text.append("/heartbeat ", style="cyan")
                event_text.append(f"(ID: {request_id[:8]})", style="yellow")
                
                # Add action info
                if action and action != "N/A":
                    event_text.append(f" | Action: {action}", style="bright_magenta")
                
                # Create details
                details = Text()
                
                question = data.get("question", "")
                if question:
                    details.append("Question: ", style="bright_white")
                    from config.heartbeat import QUESTION_PREVIEW_LENGTH
                    question_preview = question[:QUESTION_PREVIEW_LENGTH] + "..." if len(question) > QUESTION_PREVIEW_LENGTH else question
                    details.append(f"{question_preview}\n", style="white")
                
                current_position = data.get("current_position")
                if current_position:
                    details.append("Position: ", style="bright_white")
                    from config.heartbeat import POSITION_PREVIEW_LENGTH
                    details.append(f"{str(current_position)[:POSITION_PREVIEW_LENGTH]}...\n", style="dim")
                
                # Combine event info and details
                content = Text()
                content.append_text(event_text)
                if details.plain:
                    content.append("\n\n")
                    content.append_text(details)
                
                panel = Panel(
                    content,
                    title="🤖 AI Consciousness Request",
                    style="bright_blue",
                    padding=(0, 1)
                )
            
            # Display the panel
            self.console.print(panel)
            
        except Exception as e:
            # Silently handle terminal display errors
            pass


# Global logger instance with terminal display enabled
_logger = HeartbeatLogger(show_terminal=True)


def log_heartbeat_event(
    event_type: EventType,
    data: Dict[str, Any],
    request_id: Optional[str] = None,
    action: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Convenience function to log heartbeat events.
    
    Args:
        event_type: Type of event being logged
        data: The actual data being logged
        request_id: Unique identifier for the request
        action: The action being performed
        metadata: Additional metadata about the event
    """
    _logger.log_event(event_type, data, request_id, action, metadata)


def generate_request_id() -> str:
    """Generate a unique request ID for tracking."""
    from uuid import uuid4
    return str(uuid4())[:8]