"""
User Schemas

Pydantic models for user-related request/response validation.
These schemas define the structure of data for user registration,
login, profile updates, and API responses.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator


class UserCreate(BaseModel):
    """
    Schema for user registration request.
    
    Attributes:
        username: Unique username (3-50 characters)
        email: Valid email address
        password: Password (min 8 characters)
        
    Example:
        {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "SecurePass123!"
        }
    """
    
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username for the account"
    )
    
    email: EmailStr = Field(
        ...,
        description="Valid email address"
    )
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (minimum 8 characters)"
    )
    
    @validator('username')
    def username_alphanumeric(cls, v):
        """Validate username contains only alphanumeric and underscore."""
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    """
    Schema for user login request.
    
    Attributes:
        email: User's email address
        password: User's password
        
    Example:
        {
            "email": "john@example.com",
            "password": "SecurePass123!"
        }
    """
    
    email: EmailStr = Field(
        ...,
        description="User's email address"
    )
    
    password: str = Field(
        ...,
        description="User's password"
    )


class UserUpdate(BaseModel):
    """
    Schema for user profile update request.
    
    All fields are optional. Only provided fields will be updated.
    
    Attributes:
        username: New username (optional)
        email: New email address (optional)
        
    Example:
        {
            "username": "new_username"
        }
    """
    
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description="New username"
    )
    
    email: Optional[EmailStr] = Field(
        None,
        description="New email address"
    )
    
    @validator('username')
    def username_alphanumeric(cls, v):
        """Validate username if provided."""
        if v and not v.replace('_', '').isalnum():
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v


class UserResponse(BaseModel):
    """
    Schema for user data in API responses.
    
    This schema excludes sensitive data like password hashes.
    
    Attributes:
        id: User ID
        username: Username
        email: Email address
        created_at: Account creation timestamp
        last_login: Last login timestamp
        status: Account status
        is_active: Whether account is active
        is_verified: Whether email is verified
        
    Example:
        {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "created_at": "2024-01-01T12:00:00",
            "status": "active",
            "is_active": true,
            "is_verified": false
        }
    """
    
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    status: str = Field(..., description="Account status")
    is_active: bool = Field(..., description="Whether account is active")
    is_verified: bool = Field(..., description="Whether email is verified")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00",
                "last_login": "2024-01-01T12:00:00",
                "status": "active",
                "is_active": True,
                "is_verified": False
            }
        }


class TokenResponse(BaseModel):
    """
    Schema for authentication token response.
    
    Attributes:
        access_token: JWT access token
        token_type: Token type (always "bearer")
        expires_in: Token expiration time in seconds
        
    Example:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "expires_in": 1800
        }
    """
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }
