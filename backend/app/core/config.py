"""
Configuration Module

This module manages all application configuration settings using Pydantic.
It loads configuration from environment variables and provides type-safe
access to settings throughout the application.

Configuration is loaded from a .env file in the project root directory.
All sensitive information should be stored in environment variables.

Author: AssistGen Team
License: MIT
"""

from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


# Determine project root directory
ROOT_DIR = Path(__file__).parent.parent.parent
ENV_FILE = ROOT_DIR / ".env"


class ServiceType(str, Enum):
    """
    Enumeration of supported LLM service types.
    
    Attributes:
        DEEPSEEK: DeepSeek API service
        OLLAMA: Ollama local service
    """
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    This class uses Pydantic to validate and parse configuration from
    environment variables. All settings are type-checked and validated
    at application startup.
    
    Attributes:
        DEEPSEEK_API_KEY: API key for DeepSeek service
        DEEPSEEK_BASE_URL: Base URL for DeepSeek API
        DEEPSEEK_MODEL: Model name for DeepSeek
        VISION_API_KEY: API key for vision model
        VISION_BASE_URL: Base URL for vision API
        VISION_MODEL: Vision model name
        OLLAMA_BASE_URL: Base URL for Ollama service
        OLLAMA_CHAT_MODEL: Ollama model for chat
        OLLAMA_REASON_MODEL: Ollama model for reasoning
        OLLAMA_EMBEDDING_MODEL: Ollama model for embeddings
        OLLAMA_AGENT_MODEL: Ollama model for agent workflows
        CHAT_SERVICE: Selected service for chat functionality
        REASON_SERVICE: Selected service for reasoning
        AGENT_SERVICE: Selected service for agent workflows
        SERPAPI_KEY: API key for SerpAPI search
        SEARCH_RESULT_COUNT: Number of search results to return
        DB_HOST: MySQL database host
        DB_PORT: MySQL database port
        DB_USER: MySQL database username
        DB_PASSWORD: MySQL database password
        DB_NAME: MySQL database name
        NEO4J_URL: Neo4j connection URL
        NEO4J_USERNAME: Neo4j username
        NEO4J_PASSWORD: Neo4j password
        NEO4J_DATABASE: Neo4j database name
        SECRET_KEY: Secret key for JWT token signing
        ALGORITHM: JWT algorithm
        ACCESS_TOKEN_EXPIRE_MINUTES: JWT token expiration time
        REDIS_HOST: Redis server host
        REDIS_PORT: Redis server port
        REDIS_DB: Redis database number
        REDIS_PASSWORD: Redis password
        REDIS_CACHE_EXPIRE: Cache expiration time in seconds
        REDIS_CACHE_THRESHOLD: Semantic similarity threshold for caching
        EMBEDDING_TYPE: Type of embedding service
        EMBEDDING_MODEL: Embedding model name
        EMBEDDING_THRESHOLD: Similarity threshold for embeddings
        GRAPHRAG_PROJECT_DIR: GraphRAG project directory
        GRAPHRAG_DATA_DIR: GraphRAG data directory
        GRAPHRAG_QUERY_TYPE: GraphRAG query type
        GRAPHRAG_RESPONSE_TYPE: GraphRAG response type
        GRAPHRAG_COMMUNITY_LEVEL: GraphRAG community detection level
        GRAPHRAG_DYNAMIC_COMMUNITY: Enable dynamic community selection
    """
    
    # ========================================================================
    # LLM Service Configuration
    # ========================================================================
    
    # DeepSeek settings
    DEEPSEEK_API_KEY: str = Field(
        ...,
        description="API key for DeepSeek service"
    )
    DEEPSEEK_BASE_URL: str = Field(
        default="https://api.deepseek.com/v1",
        description="Base URL for DeepSeek API"
    )
    DEEPSEEK_MODEL: str = Field(
        default="deepseek-chat",
        description="Model name for DeepSeek"
    )
    
    # Vision Model settings
    VISION_API_KEY: str = Field(
        ...,
        description="API key for vision model"
    )
    VISION_BASE_URL: str = Field(
        default="https://api.deepseek.com/v1",
        description="Base URL for vision API"
    )
    VISION_MODEL: str = Field(
        default="deepseek-vl",
        description="Vision model name"
    )
    
    # Ollama settings
    OLLAMA_BASE_URL: str = Field(
        default="http://localhost:11434",
        description="Base URL for Ollama service"
    )
    OLLAMA_CHAT_MODEL: str = Field(
        default="qwen2.5:7b",
        description="Ollama model for chat"
    )
    OLLAMA_REASON_MODEL: str = Field(
        default="deepseek-r1:7b",
        description="Ollama model for reasoning"
    )
    OLLAMA_EMBEDDING_MODEL: str = Field(
        default="bge-m3",
        description="Ollama model for embeddings"
    )
    OLLAMA_AGENT_MODEL: str = Field(
        default="qwen2.5:7b",
        description="Ollama model for agent workflows"
    )
    
    # Service selection
    CHAT_SERVICE: ServiceType = Field(
        default=ServiceType.DEEPSEEK,
        description="Selected service for chat functionality"
    )
    REASON_SERVICE: ServiceType = Field(
        default=ServiceType.OLLAMA,
        description="Selected service for reasoning"
    )
    AGENT_SERVICE: ServiceType = Field(
        default=ServiceType.DEEPSEEK,
        description="Selected service for agent workflows"
    )
    
    # ========================================================================
    # Search Configuration
    # ========================================================================
    
    SERPAPI_KEY: str = Field(
        ...,
        description="API key for SerpAPI search"
    )
    SEARCH_RESULT_COUNT: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of search results to return"
    )
    
    # ========================================================================
    # Database Configuration
    # ========================================================================
    
    # MySQL settings
    DB_HOST: str = Field(..., description="MySQL database host")
    DB_PORT: int = Field(default=3306, ge=1, le=65535, description="MySQL database port")
    DB_USER: str = Field(..., description="MySQL database username")
    DB_PASSWORD: str = Field(..., description="MySQL database password")
    DB_NAME: str = Field(..., description="MySQL database name")
    
    # Neo4j settings
    NEO4J_URL: str = Field(
        default="bolt://localhost:7687",
        description="Neo4j connection URL"
    )
    NEO4J_USERNAME: str = Field(
        default="neo4j",
        description="Neo4j username"
    )
    NEO4J_PASSWORD: str = Field(
        default="password",
        description="Neo4j password"
    )
    NEO4J_DATABASE: str = Field(
        default="neo4j",
        description="Neo4j database name"
    )
    
    # ========================================================================
    # Security Configuration
    # ========================================================================
    
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        min_length=32,
        description="Secret key for JWT token signing (must be changed in production)"
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        ge=1,
        description="JWT token expiration time in minutes"
    )
    
    # ========================================================================
    # Redis Configuration
    # ========================================================================
    
    REDIS_HOST: str = Field(..., description="Redis server host")
    REDIS_PORT: int = Field(default=6379, ge=1, le=65535, description="Redis server port")
    REDIS_DB: int = Field(default=0, ge=0, le=15, description="Redis database number")
    REDIS_PASSWORD: str = Field(default="", description="Redis password")
    REDIS_CACHE_EXPIRE: int = Field(
        default=3600,
        ge=60,
        description="Cache expiration time in seconds"
    )
    REDIS_CACHE_THRESHOLD: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Semantic similarity threshold for caching"
    )
    
    # ========================================================================
    # Embedding Configuration
    # ========================================================================
    
    EMBEDDING_TYPE: str = Field(
        default="ollama",
        description="Type of embedding service (ollama or sentence_transformer)"
    )
    EMBEDDING_MODEL: str = Field(
        default="bge-m3",
        description="Embedding model name"
    )
    EMBEDDING_THRESHOLD: float = Field(
        default=0.90,
        ge=0.0,
        le=1.0,
        description="Similarity threshold for embeddings"
    )
    
    # ========================================================================
    # GraphRAG Configuration
    # ========================================================================
    
    GRAPHRAG_PROJECT_DIR: str = Field(
        default="backend/app/graphrag",
        description="GraphRAG project directory"
    )
    GRAPHRAG_DATA_DIR: str = Field(
        default="data",
        description="GraphRAG data directory"
    )
    GRAPHRAG_QUERY_TYPE: str = Field(
        default="local",
        description="GraphRAG query type (local or global)"
    )
    GRAPHRAG_RESPONSE_TYPE: str = Field(
        default="text",
        description="GraphRAG response type (text or json)"
    )
    GRAPHRAG_COMMUNITY_LEVEL: int = Field(
        default=3,
        ge=1,
        description="GraphRAG community detection level"
    )
    GRAPHRAG_DYNAMIC_COMMUNITY: bool = Field(
        default=False,
        description="Enable dynamic community selection"
    )
    
    # ========================================================================
    # Application Configuration
    # ========================================================================
    
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, ge=1, le=65535, description="Server port")
    CORS_ORIGINS: str = Field(
        default="*",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # HTTP Client Configuration
    HTTP_TIMEOUT: int = Field(
        default=30,
        ge=1,
        le=300,
        description="HTTP request timeout in seconds for external API calls"
    )
    HTTP_CONNECT_TIMEOUT: int = Field(
        default=10,
        ge=1,
        le=60,
        description="HTTP connection timeout in seconds"
    )
    HTTP_MAX_RETRIES: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retries for failed HTTP requests"
    )
    
    # ========================================================================
    # Computed Properties
    # ========================================================================
    
    @property
    def DATABASE_URL(self) -> str:
        """
        Construct MySQL database connection URL.
        
        Returns:
            str: SQLAlchemy-compatible database URL
        """
        return (
            f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
    
    @property
    def REDIS_URL(self) -> str:
        """
        Construct Redis connection URL.
        
        Returns:
            str: Redis connection URL
        """
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def NEO4J_CONN_URL(self) -> str:
        """
        Get Neo4j connection URL.
        
        Returns:
            str: Neo4j connection URL
        """
        return self.NEO4J_URL
    
    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        """
        Parse CORS origins string into a list.
        
        Returns:
            List[str]: List of allowed CORS origins
        """
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # ========================================================================
    # Validators
    # ========================================================================
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """
        Validate that SECRET_KEY is not a default value in production.
        
        Args:
            v: Secret key value
            
        Returns:
            str: Validated secret key
            
        Raises:
            ValueError: If using default key in production
        """
        weak_keys = ["your-secret-key", "change-me", "secret", "password"]
        if any(weak in v.lower() for weak in weak_keys):
            import os
            if os.getenv("DEBUG", "false").lower() != "true":
                raise ValueError(
                    "SECRET_KEY appears to be a default value. "
                    "Please use a strong random key in production."
                )
        return v
    
    class Config:
        """Pydantic configuration."""
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env file


# Create global settings instance
settings = Settings()
