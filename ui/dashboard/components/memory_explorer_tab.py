"""
Memory Explorer Tab Component
Browse and explore Ray's memories in detail
"""

import streamlit as st
import pandas as pd
from datetime import datetime

def render_memory_explorer_tab():
    """Render the memory explorer tab"""
    
    st.header("🗂️ Memory Explorer")
    
    # Check system status
    if not st.session_state.get('system_ready', False):
        st.error("❌ Memory system is not ready. Please ensure FAISS index and metadata files exist.")
        return
    
    memory_service = st.session_state.memory_service
    
    # Explorer options
    st.subheader("🔧 Explorer Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        view_mode = st.selectbox(
            "View Mode",
            ["Recent Memories", "By Source", "By Memory ID", "Content Analysis"],
            help="Choose how to explore the memories"
        )
    
    with col2:
        if view_mode in ["Recent Memories", "By Source"]:
            limit = st.slider("Number of Results", 10, 100, 25)
        else:
            limit = 25
    
    with col3:
        if view_mode == "By Source":
            source_filter = st.selectbox(
                "Source Type",
                ["agent_response", "user_input"],
                help="Filter memories by source type"
            )
    
    # Display memories based on selected mode
    if view_mode == "Recent Memories":
        st.subheader("⏰ Most Recent Memories")
        memories = memory_service.get_recent_memories(limit=limit)
        _display_memory_list(memories, show_timestamps=True)
    
    elif view_mode == "By Source":
        st.subheader(f"📝 {source_filter.replace('_', ' ').title()} Memories")
        memories = memory_service.search_by_source(source_filter, limit=limit)
        _display_memory_list(memories, show_timestamps=True)
    
    elif view_mode == "By Memory ID":
        st.subheader("🔍 Search by Memory ID")
        
        memory_id = st.text_input(
            "Enter Memory ID (e.g., mem-123):",
            placeholder="mem-0",
            help="Enter the specific memory ID to view"
        )
        
        if memory_id:
            memory = memory_service.get_memory_by_id(memory_id)
            if memory:
                _display_single_memory(memory, memory_id)
            else:
                st.error(f"Memory with ID '{memory_id}' not found.")
    
    elif view_mode == "Content Analysis":
        st.subheader("📊 Content Analysis")
        _render_content_analysis(memory_service)

def _display_memory_list(memories, show_timestamps=False):
    """Display a list of memories"""
    
    if not memories:
        st.warning("No memories found matching the criteria.")
        return
    
    try:
        # Summary stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Memories", len(memories))
        
        with col2:
            try:
                avg_length = sum(len(str(mem.get('content', ''))) for mem in memories) / len(memories)
                st.metric("Avg Content Length", f"{avg_length:.0f} chars")
            except:
                st.metric("Avg Content Length", "N/A")
        
        with col3:
            agent_count = sum(1 for mem in memories if mem.get('source') == 'agent_response')
            st.metric("Agent Responses", agent_count)
        
        # Display memories
        for i, memory in enumerate(memories):
            try:
                # Safe content preview
                content_preview = str(memory.get('content', 'No content'))[:100]
                if len(content_preview) == 100:
                    content_preview += "..."
                
                with st.expander(f"Memory {i+1}: {content_preview}"):
                    _display_single_memory(memory, f"mem-{i}")
                    
            except Exception as e:
                st.error(f"Error displaying memory {i+1}: {e}")
                
    except Exception as e:
        st.error(f"Error displaying memory list: {e}")
        st.info("Try refreshing the page or check the memory data format.")

