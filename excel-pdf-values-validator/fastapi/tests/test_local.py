#!/usr/bin/env python3
"""
Local testing script for PDF and Excel processing
Run this to test the core functionality before Docker deployment
"""

import sys
import os

# Add the fastapi app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from services.pdf_processor import PDFProcessor
from services.excel_processor import ExcelProcessor

def test_pdf_processing():
    """Test PDF processing with the sample file"""
    print("Testing PDF processing...")
    
    pdf_processor = PDFProcessor()
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "..", "files", "BunkerDeliveryNote-1.16.3.PDF")
    
    assert os.path.exists(pdf_path), f"PDF file not found: {pdf_path}"
    
    chunks = pdf_processor.process_pdf(pdf_path, "BunkerDeliveryNote-1.16.3.PDF")
    print(f"✓ PDF processing successful: {len(chunks)} chunks extracted")
    
    # Show first few chunks
    for i, chunk in enumerate(chunks[:5]):
        print(f"  Chunk {i+1}: {chunk['chunk_text'][:100]}...")
    
    assert len(chunks) > 0, "Should extract at least some chunks"
    assert isinstance(chunks, list), "Should return a list"

def test_excel_processing():
    """Test Excel processing with the sample file"""
    print("\nTesting Excel processing...")
    
    excel_processor = ExcelProcessor()
    excel_path = os.path.join(os.path.dirname(__file__), "..", "..", "files", "output_parameters.xlsx")
    
    assert os.path.exists(excel_path), f"Excel file not found: {excel_path}"
    
    data = excel_processor.process_excel(excel_path)
    print(f"✓ Excel processing successful: {len(data)} parameters extracted")
    
    # Show extracted data
    for item in data[:5]:
        print(f"  Parameter: {item['parameter']}, Value: {item['value']}, Unit: {item['unit']}")
    
    assert len(data) > 0, "Should extract at least some parameters"
    assert isinstance(data, list), "Should return a list"

def install_requirements():
    """Install required packages if not available"""
    required_packages = [
        'PyMuPDF',
        'openpyxl', 
        'pandas',
        'sentence-transformers'
    ]
    
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
        except ImportError:
            print(f"Installing {package}...")
            os.system(f"pip install {package}")

if __name__ == "__main__":
    print("Excel-PDF Values Validator - Local Testing")
    print("=" * 50)
    
    # Check if required packages are installed
    try:
        import fitz  # PyMuPDF
        import pandas
        import openpyxl
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please install required packages:")
        print("pip install PyMuPDF openpyxl pandas sentence-transformers")
        sys.exit(1)
    
    # Test PDF processing
    pdf_success = test_pdf_processing()
    
    # Test Excel processing  
    excel_success = test_excel_processing()
    
    print("\n" + "=" * 50)
    if pdf_success and excel_success:
        print("✓ All tests passed! Ready for Docker deployment.")
    else:
        print("✗ Some tests failed. Please check the errors above.")
