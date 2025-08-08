#!/bin/bash
# run-e2e-cached.sh - Run E2E tests with pre-cached models
# This script ensures models are downloaded before starting containers

set -e  # Exit on any error

echo "🚀 Starting E2E Integration Tests with Model Caching..."

# Function to cleanup containers
cleanup() {
    echo "🧹 Cleaning up test containers..."
    docker-compose -f docker-compose.test.yml down --volumes --remove-orphans
}

# Trap cleanup on exit
trap cleanup EXIT

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Navigate to project root
cd "$(dirname "$0")/.."

# Check if models are cached locally
MODELS_DIR="./models_cache"
if [ ! -d "$MODELS_DIR" ] || [ -z "$(ls -A $MODELS_DIR 2>/dev/null)" ]; then
    echo "📥 Models not found in cache, downloading..."
    
    # Check if Python environment has required packages
    python -c "import sentence_transformers, transformers" 2>/dev/null || {
        echo "❌ Required Python packages not found."
        echo "   Please install with: pip install sentence-transformers transformers torch"
        echo "   Or run in a virtual environment with these packages."
        exit 1
    }
    
    # Download models
    python scripts/download-models.py --cache-dir "$MODELS_DIR"
    
    if [ ! -d "$MODELS_DIR" ] || [ -z "$(ls -A $MODELS_DIR 2>/dev/null)" ]; then
        echo "❌ Model download failed. Please check your internet connection."
        exit 1
    fi
else
    echo "✅ Models found in cache: $MODELS_DIR"
    
    # Show cache info
    CACHE_SIZE=$(du -sh "$MODELS_DIR" 2>/dev/null | cut -f1 || echo "Unknown")
    echo "💾 Cache size: $CACHE_SIZE"
fi

echo "📦 Building and starting test services..."

# Start all services except cypress
docker-compose -f docker-compose.test.yml up -d --build redis postgres backend celery-worker frontend

echo "⏳ Waiting for services to be healthy..."

# Wait for backend to be healthy
echo "Waiting for backend service..."
timeout 180 bash -c 'until curl -f http://localhost:8000/health > /dev/null 2>&1; do sleep 5; echo "Still waiting for backend..."; done' || {
    echo "❌ Backend service failed to become healthy"
    echo "Backend logs:"
    docker-compose -f docker-compose.test.yml logs backend | tail -50
    exit 1
}

# Wait for frontend to be healthy
echo "Waiting for frontend service..."
timeout 120 bash -c 'until curl -f http://localhost:3000 > /dev/null 2>&1; do sleep 5; echo "Still waiting for frontend..."; done' || {
    echo "❌ Frontend service failed to become healthy"
    echo "Frontend logs:"
    docker-compose -f docker-compose.test.yml logs frontend | tail -50
    exit 1
}

echo "✅ All services are healthy!"

# Show service status
echo "📊 Service Status:"
echo "   Backend:  http://localhost:8000/health"
echo "   Frontend: http://localhost:3000"
echo "   Redis:    localhost:6379"
echo "   Postgres: localhost:5433"

# Quick API test
echo "🔍 Quick API health check..."
curl -s http://localhost:8000/health | jq '.' 2>/dev/null || echo "API response received"

# Run Cypress tests
echo "🧪 Running Cypress E2E tests..."
docker-compose -f docker-compose.test.yml --profile testing run --rm cypress

echo "🎉 E2E tests completed successfully!"
echo ""
echo "📝 Test artifacts:"
echo "   Videos:      frontend/cypress/videos/"
echo "   Screenshots: frontend/cypress/screenshots/"
echo "   Logs:        docker-compose -f docker-compose.test.yml logs [service]"
