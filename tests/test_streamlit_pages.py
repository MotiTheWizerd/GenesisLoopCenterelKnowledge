#!/usr/bin/env python3
"""
Test script to validate all Streamlit pages can be imported without errors.
"""

import sys
from pathlib import Path
import importlib.util

def test_page(page_path):
    """Test if a page can be imported without syntax errors."""
    try:
        spec = importlib.util.spec_from_file_location("test_module", page_path)
        module = importlib.util.module_from_spec(spec)
        
        # Add the page directory to sys.path temporarily
        page_dir = page_path.parent
        if str(page_dir) not in sys.path:
            sys.path.insert(0, str(page_dir))
        
        # Try to load the module (this will catch syntax errors)
        spec.loader.exec_module(module)
        
        return True, "✅ OK"
    
    except SyntaxError as e:
        return False, f"❌ Syntax Error: {e}"
    except ImportError as e:
        return False, f"⚠️ Import Error: {e}"
    except Exception as e:
        return False, f"⚠️ Other Error: {e}"

def main():
    """Test all Streamlit pages."""
    
    print("🧪 Testing Streamlit Pages")
    print("=" * 50)
    
    # Find all Python files in the streamlit directory
    streamlit_dir = Path("ui/streamlit")
    
    if not streamlit_dir.exists():
        print("❌ Streamlit directory not found!")
        return 1
    
    # Test main menu
    main_menu = streamlit_dir / "main_menu.py"
    if main_menu.exists():
        success, message = test_page(main_menu)
        print(f"main_menu.py: {message}")
    
    # Test health dashboard
    health_dashboard = streamlit_dir / "health_dashboard.py"
    if health_dashboard.exists():
        success, message = test_page(health_dashboard)
        print(f"health_dashboard.py: {message}")
    
    # Test pages
    pages_dir = streamlit_dir / "pages"
    if pages_dir.exists():
        for page_file in sorted(pages_dir.glob("*.py")):
            success, message = test_page(page_file)
            print(f"pages/{page_file.name}: {message}")
    
    print("=" * 50)
    print("🏁 Testing complete!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())