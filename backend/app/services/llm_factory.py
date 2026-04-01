"""
LLM Factory Module

This module provides a factory pattern for creating LLM (Large Language Model)
service instances. It abstracts the creation logic and allows switching between
different LLM providers based on configuration.

Key Features:
- Factory pattern for LLM service creation
- Support for multiple LLM providers (DeepSeek, Ollama)
- Configuration-based service selection
- Separate services for chat and reasoning tasks
- Search service integration

Supported Providers:
- DeepSeek: Commercial API service
- Ollama: Local/self-hosted LLM service

Usage:
    from app.services import LLMFactory
    
    # Create chat service based on configuration
    chat_service = LLMFactory.create_chat_service()
    response = await chat_service.chat(messages)
    
    # Create reasoning service
    reasoner = LLMFactory.create_reasoner_service()
    result = await reasoner.reason(prompt)
    
    # Create search service
    search = LLMFactory.create_search_service()
    results = await search.search(query)
"""

from typing import Union

from app.core.config import settings, ServiceType
from app.services.deepseek_service import DeepseekService
from app.services.ollama_service import OllamaService
from app.services.search_service import SearchService
from app.core.logger import get_logger

logger = get_logger(service="llm_factory")


class LLMFactory:
    """
    Factory class for creating LLM service instances.
    
    This class implements the Factory design pattern to create appropriate
    LLM service instances based on application configuration. It allows
    easy switching between different LLM providers without changing
    application code.
    
    The factory supports:
    - Chat services for conversational interactions
    - Reasoning services for complex problem-solving
    - Search services for information retrieval
    
    Configuration:
        LLM providers are configured via environment variables:
        - CHAT_SERVICE: Provider for chat interactions (DEEPSEEK or OLLAMA)
        - REASON_SERVICE: Provider for reasoning tasks (DEEPSEEK or OLLAMA)
    """
    
    @staticmethod
    def create_chat_service() -> Union[DeepseekService, OllamaService]:
        """
        Create a chat service instance based on configuration.
        
        This method creates the appropriate LLM service for handling
        conversational chat interactions. The service type is determined
        by the CHAT_SERVICE configuration setting.
        
        Returns:
            Union[DeepseekService, OllamaService]: Chat service instance
            
        Example:
            chat_service = LLMFactory.create_chat_service()
            
            messages = [
                {"role": "user", "content": "Hello!"}
            ]
            response = await chat_service.chat(messages)
            print(response)
            
        Configuration:
            Set CHAT_SERVICE in .env file:
            - CHAT_SERVICE=DEEPSEEK  # Use DeepSeek API
            - CHAT_SERVICE=OLLAMA    # Use local Ollama
            
        Note:
            - DeepSeek requires API key configuration
            - Ollama requires local installation and running service
        """
        if settings.CHAT_SERVICE == ServiceType.DEEPSEEK:
            logger.info("Creating DeepSeek chat service")
            return DeepseekService()
        else:
            logger.info("Creating Ollama chat service")
            return OllamaService()
    
    @staticmethod
    def create_reasoner_service() -> Union[DeepseekService, OllamaService]:
        """
        Create a reasoning service instance based on configuration.
        
        This method creates the appropriate LLM service for handling
        complex reasoning and problem-solving tasks. The service type
        is determined by the REASON_SERVICE configuration setting.
        
        Reasoning services are typically used for:
        - Complex problem decomposition
        - Multi-step logical reasoning
        - Code analysis and generation
        - Mathematical problem solving
        
        Returns:
            Union[DeepseekService, OllamaService]: Reasoning service instance
            
        Example:
            reasoner = LLMFactory.create_reasoner_service()
            
            problem = "Solve this complex problem: ..."
            solution = await reasoner.reason(problem)
            print(solution)
            
        Configuration:
            Set REASON_SERVICE in .env file:
            - REASON_SERVICE=DEEPSEEK  # Use DeepSeek API
            - REASON_SERVICE=OLLAMA    # Use local Ollama
            
        Note:
            - Reasoning tasks may require more powerful models
            - Consider using different models for chat vs reasoning
            - DeepSeek's reasoning models are optimized for complex tasks
        """
        if settings.REASON_SERVICE == ServiceType.DEEPSEEK:
            logger.info("Creating DeepSeek reasoning service")
            return DeepseekService()
        else:
            logger.info("Creating Ollama reasoning service")
            return OllamaService()
    
    @staticmethod
    def create_search_service() -> SearchService:
        """
        Create a search service instance.
        
        This method creates a search service for information retrieval
        and search-enhanced chat functionality. The search service
        integrates with external search APIs and knowledge bases.
        
        Returns:
            SearchService: Search service instance
            
        Example:
            search_service = LLMFactory.create_search_service()
            
            query = "What is Python?"
            results = await search_service.search(query)
            for result in results:
                print(f"{result['title']}: {result['url']}")
            
            # Search-enhanced chat
            response = await search_service.search_chat(
                query="Latest Python features",
                messages=conversation_history
            )
            
        Features:
            - Web search integration
            - Knowledge base queries
            - Search result ranking
            - Context-aware search
            - Search-enhanced chat responses
            
        Note:
            - Search service may require API keys for external search providers
            - Configure search providers in .env file
        """
        logger.info("Creating search service")
        return SearchService()
    
    @staticmethod
    def get_available_services() -> dict:
        """
        Get information about available LLM services.
        
        This method returns configuration information about which
        LLM services are currently configured and available.
        
        Returns:
            dict: Dictionary containing service configuration
            
        Example:
            services = LLMFactory.get_available_services()
            print(f"Chat service: {services['chat_service']}")
            print(f"Reasoning service: {services['reason_service']}")
            
        Response Format:
            {
                "chat_service": "DEEPSEEK",
                "reason_service": "OLLAMA",
                "search_available": True
            }
        """
        return {
            "chat_service": settings.CHAT_SERVICE.value,
            "reason_service": settings.REASON_SERVICE.value,
            "search_available": True
        }
    
    @staticmethod
    def validate_configuration() -> bool:
        """
        Validate that LLM services are properly configured.
        
        This method checks that all required configuration settings
        are present and valid for the selected LLM providers.
        
        Returns:
            bool: True if configuration is valid, False otherwise
            
        Example:
            if LLMFactory.validate_configuration():
                print("LLM services configured correctly")
            else:
                print("Configuration error - check .env file")
                
        Validation Checks:
            - CHAT_SERVICE is set to valid provider
            - REASON_SERVICE is set to valid provider
            - Required API keys are present for selected providers
            - Service endpoints are accessible (if applicable)
        """
        try:
            # Check chat service configuration
            if settings.CHAT_SERVICE not in [ServiceType.DEEPSEEK, ServiceType.OLLAMA]:
                logger.error(f"Invalid CHAT_SERVICE: {settings.CHAT_SERVICE}")
                return False
            
            # Check reasoning service configuration
            if settings.REASON_SERVICE not in [ServiceType.DEEPSEEK, ServiceType.OLLAMA]:
                logger.error(f"Invalid REASON_SERVICE: {settings.REASON_SERVICE}")
                return False
            
            # Check DeepSeek API key if DeepSeek is configured
            if (settings.CHAT_SERVICE == ServiceType.DEEPSEEK or 
                settings.REASON_SERVICE == ServiceType.DEEPSEEK):
                if not hasattr(settings, 'DEEPSEEK_API_KEY') or not settings.DEEPSEEK_API_KEY:
                    logger.error("DeepSeek configured but DEEPSEEK_API_KEY not set")
                    return False
            
            # Check Ollama configuration if Ollama is configured
            if (settings.CHAT_SERVICE == ServiceType.OLLAMA or 
                settings.REASON_SERVICE == ServiceType.OLLAMA):
                if not hasattr(settings, 'OLLAMA_BASE_URL') or not settings.OLLAMA_BASE_URL:
                    logger.warning("Ollama configured but OLLAMA_BASE_URL not set, using default")
            
            logger.info("LLM service configuration validated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error validating LLM configuration: {e}", exc_info=True)
            return False
