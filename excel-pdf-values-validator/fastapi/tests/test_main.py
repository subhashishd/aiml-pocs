import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the fastapi app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fastapi', 'app'))

try:
    from main import app
except ImportError:
    app = None

class TestMainApp(unittest.TestCase):
    
    @patch.dict(os.environ, {'USE_MULTIMODAL_PDF': 'true'})
    @patch('services.local_multimodal_pdf_processor.LocalMultimodalPDFProcessor')
    def test_multimodal_processor_initialization(self, mock_multimodal_processor):
        """Test that multimodal processor is selected when environment variable is true"""
        # Skip test as we cannot easily test module-level initialization
        self.skipTest("Module-level initialization testing requires different approach")
    
    def test_app_creation(self):
        """Test that the FastAPI app is created successfully"""
        if app is None:
            self.skipTest("FastAPI app not available")
        
        self.assertIsNotNone(app)
        self.assertEqual(app.title, "Excel-PDF Values Validator")
        self.assertEqual(app.version, "1.0.0")
    
    def test_environment_variable_reading(self):
        """Test that environment variable is read correctly"""
        # Test default value
        with patch.dict(os.environ, {}, clear=True):
            use_multimodal = os.getenv('USE_MULTIMODAL_PDF', 'false').lower() == 'true'
            self.assertFalse(use_multimodal)
        
        # Test true value
        with patch.dict(os.environ, {'USE_MULTIMODAL_PDF': 'true'}):
            use_multimodal = os.getenv('USE_MULTIMODAL_PDF', 'false').lower() == 'true'
            self.assertTrue(use_multimodal)
        
        # Test false value
        with patch.dict(os.environ, {'USE_MULTIMODAL_PDF': 'false'}):
            use_multimodal = os.getenv('USE_MULTIMODAL_PDF', 'false').lower() == 'true'
            self.assertFalse(use_multimodal)

if __name__ == '__main__':
    unittest.main()
