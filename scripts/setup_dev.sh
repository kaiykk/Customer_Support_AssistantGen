#!/bin/bash

###############################################################################
# Development Environment Setup Script for AssistGen
#
# This script sets up a complete development environment for AssistGen.
# It performs the following tasks:
# - Checks system prerequisites
# - Creates Python virtual environment
# - Installs backend dependencies
# - Installs frontend dependencies
# - Sets up configuration files
# - Initializes databases
# - Runs initial tests
#
# Usage: ./scripts/setup_dev.sh
#
# Author: AssistGen Team
###############################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

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

log_step() {
    echo -e "\n${BLUE}==== $1 ====${NC}\n"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        log_info "$1 is installed: $(command -v $1)"
        return 0
    else
        log_error "$1 is not installed"
        return 1
    fi
}

###############################################################################
# Setup Functions
###############################################################################

check_prerequisites() {
    log_step "Checking Prerequisites"
    
    local all_ok=true
    
    # Check Python
    if check_command python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_info "Python version: $PYTHON_VERSION"
    else
        all_ok=false
    fi
    
    # Check Node.js
    if check_command node; then
        NODE_VERSION=$(node --version)
        log_info "Node.js version: $NODE_VERSION"
    else
        all_ok=false
    fi
    
    # Check npm
    if check_command npm; then
        NPM_VERSION=$(npm --version)
        log_info "npm version: $NPM_VERSION"
    else
        all_ok=false
    fi
    
    # Check Docker (optional but recommended)
    if check_command docker; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
        log_info "Docker version: $DOCKER_VERSION"
    else
        log_warn "Docker is not installed (optional for development)"
    fi
    
    # Check Docker Compose (optional but recommended)
    if check_command docker-compose; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | tr -d ',')
        log_info "Docker Compose version: $COMPOSE_VERSION"
    else
        log_warn "Docker Compose is not installed (optional for development)"
    fi
    
    if [ "$all_ok" = false ]; then
        log_error "Some prerequisites are missing. Please install them first."
        exit 1
    fi
    
    log_info "All required prerequisites are installed"
}

setup_backend() {
    log_step "Setting Up Backend"
    
    cd "$PROJECT_ROOT/backend"
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
    else
        log_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    log_info "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        log_info "Installing Python dependencies..."
        pip install -r requirements.txt
    else
        log_warn "requirements.txt not found, skipping dependency installation"
    fi
    
    # Create necessary directories
    log_info "Creating necessary directories..."
    mkdir -p uploads logs data
    
    log_info "Backend setup completed"
}

setup_frontend() {
    log_step "Setting Up Frontend"
    
    cd "$PROJECT_ROOT/frontend"
    
    # Install dependencies
    if [ -f "package.json" ]; then
        log_info "Installing Node.js dependencies..."
        npm install
    else
        log_warn "package.json not found, skipping dependency installation"
    fi
    
    log_info "Frontend setup completed"
}

setup_config() {
    log_step "Setting Up Configuration"
    
    cd "$PROJECT_ROOT"
    
    # Backend configuration
    if [ ! -f "backend/.env" ]; then
        if [ -f "config/development.env.example" ]; then
            log_info "Creating backend .env file from example..."
            cp config/development.env.example backend/.env
            log_warn "Please update backend/.env with your actual configuration values"
        else
            log_warn "config/development.env.example not found"
        fi
    else
        log_info "backend/.env already exists"
    fi
    
    # Frontend configuration
    if [ ! -f "frontend/.env" ]; then
        if [ -f "frontend/.env.example" ]; then
            log_info "Creating frontend .env file from example..."
            cp frontend/.env.example frontend/.env
            log_warn "Please update frontend/.env with your actual configuration values"
        else
            log_warn "frontend/.env.example not found"
        fi
    else
        log_info "frontend/.env already exists"
    fi
    
    log_info "Configuration setup completed"
}

setup_database() {
    log_step "Setting Up Database"
    
    # Check if Docker is available
    if command -v docker-compose &> /dev/null; then
        log_info "Starting database services with Docker Compose..."
        cd "$PROJECT_ROOT"
        
        if [ -f "docker-compose.yml" ]; then
            # Start only database and redis services
            docker-compose up -d database redis
            
            log_info "Waiting for database to be ready..."
            sleep 10
            
            log_info "Database services started"
        else
            log_warn "docker-compose.yml not found"
        fi
    else
        log_warn "Docker Compose not available. Please set up MySQL and Redis manually."
        log_info "MySQL: localhost:3306"
        log_info "Redis: localhost:6379"
    fi
}

run_tests() {
    log_step "Running Tests"
    
    # Backend tests
    cd "$PROJECT_ROOT/backend"
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        
        if [ -f "pytest.ini" ]; then
            log_info "Running backend tests..."
            pytest tests/ -v || log_warn "Some backend tests failed"
        else
            log_warn "pytest.ini not found, skipping backend tests"
        fi
    fi
    
    # Frontend tests
    cd "$PROJECT_ROOT/frontend"
    if [ -f "package.json" ]; then
        log_info "Running frontend tests..."
        npm test || log_warn "Some frontend tests failed"
    fi
}

show_next_steps() {
    log_step "Setup Complete!"
    
    echo -e "${GREEN}Development environment is ready!${NC}\n"
    echo "Next steps:"
    echo ""
    echo "1. Update configuration files:"
    echo "   - backend/.env"
    echo "   - frontend/.env"
    echo ""
    echo "2. Start the backend server:"
    echo "   cd backend"
    echo "   source venv/bin/activate"
    echo "   uvicorn main:app --reload"
    echo ""
    echo "3. Start the frontend development server:"
    echo "   cd frontend"
    echo "   npm run dev"
    echo ""
    echo "4. Access the application:"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Backend API: http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/api/docs"
    echo ""
    echo "5. Run tests:"
    echo "   ./scripts/run_tests.sh"
    echo ""
    echo "For more information, see the documentation in docs/"
}

###############################################################################
# Main Setup Flow
###############################################################################

main() {
    log_info "Starting AssistGen development environment setup..."
    log_info "Project root: $PROJECT_ROOT"
    
    check_prerequisites
    setup_backend
    setup_frontend
    setup_config
    setup_database
    
    # Ask user if they want to run tests
    read -p "Do you want to run tests now? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_tests
    fi
    
    show_next_steps
}

# Run main function
main
