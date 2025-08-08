#!/usr/bin/env python3
"""
Statistics Dashboard - Provides detailed analytics and metrics about system performance.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from utils.log_viewer import load_logs

st.set_page_config(
    page_title="Statistics Dashboard",
    page_icon="📊",
    layout="wide"
)

def format_timestamp(ts):
    """Format timestamp for display."""
    if pd.isna(ts):
        return "N/A"
    try:
        return pd.to_datetime(ts).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return str(ts)

def load_and_prepare_data():
    """Load and prepare log data for analysis."""
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def load_cached_logs():
        return load_logs()
    
    logs = load_cached_logs()
    if not logs:
        return None
        
    # Convert to DataFrame
    df = pd.DataFrame(logs)
    
    # Parse timestamps
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce', utc=True)
        df['date'] = df['timestamp'].dt.date
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.day_name()
    
    return df

def show_metrics(df):
    """Display key metrics."""
    if df is None or df.empty:
        return
        
    st.subheader("📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Log Entries", len(df))
    
    with col2:
        if 'event_type' in df.columns:
            st.metric("Unique Event Types", df['event_type'].nunique())
    
    with col3:
        if 'timestamp' in df.columns and not df['timestamp'].isna().all():
            st.metric("Time Range", 
                     f"{format_timestamp(df['timestamp'].min())} to {format_timestamp(df['timestamp'].max())}")
    
    with col4:
        if 'action' in df.columns:
            st.metric("Unique Actions", df['action'].nunique())

def show_time_series(df):
    """Display time series of log events."""
    if df is None or df.empty or 'timestamp' not in df.columns:
        return
        
    st.subheader("🕒 Log Activity Over Time")
    
    # Resample time series
    time_series = df.set_index('timestamp').resample('H').size()
    
    # Create figure
    fig = px.line(
        time_series, 
        title='Log Entries per Hour',
        labels={'value': 'Number of Logs', 'timestamp': 'Time'}
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Number of Logs",
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_event_distribution(df):
    """Show distribution of event types."""
    if df is None or 'event_type' not in df.columns:
        return
        
    st.subheader("📈 Event Type Distribution")
    
    # Calculate counts
    event_counts = df['event_type'].value_counts().reset_index()
    event_counts.columns = ['Event Type', 'Count']
    
    # Create two columns for chart and table
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Bar chart
        fig = px.bar(
            event_counts.head(10),
            x='Event Type',
            y='Count',
            title='Top 10 Event Types',
            color='Event Type'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Table with all events
        st.dataframe(
            event_counts,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Event Type": "Event Type",
                "Count": "Count"
            }
        )

def show_hourly_heatmap(df):
    """Show hourly distribution heatmap."""
    if df is None or 'hour' not in df.columns or 'day_of_week' not in df.columns:
        return
        
    st.subheader("🔥 Activity Heatmap")
    
    # Create pivot table for heatmap
    heatmap_data = df.pivot_table(
        index='day_of_week',
        columns='hour',
        aggfunc='size',
        fill_value=0
    )
    
    # Ensure we have all 24 hours (0-23) as columns
    all_hours = list(range(24))
    for hour in all_hours:
        if hour not in heatmap_data.columns:
            heatmap_data[hour] = 0
    
    # Reorder columns to be 0-23
    heatmap_data = heatmap_data.reindex(columns=all_hours)
    
    # Reorder days of week (only include days that exist in data)
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    existing_days = [day for day in days if day in heatmap_data.index]
    
    if not existing_days:
        st.warning("No day-of-week data available for heatmap")
        return
    
    heatmap_data = heatmap_data.reindex(existing_days, fill_value=0)
    
    # Create heatmap with proper dimensions
    try:
        fig = px.imshow(
            heatmap_data,
            labels=dict(x="Hour of Day", y="Day of Week", color="Log Count"),
            x=[f"{h:02d}:00" for h in range(24)],
            y=heatmap_data.index,
            aspect="auto",
            color_continuous_scale="Blues"
        )
        
        # Update layout
        fig.update_xaxes(side="bottom")
        fig.update_layout(
            xaxis_title="Hour of Day",
            yaxis_title="Day of Week",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating heatmap: {str(e)}")
        
        # Fallback: show data as table
        st.subheader("📊 Activity Data (Table View)")
        st.dataframe(heatmap_data, use_container_width=True)
        
        # Debug information
        with st.expander("🔍 Debug Information"):
            st.write(f"Heatmap data shape: {heatmap_data.shape}")
            st.write(f"Hours in data: {sorted(heatmap_data.columns.tolist())}")
            st.write(f"Days in data: {heatmap_data.index.tolist()}")
            st.write(f"Data types: {heatmap_data.dtypes.to_dict()}")

def main():
    st.title("📊 Statistics Dashboard")
    
    # Load data
    df = load_and_prepare_data()
    
    if df is None or df.empty:
        st.error("No log data available!")
        return
    
    # Show metrics
    show_metrics(df)
    
    # Add a divider
    st.markdown("---")
    
    # Show time series
    show_time_series(df)
    
    # Add a divider
    st.markdown("---")
    
    # Show event distribution
    show_event_distribution(df)
    
    # Add a divider
    st.markdown("---")
    
    # Show hourly heatmap
    show_hourly_heatmap(df)
    
    # Add a divider
    st.markdown("---")
    
    # Show raw data section
    st.subheader("📋 Raw Data Preview")
    st.dataframe(df.head(100), use_container_width=True)

if __name__ == "__main__":
    main()
