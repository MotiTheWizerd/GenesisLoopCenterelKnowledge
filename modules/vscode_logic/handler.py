"""
VSCode Logic handler for Ray's consciousness.
Provides capabilities for interacting with VSCode.
"""

import time
from typing import Dict, Any, Union, List
from datetime import datetime, timezone

from .models import (
    VSCodeLogicRequest, VSCodeLogicResponse, VSCodeTaskRequest, VSCodeAction
)
from modules.logging.middleware import log_module_call
from modules.logging.heartbeat_logger import log_heartbeat_event, EventType
from modules.routes.coding_routes import forward_vscode_response


class VSCodeLogicHandler:
    """Handler for all VSCode Logic operations in Ray's consciousness."""
    
    def __init__(self):
        self.operation_count = 0
        print("💻 VSCode Logic Handler initialized")
    
    @log_module_call("vscode_logic")
    async def handle_task(self, task_data: Dict[str, Any]) -> VSCodeLogicResponse:
        """
        Handle a VSCode Logic task.
        
        Args:
            task_data: Task data containing VSCode Logic operation details
            
        Returns:
            Response object based on operation type
        """
        try:
            # Parse the task request
            task_request = VSCodeTaskRequest(**task_data)
            action = task_request.get_action_type()
            
            print(f"💻 Processing VSCode Logic operation: {action}")
            
            if action == VSCodeAction.SEND_RESPONSE:
                return await self._handle_send_response(task_request)
            else:
                raise ValueError(f"Unsupported VSCode Logic operation: {action}")
                
        except Exception as e:
            print(f"❌ VSCode Logic operation failed: {str(e)}")
            
            # Log the error
            log_heartbeat_event(
                EventType.TASK_ERROR,
                {
                    "module": "vscode_logic",
                    "error": str(e),
                    "task_data": task_data
                },
                action="vscode_logic_error"
            )
            
            # Return error response
            return VSCodeLogicResponse(
                success=False,
                action=task_data.get("task", [{}])[0].get("action", "unknown"),
                message="",
                is_final=False,
                execution_time_ms=0,
                error_message=str(e)
            )
    
    async def _handle_send_response(self, task_request: VSCodeTaskRequest) -> VSCodeLogicResponse:
        """Handle sending a response to VSCode."""
        start_time = time.time()
        
        try:
            # Extract data from the first task item
            task_item = task_request.task[0]
            
            # Create a VSCodeLogicRequest from the task item
            vscode_request = VSCodeLogicRequest(
                action=task_item.get("action"),
                message=task_item.get("message"),
                ray_prompt=task_item.get("ray_prompt"),
                is_final=task_item.get("is_final", False),
                timestamp=task_item.get("timestamp", datetime.now(timezone.utc).isoformat()),
                additional_data=task_item.get("additional_data")
            )
            
            # Log the event
            log_heartbeat_event(
                EventType.MODULE_CALL,
                {
                    "module": "vscode_logic",
                    "action": "send_response",
                    "message_length": len(vscode_request.message),
                    "is_final": vscode_request.is_final
                },
                action="send_vs_response"
            )
            
            # Convert VSCodeLogicRequest to a dictionary for forwarding
            request_data = {
                "message": vscode_request.message,
                "ray_prompt": vscode_request.ray_prompt,
                "is_final": vscode_request.is_final,
                "timestamp": vscode_request.timestamp,
                "additional_data": vscode_request.additional_data
            }
            
            # Forward the response to VSCode using the forward_vscode_response function
            # This function handles the actual HTTP request to the VSCode extension
            await forward_vscode_response(request_data)
            
            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Return success response
            return VSCodeLogicResponse(
                success=True,
                action=vscode_request.action,
                message=vscode_request.message,
                is_final=vscode_request.is_final,
                execution_time_ms=execution_time_ms,
                error_message=None
            )
            
        except Exception as e:
            # Calculate execution time even for failures
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Log the error
            log_heartbeat_event(
                EventType.TASK_ERROR,
                {
                    "module": "vscode_logic",
                    "error": str(e),
                    "operation": "send_response"
                },
                action="vscode_logic_error"
            )
            
            # Return error response
            return VSCodeLogicResponse(
                success=False,
                action="send_vs_response",
                message="",
                is_final=False,
                execution_time_ms=execution_time_ms,
                error_message=str(e)
            )


# Create a singleton instance
vscode_logic_manager = VSCodeLogicHandler()