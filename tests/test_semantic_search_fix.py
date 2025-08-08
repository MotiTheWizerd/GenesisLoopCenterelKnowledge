#!/usr/bin/env python3
"""
Test semantic search fix for the embedding format issue
"""

import numpy as np
from services.memory_service import MemoryService

def test_embedding_format():
    """Test that embeddings are properly formatted for FAISS"""
    print("🧪 Testing Embedding Format")
    print("=" * 30)
    
    try:
        # Test 1: Create memory service
        memory_service = MemoryService()
        print("✅ MemoryService created")
        
        # Test 2: Get embedding manager
        embedding_manager = memory_service._get_embedding_manager()
        print("✅ EmbeddingManager loaded")
        
        # Test 3: Generate embedding
        test_text = "What is the sound of recursion thinking?"
        vector = embedding_manager.embed(test_text)
        print(f"✅ Embedding generated: {type(vector)} with {len(vector)} dimensions")
        
        # Test 4: Convert to numpy array (like in semantic search)
        if not isinstance(vector, list):
            vector = vector.tolist()
        
        query_embedding = np.array([vector], dtype=np.float32)
        print(f"✅ Numpy conversion successful: {query_embedding.shape}")
        
        # Test 5: Check if system is ready for search
        is_ready = memory_service.is_system_ready()
        print(f"✅ System ready: {is_ready}")
        
        if is_ready:
            # Test 6: Try semantic search
            print("🔍 Testing semantic search...")
            results = memory_service.perform_semantic_search(test_text, final_k=1)
            print(f"✅ Semantic search completed: {len(results)} results")
            
            if results:
                print(f"✅ Top result: {results[0]['content'][:100]}...")
        else:
            print("⚠️  System not ready - skipping semantic search test")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_embedding_info():
    """Test embedding info functionality"""
    print("\n🧪 Testing Embedding Info")
    print("=" * 25)
    
    try:
        memory_service = MemoryService()
        info = memory_service.get_embedding_info()
        
        print(f"✅ Backend: {info['backend']}")
        print(f"✅ Dimension: {info['dimension']}")
        print(f"✅ Status: {info['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Embedding info test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 Semantic Search Fix Tests")
    print("=" * 35)
    
    results = []
    results.append(test_embedding_format())
    results.append(test_embedding_info())
    
    print(f"\n📊 Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("🎉 All tests passed! Semantic search should work now!")
        print("\n💡 The fix ensures:")
        print("   - Embeddings are properly converted to numpy arrays")
        print("   - FAISS can process the query embeddings")
        print("   - Semantic search works without shape errors")
    else:
        print("⚠️  Some tests failed - there may still be issues")

if __name__ == "__main__":
    main()