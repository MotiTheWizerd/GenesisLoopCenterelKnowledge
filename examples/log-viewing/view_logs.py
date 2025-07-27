#!/usr/bin/env python3
"""
CLI script for viewing heartbeat logs with beautiful rich UI.
"""

import sys
from rich.console import Console

# Try to use rich UI, fallback to basic if not available
try:
    from ui.terminal.log_viewer import (
        view_recent_logs_rich, view_log_stats_rich, 
        view_request_logs_rich, view_error_logs_rich
    )
    RICH_AVAILABLE = True
except ImportError:
    from modules.logging import view_recent_logs, view_log_stats, view_request_logs, view_error_logs
    RICH_AVAILABLE = False


def main():
    """Main CLI function."""
    console = Console()
    
    if len(sys.argv) < 2:
        console.print("[bold cyan]Heartbeat Log Viewer[/bold cyan]")
        console.print("\n[bold]Usage:[/bold]")
        console.print("  python view_logs.py recent [limit]     - View recent events")
        console.print("  python view_logs.py stats              - View statistics")
        console.print("  python view_logs.py request <id>       - View events for request ID")
        console.print("  python view_logs.py errors             - View error events")
        console.print("  python view_logs.py monitor            - Start real-time monitor")
        
        if RICH_AVAILABLE:
            console.print("\n[dim]✨ Rich UI enabled for beautiful output[/dim]")
        else:
            console.print("\n[dim]💡 Install 'rich' for enhanced UI: pip install rich[/dim]")
        return
    
    command = sys.argv[1].lower()
    
    if command == "recent":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        if RICH_AVAILABLE:
            view_recent_logs_rich(limit)
        else:
            view_recent_logs(limit)
    
    elif command == "stats":
        if RICH_AVAILABLE:
            view_log_stats_rich()
        else:
            view_log_stats()
    
    elif command == "request":
        if len(sys.argv) < 3:
            console.print("[bold red]Error:[/bold red] Please provide a request ID")
            return
        request_id = sys.argv[2]
        if RICH_AVAILABLE:
            view_request_logs_rich(request_id)
        else:
            view_request_logs(request_id)
    
    elif command == "errors":
        if RICH_AVAILABLE:
            view_error_logs_rich()
        else:
            view_error_logs()
    
    elif command == "monitor":
        if RICH_AVAILABLE:
            console.print("[bold green]Starting real-time monitor...[/bold green]")
            console.print("[dim]Use: python monitor_heartbeat.py[/dim]")
            import subprocess
            subprocess.run([sys.executable, "monitor_heartbeat.py"])
        else:
            console.print("[bold red]Error:[/bold red] Rich library required for monitor")
            console.print("Install with: pip install rich")
    
    else:
        console.print(f"[bold red]Unknown command:[/bold red] {command}")
        console.print("Use 'recent', 'stats', 'request', 'errors', or 'monitor'")


if __name__ == "__main__":
    main()