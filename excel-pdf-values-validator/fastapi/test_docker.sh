#!/bin/bash

# Test script for autonomous agent system with Docker
set -e

echo "🚀 Testing Autonomous Agent System with Docker"
echo "=============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t autonomous-agents .

echo "✅ Docker image built successfully"

# Start the services
echo "🎯 Starting services with docker-compose..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🏥 Checking service health..."

# Check Redis
if docker-compose exec redis redis-cli ping | grep -q PONG; then
    echo "✅ Redis is healthy"
else
    echo "❌ Redis is not responding"
fi

# Check FastAPI
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ FastAPI is healthy"
else
    echo "❌ FastAPI is not responding"
    echo "📋 FastAPI logs:"
    docker-compose logs web
fi

# Check Celery worker
if docker-compose exec celery-worker celery -A autonomous_agents.worker status > /dev/null 2>&1; then
    echo "✅ Celery worker is healthy"
else
    echo "❌ Celery worker is not responding"
    echo "📋 Celery worker logs:"
    docker-compose logs celery-worker
fi

echo ""
echo "🌐 Services are available at:"
echo "   FastAPI: http://localhost:8000"
echo "   Flower (monitoring): http://localhost:5555 (run with --profile monitoring)"
echo ""
echo "📊 To view logs:"
echo "   docker-compose logs -f [service_name]"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose down"
echo ""
echo "🧹 To clean up everything:"
echo "   docker-compose down -v --rmi all"
