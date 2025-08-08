#!/usr/bin/env python3
"""
Memory Explorer - Browse and analyze memory data.
"""

import streamlit as st
import json
import pandas as pd
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import dashboard config
sys.path.append(str(Path(__file__).parent))
from dashboard_config import config

st.set_page_config(
    page_title="Memory Explorer",
    page_icon="🧠",
    layout="wide"
)

def load_memory_files():
    """Load available memory files using config."""
    return config.get_memory_files()

def main():
    st.title("🧠 Memory Explorer")
    
    # Debug: Show current working directory
    import os
    st.info(f"🔍 Current working directory: {os.getcwd()}")
    
    # Load available memory files
    memory_files = load_memory_files()
    
    # Debug information using config
    debug_info = config.get_debug_info()
    
    with st.expander("🔍 Debug Information"):
        st.write(f"**Project Root:** {debug_info['project_root']}")
        st.write(f"**Current Working Dir:** {debug_info['current_working_dir']}")
        
        st.write("**Path Status:**")
        for name, info in debug_info["paths_exist"].items():
            status = "✅" if info["exists"] else "❌"
            st.write(f"{status} {name}: {info['path']}")
    
    if not memory_files:
        st.warning("No memory files found!")
        st.info("Check the debug information above to see which paths exist")
        return
    
    st.success(f"Found {len(memory_files)} memory files")
    
    # File selector
    selected_file = st.selectbox("Select memory file to explore:", memory_files)
    
    if selected_file:
        try:
            with open(selected_file, 'r', encoding='utf-8') as f:
                if selected_file.endswith('.json'):
                    data = json.load(f)
                    
                    st.subheader(f"📄 {Path(selected_file).name}")
                    
                    # Show file info
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("File Size", f"{Path(selected_file).stat().st_size} bytes")
                    with col2:
                        if isinstance(data, dict):
                            st.metric("Keys", len(data.keys()))
                        elif isinstance(data, list):
                            st.metric("Items", len(data))
                    
                    # Display data with size optimization
                    st.subheader("📊 Data Preview")
                    
                    # Check file size first
                    file_size = Path(selected_file).stat().st_size
                    
                    if file_size > 1024 * 1024:  # 1MB limit
                        st.warning(f"⚠️ Large file ({file_size / 1024 / 1024:.1f} MB). Showing summary only.")
                        
                        if isinstance(data, dict):
                            st.write(f"**Dictionary with {len(data)} keys:**")
                            for i, key in enumerate(list(data.keys())[:10]):
                                value = data[key]
                                value_type = type(value).__name__
                                if isinstance(value, (list, dict)):
                                    size_info = f" ({len(value)} items)"
                                else:
                                    size_info = ""
                                st.write(f"- `{key}`: {value_type}{size_info}")
                        elif isinstance(data, list):
                            st.write(f"**List with {len(data)} items**")
                            st.write("First few items:")
                            st.json(data[:3])
                        else:
                            st.write("**Data type:**", type(data).__name__)
                    
                    elif isinstance(data, dict):
                        # Show as expandable sections for manageable size
                        for key, value in data.items():
                            with st.expander(f"🔑 {key}"):
                                if isinstance(value, (dict, list)):
                                    # Limit display size for nested structures
                                    if len(str(value)) > 5000:
                                        if isinstance(value, dict):
                                            st.write(f"Dictionary with {len(value)} keys (too large to display)")
                                        elif isinstance(value, list):
                                            st.write(f"List with {len(value)} items (showing first 3)")
                                            st.json(value[:3])
                                    else:
                                        st.json(value)
                                else:
                                    st.write(value)
                    
                    elif isinstance(data, list):
                        # Show as table if possible
                        if data and isinstance(data[0], dict):
                            try:
                                df = pd.DataFrame(data)
                                st.dataframe(df.head(100), use_container_width=True)  # Limit to 100 rows
                                if len(data) > 100:
                                    st.info(f"Showing first 100 of {len(data)} rows")
                            except:
                                st.json(data[:10])  # Fallback to first 10 items
                        else:
                            st.json(data[:20])  # Show first 20 items for lists
                    
                    else:
                        st.json(data)
                    
                    # Raw data view with size check
                    with st.expander("🔍 Raw JSON (Use with caution for large files)"):
                        if file_size > 500 * 1024:  # 500KB limit for raw view
                            st.warning("⚠️ File too large for raw display. Use a JSON viewer instead.")
                            st.write(f"File size: {file_size / 1024:.1f} KB")
                        else:
                            st.json(data)
                
                elif selected_file.endswith('.jsonl'):
                    # Handle JSONL files
                    lines = f.readlines()
                    st.subheader(f"📄 {Path(selected_file).name}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("File Size", f"{Path(selected_file).stat().st_size} bytes")
                    with col2:
                        st.metric("Lines", len(lines))
                    
                    # Show recent entries
                    st.subheader("📊 Recent Entries")
                    
                    recent_entries = []
                    for line in lines[-10:]:  # Last 10 entries
                        try:
                            entry = json.loads(line.strip())
                            recent_entries.append(entry)
                        except json.JSONDecodeError:
                            continue
                    
                    if recent_entries:
                        for i, entry in enumerate(recent_entries):
                            with st.expander(f"Entry {len(lines) - 10 + i + 1}"):
                                st.json(entry)
                    else:
                        st.warning("No valid JSON entries found")
                
                elif selected_file.endswith('.md'):
                    # Handle Markdown files
                    content = f.read()
                    st.subheader(f"📄 {Path(selected_file).name}")
                    st.markdown(content)
                
                else:
                    # Handle other text files
                    content = f.read()
                    st.subheader(f"📄 {Path(selected_file).name}")
                    st.text_area("File Content", content, height=400)
        
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
    
    # Memory statistics
    st.subheader("📈 Memory Statistics")
    
    total_size = sum(Path(f).stat().st_size for f in memory_files if Path(f).exists())
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Files", len(memory_files))
    with col2:
        st.metric("Total Size", f"{total_size / 1024:.1f} KB")
    with col3:
        json_files = [f for f in memory_files if f.endswith('.json')]
        st.metric("JSON Files", len(json_files))

if __name__ == "__main__":
    main()