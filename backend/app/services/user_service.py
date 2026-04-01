"""
User Service Module

This module provides business logic for user management operations including
user registration, authentication, profile management, and user queries.

Key Features:
- User registration with duplicate checking
- User authentication with password verification
- Last login timestamp tracking
- User profile retrieval
- Password hashing and verification

Security:
- Passwords are hashed using bcrypt/argon2
- Email and username uniqueness is enforced
- Authentication failures are logged for security monitoring

Usage:
    from app.services import UserService
    
    # In endpoint
    @app.post("/register")
    async def register(
        user_data: UserCreate,
        db: AsyncSession = Depends(get_db)
    ):
        service = UserService(db)
        user = await service.create_user(user_data)
        return {"id": user.id, "email": user.email}
"""

from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.hashing import get_password_hash, verify_password
from app.core.logger import get_logger
from app.services.base_service import BaseService

logger = get_logger(service="user_service")


class UserService(BaseService[User]):
    """
    Service class for user management operations.
    
    This service handles all user-related business logic including
    registration, authentication, and profile management.
    
    Attributes:
        db: Database session for this service instance
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the user service.
        
        Args:
            db: Database session for user operations
        """
        super().__init__(db, User)
        self.logger = logger
    
    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user account.
        
        This method validates that the email and username are unique,
        hashes the password, and creates the user record in the database.
        
        Args:
            user_data: User registration data containing username, email, and password
            
        Returns:
            User: Created user object with ID and timestamps
            
        Raises:
            ValueError: If email or username already exists
            
        Example:
            user_data = UserCreate(
                username="john_doe",
                email="john@example.com",
                password="secure_password_123"
            )
            user = await service.create_user(user_data)
            print(f"Created user: {user.id}")
            
        Security Notes:
            - Password is hashed before storage
            - Email and username uniqueness is enforced
            - Original password is never stored
        """
        # Check if email or username already exists
        query = select(User).where(
            or_(
                User.email == user_data.email,
                User.username == user_data.username
            )
        )
        result = await self.db.execute(query)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            # Provide specific error message based on which field conflicts
            if existing_user.email == user_data.email:
                self.logger.warning(
                    f"Registration attempt with existing email: {user_data.email}"
                )
                raise ValueError("This email is already registered")
            else:
                self.logger.warning(
                    f"Registration attempt with existing username: {user_data.username}"
                )
                raise ValueError("This username is already taken")
        
        # Create new user with hashed password
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password)
        )
        
        # Add to database
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        
        self.logger.info(f"Created new user: {db_user.id} ({db_user.email})")
        
        return db_user
    
    async def authenticate_user(
        self,
        email: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate a user with email and password.
        
        This method verifies the user's credentials and updates the
        last login timestamp if authentication is successful.
        
        Args:
            email: User's email address
            password: User's password (plain text or SHA256 hash from frontend)
            
        Returns:
            Optional[User]: User object if authentication successful, None otherwise
            
        Example:
            user = await service.authenticate_user(
                email="john@example.com",
                password="secure_password_123"
            )
            if user:
                print(f"Login successful for {user.email}")
            else:
                print("Invalid credentials")
                
        Security Notes:
            - Failed authentication attempts are logged
            - Last login timestamp is updated on successful login
            - Password verification uses constant-time comparison
        """
        # Query user by email
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        
        # Check if user exists
        if not user:
            self.logger.warning(f"Authentication failed: User not found - {email}")
            return None
        
        # Verify password
        if not verify_password(password, user.password_hash):
            self.logger.warning(
                f"Authentication failed: Invalid password for user - {email}"
            )
            return None
        
        # Update last login timestamp
        user.last_login = datetime.utcnow()
        await self.db.commit()
        
        self.logger.info(f"User authenticated successfully: {user.id} ({email})")
        
        return user
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieve a user by their ID.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            Optional[User]: User object if found, None otherwise
            
        Example:
            user = await service.get_user_by_id(123)
            if user:
                print(f"Found user: {user.email}")
        """
        return await self.get_by_id(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.
        
        Args:
            email: User's email address
            
        Returns:
            Optional[User]: User object if found, None otherwise
            
        Example:
            user = await service.get_user_by_email("john@example.com")
            if user:
                print(f"Found user: {user.id}")
        """
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve a user by their username.
        
        Args:
            username: User's username
            
        Returns:
            Optional[User]: User object if found, None otherwise
            
        Example:
            user = await service.get_user_by_username("john_doe")
            if user:
                print(f"Found user: {user.email}")
        """
        query = select(User).where(User.username == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_user_profile(
        self,
        user_id: int,
        **kwargs
    ) -> Optional[User]:
        """
        Update user profile information.
        
        This method allows updating user fields like username, email, etc.
        Password updates should use update_password() instead.
        
        Args:
            user_id: User's unique identifier
            **kwargs: Fields to update (e.g., username="new_name")
            
        Returns:
            Optional[User]: Updated user object if found, None otherwise
            
        Example:
            updated_user = await service.update_user_profile(
                user_id=123,
                username="new_username"
            )
            
        Note:
            This method does not update passwords. Use update_password() for that.
        """
        # Remove password-related fields if present
        kwargs.pop('password', None)
        kwargs.pop('password_hash', None)
        
        return await self.update(user_id, **kwargs)
    
    async def update_password(
        self,
        user_id: int,
        new_password: str
    ) -> Optional[User]:
        """
        Update a user's password.
        
        Args:
            user_id: User's unique identifier
            new_password: New password (will be hashed)
            
        Returns:
            Optional[User]: Updated user object if found, None otherwise
            
        Example:
            updated_user = await service.update_password(
                user_id=123,
                new_password="new_secure_password"
            )
            
        Security Notes:
            - Password is hashed before storage
            - Old password is not verified (use change_password for that)
        """
        password_hash = get_password_hash(new_password)
        return await self.update(user_id, password_hash=password_hash)
    
    async def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        Change a user's password with old password verification.
        
        This method verifies the old password before updating to the new one.
        
        Args:
            user_id: User's unique identifier
            old_password: Current password for verification
            new_password: New password to set
            
        Returns:
            bool: True if password changed successfully, False if old password invalid
            
        Example:
            success = await service.change_password(
                user_id=123,
                old_password="old_password",
                new_password="new_password"
            )
            if success:
                print("Password changed successfully")
            else:
                print("Invalid old password")
        """
        # Get user
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        # Verify old password
        if not verify_password(old_password, user.password_hash):
            self.logger.warning(
                f"Password change failed: Invalid old password for user {user_id}"
            )
            return False
        
        # Update to new password
        await self.update_password(user_id, new_password)
        
        self.logger.info(f"Password changed successfully for user {user_id}")
        
        return True
    
    async def deactivate_user(self, user_id: int) -> bool:
        """
        Deactivate a user account.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            bool: True if user was deactivated, False if not found
            
        Example:
            deactivated = await service.deactivate_user(123)
            if deactivated:
                print("User account deactivated")
        """
        user = await self.update(user_id, is_active=False)
        if user:
            self.logger.info(f"User {user_id} deactivated")
            return True
        return False
    
    async def activate_user(self, user_id: int) -> bool:
        """
        Activate a user account.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            bool: True if user was activated, False if not found
            
        Example:
            activated = await service.activate_user(123)
            if activated:
                print("User account activated")
        """
        user = await self.update(user_id, is_active=True)
        if user:
            self.logger.info(f"User {user_id} activated")
            return True
        return False
