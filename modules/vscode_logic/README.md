# VSCode Logic Module

## Overview

The VSCode Logic module provides capabilities for Ray to interact with VSCode. It enables Ray to send structured responses to VSCode, including reasoning for the next round of conversation and additional data. The module integrates with the `/vscode/response` route to forward responses to the VSCode extension.

## Key Features

- **Structured Responses**: Send formatted responses to VSCode with clear structure
- **Conversation Continuity**: Track conversation state with is_final flag
- **Reasoning Transparency**: Include Ray's reasoning for the next round
- **Additional Data Support**: Attach nested data structures for rich interactions

## Module Structure

- **models.py**: Defines data models for VSCode Logic operations
- **handler.py**: Implements the VSCodeLogicHandler for processing VSCode Logic tasks
- **__init__.py**: Exports the module components

## Usage Example

```python
import asyncio
from datetime import datetime

# Create a VSCode Logic task
vscode_task = {
    "task": [{
        "action": "send_vs_response",
        "message": "Hello, this is a response from Ray to the VSCode user!",
        "ray_prompt": "I'm providing a helpful response to the user's question.",
        "is_final": False,
        "timestamp": datetime.now().isoformat(),
        "additional_data": {
            "nested": "structure",
            "works": True
        }
    }],
    "assigned_by": "ray",
    "execute_immediately": True
}

async def main():
    # Create a task request
    task_request = TaskRequestFromRay(**vscode_task)
    
    # Process the task
    response = task_manager.create_batch_tasks(task_request)
    print(response)

# Run the async function
asyncio.run(main())
```

## Integration with Task System

The VSCode Logic module integrates with Ray's task system through the `_execute_vscode_logic_action` method in the TaskManager class. This method handles VSCode Logic operations by:

1. Importing the vscode_logic_manager from the module
2. Creating a VSCodeTaskRequest with the task data
3. Executing the asynchronous VSCode Logic operation using asyncio
4. Forwarding the response to the VSCode extension via the `/vscode/response` route
5. Returning the results

The module uses the `forward_vscode_response` function from `modules.routes.coding_routes` to send the response to the VSCode extension at `http://localhost:3001/ray-response`.

## Data Models

### VSCodeLogicRequest

Represents a request for VSCode Logic operations with fields:

- **action**: The VSCode action to perform (e.g., "send_vs_response")
- **message**: Response to user
- **ray_prompt**: Reasoning for next round
- **is_final**: Whether this is the final response in a conversation
- **timestamp**: When the request was created
- **additional_data**: Additional data for the request

### VSCodeLogicResponse

Represents a response from VSCode Logic operations with fields:

- **success**: Whether the operation succeeded
- **action**: The VSCode action that was performed
- **message**: Response sent to user
- **is_final**: Whether this is the final response
- **timestamp**: When the operation was completed
- **execution_time_ms**: Time taken to complete operation in milliseconds
- **error_message**: Error message if operation failed

## Testing

The module includes comprehensive tests for both models and handler functionality:

- **test_models.py**: Tests for VSCode Logic models
- **test_handler.py**: Tests for VSCode Logic handler
- **test_forward_integration.py**: Tests for integration with forward_vscode_response function

To run the tests, use the provided run_tests.py script:

```bash
python tests/modules/vscode_logic/run_tests.py
```

### Test Requirements

The tests require the pytest-asyncio plugin for testing asynchronous code. Install it with:

```bash
pip install pytest-asyncio
```