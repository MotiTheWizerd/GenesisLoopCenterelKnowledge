# Interactive Log Dashboard Guide

## Fixed Issue: Detailed View Not Updating

**Problem:** When selecting different log entries, the detailed view at the bottom wasn't updating.

**Solution:** Added proper Streamlit reactivity with unique keys and improved state management.

## Available Dashboards

### 1. 📝 Simple Log Viewer (Recommended)
- **File:** `ui/streamlit/simple_log_viewer.py`
- **Best for:** Quick log browsing with reliable detailed view
- **Features:**
  - Clean table view with pagination
  - Radio button selection (more reliable than dropdown)
  - Tabbed detailed view (Summary, Data, Raw)
  - Proper reactivity - details update immediately when you select a log

### 2. 📋 Standard Log Dashboard  
- **File:** `ui/streamlit/log_dashboard.py`
- **Best for:** General log analysis with metrics
- **Features:**
  - Multiple filter options
  - Log statistics
  - Dropdown selection with improved keys
  - Fixed detailed view reactivity

### 3. 🔬 Advanced Log Viewer
- **File:** `ui/streamlit/advanced_log_viewer.py`
- **Best for:** Deep analysis and consciousness patterns
- **Features:**
  - Multiple tabs (Browser, Sessions, Analytics, Search)
  - Reflect session analysis
  - Consciousness pattern visualization
  - Advanced search capabilities

## How to Launch

```bash
# Interactive launcher with menu
python launch_log_dashboard.py

# Direct launch of specific dashboard
streamlit run ui/streamlit/simple_log_viewer.py --server.port 8501
```

## Key Fixes Applied

### 1. Unique Keys for Reactivity
```python
# Before (problematic)
selected_idx = st.selectbox("Select log", range(len(logs)))

# After (fixed)
selectbox_key = f"log_select_{page}_{len(page_logs)}"
selected_idx = st.selectbox("Select log", range(len(logs)), key=selectbox_key)
```

### 2. Radio Buttons Instead of Dropdowns
Radio buttons are more reliable for Streamlit reactivity:
```python
selected_option = st.radio(
    "Select a log entry:",
    options=range(len(page_logs)),
    format_func=lambda x: f"{table_data[x]['Time']} - {table_data[x]['Event']}",
    key=f"log_selector_{page}_{len(page_logs)}"
)
```

### 3. Tabbed Detailed View
Organized information into tabs for better UX:
- **Summary:** Key information and extracted details
- **Data:** JSON data and metadata
- **Raw:** Complete log entry

### 4. Better State Management
- Unique keys prevent state conflicts
- Proper page-based keys ensure selection resets on page change
- Immediate visual feedback when selection changes

## Usage Tips

1. **For Quick Browsing:** Use Simple Log Viewer
2. **For Analysis:** Use Advanced Log Viewer  
3. **For General Use:** Use Standard Dashboard

## Reflect Log Analysis

All dashboards can filter and analyze reflect logs:
- View Ray's reflection questions
- See consciousness depth levels (surface/deep/profound)
- Track current_position context
- Monitor reflection responses and insights

## Troubleshooting

If detailed view still doesn't update:
1. Refresh the browser page
2. Try the Simple Log Viewer (most reliable)
3. Check browser console for JavaScript errors
4. Restart the Streamlit server

The Simple Log Viewer is specifically designed to avoid these reactivity issues and should work reliably for log analysis.