#!/bin/bash

# Oracle VM Deployment Script for ValidatorAI
# This script deploys the application to Oracle VM using Docker Compose

set -e  # Exit on any error

# Configuration
APP_NAME="validator-ai"
APP_VERSION=${1:-"latest"}
ORACLE_VM_HOST=${ORACLE_VM_HOST:-"your-oracle-vm-host.com"}
ORACLE_VM_USER=${ORACLE_VM_USER:-"opc"}
SSH_KEY_PATH=${SSH_KEY_PATH:-"~/.ssh/oracle_vm_key"}
DEPLOY_PATH="/opt/validator-ai"
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"your-registry.com"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if SSH key exists
    if [ ! -f "$SSH_KEY_PATH" ]; then
        log_error "SSH key not found at $SSH_KEY_PATH"
        exit 1
    fi
    
    # Check if docker is available locally for building
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check if ssh is available
    if ! command -v ssh &> /dev/null; then
        log_error "SSH is not installed or not in PATH"
        exit 1
    fi
    
    log_info "Prerequisites check passed"
}

# Test SSH connection
test_ssh_connection() {
    log_info "Testing SSH connection to Oracle VM..."
    
    if ssh -i "$SSH_KEY_PATH" -o ConnectTimeout=10 -o BatchMode=yes "$ORACLE_VM_USER@$ORACLE_VM_HOST" "echo 'Connection successful'" &>/dev/null; then
        log_info "SSH connection successful"
    else
        log_error "Failed to connect to Oracle VM. Please check your SSH configuration."
        exit 1
    fi
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    # Build backend image
    log_info "Building backend image..."
    docker build -t "$DOCKER_REGISTRY/$APP_NAME-backend:$APP_VERSION" .
    
    # Build frontend image
    log_info "Building frontend image..."
    docker build -t "$DOCKER_REGISTRY/$APP_NAME-frontend:$APP_VERSION" ./frontend
    
    log_info "Docker images built successfully"
}

# Push images to registry (if using a registry)
push_images() {
    if [ "$DOCKER_REGISTRY" != "local" ]; then
        log_info "Pushing images to registry..."
        docker push "$DOCKER_REGISTRY/$APP_NAME-backend:$APP_VERSION"
        docker push "$DOCKER_REGISTRY/$APP_NAME-frontend:$APP_VERSION"
        log_info "Images pushed successfully"
    else
        log_info "Using local registry, skipping push"
    fi
}

# Copy deployment files to Oracle VM
copy_deployment_files() {
    log_info "Copying deployment files to Oracle VM..."
    
    # Create deployment directory
    ssh -i "$SSH_KEY_PATH" "$ORACLE_VM_USER@$ORACLE_VM_HOST" "sudo mkdir -p $DEPLOY_PATH"
    ssh -i "$SSH_KEY_PATH" "$ORACLE_VM_USER@$ORACLE_VM_HOST" "sudo chown $ORACLE_VM_USER:$ORACLE_VM_USER $DEPLOY_PATH"
    
    # Copy docker-compose and configuration files
    scp -i "$SSH_KEY_PATH" deploy/oracle-vm/docker-compose.prod.yml "$ORACLE_VM_USER@$ORACLE_VM_HOST:$DEPLOY_PATH/docker-compose.yml"
    scp -i "$SSH_KEY_PATH" deploy/oracle-vm/.env.prod "$ORACLE_VM_USER@$ORACLE_VM_HOST:$DEPLOY_PATH/.env"
    scp -i "$SSH_KEY_PATH" deploy/oracle-vm/nginx.conf "$ORACLE_VM_USER@$ORACLE_VM_HOST:$DEPLOY_PATH/"
    
    # Copy systemd service file
    scp -i "$SSH_KEY_PATH" deploy/oracle-vm/validator-ai.service "$ORACLE_VM_USER@$ORACLE_VM_HOST:/tmp/"
    ssh -i "$SSH_KEY_PATH" "$ORACLE_VM_USER@$ORACLE_VM_HOST" "sudo mv /tmp/validator-ai.service /etc/systemd/system/"
    
    log_info "Deployment files copied successfully"
}

