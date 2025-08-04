# MemoryService API Reference

## Overview

The `MemoryService` class is the main interface for all memory operations in Ray's consciousness system. It provides semantic search, memory retrieval, statistics, and embedding management.

## Class: MemoryService

### Constructor

```python
MemoryService(backend="minilm", gemini_api_key=None)
```

**Parameters:**
- `backend` (str, optional): Embedding backend to use. Options: `"minilm"`, `"gemini"`. Default: `"minilm"`
- `gemini_api_key` (str, optional): API key for Gemini backend. Can also be set via `GEMINI_API_KEY` environment variable.

**Example:**
```python
# Default MiniLM backend
memory_service = MemoryService()

# Gemini backend with API key
memory_service = MemoryService(backend="gemini", gemini_api_key="your-key")

# Gemini backend with environment variable
import os
os.environ['GEMINI_API_KEY'] = "your-key"
memory_service = MemoryService(backend="gemini")
```

## System Status Methods

### is_system_ready()

Check if the memory system is ready for operations.

**Returns:** `bool`
- `True` if all required files exist (FAISS index, metadata, memories)
- `False` if any required files are missing

**Example:**
```python
if memory_service.is_system_ready():
    print("✅ Memory system online")
    # Proceed with operations
else:
    print("❌ System not ready - run setup first")
    # Run: python extract/embed.py
```

**Required Files:**
- `extract/faiss_index.bin` - Vector search index
- `extract/memory_metadata.json` - Memory metadata
- `extract/agent_memories.json` - Raw memory data

## Statistics Methods

### get_basic_statistics()

Get basic memory statistics quickly without loading heavy data.

**Returns:** `Dict[str, Any]`

**Response Format:**
```python
{
    'system_ready': bool,
    'total_memories': int,
    'agent_responses': int,
    'user_queries': int,
    'metadata_file_size': int,  # bytes
    'memory_file_size': int,    # bytes
    'faiss_index_size': int     # bytes
}
```

**Example:**
```python
stats = memory_service.get_basic_statistics()
print(f"System has {stats['total_memories']} memories")
print(f"Agent responses: {stats['agent_responses']}")
print(f"User queries: {stats['user_queries']}")
```

### get_memory_statistics()

Get comprehensive memory statistics (slower, loads full data).

**Returns:** `Dict[str, Any]`

**Response Format:**
```python
{
    'total_memories': int,
    'agent_responses': int,
    'user_queries': int,
    'system_ready': bool,
    'earliest_memory': str,      # ISO timestamp
    'latest_memory': str,        # ISO timestamp
    'total_content_length': int,
    'avg_content_length': float,
    'faiss_index_size': int,
    'metadata_entries': int,
    'is_sampled': bool          # True if analysis used sampling
}
```

**Example:**
```python
stats = memory_service.get_memory_statistics()
print(f"Memory span: {stats['earliest_memory']} to {stats['latest_memory']}")
print(f"Average content length: {stats['avg_content_length']} chars")
```

## Search Methods

### perform_semantic_search()

Perform semantic search with reranking across Ray's memories.

**Parameters:**
- `query` (str): Natural language search query
- `initial_k` (int, optional): Number of initial FAISS candidates. Default: 20
- `final_k` (int, optional): Number of final results after reranking. Default: 3

**Returns:** `List[Dict[str, Any]]`

**Response Format:**
```python
[
    {
        "id": str,              # Memory ID (e.g., "mem-123")
        "content": str,         # Memory content
        "source": str,          # "agent_response" or "user_input"
        "timestamp": float,     # Unix timestamp
        "faiss_score": float,   # FAISS similarity score
        "rerank_score": float,  # Cross-encoder rerank score
        "tags": List[str]       # Memory tags
    }
]
```

**Example:**
```python
# Basic search
results = memory_service.perform_semantic_search("What is consciousness?")

# Advanced search with more candidates and results
results = memory_service.perform_semantic_search(
    query="Ray's thoughts on self-awareness",
    initial_k=50,  # More FAISS candidates (better recall)
    final_k=10     # More final results
)

for result in results:
    print(f"Memory {result['id']}: {result['content'][:100]}...")
    print(f"Relevance score: {result['rerank_score']:.3f}")
```

