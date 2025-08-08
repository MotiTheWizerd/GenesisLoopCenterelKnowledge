#!/usr/bin/env python3
"""
Test the dashboard configuration to ensure paths are correct.
"""

import sys
from pathlib import Path

# Add the streamlit directory to path
sys.path.append(str(Path("ui/streamlit")))

try:
    from dashboard_config import config
    
    print("🧪 Testing Dashboard Configuration")
    print("=" * 50)
    
    debug_info = config.get_debug_info()
    
    print(f"📁 Project Root: {debug_info['project_root']}")
    print(f"📁 Current Working Dir: {debug_info['current_working_dir']}")
    print()
    
    print("📋 Path Status:")
    for name, info in debug_info["paths_exist"].items():
        status = "✅" if info["exists"] else "❌"
        print(f"{status} {name}: {info['path']}")
    
    print()
    print("📄 Memory Files Found:")
    memory_files = config.get_memory_files()
    if memory_files:
        for i, file_path in enumerate(memory_files[:10]):  # Show first 10
            print(f"  {i+1}. {file_path}")
        if len(memory_files) > 10:
            print(f"  ... and {len(memory_files) - 10} more files")
        print(f"\n✅ Total: {len(memory_files)} memory files found")
    else:
        print("❌ No memory files found")
    
    print("\n" + "=" * 50)
    print("🎯 Configuration test complete!")
    
except Exception as e:
    print(f"❌ Error testing configuration: {e}")
    import traceback
    traceback.print_exc()