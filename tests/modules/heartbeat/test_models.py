"""
Tests for heartbeat models.
"""

from datetime import datetime
from modules.heartbeat.models import Event, Stats, EventType


def test_stats_initialization():
    """Test Stats dataclass initialization."""
    stats = Stats()
    
    assert stats.total_requests == 0
    assert stats.get_requests == 0
    assert stats.post_requests == 0
    assert stats.reflect_actions == 0
    assert stats.errors == 0
    assert isinstance(stats.start_time, datetime)


def test_stats_update_from_incoming_get():
    """Test stats update from incoming GET event."""
    stats = Stats()
    
    event: Event = {
        "timestamp": "2024-01-01T10:00:00Z",
        "event_type": "incoming_get",
        "request_id": "test-123",
        "data": {}
    }
    
    stats.update_from_event(event)
    
    assert stats.get_requests == 1
    assert stats.total_requests == 1
    assert stats.post_requests == 0
    assert stats.reflect_actions == 0
    assert stats.errors == 0


def test_stats_update_from_incoming_post():
    """Test stats update from incoming POST event."""
    stats = Stats()
    
    event: Event = {
        "timestamp": "2024-01-01T10:00:00Z",
        "event_type": "incoming_post",
        "request_id": "test-123",
        "action": "reflect",
        "data": {"question": "Test question"}
    }
    
    stats.update_from_event(event)
    
    assert stats.post_requests == 1
    assert stats.total_requests == 1
    assert stats.get_requests == 0
    assert stats.reflect_actions == 1
    assert stats.errors == 0


def test_stats_update_from_error():
    """Test stats update from error event."""
    stats = Stats()
    
    event: Event = {
        "timestamp": "2024-01-01T10:00:00Z",
        "event_type": "error",
        "request_id": "test-123",
        "data": {"error": "Test error"}
    }
    
    stats.update_from_event(event)
    
    assert stats.errors == 1
    assert stats.total_requests == 0
    assert stats.get_requests == 0
    assert stats.post_requests == 0
    assert stats.reflect_actions == 0


def test_stats_multiple_updates():
    """Test stats with multiple event updates."""
    stats = Stats()
    
    # Add GET request
    get_event: Event = {
        "timestamp": "2024-01-01T10:00:00Z",
        "event_type": "incoming_get",
        "request_id": "test-1",
        "data": {}
    }
    stats.update_from_event(get_event)
    
    # Add POST request with reflect action
    post_event: Event = {
        "timestamp": "2024-01-01T10:01:00Z",
        "event_type": "incoming_post",
        "request_id": "test-2",
        "action": "reflect",
        "data": {"question": "Test"}
    }
    stats.update_from_event(post_event)
    
    # Add error
    error_event: Event = {
        "timestamp": "2024-01-01T10:02:00Z",
        "event_type": "error",
        "request_id": "test-3",
        "data": {"error": "Test error"}
    }
    stats.update_from_event(error_event)
    
    assert stats.total_requests == 2
    assert stats.get_requests == 1
    assert stats.post_requests == 1
    assert stats.reflect_actions == 1
    assert stats.errors == 1


def test_event_type_literal():
    """Test that EventType literal works correctly."""
    # This should not raise any type errors
    valid_types: list[EventType] = [
        "incoming_get", "incoming_post", "outgoing_response",
        "processing_start", "processing_end", "module_call",
        "module_response", "error"
    ]
    
    assert len(valid_types) == 8


def test_event_typed_dict():
    """Test Event TypedDict structure."""
    # Test minimal event
    minimal_event: Event = {
        "timestamp": "2024-01-01T10:00:00Z",
        "event_type": "incoming_get",
        "request_id": "test-123"
    }
    
    assert minimal_event["timestamp"] == "2024-01-01T10:00:00Z"
    assert minimal_event["event_type"] == "incoming_get"
    assert minimal_event["request_id"] == "test-123"
    
    # Test full event
    full_event: Event = {
        "timestamp": "2024-01-01T10:00:00Z",
        "event_type": "incoming_post",
        "request_id": "test-123",
        "action": "reflect",
        "data": {"question": "Test question"},
        "metadata": {"endpoint": "POST /heartbeat"}
    }
    
    assert full_event["action"] == "reflect"
    assert full_event["data"]["question"] == "Test question"
    assert full_event["metadata"]["endpoint"] == "POST /heartbeat"