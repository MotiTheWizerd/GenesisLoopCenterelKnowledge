# Testing Examples

Test scripts and validation utilities for the AI consciousness server components.

## Files

### API Testing
- `test_api.py` - API endpoint testing
- `test_server.py` - Server functionality testing

### Component Testing
- `test_imports.py` - Import validation tests
- `test_logging.py` - Logging system tests
- `test_dashboard.py` - Dashboard functionality tests

### Minimal Testing
- `minimal_test.py` - Basic functionality tests
- `test_minimal.py` - Minimal server tests

## Usage

### Run Individual Tests
```bash
python examples/testing/test_api.py
python examples/testing/test_server.py
```

### Run All Tests
```bash
# From project root
python -m pytest examples/testing/
```

## Test Categories
- **API Tests**: Validate endpoint functionality
- **Component Tests**: Test individual modules
- **Integration Tests**: Test system interactions
- **Minimal Tests**: Basic smoke tests

## Note
For comprehensive testing, use the main test suite in the `tests/` directory. These examples are for quick validation and development testing.