"""
Memory Management Tab Component
Provides editing, deletion, and bulk operations for memory entries
"""

import streamlit as st
import pandas as pd
import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any

def render_memory_management_tab():
    """Render the memory management tab"""
    
    st.header("🛠️ Memory Management")
    st.markdown("*Edit, delete, and manage Ray's memory entries*")
    
    # Check system status
    if not st.session_state.get('system_ready', False):
        st.error("❌ Memory system is not ready. Please ensure FAISS index and metadata files exist.")
        return
    
    memory_service = st.session_state.memory_service
    
    # Management options
    st.subheader("🔧 Management Options")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🗑️ Bulk Delete", help="Delete multiple low-value memories"):
            st.session_state.show_bulk_delete = True
    
    with col2:
        if st.button("✏️ Edit Memory", help="Edit individual memory entries"):
            st.session_state.show_edit_memory = True
    
    with col3:
        if st.button("🏷️ Manage Tags", help="Edit tags and importance scores"):
            st.session_state.show_tag_manager = True
    
    with col4:
        if st.button("🔄 Rebuild Index", help="Rebuild FAISS index after changes"):
            st.session_state.show_rebuild_index = True
    
    # Dangerous operations section
    st.markdown("---")
    st.subheader("⚠️ Dangerous Operations")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("💥 Delete ALL Memories", help="⚠️ DANGER: This will delete ALL memories permanently!", type="secondary"):
            st.session_state.show_delete_all = True
    
    with col2:
        st.warning("⚠️ **DANGER ZONE**: The button above will permanently delete ALL memories. Use with extreme caution!")
    
    # Display management interfaces based on selection
    if st.session_state.get('show_bulk_delete', False):
        render_bulk_delete_interface(memory_service)
    
    if st.session_state.get('show_edit_memory', False):
        render_edit_memory_interface(memory_service)
    
    if st.session_state.get('show_tag_manager', False):
        render_tag_manager_interface(memory_service)
    
    if st.session_state.get('show_rebuild_index', False):
        render_rebuild_index_interface(memory_service)
    
    if st.session_state.get('show_delete_all', False):
        render_delete_all_interface(memory_service)

def render_bulk_delete_interface(memory_service):
    """Render bulk delete interface for low-value memories"""
    st.subheader("🗑️ Bulk Delete Low-Value Memories")
    
    with st.spinner("Analyzing memories for bulk operations..."):
        try:
            memories = memory_service._load_memories()
            
            # Identify low-value memories
            low_value_memories = []
            for i, memory in enumerate(memories):
                content = str(memory.get('content', '')).lower()
                importance = memory.get('importance', 0)
                
                # Low-value criteria
                is_low_value = (
                    len(content) < 30 or  # Very short
                    any(pattern in content for pattern in ['yep', 'got it', 'sound good', 'okay', 'sure']) or
                    (isinstance(importance, (int, float)) and importance < 0.3)
                )
                
                if is_low_value:
                    low_value_memories.append({
                        'id': f"mem-{i}",
                        'index': i,
                        'content': memory.get('content', ''),
                        'source': memory.get('source', ''),
                        'importance': importance,
                        'length': len(content)
                    })
            
            st.info(f"Found {len(low_value_memories)} low-value memories out of {len(memories)} total")
            
            if low_value_memories:
                # Show preview of memories to delete
                st.subheader("📋 Memories Marked for Deletion")
                
                # Create DataFrame for display
                preview_data = []
                for mem in low_value_memories[:20]:  # Show first 20
                    preview_data.append({
                        'ID': str(mem['id']),
                        'Content': str(mem['content'][:100] + "..." if len(mem['content']) > 100 else mem['content']),
                        'Source': str(mem['source']),
                        'Length': str(mem['length']),
                        'Importance': f"{float(mem['importance']):.2f}" if mem['importance'] is not None else "0.00"
                    })
                
                preview_df = pd.DataFrame(preview_data)
                st.dataframe(preview_df, use_container_width=True)
                
                if len(low_value_memories) > 20:
                    st.info(f"Showing first 20 of {len(low_value_memories)} memories")
                
                # Confirmation and deletion
                st.warning("⚠️ This action cannot be undone!")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Confirm Bulk Delete", type="primary"):
                        delete_memories_bulk(memory_service, low_value_memories)
                
                with col2:
                    if st.button("❌ Cancel"):
                        st.session_state.show_bulk_delete = False
                        st.rerun()
            else:
                st.success("✅ No low-value memories found for deletion!")
                
        except Exception as e:
            st.error(f"Error analyzing memories: {e}")

