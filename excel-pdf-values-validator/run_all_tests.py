#!/usr/bin/env python3
"""
Comprehensive test runner for Excel-PDF Values Validator
Runs unit tests, integration tests, and Docker deployment tests
"""

import sys
import os
import subprocess
import argparse

def run_unit_tests():
    """Run unit tests"""
    print("\n" + "=" * 60)
    print("RUNNING UNIT TESTS")
    print("=" * 60)
    
    # Test multimodal PDF processor
    result1 = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/test_multimodal_pdf_processor.py",
        "-v"
    ], cwd=os.getcwd())
    
    # Test main app (needs to run from fastapi/app directory)
    result2 = subprocess.run([
        sys.executable, "-m", "pytest", 
        "../../tests/test_main.py",
        "-v"
    ], cwd=os.path.join(os.getcwd(), "fastapi", "app"))
    
    return result1.returncode == 0 and result2.returncode == 0

def run_integration_tests():
    """Run integration tests"""
    print("\n" + "=" * 60)
    print("RUNNING INTEGRATION TESTS")
    print("=" * 60)
    
    result = subprocess.run([
        sys.executable, "tests/run_tests.py"
    ], cwd=os.getcwd())
    
    return result.returncode == 0

def run_docker_tests():
    """Run Docker deployment tests"""
    print("\n" + "=" * 60)
    print("RUNNING DOCKER DEPLOYMENT TESTS")
    print("=" * 60)
    
    result = subprocess.run([
        sys.executable, "tests/test_docker_deployment.py"
    ], cwd=os.getcwd())
    
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description="Run comprehensive test suite")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--docker", action="store_true", help="Run Docker tests only")
    parser.add_argument("--skip-docker", action="store_true", help="Skip Docker tests")
    
    args = parser.parse_args()
    
    print("Excel-PDF Values Validator - Comprehensive Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run specific test types if requested
    if args.unit:
        results.append(("Unit Tests", run_unit_tests()))
    elif args.integration:
        results.append(("Integration Tests", run_integration_tests()))
    elif args.docker:
        results.append(("Docker Tests", run_docker_tests()))
    else:
        # Run all tests
        results.append(("Unit Tests", run_unit_tests()))
        results.append(("Integration Tests", run_integration_tests()))
        
        if not args.skip_docker:
            results.append(("Docker Tests", run_docker_tests()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("The multimodal PDF processor is ready for deployment.")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please fix the failing tests before deployment.")
        sys.exit(1)

if __name__ == "__main__":
    main()
