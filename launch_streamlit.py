#!/usr/bin/env python3
"""
Launch script for Ray's Streamlit Dashboard Hub.
"""

import subprocess
import sys
import time
from pathlib import Path

def check_port_available(port):
    """Check if a port is available."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def main():
    """Launch the Streamlit dashboard."""
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    streamlit_dir = script_dir / "ui" / "streamlit"
    
    if not streamlit_dir.exists():
        print("❌ Streamlit directory not found!")
        return 1
    
    # Check if main_menu.py exists
    main_menu = streamlit_dir / "main_menu.py"
    if not main_menu.exists():
        print("❌ main_menu.py not found!")
        return 1
    
    # Find an available port
    port = 8500
    while not check_port_available(port) and port < 8510:
        print(f"⚠️ Port {port} is busy, trying {port + 1}...")
        port += 1
    
    if port >= 8510:
        print("❌ No available ports found between 8501-8509")
        return 1
    
    print("🚀 Launching Ray's Dashboard Hub...")
    print(f"📁 Working directory: {streamlit_dir}")
    print(f"🌐 Port: {port}")
    
    try:
        # Launch Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            "main_menu.py",  # Use relative path
            "--server.port", str(port),
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false",
            "--server.headless", "false"  # Allow browser to open
        ]
        
        print(f"🔧 Command: {' '.join(cmd)}")
        print(f"🌐 Dashboard will be available at: http://localhost:{port}")
        
        # Run from project root, not streamlit directory
        # This ensures all relative paths work correctly
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            "ui/streamlit/main_menu.py",  # Full path from project root
            "--server.port", str(port),
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false",
            "--server.headless", "false"  # Allow browser to open
        ]
        
        print(f"🔧 Command: {' '.join(cmd)}")
        print(f"🌐 Dashboard will be available at: http://localhost:{port}")
        
        # Run from project root directory
        subprocess.run(cmd, cwd=script_dir, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to launch Streamlit: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())