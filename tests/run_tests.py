#!/usr/bin/env python3
"""
Test runner script for compare-har.py tests

This script provides an easy way to run all tests with different configurations.
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and print the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print(f"Error: Command not found. Make sure pytest is installed.")
        return False

def main():
    """Main test runner function."""
    print("HAR Comparison Tool - Test Suite Runner")
    print("=" * 60)
    
    # Check if pytest is available
    try:
        subprocess.run(["pytest", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: pytest is not installed or not in PATH")
        print("Install with: pip install pytest")
        sys.exit(1)
    
    # Check if the main module exists
    main_module_path = os.path.join("..", "compare_har.py")
    if not os.path.exists(main_module_path):
        print("Error: compare_har.py not found in parent directory")
        sys.exit(1)
    
    # Run different test configurations
    test_configs = [
        {
            "cmd": ["pytest", "test_compare_har.py", "-v"],
            "description": "Basic test run with verbose output"
        },
        {
            "cmd": ["pytest", "test_compare_har.py", "-v", "--tb=long"],
            "description": "Test run with detailed traceback"
        },
        {
            "cmd": ["pytest", "test_compare_har.py", "-v", "-k", "test_load"],
            "description": "Run only load_har tests"
        },
        {
            "cmd": ["pytest", "test_compare_har.py", "-v", "-k", "test_extract"],
            "description": "Run only extract_timings tests"
        },
        {
            "cmd": ["pytest", "test_compare_har.py", "-v", "-k", "test_compare"],
            "description": "Run only compare_har_files tests"
        },
        {
            "cmd": ["pytest", "test_compare_har.py", "-v", "-k", "integration"],
            "description": "Run only integration tests"
        }
    ]
    
    # Optional: Run with coverage if pytest-cov is available
    try:
        subprocess.run(["pytest", "--cov", "--version"], capture_output=True, check=True)
        test_configs.append({
            "cmd": ["pytest", "test_compare_har.py", "--cov=compare_har", "--cov-report=html", "--cov-report=term"],
            "description": "Test run with coverage report"
        })
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Note: pytest-cov not available, skipping coverage tests")
    
    # Run each test configuration
    results = []
    for config in test_configs:
        success = run_command(config["cmd"], config["description"])
        results.append((config["description"], success))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    for description, success in results:
        status = "PASSED" if success else "FAILED"
        print(f"{status:>8}: {description}")
    
    # Overall result
    all_passed = all(success for _, success in results)
    if all_passed:
        print(f"\n🎉 All test configurations passed!")
        sys.exit(0)
    else:
        print(f"\n❌ Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()