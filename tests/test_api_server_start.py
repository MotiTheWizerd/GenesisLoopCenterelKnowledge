#!/usr/bin/env python3
"""
Test script to verify API server can start
"""

import subprocess
import time
import requests
import sys
from pathlib import Path

def test_api_server():
    """Test that the API server can start and respond"""
    print("🚀 Testing API Server Startup")
    print("=" * 40)
    
    # Start the server in background
    print("📡 Starting FastAPI server...")
    
    try:
        # Start server process
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app", 
            "--host", "0.0.0.0", "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(3)
        
        # Test if server is responding
        try:
            response = requests.get("http://localhost:8000/health/status", timeout=5)
            if response.status_code == 200:
                print("✅ API server is running and responding!")
                print(f"📊 Health status: {response.json()}")
                success = True
            else:
                print(f"❌ Server responded with status: {response.status_code}")
                success = False
        except requests.exceptions.RequestException as e:
            print(f"❌ Could not connect to server: {e}")
            success = False
        
        # Stop the server
        print("🛑 Stopping server...")
        process.terminate()
        process.wait(timeout=5)
        
        return success
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def main():
    print("🧪 API Server Test Suite")
    print("=" * 40)
    
    # Check if main.py exists
    if not Path("main.py").exists():
        print("❌ main.py not found!")
        return
    
    # Test server startup
    if test_api_server():
        print("\n🎉 API server test passed!")
        print("\n🚀 To start the server manually:")
        print("   poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        print("\n🌐 Server will be available at:")
        print("   - API: http://localhost:8000")
        print("   - Docs: http://localhost:8000/docs")
        print("   - ReDoc: http://localhost:8000/redoc")
    else:
        print("\n❌ API server test failed!")
        print("💡 Check the server logs for errors")

if __name__ == "__main__":
    main()