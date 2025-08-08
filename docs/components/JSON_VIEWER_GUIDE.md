# JSON Viewer Component Guide

## Overview

The JSON Viewer component (`ui/streamlit/components/json_viewer.py`) provides enhanced JSON visualization capabilities for Ray's Streamlit dashboard system. It offers multiple viewing modes, syntax highlighting, and intelligent handling of large datasets.

## 🎯 Features

### Multiple View Modes
1. **🌳 Interactive Tree View** - Expandable/collapsible structure
2. **🎨 Syntax Highlighted** - ACE editor with color coding
3. **🖼️ Pretty Print** - Pygments-powered formatting
4. **📄 Raw JSON** - Standard Streamlit display
5. **📊 Data Summary** - Structure analysis and statistics

### Smart Size Handling
- Automatic detection of large files (>10KB)
- Progressive loading for performance
- Size warnings and alternatives
- Memory usage estimation

### Interactive Features
- Expandable tree nodes
- Value truncation for readability
- Type-aware display
- Search and navigation

## 📦 Dependencies

Required packages (add to `pyproject.toml`):
```toml
streamlit-ace = ">=0.1.1"        # Syntax highlighting editor
streamlit-extras = ">=0.3.0"     # Additional UI components  
pygments = ">=2.15.0"            # Syntax highlighting engine
```

Install with Poetry:
```bash
poetry add streamlit-ace streamlit-extras pygments
```

## 🚀 Usage

### Basic Usage
```python
from components.json_viewer import smart_json_display

# Simple display
data = {"key": "value", "nested": {"items": [1, 2, 3]}}
smart_json_display(data, "My Data")
```

### Advanced Usage
```python
# With custom options
smart_json_display(
    data=large_json_data,
    title="Complex Dataset", 
    max_size=50000,           # Size limit for full display
    default_view="tree"       # Default tab to show
)
```

### Individual Components
```python
from components.json_viewer import (
    create_json_tree,
    display_json_with_ace,
    display_json_with_pygments
)

# Tree view only
create_json_tree(data, max_depth=3)

# Syntax highlighted editor
display_json_with_ace(data, height=400, theme="monokai")

# Pretty print with Pygments
display_json_with_pygments(data)
```

## 🎨 View Modes Explained

### 1. Interactive Tree View
**Best for**: Exploring nested structures, large objects
```python
# Features:
- Expandable nodes for objects and arrays
- Smart value truncation (strings >50 chars)
- Type indicators (Object, Array, String, etc.)
- Depth limiting to prevent infinite expansion
- Empty object/array detection
```

**Example Display**:
```
🔑 user_data - Object (3 keys)
  ├── 📋 preferences - Array (5 items)
  │   ├── Item 1 - "theme: dark"
  │   └── Item 2 - "language: en"
  ├── 🔑 profile - Object (4 keys)
  └── last_login - "2024-01-15T10:30:00Z"
```

### 2. Syntax Highlighted View
**Best for**: Code review, detailed inspection
```python
# Features:
- ACE editor with multiple themes
- Line numbers and syntax coloring
- Proper JSON indentation
- Read-only mode for safety
- Customizable height and font size
```

**Themes Available**:
- `monokai` (dark, recommended)
- `github` (light)
- `tomorrow_night`
- `solarized_dark`
- `dracula`

### 3. Pretty Print View
**Best for**: Documentation, presentations
```python
# Features:
- Pygments syntax highlighting
- HTML output with CSS styling
- Multiple color schemes
- Clean, professional appearance
- Copy-friendly formatting
```

### 4. Raw JSON View
**Best for**: Debugging, compatibility
```python
# Features:
- Standard Streamlit st.json() display
- Collapsible sections
- Native browser JSON handling
- Fallback when other modes fail
```

### 5. Data Summary View
**Best for**: Understanding data structure
```python
# Displays:
- File size and memory usage
- Data type breakdown
- Key/item counts
- Structure analysis
- Performance metrics
```

## 🔧 Configuration Options

### Size Limits
```python
# Default limits
MAX_TREE_SIZE = 10000      # Characters for tree view
MAX_ACE_SIZE = 10000       # Characters for syntax highlighting
MAX_PYGMENTS_SIZE = 10000  # Characters for pretty print
MAX_DEPTH = 3              # Tree expansion depth
```

### Customization
```python
# ACE Editor themes
AVAILABLE_THEMES = [
    "monokai", "github", "tomorrow_night", 
    "solarized_dark", "dracula", "chrome"
]

# Tree view settings
TREE_MAX_ITEMS = 5         # Items shown in arrays
TREE_MAX_STRING = 50       # String truncation length
TREE_MAX_KEYS = 10         # Keys shown in summary
```

