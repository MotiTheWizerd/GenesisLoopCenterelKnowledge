"""
Configuration constants for heartbeat monitoring system.
"""

from typing import Dict

# Monitor settings
MAX_EVENTS = 50
REFRESH_RATE = 0.5  # seconds
DEFAULT_LOG_FILE = "logs/heartbeat_detailed.jsonl"

# UI Colors and styles
EVENT_TYPE_STYLES: Dict[str, str] = {
    "incoming_get": "bright_green",
    "incoming_post": "bright_blue", 
    "outgoing_response": "bright_magenta",
    "processing_start": "yellow",
    "processing_end": "bright_yellow",
    "module_call": "cyan",
    "module_response": "bright_cyan",
    "error": "bright_red"
}

PANEL_STYLES: Dict[str, str] = {
    "incoming_get": "green",
    "incoming_post": "bright_blue",
    "outgoing_response": "magenta", 
    "processing_start": "yellow",
    "processing_end": "bright_yellow",
    "module_call": "cyan",
    "module_response": "bright_cyan",
    "error": "bright_red"
}

# Terminal display settings
TERMINAL_LOGGING_ENABLED = True
QUESTION_PREVIEW_LENGTH = 100
POSITION_PREVIEW_LENGTH = 200

# Monitor dashboard settings
MONITOR_EVENTS_DISPLAY = 20
MONITOR_TITLE = "🤖 AI Consciousness Heartbeat Monitor"
STATS_PANEL_TITLE = "📊 Statistics"
EVENTS_PANEL_TITLE = "📡 Live Events"
LATEST_PANEL_TITLE = "🔍 Latest Request"