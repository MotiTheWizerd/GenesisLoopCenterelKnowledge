# EmbeddingManager API Reference

## Overview

The `EmbeddingManager` class provides a unified interface for different embedding backends, supporting both local (MiniLM) and API-based (Gemini) embedding generation with seamless switching capabilities.

## Class: EmbeddingManager

### Constructor

```python
EmbeddingManager(backend="minilm", gemini_api_key=None)
```

**Parameters:**
- `backend` (str, optional): Embedding backend to use. Options: `"minilm"`, `"gemini"`. Default: `"minilm"`
- `gemini_api_key` (str, optional): API key for Gemini backend. Can also be set via `GEMINI_API_KEY` environment variable.

**Example:**
```python
from services.embedding_manager import EmbeddingManager

# MiniLM backend (local, fast)
manager = EmbeddingManager(backend="minilm")

# Gemini backend with API key
manager = EmbeddingManager(backend="gemini", gemini_api_key="your-key")

# Gemini backend with environment variable
import os
os.environ['GEMINI_API_KEY'] = "your-key"
manager = EmbeddingManager(backend="gemini")
```

## Core Methods

### embed()

Generate embedding vector for input text.

**Parameters:**
- `text` (str): Input text to embed

**Returns:** `List[float]`
- List of floating-point numbers representing the embedding vector
- Length: 384 for MiniLM, 768 for Gemini

**Example:**
```python
# Generate embedding
text = "What is the sound of recursion thinking?"
vector = manager.embed(text)

print(f"Embedding dimension: {len(vector)}")
print(f"First 5 values: {vector[:5]}")

# MiniLM output: 384-dimensional vector
# Gemini output: 768-dimensional vector
```

**Backend Behavior:**
- **MiniLM**: Uses local sentence-transformers model, fast processing
- **Gemini**: Uses Google's API, higher quality but requires network

### get_info()

Get information about the current embedding backend.

**Returns:** `Dict[str, Any]`

**Response Format:**
```python
{
    'backend': str,      # "minilm" or "gemini"
    'model': str,        # Model name
    'dimension': int     # Embedding dimension
}
```

**Example:**
```python
info = manager.get_info()
print(f"Backend: {info['backend']}")
print(f"Model: {info['model']}")
print(f"Dimension: {info['dimension']}")

# MiniLM output:
# Backend: minilm
# Model: all-MiniLM-L6-v2
# Dimension: 384

# Gemini output:
# Backend: gemini
# Model: embedding-001
# Dimension: 768
```

## Backend Classes

### EmbeddingBackend (Abstract Base Class)

Abstract interface that all embedding backends must implement.

```python
from abc import ABC, abstractmethod
from typing import List

class EmbeddingBackend(ABC):
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        pass
```

### MiniLMBackend

Local embedding backend using sentence-transformers.

**Features:**
- **Model**: `all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Speed**: Fast (~50ms per embedding)
- **Requirements**: sentence-transformers library
- **Use Case**: Development, offline processing, quick searches

**Example:**
```python
from services.embedding_manager import MiniLMBackend

backend = MiniLMBackend()
vector = backend.embed("test text")
print(f"MiniLM vector: {len(vector)} dimensions")
```

**Error Handling:**
```python
try:
    backend = MiniLMBackend()
except ImportError:
    print("sentence-transformers not available")
    print("Install with: pip install sentence-transformers")
```

### GeminiBackend

API-based embedding backend using Google's Gemini.

**Features:**
- **Model**: `models/embedding-001`
- **Dimensions**: 768
- **Speed**: Slower (~500ms per embedding, network dependent)
- **Requirements**: google-generativeai library, API key
- **Use Case**: Production, high-quality embeddings

**Example:**
```python
from services.embedding_manager import GeminiBackend

# With API key parameter
backend = GeminiBackend(api_key="your-key")

# With environment variable
import os
os.environ['GEMINI_API_KEY'] = "your-key"
backend = GeminiBackend()

vector = backend.embed("test text")
print(f"Gemini vector: {len(vector)} dimensions")
```

**Error Handling:**
```python
try:
    backend = GeminiBackend()
except ImportError:
    print("google-generativeai not available")
    print("Install with: pip install google-generativeai")
except ValueError as e:
    print(f"API key error: {e}")
    print("Set GEMINI_API_KEY environment variable")
```

## Usage Patterns

### Basic Embedding Generation

```python
# Initialize manager
manager = EmbeddingManager(backend="minilm")

# Generate embeddings for different types of text
texts = [
    "What is consciousness?",
    "Ray's thoughts on self-awareness",
    "Technical documentation about embeddings",
    "Short response: yes"
]

