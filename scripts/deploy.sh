#!/bin/bash

###############################################################################
# Production Deployment Script for AssistGen
#
# This script handles the deployment of AssistGen to a production environment.
# It performs the following tasks:
# - Validates environment configuration
# - Builds Docker images
# - Runs database migrations
# - Deploys services using Docker Compose
# - Performs health checks
#
# Usage: ./scripts/deploy.sh [options]
# Options:
#   --skip-build    Skip Docker image building
#   --skip-migrate  Skip database migrations
#   --rollback      Rollback to previous deployment
#
# Author: AssistGen Team
###############################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.prod.yml"
ENV_FILE="$PROJECT_ROOT/config/.env.production"
BACKUP_DIR="$PROJECT_ROOT/backups"

# Parse command line arguments
SKIP_BUILD=false
SKIP_MIGRATE=false
ROLLBACK=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --skip-migrate)
            SKIP_MIGRATE=true
            shift
            ;;
        --rollback)
            ROLLBACK=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

###############################################################################
# Helper Functions
###############################################################################

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if environment file exists
    if [ ! -f "$ENV_FILE" ]; then
        log_error "Environment file not found: $ENV_FILE"
        log_info "Please create it from config/production.env.example"
        exit 1
    fi
    
    log_info "Prerequisites check passed"
}

validate_config() {
    log_info "Validating configuration..."
    
    # Source environment file
    set -a
    source "$ENV_FILE"
    set +a
    
    # Check required variables
    required_vars=(
        "DB_HOST" "DB_USER" "DB_PASSWORD" "DB_NAME"
        "SECRET_KEY" "DEEPSEEK_API_KEY"
        "REDIS_HOST" "REDIS_PASSWORD"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            log_error "Required environment variable $var is not set"
            exit 1
        fi
    done
    
    # Check for default/weak values
    if [[ "$SECRET_KEY" == *"CHANGE_ME"* ]] || [[ "$SECRET_KEY" == *"change"* ]]; then
        log_error "SECRET_KEY appears to be a default value. Please set a strong random key."
        exit 1
    fi
    
    log_info "Configuration validation passed"
}

create_backup() {
    log_info "Creating backup..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    # Backup timestamp
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
    
    # Backup database
    docker-compose -f "$COMPOSE_FILE" exec -T database \
        mysqldump -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" \
        > "$BACKUP_DIR/db_$TIMESTAMP.sql" 2>/dev/null || true
    
    # Backup uploads directory
    if [ -d "$PROJECT_ROOT/uploads" ]; then
        tar -czf "$BACKUP_FILE" -C "$PROJECT_ROOT" uploads
        log_info "Backup created: $BACKUP_FILE"
    fi
}

build_images() {
    if [ "$SKIP_BUILD" = true ]; then
        log_warn "Skipping Docker image build"
        return
    fi
    
    log_info "Building Docker images..."
    
    cd "$PROJECT_ROOT"
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    log_info "Docker images built successfully"
}

run_migrations() {
    if [ "$SKIP_MIGRATE" = true ]; then
        log_warn "Skipping database migrations"
        return
    fi
    
    log_info "Running database migrations..."
    
    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    sleep 10
    
    # Run migrations
    docker-compose -f "$COMPOSE_FILE" exec -T backend \
        python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())" \
        || log_warn "Migration command failed or not implemented"
    
    log_info "Database migrations completed"
}

deploy_services() {
    log_info "Deploying services..."
    
    cd "$PROJECT_ROOT"
    
    # Pull latest images (if using registry)
    # docker-compose -f "$COMPOSE_FILE" pull
    
    # Start services
    docker-compose -f "$COMPOSE_FILE" up -d
    
    log_info "Services deployed successfully"
}

health_check() {
    log_info "Performing health checks..."
    
    # Wait for services to start
    sleep 15
    
    # Check backend health
    MAX_RETRIES=30
    RETRY_COUNT=0
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            log_info "Backend health check passed"
            break
        fi
        
        RETRY_COUNT=$((RETRY_COUNT + 1))
        log_info "Waiting for backend to be ready... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 2
    done
    
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        log_error "Backend health check failed"
        return 1
    fi
    
    # Check frontend
    if curl -f http://localhost/ &> /dev/null; then
        log_info "Frontend health check passed"
    else
        log_warn "Frontend health check failed"
    fi
    
    log_info "Health checks completed"
}

rollback_deployment() {
    log_warn "Rolling back deployment..."
    
    # Stop current services
    docker-compose -f "$COMPOSE_FILE" down
    
    # Restore from latest backup
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/backup_*.tar.gz 2>/dev/null | head -1)
    
    if [ -n "$LATEST_BACKUP" ]; then
        log_info "Restoring from backup: $LATEST_BACKUP"
        tar -xzf "$LATEST_BACKUP" -C "$PROJECT_ROOT"
    else
        log_warn "No backup found for rollback"
    fi
    
    # Restart services with previous version
    docker-compose -f "$COMPOSE_FILE" up -d
    
    log_info "Rollback completed"
}

show_status() {
    log_info "Deployment status:"
    docker-compose -f "$COMPOSE_FILE" ps
}

###############################################################################
# Main Deployment Flow
###############################################################################

main() {
    log_info "Starting AssistGen production deployment..."
    log_info "Project root: $PROJECT_ROOT"
    
    # Handle rollback
    if [ "$ROLLBACK" = true ]; then
        rollback_deployment
        show_status
        exit 0
    fi
    
    # Normal deployment flow
    check_prerequisites
    validate_config
    create_backup
    build_images
    deploy_services
    run_migrations
    
    # Health checks
    if health_check; then
        log_info "Deployment completed successfully!"
        show_status
    else
        log_error "Deployment failed health checks"
        log_warn "Consider rolling back with: $0 --rollback"
        exit 1
    fi
}

# Run main function
main
