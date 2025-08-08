#!/bin/bash
set -e

echo "🚀 Building and Testing Hugging Face Model Integration"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed or not in PATH"
    exit 1
fi

print_status "Docker and Docker Compose are available"

# Clean up any existing containers
print_status "Cleaning up existing containers..."
docker-compose down --volumes --remove-orphans 2>/dev/null || true

# Build the model converter image
print_status "Building model converter image..."
docker build -t huggingface-model-converter:latest ./docker/model-converter

# Test model conversion in isolation
print_status "Testing model conversion..."
docker run --rm \
    -v $(pwd)/models:/models \
    huggingface-model-converter:latest \
    python3 /workspace/scripts/convert_table_models.py

# Check if models were created
if [ -f "./models/huggingface/table-structure-recognition/model.onnx" ]; then
    print_success "Table structure recognition model converted successfully"
    MODEL_SIZE=$(du -h "./models/huggingface/table-structure-recognition/model.onnx" | cut -f1)
    print_status "Model size: $MODEL_SIZE"
else
    print_error "Table structure recognition model conversion failed"
    exit 1
fi

if [ -f "./models/huggingface/table-detection/model.onnx" ]; then
    print_success "Table detection model converted successfully"
    MODEL_SIZE=$(du -h "./models/huggingface/table-detection/model.onnx" | cut -f1)
    print_status "Model size: $MODEL_SIZE"
else
    print_warning "Table detection model conversion failed (continuing with primary model)"
fi

# Check model manifest
if [ -f "./models/huggingface/model_manifest.json" ]; then
    print_success "Model manifest created successfully"
    print_status "Model manifest contents:"
    cat "./models/huggingface/model_manifest.json" | jq '.' || cat "./models/huggingface/model_manifest.json"
else
    print_warning "Model manifest not found"
fi

# Test ONNX model loading with a simple Python script
print_status "Testing ONNX model loading..."
python3 -c "
import onnxruntime as ort
import sys

try:
    session = ort.InferenceSession('./models/huggingface/table-structure-recognition/model.onnx')
    print('✅ ONNX model loads successfully')
    
    # Print input/output info
    print('📥 Inputs:')
    for input_meta in session.get_inputs():
        print(f'  - {input_meta.name}: {input_meta.shape} ({input_meta.type})')
    
    print('📤 Outputs:')
    for output_meta in session.get_outputs():
        print(f'  - {output_meta.name}: {output_meta.shape} ({output_meta.type})')
    
    providers = ort.get_available_providers()
    print(f'🔧 Available providers: {providers}')
    
except Exception as e:
    print(f'❌ Error loading ONNX model: {e}')
    sys.exit(1)
" || {
    print_error "ONNX model loading test failed"
    print_status "Installing required Python packages..."
    pip3 install onnxruntime numpy
    
    # Retry the test
    python3 -c "
import onnxruntime as ort
session = ort.InferenceSession('./models/huggingface/table-structure-recognition/model.onnx')
print('✅ ONNX model loads successfully (after installing dependencies)')
"
}

print_success "Model conversion and testing completed successfully!"
print_status "Models are ready for Orleans integration"

echo ""
echo "📋 Summary:"
echo "- Models location: ./models/huggingface/"
echo "- Primary model: table-structure-recognition/model.onnx"
echo "- Model manifest: model_manifest.json"
echo "- Container integration: Ready for docker-compose up"

echo ""
print_status "Next steps:"
echo "1. Start the full stack: docker-compose up --build"
echo "2. Test Orleans integration: curl http://localhost:8080/health"
echo "3. Test model loading in ModelManagerGrain"