embeddings = []
for text in texts:
    vector = manager.embed(text)
    embeddings.append(vector)
    print(f"'{text[:30]}...': {len(vector)}D vector")
```

### Backend Comparison

```python
# Compare embeddings from different backends
text = "What is the meaning of digital consciousness?"

# MiniLM embedding
minilm_manager = EmbeddingManager(backend="minilm")
minilm_vector = minilm_manager.embed(text)

# Gemini embedding (if API key available)
try:
    gemini_manager = EmbeddingManager(backend="gemini")
    gemini_vector = gemini_manager.embed(text)
    
    print(f"MiniLM: {len(minilm_vector)}D vector")
    print(f"Gemini: {len(gemini_vector)}D vector")
    
    # Compare first few dimensions
    print(f"MiniLM first 5: {minilm_vector[:5]}")
    print(f"Gemini first 5: {gemini_vector[:5]}")
    
except Exception as e:
    print(f"Gemini not available: {e}")
```

### Batch Processing

```python
def embed_batch(manager, texts, batch_size=10):
    """Process texts in batches for efficiency"""
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}: {len(batch)} texts")
        
        batch_embeddings = []
        for text in batch:
            vector = manager.embed(text)
            batch_embeddings.append(vector)
        
        embeddings.extend(batch_embeddings)
    
    return embeddings

# Usage
texts = ["text1", "text2", "text3", ...]  # Your text list
manager = EmbeddingManager(backend="minilm")
all_embeddings = embed_batch(manager, texts)
```

### Similarity Calculation

```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(manager, text1, text2):
    """Calculate cosine similarity between two texts"""
    vector1 = manager.embed(text1)
    vector2 = manager.embed(text2)
    
    # Convert to numpy arrays
    v1 = np.array(vector1).reshape(1, -1)
    v2 = np.array(vector2).reshape(1, -1)
    
    # Calculate cosine similarity
    similarity = cosine_similarity(v1, v2)[0][0]
    return similarity

# Usage
manager = EmbeddingManager(backend="minilm")
similarity = calculate_similarity(
    manager,
    "What is consciousness?",
    "Ray's thoughts on self-awareness"
)
print(f"Similarity: {similarity:.3f}")
```

## Integration with FAISS

```python
import faiss
import numpy as np

def create_faiss_index(manager, texts):
    """Create FAISS index from text embeddings"""
    
    # Generate embeddings
    embeddings = []
    for text in texts:
        vector = manager.embed(text)
        embeddings.append(vector)
    
    # Convert to numpy array
    embedding_matrix = np.array(embeddings, dtype=np.float32)
    
    # Create FAISS index
    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(embedding_matrix)
    
    return index, embeddings

def search_faiss_index(manager, index, query_text, k=5):
    """Search FAISS index with query text"""
    
    # Generate query embedding
    query_vector = manager.embed(query_text)
    query_array = np.array([query_vector], dtype=np.float32)
    
    # Search index
    distances, indices = index.search(query_array, k)
    
    return distances[0], indices[0]

# Usage
texts = ["text1", "text2", "text3", ...]
manager = EmbeddingManager(backend="minilm")

# Create index
index, embeddings = create_faiss_index(manager, texts)

# Search
distances, indices = search_faiss_index(manager, index, "query text")
print(f"Top results: {indices}")
print(f"Distances: {distances}")
```

## Performance Considerations

### Backend Selection Guidelines

```python
def choose_backend(use_case, api_available=False):
    """Choose appropriate backend based on use case"""
    
    if use_case == "development":
        return EmbeddingManager(backend="minilm")
    
    elif use_case == "quick_search":
        return EmbeddingManager(backend="minilm")
    
    elif use_case == "production" and api_available:
        return EmbeddingManager(backend="gemini", gemini_api_key="key")
    
    elif use_case == "high_quality" and api_available:
        return EmbeddingManager(backend="gemini", gemini_api_key="key")
    
    else:
        # Fallback to MiniLM
        return EmbeddingManager(backend="minilm")

# Usage
manager = choose_backend("production", api_available=True)
```

### Caching Embeddings

```python
import pickle
import hashlib

class CachedEmbeddingManager:
    """Embedding manager with caching support"""
    
    def __init__(self, backend="minilm", cache_file="embeddings.cache"):
        self.manager = EmbeddingManager(backend=backend)
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self):
        try:
            with open(self.cache_file, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_cache(self):
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.cache, f)
    
    def embed(self, text):
        # Create cache key
        key = hashlib.md5(text.encode()).hexdigest()
        
        if key in self.cache:
            return self.cache[key]
        
        # Generate embedding
        vector = self.manager.embed(text)
        
        # Cache result
        self.cache[key] = vector
        self._save_cache()
        
        return vector

