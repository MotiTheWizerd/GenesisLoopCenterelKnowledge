#!/usr/bin/env python3
"""
Debug script to monitor memory endpoint requests and identify 422 errors
"""

import json
import time
from pathlib import Path
from datetime import datetime

def monitor_memory_requests():
    """Monitor the heartbeat logs for memory-related requests"""
    
    log_file = Path("logs/heartbeat_detailed.jsonl")
    
    if not log_file.exists():
        print("❌ Log file not found: logs/heartbeat_detailed.jsonl")
        return
    
    print("🔍 Monitoring memory requests...")
    print("Looking for 422 errors and memory-related requests...")
    print("-" * 60)
    
    # Read the last 50 lines to see recent activity
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            recent_lines = lines[-50:] if len(lines) > 50 else lines
            
            memory_requests = []
            error_requests = []
            
            for line in recent_lines:
                try:
                    log_entry = json.loads(line.strip())
                    
                    # Check for memory-related requests
                    if 'memory' in log_entry.get('data', {}).get('endpoint', '').lower():
                        memory_requests.append(log_entry)
                    
                    # Check for error responses
                    if log_entry.get('event_type') == 'error':
                        error_requests.append(log_entry)
                        
                except json.JSONDecodeError:
                    continue
            
            print(f"📊 Found {len(memory_requests)} memory-related requests in recent logs")
            print(f"📊 Found {len(error_requests)} error requests in recent logs")
            print()
            
            # Show recent memory requests
            if memory_requests:
                print("🧠 Recent Memory Requests:")
                for req in memory_requests[-10:]:  # Show last 10
                    timestamp = req.get('timestamp', 'unknown')
                    endpoint = req.get('data', {}).get('endpoint', 'unknown')
                    event_type = req.get('event_type', 'unknown')
                    print(f"  {timestamp} | {event_type} | {endpoint}")
                print()
            
            # Show recent errors
            if error_requests:
                print("❌ Recent Error Requests:")
                for req in error_requests[-5:]:  # Show last 5
                    timestamp = req.get('timestamp', 'unknown')
                    error = req.get('data', {}).get('error', 'unknown')
                    action = req.get('action', 'unknown')
                    print(f"  {timestamp} | {action} | {error}")
                print()
            
            # Look for specific patterns that might cause 422 errors
            print("🔍 Analyzing request patterns...")
            
            # Check if there are any requests with missing required fields
            for req in memory_requests:
                data = req.get('data', {})
                if 'store' in data.get('endpoint', '').lower():
                    print(f"📤 Memory store request found:")
                    print(f"   Timestamp: {req.get('timestamp')}")
                    print(f"   Event: {req.get('event_type')}")
                    print(f"   Data: {json.dumps(data, indent=4)}")
                    print()
                    
    except Exception as e:
        print(f"❌ Error reading log file: {e}")

def check_server_status():
    """Check if the server is running and responding"""
    import requests
    
    try:
        response = requests.get("http://localhost:8000/heartbeat", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and responding")
            return True
        else:
            print(f"⚠️ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Server is not responding: {e}")
        return False

def main():
    print("🚀 Memory Request Debugger")
    print("=" * 60)
    
    # Check server status
    server_running = check_server_status()
    print()
    
    # Monitor recent requests
    monitor_memory_requests()
    
    if server_running:
        print("💡 Recommendations:")
        print("1. Check what client/agent is making requests to /memory/store")
        print("2. Ensure all requests include the required 'memories' field")
        print("3. Validate request format matches StoreRequest model")
        print("4. Monitor logs in real-time: tail -f logs/heartbeat_detailed.jsonl")
    else:
        print("💡 Start the server first: python main.py")

if __name__ == "__main__":
    main()