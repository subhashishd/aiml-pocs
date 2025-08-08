import logging
from typing import List, Dict, Any
import openpyxl
import pandas as pd

logger = logging.getLogger(__name__)

class ExcelProcessor:
    def process_excel(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Process Excel file to extract parameter-value pairs
        Expected format: Parameter | Value | Unit
        """
        try:
            logger.info(f"Processing Excel file: {file_path}")
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Ensure required columns exist
            expected_columns = ['Parameter', 'Value', 'Unit']
            missing_columns = [col for col in expected_columns if col not in df.columns]
            
            if missing_columns:
                logger.warning(f"Missing columns: {missing_columns}")
                # Try to find columns with similar names
                df.columns = df.columns.str.strip().str.title()
            
            data = []
            for _, row in df.iterrows():
                if pd.notna(row.get('Parameter')) and pd.notna(row.get('Value')):
                    parameter = str(row['Parameter']).strip()
                    value = row['Value']
                    unit = str(row.get('Unit', '')).strip()
                    
                    # Convert value to appropriate type
                    if isinstance(value, str):
                        try:
                            # Try to convert to float for numeric values
                            value = float(value)
                        except ValueError:
                            pass  # Keep as string if not numeric
                    
                    data.append({
                        'parameter': parameter,
                        'value': value,
                        'unit': unit,
                        'original_text': f"{parameter}: {value} {unit}".strip()
                    })
            
            logger.info(f"Extracted {len(data)} parameter-value pairs from Excel")
            return data
            
        except Exception as e:
            logger.error(f"Error processing Excel file: {str(e)}")
            raise
