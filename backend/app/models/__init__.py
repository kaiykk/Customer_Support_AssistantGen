"""
Database Models Package

This package contains all SQLAlchemy ORM models for the application.
Models define the database schema and relationships between tables.

Available Models:
- User: User account and authentication
- Conversation: Chat conversation sessions
- Message: Individual messages within conversations

Usage:
    from app.models import User, Conversation, Message
    
    # Create new user
    user = User(username="john", email="john@example.com")
    
    # Create conversation
    conversation = Conversation(user_id=user.id, title="Help")
    
    # Create message
    message = Message(
        conversation_id=conversation.id,
        sender="user",
        content="Hello"
    )
"""

from app.models.user import User
from app.models.conversation import Conversation, DialogueType
from app.models.message import Message

__all__ = [
    "User",
    "Conversation",
    "DialogueType",
    "Message",
]
