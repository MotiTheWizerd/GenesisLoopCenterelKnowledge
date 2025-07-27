"""
Simple logging utility that doesn't interfere with FastAPI middleware.
"""

from datetime import datetime, timezone
from .heartbeat_logger import log_heartbeat_event, EventType, generate_request_id


def log_request(endpoint: str, request_data: dict = None, action: str = None):
    """
    Simple function to log incoming requests.
    """
    request_id = generate_request_id()
    
    if "GET" in endpoint:
        log_heartbeat_event(
            EventType.INCOMING_GET,
            request_data or {},
            request_id=request_id,
            action=action,
            metadata={"endpoint": endpoint}
        )
    else:
        log_heartbeat_event(
            EventType.INCOMING_POST,
            request_data or {},
            request_id=request_id,
            action=action,
            metadata={"endpoint": endpoint}
        )
    
    return request_id


def log_response(request_id: str, response_data: dict, action: str = None):
    """
    Simple function to log outgoing responses.
    """
    log_heartbeat_event(
        EventType.OUTGOING_RESPONSE,
        response_data,
        request_id=request_id,
        action=action
    )


def log_error(request_id: str, error: Exception, function_name: str, action: str = None):
    """
    Simple function to log errors.
    """
    error_data = {
        "error": str(error),
        "function": function_name,
        "traceback": str(error)
    }
    
    log_heartbeat_event(
        EventType.ERROR,
        error_data,
        request_id=request_id,
        action=action
    )