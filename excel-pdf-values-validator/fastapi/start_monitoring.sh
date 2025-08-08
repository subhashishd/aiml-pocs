#!/bin/bash

# Complete Monitoring Setup Script for Autonomous Agent System
set -e

echo "🔍 Starting Comprehensive Monitoring Setup for Autonomous Agent System"
echo "============================================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"

# Create monitoring directory if it doesn't exist
mkdir -p monitoring

# Check if monitoring configurations exist
if [ ! -f "monitoring/prometheus.yml" ]; then
    echo "❌ Prometheus configuration not found. Please ensure monitoring files are in place."
    exit 1
fi

echo "✅ Monitoring configurations found"

# Start the complete monitoring stack
echo "🚀 Starting complete monitoring stack with Prometheus and Grafana..."
docker-compose -f docker-compose.monitoring.yml up -d

echo "⏳ Waiting for services to be ready..."
sleep 60

# Check service health
echo "🏥 Checking service health..."

# Check Redis
if docker-compose -f docker-compose.monitoring.yml exec -T redis redis-cli ping | grep -q PONG; then
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
    docker-compose -f docker-compose.monitoring.yml logs web
fi

# Check Prometheus
if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo "✅ Prometheus is healthy"
else
    echo "❌ Prometheus is not responding"
fi

# Check Grafana
if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✅ Grafana is healthy"
else
    echo "❌ Grafana is not responding"
fi

# Check metrics endpoint
if curl -f http://localhost:8000/metrics > /dev/null 2>&1; then
    echo "✅ Metrics endpoint is responding"
else
    echo "❌ Metrics endpoint is not responding"
fi

echo ""
echo "🌐 Services are available at:"
echo "   📊 Grafana Dashboard: http://localhost:3000 (admin/admin123)"
echo "   📈 Prometheus: http://localhost:9090"
echo "   🌸 Flower (Celery): http://localhost:5555"
echo "   🚀 FastAPI: http://localhost:8000"
echo "   📊 cAdvisor: http://localhost:8080"
echo "   📝 Metrics Endpoint: http://localhost:8000/metrics"
echo ""
echo "📊 Key Monitoring Endpoints:"
echo "   System Status: http://localhost:8000/system-status"
echo "   Memory Stats: http://localhost:8000/memory-stats"
echo "   Agent Telemetry: http://localhost:8000/agent-telemetry"
echo ""
echo "🔍 Monitoring Stack Features:"
echo "   ✅ Real-time system metrics"
echo "   ✅ Agent performance tracking"
echo "   ✅ Memory usage monitoring"
echo "   ✅ Task execution analytics"
echo "   ✅ Automated alerting"
echo "   ✅ Trend analysis"
echo "   ✅ Container metrics"
echo "   ✅ Redis metrics"
echo ""
echo "📋 To view logs:"
echo "   All services: docker-compose -f docker-compose.monitoring.yml logs -f"
echo "   Specific service: docker-compose -f docker-compose.monitoring.yml logs -f [service_name]"
echo ""
echo "🛑 To stop monitoring:"
echo "   docker-compose -f docker-compose.monitoring.yml down"
echo ""
echo "🧹 To clean up everything:"
echo "   docker-compose -f docker-compose.monitoring.yml down -v --rmi all"
echo ""

# Wait a bit more and try to import Grafana dashboard
echo "⏳ Setting up Grafana dashboard..."
sleep 30

# Try to set up Grafana dashboard (this might fail if Grafana isn't fully ready)
if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "📊 Grafana is ready for dashboard import"
    echo "   Import the dashboard from: monitoring/grafana-dashboard.json"
    echo "   Or it should be auto-provisioned at startup"
else
    echo "⏳ Grafana still starting up - dashboard will be available shortly"
fi

echo ""
echo "🎉 Monitoring Setup Complete!"
echo "============================================================================="
echo "📊 Dashboard: http://localhost:3000 (admin/admin123)"
echo "🔍 Start monitoring your autonomous agent system!"
