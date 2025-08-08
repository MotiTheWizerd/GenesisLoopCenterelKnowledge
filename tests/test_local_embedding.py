#!/usr/bin/env python3
"""
Test the local embedding manager
"""

import sys
import os

print("🧪 Testing Local Embedding Manager")
print("=" * 40)

try:
    # Test 1: Import local embedding manager
    from services.embedding_manager import EmbeddingManager
    print("✅ Local EmbeddingManager imported")
    
    # Test 2: Create manager
    manager = EmbeddingManager(backend="minilm")
    print("✅ EmbeddingManager created")
    
    # Test 3: Get info
    info = manager.get_info()
    print(f"✅ Backend info: {info}")
    
    # Test 4: Generate embedding
    vector = manager.embed("test text")
    print(f"✅ Embedding generated: {len(vector)} dimensions")
    
    # Test 5: Import memory service
    from services.memory_service import MemoryService
    print("✅ MemoryService imported")
    
    # Test 6: Create memory service
    memory_service = MemoryService()
    print("✅ MemoryService created")
    
    # Test 7: Get embedding info
    info = memory_service.get_embedding_info()
    print(f"✅ Memory service embedding info: {info}")
    
    print("\n🎉 All tests passed!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n🎯 Test complete")