#!/usr/bin/env python3
"""
Enhanced JSON viewer component with syntax highlighting and better formatting.
"""

import streamlit as st
import json
import time
from typing import Any, Dict, List, Union
import pandas as pd

try:
    from streamlit_ace import st_ace
    ACE_AVAILABLE = True
except ImportError:
    ACE_AVAILABLE = False

try:
    from pygments import highlight
    from pygments.lexers import JsonLexer
    from pygments.formatters import HtmlFormatter
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False

def format_json_value(value: Any) -> str:
    """Format a JSON value for better display."""
    if isinstance(value, dict):
        return f"Object ({len(value)} keys)"
    elif isinstance(value, list):
        return f"Array ({len(value)} items)"
    elif isinstance(value, str):
        if len(value) > 50:
            return f'"{value[:47]}..."'
        return f'"{value}"'
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif value is None:
        return "null"
    else:
        return str(value)

def filter_json_data(data: Any, search_term: str, case_sensitive: bool = False) -> Any:
    """Filter JSON data based on search term."""
    if not search_term:
        return data
    
    if not case_sensitive:
        search_term = search_term.lower()
    
    def matches_search(text: str) -> bool:
        if not case_sensitive:
            text = text.lower()
        return search_term in text
    
    def filter_recursive(obj: Any) -> Any:
        if isinstance(obj, dict):
            filtered = {}
            for key, value in obj.items():
                # Check if key matches
                key_matches = matches_search(str(key))
                
                # Check if value matches (for simple values)
                value_matches = False
                if isinstance(value, (str, int, float, bool)):
                    value_matches = matches_search(str(value))
                
                # Recursively filter nested objects/arrays
                filtered_value = filter_recursive(value)
                
                # Include if key matches, value matches, or nested content matches
                if key_matches or value_matches or (
                    isinstance(filtered_value, dict) and len(filtered_value) > 0
                ) or (
                    isinstance(filtered_value, list) and len(filtered_value) > 0
                ):
                    filtered[key] = filtered_value if isinstance(filtered_value, (dict, list)) else value
            
            return filtered
        
        elif isinstance(obj, list):
            filtered = []
            for item in obj:
                if isinstance(item, (dict, list)):
                    filtered_item = filter_recursive(item)
                    if (isinstance(filtered_item, dict) and len(filtered_item) > 0) or \
                       (isinstance(filtered_item, list) and len(filtered_item) > 0):
                        filtered.append(filtered_item)
                else:
                    # Simple value in array
                    if matches_search(str(item)):
                        filtered.append(item)
            
            return filtered
        
        else:
            # Simple value
            return obj if matches_search(str(obj)) else None
    
    return filter_recursive(data)

def create_json_tree(data: Dict[str, Any], max_depth: int = 3, current_depth: int = 0) -> None:
    """Create an expandable tree view of JSON data."""
    
    if current_depth >= max_depth:
        st.write("... (max depth reached)")
        return
    
    for key, value in data.items():
        if isinstance(value, dict):
            with st.expander(f"🔑 **{key}** - {format_json_value(value)}", expanded=current_depth < 2):
                if value:
                    create_json_tree(value, max_depth, current_depth + 1)
                else:
                    st.write("*Empty object*")
        
        elif isinstance(value, list):
            with st.expander(f"📋 **{key}** - {format_json_value(value)}", expanded=current_depth < 2):
                if value:
                    # Add pagination for large arrays
                    display_paginated_array(value, f"array_{key}", max_depth, current_depth)
                else:
                    st.write("*Empty array*")
        
        else:
            # Simple value
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write(f"**{key}:**")
            with col2:
                if isinstance(value, str) and len(value) > 100:
                    with st.expander("View full text"):
                        st.text(value)
                    st.write(f'"{value[:50]}..."')
                else:
                    st.write(format_json_value(value))

