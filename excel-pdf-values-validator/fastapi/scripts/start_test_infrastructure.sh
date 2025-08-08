#!/bin/bash

# Script to start the test infrastructure

echo "🚀 Starting test infrastructure with Docker..."

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start Redis for testing
echo "📦 Starting Redis for testing..."
docker run -d \
    --name redis-test \
    --rm \
    -p 6380:6379 \
    redis:7-alpine \
    redis-server --appendonly yes

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
sleep 3

# Test Redis connection
if docker exec redis-test redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis is ready!"
else
    echo "❌ Redis failed to start"
    exit 1
fi

echo "🎯 Test infrastructure is ready!"
echo "Redis is available at: localhost:6380"
echo ""
echo "To run tests with infrastructure:"
echo "  CELERY_BROKER_URL=redis://localhost:6380/0 python -m pytest tests/ -v"
echo ""
echo "To stop the infrastructure:"
echo "  docker stop redis-test"
