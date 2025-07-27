"""
Real-time terminal UI for monitoring heartbeat requests.
Beautiful terminal interface using rich library with proper separation of concerns.
"""

import json
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Deque, Optional

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.align import Align
from rich.syntax import Syntax
from rich import traceback

from modules.heartbeat.models import Event, Stats
from modules.heartbeat.reader import LogReader
from config.heartbeat import (
    MAX_EVENTS, REFRESH_RATE, EVENT_TYPE_STYLES, PANEL_STYLES,
    MONITOR_EVENTS_DISPLAY, MONITOR_TITLE, STATS_PANEL_TITLE,
    EVENTS_PANEL_TITLE, LATEST_PANEL_TITLE, QUESTION_PREVIEW_LENGTH
)

# Install rich traceback handler
traceback.install(show_locals=False)


class HeartbeatMonitorUI:
    """
    Pure UI renderer for heartbeat monitoring.
    Accepts data and renders, nothing else.
    """
    
    def __init__(self, console: Console):
        """Initialize the UI renderer."""
        self.console = console
        
        # Cache styles to avoid repeated instantiation
        self._cached_styles = EVENT_TYPE_STYLES.copy()
        self._cached_panel_styles = PANEL_STYLES.copy()
    
    def create_header(self, stats: Stats) -> Panel:
        """Create the header panel."""
        uptime = datetime.now() - stats.start_time
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        
        header_text = Text()
        header_text.append(MONITOR_TITLE, style="bold cyan")
        header_text.append(f" | Uptime: {uptime_str}", style="dim")
        
        return Panel(
            Align.center(header_text),
            style="bright_blue",
            padding=(0, 1)
        )
    
    def create_stats_panel(self, stats: Stats, events_count: int) -> Panel:
        """Create the statistics panel."""
        stats_table = Table.grid(padding=1)
        stats_table.add_column(style="cyan", no_wrap=True)
        stats_table.add_column(style="magenta")
        stats_table.add_column(style="cyan", no_wrap=True)
        stats_table.add_column(style="magenta")
        
        stats_table.add_row(
            "Total Requests:", str(stats.total_requests),
            "GET Requests:", str(stats.get_requests)
        )
        stats_table.add_row(
            "POST Requests:", str(stats.post_requests),
            "Reflect Actions:", str(stats.reflect_actions)
        )
        stats_table.add_row(
            "Errors:", str(stats.errors),
            "Events Shown:", str(events_count)
        )
        
        return Panel(
            stats_table,
            title=STATS_PANEL_TITLE,
            style="green"
        )
    
    def create_events_table(self, events: Deque[Event]) -> Table:
        """Create the events table."""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Time", style="dim", width=12)
        table.add_column("Type", style="cyan", width=15)
        table.add_column("ID", style="yellow", width=10)
        table.add_column("Action", style="green", width=10)
        table.add_column("Details", style="white")
        
        # Show recent events
        recent_events = list(events)[-MONITOR_EVENTS_DISPLAY:]
        
        for event in recent_events:
            timestamp = event.get("timestamp", "")
            time_str = timestamp.split("T")[1][:8] if "T" in timestamp else timestamp[:8]
            
            event_type = event.get("event_type", "unknown")
            request_id = event.get("request_id", "N/A")[:8]
            action = event.get("action", "N/A")
            
            # Create details based on event type
            details = self._format_event_details(event)
            
            # Color coding for event types
            type_style = self._cached_styles.get(event_type, "white")
            
            table.add_row(
                time_str,
                Text(event_type.replace("_", " ").title(), style=type_style),
                request_id,
                action or "N/A",
                details
            )
        
        return table
    
    def _format_event_details(self, event: Event) -> Text:
        """Format event details for display."""
        event_type = event.get("event_type", "")
        data = event.get("data", {})
        
        details = Text()
        
        if event_type == "incoming_post":
            question = data.get("question", "")
            if question:
                question_preview = question[:60] + "..." if len(question) > 60 else question
                details.append(f"Q: {question_preview}", style="bright_white")
            
            current_position = data.get("current_position")
            if current_position:
                details.append(f" | Pos: {str(current_position)[:30]}...", style="dim")
                
        elif event_type == "incoming_get":
            details.append("Status check", style="bright_green")
            
        elif event_type == "outgoing_response":
            status = data.get("status", "")
            if status:
                details.append(f"Status: {status}", style="bright_blue")
                
        elif event_type == "module_call":
            module = data.get("module", "")
            function = data.get("function", "")
            details.append(f"{module}.{function}()", style="bright_yellow")
            
        elif event_type == "error":
            error = data.get("error", "")[:50]
            details.append(f"Error: {error}...", style="bright_red")
            
        elif event_type in ["processing_start", "processing_end"]:
            function = data.get("function", "")
            success = data.get("success", True)
            status_icon = "✅" if success else "❌"
            details.append(f"{status_icon} {function}", style="bright_cyan")
        
        return details
    
    def create_latest_request_panel(self, events: Deque[Event]) -> Panel:
        """Create a panel showing the latest request details."""
        if not events:
            return Panel("No requests yet...", title=LATEST_PANEL_TITLE, style="dim")
        
        # Find the most recent incoming request
        latest_request = None
        for event in reversed(events):
            if event.get("event_type") in ["incoming_get", "incoming_post"]:
                latest_request = event
                break
        
        if not latest_request:
            return Panel("No requests yet...", title=LATEST_PANEL_TITLE, style="dim")
        
        data = latest_request.get("data", {})
        event_type = latest_request.get("event_type", "")
        
        if event_type == "incoming_post":
            # Format JSON data nicely
            json_str = json.dumps(data, indent=2)
            syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
            
            title = f"{LATEST_PANEL_TITLE} POST (ID: {latest_request.get('request_id', 'N/A')[:8]})"
            return Panel(syntax, title=title, style="bright_white")
        else:
            return Panel(
                "GET /heartbeat - Status check",
                title=f"{LATEST_PANEL_TITLE} GET (ID: {latest_request.get('request_id', 'N/A')[:8]})",
                style="bright_white"
            )
    
    def create_layout(self, stats: Stats, events: Deque[Event], log_file: Path) -> Layout:
        """Create the main layout with pre-rendered components."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=8)
        )
        
        layout["body"].split_row(
            Layout(name="main", ratio=2),
            Layout(name="sidebar", ratio=1)
        )
        
        layout["sidebar"].split_column(
            Layout(name="stats"),
            Layout(name="latest")
        )
        
        # Fill the layout with pre-rendered components
        layout["header"].update(self.create_header(stats))
        layout["stats"].update(self.create_stats_panel(stats, len(events)))
        layout["main"].update(Panel(self.create_events_table(events), title=EVENTS_PANEL_TITLE, style="bright_blue"))
        layout["latest"].update(self.create_latest_request_panel(events))
        
        # Footer with instructions
        footer_text = Text()
        footer_text.append("Press ", style="dim")
        footer_text.append("Ctrl+C", style="bold red")
        footer_text.append(" to exit | Monitoring: ", style="dim")
        footer_text.append(str(log_file), style="bright_cyan")
        
        layout["footer"].update(Panel(Align.center(footer_text), style="dim"))
        
        return layout


class HeartbeatMonitor:
    """
    Real-time terminal monitor for heartbeat requests.
    Handles data management and coordinates with UI renderer.
    """
    
    def __init__(self, log_file: Path):
        """
        Initialize the heartbeat monitor.
        
        Args:
            log_file: Path to the detailed log file to monitor
        """
        self.log_file = log_file
        self.console = Console()
        self.ui = HeartbeatMonitorUI(self.console)
        self.reader = LogReader(log_file)
        
        # Use deque with maxlen for automatic size management
        self.events: Deque[Event] = deque(maxlen=MAX_EVENTS)
        self.stats = Stats()
        self.running = False
    
    def _process_new_events(self) -> None:
        """Process new events from the log file."""
        for event_data in self.reader.read():
            # Cast to Event type (runtime validation could be added here)
            event: Event = event_data  # type: ignore
            
            self.events.append(event)
            self.stats.update_from_event(event)
    
    def start_monitoring(self) -> None:
        """Start the real-time monitoring."""
        self.running = True
        
        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Clear screen and show initial message
        self.console.clear()
        
        with Live(
            self.ui.create_layout(self.stats, self.events, self.log_file),
            console=self.console,
            refresh_per_second=int(1 / REFRESH_RATE)
        ) as live:
            try:
                while self.running:
                    self._process_new_events()
                    live.update(self.ui.create_layout(self.stats, self.events, self.log_file))
                    time.sleep(REFRESH_RATE)
                    
            except KeyboardInterrupt:
                self.running = False
                self.console.print("\n[bold red]Monitoring stopped.[/bold red]")
    
    def stop_monitoring(self) -> None:
        """Stop the monitoring."""
        self.running = False


def start_heartbeat_monitor(log_file: str) -> None:
    """
    Start the heartbeat monitor.
    
    Args:
        log_file: Path to the log file to monitor
    """
    monitor = HeartbeatMonitor(Path(log_file))
    
    try:
        monitor.start_monitoring()
    except Exception as e:
        console = Console()
        console.print(f"[bold red]Error starting monitor: {e}[/bold red]")


if __name__ == "__main__":
    from config.heartbeat import DEFAULT_LOG_FILE
    start_heartbeat_monitor(DEFAULT_LOG_FILE)