"""
Conversation Schemas

Pydantic models for conversation-related request/response validation.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.conversation import DialogueType


class ConversationCreate(BaseModel):
    """
    Schema for creating a new conversation.
    
    Attributes:
        title: Conversation title (optional, auto-generated if not provided)
        dialogue_type: Type of dialogue (default: NORMAL)
        
    Example:
        {
            "title": "Python Help",
            "dialogue_type": "normal"
        }
    """
    
    title: Optional[str] = Field(
        "New Conversation",
        max_length=100,
        description="Conversation title"
    )
    
    dialogue_type: DialogueType = Field(
        default=DialogueType.NORMAL,
        description="Type of dialogue"
    )


class ConversationUpdate(BaseModel):
    """
    Schema for updating conversation metadata.
    
    Attributes:
        title: New conversation title
        status: New conversation status
        
    Example:
        {
            "title": "Updated Title"
        }
    """
    
    title: Optional[str] = Field(
        None,
        max_length=100,
        description="New conversation title"
    )
    
    status: Optional[str] = Field(
        None,
        description="New conversation status"
    )


class ConversationResponse(BaseModel):
    """
    Schema for conversation data in API responses.
    
    Attributes:
        id: Conversation ID
        user_id: Owner user ID
        title: Conversation title
        created_at: Creation timestamp
        updated_at: Last update timestamp
        status: Conversation status
        dialogue_type: Type of dialogue
        message_count: Number of messages
        
    Example:
        {
            "id": 1,
            "user_id": 1,
            "title": "Python Help",
            "created_at": "2024-01-01T12:00:00",
            "status": "ongoing",
            "dialogue_type": "normal",
            "message_count": 5
        }
    """
    
    id: int = Field(..., description="Conversation ID")
    user_id: int = Field(..., description="Owner user ID")
    title: str = Field(..., description="Conversation title")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    status: str = Field(..., description="Conversation status")
    dialogue_type: str = Field(..., description="Type of dialogue")
    message_count: int = Field(..., description="Number of messages")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
