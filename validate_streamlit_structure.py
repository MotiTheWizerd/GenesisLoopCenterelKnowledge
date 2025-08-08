#!/usr/bin/env python3
"""
Validate Streamlit structure and page references.
"""

from pathlib import Path
import re

def validate_structure():
    """Validate the Streamlit directory structure."""
    
    print("🔍 Validating Streamlit Structure")
    print("=" * 50)
    
    streamlit_dir = Path("ui/streamlit")
    pages_dir = streamlit_dir / "pages"
    
    # Check main directory
    if not streamlit_dir.exists():
        print("❌ ui/streamlit directory missing!")
        return False
    
    if not pages_dir.exists():
        print("❌ ui/streamlit/pages directory missing!")
        return False
    
    print("✅ Directory structure OK")
    
    # Check main menu exists
    main_menu = streamlit_dir / "main_menu.py"
    if not main_menu.exists():
        print("❌ main_menu.py missing!")
        return False
    
    print("✅ Main menu exists")
    
    # Read main menu and extract page references
    with open(main_menu, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all st.switch_page calls
    page_refs = re.findall(r'st\.switch_page\("([^"]+)"\)', content)
    
    print(f"\n📄 Found {len(page_refs)} page references:")
    
    all_valid = True
    for page_ref in page_refs:
        page_path = streamlit_dir / page_ref
        if page_path.exists():
            print(f"✅ {page_ref}")
        else:
            print(f"❌ {page_ref} - FILE MISSING!")
            all_valid = False
    
    # List actual pages in pages directory
    actual_pages = list(pages_dir.glob("*.py"))
    print(f"\n📁 Actual pages in pages/ directory ({len(actual_pages)}):")
    for page in sorted(actual_pages):
        print(f"   📄 {page.name}")
    
    # Check for orphaned pages (pages not referenced in main menu)
    referenced_pages = {Path(ref).name for ref in page_refs if ref.startswith("pages/")}
    actual_page_names = {page.name for page in actual_pages}
    
    orphaned = actual_page_names - referenced_pages
    if orphaned:
        print(f"\n⚠️ Orphaned pages (not referenced in main menu):")
        for page in sorted(orphaned):
            print(f"   📄 {page}")
    
    print("\n" + "=" * 50)
    
    if all_valid:
        print("✅ All page references are valid!")
        return True
    else:
        print("❌ Some page references are broken!")
        return False

if __name__ == "__main__":
    success = validate_structure()
    exit(0 if success else 1)