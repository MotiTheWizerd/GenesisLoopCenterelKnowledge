#!/usr/bin/env python3
"""
Quick script to add large JSON files to Ray's memory system
Usage: python scripts/add_json_to_memory.py path/to/your/file.json
"""

import json
import sys
import os
import numpy as np
import faiss
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def calculate_importance(content):
    """Calculate importance score based on content analysis"""
    if not content:
        return 0.1
    
    score = 0.3  # Base score
    
    # Length factor
    if len(content) > 100:
        score += 0.2
    if len(content) > 500:
        score += 0.2
    
    # Word count factor
    words = len(content.split())
    if words > 20:
        score += 0.1
    if words > 50:
        score += 0.1
    
    # Content quality indicators
    content_lower = content.lower()
    
    # Technical content
    if any(word in content_lower for word in ['function', 'class', 'method', 'algorithm', 'implementation']):
        score += 0.1
    
    # Important keywords
    if any(word in content_lower for word in ['important', 'critical', 'key', 'essential', 'note']):
        score += 0.1
    
    return min(score, 1.0)

def process_json_content(data, filename, chunk_size=1000):
    """Process JSON data into memory chunks"""
    chunks = []
    timestamp = datetime.now().timestamp()
    
    if isinstance(data, list):
        print(f"📋 Processing JSON array with {len(data)} items...")
        
        for i, item in enumerate(data):
            if isinstance(item, dict):
                # Handle dictionary items
                content = json.dumps(item, indent=2, ensure_ascii=False)
            else:
                # Handle primitive items
                content = str(item)
            
            # Split large content into chunks
            if len(content) > chunk_size:
                for j in range(0, len(content), chunk_size):
                    chunk_content = content[j:j + chunk_size]
                    chunks.append({
                        'content': chunk_content,
                        'source': f'json_file_{filename}',
                        'timestamp': timestamp,
                        'type': 'memory_entry',
                        'importance': calculate_importance(chunk_content),
                        'tags': ['json_upload', 'file_import', f'item_{i}', f'chunk_{j//chunk_size}'],
                        'original_file': filename,
                        'file_type': 'json',
                        'array_index': i,
                        'chunk_index': j // chunk_size
                    })
            else:
                chunks.append({
                    'content': content,
                    'source': f'json_file_{filename}',
                    'timestamp': timestamp,
                    'type': 'memory_entry',
                    'importance': calculate_importance(content),
                    'tags': ['json_upload', 'file_import', f'item_{i}'],
                    'original_file': filename,
                    'file_type': 'json',
                    'array_index': i
                })
    
    elif isinstance(data, dict):
        print(f"📄 Processing JSON object with {len(data)} keys...")
        
        # Process each key-value pair
        for key, value in data.items():
            content = f"{key}: {json.dumps(value, indent=2, ensure_ascii=False)}"
            
            # Split large content into chunks
            if len(content) > chunk_size:
                for j in range(0, len(content), chunk_size):
                    chunk_content = content[j:j + chunk_size]
                    chunks.append({
                        'content': chunk_content,
                        'source': f'json_file_{filename}',
                        'timestamp': timestamp,
                        'type': 'memory_entry',
                        'importance': calculate_importance(chunk_content),
                        'tags': ['json_upload', 'file_import', f'key_{key}', f'chunk_{j//chunk_size}'],
                        'original_file': filename,
                        'file_type': 'json',
                        'object_key': key,
                        'chunk_index': j // chunk_size
                    })
            else:
                chunks.append({
                    'content': content,
                    'source': f'json_file_{filename}',
                    'timestamp': timestamp,
                    'type': 'memory_entry',
                    'importance': calculate_importance(content),
                    'tags': ['json_upload', 'file_import', f'key_{key}'],
                    'original_file': filename,
                    'file_type': 'json',
                    'object_key': key
                })
    
    else:
        # Single value
        content = json.dumps(data, indent=2, ensure_ascii=False)
        chunks.append({
            'content': content,
            'source': f'json_file_{filename}',
            'timestamp': timestamp,
            'type': 'memory_entry',
            'importance': calculate_importance(content),
            'tags': ['json_upload', 'file_import'],
            'original_file': filename,
            'file_type': 'json'
        })
    
    return chunks

def generate_embeddings(chunks, backend='minilm'):
    """Generate embeddings for chunks"""
    print(f"🧠 Generating embeddings using {backend} backend...")
    
    embeddings = []
    
    if backend == 'minilm':
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer("all-MiniLM-L6-v2")
            
            contents = [chunk['content'] for chunk in chunks]
            vectors = model.encode(contents, show_progress_bar=True)
            embeddings = [vector.tolist() for vector in vectors]
            
        except ImportError:
            print("❌ sentence-transformers not installed. Install with: pip install sentence-transformers")
            return None
    
    elif backend == 'gemini':
        try:
            from services.embedding_manager import EmbeddingManager
            
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                print("❌ GEMINI_API_KEY environment variable not set")
                return None
            
            embedding_manager = EmbeddingManager(backend="gemini", gemini_api_key=api_key)
            
            for i, chunk in enumerate(chunks):
                if i % 10 == 0:
                    print(f"  Processing chunk {i+1}/{len(chunks)}")
                
                vector = embedding_manager.embed(chunk['content'])
                embeddings.append(vector)
                
        except ImportError:
            print("❌ Gemini embedding service not available")
            return None
    
    return embeddings

