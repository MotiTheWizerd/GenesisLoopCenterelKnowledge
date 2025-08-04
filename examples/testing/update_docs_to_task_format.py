#!/usr/bin/env python3
"""
Script to update the directory API documentation from old search_type format 
to new task-based format with action field.
"""

import re

# Read the current documentation
with open('docs/api-reference/directory-api-json-reference.md', 'r') as f:
    content = f.read()

print("🔄 Converting documentation from search_type to task-based format...")

# Function to convert old format to new task format
def convert_to_task_format(match):
    # Extract the JSON content
    json_content = match.group(1)
    
    # Replace search_type with action
    json_content = json_content.replace('"search_type":', '"action":')
    
    # Wrap in task array format
    new_format = f'''{{
  "task": [
    {{{json_content}
    }}
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}}'''
    
    return new_format

# Pattern to match JSON blocks with search_type
pattern = r'```json\s*\{\s*"search_type":[^}]+(?:\}[^}]*)*\}\s*```'

# Find all matches
matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
print(f"Found {len(matches)} JSON blocks to convert")

# Replace old format with new format
def replace_json_block(match):
    old_json = match.group(0)
    
    # Extract just the inner JSON object
    inner_match = re.search(r'```json\s*(\{.*?\})\s*```', old_json, re.DOTALL)
    if inner_match:
        inner_json = inner_match.group(1)
        # Replace search_type with action
        inner_json = inner_json.replace('"search_type":', '"action":')
        
        # Create new task format
        new_json = f'''```json
{{
  "task": [
    {{{inner_json}
    }}
  ],
  "assigned_by": "ray",
  "execute_immediately": true,
  "self_destruct": true
}}
```'''
        return new_json
    
    return old_json

# Apply the replacement
new_content = re.sub(pattern, replace_json_block, content, flags=re.MULTILINE | re.DOTALL)

# Also update endpoint references
new_content = new_content.replace('**Endpoint:** `POST /directory/search`', '**Endpoint:** `POST /tasks`')
new_content = new_content.replace('**Endpoint:** `POST /directory/save`', '**Endpoint:** `POST /tasks`')
new_content = new_content.replace('**Endpoint:** `POST /directory/rename`', '**Endpoint:** `POST /tasks`')
new_content = new_content.replace('**Endpoint:** `POST /directory/move`', '**Endpoint:** `POST /tasks`')
new_content = new_content.replace('**Endpoint:** `POST /directory/delete`', '**Endpoint:** `POST /tasks`')
new_content = new_content.replace('**Endpoint:** `POST /directory/content-search`', '**Endpoint:** `POST /tasks`')

# Update any remaining references to the old system
new_content = new_content.replace('search_type', 'action')

# Write the updated content
with open('docs/api-reference/directory-api-json-reference.md', 'w') as f:
    f.write(new_content)

print("✅ Documentation updated successfully!")
print("📝 All search_type references converted to action")
print("🎯 All endpoints updated to POST /tasks")
print("🚀 Documentation now reflects current task-based system")