def _display_single_memory(memory, memory_id):
    """Display a single memory in detail"""
    
    try:
        # Header information
        col1, col2 = st.columns(2)
        
        with col1:
            source_emoji = "🤖" if memory.get('source') == 'agent_response' else "👤"
            source_name = memory.get('source', 'unknown').replace('_', ' ').title()
            st.markdown(f"**Source:** {source_emoji} {source_name}")
            
            if memory.get('timestamp'):
                try:
                    timestamp_str = datetime.fromtimestamp(memory['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
                    st.markdown(f"**Timestamp:** 🕒 {timestamp_str}")
                except (ValueError, OSError):
                    st.markdown(f"**Timestamp:** Invalid timestamp: {memory['timestamp']}")
        
        with col2:
            st.markdown(f"**Memory ID:** `{memory_id}`")
            content_length = len(memory.get('content', ''))
            st.markdown(f"**Content Length:** {content_length} characters")
        
        # Tags
        if memory.get('tags') and isinstance(memory['tags'], list):
            st.markdown("**Tags:** " + ", ".join(f"`{tag}`" for tag in memory['tags'] if tag))
        
        # Content
        st.markdown("**Content:**")
        content = memory.get('content', 'No content available')
        
        # Ensure content is a string
        if not isinstance(content, str):
            content = str(content)
        
        # Use text area for long content
        if len(content) > 500:
            st.text_area("Memory Content", content, height=200, disabled=True, label_visibility="collapsed")
        else:
            st.markdown(content)
        
        # Additional metadata
        if memory.get('importance'):
            st.markdown(f"**Importance:** {memory['importance']}")
        
        if memory.get('notes'):
            st.markdown(f"**Notes:** {memory['notes']}")
        
        # Memory type
        if memory.get('type'):
            st.markdown(f"**Type:** {memory['type']}")
            
    except Exception as e:
        st.error(f"Error displaying memory {memory_id}: {e}")
        st.json(memory)  # Show raw data as fallback

def _render_content_analysis(memory_service):
    """Render content analysis section"""
    
    memories = memory_service._load_memories()
    
    if not memories:
        st.warning("No memories available for analysis.")
        return
    
    # Content length analysis
    st.subheader("📏 Content Length Analysis")
    
    content_lengths = [len(mem.get('content', '')) for mem in memories]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Min Length", f"{min(content_lengths)} chars")
    
    with col2:
        st.metric("Max Length", f"{max(content_lengths)} chars")
    
    with col3:
        st.metric("Avg Length", f"{sum(content_lengths)/len(content_lengths):.0f} chars")
    
    with col4:
        st.metric("Total Content", f"{sum(content_lengths):,} chars")
    
    # Source distribution
    st.subheader("📊 Source Distribution")
    
    source_counts = {}
    for memory in memories:
        source = memory.get('source', 'unknown')
        source_counts[source] = source_counts.get(source, 0) + 1
    
    source_df = pd.DataFrame([
        {"Source": source, "Count": count, "Percentage": f"{count/len(memories)*100:.1f}%"}
        for source, count in source_counts.items()
    ])
    
    st.dataframe(source_df, hide_index=True, use_container_width=True)
    
    # Timeline analysis
    st.subheader("⏰ Timeline Analysis")
    
    timestamps = [mem.get('timestamp') for mem in memories if mem.get('timestamp')]
    
    if timestamps:
        earliest = min(timestamps)
        latest = max(timestamps)
        span_days = (latest - earliest) / (24 * 3600)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Earliest Memory", datetime.fromtimestamp(earliest).strftime("%Y-%m-%d"))
        
        with col2:
            st.metric("Latest Memory", datetime.fromtimestamp(latest).strftime("%Y-%m-%d"))
        
        with col3:
            st.metric("Time Span", f"{span_days:.1f} days")
    
    # Top content samples
    st.subheader("📝 Content Samples")
    
    # Longest memories
    longest_memories = sorted(memories, key=lambda x: len(x.get('content', '')), reverse=True)[:5]
    
    st.markdown("**Longest Memories:**")
    for i, memory in enumerate(longest_memories, 1):
        content_preview = memory.get('content', '')[:150] + "..." if len(memory.get('content', '')) > 150 else memory.get('content', '')
        source_emoji = "🤖" if memory.get('source') == 'agent_response' else "👤"
        st.markdown(f"{i}. {source_emoji} ({len(memory.get('content', ''))} chars): {content_preview}")
    
    # Search functionality within explorer
    st.subheader("🔍 Quick Search")
    
    search_term = st.text_input("Search in content:", placeholder="Enter keywords to search...")
    
    if search_term:
        matching_memories = [
            mem for mem in memories 
            if search_term.lower() in mem.get('content', '').lower()
        ]
        
        st.write(f"Found {len(matching_memories)} memories containing '{search_term}'")
        
        if matching_memories:
            for i, memory in enumerate(matching_memories[:10]):  # Show first 10 matches
                with st.expander(f"Match {i+1}: {memory.get('content', '')[:100]}..."):
                    _display_single_memory(memory, f"search-result-{i}")