"""
Command history routes for Ray's command tracking
"""

from fastapi import APIRouter
from typing import Optional
import logging
from datetime import datetime

from modules.command_history.handler import command_history_handler
from utils.timestamp_utils import add_ray_timestamp_to_response, get_ray_time_context

logger = logging.getLogger(__name__)

# Create router
command_history_router = APIRouter(prefix="/commands", tags=["commands"])


@command_history_router.get("/recent")
async def get_recent_commands(
    limit: Optional[int] = 20,
    hours: Optional[int] = None
):
    """
    Get Ray's recent commands
    
    Args:
        limit: Maximum number of commands to return (default: 20)
        hours: Only return commands from the last N hours (optional)
    """
    try:
        history = command_history_handler.get_recent_commands(limit=limit, hours=hours)
        
        # Convert to dict for JSON response
        result = {
            "commands": [
                {
                    "timestamp": cmd.timestamp.isoformat(),
                    "command_type": cmd.command_type,
                    "endpoint": cmd.endpoint,
                    "method": cmd.method,
                    "request_data": cmd.request_data,
                    "response_status": cmd.response_status,
                    "response_time_ms": cmd.response_time_ms,
                    "success": cmd.success,
                    "error_message": cmd.error_message,
                    "request_id": cmd.request_id,
                    "assigned_by": cmd.assigned_by,
                    "summary": cmd.summary,
                    "time_ago": _format_time_ago(cmd.timestamp)
                } for cmd in history.commands
            ],
            "total_commands": history.total_commands,
            "time_range_hours": history.time_range_hours,
            "oldest_command": history.oldest_command.isoformat() if history.oldest_command else None,
            "newest_command": history.newest_command.isoformat() if history.newest_command else None,
            "command_types": history.command_types,
            "success_rate": history.success_rate,
            "average_response_time_ms": history.average_response_time_ms,
            "timestamp": history.timestamp.isoformat()
        }
        
        logger.info(f"Retrieved {len(history.commands)} recent commands")
        
        # Add comprehensive timestamp information for Ray
        result = add_ray_timestamp_to_response(result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving recent commands: {str(e)}")
        return {
            "commands": [],
            "total_commands": 0,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@command_history_router.get("/stats")
async def get_command_stats():
    """Get command statistics"""
    try:
        stats = command_history_handler.get_command_stats()
        stats["timestamp"] = datetime.now().isoformat()
        
        logger.info("Retrieved command statistics")
        
        # Add comprehensive timestamp information for Ray
        stats = add_ray_timestamp_to_response(stats)
        
        return stats
        
    except Exception as e:
        logger.error(f"Error retrieving command stats: {str(e)}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@command_history_router.get("/live")
async def get_live_commands():
    """Get live command feed (last 10 commands for dashboard)"""
    try:
        history = command_history_handler.get_recent_commands(limit=10, hours=1)
        
        # Simplified format for live updates
        result = {
            "commands": [
                {
                    "timestamp": cmd.timestamp.isoformat(),
                    "time_ago": _format_time_ago(cmd.timestamp),
                    "command_type": cmd.command_type,
                    "summary": cmd.summary,
                    "success": cmd.success,
                    "response_time_ms": cmd.response_time_ms,
                    "status_icon": "✅" if cmd.success else "❌"
                } for cmd in history.commands
            ],
            "total_commands_today": len([cmd for cmd in history.commands if cmd.timestamp.date() == datetime.now().date()]),
            "success_rate": history.success_rate,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add comprehensive timestamp information for Ray
        result = add_ray_timestamp_to_response(result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving live commands: {str(e)}")
        return {
            "commands": [],
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def _format_time_ago(timestamp: datetime) -> str:
    """Format timestamp as 'time ago' string"""
    try:
        now = datetime.now()
        diff = now - timestamp
        
        if diff.total_seconds() < 60:
            return f"{int(diff.total_seconds())}s ago"
        elif diff.total_seconds() < 3600:
            return f"{int(diff.total_seconds() / 60)}m ago"
        elif diff.total_seconds() < 86400:
            return f"{int(diff.total_seconds() / 3600)}h ago"
        else:
            return f"{int(diff.total_seconds() / 86400)}d ago"
    except:
        return "unknown"