def render_edit_memory_interface(memory_service):
    """Render interface for editing individual memories"""
    st.subheader("✏️ Edit Individual Memory")
    
    # Memory selection
    col1, col2 = st.columns([3, 1])
    with col1:
        memory_id = st.text_input("Memory ID to edit:", value="mem-6", help="Enter memory ID (e.g., mem-6)")
    with col2:
        if st.button("📝 Load for Editing"):
            st.session_state.edit_memory_id = memory_id
    
    # Load and edit memory
    if st.session_state.get('edit_memory_id'):
        edit_memory_id = st.session_state.edit_memory_id
        
        try:
            # Get memory from metadata
            metadata = memory_service._load_metadata()
            memory = metadata.get(edit_memory_id)
            
            if not memory:
                # Try to find in raw memories
                try:
                    idx = int(edit_memory_id.replace('mem-', ''))
                    memories = memory_service._load_memories()
                    if idx < len(memories):
                        memory = memories[idx]
                        st.info(f"Found memory at index {idx}")
                except:
                    pass
            
            if memory:
                st.success(f"✅ Editing {edit_memory_id}")
                
                # Edit form
                with st.form(f"edit_form_{edit_memory_id}"):
                    new_content = st.text_area("Content:", value=memory.get('content', ''), height=200)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        new_importance = st.slider("Importance:", 0.0, 1.0, float(memory.get('importance', 0.5)), 0.1)
                    with col2:
                        new_source = st.selectbox("Source:", ['agent_response', 'user_input'], 
                                                index=0 if memory.get('source') == 'agent_response' else 1)
                    
                    # Tags editing
                    current_tags = memory.get('tags', [])
                    if isinstance(current_tags, list):
                        tags_str = ', '.join(current_tags)
                    else:
                        tags_str = str(current_tags)
                    
                    new_tags_str = st.text_input("Tags (comma-separated):", value=tags_str)
                    
                    # Submit buttons
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.form_submit_button("💾 Save Changes", type="primary"):
                            save_memory_changes(memory_service, edit_memory_id, {
                                'content': new_content,
                                'importance': new_importance,
                                'source': new_source,
                                'tags': [tag.strip() for tag in new_tags_str.split(',') if tag.strip()]
                            })
                    
                    with col2:
                        if st.form_submit_button("🗑️ Delete Memory"):
                            delete_single_memory(memory_service, edit_memory_id)
                    
                    with col3:
                        if st.form_submit_button("❌ Cancel"):
                            st.session_state.edit_memory_id = None
                            st.rerun()
            else:
                st.error(f"Memory {edit_memory_id} not found")
                
        except Exception as e:
            st.error(f"Error loading memory for editing: {e}")

