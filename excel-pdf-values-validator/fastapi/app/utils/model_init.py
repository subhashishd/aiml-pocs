import logging
import os
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

def initialize_models():
    """
    Initialize and warm up all required models during startup
    This ensures models are loaded and ready for use
    """
    try:
        logger.info("Initializing models for offline usage...")
        
        # Set model cache directory
        model_cache_dir = os.getenv('SENTENCE_TRANSFORMERS_HOME', '/app/models')
        
        # Initialize BGE model
        logger.info("Loading BGE-small-en-v1.5 model...")
        model = SentenceTransformer('BAAI/bge-small-en-v1.5', cache_folder=model_cache_dir)
        
        # Skip warmup to avoid hanging during startup
        logger.info("Skipping model warmup for faster startup")
        
        # Try to initialize multimodal models if enabled
        use_multimodal = os.getenv('USE_MULTIMODAL_PDF', 'false').lower() == 'true'
        if use_multimodal:
            try:
                logger.info("Loading BLIP model for multimodal processing...")
                from transformers import BlipProcessor, BlipForConditionalGeneration
                processor = BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base', cache_dir=model_cache_dir)
                blip_model = BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base', cache_dir=model_cache_dir)
                logger.info("BLIP model loaded successfully")
            except Exception as e:
                logger.warning(f"Could not load BLIP model: {str(e)}")
        
        logger.info("Model initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing models: {str(e)}")
        return False

if __name__ == "__main__":
    initialize_models()
