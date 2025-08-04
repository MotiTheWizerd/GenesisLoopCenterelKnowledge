#!/usr/bin/env python3
"""
Test if the ActionType enum includes the new get_current_directory value.
"""

import sys
sys.path.append('.')

from modules.directory.models import ActionType

print("🧪 Testing ActionType enum...")

# Test if the new action exists
try:
    action = ActionType.GET_CURRENT_DIRECTORY
    print(f"✅ ActionType.GET_CURRENT_DIRECTORY exists: {action}")
    print(f"   Value: '{action.value}'")
except AttributeError as e:
    print(f"❌ ActionType.GET_CURRENT_DIRECTORY not found: {e}")

# Test if we can create it from string
try:
    action_from_string = ActionType("get_current_directory")
    print(f"✅ ActionType('get_current_directory') works: {action_from_string}")
except ValueError as e:
    print(f"❌ ActionType('get_current_directory') failed: {e}")

# List all available actions
print(f"\n📋 All available ActionType values:")
for action in ActionType:
    print(f"   - {action.name} = '{action.value}'")

print(f"\n🎯 Total actions: {len(list(ActionType))}")

# Test the specific case that's failing
test_action = "get_current_directory"
try:
    converted = ActionType(test_action)
    print(f"✅ Converting '{test_action}' to ActionType works: {converted}")
except Exception as e:
    print(f"❌ Converting '{test_action}' to ActionType failed: {e}")
    print(f"   This is likely why the task handler is failing")