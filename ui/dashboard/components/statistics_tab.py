"""
Statistics Tab Component
Displays comprehensive memory system statistics and analytics
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from ui.dashboard.utils.session_state import refresh_statistics

def safe_balance_calculation(agent_responses, user_queries):
    """Safely calculate balance ratio avoiding division by zero"""
    if agent_responses == 0 and user_queries == 0:
        return 0
    max_val = max(agent_responses, user_queries)
    if max_val == 0:
        return 0
    return min(agent_responses, user_queries) / max_val

def render_statistics_tab():
    """Render the statistics and analytics tab"""
    
    st.header("📊 Memory System Statistics")
    
    # Check system status
    if not st.session_state.get('system_ready', False):
        st.error("❌ Memory system is not ready. Please ensure FAISS index and metadata files exist.")
        st.info("Run the embedding creation scripts first: `embed.py` or `create_memory_datase.py`")
        return
    
    # Refresh button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Refresh Stats"):
            refresh_statistics()
            st.rerun()
    
    # Get fresh statistics
    memory_service = st.session_state.memory_service
    try:
        stats = memory_service.get_memory_statistics()
    except Exception as e:
        st.error(f"Error loading statistics: {e}")
        return
    
    # Overview metrics
    st.subheader("📈 Overview Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Memories",
            value=f"{stats['total_memories']:,}",
            help="Total number of memory entries in the system"
        )
    
    with col2:
        st.metric(
            label="Agent Responses", 
            value=f"{stats['agent_responses']:,}",
            delta=f"{stats['agent_responses']/stats['total_memories']*100:.1f}%" if stats['total_memories'] > 0 else "0%",
            help="Number of agent response memories"
        )
    
    with col3:
        st.metric(
            label="User Queries",
            value=f"{stats['user_queries']:,}",
            delta=f"{stats['user_queries']/stats['total_memories']*100:.1f}%" if stats['total_memories'] > 0 else "0%",
            help="Number of user input memories"
        )
    
    with col4:
        st.metric(
            label="Avg Content Length",
            value=f"{stats['avg_content_length']:.0f} chars",
            help="Average character length of memory content"
        )
    
    # Memory distribution chart
    st.subheader("📊 Memory Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart for source distribution
        source_data = {
            'Agent Responses': stats['agent_responses'],
            'User Queries': stats['user_queries']
        }
        
        fig_pie = px.pie(
            values=list(source_data.values()),
            names=list(source_data.keys()),
            title="Memory Sources Distribution",
            color_discrete_map={
                'Agent Responses': '#1f77b4',
                'User Queries': '#ff7f0e'
            }
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # System information
        st.subheader("🔧 System Information")
        
        # File sizes and technical details
        faiss_size_mb = stats['faiss_index_size'] / (1024 * 1024)
        
        info_data = {
            "Metric": [
                "FAISS Index Size",
                "Metadata Entries", 
                "Total Content Length",
                "Embedding Dimension",
                "Search Model"
            ],
            "Value": [
                f"{faiss_size_mb:.2f} MB",
                f"{stats.get('metadata_entries', 0):,}",
                f"{stats.get('total_content_length', 0):,} chars",
                f"{stats.get('embedding_dimension', 384)} dimensions",
                "all-MiniLM-L6-v2"
            ]
        }
        
        info_df = pd.DataFrame(info_data)
        st.dataframe(info_df, hide_index=True, use_container_width=True)
    
    # Timeline analysis
    st.subheader("⏰ Memory Timeline")
    
    if stats['earliest_memory'] and stats['latest_memory']:
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Earliest Memory:** {stats['earliest_memory'][:19]}")
        
        with col2:
            st.info(f"**Latest Memory:** {stats['latest_memory'][:19]}")
        
        # Get recent memories for timeline visualization
        recent_memories = memory_service.get_recent_memories(limit=50)
        
        if recent_memories:
            # Create timeline data
            timeline_data = []
            for mem in recent_memories:
                if mem.get('timestamp'):
                    timeline_data.append({
                        'timestamp': datetime.fromtimestamp(mem['timestamp']),
                        'source': mem.get('source', 'unknown'),
                        'content_length': len(mem.get('content', ''))
                    })
            
            if timeline_data:
                timeline_df = pd.DataFrame(timeline_data)
                
                # Timeline scatter plot
                fig_timeline = px.scatter(
                    timeline_df,
                    x='timestamp',
                    y='content_length',
                    color='source',
                    title="Recent Memory Timeline (Last 50 entries)",
                    labels={
                        'timestamp': 'Time',
                        'content_length': 'Content Length (chars)',
                        'source': 'Memory Source'
                    },
                    color_discrete_map={
                        'agent_response': '#1f77b4',
                        'user_input': '#ff7f0e'
                    }
                )
                fig_timeline.update_layout(height=400)
                st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Advanced analytics
    st.subheader("🔍 Advanced Analytics")
    
    # Content length distribution
    memories = memory_service._load_memories()
    if memories:
        content_lengths = [len(mem.get('content', '')) for mem in memories]
        
        fig_hist = px.histogram(
            x=content_lengths,
            nbins=50,
            title="Content Length Distribution",
            labels={'x': 'Content Length (characters)', 'y': 'Frequency'}
        )
        fig_hist.update_layout(height=400)
        st.plotly_chart(fig_hist, use_container_width=True)
        
        # Content length statistics
        st.subheader("📏 Content Length Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Min Length", f"{min(content_lengths)} chars")
        with col2:
            st.metric("Max Length", f"{max(content_lengths)} chars")
        with col3:
            st.metric("Median Length", f"{sorted(content_lengths)[len(content_lengths)//2]} chars")
    
    # Memory health indicators
    st.subheader("🏥 System Health")
    
    health_col1, health_col2, health_col3 = st.columns(3)
    
    with health_col1:
        # Data completeness
        complete_memories = sum(1 for mem in memories if all([
            mem.get('content'),
            mem.get('source'),
            mem.get('timestamp')
        ]))
        completeness = (complete_memories / len(memories)) * 100 if memories else 0
        
        if completeness >= 95:
            st.success(f"✅ Data Completeness: {completeness:.1f}%")
        elif completeness >= 80:
            st.warning(f"⚠️ Data Completeness: {completeness:.1f}%")
        else:
            st.error(f"❌ Data Completeness: {completeness:.1f}%")
    
    with health_col2:
        # Source balance (fixed division by zero)
        if stats['total_memories'] > 0:
            balance_ratio = safe_balance_calculation(stats['agent_responses'], stats['user_queries'])
            balance_pct = balance_ratio * 100
            
            if balance_pct >= 30:
                st.success(f"✅ Source Balance: {balance_pct:.1f}%")
            elif balance_pct >= 15:
                st.warning(f"⚠️ Source Balance: {balance_pct:.1f}%")
            elif balance_pct > 0:
                st.error(f"❌ Source Balance: {balance_pct:.1f}%")
            else:
                st.info("📊 Source Balance: No data")
        else:
            st.info("📊 Source Balance: No memories")
    
    with health_col3:
        # System readiness
        if stats['system_ready']:
            st.success("✅ System Ready")
        else:
            st.error("❌ System Not Ready")