"""
Test runner for health module
"""

import sys
import os
import pytest

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def run_health_tests():
    """Run all health module tests"""
    print("💚 Running Health Module Tests...")
    print("=" * 50)
    
    # Test paths
    test_paths = [
        "tests/modules/health/test_models.py"
    ]
    
    # Run tests with verbose output
    args = [
        "-v",  # Verbose
        "--tb=short",  # Short traceback format
        "--color=yes",  # Colored output
        "-x",  # Stop on first failure
    ] + test_paths
    
    result = pytest.main(args)
    
    if result == 0:
        print("\n✅ All health module tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code: {result}")
    
    return result

if __name__ == "__main__":
    exit_code = run_health_tests()
    sys.exit(exit_code)