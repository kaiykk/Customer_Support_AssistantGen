# Database Documentation

This document describes the database schema, relationships, and operations for the AssistGen application.

## Database Technology

- **Primary Database**: MySQL 8.0+ or PostgreSQL 13+
- **ORM**: SQLAlchemy 2.0 (async)
- **Migration Tool**: Alembic
- **Connection Pooling**: Built-in SQLAlchemy pooling

## Database Schema

### Entity-Relationship Diagram

```
┌─────────────────┐
│     users       │
├─────────────────┤
│ id (PK)         │
│ username        │
│ email           │
│ hashed_password │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────────┐
│   conversations     │
├─────────────────────┤
│ id (PK)             │
│ user_id (FK)        │
│ title               │
│ dialogue_type       │
│ status              │
│ created_at          │
│ updated_at          │
└────────┬────────────┘
         │
         │ 1:N
         │
┌────────▼────────────┐
│     messages        │
├─────────────────────┤
│ id (PK)             │
│ conversation_id (FK)│
│ role                │
│ content             │
│ message_type        │
│ metadata            │
│ created_at          │
└─────────────────────┘
```

## Tables

### users

Stores user account information.

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| username | VARCHAR(50) | UNIQUE, NOT NULL | User's login name |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User's email address |
| hashed_password | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| is_active | BOOLEAN | DEFAULT TRUE | Account active status |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation time |
| updated_at | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | Last profile update time |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `username`
- UNIQUE INDEX on `email`
- INDEX on `created_at` for sorting

**Constraints:**
- `username` must be 3-50 characters
- `email` must be valid email format
- `hashed_password` must be bcrypt hash

**Sample Data:**
```sql
INSERT INTO users (username, email, hashed_password) VALUES
('john_doe', 'john@example.com', '$2b$12$...'),
('jane_smith', 'jane@example.com', '$2b$12$...');
```

---

### conversations

Stores conversation metadata and settings.

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique conversation identifier |
| user_id | INTEGER | FOREIGN KEY (users.id), NOT NULL | Owner of the conversation |
| title | VARCHAR(200) | NOT NULL | Conversation title |
| dialogue_type | ENUM | NOT NULL | Type of conversation |
| status | ENUM | DEFAULT 'active' | Conversation status |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | Last update time |

**Dialogue Types:**
- `normal`: Standard chat conversation
- `deep_thinking`: Reasoning-enhanced conversation
- `web_search`: Search-augmented conversation
- `rag`: Document-based conversation

**Status Values:**
- `active`: Currently active conversation
- `archived`: Archived but not deleted
- `completed`: Marked as completed

**Indexes:**
- PRIMARY KEY on `id`
- FOREIGN KEY on `user_id` REFERENCES `users(id)` ON DELETE CASCADE
- INDEX on `user_id, created_at` for user conversation queries
- INDEX on `status` for filtering

**Sample Data:**
```sql
INSERT INTO conversations (user_id, title, dialogue_type, status) VALUES
(1, 'Python Help', 'normal', 'active'),
(1, 'Code Review', 'deep_thinking', 'active'),
(2, 'Documentation Search', 'web_search', 'archived');
```

---

### messages

Stores individual messages within conversations.

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique message identifier |
| conversation_id | INTEGER | FOREIGN KEY (conversations.id), NOT NULL | Parent conversation |
| role | ENUM | NOT NULL | Message sender role |
| content | TEXT | NOT NULL | Message content |
| message_type | VARCHAR(50) | DEFAULT 'text' | Type of message |
| metadata | JSON | NULL | Additional message data |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Message creation time |

**Role Values:**
- `user`: Message from user
- `assistant`: Message from AI assistant
- `system`: System-generated message

**Message Types:**
- `text`: Plain text message
- `code`: Code snippet
- `image`: Image reference
- `file`: File attachment reference

**Indexes:**
- PRIMARY KEY on `id`
- FOREIGN KEY on `conversation_id` REFERENCES `conversations(id)` ON DELETE CASCADE
- INDEX on `conversation_id, created_at` for message retrieval
- INDEX on `created_at` for time-based queries

