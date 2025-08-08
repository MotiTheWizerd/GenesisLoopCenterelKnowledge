#!/usr/bin/env python3
"""Launch the main dashboard"""
import subprocess
import sys

if __name__ == "__main__":
    print("Starting Ray's Dashboard...")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "ui/streamlit/main_menu.py", "--server.port", "8501"
    ])
