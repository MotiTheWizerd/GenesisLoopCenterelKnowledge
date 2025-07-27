"""
Typed models for heartbeat monitoring system.
"""

from dataclasses import dataclass, field
from typing import Literal, TypedDict, Optional, Dict, Any
from datetime import datetime


EventType = Literal[
    "incoming_get", "incoming_post", "outgoing_response",
    "processing_start", "processing_end", "module_call",
    "module_response", "error"
]


class Event(TypedDict, total=False):
    """Typed event structure for heartbeat monitoring."""
    timestamp: str
    event_type: EventType
    request_id: str
    action: Optional[str]
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]]


@dataclass
class Stats:
    """Statistics for heartbeat monitoring."""
    total_requests: int = 0
    get_requests: int = 0
    post_requests: int = 0
    reflect_actions: int = 0
    errors: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    
    def update_from_event(self, event: Event) -> None:
        """Update statistics based on an event."""
        event_type = event.get("event_type", "")
        
        if event_type == "incoming_get":
            self.get_requests += 1
            self.total_requests += 1
        elif event_type == "incoming_post":
            self.post_requests += 1
            self.total_requests += 1
            
            # Check for reflect actions
            if event.get("action") == "reflect":
                self.reflect_actions += 1
        elif event_type == "error":
            self.errors += 1