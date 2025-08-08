#!/usr/bin/env python3
"""
Install JSON viewer dependencies for better Streamlit JSON display.
"""

import subprocess
import sys

def install_packages():
    """Install required packages for enhanced JSON display."""
    
    packages = [
        "streamlit-ace",  # For syntax-highlighted code display
        "pygments",      # For syntax highlighting
        "streamlit-extras"  # For additional UI components
    ]
    
    print("🔧 Installing JSON viewer enhancements...")
    
    for package in packages:
        try:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            print("⚠️ Continuing with other packages...")
    
    print("🎉 Installation complete!")

if __name__ == "__main__":
    install_packages()