#!/usr/bin/env python3
"""
Memory Analysis - Analyze memory patterns and usage.
"""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import dashboard config
sys.path.append(str(Path(__file__).parent))
from dashboard_config import config

# Import enhanced JSON viewer
sys.path.append(str(Path(__file__).parent.parent))
from components.json_viewer import smart_json_display

st.set_page_config(
    page_title="Memory Analysis",
    page_icon="📊",
    layout="wide"
)

def analyze_memory_metadata():
    """Analyze memory metadata if available."""
    metadata_path = config.extract_dir / "memory_metadata.json"
    
    if not metadata_path.exists():
        return None
    
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading memory metadata: {e}")
        return None

def analyze_memory_directory():
    """Analyze memory directory structure."""
    memory_paths = [
        config.extract_dir,
        config.rays_memory_room,
        config.ray_workspace,
        config.logs_dir,
        config.memories_dir  # Keep original for backward compatibility
    ]
    
    # Find the first existing memory directory
    memories_path = None
    for path in memory_paths:
        if path.exists():
            memories_path = path
            break
    
    if not memories_path:
        return None
    
    analysis = {
        "total_files": 0,
        "total_size": 0,
        "file_types": {},
        "files_by_date": {},
        "memory_locations": []
    }
    
    # Analyze all memory locations
    for path in memory_paths:
        if path.exists():
            location_info = {
                "path": str(path),
                "files": 0,
                "size": 0
            }
            
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    analysis["total_files"] += 1
                    location_info["files"] += 1
                    
                    file_size = file_path.stat().st_size
                    analysis["total_size"] += file_size
                    location_info["size"] += file_size
                    
                    # File type analysis
                    suffix = file_path.suffix or "no_extension"
                    analysis["file_types"][suffix] = analysis["file_types"].get(suffix, 0) + 1
                    
                    # Date analysis
                    mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    date_key = mod_time.strftime("%Y-%m-%d")
                    analysis["files_by_date"][date_key] = analysis["files_by_date"].get(date_key, 0) + 1
            
            if location_info["files"] > 0:
                analysis["memory_locations"].append(location_info)
    
    return analysis

