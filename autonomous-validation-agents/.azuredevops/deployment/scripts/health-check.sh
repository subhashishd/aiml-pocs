#!/bin/bash

# Autonomous Validation Agents - Health Check Script
# Usage: ./health-check.sh <environment>

set -euo pipefail

ENVIRONMENT=${1:-dev}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOYMENT_DIR="$(dirname "$SCRIPT_DIR")"

# Configuration
APP_NAME="autonomous-validation"
COMPOSE_FILE="$DEPLOYMENT_DIR/docker-compose.$ENVIRONMENT.yml"
HEALTH_ENDPOINT="http://localhost:8080/health"
TIMEOUT=300
INTERVAL=5

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

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|prod)$ ]]; then
    log_error "Invalid environment: $ENVIRONMENT. Must be 'dev' or 'prod'"
    exit 1
fi

log "Starting health check for $ENVIRONMENT environment..."

# Check if docker-compose file exists
if [[ ! -f "$COMPOSE_FILE" ]]; then
    log_error "Docker compose file not found: $COMPOSE_FILE"
    exit 1
fi

# Function to check container health
check_container_health() {
    local container_name="$1"
    local health_status
    
    health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "not_found")
    
    case "$health_status" in
        "healthy")
            return 0
            ;;
        "unhealthy")
            log_error "Container $container_name is unhealthy"
            return 1
            ;;
        "starting")
            log "Container $container_name is still starting..."
            return 2
            ;;
        "not_found")
            log_error "Container $container_name not found"
            return 1
            ;;
        *)
            log_warning "Container $container_name health status: $health_status"
            return 2
            ;;
    esac
}

# Function to check HTTP endpoint
check_http_endpoint() {
    local url="$1"
    local response_code
    
    response_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [[ "$response_code" == "200" ]]; then
        return 0
    else
        log_error "HTTP endpoint $url returned status code: $response_code"
        return 1
    fi
}

# Function to get container logs
get_container_logs() {
    local container_name="$1"
    local lines="${2:-20}"
    
    if docker ps --format '{{.Names}}' | grep -q "^$container_name$"; then
        log "Recent logs from $container_name (last $lines lines):"
        docker logs --tail "$lines" "$container_name" 2>&1 | sed 's/^/  /'
    else
        log_error "Container $container_name is not running"
    fi
}

# Main health check logic
main_health_check() {
    local elapsed=0
    local all_healthy=false
    
    # List of containers to check
    local containers=(
        "${APP_NAME}-orleans-silo"
    )
    
    log "Checking container health..."
    
    while [[ $elapsed -lt $TIMEOUT ]]; do
        all_healthy=true
        
        for container in "${containers[@]}"; do
            if ! check_container_health "$container"; then
                all_healthy=false
                case $? in
                    1) # Unhealthy or not found
                        get_container_logs "$container" 10
                        return 1
                        ;;
                    2) # Still starting
                        if [[ $((elapsed % 30)) -eq 0 ]] && [[ $elapsed -gt 0 ]]; then
                            log "Container $container is still starting... (${elapsed}s elapsed)"
                        fi
                        ;;
                esac
                break
            fi
        done
        
        if [[ "$all_healthy" == "true" ]]; then
            log_success "All containers are healthy!"
            break
        fi
        
        sleep $INTERVAL
        elapsed=$((elapsed + INTERVAL))
    done
    
    if [[ "$all_healthy" != "true" ]]; then
        log_error "Health check timed out after ${TIMEOUT}s"
        return 1
    fi
    
    # Check HTTP endpoints
    log "Checking HTTP endpoints..."
    
    if check_http_endpoint "$HEALTH_ENDPOINT"; then
        log_success "Health endpoint is responding correctly"
    else
        log_error "Health endpoint check failed"
        return 1
    fi
    
    return 0
}

