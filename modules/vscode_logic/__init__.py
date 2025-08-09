"""
VSCode Logic module for Ray's consciousness.

This module provides VSCode interaction capabilities including:
- Sending responses to VSCode
- Processing VSCode requests
- Managing VSCode communication
"""

from .handler import vscode_logic_manager
from .models import VSCodeLogicRequest, VSCodeLogicResponse, VSCodeTaskRequest, VSCodeAction

__all__ = [
    'vscode_logic_manager',
    'VSCodeLogicRequest',
    'VSCodeLogicResponse',
    'VSCodeTaskRequest',
    'VSCodeAction'
]