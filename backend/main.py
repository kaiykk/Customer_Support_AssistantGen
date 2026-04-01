"""
AssistGen Main Application Module

This module serves as the entry point for the AssistGen intelligent customer service system.
It configures the FastAPI application, sets up middleware, and defines all API endpoints.

The application provides:
- Chat functionality with multiple LLM providers (DeepSeek, Ollama)
- Reasoning capabilities for complex queries
- Search-enhanced conversations
- Document upload and RAG (Retrieval-Augmented Generation)
- LangGraph agent workflows
- Conversation management

Author: AssistGen Team
License: MIT
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from langgraph.types import Command
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api import api_router
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.logger import get_logger, log_structured
from app.core.middleware import LoggingMiddleware
from app.lg_agent.lg_builder import graph
from app.lg_agent.lg_states import AgentState, InputState
from app.lg_agent.utils import new_uuid
from app.models.conversation import Conversation, DialogueType
from app.models.message import Message
from app.services.conversation_service import ConversationService
from app.services.indexing_service import IndexingService
from app.services.llm_factory import LLMFactory

# Configure upload directory for RAG functionality
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize logger for this module
logger = get_logger(service="main")

# Create FastAPI application instance
app = FastAPI(
    title="AssistGen REST API",
    description="Intelligent Customer Service System with Multi-LLM Support",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add logging middleware to replace FastAPI's default logging
app.add_middleware(LoggingMiddleware)

# Configure CORS (Cross-Origin Resource Sharing)
# In production, replace "*" with specific allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if hasattr(settings, 'CORS_ORIGINS') else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication and user management routes
app.include_router(api_router, prefix="/api")


# ============================================================================
# Request/Response Models
# ============================================================================

class ReasonRequest(BaseModel):
    """Request model for reasoning endpoint."""
    messages: List[Dict[str, str]] = Field(..., description="List of conversation messages")
    user_id: int = Field(..., description="User ID making the request")


class ChatMessage(BaseModel):
    """Request model for chat endpoint."""
    messages: List[Dict[str, str]] = Field(..., description="List of conversation messages")
    user_id: int = Field(..., description="User ID making the request")
    conversation_id: int = Field(..., description="Conversation ID for message history")


class RAGChatRequest(BaseModel):
    """Request model for RAG (Retrieval-Augmented Generation) chat."""
    messages: List[Dict[str, str]] = Field(..., description="List of conversation messages")
    index_id: str = Field(..., description="Document index ID for context retrieval")
    user_id: int = Field(..., description="User ID making the request")


class CreateConversationRequest(BaseModel):
    """Request model for creating a new conversation."""
    user_id: int = Field(..., description="User ID creating the conversation")


class UpdateConversationNameRequest(BaseModel):
    """Request model for updating conversation name."""
    name: str = Field(..., description="New name for the conversation")


class LangGraphResumeRequest(BaseModel):
    """Request model for resuming LangGraph workflow."""
    query: str = Field(..., description="User query to resume with")
    user_id: int = Field(..., description="User ID making the request")
    conversation_id: str = Field(..., description="Conversation ID to resume")


# ============================================================================
# Health Check Endpoint
# ============================================================================

@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint to verify the service is running.
    
    Returns:
        dict: Status information
    """
    return {
        "status": "ok",
        "service": "AssistGen",
        "version": "2.0.0"
    }


# ============================================================================
# Chat Endpoints
# ============================================================================

@app.post("/api/chat", tags=["Chat"])
async def chat_endpoint(request: ChatMessage):
    """
    Handle chat requests with streaming responses.
    
    This endpoint processes user messages and returns AI-generated responses
    in a streaming fashion using Server-Sent Events (SSE).
    
    Args:
        request: ChatMessage containing messages, user_id, and conversation_id
        
    Returns:
        StreamingResponse: Server-sent events stream with AI responses
        
    Raises:
        HTTPException: If chat processing fails
    """
    try:
        logger.info(
            f"Processing chat request for user {request.user_id} "
            f"in conversation {request.conversation_id}"
        )
        
        # Validate request
        if not request.messages:
            raise HTTPException(status_code=400, detail="Messages cannot be empty")
        
        # Create chat service instance
        chat_service = LLMFactory.create_chat_service()
        
        # Return streaming response
        return StreamingResponse(
            chat_service.generate_stream(
                messages=request.messages,
                user_id=request.user_id,
                conversation_id=request.conversation_id,
                on_complete=ConversationService.save_message
            ),
            media_type="text/event-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat request: {str(e)}"
        )


