#!/usr/bin/env python3
"""
Test runner for simple main.
"""

import subprocess
import sys

print("🚀 Starting simple server...")
try:
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "simple_main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ])
except KeyboardInterrupt:
    print("\n👋 Server stopped")
except Exception as e:
    print(f"❌ Error: {e}")