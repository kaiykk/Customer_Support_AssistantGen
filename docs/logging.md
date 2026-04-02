# Logging Configuration Guide

This document describes the logging infrastructure and configuration options for the AssistGen application.

## Overview

AssistGen uses Python's built-in `logging` module with structured logging capabilities. The logging system provides:

- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Multiple output handlers (console, file, error file)
- Structured JSON logging for machine parsing
- Request/response logging with timing information
- Automatic log rotation to prevent disk space issues
- Context-aware logging with request IDs

## Log Levels

### DEBUG
- Detailed diagnostic information
- SQL queries and database operations
- Internal state changes
- Only enabled in development environments

### INFO
- General informational messages
- API request/response logs
- Service operation confirmations
- User actions (login, logout, etc.)

### WARNING
- Potentially problematic situations
- Slow requests (>1 second)
- Deprecated feature usage
- Resource usage warnings

### ERROR
- Error conditions that don't stop the application
- Failed API calls
- Database errors with recovery
- Validation failures

### CRITICAL
- Severe errors requiring immediate attention
- Application startup failures
- Database connection failures
- Security breaches

## Configuration

### Environment Variables

Configure logging behavior using these environment variables:

```bash
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Enable/disable console logging
LOG_TO_CONSOLE=true

# Enable/disable file logging
LOG_TO_FILE=true

# Log file directory
LOG_DIR=logs

# Log file name
LOG_FILE=assistgen.log

# Error log file name
ERROR_LOG_FILE=assistgen_error.log

# Maximum log file size before rotation (in bytes)
LOG_MAX_BYTES=10485760  # 10MB

# Number of backup log files to keep
LOG_BACKUP_COUNT=5
```

### Development Environment

Recommended settings for development:

```bash
LOG_LEVEL=DEBUG
LOG_TO_CONSOLE=true
LOG_TO_FILE=true
```

### Production Environment

Recommended settings for production:

```bash
LOG_LEVEL=INFO
LOG_TO_CONSOLE=false
LOG_TO_FILE=true
LOG_MAX_BYTES=52428800  # 50MB
LOG_BACKUP_COUNT=10
```

## Log Rotation

Log files are automatically rotated when they reach the configured size limit:

- **Rotation trigger**: When log file reaches `LOG_MAX_BYTES`
- **Backup files**: Keeps `LOG_BACKUP_COUNT` old log files
- **Naming pattern**: `assistgen.log`, `assistgen.log.1`, `assistgen.log.2`, etc.
- **Automatic cleanup**: Oldest files are deleted when backup count is exceeded

### Manual Log Rotation

To manually rotate logs:

```bash
# Linux/Mac
mv logs/assistgen.log logs/assistgen.log.$(date +%Y%m%d)

# Windows PowerShell
Move-Item logs/assistgen.log logs/assistgen.log.$(Get-Date -Format 'yyyyMMdd')
```

## Log Format

### Console Output

Human-readable format for development:

```
2024-01-01 12:00:00,123 - INFO - [main] - Application started successfully
2024-01-01 12:00:01,456 - INFO - [http] - 127.0.0.1:54321 - "GET /api/users HTTP/1.1" 200 - 0.15s
2024-01-01 12:00:02,789 - ERROR - [conversation] - Error saving message: Connection timeout
```

### File Output

Structured JSON format for machine parsing:

```json
{
  "timestamp": "2024-01-01T12:00:00.123Z",
  "level": "INFO",
  "service": "main",
  "message": "Application started successfully",
  "request_id": "abc-123-def-456"
}
```

## Usage Examples

### Basic Logging

```python
from app.core.logger import get_logger

logger = get_logger(service="my_service")

logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical failure")
```

### Structured Logging

```python
from app.core.logger import log_structured

log_structured(
    level="info",
    message="User logged in",
    user_id=123,
    ip_address="192.168.1.1",
    timestamp=datetime.utcnow().isoformat()
)
```

### API Call Logging

