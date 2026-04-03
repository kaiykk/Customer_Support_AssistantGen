# AssistGen Scripts Documentation

This directory contains utility scripts for development, testing, deployment, and maintenance of the AssistGen application.

## Available Scripts

### 1. setup_dev.sh - Development Environment Setup

Sets up a complete development environment including dependencies, configuration, and databases.

**Usage:**
```bash
./scripts/setup_dev.sh
```

**What it does:**
- Checks system prerequisites (Python, Node.js, Docker)
- Creates Python virtual environment
- Installs backend dependencies
- Installs frontend dependencies
- Creates configuration files from examples
- Starts database services (MySQL, Redis) via Docker
- Optionally runs tests

**Prerequisites:**
- Python 3.11+
- Node.js 16+
- Docker and Docker Compose (optional but recommended)

**First-time setup:**
```bash
# Clone the repository
cd assistgen-refactored

# Run setup script
./scripts/setup_dev.sh

# Follow the prompts and update configuration files
# Edit backend/.env with your API keys and credentials
# Edit frontend/.env with your configuration
```

---

### 2. run_tests.sh - Test Execution

Runs all tests for the AssistGen project with various options.

**Usage:**
```bash
# Run all tests
./scripts/run_tests.sh

# Run only unit tests
./scripts/run_tests.sh --unit

# Run only integration tests
./scripts/run_tests.sh --integration

# Run only backend tests
./scripts/run_tests.sh --backend

# Run only frontend tests
./scripts/run_tests.sh --frontend

# Run with coverage report
./scripts/run_tests.sh --coverage

# Run end-to-end tests
./scripts/run_tests.sh --e2e
```

**Options:**
- `--unit` - Run only unit tests
- `--integration` - Run only integration tests
- `--e2e` - Run only end-to-end tests
- `--backend` - Run only backend tests
- `--frontend` - Run only frontend tests
- `--coverage` - Generate coverage reports

**Examples:**
```bash
# Run backend unit tests with coverage
./scripts/run_tests.sh --backend --unit --coverage

# Run all frontend tests
./scripts/run_tests.sh --frontend

# Run integration tests only
./scripts/run_tests.sh --integration
```

**Output:**
- Test results displayed in terminal
- Coverage reports in `backend/htmlcov/` and `frontend/coverage/`
- Test reports in `test-reports/` directory

---

### 3. deploy.sh - Production Deployment

Handles production deployment with Docker Compose including validation, backup, and health checks.

**Usage:**
```bash
# Full deployment
./scripts/deploy.sh

# Skip Docker image building
./scripts/deploy.sh --skip-build

# Skip database migrations
./scripts/deploy.sh --skip-migrate

# Rollback to previous deployment
./scripts/deploy.sh --rollback
```

**Options:**
- `--skip-build` - Skip Docker image building (use existing images)
- `--skip-migrate` - Skip database migrations
- `--rollback` - Rollback to previous deployment from backup

**What it does:**
1. Checks prerequisites (Docker, Docker Compose)
2. Validates configuration (environment variables)
3. Creates backup of current deployment
4. Builds Docker images (unless --skip-build)
5. Deploys services using Docker Compose
6. Runs database migrations (unless --skip-migrate)
7. Performs health checks
8. Shows deployment status

**Prerequisites:**
- Docker and Docker Compose installed
- `config/.env.production` file configured
- All required environment variables set

**Before first deployment:**
```bash
# Create production environment file
cp config/production.env.example config/.env.production

# Edit with production values
nano config/.env.production

# Ensure strong passwords and API keys are set
# Never use default values in production!

# Run deployment
./scripts/deploy.sh
```

**Rollback procedure:**
```bash
# If deployment fails or issues are detected
./scripts/deploy.sh --rollback
```

---

### 4. backup_db.sh - Database Backup

Creates backups of databases and uploaded files with automatic cleanup.

**Usage:**
```bash
# Backup everything
./scripts/backup_db.sh

# Backup only MySQL
./scripts/backup_db.sh --mysql-only

# Backup only Redis
./scripts/backup_db.sh --redis-only

# Skip file uploads backup
./scripts/backup_db.sh --no-files

# Custom retention (keep last 14 backups)
./scripts/backup_db.sh --retention 14
```

**Options:**
- `--mysql-only` - Backup only MySQL database
- `--redis-only` - Backup only Redis data
- `--no-files` - Skip uploaded files backup
- `--retention N` - Keep only last N backups (default: 7)

**What it backs up:**
- MySQL database (full dump with routines, triggers, events)
- Redis data (RDB snapshot)
- Uploaded files (tar.gz archive)

**Backup location:**
```
backups/
├── mysql/
│   └── mysql_backup_YYYYMMDD_HHMMSS.sql.gz
├── redis/
│   └── redis_backup_YYYYMMDD_HHMMSS.rdb
├── files/
│   └── files_backup_YYYYMMDD_HHMMSS.tar.gz
└── backup_manifest_YYYYMMDD_HHMMSS.txt
```

