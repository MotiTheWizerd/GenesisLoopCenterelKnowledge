# Dashboard Configuration Guide

## Overview

The Dashboard Configuration system (`ui/streamlit/dashboard_config.py`) provides centralized configuration management for Ray's Streamlit dashboard, ensuring consistent path resolution and settings across all dashboard pages.

## 🎯 Purpose

### Problems Solved
- **Path Resolution Issues**: Streamlit pages running from different directories
- **Hardcoded Paths**: Scattered path definitions throughout codebase
- **Port Configuration**: Manual API server port management
- **File Discovery**: Inconsistent memory file detection

### Benefits
- Centralized configuration management
- Automatic project root detection
- Smart fallback mechanisms
- Consistent API across all pages

## 🏗️ Architecture

### Core Components

#### 1. DashboardConfig Class
```python
class DashboardConfig:
    def __init__(self):
        self.project_root = self._detect_project_root()
        self._validate_project_root()
```

#### 2. Path Properties
```python
@property
def extract_dir(self) -> Path:
    """Path to extract directory."""
    return self.project_root / "extract"

@property  
def logs_dir(self) -> Path:
    """Path to logs directory."""
    return self.project_root / "logs"
```

#### 3. Smart Detection Methods
```python
def get_memory_files(self) -> List[str]:
    """Get list of all memory files."""
    
def get_api_ports(self) -> List[int]:
    """Get list of common API server ports to try."""
    
def get_debug_info(self) -> Dict[str, Any]:
    """Get debug information about paths."""
```

## 🔧 Configuration Options

### Project Root Detection
```python
# Detection methods (in order of preference):
1. Look for pyproject.toml
2. Look for main.py  
3. Look for extract/memory_metadata.json
4. Check parent directories
5. Fallback to current directory
```

### Path Configuration
```python
# Default paths relative to project root:
EXTRACT_DIR = "extract"
LOGS_DIR = "logs" 
RAYS_MEMORY_ROOM = "RaysHome/MemoryRoom"
RAY_WORKSPACE = "ray_workspace"
MEMORIES_DIR = "memories"
BACKUPS_DIR = "backups"
```

### API Port Configuration
```python
# Default API ports to try (in order):
DEFAULT_API_PORTS = [8000, 8001, 8080, 3000, 8500]
```

## 📝 Usage Examples

### Basic Usage
```python
from dashboard_config import config

# Get paths
extract_dir = config.extract_dir
logs_dir = config.logs_dir

# Get memory files
memory_files = config.get_memory_files()

# Get API ports
api_ports = config.get_api_ports()
```

### In Streamlit Pages
```python
# Import in page header
sys.path.append(str(Path(__file__).parent))
from dashboard_config import config

# Use throughout the page
def load_memory_data():
    metadata_path = config.extract_dir / "memory_metadata.json"
    if metadata_path.exists():
        with open(metadata_path) as f:
            return json.load(f)
    return None
```

### Debug Information
```python
# Get comprehensive debug info
debug_info = config.get_debug_info()

# Display in Streamlit
with st.expander("🔍 Debug Information"):
    st.write(f"Project Root: {debug_info['project_root']}")
    st.write(f"Current Dir: {debug_info['current_working_dir']}")
    
    for name, info in debug_info["paths_exist"].items():
        status = "✅" if info["exists"] else "❌"
        st.write(f"{status} {name}: {info['path']}")
```

## 🔍 Path Resolution Logic

### Detection Algorithm
```python
def _detect_project_root(self) -> Path:
    """Detect project root using multiple strategies."""
    
    current = Path.cwd()
    
    # Strategy 1: Look for project indicators
    indicators = ["pyproject.toml", "main.py", "extract/memory_metadata.json"]
    
    # Check current directory and parents
    for path in [current] + list(current.parents):
        for indicator in indicators:
            if (path / indicator).exists():
                return path
    
    # Strategy 2: Check relative to script location
    script_dir = Path(__file__).parent
    for path in [script_dir] + list(script_dir.parents):
        for indicator in indicators:
            if (path / indicator).exists():
                return path
    
    # Fallback: use current directory
    return current
```

### Validation Process
```python
def _validate_project_root(self):
    """Validate that we found the correct project root."""
    
    expected_files = [
        "extract/memory_metadata.json",
        "pyproject.toml", 
        "main.py"
    ]
    
    # Check if at least one expected file exists
    for file_path in expected_files:
        if (self.project_root / file_path).exists():
            return  # Valid root found
    
    # Try alternative detection methods
    self._try_alternative_roots()
```

## 🚀 Integration Guide

### Adding New Paths
```python
# In DashboardConfig class:
@property
def new_directory(self) -> Path:
    """Path to new directory."""
    return self.project_root / "new_directory"

# Update get_debug_info method:
def get_debug_info(self):
    paths_to_check = [
        # ... existing paths ...
        ("new_directory", self.new_directory),
    ]
```

