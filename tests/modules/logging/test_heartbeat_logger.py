"""
Tests for the heartbeat logger module.
"""

import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

from modules.logging.heartbeat_logger import HeartbeatLogger, EventType, log_heartbeat_event, generate_request_id


def test_heartbeat_logger_initialization():
    """Test HeartbeatLogger initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        logger = HeartbeatLogger(temp_dir)
        
        assert logger.log_dir == Path(temp_dir)
        assert logger.heartbeat_log == Path(temp_dir) / "heartbeat_events.log"
        assert logger.detailed_log == Path(temp_dir) / "heartbeat_detailed.jsonl"
        assert logger.error_log == Path(temp_dir) / "heartbeat_errors.log"


def test_log_event():
    """Test logging an event."""
    with tempfile.TemporaryDirectory() as temp_dir:
        logger = HeartbeatLogger(temp_dir)
        
        test_data = {"test": "data", "value": 123}
        logger.log_event(
            EventType.INCOMING_POST,
            test_data,
            request_id="test-123",
            action="reflect",
            metadata={"endpoint": "POST /heartbeat"}
        )
        
        # Check that files were created
        assert logger.detailed_log.exists()
        assert logger.heartbeat_log.exists()
        
        # Check detailed log content
        with open(logger.detailed_log, "r") as f:
            log_entry = json.loads(f.read().strip())
            
        assert log_entry["event_type"] == "incoming_post"
        assert log_entry["request_id"] == "test-123"
        assert log_entry["action"] == "reflect"
        assert log_entry["data"] == test_data
        assert log_entry["metadata"]["endpoint"] == "POST /heartbeat"
        
        # Check readable log content
        with open(logger.heartbeat_log, "r") as f:
            readable_content = f.read()
            
        assert "INCOMING_POST" in readable_content
        assert "test-123" in readable_content
        assert "reflect" in readable_content


def test_error_logging():
    """Test error event logging."""
    with tempfile.TemporaryDirectory() as temp_dir:
        logger = HeartbeatLogger(temp_dir)
        
        error_data = {
            "error": "Test error message",
            "traceback": "Traceback (most recent call last):\n  File test.py"
        }
        
        logger.log_event(
            EventType.ERROR,
            error_data,
            request_id="error-123",
            action="reflect"
        )
        
        # Check that error log was created
        assert logger.error_log.exists()
        
        # Check error log content
        with open(logger.error_log, "r") as f:
            error_content = f.read()
            
        assert "ERROR: Test error message" in error_content
        assert "Traceback" in error_content


def test_generate_request_id():
    """Test request ID generation."""
    request_id = generate_request_id()
    
    assert isinstance(request_id, str)
    assert len(request_id) == 8
    
    # Test uniqueness
    request_id2 = generate_request_id()
    assert request_id != request_id2


def test_log_heartbeat_event_function():
    """Test the convenience function for logging events."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('modules.logging.heartbeat_logger._logger') as mock_logger:
            mock_logger.log_event = lambda *args, **kwargs: None
            
            log_heartbeat_event(
                EventType.PROCESSING_START,
                {"function": "test_function"},
                request_id="func-123",
                action="test"
            )
            
            mock_logger.log_event.assert_called_once()