# Deployment Guide

This guide covers deploying AssistGen to various environments including development, staging, and production.

## System Requirements

### Minimum Requirements

- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disk**: 20 GB SSD
- **OS**: Linux (Ubuntu 20.04+), macOS, Windows Server

### Recommended Requirements (Production)

- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Disk**: 50+ GB SSD
- **OS**: Linux (Ubuntu 22.04 LTS)
- **Network**: 100 Mbps+

### Software Dependencies

- **Python**: 3.11 or higher
- **Node.js**: 18 or higher
- **MySQL**: 8.0+ or PostgreSQL 13+
- **Redis**: 6.0+ (optional, for caching)
- **Nginx**: 1.18+ (for reverse proxy)

## Deployment Methods

### Method 1: Docker Compose (Recommended)

Easiest way to deploy with all dependencies.

#### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

#### Steps

1. **Clone repository**
```bash
git clone https://github.com/assistgen/assistgen.git
cd assistgen/assistgen-refactored
```

2. **Configure environment**
```bash
cp config/production.env.example .env
# Edit .env with your configuration
```

3. **Build and start services**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

4. **Initialize database**
```bash
docker-compose exec backend alembic upgrade head
```

5. **Verify deployment**
```bash
curl http://localhost:8000/health
```

#### Docker Compose Services

- **backend**: FastAPI application
- **frontend**: Nginx serving Vue app
- **database**: MySQL 8.0
- **redis**: Redis cache (optional)

---

### Method 2: Manual Deployment

For custom setups or when Docker is not available.

#### Backend Deployment

1. **Install Python dependencies**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp ../config/production.env.example .env
# Edit .env with your configuration
```

3. **Initialize database**
```bash
alembic upgrade head
```

4. **Start application**
```bash
# Development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production (with Gunicorn)
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

#### Frontend Deployment

1. **Install Node dependencies**
```bash
cd frontend
npm install
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with API URL
```

3. **Build for production**
```bash
npm run build
```

4. **Serve with Nginx**
```bash
# Copy build files to web root
sudo cp -r dist/* /var/www/assistgen/

# Configure Nginx (see Nginx configuration below)
sudo systemctl restart nginx
```

---

### Method 3: Cloud Platform Deployment

#### AWS Deployment

**Services Used**:
- **EC2**: Application servers
- **RDS**: MySQL database
- **S3**: File storage
- **CloudFront**: CDN for frontend
- **ALB**: Load balancer
- **ElastiCache**: Redis cache

**Deployment Steps**:

1. **Create RDS MySQL instance**
2. **Create ElastiCache Redis cluster**
3. **Create S3 bucket for uploads**
4. **Launch EC2 instances with Auto Scaling**
5. **Configure ALB with health checks**
6. **Deploy application using CodeDeploy**
7. **Configure CloudFront for frontend**

#### Heroku Deployment

```bash
# Login to Heroku
heroku login

# Create app
heroku create assistgen-app

# Add MySQL addon
heroku addons:create jawsdb:kitefin

# Add Redis addon
heroku addons:create heroku-redis:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY=your_secret_key
heroku config:set DEEPSEEK_API_KEY=your_api_key

# Deploy
git push heroku main

# Run migrations
heroku run alembic upgrade head
```

#### DigitalOcean App Platform

```yaml
# app.yaml
name: assistgen
services:
  - name: backend
    github:
      repo: assistgen/assistgen
      branch: main
      deploy_on_push: true
    build_command: pip install -r requirements.txt
    run_command: gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
    envs:
      - key: DATABASE_URL
        scope: RUN_TIME
        value: ${db.DATABASE_URL}
    
  - name: frontend
    github:
      repo: assistgen/assistgen
      branch: main
    build_command: npm run build
    routes:
      - path: /
    
databases:
  - name: db
    engine: MYSQL
    version: "8"
```

## Configuration

### Environment Variables

Create `.env` file with these variables:

