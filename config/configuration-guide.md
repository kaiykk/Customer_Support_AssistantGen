# Configuration Guide

This guide explains all configuration parameters for the AssistGen system.

## Environment Files

The system uses environment-specific configuration files:

- `development.env.example` - Development environment template
- `staging.env.example` - Staging environment template  
- `production.env.example` - Production environment template

## Setup Instructions

1. Copy the appropriate `.env.example` file to `.env`:
   ```bash
   cp config/development.env.example backend/.env
   ```

2. Update the values in `.env` according to your environment

3. Never commit `.env` files to version control

## Configuration Parameters

### LLM Service Configuration

#### Service Selection
- `CHAT_SERVICE`: LLM service for chat functionality (`deepseek` or `ollama`)
- `REASON_SERVICE`: LLM service for reasoning tasks (`deepseek` or `ollama`)
- `AGENT_SERVICE`: LLM service for agent workflows (`deepseek` or `ollama`)

#### DeepSeek Configuration
- `DEEPSEEK_API_KEY`: Your DeepSeek API key (required if using DeepSeek)
- `DEEPSEEK_BASE_URL`: DeepSeek API base URL (default: `https://api.deepseek.com/v1`)
- `DEEPSEEK_MODEL`: Model name to use (e.g., `deepseek-chat`)

#### Vision Model Configuration
- `VISION_API_KEY`: API key for vision/image processing model
- `VISION_BASE_URL`: Vision model API base URL
- `VISION_MODEL`: Vision model name (e.g., `deepseek-vl`)

#### Ollama Configuration
- `OLLAMA_BASE_URL`: Ollama server URL (default: `http://localhost:11434`)
- `OLLAMA_CHAT_MODEL`: Model for chat (e.g., `qwen2.5:7b`)
- `OLLAMA_REASON_MODEL`: Model for reasoning (e.g., `deepseek-r1:7b`)
- `OLLAMA_EMBEDDING_MODEL`: Model for embeddings (e.g., `bge-m3`)
- `OLLAMA_AGENT_MODEL`: Model for agent workflows

### Database Configuration

#### MySQL
- `DB_HOST`: MySQL server hostname
- `DB_PORT`: MySQL server port (default: `3306`)
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_NAME`: Database name

#### Neo4j
- `NEO4J_URL`: Neo4j connection URL (e.g., `bolt://localhost:7687`)
- `NEO4J_USERNAME`: Neo4j username
- `NEO4J_PASSWORD`: Neo4j password
- `NEO4J_DATABASE`: Neo4j database name

### Redis Configuration

- `REDIS_HOST`: Redis server hostname
- `REDIS_PORT`: Redis server port (default: `6379`)
- `REDIS_DB`: Redis database number (default: `0`)
- `REDIS_PASSWORD`: Redis password (leave empty if no password)
- `REDIS_CACHE_EXPIRE`: Cache expiration time in seconds (default: `3600`)
- `REDIS_CACHE_THRESHOLD`: Similarity threshold for semantic caching (default: `0.8`)

### Security Configuration

- `SECRET_KEY`: Secret key for JWT token signing (MUST be strong and random in production)
- `ALGORITHM`: JWT algorithm (default: `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes (default: `30`)

### Search Configuration

- `SERPAPI_KEY`: SerpAPI key for web search functionality
- `SEARCH_RESULT_COUNT`: Number of search results to return (default: `3`)

### Embedding Configuration

- `EMBEDDING_TYPE`: Embedding service type (`ollama` or `sentence_transformer`)
- `EMBEDDING_MODEL`: Embedding model name
- `EMBEDDING_THRESHOLD`: Similarity threshold for semantic matching (default: `0.90`)

### GraphRAG Configuration

- `GRAPHRAG_PROJECT_DIR`: GraphRAG project directory path
- `GRAPHRAG_DATA_DIR`: Data directory name within project
- `GRAPHRAG_QUERY_TYPE`: Query type (`local` or `global`)
- `GRAPHRAG_RESPONSE_TYPE`: Response format (`text` or `json`)
- `GRAPHRAG_COMMUNITY_LEVEL`: Community detection level (default: `3`)
- `GRAPHRAG_DYNAMIC_COMMUNITY`: Enable dynamic community selection (`true` or `false`)

### Application Configuration

- `HOST`: Server bind address (default: `0.0.0.0`)
- `PORT`: Server port (default: `8000`)
- `DEBUG`: Enable debug mode (`true` or `false`)
- `RELOAD`: Enable auto-reload on code changes (`true` or `false`)
- `CORS_ORIGINS`: Comma-separated list of allowed CORS origins
- `LOG_LEVEL`: Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- `LOG_FILE`: Log file path

## Validation

The system validates configuration on startup. Run validation manually:

```bash
python backend/app/core/config_validator.py
```

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use strong random keys** for `SECRET_KEY` in production
3. **Rotate credentials regularly** in production environments
4. **Use environment-specific configurations** (don't use dev config in production)
5. **Restrict database access** to only necessary hosts
6. **Enable HTTPS** in production
7. **Use strong passwords** for all services

## Troubleshooting

### Missing Configuration Error

If you see "Missing required configuration" errors:
1. Check that your `.env` file exists in the correct location
2. Verify all required keys are present
3. Run the configuration validator to see specific missing keys

### Invalid Value Format

If you see "Invalid value format" errors:
1. Check that port numbers are valid integers (1-65535)
2. Verify boolean values are `true` or `false`
3. Ensure URLs are properly formatted

### Service Connection Errors

If services can't connect:
1. Verify hostnames and ports are correct
2. Check that services are running
3. Verify network connectivity
4. Check firewall rules
