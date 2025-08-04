"""
Memory Service - Business Logic Layer
Handles all memory operations and statistics
"""

import json
import os
import faiss
import time
import sys
import numpy as np
from datetime import datetime
from sentence_transformers import CrossEncoder
from typing import Dict, List, Optional, Any

# Add project root to path if not already there
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Also add the current directory to ensure relative imports work
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import local embedding manager
from .embedding_manager import EmbeddingManager

class MemoryService:
    """Service class for memory operations"""
    
    def __init__(self, backend="minilm", gemini_api_key=None):
        # Configuration
        self.RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
        self.FAISS_INDEX_FILE = "extract/faiss_index.bin"
        self.METADATA_FILE = "extract/memory_metadata.json"
        self.MEMORY_FILE = "extract/agent_memories.json"
        
        # Embedding configuration
        self.embedding_backend = backend
        self.gemini_api_key = gemini_api_key
        
        # Models (lazy loading)
        self._embedding_manager = None
        self._reranker_model = None
        self._faiss_index = None
        self._metadata = None
        self._memories = None
    
    def is_system_ready(self) -> bool:
        """Check if the memory system is ready"""
        return (
            os.path.exists(self.FAISS_INDEX_FILE) and 
            os.path.exists(self.METADATA_FILE) and
            os.path.exists(self.MEMORY_FILE)
        )
    
    def get_basic_statistics(self) -> Dict[str, Any]:
        """Get basic statistics quickly without loading heavy data"""
        if not self.is_system_ready():
            return {
                'system_ready': False,
                'total_memories': 0,
                'agent_responses': 0,
                'user_queries': 0
            }
        
        try:
            # Try to get quick file info first
            metadata_size = os.path.getsize(self.METADATA_FILE)
            memory_size = os.path.getsize(self.MEMORY_FILE)
            faiss_size = self._get_faiss_index_size()
            
            # If files are reasonable size, load basic counts
            if memory_size < 50 * 1024 * 1024:  # Less than 50MB
                memories = self._load_memories()
                agent_responses = sum(1 for mem in memories if mem.get('source') == 'agent_response')
                user_queries = sum(1 for mem in memories if mem.get('source') == 'user_input')
                
                return {
                    'system_ready': True,
                    'total_memories': len(memories),
                    'agent_responses': agent_responses,
                    'user_queries': user_queries,
                    'metadata_file_size': metadata_size,
                    'memory_file_size': memory_size,
                    'faiss_index_size': faiss_size
                }
            else:
                # For large files, just return file info
                return {
                    'system_ready': True,
                    'total_memories': "Large file - click to load",
                    'agent_responses': "Large file - click to load", 
                    'user_queries': "Large file - click to load",
                    'metadata_file_size': metadata_size,
                    'memory_file_size': memory_size,
                    'faiss_index_size': faiss_size
                }
                
        except Exception as e:
            print(f"Error getting basic statistics: {e}")
            return {
                'system_ready': False,
                'total_memories': 0,
                'agent_responses': 0,
                'user_queries': 0
            }
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics (slower, loads full data)"""
        if not self.is_system_ready():
            return {
                'total_memories': 0,
                'agent_responses': 0,
                'user_queries': 0,
                'system_ready': False
            }
        
        # Load data only when specifically requested
        memories = self._load_memories()
        
        # Count by source
        agent_responses = sum(1 for mem in memories if mem.get('source') == 'agent_response')
        user_queries = sum(1 for mem in memories if mem.get('source') == 'user_input')
        
        # Time range analysis (sample first 1000 for speed)
        sample_memories = memories[:1000] if len(memories) > 1000 else memories
        timestamps = [mem.get('timestamp', 0) for mem in sample_memories if mem.get('timestamp')]
        earliest = min(timestamps) if timestamps else 0
        latest = max(timestamps) if timestamps else 0
        
        # Content analysis (sample for speed)
        total_content_length = sum(len(mem.get('content', '')) for mem in sample_memories)
        avg_content_length = total_content_length / len(sample_memories) if sample_memories else 0
        
        return {
            'total_memories': len(memories),
            'agent_responses': agent_responses,
            'user_queries': user_queries,
            'system_ready': True,
            'earliest_memory': datetime.fromtimestamp(earliest).isoformat() if earliest else None,
            'latest_memory': datetime.fromtimestamp(latest).isoformat() if latest else None,
            'total_content_length': total_content_length,
            'avg_content_length': round(avg_content_length, 2),
            'faiss_index_size': self._get_faiss_index_size(),
            'metadata_entries': len(memories),
            'is_sampled': len(memories) > 1000
        }
    
    def perform_semantic_search(self, query: str, initial_k: int = 20, final_k: int = 3) -> List[Dict[str, Any]]:
        """Perform semantic search with reranking"""
        if not self.is_system_ready():
            return []
        
        try:
            # Load models and data
            embedding_manager = self._get_embedding_manager()
            reranker = self._get_reranker_model()
            index = self._get_faiss_index()
            metadata = self._load_metadata()
            
            # Generate query embedding
            query_vector = embedding_manager.embed(query)
            
            # Ensure query_vector is a list and convert to numpy array for FAISS
            if not isinstance(query_vector, list):
                query_vector = query_vector.tolist()
            
            query_embedding = np.array([query_vector], dtype=np.float32)
            
            # Initial FAISS search
            distances, indices = index.search(query_embedding, initial_k)
            
            # Collect initial results
            initial_results = []
            for rank, idx in enumerate(indices[0]):
                unique_id = f"mem-{int(idx)}"
                memory_entry = metadata.get(unique_id)
                if memory_entry:
                    initial_results.append({
                        "id": unique_id,
                        "content": memory_entry['content'],
                        "source": memory_entry['source'],
                        "timestamp": memory_entry.get('timestamp'),
                        "faiss_score": float(distances[0][rank]),
                        "tags": memory_entry.get('tags', [])
                    })
            
            # Filter agent responses
            agent_responses = [r for r in initial_results if r['source'] == 'agent_response']
            
            if not agent_responses:
                return initial_results[:final_k]  # Return best initial results if no agent responses
            
            # Rerank agent responses
            sentence_pairs = [[query, r['content']] for r in agent_responses]
            rerank_scores = reranker.predict(sentence_pairs)
            
            # Add rerank scores
            for i, score in enumerate(rerank_scores):
                agent_responses[i]['rerank_score'] = float(score)
            
            # Sort by rerank score
            sorted_results = sorted(agent_responses, key=lambda x: x['rerank_score'], reverse=True)
            
            return sorted_results[:final_k]
            
        except Exception as e:
            print(f"Error during semantic search: {e}")
            return []
    
    def get_memory_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get specific memory by ID"""
        metadata = self._load_metadata()
        return metadata.get(memory_id)
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent memories"""
        memories = self._load_memories()
        sorted_memories = sorted(memories, key=lambda x: x.get('timestamp', 0), reverse=True)
        return sorted_memories[:limit]
    
    def search_by_source(self, source: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search memories by source type"""
        memories = self._load_memories()
        filtered = [mem for mem in memories if mem.get('source') == source]
        return filtered[:limit]
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp as ISO string"""
        return datetime.now().isoformat()
    
    def switch_embedding_backend(self, backend: str, gemini_api_key: Optional[str] = None):
        """Switch embedding backend (minilm or gemini)"""
        self.embedding_backend = backend
        if gemini_api_key:
            self.gemini_api_key = gemini_api_key
        self._embedding_manager = None  # Force reload
        print(f"Switched to {backend} embedding backend")
    
    def get_embedding_info(self) -> Dict[str, Any]:
        """Get current embedding backend information"""
        try:
            manager = self._get_embedding_manager()
            # Test embedding to get dimension
            test_vector = manager.embed("test")
            return {
                'backend': self.embedding_backend,
                'dimension': len(test_vector),
                'status': 'ready'
            }
        except Exception as e:
            return {
                'backend': self.embedding_backend,
                'dimension': 0,
                'status': f'error: {str(e)}'
            }
    
    # Private methods
    def _get_embedding_manager(self):
        """Lazy load embedding manager"""
        if self._embedding_manager is None:
            self._embedding_manager = EmbeddingManager(
                backend=self.embedding_backend,
                gemini_api_key=self.gemini_api_key
            )
        return self._embedding_manager
    
    def _get_reranker_model(self):
        """Lazy load reranker model"""
        if self._reranker_model is None:
            self._reranker_model = CrossEncoder(self.RERANKER_MODEL_NAME)
        return self._reranker_model
    
    def _get_faiss_index(self):
        """Lazy load FAISS index"""
        if self._faiss_index is None:
            self._faiss_index = faiss.read_index(self.FAISS_INDEX_FILE)
        return self._faiss_index
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata with caching"""
        if self._metadata is None:
            print("Loading metadata...")
            with open(self.METADATA_FILE, 'r', encoding='utf-8') as f:
                self._metadata = json.load(f)
            print(f"Loaded {len(self._metadata)} metadata entries")
        return self._metadata
    
    def _load_memories(self) -> List[Dict[str, Any]]:
        """Load memories with caching"""
        if self._memories is None:
            print("Loading memories...")
            with open(self.MEMORY_FILE, 'r', encoding='utf-8') as f:
                self._memories = json.load(f)
            print(f"Loaded {len(self._memories)} memory entries")
        return self._memories
    
    def _get_faiss_index_size(self) -> int:
        """Get FAISS index file size in bytes"""
        try:
            return os.path.getsize(self.FAISS_INDEX_FILE)
        except:
            return 0