@app.post("/api/reason", tags=["Chat"])
async def reason_endpoint(request: ReasonRequest):
    """
    Handle reasoning requests for complex queries.
    
    This endpoint uses advanced reasoning capabilities to process
    complex user queries that require deeper analysis.
    
    Args:
        request: ReasonRequest containing messages and user_id
        
    Returns:
        StreamingResponse: Server-sent events stream with reasoning responses
        
    Raises:
        HTTPException: If reasoning processing fails
    """
    try:
        logger.info(f"Processing reasoning request for user {request.user_id}")
        
        # Validate request
        if not request.messages:
            raise HTTPException(status_code=400, detail="Messages cannot be empty")
        
        # Create reasoner service instance
        reasoner = LLMFactory.create_reasoner_service()
        
        # Log structured data for analytics
        log_structured("reason_request", {
            "user_id": request.user_id,
            "message_count": len(request.messages),
            "last_message": request.messages[-1]["content"][:100] + "..."
        })
        
        # Return streaming response
        return StreamingResponse(
            reasoner.generate_stream(request.messages),
            media_type="text/event-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Reasoning error for user {request.user_id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process reasoning request: {str(e)}"
        )


@app.post("/api/search", tags=["Chat"])
async def search_endpoint(request: ChatMessage):
    """
    Handle search-enhanced chat requests.
    
    This endpoint combines web search capabilities with chat functionality
    to provide more informed and up-to-date responses.
    
    Args:
        request: ChatMessage containing messages, user_id, and conversation_id
        
    Returns:
        StreamingResponse: Server-sent events stream with search-enhanced responses
        
    Raises:
        HTTPException: If search processing fails
    """
    try:
        logger.info(
            f"Processing search request for user {request.user_id} "
            f"in conversation {request.conversation_id}"
        )
        
        # Validate request
        if not request.messages or not request.messages[0].get("content"):
            raise HTTPException(status_code=400, detail="Query content cannot be empty")
        
        # Create search service instance
        search_service = LLMFactory.create_search_service()
        
        # Return streaming response
        return StreamingResponse(
            search_service.generate_stream(
                query=request.messages[0]["content"],
                user_id=request.user_id,
                conversation_id=request.conversation_id,
            ),
            media_type="text/event-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process search request: {str(e)}"
        )


# ============================================================================
# File Upload Endpoints
# ============================================================================

@app.post("/api/upload", tags=["Files"])
async def upload_file(
    file: UploadFile = File(...),
    user_id: int = Form(...)
):
    """
    Upload a file for RAG (Retrieval-Augmented Generation) processing.
    
    This endpoint handles file uploads, stores them in a structured directory,
    and processes them for document indexing.
    
    Args:
        file: Uploaded file
        user_id: User ID uploading the file
        
    Returns:
        dict: File information including path, size, and index result
        
    Raises:
        HTTPException: If file upload or processing fails
    """
    try:
        logger.info(f"Uploading file for user {user_id}: {file.filename}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename cannot be empty")
        
        # Create user-specific directory using UUID
        user_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"user_{user_id}"))
        first_level_dir = UPLOAD_DIR / user_uuid
        
        # Create timestamp-based subdirectory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        second_level_dir = first_level_dir / timestamp
        second_level_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamped filename
        original_name, ext = os.path.splitext(file.filename)
        new_filename = f"{original_name}_{timestamp}{ext}"
        file_path = second_level_dir / new_filename
        
        # Save file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Prepare file information
        file_info = {
            "filename": new_filename,
            "original_name": file.filename,
            "size": len(content),
            "type": file.content_type,
            "path": str(file_path).replace('\\', '/'),
            "user_id": user_id,
            "user_uuid": user_uuid,
            "upload_time": timestamp,
            "directory": str(second_level_dir)
        }
        
        # Process file for indexing
        indexing_service = IndexingService()
        index_result = await indexing_service.process_file(file_info)
        
        # Merge results
        result = {**file_info, "index_result": index_result}
        
        logger.info(f"File uploaded successfully: {new_filename}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed for user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file: {str(e)}"
        )


