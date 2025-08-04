# Dependency Conflict Resolution Guide

## Overview

This document details the resolution of a critical dependency conflict that occurred when attempting to add `google-adk` to the project, and provides guidance for handling similar issues in the future.

## The Problem

### Initial Error
```
Because no versions of google-adk match >1.8.0,<2.0.0
and google-adk (1.8.0) depends on uvicorn (>=0.34.0), 
google-adk (>=1.8.0,<2.0.0) requires uvicorn (>=0.34.0).
So, because fastapi-basic depends on both uvicorn (0.24.0) and google-adk (^1.8.0), 
version solving failed.
```

### Root Cause Analysis

The project had **pinned older versions** of core dependencies that were incompatible with newer packages:

- **uvicorn**: Pinned to `0.24.0` (released ~6 months ago)
- **starlette**: Pinned to `0.27.0` (released ~8 months ago)  
- **fastapi**: Pinned to `0.104.1` (released ~4 months ago)

Modern packages like `google-adk` require newer versions:
- **uvicorn**: `>=0.34.0`
- **starlette**: `>=0.46.2`
- **fastapi**: `>=0.115.0`

## The Resolution Process

### Step 1: Update Core Dependencies

Updated `pyproject.toml` to use compatible versions:

```toml
# Before
fastapi = "0.104.1"
uvicorn = "0.24.0"
starlette = "0.27.0"

# After
fastapi = "^0.115.0"
uvicorn = "^0.34.0"
starlette = "^0.46.2"
```

### Step 2: Handle Process Conflicts

During the update, encountered a Windows-specific issue:
```
PermissionError: [WinError 32] The process cannot access the file because it is being used by another process: 'uvicorn.exe'
```

**Solution**: Kill running processes before updating:
```powershell
taskkill /f /im uvicorn.exe
taskkill /f /im python.exe
```

### Step 3: Critical anyio Bug Discovery

After successful dependency updates, encountered a **runtime error**:

```
ImportError: cannot import name 'iterate_exceptions' from 'anyio._core._exceptions'
```

**Root Cause**: `anyio 4.9.0` is a **broken release** with internal import errors.

### Step 4: Complete Environment Reset

Due to corrupted package state, performed a complete reset:

```powershell
# Remove virtual environment
poetry env remove --all

# Remove lock file for fresh resolution
rm poetry.lock

# Clean install
poetry install
```

### Step 5: Pin Working anyio Version

Fixed the anyio issue by pinning to a stable version:

```toml
anyio = "4.6.0"
```

### Step 6: Remove Incompatible Dependencies

Since `google-adk` requires the broken `anyio >=4.9.0`, it was removed from dependencies until a fix is available.

## Final Working Configuration

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

## Key Lessons Learned

### 1. Avoid Pinning Core Dependencies
- Use caret ranges (`^`) instead of exact versions
- Pin only when absolutely necessary for stability
- Regularly update dependencies to avoid conflicts

### 2. Known Issues to Watch For
- **anyio 4.9.0**: Broken release with import errors
- **Windows process locks**: Kill processes before updating packages
- **Poetry cache issues**: Clear cache when encountering corruption

### 3. Dependency Conflict Resolution Strategy

1. **Identify the conflict**: Read error messages carefully
2. **Update core dependencies**: Start with FastAPI, uvicorn, starlette
3. **Handle process conflicts**: Kill running processes on Windows
4. **Check for known bugs**: Research specific version issues
5. **Reset environment if needed**: Complete clean install
6. **Pin problematic versions**: Use exact versions for broken releases

## Prevention Guidelines

### Dependency Management Best Practices

1. **Use semantic versioning ranges**:
   ```toml
   fastapi = "^0.115.0"  # Good: allows compatible updates
   fastapi = "0.104.1"   # Bad: locks to old version
   ```

2. **Regular maintenance**:
   ```bash
   # Check for outdated packages
   poetry show --outdated
   
   # Update dependencies regularly
   poetry update
   ```

3. **Test after updates**:
   ```bash
   # Run tests after dependency updates
   poetry run pytest
   
   # Test server startup
   poetry run python main.py
   ```

### Environment Management

1. **Clean environments**:
   ```bash
   # Periodic clean install
   poetry env remove --all
   rm poetry.lock
   poetry install
   ```

2. **Process management on Windows**:
   ```bash
   # Before major updates
   taskkill /f /im python.exe
   taskkill /f /im uvicorn.exe
   ```

## Troubleshooting Common Issues

### "Process cannot access file" on Windows
```bash
taskkill /f /im python.exe
taskkill /f /im uvicorn.exe
```

### "Cannot import" errors after updates
```bash
poetry env remove --all
rm poetry.lock
poetry install
```

### Version solving failures
1. Check for pinned versions in `pyproject.toml`
2. Update core dependencies first
3. Remove incompatible packages temporarily

### anyio import errors
```toml
# Pin to working version
anyio = "4.6.0"
```

## Future Considerations

### When google-adk Becomes Compatible

Monitor for:
1. **anyio bug fixes**: Check for anyio versions > 4.9.0 that fix the import issue
2. **google-adk updates**: New versions that work with stable anyio
3. **Alternative packages**: Consider other Google AI SDK options

### Dependency Update Strategy

1. **Monthly reviews**: Check for outdated dependencies
2. **Staged updates**: Update core dependencies first, then add-ons
3. **Testing protocol**: Always test after dependency changes
4. **Documentation**: Keep this guide updated with new issues

## Related Documentation

- [Project Setup Guide](../setup/installation.md)
- [Development Environment](../development/environment.md)
- [Known Issues](../troubleshooting/known-issues.md)