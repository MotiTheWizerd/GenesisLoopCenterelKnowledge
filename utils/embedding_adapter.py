from abc import ABC, abstractmethod
from typing import List
import os

try:
    import google.generativeai as genai
    GEMINI = True
except ImportError:
    GEMINI = False

from sentence_transformers import SentenceTransformer

class EmbeddingBackend(ABC):
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        pass

class MiniLMBackend(EmbeddingBackend):
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
    
    def embed(self, text: str) -> List[float]:
        return self.model.encode([text])[0]

class GeminiBackend(EmbeddingBackend):
    def __init__(self, api_key=None):
        if not GEMINI:
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
        self.backend = MiniLMBackend() if backend == "minilm" else GeminiBackend(gemini_api_key)
    
    def embed(self, text: str) -> List[float]:
        return self.backend.embed(text)