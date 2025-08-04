#!/usr/bin/env python3
"""
Environment Setup Script
Install dependencies for either the dashboard or API server
"""

import subprocess
import sys
import os

def install_dashboard_deps():
    """Install Streamlit dashboard dependencies"""
    print("📊 Installing Streamlit Dashboard Dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dashboard dependencies installed successfully!")
        print("🚀 You can now run: python run_dashboard_simple.py")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dashboard dependencies: {e}")
        return False

def install_api_deps():
    """Install FastAPI server dependencies"""
    print("🧠 Installing FastAPI Server Dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-api.txt"], check=True)
        print("✅ API server dependencies installed successfully!")
        print("🚀 You can now run: python run_api_server.py")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install API dependencies: {e}")
        return False

def install_minimal_api():
    """Install minimal FastAPI dependencies"""
    print("⚡ Installing Minimal FastAPI Dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn"], check=True)
        print("✅ Minimal API dependencies installed!")
        print("🚀 You can now run: python run_api_server.py")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install minimal API dependencies: {e}")
        return False

def main():
    """Main setup interface"""
    print("🔧 Ray's Environment Setup")
    print("=" * 40)
    print("Choose what you want to run:")
    print()
    print("1. 📊 Streamlit Dashboard (Memory Analysis, Timeline, etc.)")
    print("2. 🧠 FastAPI Server (Ray's Consciousness API)")
    print("3. ⚡ Minimal FastAPI (Just FastAPI + Uvicorn)")
    print("4. 🎯 Both (Dashboard + API)")
    print("5. ❌ Exit")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == "1":
                install_dashboard_deps()
                break
            elif choice == "2":
                install_api_deps()
                break
            elif choice == "3":
                install_minimal_api()
                break
            elif choice == "4":
                print("🎯 Installing both dashboard and API dependencies...")
                success1 = install_dashboard_deps()
                success2 = install_api_deps()
                if success1 and success2:
                    print("🎉 All dependencies installed!")
                    print("🚀 Dashboard: python run_dashboard_simple.py")
                    print("🚀 API Server: python run_api_server.py")
                break
            elif choice == "5":
                print("👋 Setup cancelled")
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")
        except KeyboardInterrupt:
            print("\n👋 Setup cancelled")
            break

if __name__ == "__main__":
    main()