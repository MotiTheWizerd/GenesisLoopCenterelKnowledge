#!/usr/bin/env python3
"""
Test script to validate memory pages work correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_memory_functions():
    """Test the memory page functions."""
    
    print("🧪 Testing Memory Page Functions")
    print("=" * 50)
    
    try:
        # Test memory explorer
        print("📁 Testing Memory Explorer...")
        sys.path.append(str(Path("ui/streamlit/pages")))
        
        from memory_explorer_tab import load_memory_files
        memory_files = load_memory_files()
        print(f"✅ Memory Explorer: Found {len(memory_files)} files")
        
        # Test memory analysis
        print("📊 Testing Memory Analysis...")
        from memory_analysis_tab import analyze_memory_metadata, analyze_memory_directory
        
        metadata = analyze_memory_metadata()
        if metadata:
            print("✅ Memory Analysis: Metadata loaded successfully")
        else:
            print("⚠️ Memory Analysis: No metadata found (this may be normal)")
        
        directory_analysis = analyze_memory_directory()
        if directory_analysis:
            print(f"✅ Memory Analysis: Found {directory_analysis['total_files']} files in {len(directory_analysis['memory_locations'])} locations")
        else:
            print("⚠️ Memory Analysis: No memory directories found")
        
        # Test memory management
        print("⚙️ Testing Memory Management...")
        from memory_management_tab import get_memory_stats
        
        stats = get_memory_stats()
        print(f"✅ Memory Management: Stats loaded - {stats['memory_files']} files, {stats['memory_size']/1024:.1f} KB")
        
        print("\n" + "=" * 50)
        print("✅ All memory page functions working correctly!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing memory functions: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_memory_functions()
    sys.exit(0 if success else 1)