# Ray's Memory System - Usage Examples

## 🚀 Getting Started Examples

### 1. Basic Setup and First Search

```python
from services.memory_service import MemoryService

# Initialize memory service
memory_service = MemoryService()

# Check if system is ready
if not memory_service.is_system_ready():
    print("❌ System not ready. Run: python extract/embed.py")
    exit()

print("✅ Memory system online!")

# Get basic statistics
stats = memory_service.get_basic_statistics()
print(f"📊 System has {stats['total_memories']} memories")
print(f"🤖 Agent responses: {stats['agent_responses']}")
print(f"👤 User queries: {stats['user_queries']}")

# Perform your first semantic search
results = memory_service.perform_semantic_search("What is consciousness?")

print(f"\n🔍 Foun