import logging
import re
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF
import base64
import json
import os
from PIL import Image
import io
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from transformers import DonutProcessor, VisionEncoderDecoderModel
import numpy as np

logger = logging.getLogger(__name__)

class LocalMultimodalPDFProcessor:
    """
    PDF processor using local multimodal models for edge deployment
    Uses models like BLIP-2, Donut, or similar that can run locally
    """
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Initializing local multimodal processor on device: {self.device}")
        
        # Initialize local models
        self.vision_model = None
        self.processor = None
        self._load_local_models()
    
    def _load_local_models(self):
        """Load local multimodal models for document understanding"""
        try:
            # Option 1: Use BLIP-2 for general vision-language understanding
            # Smaller model that works well for document analysis
            model_name = "Salesforce/blip2-opt-2.7b"
            
            # Check if we should use a lighter model for edge deployment
            if os.getenv('USE_LIGHTWEIGHT_MODEL', 'true').lower() == 'true':
                model_name = "Salesforce/blip-image-captioning-base"
                
            logger.info(f"Loading vision model: {model_name}")
            self.processor = BlipProcessor.from_pretrained(model_name, cache_dir="/app/models")
            self.vision_model = BlipForConditionalGeneration.from_pretrained(
                model_name, 
                cache_dir="/app/models",
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            ).to(self.device)
            
            logger.info("Local multimodal models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading local models: {str(e)}")
            # Set to None to use fallback method
            self.vision_model = None
            self.processor = None
    
    def process_pdf(self, file_path: str, file_name: str) -> List[Dict[str, Any]]:
        """
        Process PDF using local multimodal model to extract parameter-value pairs
        """
        try:
            logger.info(f"Processing PDF with local multimodal model: {file_name}")
            doc = fitz.open(file_path)
            all_chunks = []
            
            for page_num, page in enumerate(doc):
                logger.info(f"Processing page {page_num + 1} with local vision model")
                
                # Convert page to PIL Image
                page_image = self._convert_page_to_pil_image(page)
                
                # Use local model to extract key-value pairs
                page_chunks = self._extract_kv_pairs_with_local_model(
                    page_image, file_name, page_num + 1
                )
                all_chunks.extend(page_chunks)
            
            logger.info(f"Extracted {len(all_chunks)} key-value pairs using local multimodal model")
            return all_chunks
            
        except Exception as e:
            logger.error(f"Error processing PDF with local multimodal model: {str(e)}")
            # Fallback to traditional text extraction
            return self._fallback_text_extraction(file_path, file_name)
        finally:
            if 'doc' in locals():
                doc.close()
    
    def _convert_page_to_pil_image(self, page) -> Image.Image:
        """Convert PDF page to PIL Image"""
        try:
            # Render page as image with good resolution
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom
            img_data = pix.tobytes("png")
            
            # Convert to PIL Image
            img = Image.open(io.BytesIO(img_data))
            return img
            
        except Exception as e:
            logger.error(f"Error converting page to PIL image: {str(e)}")
            raise
    
    def _extract_kv_pairs_with_local_model(self, image: Image.Image, file_name: str, page_num: int) -> List[Dict[str, Any]]:
        """
        Use local multimodal model to extract key-value pairs from page image
        """
        try:
            if self.vision_model is None or self.processor is None:
                logger.warning("Local models not available, using fallback")
                return self._extract_from_image_ocr(image, file_name, page_num)
            
            # Create prompts for different types of extractions
            prompts = [
                "Extract all parameter names and their values from this document page",
                "List all measurements and their units shown in tables",
                "Find numerical data with labels in this document"
            ]
            
            all_extractions = []
            
            for prompt in prompts:
                try:
                    # Process with BLIP model
                    inputs = self.processor(image, prompt, return_tensors="pt").to(self.device)
                    
                    with torch.no_grad():
                        outputs = self.vision_model.generate(
                            **inputs, 
                            max_length=150,
                            num_beams=3,
                            temperature=0.7,
                            do_sample=True
                        )
                    
                    # Decode the output
                    generated_text = self.processor.decode(outputs[0], skip_special_tokens=True)
                    logger.info(f"Model output for '{prompt}': {generated_text}")
                    
                    # Parse the generated text for key-value pairs
                    extractions = self._parse_model_output(generated_text)
                    all_extractions.extend(extractions)
                    
                except Exception as e:
                    logger.error(f"Error with prompt '{prompt}': {str(e)}")
                    continue
            
            # Convert extractions to chunk format
            chunks = self._convert_extractions_to_chunks(all_extractions, file_name, page_num)
            
            # If no good extractions, fallback to OCR-based approach
            if not chunks:
                logger.info("No extractions from vision model, trying OCR fallback")
                return self._extract_from_image_ocr(image, file_name, page_num)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error in local model extraction: {str(e)}")
            return self._extract_from_image_ocr(image, file_name, page_num)
    
    def _parse_model_output(self, text: str) -> List[Dict[str, Any]]:
        """Parse model output to extract parameter-value pairs"""
        extractions = []
        
        # Look for patterns like "Parameter: Value Unit" or "Parameter Value Unit"
        patterns = [
            r'([A-Za-z][A-Za-z\s]+?):\s*([+-]?\d+\.?\d*)\s*([A-Za-z³²°%/]+)?',
            r'([A-Za-z][A-Za-z\s]+?)\s+([+-]?\d+\.?\d*)\s*([A-Za-z³²°%/]+)?',
            r'([A-Za-z][A-Za-z\s]+?)\s*=\s*([+-]?\d+\.?\d*)\s*([A-Za-z³²°%/]+)?'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                param, value, unit = match
                param = param.strip()
                unit = unit.strip() if unit else ""
                
                # Filter out common non-parameter text
                if len(param) > 2 and param.lower() not in ['the', 'and', 'for', 'with', 'this', 'that']:
                    try:
                        numeric_value = float(value)
                        extractions.append({
                            'parameter': param,
                            'value': numeric_value,
                            'unit': unit
                        })
                    except ValueError:
                        continue
        
        return extractions
    
    def _convert_extractions_to_chunks(self, extractions: List[Dict], file_name: str, page_num: int) -> List[Dict[str, Any]]:
        """Convert extractions to chunk format"""
        chunks = []
        
        for extraction in extractions:
            chunk_text = f"{extraction['parameter']}: {extraction['value']}"
            if extraction.get('unit'):
                chunk_text += f" {extraction['unit']}"
            
            chunks.append({
                'file_name': file_name,
                'chunk_text': chunk_text,
                'page': page_num,
                'extraction_method': 'local_multimodal',
                'embedding': None
            })
        
        return chunks
    
    def _extract_from_image_ocr(self, image: Image.Image, file_name: str, page_num: int) -> List[Dict[str, Any]]:
        """
        Fallback OCR-based extraction when vision model is not available
        """
        try:
            # Use pytesseract for OCR if available
            import pytesseract
            
            # Extract text from image
            ocr_text = pytesseract.image_to_string(image)
            logger.info(f"OCR extracted text length: {len(ocr_text)}")
            
            # Parse OCR text for key-value pairs
            chunks = []
            lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
            
            for line_num, line in enumerate(lines):
                # Look for parameter-value patterns
                if ':' in line or '=' in line:
                    # Try colon separator
                    if ':' in line:
                        parts = line.split(':', 1)
                    else:
                        parts = line.split('=', 1)
                    
                    if len(parts) == 2:
                        param = parts[0].strip()
                        value_text = parts[1].strip()
                        
                        # Extract numeric value
                        value_match = re.search(r'([+-]?\d+\.?\d*)', value_text)
                        if value_match and len(param) > 2:
                            chunks.append({
                                'file_name': file_name,
                                'chunk_text': line,
                                'page': page_num,
                                'line': line_num + 1,
                                'extraction_method': 'ocr_fallback',
                                'embedding': None
                            })
            
            return chunks
            
        except ImportError:
            logger.warning("pytesseract not available for OCR fallback")
            return []
        except Exception as e:
            logger.error(f"OCR fallback failed: {str(e)}")
            return []
    
    def _fallback_text_extraction(self, file_path: str, file_name: str) -> List[Dict[str, Any]]:
        """Final fallback to traditional text extraction"""
        logger.info("Using traditional text extraction as final fallback")
        
        try:
            doc = fitz.open(file_path)
            chunks = []
            
            for page_num, page in enumerate(doc):
                text = page.get_text("text")
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                
                for line_num, line in enumerate(lines):
                    # Look for parameter-value patterns
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            param = parts[0].strip()
                            value = parts[1].strip()
                            if param and value and len(param) > 2:
                                chunks.append({
                                    'file_name': file_name,
                                    'chunk_text': line,
                                    'page': page_num + 1,
                                    'line': line_num + 1,
                                    'extraction_method': 'text_fallback',
                                    'embedding': None
                                })
            
            return chunks
            
        except Exception as e:
            logger.error(f"Text fallback also failed: {str(e)}")
            return []
        finally:
            if 'doc' in locals():
                doc.close()