# Additional system checks
system_checks() {
    log "Performing system checks..."
    
    # Check disk space
    local disk_usage
    disk_usage=$(df /opt/autonomous-validation | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [[ $disk_usage -gt 85 ]]; then
        log_warning "Disk usage is high: ${disk_usage}%"
    else
        log "Disk usage: ${disk_usage}%"
    fi
    
    # Check memory usage
    local memory_usage
    memory_usage=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
    
    if [[ $(echo "$memory_usage > 85" | bc) -eq 1 ]]; then
        log_warning "Memory usage is high: ${memory_usage}%"
    else
        log "Memory usage: ${memory_usage}%"
    fi
    
    # Check container resource usage
    log "Container resource usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" \
        $(docker ps --filter "name=${APP_NAME}" --format "{{.Names}}") | sed 's/^/  /'
}

# Performance metrics
performance_metrics() {
    log "Gathering performance metrics..."
    
    # Test response time
    local response_time
    response_time=$(curl -s -o /dev/null -w "%{time_total}" "$HEALTH_ENDPOINT" 2>/dev/null || echo "0")
    
    log "Health endpoint response time: ${response_time}s"
    
    if [[ $(echo "$response_time > 5" | bc) -eq 1 ]]; then
        log_warning "Health endpoint response time is slow: ${response_time}s"
    fi
}

# Generate health report
generate_health_report() {
    local report_file="/opt/autonomous-validation/health-reports/health-$(date +%Y%m%d-%H%M%S).json"
    
    mkdir -p "$(dirname "$report_file")"
    
    cat > "$report_file" << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "environment": "$ENVIRONMENT",
  "status": "healthy",
  "containers": {
EOF

    local first=true
    for container in "${APP_NAME}-orleans-silo"; do
        if [[ "$first" != "true" ]]; then
            echo "," >> "$report_file"
        fi
        first=false
        
        local health_status
        health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "not_found")
        
        cat >> "$report_file" << EOF
    "$container": {
      "status": "$health_status",
      "uptime": "$(docker inspect --format='{{.State.StartedAt}}' "$container" 2>/dev/null || echo "N/A")"
    }
EOF
    done

    cat >> "$report_file" << EOF
  },
  "endpoints": {
    "health": {
      "url": "$HEALTH_ENDPOINT",
      "status": "$(check_http_endpoint "$HEALTH_ENDPOINT" && echo "healthy" || echo "unhealthy")",
      "response_time": "$(curl -s -o /dev/null -w "%{time_total}" "$HEALTH_ENDPOINT" 2>/dev/null || echo "0")s"
    }
  },
  "system": {
    "disk_usage": "$(df /opt/autonomous-validation | awk 'NR==2 {print $5}')%",
    "memory_usage": "$(free | awk 'NR==2{printf "%.1f%%", $3*100/$2}')"
  }
}
EOF

    log "Health report saved to: $report_file"
}

# Main execution
log "=== Autonomous Validation Agents Health Check ==="
log "Environment: $ENVIRONMENT"
log "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
log ""

# Run main health check
if main_health_check; then
    log_success "=== Primary Health Check PASSED ==="
    
    # Run additional checks
    system_checks
    performance_metrics
    generate_health_report
    
    log ""
    log_success "=== All Health Checks COMPLETED SUCCESSFULLY ==="
    log ""
    
    # Summary
    log "=== Health Check Summary ==="
    log "Environment: $ENVIRONMENT"
    log "Status: HEALTHY"
    log "Containers: $(docker ps --filter "name=${APP_NAME}" --format "{{.Names}}" | wc -l) running"
    log "Health Endpoint: $HEALTH_ENDPOINT (200 OK)"
    log "Check Duration: ${ELAPSED}s"
    log ""
    
    exit 0
else
    log_error "=== Primary Health Check FAILED ==="
    log ""
    
    # Show current status
    log "Current container status:"
    docker-compose -f "$COMPOSE_FILE" ps | sed 's/^/  /'
    log ""
    
    log "Recent container logs:"
    get_container_logs "${APP_NAME}-orleans-silo" 20
    log ""
    
    log_error "=== Health Check FAILED ==="
    exit 1
fi
