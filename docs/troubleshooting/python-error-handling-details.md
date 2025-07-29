# Python Execution Error Handling for Ray

## Overview
Ray will receive comprehensive error details for all types of failures during Python code execution. The system is designed to provide maximum debugging information while maintaining security.

## Error Response Structure

### Complete Error Response Format
```json
{
    "success": false,
    "execution_result": {
        "stdout": "Any output before the error occurred",
        "stderr": "Full error traceback and messages",
        "return_value": null,
        "variables": {},
        "execution_time": 0.123,
        "memory_used": "2.5MB",
        "exit_code": 1,
        "exception_info": {
            "type": "NameError",
            "message": "name 'undefined_variable' is not defined",
            "traceback": [
                {
                    "filename": "<string>",
                    "line_number": 3,
                    "function_name": "<module>",
                    "code_line": "print(undefined_variable)"
                }
            ],
            "full_traceback": "Traceback (most recent call last):\n  File \"<string>\", line 3, in <module>\n    print(undefined_variable)\nNameError: name 'undefined_variable' is not defined"
        }
    },
    "error_category": "runtime_error",
    "error_details": {
        "error_type": "NameError",
        "error_message": "name 'undefined_variable' is not defined",
        "line_number": 3,
        "column_number": 6,
        "context": "Variable 'undefined_variable' was referenced but never defined",
        "suggestions": [
            "Check if the variable name is spelled correctly",
            "Ensure the variable is defined before use",
            "Check if the variable is in the correct scope"
        ]
    },
    "timestamp": "2025-01-28T10:30:00Z",
    "assigned_by": "ray"
}
```

## Error Categories Ray Will Receive

### 1. Syntax Errors
```json
{
    "success": false,
    "error_category": "syntax_error",
    "error_details": {
        "error_type": "SyntaxError",
        "error_message": "invalid syntax",
        "line_number": 2,
        "column_number": 15,
        "problematic_code": "if x = 5:",
        "context": "Assignment operator '=' used instead of comparison '=='",
        "suggestions": [
            "Use '==' for comparison instead of '='",
            "Use 'is' for identity comparison",
            "Check Python syntax documentation"
        ]
    }
}
```

### 2. Runtime Errors
```json
{
    "success": false,
    "error_category": "runtime_error",
    "error_details": {
        "error_type": "ZeroDivisionError",
        "error_message": "division by zero",
        "line_number": 5,
        "function_name": "calculate_average",
        "local_variables": {
            "total": 100,
            "count": 0,
            "numbers": "[10, 20, 30, 40]"
        },
        "context": "Division by zero occurred in average calculation",
        "suggestions": [
            "Check if denominator is zero before division",
            "Add error handling with try/except",
            "Validate input data before processing"
        ]
    }
}
```

### 3. Import Errors
```json
{
    "success": false,
    "error_category": "import_error",
    "error_details": {
        "error_type": "ModuleNotFoundError",
        "error_message": "No module named 'nonexistent_module'",
        "attempted_import": "nonexistent_module",
        "available_modules": ["math", "json", "datetime", "random"],
        "context": "Attempted to import a module not available in the sandbox",
        "suggestions": [
            "Check if the module name is spelled correctly",
            "Use one of the available modules: math, json, datetime, random",
            "Request additional modules if needed for your task"
        ]
    }
}
```

### 4. Security Errors
```json
{
    "success": false,
    "error_category": "security_error",
    "error_details": {
        "error_type": "SecurityViolation",
        "error_message": "Attempted to access restricted module 'os'",
        "violation_type": "blocked_import",
        "attempted_action": "import os",
        "security_level": "strict",
        "context": "The 'os' module is blocked in strict security mode",
        "suggestions": [
            "Use allowed modules for file operations",
            "Request permission for specific operations",
            "Consider using safer alternatives"
        ]
    }
}
```

### 5. Timeout Errors
```json
{
    "success": false,
    "error_category": "timeout_error",
    "error_details": {
        "error_type": "ExecutionTimeout",
        "error_message": "Code execution exceeded 30 second timeout",
        "timeout_limit": 30,
        "execution_time": 30.001,
        "last_executed_line": 15,
        "context": "Infinite loop or long-running operation detected",
        "partial_output": "Output generated before timeout...",
        "suggestions": [
            "Optimize code for better performance",
            "Add break conditions to loops",
            "Request longer timeout if needed",
            "Split long operations into smaller chunks"
        ]
    }
}
```

### 6. Memory Errors
```json
{
    "success": false,
    "error_category": "memory_error",
    "error_details": {
        "error_type": "MemoryError",
        "error_message": "Memory limit of 100MB exceeded",
        "memory_limit": "100MB",
        "memory_used": "105MB",
        "context": "Large data structure or memory leak detected",
        "suggestions": [
            "Optimize memory usage in your code",
            "Process data in smaller chunks",
            "Use generators instead of lists for large datasets",
            "Request higher memory limit if necessary"
        ]
    }
}
```

