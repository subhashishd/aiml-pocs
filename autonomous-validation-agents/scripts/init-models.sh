#!/bin/bash

# Model initialization script for Orleans container
# This script ensures models are available, either real ONNX or mock models

set -e

MODEL_PATH="${MODEL_PATH:-/models/huggingface}"
USE_MOCK_MODELS="${USE_MOCK_MODELS:-false}"

echo "Initializing models in $MODEL_PATH..."

# Wait a bit for volume mounts to be ready
echo "Waiting for volume mounts to be ready..."
sleep 2

# Debug: List what's actually available
echo "Contents of $MODEL_PATH:"
ls -la "$MODEL_PATH" || echo "Path not accessible yet"

# Model types we need
MODELS=(
    "table-structure-recognition"
    "table-detection"
)

for model in "${MODELS[@]}"; do
    MODEL_DIR="$MODEL_PATH/$model"
    MODEL_FILE="$MODEL_DIR/model.onnx"
    
    # Check if real model exists and is valid
    if [[ -f "$MODEL_FILE" && $(stat -f%z "$MODEL_FILE" 2>/dev/null || stat -c%s "$MODEL_FILE" 2>/dev/null) -gt 1000 ]]; then
        echo "✓ Real ONNX model found: $MODEL_FILE"
        continue
    fi
    
    # Check if we should use mock models
    if [[ "$USE_MOCK_MODELS" == "true" ]] || [[ ! -f "$MODEL_FILE" ]]; then
        echo "Creating mock model: $MODEL_FILE"
        mkdir -p "$MODEL_DIR"
        echo "MOCK_ONNX_MODEL" > "$MODEL_FILE"
        echo "✓ Mock model created: $MODEL_FILE"
    else
        echo "❌ No valid model found for: $model"
        exit 1
    fi
done

echo "Model initialization complete!"
echo "Available models:"
find "$MODEL_PATH" -name "*.onnx" -exec ls -lh {} \;
