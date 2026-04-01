"""
HTTP Middleware Components

This module provides custom middleware for the FastAPI application.
Middleware components intercept and process HTTP requests and responses,
adding cross-cutting concerns like logging, performance monitoring,
error handling, and security headers.

Key Features:
- Request/response logging with timing information
- Performance monitoring and slow request detection
- Error handling and exception logging
- Security headers injection
- Request ID tracking for distributed tracing

Middleware Execution Order:
Middleware is executed in the order it's added to the application.
For this module:
1. SecurityHeadersMiddleware (adds security headers)
2. RequestIDMiddleware (adds request ID for tracing)
3. LoggingMiddleware (logs requests and responses)
4. ErrorHandlingMiddleware (catches and logs exceptions)

Usage:
    from app.core.middleware import (
        LoggingMiddleware,
        SecurityHeadersMiddleware,
        RequestIDMiddleware,
        ErrorHandlingMiddleware
    )
    
    app = FastAPI()
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logger import get_logger, log_api_call

# Get logger for HTTP middleware
logger = get_logger(service="http")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    
    This middleware logs details about each HTTP request including:
    - Client IP address and port
    - HTTP method and path
    - Response status code
    - Request processing time
    
    Slow requests (>1 second) are logged as warnings for performance monitoring.
    
    Example Log Output:
        192.168.1.1:54321 - "GET /api/users HTTP/1.1" 200 - 0.15s
        192.168.1.1:54322 - "POST /api/login HTTP/1.1" 401 - 0.08s
        192.168.1.1:54323 - "GET /api/slow-endpoint HTTP/1.1" 200 - 1.25s [SLOW]
    """
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process the request and log details.
        
        Args:
            request: Incoming HTTP request
            call_next: Function to call the next middleware or endpoint
            
        Returns:
            Response: HTTP response from the endpoint
        """
        # Record start time for performance measurement
        start_time = time.time()
        
        # Get client information
        client_host = request.client.host if request.client else "unknown"
        client_port = request.client.port if request.client else 0
        
        # Process the request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Get HTTP version from request scope
        http_version = request.scope.get('http_version', '1.1')
        
        # Format log message
        log_message = (
            f"{client_host}:{client_port} - "
            f'"{request.method} {request.url.path} HTTP/{http_version}" '
            f"{response.status_code} - {process_time:.2f}s"
        )
        
        # Log as warning if request took more than 1 second
        if process_time > 1.0:
            logger.warning(f"{log_message} [SLOW REQUEST]")
        else:
            logger.info(log_message)
        
        # Log structured API call data for analytics
        log_api_call(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            response_time_ms=process_time * 1000,
            user_id=getattr(request.state, "user_id", None)
        )
        
        # Add processing time to response headers
        response.headers["X-Process-Time"] = f"{process_time:.3f}"
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding security headers to HTTP responses.
    
    This middleware adds important security headers to protect against
    common web vulnerabilities:
    
    Headers Added:
    - X-Content-Type-Options: nosniff
      Prevents MIME type sniffing
      
    - X-Frame-Options: DENY
      Prevents clickjacking attacks
      
    - X-XSS-Protection: 1; mode=block
      Enables browser XSS protection
      
    - Strict-Transport-Security: max-age=31536000; includeSubDomains
      Enforces HTTPS connections
      
    - Content-Security-Policy: default-src 'self'
      Restricts resource loading to same origin
      
    Note:
        These headers provide defense-in-depth security.
        Adjust CSP policy based on your application's needs.
    """
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process the request and add security headers to response.
        
        Args:
            request: Incoming HTTP request
            call_next: Function to call the next middleware or endpoint
            
        Returns:
            Response: HTTP response with security headers added
        """
        # Process the request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding unique request IDs to each request.
    
    This middleware generates a unique ID for each request and adds it
    to both the request state and response headers. This is useful for:
    - Distributed tracing across services
    - Correlating logs from the same request
    - Debugging issues by tracking specific requests
    
    The request ID is:
    - Generated as a UUID4
    - Stored in request.state.request_id
    - Added to response headers as X-Request-ID
    - Available to all downstream middleware and endpoints
    
    Example:
        @app.get("/users")
        async def get_users(request: Request):
            request_id = request.state.request_id
            logger.info(f"Processing request {request_id}")
            ...
    """
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process the request and add request ID.
        
        Args:
            request: Incoming HTTP request
            call_next: Function to call the next middleware or endpoint
            
        Returns:
            Response: HTTP response with X-Request-ID header
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Store in request state for access in endpoints
        request.state.request_id = request_id
        
        # Process the request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for catching and handling unhandled exceptions.
    
    This middleware provides a safety net for exceptions that aren't
    caught by endpoint handlers. It:
    - Catches all unhandled exceptions
    - Logs detailed error information
    - Returns user-friendly error responses
    - Prevents sensitive error details from leaking to clients
    
    Error Response Format:
        {
            "detail": "Internal server error",
            "request_id": "abc-123-def-456"
        }
    
    Note:
        This middleware should be added last (first in execution order)
        to catch exceptions from all other middleware and endpoints.
    """
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process the request with exception handling.
        
        Args:
            request: Incoming HTTP request
            call_next: Function to call the next middleware or endpoint
            
        Returns:
            Response: HTTP response or error response if exception occurred
        """
        try:
            # Process the request
            response = await call_next(request)
            return response
            
        except Exception as exc:
            # Get request ID if available
            request_id = getattr(request.state, "request_id", "unknown")
            
            # Log detailed error information
            logger.error(
                f"Unhandled exception in request {request_id}: "
                f"{type(exc).__name__}: {str(exc)}",
                exc_info=True  # Include full traceback
            )
            
            # Return user-friendly error response
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "request_id": request_id
                }
            )


class CORSMiddleware(BaseHTTPMiddleware):
    """
    Custom CORS middleware with detailed logging.
    
    This middleware handles Cross-Origin Resource Sharing (CORS) requests
    and logs CORS-related information for debugging.
    
    Note:
        FastAPI provides built-in CORSMiddleware which is recommended
        for production use. This custom implementation is provided for
        educational purposes and custom CORS logic if needed.
    
    Example:
        from fastapi.middleware.cors import CORSMiddleware
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    """
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process the request and handle CORS.
        
        Args:
            request: Incoming HTTP request
            call_next: Function to call the next middleware or endpoint
            
        Returns:
            Response: HTTP response with CORS headers if applicable
        """
        # Get origin from request headers
        origin = request.headers.get("origin")
        
        if origin:
            logger.debug(f"CORS request from origin: {origin}")
        
        # Process the request
        response = await call_next(request)
        
        return response


# Export all middleware classes
__all__ = [
    "LoggingMiddleware",
    "SecurityHeadersMiddleware",
    "RequestIDMiddleware",
    "ErrorHandlingMiddleware",
    "CORSMiddleware",
]
