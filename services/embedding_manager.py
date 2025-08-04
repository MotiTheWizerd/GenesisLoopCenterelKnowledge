"""
Embedding Manager - Local to services directory
Handles embedding operations with fallback support
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import List

# Try to import optional dependencies
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

class EmbeddingBackend(ABC):
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        pass

class MiniLMBackend(EmbeddingBackend):
    def __init__(self):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers not available")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
    
    def embed(self, text: str) -> List[float]:
        return self.model.encode([text])[0].tolist()

class GeminiBackend(EmbeddingBackend):
    def __init__(self, api_key=None):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai not installed")
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("No Gemini API key")
        genai.configure(api_key=self.api_key)
    
    def embed(self, text: str) -> List[float]:
        return genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="RETRIEVAL_DOCUMENT"
        )['embedding']

class EmbeddingManager:
    def __init__(self, backend="minilm", gemini_api_key=None):
        self.backend_name = backend
        
        if backend == "minilm":
            self.backend = MiniLMBackend()
        elif backend == "gemini":
            self.backend = GeminiBackend(gemini_api_key)
        else:
            raise ValueError(f"Unknown backend: {backend}")
    
    def embed(self, text: str) -> List[float]:
        return self.backend.embed(text)
    
    def get_info(self):
        """Get backend information"""
        if self.backend_name == "minilm":
            return {
                'backend': 'minilm',
                'model': 'all-MiniLM-L6-v2',
                'dimension': 384
            }
        elif self.backend_name == "gemini":
            return {
                'backend': 'gemini', 
                'model': 'embedding-001',
                'dimension': 768
            }
        else:
            return {'backend': 'unknown'}