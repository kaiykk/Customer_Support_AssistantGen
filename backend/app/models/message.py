"""
Message Model

This module defines the Message model for storing individual messages
within conversations between users and the AI assistant.

Each message represents a single exchange in a conversation, either from
the user or from the assistant. Messages are ordered chronologically
within their parent conversation.

Database Table: messages

Relationships:
- Many-to-One with Conversation (message belongs to one conversation)

Indexes:
- Primary key on id
- Foreign key index on conversation_id
"""

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship, Mapped

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.conversation import Conversation


class Message(Base):
    """
    Message model for individual chat messages.
    
    This model represents a single message within a conversation,
    either from the user or from the AI assistant. Messages are
    stored in chronological order and can contain various types
    of content (text, code, images, etc.).
    
    Attributes:
        id (int): Unique message identifier (primary key)
        conversation_id (int): ID of parent conversation (foreign key)
        sender (str): Message sender ("user" or "assistant")
        content (str): Message content (text, markdown, etc.)
        created_at (datetime): Message creation timestamp
        message_type (str): Type of message content (text, code, image, etc.)
        metadata (str): Optional JSON metadata for additional info
        
    Relationships:
        conversation: Parent conversation containing this message
        
    Constraints:
        - conversation_id must reference valid conversation
        - sender is required (user or assistant)
        - content is required
        - message_type defaults to "text"
        
    Example:
        message = Message(
            conversation_id=1,
            sender="user",
            content="What is Python?",
            message_type="text"
        )
        db.add(message)
        await db.commit()
    """
    
    __tablename__ = "messages"
    
    # Primary key
    id: Mapped[int] = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Unique message identifier"
    )
    
    # Foreign keys
    conversation_id: Mapped[int] = Column(
        Integer,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID of parent conversation"
    )
    
    # Message data
    sender: Mapped[str] = Column(
        String(50),
        nullable=False,
        comment="Message sender (user or assistant)"
    )
    
    content: Mapped[str] = Column(
        Text,
        nullable=False,
        comment="Message content (text, markdown, code, etc.)"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="Message creation timestamp"
    )
    
    # Message metadata
    message_type: Mapped[str] = Column(
        String(20),
        default="text",
        nullable=False,
        comment="Type of message content (text, code, image, file, etc.)"
    )
    
    metadata: Mapped[str] = Column(
        Text,
        nullable=True,
        comment="Optional JSON metadata for additional information"
    )
    
    # Relationships
    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="messages",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        """String representation of Message."""
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return (
            f"<Message(id={self.id}, conversation_id={self.conversation_id}, "
            f"sender='{self.sender}', content='{content_preview}')>"
        )
    
    def to_dict(self) -> dict:
        """
        Convert message to dictionary.
        
        Returns:
            dict: Message data with all fields
            
        Example:
            msg_data = message.to_dict()
            # {'id': 1, 'sender': 'user', 'content': 'Hello', ...}
        """
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "sender": self.sender,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "message_type": self.message_type,
            "metadata": self.metadata,
            "is_user_message": self.is_user_message,
            "is_assistant_message": self.is_assistant_message,
            "content_length": self.content_length
        }
    
    @property
    def is_user_message(self) -> bool:
        """Check if this message is from the user."""
        return self.sender.lower() == "user"
    
    @property
    def is_assistant_message(self) -> bool:
        """Check if this message is from the assistant."""
        return self.sender.lower() in ["assistant", "ai", "bot"]
    
    @property
    def content_length(self) -> int:
        """Get length of message content in characters."""
        return len(self.content) if self.content else 0
    
    @property
    def word_count(self) -> int:
        """Get approximate word count of message content."""
        return len(self.content.split()) if self.content else 0
    
    def truncate_content(self, max_length: int = 100) -> str:
        """
        Get truncated version of message content.
        
        Args:
            max_length: Maximum length of truncated content
            
        Returns:
            str: Truncated content with ellipsis if needed
            
        Example:
            preview = message.truncate_content(50)
            # "This is a long message that will be trunca..."
        """
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + "..."
    
    @classmethod
    def create_user_message(
        cls,
        conversation_id: int,
        content: str,
        message_type: str = "text"
    ) -> "Message":
        """
        Factory method to create a user message.
        
        Args:
            conversation_id: ID of parent conversation
            content: Message content
            message_type: Type of message (default: "text")
            
        Returns:
            Message: New user message instance
            
        Example:
            msg = Message.create_user_message(
                conversation_id=1,
                content="Hello!"
            )
        """
        return cls(
            conversation_id=conversation_id,
            sender="user",
            content=content,
            message_type=message_type
        )
    
    @classmethod
    def create_assistant_message(
        cls,
        conversation_id: int,
        content: str,
        message_type: str = "text"
    ) -> "Message":
        """
        Factory method to create an assistant message.
        
        Args:
            conversation_id: ID of parent conversation
            content: Message content
            message_type: Type of message (default: "text")
            
        Returns:
            Message: New assistant message instance
            
        Example:
            msg = Message.create_assistant_message(
                conversation_id=1,
                content="Hello! How can I help?"
            )
        """
        return cls(
            conversation_id=conversation_id,
            sender="assistant",
            content=content,
            message_type=message_type
        )
