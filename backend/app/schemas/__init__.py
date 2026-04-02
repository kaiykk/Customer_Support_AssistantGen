"""
Pydantic Schemas Package

This package contains Pydantic models for request/response validation
and serialization. Schemas define the structure of data exchanged
between the API and clients.

Available Schemas:
- User schemas: UserCreate, UserLogin, UserResponse
- Conversation schemas: ConversationCreate, ConversationResponse
- Message schemas: MessageCreate, MessageResponse
- Chat schemas: ChatRequest, ChatResponse

Usage:
    from app.schemas import UserCreate, ChatRequest
    
    # Validate user registration data
    user_data = UserCreate(
        username="john",
        email="john@example.com",
        password="secure123"
    )
    
    # Validate chat request
    chat_request = ChatRequest(
        messages=[{"role": "user", "content": "Hello"}]
    )
"""

from app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate
)
from app.schemas.message import MessageCreate, MessageResponse
from app.schemas.chat import (
    ChatRequest,
    ChatMessage,
    ChatResponse,
    SearchChatRequest,
    AgentChatRequest
)

__all__ = [
    # User schemas
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
    # Conversation schemas
    "ConversationCreate",
    "ConversationResponse",
    "ConversationUpdate",
    # Message schemas
    "MessageCreate",
    "MessageResponse",
    # Chat schemas
    "ChatRequest",
    "ChatMessage",
    "ChatResponse",
    "SearchChatRequest",
    "AgentChatRequest",
]
