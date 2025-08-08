#!/usr/bin/env python3
"""
Hugging Face Table Transformer Model Converter
Converts microsoft/table-transformer models to ONNX format for .NET integration
"""

import os
import sys
import logging
import json
from pathlib import Path
from typing import Dict, Any

import torch
from transformers import AutoImageProcessor, TableTransformerForObjectDetection
from optimum.exporters.onnx import main_export
from optimum.onnxruntime import ORTModel
import onnx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model configurations
MODELS = {
    "table-structure-recognition": {
        "hf_name": "microsoft/table-transformer-structure-recognition",
        "description": "Table structure detection and cell boundary recognition",
        "input_size": (3, 800, 800),  # channels, height, width
        "output_dir": "local-models/huggingface/table-structure-recognition"
    },
    "table-detection": {
        "hf_name": "microsoft/table-transformer-detection", 
        "description": "Table detection within documents",
        "input_size": (3, 800, 800),
        "output_dir": "local-models/huggingface/table-detection"
    }
}

def validate_environment():
    """Validate that all required dependencies are available"""
    try:
        import torch
        import transformers
        import onnx
        import onnxruntime
        from optimum.onnxruntime import ORTModel
        logger.info("✅ All required dependencies are available")
        logger.info(f"PyTorch version: {torch.__version__}")
        logger.info(f"Transformers version: {transformers.__version__}")
        logger.info(f"ONNX version: {onnx.__version__}")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        return False

def convert_model_to_onnx(model_name: str, config: Dict[str, Any]) -> bool:
    """Convert a single Hugging Face model to ONNX format"""
    logger.info(f"🔄 Converting {model_name}: {config['description']}")
    
    try:
        # Create output directory
        output_path = Path(config["output_dir"])
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Load the model and processor
        hf_model_name = config["hf_name"]
        logger.info(f"📥 Downloading model: {hf_model_name}")
        
        # Load model and processor
        model = TableTransformerForObjectDetection.from_pretrained(hf_model_name)
        processor = AutoImageProcessor.from_pretrained(hf_model_name)
        
        # Set model to evaluation mode
        model.eval()
        
        # Create dummy input for export
        dummy_input = torch.randn(1, *config["input_size"])
        
        # Export to ONNX
        onnx_model_path = output_path / "model.onnx"
        logger.info(f"💾 Exporting ONNX model to: {onnx_model_path}")
        
        torch.onnx.export(
            model,
            dummy_input,
            str(onnx_model_path),
            export_params=True,
            opset_version=11,
            do_constant_folding=True,
            input_names=['pixel_values'],
            output_names=['logits', 'pred_boxes'],
            dynamic_axes={
                'pixel_values': {0: 'batch_size'},
                'logits': {0: 'batch_size'},
                'pred_boxes': {0: 'batch_size'}
            }
        )
        
        # Save preprocessing configuration
        preprocessing_config = {
            "do_resize": getattr(processor, 'do_resize', True),
            "size": getattr(processor, 'size', {"height": 800, "width": 800}),
            "do_normalize": getattr(processor, 'do_normalize', True),
            "image_mean": getattr(processor, 'image_mean', [0.485, 0.456, 0.406]),
            "image_std": getattr(processor, 'image_std', [0.229, 0.224, 0.225]),
            "do_rescale": getattr(processor, 'do_rescale', True),
            "rescale_factor": getattr(processor, 'rescale_factor', 1/255.0),
            "input_size": config["input_size"]
        }
        
        # Save preprocessing config
        config_path = output_path / "preprocessing_config.json"
        with open(config_path, 'w') as f:
            json.dump(preprocessing_config, f, indent=2)
        
        # Validate the converted model
        if onnx_model_path.exists():
            # Load with ONNX to validate
            onnx_model_check = onnx.load(str(onnx_model_path))
            onnx.checker.check_model(onnx_model_check)
            
            # Get model info
            model_size = onnx_model_path.stat().st_size / (1024 * 1024)  # MB
            logger.info(f"✅ Model {model_name} converted successfully")
            logger.info(f"📊 Model size: {model_size:.2f} MB")
            logger.info(f"🔧 Preprocessing config saved to: {config_path}")
            
            # Log input/output shapes for .NET integration
            for input_tensor in onnx_model_check.graph.input:
                shape = [dim.dim_value if dim.dim_value > 0 else 'dynamic' for dim in input_tensor.type.tensor_type.shape.dim]
                logger.info(f"📥 Input '{input_tensor.name}': {shape}")
            
            for output_tensor in onnx_model_check.graph.output:
                shape = [dim.dim_value if dim.dim_value > 0 else 'dynamic' for dim in output_tensor.type.tensor_type.shape.dim]
                logger.info(f"📤 Output '{output_tensor.name}': {shape}")
            
            return True
        else:
            logger.error(f"❌ ONNX model file not found: {onnx_model_path}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to convert {model_name}: {str(e)}")
        logger.exception("Full error details:")
        return False

def create_model_manifest():
    """Create a manifest file with information about all converted models"""
    manifest = {
        "conversion_info": {
            "timestamp": "2025-07-25T11:20:00Z",
            "torch_version": torch.__version__,
            "target_runtime": "Microsoft.ML.OnnxRuntime",
            "optimization": "CPU-optimized"
        },
        "models": {}
    }
    
    for model_name, config in MODELS.items():
        model_path = Path(config["output_dir"])
        onnx_file = model_path / "model.onnx"
        
        if onnx_file.exists():
            model_size = onnx_file.stat().st_size
            manifest["models"][model_name] = {
                "description": config["description"],
                "hf_source": config["hf_name"],
                "onnx_path": str(onnx_file),
                "size_bytes": model_size,
                "size_mb": round(model_size / (1024 * 1024), 2),
                "input_size": config["input_size"],
                "status": "ready"
            }
        else:
            manifest["models"][model_name] = {
                "description": config["description"],
                "hf_source": config["hf_name"],
                "status": "failed"
            }
    
    # Save manifest
    manifest_path = Path("local-models/huggingface/model_manifest.json")
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    logger.info(f"📋 Model manifest saved to: {manifest_path}")

def main():
    """Main conversion process"""
    logger.info("🚀 Starting Hugging Face Table Transformer to ONNX conversion")
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    # Convert each model
    success_count = 0
    total_count = len(MODELS)
    
    for model_name, config in MODELS.items():
        if convert_model_to_onnx(model_name, config):
            success_count += 1
        else:
            logger.error(f"❌ Failed to convert {model_name}")
    
    # Create model manifest
    create_model_manifest()
    
    # Summary
    logger.info(f"🎯 Conversion Summary: {success_count}/{total_count} models converted successfully")
    
    if success_count == total_count:
        logger.info("✅ All models converted successfully!")
        logger.info("🔗 Models ready for .NET Orleans integration")
        sys.exit(0)
    else:
        logger.error(f"❌ {total_count - success_count} models failed to convert")
        sys.exit(1)

if __name__ == "__main__":
    main()
