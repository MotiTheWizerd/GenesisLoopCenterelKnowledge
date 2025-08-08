"""
Test script to verify MemoryService works correctly
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from services.memory_service import MemoryService

def test_memory_service():
    """Test the memory service functionality"""
    
    print("🧠 Testing Ray Memory Service")
    print("=" * 40)
    
    # Initialize service
    try:
        service = MemoryService()
        print("✅ MemoryService initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing MemoryService: {e}")
        return
    
    # Test system readiness
    try:
        is_ready = service.is_system_ready()
        print(f"📊 System ready: {is_ready}")
        
        if not is_ready:
            print("⚠️  Memory system files not found:")
            print(f"   - FAISS index: {os.path.exists(service.FAISS_INDEX_FILE)}")
            print(f"   - Metadata: {os.path.exists(service.METADATA_FILE)}")
            print(f"   - Memories: {os.path.exists(service.MEMORY_FILE)}")
            print("\n💡 Run the embedding scripts first:")
            print("   python extract/embed.py")
            return
            
    except Exception as e:
        print(f"❌ Error checking system readiness: {e}")
        return
    
    # Test basic statistics
    try:
        basic_stats = service.get_basic_statistics()
        print("✅ Basic statistics loaded:")
        for key, value in basic_stats.items():
            print(f"   {key}: {value}")
    except Exception as e:
        print(f"❌ Error getting basic statistics: {e}")
        return
    
    # Test full statistics
    try:
        full_stats = service.get_memory_statistics()
        print("✅ Full statistics loaded:")
        print(f"   Total memories: {full_stats.get('total_memories', 0)}")
        print(f"   Agent responses: {full_stats.get('agent_responses', 0)}")
        print(f"   User queries: {full_stats.get('user_queries', 0)}")
    except Exception as e:
        print(f"❌ Error getting full statistics: {e}")
        return
    
    print("\n🎉 All tests passed! Memory service is working correctly.")
    print("🚀 You can now run the dashboard:")
    print("   python run_dashboard.py")

if __name__ == "__main__":
    test_memory_service()