### Custom Configuration
```python
# Create custom config class
class CustomDashboardConfig(DashboardConfig):
    def __init__(self, custom_root: Path = None):
        if custom_root:
            self.project_root = custom_root
        else:
            super().__init__()
    
    @property
    def custom_dir(self) -> Path:
        return self.project_root / "custom"

# Use custom config
custom_config = CustomDashboardConfig(Path("/custom/root"))
```

### Environment-Based Configuration
```python
import os

class EnvironmentConfig(DashboardConfig):
    def __init__(self):
        super().__init__()
        
        # Override with environment variables
        if "RAY_PROJECT_ROOT" in os.environ:
            self.project_root = Path(os.environ["RAY_PROJECT_ROOT"])
        
        if "RAY_API_PORT" in os.environ:
            self.api_port = int(os.environ["RAY_API_PORT"])
    
    def get_api_ports(self) -> List[int]:
        if hasattr(self, 'api_port'):
            return [self.api_port] + super().get_api_ports()
        return super().get_api_ports()
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Wrong Project Root Detected
```python
# Symptoms:
- Files not found errors
- Empty memory file lists
- Path not found exceptions

# Solutions:
- Check for project indicator files
- Verify working directory
- Use debug info to inspect paths
- Set explicit project root
```

#### 2. Memory Files Not Found
```python
# Debug steps:
debug_info = config.get_debug_info()
print(f"Project root: {debug_info['project_root']}")
print(f"Extract dir exists: {config.extract_dir.exists()}")

# Check specific files:
for file_path in config.get_memory_files():
    print(f"Found: {file_path}")
```

#### 3. API Port Issues
```python
# Test API connectivity:
import requests

for port in config.get_api_ports():
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=1)
        print(f"Port {port}: {response.status_code}")
    except:
        print(f"Port {port}: Not responding")
```

### Debug Mode
```python
# Enable detailed logging
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DebugConfig(DashboardConfig):
    def __init__(self):
        logger.debug("Initializing DashboardConfig")
        super().__init__()
        logger.debug(f"Project root: {self.project_root}")
        
    def get_memory_files(self):
        files = super().get_memory_files()
        logger.debug(f"Found {len(files)} memory files")
        return files
```

## 📊 Performance Considerations

### Caching
```python
from functools import lru_cache

class CachedConfig(DashboardConfig):
    @lru_cache(maxsize=1)
    def get_memory_files(self) -> List[str]:
        """Cached version of get_memory_files."""
        return super().get_memory_files()
    
    def clear_cache(self):
        """Clear cached data."""
        self.get_memory_files.cache_clear()
```

### Lazy Loading
```python
class LazyConfig(DashboardConfig):
    def __init__(self):
        super().__init__()
        self._memory_files = None
    
    def get_memory_files(self) -> List[str]:
        if self._memory_files is None:
            self._memory_files = super().get_memory_files()
        return self._memory_files
```

## 🔮 Future Enhancements

### Planned Features
- Configuration file support (YAML/JSON)
- Environment variable integration
- Remote configuration loading
- Dynamic path watching
- Configuration validation

### Advanced Features
```python
# Configuration file support
def load_config_file(self, config_path: Path):
    """Load configuration from YAML/JSON file."""
    
# Remote configuration
def load_remote_config(self, url: str):
    """Load configuration from remote source."""
    
# Path watching
def watch_paths(self, callback):
    """Watch for changes in configured paths."""
```

## 📝 Best Practices

### Usage Guidelines
1. **Always use config object**: Don't hardcode paths
2. **Check existence**: Verify paths exist before using
3. **Handle errors gracefully**: Provide fallbacks
4. **Use debug info**: For troubleshooting issues
5. **Cache when appropriate**: For expensive operations

### Code Examples
```python
# Good: Using config object
metadata_path = config.extract_dir / "memory_metadata.json"
if metadata_path.exists():
    # Process file
    pass

# Bad: Hardcoded path
metadata_path = Path("extract/memory_metadata.json")  # May not work
```

### Error Handling
```python
try:
    memory_files = config.get_memory_files()
    if not memory_files:
        st.warning("No memory files found")
        return
except Exception as e:
    st.error(f"Configuration error: {e}")
    # Show debug information
    debug_info = config.get_debug_info()
    st.json(debug_info)
```

## 📞 Support

### Getting Help
1. Check debug information first
2. Verify file permissions
3. Test with minimal configuration
4. Review logs for errors
5. Check environment variables

### Reporting Issues
Include in bug reports:
- Debug information output
- Working directory
- File structure
- Error messages
- Steps to reproduce