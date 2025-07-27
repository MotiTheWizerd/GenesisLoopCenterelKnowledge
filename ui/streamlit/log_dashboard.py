#!/usr/bin/env python3
"""
Interactive Streamlit dashboard for viewing AI consciousness logs.
Completely separated from business logic.
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sys
from pathlib import Path

# Add project root to path to import utilities
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from utils.log_viewer import load_logs, filter_reflect_logs

# Page configuration
st.set_page_config(
    page_title="AI Consciousness Log Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

class LogDashboard:
    def __init__(self):
        self.logs = []
        self.filtered_logs = []
        
    def load_data(self):
        """Load logs from file."""
        self.logs = load_logs()
        return len(self.logs) > 0
    
    def filter_logs_by_type(self, log_type: str) -> List[Dict]:
        """Filter logs by type."""
        if log_type == "All Logs":
            return self.logs
        elif log_type == "Reflect Logs":
            return filter_reflect_logs(self.logs)
        elif log_type == "Heartbeat Logs":
            return [log for log in self.logs if log.get('action') != 'reflect' and 
                   'reflect' not in str(log.get('data', {}))]
        elif log_type == "Error Logs":
            return [log for log in self.logs if log.get('event_type') == 'error']
        else:
            return self.logs
    
    def filter_logs_by_time(self, logs: List[Dict], hours: int) -> List[Dict]:
        """Filter logs by time range."""
        if hours == 0:  # All time
            return logs
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        filtered = []
        
        for log in logs:
            try:
                log_time = datetime.fromisoformat(log.get('timestamp', '').replace('Z', '+00:00'))
                if log_time.replace(tzinfo=None) >= cutoff_time:
                    filtered.append(log)
            except:
                continue
                
        return filtered
    
    def format_log_for_display(self, log: Dict) -> Dict:
        """Format log entry for table display."""
        timestamp = log.get('timestamp', '')
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime('%H:%M:%S')
        except:
            formatted_time = timestamp
        
        event_type = log.get('event_type', '').replace('_', ' ').title()
        request_id = log.get('request_id', '')[:8]
        action = log.get('action', 'N/A')
        
        # Extract key information based on event type
        data = log.get('data', {})
        details = ""
        
        if log.get('event_type') == 'module_call' and data.get('module') == 'reflect':
            question = data.get('input_data', {}).get('question', 'N/A')
            depth = data.get('input_data', {}).get('depth', 'surface')
            details = f"Q: {question[:50]}... | Depth: {depth}"
        elif log.get('event_type') == 'module_response' and data.get('module') == 'reflect':
            output = data.get('output_data', {})
            reflection = output.get('reflection', '')
            details = f"Reflection: {reflection[:60]}..."
        elif 'function' in data:
            details = f"Function: {data['function']}"
        elif 'error' in data:
            details = f"Error: {data['error'][:50]}..."
        
        return {
            'Time': formatted_time,
            'Event': event_type,
            'Request ID': request_id,
            'Action': action,
            'Details': details
        }

def main():
    st.title("🧠 AI Consciousness Log Dashboard")
    st.markdown("Interactive viewer for AI consciousness and system logs")
    
    dashboard = LogDashboard()
    
    # Sidebar controls
    st.sidebar.header("🔧 Controls")
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Logs"):
        st.rerun()
    
    # Load data
    if not dashboard.load_data():
        st.error("❌ Could not load logs. Make sure the log file exists.")
        return
    
    st.sidebar.success(f"✅ Loaded {len(dashboard.logs)} log entries")
    
    # Log type filter
    log_types = ["All Logs", "Reflect Logs", "Heartbeat Logs", "Error Logs"]
    selected_type = st.sidebar.selectbox("📋 Log Type", log_types)
    
    # Time range filter
    time_ranges = {
        "All Time": 0,
        "Last Hour": 1,
        "Last 6 Hours": 6,
        "Last 24 Hours": 24,
        "Last Week": 168
    }
    selected_range = st.sidebar.selectbox("⏰ Time Range", list(time_ranges.keys()))
    
    # Event type filter
    all_event_types = list(set([log.get('event_type', '') for log in dashboard.logs]))
    selected_events = st.sidebar.multiselect(
        "🎯 Event Types", 
        all_event_types, 
        default=all_event_types
    )
    
    # Apply filters
    filtered_logs = dashboard.filter_logs_by_type(selected_type)
    filtered_logs = dashboard.filter_logs_by_time(filtered_logs, time_ranges[selected_range])
    filtered_logs = [log for log in filtered_logs if log.get('event_type') in selected_events]
    
    # Reverse for most recent first
    filtered_logs.reverse()
    
    # Main content area
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Total Logs", len(dashboard.logs))
    
    with col2:
        st.metric("🔍 Filtered Logs", len(filtered_logs))
    
    with col3:
        reflect_count = len(filter_reflect_logs(dashboard.logs))
        st.metric("🧠 Reflect Sessions", reflect_count)
    
    # Pagination
    st.subheader("📋 Log Entries")
    
    if not filtered_logs:
        st.warning("No logs match the current filters.")
        return
    
    # Pagination controls
    logs_per_page = st.selectbox("Logs per page", [10, 25, 50, 100], index=1)
    total_pages = (len(filtered_logs) - 1) // logs_per_page + 1
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        page = st.number_input(
            f"Page (1-{total_pages})", 
            min_value=1, 
            max_value=total_pages, 
            value=1
        )
    
    # Calculate pagination
    start_idx = (page - 1) * logs_per_page
    end_idx = start_idx + logs_per_page
    page_logs = filtered_logs[start_idx:end_idx]
    
    # Display logs in table format
    if page_logs:
        display_data = [dashboard.format_log_for_display(log) for log in page_logs]
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True)
        
        # Detailed view section
        st.subheader("🔍 Detailed View")
        
        # Select log for detailed view
        if len(page_logs) > 0:
            # Create a unique key for the selectbox to ensure proper reactivity
            selectbox_key = f"log_select_{page}_{len(page_logs)}"
            
            selected_idx = st.selectbox(
                "Select log entry for details", 
                range(len(page_logs)),
                format_func=lambda x: f"{display_data[x]['Time']} - {display_data[x]['Event']} - {display_data[x]['Request ID']}",
                key=selectbox_key
            )
            
            if selected_idx is not None:
                selected_log = page_logs[selected_idx]
                
                # Display selected log info
                st.info(f"**Selected:** {display_data[selected_idx]['Time']} - {display_data[selected_idx]['Event']} - Request ID: {display_data[selected_idx]['Request ID']}")
                
                # Display detailed log information
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📋 Basic Info")
                    basic_info = {
                        "timestamp": selected_log.get('timestamp'),
                        "event_type": selected_log.get('event_type'),
                        "request_id": selected_log.get('request_id'),
                        "action": selected_log.get('action')
                    }
                    st.json(basic_info)
                
                with col2:
                    st.subheader("📊 Data")
                    data = selected_log.get('data', {})
                    if data:
                        st.json(data)
                    else:
                        st.write("No data available")
                
                # Show metadata if available
                metadata = selected_log.get('metadata')
                if metadata:
                    st.subheader("📋 Metadata")
                    st.json(metadata)
                
                # Show full raw log
                with st.expander("🔍 Full Raw Log"):
                    st.json(selected_log)
    
    # Statistics section
    if st.sidebar.checkbox("📊 Show Statistics"):
        st.subheader("📈 Log Statistics")
        
        # Event type distribution
        event_counts = {}
        for log in filtered_logs:
            event_type = log.get('event_type', 'unknown')
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        if event_counts:
            st.bar_chart(event_counts)
        
        # Recent activity timeline
        if len(filtered_logs) > 0:
            st.subheader("⏰ Recent Activity")
            recent_logs = filtered_logs[:20]  # Last 20 entries
            
            timeline_data = []
            for log in recent_logs:
                try:
                    timestamp = datetime.fromisoformat(log.get('timestamp', '').replace('Z', '+00:00'))
                    timeline_data.append({
                        'Time': timestamp,
                        'Event': log.get('event_type', ''),
                        'Action': log.get('action', 'N/A')
                    })
                except:
                    continue
            
            if timeline_data:
                timeline_df = pd.DataFrame(timeline_data)
                st.dataframe(timeline_df, use_container_width=True)

if __name__ == "__main__":
    main()