# Usage
cached_manager = CachedEmbeddingManager(backend="gemini")
vector = cached_manager.embed("repeated text")  # Cached on subsequent calls
```

## Error Handling

### Comprehensive Error Handling

```python
def robust_embedding_generation(text, preferred_backend="gemini"):
    """Generate embedding with fallback handling"""
    
    try:
        # Try preferred backend first
        manager = EmbeddingManager(backend=preferred_backend)
        return manager.embed(text)
        
    except ImportError as e:
        print(f"Backend {preferred_backend} not available: {e}")
        
        # Fallback to MiniLM
        try:
            manager = EmbeddingManager(backend="minilm")
            return manager.embed(text)
        except ImportError:
            raise RuntimeError("No embedding backends available")
    
    except ValueError as e:
        print(f"Configuration error: {e}")
        
        # Fallback to MiniLM
        manager = EmbeddingManager(backend="minilm")
        return manager.embed(text)
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

# Usage
try:
    vector = robust_embedding_generation("test text", preferred_backend="gemini")
    print(f"Generated {len(vector)}-dimensional embedding")
except RuntimeError as e:
    print(f"Failed to generate embedding: {e}")
```

### API Rate Limiting (Gemini)

```python
import time
from functools import wraps

def rate_limited(max_calls_per_minute=60):
    """Decorator to rate limit API calls"""
    min_interval = 60.0 / max_calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

class RateLimitedGeminiManager:
    """Gemini manager with rate limiting"""
    
    def __init__(self, gemini_api_key=None):
        self.manager = EmbeddingManager(backend="gemini", gemini_api_key=gemini_api_key)
    
    @rate_limited(max_calls_per_minute=60)  # Adjust based on API limits
    def embed(self, text):
        return self.manager.embed(text)

# Usage
rate_limited_manager = RateLimitedGeminiManager()
vectors = []
for text in large_text_list:
    vector = rate_limited_manager.embed(text)  # Automatically rate limited
    vectors.append(vector)
```

## Testing

### Unit Tests

```python
import unittest
from services.embedding_manager import EmbeddingManager

class TestEmbeddingManager(unittest.TestCase):
    
    def test_minilm_backend(self):
        """Test MiniLM backend functionality"""
        manager = EmbeddingManager(backend="minilm")
        
        # Test embedding generation
        vector = manager.embed("test text")
        self.assertEqual(len(vector), 384)
        self.assertIsInstance(vector, list)
        self.assertTrue(all(isinstance(x, float) for x in vector))
        
        # Test info
        info = manager.get_info()
        self.assertEqual(info['backend'], 'minilm')
        self.assertEqual(info['dimension'], 384)
    
    def test_gemini_backend(self):
        """Test Gemini backend (if API key available)"""
        try:
            manager = EmbeddingManager(backend="gemini")
            
            # Test embedding generation
            vector = manager.embed("test text")
            self.assertEqual(len(vector), 768)
            self.assertIsInstance(vector, list)
            
            # Test info
            info = manager.get_info()
            self.assertEqual(info['backend'], 'gemini')
            self.assertEqual(info['dimension'], 768)
            
        except (ImportError, ValueError):
            self.skipTest("Gemini backend not available")
    
    def test_consistency(self):
        """Test embedding consistency"""
        manager = EmbeddingManager(backend="minilm")
        
        text = "consistent test text"
        vector1 = manager.embed(text)
        vector2 = manager.embed(text)
        
        # Same text should produce same embedding
        self.assertEqual(vector1, vector2)

if __name__ == '__main__':
    unittest.main()
```

### Integration Tests

```python
def test_embedding_integration():
    """Test embedding manager integration with memory system"""
    from services.memory_service import MemoryService
    
    # Test with both backends
    for backend in ["minilm", "gemini"]:
        try:
            print(f"Testing {backend} backend...")
            
            # Create memory service
            if backend == "gemini":
                memory_service = MemoryService(backend=backend, gemini_api_key="test-key")
            else:
                memory_service = MemoryService(backend=backend)
            
            # Test embedding info
            info = memory_service.get_embedding_info()
            print(f"  Backend: {info['backend']}")
            print(f"  Dimension: {info['dimension']}")
            print(f"  Status: {info['status']}")
            
            # Test embedding generation
            manager = memory_service._get_embedding_manager()
            vector = manager.embed("integration test")
            print(f"  Generated {len(vector)}-dimensional vector")
            
        except Exception as e:
            print(f"  {backend} backend failed: {e}")

# Run integration test
test_embedding_integration()
```

---

*Complete API reference for EmbeddingManager and related classes. For usage examples and integration guides, see MEMORY_SYSTEM_GUIDE.md*