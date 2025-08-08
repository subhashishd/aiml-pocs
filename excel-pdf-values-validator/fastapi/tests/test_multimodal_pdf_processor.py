import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from PIL import Image
import torch

# Add the fastapi app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fastapi', 'app'))

from services.local_multimodal_pdf_processor import LocalMultimodalPDFProcessor

class TestMultimodalPDFProcessor(unittest.TestCase):
    
    def setUp(self):
        # Mock model loading to prevent actual model downloads
        with patch.object(LocalMultimodalPDFProcessor, '_load_local_models'):
            self.processor = LocalMultimodalPDFProcessor()
    
    @patch('torch.cuda.is_available', return_value=False)  # Force CPU for tests
    def test_initialization(self, mock_cuda):
        """Test processor initialization"""
        with patch.object(LocalMultimodalPDFProcessor, '_load_local_models'):
            processor = LocalMultimodalPDFProcessor()
            self.assertIsNotNone(processor)
            self.assertEqual(processor.device, torch.device('cpu'))
    
    def test_model_output_parsing(self):
        """Test parsing of model output text"""
        # Test the actual parsing method
        test_text = "Volume: 30.8 m³\nTemperature: 25.5 °C\nPressure = 1.2 bar"
        
        extractions = self.processor._parse_model_output(test_text)
        
        # Should extract 3 parameter-value pairs
        self.assertGreater(len(extractions), 0)
        
        # Check that values are parsed correctly
        for extraction in extractions:
            self.assertIn('parameter', extraction)
            self.assertIn('value', extraction)
            self.assertIn('unit', extraction)
            self.assertIsInstance(extraction['value'], float)
    
    def test_extractions_to_chunks_conversion(self):
        """Test conversion of extractions to chunk format"""
        test_extractions = [
            {'parameter': 'Volume', 'value': 30.8, 'unit': 'm³'},
            {'parameter': 'Temperature', 'value': 25.5, 'unit': '°C'}
        ]
        
        chunks = self.processor._convert_extractions_to_chunks(
            test_extractions, 'test.pdf', 1
        )
        
        self.assertEqual(len(chunks), 2)
        for chunk in chunks:
            self.assertIn('file_name', chunk)
            self.assertIn('chunk_text', chunk)
            self.assertIn('page', chunk)
            self.assertIn('extraction_method', chunk)
            self.assertEqual(chunk['extraction_method'], 'local_multimodal')
    
    def test_ocr_fallback(self):
        """Test OCR fallback when vision model is not available"""
        try:
            import pytesseract
        except ImportError:
            self.skipTest("pytesseract not available")
        
        with patch('pytesseract.image_to_string') as mock_ocr:
            # Mock OCR output
            mock_ocr.return_value = "Volume: 30.8 m³\nTemperature: 25.5 °C"
            
            # Create a dummy PIL image
            mock_image = MagicMock(spec=Image.Image)
            
            # Test OCR fallback
            chunks = self.processor._extract_from_image_ocr(mock_image, 'test.pdf', 1)
            
            # Should extract chunks from OCR text
            self.assertGreater(len(chunks), 0)
            for chunk in chunks:
                self.assertEqual(chunk['extraction_method'], 'ocr_fallback')
    
    @patch('fitz.open')
    def test_fallback_text_extraction(self, mock_fitz_open):
        """Test fallback text extraction"""
        # Mock PyMuPDF document
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Volume: 30.8\nTemperature: 25.5"
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz_open.return_value = mock_doc
        
        chunks = self.processor._fallback_text_extraction('test.pdf', 'test.pdf')
        
        # Should extract chunks from text
        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertEqual(chunk['extraction_method'], 'text_fallback')

if __name__ == '__main__':
    unittest.main()