def main():
    st.title("📊 Memory Analysis")
    
    # Analyze memory metadata
    metadata = analyze_memory_metadata()
    memory_analysis = analyze_memory_directory()
    
    if not metadata and not memory_analysis:
        st.warning("No memory data found for analysis!")
        st.info("Expected: extract/memory_metadata.json or memories/ directory")
        return
    
    # Memory Metadata Analysis
    if metadata:
        st.subheader("🧠 Memory Metadata Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if isinstance(metadata, dict):
                st.metric("Metadata Keys", len(metadata.keys()))
        
        with col2:
            # Try to find memory-related metrics
            memory_count = 0
            if isinstance(metadata, dict):
                for key, value in metadata.items():
                    if isinstance(value, list):
                        memory_count += len(value)
            st.metric("Memory Items", memory_count)
        
        with col3:
            metadata_path = config.extract_dir / "memory_metadata.json"
            if metadata_path.exists():
                metadata_size = metadata_path.stat().st_size
                st.metric("Metadata Size", f"{metadata_size / 1024:.1f} KB")
            else:
                st.metric("Metadata Size", "0 KB")
        
        # Display metadata structure (with size limits)
        with st.expander("📋 Metadata Structure"):
            if isinstance(metadata, dict):
                # Check if metadata is too large to display
                metadata_str = str(metadata)
                if len(metadata_str) > 50000:  # 50KB text limit
                    st.warning("⚠️ Metadata is too large to display fully. Showing summary instead.")
                    
                    # Show summary instead
                    st.write("**Metadata Summary:**")
                    st.write(f"- Total keys: {len(metadata.keys())}")
                    
                    # Show first few keys with their types and sizes
                    st.write("**Top-level keys:**")
                    for i, (key, value) in enumerate(list(metadata.items())[:10]):
                        value_type = type(value).__name__
                        if isinstance(value, (list, dict)):
                            size_info = f" ({len(value)} items)"
                        else:
                            size_info = ""
                        st.write(f"- `{key}`: {value_type}{size_info}")
                        
                        if i >= 9:  # Show max 10 keys
                            remaining = len(metadata) - 10
                            if remaining > 0:
                                st.write(f"... and {remaining} more keys")
                            break
                    
                    # Option to show specific keys
                    st.write("**Explore specific keys:**")
                    selected_key = st.selectbox(
                        "Select a key to explore:",
                        options=[""] + list(metadata.keys())[:20],  # Limit to first 20 keys
                        key="metadata_key_selector"
                    )
                    
                    if selected_key:
                        st.write(f"**Content of '{selected_key}':**")
                        key_value = metadata[selected_key]
                        
                        # Handle different types of values
                        if isinstance(key_value, dict):
                            if len(str(key_value)) > 10000:
                                st.write(f"Dictionary with {len(key_value)} keys (too large to display)")
                                # Show just the keys
                                st.write("Keys:", list(key_value.keys())[:20])
                            else:
                                st.json(key_value)
                        elif isinstance(key_value, list):
                            if len(str(key_value)) > 10000:
                                st.write(f"List with {len(key_value)} items (showing first 5)")
                                st.json(key_value[:5])
                            else:
                                st.json(key_value)
                        else:
                            st.write(key_value)
                else:
                    # Small enough to display normally
                    st.json(metadata)
            else:
                st.json(metadata)
    
    # Memory Directory Analysis
    if memory_analysis:
        st.subheader("📁 Memory Directory Analysis")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Files", memory_analysis["total_files"])
        
        with col2:
            st.metric("Total Size", f"{memory_analysis['total_size'] / 1024:.1f} KB")
        
        with col3:
            st.metric("File Types", len(memory_analysis["file_types"]))
        
        with col4:
            avg_size = memory_analysis["total_size"] / max(memory_analysis["total_files"], 1)
            st.metric("Avg File Size", f"{avg_size / 1024:.1f} KB")
        
        # File type distribution
        if memory_analysis["file_types"]:
            st.subheader("📈 File Type Distribution")
            
            file_types_df = pd.DataFrame(
                list(memory_analysis["file_types"].items()),
                columns=["File Type", "Count"]
            )
            
            fig = px.pie(
                file_types_df,
                values="Count",
                names="File Type",
                title="Distribution of File Types"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Memory locations breakdown
        if memory_analysis["memory_locations"]:
            st.subheader("📍 Memory Locations")
            
            locations_df = pd.DataFrame(memory_analysis["memory_locations"])
            locations_df["size_kb"] = locations_df["size"] / 1024
            
            fig = px.bar(
                locations_df,
                x="path",
                y="files",
                title="Files by Memory Location",
                hover_data=["size_kb"]
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Files by date
        if memory_analysis["files_by_date"]:
            st.subheader("📅 Memory Creation Timeline")
            
            dates_df = pd.DataFrame(
                list(memory_analysis["files_by_date"].items()),
                columns=["Date", "Files Created"]
            )
            dates_df["Date"] = pd.to_datetime(dates_df["Date"])
            dates_df = dates_df.sort_values("Date")
            
            fig = px.line(
                dates_df,
                x="Date",
                y="Files Created",
                title="Memory Files Created Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Memory Health Check
    st.subheader("🏥 Memory Health Check")
    
    health_issues = []
    
    if not metadata:
        health_issues.append("❌ No memory metadata found")
    
    if not memory_analysis or memory_analysis["total_files"] == 0:
        health_issues.append("❌ No memory files found")
    
    if memory_analysis and memory_analysis["total_size"] > 100 * 1024 * 1024:  # 100MB
        health_issues.append("⚠️ Memory usage is high (>100MB)")
    
    if not health_issues:
        st.success("✅ Memory system appears healthy!")
    else:
        for issue in health_issues:
            if issue.startswith("❌"):
                st.error(issue)
            else:
                st.warning(issue)

if __name__ == "__main__":
    main()