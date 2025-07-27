"""
Enhanced log viewer with rich terminal UI.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from rich.columns import Columns
from rich.rule import Rule

from modules.logging.log_viewer import LogViewer as BaseLogViewer


class RichLogViewer(BaseLogViewer):
    """
    Enhanced log viewer with rich terminal formatting.
    """
    
    def __init__(self, log_dir: str = "logs"):
        """Initialize the rich log viewer."""
        super().__init__(log_dir)
        self.console = Console()
    
    def print_recent_events_rich(self, limit: int = 10) -> None:
        """Print recent events with rich formatting."""
        events = self.get_recent_events(limit)
        
        if not events:
            self.console.print("[dim]No events found.[/dim]")
            return
        
        self.console.print(Rule(f"[bold cyan]Recent {len(events)} Events[/bold cyan]"))
        
        for i, event in enumerate(events):
            self._print_event_rich(event, i + 1)
    
    def _print_event_rich(self, event: Dict[str, Any], index: int) -> None:
        """Print a single event with rich formatting."""
        timestamp = event.get("timestamp", "N/A")
        event_type = event.get("event_type", "N/A")
        request_id = event.get("request_id", "N/A")
        action = event.get("action", "N/A")
        data = event.get("data", {})
        
        # Format timestamp
        time_str = timestamp.split("T")[1][:8] if "T" in timestamp else timestamp[:8]
        
        # Create header
        header = Text()
        header.append(f"{index:2d}. ", style="dim")
        header.append(f"[{time_str}] ", style="bright_black")
        header.append(event_type.replace("_", " ").title(), style=self._get_event_style(event_type))
        header.append(f" | ID: {request_id[:8]}", style="yellow")
        
        if action and action != "N/A":
            header.append(f" | Action: {action}", style="bright_magenta")
        
        # Create content based on event type
        content = self._format_event_content_rich(event_type, data)
        
        # Create panel
        panel_content = Text()
        panel_content.append_text(header)
        if content:
            panel_content.append("\n")
            panel_content.append_text(content)
        
        panel = Panel(
            panel_content,
            style=self._get_panel_style(event_type),
            padding=(0, 1)
        )
        
        self.console.print(panel)
    
    def _format_event_content_rich(self, event_type: str, data: Dict[str, Any]) -> Text:
        """Format event content with rich styling."""
        content = Text()
        
        if event_type == "incoming_post":
            question = data.get("question", "")
            if question:
                content.append("Question: ", style="bright_white")
                content.append(f"{question}\n", style="white")
            
            current_position = data.get("current_position")
            if current_position:
                content.append("Position: ", style="bright_white")
                content.append(f"{str(current_position)}", style="dim")
                
        elif event_type == "incoming_get":
            content.append("Status check request", style="bright_green")
            
        elif event_type == "outgoing_response":
            status = data.get("status", "")
            if status:
                content.append("Status: ", style="bright_white")
                content.append(status, style="bright_blue")
                
        elif event_type == "module_call":
            module = data.get("module", "")
            function = data.get("function", "")
            content.append(f"Calling: ", style="bright_white")
            content.append(f"{module}.{function}()", style="bright_yellow")
            
        elif event_type == "error":
            error = data.get("error", "")
            content.append("Error: ", style="bright_red")
            content.append(error, style="red")
            
        elif event_type in ["processing_start", "processing_end"]:
            function = data.get("function", "")
            success = data.get("success", True)
            status_icon = "✅" if success else "❌"
            content.append(f"{status_icon} Processing: ", style="bright_white")
            content.append(function, style="bright_cyan")
        
        return content
    
    def _get_event_style(self, event_type: str) -> str:
        """Get style for event type."""
        styles = {
            "incoming_get": "bright_green bold",
            "incoming_post": "bright_blue bold",
            "outgoing_response": "bright_magenta bold",
            "processing_start": "yellow bold",
            "processing_end": "bright_yellow bold",
            "module_call": "cyan bold",
            "module_response": "bright_cyan bold",
            "error": "bright_red bold"
        }
        return styles.get(event_type, "white bold")
    
    def _get_panel_style(self, event_type: str) -> str:
        """Get panel style for event type."""
        styles = {
            "incoming_get": "green",
            "incoming_post": "bright_blue",
            "outgoing_response": "magenta",
            "processing_start": "yellow",
            "processing_end": "bright_yellow",
            "module_call": "cyan",
            "module_response": "bright_cyan",
            "error": "bright_red"
        }
        return styles.get(event_type, "white")
    
    def print_statistics_rich(self) -> None:
        """Print statistics with rich formatting."""
        stats = self.get_statistics()
        
        self.console.print(Rule("[bold cyan]Heartbeat Log Statistics[/bold cyan]"))
        
        # Main stats
        main_table = Table.grid(padding=1)
        main_table.add_column(style="cyan", no_wrap=True)
        main_table.add_column(style="bright_white")
        
        main_table.add_row("Total Events:", str(stats['total_events']))
        main_table.add_row("Unique Requests:", str(stats['unique_request_count']))
        main_table.add_row("Error Count:", str(stats['error_count']))
        
        if stats['time_range']['start'] and stats['time_range']['end']:
            main_table.add_row("Time Range:", f"{stats['time_range']['start']} to {stats['time_range']['end']}")
        
        main_panel = Panel(main_table, title="📊 Overview", style="bright_blue")
        
        # Events by type
        type_table = Table(show_header=True, header_style="bold magenta")
        type_table.add_column("Event Type", style="cyan")
        type_table.add_column("Count", style="bright_white", justify="right")
        
        for event_type, count in stats['events_by_type'].items():
            type_table.add_row(event_type.replace("_", " ").title(), str(count))
        
        type_panel = Panel(type_table, title="📈 Events by Type", style="green")
        
        # Events by action (if any)
        action_panel = None
        if stats['events_by_action']:
            action_table = Table(show_header=True, header_style="bold magenta")
            action_table.add_column("Action", style="cyan")
            action_table.add_column("Count", style="bright_white", justify="right")
            
            for action, count in stats['events_by_action'].items():
                action_table.add_row(action, str(count))
            
            action_panel = Panel(action_table, title="🎯 Events by Action", style="yellow")
        
        # Display panels
        if action_panel:
            columns = Columns([main_panel, type_panel, action_panel], equal=True)
        else:
            columns = Columns([main_panel, type_panel], equal=True)
        
        self.console.print(columns)
    
    def print_request_logs_rich(self, request_id: str) -> None:
        """Print all logs for a specific request ID with rich formatting."""
        events = self.get_events_by_request_id(request_id)
        
        if not events:
            self.console.print(f"[dim]No events found for request ID: {request_id}[/dim]")
            return
        
        self.console.print(Rule(f"[bold cyan]Events for Request ID: {request_id}[/bold cyan]"))
        
        for i, event in enumerate(events):
            self._print_event_rich(event, i + 1)
    
    def print_error_logs_rich(self) -> None:
        """Print all error events with rich formatting."""
        errors = self.get_error_events()
        
        if not errors:
            self.console.print("[dim]No error events found.[/dim]")
            return
        
        self.console.print(Rule(f"[bold red]Error Events ({len(errors)} total)[/bold red]"))
        
        for i, error in enumerate(errors):
            self._print_event_rich(error, i + 1)


# Convenience functions with rich formatting
def view_recent_logs_rich(limit: int = 10) -> None:
    """View recent log events with rich formatting."""
    viewer = RichLogViewer()
    viewer.print_recent_events_rich(limit)


def view_log_stats_rich() -> None:
    """View log statistics with rich formatting."""
    viewer = RichLogViewer()
    viewer.print_statistics_rich()


def view_request_logs_rich(request_id: str) -> None:
    """View all logs for a specific request ID with rich formatting."""
    viewer = RichLogViewer()
    viewer.print_request_logs_rich(request_id)


def view_error_logs_rich() -> None:
    """View all error events with rich formatting."""
    viewer = RichLogViewer()
    viewer.print_error_logs_rich()