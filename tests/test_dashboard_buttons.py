#!/usr/bin/env python3
"""
Test script to verify dashboard buttons work without duplicate key errors
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_button_keys():
    """Test that all buttons have unique keys"""
    print("🔍 Testing button keys in dashboard pages...")
    
    # Test embedding search page
    embedding_file = Path("ui/streamlit/pages/embedding_search.py")
    if embedding_file.exists():
        with open(embedding_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for button keys
        button_keys = []
        lines = content.split('\n')
        for line in lines:
            if 'st.button(' in line and 'key=' in line:
                # Extract key value
                key_start = line.find('key="') + 5
                key_end = line.find('"', key_start)
                if key_start > 4 and key_end > key_start:
                    key = line[key_start:key_end]
                    button_keys.append(key)
        
        print(f"✅ Embedding search page: Found {len(button_keys)} buttons with keys")
        for key in button_keys:
            print(f"   - {key}")
        
        # Check for duplicates
        if len(button_keys) == len(set(button_keys)):
            print("✅ All button keys are unique")
        else:
            print("❌ Duplicate button keys found!")
            return False
    
    # Test learning planner page
    learning_file = Path("ui/streamlit/pages/learning_planner.py")
    if learning_file.exists():
        with open(learning_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for button keys
        button_keys = []
        lines = content.split('\n')
        for line in lines:
            if 'st.button(' in line and 'key=' in line:
                # Extract key value
                key_start = line.find('key="') + 5
                key_end = line.find('"', key_start)
                if key_start > 4 and key_end > key_start:
                    key = line[key_start:key_end]
                    button_keys.append(key)
        
        print(f"✅ Learning planner page: Found {len(button_keys)} buttons with keys")
        for key in button_keys:
            print(f"   - {key}")
        
        # Check for duplicates
        if len(button_keys) == len(set(button_keys)):
            print("✅ All button keys are unique")
        else:
            print("❌ Duplicate button keys found!")
            return False
    
    return True

def test_imports():
    """Test that pages can be imported without errors"""
    print("\n🔍 Testing page imports...")
    
    try:
        # Test dashboard config
        sys.path.append(str(Path("ui/streamlit")))
        from dashboard_config import config
        print("✅ Dashboard config imported successfully")
        
        # Test JSON viewer component
        from components.json_viewer import smart_json_display
        print("✅ JSON viewer component imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    print("🧠 Dashboard Button Test Suite")
    print("=" * 40)
    
    tests = [
        ("Button Keys", test_button_keys),
        ("Page Imports", test_imports)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results Summary:")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Dashboard should work without button errors.")
        print("\n🚀 To launch the dashboard:")
        print("   python launch_streamlit.py")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    main()