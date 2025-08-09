""
Tests for VSCode Logic module models.
"""

import pytest
from datetime import datetime
from modules.vscode_logic.models import VSCodeAction, VSCodeLogicRequest, VSCodeLogicResponse, VSCodeTaskRequest


class TestVSCodeLogicModels:
    def test_vscode_action_enum(self):