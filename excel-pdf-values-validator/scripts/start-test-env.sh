#!/bin/bash
# start-test-env.sh - Start development environment for manual E2E testing

set -e

echo "🚀 Starting Test Environment..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "📦 Building and starting all test services..."
docker-compose -f docker-compose.test.yml up --build -d redis postgres backend celery-worker frontend

echo "⏳ Waiting for services to start..."
sleep 10

echo "🔍 Service Status:"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Redis:    localhost:6379"
echo "Postgres: localhost:5433"

echo ""
echo "✅ Test environment is starting up!"
echo ""
echo "📋 Available commands:"
echo "  Check backend health:  curl http://localhost:8000/health"
echo "  Check frontend:        curl http://localhost:3000"
echo "  View logs:             docker-compose -f docker-compose.test.yml logs [service]"
echo "  Stop services:         docker-compose -f docker-compose.test.yml down"
echo "  Run Cypress UI:        cd frontend && npx cypress open"
echo "  Run Cypress headless:  cd frontend && npx cypress run"
echo ""