def save_to_memory_system(chunks, embeddings):
    """Save chunks and embeddings to Ray's memory system"""
    print("💾 Saving to memory system...")
    
    # Create extract directory if it doesn't exist
    os.makedirs("extract", exist_ok=True)
    
    # Load existing memories
    existing_memories = []
    if os.path.exists("extract/agent_memories.json"):
        with open("extract/agent_memories.json", 'r', encoding='utf-8') as f:
            existing_memories = json.load(f)
        print(f"📚 Found {len(existing_memories)} existing memories")
    
    # Combine memories
    all_memories = existing_memories + chunks
    print(f"📈 Total memories after addition: {len(all_memories)}")
    
    # Create metadata
    metadata = {}
    for i, memory in enumerate(all_memories):
        metadata[f"mem-{i}"] = memory
    
    # Backup existing files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if os.path.exists("extract/agent_memories.json"):
        os.rename("extract/agent_memories.json", f"extract/agent_memories_backup_{timestamp}.json")
        print(f"📦 Backed up existing memories to agent_memories_backup_{timestamp}.json")
    
    if os.path.exists("extract/memory_metadata.json"):
        os.rename("extract/memory_metadata.json", f"extract/memory_metadata_backup_{timestamp}.json")
        print(f"📦 Backed up existing metadata to memory_metadata_backup_{timestamp}.json")
    
    # Save new files
    with open("extract/agent_memories.json", 'w', encoding='utf-8') as f:
        json.dump(all_memories, f, indent=2, ensure_ascii=False)
    
    with open("extract/memory_metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print("✅ Saved memories and metadata")
    
    # Build FAISS index
    if embeddings:
        print("🔍 Building FAISS index...")
        
        # Load existing embeddings if available
        existing_embeddings = []
        if os.path.exists("extract/faiss_index.bin"):
            try:
                existing_index = faiss.read_index("extract/faiss_index.bin")
                # For simplicity, we'll rebuild the entire index
                # In production, you might want to add to existing index
                print(f"🔄 Rebuilding index (was {existing_index.ntotal} entries)")
            except:
                print("⚠️ Could not load existing index, creating new one")
        
        # Create embeddings for all memories (existing + new)
        print("🧠 Generating embeddings for all memories...")
        
        # For existing memories without embeddings, use a simple approach
        all_embeddings = []
        
        # Add existing embeddings (simplified - in practice you'd store these separately)
        if len(existing_memories) > 0:
            print("⚠️ Note: Existing memories will get new embeddings (index rebuild)")
            
            # Generate embeddings for existing memories too
            if len(existing_memories) > 0:
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer("all-MiniLM-L6-v2")
                
                existing_contents = [mem.get('content', '') for mem in existing_memories]
                existing_vectors = model.encode(existing_contents, show_progress_bar=True)
                all_embeddings.extend([vector.tolist() for vector in existing_vectors])
        
        # Add new embeddings
        all_embeddings.extend(embeddings)
        
        # Create FAISS index
        embeddings_array = np.array(all_embeddings, dtype=np.float32)
        dimension = embeddings_array.shape[1]
        
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings_array)
        
        # Backup existing index
        if os.path.exists("extract/faiss_index.bin"):
            os.rename("extract/faiss_index.bin", f"extract/faiss_index_backup_{timestamp}.bin")
            print(f"📦 Backed up existing index to faiss_index_backup_{timestamp}.bin")
        
        # Save new index
        faiss.write_index(index, "extract/faiss_index.bin")
        print(f"✅ Built FAISS index with {index.ntotal} entries, dimension {dimension}")
    
    return len(chunks)

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python scripts/add_json_to_memory.py <json_file_path>")
        print("Example: python scripts/add_json_to_memory.py data/my_data.json")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    
    if not os.path.exists(json_file_path):
        print(f"❌ File not found: {json_file_path}")
        sys.exit(1)
    
    filename = os.path.basename(json_file_path)
    print(f"🚀 Processing JSON file: {filename}")
    print(f"📁 Full path: {json_file_path}")
    
    # Load JSON file
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Successfully loaded JSON file")
    except Exception as e:
        print(f"❌ Error loading JSON file: {e}")
        sys.exit(1)
    
    # Process into chunks
    chunks = process_json_content(data, filename)
    print(f"📝 Created {len(chunks)} memory chunks")
    
    if not chunks:
        print("❌ No chunks created from JSON file")
        sys.exit(1)
    
    # Generate embeddings
    backend = 'minilm'  # Default to MiniLM for simplicity
    embeddings = generate_embeddings(chunks, backend)
    
    if embeddings is None:
        print("❌ Failed to generate embeddings")
        sys.exit(1)
    
    print(f"✅ Generated {len(embeddings)} embeddings")
    
    # Save to memory system
    added_count = save_to_memory_system(chunks, embeddings)
    
    print(f"\n🎉 Successfully added {added_count} memories from {filename}")
    print("🔄 Restart your dashboard to see the new memories!")
    print("\nNext steps:")
    print("1. Restart the dashboard: python run_dashboard.py")
    print("2. Go to Memory Management tab to view/edit the new memories")
    print("3. Use Memory Query tab to search the new content")

if __name__ == "__main__":
    main()