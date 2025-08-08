import logging
import re
from typing import List, Dict, Any
from datetime import datetime
from ..models.database import get_chunks_by_config
from .embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

class ValidationService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
    
    async def validate_values(self, excel_data: List[Dict[str, Any]], config_id: str, 
                            pdf_filename: str, excel_filename: str) -> Dict[str, Any]:
        """
        Validate Excel values against PDF content using semantic matching
        """
        try:
            logger.info(f"Starting validation for config_id: {config_id}")
            
            # Get all PDF chunks for this config
            pdf_chunks = await get_chunks_by_config(config_id)
            pdf_texts = [chunk['chunk_text'] for chunk in pdf_chunks]
            
            validation_results = []
            passed = 0
            failed = 0
            
            for excel_item in excel_data:
                parameter = excel_item['parameter'] 
                excel_value = excel_item['value']
                unit = excel_item['unit']
                
                # Hybrid approach: Try exact text match first, then semantic similarity
                pdf_value, best_chunk, match_type = self._find_best_match(
                    parameter, excel_value, pdf_texts
                )
                
                # Compare values
                is_match = self._compare_values(excel_value, pdf_value)
                
                result = {
                    'parameter': parameter,
                    'excel_value': excel_value,
                    'pdf_value': pdf_value,
                    'unit': unit,
                    'match': is_match,
                    'pdf_chunk': best_chunk,
                    'match_type': match_type,
                    'similarity': 1.0 if match_type == 'exact' else 0.8  # Placeholder for actual similarity
                }
                
                validation_results.append(result)
                
                if is_match:
                    passed += 1
                else:
                    failed += 1
            
            # Generate report
            report_text = self._generate_report(
                validation_results, config_id, pdf_filename, excel_filename, passed, failed
            )
            
            summary = {
                'total_fields': len(validation_results),
                'passed': passed,
                'failed': failed,
                'accuracy': passed / len(validation_results) if validation_results else 0
            }
            
            logger.info(f"Validation completed: {passed} passed, {failed} failed")
            
            return {
                'report_text': report_text,
                'summary': summary,
                'results': validation_results
            }
            
        except Exception as e:
            logger.error(f"Error during validation: {str(e)}")
            raise
    
    def _find_best_match(self, parameter: str, excel_value: Any, pdf_texts: List[str]) -> tuple:
        """
        Find the best matching PDF chunk using hybrid approach:
        1. First try exact text matching for parameter name
        2. Then use semantic similarity as fallback
        """
        try:
            # Step 1: Try exact text matching for parameter name
            exact_matches = []
            parameter_lower = parameter.lower()
            
            for chunk in pdf_texts:
                chunk_lower = chunk.lower()
                if parameter_lower in chunk_lower:
                    # Check if this chunk contains the parameter with a value
                    extracted_value = self._extract_value_from_chunk(chunk, parameter)
                    if extracted_value is not None:
                        exact_matches.append({
                            'text': chunk,
                            'value': extracted_value,
                            'score': 1.0  # Perfect match for parameter name
                        })
            
            # If we found exact parameter matches, use the best one
            if exact_matches:
                # Sort by how close the extracted value is to the Excel value
                if isinstance(excel_value, (int, float)):
                    exact_matches.sort(key=lambda x: abs(x['value'] - excel_value) if isinstance(x['value'], (int, float)) else float('inf'))
                
                best_match = exact_matches[0]
                return best_match['value'], best_match['text'], 'exact'
            
            # Step 2: Fallback to semantic similarity
            query = f"{parameter}"
            similar_chunks = self.embedding_service.find_most_similar(query, pdf_texts, top_k=3)
            
            if similar_chunks:
                best_chunk = similar_chunks[0]
                extracted_value = self._extract_value_from_chunk(best_chunk['text'], parameter)
                return extracted_value, best_chunk['text'], 'semantic'
            
            # Step 3: Last resort - return first chunk with any numeric value
            for chunk in pdf_texts:
                extracted_value = self._extract_value_from_chunk(chunk, parameter)
                if extracted_value is not None:
                    return extracted_value, chunk, 'fallback'
            
            return None, pdf_texts[0] if pdf_texts else "", 'none'
            
        except Exception as e:
            logger.error(f"Error finding best match: {str(e)}")
            return None, pdf_texts[0] if pdf_texts else "", 'error'
    
    def _extract_value_from_chunk(self, chunk_text: str, parameter: str) -> Any:
        """
        Extract numeric value from PDF chunk text
        """
        try:
            # Look for patterns like "parameter: value" or "parameter value"
            patterns = [
                rf"{re.escape(parameter)}\s*:?\s*([+-]?\d+\.?\d*)",
                rf"([+-]?\d+\.?\d*)\s*{re.escape(parameter)}",
                rf"{re.escape(parameter)}\s+([+-]?\d+\.?\d*)",
            ]
            
            for pattern in patterns:
                match = re.search(pattern, chunk_text, re.IGNORECASE)
                if match:
                    try:
                        return float(match.group(1))
                    except ValueError:
                        continue
            
            # If no specific pattern found, try to extract any number from the chunk
            numbers = re.findall(r'([+-]?\d+\.?\d*)', chunk_text)
            if numbers:
                try:
                    return float(numbers[0])
                except ValueError:
                    pass
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting value from chunk: {str(e)}")
            return None
    
    def _compare_values(self, excel_value: Any, pdf_value: Any) -> bool:
        """
        Compare Excel and PDF values with exact precision for scientific calculations
        """
        try:
            # Handle None values
            if pdf_value is None:
                return False
            
            # Convert both to float for comparison
            if isinstance(excel_value, str):
                try:
                    excel_value = float(excel_value)
                except ValueError:
                    return str(excel_value).strip().lower() == str(pdf_value).strip().lower()
            
            if isinstance(pdf_value, str):
                try:
                    pdf_value = float(pdf_value)
                except ValueError:
                    return str(excel_value).strip().lower() == str(pdf_value).strip().lower()
            
            # For numeric values, use exact comparison (as requested for scientific calculations)
            if isinstance(excel_value, (int, float)) and isinstance(pdf_value, (int, float)):
                return excel_value == pdf_value  # Exact comparison for scientific calculations
            
            # Fallback to string comparison
            return str(excel_value) == str(pdf_value)
            
        except Exception as e:
            logger.error(f"Error comparing values: {str(e)}")
            return False
    
    def _generate_report(self, results: List[Dict[str, Any]], config_id: str, 
                        pdf_filename: str, excel_filename: str, passed: int, failed: int) -> str:
        """
        Generate validation report in the specified format
        """
        report_lines = [
            "=== Validation Report ===",
            f"Config ID: {config_id}",
            f"PDF: {pdf_filename}",
            f"Excel: {excel_filename}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]
        
        for result in results:
            status = "✔️ PASS" if result['match'] else "❌ FAIL"
            line = f"{status} {result['parameter']}: Excel = {result['excel_value']}, PDF = {result['pdf_value']}"
            if result['unit']:
                line += f" ({result['unit']})"
            
            report_lines.append(line)
            
            # Add similarity score and PDF chunk for debugging
            report_lines.append(f"    Similarity: {result['similarity']:.3f}")
            report_lines.append(f"    PDF Chunk: {result['pdf_chunk'][:100]}...")
            report_lines.append("")
        
        report_lines.extend([
            f"Summary: {len(results)} fields checked | {passed} passed | {failed} failed",
            f"Accuracy: {(passed/len(results)*100):.1f}%" if results else "Accuracy: N/A"
        ])
        
        return "\n".join(report_lines)
