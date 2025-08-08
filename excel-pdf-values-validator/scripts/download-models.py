#!/usr/bin/env python3
"""
Model Download and Caching Script
Pre-downloads all required ML models for offline usage in Docker containers
"""

import os
import sys
import logging
from pathlib import Path
import argparse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_cache_directory(cache_dir: str) -> Path:
    """Create and setup model cache directory"""
    cache_path = Path(cache_dir).absolute()
    cache_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Model cache directory: {cache_path}")
    return cache_path

def download_sentence_transformers_model(model_name: str, cache_dir: Path) -> bool:
    """Download sentence transformers model"""
    try:
        logger.info(f"Downloading SentenceTransformer model: {model_name}")
        from sentence_transformers import SentenceTransformer
        
        # Set environment variable for cache
        os.environ['SENTENCE_TRANSFORMERS_HOME'] = str(cache_dir)
        
        model = SentenceTransformer(model_name, cache_folder=str(cache_dir))
        logger.info(f"✅ Successfully downloaded: {model_name}")
        
        # Test the model with a simple encoding
        test_text = "This is a test sentence."
        embedding = model.encode([test_text])
        logger.info(f"✅ Model test successful, embedding shape: {embedding.shape}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Failed to download {model_name}: {str(e)}")
        return False

def download_transformers_model(model_name: str, cache_dir: Path, model_class=None, processor_class=None) -> bool:
    """Download transformers model"""
    try:
        logger.info(f"Downloading Transformers model: {model_name}")
        from transformers import AutoTokenizer, AutoModel
        
        # Set environment variables for cache
        os.environ['TRANSFORMERS_CACHE'] = str(cache_dir)
        os.environ['HF_HOME'] = str(cache_dir)
        
        if model_class and processor_class:
            # For specific model classes like BLIP
            processor = processor_class.from_pretrained(model_name, cache_dir=str(cache_dir))
            model = model_class.from_pretrained(model_name, cache_dir=str(cache_dir))
            logger.info(f"✅ Successfully downloaded {model_name} with specific classes")
        else:
            # For generic models
            tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=str(cache_dir))
            model = AutoModel.from_pretrained(model_name, cache_dir=str(cache_dir))
            logger.info(f"✅ Successfully downloaded: {model_name}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Failed to download {model_name}: {str(e)}")
        return False

def download_blip_model(cache_dir: Path) -> bool:
    """Download BLIP image captioning model"""
    try:
        logger.info("Downloading BLIP image captioning model...")
        from transformers import BlipProcessor, BlipForConditionalGeneration
        
        model_name = "Salesforce/blip-image-captioning-base"
        
        # Set environment variables for cache
        os.environ['TRANSFORMERS_CACHE'] = str(cache_dir)
        os.environ['HF_HOME'] = str(cache_dir)
        
        processor = BlipProcessor.from_pretrained(model_name, cache_dir=str(cache_dir))
        model = BlipForConditionalGeneration.from_pretrained(model_name, cache_dir=str(cache_dir))
        
        logger.info("✅ Successfully downloaded BLIP model")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to download BLIP model: {str(e)}")
        return False

def get_model_size(cache_dir: Path) -> str:
    """Calculate total size of downloaded models"""
    try:
        import subprocess
        result = subprocess.run(['du', '-sh', str(cache_dir)], 
                              capture_output=True, text=True)
        return result.stdout.split('\t')[0] if result.returncode == 0 else "Unknown"
    except:
        return "Unknown"

def main():
    parser = argparse.ArgumentParser(description="Download and cache ML models")
    parser.add_argument('--cache-dir', '-c', 
                       default='./models_cache',
                       help='Directory to cache models (default: ./models_cache)')
    parser.add_argument('--minimal', '-m',
                       action='store_true',
                       help='Download only essential models')
    parser.add_argument('--check', '--dry-run',
                       action='store_true',
                       help='Check which models would be downloaded')
    
    args = parser.parse_args()
    
    # Setup cache directory
    cache_dir = setup_cache_directory(args.cache_dir)
    
    # Define models to download
    models_to_download = [
        {
            'name': 'BGE Small English v1.5',
            'type': 'sentence_transformers',
            'model_id': 'BAAI/bge-small-en-v1.5',
            'essential': True,
            'description': 'Main embedding model for text similarity'
        },
        {
            'name': 'BLIP Image Captioning',
            'type': 'blip',
            'model_id': 'Salesforce/blip-image-captioning-base',
            'essential': False,
            'description': 'Multimodal model for PDF image processing'
        }
    ]
    
    if args.check:
        logger.info("Models that would be downloaded:")
        for model in models_to_download:
            if not args.minimal or model['essential']:
                status = "✓ Essential" if model['essential'] else "○ Optional"
                logger.info(f"  {status} {model['name']}: {model['description']}")
        return
    
    logger.info(f"Starting model download to: {cache_dir}")
    
    success_count = 0
    total_count = 0
    
    for model_info in models_to_download:
        if args.minimal and not model_info['essential']:
            logger.info(f"⏭️  Skipping optional model: {model_info['name']} (minimal mode)")
            continue
            
        total_count += 1
        logger.info(f"\n📥 Downloading: {model_info['name']}")
        logger.info(f"   Description: {model_info['description']}")
        
        try:
            if model_info['type'] == 'sentence_transformers':
                success = download_sentence_transformers_model(model_info['model_id'], cache_dir)
            elif model_info['type'] == 'blip':
                success = download_blip_model(cache_dir)
            else:
                logger.warning(f"Unknown model type: {model_info['type']}")
                continue
                
            if success:
                success_count += 1
        except KeyboardInterrupt:
            logger.info("\n⏹️  Download interrupted by user")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Unexpected error downloading {model_info['name']}: {str(e)}")
    
    # Summary
    logger.info(f"\n📊 Download Summary:")
    logger.info(f"   Successfully downloaded: {success_count}/{total_count} models")
    logger.info(f"   Cache directory: {cache_dir}")
    logger.info(f"   Total cache size: {get_model_size(cache_dir)}")
    
    if success_count == total_count:
        logger.info("🎉 All models downloaded successfully!")
        logger.info("\n📝 Next steps:")
        logger.info("   1. Run Docker containers with: docker-compose up")
        logger.info("   2. Models will be mounted from local cache")
        logger.info("   3. No internet required for model loading")
    else:
        logger.warning(f"⚠️  Only {success_count}/{total_count} models downloaded successfully")
        if success_count > 0:
            logger.info("You can still run the application with available models")

if __name__ == "__main__":
    main()
