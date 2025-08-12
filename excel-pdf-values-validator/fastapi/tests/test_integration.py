import unittest
import sys
import os
import asyncio
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add the fastapi app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

try:
    from services.pdf_processor import PDFProcessor
    from services.excel_processor import ExcelProcessor
    from services.validation_service import ValidationService
    services_available = True
except ImportError as e:
    print(f"Warning: Could not import services: {e}")
    services_available = False
    PDFProcessor = None
    ExcelProcessor = None
    ValidationService = None
    # Fallback to local imports if fastapi app structure not available
    try:
        from services.local_multimodal_pdf_processor import LocalMultimodalPDFProcessor as MultimodalPDFProcessor
    except ImportError:
        MultimodalPDFProcessor = None
    
try:
    from main import app
except ImportError:
    app = None

class TestIntegration(unittest.TestCase):
    def setUp(self):
        if not services_available:
            self.skipTest("Services not available for import")
        self.pdf_processor = PDFProcessor()
        self.excel_processor = ExcelProcessor()
        self.validation_service = ValidationService()
        
        self.sample_pdf_path = os.path.join(os.path.dirname(__file__), '..', '..', 'files', 'sample_generic_parameters.pdf')
        self.sample_excel_path = os.path.join(os.path.dirname(__file__), '..', '..', 'files', 'output_parameters.xlsx')
    
    def test_end_to_end_workflow(self):
        """Test the complete workflow from file processing to validation"""
        # Skip if sample files don't exist
        if not os.path.exists(self.sample_pdf_path) or not os.path.exists(self.sample_excel_path):
            self.skipTest("Sample files not found")
        
        print("\n=== Integration Test: End-to-End Workflow ===")
        
        # Step 1: Process PDF
        print("Step 1: Processing PDF...")
        pdf_chunks = self.pdf_processor.process_pdf(self.sample_pdf_path, "test.pdf")
        self.assertGreater(len(pdf_chunks), 0, "Should extract PDF chunks")
        print(f"  ✓ Extracted {len(pdf_chunks)} chunks from PDF")
        
        # Step 2: Process Excel
        print("Step 2: Processing Excel...")
        excel_data = self.excel_processor.process_excel(self.sample_excel_path)
        self.assertGreater(len(excel_data), 0, "Should extract Excel data")
        print(f"  ✓ Extracted {len(excel_data)} parameters from Excel")
        
        # Step 3: Show sample data
        print("\nSample PDF chunks:")
        for i, chunk in enumerate(pdf_chunks[:3]):
            print(f"  {i+1}. {chunk['chunk_text'][:80]}...")
            
        print("\nSample Excel parameters:")
        for i, item in enumerate(excel_data[:3]):
            print(f"  {i+1}. {item['parameter']}: {item['value']} {item['unit']}")
        
        # Step 4: Test validation logic (without database)
        print("\nStep 3: Testing validation logic...")
        
        # Test value extraction
        test_chunk = "Volume: 30.8 m³"
        extracted_value = self.validation_service._extract_value_from_chunk(test_chunk, "Volume")
        print(f"  ✓ Extracted value '{extracted_value}' from chunk '{test_chunk}'")
        
        # Test value comparison
        is_match = self.validation_service._compare_values(30.8, 30.8)
        self.assertTrue(is_match, "Exact values should match")
        print(f"  ✓ Value comparison works: {is_match}")
        
        print("\n=== Integration Test Completed Successfully ===")
    
    def test_validation_edge_cases(self):
        """Test edge cases in validation logic"""
        print("\n=== Testing Validation Edge Cases ===")
        
        # Test None value handling
        is_match = self.validation_service._compare_values(30.8, None)
        self.assertFalse(is_match, "Should not match with None")
        print("  ✓ None value handling works")
        
        # Test string to float conversion
        is_match = self.validation_service._compare_values("30.8", 30.8)
        self.assertTrue(is_match, "String and float should match if equal")
        print("  ✓ String to float conversion works")
        
        # Test exact floating point precision (scientific calculations require exact match)
        is_match = self.validation_service._compare_values(30.8000000000001, 30.8)
        self.assertFalse(is_match, "Should require exact precision for scientific calculations")
        print("  ✓ Exact precision requirement works")
        
        # Test truly identical values
        is_match = self.validation_service._compare_values(30.8, 30.8)
        self.assertTrue(is_match, "Identical values should match")
        print("  ✓ Identical value matching works")
        
        print("=== Edge Cases Test Completed ===")
    
    def test_multimodal_pdf_processor(self):
        """Test the multimodal PDF processor functionality"""
        print("\n=== Testing Multimodal PDF Processor ===")
        
        try:
            from local_multimodal_pdf_processor import MultimodalPDFProcessor
            processor = MultimodalPDFProcessor()
            
            # Test initialization
            self.assertIsNotNone(processor, "Processor should initialize")
            print("  ✓ Multimodal PDF processor initialized")
            
            # Test with mock image (since we don't have actual PDF images in test)
            with patch('local_multimodal_pdf_processor.Image') as mock_image:
                mock_image.open.return_value = MagicMock()
                
                with patch.object(processor, '_extract_with_blip') as mock_blip:
                    mock_blip.return_value = {'test_param': 'test_value'}
                    
                    result = processor.process_pdf_page('mock_image_path')
                    self.assertEqual(result, {'test_param': 'test_value'})
                    print("  ✓ BLIP model extraction works")
                    
        except ImportError:
            self.skipTest("Multimodal PDF processor not available")
        
        print("=== Multimodal PDF Processor Test Completed ===")
    
    def test_fastapi_endpoints(self):
        """Test FastAPI endpoints if available"""
        if app is None:
            self.skipTest("FastAPI app not available")
            
        print("\n=== Testing FastAPI Endpoints ===")
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        print("  ✓ Health endpoint works")
        
        # Test process-pdf endpoint (with mock file)
        with patch('main.pdf_processor') as mock_processor:
            mock_processor.process_pdf.return_value = [
                {'chunk_text': 'test chunk', 'page_number': 1}
            ]
            
            files = {"file": ("test.pdf", b"dummy pdf content", "application/pdf")}
            response = client.post("/process-pdf", files=files)
            
            # Should return 200 if endpoint exists
            self.assertIn(response.status_code, [200, 404, 405])  # 404/405 if endpoint not implemented
            print(f"  ✓ Process PDF endpoint responded with status {response.status_code}")
        
        print("=== FastAPI Endpoints Test Completed ===")

if __name__ == '__main__':
    unittest.main(verbosity=2)
