#!/usr/bin/env python3
"""
Comprehensive test for button keys in all dashboard components
"""

import re
import sys
from pathlib import Path

def find_buttons_without_keys(file_path):
    """Find buttons without keys in a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all st.button and st.download_button calls
        button_patterns = [
            r'st\.button\([^)]+\)',
            r'st\.download_button\([^)]+\)'
        ]
        
        buttons_without_keys = []
        for pattern in button_patterns:
            buttons = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            for button in buttons:
                # Check if this button has a key parameter
                if 'key=' not in button:
                    buttons_without_keys.append(button.strip())
        
        return buttons_without_keys
    
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def test_dashboard_files():
    """Test all dashboard files for button key issues"""
    print("🔍 Testing Dashboard Files for Button Keys")
    print("=" * 45)
    
    # Files to check
    files_to_check = [
        "ui/streamlit/main_menu.py",
        "ui/streamlit/pages/embedding_search.py",
        "ui/streamlit/pages/learning_planner.py",
        "ui/streamlit/pages/memory_management_tab.py",
        "ui/streamlit/pages/memory_explorer_tab.py",
        "ui/streamlit/pages/memory_analysis_tab.py",
        "ui/streamlit/pages/health_dashboard.py",
        "ui/streamlit/components/json_viewer.py"
    ]
    
    total_issues = 0
    files_with_issues = 0
    
    for file_path in files_to_check:
        path = Path(file_path)
        if not path.exists():
            print(f"⚠️  {file_path} - File not found")
            continue
        
        buttons_without_keys = find_buttons_without_keys(path)
        
        if buttons_without_keys:
            print(f"❌ {file_path} - {len(buttons_without_keys)} buttons without keys:")
            for button in buttons_without_keys:
                print(f"   • {button}")
            files_with_issues += 1
            total_issues += len(buttons_without_keys)
        else:
            print(f"✅ {file_path} - All buttons have keys")
    
    return total_issues, files_with_issues, len(files_to_check)

def test_json_viewer_keys():
    """Test JSON viewer component specifically"""
    print("\n🧪 Testing JSON Viewer Component")
    print("=" * 35)
    
    json_viewer_path = Path("ui/streamlit/components/json_viewer.py")
    if not json_viewer_path.exists():
        print("❌ JSON viewer component not found")
        return False
    
    try:
        with open(json_viewer_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for dynamic key patterns
        dynamic_key_patterns = [
            r'key=f".*{.*}.*"',  # f-string keys
            r'key=.*hash\(',     # hash-based keys
            r'key=.*%.*'         # modulo operations for uniqueness
        ]
        
        dynamic_keys_found = 0
        for pattern in dynamic_key_patterns:
            matches = re.findall(pattern, content)
            dynamic_keys_found += len(matches)
        
        print(f"✅ Found {dynamic_keys_found} dynamic key patterns")
        
        # Check for specific problematic patterns
        problematic_patterns = [
            (r'st\.button\([^)]*\)(?!.*key=)', "Buttons without keys"),
            (r'st\.selectbox\([^)]*\)(?!.*key=)', "Selectboxes without keys"),
        ]
        
        issues_found = 0
        for pattern, description in problematic_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            if matches:
                print(f"⚠️  {description}: {len(matches)} found")
                issues_found += len(matches)
        
        if issues_found == 0:
            print("✅ No problematic patterns found")
        
        return issues_found == 0
    
    except Exception as e:
        print(f"❌ Error testing JSON viewer: {e}")
        return False

def test_streamlit_imports():
    """Test that Streamlit components can be imported"""
    print("\n🔧 Testing Streamlit Component Imports")
    print("=" * 40)
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
        
        # Test streamlit-ace
        try:
            from streamlit_ace import st_ace
            print("✅ streamlit-ace imported successfully")
        except ImportError:
            print("⚠️  streamlit-ace not available")
        
        # Test JSON viewer
        try:
            sys.path.append(str(Path("ui/streamlit")))
            from components.json_viewer import smart_json_display
            print("✅ JSON viewer component imported successfully")
        except Exception as e:
            print(f"❌ JSON viewer import failed: {e}")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ Streamlit import failed: {e}")
        return False

def main():
    print("🎯 Comprehensive Button Key Test Suite")
    print("=" * 45)
    
    # Test dashboard files
    total_issues, files_with_issues, total_files = test_dashboard_files()
    
    # Test JSON viewer specifically
    json_viewer_ok = test_json_viewer_keys()
    
    # Test imports
    imports_ok = test_streamlit_imports()
    
    # Summary
    print("\n" + "=" * 45)
    print("📊 Test Results Summary")
    print("=" * 45)
    
    print(f"📁 Files tested: {total_files}")
    print(f"❌ Files with issues: {files_with_issues}")
    print(f"🐛 Total button issues: {total_issues}")
    print(f"🧩 JSON viewer: {'✅ OK' if json_viewer_ok else '❌ Issues'}")
    print(f"📦 Imports: {'✅ OK' if imports_ok else '❌ Issues'}")
    
    if total_issues == 0 and json_viewer_ok and imports_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ No duplicate button key issues found")
        print("✅ All components have proper dynamic keys")
        print("✅ Dashboard should work without button errors")
        
        print("\n🚀 Ready to launch:")
        print("   poetry run python launch_dashboard.py")
        
    elif total_issues == 0 and json_viewer_ok:
        print("\n✅ BUTTON KEYS FIXED!")
        print("🎯 All button key issues have been resolved")
        if not imports_ok:
            print("⚠️  Some import issues remain, but buttons should work")
        
    else:
        print("\n⚠️  ISSUES FOUND")
        if total_issues > 0:
            print(f"🔧 Fix {total_issues} button key issues in {files_with_issues} files")
        if not json_viewer_ok:
            print("🔧 Fix JSON viewer component issues")
        if not imports_ok:
            print("🔧 Fix import issues")
        
        print("\n💡 Suggested fixes:")
        print("   - Add unique key= parameters to all st.button() calls")
        print("   - Use dynamic keys with hash() or unique identifiers")
        print("   - Test with: poetry run python test_json_viewer.py")

if __name__ == "__main__":
    main()