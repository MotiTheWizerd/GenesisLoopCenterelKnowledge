"""Example script demonstrating how to use the VSCode Logic module.

This example shows how to create and process a VSCode response task.
"""

import sys
import os
import json
import asyncio
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from modules.task.handler import task_manager
from modules.task.models import TaskRequestFromRay


async def main():
    print("🚀 VSCode Logic Module Example")
    print("================================")
    
    # Create a sample VSCode response task
    vscode_task = {
        "task": [{
            "action": "send_vs_response",
            "message": "Hello, this is a response from Ray to the VSCode user!",
            "ray_prompt": "I'm providing a helpful response to the user's question about Python.",
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
    
    # Create a task request
    task_request = TaskRequestFromRay(**vscode_task)
    
    # Process the task
    print("\n📤 Sending VSCode response task...")
    response = task_manager.create_batch_tasks(task_request)
    
    # Print the response
    print("\n📥 Task processing response:")
    print(json.dumps(response.dict(), indent=2))
    
    print("\n✅ VSCode Logic task processed successfully!")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())