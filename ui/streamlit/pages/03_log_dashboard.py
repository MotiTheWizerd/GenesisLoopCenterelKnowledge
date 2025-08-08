#!/usr/bin/env python3
"""
Main log dashboard with comprehensive log analysis and visualization.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path
import sys
from datetime import timezone

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from utils.log_viewer import load_logs, filter_reflect_logs

st.set_page_config(
    page_title="Log Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

def format_timestamp(timestamp_str):
    """Format timestamp for display."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, AttributeError):
        return timestamp_str

def parse_timestamps(logs):
    """Parse timestamps in logs and add timezone-aware datetime objects."""
    for log in logs:
        if 'timestamp' in log and log['timestamp']:
            try:
                # Parse timestamp and ensure it's timezone-aware
                dt = datetime.fromisoformat(
                    log['timestamp'].replace('Z', '+00:00')
                )
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                log['datetime'] = dt
            except (ValueError, AttributeError, TypeError) as e:
                print(f"Error parsing timestamp {log.get('timestamp')}: {e}")
                log['datetime'] = None
    return logs

def main():
    st.title("📊 Log Analytics Dashboard")
    
    # Load logs with caching
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def load_cached_logs():
        logs = load_logs()
        return parse_timestamps(logs) if logs else []
    
    logs = load_cached_logs()
    
    if not logs:
        st.error("No logs found!")
        return
    
    st.success(f"Loaded {len(logs)} log entries")
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(logs)
    
    # Ensure we have datetime column
    if 'datetime' not in df.columns:
        df['datetime'] = pd.to_datetime(df.get('timestamp', ''), errors='coerce')
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Date range filter
    if not df.empty and 'datetime' in df.columns and not df['datetime'].isna().all():
        # Ensure we have timezone-aware datetimes
        df['datetime'] = pd.to_datetime(df['datetime'], utc=True)
        
        # Get min/max dates for the date picker
        min_date = df['datetime'].min().to_pydatetime()
        max_date = df['datetime'].max().to_pydatetime()
        
        # Default to last 7 days
        default_end = max_date
        default_start = max(min_date, default_end - timedelta(days=7))
        
        date_range = st.sidebar.date_input(
            "Date Range",
            value=(default_start, default_end),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            # Convert to timezone-aware timestamps
            start_dt = pd.Timestamp(start_date).tz_localize('UTC')
            # Include the entire end date
            end_dt = pd.Timestamp(end_date + timedelta(days=1)).tz_localize('UTC')
            
            # Apply the filter
            mask = (df['datetime'] >= start_dt) & (df['datetime'] <= end_dt)
            df = df[mask]
    
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
    
    # Main metrics
    st.subheader("📈 Log Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Logs", len(df))
    
    with col2:
        if 'event_type' in df.columns:
            st.metric("Unique Event Types", df['event_type'].nunique())
    
    with col3:
        if 'action' in df.columns:
            st.metric("Unique Actions", df['action'].nunique())
    
    # Time series chart
    st.subheader("🕒 Log Activity Over Time")
    
    if not df.empty and 'datetime' in df.columns:
        time_series = df.set_index('datetime').resample('H').size()
        fig = px.line(
            time_series, 
            title='Log Entries per Hour',
            labels={'value': 'Number of Logs', 'datetime': 'Time'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Event type distribution
    st.subheader("📊 Event Type Distribution")
    
    if 'event_type' in df.columns:
        event_counts = df['event_type'].value_counts().reset_index()
        event_counts.columns = ['Event Type', 'Count']
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                event_counts.head(10),
                x='Event Type',
                y='Count',
                title='Top 10 Event Types'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.dataframe(
                event_counts,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Event Type": st.column_config.TextColumn("Event Type"),
                    "Count": st.column_config.NumberColumn("Count")
                }
            )
    
    # Recent logs table
    st.subheader("📝 Recent Log Entries")
    
    if not df.empty:
        # Select columns to display
        display_cols = ['timestamp', 'event_type', 'action']
        display_cols = [col for col in display_cols if col in df.columns]

        # Ensure 'datetime' exists before sorting
        if 'datetime' not in df.columns:
            st.warning("'datetime' column missing; skipping sorting.")
            sorted_df = df
        else:
            sorted_df = df.sort_values('datetime', ascending=False)

        # Format timestamp
        if 'timestamp' in df.columns:
            df['timestamp'] = df['timestamp'].apply(format_timestamp)

        # Display
        st.dataframe(
            sorted_df[display_cols].head(100),
            use_container_width=True,
            hide_index=True,
            column_config={
                "timestamp": "Timestamp",
                "event_type": "Event Type",
                "action": "Action"
            }
        )
    else:
        st.warning("No logs match the current filters")

if __name__ == "__main__":
    main()