```python
from app.core.logger import log_api_call

log_api_call(
    method="POST",
    endpoint="/api/chat",
    status_code=200,
    response_time_ms=150.5,
    user_id=123
)
```

### Context Manager Logging

```python
from app.core.logger import log_context

with log_context(operation="database_query", user_id=123):
    # Your code here
    result = await db.execute(query)
```

## Log Analysis

### View Recent Logs

```bash
# Last 100 lines
tail -n 100 logs/assistgen.log

# Follow logs in real-time
tail -f logs/assistgen.log

# Search for errors
grep "ERROR" logs/assistgen.log

# Search for specific user
grep "user_id=123" logs/assistgen.log
```

### Parse JSON Logs

```python
import json

with open('logs/assistgen.log') as f:
    for line in f:
        try:
            log_entry = json.loads(line)
            if log_entry['level'] == 'ERROR':
                print(f"{log_entry['timestamp']}: {log_entry['message']}")
        except json.JSONDecodeError:
            # Skip non-JSON lines
            pass
```

## Monitoring and Alerts

### Key Metrics to Monitor

1. **Error Rate**: Number of ERROR/CRITICAL logs per minute
2. **Slow Requests**: Requests taking >1 second
3. **Authentication Failures**: Failed login attempts
4. **Database Errors**: Connection failures, query timeouts
5. **Rate Limit Hits**: 429 responses

### Alert Thresholds

Recommended alert thresholds:

- **Error rate** > 10 errors/minute → Warning
- **Error rate** > 50 errors/minute → Critical
- **Slow requests** > 20% of total → Warning
- **Database errors** > 5/minute → Critical
- **Authentication failures** > 100/hour from single IP → Security alert

## Troubleshooting

### Logs Not Appearing

1. Check `LOG_LEVEL` is not set too high (e.g., ERROR when you want INFO)
2. Verify `LOG_TO_CONSOLE` or `LOG_TO_FILE` is enabled
3. Check file permissions on log directory
4. Verify `LOG_DIR` path exists and is writable

### Log Files Growing Too Large

1. Reduce `LOG_MAX_BYTES` to rotate more frequently
2. Reduce `LOG_BACKUP_COUNT` to keep fewer old files
3. Increase `LOG_LEVEL` to reduce log volume
4. Set up external log aggregation (e.g., ELK stack)

### Performance Impact

If logging impacts performance:

1. Disable DEBUG logging in production
2. Use asynchronous logging handlers
3. Reduce log verbosity for high-traffic endpoints
4. Consider sampling (log 1 in N requests)

## Best Practices

1. **Use appropriate log levels**: Don't log everything as ERROR
2. **Include context**: Add user_id, request_id, etc. to logs
3. **Sanitize sensitive data**: Never log passwords, tokens, or PII
4. **Log exceptions with traceback**: Use `exc_info=True`
5. **Monitor log volume**: Set up alerts for unusual log patterns
6. **Rotate logs regularly**: Prevent disk space issues
7. **Centralize logs**: Use log aggregation for multi-server deployments
8. **Test logging**: Verify logs contain useful information

## Integration with External Services

### ELK Stack (Elasticsearch, Logstash, Kibana)

Configure Logstash to parse JSON logs:

```ruby
input {
  file {
    path => "/path/to/logs/assistgen.log"
    codec => "json"
  }
}

filter {
  # Add filters as needed
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "assistgen-%{+YYYY.MM.dd}"
  }
}
```

### Sentry Integration

For error tracking and monitoring:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment="production"
)
```

## Security Considerations

1. **Never log sensitive data**: Passwords, tokens, credit cards, PII
2. **Sanitize user input**: Prevent log injection attacks
3. **Restrict log access**: Only authorized personnel should access logs
4. **Encrypt logs at rest**: For compliance requirements
5. **Audit log access**: Track who accesses production logs
6. **Retention policies**: Delete old logs per compliance requirements

## References

- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [FastAPI Logging Guide](https://fastapi.tiangolo.com/tutorial/logging/)
- [Structured Logging Best Practices](https://www.structlog.org/)
