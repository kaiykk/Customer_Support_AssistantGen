"""
Security and Authentication Module

This module provides JWT-based authentication and authorization functionality
for the application. It handles token creation, validation, and user authentication.

Key Features:
- JWT token generation with configurable expiration
- OAuth2 password bearer authentication
- User authentication from JWT tokens
- Automatic token validation and user retrieval
- Secure credential handling

Security Considerations:
- Tokens are signed with SECRET_KEY from configuration
- Tokens expire after configured time period
- Invalid tokens return 401 Unauthorized
- User credentials are validated against database

Usage:
    from app.core.security import create_access_token, get_current_user
    
    # Create token after login
    token = create_access_token(data={"sub": user.email})
    
    # Protect endpoint with authentication
    @app.get("/protected")
    async def protected_route(current_user = Depends(get_current_user)):
        return {"user": current_user.email}
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.user_service import UserService
from app.core.database import get_db

# OAuth2 password bearer scheme for token authentication
# This tells FastAPI to look for Bearer tokens in the Authorization header
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token",  # URL where clients can obtain tokens
    scheme_name="JWT"
)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token with user data and expiration.
    
    This function generates a signed JWT token containing user information
    and an expiration timestamp. The token is signed with the application's
    SECRET_KEY to prevent tampering.
    
    Args:
        data: Dictionary containing user data to encode in token.
              Typically includes {"sub": user_email} where "sub" is the subject.
        expires_delta: Optional custom expiration time.
                      If not provided, defaults to 15 minutes.
    
    Returns:
        str: Encoded JWT token string
        
    Example:
        # Create token with default 15-minute expiration
        token = create_access_token(data={"sub": "user@example.com"})
        
        # Create token with custom 7-day expiration
        token = create_access_token(
            data={"sub": "user@example.com"},
            expires_delta=timedelta(days=7)
        )
        
    Token Structure:
        {
            "sub": "user@example.com",  # User identifier
            "exp": 1234567890,           # Expiration timestamp
            ...                          # Additional data from 'data' parameter
        }
    """
    # Create a copy to avoid modifying the original data
    to_encode = data.copy()
    
    # Calculate expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default to 15 minutes if not specified
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    # Add expiration to token payload
    to_encode.update({"exp": expire})
    
    # Encode and sign the token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token for obtaining new access tokens.
    
    Refresh tokens have longer expiration times and are used to obtain
    new access tokens without requiring the user to log in again.
    
    Args:
        data: Dictionary containing user data to encode in token
        expires_delta: Optional custom expiration time.
                      If not provided, defaults to 7 days.
    
    Returns:
        str: Encoded JWT refresh token string
        
    Example:
        refresh_token = create_refresh_token(
            data={"sub": "user@example.com"}
        )
    """
    to_encode = data.copy()
    
    # Refresh tokens typically have longer expiration (7 days default)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    
    # Mark as refresh token and add expiration
    to_encode.update({"exp": expire, "type": "refresh"})
    
    # Encode and sign the token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Validate JWT token and retrieve the current authenticated user.
    
    This dependency function extracts and validates the JWT token from
    the request, then retrieves the corresponding user from the database.
    It's used to protect endpoints that require authentication.
    
    Args:
        token: JWT token from Authorization header (injected by oauth2_scheme)
        db: Database session (injected by get_db dependency)
    
    Returns:
        User: The authenticated user object from database
        
    Raises:
        HTTPException: 401 Unauthorized if:
            - Token is invalid or expired
            - Token doesn't contain required user identifier
            - User doesn't exist in database
            
    Example:
        @app.get("/profile")
        async def get_profile(
            current_user = Depends(get_current_user)
        ):
            return {
                "email": current_user.email,
                "name": current_user.name
            }
            
    Security Flow:
        1. Extract token from Authorization: Bearer <token>
        2. Decode and verify token signature
        3. Extract user email from token payload
        4. Query database for user with that email
        5. Return user object or raise 401 error
    """
    # Prepare exception for authentication failures
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode and verify the JWT token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Extract user email from token payload
        # "sub" (subject) is the standard JWT claim for user identifier
        email: str = payload.get("sub")
        
        if email is None:
            raise credentials_exception
            
    except JWTError as e:
        # Token is invalid, expired, or tampered with
        raise credentials_exception
    
    # Retrieve user from database
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    
    if user is None:
        # User no longer exists in database
        raise credentials_exception
        
    return user


async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """
    Get current user and verify they are active.
    
    This is an additional layer of protection that checks if the user
    account is still active (not disabled or suspended).
    
    Args:
        current_user: User object from get_current_user dependency
    
    Returns:
        User: The authenticated and active user
        
    Raises:
        HTTPException: 400 Bad Request if user account is inactive
        
    Example:
        @app.delete("/account")
        async def delete_account(
            current_user = Depends(get_current_active_user)
        ):
            # Only active users can delete their account
            ...
    """
    if hasattr(current_user, 'is_active') and not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    return current_user


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token without database lookup.
    
    This function is useful for validating tokens without the overhead
    of a database query. It only verifies the token signature and expiration.
    
    Args:
        token: JWT token string to verify
    
    Returns:
        Optional[Dict[str, Any]]: Token payload if valid, None if invalid
        
    Example:
        payload = verify_token(token)
        if payload:
            user_email = payload.get("sub")
            print(f"Token is valid for {user_email}")
        else:
            print("Invalid token")
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
