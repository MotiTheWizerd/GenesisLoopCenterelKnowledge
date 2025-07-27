"""
Tests for log reader with rotation detection.
"""

import json
import tempfile
from pathlib import Path
from modules.heartbeat.reader import LogReader


def test_log_reader_basic():
    """Test basic log reading functionality."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        # Write test events
        test_events = [
            {"timestamp": "2024-01-01T10:00:00Z", "event_type": "incoming_get"},
            {"timestamp": "2024-01-01T10:01:00Z", "event_type": "incoming_post"}
        ]
        
        for event in test_events:
            f.write(json.dumps(event) + '\n')
        f.flush()
        
        log_path = Path(f.name)
    
    # File is now closed, safe to read
    reader = LogReader(log_path)
    
    # Read events
    events = list(reader.read())
    
    assert len(events) == 2
    assert events[0]["event_type"] == "incoming_get"
    assert events[1]["event_type"] == "incoming_post"
    
    # Clean up
    try:
        log_path.unlink()
    except PermissionError:
        pass  # Ignore cleanup errors on Windows


def test_log_reader_incremental():
    """Test incremental reading (only new events)."""
    with tempfile.TemporaryDirectory() as temp_dir:
        log_path = Path(temp_dir) / "test.jsonl"
        
        # Write initial events
        with log_path.open('w') as f:
            f.write(json.dumps({"timestamp": "2024-01-01T10:00:00Z", "event_type": "incoming_get"}) + '\n')
        
        reader = LogReader(log_path)
        
        # First read
        events1 = list(reader.read())
        assert len(events1) == 1
        
        # Append more events
        with log_path.open('a') as f:
            f.write(json.dumps({"timestamp": "2024-01-01T10:01:00Z", "event_type": "incoming_post"}) + '\n')
            f.write(json.dumps({"timestamp": "2024-01-01T10:02:00Z", "event_type": "error"}) + '\n')
        
        # Second read should only return new events
        events2 = list(reader.read())
        assert len(events2) == 2
        assert events2[0]["event_type"] == "incoming_post"
        assert events2[1]["event_type"] == "error"
        
        # Third read should return nothing
        events3 = list(reader.read())
        assert len(events3) == 0


def test_log_reader_rotation_detection():
    """Test log rotation detection."""
    with tempfile.TemporaryDirectory() as temp_dir:
        log_path = Path(temp_dir) / "test.jsonl"
        
        # Create initial log file
        with log_path.open('w') as f:
            f.write(json.dumps({"event": "initial"}) + '\n')
        
        reader = LogReader(log_path)
        
        # First read
        events1 = list(reader.read())
        assert len(events1) == 1
        assert events1[0]["event"] == "initial"
        
        # Simulate log rotation by removing and recreating file
        log_path.unlink()
        
        with log_path.open('w') as f:
            f.write(json.dumps({"event": "after_rotation"}) + '\n')
        
        # Read after rotation should detect new file and read from beginning
        events2 = list(reader.read())
        assert len(events2) == 1
        assert events2[0]["event"] == "after_rotation"


def test_log_reader_malformed_json():
    """Test handling of malformed JSON lines."""
    with tempfile.TemporaryDirectory() as temp_dir:
        log_path = Path(temp_dir) / "test.jsonl"
        
        # Write mix of valid and invalid JSON
        with log_path.open('w') as f:
            f.write(json.dumps({"valid": "event1"}) + '\n')
            f.write('{"invalid": json}\n')  # Malformed JSON
            f.write(json.dumps({"valid": "event2"}) + '\n')
            f.write('\n')  # Empty line
            f.write(json.dumps({"valid": "event3"}) + '\n')
        
        reader = LogReader(log_path)
        
        # Should only return valid events
        events = list(reader.read())
        
        assert len(events) == 3
        assert events[0]["valid"] == "event1"
        assert events[1]["valid"] == "event2"
        assert events[2]["valid"] == "event3"


def test_log_reader_nonexistent_file():
    """Test behavior with nonexistent file."""
    reader = LogReader(Path("/nonexistent/file.jsonl"))
    
    # Should return empty iterator without error
    events = list(reader.read())
    assert len(events) == 0


def test_log_reader_empty_file():
    """Test behavior with empty file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        log_path = Path(temp_dir) / "empty.jsonl"
        
        # Create empty file
        log_path.touch()
        
        reader = LogReader(log_path)
        
        events = list(reader.read())
        assert len(events) == 0