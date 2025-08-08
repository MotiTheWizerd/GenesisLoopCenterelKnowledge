#!/usr/bin/env python3
"""
Simple test to debug the import issue
"""

import sys
import os

print("🔍 Debugging Import Issue")
print("=" * 30)

print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Test 1: Check if files exist
print("\n📁 File Existence Check:")
files_to_check = [
    "utils/__init__.py",
    "utils/embedding_adapter.py",
    "services/memory_service.py"
]

for file_path in files_to_check:
    exists = os.path.exists(file_path)
    print(f"   {file_path}: {'✅' if exists else '❌'}")

# Test 2: Try direct import
print("\n🧪 Direct Import Test:")
try:
    import utils.embedding_adapter
    print("   ✅ utils.embedding_adapter imported successfully")
except Exception as e:
    print(f"   ❌ utils.embedding_adapter failed: {e}")

# Test 3: Try adding paths manually
print("\n🛠️  Manual Path Test:")
project_root = os.path.dirname(os.path.abspath(__file__))
utils_path = os.path.join(project_root, 'utils')

print(f"   Project root: {project_root}")
print(f"   Utils path: {utils_path}")
print(f"   Utils exists: {os.path.exists(utils_path)}")

if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print("   Added project root to path")

try:
    from utils.embedding_adapter import EmbeddingManager
    print("   ✅ EmbeddingManager imported after path fix")
    
    # Test creation
    manager = EmbeddingManager()
    print("   ✅ EmbeddingManager created successfully")
    
except Exception as e:
    print(f"   ❌ Still failed: {e}")

# Test 4: Try memory service import
print("\n🧠 Memory Service Test:")
try:
    from services.memory_service import MemoryService
    print("   ✅ MemoryService imported successfully")
    
    memory_service = MemoryService()
    print("   ✅ MemoryService created successfully")
    
except Exception as e:
    print(f"   ❌ MemoryService failed: {e}")
    import traceback
    traceback.print_exc()

print("\n🎯 Test Complete")