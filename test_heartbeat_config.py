#!/usr/bin/env python3
"""
Test script to verify heartbeat configuration is loading correctly.
"""

from modules.heartbeat.handler import heartbeat_handler
import json

def test_heartbeat_config():
    """Test that the heartbeat configuration loads correctly."""
    print("🔧 Testing heartbeat configuration...")
    
    # Get current heartbeat
    heartbeat = heartbeat_handler.get_current_heartbeat()
    
    # Check execution protocols
    execution_protocols = heartbeat.get('execution_protocols', {})
    
    print(f"✅ Heartbeat loaded successfully")
    print(f"📋 Execution Protocols:")
    print(f"   - auto_reflection: {execution_protocols.get('auto_reflection')}")
    print(f"   - reflection_threshold_sec: {execution_protocols.get('reflection_threshold_sec')}")
    print(f"   - max_idle_loops: {execution_protocols.get('max_idle_loops')}")
    print(f"   - signal_emission_mode: {execution_protocols.get('signal_emission_mode')}")
    
    # Pretty print the full heartbeat
    print(f"\n📄 Full heartbeat structure:")
    print(json.dumps(heartbeat, indent=2))
    
    return heartbeat

if __name__ == "__main__":
    test_heartbeat_config()