def render_tag_manager_interface(memory_service):
    """Render tag management interface"""
    st.subheader("🏷️ Tag Manager")
    
    with st.spinner("Loading tag information..."):
        try:
            memories = memory_service._load_memories()
            
            # Collect all tags
            all_tags = {}
            for i, memory in enumerate(memories):
                tags = memory.get('tags', [])
                if isinstance(tags, list):
                    for tag in tags:
                        if tag not in all_tags:
                            all_tags[tag] = []
                        all_tags[tag].append(f"mem-{i}")
            
            st.info(f"Found {len(all_tags)} unique tags across {len(memories)} memories")
            
            # Display tags
            if all_tags:
                tag_data = []
                for tag, memory_ids in all_tags.items():
                    tag_data.append({
                        'Tag': str(tag),
                        'Count': str(len(memory_ids)),
                        'Memory IDs': str(', '.join(memory_ids[:5]) + ('...' if len(memory_ids) > 5 else ''))
                    })
                
                tag_df = pd.DataFrame(tag_data)
                st.dataframe(tag_df, use_container_width=True)
                
                # Tag operations
                st.subheader("🔧 Tag Operations")
                
                col1, col2 = st.columns(2)
                with col1:
                    old_tag = st.selectbox("Select tag to rename:", list(all_tags.keys()))
                    new_tag = st.text_input("New tag name:")
                    if st.button("🔄 Rename Tag") and new_tag:
                        rename_tag_globally(memory_service, old_tag, new_tag)
                
                with col2:
                    delete_tag = st.selectbox("Select tag to delete:", list(all_tags.keys()), key="delete_tag")
                    if st.button("🗑️ Delete Tag"):
                        delete_tag_globally(memory_service, delete_tag)
            else:
                st.info("No tags found in the memory system")
                
        except Exception as e:
            st.error(f"Error loading tags: {e}")

def render_rebuild_index_interface(memory_service):
    """Render FAISS index rebuild interface"""
    st.subheader("🔄 Rebuild FAISS Index")
    
    st.info("Rebuild the FAISS index after making changes to memories")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Current Index Info:**")
        try:
            index = memory_service._get_faiss_index()
            st.write(f"- Entries: {index.ntotal}")
            st.write(f"- Dimension: {index.d}")
        except:
            st.write("- Index not loaded")
    
    with col2:
        st.write("**Embedding Backend:**")
        try:
            info = memory_service.get_embedding_info()
            st.write(f"- Backend: {info['backend']}")
            st.write(f"- Dimension: {info['dimension']}")
        except:
            st.write("- Backend not available")
    
    st.warning("⚠️ This process may take several minutes for large memory sets")
    
    if st.button("🔄 Rebuild Index", type="primary"):
        rebuild_faiss_index(memory_service)

# Helper functions for memory operations
def delete_memories_bulk(memory_service, memories_to_delete):
    """Delete multiple memories and update files"""
    try:
        with st.spinner(f"Deleting {len(memories_to_delete)} memories..."):
            # Load current data
            memories = memory_service._load_memories()
            metadata = memory_service._load_metadata()
            
            # Get indices to delete (sort in reverse to avoid index shifting)
            indices_to_delete = sorted([mem['index'] for mem in memories_to_delete], reverse=True)
            
            # Remove from memories list
            for idx in indices_to_delete:
                if idx < len(memories):
                    del memories[idx]
            
            # Remove from metadata
            for mem in memories_to_delete:
                if mem['id'] in metadata:
                    del metadata[mem['id']]
            
            # Save updated data
            save_memories_and_metadata(memories, metadata)
            
            st.success(f"✅ Successfully deleted {len(memories_to_delete)} memories!")
            st.info("🔄 Remember to rebuild the FAISS index")
            
            # Clear cache
            memory_service._memories = None
            memory_service._metadata = None
            
    except Exception as e:
        st.error(f"Error during bulk delete: {e}")

def save_memory_changes(memory_service, memory_id, changes):
    """Save changes to a specific memory"""
    try:
        with st.spinner("Saving changes..."):
            # Load current data
            memories = memory_service._load_memories()
            metadata = memory_service._load_metadata()
            
            # Update in memories list
            idx = int(memory_id.replace('mem-', ''))
            if idx < len(memories):
                memories[idx].update(changes)
                memories[idx]['last_modified'] = datetime.now().isoformat()
            
            # Update in metadata
            if memory_id in metadata:
                metadata[memory_id].update(changes)
                metadata[memory_id]['last_modified'] = datetime.now().isoformat()
            
            # Save updated data
            save_memories_and_metadata(memories, metadata)
            
            st.success(f"✅ Successfully updated {memory_id}!")
            
            # Clear cache
            memory_service._memories = None
            memory_service._metadata = None
            
    except Exception as e:
        st.error(f"Error saving changes: {e}")

