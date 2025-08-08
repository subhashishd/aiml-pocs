#!/bin/bash

# Autonomous Validation Agents - Service Deployment Script
# Usage: ./deploy-services.sh <environment> <image_tag>

set -euo pipefail

ENVIRONMENT=${1:-dev}
IMAGE_TAG=${2:-latest}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOYMENT_DIR="$(dirname "$SCRIPT_DIR")"

# Configuration
APP_NAME="autonomous-validation"
COMPOSE_FILE="$DEPLOYMENT_DIR/docker-compose.$ENVIRONMENT.yml"
ENV_FILE="$DEPLOYMENT_DIR/env/$ENVIRONMENT.env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Validate inputs
if [[ ! "$ENVIRONMENT" =~ ^(dev|prod)$ ]]; then
    log_error "Invalid environment: $ENVIRONMENT. Must be 'dev' or 'prod'"
    exit 1
fi

if [[ -z "$IMAGE_TAG" ]]; then
    log_error "Image tag cannot be empty"
    exit 1
fi

log "Starting deployment to $ENVIRONMENT environment with image tag: $IMAGE_TAG"

# Create necessary directories
sudo mkdir -p /opt/autonomous-validation/{logs,data,config}
sudo mkdir -p /var/log/autonomous-validation

# Set permissions
sudo chown -R $USER:$USER /opt/autonomous-validation
sudo chmod -R 755 /opt/autonomous-validation

# Create environment-specific docker-compose file
log "Creating environment-specific configuration..."

cat > "$COMPOSE_FILE" << EOF
version: '3.8'

services:
  orleans-silo:
    image: ghcr.io/autonomous-validation-agents/orleans-silo:${IMAGE_TAG}
    container_name: ${APP_NAME}-orleans-silo
    restart: unless-stopped
    ports:
      - "8080:8080"   # HTTP endpoint
      - "11111:11111" # Orleans silo port
      - "30000:30000" # Orleans gateway port
    environment:
      - ASPNETCORE_ENVIRONMENT=${ENVIRONMENT}
      - ORLEANS_CLUSTERING_PROVIDER=Localhost
      - LOGGING__LOGLEVEL__DEFAULT=Information
      - LOGGING__LOGLEVEL__ORLEANS=Warning
      - LOGGING__CONSOLE__LOGLEVEL__DEFAULT=Information
      - BUILD_NUMBER=\${BUILD_NUMBER:-unknown}
      - DEPLOYMENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    volumes:
      - /opt/autonomous-validation/logs:/app/logs
      - /opt/autonomous-validation/data:/app/data
      - /opt/autonomous-validation/config:/app/config
    networks:
      - autonomous-validation
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G

networks:
  autonomous-validation:
    driver: bridge
    name: ${APP_NAME}-network

volumes:
  app-logs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/autonomous-validation/logs
  app-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/autonomous-validation/data
EOF

# Create environment file
log "Creating environment configuration file..."

cat > "$ENV_FILE" << EOF
# Environment: $ENVIRONMENT
# Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

ENVIRONMENT=$ENVIRONMENT
IMAGE_TAG=$IMAGE_TAG
BUILD_NUMBER=${BUILD_NUMBER:-unknown}

# Orleans Configuration
ORLEANS_CLUSTERING_PROVIDER=Localhost
ORLEANS_GRAIN_DIRECTORY_CACHE_SIZE=1000000

# Logging Configuration
LOGGING__LOGLEVEL__DEFAULT=Information
LOGGING__LOGLEVEL__MICROSOFT=Warning
LOGGING__LOGLEVEL__ORLEANS=Warning

# Performance Configuration
DOTNET_gcServer=1
DOTNET_gcConcurrent=1
DOTNET_GCRetainVM=1

# Security Configuration
ASPNETCORE_HTTPS_PORT=8443
ASPNETCORE_Kestrel__Certificates__Default__Password=${SSL_CERT_PASSWORD:-}
EOF

# Stop existing services gracefully
log "Stopping existing services..."
if docker-compose -f "$COMPOSE_FILE" ps -q | grep -q .; then
    docker-compose -f "$COMPOSE_FILE" down --timeout 30
    log "Existing services stopped"
else
    log "No existing services found"
fi

# Pull latest images
log "Pulling container images..."
docker-compose -f "$COMPOSE_FILE" pull

# Start services
log "Starting services..."
docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

# Wait for services to be healthy
log "Waiting for services to be healthy..."
TIMEOUT=300
ELAPSED=0
INTERVAL=5

while [ $ELAPSED -lt $TIMEOUT ]; do
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "healthy"; then
        log_success "Services are healthy!"
        break
    fi
    
    if [ $ELAPSED -gt 0 ] && [ $((ELAPSED % 30)) -eq 0 ]; then
        log "Still waiting for services to be healthy... (${ELAPSED}s elapsed)"
        docker-compose -f "$COMPOSE_FILE" ps
    fi
    
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
done

if [ $ELAPSED -ge $TIMEOUT ]; then
    log_error "Services failed to become healthy within $TIMEOUT seconds"
    log "Container status:"
    docker-compose -f "$COMPOSE_FILE" ps
    log "Container logs:"
    docker-compose -f "$COMPOSE_FILE" logs --tail=50
    exit 1
fi

# Display deployment status
log "Deployment completed successfully!"
log "Services status:"
docker-compose -f "$COMPOSE_FILE" ps

log "Service endpoints:"
log "  - Health Check: http://localhost:8080/health"
log "  - Orleans Dashboard: http://localhost:8080/dashboard (if enabled)"

# Create deployment record
DEPLOYMENT_RECORD="/opt/autonomous-validation/deployments.log"
echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") | $ENVIRONMENT | $IMAGE_TAG | ${BUILD_NUMBER:-unknown} | SUCCESS" >> "$DEPLOYMENT_RECORD"

log_success "Deployment to $ENVIRONMENT environment completed successfully!"
log "Image tag: $IMAGE_TAG"
log "Build number: ${BUILD_NUMBER:-unknown}"