## Detailed Exception Information

### Exception Tracking
```python
@dataclass
class ExceptionInfo:
    type: str                    # Exception class name
    message: str                 # Exception message
    traceback: List[TracebackFrame]  # Detailed traceback
    full_traceback: str          # Complete traceback string
    local_variables: Dict[str, str]  # Variables at error point
    global_variables: Dict[str, str] # Global variables
    context: str                 # Human-readable context
    suggestions: List[str]       # Helpful suggestions

@dataclass
class TracebackFrame:
    filename: str
    line_number: int
    function_name: str
    code_line: str
    local_vars: Dict[str, str]
```

## Ray's Error Analysis Capabilities

### 1. Intelligent Error Interpretation
Ray will receive:
- **Root Cause Analysis**: What actually caused the error
- **Context Information**: State of variables and execution environment
- **Actionable Suggestions**: Specific steps to fix the problem
- **Code Snippets**: Exact lines that caused issues

### 2. Progressive Error Details
```json
{
    "error_summary": "NameError on line 3: undefined variable",
    "error_details": {
        "immediate_cause": "Variable 'result' used before definition",
        "contributing_factors": [
            "Variable defined in conditional block that didn't execute",
            "Possible typo in variable name"
        ],
        "execution_context": {
            "variables_in_scope": ["x", "y", "total"],
            "last_successful_line": 2,
            "execution_path": ["line 1", "line 2", "line 3 (failed)"]
        }
    }
}
```

### 3. Multi-Level Error Reporting
- **Level 1**: Quick error summary for immediate understanding
- **Level 2**: Detailed technical information for debugging
- **Level 3**: Complete execution context and suggestions
- **Level 4**: Full system state and diagnostic information

## Error Recovery Information

### Partial Execution Results
Even when code fails, Ray gets:
```json
{
    "success": false,
    "partial_results": {
        "completed_lines": 5,
        "total_lines": 10,
        "stdout_before_error": "Processing item 1\nProcessing item 2\n",
        "variables_before_error": {
            "processed_count": 2,
            "current_item": "item_3",
            "results": "[1, 4]"
        },
        "successful_operations": [
            "Variable initialization",
            "Loop setup",
            "First 2 iterations"
        ]
    }
}
```

### Recovery Suggestions
```json
{
    "recovery_options": [
        {
            "option": "fix_and_retry",
            "description": "Fix the variable name and run again",
            "suggested_fix": "Change 'undefined_variable' to 'defined_variable'"
        },
        {
            "option": "partial_execution",
            "description": "Run only the successful part of the code",
            "code_snippet": "# First 2 lines that worked:\nx = 10\ny = 20"
        },
        {
            "option": "debug_mode",
            "description": "Run in step-by-step debug mode",
            "next_steps": ["Add debug prints", "Check variable values"]
        }
    ]
}
```

## Security Error Details

### Blocked Operations
```json
{
    "security_violation": {
        "attempted_operation": "file_write",
        "blocked_code": "open('/etc/passwd', 'w')",
        "reason": "File write access denied in strict mode",
        "alternative_approaches": [
            "Use temporary files in allowed directory",
            "Request specific file permissions",
            "Use in-memory data structures"
        ]
    }
}
```

## Real-Time Error Monitoring

### Live Error Tracking
Ray can receive real-time updates during execution:
```json
{
    "execution_status": "error_occurred",
    "error_stream": [
        {
            "timestamp": "2025-01-28T10:30:01Z",
            "level": "warning",
            "message": "Variable 'temp' used before assignment"
        },
        {
            "timestamp": "2025-01-28T10:30:02Z",
            "level": "error",
            "message": "NameError: name 'temp' is not defined"
        }
    ]
}
```

## Error Logging and History

### Comprehensive Error Logs
```json
{
    "error_history": [
        {
            "execution_id": "exec_123",
            "timestamp": "2025-01-28T10:30:00Z",
            "error_type": "NameError",
            "resolution": "Fixed variable name",
            "learning": "Always check variable names for typos"
        }
    ],
    "common_errors": [
        {
            "error_pattern": "NameError with undefined variables",
            "frequency": 15,
            "typical_causes": ["Typos", "Scope issues", "Initialization problems"]
        }
    ]
}
```

## Summary

**Ray will receive:**
✅ **Complete error details** with full tracebacks
✅ **Contextual information** about what went wrong
✅ **Actionable suggestions** for fixing problems
✅ **Partial results** from successful parts of execution
✅ **Security violation details** with alternatives
✅ **Recovery options** and next steps
✅ **Real-time error monitoring** during execution
✅ **Historical error patterns** for learning

This comprehensive error handling ensures Ray can understand, learn from, and effectively respond to any issues during Python code execution.