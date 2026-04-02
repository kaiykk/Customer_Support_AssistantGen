"""
Chat Schemas

Pydantic models for chat-related request/response validation.
These schemas define the structure for chat interactions with the AI.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, validator


class ChatMessage(BaseModel):
    """
    Schema for a single chat message.
    
    Attributes:
        role: Message role (user, assistant, system)
        content: Message content
        
    Example:
        {
            "role": "user",
            "content": "What is Python?"
        }
    """
    
    role: str = Field(
        ...,
        description="Message role (user, assistant, system)"
    )
    
    content: str = Field(
        ...,
        description="Message content"
    )
    
    @validator('role')
    def validate_role(cls, v):
        """Validate message role."""
        allowed_roles = ['user', 'assistant', 'system']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v


class ChatRequest(BaseModel):
    """
    Schema for chat request.
    
    Attributes:
        messages: List of chat messages
        conversation_id: Optional conversation ID for context
        stream: Whether to stream the response
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens in response
        
    Example:
        {
            "messages": [
                {"role": "user", "content": "What is Python?"}
            ],
            "conversation_id": 1,
            "stream": true,
            "temperature": 0.7
        }
    """
    
    messages: List[ChatMessage] = Field(
        ...,
        min_length=1,
        description="List of chat messages"
    )
    
    conversation_id: Optional[int] = Field(
        None,
        description="Conversation ID for context"
    )
    
    stream: bool = Field(
        default=True,
        description="Whether to stream the response"
    )
    
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature"
    )
    
    max_tokens: Optional[int] = Field(
        None,
        gt=0,
        description="Maximum tokens in response"
    )


class SearchChatRequest(ChatRequest):
    """
    Schema for search-enhanced chat request.
    
    Extends ChatRequest with search-specific parameters.
    
    Attributes:
        search_query: Optional custom search query
        max_search_results: Maximum number of search results
        
    Example:
        {
            "messages": [
                {"role": "user", "content": "Latest Python features"}
            ],
            "search_query": "Python 3.12 new features",
            "max_search_results": 5
        }
    """
    
    search_query: Optional[str] = Field(
        None,
        description="Custom search query (auto-generated if not provided)"
    )
    
    max_search_results: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of search results"
    )


class AgentChatRequest(ChatRequest):
    """
    Schema for agent-based chat request.
    
    Extends ChatRequest with agent-specific parameters.
    
    Attributes:
        tools: List of tools available to the agent
        max_iterations: Maximum agent iterations
        
    Example:
        {
            "messages": [
                {"role": "user", "content": "Calculate 15% of 200"}
            ],
            "tools": ["calculator", "search"],
            "max_iterations": 5
        }
    """
    
    tools: Optional[List[str]] = Field(
        None,
        description="List of tools available to the agent"
    )
    
    max_iterations: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum agent iterations"
    )


class ChatResponse(BaseModel):
    """
    Schema for chat response.
    
    Attributes:
        content: Response content
        conversation_id: Conversation ID
        message_id: Message ID
        model: Model used for generation
        usage: Token usage statistics
        
    Example:
        {
            "content": "Python is a programming language...",
            "conversation_id": 1,
            "message_id": 2,
            "model": "deepseek-chat",
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 50,
                "total_tokens": 60
            }
        }
    """
    
    content: str = Field(..., description="Response content")
    conversation_id: Optional[int] = Field(None, description="Conversation ID")
    message_id: Optional[int] = Field(None, description="Message ID")
    model: str = Field(..., description="Model used for generation")
    usage: Optional[Dict[str, int]] = Field(None, description="Token usage statistics")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "content": "Python is a high-level programming language...",
                "conversation_id": 1,
                "message_id": 2,
                "model": "deepseek-chat",
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 50,
                    "total_tokens": 60
                }
            }
        }


class StreamChunk(BaseModel):
    """
    Schema for streaming response chunk.
    
    Attributes:
        content: Chunk content
        done: Whether streaming is complete
        
    Example:
        {
            "content": "Python",
            "done": false
        }
    """
    
    content: str = Field(..., description="Chunk content")
    done: bool = Field(default=False, description="Whether streaming is complete")
