"""
Comprehensive test runner for all AI consciousness server components.

This script runs tests organized by feature groups and provides detailed reporting.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_feature_tests():
    """Run all tests organized by feature groups."""
    print("🧪 AI Consciousness Server - Comprehensive Test Suite")
    print("=" * 60)
    
    # Define test groups
    test_groups = {
        "Task System": "tests/modules/task/",
        "Heartbeat System": "tests/modules/heartbeat/",
        "Reflection System": "tests/modules/reflect/", 
        "Routing System": "tests/modules/routes/",
        "Logging System": "tests/modules/logging/",
        "Directory System": "tests/modules/directory/",
        "Read File System": "tests/modules/directory/test_read_file_integration.py"
    }
    
    total_passed = 0
    total_failed = 0
    
    for group_name, test_path in test_groups.items():
        print(f"\n🎯 Running {group_name} Tests")
        print("-" * 40)
        
        # Run tests for this group
        exit_code = pytest.main([
            test_path,
            "-v",
            "--tb=short",
            "--color=yes",
            "-q"
        ])
        
        if exit_code == 0:
            print(f"✅ {group_name}: All tests passed!")
            total_passed += 1
        else:
            print(f"❌ {group_name}: Some tests failed!")
            total_failed += 1
    
    # Summary
    print(f"\n📊 Test Summary")
    print("=" * 30)
    print(f"✅ Passed Groups: {total_passed}")
    print(f"❌ Failed Groups: {total_failed}")
    print(f"📈 Success Rate: {(total_passed/(total_passed+total_failed)*100):.1f}%")
    
    if total_failed == 0:
        print(f"\n🎉 All feature groups passed! System is healthy.")
        return 0
    else:
        print(f"\n⚠️  Some feature groups failed. Check output above.")
        return 1

def run_quick_tests():
    """Run a quick smoke test of core functionality."""
    print("🚀 Quick Smoke Tests")
    print("=" * 30)
    
    # Run just the most critical tests
    critical_tests = [
        "tests/modules/task/test_models.py::TestTaskRequestFromRay::test_create_basic_request",
        "tests/modules/task/test_handler.py::TestTaskManager::test_create_batch_tasks",
        "tests/modules/routes/test_reflect_routes.py"
    ]
    
    exit_code = pytest.main([
        *critical_tests,
        "-v",
        "--tb=short",
        "--color=yes"
    ])
    
    if exit_code == 0:
        print("✅ Quick tests passed! Core functionality is working.")
    else:
        print("❌ Quick tests failed! Check core functionality.")
    
    return exit_code

def run_specific_feature(feature_name: str):
    """Run tests for a specific feature."""
    feature_map = {
        "task": "tests/modules/task/",
        "heartbeat": "tests/modules/heartbeat/",
        "reflect": "tests/modules/reflect/",
        "routes": "tests/modules/routes/",
        "logging": "tests/modules/logging/",
        "directory": "tests/modules/directory/",
        "read_file": "tests/run_read_file_tests.py"
    }
    
    if feature_name not in feature_map:
        print(f"❌ Unknown feature: {feature_name}")
        print(f"Available features: {', '.join(feature_map.keys())}")
        return 1
    
    test_path = feature_map[feature_name]
    print(f"🎯 Running {feature_name.title()} Tests")
    print("=" * 40)
    
    exit_code = pytest.main([
        test_path,
        "-v",
        "--tb=short",
        "--color=yes"
    ])
    
    return exit_code

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Consciousness Server Test Runner")
    parser.add_argument("--quick", action="store_true", help="Run quick smoke tests only")
    parser.add_argument("--feature", type=str, help="Run tests for specific feature (task, heartbeat, reflect, routes, logging)")
    
    args = parser.parse_args()
    
    if args.quick:
        exit_code = run_quick_tests()
    elif args.feature:
        exit_code = run_specific_feature(args.feature)
    else:
        exit_code = run_feature_tests()
    
    sys.exit(exit_code)