```bash
# Application
APP_NAME=AssistGen
APP_ENV=production
DEBUG=false
SECRET_KEY=your-secret-key-here-min-32-chars

# Database
DATABASE_URL=mysql+aiomysql://user:pass@localhost:3306/assistgen

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# LLM Configuration
CHAT_SERVICE=DEEPSEEK
DEEPSEEK_API_KEY=your-deepseek-api-key
OLLAMA_BASE_URL=http://localhost:11434

# CORS
CORS_ORIGINS=https://assistgen.example.com

# Security
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=true
LOG_DIR=logs
```

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/assistgen

upstream backend {
    server 127.0.0.1:8000;
    # Add more servers for load balancing
    # server 127.0.0.1:8001;
    # server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name assistgen.example.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name assistgen.example.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/assistgen.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/assistgen.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Frontend (Vue app)
    location / {
        root /var/www/assistgen;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # API documentation
    location /docs {
        proxy_pass http://backend/docs;
    }
    
    # Health check
    location /health {
        proxy_pass http://backend/health;
        access_log off;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/assistgen /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Database Setup

### MySQL Setup

```bash
# Install MySQL
sudo apt-get update
sudo apt-get install mysql-server

# Secure installation
sudo mysql_secure_installation

# Create database and user
sudo mysql -u root -p
```

```sql
CREATE DATABASE assistgen CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'assistgen'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON assistgen.* TO 'assistgen'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### PostgreSQL Setup

```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
```

```sql
CREATE DATABASE assistgen;
CREATE USER assistgen WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE assistgen TO assistgen;
\q
```

### Run Migrations

```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

## SSL/TLS Certificate

### Using Let's Encrypt (Free)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d assistgen.example.com

# Auto-renewal (already configured by certbot)
sudo certbot renew --dry-run
```

### Using Custom Certificate

```nginx
ssl_certificate /path/to/certificate.crt;
ssl_certificate_key /path/to/private.key;
```

## Process Management

### Using Systemd (Linux)

Create service file `/etc/systemd/system/assistgen.service`:

```ini
[Unit]
Description=AssistGen Backend Service
After=network.target mysql.service

[Service]
Type=notify
User=assistgen
Group=assistgen
WorkingDirectory=/opt/assistgen/backend
Environment="PATH=/opt/assistgen/backend/venv/bin"
ExecStart=/opt/assistgen/backend/venv/bin/gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable assistgen
sudo systemctl start assistgen
sudo systemctl status assistgen
```

### Using Supervisor

Install Supervisor:
```bash
sudo apt-get install supervisor
```

Create config `/etc/supervisor/conf.d/assistgen.conf`:
```ini
[program:assistgen]
command=/opt/assistgen/backend/venv/bin/gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
directory=/opt/assistgen/backend
user=assistgen
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/assistgen/app.log
```

Start service:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start assistgen
```

## Backup Procedures

### Database Backup

**Daily automated backup**:

Create `/opt/assistgen/scripts/backup_db.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/opt/assistgen/backups"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="assistgen_${DATE}.sql"

# Create backup
mysqldump -u assistgen -p$DB_PASSWORD assistgen > "${BACKUP_DIR}/${FILENAME}"

# Compress backup
gzip "${BACKUP_DIR}/${FILENAME}"

# Delete backups older than 30 days
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: ${FILENAME}.gz"
```

Make executable and add to cron:
```bash
chmod +x /opt/assistgen/scripts/backup_db.sh

# Add to crontab (daily at 2 AM)
crontab -e
0 2 * * * /opt/assistgen/scripts/backup_db.sh
```

### File Backup

Backup uploaded files:
```bash
# Sync to S3
aws s3 sync /opt/assistgen/uploads s3://assistgen-backups/uploads/

# Or use rsync to remote server
rsync -avz /opt/assistgen/uploads/ backup-server:/backups/assistgen/
```

### Restore Procedures

**Restore database**:
```bash
# Decompress backup
gunzip assistgen_20240101_020000.sql.gz

# Restore to database
mysql -u assistgen -p assistgen < assistgen_20240101_020000.sql
```

**Restore files**:
```bash
# From S3
aws s3 sync s3://assistgen-backups/uploads/ /opt/assistgen/uploads/

# From remote server
rsync -avz backup-server:/backups/assistgen/ /opt/assistgen/uploads/
```

## Monitoring Setup

### Health Checks

AssistGen provides health check endpoints:

```bash
# Application health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/health/db

# Redis health (if configured)
curl http://localhost:8000/health/redis
```

### Uptime Monitoring

Use services like:
- **UptimeRobot**: Free tier available
- **Pingdom**: Comprehensive monitoring
- **StatusCake**: Multiple check locations

Configure alerts for:
- HTTP 5xx errors
- Response time > 2 seconds
- Service downtime

### Application Monitoring

#### Using Prometheus + Grafana

1. **Install Prometheus exporter**
```bash
pip install prometheus-fastapi-instrumentator
```

2. **Add to application**
```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

3. **Configure Prometheus** (`prometheus.yml`)
```yaml
scrape_configs:
  - job_name: 'assistgen'
    static_configs:
      - targets: ['localhost:8000']
```

4. **Create Grafana dashboard** for metrics visualization

## Scaling Strategies

### Horizontal Scaling

Add more application servers behind a load balancer:

```
                    ┌─────────────┐
                    │Load Balancer│
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌─────▼────┐      ┌─────▼────┐
   │ Server 1│       │ Server 2 │      │ Server 3 │
   └─────────┘       └──────────┘      └──────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Database   │
                    └─────────────┘
```

**Steps**:
1. Deploy application to multiple servers
2. Configure load balancer (Nginx, HAProxy, AWS ALB)
3. Use shared database and Redis
4. Enable session persistence if needed

### Vertical Scaling

Increase resources on existing server:

1. **Increase worker processes**
```bash
gunicorn main:app --workers 8  # Increase from 4 to 8
```

2. **Optimize database**
```sql
-- Increase connection pool
SET GLOBAL max_connections = 200;

-- Increase buffer pool (MySQL)
SET GLOBAL innodb_buffer_pool_size = 2G;
```

3. **Add more RAM/CPU** to server

### Database Scaling

#### Read Replicas

For read-heavy workloads:

```python
# Configure read/write splitting
SQLALCHEMY_DATABASE_URI = "mysql://master:3306/assistgen"
SQLALCHEMY_BINDS = {
    'read': "mysql://replica:3306/assistgen"
}

# Use read replica for queries
@app.get("/conversations")
async def get_conversations(db: Session = Depends(get_read_db)):
    ...
```

#### Caching Layer

Add Redis caching:

```python
import redis

cache = redis.Redis(host='localhost', port=6379, db=0)

@app.get("/conversations")
async def get_conversations(user_id: int):
    # Check cache first
    cached = cache.get(f"conversations:{user_id}")
    if cached:
        return json.loads(cached)
    
    # Query database
    conversations = await ConversationService.get_user_conversations(user_id)
    
    # Cache result (5 minute TTL)
    cache.setex(
        f"conversations:{user_id}",
        300,
        json.dumps(conversations)
    )
    
    return conversations
```

## Security Hardening

### Application Security

1. **Use environment variables** for secrets
2. **Enable HTTPS** only (no HTTP)
3. **Set secure headers** (already configured in middleware)
4. **Implement rate limiting** (already configured)
5. **Validate all inputs** (Pydantic schemas)
6. **Use prepared statements** (SQLAlchemy ORM)

### Server Security

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade

# Configure firewall
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# Disable root SSH login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# Install fail2ban
sudo apt-get install fail2ban
sudo systemctl enable fail2ban
```

### Database Security

```sql
-- Remove anonymous users
DELETE FROM mysql.user WHERE User='';

-- Remove test database
DROP DATABASE IF EXISTS test;

-- Require SSL connections
GRANT ALL PRIVILEGES ON assistgen.* TO 'assistgen'@'%' REQUIRE SSL;

-- Set strong password policy
SET GLOBAL validate_password.policy = STRONG;
```

## Troubleshooting

### Application Won't Start

**Check logs**:
```bash
# Systemd service
sudo journalctl -u assistgen -n 50

# Docker
docker-compose logs backend

# Manual deployment
tail -f logs/assistgen.log
```

**Common issues**:
- Missing environment variables
- Database connection failure
- Port already in use
- Permission issues

### Database Connection Errors

**Check database status**:
```bash
sudo systemctl status mysql
```

**Test connection**:
```bash
mysql -u assistgen -p -h localhost assistgen
```

**Check connection string** in `.env`:
```bash
# Correct format
DATABASE_URL=mysql+aiomysql://user:pass@host:port/database
```

### High Memory Usage

**Check process memory**:
```bash
ps aux | grep gunicorn
```

**Reduce workers**:
```bash
# Reduce from 4 to 2 workers
gunicorn main:app --workers 2 ...
```

**Enable memory profiling**:
```python
import tracemalloc
tracemalloc.start()
```

### Slow Response Times

**Check database queries**:
```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;

-- View slow queries
SELECT * FROM mysql.slow_log ORDER BY start_time DESC LIMIT 10;
```

**Add caching**:
- Cache user profiles
- Cache conversation lists
- Cache frequently accessed data

**Optimize queries**:
- Add missing indexes
- Use pagination
- Avoid N+1 queries

## Rollback Procedures

### Application Rollback

**Docker deployment**:
```bash
# Rollback to previous version
docker-compose down
git checkout previous-tag
docker-compose up -d
```

**Manual deployment**:
```bash
# Stop service
sudo systemctl stop assistgen

# Checkout previous version
git checkout previous-tag

# Restart service
sudo systemctl start assistgen
```

### Database Rollback

```bash
# Downgrade one migration
alembic downgrade -1

# Downgrade to specific version
alembic downgrade abc123

# Restore from backup
mysql -u assistgen -p assistgen < backup_20240101.sql
```

## Performance Tuning

### Application Tuning

```bash
# Optimal worker count: (2 x CPU cores) + 1
gunicorn main:app --workers 9  # For 4-core server

# Increase worker timeout for slow LLM responses
gunicorn main:app --timeout 120

# Use gevent for better concurrency
gunicorn main:app --worker-class gevent --workers 4
```

### Database Tuning

**MySQL configuration** (`/etc/mysql/my.cnf`):
```ini
[mysqld]
# Connection settings
max_connections = 200
wait_timeout = 600

# Buffer pool (set to 70% of RAM)
innodb_buffer_pool_size = 4G

# Log settings
slow_query_log = 1
long_query_time = 1

# Performance
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT
```

Restart MySQL:
```bash
sudo systemctl restart mysql
```

## Disaster Recovery

### Recovery Time Objective (RTO)

Target: 1 hour

### Recovery Point Objective (RPO)

Target: 15 minutes (with frequent backups)

### Disaster Recovery Plan

1. **Detect failure** (monitoring alerts)
2. **Assess impact** (what's affected?)
3. **Notify stakeholders** (users, team)
4. **Restore from backup** (database, files)
5. **Verify functionality** (run health checks)
6. **Resume operations** (enable traffic)
7. **Post-mortem** (document incident)

## Maintenance Windows

Schedule regular maintenance:

- **Weekly**: Security updates
- **Monthly**: Database optimization
- **Quarterly**: Major updates

Notify users in advance:
```bash
# Display maintenance banner
curl -X POST http://localhost:8000/admin/maintenance \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"enabled": true, "message": "Scheduled maintenance in 1 hour"}'
```

## Support and Resources

- **Documentation**: https://docs.assistgen.example.com
- **Status Page**: https://status.assistgen.example.com
- **Support Email**: support@assistgen.example.com
- **GitHub Issues**: https://github.com/assistgen/assistgen/issues
