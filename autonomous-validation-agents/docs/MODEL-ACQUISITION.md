# Model Acquisition Strategy

**Date**: July 25, 2025  
**Goal**: Download and convert Hugging Face table transformer models to ONNX format for edge deployment

## Target Models

### Primary Model: microsoft/table-transformer-structure-recognition
- **Purpose**: Table structure detection and cell boundary recognition
- **Model Type**: Vision Transformer (ViT) based
- **Input**: Images (PDF pages converted to images)
- **Output**: Table structure with cell boundaries
- **Size**: ~50MB (estimated)
- **Hugging Face URL**: https://huggingface.co/microsoft/table-transformer-structure-recognition

### Secondary Model: microsoft/table-transformer-detection
- **Purpose**: Table detection within documents
- **Model Type**: Vision Transformer (ViT) based  
- **Input**: Document images
- **Output**: Table bounding boxes
- **Size**: ~50MB (estimated)
- **Hugging Face URL**: https://huggingface.co/microsoft/table-transformer-detection

## Acquisition Strategy

### Phase 1: Model Download and Conversion
1. **Python Environment Setup**: Create isolated environment for model conversion
2. **Hugging Face Model Download**: Use transformers library to download models
3. **ONNX Conversion**: Convert PyTorch models to ONNX format
4. **Validation**: Test ONNX models for compatibility with Microsoft.ML.OnnxRuntime

### Phase 2: Model Integration
1. **ONNX Model Testing**: Load models in our ModelManagerGrain
2. **Input/Output Mapping**: Define tensor shapes and data types
3. **Preprocessing Pipeline**: Image conversion and normalization
4. **Performance Benchmarking**: CPU vs CoreML performance testing

### Phase 3: Container Strategy
1. **Docker Image Creation**: Package models in container volumes
2. **Volume Mounting**: Configure Orleans to access containerized models
3. **Model Versioning**: Strategy for model updates and rollbacks

## Implementation Steps

### Step 1: Python Environment Setup
```bash
# Create virtual environment for model conversion
python3 -m venv model-conversion-env
source model-conversion-env/bin/activate
pip install torch transformers onnx onnxruntime optimum[onnxruntime]
```

### Step 2: Model Download Script
```python
from transformers import AutoModel, AutoTokenizer
from optimum.onnxruntime import ORTModelForImageClassification
import torch

# Download and convert table structure recognition model
model_name = "microsoft/table-transformer-structure-recognition"
onnx_model = ORTModelForImageClassification.from_pretrained(
    model_name, 
    export=True,
    provider="CPUExecutionProvider"
)
onnx_model.save_pretrained("./models/huggingface/table-structure-recognition")
```

### Step 3: Model Validation
```csharp
// Test ONNX model loading in .NET
var modelPath = "./models/huggingface/table-structure-recognition/model.onnx";
using var session = new InferenceSession(modelPath);

// Verify input/output metadata
foreach (var input in session.InputMetadata)
{
    Console.WriteLine($"Input: {input.Key}, Shape: {string.Join(",", input.Value.Dimensions)}");
}
```

## Expected Outputs

### ONNX Model Files
```
models/huggingface/
├── table-structure-recognition/
│   ├── model.onnx                 # Main ONNX model file
│   ├── config.json               # Model configuration
│   └── preprocessing_config.json  # Input preprocessing parameters
└── table-detection/
    ├── model.onnx
    ├── config.json
    └── preprocessing_config.json
```

### Integration Points
1. **ModelManagerGrain**: Load ONNX models on startup
2. **PDFIntelligenceGrain**: Use loaded models for table extraction
3. **Resource Monitoring**: Track model memory usage and performance
4. **Container Deployment**: Package models for edge deployment

## Performance Targets

### Inference Performance
- **Target**: <100ms per PDF page
- **CPU Optimization**: Leverage ONNX Runtime CPU optimizations
- **CoreML**: Use Apple Silicon acceleration when available
- **Memory**: <200MB per loaded model

### Quality Metrics
- **Table Detection Accuracy**: >90%
- **Structure Recognition Accuracy**: >85%
- **False Positive Rate**: <5%
- **Processing Success Rate**: >95%

## Fallback Strategy

### Model Unavailable
- **Graceful Degradation**: Use basic PDF text extraction
- **Error Handling**: Log model loading failures without breaking workflow
- **Resource Constraints**: Unload models under memory pressure
- **Network Issues**: Cache models locally for offline operation

## Next Steps

1. **Immediate**: Set up Python environment and download first model
2. **Convert**: Transform to ONNX format with CPU optimization
3. **Test**: Validate ONNX model loading in ModelManagerGrain
4. **Integrate**: Connect to PDFIntelligenceGrain for real inference
5. **Container**: Package models for edge deployment

---

**Status**: 🔄 Ready for Implementation  
**Priority**: High - Foundation for ML-enhanced table extraction