def delete_single_memory(memory_service, memory_id):
    """Delete a single memory"""
    try:
        with st.spinner(f"Deleting {memory_id}..."):
            # Load current data
            memories = memory_service._load_memories()
            metadata = memory_service._load_metadata()
            
            # Remove from memories list
            idx = int(memory_id.replace('mem-', ''))
            if idx < len(memories):
                del memories[idx]
            
            # Remove from metadata
            if memory_id in metadata:
                del metadata[memory_id]
            
            # Save updated data
            save_memories_and_metadata(memories, metadata)
            
            st.success(f"✅ Successfully deleted {memory_id}!")
            st.info("🔄 Remember to rebuild the FAISS index")
            
            # Clear cache and editing state
            memory_service._memories = None
            memory_service._metadata = None
            st.session_state.edit_memory_id = None
            
    except Exception as e:
        st.error(f"Error deleting memory: {e}")

def save_memories_and_metadata(memories, metadata):
    """Save memories and metadata to files"""
    # Backup original files
    import shutil
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    shutil.copy("extract/agent_memories.json", f"extract/agent_memories_backup_{timestamp}.json")
    shutil.copy("extract/memory_metadata.json", f"extract/memory_metadata_backup_{timestamp}.json")
    
    # Save updated files
    with open("extract/agent_memories.json", 'w', encoding='utf-8') as f:
        json.dump(memories, f, indent=2, ensure_ascii=False)
    
    with open("extract/memory_metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

def rename_tag_globally(memory_service, old_tag, new_tag):
    """Rename a tag across all memories"""
    try:
        with st.spinner(f"Renaming tag '{old_tag}' to '{new_tag}'..."):
            memories = memory_service._load_memories()
            metadata = memory_service._load_metadata()
            
            count = 0
            # Update in memories
            for memory in memories:
                tags = memory.get('tags', [])
                if isinstance(tags, list) and old_tag in tags:
                    tags[tags.index(old_tag)] = new_tag
                    count += 1
            
            # Update in metadata
            for memory in metadata.values():
                tags = memory.get('tags', [])
                if isinstance(tags, list) and old_tag in tags:
                    tags[tags.index(old_tag)] = new_tag
            
            save_memories_and_metadata(memories, metadata)
            st.success(f"✅ Renamed tag in {count} memories!")
            
            # Clear cache
            memory_service._memories = None
            memory_service._metadata = None
            
    except Exception as e:
        st.error(f"Error renaming tag: {e}")

def delete_tag_globally(memory_service, tag_to_delete):
    """Delete a tag from all memories"""
    try:
        with st.spinner(f"Deleting tag '{tag_to_delete}'..."):
            memories = memory_service._load_memories()
            metadata = memory_service._load_metadata()
            
            count = 0
            # Remove from memories
            for memory in memories:
                tags = memory.get('tags', [])
                if isinstance(tags, list) and tag_to_delete in tags:
                    tags.remove(tag_to_delete)
                    count += 1
            
            # Remove from metadata
            for memory in metadata.values():
                tags = memory.get('tags', [])
                if isinstance(tags, list) and tag_to_delete in tags:
                    tags.remove(tag_to_delete)
            
            save_memories_and_metadata(memories, metadata)
            st.success(f"✅ Deleted tag from {count} memories!")
            
            # Clear cache
            memory_service._memories = None
            memory_service._metadata = None
            
    except Exception as e:
        st.error(f"Error deleting tag: {e}")

def rebuild_faiss_index(memory_service):
    """Rebuild the FAISS index from current memories"""
    try:
        with st.spinner("Rebuilding FAISS index..."):
            import numpy as np
            import faiss
            
            # Load current memories
            memories = memory_service._load_memories()
            
            # Get embedding manager
            embedding_manager = memory_service._get_embedding_manager()
            
            # Generate embeddings for all memories
            embeddings = []
            for i, memory in enumerate(memories):
                content = memory.get('content', '')
                if content:
                    vector = embedding_manager.embed(content)
                    embeddings.append(vector)
                    
                    # Progress update
                    if i % 100 == 0:
                        st.write(f"Processed {i}/{len(memories)} memories...")
            
            # Create new FAISS index
            if embeddings:
                embeddings_array = np.array(embeddings, dtype=np.float32)
                
                # Create index
                dimension = len(embeddings[0])
                index = faiss.IndexFlatL2(dimension)
                index.add(embeddings_array)
                
                # Save index
                faiss.write_index(index, "extract/faiss_index.bin")
                
                st.success(f"✅ Successfully rebuilt FAISS index with {len(embeddings)} entries!")
                st.info(f"Index dimension: {dimension}")
                
                # Clear cache
                memory_service._faiss_index = None
            else:
                st.error("No valid memories found to rebuild index")
                
    except Exception as e:
        st.error(f"Error rebuilding index: {e}")
        import traceback
        st.code(traceback.format_exc())

def render_delete_all_interface(memory_service):
    """Render the delete all memories interface with multiple confirmations"""
    st.subheader("💥 Delete ALL Memories")
    
    st.error("⚠️ **EXTREME DANGER ZONE** ⚠️")
    st.markdown("""
    **This action will:**
    - Delete ALL memory entries permanently
    - Remove the entire FAISS index
    - Clear all metadata
    - Reset Ray's memory system to empty state
    - **CANNOT BE UNDONE**
    """)
    
    # Get current memory count
    try:
        memories = memory_service._load_memories()
        memory_count = len(memories)
        
        st.info(f"📊 Current system contains **{memory_count:,} memories** that will be deleted")
        
        if memory_count == 0:
            st.success("✅ Memory system is already empty!")
            if st.button("❌ Cancel"):
                st.session_state.show_delete_all = False
                st.rerun()
            return
        
    except Exception as e:
        st.error(f"Error reading memory count: {e}")
        memory_count = "unknown"
    
    # Multiple confirmation steps
    st.markdown("---")
    st.subheader("🔐 Confirmation Steps")
    
    # Step 1: Checkbox confirmation
    confirm_understand = st.checkbox(
        "✅ I understand this will delete ALL memories permanently",
        help="Check this box to confirm you understand the consequences"
    )
    
    # Step 2: Type confirmation
    if confirm_understand:
        st.write("**Step 2:** Type `DELETE ALL MEMORIES` to confirm:")
        confirmation_text = st.text_input(
            "Confirmation text:",
            placeholder="Type: DELETE ALL MEMORIES",
            help="Type exactly: DELETE ALL MEMORIES"
        )
        
        text_confirmed = confirmation_text.strip() == "DELETE ALL MEMORIES"
        
        # Step 3: Final confirmation with memory count
        if text_confirmed:
            st.write(f"**Step 3:** Final confirmation - you are about to delete **{memory_count}** memories:")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(
                    "💥 YES, DELETE ALL", 
                    type="primary",
                    help=f"This will permanently delete all {memory_count} memories"
                ):
                    delete_all_memories(memory_service, memory_count)
            
            with col2:
                if st.button("❌ Cancel", help="Cancel and keep all memories"):
                    st.session_state.show_delete_all = False
                    st.rerun()
            
            with col3:
                st.write("") # Spacer
        
        elif confirmation_text.strip() and not text_confirmed:
            st.error("❌ Confirmation text doesn't match. Type exactly: `DELETE ALL MEMORIES`")
    
    # Always show cancel option
    if not confirm_understand:
        if st.button("❌ Cancel"):
            st.session_state.show_delete_all = False
            st.rerun()

def delete_all_memories(memory_service, memory_count):
    """Actually delete all memories with progress tracking"""
    try:
        with st.spinner("🗑️ Deleting all memories..."):
            # Create backup timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Step 1: Backup existing files
            st.write("📦 Creating backup files...")
            
            backup_files = []
            if os.path.exists("extract/agent_memories.json"):
                backup_path = f"extract/agent_memories_FULL_BACKUP_{timestamp}.json"
                shutil.copy("extract/agent_memories.json", backup_path)
                backup_files.append(backup_path)
            
            if os.path.exists("extract/memory_metadata.json"):
                backup_path = f"extract/memory_metadata_FULL_BACKUP_{timestamp}.json"
                shutil.copy("extract/memory_metadata.json", backup_path)
                backup_files.append(backup_path)
            
            if os.path.exists("extract/faiss_index.bin"):
                backup_path = f"extract/faiss_index_FULL_BACKUP_{timestamp}.bin"
                shutil.copy("extract/faiss_index.bin", backup_path)
                backup_files.append(backup_path)
            
            # Step 2: Delete memory files
            st.write("🗑️ Deleting memory files...")
            
            files_to_delete = [
                "extract/agent_memories.json",
                "extract/memory_metadata.json", 
                "extract/faiss_index.bin"
            ]
            
            for file_path in files_to_delete:
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # Step 3: Create empty files
            st.write("📝 Creating empty memory system...")
            
            # Create empty memories file
            with open("extract/agent_memories.json", 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)
            
            # Create empty metadata file
            with open("extract/memory_metadata.json", 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=2)
            
            # Create empty FAISS index (384 dimensions for MiniLM, 768 for Gemini)
            import faiss
            import numpy as np
            
            # Determine dimension based on backend
            backend = os.getenv('EMBEDDING_BACKEND', 'minilm')
            dimension = 768 if backend == 'gemini' else 384
            
            empty_index = faiss.IndexFlatL2(dimension)
            faiss.write_index(empty_index, "extract/faiss_index.bin")
            
            # Step 4: Clear cache
            st.write("🧹 Clearing system cache...")
            
            memory_service._memories = None
            memory_service._metadata = None
            memory_service._faiss_index = None
            
            # Clear session state
            if hasattr(st.session_state, 'memory_service'):
                st.session_state.memory_service._memories = None
                st.session_state.memory_service._metadata = None
                st.session_state.memory_service._faiss_index = None
            
            # Reset session state counters
            st.session_state.total_memories = 0
            st.session_state.agent_responses = 0
            st.session_state.user_queries = 0
            st.session_state.full_stats_loaded = False
            st.session_state.basic_stats_loaded = False
            
        # Success message
        st.success(f"✅ Successfully deleted all {memory_count} memories!")
        
        st.info("📦 **Backup files created:**")
        for backup_file in backup_files:
            st.write(f"- `{backup_file}`")
        
        st.info("🔄 **Memory system reset:**")
        st.write("- Empty memories file created")
        st.write("- Empty metadata file created") 
        st.write(f"- Empty FAISS index created ({dimension}D)")
        st.write("- System cache cleared")
        
        st.warning("🔄 **Refresh the dashboard** to see the empty system")
        
        # Auto-close the interface
        st.session_state.show_delete_all = False
        
        # Show refresh button
        if st.button("🔄 Refresh Dashboard"):
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Error during deletion: {e}")
        st.error("Some files may have been partially deleted. Check backup files.")
        import traceback
        st.code(traceback.format_exc())

# Initialize session state for this tab
if 'show_bulk_delete' not in st.session_state:
    st.session_state.show_bulk_delete = False
if 'show_edit_memory' not in st.session_state:
    st.session_state.show_edit_memory = False
if 'show_tag_manager' not in st.session_state:
    st.session_state.show_tag_manager = False
if 'show_rebuild_index' not in st.session_state:
    st.session_state.show_rebuild_index = False
if 'show_delete_all' not in st.session_state:
    st.session_state.show_delete_all = False
if 'edit_memory_id' not in st.session_state:
    st.session_state.edit_memory_id = None