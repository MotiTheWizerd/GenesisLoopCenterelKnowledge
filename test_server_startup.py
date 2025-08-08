#!/usr/bin/env python3
"""
Test script to verify the server can start without hanging.
"""

import sys
import importlib.util

def test_imports():
    """Test that all imports work without hanging."""
    print("🧪 Testing imports...")
    
    try:
        print("  - Testing FastAPI import...")
        from fastapi import FastAPI
        
        print("  - Testing routes import...")
        from modules.routes import agents_router
        
        print("  - Testing agents handler...")
        from modules.agents.handler import handle_agent_message
        
        print("  - Testing agents models...")
        from modules.agents.models import AgentMessageRequest
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_app_creation():
    """Test that the FastAPI app can be created."""
    print("🧪 Testing app creation...")
    
    try:
        from main import app
        print(f"✅ App created successfully: {app.title}")
        return True
        
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def main():
    print("🔧 Server Startup Test")
    print("=" * 30)
    
    success = True
    
    if not test_imports():
        success = False
    
    if not test_app_creation():
        success = False
    
    if success:
        print("\n✅ All tests passed! Server should start normally.")
        print("💡 Run: python start_server.py")
    else:
        print("\n❌ Tests failed! Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()