@app.post("/api/upload/image", tags=["Files"])
async def upload_image(
    image: UploadFile = File(...),
    user_id: int = Form(...),
    conversation_id: Optional[str] = Form(None)
):
    """
    Upload an image file.
    
    This endpoint handles image uploads and stores them in a structured directory.
    Images can be associated with specific conversations.
    
    Args:
        image: Uploaded image file
        user_id: User ID uploading the image
        conversation_id: Optional conversation ID to associate with
        
    Returns:
        dict: Image information including path and metadata
        
    Raises:
        HTTPException: If image upload fails
    """
    try:
        logger.info(f"Uploading image for user {user_id}")
        
        # Validate image file
        if not image.filename:
            raise HTTPException(status_code=400, detail="Image filename cannot be empty")
        
        # Create image storage directory
        image_dir = Path("uploads/images")
        if conversation_id:
            image_dir = image_dir / conversation_id
        image_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_name, ext = os.path.splitext(image.filename)
        new_filename = f"{original_name}_{timestamp}{ext}"
        image_path = image_dir / new_filename
        
        # Save image
        content = await image.read()
        with open(image_path, "wb") as f:
            f.write(content)
        
        # Prepare image information
        image_info = {
            "filename": new_filename,
            "original_name": image.filename,
            "size": len(content),
            "type": image.content_type,
            "path": str(image_path).replace('\\', '/'),
            "user_id": user_id,
            "conversation_id": conversation_id,
            "upload_time": timestamp
        }
        
        logger.info(f"Image uploaded successfully: {new_filename}")
        return image_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image upload failed for user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image: {str(e)}"
        )


# ============================================================================
# Conversation Management Endpoints
# ============================================================================

# Import and include conversation router
from app.api.conversations import router as conversations_router
app.include_router(conversations_router, prefix="/api")


# ============================================================================
# LangGraph Agent Endpoints
# ============================================================================

@app.post("/api/langgraph/query", tags=["Agent"])
async def langgraph_query(
    query: str = Form(...),
    user_id: int = Form(...),
    conversation_id: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None)
):
    """
    Process user query using LangGraph agent workflow.
    
    This endpoint uses LangGraph to handle complex multi-step agent workflows,
    supporting both text and image inputs.
    
    Args:
        query: User query text
        user_id: User ID making the request
        conversation_id: Optional conversation ID for context
        image: Optional image file for multimodal processing
        
    Returns:
        StreamingResponse: Server-sent events stream with agent responses
        
    Raises:
        HTTPException: If query processing fails
    """
    try:
        logger.info(
            f"Processing LangGraph query for user {user_id} "
            f"and conversation {conversation_id}"
        )
        
        # Validate query
        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Handle image upload if provided
        image_path = None
        if image:
            image_dir = Path("uploads/images")
            image_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_name, ext = os.path.splitext(image.filename)
            new_filename = f"{original_name}_{timestamp}{ext}"
            image_path = image_dir / new_filename
            
            content = await image.read()
            with open(image_path, "wb") as f:
                f.write(content)
            
            logger.info(f"Saved image {new_filename} for user {user_id}")
        
        # Use conversation_id as thread_id, or create new one
        thread_id = conversation_id if conversation_id else new_uuid()
        thread_config = {
            "configurable": {
                "thread_id": thread_id,
                "user_id": user_id,
                "image_path": str(image_path) if image_path else None
            }
        }
        
        # Check for existing conversation state
        state_history = None
        try:
            if thread_id:
                state_history = graph.get_state(thread_config)
                if state_history:
                    logger.info(f"Found existing state for thread_id: {thread_id}")
        except Exception as e:
            logger.warning(f"Error retrieving state: {e}. Starting fresh.")
        
        # Process query based on conversation state
        async def process_stream():
            """Generate streaming response from LangGraph."""
            if state_history and len(state_history) > 0 and len(state_history[-1]) > 0:
                # Resume existing conversation
                logger.info("Using existing conversation state")
                async for c, metadata in graph.astream(
                    Command(resume=query),
                    stream_mode="messages",
                    config=thread_config
                ):
                    if c.content and "research_plan" not in metadata.get("tags", []) \
                            and not c.additional_kwargs.get("tool_calls"):
                        content_json = json.dumps(c.content, ensure_ascii=False)
                        yield f"data: {content_json}\n\n"
                    elif c.additional_kwargs.get("tool_calls"):
                        tool_data = c.additional_kwargs.get("tool_calls")[0]["function"].get("arguments")
                        logger.debug(f"Tool call: {tool_data}")
            else:
                # Start new conversation
                logger.info("Creating new conversation state")
                input_state = InputState(messages=query)
                async for c, metadata in graph.astream(
                    input=input_state,
                    stream_mode="messages",
                    config=thread_config
                ):
                    if c.content and "research_plan" not in metadata.get("tags", []) \
                            and not c.additional_kwargs.get("tool_calls"):
                        content_json = json.dumps(c.content, ensure_ascii=False)
                        yield f"data: {content_json}\n\n"
                    elif c.additional_kwargs.get("tool_calls"):
                        tool_data = c.additional_kwargs.get("tool_calls")[0]["function"].get("arguments")
                        logger.debug(f"Tool call: {tool_data}")
            
            # Handle interruptions
            state = graph.get_state(thread_config)
            if len(state) > 0 and len(state[-1]) > 0:
                if len(state[-1][0].interrupts) > 0:
                    interrupt_json = json.dumps({
                        "interruption": True,
                        "conversation_id": thread_id
                    })
                    yield f"data: {interrupt_json}\n\n"
        
        response = StreamingResponse(
            process_stream(),
            media_type="text/event-stream"
        )
        
        # Add conversation ID to response headers
        response.headers["X-Conversation-ID"] = thread_id
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LangGraph query error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process LangGraph query: {str(e)}"
        )


