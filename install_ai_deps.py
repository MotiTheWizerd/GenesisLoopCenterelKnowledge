#!/usr/bin/env python3
"""
Install AI dependencies for embedding search and learning features
"""

import subprocess
import sys
import os

def install_package_poetry(package):
    """Install a package using Poetry"""
    try:
        subprocess.check_call(["poetry", "add", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def install_package_pip(package):
    """Install a package using pip (fallback)"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    print("🤖 Installing AI dependencies for Ray's dashboard...")
    print("=" * 50)
    
    # Required packages for AI features
    ai_packages = [
        "sentence-transformers",
        "faiss-cpu",  # Use CPU version for compatibility
        "plotly",
        "pandas",
        "numpy",
        "chardet"  # For encoding detection
    ]
    
    success_count = 0
    total_packages = len(ai_packages)
    
    # Try Poetry first, fallback to pip
    use_poetry = True
    try:
        subprocess.check_call(["poetry", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("🎯 Using Poetry for package installation...")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Poetry not found, falling back to pip...")
        use_poetry = False
    
    for package in ai_packages:
        print(f"\n📦 Installing {package}...")
        if use_poetry:
            if install_package_poetry(package):
                success_count += 1
        else:
            if install_package_pip(package):
                success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Installation Summary: {success_count}/{total_packages} packages installed successfully")
    
    if success_count == total_packages:
        print("🎉 All AI dependencies installed successfully!")
        print("\n🚀 You can now use:")
        print("   • Embedding Search - Semantic search through Ray's memories")
        print("   • Learning & Planning - Analysis and planning dashboard")
    else:
        print("⚠️  Some packages failed to install. Please check the errors above.")
        print("💡 You may need to install them manually or check your Python environment.")
    
    print("\n🔧 To run the dashboard with new features:")
    print("   python launch_streamlit.py")

if __name__ == "__main__":
    main()