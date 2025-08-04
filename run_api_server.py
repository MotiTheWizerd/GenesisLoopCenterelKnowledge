#!/usr/bin/env python3
"""
Ray's API Server Launcher
Launch the FastAPI consciousness server
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        return True
    except ImportError as e:
        print("❌ Missing dependencies for FastAPI server!")
        print(f"   Error: {e}")
        print("\n💡 To fix this, install the required packages:")
        print("   pip install -r requirements-api.txt")
        print("   or")
        print("   pip install fastapi uvicorn")
        print("\n🔄 Alternatively, run the Streamlit dashboard instead:")
        print("   python run_dashboard_simple.py")
        return False

def main():
    """Launch Ray's FastAPI server"""
    
    if not os.path.exists("main.py"):
        print("❌ Error: main.py not found.")
        print("Make sure you're running this from the project root directory.")
        return
    
    # Check dependencies first
    if not check_dependencies():
        return
    
    print("🚀 Starting Ray's AI Consciousness API Server")
    print("🧠 FastAPI server with consciousness endpoints")
    print("🔗 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("\n" + "="*50)
    
    # Try different methods to start the server
    methods = [
        # Method 1: Direct uvicorn command
        ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        # Method 2: Python module uvicorn
        [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        # Method 3: Direct Python execution (built-in uvicorn)
        [sys.executable, "main.py"]
    ]
    
    for i, method in enumerate(methods, 1):
        try:
            print(f"🔄 Trying method {i}: {' '.join(method)}")
            subprocess.run(method)
            break
        except FileNotFoundError:
            print(f"⚠️  Method {i} failed - command not found")
            if i < len(methods):
                print(f"🔄 Trying next method...")
                continue
            else:
                print("❌ All methods failed!")
                print("\n💡 To fix this, install uvicorn:")
                print("   pip install uvicorn")
                print("   or")
                print("   pip install fastapi[all]")
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
            break
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            break

if __name__ == "__main__":
    main()