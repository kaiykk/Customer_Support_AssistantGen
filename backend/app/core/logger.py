"""
Logging Configuration and Utilities

This module provides centralized logging configuration using Loguru.
It sets up structured logging with file rotation, compression, and
separate error log files.

Key Features:
- Console output with colored formatting
- File-based logging with automatic rotation
- Separate error log file for ERROR and above
- Automatic log compression (zip) for old files
- Configurable retention periods
- Structured logging support for JSON-like data
- Service-specific logger binding

Log Files:
- logs/app.log: General application logs (INFO and above)
  - Rotation: 500 MB
  - Retention: 10 days
  
- logs/error.log: Error logs only (ERROR and above)
  - Rotation: 100 MB
  - Retention: 30 days

Log Directory:
The logs directory is created relative to the current working directory
where the application is started. Different components may create logs
in different locations depending on their working directory.

Usage:
    from app.core.logger import get_logger, log_structured
    
    # Get logger for a specific service
    logger = get_logger("user_service")
    logger.info("User created successfully")
    
    # Log structured data
    log_structured("user_login", {
        "user_id": 123,
        "ip_address": "192.168.1.1",
        "timestamp": "2024-01-01T12:00:00"
    })
"""

from loguru import logger
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import json

# Create logs directory in current working directory
# Note: The location depends on where the application is started
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Remove default Loguru handler to customize output
logger.remove()

# Add console output handler with colored formatting
# This provides real-time log visibility during development
logger.add(
    sys.stdout,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ),
    level="INFO",
    colorize=True,
    backtrace=True,  # Show full traceback on errors
    diagnose=True,   # Show variable values in traceback
)

# Add general application log file handler
# Captures all INFO and above messages with automatic rotation
logger.add(
    "logs/app.log",
    rotation="500 MB",  # Create new file when current reaches 500 MB
    retention="10 days",  # Keep logs for 10 days
    compression="zip",  # Compress old log files to save space
    format=(
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} - "
        "{message}"
    ),
    level="INFO",
    encoding="utf-8",
    enqueue=True,  # Thread-safe logging
    backtrace=True,
    diagnose=True,
)

# Add separate error log file handler
# Captures only ERROR and CRITICAL messages for easier error tracking
logger.add(
    "logs/error.log",
    rotation="100 MB",  # Smaller rotation size for error logs
    retention="30 days",  # Keep error logs longer (30 days)
    compression="zip",
    format=(
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} - "
        "{message}"
    ),
    level="ERROR",
    encoding="utf-8",
    enqueue=True,
    backtrace=True,
    diagnose=True,
)


def get_logger(service: str):
    """
    Get a logger instance bound to a specific service name.
    
    This function returns a logger that automatically includes the service
    name in all log messages, making it easier to trace logs from different
    components of the application.
    
    Args:
        service: Name of the service/component (e.g., "user_service", "auth")
    
    Returns:
        Logger: Loguru logger instance bound to the service name
        
    Example:
        # In user_service.py
        logger = get_logger("user_service")
        logger.info("Processing user registration")
        # Output: ... | user_service | Processing user registration
        
        # In auth.py
        logger = get_logger("auth")
        logger.error("Authentication failed")
        # Output: ... | auth | Authentication failed
    """
    return logger.bind(service=service)


def log_structured(event_type: str, data: Dict[str, Any]) -> None:
    """
    Log structured data in JSON-like format.
    
    This function is useful for logging events with associated metadata
    that can be easily parsed and analyzed by log aggregation tools.
    
    Args:
        event_type: Type of event being logged (e.g., "user_login", "api_call")
        data: Dictionary containing event metadata
        
    Example:
        log_structured("user_login", {
            "user_id": 123,
            "email": "user@example.com",
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0...",
            "success": True
        })
        
        log_structured("api_call", {
            "endpoint": "/api/users",
            "method": "POST",
            "status_code": 201,
            "response_time_ms": 45.2
        })
        
    Output Format:
        The log message will be a JSON string containing both event_type and data:
        {"event_type": "user_login", "data": {"user_id": 123, ...}}
    """
    log_entry = {
        "event_type": event_type,
        "data": data
    }
    logger.info(json.dumps(log_entry))


def log_api_call(
    method: str,
    endpoint: str,
    status_code: int,
    response_time_ms: float,
    user_id: Optional[int] = None,
    error: Optional[str] = None
) -> None:
    """
    Log API call details in structured format.
    
    This is a convenience function for logging API requests with
    consistent formatting across the application.
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        endpoint: API endpoint path
        status_code: HTTP status code
        response_time_ms: Response time in milliseconds
        user_id: Optional user ID making the request
        error: Optional error message if request failed
        
    Example:
        log_api_call(
            method="POST",
            endpoint="/api/users",
            status_code=201,
            response_time_ms=45.2,
            user_id=123
        )
        
        log_api_call(
            method="GET",
            endpoint="/api/users/999",
            status_code=404,
            response_time_ms=12.5,
            error="User not found"
        )
    """
    data = {
        "method": method,
        "endpoint": endpoint,
        "status_code": status_code,
        "response_time_ms": response_time_ms,
    }
    
    if user_id is not None:
        data["user_id"] = user_id
        
    if error is not None:
        data["error"] = error
    
    log_structured("api_call", data)


def log_database_query(
    query_type: str,
    table: str,
    duration_ms: float,
    rows_affected: Optional[int] = None,
    error: Optional[str] = None
) -> None:
    """
    Log database query details in structured format.
    
    This function helps track database performance and identify
    slow queries or database errors.
    
    Args:
        query_type: Type of query (SELECT, INSERT, UPDATE, DELETE)
        table: Database table name
        duration_ms: Query execution time in milliseconds
        rows_affected: Number of rows affected by the query
        error: Optional error message if query failed
        
    Example:
        log_database_query(
            query_type="SELECT",
            table="users",
            duration_ms=15.3,
            rows_affected=10
        )
        
        log_database_query(
            query_type="INSERT",
            table="users",
            duration_ms=8.7,
            rows_affected=1
        )
    """
    data = {
        "query_type": query_type,
        "table": table,
        "duration_ms": duration_ms,
    }
    
    if rows_affected is not None:
        data["rows_affected"] = rows_affected
        
    if error is not None:
        data["error"] = error
    
    log_structured("database_query", data)


class LogContext:
    """
    Context manager for adding temporary context to log messages.
    
    This class allows you to add contextual information to all log
    messages within a specific code block.
    
    Example:
        with LogContext(request_id="abc-123", user_id=456):
            logger.info("Processing request")
            # Log will include request_id and user_id
            
            logger.error("Request failed")
            # Error log will also include request_id and user_id
    """
    
    def __init__(self, **kwargs):
        """
        Initialize log context with key-value pairs.
        
        Args:
            **kwargs: Arbitrary key-value pairs to add to log context
        """
        self.context = kwargs
        self.token = None
    
    def __enter__(self):
        """Enter the context and bind context data to logger."""
        self.token = logger.contextualize(**self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context and remove context data from logger."""
        # Context is automatically removed when exiting
        pass


# Export logger instance for direct use
__all__ = [
    "logger",
    "get_logger",
    "log_structured",
    "log_api_call",
    "log_database_query",
    "LogContext",
]