@app.post("/api/langgraph/resume", tags=["Agent"])
async def langgraph_resume(request: LangGraphResumeRequest):
    """
    Resume a paused LangGraph workflow.
    
    This endpoint continues execution of a previously interrupted
    LangGraph agent workflow.
    
    Args:
        request: LangGraphResumeRequest with query, user_id, and conversation_id
        
    Returns:
        StreamingResponse: Server-sent events stream with agent responses
        
    Raises:
        HTTPException: If resume processing fails
    """
    try:
        logger.info(
            f"Resuming LangGraph query for user {request.user_id} "
            f"with conversation {request.conversation_id}"
        )
        
        # Validate request
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        if not request.conversation_id:
            raise HTTPException(status_code=400, detail="Conversation ID is required")
        
        # Configure thread
        thread_config = {
            "configurable": {
                "thread_id": request.conversation_id
            }
        }
        
        # Process resume
        async def process_resume():
            """Generate streaming response for resumed workflow."""
            async for c, metadata in graph.astream(
                Command(resume=request.query),
                stream_mode="messages",
                config=thread_config
            ):
                if c.content and not c.additional_kwargs.get("tool_calls"):
                    content_json = json.dumps(c.content, ensure_ascii=False)
                    yield f"data: {content_json}\n\n"
                elif c.additional_kwargs.get("tool_calls"):
                    tool_data = c.additional_kwargs.get("tool_calls")[0]["function"].get("arguments")
                    logger.debug(f"Tool call: {tool_data}")
        
        return StreamingResponse(
            process_resume(),
            media_type="text/event-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LangGraph resume error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resume LangGraph workflow: {str(e)}"
        )


# ============================================================================
# Static Files
# ============================================================================

# Mount static files for frontend (must be last to avoid route conflicts)
STATIC_DIR = Path(__file__).parent / "static" / "dist"
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
    logger.info(f"Mounted static files from: {STATIC_DIR}")
else:
    logger.warning(f"Static directory not found: {STATIC_DIR}")


# ============================================================================
# Application Startup and Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Execute tasks on application startup.
    
    This function runs when the FastAPI application starts,
    performing initialization tasks like database connections.
    """
    logger.info("AssistGen application starting up...")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    logger.info(f"Chat Service: {settings.CHAT_SERVICE}")
    logger.info(f"Reason Service: {settings.REASON_SERVICE}")
    
    # Validate configuration
    try:
        from app.core.config_validator import validate_config
        validate_config()
        logger.info("Configuration validation passed")
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        # In production, you might want to exit here
        if not settings.DEBUG:
            import sys
            sys.exit(1)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Execute cleanup tasks on application shutdown.
    
    This function runs when the FastAPI application shuts down,
    performing cleanup tasks like closing database connections.
    """
    logger.info("AssistGen application shutting down...")
    # Add any cleanup tasks here (e.g., close database connections)


if __name__ == "__main__":
    """
    Run the application directly (for development only).
    
    In production, use a proper ASGI server like uvicorn:
        uvicorn main:app --host 0.0.0.0 --port 8000
    """
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST if hasattr(settings, 'HOST') else "0.0.0.0",
        port=settings.PORT if hasattr(settings, 'PORT') else 8000,
        reload=settings.DEBUG if hasattr(settings, 'DEBUG') else True,
        log_level="info"
    )
