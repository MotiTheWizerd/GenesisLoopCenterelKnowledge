# Known Issues and Workarounds

## Critical Issues

### anyio 4.9.0 Import Error

**Status**: 🔴 Critical - Breaks application startup

**Error**:
```
ImportError: cannot import name 'iterate_exceptions' from 'anyio._core._exceptions'
```

**Cause**: anyio 4.9.0 is a broken release with internal import errors.

**Workaround**: Pin to working version in `pyproject.toml`:
```toml
anyio = "4.6.0"
```

**Tracking**: Monitor [anyio releases](https://github.com/agronholm/anyio/releases) for fixes.

---

### google-adk Compatibility

**Status**: 🟡 Blocked - Cannot install due to anyio dependency

**Issue**: google-adk requires `anyio >=4.9.0`, but 4.9.0 is broken.

**Workaround**: google-adk temporarily removed from dependencies.

**Resolution**: Wait for either:
- anyio fix in version > 4.9.0
- google-adk update to support older anyio versions

---

## Windows-Specific Issues

### Process Lock During Updates

**Status**: 🟡 Common - Affects Windows development

**Error**:
```
PermissionError: [WinError 32] The process cannot access the file because it is being used by another process
```

**Cause**: Windows locks executable files when processes are running.

**Workaround**: Kill processes before updating:
```powershell
taskkill /f /im python.exe
taskkill /f /im uvicorn.exe
```

---

### Poetry Virtual Environment Corruption

**Status**: 🟡 Occasional - Happens during failed updates

**Symptoms**:
- Import errors after updates
- Package version mismatches
- Dependency resolution failures

**Solution**: Complete environment reset:
```bash
poetry env remove --all
rm poetry.lock
poetry install
```

---

## Development Issues

### uvicorn Reload Warning

**Status**: 🟢 Minor - Cosmetic warning only

**Warning**:
```
WARNING: You must pass the application as an import string to enable 'reload' or 'workers'.
```

**Fix**: Use import string in main.py:
```python
# Fixed version
uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# Old version that causes warning
uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

---

## Dependency Management

### Pinned Version Conflicts

**Status**: 🟡 Common - Affects new package additions

**Issue**: Old pinned versions prevent adding modern packages.

**Prevention**: Use semantic version ranges:
```toml
# Good - allows compatible updates
fastapi = "^0.115.0"

# Bad - locks to old version
fastapi = "0.104.1"
```

**Resolution**: Update core dependencies first, then add new packages.

---

## Monitoring and Updates

### Package Status Tracking

| Package | Current Version | Known Issues | Update Status |
|---------|----------------|--------------|---------------|
| anyio | 4.6.0 (pinned) | 4.9.0 broken | 🔴 Waiting for fix |
| google-adk | Not installed | Requires broken anyio | 🟡 Blocked |
| fastapi | ^0.115.0 | None | ✅ Up to date |
| uvicorn | ^0.34.0 | None | ✅ Up to date |
| starlette | ^0.46.2 | None | ✅ Up to date |

### Update Schedule

- **Weekly**: Check for anyio fixes
- **Monthly**: Review all dependencies for updates
- **Quarterly**: Full dependency audit and cleanup

---

## Reporting New Issues

When encountering new issues:

1. **Check this document** for existing workarounds
2. **Document the error** with full stack trace
3. **Test workarounds** and document results
4. **Update this file** with new findings
5. **Notify team** of critical issues

### Issue Template

```markdown
### [Issue Title]

**Status**: 🔴/🟡/🟢 [Severity] - [Brief description]

**Error**:
```
[Full error message]
```

**Cause**: [Root cause analysis]

**Workaround**: [Temporary solution]

**Resolution**: [Permanent fix or tracking info]
```

---

## Related Documentation

- [Dependency Conflict Resolution](dependency-conflicts.md)
- [Development Environment Setup](../development/environment.md)
- [Troubleshooting Guide](../troubleshooting/README.md)