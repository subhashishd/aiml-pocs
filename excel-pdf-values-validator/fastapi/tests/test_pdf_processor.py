import unittest
import sys
import os

# Add the fastapi app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from services.pdf_processor import PDFProcessor

class TestPDFProcessor(unittest.TestCase):
    def setUp(self):
        self.pdf_processor = PDFProcessor()
        self.sample_pdf_path = os.path.join(os.path.dirname(__file__), '..', '..', 'files', 'sample_generic_parameters.pdf')
        
    def test_pdf_exists(self):
        """Test that the sample PDF file exists"""
        self.assertTrue(os.path.exists(self.sample_pdf_path), 
                       f"Sample PDF file not found at {self.sample_pdf_path}")
    
    def test_process_pdf(self):
        """Test PDF processing functionality"""
        if not os.path.exists(self.sample_pdf_path):
            self.skipTest("Sample PDF file not found")
            
        chunks = self.pdf_processor.process_pdf(self.sample_pdf_path, "test.pdf")
        
        # Basic assertions
        self.assertIsInstance(chunks, list, "Should return a list of chunks")
        self.assertGreater(len(chunks), 0, "Should extract at least some chunks")
        
        # Check chunk structure
        if chunks:
            chunk = chunks[0]
            self.assertIn('file_name', chunk, "Chunk should have file_name")
            self.assertIn('chunk_text', chunk, "Chunk should have chunk_text")
            self.assertIn('embedding', chunk, "Chunk should have embedding placeholder")
    
    def test_is_numeric(self):
        """Test numeric detection functionality"""
        # Test numeric values
        self.assertTrue(self.pdf_processor._is_numeric("123"))
        self.assertTrue(self.pdf_processor._is_numeric("123.45"))
        self.assertTrue(self.pdf_processor._is_numeric("-123.45"))
        self.assertTrue(self.pdf_processor._is_numeric("+123.45"))
        
        # Test non-numeric values
        self.assertFalse(self.pdf_processor._is_numeric("abc"))
        self.assertFalse(self.pdf_processor._is_numeric(""))
        self.assertFalse(self.pdf_processor._is_numeric("123abc"))
    
    def test_extract_param_value_from_line(self):
        """Test parameter-value extraction from text lines"""
        # Test colon-separated format
        result = self.pdf_processor._extract_param_value_from_line("Volume: 30.8")
        self.assertEqual(result, ("Volume", "30.8"))
        
        # Test space-separated format
        result = self.pdf_processor._extract_param_value_from_line("Mass 13791.1 kg")
        self.assertIsNotNone(result)
        
        # Test invalid format
        result = self.pdf_processor._extract_param_value_from_line("Just some text")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
