"""
Command history handler for tracking Ray's recent commands
"""

import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from .models import CommandEntry, CommandHistoryResponse

logger = logging.getLogger(__name__)


class CommandHistoryHandler:
    """Handles tracking and retrieval of Ray's command history"""
    
    def __init__(self, max_history_size: int = 1000):
        self.max_history_size = max_history_size
        self.command_history: List[CommandEntry] = []
        self.history_file = Path("logs/command_history.jsonl")
        self.history_file.parent.mkdir(exist_ok=True)
        
        # Load existing history
        self._load_history_from_file()
    
    def record_command(self, 
                      command_type: str,
                      endpoint: str,
                      method: str,
                      request_data: Optional[Dict[str, Any]] = None,
                      response_status: int = 200,
                      response_time_ms: float = 0.0,
                      success: bool = True,
                      error_message: Optional[str] = None,
                      request_id: Optional[str] = None,
                      assigned_by: Optional[str] = None) -> None:
        """Record a new command in Ray's history"""
        
        try:
            # Create summary
            summary = self._create_command_summary(
                command_type, endpoint, method, request_data, success
            )
            
            # Create command entry
            command = CommandEntry(
                timestamp=datetime.now(),
                command_type=command_type,
                endpoint=endpoint,
                method=method,
                request_data=request_data,
                response_status=response_status,
                response_time_ms=response_time_ms,
                success=success,
                error_message=error_message,
                request_id=request_id,
                assigned_by=assigned_by or "unknown",
                summary=summary
            )
            
            # Add to memory
            self.command_history.append(command)
            
            # Maintain size limit
            if len(self.command_history) > self.max_history_size:
                self.command_history = self.command_history[-self.max_history_size:]
            
            # Save to file
            self._save_command_to_file(command)
            
            logger.debug(f"Recorded command: {command_type} - {endpoint}")
            
        except Exception as e:
            logger.error(f"Error recording command: {str(e)}")
    
    def get_recent_commands(self, limit: int = 20, hours: Optional[int] = None) -> CommandHistoryResponse:
        """Get Ray's recent commands"""
        
        try:
            # Filter by time if specified
            commands = self.command_history
            if hours:
                cutoff_time = datetime.now() - timedelta(hours=hours)
                commands = [cmd for cmd in commands if cmd.timestamp >= cutoff_time]
            
            # Sort by timestamp (newest first) and limit
            commands = sorted(commands, key=lambda x: x.timestamp, reverse=True)[:limit]
            
            # Calculate statistics
            total_commands = len(self.command_history)
            success_rate = self._calculate_success_rate(commands)
            avg_response_time = self._calculate_average_response_time(commands)
            command_types = list(set(cmd.command_type for cmd in commands))
            
            # Time range info
            oldest_command = min(cmd.timestamp for cmd in commands) if commands else None
            newest_command = max(cmd.timestamp for cmd in commands) if commands else None
            time_range_hours = hours or 24.0
            
            return CommandHistoryResponse(
                commands=commands,
                total_commands=total_commands,
                time_range_hours=time_range_hours,
                oldest_command=oldest_command,
                newest_command=newest_command,
                command_types=command_types,
                success_rate=success_rate,
                average_response_time_ms=avg_response_time,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error getting recent commands: {str(e)}")
            return CommandHistoryResponse(
                commands=[],
                total_commands=0,
                time_range_hours=hours or 24.0,
                oldest_command=None,
                newest_command=None,
                command_types=[],
                success_rate=0.0,
                average_response_time_ms=0.0,
                timestamp=datetime.now()
            )
    
    def get_command_stats(self) -> Dict[str, Any]:
        """Get command statistics"""
        
        if not self.command_history:
            return {
                "total_commands": 0,
                "command_types": {},
                "success_rate": 0.0,
                "average_response_time_ms": 0.0,
                "commands_last_hour": 0,
                "most_used_command": None
            }
        
        # Command type distribution
        command_types = {}
        for cmd in self.command_history:
            command_types[cmd.command_type] = command_types.get(cmd.command_type, 0) + 1
        
        # Commands in last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_commands = [cmd for cmd in self.command_history if cmd.timestamp >= one_hour_ago]
        
        # Most used command
        most_used = max(command_types.items(), key=lambda x: x[1]) if command_types else None
        
        return {
            "total_commands": len(self.command_history),
            "command_types": command_types,
            "success_rate": self._calculate_success_rate(self.command_history),
            "average_response_time_ms": self._calculate_average_response_time(self.command_history),
            "commands_last_hour": len(recent_commands),
            "most_used_command": most_used[0] if most_used else None
        }
    
    def _create_command_summary(self, command_type: str, endpoint: str, method: str, 
                               request_data: Optional[Dict], success: bool) -> str:
        """Create a human-readable summary of the command"""
        
        if not success:
            return f"❌ Failed {command_type} command"
        
        # Create specific summaries based on command type
        if command_type == "search":
            query = request_data.get("task", {}).get("query", "unknown") if request_data else "unknown"
            return f"🔍 Searched for: {query[:50]}..."
        
        elif command_type == "scrape":
            url = request_data.get("task", {}).get("url", "unknown") if request_data else "unknown"
            domain = url.split("//")[-1].split("/")[0] if "://" in url else url
            return f"🕷️ Scraped content from: {domain}"
        
        elif command_type == "reflect":
            question = request_data.get("question", "unknown") if request_data else "unknown"
            return f"🧠 Reflected on: {question[:50]}..."
        
        elif command_type == "directory":
            if "search" in endpoint:
                pattern = request_data.get("pattern", "unknown") if request_data else "unknown"
                return f"📁 Directory search: {pattern[:30]}..."
            elif "list" in endpoint:
                path = request_data.get("path", "unknown") if request_data else "unknown"
                return f"📂 Listed directory: {path[:30]}..."
            else:
                return f"📁 Directory operation: {endpoint}"
        
        elif command_type == "health":
            if "status" in endpoint:
                return "💚 Checked complete health status"
            elif "quick" in endpoint:
                return "💚 Quick health check"
            elif "vitals" in endpoint:
                return "💚 Checked system vitals"
            else:
                return "💚 Health monitoring"
        
        elif command_type == "memory":
            return f"💾 Memory operation: {endpoint}"
        
        elif command_type == "task":
            return f"📋 Task operation: {endpoint}"
        
        elif command_type == "heartbeat":
            return "💓 Heartbeat pulse"
        
        else:
            return f"⚡ {command_type.title()} command: {method} {endpoint}"
    
    def _calculate_success_rate(self, commands: List[CommandEntry]) -> float:
        """Calculate success rate for commands"""
        if not commands:
            return 0.0
        
        successful = sum(1 for cmd in commands if cmd.success)
        return (successful / len(commands)) * 100.0
    
    def _calculate_average_response_time(self, commands: List[CommandEntry]) -> float:
        """Calculate average response time for commands"""
        if not commands:
            return 0.0
        
        total_time = sum(cmd.response_time_ms for cmd in commands)
        return total_time / len(commands)
    
    def _load_history_from_file(self) -> None:
        """Load command history from file"""
        try:
            if not self.history_file.exists():
                return
            
            with open(self.history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        command = CommandEntry(
                            timestamp=datetime.fromisoformat(data['timestamp']),
                            command_type=data['command_type'],
                            endpoint=data['endpoint'],
                            method=data['method'],
                            request_data=data.get('request_data'),
                            response_status=data['response_status'],
                            response_time_ms=data['response_time_ms'],
                            success=data['success'],
                            error_message=data.get('error_message'),
                            request_id=data.get('request_id'),
                            assigned_by=data.get('assigned_by', 'unknown'),
                            summary=data['summary']
                        )
                        self.command_history.append(command)
                    except Exception as e:
                        logger.warning(f"Error parsing command history line: {str(e)}")
                        continue
            
            # Keep only recent commands
            if len(self.command_history) > self.max_history_size:
                self.command_history = self.command_history[-self.max_history_size:]
            
            logger.info(f"Loaded {len(self.command_history)} commands from history file")
            
        except Exception as e:
            logger.error(f"Error loading command history: {str(e)}")
    
    def _save_command_to_file(self, command: CommandEntry) -> None:
        """Save a single command to the history file"""
        try:
            command_data = {
                'timestamp': command.timestamp.isoformat(),
                'command_type': command.command_type,
                'endpoint': command.endpoint,
                'method': command.method,
                'request_data': command.request_data,
                'response_status': command.response_status,
                'response_time_ms': command.response_time_ms,
                'success': command.success,
                'error_message': command.error_message,
                'request_id': command.request_id,
                'assigned_by': command.assigned_by,
                'summary': command.summary
            }
            
            with open(self.history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(command_data) + '\n')
                
        except Exception as e:
            logger.error(f"Error saving command to file: {str(e)}")


# Global command history handler instance
command_history_handler = CommandHistoryHandler()