**Sample Data:**
```sql
INSERT INTO messages (conversation_id, role, content, message_type) VALUES
(1, 'user', 'What is Python?', 'text'),
(1, 'assistant', 'Python is a high-level programming language...', 'text'),
(1, 'user', 'Show me an example', 'text'),
(1, 'assistant', 'Here is a Python example:\n```python\nprint("Hello")\n```', 'code');
```

## Relationships

### users → conversations (One-to-Many)

- One user can have multiple conversations
- Deleting a user cascades to delete all their conversations
- Foreign key: `conversations.user_id` → `users.id`

### conversations → messages (One-to-Many)

- One conversation can have multiple messages
- Deleting a conversation cascades to delete all its messages
- Foreign key: `messages.conversation_id` → `conversations.id`

## Common Queries

### Get User's Recent Conversations

```sql
SELECT c.id, c.title, c.created_at, COUNT(m.id) as message_count
FROM conversations c
LEFT JOIN messages m ON c.id = m.conversation_id
WHERE c.user_id = ?
  AND c.status = 'active'
GROUP BY c.id
ORDER BY c.updated_at DESC
LIMIT 20;
```

### Get Conversation with Messages

```sql
SELECT 
  c.id as conversation_id,
  c.title,
  m.id as message_id,
  m.role,
  m.content,
  m.created_at
FROM conversations c
LEFT JOIN messages m ON c.id = m.conversation_id
WHERE c.id = ?
  AND c.user_id = ?
ORDER BY m.created_at ASC;
```

### Count Messages Per User

```sql
SELECT 
  u.id,
  u.username,
  COUNT(DISTINCT c.id) as conversation_count,
  COUNT(m.id) as message_count
FROM users u
LEFT JOIN conversations c ON u.id = c.user_id
LEFT JOIN messages m ON c.id = m.conversation_id
GROUP BY u.id, u.username;
```

### Find Active Conversations

```sql
SELECT c.*, MAX(m.created_at) as last_message_time
FROM conversations c
LEFT JOIN messages m ON c.id = m.conversation_id
WHERE c.status = 'active'
GROUP BY c.id
HAVING last_message_time > DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY last_message_time DESC;
```

## Database Migrations

### Migration Tool

AssistGen uses Alembic for database migrations.

### Create Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add user profile fields"

# Create empty migration
alembic revision -m "Custom migration"
```

### Apply Migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade to specific version
alembic upgrade abc123

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

### Migration Best Practices

1. **Always review auto-generated migrations** before applying
2. **Test migrations on development database** first
3. **Backup production database** before migrating
4. **Write reversible migrations** (implement downgrade)
5. **Keep migrations small** and focused
6. **Document breaking changes** in migration comments

## Database Initialization

### First-Time Setup

```bash
# Create database
mysql -u root -p -e "CREATE DATABASE assistgen CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Create database user
mysql -u root -p -e "CREATE USER 'assistgen'@'localhost' IDENTIFIED BY 'secure_password';"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON assistgen.* TO 'assistgen'@'localhost';"

# Run migrations
alembic upgrade head

# Verify tables
mysql -u assistgen -p assistgen -e "SHOW TABLES;"
```

### Seed Data (Optional)

```bash
# Run seed script
python scripts/seed_database.py
```

## Performance Optimization

### Connection Pooling

SQLAlchemy connection pool configuration:

```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,          # Persistent connections
    max_overflow=10,      # Additional connections
    pool_timeout=30,      # Wait time for connection
    pool_recycle=3600,    # Recycle after 1 hour
    pool_pre_ping=True    # Test before use
)
```

### Query Optimization

1. **Use indexes** for frequently queried columns
2. **Avoid N+1 queries** by using joins or eager loading
3. **Paginate large result sets** to reduce memory usage
4. **Use database-level aggregations** instead of application-level
5. **Cache frequently accessed data** in Redis

### Index Recommendations

```sql
-- Speed up user conversation queries
CREATE INDEX idx_conversations_user_created 
ON conversations(user_id, created_at DESC);

-- Speed up message retrieval
CREATE INDEX idx_messages_conversation_created 
ON messages(conversation_id, created_at ASC);

-- Speed up user lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

## Backup and Restore

### Backup Database

