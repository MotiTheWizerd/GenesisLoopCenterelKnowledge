#!/usr/bin/env python3
"""
Launcher for the AI Consciousness Log Dashboard.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch the Streamlit log dashboard."""
    print("🚀 AI Consciousness Log Dashboard Launcher")
    print("=" * 50)
    print("Choose a dashboard:")
    print("1. 📝 Simple Log Viewer (Recommended)")
    print("2. 📋 Standard Log Dashboard")
    print("3. 🔬 Advanced Log Viewer")
    print()
    
    choice = input("Enter your choice (1-3): ").strip()
    
    dashboards = {
        "1": "ui/streamlit/simple_log_viewer.py",
        "2": "ui/streamlit/log_dashboard.py", 
        "3": "ui/streamlit/advanced_log_viewer.py"
    }
    
    dashboard_path = Path(dashboards.get(choice, dashboards["1"]))
    
    if not dashboard_path.exists():
        print("❌ Dashboard file not found!")
        return
    
    print(f"🚀 Launching {dashboard_path.name}...")
    print("📊 Dashboard will open in your browser")
    print("🔄 Press Ctrl+C to stop")
    print()
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.port", "8501",
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        print("💡 Make sure streamlit is installed: poetry install")

if __name__ == "__main__":
    main()t