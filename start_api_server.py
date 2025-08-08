#!/usr/bin/env python3
"""
Simple script to start the API server
"""

import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 Starting Ray's API Server...")
    print("📡 Server will be available at:")
    print("   - API: http://localhost:8000")
    print("   - Docs: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("\n🛑 Press Ctrl+C to stop the server")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )