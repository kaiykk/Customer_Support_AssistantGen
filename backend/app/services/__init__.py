"""
Service Layer Package

This package contains all business logic services for the application.
Services encapsulate business operations and coordinate between
controllers (API endpoints) and data access layers (models).

Service Architecture:
- BaseService: Abstract base class with common functionality
- UserService: User management and authentication
- ConversationService: Conversation and message management
- LLMFactory: Factory for creating LLM service instances
- DeepseekService: DeepSeek AI integration
- OllamaService: Ollama AI integration
- SearchService: Search functionality
- EmbeddingService: Text embedding generation
- IndexingService: Document indexing
- RedisCacheService: Redis-based semantic caching

Design Principles:
- Single Responsibility: Each service handles one domain
- Dependency Injection: Services receive dependencies via constructor
- Separation of Concerns: Business logic separate from data access
- Testability: Services are easily mockable for testing

Usage:
    from app.services import UserService, LLMFactory
    
    # In endpoint
    @app.post("/users")
    async def create_user(
        user_data: UserCreate,
        db: AsyncSession = Depends(get_db)
    ):
        service = UserService(db)
        user = await service.create_user(user_data)
        return user
"""

from app.services.base_service import BaseService
from app.services.user_service import UserService
from app.services.conversation_service import ConversationService
from app.services.llm_factory import LLMFactory

__all__ = [
    "BaseService",
    "UserService",
    "ConversationService",
    "LLMFactory",
]
