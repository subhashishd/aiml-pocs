import logging
import re
import gc
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF
import os
from PIL import Image
import io
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
import numpy as np
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class OptimizedMultimodalPDFProcessor:
    """
    Memory-optimized PDF processor using local multimodal models for edge deployment
    Features:
    - Lazy model loading (models loaded only when needed)
    - Model unloading after processing
    - Memory-efficient image processing
    - Batch processing optimization
    - Quantization support
    """
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Initializing optimized multimodal processor on device: {self.device}")
        
        # Models are loaded lazily - not loaded at init
        self.vision_model = None
        self.processor = None
        self.model_loaded = False
        
        # Memory optimization settings
        self.use_quantization = os.getenv('USE_MODEL_QUANTIZATION', 'true').lower() == 'true'
        self.unload_after_processing = os.getenv('UNLOAD_MODELS_AFTER_PROCESSING', 'true').lower() == 'true'
        self.max_image_size = int(os.getenv('MAX_IMAGE_SIZE', '1024'))  # Max dimension
        
        logger.info(f"Memory optimizations: quantization={self.use_quantization}, "
                   f"unload_after_processing={self.unload_after_processing}, "
                   f"max_image_size={self.max_image_size}")
    
    @contextmanager
    def _model_context(self):
        """Context manager for lazy model loading and automatic cleanup"""
        try:
            self._load_models_if_needed()
            yield
        finally:
            if self.unload_after_processing:
                self._unload_models()
    
    def _load_models_if_needed(self):
        """Lazy load models only when needed"""
        if self.model_loaded:
            return
            
        try:
            model_name = "Salesforce/blip-image-captioning-base"
            logger.info(f"Lazy loading vision model: {model_name}")
            
            # Load processor (lightweight)
            self.processor = BlipProcessor.from_pretrained(model_name, cache_dir="/app/models")
            
            # Load model with optimizations
            model_kwargs = {
                "cache_dir": "/app/models",
                "torch_dtype": torch.float16 if torch.cuda.is_available() else torch.float32,
                "low_cpu_mem_usage": True,  # Reduces peak memory during loading
            }
            
            # Add quantization if enabled and available
            if self.use_quantization and hasattr(torch, 'quantization'):
                try:
                    model_kwargs["load_in_8bit"] = True
                    logger.info("Loading model with 8-bit quantization")
                except Exception as e:
                    logger.warning(f"Quantization not available: {e}")
            
            self.vision_model = BlipForConditionalGeneration.from_pretrained(
                model_name, **model_kwargs
            ).to(self.device)
            
            # Enable memory efficient attention if available
            if hasattr(self.vision_model, 'enable_memory_efficient_attention'):
                self.vision_model.enable_memory_efficient_attention()
            
            # Set to evaluation mode to save memory
            self.vision_model.eval()
            
            self.model_loaded = True
            logger.info("Models loaded with memory optimizations")
            
        except Exception as e:
            logger.error(f"Error loading optimized models: {str(e)}")
            raise
    
    def _unload_models(self):
        """Unload models to free memory"""
        if self.vision_model is not None:
            del self.vision_model
            self.vision_model = None
        
        if self.processor is not None:
            del self.processor  
            self.processor = None
            
        self.model_loaded = False
        
        # Force garbage collection
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        logger.info("Models unloaded and memory cleared")
    
    def process_pdf(self, file_path: str, file_name: str) -> List[Dict[str, Any]]:
        """
        Process PDF using optimized multimodal model to extract parameter-value pairs
        """
        try:
            logger.info(f"Processing PDF with optimized multimodal model: {file_name}")
            
            with self._model_context():
                doc = fitz.open(file_path)
                all_chunks = []
                
                for page_num, page in enumerate(doc):
                    logger.info(f"Processing page {page_num + 1} with optimized vision model")
                    
                    # Convert page to optimized PIL Image
                    page_image = self._convert_page_to_optimized_image(page)
                    
                    # Use optimized model to extract key-value pairs
                    page_chunks = self._extract_kv_pairs_optimized(
                        page_image, file_name, page_num + 1
                    )
                    all_chunks.extend(page_chunks)
                    
                    # Clear page image from memory
                    del page_image
                
                doc.close()
                
            logger.info(f"Extracted {len(all_chunks)} key-value pairs using optimized multimodal model")
            return all_chunks
            
        except Exception as e:
            logger.error(f"Error processing PDF with optimized multimodal model: {str(e)}")
            # Fallback to traditional text extraction
            return self._fallback_text_extraction(file_path, file_name)
    
    def _convert_page_to_optimized_image(self, page) -> Image.Image:
        """Convert PDF page to memory-optimized PIL Image"""
        try:
            # Use lower resolution initially to save memory
            base_zoom = 1.5  # Reduced from 2.0
            pix = page.get_pixmap(matrix=fitz.Matrix(base_zoom, base_zoom))
            img_data = pix.tobytes("png")
            
            # Convert to PIL Image
            img = Image.open(io.BytesIO(img_data))
            
            # Resize if too large
            if max(img.size) > self.max_image_size:
                ratio = self.max_image_size / max(img.size)
                new_size = tuple(int(dim * ratio) for dim in img.size)
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                logger.info(f"Resized image from {pix.width}x{pix.height} to {new_size}")
            
            # Convert to RGB if not already (saves memory vs RGBA)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            return img
            
        except Exception as e:
            logger.error(f"Error converting page to optimized image: {str(e)}")
            raise
    
    def _extract_kv_pairs_optimized(self, image: Image.Image, file_name: str, page_num: int) -> List[Dict[str, Any]]:
        """
        Use optimized multimodal model to extract key-value pairs from page image
        """
        try:
            if self.vision_model is None or self.processor is None:
                logger.warning("Optimized models not available, using fallback")
                return self._extract_from_image_ocr(image, file_name, page_num)
            
            # Use fewer, more targeted prompts to reduce processing time and memory
            prompts = [
                "Extract parameter names and values from this document",
                "List measurements with units from tables"
            ]
            
            all_extractions = []
            
            for prompt in prompts:
                try:
                    # Process with optimized BLIP model
                    inputs = self.processor(image, prompt, return_tensors="pt").to(self.device)
                    
                    with torch.no_grad():
                        # Use more memory-efficient generation parameters
                        outputs = self.vision_model.generate(
                            **inputs, 
                            max_length=100,  # Reduced from 150
                            num_beams=2,     # Reduced from 3
                            temperature=0.8,
                            do_sample=False,  # Disable sampling for consistency and speed
                            pad_token_id=self.processor.tokenizer.eos_token_id
                        )
                    
                    # Clear inputs from GPU memory immediately
                    del inputs
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                    
                    # Decode the output
                    generated_text = self.processor.decode(outputs[0], skip_special_tokens=True)
                    logger.info(f"Optimized model output for '{prompt}': {generated_text}")
                    
                    # Parse the generated text for key-value pairs
                    extractions = self._parse_model_output(generated_text)
                    all_extractions.extend(extractions)
                    
                    # Clear outputs from memory
                    del outputs
                    
                except Exception as e:
                    logger.error(f"Error with optimized prompt '{prompt}': {str(e)}")
                    continue
            
            # Convert extractions to chunk format
            chunks = self._convert_extractions_to_chunks(all_extractions, file_name, page_num)
            
            # If no good extractions, fallback to OCR-based approach
            if not chunks:
                logger.info("No extractions from optimized vision model, trying OCR fallback")
                return self._extract_from_image_ocr(image, file_name, page_num)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error in optimized model extraction: {str(e)}")
            return self._extract_from_image_ocr(image, file_name, page_num)
    
    def _parse_model_output(self, text: str) -> List[Dict[str, Any]]:
        """Parse model output to extract parameter-value pairs (same as original)"""
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
        """Convert extractions to chunk format (same as original)"""
        chunks = []
        
        for extraction in extractions:
            parameter = extraction['parameter']
            value = extraction['value']
            unit = extraction['unit']
            
            # Create chunk text
            chunk_text = f"{parameter}: {value}"
            if unit:
                chunk_text += f" {unit}"
            
            chunk = {
                'text': chunk_text,
                'parameter': parameter,
                'value': value,
                'unit': unit,
                'source': f"{file_name} - Page {page_num}",
                'page_number': page_num,
                'extraction_method': 'optimized_multimodal_vision'
            }
            chunks.append(chunk)
        
        return chunks
    
    def _extract_from_image_ocr(self, image: Image.Image, file_name: str, page_num: int) -> List[Dict[str, Any]]:
        """Fallback OCR extraction (placeholder - same as original)"""
        logger.info("Using OCR fallback for parameter extraction")
        
        try:
            import pytesseract
            # Extract text using OCR
            ocr_text = pytesseract.image_to_string(image)
            
            # Parse OCR text for parameter-value pairs
            extractions = self._parse_model_output(ocr_text)
            return self._convert_extractions_to_chunks(extractions, file_name, page_num)
            
        except ImportError:
            logger.warning("pytesseract not available for OCR fallback")
            return []
        except Exception as e:
            logger.error(f"Error in OCR fallback: {str(e)}")
            return []
    
    def _fallback_text_extraction(self, file_path: str, file_name: str) -> List[Dict[str, Any]]:
        """Fallback to traditional text extraction (same as original)"""
        logger.info("Using fallback text extraction")
        
        try:
            doc = fitz.open(file_path)
            chunks = []
            
            for page_num, page in enumerate(doc):
                text = page.get_text()
                if text.strip():
                    # Simple extraction from text
                    extractions = self._parse_model_output(text)
                    page_chunks = self._convert_extractions_to_chunks(extractions, file_name, page_num + 1)
                    chunks.extend(page_chunks)
            
            doc.close()
            return chunks
            
        except Exception as e:
            logger.error(f"Error in fallback text extraction: {str(e)}")
            return []

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory usage statistics"""
        stats = {
            'model_loaded': self.model_loaded,
            'device': str(self.device),
            'optimizations_enabled': {
                'quantization': self.use_quantization,
                'unload_after_processing': self.unload_after_processing,
                'max_image_size': self.max_image_size
            }
        }
        
        if torch.cuda.is_available():
            stats['gpu_memory'] = {
                'allocated': torch.cuda.memory_allocated(),
                'reserved': torch.cuda.memory_reserved(),
                'max_allocated': torch.cuda.max_memory_allocated()
            }
        
        return stats
