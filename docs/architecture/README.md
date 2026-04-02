# AssistGen Architecture Documentation

This document describes the system architecture, design patterns, and data flow of the AssistGen intelligent customer service system.

## System Overview

AssistGen is a modern, scalable intelligent customer service system built with a microservices-inspired architecture. It provides AI-powered chat capabilities with multiple LLM providers, document understanding, and agent-based workflows.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Web Browser │  │ Mobile App   │  │  API Client  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │ HTTPS
┌────────────────────────────▼─────────────────────────────────┐
│                     API Gateway / Load Balancer              │
└────────────────────────────┬─────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────┐
│                    Application Layer (FastAPI)               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Middleware Stack                        │   │
│  │  • Rate Limiting  • Security Headers                 │   │
│  │  • Request Logging  • Error Handling                 │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Endpoints                           │   │
│  │  • Auth  • Chat  • Conversations  • Users            │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Service Layer                           │   │
│  │  • UserService  • ConversationService                │   │
│  │  • LLMFactory  • IndexingService                     │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────────┬─────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│   MySQL/       │  │   Redis Cache   │  │  File Storage  │
│   PostgreSQL   │  │                 │  │   (Uploads)    │
└────────────────┘  └─────────────────┘  └────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│  DeepSeek API  │  │  Ollama Local   │  │   Neo4j Graph  │
│   (External)   │  │   LLM Server    │  │   Database     │
└────────────────┘  └─────────────────┘  └────────────────┘
```

## Architecture Layers

### 1. Presentation Layer (Frontend)

**Technology**: Vue 3 + TypeScript + Vite

**Components**:
- **Views**: Login, Home (Chat Interface)
- **Stores**: User Store, Conversation Store (Pinia)
- **Router**: Vue Router for navigation
- **API Client**: Axios-based HTTP client

**Responsibilities**:
- User interface rendering
- User input handling
- State management
- API communication
- Real-time updates

---

### 2. API Layer (Backend)

**Technology**: FastAPI + Python 3.11+

**Components**:
- **Endpoints**: RESTful API routes
- **Middleware**: Request processing pipeline
- **Authentication**: JWT-based auth
- **Validation**: Pydantic schemas

**Responsibilities**:
- Request routing
- Input validation
- Authentication/authorization
- Response formatting
- Error handling

---

### 3. Service Layer

**Pattern**: Service-oriented architecture

**Services**:

#### UserService
- User registration and authentication
- Profile management
- Password operations
- User queries

#### ConversationService
- Conversation CRUD operations
- Message storage and retrieval
- Conversation history management
- Title generation

#### LLMFactory
- LLM provider abstraction
- DeepSeek API integration
- Ollama integration
- Provider selection logic

#### IndexingService
- Document processing
- Vector embedding generation
- Similarity search
- RAG pipeline

**Responsibilities**:
- Business logic implementation
- Data validation
- External service integration
- Transaction management

---

### 4. Data Layer

**Technology**: SQLAlchemy 2.0 (Async ORM)

**Models**:
- **User**: User accounts and authentication
- **Conversation**: Chat conversations
- **Message**: Individual messages

**Responsibilities**:
- Data persistence
- Relationship management
- Query execution
- Transaction handling

---

### 5. External Services Layer

**Integrations**:

#### LLM Providers
- **DeepSeek API**: Cloud-based LLM service
- **Ollama**: Local LLM deployment

#### Storage
- **MySQL/PostgreSQL**: Relational data
- **Redis**: Caching and session storage
- **Neo4j**: Knowledge graph (optional)
- **File System**: Document uploads

## Design Patterns

### 1. Factory Pattern

Used in `LLMFactory` for creating LLM service instances:

```python
class LLMFactory:
    @staticmethod
    def create_llm_service(provider: str):
        if provider == "deepseek":
            return DeepSeekService()
        elif provider == "ollama":
            return OllamaService()
        else:
            raise ValueError(f"Unknown provider: {provider}")
