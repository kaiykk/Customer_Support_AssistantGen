"""
Conversation Service Module

This module provides business logic for conversation and message management.
It handles creating conversations, saving messages, retrieving conversation
history, and managing conversation metadata.

Key Features:
- Conversation creation and management
- Message storage and retrieval
- Automatic conversation title generation
- Conversation history queries
- Conversation deletion with cascade
- Conversation renaming

Usage:
    from app.services import ConversationService
    
    # Create new conversation
    conversation_id = await ConversationService.create_conversation(user_id=123)
    
    # Save messages
    await ConversationService.save_message(
        user_id=123,
        conversation_id=conversation_id,
        messages=[{"role": "user", "content": "Hello"}],
        response="Hi there!"
    )
"""

from typing import List, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.conversation import Conversation, DialogueType
from app.models.message import Message
from app.core.logger import get_logger

logger = get_logger(service="conversation")


class ConversationService:
    """
    Service class for conversation and message management.
    
    This service handles all conversation-related business logic including
    creating conversations, saving messages, and retrieving conversation history.
    
    Note:
        This service uses AsyncSessionLocal directly for database operations
        rather than dependency injection. This allows it to be used as a
        static service without requiring a database session parameter.
    """
    
    @staticmethod
    def get_conversation_title(message: str, max_length: int = 20) -> str:
        """
        Generate a conversation title from the first user message.
        
        This method extracts a short title from the user's first message
        by taking the first few words and truncating if necessary.
        
        Args:
            message: User's first message content
            max_length: Maximum length of the title (default: 20 characters)
            
        Returns:
            str: Generated conversation title
            
        Example:
            title = ConversationService.get_conversation_title(
                "How do I install Python on Windows?"
            )
            # Returns: "How do I install..."
            
        Note:
            - Multiple spaces are collapsed to single spaces
            - Title is truncated with "..." if longer than max_length
        """
        # Normalize whitespace (collapse multiple spaces to single space)
        title = " ".join(message.split())
        
        # Truncate if too long
        if len(title) > max_length:
            title = title[:max_length] + "..."
        
        return title
    
    @staticmethod
    async def create_conversation(
        user_id: int,
        title: str = "New Conversation",
        dialogue_type: DialogueType = DialogueType.NORMAL
    ) -> int:
        """
        Create a new conversation for a user.
        
        Args:
            user_id: ID of the user creating the conversation
            title: Initial conversation title (default: "New Conversation")
            dialogue_type: Type of dialogue (NORMAL, SEARCH, AGENT, etc.)
            
        Returns:
            int: ID of the created conversation
            
        Raises:
            Exception: If database operation fails
            
        Example:
            conversation_id = await ConversationService.create_conversation(
                user_id=123,
                title="Python Help",
                dialogue_type=DialogueType.NORMAL
            )
            print(f"Created conversation: {conversation_id}")
        """
        async with AsyncSessionLocal() as db:
            try:
                # Create new conversation
                conversation = Conversation(
                    user_id=user_id,
                    title=title,
                    dialogue_type=dialogue_type
                )
                
                db.add(conversation)
                await db.commit()
                await db.refresh(conversation)
                
                logger.info(
                    f"Created new conversation {conversation.id} "
                    f"for user {user_id} (type: {dialogue_type.value})"
                )
                
                return conversation.id
                
            except Exception as e:
                await db.rollback()
                logger.error(
                    f"Error creating conversation for user {user_id}: {e}",
                    exc_info=True
                )
                raise
    
    @staticmethod
    async def save_message(
        user_id: int,
        conversation_id: int,
        messages: List[Dict],
        response: str
    ) -> None:
        """
        Save user message and assistant response to a conversation.
        
        This method saves both the user's message and the assistant's response
        to the database. If this is the first message in the conversation,
        it also updates the conversation title based on the user's message.
        
        Args:
            user_id: ID of the user sending the message
            conversation_id: ID of the conversation
            messages: List of message dictionaries with 'role' and 'content' keys
            response: Assistant's response text
            
        Raises:
            Exception: If database operation fails
            
        Example:
            await ConversationService.save_message(
                user_id=123,
                conversation_id=456,
                messages=[
                    {"role": "user", "content": "What is Python?"}
                ],
                response="Python is a programming language..."
            )
            
        Note:
            - Automatically updates conversation title for first message
            - Saves both user and assistant messages in order
            - Logs errors but doesn't raise to prevent conversation interruption
        """
        try:
            async with AsyncSessionLocal() as db:
                # Query conversation
                stmt = select(Conversation).where(
                    Conversation.id == conversation_id
                )
                result = await db.execute(stmt)
                conversation = result.scalar_one_or_none()
                
                if not conversation:
                    logger.error(
                        f"Conversation {conversation_id} not found "
                        f"when saving message for user {user_id}"
                    )
                    return
                
                # Verify conversation belongs to user
                if conversation.user_id != user_id:
                    logger.error(
                        f"User {user_id} attempted to save message to "
                        f"conversation {conversation_id} owned by user {conversation.user_id}"
                    )
                    return
                
                # Query existing messages count
                stmt = select(Message).where(
                    Message.conversation_id == conversation_id
                )
                result = await db.execute(stmt)
                messages_count = len(result.all())
                
                # Extract user's message content
                user_content = next(
                    (msg["content"] for msg in messages if msg["role"] == "user"),
                    ""
                )
                
                # Update conversation title if this is the first message
                if messages_count == 0 and user_content:
                    title = ConversationService.get_conversation_title(user_content)
                    conversation.title = title
                    logger.info(
                        f"Updated conversation {conversation_id} title to: {title}"
                    )
                
                # Save user message
                user_message = Message(
                    conversation_id=conversation_id,
                    sender="user",
                    content=user_content
                )
                db.add(user_message)
                
                # Save assistant response
                assistant_message = Message(
                    conversation_id=conversation_id,
                    sender="assistant",
                    content=response
                )
                db.add(assistant_message)
                
                await db.commit()
                
                logger.info(
                    f"Saved message pair to conversation {conversation_id} "
                    f"(user: {len(user_content)} chars, "
                    f"assistant: {len(response)} chars)"
                )
                
        except Exception as e:
            logger.error(
                f"Error saving conversation: {str(e)}",
                exc_info=True
            )
            logger.error(
                f"Error details - user_id: {user_id}, "
                f"conversation_id: {conversation_id}"
            )
            logger.error(f"Messages: {messages}")
    
    @staticmethod
    async def get_user_conversations(
        user_id: int,
        include_empty: bool = False,
        skip: int = 0,
        limit: int = 50
    ) -> Dict[str, any]:
        """
        Retrieve conversations for a user with pagination support.
        
        Args:
            user_id: ID of the user
            include_empty: Whether to include conversations with no messages
                          (default: False, excludes "New Conversation" entries)
            skip: Number of conversations to skip (for pagination)
            limit: Maximum number of conversations to return (default: 50)
            
        Returns:
            Dict: Dictionary containing conversations list and pagination metadata
            
        Raises:
            Exception: If database operation fails
            
        Example:
            result = await ConversationService.get_user_conversations(
                user_id=123,
                skip=0,
                limit=20
            )
            print(f"Total: {result['total']}, Page: {result['conversations']}")
                
        Response Format:
            {
                "conversations": [
                    {
                        "id": 1,
                        "title": "Python Help",
                        "created_at": "2024-01-01T12:00:00",
                        "status": "active",
                        "dialogue_type": "normal"
                    },
                    ...
                ],
                "total": 100,
                "skip": 0,
                "limit": 20
            }
        """
        try:
            async with AsyncSessionLocal() as db:
                # Build base query
                base_stmt = select(Conversation).where(
                    Conversation.user_id == user_id
                )
                
                # Exclude empty conversations unless requested
                if not include_empty:
                    base_stmt = base_stmt.where(Conversation.title != "New Conversation")
                
                # Get total count
                from sqlalchemy import func
                count_stmt = select(func.count()).select_from(
                    base_stmt.subquery()
                )
                total_result = await db.execute(count_stmt)
                total = total_result.scalar() or 0
                
                # Build paginated query
                stmt = base_stmt.order_by(
                    Conversation.created_at.desc()
                ).offset(skip).limit(limit)
                
                result = await db.execute(stmt)
                conversations = result.scalars().all()
                
                logger.info(
                    f"Retrieved {len(conversations)} conversations for user {user_id} "
                    f"(skip={skip}, limit={limit}, total={total})"
                )
                
                return {
                    "conversations": [
                        {
                            "id": conv.id,
                            "title": conv.title,
                            "created_at": conv.created_at.isoformat(),
                            "status": conv.status,
                            "dialogue_type": conv.dialogue_type.value
                        }
                        for conv in conversations
                    ],
                    "total": total,
                    "skip": skip,
                    "limit": limit
                }
                
        except Exception as e:
            logger.error(
                f"Error getting conversations for user {user_id}: {str(e)}",
                exc_info=True
            )
            raise
    
    @staticmethod
    async def get_conversation_messages(
        conversation_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, any]:
        """
        Retrieve messages from a conversation with pagination support.
        
        This method verifies that the conversation belongs to the user
        before returning messages.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for ownership verification)
            skip: Number of messages to skip (for pagination)
            limit: Maximum number of messages to return (default: 100)
            
        Returns:
            Dict: Dictionary containing messages list and pagination metadata
            
        Raises:
            ValueError: If conversation not found or not owned by user
            Exception: If database operation fails
            
        Example:
            result = await ConversationService.get_conversation_messages(
                conversation_id=456,
                user_id=123,
                skip=0,
                limit=50
            )
            for msg in result['messages']:
                print(f"{msg['sender']}: {msg['content']}")
                
        Response Format:
            {
                "messages": [
                    {
                        "id": 1,
                        "sender": "user",
                        "content": "What is Python?",
                        "created_at": "2024-01-01T12:00:00",
                        "message_type": "text"
                    },
                    ...
                ],
                "total": 150,
                "skip": 0,
                "limit": 50
            }
        """
        try:
            async with AsyncSessionLocal() as db:
                # Verify conversation exists and belongs to user
                stmt = select(Conversation).where(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id
                )
                result = await db.execute(stmt)
                conversation = result.scalar_one_or_none()
                
                if not conversation:
                    logger.warning(
                        f"Conversation {conversation_id} not found or "
                        f"not owned by user {user_id}"
                    )
                    raise ValueError(
                        f"Conversation {conversation_id} not found or "
                        f"not owned by user {user_id}"
                    )
                
                # Get total count
                from sqlalchemy import func
                count_stmt = select(func.count()).where(
                    Message.conversation_id == conversation_id
                )
                total_result = await db.execute(count_stmt)
                total = total_result.scalar() or 0
                
                # Query messages with pagination
                stmt = select(Message).where(
                    Message.conversation_id == conversation_id
                ).order_by(Message.created_at).offset(skip).limit(limit)
                
                result = await db.execute(stmt)
                messages = result.scalars().all()
                
                logger.info(
                    f"Retrieved {len(messages)} messages from "
                    f"conversation {conversation_id} (skip={skip}, limit={limit}, total={total})"
                )
                
                return {
                    "messages": [
                        {
                            "id": msg.id,
                            "sender": msg.sender,
                            "content": msg.content,
                            "created_at": msg.created_at.isoformat(),
                            "message_type": msg.message_type
                        }
                        for msg in messages
                    ],
                    "total": total,
                    "skip": skip,
                    "limit": limit
                }
                
        except Exception as e:
            logger.error(
                f"Error getting messages for conversation {conversation_id}: {str(e)}",
                exc_info=True
            )
            raise
    
    @staticmethod
    async def delete_conversation(conversation_id: int, user_id: Optional[int] = None) -> None:
        """
        Delete a conversation and all its messages.
        
        This method deletes the conversation and all associated messages.
        The deletion is cascaded automatically by the database.
        
        Args:
            conversation_id: ID of the conversation to delete
            user_id: Optional user ID for ownership verification
            
        Raises:
            ValueError: If conversation not found or not owned by user
            Exception: If database operation fails
            
        Example:
            await ConversationService.delete_conversation(
                conversation_id=456,
                user_id=123
            )
            print("Conversation deleted successfully")
            
        Note:
            - All messages are automatically deleted (cascade)
            - Operation is logged for audit purposes
        """
        try:
            async with AsyncSessionLocal() as db:
                # Query conversation
                stmt = select(Conversation).where(
                    Conversation.id == conversation_id
                )
                
                # Add user ownership check if user_id provided
                if user_id is not None:
                    stmt = stmt.where(Conversation.user_id == user_id)
                
                result = await db.execute(stmt)
                conversation = result.scalar_one_or_none()
                
                if not conversation:
                    error_msg = f"Conversation {conversation_id} not found"
                    if user_id is not None:
                        error_msg += f" or not owned by user {user_id}"
                    logger.warning(error_msg)
                    raise ValueError(error_msg)
                
                # Delete conversation (messages are cascade deleted)
                await db.delete(conversation)
                await db.commit()
                
                logger.info(
                    f"Deleted conversation {conversation_id} "
                    f"and all associated messages"
                )
                
        except Exception as e:
            logger.error(
                f"Error deleting conversation {conversation_id}: {str(e)}",
                exc_info=True
            )
            raise
    
    @staticmethod
    async def update_conversation_name(
        conversation_id: int,
        name: str,
        user_id: Optional[int] = None
    ) -> None:
        """
        Update a conversation's title.
        
        Args:
            conversation_id: ID of the conversation
            name: New title for the conversation
            user_id: Optional user ID for ownership verification
            
        Raises:
            ValueError: If conversation not found or not owned by user
            Exception: If database operation fails
            
        Example:
            await ConversationService.update_conversation_name(
                conversation_id=456,
                name="Python Tutorial",
                user_id=123
            )
            print("Conversation renamed successfully")
        """
        try:
            async with AsyncSessionLocal() as db:
                # Query conversation
                stmt = select(Conversation).where(
                    Conversation.id == conversation_id
                )
                
                # Add user ownership check if user_id provided
                if user_id is not None:
                    stmt = stmt.where(Conversation.user_id == user_id)
                
                result = await db.execute(stmt)
                conversation = result.scalar_one_or_none()
                
                if not conversation:
                    error_msg = f"Conversation {conversation_id} not found"
                    if user_id is not None:
                        error_msg += f" or not owned by user {user_id}"
                    logger.warning(error_msg)
                    raise ValueError(error_msg)
                
                # Update title
                conversation.title = name
                await db.commit()
                
                logger.info(
                    f"Updated conversation {conversation_id} title to: {name}"
                )
                
        except Exception as e:
            logger.error(
                f"Error updating conversation {conversation_id} name: {str(e)}",
                exc_info=True
            )
            raise
    
    @staticmethod
    async def get_conversation_by_id(
        conversation_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Retrieve a single conversation by ID.
        
        Args:
            conversation_id: ID of the conversation
            user_id: Optional user ID for ownership verification
            
        Returns:
            Optional[Dict]: Conversation dictionary if found, None otherwise
            
        Example:
            conversation = await ConversationService.get_conversation_by_id(
                conversation_id=456,
                user_id=123
            )
            if conversation:
                print(f"Found: {conversation['title']}")
        """
        try:
            async with AsyncSessionLocal() as db:
                stmt = select(Conversation).where(
                    Conversation.id == conversation_id
                )
                
                if user_id is not None:
                    stmt = stmt.where(Conversation.user_id == user_id)
                
                result = await db.execute(stmt)
                conversation = result.scalar_one_or_none()
                
                if not conversation:
                    return None
                
                return {
                    "id": conversation.id,
                    "title": conversation.title,
                    "created_at": conversation.created_at.isoformat(),
                    "status": conversation.status,
                    "dialogue_type": conversation.dialogue_type.value,
                    "user_id": conversation.user_id
                }
                
        except Exception as e:
            logger.error(
                f"Error getting conversation {conversation_id}: {str(e)}",
                exc_info=True
            )
            raise
