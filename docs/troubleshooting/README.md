# Troubleshooting Guide

This directory contains comprehensive troubleshooting documentation for the AI Consciousness API project.

## Quick Reference

### 🔴 Critical Issues (Application Breaking)
- [anyio 4.9.0 Import Error](known-issues.md#anyio-490-import-error) - Breaks application startup
- [Complete Environment Corruption](dependency-conflicts.md#step-4-complete-environment-reset) - Requires full reset

### 🟡 Common Issues (Development Impact)
- [Process Lock During Updates](known-issues.md#process-lock-during-updates) - Windows-specific
- [Dependency Version Conflicts](dependency-conflicts.md) - Package compatibility issues
- [google-adk Compatibility](known-issues.md#google-adk-compatibility) - Currently blocked

### 🟢 Minor Issues (Cosmetic)
- [uvicorn Reload Warning](known-issues.md#uvicorn-reload-warning) - Harmless warning

## Documentation Structure

### [dependency-conflicts.md](dependency-conflicts.md)
Comprehensive guide to resolving dependency conflicts, including:
- Root cause analysis of version incompatibilities
- Step-by-step resolution process
- Prevention strategies
- Best practices for dependency management

### [known-issues.md](known-issues.md)
Current known issues and their workarounds:
- Critical bugs affecting functionality
- Platform-specific problems
- Temporary solutions and tracking status
- Package compatibility matrix

## Emergency Procedures

### Application Won't Start
1. Check for [anyio import errors](known-issues.md#anyio-490-import-error)
2. Try [complete environment reset](dependency-conflicts.md#step-4-complete-environment-reset)
3. Verify [dependency versions](dependency-conflicts.md#final-working-configuration)

### Dependency Update Failures
1. Kill running processes (Windows):
   ```bash
   taskkill /f /im python.exe
   taskkill /f /im uvicorn.exe
   ```
2. Follow [dependency conflict resolution](dependency-conflicts.md#the-resolution-process)
3. Consider [environment reset](dependency-conflicts.md#step-4-complete-environment-reset) if corruption suspected

### Package Installation Errors
1. Check [known compatibility issues](known-issues.md#dependency-management)
2. Update core dependencies first
3. Use [staged update approach](dependency-conflicts.md#dependency-update-strategy)

## Getting Help

### Before Reporting Issues
1. ✅ Check [known issues](known-issues.md) for existing solutions
2. ✅ Try [common fixes](#emergency-procedures)
3. ✅ Review [dependency conflicts guide](dependency-conflicts.md)
4. ✅ Test with [clean environment](dependency-conflicts.md#step-4-complete-environment-reset)

### When Reporting New Issues
Use the [issue template](known-issues.md#issue-template) and include:
- Full error messages and stack traces
- Environment details (OS, Python version, Poetry version)
- Steps to reproduce
- Attempted solutions

### Escalation Path
1. **Self-service**: Use this documentation
2. **Team consultation**: Share findings with development team
3. **External research**: Check package repositories and issue trackers
4. **Documentation update**: Add new findings to this guide

## Maintenance

### Regular Tasks
- **Weekly**: Check for fixes to [critical issues](known-issues.md#critical-issues)
- **Monthly**: Review and update [package status](known-issues.md#package-status-tracking)
- **Quarterly**: Audit and update all troubleshooting documentation

### Documentation Updates
When resolving new issues:
1. Document the solution in appropriate file
2. Update [known issues](known-issues.md) status
3. Add prevention guidance if applicable
4. Update this README if new categories emerge

## Related Documentation
- [Development Environment Setup](../development/environment.md)
- [Project Setup Guide](../setup/installation.md)
- [API Documentation](../api-reference/)