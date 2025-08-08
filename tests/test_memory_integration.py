#!/usr/bin/env python3
"""
Test the memory service integration with the new embedding adapter
"""

import os
from services.memory_service import MemoryService

def test_minilm_integration():
    """Test MiniLM backend integration"""
    print("🧪 Testing MiniLM Integration")
    print("-" * 35)
    
    try:
        # Create memory service with MiniLM (default)
        memory_service = MemoryService(backend="minilm")
        print("✅ MemoryService created with MiniLM backend")
        
        # Get embedding info
        info = memory_service.get_embedding_info()
        print(f"✅ Backend: {info['backend']}")
        print(f"✅ Dimension: {info['dimension']}")
        print(f"✅ Status: {info['status']}")
        
        # Test system readiness
        is_ready = memory_service.is_system_ready()
        print(f"✅ System ready: {is_ready}")
        
        return True
        
    except Exception as e:
        print(f"❌ MiniLM integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gemini_integration():
    """Test Gemini backend integration"""
    print("\n🧪 Testing Gemini Integration")
    print("-" * 35)
    
    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("⚠️  GEMINI_API_KEY not set - skipping Gemini test")
        print("   Set environment variable: export GEMINI_API_KEY='AIzaSyB9T0S4iI4lRYfSDiYXvwsfE_-VqVbvfEI'")
        return False
    
    try:
        # Create memory service with Gemini
        memory_service = MemoryService(backend="gemini", gemini_api_key=api_key)
        print("✅ MemoryService created with Gemini backend")
        
        # Get embedding info
        info = memory_service.get_embedding_info()
        print(f"✅ Backend: {info['backend']}")
        print(f"✅ Dimension: {info['dimension']}")
        print(f"✅ Status: {info['status']}")
        
        # Test system readiness
        is_ready = memory_service.is_system_ready()
        print(f"✅ System ready: {is_ready}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_switching():
    """Test switching between backends"""
    print("\n🧪 Testing Backend Switching")
    print("-" * 35)
    
    try:
        # Start with MiniLM
        memory_service = MemoryService(backend="minilm")
        info1 = memory_service.get_embedding_info()
        print(f"✅ Started with: {info1['backend']} ({info1['dimension']}D)")
        
        # Test switching (even without API key, should show error gracefully)
        memory_service.switch_embedding_backend("gemini")
        info2 = memory_service.get_embedding_info()
        print(f"✅ Switched to: {info2['backend']} - Status: {info2['status']}")
        
        # Switch back to MiniLM
        memory_service.switch_embedding_backend("minilm")
        info3 = memory_service.get_embedding_info()
        print(f"✅ Switched back to: {info3['backend']} ({info3['dimension']}D)")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend switching failed: {e}")
        return False

def test_embedding_example():
    """Test the exact example from your specification"""
    print("\n🧪 Testing Your Example")
    print("-" * 25)
    
    try:
        # Your example with MiniLM first
        memory_service = MemoryService(backend="minilm")
        
        # Test the philosophical question
        if memory_service.is_system_ready():
            results = memory_service.perform_semantic_search(
                "What is the sound of recursion thinking?", 
                final_k=1
            )
            print(f"✅ Search completed - found {len(results)} results")
            if results:
                print(f"✅ Top result: {results[0]['content'][:100]}...")
        else:
            print("⚠️  Memory system not ready (missing FAISS index)")
            # Just test embedding generation
            manager = memory_service._get_embedding_manager()
            vector = manager.embed("What is the sound of recursion thinking?")
            print(f"✅ Generated embedding: {len(vector)} dimensions")
        
        return True
        
    except Exception as e:
        print(f"❌ Example test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Memory Service Integration Tests")
    print("=" * 50)
    
    results = []
    results.append(test_minilm_integration())
    results.append(test_gemini_integration())
    results.append(test_backend_switching())
    results.append(test_embedding_example())
    
    print(f"\n📊 Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("🎉 All tests passed! Integration complete!")
    else:
        print("⚠️  Some tests failed or were skipped")
    
    print("\n💡 Usage Examples:")
    print("   # Use MiniLM (default)")
    print("   memory_service = MemoryService()")
    print("   ")
    print("   # Use Gemini with API key")
    print("   memory_service = MemoryService(backend='gemini', gemini_api_key='your-key')")
    print("   ")
    print("   # Use Gemini with env variable")
    print("   # export GEMINI_API_KEY='your-key'")
    print("   memory_service = MemoryService(backend='gemini')")

if __name__ == "__main__":
    main()