#!/usr/bin/env python3
"""
Run integration tests for the GenesisLoop project.

This script runs the integration tests for the GenesisLoop project,
including the VSCode response flow test.
"""

import os
import sys
import pytest

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


def main():
    """Run the integration tests."""
    print("🧪 Running integration tests...")
    
    # Get the directory of this script
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Run the tests
    result = pytest.main([
        test_dir,
        '-v',  # Verbose output
        '--asyncio-mode=strict',  # Strict asyncio mode
    ])
    
    # Return the exit code
    return result


if __name__ == "__main__":
    sys.exit(main())