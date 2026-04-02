"""
Message Schemas

Pydantic models for message-related request/response validation.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    """
    Schema for creating a new message.
    
    Attributes:
        conversation_id: Parent conversation ID
        sender: Message sender (user or assistant)
        content: Message content
        message_type: Type of message (default: text)
        
    Example:
        {
            "conversation_id": 1,
            "sender": "user",
            "content": "What is Python?",
            "message_type": "text"
        }
    """
    
    conversation_id: int = Field(..., description="Parent conversation ID")
    sender: str = Field(..., description="Message sender")
    content: str = Field(..., description="Message content")
    message_type: str = Field(default="text", description="Type of message")


class MessageResponse(BaseModel):
    """
    Schema for message data in API responses.
    
    Attributes:
        id: Message ID
        conversation_id: Parent conversation ID
        sender: Message sender
        content: Message content
        created_at: Creation timestamp
        message_type: Type of message
        
    Example:
        {
            "id": 1,
            "conversation_id": 1,
            "sender": "user",
            "content": "What is Python?",
            "created_at": "2024-01-01T12:00:00",
            "message_type": "text"
        }
    """
    
    id: int = Field(..., description="Message ID")
    conversation_id: int = Field(..., description="Parent conversation ID")
    sender: str = Field(..., description="Message sender")
    content: str = Field(..., description="Message content")
    created_at: datetime = Field(..., description="Creation timestamp")
    message_type: str = Field(..., description="Type of message")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
