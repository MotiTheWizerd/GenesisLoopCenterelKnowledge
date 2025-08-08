#!/usr/bin/env python3
"""
Test dashboard imports to verify the fix works
"""

import sys
import os

def test_imports():
    """Test that all dashboard imports work"""
    print("🧪 Testing Dashboard Imports")
    print("=" * 40)
    
    try:
        # Test 1: Direct memory service import
        print("1. Testing memory service import...")
        from services.memory_service import MemoryService
        print("   ✅ MemoryService imported")
        
        # Test 2: Memory service creation
        print("2. Testing memory service creation...")
        memory_service = MemoryService()
        print("   ✅ MemoryService created")
        
        # Test 3: Embedding info
        print("3. Testing embedding info...")
        info = memory_service.get_embedding_info()
        print(f"   ✅ Backend: {info['backend']}")
        print(f"   ✅ Status: {info['status']}")
        
        # Test 4: Session state import
        print("4. Testing session state import...")
        from ui.dashboard.utils.session_state import initialize_session_state
        print("   ✅ Session state imported")
        
        # Test 5: Statistics tab import
        print("5. Testing statistics tab import...")
        from ui.dashboard.components.statistics_tab import render_statistics_tab
        print("   ✅ Statistics tab imported")
        
        # Test 6: Memory analysis tab import
        print("6. Testing memory analysis tab import...")
        from ui.dashboard.components.memory_analysis_tab import render_memory_analysis_tab
        print("   ✅ Memory analysis tab imported")
        
        # Test 7: Main dashboard import
        print("7. Testing main dashboard import...")
        from ui.dashboard.main import main
        print("   ✅ Main dashboard imported")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_from_dashboard_directory():
    """Test imports from dashboard directory context"""
    print("\n🧪 Testing from Dashboard Directory Context")
    print("=" * 50)
    
    # Change to dashboard directory
    original_cwd = os.getcwd()
    dashboard_path = os.path.join(os.path.dirname(__file__), 'ui', 'dashboard')
    
    try:
        os.chdir(dashboard_path)
        print(f"Changed to: {os.getcwd()}")
        
        # Test imports from this context
        from utils.session_state import initialize_session_state
        print("✅ Session state imported from dashboard context")
        
        # Restore directory
        os.chdir(original_cwd)
        return True
        
    except Exception as e:
        print(f"❌ Dashboard context test failed: {e}")
        os.chdir(original_cwd)  # Restore even on failure
        return False

def main():
    """Run all import tests"""
    print("🚀 Dashboard Import Tests")
    print("=" * 30)
    
    results = []
    results.append(test_imports())
    results.append(test_from_dashboard_directory())
    
    print(f"\n📊 Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("🎉 All tests passed! Dashboard should work now!")
        print("\n🚀 Try running: python run_dashboard.py")
    else:
        print("⚠️  Some tests failed - there may still be import issues")

if __name__ == "__main__":
    main()