**Automated backups:**
```bash
# Add to crontab for daily backups at 2 AM
0 2 * * * /path/to/assistgen-refactored/scripts/backup_db.sh

# Weekly backups with longer retention
0 3 * * 0 /path/to/assistgen-refactored/scripts/backup_db.sh --retention 30
```

**Restore from backup:**
```bash
# Restore MySQL
gunzip < backups/mysql/mysql_backup_YYYYMMDD_HHMMSS.sql.gz | \
  mysql -u username -p database_name

# Restore Redis
cp backups/redis/redis_backup_YYYYMMDD_HHMMSS.rdb /var/lib/redis/dump.rdb
systemctl restart redis

# Restore files
tar -xzf backups/files/files_backup_YYYYMMDD_HHMMSS.tar.gz
```

---

## Python Analysis Scripts

### analyze_backend.py

Analyzes backend Python code for quality issues, missing documentation, and code smells.

**Usage:**
```bash
cd assistgen-refactored
python scripts/analyze_backend.py
```

**Output:**
- JSON report: `docs/analysis/backend_analysis_report.json`
- Markdown summary: `docs/analysis/backend_analysis_summary.md`

---

### analyze_frontend.py

Analyzes frontend Vue.js code for UI/UX issues, accessibility problems, and code quality.

**Usage:**
```bash
cd assistgen-refactored
python scripts/analyze_frontend.py
```

**Output:**
- JSON report: `docs/analysis/frontend_analysis_report.json`
- Markdown summary: `docs/analysis/frontend_analysis_summary.md`

---

### validate_quality.py

Validates code quality standards including PEP 8, type hints, error handling, and security.

**Usage:**
```bash
cd assistgen-refactored
python scripts/validate_quality.py
```

**Output:**
- JSON report: `docs/quality/quality_report.json`
- Markdown report: `docs/quality/quality_report.md`
- Console output with pass/fail status

---

## Common Workflows

### Initial Development Setup
```bash
# 1. Set up development environment
./scripts/setup_dev.sh

# 2. Update configuration files
nano backend/.env
nano frontend/.env

# 3. Run tests to verify setup
./scripts/run_tests.sh

# 4. Start development servers
cd backend && source venv/bin/activate && uvicorn main:app --reload
cd frontend && npm run dev
```

### Before Committing Code
```bash
# 1. Run quality validation
python scripts/validate_quality.py

# 2. Run all tests
./scripts/run_tests.sh --coverage

# 3. Check test coverage
# Backend: open backend/htmlcov/index.html
# Frontend: open frontend/coverage/index.html
```

### Production Deployment
```bash
# 1. Create backup
./scripts/backup_db.sh

# 2. Run tests in staging
./scripts/run_tests.sh

# 3. Deploy to production
./scripts/deploy.sh

# 4. Monitor logs
docker-compose -f docker-compose.prod.yml logs -f

# 5. If issues occur, rollback
./scripts/deploy.sh --rollback
```

### Regular Maintenance
```bash
# Daily: Automated backup (via cron)
0 2 * * * /path/to/scripts/backup_db.sh

# Weekly: Run quality checks
python scripts/validate_quality.py

# Monthly: Clean up old backups
./scripts/backup_db.sh --retention 30
```

---

## Troubleshooting

### Script Permission Denied
```bash
# Make scripts executable (Linux/Mac)
chmod +x scripts/*.sh

# On Windows, use Git Bash or WSL
```

### Docker Not Found
```bash
# Install Docker
# See: https://docs.docker.com/get-docker/

# Install Docker Compose
# See: https://docs.docker.com/compose/install/
```

### Python Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf backend/venv
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
```

### Database Connection Failed
```bash
# Check if services are running
docker-compose ps

# Restart services
docker-compose restart database redis

# Check logs
docker-compose logs database
docker-compose logs redis
```

### Test Failures
```bash
# Run tests with verbose output
./scripts/run_tests.sh --backend --unit -v

# Check test logs
cat test-reports/test_report_*.txt

# Run specific test file
cd backend
source venv/bin/activate
pytest tests/unit/test_specific.py -v
```

---

## Script Maintenance

### Adding New Scripts

When adding new scripts:
1. Add shebang line: `#!/bin/bash`
2. Add comprehensive header documentation
3. Include usage examples
4. Add error handling with `set -e`
5. Use color-coded output
6. Make executable: `chmod +x scripts/new_script.sh`
7. Update this README

### Script Standards

All scripts should follow these standards:
- Use bash for shell scripts
- Include comprehensive error handling
- Provide clear, color-coded output
- Include help/usage information
- Log important operations
- Clean up temporary files
- Return appropriate exit codes

---

## Additional Resources

- [Deployment Documentation](../docs/deployment/README.md)
- [Testing Documentation](../docs/testing/README.md)
- [Configuration Guide](../config/README.md)
- [Migration Guide](../docs/migration/README.md)

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the main documentation in `docs/`
3. Check the integration notes in `INTEGRATION_NOTES.md`
4. Contact the development team
