# Model Caching Strategy

This document explains the model caching implementation for the Excel-PDF Validator project, which optimizes model loading and reduces startup times in Docker environments.

## Overview

Instead of downloading models every time a Docker container is built or started, we pre-download models locally and mount them as volumes. This approach provides:

- **Faster container startup** (from ~5-10 minutes to ~30 seconds)
- **Reduced bandwidth usage** (models downloaded only once)
- **Offline deployment capability** (no internet required after initial download)
- **Consistent model versions** across all environments

## Architecture

```
Host Machine                          Docker Container
├── models_cache/                     ├── /app/models/ (mounted)
│   ├── BAAI/                        │   ├── BAAI/
│   │   └── bge-small-en-v1.5/       │   │   └── bge-small-en-v1.5/
│   └── Salesforce/                  │   └── Salesforce/
│       └── blip-image-captioning-base/ │       └── blip-image-captioning-base/
└── scripts/                         └── app/
    └── download-models.py               ├── services/
                                        └── utils/model_init.py
```

## Models Used

### Primary Models

1. **BGE Small English v1.5** (`BAAI/bge-small-en-v1.5`)
   - **Purpose**: Text embeddings for similarity search
   - **Size**: ~130 MB
   - **Framework**: sentence-transformers
   - **Essential**: Yes

2. **BLIP Image Captioning Base** (`Salesforce/blip-image-captioning-base`)
   - **Purpose**: Multimodal PDF processing (image analysis)
   - **Size**: ~990 MB
   - **Framework**: transformers
   - **Essential**: No (optional for advanced PDF processing)

## Usage

### 1. Download Models Locally

```bash
# Download all models
python scripts/download-models.py

# Download only essential models
python scripts/download-models.py --minimal

# Download to custom directory
python scripts/download-models.py --cache-dir /path/to/custom/cache

# Check what would be downloaded
python scripts/download-models.py --check
```

### 2. Run with Cached Models

```bash
# Run E2E tests with caching
./scripts/run-e2e-cached.sh

# Or manually run docker-compose
docker-compose -f docker-compose.test.yml up
```

### 3. Verify Model Cache

```bash
# Check cache size
du -sh ./models_cache

# List cached models
find ./models_cache -name "config.json" -o -name "*.bin" -o -name "*.safetensors"
```

## File Structure

### Scripts

- **`scripts/download-models.py`**: Downloads and caches models locally
- **`scripts/run-e2e-cached.sh`**: Runs E2E tests with model caching
- **`fastapi/docker-entrypoint.sh`**: Container startup script with model validation

### Docker Files

- **`fastapi/Dockerfile.cached`**: Optimized Dockerfile that expects mounted models
- **`docker-compose.test.yml`**: Updated with model volume mounts

### Application Files

- **`fastapi/app/utils/model_init.py`**: Model initialization and validation
- **`fastapi/app/services/embedding_service.py`**: Service using cached models

## Environment Variables

```bash
# Model cache directories (consistent across all containers)
SENTENCE_TRANSFORMERS_HOME=/app/models
TRANSFORMERS_CACHE=/app/models
HF_HOME=/app/models

# Model configuration
USE_MULTIMODAL_PDF=true          # Enable BLIP model usage
USE_LIGHTWEIGHT_MODEL=true       # Use smaller models when available
UNLOAD_MODELS_AFTER_PROCESSING=true  # Free memory after processing
```

## Volume Mounting

### Docker Compose

```yaml
services:
  backend:
    volumes:
      # Read-only mount of local model cache
      - ./models_cache:/app/models:ro
```

### Manual Docker Run

```bash
docker run -v ./models_cache:/app/models:ro your-app
```

## Validation and Health Checks

The system includes several validation mechanisms:

1. **Startup Validation**: `docker-entrypoint.sh` checks if models are available
2. **Application Health**: Model initialization during app startup
3. **Runtime Fallback**: Download models if cache fails (with warnings)

## Troubleshooting

### Models Not Found

```bash
# Check if cache directory exists
ls -la ./models_cache

# Re-download models
rm -rf ./models_cache
python scripts/download-models.py
```

### Container Startup Issues

```bash
# Check container logs
docker logs fastapi-backend-test

# Verify model mount
docker exec fastapi-backend-test ls -la /app/models
```

### Permission Issues

```bash
# Fix permissions on model cache
chmod -R 755 ./models_cache

# Or run with user mapping
docker run --user $(id -u):$(id -g) -v ./models_cache:/app/models:ro your-app
```

## Performance Benefits

| Scenario | Without Caching | With Caching | Improvement |
|----------|----------------|---------------|-------------|
| First build | 8-12 minutes | 15 minutes* | N/A |
| Subsequent builds | 8-12 minutes | 2-3 minutes | 75-80% faster |
| Container startup | 30-60 seconds | 10-15 seconds | 50-75% faster |
| Bandwidth usage | ~1.1 GB per build | ~1.1 GB once | 90%+ reduction |

*Initial download time, subsequent builds much faster

## Development Workflow

### Recommended Workflow

1. **Setup** (once per machine):
   ```bash
   python scripts/download-models.py
   ```

2. **Development**:
   ```bash
   docker-compose -f docker-compose.test.yml up
   ```

3. **Testing**:
   ```bash
   ./scripts/run-e2e-cached.sh
   ```

### CI/CD Integration

```yaml
# Example GitHub Actions
- name: Cache ML Models
  uses: actions/cache@v3
  with:
    path: models_cache
    key: ml-models-v1-${{ hashFiles('scripts/download-models.py') }}
    
- name: Download Models
  run: |
    if [ ! -d "models_cache" ]; then
      python scripts/download-models.py
    fi
```

## Security Considerations

- **Read-only mounts**: Models are mounted as read-only in containers
- **Integrity checks**: Models are validated during download and startup
- **Version pinning**: Specific model versions are used to ensure consistency
- **No secrets**: No API keys or credentials required for model access

## Future Enhancements

- **Model versioning**: Support for multiple model versions
- **Automatic updates**: Scheduled model updates with rollback capability
- **Compression**: Compress model cache for faster transfers
- **Distributed caching**: Share cache across multiple machines