# Setup Oracle VM environment
setup_vm_environment() {
    log_info "Setting up Oracle VM environment..."
    
    ssh -i "$SSH_KEY_PATH" "$ORACLE_VM_USER@$ORACLE_VM_HOST" << 'EOF'
        # Update system packages
        sudo yum update -y
        
        # Install Docker if not present
        if ! command -v docker &> /dev/null; then
            echo "Installing Docker..."
            sudo yum install -y docker
            sudo systemctl start docker
            sudo systemctl enable docker
            sudo usermod -aG docker $USER
        fi
        
        # Install Docker Compose if not present
        if ! command -v docker-compose &> /dev/null; then
            echo "Installing Docker Compose..."
            sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
        fi
        
        # Create application directories
        sudo mkdir -p /var/log/validator-ai
        sudo mkdir -p /var/lib/validator-ai/data
        sudo mkdir -p /var/lib/validator-ai/uploads
        
        # Set permissions
        sudo chown -R $USER:$USER /var/lib/validator-ai
        sudo chown -R $USER:$USER /var/log/validator-ai
        
        # Setup firewall rules
        sudo firewall-cmd --permanent --add-port=80/tcp
        sudo firewall-cmd --permanent --add-port=443/tcp
        sudo firewall-cmd --reload
        
        echo "Oracle VM environment setup completed"
EOF
    
    log_info "Oracle VM environment setup completed"
}

# Deploy application
deploy_application() {
    log_info "Deploying application to Oracle VM..."
    
    ssh -i "$SSH_KEY_PATH" "$ORACLE_VM_USER@$ORACLE_VM_HOST" << EOF
        cd $DEPLOY_PATH
        
        # Stop existing services
        if [ -f docker-compose.yml ]; then
            docker-compose down || true
        fi
        
        # Pull latest images (if using registry)
        if [ "$DOCKER_REGISTRY" != "local" ]; then
            docker-compose pull
        fi
        
        # Start services
        docker-compose up -d
        
        # Enable systemd service
        sudo systemctl daemon-reload
        sudo systemctl enable validator-ai
        sudo systemctl start validator-ai
        
        # Wait for services to start
        sleep 30
        
        # Check service status
        docker-compose ps
        
        echo "Application deployed successfully"
EOF
    
    log_info "Application deployed successfully"
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    # Wait a bit for services to fully start
    sleep 10
    
    # Check if services are responding
    if curl -f -s "http://$ORACLE_VM_HOST/health" > /dev/null; then
        log_info "Health check passed - Application is running"
    else
        log_warn "Health check failed - Application may still be starting"
        log_info "You can check the status manually with: ssh -i $SSH_KEY_PATH $ORACLE_VM_USER@$ORACLE_VM_HOST 'cd $DEPLOY_PATH && docker-compose ps'"
    fi
}

# Rollback function
rollback() {
    log_warn "Rolling back to previous version..."
    
    ssh -i "$SSH_KEY_PATH" "$ORACLE_VM_USER@$ORACLE_VM_HOST" << EOF
        cd $DEPLOY_PATH
        
        # Stop current deployment
        docker-compose down
        
        # Restore previous version (if backup exists)
        if [ -f docker-compose.yml.backup ]; then
            mv docker-compose.yml.backup docker-compose.yml
            docker-compose up -d
            echo "Rollback completed"
        else
            echo "No backup found for rollback"
        fi
EOF
}

# Cleanup old images
cleanup() {
    log_info "Cleaning up old Docker images..."
    
    ssh -i "$SSH_KEY_PATH" "$ORACLE_VM_USER@$ORACLE_VM_HOST" << 'EOF'
        # Remove unused images
        docker image prune -f
        
        # Remove unused containers
        docker container prune -f
        
        # Remove unused volumes
        docker volume prune -f
        
        echo "Cleanup completed"
EOF
    
    log_info "Cleanup completed"
}

# Main deployment process
main() {
    log_info "Starting deployment of ValidatorAI to Oracle VM..."
    log_info "Version: $APP_VERSION"
    log_info "Target: $ORACLE_VM_USER@$ORACLE_VM_HOST"
    
    # Trap to handle errors
    trap 'log_error "Deployment failed. You may need to rollback manually."; exit 1' ERR
    
    # Run deployment steps
    check_prerequisites
    test_ssh_connection
    
    # Ask for confirmation
    read -p "Do you want to continue with deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Deployment cancelled"
        exit 0
    fi
    
    build_images
    push_images
    copy_deployment_files
    setup_vm_environment
    deploy_application
    health_check
    cleanup
    
    log_info "🎉 Deployment completed successfully!"
    log_info "Application should be available at: http://$ORACLE_VM_HOST"
    log_info "To monitor logs: ssh -i $SSH_KEY_PATH $ORACLE_VM_USER@$ORACLE_VM_HOST 'cd $DEPLOY_PATH && docker-compose logs -f'"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "rollback")
        rollback
        ;;
    "cleanup")
        cleanup
        ;;
    "health")
        health_check
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|cleanup|health} [version]"
        echo "  deploy  - Deploy application (default)"
        echo "  rollback - Rollback to previous version"
        echo "  cleanup - Clean up old Docker images"
        echo "  health  - Perform health check"
        exit 1
        ;;
esac