## 📊 Performance Considerations

### Large Data Handling
```python
# Automatic optimizations:
- Size detection before rendering
- Progressive loading for large datasets
- Memory usage warnings
- Fallback to summary views
- Lazy expansion of tree nodes
```

### Memory Usage
```python
# Estimated memory usage:
- JSON string: ~1x data size
- Tree view: ~2x data size (DOM elements)
- ACE editor: ~3x data size (syntax parsing)
- Pygments: ~2x data size (HTML generation)
```

## 🎯 Integration Examples

### Health Dashboard
```python
# In health_dashboard.py
consciousness_metrics = data.get("consciousness_metrics", {})
if consciousness_metrics:
    smart_json_display(consciousness_metrics, "Consciousness Metrics")
```

### Memory Analysis
```python
# In memory_analysis_tab.py
with st.expander("📋 Metadata Structure"):
    smart_json_display(metadata, "Memory Metadata", max_size=50000)
```

### Log Viewer
```python
# For log entries
for log_entry in recent_logs:
    with st.expander(f"Log {log_entry['timestamp']}"):
        smart_json_display(log_entry, "Log Details")
```

## 🐛 Error Handling

### Graceful Degradation
```python
# Fallback hierarchy:
1. Try ACE editor (if available)
2. Try Pygments (if available) 
3. Use tree view
4. Fall back to st.json()
5. Show error message
```

### Common Issues
```python
# Import errors
try:
    from streamlit_ace import st_ace
    ACE_AVAILABLE = True
except ImportError:
    ACE_AVAILABLE = False
    # Gracefully disable ACE features

# Large data handling
if data_size > MAX_SIZE:
    st.warning("Data too large for full display")
    show_summary_instead()
```

## 🔍 Debugging

### Debug Information
```python
# Enable debug mode
DEBUG_MODE = True

if DEBUG_MODE:
    st.write(f"Data size: {len(json_str)} characters")
    st.write(f"Data type: {type(data).__name__}")
    st.write(f"Available libraries: ACE={ACE_AVAILABLE}, Pygments={PYGMENTS_AVAILABLE}")
```

### Performance Monitoring
```python
import time

start_time = time.time()
smart_json_display(data)
render_time = time.time() - start_time

if render_time > 1.0:
    st.warning(f"Slow render time: {render_time:.2f}s")
```

## 🎨 Styling Customization

### CSS Overrides
```python
# Custom CSS for JSON display
st.markdown("""
<style>
.json-tree {
    font-family: 'Monaco', 'Consolas', monospace;
    font-size: 14px;
    line-height: 1.4;
}
.json-key {
    color: #e06c75;
    font-weight: bold;
}
.json-string {
    color: #98c379;
}
.json-number {
    color: #d19a66;
}
</style>
""", unsafe_allow_html=True)
```

### Theme Configuration
```python
# ACE editor theme mapping
THEME_MAPPING = {
    "dark": "monokai",
    "light": "github", 
    "auto": "tomorrow_night"
}

# Apply theme based on user preference
user_theme = st.selectbox("Theme", ["dark", "light", "auto"])
ace_theme = THEME_MAPPING[user_theme]
```

## 🚀 Future Enhancements

### Planned Features
- Search within JSON data
- Export to different formats
- Custom color schemes
- Diff view for comparing JSON
- Schema validation display

### Performance Improvements
- Virtual scrolling for large arrays
- Incremental rendering
- Background processing
- Caching of parsed data

## 📝 Best Practices

### When to Use Each View
- **Tree View**: Exploring unknown data structures
- **Syntax Highlighted**: Code review and detailed inspection  
- **Pretty Print**: Documentation and presentations
- **Raw JSON**: Debugging and compatibility testing
- **Summary**: Understanding large datasets quickly

### Performance Tips
- Set appropriate `max_size` limits
- Use tree view for large nested objects
- Enable caching for frequently accessed data
- Monitor render times in production

### User Experience
- Provide clear loading indicators
- Show data size warnings
- Offer multiple view options
- Include helpful error messages

## 📞 Support

### Common Issues
1. **Import errors**: Install required dependencies
2. **Slow rendering**: Reduce `max_size` or use summary view
3. **Memory issues**: Enable size warnings and limits
4. **Display problems**: Clear browser cache

### Debug Steps
1. Check browser console for errors
2. Verify all dependencies are installed
3. Test with smaller datasets
4. Enable debug mode for detailed information