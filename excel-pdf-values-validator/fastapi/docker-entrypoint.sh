#!/bin/bash
set -e

# Docker entrypoint script for FastAPI backend with model validation
# This script ensures models are available before starting the application

echo "🚀 Starting FastAPI backend with cached models..."

# Check if models directory is mounted and populated
MODEL_DIR="/app/models"
REQUIRED_MODELS=(
    "BAAI/bge-small-en-v1.5"
    "Salesforce/blip-image-captioning-base"
)

echo "🔍 Validating model cache..."

# Check if models directory exists and is not empty
if [ ! -d "$MODEL_DIR" ] || [ -z "$(ls -A $MODEL_DIR 2>/dev/null)" ]; then
    echo "⚠️  WARNING: Models directory is empty or not mounted!"
    echo "   Expected: $MODEL_DIR"
    echo "   This will cause models to be downloaded at runtime."
    echo "   To fix this:"
    echo "   1. Run: python scripts/download-models.py"
    echo "   2. Mount models with: -v ./models_cache:/app/models"
    echo ""
else
    echo "✅ Models directory found: $MODEL_DIR"
    
    # List available models
    echo "📦 Available cached models:"
    find "$MODEL_DIR" -name "config.json" -o -name "pytorch_model.bin" -o -name "model.safetensors" | \
        head -10 | sed 's|^|   |'
    
    # Check model sizes
    TOTAL_SIZE=$(du -sh "$MODEL_DIR" 2>/dev/null | cut -f1 || echo "Unknown")
    echo "💾 Total model cache size: $TOTAL_SIZE"
fi

# Set up Python path
export PYTHONPATH="/app:$PYTHONPATH"

# Wait for dependencies if needed
if [ -n "$DATABASE_URL" ]; then
    echo "⏳ Waiting for database to be ready..."
    python -c "
try:
    import time
    import psycopg2
    import os
    from urllib.parse import urlparse

    db_url = os.getenv('DATABASE_URL', '')
    if db_url:
        parsed = urlparse(db_url)
        for i in range(30):
            try:
                conn = psycopg2.connect(
                    host=parsed.hostname,
                    port=parsed.port or 5432,
                    user=parsed.username,
                    password=parsed.password,
                    database=parsed.path[1:] if parsed.path else 'postgres'
                )
                conn.close()
                print('✅ Database is ready')
                break
            except:
                if i < 29:
                    print(f'⏳ Database not ready, retrying... ({i+1}/30)')
                    time.sleep(2)
                else:
                    print('❌ Database connection failed after 30 attempts')
                    exit(1)
except ImportError:
    print('⚠️  psycopg2 not available, skipping database check')
    print('   Make sure your requirements.txt includes psycopg2-binary')
"
fi

if [ -n "$REDIS_URL" ]; then
    echo "⏳ Waiting for Redis to be ready..."
    python -c "
import time
import redis
import os
from urllib.parse import urlparse

redis_url = os.getenv('REDIS_URL', '')
if redis_url:
    parsed = urlparse(redis_url)
    for i in range(30):
        try:
            r = redis.Redis(host=parsed.hostname, port=parsed.port or 6379, db=parsed.path[1:] if parsed.path else 0)
            r.ping()
            print('✅ Redis is ready')
            break
        except:
            if i < 29:
                print(f'⏳ Redis not ready, retrying... ({i+1}/30)')
                time.sleep(1)
            else:
                print('❌ Redis connection failed after 30 attempts')
                exit(1)
"
fi

# Initialize models if needed (this should be fast with cached models)
echo "🧠 Initializing ML models..."
python -c "
try:
    from app.utils.model_init import initialize_models
    success = initialize_models()
    if success:
        print('✅ Models initialized successfully')
    else:
        print('⚠️  Model initialization had some issues but continuing...')
except Exception as e:
    print(f'⚠️  Model initialization failed: {e}')
    print('   Application will try to load models on-demand')
"

echo "🎯 Starting application: $@"

# Execute the main command
exec "$@"
