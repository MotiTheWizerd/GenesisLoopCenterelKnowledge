#!/usr/bin/env python3
"""
Test script to demonstrate the heartbeat logging system.
"""

import asyncio
import json
from modules.logging import view_recent_logs, view_log_stats
from main import HeartbeatRequest, heartbeat_status, heartbeat_action


async def test_logging_system():
    """Test the logging system with sample requests."""
    print("Testing heartbeat logging system...\n")
    
    # Test GET heartbeat
    print("1. Testing GET /heartbeat")
    get_response = await heartbeat_status()
    print(f"Response: {json.dumps(get_response, indent=2)}\n")
    
    # Test POST heartbeat with reflect action
    print("2. Testing POST /heartbeat with reflect action")
    reflect_request = HeartbeatRequest(
        action="reflect",
        question="What is the meaning of consciousness?",
        current_position={"context": "testing"}
    )
    post_response = await heartbeat_action(reflect_request)
    print(f"Response: {json.dumps(post_response, indent=2)}\n")
    
    # Test POST heartbeat with unknown action
    print("3. Testing POST /heartbeat with unknown action")
    unknown_request = HeartbeatRequest(
        action="unknown_action",
        question="This should trigger an error response"
    )
    unknown_response = await heartbeat_action(unknown_request)
    print(f"Response: {json.dumps(unknown_response, indent=2)}\n")
    
    # View the logs
    print("4. Viewing recent logs:")
    view_recent_logs(10)
    
    print("\n5. Viewing log statistics:")
    view_log_stats()


if __name__ == "__main__":
    asyncio.run(test_logging_system())