#!/usr/bin/env python3
"""Launch both API server and dashboard"""
import subprocess
import sys
import time
import threading

def start_api():
    """Start API server in background"""
    subprocess.run([sys.executable, "launch_api.py"])

def start_dashboard():
    """Start dashboard"""
    time.sleep(2)  # Wait for API to start
    subprocess.run([sys.executable, "launch_dashboard.py"])

if __name__ == "__main__":
    print("Starting Ray's Complete System...")
    
    # Start API server in background thread
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    
    # Start dashboard in main thread
    start_dashboard()
