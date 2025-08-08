#!/usr/bin/env python3
"""
Test runner for Excel-PDF Values Validator
Runs all tests and provides a summary
"""

import unittest
import sys
import os

def run_integration_tests():
    """Run integration tests (excluding Docker tests)"""
    # Run specific test patterns, excluding Docker deployment tests
    loader = unittest.TestLoader()
    test_dir = os.path.dirname(__file__)
    
    # Load specific test files
    test_files = [
        'test_integration.py',
        'test_excel_processor.py', 
        'test_pdf_processor.py',
        'test_multimodal_pdf_processor.py'
    ]
    
    suite = unittest.TestSuite()
    for test_file in test_files:
        try:
            test_module = loader.loadTestsFromName(test_file.replace('.py', ''))
            suite.addTest(test_module)
        except Exception as e:
            print(f"Warning: Could not load {test_file}: {e}")
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_all_tests():
    """Run all non-Docker tests"""
    return run_integration_tests()

def check_dependencies():
    """Check if required dependencies are available"""
    required_packages = {
        'fitz': 'PyMuPDF',
        'pandas': 'pandas', 
        'openpyxl': 'openpyxl',
        'sentence_transformers': 'sentence-transformers'
    }
    
    optional_packages = {
        'PIL': 'Pillow',
        'torch': 'torch',
        'torchvision': 'torchvision',
        'transformers': 'transformers',
        'pytesseract': 'pytesseract'
    }
    
    missing = []
    for module, package in required_packages.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    optional_missing = []
    for module, package in optional_packages.items():
        try:
            __import__(module)
        except ImportError:
            optional_missing.append(package)
    
    if missing:
        print("Missing required packages:")
        for package in missing:
            print(f"  - {package}")
        print("\nInstall with: pip install " + " ".join(missing))
        return False
    
    if optional_missing:
        print("Missing optional packages (multimodal features may not work):")
        for package in optional_missing:
            print(f"  - {package}")
        print("\nInstall with: pip install " + " ".join(optional_missing))
        print("\nProceeding with tests (optional features will be skipped)...\n")
    
    return True

if __name__ == "__main__":
    print("Excel-PDF Values Validator - Test Suite")
    print("=" * 50)
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Run tests
    success = run_all_tests()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed!")
        sys.exit(1)