```

**Benefits**:
- Decouples LLM provider selection from business logic
- Easy to add new providers
- Centralized configuration

---

### 2. Repository Pattern

Service layer acts as repositories for data access:

```python
class ConversationService:
    @staticmethod
    async def get_user_conversations(user_id: int):
        # Data access logic
        ...
```

**Benefits**:
- Separates business logic from data access
- Easier to test (mock repositories)
- Consistent data access patterns

---

### 3. Dependency Injection

FastAPI's dependency injection for database sessions and authentication:

```python
@app.get("/users/me")
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    ...
```

**Benefits**:
- Loose coupling between components
- Easier testing with mock dependencies
- Automatic resource management

---

### 4. Middleware Pattern

Request/response processing pipeline:

```python
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
```

**Benefits**:
- Cross-cutting concerns (logging, security)
- Reusable components
- Clean separation of concerns

## Data Flow

### Authentication Flow

```
┌──────┐                ┌──────────┐              ┌──────────┐
│Client│                │  FastAPI │              │ Database │
└───┬──┘                └────┬─────┘              └────┬─────┘
    │                        │                         │
    │ POST /auth/login       │                         │
    ├───────────────────────>│                         │
    │ {username, password}   │                         │
    │                        │ Query user              │
    │                        ├────────────────────────>│
    │                        │                         │
    │                        │ User data               │
    │                        │<────────────────────────┤
    │                        │                         │
    │                        │ Verify password         │
    │                        │ (bcrypt)                │
    │                        │                         │
    │                        │ Generate JWT tokens     │
    │                        │                         │
    │ {access_token,         │                         │
    │  refresh_token, user}  │                         │
    │<───────────────────────┤                         │
    │                        │                         │
```

### Chat Message Flow

```
┌──────┐         ┌──────────┐         ┌─────────┐         ┌─────────┐
│Client│         │  FastAPI │         │ Service │         │   LLM   │
└───┬──┘         └────┬─────┘         └────┬────┘         └────┬────┘
    │                 │                    │                   │
    │ POST /chat      │                    │                   │
    ├────────────────>│                    │                   │
    │ {message, ...}  │                    │                   │
    │                 │ Validate token     │                   │
    │                 │                    │                   │
    │                 │ Save user message  │                   │
    │                 ├───────────────────>│                   │
    │                 │                    │ Store in DB       │
    │                 │                    │                   │
    │                 │                    │ Call LLM          │
    │                 │                    ├──────────────────>│
    │                 │                    │                   │
    │                 │                    │ Response          │
    │                 │                    │<──────────────────┤
    │                 │                    │                   │
    │                 │ Save assistant msg │                   │
    │                 │<───────────────────┤                   │
    │                 │                    │                   │
    │ {message, ...}  │                    │                   │
    │<────────────────┤                    │                   │
    │                 │                    │                   │
```

### RAG (Document-Based) Flow

```
┌──────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌─────┐
│Client│      │  FastAPI │      │ Indexing │      │  Vector  │      │ LLM │
│      │      │          │      │ Service  │      │   DB     │      │     │
└───┬──┘      └────┬─────┘      └────┬─────┘      └────┬─────┘      └──┬──┘
    │              │                 │                 │               │
    │ POST /upload │                 │                 │               │
    ├─────────────>│                 │                 │               │
    │ {file}       │                 │                 │               │
    │              │ Process doc     │                 │               │
    │              ├────────────────>│                 │               │
    │              │                 │ Generate        │               │
    │              │                 │ embeddings      │               │
    │              │                 ├────────────────>│               │
    │              │                 │                 │               │
    │              │ {file_id}       │                 │               │
    │<─────────────┤                 │                 │               │
    │              │                 │                 │               │
    │ POST /chat   │                 │                 │               │
    ├─────────────>│                 │                 │               │
    │ {message}    │                 │                 │               │
    │              │ Search similar  │                 │               │
    │              ├────────────────>│                 │               │
    │              │                 │ Query vectors   │               │
    │              │                 ├────────────────>│               │
    │              │                 │                 │               │
    │              │                 │ Similar chunks  │               │
    │              │                 │<────────────────┤               │
    │              │ Context + query │                 │               │
    │              ├─────────────────────────────────────────────────>│
    │              │                 │                 │               │
    │              │                 │                 │ Response      │
    │              │<─────────────────────────────────────────────────┤
    │ {response}   │                 │                 │               │
    │<─────────────┤                 │                 │               │
