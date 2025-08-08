#!/usr/bin/env python3
"""
Advanced log viewer with filtering, search, and analysis capabilities.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from utils.log_viewer import load_logs, filter_reflect_logs

st.set_page_config(
    page_title="Advanced Log Viewer",
    page_icon="🔍",
    layout="wide"
)

def format_timestamp(timestamp_str):
    """Format timestamp for display."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp_str

def main():
    st.title("🔍 Advanced Log Viewer")
    
    # Load logs with caching
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def load_cached_logs():
        return load_logs()
    
    logs = load_cached_logs()
    
    if not logs:
        st.error("No logs found!")
        return
    
    st.success(f"Loaded {len(logs)} log entries")
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(logs)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Date range filter
    if 'timestamp' in df.columns:
        try:
            df['datetime'] = pd.to_datetime(df['timestamp'].str.replace('Z', '+00:00'))
            min_date = df['datetime'].min().to_pydatetime()
            max_date = df['datetime'].max().to_pydatetime()
            
            date_range = st.sidebar.date_input(
                "Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                df = df[(df['datetime'].dt.date >= start_date) & 
                       (df['datetime'].dt.date <= end_date)]
        except Exception as e:
            st.sidebar.warning(f"Could not parse dates: {e}")
    
    # Event type filter
    if 'event_type' in df.columns:
        event_types = ['All'] + sorted(df['event_type'].dropna().unique().tolist())
        selected_event = st.sidebar.selectbox("Event Type", event_types)
        if selected_event != 'All':
            df = df[df['event_type'] == selected_event]
    
    # Action filter
    if 'action' in df.columns:
        actions = ['All'] + sorted(df['action'].dropna().unique().tolist())
        selected_action = st.sidebar.selectbox("Action", actions)
        if selected_action != 'All':
            df = df[df['action'] == selected_action]
    
    # Search
    search_term = st.sidebar.text_input("Search in logs")
    if search_term:
        search_columns = ['event_type', 'action', 'data']
        search_columns = [col for col in search_columns if col in df.columns]
        
        if search_columns:
            mask = df[search_columns].apply(
                lambda x: x.astype(str).str.contains(search_term, case=False, na=False)
            ).any(axis=1)
            df = df[mask]
    
    # Show filtered results
    st.subheader(f"📊 Log Entries ({len(df)} filtered)")
    
    # Pagination
    items_per_page = st.sidebar.slider("Items per page", 10, 100, 25)
    total_pages = (len(df) - 1) // items_per_page + 1 if not df.empty else 1
    page = st.sidebar.number_input("Page", 1, total_pages, 1)
    
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    
    # Display the table
    if not df.empty:
        display_cols = ['timestamp', 'event_type', 'action']
        display_cols = [col for col in display_cols if col in df.columns]
        
        # Format timestamp for display
        if 'timestamp' in df.columns:
            df['timestamp'] = df['timestamp'].apply(format_timestamp)
        
        st.dataframe(
            df[display_cols].iloc[start_idx:end_idx],
            use_container_width=True,
            hide_index=True,
            column_config={
                "timestamp": "Timestamp",
                "event_type": "Event Type",
                "action": "Action"
            }
        )
        
        # Show pagination info
        st.caption(f"Showing {start_idx + 1} to {min(end_idx, len(df))} of {len(df)} entries")
        
        # Log details section
        st.subheader("📝 Log Details")
        
        if len(df) > 0:
            selected_idx = st.slider(
                "Select log entry",
                0, 
                min(len(df) - 1, items_per_page - 1),
                key="log_selector"
            )
            
            selected_log = df.iloc[start_idx + selected_idx].to_dict()
            
            # Show selected log details
            col1, col2 = st.columns(2)
            
            with col1:
                st.json({k: v for k, v in selected_log.items() if k != 'data'})
            
            with col2:
                if 'data' in selected_log and selected_log['data']:
                    st.subheader("Event Data")
                    st.json(selected_log['data'])
    else:
        st.warning("No logs match the current filters")
    
    # Add some basic statistics
    st.sidebar.header("📈 Statistics")
    if not df.empty:
        st.sidebar.metric("Total Logs", len(df))
        
        if 'event_type' in df.columns:
            st.sidebar.subheader("By Event Type")
            event_counts = df['event_type'].value_counts()
            st.sidebar.bar_chart(event_counts)
        
        if 'action' in df.columns:
            st.sidebar.subheader("By Action")
            action_counts = df['action'].value_counts()
            st.sidebar.bar_chart(action_counts)

if __name__ == "__main__":
    main()
