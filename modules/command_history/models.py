"""
Data models for Ray's command history tracking
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class CommandEntry:
    """Individual command entry"""
    timestamp: datetime
    command_type: str  # 'search', 'scrape', 'reflect', 'directory', 'health', etc.
    endpoint: str
    method: str  # GET, POST, etc.
    request_data: Optional[Dict[str, Any]]
    response_status: int
    response_time_ms: float
    success: bool
    error_message: Optional[str]
    request_id: Optional[str]
    assigned_by: Optional[str]
    summary: str  # Human-readable summary of the command


@dataclass
class CommandHistoryResponse:
    """Response containing Ray's recent command history"""
    commands: List[CommandEntry]
    total_commands: int
    time_range_hours: float
    oldest_command: Optional[datetime]
    newest_command: Optional[datetime]
    command_types: List[str]
    success_rate: float
    average_response_time_ms: float
    timestamp: datetime