#!/usr/bin/env python3
"""
Embedding Search Dashboard - Query Ray's memory using semantic search
"""

import streamlit as st
import sys
import json
import os
import faiss
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer, CrossEncoder

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from dashboard_config import config
from components.json_viewer import smart_json_display

st.set_page_config(
    page_title="🔍 Embedding Search",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Embedding Memory Search")
st.markdown("### Query Ray's memories using semantic search and re-ranking")

# Configuration
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
FAISS_INDEX_FILE = config.extract_dir / "faiss_index.bin"
METADATA_FILE = config.extract_dir / "memory_metadata.json"

@st.cache_resource
def load_models():
    """Load embedding and reranking models"""
    try:
        embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        reranker = CrossEncoder(RERANKER_MODEL_NAME)
        return embedding_model, reranker
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None, None

@st.cache_data
def load_index_and_metadata():
    """Load FAISS index and metadata"""
    try:
        if not FAISS_INDEX_FILE.exists() or not METADATA_FILE.exists():
            return None, None
        
        index = faiss.read_index(str(FAISS_INDEX_FILE))
        with open(METADATA_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            metadata = json.load(f)
        
        return index, metadata
    except Exception as e:
        st.error(f"Error loading index/metadata: {e}")
        return None, None

def perform_semantic_search(query_text, initial_k=20, final_k=5):
    """Perform semantic search with reranking"""
    
    # Load models and data
    embedding_model, reranker = load_models()
    index, metadata = load_index_and_metadata()
    
    if not all([embedding_model, reranker, index, metadata]):
        st.error("Required models or data not available")
        return []
    
    try:
        # Generate query embedding
        query_embedding = embedding_model.encode([query_text])
        
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
                    "faiss_score": float(distances[0][rank]),
                    "timestamp": memory_entry.get('timestamp', 'Unknown')
                })
        
        # Filter agent responses for reranking
        agent_responses = [r for r in initial_results if r['source'] == 'agent_response']
        
        if not agent_responses:
            return initial_results[:final_k]  # Return initial results if no agent responses
        
        # Rerank agent responses
        sentence_pairs = [[query_text, r['content']] for r in agent_responses]
        rerank_scores = reranker.predict(sentence_pairs)
        
        # Add rerank scores
        for i, score in enumerate(rerank_scores):
            agent_responses[i]['rerank_score'] = float(score)
        
        # Sort by rerank score
        sorted_results = sorted(agent_responses, key=lambda x: x['rerank_score'], reverse=True)
        
        return sorted_results[:final_k]
        
    except Exception as e:
        st.error(f"Search error: {e}")
        return []

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    # Search interface
    st.subheader("🔍 Search Interface")
    
    query = st.text_input(
        "Enter your search query:",
        value=st.session_state.get('search_query', ''),
        placeholder="What would you like to search for in Ray's memories?",
        help="Use natural language to describe what you're looking for",
        key="main_search_input"
    )
    
    col_search1, col_search2 = st.columns(2)
    with col_search1:
        initial_k = st.slider("Initial results", 10, 50, 20, help="Number of initial FAISS results")
    with col_search2:
        final_k = st.slider("Final results", 3, 15, 5, help="Number of final reranked results")

with col2:
    # System status
    st.subheader("📊 System Status")
    
    # Check if files exist
    faiss_exists = FAISS_INDEX_FILE.exists()
    metadata_exists = METADATA_FILE.exists()
    
    st.write(f"🗂️ FAISS Index: {'✅' if faiss_exists else '❌'}")
    st.write(f"📋 Metadata: {'✅' if metadata_exists else '❌'}")
    
    if faiss_exists and metadata_exists:
        try:
            with open(METADATA_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                metadata = json.load(f)
            st.write(f"📊 Total memories: {len(metadata)}")
        except:
            st.write("📊 Total memories: Unknown")
    
    # Model status
    embedding_model, reranker = load_models()
    st.write(f"🤖 Embedding model: {'✅' if embedding_model else '❌'}")
    st.write(f"🔄 Reranker model: {'✅' if reranker else '❌'}")

# Search execution
if st.button("🔍 Search Memories", type="primary", disabled=not query, key="main_search_button"):
    if query:
        with st.spinner("Searching Ray's memories..."):
            results = perform_semantic_search(query, initial_k, final_k)
        
        if results:
            st.success(f"Found {len(results)} relevant memories")
            
            # Display results
            st.subheader("🎯 Search Results")
            
            for i, result in enumerate(results):
                with st.expander(f"📝 Result {i+1} - {result['id']}", expanded=i==0):
                    
                    # Metadata
                    col_meta1, col_meta2, col_meta3 = st.columns(3)
                    with col_meta1:
                        st.write(f"**Source:** {result['source']}")
                    with col_meta2:
                        st.write(f"**FAISS Score:** {result['faiss_score']:.4f}")
                    with col_meta3:
                        if 'rerank_score' in result:
                            st.write(f"**Rerank Score:** {result['rerank_score']:.4f}")
                    
                    st.write(f"**Timestamp:** {result['timestamp']}")
                    
                    # Content
                    st.markdown("**Content:**")
                    st.markdown(f"```\n{result['content']}\n```")
                    
                    # JSON view
                    with st.expander("🔍 Raw Data"):
                        smart_json_display(result, f"Result {i+1} Data")
        else:
            st.warning("No relevant memories found. Try a different query.")

# Quick search examples
st.markdown("---")
st.subheader("💡 Example Queries")

example_queries = [
    "What did Ray say about consciousness?",
    "How does Ray handle memory?",
    "Ray's thoughts on learning",
    "What are Ray's goals?",
    "Ray's reflections on existence"
]

cols = st.columns(len(example_queries))
for i, example in enumerate(example_queries):
    with cols[i]:
        if st.button(f"'{example}'", key=f"example_query_{i}"):
            # Set the query and trigger search
            st.session_state.search_query = example
            st.rerun()

# Help section
with st.expander("ℹ️ How to Use"):
    st.markdown("""
    ### How Semantic Search Works:
    
    1. **Query Processing**: Your natural language query is converted to embeddings
    2. **Initial Search**: FAISS finds the most similar memories based on semantic similarity
    3. **Filtering**: Results are filtered to focus on agent responses
    4. **Reranking**: A cross-encoder model reranks results for better relevance
    5. **Results**: Top results are displayed with scores and metadata
    
    ### Tips for Better Results:
    - Use natural language descriptions
    - Be specific about what you're looking for
    - Try different phrasings if results aren't relevant
    - Use the example queries as starting points
    
    ### Scores Explained:
    - **FAISS Score**: Lower is better (distance in embedding space)
    - **Rerank Score**: Higher is better (relevance confidence)
    """)

# Debug information
with st.expander("🔍 Debug Information"):
    debug_info = {
        "faiss_index_path": str(FAISS_INDEX_FILE),
        "metadata_path": str(METADATA_FILE),
        "faiss_exists": faiss_exists,
        "metadata_exists": metadata_exists,
        "embedding_model": EMBEDDING_MODEL_NAME,
        "reranker_model": RERANKER_MODEL_NAME,
        "project_root": str(config.project_root),
        "extract_dir": str(config.extract_dir)
    }
    smart_json_display(debug_info, "Debug Information")