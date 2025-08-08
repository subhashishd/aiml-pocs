# Docker Deployment Guide - Orleans with Model Management

This guide explains how to deploy the Orleans application with different model configurations.

## Architecture Overview

```
┌─────────────────────┐    ┌─────────────────────┐
│  model-provider     │    │   orleans-app       │
│  (ONNX converter)   │───▶│   (Orleans + ONNX)  │
│                     │    │                     │
│  - Python env      │    │  - .NET 9.0         │
│  - Hugging Face     │    │  - ONNX Runtime     │
│  - Model conversion │    │  - Model loading    │
└─────────────────────┘    └─────────────────────┘
         │                           │
         └──────── model-volume ─────┘
```

## Deployment Options

### 1. Production Deployment (Real ONNX Models)

Uses converted Hugging Face models for actual inference:

```bash
# Build and start with real models
docker-compose up --build

# Or build models separately first
docker-compose build model-provider
docker-compose up
```

**What happens:**
- `model-provider` downloads and converts Hugging Face models to ONNX
- Models are stored in Docker volume `model-volume`
- `orleans-app` mounts the volume and loads real ONNX models
- Health checks ensure models are available before Orleans starts

### 2. Development/Testing (Mock Models)

Uses lightweight mock models for testing without model conversion:

```bash
# Run with mock models only
docker-compose -f docker-compose.yml -f docker-compose.test.yml up --build orleans-app
```

**What happens:**
- No model conversion step
- Orleans container creates small mock files containing "MOCK_ONNX_MODEL"
- `ModelManagerGrain` detects mock models and creates null sessions
- Perfect for development and CI/CD pipelines

### 3. Local Testing (Orleans Only)

Run just the Orleans container for development:

```bash
# Build Orleans container
docker build -f Dockerfile.orleans -t orleans-model-manager .

# Run with mock models
docker run -p 8080:8080 -e USE_MOCK_MODELS=true orleans-model-manager

# Run expecting real models (will fail without volume)
docker run -p 8080:8080 -v /path/to/models:/models orleans-model-manager
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_PATH` | `/models/huggingface` | Path where models are stored |
| `USE_MOCK_MODELS` | `false` | Force use of mock models |
| `EXECUTION_PROVIDER` | `CPUExecutionProvider` | ONNX execution provider |
| `ASPNETCORE_ENVIRONMENT` | `Production` | ASP.NET Core environment |

## Model Initialization Process

The Orleans container uses a smart initialization script:

1. **Check for real models**: Look for valid ONNX files (>1KB)
2. **Fallback to mocks**: Create mock models if real ones aren't found
3. **Environment override**: Respect `USE_MOCK_MODELS=true`
4. **Logging**: Clear indication of which models are loaded

## Health Checks

- **Model Provider**: Ensures ONNX models exist
- **Orleans App**: HTTP health endpoint at `/health`
- **Startup Dependencies**: Orleans waits for model-provider to be healthy

## File Structure

```
/models/huggingface/
├── table-structure-recognition/
│   └── model.onnx              # Structure recognition model
└── table-detection/
    └── model.onnx              # Table detection model
```

## Troubleshooting

### Orleans starts but models aren't loaded
```bash
# Check if models exist
docker exec -it autonomous-validation-orleans ls -la /models/huggingface/

# Check initialization logs
docker logs autonomous-validation-orleans
```

### Model conversion fails
```bash
# Check model provider logs
docker logs huggingface-models

# Rebuild model provider only
docker-compose build model-provider
```

### Performance issues
```bash
# Check available execution providers
curl http://localhost:8080/api/models/execution-providers

# Monitor memory usage
docker stats autonomous-validation-orleans
```

## Integration with .NET Code

The `ModelManagerGrain` automatically handles both real and mock models:

```csharp
// This works with both real and mock models
var loaded = await modelManager.LoadModelAsync(
    "/models/huggingface/table-structure-recognition/model.onnx", 
    "structure-recognition"
);

// Mock models return placeholder results
var result = await modelManager.RunInferenceAsync("structure-recognition", input);
```

## CI/CD Integration

For automated testing:

```yaml
# GitHub Actions example
- name: Test with mock models
  run: |
    docker-compose -f docker-compose.test.yml up -d orleans-app
    # Run integration tests
    docker-compose down
```

This setup provides maximum flexibility for different deployment scenarios while maintaining a consistent interface in the Orleans application.
