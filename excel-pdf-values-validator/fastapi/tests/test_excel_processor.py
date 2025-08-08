import unittest
import sys
import os

# Add the fastapi app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from services.excel_processor import ExcelProcessor

class TestExcelProcessor(unittest.TestCase):
    def setUp(self):
        self.excel_processor = ExcelProcessor()
        self.sample_excel_path = os.path.join(os.path.dirname(__file__), '..', '..', 'files', 'output_parameters.xlsx')
        
    def test_excel_exists(self):
        """Test that the sample Excel file exists"""
        self.assertTrue(os.path.exists(self.sample_excel_path), 
                       f"Sample Excel file not found at {self.sample_excel_path}")
    
    def test_process_excel(self):
        """Test Excel processing functionality"""
        if not os.path.exists(self.sample_excel_path):
            self.skipTest("Sample Excel file not found")
            
        data = self.excel_processor.process_excel(self.sample_excel_path)
        
        # Basic assertions
        self.assertIsInstance(data, list, "Should return a list of parameter data")
        self.assertGreater(len(data), 0, "Should extract at least some parameters")
        
        # Check data structure
        if data:
            item = data[0]
            self.assertIn('parameter', item, "Item should have parameter")
            self.assertIn('value', item, "Item should have value")
            self.assertIn('unit', item, "Item should have unit")
            self.assertIn('original_text', item, "Item should have original_text")
            
        # Print extracted data for verification
        print(f"\nExtracted {len(data)} parameters from Excel:")
        for i, item in enumerate(data[:5]):  # Show first 5
            print(f"  {i+1}. {item['parameter']}: {item['value']} {item['unit']}")

if __name__ == '__main__':
    unittest.main()
