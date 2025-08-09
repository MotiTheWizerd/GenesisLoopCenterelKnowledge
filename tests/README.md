# GenesisLoop Tests

This directory contains tests for the GenesisLoop project. The tests are organized by module and feature, with integration tests in a separate directory.

## Test Structure

```
tests/
├── integration/                # Integration tests across modules
│   ├── conftest.py            # Pytest configuration for integration tests
│   ├── __init__.py            # Package initialization
│   ├── run_tests.py           # Script to run integration tests
│   └── test_vscode_response_flow.py  # Test for VSCode response flow
├── modules/                   # Module-specific tests
│   ├── directory/             # Directory module tests
│   ├── heartbeat/             # Heartbeat module tests
│   ├── logging/               # Logging module tests
│   ├── reflect/               # Reflection module tests
│   ├── routes/                # Routes module tests
│   │   ├── test_coding_routes.py  # Tests for coding_routes.py
│   │   ├── test_heartbeat_routes.py
│   │   └── test_reflect_routes.py
│   ├── task/                  # Task module tests
│   │   └── test_vscode_integration.py  # Tests for TaskManager integration with VSCode Logic
│   └── vscode_logic/          # VSCode Logic module tests
│       ├── conftest.py        # Pytest configuration for VSCode Logic tests
│       ├── run_tests.py       # Script to run VSCode Logic tests
│       ├── test_forward_integration.py  # Tests for forward_vscode_response integration
│       └── test_handler.py    # Tests for VSCodeLogicHandler
└── run_all_tests.py          # Script to run all tests
```

## Running Tests

### Running All Tests

To run all tests, use the `run_all_tests.py` script:

```bash
python tests/run_all_tests.py
```

### Running Tests for a Specific Feature

To run tests for a specific feature, use the `--feature` option:

```bash
python tests/run_all_tests.py --feature vscode
```

Available features:
- `task` - Task module tests
- `heartbeat` - Heartbeat module tests
- `reflect` - Reflection module tests
- `routes` - Routes module tests
- `logging` - Logging module tests
- `directory` - Directory module tests
- `read_file` - Read File tests
- `vscode` - VSCode Logic module tests
- `integration` - Integration tests

### Running Quick Tests

To run a quick smoke test of core functionality, use the `--quick` option:

```bash
python tests/run_all_tests.py --quick
```

### Running VSCode Logic Tests

To run only the VSCode Logic module tests, use the `run_tests.py` script in the `vscode_logic` directory:

```bash
python tests/modules/vscode_logic/run_tests.py
```

### Running Integration Tests

To run only the integration tests, use the `run_tests.py` script in the `integration` directory:

```bash
python tests/integration/run_tests.py
```

## Test Requirements

The tests require the following packages:

- `pytest` - Test framework
- `pytest-asyncio` - Pytest plugin for testing asyncio code
- `httpx` - HTTP client for testing HTTP endpoints
- `unittest.mock` - Mocking library for unit tests

Install the required packages with:

```bash
pip install pytest pytest-asyncio httpx
```