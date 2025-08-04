"""
Query Tab Component
Interactive memory search and query interface
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from ui.dashboard.utils.session_state import add_to_query_history

def render_query_tab():
    """Render the memory query tab"""
    
    st.header("🔍 Memory Query Interface")
    
    # Check system status
    if not st.session_state.get('system_ready', False):
        st.error("❌ Memory system is not ready. Please ensure FAISS index and metadata files exist.")
        return
    
    memory_service = st.session_state.memory_service
    
    # Query input section
    st.subheader("💭 Ask Ray's Memory")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query_text = st.text_input(
            "Enter your query:",
            placeholder="What do you want to know about Ray's memories?",
            help="Use natural language to search through Ray's consciousness"
        )
    
    with col2:
        st.write("")  # Spacing
        search_button = st.button("🔍 Search", type="primary")
    
    # Advanced search options
    with st.expander("⚙️ Advanced Search Options"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            initial_k = st.slider(
                "Initial Results (FAISS)",
                min_value=5,
                max_value=50,
                value=20,
                help="Number of initial results from semantic search"
            )
        
        with col2:
            final_k = st.slider(
                "Final Results (Reranked)",
                min_value=1,
                max_value=10,
                value=3,
                help="Number of final results after reranking"
            )
        
        with col3:
            show_scores = st.checkbox(
                "Show Relevance Scores",
                value=True,
                help="Display FAISS and reranking scores"
            )
    
    # Perform search
    if search_button and query_text.strip():
        with st.spinner("🧠 Searching Ray's memories..."):
            try:
                results = memory_service.perform_semantic_search(
                    query_text.strip(),
                    initial_k=initial_k,
                    final_k=final_k
                )
                
                st.session_state.current_results = results
                add_to_query_history(query_text.strip(), results)
                
            except Exception as e:
                st.error(f"Error during search: {e}")
                st.info("Please check that the memory system files exist and are properly formatted.")
    
    # Display results
    if st.session_state.get('current_results'):
        results = st.session_state.current_results
        
        st.subheader(f"📋 Search Results ({len(results)} found)")
        
        if not results:
            st.warning("No relevant memories found. Try a different query or check if the memory system is properly initialized.")
        else:
            # Results summary
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_rerank_score = sum(r.get('rerank_score', 0) for r in results) / len(results)
                st.metric("Avg Relevance", f"{avg_rerank_score:.3f}")
            
            with col2:
                agent_responses = sum(1 for r in results if r.get('source') == 'agent_response')
                st.metric("Agent Responses", agent_responses)
            
            with col3:
                avg_content_length = sum(len(r.get('content', '')) for r in results) / len(results)
                st.metric("Avg Length", f"{avg_content_length:.0f} chars")
            
            # Display each result
            for i, result in enumerate(results, 1):
                with st.container():
                    # Result header
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.markdown(f"### 🎯 Result {i}")
                    
                    with col2:
                        source_emoji = "🤖" if result.get('source') == 'agent_response' else "👤"
                        st.markdown(f"{source_emoji} **{result.get('source', 'unknown').replace('_', ' ').title()}**")
                    
                    with col3:
                        if result.get('timestamp'):
                            timestamp_str = datetime.fromtimestamp(result['timestamp']).strftime("%Y-%m-%d %H:%M")
                            st.markdown(f"🕒 {timestamp_str}")
                    
                    # Scores (if enabled)
                    if show_scores:
                        score_col1, score_col2, score_col3 = st.columns(3)
                        
                        with score_col1:
                            if 'rerank_score' in result:
                                st.metric("Rerank Score", f"{result['rerank_score']:.4f}")
                        
                        with score_col2:
                            if 'faiss_score' in result:
                                st.metric("FAISS Distance", f"{result['faiss_score']:.4f}")
                        
                        with score_col3:
                            st.metric("Content Length", f"{len(result.get('content', ''))} chars")
                    
                    # Content
                    content = result.get('content', 'No content available')
                    
                    # Truncate very long content
                    if len(content) > 1000:
                        with st.expander(f"📄 Content Preview ({len(content)} characters)"):
                            st.markdown(content[:500] + "...")
                            st.markdown("---")
                            st.markdown(content)
                    else:
                        st.markdown("**Content:**")
                        st.markdown(content)
                    
                    # Tags and metadata
                    if result.get('tags'):
                        st.markdown("**Tags:** " + ", ".join(f"`{tag}`" for tag in result['tags']))
                    
                    # Memory ID
                    st.markdown(f"**Memory ID:** `{result.get('id', 'unknown')}`")
                    
                    st.markdown("---")
    
    # Query history sidebar
    st.subheader("📚 Recent Queries")
    
    if st.session_state.get('query_history'):
        history_df = pd.DataFrame(st.session_state.query_history)
        history_df = history_df.sort_values('timestamp', ascending=False)
        
        # Display recent queries
        for _, query_record in history_df.head(5).iterrows():
            with st.expander(f"🔍 {query_record['query'][:50]}..."):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Results:** {query_record['results_count']}")
                with col2:
                    st.write(f"**Time:** {query_record['timestamp'][:19]}")
                
                if st.button(f"Repeat Query", key=f"repeat_{query_record['timestamp']}"):
                    st.session_state.current_results = memory_service.perform_semantic_search(
                        query_record['query'],
                        initial_k=initial_k,
                        final_k=final_k
                    )
                    st.rerun()
    else:
        st.info("No queries yet. Start searching to build your query history!")
    
    # Quick search suggestions
    st.subheader("💡 Quick Search Suggestions")
    
    suggestions = [
        "What is consciousness?",
        "How does Ray think about AI?",
        "Google Drive integration",
        "Memory and embedding systems",
        "Ray's personality and responses",
        "Technical discussions about APIs"
    ]
    
    suggestion_cols = st.columns(3)
    for i, suggestion in enumerate(suggestions):
        with suggestion_cols[i % 3]:
            if st.button(f"💭 {suggestion}", key=f"suggestion_{i}"):
                st.session_state.current_results = memory_service.perform_semantic_search(
                    suggestion,
                    initial_k=initial_k,
                    final_k=final_k
                )
                add_to_query_history(suggestion, st.session_state.current_results)
                st.rerun()