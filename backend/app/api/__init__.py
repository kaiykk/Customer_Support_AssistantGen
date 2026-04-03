"""
API Module

This module contains all API route definitions for the AssistGen application.
It provides a centralized router that includes all endpoint modules.

The API is organized into the following modules:
- conversations: Conversation and message management endpoints
- auth: Authentication and authorization endpoints (if implemented)
- users: User management endpoints (if implemented)

Author: AssistGen Team
License: MIT
"""

from fastapi import APIRouter

# Create main API router
api_router = APIRouter()

# Import and include sub-routers
from app.api.conversations import router as conversations_router

# Include conversation routes
api_router.include_router(
    conversations_router,
    tags=["Conversations"]
)

# Export router
__all__ = ["api_router"]
