"""
Conversation Model

This module defines the Conversation model for storing chat conversation
sessions between users and the AI assistant.

A conversation represents a complete chat session with multiple messages
exchanged between the user and assistant. Each conversation has a type
that determines the AI behavior (normal chat, deep thinking, web search, RAG).

Database Table: conversations

Relationships:
- Many-to-One with User (conversation belongs to one user)
- One-to-Many with Message (conversation has multiple messages)

Indexes:
- Primary key on id
- Foreign key index on user_id
"""

import enum
from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Enum
from sqlalchemy.orm import relationship, Mapped

from app.core.database import Base
from app.core.logger import get_logger

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.message import Message

logger = get_logger(service="conversation")


class DialogueType(enum.Enum):
    """
    Enumeration of conversation dialogue types.
    
    Each type determines how the AI assistant processes and responds
    to user messages within the conversation.
    
    Values:
        NORMAL: Standard conversational chat
        DEEP_THINKING: Deep reasoning and analysis mode
        WEB_SEARCH: Web search-enhanced responses
        RAG: Retrieval-Augmented Generation with knowledge base
    """
    
    NORMAL = "normal"
    DEEP_THINKING = "deep_thinking"
    WEB_SEARCH = "web_search"
    RAG = "rag"
    
    @classmethod
    def get_description(cls, dialogue_type: "DialogueType") -> str:
        """
        Get human-readable description of dialogue type.
        
        Args:
            dialogue_type: The dialogue type enum value
            
        Returns:
            str: Description of the dialogue type
        """
        descriptions = {
            cls.NORMAL: "Standard conversational chat",
            cls.DEEP_THINKING: "Deep reasoning and complex problem solving",
            cls.WEB_SEARCH: "Web search-enhanced responses with current information",
            cls.RAG: "Knowledge base-enhanced responses using RAG"
        }
        return descriptions.get(dialogue_type, "Unknown dialogue type")


class Conversation(Base):
    """
    Conversation model for chat sessions.
    
    This model represents a complete conversation session between a user
    and the AI assistant. Each conversation contains multiple messages
    and has a specific dialogue type that determines AI behavior.
    
    Attributes:
        id (int): Unique conversation identifier (primary key)
        user_id (int): ID of user who owns this conversation (foreign key)
        title (str): Conversation title (max 100 characters)
        created_at (datetime): Conversation creation timestamp
        updated_at (datetime): Last message timestamp
        status (str): Conversation status (ongoing, completed, archived)
        dialogue_type (DialogueType): Type of dialogue/AI behavior
        
    Relationships:
        user: User who owns this conversation
        messages: List of messages in this conversation (cascade delete)
        
    Constraints:
        - user_id must reference valid user
        - title is required
        - dialogue_type is required
        - status defaults to "ongoing"
        
    Example:
        conversation = Conversation(
            user_id=1,
            title="Python Help",
            dialogue_type=DialogueType.NORMAL
        )
        db.add(conversation)
        await db.commit()
    """
    
    __tablename__ = "conversations"
    
    # Primary key
    id: Mapped[int] = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Unique conversation identifier"
    )
    
    # Foreign keys
    user_id: Mapped[int] = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID of user who owns this conversation"
    )
    
    # Conversation metadata
    title: Mapped[str] = Column(
        String(100),
        nullable=False,
        comment="Conversation title"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        comment="Conversation creation timestamp"
    )
    
    updated_at: Mapped[datetime] = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last message timestamp"
    )
    
    # Status and type
    status: Mapped[str] = Column(
        String(20),
        default="ongoing",
        nullable=False,
        comment="Conversation status (ongoing, completed, archived)"
    )
    
    dialogue_type: Mapped[DialogueType] = Column(
        Enum(DialogueType),
        nullable=False,
        default=DialogueType.NORMAL,
        comment="Type of dialogue/AI behavior"
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="conversations",
        lazy="selectin"
    )
    
    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Message.created_at"
    )
    
    def __repr__(self) -> str:
        """String representation of Conversation."""
        return (
            f"<Conversation(id={self.id}, user_id={self.user_id}, "
            f"title='{self.title}', type={self.dialogue_type.value})>"
        )
    
    def to_dict(self) -> dict:
        """
        Convert conversation to dictionary.
        
        Returns:
            dict: Conversation data with metadata
            
        Example:
            conv_data = conversation.to_dict()
            # {'id': 1, 'title': 'Help', 'message_count': 5, ...}
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "status": self.status,
            "dialogue_type": self.dialogue_type.value,
            "dialogue_type_description": DialogueType.get_description(self.dialogue_type),
            "message_count": self.message_count
        }
    
    @property
    def message_count(self) -> int:
        """Get number of messages in this conversation."""
        return len(self.messages) if self.messages else 0
    
    @property
    def is_active(self) -> bool:
        """Check if conversation is active (ongoing)."""
        return self.status == "ongoing"
    
    @property
    def last_message_time(self) -> datetime:
        """Get timestamp of last message in conversation."""
        if self.messages:
            return max(msg.created_at for msg in self.messages)
        return self.created_at
    
    def archive(self) -> None:
        """Archive this conversation (set status to archived)."""
        self.status = "archived"
        logger.info(f"Conversation {self.id} archived")
    
    def complete(self) -> None:
        """Mark this conversation as completed."""
        self.status = "completed"
        logger.info(f"Conversation {self.id} marked as completed")
    
    def reopen(self) -> None:
        """Reopen this conversation (set status to ongoing)."""
        self.status = "ongoing"
        logger.info(f"Conversation {self.id} reopened")
