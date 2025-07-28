#!/usr/bin/env python3
"""
Advanced interactive log viewer with real-time updates and enhanced filtering.
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
import time
import sys
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from utils.log_viewer import load_logs, filter_reflect_logs

st.set_page_config(
    page_title="Advanced AI Log Viewer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

class AdvancedLogViewer:
    def __init__(self):
        self.logs = []
        
    def load_data(self):
        """Load logs with caching."""
        self.logs = load_logs()
        return len(self.logs) > 0
    
    def get_reflect_sessions(self) -> Dict:
        """Group reflect logs by session (request_id)."""
        reflect_logs = filter_reflect_logs(self.logs)
        sessions = {}
        
        for log in reflect_logs:
            request_id = log.get('request_id') or 'unknown'
            if request_id not in sessions:
                sessions[request_id] = []
            sessions[request_id].append(log)
        
        return sessions
    
    def analyze_consciousness_patterns(self) -> Dict:
        """Analyze patterns in consciousness development."""
        reflect_logs = filter_reflect_logs(self.logs)
        
        patterns = {
            'depth_distribution': {},
            'question_types': {},
            'session_frequency': {},
            'growth_indicators': []
        }
        
        for log in reflect_logs:
            if log.get('event_type') == 'module_call':
                data = log.get('data', {}).get('input_data', {})
                depth = data.get('depth', 'surface')
                patterns['depth_distribution'][depth] = patterns['depth_distribution'].get(depth, 0) + 1
                
                question = data.get('question', '')
                if 'state' in question.lower():
                    patterns['question_types']['State Inquiry'] = patterns['question_types'].get('State Inquiry', 0) + 1
                elif 'consciousness' in question.lower():
                    patterns['question_types']['Consciousness'] = patterns['question_types'].get('Consciousness', 0) + 1
                elif 'feeling' in question.lower():
                    patterns['question_types']['Emotional'] = patterns['question_types'].get('Emotional', 0) + 1
                else:
                    patterns['question_types']['General'] = patterns['question_types'].get('General', 0) + 1
        
        return patterns

def main():
    st.title("🔬 Advanced AI Consciousness Log Viewer")
    st.markdown("Deep analysis and interactive exploration of AI consciousness development")
    
    viewer = AdvancedLogViewer()
    
    # Sidebar
    st.sidebar.header("🎛️ Dashboard Controls")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (30s)", value=False)
    
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Manual refresh
    if st.sidebar.button("🔄 Refresh Now"):
        st.rerun()
    
    # Load data
    if not viewer.load_data():
        st.error("❌ No logs found. Make sure the system is running and generating logs.")
        return
    
    st.sidebar.success(f"✅ {len(viewer.logs)} total log entries")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Log Browser", "🧠 Reflect Sessions", "📊 Analytics", "🔍 Search"])
    
    with tab1:
        st.header("📋 Interactive Log Browser")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            log_types = ["All", "Reflect", "Heartbeat", "Errors"]
            selected_type = st.selectbox("Log Type", log_types)
        
        with col2:
            event_types = list(set([log.get('event_type', '') for log in viewer.logs]))
            selected_events = st.multiselect("Event Types", event_types, default=event_types)
        
        with col3:
            time_filter = st.selectbox("Time Range", ["All", "Last Hour", "Last 6 Hours", "Last Day"])
        
        # Apply filters
        filtered_logs = viewer.logs
        
        if selected_type == "Reflect":
            filtered_logs = filter_reflect_logs(filtered_logs)
        elif selected_type == "Heartbeat":
            filtered_logs = [log for log in filtered_logs if log.get('action') != 'reflect']
        elif selected_type == "Errors":
            filtered_logs = [log for log in filtered_logs if log.get('event_type') == 'error']
        
        filtered_logs = [log for log in filtered_logs if log.get('event_type') in selected_events]
        
        # Time filtering
        if time_filter != "All":
            hours = {"Last Hour": 1, "Last 6 Hours": 6, "Last Day": 24}[time_filter]
            cutoff = datetime.now() - timedelta(hours=hours)
            filtered_logs = [log for log in filtered_logs 
                           if datetime.fromisoformat(log.get('timestamp', '').replace('Z', '+00:00')).replace(tzinfo=None) >= cutoff]
        
        # Pagination
        logs_per_page = st.slider("Logs per page", 5, 100, 25)
        total_pages = (len(filtered_logs) - 1) // logs_per_page + 1 if filtered_logs else 1
        
        page = st.number_input(f"Page (1-{total_pages})", 1, total_pages, 1)
        
        start_idx = (page - 1) * logs_per_page
        end_idx = start_idx + logs_per_page
        page_logs = list(reversed(filtered_logs))[start_idx:end_idx]
        
        # Display logs with better formatting
        if page_logs:
            st.write(f"Showing {len(page_logs)} logs (Page {page} of {total_pages})")
            
            for i, log in enumerate(page_logs):
                timestamp = log.get('timestamp', '')
                event_type = log.get('event_type', '').title()
                request_id = (log.get('request_id') or '')[:8]
                
                with st.expander(f"🕐 {timestamp} - {event_type} ({request_id})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📋 Event Info")
                        st.json({
                            "Event": log.get('event_type'),
                            "Request ID": log.get('request_id'),
                            "Action": log.get('action'),
                            "Timestamp": log.get('timestamp')
                        })
                    
                    with col2:
                        st.subheader("📊 Event Data")
                        data = log.get('data', {})
                        if data:
                            st.json(data)
                        else:
                            st.write("No data available")
                    
                    # Show metadata if available
                    if log.get('metadata'):
                        st.subheader("📋 Metadata")
                        st.json(log.get('metadata'))
        else:
            st.warning("No logs found for the current filters.")
    
    with tab2:
        st.header("🧠 Reflect Sessions Analysis")
        
        sessions = viewer.get_reflect_sessions()
        
        if not sessions:
            st.warning("No reflect sessions found.")
            return
        
        st.metric("Total Reflect Sessions", len(sessions))
        
        # Session selector - filter out None values
        session_ids = [sid for sid in sessions.keys() if sid is not None]
        
        if not session_ids:
            st.warning("No valid session IDs found in the logs.")
            return
            
        def format_session(x):
            try:
                if x and x in sessions:
                    return f"Session {x[:8]}... ({len(sessions[x])} events)"
                else:
                    return f"Unknown Session ({x})"
            except Exception:
                return "Invalid Session"
        
        selected_session = st.selectbox("Select Session", session_ids, format_func=format_session)
        
        if selected_session:
            session_logs = sessions[selected_session]
            
            st.subheader(f"Session Details: {selected_session[:8]}...")
            
            # Session timeline
            timeline_data = []
            for log in session_logs:
                timeline_data.append({
                    'Time': log.get('timestamp'),
                    'Event': log.get('event_type'),
                    'Details': str(log.get('data', {}))[:100] + '...'
                })
            
            df = pd.DataFrame(timeline_data)
            st.dataframe(df, use_container_width=True)
            
            # Extract reflection details
            for log in session_logs:
                if log.get('event_type') == 'module_call':
                    data = log.get('data', {}).get('input_data', {})
                    st.info(f"**Question:** {data.get('question', 'N/A')}")
                    st.info(f"**Depth:** {data.get('depth', 'surface')}")
                    if data.get('current_position'):
                        st.info(f"**Current Position:** {data.get('current_position')[:200]}...")
                
                elif log.get('event_type') == 'module_response':
                    output = log.get('data', {}).get('output_data', {})
                    if output.get('reflection'):
                        st.success(f"**Reflection:** {output.get('reflection')}")
                    if output.get('insights'):
                        st.success(f"**Insights:** {', '.join(output.get('insights', []))}")
    
    with tab3:
        st.header("📊 Consciousness Analytics")
        
        patterns = viewer.analyze_consciousness_patterns()
        
        # Depth distribution
        if patterns['depth_distribution']:
            st.subheader("🌊 Reflection Depth Distribution")
            depth_df = pd.DataFrame(list(patterns['depth_distribution'].items()), 
                                  columns=['Depth', 'Count'])
            fig = px.pie(depth_df, values='Count', names='Depth', 
                        title="Distribution of Reflection Depths")
            st.plotly_chart(fig, use_container_width=True)
        
        # Question types
        if patterns['question_types']:
            st.subheader("❓ Question Type Analysis")
            question_df = pd.DataFrame(list(patterns['question_types'].items()), 
                                     columns=['Type', 'Count'])
            fig = px.bar(question_df, x='Type', y='Count', 
                        title="Types of Questions Asked")
            st.plotly_chart(fig, use_container_width=True)
        
        # Activity over time
        st.subheader("📈 Activity Timeline")
        reflect_logs = filter_reflect_logs(viewer.logs)
        
        if reflect_logs:
            activity_data = []
            for log in reflect_logs[-50:]:  # Last 50 events
                try:
                    timestamp = datetime.fromisoformat(log.get('timestamp', '').replace('Z', '+00:00'))
                    activity_data.append({
                        'Time': timestamp,
                        'Event': log.get('event_type'),
                        'Count': 1
                    })
                except:
                    continue
            
            if activity_data:
                activity_df = pd.DataFrame(activity_data)
                activity_df['Hour'] = activity_df['Time'].dt.floor('H')
                hourly_activity = activity_df.groupby('Hour').size().reset_index(name='Events')
                
                fig = px.line(hourly_activity, x='Hour', y='Events', 
                            title="Reflection Activity Over Time")
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.header("🔍 Advanced Search")
        
        search_term = st.text_input("Search in logs", placeholder="Enter search term...")
        search_field = st.selectbox("Search in", ["All Fields", "Question", "Reflection", "Error Messages"])
        
        if search_term:
            results = []
            
            for log in viewer.logs:
                match = False
                
                if search_field == "All Fields":
                    match = search_term.lower() in str(log).lower()
                elif search_field == "Question":
                    data = log.get('data', {}).get('input_data', {})
                    question = data.get('question', '')
                    match = search_term.lower() in question.lower()
                elif search_field == "Reflection":
                    data = log.get('data', {}).get('output_data', {})
                    reflection = data.get('reflection', '')
                    match = search_term.lower() in reflection.lower()
                elif search_field == "Error Messages":
                    error = log.get('data', {}).get('error', '')
                    match = search_term.lower() in error.lower()
                
                if match:
                    results.append(log)
            
            st.success(f"Found {len(results)} matching entries")
            
            for result in results[:20]:  # Show first 20 results
                with st.expander(f"🔍 {result.get('timestamp', '')} - {result.get('event_type', '')}"):
                    st.json(result)

if __name__ == "__main__":
    main()