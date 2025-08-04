"""
Session State Management for Ray Memory Dashboard
"""

import streamlit as st
import sys
import os

# Add project root to path if not already there
project_root = os.path.join(os.path.dirname(__file__), '..', '..', '..')
project_root = os.path.abspath(project_root)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from services.memory_service import MemoryService

def initialize_session_state():
    """Initialize Streamlit session state variables with fast loading"""
    
    # Initialize memory service
    if 'memory_service' not in st.session_state:
        # Get backend from environment or use default
        backend = os.getenv('EMBEDDING_BACKEND', 'minilm')
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if backend == 'gemini' and gemini_api_key:
            st.session_state.memory_service = MemoryService(backend="gemini", gemini_api_key=gemini_api_key)
        else:
            st.session_state.memory_service = MemoryService(backend="minilm")
    
    # System status (quick check)
    if 'system_ready' not in st.session_state:
        st.session_state.system_ready = st.session_state.memory_service.is_system_ready()
    
    # Basic statistics only (fast)
    if 'basic_stats_loaded' not in st.session_state:
        try:
            basic_stats = st.session_state.memory_service.get_basic_statistics()
            st.session_state.system_ready = basic_stats.get('system_ready', False)
            st.session_state.basic_stats_loaded = True
            
            # Set basic values if system is ready
            if st.session_state.system_ready:
                st.session_state.total_memories = basic_stats.get('total_memories', 0)
                st.session_state.agent_responses = basic_stats.get('agent_responses', 0)
                st.session_state.user_queries = basic_stats.get('user_queries', 0)
            else:
                st.session_state.total_memories = 0
                st.session_state.agent_responses = 0
                st.session_state.user_queries = 0
                
        except Exception as e:
            print(f"Error loading basic statistics: {e}")
            st.session_state.system_ready = False
            st.session_state.basic_stats_loaded = True
            st.session_state.total_memories = 0
            st.session_state.agent_responses = 0
            st.session_state.user_queries = 0
    
    # Query history
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    
    # Current query results
    if 'current_results' not in st.session_state:
        st.session_state.current_results = None
    
    # Full stats loading flag
    if 'full_stats_loaded' not in st.session_state:
        st.session_state.full_stats_loaded = False

def load_full_statistics():
    """Load full statistics (slower operation)"""
    if not st.session_state.get('full_stats_loaded', False):
        with st.spinner("Loading memory statistics..."):
            stats = st.session_state.memory_service.get_memory_statistics()
            st.session_state.total_memories = stats.get('total_memories', 0)
            st.session_state.agent_responses = stats.get('agent_responses', 0)
            st.session_state.user_queries = stats.get('user_queries', 0)
            st.session_state.full_stats_loaded = True

def refresh_statistics():
    """Refresh memory statistics in session state"""
    st.session_state.full_stats_loaded = False
    load_full_statistics()

def add_to_query_history(query, results):
    """Add query and results to history"""
    st.session_state.query_history.append({
        'query': query,
        'results_count': len(results) if results else 0,
        'timestamp': st.session_state.memory_service.get_current_timestamp()
    })
    
    # Keep only last 10 queries
    if len(st.session_state.query_history) > 10:
        st.session_state.query_history = st.session_state.query_history[-10:]