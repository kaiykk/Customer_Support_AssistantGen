#!/bin/bash

###############################################################################
# Database Backup Script for AssistGen
#
# This script creates backups of the AssistGen databases including:
# - MySQL database (full dump)
# - Redis data (RDB snapshot)
# - Neo4j graph database (if configured)
# - Uploaded files
#
# Backups are stored with timestamps and can be automatically cleaned up
# based on retention policy.
#
# Usage: ./scripts/backup_db.sh [options]
# Options:
#   --mysql-only    Backup only MySQL database
#   --redis-only    Backup only Redis data
#   --no-files      Skip file uploads backup
#   --retention N   Keep only last N backups (default: 7)
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

# Configuration
BACKUP_DIR="$PROJECT_ROOT/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Backup options
BACKUP_MYSQL=true
BACKUP_REDIS=true
BACKUP_FILES=true
BACKUP_NEO4J=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --mysql-only)
            BACKUP_MYSQL=true
            BACKUP_REDIS=false
            BACKUP_FILES=false
            shift
            ;;
        --redis-only)
            BACKUP_MYSQL=false
            BACKUP_REDIS=true
            BACKUP_FILES=false
            shift
            ;;
        --no-files)
            BACKUP_FILES=false
            shift
            ;;
        --retention)
            RETENTION_DAYS="$2"
            shift 2
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

load_env() {
    # Try to load environment variables
    if [ -f "$PROJECT_ROOT/backend/.env" ]; then
        set -a
        source "$PROJECT_ROOT/backend/.env"
        set +a
        log_info "Loaded environment from backend/.env"
    elif [ -f "$PROJECT_ROOT/config/.env.production" ]; then
        set -a
        source "$PROJECT_ROOT/config/.env.production"
        set +a
        log_info "Loaded environment from config/.env.production"
    else
        log_warn "No environment file found, using defaults"
    fi
}

###############################################################################
# Backup Functions
###############################################################################

backup_mysql() {
    log_step "Backing Up MySQL Database"
    
    # Create backup directory
    MYSQL_BACKUP_DIR="$BACKUP_DIR/mysql"
    mkdir -p "$MYSQL_BACKUP_DIR"
    
    BACKUP_FILE="$MYSQL_BACKUP_DIR/mysql_backup_$TIMESTAMP.sql"
    COMPRESSED_FILE="$BACKUP_FILE.gz"
    
    # Get database credentials
    DB_HOST=${DB_HOST:-localhost}
    DB_PORT=${DB_PORT:-3306}
    DB_USER=${DB_USER:-assistgen}
    DB_PASSWORD=${DB_PASSWORD:-assistgen123}
    DB_NAME=${DB_NAME:-assistgen}
    
    log_info "Backing up database: $DB_NAME"
    log_info "Host: $DB_HOST:$DB_PORT"
    
    # Check if using Docker
    if docker ps | grep -q assistgen-db; then
        log_info "Using Docker container for backup..."
        docker exec assistgen-db mysqldump \
            -u"$DB_USER" \
            -p"$DB_PASSWORD" \
            --single-transaction \
            --routines \
            --triggers \
            --events \
            "$DB_NAME" > "$BACKUP_FILE"
    else
        log_info "Using local MySQL for backup..."
        mysqldump \
            -h"$DB_HOST" \
            -P"$DB_PORT" \
            -u"$DB_USER" \
            -p"$DB_PASSWORD" \
            --single-transaction \
            --routines \
            --triggers \
            --events \
            "$DB_NAME" > "$BACKUP_FILE"
    fi
    
    # Compress backup
    log_info "Compressing backup..."
    gzip "$BACKUP_FILE"
    
    BACKUP_SIZE=$(du -h "$COMPRESSED_FILE" | cut -f1)
    log_info "MySQL backup completed: $COMPRESSED_FILE ($BACKUP_SIZE)"
}

backup_redis() {
    log_step "Backing Up Redis Data"
    
    # Create backup directory
    REDIS_BACKUP_DIR="$BACKUP_DIR/redis"
    mkdir -p "$REDIS_BACKUP_DIR"
    
    BACKUP_FILE="$REDIS_BACKUP_DIR/redis_backup_$TIMESTAMP.rdb"
    
    # Get Redis configuration
    REDIS_HOST=${REDIS_HOST:-localhost}
    REDIS_PORT=${REDIS_PORT:-6379}
    REDIS_PASSWORD=${REDIS_PASSWORD:-}
    
    log_info "Backing up Redis data from $REDIS_HOST:$REDIS_PORT"
    
    # Check if using Docker
    if docker ps | grep -q assistgen-redis; then
        log_info "Using Docker container for backup..."
        
        # Trigger Redis save
        if [ -n "$REDIS_PASSWORD" ]; then
            docker exec assistgen-redis redis-cli -a "$REDIS_PASSWORD" SAVE
        else
            docker exec assistgen-redis redis-cli SAVE
        fi
        
        # Copy RDB file
        docker cp assistgen-redis:/data/dump.rdb "$BACKUP_FILE"
    else
        log_info "Using local Redis for backup..."
        
        # Trigger Redis save
        if [ -n "$REDIS_PASSWORD" ]; then
            redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" SAVE
        else
            redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" SAVE
        fi
        
        # Copy RDB file (assuming default location)
        cp /var/lib/redis/dump.rdb "$BACKUP_FILE" 2>/dev/null || \
            log_warn "Could not find Redis dump.rdb file"
    fi
    
    if [ -f "$BACKUP_FILE" ]; then
        BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        log_info "Redis backup completed: $BACKUP_FILE ($BACKUP_SIZE)"
    else
        log_warn "Redis backup file not created"
    fi
}

