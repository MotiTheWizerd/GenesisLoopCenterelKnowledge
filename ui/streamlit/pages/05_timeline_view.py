#!/usr/bin/env python3
"""
Timeline view for visualizing log events chronologically.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from utils.log_viewer import load_logs

st.set_page_config(
    page_title="Timeline View",
    page_icon="⏱️",
    layout="wide"
)

def main():
    st.title("⏱️ Timeline View")
    
    # Load logs with caching
    @st.cache_data(ttl=300)
    def load_cached_logs():
        return load_logs()
    
    logs = load_cached_logs()
    
    if not logs:
        st.error("No logs found!")
        return
    
    st.success(f"Loaded {len(logs)} log entries")
    
    # Convert to DataFrame
    df = pd.DataFrame(logs)
    
    # Parse timestamps
    if 'timestamp' in df.columns:
        df['datetime'] = pd.to_datetime(df['timestamp'], errors='coerce', utc=True)
        df = df.dropna(subset=['datetime'])
        df = df.sort_values('datetime')
    
    if df.empty:
        st.warning("No valid timestamps found in logs")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Time range filter
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
        start_dt = pd.Timestamp(start_date).tz_localize('UTC')
        end_dt = pd.Timestamp(end_date + timedelta(days=1)).tz_localize('UTC')
        
        mask = (df['datetime'] >= start_dt) & (df['datetime'] <= end_dt)
        df = df[mask]
    
    # Event type filter
    if 'event_type' in df.columns:
        event_types = ['All'] + sorted(df['event_type'].dropna().unique().tolist())
        selected_event = st.sidebar.selectbox("Event Type", event_types)
        if selected_event != 'All':
            df = df[df['event_type'] == selected_event]
    
    # Timeline visualization
    st.subheader("📊 Event Timeline")
    
    if not df.empty:
        # Create timeline chart
        fig = px.scatter(
            df,
            x='datetime',
            y='event_type',
            color='event_type',
            hover_data=['action', 'request_id'],
            title='Event Timeline',
            labels={'datetime': 'Time', 'event_type': 'Event Type'}
        )
        
        fig.update_layout(
            height=600,
            xaxis_title="Time",
            yaxis_title="Event Type",
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent events table
        st.subheader("📝 Recent Events")
        
        display_cols = ['datetime', 'event_type', 'action', 'request_id']
        display_cols = [col for col in display_cols if col in df.columns]
        
        recent_df = df.tail(50)[display_cols]
        recent_df['datetime'] = recent_df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        st.dataframe(
            recent_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No events match the current filters")

if __name__ == "__main__":
    main()