def display_paginated_object(
    obj: Dict[str, Any],
    key_prefix: str,
    max_depth: int = 3,
    current_depth: int = 0,
    items_per_page: int = 10
) -> None:
    """Display a large object with pagination."""
    
    keys = list(obj.keys())
    total_keys = len(keys)
    
    if total_keys <= items_per_page:
        # Small object, show all keys
        create_json_tree(obj, max_depth, current_depth)
        return
    
    # Large object, add pagination
    total_pages = (total_keys - 1) // items_per_page + 1
    
    # Pagination controls
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.write(f"**Total:** {total_keys:,} keys")
    
    with col2:
        page = st.selectbox(
            f"Page (1-{total_pages})",
            range(1, total_pages + 1),
            key=f"obj_page_{key_prefix}_{int(time.time() * 1000) % 100000}"
        )
    
    with col3:
        items_per_page = st.selectbox(
            "Keys per page",
            [5, 10, 25, 50],
            index=1,  # Default to 10
            key=f"obj_items_{key_prefix}_{int(time.time() * 1000) % 100000}_items"
        )
    
    # Recalculate pagination
    total_pages = (total_keys - 1) // items_per_page + 1
    if page > total_pages:
        page = total_pages
    
    # Calculate slice indices
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_keys)
    
    # Show page info
    st.info(f"Showing keys {start_idx + 1:,} to {end_idx:,} of {total_keys:,}")
    
    # Create paginated object
    page_keys = keys[start_idx:end_idx]
    page_obj = {key: obj[key] for key in page_keys}
    
    # Display the paginated object
    create_json_tree(page_obj, max_depth, current_depth)
    
    # Navigation buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    
    unique_id = f"{key_prefix}_{int(time.time() * 1000) % 100000}_{id(obj)}"
    
    with col1:
        if st.button("⏮️ First", disabled=page == 1, key=f"obj_first_{unique_id}"):
            st.rerun()
    
    with col2:
        if st.button("⏪ Previous", disabled=page == 1, key=f"obj_prev_{unique_id}"):
            st.rerun()
    
    with col3:
        st.write(f"Page {page} of {total_pages}")
    
    with col4:
        if st.button("Next ⏩", disabled=page == total_pages, key=f"obj_next_{unique_id}"):
            st.rerun()
    
    with col5:
        if st.button("Last ⏭️", disabled=page == total_pages, key=f"obj_last_{unique_id}"):
            st.rerun()

def display_paginated_array(
    array: List[Any], 
    key_prefix: str, 
    max_depth: int = 3, 
    current_depth: int = 0,
    items_per_page: int = 10
) -> None:
    """Display a large array with pagination."""
    
    total_items = len(array)
    
    if total_items <= items_per_page:
        # Small array, show all items
        for i, item in enumerate(array):
            if isinstance(item, dict):
                with st.expander(f"Item {i+1} - {format_json_value(item)}"):
                    create_json_tree(item, max_depth, current_depth + 1)
            else:
                st.write(f"**{i+1}.** {format_json_value(item)}")
        return
    
    # Large array, add pagination
    total_pages = (total_items - 1) // items_per_page + 1
    
    # Pagination controls
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.write(f"**Total:** {total_items:,} items")
    
    with col2:
        page = st.selectbox(
            f"Page (1-{total_pages})",
            range(1, total_pages + 1),
            key=f"page_{key_prefix}_{int(time.time() * 1000) % 100000}"
        )
    
    with col3:
        items_per_page = st.selectbox(
            "Items per page",
            [5, 10, 25, 50, 100],
            index=1,  # Default to 10
            key=f"items_{key_prefix}_{int(time.time() * 1000) % 100000}_items"
        )
    
    # Recalculate pagination with new items_per_page
    total_pages = (total_items - 1) // items_per_page + 1
    if page > total_pages:
        page = total_pages
    
    # Calculate slice indices
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    # Show page info
    st.info(f"Showing items {start_idx + 1:,} to {end_idx:,} of {total_items:,}")
    
    # Display items for current page
    page_items = array[start_idx:end_idx]
    
    for i, item in enumerate(page_items):
        actual_index = start_idx + i + 1
        
        if isinstance(item, dict):
            with st.expander(f"Item {actual_index} - {format_json_value(item)}"):
                create_json_tree(item, max_depth, current_depth + 1)
        else:
            st.write(f"**{actual_index}.** {format_json_value(item)}")
    
    # Navigation buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    
    unique_id = f"{key_prefix}_{int(time.time() * 1000) % 100000}_{id(array)}"
    
    with col1:
        if st.button("⏮️ First", disabled=page == 1, key=f"first_{unique_id}"):
            st.rerun()
    
    with col2:
        if st.button("⏪ Previous", disabled=page == 1, key=f"prev_{unique_id}"):
            st.rerun()
    
    with col3:
        st.write(f"Page {page} of {total_pages}")
    
    with col4:
        if st.button("Next ⏩", disabled=page == total_pages, key=f"next_{unique_id}"):
            st.rerun()
    
    with col5:
        if st.button("Last ⏭️", disabled=page == total_pages, key=f"last_{unique_id}"):
            st.rerun()

