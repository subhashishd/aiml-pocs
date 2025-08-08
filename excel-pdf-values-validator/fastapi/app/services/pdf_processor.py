import logging
import re
from typing import List, Dict, Any, Tuple
import fitz  # PyMuPDF
import base64
import io
from PIL import Image
import os

logger = logging.getLogger(__name__)

class PDFProcessor:
    def process_pdf(self, file_path: str, file_name: str) -> List[Dict[str, Any]]:
        """
        Process the PDF file to extract parameter-value pairs from tables
        """
        try:
            logger.info(f"Opening PDF file: {file_name}")
            doc = fitz.open(file_path)
            chunks = []
            
            for page_num, page in enumerate(doc):
                # Try to extract tables first
                try:
                    tables = page.find_tables()
                    table_list = list(tables)  # Convert to list to get length
                    
                    if table_list:
                        logger.info(f"Found {len(table_list)} tables on page {page_num + 1}")
                        for table_num, table in enumerate(table_list):
                            table_chunks = self._process_table(table, file_name, page_num + 1, table_num + 1)
                            chunks.extend(table_chunks)
                    else:
                        # Fallback to text-based extraction
                        logger.info(f"No tables found on page {page_num + 1}, using text extraction")
                        text_chunks = self._process_text(page, file_name, page_num + 1)
                        chunks.extend(text_chunks)
                except Exception as e:
                    logger.warning(f"Table extraction failed on page {page_num + 1}: {str(e)}")
                    # Fallback to text-based extraction
                    logger.info(f"Using text extraction for page {page_num + 1}")
                    text_chunks = self._process_text(page, file_name, page_num + 1)
                    chunks.extend(text_chunks)
            
            logger.info(f"Extracted {len(chunks)} chunks from PDF")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_name}: {str(e)}")
            raise
        finally:
            if 'doc' in locals():
                doc.close()
    
    def _process_table(self, table, file_name: str, page_num: int, table_num: int) -> List[Dict[str, Any]]:
        """
        Process a table to extract parameter-value pairs
        """
        chunks = []
        try:
            # Extract table data
            table_data = table.extract()
            
            if not table_data or len(table_data) < 2:
                return chunks
            
            # Assume first row contains headers
            headers = [str(cell).strip() for cell in table_data[0] if cell]
            
            # Process each data row
            for row_idx, row in enumerate(table_data[1:], 1):
                if not row or len(row) < 2:
                    continue
                
                # Clean row data
                row_cells = [str(cell).strip() if cell else "" for cell in row]
                
                # Try to identify parameter and value columns
                param_col, value_col = self._identify_param_value_columns(headers, row_cells)
                
                if param_col is not None and value_col is not None:
                    parameter = row_cells[param_col]
                    value = row_cells[value_col]
                    
                    if parameter and value and parameter.lower() not in ['parameter', 'item', 'description']:
                        # Create chunk text that includes context
                        chunk_text = f"{parameter}: {value}"
                        
                        # Add unit if available
                        unit_col = self._find_unit_column(headers)
                        if unit_col is not None and unit_col < len(row_cells):
                            unit = row_cells[unit_col]
                            if unit:
                                chunk_text += f" {unit}"
                        
                        chunks.append({
                            'file_name': file_name,
                            'chunk_text': chunk_text,
                            'page': page_num,
                            'table': table_num,
                            'row': row_idx,
                            'embedding': None
                        })
            
            logger.info(f"Extracted {len(chunks)} parameter-value pairs from table {table_num} on page {page_num}")
            
        except Exception as e:
            logger.error(f"Error processing table: {str(e)}")
        
        return chunks
    
    def _process_text(self, page, file_name: str, page_num: int) -> List[Dict[str, Any]]:
        """
        Fallback text processing when tables are not detected
        """
        chunks = []
        try:
            text = page.get_text("text")
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            for line_num, line in enumerate(lines):
                # Look for parameter-value patterns
                param_value = self._extract_param_value_from_line(line)
                if param_value:
                    parameter, value = param_value
                    chunks.append({
                        'file_name': file_name,
                        'chunk_text': line,
                        'page': page_num,
                        'line': line_num + 1,
                        'embedding': None
                    })
            
            logger.info(f"Extracted {len(chunks)} parameter-value pairs from text on page {page_num}")
            
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
        
        return chunks
    
    def _identify_param_value_columns(self, headers: List[str], row_cells: List[str]) -> Tuple[int, int]:
        """
        Identify which columns contain parameters and values
        """
        param_col = None
        value_col = None
        
        # Look for parameter column
        param_keywords = ['parameter', 'item', 'description', 'name', 'property']
        for i, header in enumerate(headers):
            if any(keyword in header.lower() for keyword in param_keywords):
                param_col = i
                break
        
        # Look for value column
        value_keywords = ['value', 'amount', 'quantity', 'result', 'measurement']
        for i, header in enumerate(headers):
            if any(keyword in header.lower() for keyword in value_keywords):
                value_col = i
                break
        
        # If headers don't help, use heuristics based on content
        if param_col is None or value_col is None:
            for i, cell in enumerate(row_cells):
                if cell and not self._is_numeric(cell) and len(cell) > 3:
                    param_col = i
                    break
            
            for i, cell in enumerate(row_cells):
                if i != param_col and cell and (self._is_numeric(cell) or len(cell) < 20):
                    value_col = i
                    break
        
        # Default to first two columns if nothing else works
        if param_col is None:
            param_col = 0
        if value_col is None and len(row_cells) > 1:
            value_col = 1
        
        return param_col, value_col
    
    def _find_unit_column(self, headers: List[str]) -> int:
        """
        Find the column that contains units
        """
        unit_keywords = ['unit', 'units', 'uom', 'measure']
        for i, header in enumerate(headers):
            if any(keyword in header.lower() for keyword in unit_keywords):
                return i
        return None
    
    def _is_numeric(self, text: str) -> bool:
        """
        Check if text represents a numeric value
        """
        try:
            # First check if the text starts with a number pattern
            if not re.match(r'^[+-]?\d*\.?\d+', text.strip()):
                return False
            
            # Try to convert to float
            float(text.strip())
            return True
        except ValueError:
            pass
        return False
    
    def _extract_param_value_from_line(self, line: str) -> Tuple[str, str]:
        """
        Extract parameter-value pair from a single line of text
        """
        # Pattern 1: "Parameter: Value"
        if ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                param = parts[0].strip()
                value = parts[1].strip()
                if param and value:
                    return param, value
        
        # Pattern 2: "Parameter Value" (space-separated)
        words = line.split()
        if len(words) >= 2:
            # Look for patterns where last word(s) could be numeric values
            for i in range(len(words) - 1, 0, -1):
                potential_value = ' '.join(words[i:])
                potential_param = ' '.join(words[:i])
                
                if self._is_numeric(potential_value.split()[0]) and len(potential_param) > 2:
                    return potential_param, potential_value
        
        return None
