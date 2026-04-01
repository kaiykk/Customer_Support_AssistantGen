"""
Conversation Management API Endpoints

This module provides API endpoints for managing user conversations,
including creating, retrieving, updating, and deleting conversations.

Author: AssistGen Team
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from app.core.logger import get_logger
from app.services.conversation_service import ConversationService

# Initialize router and logger
router = APIRouter(prefix="/conversations", tags=["Conversations"])
logger = get_logger(service="conversations_api")


# ============================================================================
# Request/Response Models
# ============================================================================

class CreateConversationRequest(BaseModel):
    """Request model for creating a new conversation."""
    user_id: int = Field(..., description="User ID creating the conversation")


class UpdateConversationNameRequest(BaseModel):
    """Request model for updating conversation name."""
    name: str = Field(..., min_length=1, max_length=255, description="New conversation name")


# ============================================================================
# Conversation Endpoints
# ============================================================================

@router.post("")
async def create_conversation(request: CreateConversationRequest):
    """
    Create a new conversation for a user.
    
    Args:
        request: CreateConversationRequest with user_id
        
    Returns:
        dict: Created conversation ID
        
    Raises:
        HTTPException: If conversation creation fails
    """
    try:
        logger.info(f"Creating conversation for user {request.user_id}")
        conversation_id = await ConversationService.create_conversation(request.user_id)
        
        return {
            "conversation_id": conversation_id,
            "message": "Conversation created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create conversation: {str(e)}"
        )


@router.get("/user/{user_id}")
async def get_user_conversations(user_id: int):
    """
    Retrieve all conversations for a specific user.
    
    Args:
        user_id: User ID to retrieve conversations for
        
    Returns:
        List[dict]: List of user conversations
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        logger.info(f"Retrieving conversations for user {user_id}")
        conversations = await ConversationService.get_user_conversations(user_id)
        
        return {
            "conversations": conversations,
            "count": len(conversations)
        }
        
    except Exception as e:
        logger.error(f"Error getting conversations: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve conversations: {str(e)}"
        )


@router.get("/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: int, user_id: int):
    """
    Retrieve all messages in a specific conversation.
    
    Args:
        conversation_id: Conversation ID to retrieve messages from
        user_id: User ID requesting the messages (for authorization)
        
    Returns:
        List[dict]: List of messages in the conversation
        
    Raises:
        HTTPException: If conversation not found or retrieval fails
    """
    try:
        logger.info(f"Retrieving messages for conversation {conversation_id}")
        messages = await ConversationService.get_conversation_messages(
            conversation_id,
            user_id
        )
        
        return {
            "messages": messages,
            "count": len(messages),
            "conversation_id": conversation_id
        }
        
    except ValueError as e:
        # Conversation not found or unauthorized
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting messages: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve messages: {str(e)}"
        )


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: int):
    """
    Delete a conversation and all its messages.
    
    Args:
        conversation_id: Conversation ID to delete
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If deletion fails
    """
    try:
        logger.info(f"Deleting conversation {conversation_id}")
        conversation_service = ConversationService()
        await conversation_service.delete_conversation(conversation_id)
        
        return {
            "message": "Conversation deleted successfully",
            "conversation_id": conversation_id
        }
        
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete conversation: {str(e)}"
        )


@router.put("/{conversation_id}/name")
async def update_conversation_name(
    conversation_id: int,
    request: UpdateConversationNameRequest
):
    """
    Update the name of a conversation.
    
    Args:
        conversation_id: Conversation ID to update
        request: UpdateConversationNameRequest with new name
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If update fails
    """
    try:
        logger.info(f"Updating name for conversation {conversation_id}")
        conversation_service = ConversationService()
        await conversation_service.update_conversation_name(
            conversation_id,
            request.name
        )
        
        return {
            "message": "Conversation name updated successfully",
            "conversation_id": conversation_id,
            "new_name": request.name
        }
        
    except Exception as e:
        logger.error(f"Error updating conversation name: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update conversation name: {str(e)}"
        )
