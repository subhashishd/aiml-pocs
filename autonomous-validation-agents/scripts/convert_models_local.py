#!/usr/bin/env python3
"""
Local Hugging Face Table Transformer Model Converter
Simple script to test model conversion locally before Docker deployment
"""

import os
import sys
import logging
import json
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required packages are available"""
    missing_packages = []
    
    try:
        import torch
        logger.info(f"✅ PyTorch version: {torch.__version__}")
    except ImportError:
        missing_packages.append("torch")
    
    try:
        import transformers
        logger.info(f"✅ Transformers version: {transformers.__version__}")
    except ImportError:
        missing_packages.append("transformers")
    
    try:
        import onnx
        logger.info(f"✅ ONNX version: {onnx.__version__}")
    except ImportError:
        missing_packages.append("onnx")
    
    try:
        import onnxruntime
        logger.info(f"✅ ONNX Runtime version: {onnxruntime.__version__}")
    except ImportError:
        missing_packages.append("onnxruntime")
    
    try:
        from optimum.onnxruntime import ORTModelForObjectDetection
        logger.info("✅ Optimum ONNX Runtime available")
    except ImportError:
        missing_packages.append("optimum[onnxruntime]")
    
    if missing_packages:
        logger.error(f"❌ Missing packages: {', '.join(missing_packages)}")
        logger.info("Install with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def test_model_loading():
    """Test loading a simple Hugging Face model to verify setup"""
    try:
        from transformers import AutoImageProcessor
        
        # Test with a lightweight model first
        logger.info("🔍 Testing model loading with a lightweight model...")
        processor = AutoImageProcessor.from_pretrained("microsoft/table-transformer-detection")
        logger.info("✅ Successfully loaded AutoImageProcessor")
        
        # Check processor configuration
        logger.info(f"📋 Processor config: {processor.size}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Model loading test failed: {e}")
        return False

def create_mock_onnx_conversion():
    """Create mock ONNX model files for testing Orleans integration"""
    models_dir = Path("models/huggingface")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Create mock model directories
    structure_dir = models_dir / "table-structure-recognition"
    detection_dir = models_dir / "table-detection"
    
    structure_dir.mkdir(exist_ok=True)
    detection_dir.mkdir(exist_ok=True)
    
    # Create mock ONNX files (for testing purposes)
    mock_onnx_content = b"MOCK_ONNX_MODEL_FOR_TESTING_ONLY"
    
    # Structure recognition model
    (structure_dir / "model.onnx").write_bytes(mock_onnx_content)
    
    structure_config = {
        "do_resize": True,
        "size": {"height": 800, "width": 800},
        "do_normalize": True,
        "image_mean": [0.485, 0.456, 0.406],
        "image_std": [0.229, 0.224, 0.225],
        "do_rescale": True,
        "rescale_factor": 0.00392156862745098,
        "input_size": [3, 800, 800]
    }
    
    with open(structure_dir / "preprocessing_config.json", 'w') as f:
        json.dump(structure_config, f, indent=2)
    
    # Detection model
    (detection_dir / "model.onnx").write_bytes(mock_onnx_content)
    
    with open(detection_dir / "preprocessing_config.json", 'w') as f:
        json.dump(structure_config, f, indent=2)
    
    # Create manifest
    manifest = {
        "conversion_info": {
            "timestamp": "2025-07-25T11:25:00Z",
            "status": "mock_models_for_testing",
            "target_runtime": "Microsoft.ML.OnnxRuntime"
        },
        "models": {
            "table-structure-recognition": {
                "description": "Table structure detection and cell boundary recognition",
                "hf_source": "microsoft/table-transformer-structure-recognition",
                "onnx_path": str(structure_dir / "model.onnx"),
                "size_bytes": len(mock_onnx_content),
                "size_mb": round(len(mock_onnx_content) / (1024 * 1024), 2),
                "input_size": [3, 800, 800],
                "status": "mock_ready"
            },
            "table-detection": {
                "description": "Table detection within documents", 
                "hf_source": "microsoft/table-transformer-detection",
                "onnx_path": str(detection_dir / "model.onnx"),
                "size_bytes": len(mock_onnx_content),
                "size_mb": round(len(mock_onnx_content) / (1024 * 1024), 2),
                "input_size": [3, 800, 800],
                "status": "mock_ready"
            }
        }
    }
    
    manifest_path = models_dir / "model_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    logger.info(f"✅ Created mock models at: {models_dir}")
    logger.info(f"📋 Model manifest: {manifest_path}")
    
    return True

def main():
    """Main function to test model conversion capabilities"""
    logger.info("🚀 Local Hugging Face Model Conversion Test")
    logger.info("=" * 50)
    
    # Check dependencies
    deps_ok = check_dependencies()
    if not deps_ok:
        logger.warning("⚠️ Some dependencies missing, but continuing with mock model creation")
    
    # Test model loading
    if not test_model_loading():
        logger.warning("⚠️ Model loading test failed, creating mock models for Orleans testing")
    else:
        logger.info("✅ Model loading test passed")
    
    # Create mock models for Orleans integration testing
    if create_mock_onnx_conversion():
        logger.info("✅ Mock models created successfully")
    else:
        logger.error("❌ Failed to create mock models")
        sys.exit(1)
    
    logger.info("🎯 Next Steps:")
    logger.info("1. Test Orleans integration with mock models")
    logger.info("2. Build and test ModelManagerGrain loading")
    logger.info("3. Verify PDFIntelligenceGrain enhancement")
    logger.info("4. Replace mock models with real ONNX conversion later")
    
    logger.info("✅ Local model preparation completed!")

if __name__ == "__main__":
    main()
