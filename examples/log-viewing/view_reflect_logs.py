#!/usr/bin/env python3
"""
Quick script to view reflect logs.
"""

from utils.log_viewer import view_reflect_logs, view_latest_reflect_session
import sys

if __name__ == "__main__":
    print("🔍 Reflect Logs Viewer")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "latest":
        view_latest_reflect_session()
    else:
        view_reflect_logs(10)
        print("\nTip: Use 'python view_reflect_logs.py latest' to see the most recent session")