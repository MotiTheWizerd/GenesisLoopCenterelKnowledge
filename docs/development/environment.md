# Development Environment Guide

## Overview

This guide covers setting up and maintaining a stable development environment for the AI Consciousness API project, including lessons learned from dependency management challenges.

## Prerequisites

- Python 3.9+ (avoid 3.9.7 due to known issues)
- Poetry for dependency management
- Git for version control

## Initial Setup

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd GenesisLoopCenterelKnowledge
```

### 2. Install Dependencies
```bash
# Create virtual environment and install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### 3. Verify Installation
```bash
# Test server startup
python main.py

# Run tests
poetry run pytest
```

## Dependency Management

### Current Stable Configuration

The project uses these core dependencies (as of latest update):

```toml
[tool.poetry.dependencies]
python = ">=3.9,<3.9.7 || >3.9.7,<4.0"
fastapi = "^0.115.0"
uvicorn = "^0.34.0"
starlette = "^0.46.2"
pydantic = "^2.0.0"
requests = "^2.32.4"
rich = "^13.7.0"
typer = "^0.9.0"
beautifulsoup4 = "^4.12.0"
lxml = "^4.9.0"
psutil = "^5.9.0"
anyio = "4.6.0"  # Pinned due to 4.9.0 bug
```

### Critical Version Pins

**anyio = "4.6.0"**: Pinned due to critical bug in 4.9.0 that causes import errors.

⚠️ **Do not update anyio** until the import bug is fixed in versions > 4.9.0.

### Adding New Dependencies

1. **Check compatibility** with current versions
2. **Test in isolated environment** first
3. **Update core dependencies** if needed
4. **Document any conflicts** in troubleshooting docs

Example:
```bash
# Add new dependency
poetry add new-package

# Test immediately
python main.py
poetry run pytest
```

## Environment Maintenance

### Regular Tasks

#### Weekly
- Check for critical security updates
- Monitor [anyio releases](https://github.com/agronholm/anyio/releases) for bug fixes

#### Monthly
```bash
# Check for outdated packages
poetry show --outdated

# Update non-critical dependencies
poetry update

# Test after updates
python main.py
poetry run pytest
```

#### Quarterly
- Full dependency audit
- Update troubleshooting documentation
- Review and update version pins

### Environment Reset (When Needed)

If you encounter dependency corruption or import errors:

```bash
# Kill any running processes (Windows)
taskkill /f /im python.exe
taskkill /f /im uvicorn.exe

# Remove virtual environment
poetry env remove --all

# Remove lock file for fresh resolution
rm poetry.lock

# Clean install
poetry install

# Verify functionality
python main.py
```

## Platform-Specific Considerations

### Windows Development

**Process Management**: Windows locks executable files when processes are running.

Before major updates:
```powershell
taskkill /f /im python.exe
taskkill /f /im uvicorn.exe
```

**Path Issues**: Use forward slashes in Python code, even on Windows.

**Virtual Environment**: Poetry handles this automatically, but be aware of path length limitations.

### Linux/macOS Development

Generally fewer issues, but still follow the same dependency management practices.

## IDE Configuration

### VS Code Settings

Recommended `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true
}
```

### PyCharm Settings

1. Set interpreter to Poetry virtual environment
2. Enable pytest as test runner
3. Configure code style to match project standards

## Development Workflow

### Starting Development Session

```bash
# Activate environment
poetry shell

# Start server with auto-reload
python main.py

# In another terminal, run tests
poetry run pytest --watch
```

### Before Committing

```bash
# Run full test suite
poetry run pytest

# Check code formatting
poetry run black --check .

# Verify server starts
python main.py
```

## Troubleshooting

### Common Issues

1. **Import errors after updates**: [Environment reset](#environment-reset-when-needed)
2. **Process lock errors**: [Kill processes](#windows-development)
3. **Dependency conflicts**: See [dependency conflicts guide](../troubleshooting/dependency-conflicts.md)
4. **anyio import errors**: Verify `anyio = "4.6.0"` in pyproject.toml

### Getting Help

1. Check [known issues](../troubleshooting/known-issues.md)
2. Try [troubleshooting guide](../troubleshooting/README.md)
3. Reset environment if needed
4. Document new issues for team

## Best Practices

### Dependency Management
- Use semantic version ranges (`^`) for most packages
- Pin only when necessary for stability
- Update regularly but test thoroughly
- Document any special version requirements

### Environment Hygiene
- Reset environment monthly or when issues arise
- Keep dependencies minimal and purposeful
- Monitor for security updates
- Test after any dependency changes

### Development Safety
- Always test after dependency updates
- Use feature branches for major changes
- Keep troubleshooting docs updated
- Share environment issues with team

## Related Documentation

- [Troubleshooting Guide](../troubleshooting/README.md)
- [Dependency Conflicts Resolution](../troubleshooting/dependency-conflicts.md)
- [Known Issues](../troubleshooting/known-issues.md)
- [Project Setup Guide](../setup/installation.md)