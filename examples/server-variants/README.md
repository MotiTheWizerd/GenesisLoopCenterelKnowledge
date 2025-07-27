# Server Variants Examples

Alternative server implementations and configurations for different use cases.

## Files

### `simple_main.py`
Minimal server implementation with basic heartbeat functionality.
```bash
python examples/server-variants/simple_main.py
```

### `clean_main.py`
Clean server implementation with structured request/response models.
```bash
python examples/server-variants/clean_main.py
```

### `run_simple.py`
Simple server runner with minimal configuration.
```bash
python examples/server-variants/run_simple.py
```

## Use Cases

### `simple_main.py`
- **Purpose**: Minimal functionality testing
- **Features**: Basic heartbeat only
- **Use When**: Testing core server functionality

### `clean_main.py`
- **Purpose**: Clean implementation reference
- **Features**: Structured models, proper CORS
- **Use When**: Learning proper FastAPI patterns

### `run_simple.py`
- **Purpose**: Quick server startup
- **Features**: Minimal configuration
- **Use When**: Rapid development testing

## Comparison with Main Server

| Feature | main.py | simple_main.py | clean_main.py |
|---------|---------|----------------|---------------|
| Heartbeat | ✅ | ✅ | ✅ |
| Reflection | ✅ | ❌ | ✅ |
| Task System | ✅ | ❌ | ❌ |
| Logging | ✅ | ❌ | ❌ |
| Full Models | ✅ | ❌ | ✅ |

## Development Workflow
1. Start with `simple_main.py` for basic testing
2. Use `clean_main.py` for structured development
3. Graduate to `main.py` for full functionality

## Note
These are development and testing variants. Use `main.py` in the root directory for production.