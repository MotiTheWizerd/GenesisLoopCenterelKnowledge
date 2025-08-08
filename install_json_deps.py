#!/usr/bin/env python3
"""
Install JSON viewer dependencies using Poetry.
"""

import subprocess
import sys

def install_with_poetry():
    """Install dependencies using Poetry."""
    
    print("🔧 Installing JSON viewer dependencies with Poetry...")
    
    try:
        # Install the dependencies
        result = subprocess.run([
            "poetry", "add", 
            "streamlit-ace", 
            "streamlit-extras", 
            "pygments"
        ], check=True, capture_output=True, text=True)
        
        print("✅ Dependencies installed successfully!")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print(f"Error output: {e.stderr}")
        
        print("\n💡 Alternative: Install manually with:")
        print("poetry add streamlit-ace streamlit-extras pygments")
        
    except FileNotFoundError:
        print("❌ Poetry not found. Please install Poetry first or use pip:")
        print("pip install streamlit-ace streamlit-extras pygments")

if __name__ == "__main__":
    install_with_poetry()