```

## Service Layer Architecture

### Service Responsibilities

Each service has a single, well-defined responsibility:

```
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │  UserService     │  │ ConversationSvc  │               │
│  ├──────────────────┤  ├──────────────────┤               │
│  │ • Registration   │  │ • Create conv    │               │
│  │ • Authentication │  │ • Save messages  │               │
│  │ • Profile mgmt   │  │ • Get history    │               │
│  │ • Password ops   │  │ • Delete conv    │               │
│  └──────────────────┘  └──────────────────┘               │
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │  LLMFactory      │  │ IndexingService  │               │
│  ├──────────────────┤  ├──────────────────┤               │
│  │ • Provider sel   │  │ • Doc processing │               │
│  │ • DeepSeek API   │  │ • Embedding gen  │               │
│  │ • Ollama API     │  │ • Vector search  │               │
│  │ • Config mgmt    │  │ • RAG pipeline   │               │
│  └──────────────────┘  └──────────────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Service Communication

Services communicate through:
1. **Direct method calls** within the same process
2. **Database** as shared state
3. **Message queues** (future: for async tasks)

## Component Interactions

### Authentication and Authorization

```
Request → Middleware → OAuth2PasswordBearer → JWT Decode
                                                    ↓
                                            Verify Signature
                                                    ↓
                                            Extract User ID
                                                    ↓
                                            Query Database
                                                    ↓
                                            Return User Object
                                                    ↓
                                            Endpoint Handler
```

### Message Processing Pipeline

```
User Input → Validation → Authentication → Service Layer
                                                ↓
                                        Save User Message
                                                ↓
                                        Select LLM Provider
                                                ↓
                                        ┌───────┴────────┐
                                        │                │
                                    Normal          RAG/Search
                                        │                │
                                    Direct LLM      Retrieve Context
                                        │                │
                                        └───────┬────────┘
                                                ↓
                                        Generate Response
                                                ↓
                                        Save Assistant Message
                                                ↓
                                        Return to Client
```

## Security Architecture

### Defense in Depth

Multiple layers of security:

1. **Network Layer**
   - HTTPS/TLS encryption
   - Firewall rules
   - DDoS protection

2. **Application Layer**
   - JWT authentication
   - Rate limiting
   - Input validation
   - SQL injection prevention

3. **Data Layer**
   - Password hashing (bcrypt)
   - Encryption at rest
   - Access control
   - Audit logging

### Authentication Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   Authentication Flow                        │
└─────────────────────────────────────────────────────────────┘

1. User Login
   ↓
2. Validate Credentials (bcrypt.verify)
   ↓
3. Generate Access Token (JWT, 15min expiry)
   ↓
4. Generate Refresh Token (JWT, 7day expiry)
   ↓
5. Return Tokens to Client
   ↓
6. Client Stores Tokens (localStorage)
   ↓
7. Client Includes Token in Requests (Authorization header)
   ↓
8. Server Validates Token (JWT signature + expiry)
   ↓
9. Server Extracts User from Token
   ↓
10. Endpoint Processes Request
```

### Authorization Model

**Role-Based Access Control (RBAC)**:

- **User**: Can access own conversations and messages
- **Admin** (future): Can access all resources
- **System**: Internal service operations

**Permission Checks**:
```python
# Verify conversation ownership
if conversation.user_id != current_user.id:
    raise HTTPException(status_code=403, detail="Permission denied")
