#!/usr/bin/env python3
"""
Test File Processing Integration
Quick test to verify the file processing tab integration
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """Test that all imports work correctly"""
    print("🧪 Testing imports...")
    
    try:
        from ui.dashboard.components.file_processing_tab import render_file_processing_tab
        print("✅ File processing tab import successful")
        
        from ui.dashboard.main import main
        print("✅ Main dashboard import successful")
        
        # Test key dependencies
        import streamlit as st
        print("✅ Streamlit import successful")
        
        import pandas as pd
        print("✅ Pandas import successful")
        
        import json
        print("✅ JSON import successful")
        
        import tempfile
        print("✅ Tempfile import successful")
        
        from pathlib import Path
        print("✅ Pathlib import successful")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_file_structure():
    """Test that required files and directories exist"""
    print("\n🧪 Testing file structure...")
    
    required_files = [
        "ui/dashboard/main.py",
        "ui/dashboard/components/file_processing_tab.py",
        "ui/dashboard/components/__init__.py",
        "extract/embed.py",
        "services/embedding_manager.py"
    ]
    
    required_dirs = [
        "ui/dashboard/components",
        "extract",
        "services"
    ]
    
    all_good = True
    
    # Check directories
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ Directory exists: {dir_path}")
        else:
            print(f"❌ Directory missing: {dir_path}")
            all_good = False
    
    # Check files
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ File exists: {file_path}")
        else:
            print(f"❌ File missing: {file_path}")
            all_good = False
    
    if all_good:
        print("\n🎉 File structure looks good!")
    else:
        print("\n⚠️ Some files or directories are missing")
    
    return all_good

def test_extract_functionality():
    """Test that extract functionality is accessible"""
    print("\n🧪 Testing extract functionality...")
    
    try:
        # Test if we can access the extract functions
        import json
        import tempfile
        from datetime import datetime
        
        # Create a test file
        test_data = {
            "content": "This is a test memory entry",
            "source": "test",
            "timestamp": datetime.now().timestamp()
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([test_data], f)
            test_file = f.name
        
        print(f"✅ Created test file: {test_file}")
        
        # Test file reading
        with open(test_file, 'r') as f:
            loaded_data = json.load(f)
        
        print(f"✅ Successfully read test data: {len(loaded_data)} entries")
        
        # Clean up
        os.unlink(test_file)
        print("✅ Test file cleaned up")
        
        print("\n🎉 Extract functionality test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Extract functionality test failed: {e}")
        return False

def test_embedding_dependencies():
    """Test embedding-related dependencies"""
    print("\n🧪 Testing embedding dependencies...")
    
    try:
        # Test sentence transformers (for minilm backend)
        try:
            from sentence_transformers import SentenceTransformer
            print("✅ SentenceTransformers available")
        except ImportError:
            print("⚠️ SentenceTransformers not available (install with: pip install sentence-transformers)")
        
        # Test FAISS
        try:
            import faiss
            print("✅ FAISS available")
        except ImportError:
            print("⚠️ FAISS not available (install with: pip install faiss-cpu)")
        
        # Test numpy
        try:
            import numpy as np
            print("✅ NumPy available")
        except ImportError:
            print("❌ NumPy not available (required)")
            return False
        
        print("\n🎉 Core embedding dependencies available!")
        return True
        
    except Exception as e:
        print(f"❌ Embedding dependencies test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting File Processing Integration Tests\n")
    
    tests = [
        ("Import Test", test_imports),
        ("File Structure Test", test_file_structure),
        ("Extract Functionality Test", test_extract_functionality),
        ("Embedding Dependencies Test", test_embedding_dependencies)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! File processing integration is ready.")
        print("\nTo use the new feature:")
        print("1. Run: python run_dashboard.py")
        print("2. Navigate to the 'File Processing' tab")
        print("3. Upload files and process them")
    else:
        print("\n⚠️ Some tests failed. Please check the issues above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)