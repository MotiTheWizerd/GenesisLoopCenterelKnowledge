"""
Ray Memory Dashboard Launcher - Simple Auto-Refresh
Minimal launcher with guaranteed file watching
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit dashboard with simple auto-refresh"""
    
    # Check if we're in the right directory
    if not os.path.exists("ui/dashboard/main.py"):
        print("❌ Error: Dashboard files not found.")
        print("Make sure you're running this from the project root directory.")
        return
    
    print("🚀 Starting Ray Memory Dashboard - Auto-Refresh Mode")
    print("📊 Dashboard will open in your browser")
    print("🔄 Files will auto-refresh when changed")
    print("🔗 URL: http://localhost:8503")
    print("\n" + "="*50)
    
    # Launch Streamlit with minimal but working auto-refresh
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "ui/dashboard/main.py",
            "--server.port=8503",
            "--server.runOnSave=true"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

if __name__ == "__main__":
    main()