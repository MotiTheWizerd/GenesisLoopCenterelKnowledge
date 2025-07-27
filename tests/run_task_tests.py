"""
Test runner for task module tests.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_task_tests():
    """Run all task module tests."""
    print("🧪 Running Task Module Tests")
    print("=" * 50)
    
    # Run tests with verbose output
    exit_code = pytest.main([
        "tests/modules/task/",
        "-v",
        "--tb=short",
        "--color=yes"
    ])
    
    if exit_code == 0:
        print("\n✅ All task tests passed!")
    else:
        print("\n❌ Some task tests failed!")
    
    return exit_code

if __name__ == "__main__":
    exit_code = run_task_tests()
    sys.exit(exit_code)