**Search Process:**
1. Generate query embedding using current backend
2. FAISS vector search for `initial_k` candidates
3. Filter for agent responses (higher quality)
4. Cross-encoder reranking for semantic relevance
5. Return top `final_k` results sorted by rerank score

### get_memory_by_id()

Get a specific memory by its ID.

**Parameters:**
- `memory_id` (str): Memory identifier (e.g., "mem-6")

**Returns:** `Optional[Dict[str, Any]]`
- Memory dictionary if found
- `None` if not found

**Example:**
```python
memory = memory_service.get_memory_by_id("mem-6")
if memory:
    print(f"Content: {memory['content']}")
    print(f"Source: {memory['source']}")
    print(f"Timestamp: {memory['timestamp']}")
else:
    print("Memory not found")
```

### get_recent_memories()

Get the most recent memories by timestamp.

**Parameters:**
- `limit` (int, optional): Maximum number of memories to return. Default: 10

**Returns:** `List[Dict[str, Any]]`

**Example:**
```python
# Get last 10 memories
recent = memory_service.get_recent_memories()

# Get last 50 memories
recent = memory_service.get_recent_memories(limit=50)

for memory in recent:
    timestamp = datetime.fromtimestamp(memory['timestamp'])
    print(f"{timestamp}: {memory['content'][:50]}...")
```

### search_by_source()

Search memories by source type.

**Parameters:**
- `source` (str): Source type to filter by
  - `"agent_response"` - Ray's responses
  - `"user_input"` - User messages
- `limit` (int, optional): Maximum results. Default: 50

**Returns:** `List[Dict[str, Any]]`

**Example:**
```python
# Get Ray's responses
agent_memories = memory_service.search_by_source("agent_response", limit=100)

# Get user inputs
user_memories = memory_service.search_by_source("user_input", limit=100)

print(f"Found {len(agent_memories)} agent responses")
print(f"Found {len(user_memories)} user inputs")
```

## Embedding Methods

### get_embedding_info()

Get information about the current embedding backend.

**Returns:** `Dict[str, Any]`

**Response Format:**
```python
{
    'backend': str,      # "minilm" or "gemini"
    'dimension': int,    # 384 for MiniLM, 768 for Gemini
    'status': str        # "ready" or error message
}
```

**Example:**
```python
info = memory_service.get_embedding_info()
print(f"Using {info['backend']} backend")
print(f"Embedding dimension: {info['dimension']}")

if info['status'] != 'ready':
    print(f"Backend error: {info['status']}")
```

### switch_embedding_backend()

Switch to a different embedding backend.

**Parameters:**
- `backend` (str): New backend to use (`"minilm"` or `"gemini"`)
- `gemini_api_key` (str, optional): API key for Gemini backend

**Returns:** None

**Example:**
```python
# Switch to Gemini
memory_service.switch_embedding_backend("gemini", gemini_api_key="your-key")

# Switch back to MiniLM
memory_service.switch_embedding_backend("minilm")

# Verify switch
info = memory_service.get_embedding_info()
print(f"Now using: {info['backend']}")
```

**Note:** Switching backends may require regenerating the FAISS index if dimensions don't match.

## Utility Methods

### get_current_timestamp()

Get current timestamp as ISO string.

**Returns:** `str` - ISO format timestamp

**Example:**
```python
timestamp = memory_service.get_current_timestamp()
print(f"Current time: {timestamp}")
# Output: "2025-02-08T14:30:45.123456"
```

## Private Methods (Advanced Usage)

### _get_embedding_manager()

Get the current embedding manager instance.

**Returns:** `EmbeddingManager`

**Example:**
```python
# Generate embedding directly
manager = memory_service._get_embedding_manager()
vector = manager.embed("What is the sound of recursion thinking?")
print(f"Generated {len(vector)}-dimensional vector")
```

### _load_memories()

