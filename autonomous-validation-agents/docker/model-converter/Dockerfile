# Multi-stage Docker build for Hugging Face model distribution
# Stage 1: Model distribution (using pre-built local models)
FROM alpine:latest as model-runtime

# Copy pre-built models from local directory
COPY models/ /models/huggingface

# Create volume mount point for Orleans to access models
VOLUME ["/models"]

# Health check to verify models are available
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD test -f /models/huggingface/table-structure-recognition/model.onnx && test -f /models/huggingface/table-detection/model.onnx || exit 1

# Default command - just sleep to keep container running
CMD ["sh", "-c", "echo 'Model container ready. Models available at /models/huggingface/' && sleep infinity"]
