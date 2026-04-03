#!/bin/bash

###############################################################################
# Test Execution Script for AssistGen
#
# This script runs all tests for the AssistGen project including:
# - Backend unit tests
# - Backend integration tests
# - Frontend unit tests
# - Frontend component tests
# - End-to-end tests
# - Code coverage reporting
#
# Usage: ./scripts/run_tests.sh [options]
# Options:
#   --unit          Run only unit tests
#   --integration   Run only integration tests
#   --e2e           Run only end-to-end tests
#   --coverage      Generate coverage report
#   --backend       Run only backend tests
#   --frontend      Run only frontend tests
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

# Test options
RUN_UNIT=true
RUN_INTEGRATION=true
RUN_E2E=false
RUN_BACKEND=true
RUN_FRONTEND=true
GENERATE_COVERAGE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --unit)
            RUN_UNIT=true
            RUN_INTEGRATION=false
            RUN_E2E=false
            shift
            ;;
        --integration)
            RUN_UNIT=false
            RUN_INTEGRATION=true
            RUN_E2E=false
            shift
            ;;
        --e2e)
            RUN_UNIT=false
            RUN_INTEGRATION=false
            RUN_E2E=true
            shift
            ;;
        --coverage)
            GENERATE_COVERAGE=true
            shift
            ;;
        --backend)
            RUN_BACKEND=true
            RUN_FRONTEND=false
            shift
            ;;
        --frontend)
            RUN_BACKEND=false
            RUN_FRONTEND=true
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

log_step() {
    echo -e "\n${BLUE}==== $1 ====${NC}\n"
}

###############################################################################
# Test Functions
###############################################################################

run_backend_unit_tests() {
    log_step "Running Backend Unit Tests"
    
    cd "$PROJECT_ROOT/backend"
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        log_error "Virtual environment not found. Run setup_dev.sh first."
        return 1
    fi
    
    # Run pytest
    if [ "$GENERATE_COVERAGE" = true ]; then
        log_info "Running tests with coverage..."
        pytest tests/unit/ -v --cov=app --cov-report=html --cov-report=term
        log_info "Coverage report generated in backend/htmlcov/"
    else
        pytest tests/unit/ -v
    fi
}

run_backend_integration_tests() {
    log_step "Running Backend Integration Tests"
    
    cd "$PROJECT_ROOT/backend"
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        log_error "Virtual environment not found. Run setup_dev.sh first."
        return 1
    fi
    
    # Check if integration tests exist
    if [ -d "tests/integration" ] && [ "$(ls -A tests/integration)" ]; then
        pytest tests/integration/ -v
    else
        log_warn "No integration tests found"
    fi
}

run_frontend_unit_tests() {
    log_step "Running Frontend Unit Tests"
    
    cd "$PROJECT_ROOT/frontend"
    
    # Check if package.json exists
    if [ ! -f "package.json" ]; then
        log_error "package.json not found"
        return 1
    fi
    
    # Run tests
    if [ "$GENERATE_COVERAGE" = true ]; then
        log_info "Running tests with coverage..."
        npm run test:coverage || npm test -- --coverage
    else
        npm test
    fi
}

run_e2e_tests() {
    log_step "Running End-to-End Tests"
    
    cd "$PROJECT_ROOT"
    
    # Check if e2e tests exist
    if [ -d "tests/e2e" ] && [ "$(ls -A tests/e2e)" ]; then
        log_info "Starting services for e2e tests..."
        
        # Start services with docker-compose
        if command -v docker-compose &> /dev/null; then
            docker-compose up -d
            
            # Wait for services to be ready
            log_info "Waiting for services to be ready..."
            sleep 15
            
            # Run e2e tests
            cd tests/e2e
            npm test || pytest . -v
            
            # Stop services
            cd "$PROJECT_ROOT"
            docker-compose down
        else
            log_warn "Docker Compose not available. Please start services manually."
        fi
    else
        log_warn "No end-to-end tests found"
    fi
}

generate_test_report() {
    log_step "Generating Test Report"
    
    REPORT_DIR="$PROJECT_ROOT/test-reports"
    mkdir -p "$REPORT_DIR"
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    REPORT_FILE="$REPORT_DIR/test_report_$TIMESTAMP.txt"
    
    {
        echo "AssistGen Test Report"
        echo "Generated: $(date)"
        echo "================================"
        echo ""
        
        if [ "$RUN_BACKEND" = true ]; then
            echo "Backend Tests:"
            if [ -f "$PROJECT_ROOT/backend/.coverage" ]; then
                cd "$PROJECT_ROOT/backend"
                source venv/bin/activate
                coverage report
            fi
            echo ""
        fi
        
        if [ "$RUN_FRONTEND" = true ]; then
            echo "Frontend Tests:"
            if [ -f "$PROJECT_ROOT/frontend/coverage/coverage-summary.json" ]; then
                cat "$PROJECT_ROOT/frontend/coverage/coverage-summary.json"
            fi
            echo ""
        fi
    } > "$REPORT_FILE"
    
    log_info "Test report saved to: $REPORT_FILE"
}

check_test_environment() {
    log_info "Checking test environment..."
    
    # Check if backend dependencies are installed
    if [ "$RUN_BACKEND" = true ]; then
        if [ ! -d "$PROJECT_ROOT/backend/venv" ]; then
            log_error "Backend virtual environment not found"
            log_info "Run: ./scripts/setup_dev.sh"
            exit 1
        fi
    fi
    
    # Check if frontend dependencies are installed
    if [ "$RUN_FRONTEND" = true ]; then
        if [ ! -d "$PROJECT_ROOT/frontend/node_modules" ]; then
            log_error "Frontend dependencies not installed"
            log_info "Run: cd frontend && npm install"
            exit 1
        fi
    fi
    
    log_info "Test environment check passed"
}

###############################################################################
# Main Test Flow
###############################################################################

main() {
    log_info "Starting AssistGen test suite..."
    log_info "Project root: $PROJECT_ROOT"
    
    # Check environment
    check_test_environment
    
    # Track test results
    TESTS_PASSED=true
    
    # Run backend tests
    if [ "$RUN_BACKEND" = true ]; then
        if [ "$RUN_UNIT" = true ]; then
            run_backend_unit_tests || TESTS_PASSED=false
        fi
        
        if [ "$RUN_INTEGRATION" = true ]; then
            run_backend_integration_tests || TESTS_PASSED=false
        fi
    fi
    
    # Run frontend tests
    if [ "$RUN_FRONTEND" = true ]; then
        if [ "$RUN_UNIT" = true ]; then
            run_frontend_unit_tests || TESTS_PASSED=false
        fi
    fi
    
    # Run e2e tests
    if [ "$RUN_E2E" = true ]; then
        run_e2e_tests || TESTS_PASSED=false
    fi
    
    # Generate report
    if [ "$GENERATE_COVERAGE" = true ]; then
        generate_test_report
    fi
    
    # Summary
    echo ""
    if [ "$TESTS_PASSED" = true ]; then
        log_info "All tests passed! ✓"
        exit 0
    else
        log_error "Some tests failed ✗"
        exit 1
    fi
}

# Run main function
main
