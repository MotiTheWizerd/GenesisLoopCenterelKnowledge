"""
Alternative installation script for Ray Memory Dashboard
Use this if Poetry dependency resolution fails
"""

import subprocess
import sys
import os

def install_with_pip():
    """Install dependencies using pip as fallback"""
    
    print("🔧 Installing Ray Memory Dashboard dependencies...")
    
    # Core dependencies
    dependencies = [
        "streamlit>=1.28.0",
        "plotly>=5.15.0", 
        "pandas>=1.5.0",
        "sentence-transformers>=2.2.0",
        "faiss-cpu>=1.7.4",
        "numpy>=1.21.0"
    ]
    
    try:
        for dep in dependencies:
            print(f"📦 Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
        
        print("✅ All dependencies installed successfully!")
        print("\n🚀 You can now run the dashboard:")
        print("   python run_dashboard.py")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print("\nTry installing manually:")
        for dep in dependencies:
            print(f"   pip install {dep}")

def install_with_poetry_simple():
    """Try Poetry with simplified dependencies"""
    
    print("🔧 Trying Poetry with simplified dependencies...")
    
    # Backup current pyproject.toml
    if os.path.exists("pyproject.toml"):
        os.rename("pyproject.toml", "pyproject.toml.backup")
    
    # Use simple version
    if os.path.exists("pyproject-simple.toml"):
        os.rename("pyproject-simple.toml", "pyproject.toml")
    
    try:
        subprocess.run(["poetry", "install"], check=True)
        print("✅ Poetry installation successful!")
        print("\n🚀 You can now run the dashboard:")
        print("   poetry run dashboard")
        
    except subprocess.CalledProcessError:
        print("❌ Poetry installation failed, falling back to pip...")
        
        # Restore original pyproject.toml
        if os.path.exists("pyproject.toml.backup"):
            os.rename("pyproject.toml.backup", "pyproject.toml")
        
        install_with_pip()

def main():
    """Main installation function"""
    
    print("🧠 Ray Memory Dashboard Installation")
    print("=" * 40)
    
    # Check if Poetry is available
    try:
        subprocess.run(["poetry", "--version"], check=True, capture_output=True)
        print("📦 Poetry detected, trying Poetry installation...")
        install_with_poetry_simple()
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📦 Poetry not found, using pip installation...")
        install_with_pip()

if __name__ == "__main__":
    main()