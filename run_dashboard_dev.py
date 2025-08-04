"""
Ray Memory Dashboard Launcher - Development Mode
Run this script to start the Streamlit dashboard with hot reload
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit dashboard in development mode"""
    
    # Check if we're in the right directory
    if not os.path.exists("ui/dashboard/main.py"):
        print("❌ Error: Dashboard files not found.")
        print("Make sure you're running this from the project root directory.")
        return
    
    print("🚀 Starting Ray Memory Dashboard - Development Mode")
    print("📊 Dashboard will open in your browser with hot reload enabled")
    print("🔄 Files will auto-refresh when changed")
    print("🔗 URL: http://localhost:8502")
    print("\n" + "="*60)
    print("💡 Development Features Enabled:")
    print("   - Auto file watching")
    print("   - Hot reload on save")
    print("   - Development mode")
    print("   - Enhanced error reporting")
    print("="*60)
    
    # Launch Streamlit with all development features
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "ui/dashboard/main.py",
            "--server.port=8502",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false",
            "--server.fileWatcherType=auto",
            "--server.runOnSave=true",
            "--server.enableCORS=false",
            "--server.enableXsrfProtection=false",
            "--logger.level=info"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

if __name__ == "__main__":
    main()