def display_json_with_ace(data: Any, height: int = 400, theme: str = "monokai") -> None:
    """Display JSON with ACE editor (syntax highlighted)."""
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    
    st_ace(
        value=json_str,
        language='json',
        theme=theme,
        height=height,
        auto_update=False,
        font_size=14,
        tab_size=2,
        wrap=True,
        key=f"json_ace_{int(time.time() * 1000) % 100000}"
    )

def display_json_with_pygments(data: Any) -> None:
    """Display JSON with Pygments syntax highlighting."""
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    
    # Create HTML with syntax highlighting
    lexer = JsonLexer()
    formatter = HtmlFormatter(style='monokai', noclasses=True)
    highlighted = highlight(json_str, lexer, formatter)
    
    # Display in Streamlit
    st.markdown(highlighted, unsafe_allow_html=True)

def smart_json_display(
    data: Any, 
    title: str = "JSON Data",
    max_size: int = 10000,
    default_view: str = "tree",
    enable_search: bool = True
) -> None:
    """
    Smart JSON display that chooses the best method based on data size and available libraries.
    
    Args:
        data: The data to display
        title: Title for the display
        max_size: Maximum size for full JSON display
        default_view: Default view type ('tree', 'ace', 'pygments', 'raw')
    """
    
    if not data:
        st.info("No data to display")
        return
    
    # Convert to JSON string to check size
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    data_size = len(json_str)
    
    # Add search functionality for large datasets
    filtered_data = data
    if enable_search and isinstance(data, (dict, list)) and data_size > 5000:
        st.subheader("🔍 Search & Filter")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input(
                "Search in keys/values", 
                placeholder="Enter search term...",
                key=f"search_{int(time.time() * 1000) % 100000}"
            )
        with col2:
            case_sensitive = st.checkbox("Case sensitive", key=f"case_{int(time.time() * 1000) % 100000}")
        
        if search_term:
            filtered_data = filter_json_data(data, search_term, case_sensitive)
            if filtered_data != data:
                if isinstance(filtered_data, dict) and len(filtered_data) == 0:
                    st.warning("No matches found")
                elif isinstance(filtered_data, list) and len(filtered_data) == 0:
                    st.warning("No matches found")
                else:
                    match_count = len(filtered_data) if isinstance(filtered_data, (dict, list)) else 1
                    st.success(f"Found {match_count} matches")
    
    # Create tabs for different view options
    available_tabs = ["🌳 Tree View"]
    
    if ACE_AVAILABLE:
        available_tabs.append("🎨 Syntax Highlighted")
    
    if PYGMENTS_AVAILABLE:
        available_tabs.append("🖼️ Pretty Print")
    
    available_tabs.extend(["📄 Raw JSON", "📊 Summary"])
    
    tabs = st.tabs(available_tabs)
    
    # Tree View Tab
    with tabs[0]:
        st.subheader("🌳 Interactive Tree View")
        
        # Use filtered data for display
        display_data = filtered_data
        display_size = len(json.dumps(display_data, indent=2, ensure_ascii=False))
        
        if display_size > max_size:
            st.warning(f"⚠️ Large data ({display_size:,} characters). Showing paginated view.")
            
            # Show paginated view for large data
            if isinstance(display_data, dict):
                # For large objects, show paginated keys
                display_paginated_object(display_data, "root_object")
            elif isinstance(display_data, list):
                # For large arrays, show paginated items
                st.write(f"**Array with {len(display_data):,} items**")
                display_paginated_array(display_data, "root_array")
            else:
                st.json(display_data)
        else:
            if isinstance(display_data, dict):
                if len(display_data) > 20:
                    display_paginated_object(display_data, "root_object_small")
                else:
                    create_json_tree(display_data)
            elif isinstance(display_data, list):
                # Even for smaller arrays, use pagination if they're large
                if len(display_data) > 20:
                    st.write(f"**Array with {len(display_data)} items**")
                    display_paginated_array(display_data, "root_array_small")
                else:
                    st.json(display_data)
            else:
                st.json(display_data)
    
    # ACE Editor Tab
    tab_index = 1
    if ACE_AVAILABLE:
        with tabs[tab_index]:
            st.subheader("🎨 Syntax Highlighted View")
            if data_size > max_size:
                st.warning(f"⚠️ Data too large ({data_size:,} characters) for syntax highlighting.")
                st.info("Use Tree View or Raw JSON for large data.")
            else:
                display_json_with_ace(data)
        tab_index += 1
    
    # Pygments Tab
    if PYGMENTS_AVAILABLE:
        with tabs[tab_index]:
            st.subheader("🖼️ Pretty Print View")
            if data_size > max_size:
                st.warning(f"⚠️ Data too large ({data_size:,} characters) for pretty printing.")
            else:
                display_json_with_pygments(data)
        tab_index += 1
    
    # Raw JSON Tab
    with tabs[tab_index]:
        st.subheader("📄 Raw JSON")
        if data_size > max_size:
            st.warning(f"⚠️ Large data ({data_size:,} characters)")
            if st.button("Show anyway (may be slow)", key=f"show_large_json_{int(time.time() * 1000) % 100000}"):
                st.json(data)
        else:
            st.json(data)
    
    # Summary Tab
    with tabs[tab_index + 1]:
        st.subheader("📊 Data Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Data Size", f"{data_size:,} chars")
        
        with col2:
            if isinstance(data, dict):
                st.metric("Type", "Object")
                st.metric("Keys", len(data))
            elif isinstance(data, list):
                st.metric("Type", "Array")
                st.metric("Items", len(data))
            else:
                st.metric("Type", type(data).__name__)
        
        with col3:
            # Estimate memory usage
            memory_mb = data_size / 1024 / 1024
            st.metric("Est. Memory", f"{memory_mb:.2f} MB")
        
        # Show structure analysis
        if isinstance(data, dict):
            st.subheader("🔍 Structure Analysis")
            
            # Analyze key types and values
            key_analysis = {}
            for key, value in data.items():
                value_type = type(value).__name__
                if value_type not in key_analysis:
                    key_analysis[value_type] = []
                key_analysis[value_type].append(key)
            
            for value_type, keys in key_analysis.items():
                st.write(f"**{value_type}** ({len(keys)} keys): {', '.join(keys[:5])}")
                if len(keys) > 5:
                    st.write(f"   ... and {len(keys) - 5} more")

# Convenience function for backward compatibility
def display_json(data: Any, title: str = "JSON Data") -> None:
    """Simple JSON display function."""
    smart_json_display(data, title)