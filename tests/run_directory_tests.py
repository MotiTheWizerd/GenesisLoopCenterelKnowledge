#!/usr/bin/env python3
"""
Directory module test runner.

This script runs all tests for the directory search module.
"""

import sys
import subprocess
from pathlib import Path

def run_directory_tests():
    """Run all directory module tests."""
    print("🧪 Running Directory Module Tests")
    print("=" * 50)
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    # Test files to run
    test_files = [
        "tests/modules/directory/test_models.py",
        "tests/modules/directory/test_handler.py", 
        "tests/modules/directory/test_routes.py"
    ]
    
    all_passed = True
    
    for test_file in test_files:
        test_path = project_root / test_file
        
        if not test_path.exists():
            print(f"❌ Test file not found: {test_file}")
            all_passed = False
            continue
        
        print(f"\n🔍 Running {test_file}...")
        print("-" * 40)
        
        try:
            # Run pytest on the specific test file
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                str(test_path), 
                "-v",
                "--tb=short"
            ], cwd=project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {test_file} - All tests passed!")
                print(result.stdout)
            else:
                print(f"❌ {test_file} - Some tests failed!")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                all_passed = False
                
        except Exception as e:
            print(f"❌ Error running {test_file}: {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All Directory Module Tests Passed!")
        return 0
    else:
        print("💥 Some Directory Module Tests Failed!")
        return 1

if __name__ == "__main__":
    sys.exit(run_directory_tests())