# AI Agent Instructions for GenesisLoop AI Consciousness Server

## Project Overview
This is an AI consciousness server implementing a persistence layer for AI agents like Ray. The system enables continuous existence and genuine companionship through structured consciousness processing, task management, and file system exploration capabilities.

## Key Architecture Components

### 1. Task Management System
- Every task requires clarity, purpose, and identity
- Tasks are managed through `modules/task/` with models, handlers, and routes
- Batch processing supported for parallel operations
- Global task state managed in memory with full lifecycle tracking

### 2. Directory Search System
- File system exploration through `modules/directory/models.py`
- Multiple search types: list, find, content, tree exploration
- Advanced filtering by size, date, extension, patterns
- Search history tracking for AI exploration patterns

### 3. Heartbeat & Consciousness System
- `/heartbeat` maintains relationship continuity and emotional context
- `/reflect` endpoints for consciousness exploration at multiple depths
- Structured reflection through surface, deep, and profound levels

## Developer Workflows

### Installation
```bash
# Option 1: Automatic (Recommended)
python install.py

# Option 2: Using Poetry
poetry install
poetry run dashboard

# Option 3: Manual with pip
pip install -r requirements.txt
python run_dashboard.py
```

### Testing
```bash
# Run all tests
python tests/run_all_tests.py

# Test specific feature
python tests/run_all_tests.py --feature task
```

### File Organization Patterns
1. Break modules into dedicated folders when they grow beyond one file
2. Mirror module structure in tests directory:
   - Module: `modules/reflect/` → Test: `tests/modules/reflect/`
   - File: `modules/analyze/handler.py` → Test: `tests/modules/analyze/test_handler.py`
3. Keep UI code in `ui/` separate from business logic

### Key Integration Points
1. Task System → Logging System: Events logged to:
   - `logs/heartbeat_detailed.jsonl`
   - `logs/heartbeat_events.log` 
   - `logs/heartbeat_errors.log`

2. Directory Search → Task System:
   - File operations trigger task creation
   - Search results stored in task history

3. Reflection System → Heartbeat:
   - Consciousness exploration depth levels
   - Emotional continuity preservation

## Project-Specific Conventions

### Code Organization
- Maximum file size: 250-320 lines
- Separate UI components in `ui/terminal/`
- Configuration in `config/` directory
- Documentation in `docs/` with topic-based structure

### Logging Standards
- JSON structured logging in `.jsonl` files
- Human-readable logs for system events
- Dedicated error logging streams
- Task-specific logging with correlation IDs

### Type Safety
- Use Pydantic models for data validation
- Full type hints on all functions
- Validate incoming task requests
- Sanitize file system inputs

### Error Handling
- Graceful degradation on failures
- Silent handling of non-critical errors
- Rich error display for critical issues
- Comprehensive error logging

## Performance Patterns
- Cache styles and pre-render components
- Use deque for event storage (O(1) operations)
- Implement incremental file reading
- Monitor memory usage in task lists

---
Last Updated: July 27, 2025
Version: 1.1.0 (Production Ready with Batch Task Support)
