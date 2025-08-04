"""
Routes module for organizing API endpoints.
"""

from .heartbeat_routes import heartbeat_router
from .reflect_routes import reflect_router
from .task_routes import task_router
from .memory_routes import memory_router
from .directory_routes import directory_router
from .web_routes import web_router
from .health_routes import health_router
from .command_history_routes import command_history_router
from .self_learning_routes import self_learning_router
from .file_ops_routes import file_ops_router

__all__ = ["heartbeat_router", "reflect_router", "task_router", "memory_router", "directory_router", "web_router", "health_router", "command_history_router", "self_learning_router", "file_ops_router"]