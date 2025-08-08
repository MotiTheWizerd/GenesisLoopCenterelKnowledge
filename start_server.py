#!/usr/bin/env python3
"""
Simple server startup script for the AI Consciousness API.
This avoids issues with poetry run and provides better control.
"""

import uvicorn
import sys
import os

def main():
    print("🚀 Starting AI Consciousness API server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API docs available at: http://localhost:8000/docs")
    print("🔧 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_excludes=["*.log", "logs/*", "*.jsonl", "__pycache__/*", "*.md"],
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()