#!/usr/bin/env python3
"""
Real-time heartbeat monitor - Beautiful terminal UI for monitoring AI consciousness interactions.
"""

import typer
from pathlib import Path
from rich.console import Console

from ui.terminal.heartbeat_monitor import start_heartbeat_monitor
from config.heartbeat import DEFAULT_LOG_FILE, REFRESH_RATE

console = Console()


def main(
    log_file: str = typer.Option(
        DEFAULT_LOG_FILE,
        "--log",
        "-l",
        help="Path to the log file to monitor"
    ),
    refresh: float = typer.Option(
        REFRESH_RATE,
        "--refresh",
        "-r",
        help="Refresh rate in seconds"
    )
) -> None:
    """
    Real-time monitor for AI consciousness heartbeat requests.
    
    The monitor displays:
    📊 Real-time statistics
    📡 Live event stream with details  
    🔍 Latest request data
    
    Press Ctrl+C to exit the monitor.
    """
    # Check if log file exists or can be created
    log_path = Path(log_file)
    if not log_path.parent.exists():
        console.print(f"[bold red]Error:[/bold red] Log directory '{log_path.parent}' does not exist.")
        console.print("Please ensure the logging system is set up and the server has been started.")
        raise typer.Exit(1)
    
    console.print("🚀 Starting heartbeat monitor...")
    console.print(f"📁 Monitoring: {log_file}")
    console.print(f"⚡ Refresh rate: {refresh}s")
    console.print("💡 Tip: Start your FastAPI server to see live events!")
    console.print()
    
    # Update refresh rate in config if different
    if refresh != REFRESH_RATE:
        import config.heartbeat
        config.heartbeat.REFRESH_RATE = refresh
    
    try:
        start_heartbeat_monitor(log_file)
    except KeyboardInterrupt:
        console.print("\n👋 Monitor stopped. Goodbye!")
    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    typer.run(main)