"""
File Processing Tab Component
Upload, split, and embed files with visual progress tracking
"""

import streamlit as st
import os
import json
import tempfile
import subprocess
from datetime import datetime
import pandas as pd
from pathlib import Path
import sys

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '..', '..', '..')
project_root = os.path.abspath(project_root)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def render_file_processing_tab():
    """Render the file processing tab with upload, split, and embed functionality"""
    
    st.header("📁 File Processing & Embedding")
    st.markdown("*Upload files, split them into chunks, and embed them into Ray's memory system*")
    
    # File upload section
    render_file_upload_section()
    
    # File management section
    render_file_management_section()
    
    # Processing status section
    render_processing_status_section()
    
    # Recent uploads section
    render_recent_uploads_section()

def render_file_upload_section():
    """Render the file upload interface"""
    st.subheader("📤 Upload Files")
    
    # File uploader with multiple file support
    uploaded_files = st.file_uploader(
        "Choose files to process",
        type=['txt', 'json', 'jsonl', 'md', 'csv'],
        accept_multiple_files=True,
        help="Upload multiple files to process them in batch. Supported formats: .txt, .json, .jsonl, .md, .csv"
    )
    
    if uploaded_files:
        # Display uploaded files info
        st.write("**📋 Uploaded Files:**")
        
        files_data = []
        total_size = 0
        
        for file in uploaded_files:
            file_size = len(file.getvalue())
            total_size += file_size
            files_data.append({
                'Filename': file.name,
                'Type': file.type or 'Unknown',
                'Size (KB)': f"{file_size / 1024:.1f}",
                'Extension': Path(file.name).suffix
            })
        
        files_df = pd.DataFrame(files_data)
        st.dataframe(files_df, use_container_width=True)
        
        st.info(f"📊 Total: {len(uploaded_files)} files, {total_size / 1024:.1f} KB")
        
        # Processing options
        render_processing_options(uploaded_files)

