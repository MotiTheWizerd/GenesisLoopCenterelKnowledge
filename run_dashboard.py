"""
Ray Memory Dashboard Launcher
Run this script to start the Streamlit dashboard
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit dashboard"""
    
    # Check if we're in the right directory
    if not os.path.exists("ui/dashboard/main.py"):
        print("❌ Error: Dashboard files not found.")
        print("Make sure you're running this from the project root directory.")
        return
    
    # Check if required files exist
    required_files = [
        "extract/faiss_index.bin",
        "extract/memory_metadata.json", 
        "extract/agent_memories.json"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print("⚠️  Warning: Some memory system files are missing:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nRun the embedding creation scripts first:")
        print("   python extract/embed.py")
        print("   or")
        print("   python extract/create_memory_datase.py")
        print("\nContinuing anyway - dashboard will show system as offline.")
    
    print("🚀 Starting Ray Memory Dashboard...")
    print("📊 Dashboard will open in your browser")
    print("🔗 URL: http://localhost:8501")
    print("\n" + "="*50)
    
    # Launch Streamlit with file watching enabled
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "ui/dashboard/main.py",
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false",
            "--server.fileWatcherType=auto",
            "--server.runOnSave=true"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

if __name__ == "__main__":
    main()