Load all memories from the JSON file (cached).

**Returns:** `List[Dict[str, Any]]`

**Example:**
```python
# Access raw memory data
memories = memory_service._load_memories()
print(f"Loaded {len(memories)} memories")

# Analyze memory patterns
for memory in memories[:5]:
    print(f"Source: {memory['source']}, Length: {len(memory['content'])}")
```

### _load_metadata()

Load memory metadata dictionary (cached).

**Returns:** `Dict[str, Any]`

**Example:**
```python
# Access metadata directly
metadata = memory_service._load_metadata()
print(f"Metadata entries: {len(metadata)}")

# Get specific memory metadata
mem_6 = metadata.get("mem-6")
if mem_6:
    print(f"Memory 6 content: {mem_6['content']}")
```

## Error Handling

### Common Exceptions

```python
try:
    memory_service = MemoryService(backend="gemini")
    results = memory_service.perform_semantic_search("test")
except ImportError as e:
    print(f"Missing dependency: {e}")
except ValueError as e:
    print(f"Configuration error: {e}")
except FileNotFoundError as e:
    print(f"Missing memory files: {e}")
    print("Run: python extract/embed.py")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Graceful Degradation

```python
# Check system readiness before operations
if not memory_service.is_system_ready():
    print("System not ready - using fallback behavior")
    # Implement fallback logic
    return

# Check embedding backend status
info = memory_service.get_embedding_info()
if info['status'] != 'ready':
    print(f"Embedding backend issue: {info['status']}")
    # Switch to fallback backend
    memory_service.switch_embedding_backend("minilm")
```

## Performance Considerations

### Memory Usage

```python
# For large memory sets, use basic statistics first
stats = memory_service.get_basic_statistics()
if stats['total_memories'] > 10000:
    print("Large memory set detected - using sampling")
    # Use sampling or pagination for analysis

# Load full statistics only when needed
if detailed_analysis_required:
    full_stats = memory_service.get_memory_statistics()
```

### Search Optimization

```python
# Adjust search parameters based on use case
if quick_lookup:
    # Fast search with fewer candidates
    results = memory_service.perform_semantic_search(query, initial_k=10, final_k=1)
elif comprehensive_search:
    # Thorough search with more candidates
    results = memory_service.perform_semantic_search(query, initial_k=100, final_k=20)
```

### Backend Selection

```python
# Choose backend based on requirements
if development_mode or offline_use:
    # Fast, local processing
    memory_service = MemoryService(backend="minilm")
elif production_mode and api_available:
    # High-quality embeddings
    memory_service = MemoryService(backend="gemini", gemini_api_key=api_key)
```

## Integration Examples

### With Streamlit Dashboard

```python
import streamlit as st
from services.memory_service import MemoryService

# Initialize in session state
if 'memory_service' not in st.session_state:
    st.session_state.memory_service = MemoryService()

# Use throughout the app
memory_service = st.session_state.memory_service
results = memory_service.perform_semantic_search(user_query)
```

### With Custom Analysis

```python
from services.memory_service import MemoryService
from collections import Counter

memory_service = MemoryService()

# Custom memory analysis
memories = memory_service._load_memories()
content_types = Counter()

for memory in memories:
    content = memory.get('content', '').lower()
    if len(content) < 50:
        content_types['short'] += 1
    elif 'filename' in content:
        content_types['file_reference'] += 1
    else:
        content_types['detailed'] += 1

print("Content distribution:", dict(content_types))
```

### Batch Processing

```python
def process_memories_in_batches(memory_service, batch_size=100):
    """Process memories in batches for memory efficiency"""
    memories = memory_service._load_memories()
    
    for i in range(0, len(memories), batch_size):
        batch = memories[i:i+batch_size]
        
        # Process batch
        for memory in batch:
            # Your processing logic here
            yield memory

# Usage
for memory in process_memories_in_batches(memory_service):
    # Process each memory
    pass
```

---

*Complete API reference for MemoryService class. For usage examples and guides, see MEMORY_SYSTEM_GUIDE.md*