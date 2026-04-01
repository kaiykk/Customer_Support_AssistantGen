"""
Pytest configuration and fixtures for backend unit tests.

This module provides common fixtures and setup for unit testing
the AssistGen backend components.
"""

import pytest
from typing import Generator
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_db_session() -> Generator[Mock, None, None]:
    """
    Provide a mock database session for testing.
    
    Yields:
        Mock: A mock database session object
    """
    session = MagicMock()
    yield session
    session.close()


@pytest.fixture
def mock_redis_client() -> Mock:
    """
    Provide a mock Redis client for testing.
    
    Returns:
        Mock: A mock Redis client object
    """
    return MagicMock()


@pytest.fixture
def mock_llm_service() -> Mock:
    """
    Provide a mock LLM service for testing.
    
    Returns:
        Mock: A mock LLM service object
    """
    service = MagicMock()
    service.generate_stream.return_value = iter(["Test", " response"])
    return service


@pytest.fixture
def sample_user_data() -> dict:
    """
    Provide sample user data for testing.
    
    Returns:
        dict: Sample user data dictionary
    """
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "is_active": True,
    }


@pytest.fixture
def sample_conversation_data() -> dict:
    """
    Provide sample conversation data for testing.
    
    Returns:
        dict: Sample conversation data dictionary
    """
    return {
        "id": 1,
        "user_id": 1,
        "name": "Test Conversation",
        "dialogue_type": "chat",
    }


@pytest.fixture
def sample_message_data() -> dict:
    """
    Provide sample message data for testing.
    
    Returns:
        dict: Sample message data dictionary
    """
    return {
        "id": 1,
        "conversation_id": 1,
        "role": "user",
        "content": "Hello, this is a test message",
    }