```

## Scalability Considerations

### Horizontal Scaling

The application is designed to scale horizontally:

1. **Stateless API servers**: No session state in memory
2. **Shared database**: All servers use same database
3. **Load balancer**: Distribute requests across servers
4. **Redis for sessions**: Shared session storage

### Vertical Scaling

For single-server deployments:

1. **Connection pooling**: Reuse database connections
2. **Async I/O**: Non-blocking operations
3. **Caching**: Reduce database queries
4. **Query optimization**: Efficient database queries

### Caching Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                      Caching Layers                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Browser Cache (Client-side)                                │
│  ↓ Static assets, API responses                             │
│                                                             │
│  CDN Cache (Edge)                                           │
│  ↓ Static files, images                                     │
│                                                             │
│  Redis Cache (Application)                                  │
│  ↓ User profiles, conversation lists, session data          │
│                                                             │
│  Database Query Cache                                       │
│  ↓ Frequently accessed queries                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

### Development Environment

```
┌──────────────────────────────────────────────────────────┐
│                  Developer Machine                        │
│                                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   Vite Dev  │  │   FastAPI   │  │   MySQL     │      │
│  │   Server    │  │   (uvicorn) │  │   (local)   │      │
│  │   :5173     │  │   :8000     │  │   :3306     │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### Production Environment

```
┌─────────────────────────────────────────────────────────────┐
│                      Load Balancer                          │
│                    (Nginx / HAProxy)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐ ┌─────▼──────┐ ┌──────▼───────┐
│  API Server 1  │ │ API Server │ │ API Server 3 │
│  (Docker)      │ │ 2 (Docker) │ │  (Docker)    │
└───────┬────────┘ └─────┬──────┘ └──────┬───────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐ ┌─────▼──────┐ ┌──────▼───────┐
│  MySQL Master  │ │   Redis    │ │ File Storage │
│  (Primary)     │ │  Cluster   │ │    (S3)      │
└───────┬────────┘ └────────────┘ └──────────────┘
        │
        │ Replication
        │
┌───────▼────────┐
│  MySQL Replica │
│  (Read-only)   │
└────────────────┘
```

## Error Handling Strategy

### Error Propagation

```
Exception Occurs
    ↓
Service Layer Catches
    ↓
Log Error (with context)
    ↓
Transform to HTTP Exception
    ↓
Middleware Catches
    ↓
Format Error Response
    ↓
Return to Client
```

### Error Response Format

```json
{
  "detail": "Human-readable error message",
  "error_code": "MACHINE_READABLE_CODE",
  "request_id": "abc-123-def-456",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Monitoring and Observability

### Logging Strategy

```
Application Logs → File System → Log Aggregator → Monitoring Dashboard
                                  (Logstash)       (Kibana/Grafana)
```

### Metrics Collection

Key metrics to monitor:

1. **Request Metrics**
   - Request rate (requests/second)
   - Response time (p50, p95, p99)
   - Error rate (errors/total requests)

2. **System Metrics**
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network I/O

3. **Database Metrics**
   - Connection pool usage
   - Query execution time
   - Slow query count
   - Deadlock count

4. **Business Metrics**
   - Active users
   - Messages per day
   - Conversations created
   - LLM API costs

## Future Enhancements

### Planned Architecture Changes

1. **Microservices**: Split into separate services
   - Auth Service
   - Chat Service
   - Document Service
   - Analytics Service

2. **Message Queue**: Add async task processing
   - Celery + Redis
   - Background document processing
   - Email notifications

3. **API Gateway**: Centralized API management
   - Kong or AWS API Gateway
   - Rate limiting
   - API versioning
   - Request routing

4. **Service Mesh**: For microservices communication
   - Istio or Linkerd
   - Service discovery
   - Load balancing
   - Circuit breaking

## Best Practices

1. **Keep services focused**: Single responsibility principle
2. **Use async/await**: Non-blocking I/O for better performance
3. **Implement caching**: Reduce database load
4. **Monitor everything**: Logs, metrics, traces
5. **Test thoroughly**: Unit, integration, and e2e tests
6. **Document APIs**: Keep documentation up-to-date
7. **Version APIs**: Support backward compatibility
8. **Secure by default**: Authentication, validation, encryption

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Vue 3 Documentation](https://vuejs.org/)
- [Twelve-Factor App](https://12factor.net/)
- [Microservices Patterns](https://microservices.io/patterns/)