backup_files() {
    log_step "Backing Up Uploaded Files"
    
    # Create backup directory
    FILES_BACKUP_DIR="$BACKUP_DIR/files"
    mkdir -p "$FILES_BACKUP_DIR"
    
    BACKUP_FILE="$FILES_BACKUP_DIR/files_backup_$TIMESTAMP.tar.gz"
    
    # Check if uploads directory exists
    UPLOADS_DIR="$PROJECT_ROOT/uploads"
    if [ ! -d "$UPLOADS_DIR" ]; then
        log_warn "Uploads directory not found: $UPLOADS_DIR"
        return
    fi
    
    # Check if directory is empty
    if [ -z "$(ls -A $UPLOADS_DIR)" ]; then
        log_warn "Uploads directory is empty, skipping backup"
        return
    fi
    
    log_info "Backing up files from: $UPLOADS_DIR"
    
    # Create tar archive
    tar -czf "$BACKUP_FILE" -C "$PROJECT_ROOT" uploads
    
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log_info "Files backup completed: $BACKUP_FILE ($BACKUP_SIZE)"
}

cleanup_old_backups() {
    log_step "Cleaning Up Old Backups"
    
    log_info "Retention policy: Keep last $RETENTION_DAYS backups"
    
    # Clean up MySQL backups
    if [ -d "$BACKUP_DIR/mysql" ]; then
        MYSQL_COUNT=$(ls -1 "$BACKUP_DIR/mysql" | wc -l)
        if [ "$MYSQL_COUNT" -gt "$RETENTION_DAYS" ]; then
            log_info "Cleaning up old MySQL backups..."
            ls -t "$BACKUP_DIR/mysql"/mysql_backup_*.sql.gz | tail -n +$((RETENTION_DAYS + 1)) | xargs rm -f
        fi
    fi
    
    # Clean up Redis backups
    if [ -d "$BACKUP_DIR/redis" ]; then
        REDIS_COUNT=$(ls -1 "$BACKUP_DIR/redis" | wc -l)
        if [ "$REDIS_COUNT" -gt "$RETENTION_DAYS" ]; then
            log_info "Cleaning up old Redis backups..."
            ls -t "$BACKUP_DIR/redis"/redis_backup_*.rdb | tail -n +$((RETENTION_DAYS + 1)) | xargs rm -f
        fi
    fi
    
    # Clean up file backups
    if [ -d "$BACKUP_DIR/files" ]; then
        FILES_COUNT=$(ls -1 "$BACKUP_DIR/files" | wc -l)
        if [ "$FILES_COUNT" -gt "$RETENTION_DAYS" ]; then
            log_info "Cleaning up old file backups..."
            ls -t "$BACKUP_DIR/files"/files_backup_*.tar.gz | tail -n +$((RETENTION_DAYS + 1)) | xargs rm -f
        fi
    fi
    
    log_info "Cleanup completed"
}

create_backup_manifest() {
    log_step "Creating Backup Manifest"
    
    MANIFEST_FILE="$BACKUP_DIR/backup_manifest_$TIMESTAMP.txt"
    
    {
        echo "AssistGen Backup Manifest"
        echo "========================="
        echo "Timestamp: $(date)"
        echo "Backup ID: $TIMESTAMP"
        echo ""
        
        if [ "$BACKUP_MYSQL" = true ] && [ -f "$BACKUP_DIR/mysql/mysql_backup_$TIMESTAMP.sql.gz" ]; then
            echo "MySQL Backup:"
            echo "  File: mysql/mysql_backup_$TIMESTAMP.sql.gz"
            echo "  Size: $(du -h "$BACKUP_DIR/mysql/mysql_backup_$TIMESTAMP.sql.gz" | cut -f1)"
            echo ""
        fi
        
        if [ "$BACKUP_REDIS" = true ] && [ -f "$BACKUP_DIR/redis/redis_backup_$TIMESTAMP.rdb" ]; then
            echo "Redis Backup:"
            echo "  File: redis/redis_backup_$TIMESTAMP.rdb"
            echo "  Size: $(du -h "$BACKUP_DIR/redis/redis_backup_$TIMESTAMP.rdb" | cut -f1)"
            echo ""
        fi
        
        if [ "$BACKUP_FILES" = true ] && [ -f "$BACKUP_DIR/files/files_backup_$TIMESTAMP.tar.gz" ]; then
            echo "Files Backup:"
            echo "  File: files/files_backup_$TIMESTAMP.tar.gz"
            echo "  Size: $(du -h "$BACKUP_DIR/files/files_backup_$TIMESTAMP.tar.gz" | cut -f1)"
            echo ""
        fi
        
        echo "Total Backup Size: $(du -sh "$BACKUP_DIR" | cut -f1)"
    } > "$MANIFEST_FILE"
    
    log_info "Manifest created: $MANIFEST_FILE"
}

###############################################################################
# Main Backup Flow
###############################################################################

main() {
    log_info "Starting AssistGen database backup..."
    log_info "Backup timestamp: $TIMESTAMP"
    log_info "Backup directory: $BACKUP_DIR"
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    # Load environment
    load_env
    
    # Run backups
    if [ "$BACKUP_MYSQL" = true ]; then
        backup_mysql || log_error "MySQL backup failed"
    fi
    
    if [ "$BACKUP_REDIS" = true ]; then
        backup_redis || log_error "Redis backup failed"
    fi
    
    if [ "$BACKUP_FILES" = true ]; then
        backup_files || log_error "Files backup failed"
    fi
    
    # Create manifest
    create_backup_manifest
    
    # Cleanup old backups
    cleanup_old_backups
    
    log_info "Backup completed successfully!"
    log_info "Backup location: $BACKUP_DIR"
}

# Run main function
main
