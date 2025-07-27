#!/usr/bin/env python3
"""
Quick test to verify dashboard functionality.
"""

import subprocess
import sys
from pathlib import Path

def test_simple_viewer():
    """Test the simple log viewer."""
    print("🧪 Testing Simple Log Viewer...")
    
    dashboard_path = Path("ui/streamlit/simple_log_viewer.py")
    
    if not dashboard_path.exists():
        print("❌ Simple viewer not found!")
        return False
    
    print("✅ Simple viewer file exists")
    
    # Try to import the modules it uses
    try:
        sys.path.append(str(Path.cwd()))
        from utils.log_viewer import load_logs, filter_reflect_logs
        
        logs = load_logs()
        print(f"✅ Successfully loaded {len(logs)} logs")
        
        reflect_logs = filter_reflect_logs(logs)
        print(f"✅ Found {len(reflect_logs)} reflect logs")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing: {e}")
        return False

if __name__ == "__main__":
    if test_simple_viewer():
        print("\n🎉 Dashboard should work correctly!")
        print("Run: python launch_log_dashboard.py")
    else:
        print("\n❌ Issues found. Check the errors above.")