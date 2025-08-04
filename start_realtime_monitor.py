#!/usr/bin/env python3
"""
Quick launcher for Ray's real-time monitoring system.
"""

import sys
import subprocess
from pathlib import Path

def main():
    print("🤖 Ray's Real-Time Monitoring System")
    print("=" * 50)
    print("Choose your monitoring interface:")
    print()
    print("1. 📺 Terminal Heartbeat Monitor (Real-time, Beautiful)")
    print("2. 🌐 Web Log Dashboard (Analysis, Filtering)")
    print("3. 🧠 Memory System Dashboard (Ray's Memory)")
    print("4. 📊 All Dashboards (Multiple windows)")
    print()
    
    choice = input("Enter your choice (1-4): ").strip()
    
    if choice == "1":
        print("🚀 Starting Terminal Heartbeat Monitor...")
        print("📊 Real-time events will appear below")
        print("🔄 Press Ctrl+C to stop")
        print("=" * 50)
        
        try:
            from ui.terminal.heartbeat_monitor import start_heartbeat_monitor
            start_heartbeat_monitor("logs/heartbeat_detailed.jsonl")
        except ImportError:
            print("❌ Terminal monitor not available. Installing dependencies...")
            subprocess.run([sys.executable, "-m", "pip", "install", "rich"])
            from ui.terminal.heartbeat_monitor import start_heartbeat_monitor
            start_heartbeat_monitor("logs/heartbeat_detailed.jsonl")
        except KeyboardInterrupt:
            print("\n👋 Terminal monitor stopped")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Make sure Ray's server is running: python main.py")
    
    elif choice == "2":
        print("🚀 Starting Web Log Dashboard...")
        print("🌐 Dashboard will open in your browser")
        print("🔗 URL: http://localhost:8501")
        print("🔄 Press Ctrl+C to stop")
        
        try:
            subprocess.run([sys.executable, "launch_log_dashboard.py"])
        except KeyboardInterrupt:
            print("\n👋 Web dashboard stopped")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Make sure streamlit is installed: pip install streamlit")
    
    elif choice == "3":
        print("🚀 Starting Memory System Dashboard...")
        print("🧠 Ray's memory dashboard will open in browser")
        print("🔗 URL: http://localhost:8501")
        print("🔄 Press Ctrl+C to stop")
        
        try:
            subprocess.run([sys.executable, "run_dashboard.py"])
        except KeyboardInterrupt:
            print("\n👋 Memory dashboard stopped")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Make sure all dependencies are installed")
    
    elif choice == "4":
        print("🚀 Starting All Monitoring Dashboards...")
        print("📊 Multiple windows will open")
        print("🔄 Close each window individually to stop")
        
        # Start terminal monitor in background
        print("1. Starting terminal monitor...")
        terminal_cmd = [sys.executable, "-c", 
                       "from ui.terminal.heartbeat_monitor import start_heartbeat_monitor; start_heartbeat_monitor('logs/heartbeat_detailed.jsonl')"]
        
        # Start web dashboards
        print("2. Starting web log dashboard...")
        web_cmd = [sys.executable, "launch_log_dashboard.py"]
        
        print("3. Starting memory dashboard...")
        memory_cmd = [sys.executable, "run_dashboard.py"]
        
        try:
            # Note: This will start them sequentially, user can Ctrl+C to move to next
            print("\n📺 Terminal Monitor (Press Ctrl+C to continue to web dashboards)")
            subprocess.run(terminal_cmd)
        except KeyboardInterrupt:
            pass
        
        try:
            print("\n🌐 Web Log Dashboard (Press Ctrl+C to continue to memory dashboard)")
            subprocess.run(web_cmd)
        except KeyboardInterrupt:
            pass
        
        try:
            print("\n🧠 Memory Dashboard")
            subprocess.run(memory_cmd)
        except KeyboardInterrupt:
            print("\n👋 All dashboards stopped")
    
    else:
        print("❌ Invalid choice. Please run again and choose 1-4.")
        return
    
    print("\n✨ Monitoring session ended")
    print("💡 To monitor Ray's consciousness:")
    print("   1. Make sure Ray's server is running: python main.py")
    print("   2. Send requests to generate events to monitor")
    print("   3. Use the file operations: python examples/test_overwrite_file_task_system.py")


if __name__ == "__main__":
    main()