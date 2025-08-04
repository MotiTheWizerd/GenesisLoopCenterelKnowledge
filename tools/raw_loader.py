#!/usr/bin/env python3
"""
Raw Memory Loader
Ingests .txt or .jsonl files, embeds with Gemini, and saves in system format
"""

import json
import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Any

# Try to import numpy and faiss with error handling
try:
    import numpy as np
    import faiss
    NUMPY_AVAILABLE = True
except ImportError as e:
    print(f"Warning: {e}")
    print("Please install missing dependencies: poetry install")
    NUMPY_AVAILABLE = False

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from services.embedding_manager import EmbeddingManager

class RawMemoryLoader:
    """Load and process raw memory files"""
    
    def __init__(self, embedding_backend="gemini", gemini_api_key=None):
        self.embedding_backend = embedding_backend
        self.gemini_api_key = gemini_api_key
        self.embedding_manager = None
        
        # Output paths
        self.memory_file = "extract/agent_memories.json"
        self.metadata_file = "extract/memory_metadata.json"
        self.faiss_file = "extract/faiss_index.bin"
    
    def _get_embedding_manager(self):
        """Get embedding manager"""
        if self.embedding_manager is None:
            self.embedding_manager = EmbeddingManager(
                backend=self.embedding_backend,
                gemini_api_key=self.gemini_api_key
            )
        return self.embedding_manager
    
    def load_txt_file(self, file_path: str, chunk_size: int = 1000) -> List[Dict[str, Any]]:
        """Load and chunk a .txt file"""
        print(f"📄 Loading .txt file: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple chunking by character count
        chunks = []
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            if chunk.strip():
                chunks.append({
                    'content': chunk.strip(),
                    'source': 'txt_import',
                    'timestamp': datetime.now().timestamp(),
                    'type': 'memory_entry',
                    'importance': 0.5,
                    'tags': ['txt_import', os.path.basename(file_path)],
                    'chunk_index': len(chunks),
                    'original_file': file_path
                })
        
        print(f"✅ Created {len(chunks)} chunks from .txt file")
        return chunks
    
    def load_jsonl_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Load a .jsonl file"""
        print(f"📄 Loading .jsonl file: {file_path}")
        
        memories = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line.strip())
                    
                    # Standardize format
                    memory = {
                        'content': data.get('content', data.get('text', str(data))),
                        'source': data.get('source', 'jsonl_import'),
                        'timestamp': data.get('timestamp', datetime.now().timestamp()),
                        'type': 'memory_entry',
                        'importance': data.get('importance', 0.5),
                        'tags': data.get('tags', ['jsonl_import', os.path.basename(file_path)]),
                        'line_number': line_num,
                        'original_file': file_path
                    }
                    
                    memories.append(memory)
                    
                except json.JSONDecodeError as e:
                    print(f"⚠️  Skipping invalid JSON on line {line_num}: {e}")
                    continue
        
        print(f"✅ Loaded {len(memories)} entries from .jsonl file")
        return memories
    
    def load_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Load a .json file (array of objects)"""
        print(f"📄 Loading .json file: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        memories = []
        if isinstance(data, list):
            for i, item in enumerate(data):
                memory = {
                    'content': item.get('content', item.get('text', str(item))),
                    'source': item.get('source', 'json_import'),
                    'timestamp': item.get('timestamp', datetime.now().timestamp()),
                    'type': 'memory_entry',
                    'importance': item.get('importance', 0.5),
                    'tags': item.get('tags', ['json_import', os.path.basename(file_path)]),
                    'array_index': i,
                    'original_file': file_path
                }
                memories.append(memory)
        else:
            # Single object
            memory = {
                'content': data.get('content', data.get('text', str(data))),
                'source': data.get('source', 'json_import'),
                'timestamp': data.get('timestamp', datetime.now().timestamp()),
                'type': 'memory_entry',
                'importance': data.get('importance', 0.5),
                'tags': data.get('tags', ['json_import', os.path.basename(file_path)]),
                'original_file': file_path
            }
            memories.append(memory)
        
        print(f"✅ Loaded {len(memories)} entries from .json file")
        return memories
    
    def generate_embeddings(self, memories: List[Dict[str, Any]]) -> List[List[float]]:
        """Generate embeddings for all memories"""
        print(f"🧠 Generating embeddings using {self.embedding_backend} backend...")
        
        embedding_manager = self._get_embedding_manager()
        embeddings = []
        
        for i, memory in enumerate(memories):
            try:
                content = memory['content']
                vector = embedding_manager.embed(content)
                embeddings.append(vector)
                
                # Progress update
                if (i + 1) % 10 == 0:
                    print(f"   Processed {i + 1}/{len(memories)} embeddings...")
                    
            except Exception as e:
                print(f"⚠️  Error embedding memory {i}: {e}")
                # Use zero vector as fallback
                dimension = 768 if self.embedding_backend == "gemini" else 384
                embeddings.append([0.0] * dimension)
        
        print(f"✅ Generated {len(embeddings)} embeddings")
        return embeddings
    
    def merge_with_existing(self, new_memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge new memories with existing ones"""
        existing_memories = []
        
        # Load existing memories if they exist
        if os.path.exists(self.memory_file):
            print("📚 Loading existing memories...")
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                existing_memories = json.load(f)
            print(f"   Found {len(existing_memories)} existing memories")
        
        # Combine memories
        all_memories = existing_memories + new_memories
        print(f"✅ Combined: {len(existing_memories)} existing + {len(new_memories)} new = {len(all_memories)} total")
        
        return all_memories
    
    def create_metadata(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create metadata dictionary"""
        print("📋 Creating metadata...")
        
        metadata = {}
        for i, memory in enumerate(memories):
            unique_id = f"mem-{i}"
            metadata[unique_id] = memory.copy()
        
        print(f"✅ Created metadata for {len(metadata)} memories")
        return metadata
    
    def build_faiss_index(self, embeddings: List[List[float]]) -> None:
        """Build and save FAISS index"""
        print("🔍 Building FAISS index...")
        
        if not embeddings:
            print("❌ No embeddings to index")
            return
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings, dtype=np.float32)
        dimension = embeddings_array.shape[1]
        
        print(f"   Index dimension: {dimension}")
        print(f"   Number of vectors: {embeddings_array.shape[0]}")
        
        # Create FAISS index
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings_array)
        
        # Save index
        faiss.write_index(index, self.faiss_file)
        print(f"✅ FAISS index saved to {self.faiss_file}")
    
    def save_memories_and_metadata(self, memories: List[Dict[str, Any]], metadata: Dict[str, Any]) -> None:
        """Save memories and metadata to files"""
        print("💾 Saving memories and metadata...")
        
        # Create backup if files exist
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if os.path.exists(self.memory_file):
            backup_file = f"extract/agent_memories_backup_{timestamp}.json"
            os.rename(self.memory_file, backup_file)
            print(f"   Backed up existing memories to {backup_file}")
        
        if os.path.exists(self.metadata_file):
            backup_file = f"extract/memory_metadata_backup_{timestamp}.json"
            os.rename(self.metadata_file, backup_file)
            print(f"   Backed up existing metadata to {backup_file}")
        
        # Save new files
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(memories, f, indent=2, ensure_ascii=False)
        
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(memories)} memories and metadata")
    
    def process_file(self, file_path: str, merge: bool = True, chunk_size: int = 1000) -> None:
        """Process a single file"""
        print(f"🚀 Processing file: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return
        
        # Determine file type and load
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.txt':
            new_memories = self.load_txt_file(file_path, chunk_size)
        elif file_ext == '.jsonl':
            new_memories = self.load_jsonl_file(file_path)
        elif file_ext == '.json':
            new_memories = self.load_json_file(file_path)
        else:
            print(f"❌ Unsupported file type: {file_ext}")
            return
        
        if not new_memories:
            print("❌ No memories loaded from file")
            return
        
        # Merge with existing if requested
        if merge:
            all_memories = self.merge_with_existing(new_memories)
        else:
            all_memories = new_memories
        
        # Generate embeddings
        embeddings = self.generate_embeddings(all_memories)
        
        # Create metadata
        metadata = self.create_metadata(all_memories)
        
        # Save everything
        self.save_memories_and_metadata(all_memories, metadata)
        
        # Build FAISS index
        self.build_faiss_index(embeddings)
        
        print(f"🎉 Successfully processed {file_path}!")
        print(f"   Total memories: {len(all_memories)}")
        print(f"   New memories: {len(new_memories)}")
        print(f"   Embedding backend: {self.embedding_backend}")

def main():
    """Main CLI interface"""
    # Check if required dependencies are available
    if not NUMPY_AVAILABLE:
        print("❌ Required dependencies not available.")
        print("Please install them with: poetry install")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description="Load raw memory files into the system")
    parser.add_argument("file_path", help="Path to the file to process (.txt, .json, .jsonl)")
    parser.add_argument("--backend", choices=["minilm", "gemini"], default="gemini",
                       help="Embedding backend to use (default: gemini)")
    parser.add_argument("--api-key", help="Gemini API key (or set GEMINI_API_KEY env var)")
    parser.add_argument("--no-merge", action="store_true", 
                       help="Don't merge with existing memories (replace instead)")
    parser.add_argument("--chunk-size", type=int, default=1000,
                       help="Chunk size for .txt files (default: 1000 characters)")
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.getenv('GEMINI_API_KEY')
    if args.backend == "gemini" and not api_key:
        print("❌ Gemini API key required. Set GEMINI_API_KEY env var or use --api-key")
        return
    
    # Create loader
    loader = RawMemoryLoader(
        embedding_backend=args.backend,
        gemini_api_key=api_key
    )
    
    # Process file
    loader.process_file(
        file_path=args.file_path,
        merge=not args.no_merge,
        chunk_size=args.chunk_size
    )

if __name__ == "__main__":
    main()