def render_processing_options(uploaded_files):
    """Render processing configuration options"""
    st.subheader("⚙️ Processing Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Embedding backend selection (auto-detect from environment)
        default_backend = os.getenv('EMBEDDING_BACKEND', 'minilm')  # Default to faster option
        backend_options = ["minilm", "gemini"]
        default_index = 0 if default_backend == "minilm" else 1
        
        embedding_backend = st.selectbox(
            "🧠 Embedding Backend:",
            backend_options,
            index=default_index,
            help="Choose your embedding backend"
        )
        
        # Speed comparison info
        if embedding_backend == "minilm":
            st.info("⚡ **MiniLM**: Fast local processing (384D) - Recommended for large files")
        else:
            st.warning("🐌 **Gemini**: High quality but slower API calls (768D) - Better for small files")
        
        # Chunk size for text files with cost optimization
        if embedding_backend == "gemini":
            default_chunk_size = 500  # Smaller for cost efficiency
            help_text = "Size of text chunks (smaller = fewer API calls = lower cost)"
        else:
            default_chunk_size = 1000  # Larger for better context
            help_text = "Size of text chunks (larger = better context, no cost impact)"
        
        chunk_size = st.slider(
            "📏 Chunk Size (characters):",
            min_value=200,
            max_value=3000,
            value=default_chunk_size,
            step=100,
            help=help_text
        )
        
        # Cost estimation
        if embedding_backend == "gemini":
            estimated_chunks = sum(len(f.getvalue()) for f in uploaded_files) // chunk_size
            estimated_cost = estimated_chunks * 0.001  # Rough estimate
            st.info(f"💰 Estimated cost: ~${estimated_cost:.2f} ({estimated_chunks:,} API calls)")
        else:
            st.info("💰 Cost: FREE (local processing)")
        
        # Processing mode
        processing_mode = st.radio(
            "🔄 Processing Mode:",
            ["Merge with existing", "Replace existing", "Create backup"],
            index=0,
            help="How to handle existing memories"
        )
    
    with col2:
        # Quality settings
        st.write("**🎯 Quality Settings:**")
        
        filter_short = st.checkbox(
            "Filter very short chunks (< 50 chars)",
            value=True,
            help="Remove chunks that are too short to be meaningful"
        )
        
        filter_duplicates = st.checkbox(
            "Remove duplicate content",
            value=True,
            help="Skip chunks with identical content"
        )
        
        auto_importance = st.checkbox(
            "Auto-calculate importance scores",
            value=True,
            help="Automatically assign importance based on content analysis"
        )
        
        # Advanced options
        with st.expander("🔧 Advanced Options"):
            custom_tags = st.text_input(
                "Custom Tags (comma-separated):",
                placeholder="document, important, reference",
                help="Add custom tags to all processed memories"
            )
            
            source_prefix = st.text_input(
                "Source Prefix:",
                value="file_upload",
                help="Prefix for source identification"
            )
    
    # API key for Gemini
    gemini_api_key = None
    if embedding_backend == "gemini":
        gemini_api_key = st.text_input(
            "🔑 Gemini API Key:",
            type="password",
            value=os.getenv('GEMINI_API_KEY', ''),
            help="Required for Gemini embedding backend"
        )
        
        if not gemini_api_key:
            st.warning("⚠️ Gemini API key required for selected backend")
    
    # Process buttons
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button(
            "⚡ Quick Process", 
            help="Process with smart defaults - fastest option",
            use_container_width=True,
            disabled=(embedding_backend == "gemini" and not gemini_api_key)
        ):
            # Use smart defaults for quick processing with cost optimization
            smart_chunk_size = 500 if embedding_backend == "gemini" else 1000
            
            process_uploaded_files(
                uploaded_files,
                embedding_backend,
                gemini_api_key,
                smart_chunk_size,  # Cost-optimized chunk size
                "Merge with existing",  # Safe default
                True,   # Filter short
                True,   # Filter duplicates  
                True,   # Auto importance
                "quick_upload",  # Simple tag
                "quick_upload"   # Simple source
            )
    
    with col2:
        if st.button(
            "🚀 Process All Files", 
            type="primary", 
            use_container_width=True,
            disabled=(embedding_backend == "gemini" and not gemini_api_key)
        ):
            process_uploaded_files(
                uploaded_files,
                embedding_backend,
                gemini_api_key,
                chunk_size,
                processing_mode,
                filter_short,
                filter_duplicates,
                auto_importance,
                custom_tags,
                source_prefix
            )

def process_uploaded_files(files, backend, api_key, chunk_size, mode, filter_short, 
                          filter_duplicates, auto_importance, custom_tags, source_prefix):
    """Process uploaded files through the extraction and embedding pipeline"""
    
    # Initialize processing session
    processing_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Store processing info in session state
    if 'processing_sessions' not in st.session_state:
        st.session_state.processing_sessions = []
    
    session_info = {
        'id': processing_id,
        'timestamp': datetime.now(),
        'files': [f.name for f in files],
        'status': 'processing',
        'backend': backend,
        'chunk_size': chunk_size,
        'mode': mode,
        'results': {}
    }
    
    st.session_state.processing_sessions.insert(0, session_info)
    
    # Create progress tracking
    progress_container = st.container()
    
    with progress_container:
        st.subheader(f"🔄 Processing Session: {processing_id}")
        
        # Overall progress
        overall_progress = st.progress(0)
        status_text = st.empty()
        
        # Detailed progress
        with st.expander("📊 Detailed Progress", expanded=True):
            file_progress_container = st.container()
        
        try:
            total_files = len(files)
            processed_files = 0
            all_results = []
            
            for i, uploaded_file in enumerate(files):
                # Update overall progress
                overall_progress.progress((i) / total_files)
                status_text.text(f"Processing {uploaded_file.name} ({i+1}/{total_files})")
                
                with file_progress_container:
                    st.write(f"**📄 Processing: {uploaded_file.name}**")
                    
                    # Create file-specific progress
                    file_progress = st.progress(0)
                    file_status = st.empty()
                
                # Save file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                try:
                    # Step 1: Extract/Split
                    file_progress.progress(0.2)
                    file_status.text("🔪 Splitting file into chunks...")
                    
                    chunks = extract_file_content(
                        tmp_file_path, 
                        uploaded_file.name,
                        chunk_size,
                        filter_short,
                        filter_duplicates,
                        custom_tags,
                        source_prefix
                    )
                    
                    # Step 2: Generate embeddings
                    file_progress.progress(0.5)
                    file_status.text("🧠 Generating embeddings...")
                    
                    embeddings = generate_embeddings_for_chunks(
                        chunks, 
                        backend, 
                        api_key
                    )
                    
                    # Step 3: Save to memory system
                    file_progress.progress(0.8)
                    file_status.text("💾 Saving to memory system...")
                    
                    result = save_to_memory_system(
                        chunks, 
                        embeddings, 
                        mode == "Merge with existing"
                    )
                    
                    # Complete
                    file_progress.progress(1.0)
                    file_status.text("✅ Complete!")
                    
                    all_results.append({
                        'file': uploaded_file.name,
                        'chunks': len(chunks),
                        'embeddings': len(embeddings),
                        'status': 'success'
                    })
                    
                except Exception as e:
                    file_progress.progress(1.0)
                    file_status.text(f"❌ Error: {str(e)}")
                    
                    all_results.append({
                        'file': uploaded_file.name,
                        'chunks': 0,
                        'embeddings': 0,
                        'status': 'error',
                        'error': str(e)
                    })
                
                finally:
                    # Clean up temp file
                    os.unlink(tmp_file_path)
                
                processed_files += 1
            
            # Final progress update
            overall_progress.progress(1.0)
            status_text.text("🎉 All files processed!")
            
            # Update session info
            session_info['status'] = 'completed'
            session_info['results'] = all_results
            
            # Display results summary
            display_processing_results(all_results)
            
            # Clear memory service cache if it exists
            if hasattr(st.session_state, 'memory_service'):
                st.session_state.memory_service._memories = None
                st.session_state.memory_service._metadata = None
                st.session_state.memory_service._faiss_index = None
            
            st.success("🔄 Memory system cache cleared. New data is ready!")
            
        except Exception as e:
            overall_progress.progress(1.0)
            status_text.text(f"❌ Processing failed: {str(e)}")
            session_info['status'] = 'failed'
            session_info['error'] = str(e)
            st.error(f"Processing failed: {e}")

def extract_messages_from_conversation(entry):
    """Extract messages from a conversation entry (ChatGPT format)."""
    messages = []
    
    try:
        # Check if this entry has a mapping field (conversation structure)
        if 'mapping' in entry and entry['mapping']:
            mapping = entry['mapping']
            
            # Iterate through the mapping to find message nodes
            for node_id, node_data in mapping.items():
                if 'message' in node_data and node_data['message']:
                    message_data = node_data['message']
                    
                    # Extract relevant message information
                    if 'content' in message_data and message_data['content']:
                        content = message_data['content']
                        
                        # Handle different content structures
                        if isinstance(content, dict) and 'parts' in content:
                            text_parts = content['parts']
                            if text_parts and len(text_parts) > 0:
                                message_text = ' '.join(str(part) for part in text_parts if part)
                                
                                if message_text.strip():  # Only add non-empty messages
                                    role = message_data.get('author', {}).get('role', 'unknown')
                                    messages.append({
                                        'role': role,
                                        'content': message_text,
                                        'create_time': message_data.get('create_time'),
                                        'conversation_id': entry.get('conversation_id', ''),
                                        'title': entry.get('title', '')
                                    })
        
        return messages
    
    except Exception as e:
        return []

def extract_file_content(file_path, filename, chunk_size, filter_short, 
                        filter_duplicates, custom_tags, source_prefix):
    """Extract and chunk content from uploaded file"""
    
    file_ext = Path(filename).suffix.lower()
    chunks = []
    
    # Parse custom tags
    tags = [tag.strip() for tag in custom_tags.split(',') if tag.strip()] if custom_tags else []
    tags.extend(['file_upload', file_ext[1:] if file_ext else 'unknown'])
    
    try:
        if file_ext == '.txt' or file_ext == '.md':
            # Text file processing
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into chunks
            for i in range(0, len(content), chunk_size):
                chunk_content = content[i:i + chunk_size].strip()
                
                if filter_short and len(chunk_content) < 50:
                    continue
                
                chunks.append({
                    'content': chunk_content,
                    'source': f"{source_prefix}_{filename}",
                    'timestamp': datetime.now().timestamp(),
                    'type': 'memory_entry',
                    'importance': calculate_importance(chunk_content) if chunk_content else 0.3,
                    'tags': tags + [f'chunk_{i//chunk_size}'],
                    'chunk_index': i // chunk_size,
                    'original_file': filename,
                    'file_type': file_ext[1:]
                })
        
        elif file_ext == '.json':
            # JSON file processing with conversation extraction for chat files
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if this looks like a ChatGPT conversation export
            is_chat_export = False
            if isinstance(data, list) and len(data) > 0:
                first_item = data[0]
                if isinstance(first_item, dict) and ('mapping' in first_item or 'conversation_id' in first_item):
                    is_chat_export = True
            elif isinstance(data, dict) and ('mapping' in data or 'conversation_id' in data):
                is_chat_export = True
            
            if is_chat_export:
                # Process as chat conversation export
                st.info("🗣️ Detected chat conversation format - extracting actual messages...")
                
                entries = data if isinstance(data, list) else [data]
                
                for i, entry in enumerate(entries):
                    messages = extract_messages_from_conversation(entry)
                    
                    for msg_idx, message in enumerate(messages):
                        # Create readable conversation content
                        role = message['role']
                        content = message['content']
                        title = message.get('title', 'Untitled Conversation')
                        
                        # Format as readable conversation
                        if role == 'user':
                            formatted_content = f"User: {content}"
                        elif role == 'assistant':
                            formatted_content = f"Assistant: {content}"
                        else:
                            formatted_content = f"{role.title()}: {content}"
                        
                        if filter_short and len(formatted_content) < 50:
                            continue
                        
                        # Split large content if needed
                        max_chunk_size = min(chunk_size, 30000)
                        
                        if len(formatted_content) > max_chunk_size:
                            for chunk_idx, start in enumerate(range(0, len(formatted_content), max_chunk_size)):
                                chunk_content = formatted_content[start:start + max_chunk_size]
                                
                                chunks.append({
                                    'content': chunk_content,
                                    'source': f"{source_prefix}_{filename}",
                                    'timestamp': message.get('create_time', datetime.now().timestamp()),
                                    'type': 'memory_entry',
                                    'importance': calculate_importance(chunk_content) + 0.2,  # Boost chat importance
                                    'tags': tags + [f'conversation', f'conv_{i}', f'msg_{msg_idx}', f'chunk_{chunk_idx}', role],
                                    'conversation_id': message.get('conversation_id', ''),
                                    'conversation_title': title,
                                    'message_role': role,
                                    'array_index': i,
                                    'message_index': msg_idx,
                                    'chunk_index': chunk_idx,
                                    'original_file': filename,
                                    'file_type': 'chat_json'
                                })
                        else:
                            chunks.append({
                                'content': formatted_content,
                                'source': f"{source_prefix}_{filename}",
                                'timestamp': message.get('create_time', datetime.now().timestamp()),
                                'type': 'memory_entry',
                                'importance': calculate_importance(formatted_content) + 0.2,  # Boost chat importance
                                'tags': tags + [f'conversation', f'conv_{i}', f'msg_{msg_idx}', role],
                                'conversation_id': message.get('conversation_id', ''),
                                'conversation_title': title,
                                'message_role': role,
                                'array_index': i,
                                'message_index': msg_idx,
                                'original_file': filename,
                                'file_type': 'chat_json'
                            })
            else:
                # Process as regular JSON (existing logic)
                if isinstance(data, list):
                    for i, item in enumerate(data):
                        content = str(item) if not isinstance(item, dict) else item.get('content', str(item))
                        
                        if filter_short and len(content) < 50:
                            continue
                        
                        # Split large content into chunks (Gemini has ~36KB limit)
                        max_chunk_size = min(chunk_size, 30000)  # Safe limit for Gemini
                        
                        if len(content) > max_chunk_size:
                            # Split large content into smaller chunks
                            for chunk_idx, start in enumerate(range(0, len(content), max_chunk_size)):
                                chunk_content = content[start:start + max_chunk_size]
                                
                                chunks.append({
                                    'content': chunk_content,
                                    'source': f"{source_prefix}_{filename}",
                                    'timestamp': datetime.now().timestamp(),
                                    'type': 'memory_entry',
                                    'importance': calculate_importance(chunk_content),
                                    'tags': tags + [f'item_{i}', f'chunk_{chunk_idx}'],
                                    'array_index': i,
                                    'chunk_index': chunk_idx,
                                    'original_file': filename,
                                    'file_type': 'json'
                                })
                        else:
                            chunks.append({
                                'content': content,
                                'source': f"{source_prefix}_{filename}",
                                'timestamp': datetime.now().timestamp(),
                                'type': 'memory_entry',
                                'importance': calculate_importance(content),
                                'tags': tags + [f'item_{i}'],
                                'array_index': i,
                                'original_file': filename,
                                'file_type': 'json'
                            })
                else:
                    # Single JSON object - also chunk if too large
                    content = str(data)
                    max_chunk_size = min(chunk_size, 30000)  # Safe limit for Gemini
                    
                    if len(content) > max_chunk_size:
                        # Split large content into smaller chunks
                        for chunk_idx, start in enumerate(range(0, len(content), max_chunk_size)):
                            chunk_content = content[start:start + max_chunk_size]
                            
                            chunks.append({
                                'content': chunk_content,
                                'source': f"{source_prefix}_{filename}",
                                'timestamp': datetime.now().timestamp(),
                                'type': 'memory_entry',
                                'importance': calculate_importance(chunk_content),
                                'tags': tags + [f'chunk_{chunk_idx}'],
                                'chunk_index': chunk_idx,
                                'original_file': filename,
                                'file_type': 'json'
                            })
                    else:
                        chunks.append({
                            'content': content,
                            'source': f"{source_prefix}_{filename}",
                            'timestamp': datetime.now().timestamp(),
                            'type': 'memory_entry',
                            'importance': calculate_importance(content),
                            'tags': tags,
                            'original_file': filename,
                            'file_type': 'json'
                        })
        
        elif file_ext == '.jsonl':
            # JSONL file processing
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        data = json.loads(line.strip())
                        content = data.get('content', data.get('text', str(data)))
                        
                        if filter_short and len(content) < 50:
                            continue
                        
                        chunks.append({
                            'content': content,
                            'source': f"{source_prefix}_{filename}",
                            'timestamp': datetime.now().timestamp(),
                            'type': 'memory_entry',
                            'importance': calculate_importance(content),
                            'tags': tags + [f'line_{line_num}'],
                            'line_number': line_num,
                            'original_file': filename,
                            'file_type': 'jsonl'
                        })
                    except json.JSONDecodeError:
                        continue
        
        elif file_ext == '.csv':
            # CSV file processing
            import pandas as pd
            df = pd.read_csv(file_path)
            
            for i, row in df.iterrows():
                content = ' | '.join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                
                if filter_short and len(content) < 50:
                    continue
                
                chunks.append({
                    'content': content,
                    'source': f"{source_prefix}_{filename}",
                    'timestamp': datetime.now().timestamp(),
                    'type': 'memory_entry',
                    'importance': calculate_importance(content),
                    'tags': tags + [f'row_{i}'],
                    'row_index': i,
                    'original_file': filename,
                    'file_type': 'csv'
                })
    
    except Exception as e:
        st.error(f"Error processing {filename}: {e}")
        return []
    
    # Remove duplicates if requested
    if filter_duplicates:
        seen_content = set()
        unique_chunks = []
        
        for chunk in chunks:
            content_hash = hash(chunk['content'])
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_chunks.append(chunk)
        
        chunks = unique_chunks
    
    return chunks

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

def generate_embeddings_for_chunks(chunks, backend, api_key):
    """Generate embeddings for chunks using the specified backend"""
    if not chunks:
        return []
    
    try:
        embeddings = []
        
        if backend == "gemini":
            # Gemini: Process one by one with progress tracking
            from services.embedding_manager import EmbeddingManager
            embedding_manager = EmbeddingManager(backend="gemini", gemini_api_key=api_key)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, chunk in enumerate(chunks):
                try:
                    content = chunk['content']
                    
                    # Update progress
                    progress = (i + 1) / len(chunks)
                    progress_bar.progress(progress)
                    status_text.text(f"🧠 Gemini embedding {i+1}/{len(chunks)} ({progress*100:.1f}%)")
                    
                    # Pre-check for Gemini size limits
                    if len(content.encode('utf-8')) > 30000:
                        st.warning(f"⚠️ Skipping chunk that's too large for Gemini: {len(content)} chars")
                        continue
                    
                    vector = embedding_manager.embed(content)
                    embeddings.append(vector)
                    
                except Exception as e:
                    error_msg = str(e)
                    if "payload size exceeds" in error_msg:
                        st.warning(f"⚠️ Chunk too large for Gemini API (skipping): {len(content)} chars")
                        continue
                    else:
                        st.warning(f"Failed to embed chunk: {e}")
                        embeddings.append([0.0] * 768)  # Gemini dimension
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
        else:
            # MiniLM: Fast batch processing
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer("all-MiniLM-L6-v2")
            
            st.info("🚀 Using MiniLM for fast local embedding...")
            
            # Extract all content for batch processing
            valid_chunks = []
            for chunk in chunks:
                content = chunk['content']
                if len(content.strip()) > 0:  # Skip empty chunks
                    valid_chunks.append(content)
            
            if valid_chunks:
                # Batch process all chunks at once (much faster!)
                with st.spinner(f"⚡ Processing {len(valid_chunks)} chunks with MiniLM..."):
                    vectors = model.encode(valid_chunks, show_progress_bar=False)
                    embeddings = [vector.tolist() for vector in vectors]
                
                st.success(f"✅ Generated {len(embeddings)} embeddings in batch!")
        
        return embeddings
        
    except Exception as e:
        st.error(f"Error generating embeddings: {e}")
        return []

def save_to_memory_system(chunks, embeddings, merge_with_existing):
    """Save chunks and embeddings to the memory system"""
    try:
        import numpy as np
        import faiss
        
        # Load existing data if merging
        existing_memories = []
        existing_metadata = {}
        
        if merge_with_existing:
            if os.path.exists("extract/agent_memories.json"):
                with open("extract/agent_memories.json", 'r', encoding='utf-8') as f:
                    existing_memories = json.load(f)
            
            if os.path.exists("extract/memory_metadata.json"):
                with open("extract/memory_metadata.json", 'r', encoding='utf-8') as f:
                    existing_metadata = json.load(f)
        
        # Combine memories
        all_memories = existing_memories + chunks
        
        # Create metadata
        metadata = {}
        for i, memory in enumerate(all_memories):
            metadata[f"mem-{i}"] = memory
        
        # Save memories and metadata
        with open("extract/agent_memories.json", 'w', encoding='utf-8') as f:
            json.dump(all_memories, f, indent=2, ensure_ascii=False)
        
        with open("extract/memory_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Build FAISS index
        if embeddings:
            # Load existing embeddings if merging
            existing_embeddings = []
            if merge_with_existing and os.path.exists("extract/faiss_index.bin"):
                try:
                    existing_index = faiss.read_index("extract/faiss_index.bin")
                    # Extract existing vectors (this is a simplified approach)
                    existing_embeddings = []
                    for i in range(len(existing_memories)):
                        # This is a placeholder - in practice, you'd need to store embeddings separately
                        pass
                except:
                    pass
            
            # Combine all embeddings
            all_embeddings = existing_embeddings + embeddings
            
            # Create FAISS index
            embeddings_array = np.array(all_embeddings, dtype=np.float32)
            dimension = embeddings_array.shape[1]
            
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings_array)
            
            # Save index
            faiss.write_index(index, "extract/faiss_index.bin")
        
        return {
            'total_memories': len(all_memories),
            'new_memories': len(chunks),
            'embeddings_created': len(embeddings)
        }
        
    except Exception as e:
        st.error(f"Error saving to memory system: {e}")
        return None

def display_processing_results(results):
    """Display processing results summary"""
    st.subheader("📊 Processing Results")
    
    # Create results dataframe
    results_df = pd.DataFrame(results)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_files = len(results)
        st.metric("Total Files", total_files)
    
    with col2:
        successful_files = len([r for r in results if r['status'] == 'success'])
        st.metric("Successful", successful_files)
    
    with col3:
        total_chunks = sum(r.get('chunks', 0) for r in results)
        st.metric("Total Chunks", total_chunks)
    
    with col4:
        total_embeddings = sum(r.get('embeddings', 0) for r in results)
        st.metric("Total Embeddings", total_embeddings)
    
    # Detailed results table
    st.dataframe(results_df, use_container_width=True)
    
    # Error details if any
    errors = [r for r in results if r['status'] == 'error']
    if errors:
        st.subheader("❌ Errors")
        for error in errors:
            st.error(f"**{error['file']}**: {error.get('error', 'Unknown error')}")

def render_processing_status_section():
    """Render current processing status"""
    if 'processing_sessions' not in st.session_state:
        return
    
    sessions = st.session_state.processing_sessions
    if not sessions:
        return
    
    st.subheader("📈 Processing Status")
    
    # Show recent sessions
    for session in sessions[:3]:  # Show last 3 sessions
        with st.expander(f"Session {session['id']} - {session['status'].title()}", 
                        expanded=(session['status'] == 'processing')):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Timestamp:** {session['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**Backend:** {session['backend']}")
                st.write(f"**Mode:** {session['mode']}")
            
            with col2:
                st.write(f"**Files:** {len(session['files'])}")
                if session.get('results'):
                    total_chunks = sum(r.get('chunks', 0) for r in session['results'])
                    st.write(f"**Total Chunks:** {total_chunks}")
            
            if session.get('results'):
                results_df = pd.DataFrame(session['results'])
                st.dataframe(results_df, use_container_width=True)

def render_file_management_section():
    """Render file management interface with delete functionality"""
    st.subheader("�️ eFile Management")
    
    # Load current memories to show files
    try:
        if os.path.exists("extract/agent_memories.json"):
            with open("extract/agent_memories.json", 'r', encoding='utf-8') as f:
                memories = json.load(f)
            
            # Group memories by original file
            files_dict = {}
            for i, memory in enumerate(memories):
                original_file = memory.get('original_file', 'Unknown')
                if original_file not in files_dict:
                    files_dict[original_file] = {
                        'memories': [],
                        'indices': [],
                        'file_type': memory.get('file_type', 'unknown'),
                        'source': memory.get('source', 'unknown'),
                        'total_chunks': 0,
                        'total_chars': 0
                    }
                
                files_dict[original_file]['memories'].append(memory)
                files_dict[original_file]['indices'].append(i)
                files_dict[original_file]['total_chunks'] += 1
                files_dict[original_file]['total_chars'] += len(memory.get('content', ''))
            
            if files_dict:
                st.write(f"**📊 Found {len(files_dict)} uploaded files with {len(memories)} total memories**")
                
                # File selection and actions
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    selected_files = st.multiselect(
                        "Select files to manage:",
                        options=list(files_dict.keys()),
                        help="Select one or more files to view details or delete"
                    )
                
                with col2:
                    st.write("**Actions:**")
                    if selected_files:
                        if st.button("🗑️ Delete Selected", type="secondary"):
                            delete_selected_files(selected_files, files_dict)
                        
                        if st.button("📊 View Details"):
                            st.session_state.show_file_details = selected_files
                
                # Show file details if selected
                if selected_files:
                    render_file_details(selected_files, files_dict)
                
                # Show detailed view if requested
                if st.session_state.get('show_file_details'):
                    render_detailed_file_view(st.session_state.show_file_details, files_dict)
            
            else:
                st.info("No uploaded files found in memory system")
        
        else:
            st.warning("No memory file found. Upload some files first!")
    
    except Exception as e:
        st.error(f"Error loading file management data: {e}")

def render_file_details(selected_files, files_dict):
    """Render details for selected files"""
    st.write("**📋 Selected Files Details:**")
    
    details_data = []
    for filename in selected_files:
        file_info = files_dict[filename]
        details_data.append({
            'Filename': filename,
            'Type': file_info['file_type'],
            'Chunks': file_info['total_chunks'],
            'Total Characters': f"{file_info['total_chars']:,}",
            'Source': file_info['source'],
            'Avg Chunk Size': f"{file_info['total_chars'] // file_info['total_chunks']:,}" if file_info['total_chunks'] > 0 else "0"
        })
    
    details_df = pd.DataFrame(details_data)
    st.dataframe(details_df, use_container_width=True)

def render_detailed_file_view(selected_files, files_dict):
    """Render detailed view of file contents"""
    st.subheader("🔍 Detailed File View")
    
    for filename in selected_files:
        with st.expander(f"📄 {filename}", expanded=len(selected_files) == 1):
            file_info = files_dict[filename]
            
            # File summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Chunks", file_info['total_chunks'])
            with col2:
                st.metric("Characters", f"{file_info['total_chars']:,}")
            with col3:
                st.metric("Type", file_info['file_type'])
            
            # Show first few chunks
            st.write("**📝 Content Preview (first 5 chunks):**")
            
            preview_chunks = file_info['memories'][:5]
            for i, chunk in enumerate(preview_chunks):
                with st.container():
                    st.write(f"**Chunk {i+1}:**")
                    content = chunk.get('content', '')
                    preview = content[:200] + "..." if len(content) > 200 else content
                    st.text_area(
                        f"Content {i+1}:",
                        value=preview,
                        height=100,
                        key=f"preview_{filename}_{i}",
                        disabled=True
                    )
            
            if len(file_info['memories']) > 5:
                st.info(f"... and {len(file_info['memories']) - 5} more chunks")
            
            # Individual chunk actions
            st.write("**🔧 Chunk Actions:**")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"🗑️ Delete All Chunks from {filename}", key=f"delete_all_{filename}"):
                    delete_file_chunks(filename, files_dict)
            
            with col2:
                if st.button(f"📥 Export {filename} Chunks", key=f"export_{filename}"):
                    export_file_chunks(filename, files_dict)

def delete_selected_files(selected_files, files_dict):
    """Delete selected files and their associated memories"""
    if not selected_files:
        st.warning("No files selected for deletion")
        return
    
    # Confirmation dialog
    st.warning(f"⚠️ You are about to delete {len(selected_files)} files and all their associated memories!")
    
    total_chunks = sum(files_dict[filename]['total_chunks'] for filename in selected_files)
    st.write(f"This will remove **{total_chunks}** memory chunks.")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("✅ Confirm Delete", type="primary", key="confirm_delete_files"):
            try:
                # Load current memories
                with open("extract/agent_memories.json", 'r', encoding='utf-8') as f:
                    memories = json.load(f)
                
                # Create backup
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"extract/agent_memories_delete_backup_{timestamp}.json"
                
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(memories, f, indent=2, ensure_ascii=False)
                
                # Get indices to remove
                indices_to_remove = set()
                for filename in selected_files:
                    indices_to_remove.update(files_dict[filename]['indices'])
                
                # Filter out memories
                filtered_memories = [
                    memory for i, memory in enumerate(memories) 
                    if i not in indices_to_remove
                ]
                
                # Save filtered memories
                with open("extract/agent_memories.json", 'w', encoding='utf-8') as f:
                    json.dump(filtered_memories, f, indent=2, ensure_ascii=False)
                
                # Update metadata
                metadata = {}
                for i, memory in enumerate(filtered_memories):
                    metadata[f"mem-{i}"] = memory
                
                with open("extract/memory_metadata.json", 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                # Clear cache
                if hasattr(st.session_state, 'memory_service'):
                    st.session_state.memory_service._memories = None
                    st.session_state.memory_service._metadata = None
                    st.session_state.memory_service._faiss_index = None
                
                st.success(f"✅ Successfully deleted {len(selected_files)} files ({total_chunks} chunks)")
                st.info(f"💾 Backup saved to: {backup_file}")
                st.warning("🔄 Remember to rebuild the FAISS index!")
                
                # Clear selection
                st.session_state.show_file_details = None
                st.rerun()
                
            except Exception as e:
                st.error(f"Error deleting files: {e}")

def delete_file_chunks(filename, files_dict):
    """Delete all chunks from a specific file"""
    try:
        # Load current memories
        with open("extract/agent_memories.json", 'r', encoding='utf-8') as f:
            memories = json.load(f)
        
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"extract/agent_memories_chunk_delete_backup_{timestamp}.json"
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(memories, f, indent=2, ensure_ascii=False)
        
        # Get indices to remove
        indices_to_remove = set(files_dict[filename]['indices'])
        
        # Filter out memories
        filtered_memories = [
            memory for i, memory in enumerate(memories) 
            if i not in indices_to_remove
        ]
        
        # Save filtered memories
        with open("extract/agent_memories.json", 'w', encoding='utf-8') as f:
            json.dump(filtered_memories, f, indent=2, ensure_ascii=False)
        
        # Update metadata
        metadata = {}
        for i, memory in enumerate(filtered_memories):
            metadata[f"mem-{i}"] = memory
        
        with open("extract/memory_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Clear cache
        if hasattr(st.session_state, 'memory_service'):
            st.session_state.memory_service._memories = None
            st.session_state.memory_service._metadata = None
            st.session_state.memory_service._faiss_index = None
        
        chunks_deleted = files_dict[filename]['total_chunks']
        st.success(f"✅ Successfully deleted {chunks_deleted} chunks from {filename}")
        st.info(f"💾 Backup saved to: {backup_file}")
        st.warning("🔄 Remember to rebuild the FAISS index!")
        
        # Clear selection and refresh
        st.session_state.show_file_details = None
        st.rerun()
        
    except Exception as e:
        st.error(f"Error deleting chunks: {e}")

def export_file_chunks(filename, files_dict):
    """Export chunks from a specific file"""
    try:
        file_info = files_dict[filename]
        
        # Prepare export data
        export_data = {
            'filename': filename,
            'export_timestamp': datetime.now().isoformat(),
            'total_chunks': file_info['total_chunks'],
            'file_type': file_info['file_type'],
            'chunks': file_info['memories']
        }
        
        # Convert to JSON string
        export_json = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        # Offer download
        st.download_button(
            label=f"📥 Download {filename} Export",
            data=export_json,
            file_name=f"{filename}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            key=f"download_{filename}"
        )
        
        st.success(f"✅ Export prepared for {filename} ({file_info['total_chunks']} chunks)")
        
    except Exception as e:
        st.error(f"Error exporting chunks: {e}")

def render_recent_uploads_section():
    """Render recent uploads and memory system status"""
    st.subheader("📚 Memory System Status")
    
    # Check if memory files exist
    memory_file = "extract/agent_memories.json"
    metadata_file = "extract/memory_metadata.json"
    faiss_file = "extract/faiss_index.bin"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if os.path.exists(memory_file):
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    memories = json.load(f)
                st.success(f"✅ Memories: {len(memories)}")
            except:
                st.error("❌ Memories: Error reading")
        else:
            st.warning("⚠️ Memories: Not found")
    
    with col2:
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                st.success(f"✅ Metadata: {len(metadata)}")
            except:
                st.error("❌ Metadata: Error reading")
        else:
            st.warning("⚠️ Metadata: Not found")
    
    with col3:
        if os.path.exists(faiss_file):
            try:
                import faiss
                index = faiss.read_index(faiss_file)
                st.success(f"✅ FAISS: {index.ntotal} vectors")
            except:
                st.error("❌ FAISS: Error reading")
        else:
            st.warning("⚠️ FAISS: Not found")
    
    # Quick actions
    st.markdown("---")
    st.write("**🔧 Quick Actions:**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Refresh Status"):
            st.rerun()
    
    with col2:
        if st.button("🧹 Clear Cache"):
            if hasattr(st.session_state, 'memory_service'):
                st.session_state.memory_service._memories = None
                st.session_state.memory_service._metadata = None
                st.session_state.memory_service._faiss_index = None
            st.success("Cache cleared!")
    
    with col3:
        if st.button("📊 View Statistics"):
            st.session_state.show_file_stats = True
    
    with col4:
        if st.button("🗑️ Bulk Delete"):
            st.session_state.show_bulk_delete = True
    
    # Bulk delete interface
    if st.session_state.get('show_bulk_delete', False):
        render_bulk_delete_interface()
    
    # File statistics
    if st.session_state.get('show_file_stats', False):
        render_file_statistics()

def render_bulk_delete_interface():
    """Render bulk delete interface"""
    st.subheader("�️ BulkP Delete Operations")
    
    try:
        if os.path.exists("extract/agent_memories.json"):
            with open("extract/agent_memories.json", 'r', encoding='utf-8') as f:
                memories = json.load(f)
            
            st.write(f"**Current Memory Count:** {len(memories)}")
            
            # Delete options
            st.write("**🎯 Delete Options:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                delete_by_source = st.checkbox("Delete by source pattern")
                if delete_by_source:
                    source_pattern = st.text_input(
                        "Source pattern to delete:",
                        placeholder="file_upload, conversation_log, etc.",
                        help="Delete all memories with sources containing this text"
                    )
                
                delete_by_file_type = st.checkbox("Delete by file type")
                if delete_by_file_type:
                    # Get available file types
                    file_types = set()
                    for memory in memories:
                        file_type = memory.get('file_type', 'unknown')
                        if file_type:
                            file_types.add(file_type)
                    
                    selected_types = st.multiselect(
                        "File types to delete:",
                        options=sorted(file_types),
                        help="Select file types to delete"
                    )
                
                delete_by_date = st.checkbox("Delete by date range")
                if delete_by_date:
                    col_start, col_end = st.columns(2)
                    with col_start:
                        start_date = st.date_input("Start date")
                    with col_end:
                        end_date = st.date_input("End date")
            
            with col2:
                delete_short_content = st.checkbox("Delete very short content (< 50 chars)")
                delete_low_importance = st.checkbox("Delete low importance (< 0.3)")
                delete_by_tags = st.checkbox("Delete by tags")
                
                if delete_by_tags:
                    # Get available tags
                    all_tags = set()
                    for memory in memories:
                        tags = memory.get('tags', [])
                        if isinstance(tags, list):
                            all_tags.update(tags)
                    
                    selected_tags = st.multiselect(
                        "Tags to delete:",
                        options=sorted(all_tags),
                        help="Delete memories containing these tags"
                    )
            
            # Preview deletion
            if st.button("👀 Preview Deletion", type="secondary"):
                preview_bulk_deletion(
                    memories,
                    delete_by_source, source_pattern if delete_by_source else None,
                    delete_by_file_type, selected_types if delete_by_file_type else [],
                    delete_by_date, (start_date, end_date) if delete_by_date else None,
                    delete_short_content,
                    delete_low_importance,
                    delete_by_tags, selected_tags if delete_by_tags else []
                )
            
            # Execute deletion
            st.markdown("---")
            st.warning("⚠️ **DANGER ZONE** - This action cannot be undone!")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🗑️ Execute Bulk Delete", type="primary"):
                    execute_bulk_deletion(
                        memories,
                        delete_by_source, source_pattern if delete_by_source else None,
                        delete_by_file_type, selected_types if delete_by_file_type else [],
                        delete_by_date, (start_date, end_date) if delete_by_date else None,
                        delete_short_content,
                        delete_low_importance,
                        delete_by_tags, selected_tags if delete_by_tags else []
                    )
            
            # Close button
            if st.button("❌ Close Bulk Delete"):
                st.session_state.show_bulk_delete = False
                st.rerun()
        
        else:
            st.info("No memory file found")
    
    except Exception as e:
        st.error(f"Error in bulk delete interface: {e}")

def preview_bulk_deletion(memories, delete_by_source, source_pattern, delete_by_file_type, selected_types,
                         delete_by_date, date_range, delete_short_content, delete_low_importance,
                         delete_by_tags, selected_tags):
    """Preview what would be deleted in bulk operation"""
    
    to_delete = []
    
    for i, memory in enumerate(memories):
        should_delete = False
        reasons = []
        
        # Check source pattern
        if delete_by_source and source_pattern:
            source = memory.get('source', '').lower()
            if source_pattern.lower() in source:
                should_delete = True
                reasons.append(f"Source contains '{source_pattern}'")
        
        # Check file type
        if delete_by_file_type and selected_types:
            file_type = memory.get('file_type', '')
            if file_type in selected_types:
                should_delete = True
                reasons.append(f"File type: {file_type}")
        
        # Check date range
        if delete_by_date and date_range:
            timestamp = memory.get('timestamp', 0)
            if timestamp:
                memory_date = datetime.fromtimestamp(timestamp).date()
                start_date, end_date = date_range
                if start_date <= memory_date <= end_date:
                    should_delete = True
                    reasons.append(f"Date in range: {memory_date}")
        
        # Check short content
        if delete_short_content:
            content = memory.get('content', '')
            if len(content) < 50:
                should_delete = True
                reasons.append("Very short content")
        
        # Check low importance
        if delete_low_importance:
            importance = memory.get('importance', 0)
            if isinstance(importance, (int, float)) and importance < 0.3:
                should_delete = True
                reasons.append("Low importance")
        
        # Check tags
        if delete_by_tags and selected_tags:
            memory_tags = memory.get('tags', [])
            if isinstance(memory_tags, list) and any(tag in memory_tags for tag in selected_tags):
                should_delete = True
                reasons.append(f"Contains tags: {[tag for tag in selected_tags if tag in memory_tags]}")
        
        if should_delete:
            to_delete.append({
                'index': i,
                'content_preview': memory.get('content', '')[:100] + '...' if len(memory.get('content', '')) > 100 else memory.get('content', ''),
                'source': memory.get('source', ''),
                'file_type': memory.get('file_type', ''),
                'reasons': ', '.join(reasons)
            })
    
    st.subheader(f"👀 Deletion Preview: {len(to_delete)} memories to delete")
    
    if to_delete:
        preview_df = pd.DataFrame(to_delete)
        st.dataframe(preview_df, use_container_width=True)
        
        st.info(f"📊 Would delete {len(to_delete)} out of {len(memories)} memories ({len(to_delete)/len(memories)*100:.1f}%)")
    else:
        st.success("✅ No memories match the deletion criteria")

def execute_bulk_deletion(memories, delete_by_source, source_pattern, delete_by_file_type, selected_types,
                         delete_by_date, date_range, delete_short_content, delete_low_importance,
                         delete_by_tags, selected_tags):
    """Execute bulk deletion operation"""
    
    try:
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"extract/agent_memories_bulk_delete_backup_{timestamp}.json"
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(memories, f, indent=2, ensure_ascii=False)
        
        # Filter memories
        filtered_memories = []
        deleted_count = 0
        
        for memory in memories:
            should_delete = False
            
            # Apply all deletion criteria
            if delete_by_source and source_pattern:
                source = memory.get('source', '').lower()
                if source_pattern.lower() in source:
                    should_delete = True
            
            if delete_by_file_type and selected_types:
                file_type = memory.get('file_type', '')
                if file_type in selected_types:
                    should_delete = True
            
            if delete_by_date and date_range:
                timestamp = memory.get('timestamp', 0)
                if timestamp:
                    memory_date = datetime.fromtimestamp(timestamp).date()
                    start_date, end_date = date_range
                    if start_date <= memory_date <= end_date:
                        should_delete = True
            
            if delete_short_content:
                content = memory.get('content', '')
                if len(content) < 50:
                    should_delete = True
            
            if delete_low_importance:
                importance = memory.get('importance', 0)
                if isinstance(importance, (int, float)) and importance < 0.3:
                    should_delete = True
            
            if delete_by_tags and selected_tags:
                memory_tags = memory.get('tags', [])
                if isinstance(memory_tags, list) and any(tag in memory_tags for tag in selected_tags):
                    should_delete = True
            
            if not should_delete:
                filtered_memories.append(memory)
            else:
                deleted_count += 1
        
        # Save filtered memories
        with open("extract/agent_memories.json", 'w', encoding='utf-8') as f:
            json.dump(filtered_memories, f, indent=2, ensure_ascii=False)
        
        # Update metadata
        metadata = {}
        for i, memory in enumerate(filtered_memories):
            metadata[f"mem-{i}"] = memory
        
        with open("extract/memory_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Clear cache
        if hasattr(st.session_state, 'memory_service'):
            st.session_state.memory_service._memories = None
            st.session_state.memory_service._metadata = None
            st.session_state.memory_service._faiss_index = None
        
        st.success(f"✅ Bulk deletion completed!")
        st.info(f"📊 Deleted {deleted_count} memories, kept {len(filtered_memories)}")
        st.info(f"💾 Backup saved to: {backup_file}")
        st.warning("🔄 Remember to rebuild the FAISS index!")
        
        # Close bulk delete interface
        st.session_state.show_bulk_delete = False
        st.rerun()
        
    except Exception as e:
        st.error(f"Error during bulk deletion: {e}")

def render_file_statistics():
    """Render detailed file statistics"""
    st.subheader("📊 File Processing Statistics")
    
    try:
        if os.path.exists("extract/agent_memories.json"):
            with open("extract/agent_memories.json", 'r', encoding='utf-8') as f:
                memories = json.load(f)
            
            # File type distribution
            file_types = {}
            sources = {}
            
            for memory in memories:
                file_type = memory.get('file_type', 'unknown')
                source = memory.get('source', 'unknown')
                
                file_types[file_type] = file_types.get(file_type, 0) + 1
                sources[source] = sources.get(source, 0) + 1
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**File Types:**")
                for file_type, count in sorted(file_types.items()):
                    st.write(f"- {file_type}: {count}")
            
            with col2:
                st.write("**Sources:**")
                for source, count in sorted(sources.items()):
                    st.write(f"- {source}: {count}")
            
            # Recent uploads
            recent_memories = sorted(memories, key=lambda x: x.get('timestamp', 0), reverse=True)[:10]
            
            st.write("**Recent Uploads:**")
            recent_df = pd.DataFrame([
                {
                    'File': m.get('original_file', 'Unknown'),
                    'Type': m.get('file_type', 'Unknown'),
                    'Content Preview': m.get('content', '')[:100] + '...' if len(m.get('content', '')) > 100 else m.get('content', ''),
                    'Timestamp': datetime.fromtimestamp(m.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M')
                }
                for m in recent_memories
            ])
            
            st.dataframe(recent_df, use_container_width=True)
            
        else:
            st.info("No memory data found")
            
    except Exception as e:
        st.error(f"Error loading statistics: {e}")

# Initialize session state
if 'processing_sessions' not in st.session_state:
    st.session_state.processing_sessions = []
if 'show_file_stats' not in st.session_state:
    st.session_state.show_file_stats = False
if 'show_file_details' not in st.session_state:
    st.session_state.show_file_details = None
if 'show_bulk_delete' not in st.session_state:
    st.session_state.show_bulk_delete = False