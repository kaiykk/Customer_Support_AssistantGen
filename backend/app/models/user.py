"""
User Model

This module defines the User model for storing user account information
including authentication credentials, profile data, and account status.

The User model is the central entity for authentication and authorization,
and maintains relationships with conversations and other user-specific data.

Database Table: users

Relationships:
- One-to-Many with Conversation (user can have multiple conversations)

Indexes:
- Primary key on id
- Unique index on username
- Unique index on email
"""

from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship, Mapped

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.conversation import Conversation


class User(Base):
    """
    User account model for authentication and profile management.
    
    This model stores user account information including credentials,
    profile data, and account status. It serves as the primary entity
    for user authentication and authorization.
    
    Attributes:
        id (int): Unique user identifier (primary key)
        username (str): Unique username for login (max 50 characters)
        email (str): Unique email address (max 100 characters)
        password_hash (str): Hashed password (never store plain text)
        created_at (datetime): Account creation timestamp
        updated_at (datetime): Last profile update timestamp
        last_login (datetime): Last successful login timestamp
        status (str): Account status (active, inactive, suspended)
        is_active (bool): Whether account is active
        is_verified (bool): Whether email is verified
        
    Relationships:
        conversations: List of user's conversations (cascade delete)
        
    Constraints:
        - username must be unique
        - email must be unique
        - password_hash is required
        - status defaults to "active"
        
    Example:
        user = User(
            username="john_doe",
            email="john@example.com",
            password_hash=hashed_password
        )
        db.add(user)
        await db.commit()
    """
    
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[int] = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Unique user identifier"
    )
    
    # Authentication fields
    username: Mapped[str] = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique username for login"
    )
    
    email: Mapped[str] = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique email address"
    )
    
    password_hash: Mapped[str] = Column(
        String(255),
        nullable=False,
        comment="Hashed password (bcrypt/argon2)"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        comment="Account creation timestamp"
    )
    
    updated_at: Mapped[datetime] = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last profile update timestamp"
    )
    
    last_login: Mapped[datetime] = Column(
        DateTime,
        nullable=True,
        comment="Last successful login timestamp"
    )
    
    # Account status
    status: Mapped[str] = Column(
        String(20),
        default="active",
        nullable=False,
        comment="Account status (active, inactive, suspended)"
    )
    
    is_active: Mapped[bool] = Column(
        Integer,
        default=1,
        nullable=False,
        comment="Whether account is active (1=active, 0=inactive)"
    )
    
    is_verified: Mapped[bool] = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Whether email is verified (1=verified, 0=unverified)"
    )
    
    # Relationships
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    def to_dict(self) -> dict:
        """
        Convert user to dictionary (excluding sensitive data).
        
        Returns:
            dict: User data without password hash
            
        Example:
            user_data = user.to_dict()
            # {'id': 1, 'username': 'john', 'email': 'john@example.com', ...}
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "status": self.status,
            "is_active": bool(self.is_active),
            "is_verified": bool(self.is_verified)
        }
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated (has valid account)."""
        return self.is_active and self.status == "active"
    
    @property
    def conversation_count(self) -> int:
        """Get number of conversations for this user."""
        return len(self.conversations) if self.conversations else 0
