"""
Middleware and decorators for automatic heartbeat logging.
"""

import json
import traceback
from functools import wraps
from typing import Callable, Any, Dict
from fastapi import Request, Response
from fastapi.responses import JSONResponse

from .heartbeat_logger import log_heartbeat_event, EventType, generate_request_id


def log_heartbeat_route(func: Callable) -> Callable:
    """
    Decorator to automatically log heartbeat route events.
    Captures incoming requests and outgoing responses.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Generate unique request ID for tracking
        request_id = generate_request_id()
        
        # Extract request data
        request_data = {}
        action = None
        
        # Handle different argument patterns
        for arg in args:
            if hasattr(arg, 'dict'):  # Pydantic model
                request_data = arg.dict()
                action = request_data.get('action')
                break
            elif isinstance(arg, dict):
                request_data = arg
                action = request_data.get('action')
                break
        
        # Log incoming request
        if func.__name__ == 'heartbeat_action':
            log_heartbeat_event(
                EventType.INCOMING_POST,
                request_data,
                request_id=request_id,
                action=action,
                metadata={"endpoint": "POST /heartbeat"}
            )
        elif func.__name__ == 'heartbeat_status':
            log_heartbeat_event(
                EventType.INCOMING_GET,
                {},
                request_id=request_id,
                metadata={"endpoint": "GET /heartbeat"}
            )
        
        # Log processing start
        log_heartbeat_event(
            EventType.PROCESSING_START,
            {"function": func.__name__},
            request_id=request_id,
            action=action
        )
        
        try:
            # Execute the original function
            result = await func(*args, **kwargs)
            
            # Log processing end
            log_heartbeat_event(
                EventType.PROCESSING_END,
                {"function": func.__name__, "success": True},
                request_id=request_id,
                action=action
            )
            
            # Log outgoing response
            log_heartbeat_event(
                EventType.OUTGOING_RESPONSE,
                result if isinstance(result, dict) else {"response": str(result)},
                request_id=request_id,
                action=action
            )
            
            return result
            
        except Exception as e:
            # Log error
            error_data = {
                "error": str(e),
                "function": func.__name__,
                "traceback": traceback.format_exc()
            }
            
            log_heartbeat_event(
                EventType.ERROR,
                error_data,
                request_id=request_id,
                action=action
            )
            
            # Re-raise the exception
            raise
    
    return wrapper


def log_module_call(module_name: str):
    """
    Decorator to log module function calls (like reflect handler).
    
    Args:
        module_name: Name of the module being called
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            request_id = kwargs.get('request_id') or generate_request_id()
            
            # Extract action from args if available
            action = None
            request_data = {}
            
            for arg in args:
                if isinstance(arg, dict):
                    request_data = arg
                    action = arg.get('action')
                    break
            
            # Log module call
            log_heartbeat_event(
                EventType.MODULE_CALL,
                {
                    "module": module_name,
                    "function": func.__name__,
                    "input_data": request_data
                },
                request_id=request_id,
                action=action
            )
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Log module response
                log_heartbeat_event(
                    EventType.MODULE_RESPONSE,
                    {
                        "module": module_name,
                        "function": func.__name__,
                        "output_data": result if isinstance(result, dict) else {"result": str(result)}
                    },
                    request_id=request_id,
                    action=action
                )
                
                return result
                
            except Exception as e:
                # Log module error
                error_data = {
                    "module": module_name,
                    "function": func.__name__,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
                
                log_heartbeat_event(
                    EventType.ERROR,
                    error_data,
                    request_id=request_id,
                    action=action
                )
                
                raise
        
        return wrapper
    return decorator