```bash
# MySQL backup
mysqldump -u assistgen -p assistgen > backup_$(date +%Y%m%d).sql

# PostgreSQL backup
pg_dump -U assistgen assistgen > backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
# MySQL restore
mysql -u assistgen -p assistgen < backup_20240101.sql

# PostgreSQL restore
psql -U assistgen assistgen < backup_20240101.sql
```

### Automated Backups

Set up daily backups using cron:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/scripts/backup_db.sh
```

## Monitoring

### Key Metrics

1. **Connection Pool Usage**: Monitor active/idle connections
2. **Query Performance**: Track slow queries (>100ms)
3. **Database Size**: Monitor disk usage growth
4. **Lock Contention**: Detect deadlocks and long-running transactions
5. **Replication Lag**: For replicated setups

### Monitoring Queries

```sql
-- Show active connections
SHOW PROCESSLIST;

-- Show slow queries (MySQL)
SELECT * FROM mysql.slow_log ORDER BY start_time DESC LIMIT 10;

-- Show database size
SELECT 
  table_schema AS 'Database',
  ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables
WHERE table_schema = 'assistgen'
GROUP BY table_schema;

-- Show table sizes
SELECT 
  table_name AS 'Table',
  ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)'
FROM information_schema.tables
WHERE table_schema = 'assistgen'
ORDER BY (data_length + index_length) DESC;
```

## Troubleshooting

### Connection Issues

**Problem**: "Too many connections" error

**Solution**:
1. Increase `max_connections` in MySQL configuration
2. Reduce `pool_size` and `max_overflow` in application
3. Check for connection leaks (unclosed sessions)

### Slow Queries

**Problem**: Queries taking too long

**Solution**:
1. Enable slow query log
2. Analyze query execution plans with `EXPLAIN`
3. Add missing indexes
4. Optimize query structure
5. Consider denormalization for read-heavy tables

### Disk Space

**Problem**: Database growing too large

**Solution**:
1. Archive old conversations
2. Implement data retention policies
3. Compress old data
4. Move attachments to object storage

## Security

### Access Control

1. **Principle of least privilege**: Grant only necessary permissions
2. **Separate users**: Different users for application, admin, backup
3. **Strong passwords**: Use long, random passwords
4. **Network restrictions**: Limit database access to application servers

### Encryption

1. **Encryption at rest**: Enable database encryption
2. **Encryption in transit**: Use SSL/TLS for connections
3. **Sensitive data**: Hash passwords, encrypt PII

### SQL Injection Prevention

AssistGen uses SQLAlchemy ORM with parameterized queries to prevent SQL injection:

```python
# SAFE: Parameterized query
stmt = select(User).where(User.username == username)

# UNSAFE: String concatenation (never do this!)
query = f"SELECT * FROM users WHERE username = '{username}'"
```

## Data Retention

### Retention Policies

- **Active conversations**: Kept indefinitely
- **Archived conversations**: Kept for 1 year
- **Deleted conversations**: Soft delete for 30 days, then hard delete
- **User accounts**: Kept until user requests deletion

### Cleanup Script

```python
# Delete old archived conversations
from datetime import datetime, timedelta
from sqlalchemy import delete

cutoff_date = datetime.utcnow() - timedelta(days=365)

stmt = delete(Conversation).where(
    Conversation.status == 'archived',
    Conversation.updated_at < cutoff_date
)

await db.execute(stmt)
await db.commit()
```

## Scaling Strategies

### Read Replicas

For read-heavy workloads:

1. Set up MySQL replication (master-slave)
2. Route read queries to replicas
3. Route write queries to master
4. Monitor replication lag

### Sharding

For very large datasets:

1. Shard by `user_id` (user-based sharding)
2. Use consistent hashing for shard selection
3. Implement shard-aware query routing
4. Consider using Vitess or similar tools

### Caching

Reduce database load with caching:

1. **Redis cache** for frequently accessed data
2. **Cache user profiles** (TTL: 5 minutes)
3. **Cache conversation lists** (TTL: 1 minute)
4. **Invalidate cache** on updates

## References

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [MySQL Performance Tuning](https://dev.mysql.com/doc/refman/8.0/en/optimization.html)
- [PostgreSQL Performance Tips](https://www.postgresql.org/docs/current/performance-tips.html)
