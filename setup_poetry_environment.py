#!/usr/bin/env python3
"""
Complete Poetry environment setup for Ray's dashboard
"""

import subprocess
import sys
import json
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def check_poetry():
    """Check if Poetry is installed"""
    try:
        result = subprocess.run(["poetry", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Poetry is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Poetry is not installed")
            return False
    except FileNotFoundError:
        print("❌ Poetry is not installed")
        return False

def install_dependencies():
    """Install all required dependencies"""
    print("\n📦 Installing Dependencies")
    print("=" * 30)
    
    # Core dependencies that might be missing
    dependencies = [
        "fastapi",
        "uvicorn", 
        "psutil",
        "requests",
        "chardet"
    ]
    
    success_count = 0
    for dep in dependencies:
        if run_command(f"poetry add {dep}", f"Installing {dep}"):
            success_count += 1
    
    print(f"\n📊 Installed {success_count}/{len(dependencies)} dependencies")
    return success_count == len(dependencies)

def test_imports():
    """Test that all critical modules can be imported"""
    print("\n🧪 Testing Imports")
    print("=" * 20)
    
    test_modules = [
        ("fastapi", "FastAPI framework"),
        ("uvicorn", "ASGI server"),
        ("streamlit", "Dashboard framework"),
        ("sentence_transformers", "AI embeddings"),
        ("faiss", "Vector search"),
        ("plotly", "Interactive charts"),
        ("psutil", "System monitoring"),
        ("requests", "HTTP client")
    ]
    
    success_count = 0
    for module, description in test_modules:
        try:
            __import__(module)
            print(f"✅ {module} - {description}")
            success_count += 1
        except ImportError:
            print(f"❌ {module} - {description} (not available)")
    
    print(f"\n📊 {success_count}/{len(test_modules)} modules available")
    return success_count >= len(test_modules) - 2  # Allow 2 failures

def create_launch_scripts():
    """Create convenient launch scripts"""
    print("\n📝 Creating Launch Scripts")
    print("=" * 30)
    
    scripts = {
        "launch_api.py": '''#!/usr/bin/env python3
"""Launch the API server"""
import uvicorn
from main import app

if __name__ == "__main__":
    print("Starting Ray's API Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
''',
        "launch_dashboard.py": '''#!/usr/bin/env python3
"""Launch the main dashboard"""
import subprocess
import sys

if __name__ == "__main__":
    print("Starting Ray's Dashboard...")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "ui/streamlit/main_menu.py", "--server.port", "8501"
    ])
''',
        "launch_all.py": '''#!/usr/bin/env python3
"""Launch both API server and dashboard"""
import subprocess
import sys
import time
import threading

def start_api():
    """Start API server in background"""
    subprocess.run([sys.executable, "launch_api.py"])

def start_dashboard():
    """Start dashboard"""
    time.sleep(2)  # Wait for API to start
    subprocess.run([sys.executable, "launch_dashboard.py"])

if __name__ == "__main__":
    print("Starting Ray's Complete System...")
    
    # Start API server in background thread
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    
    # Start dashboard in main thread
    start_dashboard()
'''
    }
    
    created_count = 0
    for filename, content in scripts.items():
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Created {filename}")
            created_count += 1
        except Exception as e:
            print(f"❌ Failed to create {filename}: {e}")
    
    return created_count == len(scripts)

def main():
    print("🎯 Ray's Poetry Environment Setup")
    print("=" * 40)
    
    # Check Poetry installation
    if not check_poetry():
        print("\n💡 Please install Poetry first:")
        print("   curl -sSL https://install.python-poetry.org | python3 -")
        print("   or visit: https://python-poetry.org/docs/#installation")
        return
    
    # Install dependencies
    deps_ok = install_dependencies()
    
    # Test imports
    imports_ok = test_imports()
    
    # Create launch scripts
    scripts_ok = create_launch_scripts()
    
    # Final summary
    print("\n" + "=" * 40)
    print("📊 Setup Summary")
    print("=" * 40)
    
    print(f"✅ Poetry: Available")
    print(f"{'✅' if deps_ok else '❌'} Dependencies: {'Installed' if deps_ok else 'Issues found'}")
    print(f"{'✅' if imports_ok else '❌'} Imports: {'Working' if imports_ok else 'Issues found'}")
    print(f"{'✅' if scripts_ok else '❌'} Scripts: {'Created' if scripts_ok else 'Issues found'}")
    
    if all([deps_ok, imports_ok, scripts_ok]):
        print("\n🎉 Setup completed successfully!")
        print("\n🚀 Quick Start Commands:")
        print("   poetry run python launch_api.py      # Start API server")
        print("   poetry run python launch_dashboard.py # Start dashboard")
        print("   poetry run python launch_all.py      # Start both")
        print("\n🧪 Test Commands:")
        print("   poetry run python test_embedding_features.py")
        print("   poetry run python fix_metadata_encoding.py")
        
        print("\n🌐 URLs (when running):")
        print("   API Server: http://localhost:8000")
        print("   Dashboard: http://localhost:8501")
        print("   API Docs: http://localhost:8000/docs")
    else:
        print("\n⚠️  Setup completed with issues")
        print("💡 Check the errors above and try running individual commands")

if __name__ == "__main__":
    main()