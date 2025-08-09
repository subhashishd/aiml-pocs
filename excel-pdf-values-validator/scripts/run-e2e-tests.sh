#!/bin/bash
# run-e2e-tests.sh - Run E2E integration tests in Docker environment

set -e  # Exit on any error

echo "🚀 Starting E2E Integration Tests..."

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

echo "📦 Building and starting test services..."

# Start all services except playwright
docker-compose -f docker-compose.test.yml up -d --build redis postgres backend celery-worker frontend

echo "⏳ Waiting for services to be healthy..."

# Wait for backend to be healthy
echo "Waiting for backend service..."
timeout 180 bash -c 'until curl -f http://localhost:8000/health >/dev/null 2>&1; do sleep 5; echo "Still waiting for backend..."; done' || {
    echo "❌ Backend service failed to become healthy"
    echo "Backend logs:"
    docker-compose -f docker-compose.test.yml logs backend
    exit 1
}

# Wait for frontend to be healthy
echo "Waiting for frontend service..."
timeout 120 bash -c 'until curl -f http://localhost:3000 >/dev/null 2>&1; do sleep 5; echo "Still waiting for frontend..."; done' || {
    echo "❌ Frontend service failed to become healthy"
    echo "Frontend logs:"
    docker-compose -f docker-compose.test.yml logs frontend
    exit 1
}

echo "✅ All services are healthy!"

# Run Playwright tests
echo "🧪 Running Playwright E2E tests..."
docker-compose -f docker-compose.test.yml --profile testing run --rm playwright

echo "🎉 E2E tests completed successfully!"
