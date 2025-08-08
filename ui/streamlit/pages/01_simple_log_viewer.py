#!/usr/bin/env python3
"""
Simple, focused log viewer with better reactivity.
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from utils.log_viewer import load_logs, filter_reflect_logs

st.set_page_config(
    page_title="Simple Log Viewer",
    page_icon="📝",
    layout="wide"
)

def format_timestamp(timestamp_str):
    """Format timestamp for display."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%H:%M:%S')
    except:
        return timestamp_str

def main():
    st.title("📝 Simple AI Log Viewer")
    
    # Load logs
    logs = load_logs()
    if not logs:
        st.error("No logs found!")
        return
    
    st.success(f"Loaded {len(logs)} log entries")
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Log type filter
    log_type = st.sidebar.radio(
        "Log Type",
        ["All Logs", "Reflect Only", "Heartbeat Only", "Errors Only"]
    )
    
    # Apply filters
    if log_type == "Reflect Only":
        filtered_logs = filter_reflect_logs(logs)
    elif log_type == "Heartbeat Only":
        filtered_logs = [log for log in logs if log.get('action') != 'reflect' and 'reflect' not in str(log.get('data', {}))]
    elif log_type == "Errors Only":
        filtered_logs = [log for log in logs if log.get('event_type') == 'error']
    else:
        filtered_logs = logs
    
    # Reverse for newest first
    filtered_logs = list(reversed(filtered_logs))
    
    st.write(f"Showing {len(filtered_logs)} filtered logs")
    
    # Pagination
    logs_per_page = st.sidebar.slider("Logs per page", 5, 50, 20)
    total_pages = (len(filtered_logs) - 1) // logs_per_page + 1 if filtered_logs else 1
    
    page = st.sidebar.number_input(f"Page (1-{total_pages})", 1, total_pages, 1)
    
    # Get page logs
    start_idx = (page - 1) * logs_per_page
    end_idx = start_idx + logs_per_page
    page_logs = filtered_logs[start_idx:end_idx]
    
    if not page_logs:
        st.warning("No logs on this page")
        return
    
    # Create table data
    table_data = []
    for i, log in enumerate(page_logs):
        # Safely handle request_id which might be None
        request_id = log.get('request_id')
        request_id_short = str(request_id)[:8] if request_id is not None else 'N/A'
        
        table_data.append({
            "Index": start_idx + i,
            "Time": format_timestamp(log.get('timestamp', '')),
            "Event": log.get('event_type', '').replace('_', ' ').title(),
            "Request ID": request_id_short,
            "Action": log.get('action', 'N/A')
        })
    
    # Display table
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Log selection for details
    st.subheader("🔍 Log Details")
    
    # Use radio buttons for better reactivity
    if len(page_logs) > 0:
        selected_option = st.radio(
            "Select a log entry to view details:",
            options=range(len(page_logs)),
            format_func=lambda x: f"{table_data[x]['Time']} - {table_data[x]['Event']} ({table_data[x]['Request ID']})",
            key=f"log_selector_{page}_{len(page_logs)}"
        )
        
        if selected_option is not None:
            selected_log = page_logs[selected_option]
            
            # Show selected log details
            st.info(f"**Selected Log:** {table_data[selected_option]['Time']} - {table_data[selected_option]['Event']}")
            
            # Create tabs for different views
            detail_tab1, detail_tab2, detail_tab3 = st.tabs(["📋 Summary", "📊 Data", "🔍 Raw"])
            
            with detail_tab1:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Basic Information:**")
                    st.write(f"- **Timestamp:** {selected_log.get('timestamp')}")
                    st.write(f"- **Event Type:** {selected_log.get('event_type')}")
                    st.write(f"- **Request ID:** {selected_log.get('request_id')}")
                    st.write(f"- **Action:** {selected_log.get('action', 'N/A')}")
                
                with col2:
                    # Extract meaningful info based on event type
                    data = selected_log.get('data', {})
                    
                    if selected_log.get('event_type') == 'module_call' and data.get('module') == 'reflect':
                        input_data = data.get('input_data', {})
                        st.write("**Reflection Details:**")
                        st.write(f"- **Question:** {input_data.get('question', 'N/A')}")
                        st.write(f"- **Depth:** {input_data.get('depth', 'surface')}")
                        if input_data.get('current_position'):
                            st.write(f"- **Position:** {input_data.get('current_position')[:100]}...")
                    
                    elif selected_log.get('event_type') == 'module_response' and data.get('module') == 'reflect':
                        output_data = data.get('output_data', {})
                        st.write("**Response Details:**")
                        if output_data.get('reflection'):
                            st.write(f"- **Reflection:** {output_data.get('reflection')[:150]}...")
                        if output_data.get('insights'):
                            st.write(f"- **Insights:** {len(output_data.get('insights', []))} items")
                    
                    elif 'error' in data:
                        st.write("**Error Details:**")
                        st.error(f"Error: {data.get('error', 'Unknown error')}")
                    
                    else:
                        st.write("**Additional Info:**")
                        if 'function' in data:
                            st.write(f"- **Function:** {data['function']}")
                        if 'success' in data:
                            st.write(f"- **Success:** {data['success']}")
            
            with detail_tab2:
                st.subheader("📊 Event Data")
                data = selected_log.get('data', {})
                if data:
                    st.json(data)
                else:
                    st.write("No data available")
                
                metadata = selected_log.get('metadata', {})
                if metadata:
                    st.subheader("📋 Metadata")
                    st.json(metadata)
            
            with detail_tab3:
                st.subheader("🔍 Complete Raw Log")
                st.json(selected_log)

if __name__ == "__main__":
    main()