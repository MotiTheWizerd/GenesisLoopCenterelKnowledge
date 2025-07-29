#!/usr/bin/env python3
"""
Test the directory handler directly to debug the 500 error.
"""

import sys
import os
sys.path.append('.')

from modules.directory.handler import directory_manager
from modules.directory.models import DirectorySearchRequest, ActionType

# Test the handler directly
request = DirectorySearchRequest(
    action=ActionType.LIST_DIRECTORY,
    path="./modules",
    include_hidden=False,
    assigned_by="ray"
)

print("Testing directory handler directly...")
print(f"Request: {request}")

try:
    response = directory_manager.search_directory(request)
    print(f"Success! Found {response.search_result.total_results} results")
    print(f"Files: {len(response.search_result.files_found)}")
    print(f"Directories: {len(response.search_result.directories_found)}")
    
    # Show first few results
    if response.search_result.files_found:
        print("\nFirst few files:")
        for file_info in response.search_result.files_found[:3]:
            print(f"  - {file_info.name}")
    
    if response.search_result.directories_found:
        print("\nFirst few directories:")
        for dir_info in response.search_result.directories_found[:3]:
            print(f"  - {dir_info.name}/")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()