"""
Ray Memory Dashboard - Main Streamlit Application
Advanced dashboard for Ray's memory and embedding system
"""

import streamlit as st
import sys
import os

# Add project root to path for imports
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
project_root = os.path.abspath(project_root)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ui.dashboard.components.statistics_tab import render_statistics_tab
from ui.dashboard.components.query_tab import render_query_tab
from ui.dashboard.components.memory_explorer_tab import render_memory_explorer_tab
from ui.dashboard.components.memory_analysis_tab import render_memory_analysis_tab
from ui.dashboard.components.memory_management_tab import render_memory_management_tab
from ui.dashboard.components.timeline_tab import render_timeline_tab
from ui.dashboard.components.batch_operations_tab import render_batch_operations_tab
from ui.dashboard.components.file_processing_tab import render_file_processing_tab
from ui.dashboard.utils.session_state import initialize_session_state

def main():
    """Main dashboard application"""
    
    # Page configuration
    st.set_page_config(
        page_title="Ray Memory Dashboard",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Data type fixes applied in individual components to prevent PyArrow errors
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("🧠 Ray Memory Dashboard")
    st.markdown("*Advanced interface for Ray's consciousness and memory system*")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        st.markdown("---")
        
        # System status
        st.subheader("System Status")
        if st.session_state.get('system_ready', False):
            st.success("✅ Memory System Online")
        else:
            st.error("❌ Memory System Offline")
        
        st.markdown("---")
        
        # Quick stats (load on demand)
        st.subheader("Quick Stats")
        if st.session_state.get('system_ready', False):
            if not st.session_state.get('full_stats_loaded', False):
                if st.button("📊 Load Statistics"):
                    from ui.dashboard.utils.session_state import load_full_statistics
                    load_full_statistics()
                    st.rerun()
            else:
                st.metric("Total Memories", st.session_state.get('total_memories', 0))
                st.metric("Agent Responses", st.session_state.get('agent_responses', 0))
                st.metric("User Queries", st.session_state.get('user_queries', 0))
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📊 Statistics & Analytics", 
        "🔍 Memory Query", 
        "🗂️ Memory Explorer",
        "🧠 Memory Analysis",
        "🛠️ Memory Management",
        "📁 File Processing",
        "⏰ Timeline",
        "⚡ Batch Operations"
    ])
    
    with tab1:
        render_statistics_tab()
    
    with tab2:
        render_query_tab()
    
    with tab3:
        render_memory_explorer_tab()
    
    with tab4:
        render_memory_analysis_tab()
    
    with tab5:
        render_memory_management_tab()
    
    with tab6:
        render_file_processing_tab()
    
    with tab7:
        render_timeline_tab()
    
    with tab8:
        render_batch_operations_tab()

if __name__ == "__main__":
    main()