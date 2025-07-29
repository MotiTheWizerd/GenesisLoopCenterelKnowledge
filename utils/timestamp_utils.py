"""
Timestamp utilities for Ray's system responses
Ensures Ray always knows the real time and date
"""

from datetime import datetime, timezone
from typing import Dict, Any


def get_current_timestamp() -> datetime:
    """Get current timestamp with timezone"""
    return datetime.now(timezone.utc)


def format_timestamp_for_ray(dt: datetime = None) -> str:
    """Format timestamp in Ray's preferred format"""
    if dt is None:
        dt = get_current_timestamp()
    
    return dt.strftime('%Y-%m-%d %H:%M:%S UTC')


def get_ray_time_context() -> Dict[str, Any]:
    """Get comprehensive time context for Ray"""
    now = get_current_timestamp()
    
    return {
        "current_timestamp": now.isoformat(),
        "current_time_formatted": format_timestamp_for_ray(now),
        "current_date": now.strftime('%Y-%m-%d'),
        "current_time": now.strftime('%H:%M:%S'),
        "current_timezone": "UTC",
        "day_of_week": now.strftime('%A'),
        "day_of_year": now.timetuple().tm_yday,
        "week_of_year": now.isocalendar()[1],
        "month_name": now.strftime('%B'),
        "year": now.year,
        "unix_timestamp": int(now.timestamp())
    }


def add_ray_timestamp_to_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Add comprehensive timestamp information to any response for Ray"""
    time_context = get_ray_time_context()
    
    # Add to existing response
    response.update({
        "ray_timestamp": time_context,
        "response_generated_at": time_context["current_time_formatted"],
        "system_time": time_context["current_timestamp"]
    })
    
    return response