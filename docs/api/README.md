# AssistGen API Documentation

This document provides comprehensive documentation for the AssistGen REST API.

## Base URL

```
Development: http://localhost:8000
Production: https://api.assistgen.example.com
```

## Authentication

AssistGen uses JWT (JSON Web Token) based authentication.

### Authentication Flow

1. **Register** or **Login** to obtain access and refresh tokens
2. Include access token in `Authorization` header for protected endpoints
3. Use refresh token to obtain new access token when it expires

### Token Format

```
Authorization: Bearer <access_token>
```

### Token Expiration

- **Access Token**: 15 minutes
- **Refresh Token**: 7 days

## API Endpoints

### Authentication

#### POST /auth/register

Register a new user account.

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response:** `201 Created`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid input data
- `409 Conflict`: Username or email already exists

---

#### POST /auth/login

Authenticate user and obtain tokens.

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "SecurePass123!"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid credentials
- `400 Bad Request`: Missing required fields

---

#### POST /auth/refresh

Obtain a new access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired refresh token

---

#### POST /auth/logout

Invalidate current session (client-side token removal).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "message": "Logged out successfully"
}
```

---

### User Management

#### GET /users/me

Get current authenticated user profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-02T10:30:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token

---

#### PUT /users/{user_id}

Update user profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "username": "new_username"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "username": "new_username",
  "email": "newemail@example.com",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-02T15:45:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: Cannot update another user's profile
- `409 Conflict`: Username or email already taken

---

### Conversations

#### GET /conversations

Get all conversations for the authenticated user with pagination.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (optional): Number of conversations to skip (default: 0)
- `limit` (optional): Maximum conversations to return (default: 50)
- `include_empty` (optional): Include empty conversations (default: false)

**Response:** `200 OK`
```json
{
  "conversations": [
    {
      "id": 1,
      "title": "Python Help",
      "dialogue_type": "normal",
      "status": "active",
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T14:30:00Z"
    }
  ],
  "total": 100,
  "skip": 0,
  "limit": 50
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token

---

#### POST /conversations

Create a new conversation.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "title": "Python Help",
  "dialogue_type": "normal"
}
```

**Dialogue Types:**
- `normal`: Standard chat conversation
- `deep_thinking`: Reasoning-enhanced conversation
- `web_search`: Search-augmented conversation
- `rag`: Document-based conversation

**Response:** `201 Created`
```json
{
  "id": 1,
  "title": "Python Help",
  "dialogue_type": "normal",
  "status": "active",
  "created_at": "2024-01-01T12:00:00Z",
  "user_id": 1
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `400 Bad Request`: Invalid dialogue type

---

#### GET /conversations/{conversation_id}

Get a specific conversation by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Python Help",
  "dialogue_type": "normal",
  "status": "active",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T14:30:00Z",
  "user_id": 1
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Conversation not found
- `403 Forbidden`: Conversation belongs to another user

---

#### PUT /conversations/{conversation_id}

Update conversation details.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "title": "Updated Title",
  "status": "archived"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Updated Title",
  "dialogue_type": "normal",
  "status": "archived",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-02T10:00:00Z",
  "user_id": 1
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Conversation not found
- `403 Forbidden`: Cannot update another user's conversation

---

#### DELETE /conversations/{conversation_id}

Delete a conversation and all its messages.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `204 No Content`

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Conversation not found
- `403 Forbidden`: Cannot delete another user's conversation

---

### Messages

#### GET /conversations/{conversation_id}/messages

Get all messages in a conversation with pagination.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (optional): Number of messages to skip (default: 0)
- `limit` (optional): Maximum messages to return (default: 100)

**Response:** `200 OK`
```json
{
  "messages": [
    {
      "id": 1,
      "sender": "user",
      "content": "What is Python?",
      "message_type": "text",
      "created_at": "2024-01-01T12:00:00Z"
    },
    {
      "id": 2,
      "sender": "assistant",
      "content": "Python is a high-level programming language...",
      "message_type": "text",
      "created_at": "2024-01-01T12:00:05Z"
    }
  ],
  "total": 50,
  "skip": 0,
  "limit": 100
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Conversation not found
- `403 Forbidden`: Cannot access another user's conversation

---

### Chat

#### POST /chat

Send a message and receive a response.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "message": "What is Python?",
  "conversation_id": 1,
  "dialogue_type": "normal",
  "stream": false
}
```

**Response:** `200 OK`
```json
{
  "message": {
    "id": 2,
    "sender": "assistant",
    "content": "Python is a high-level programming language...",
    "message_type": "text",
    "created_at": "2024-01-01T12:00:05Z"
  },
  "conversation_id": 1
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `400 Bad Request`: Invalid request format
- `404 Not Found`: Conversation not found
- `500 Internal Server Error`: LLM service error

---

#### POST /chat/stream

Send a message and receive a streaming response.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "message": "Explain quantum computing",
  "conversation_id": 1,
  "dialogue_type": "normal",
  "stream": true
}
```

**Response:** `200 OK` (Server-Sent Events)
```
data: {"content": "Quantum", "done": false}

data: {"content": " computing", "done": false}

data: {"content": " is", "done": false}

data: [DONE]
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `400 Bad Request`: Invalid request format

---

#### POST /chat/search

Send a message with web search enhancement.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "message": "Latest Python 3.12 features",
  "conversation_id": 1,
  "max_results": 5
}
```

**Response:** `200 OK`
```json
{
  "message": {
    "id": 2,
    "sender": "assistant",
    "content": "Based on recent search results, Python 3.12 includes...",
    "message_type": "text",
    "created_at": "2024-01-01T12:00:05Z",
    "metadata": {
      "sources": [
        {
          "title": "Python 3.12 Release Notes",
          "url": "https://docs.python.org/3.12/whatsnew/3.12.html"
        }
      ]
    }
  },
  "conversation_id": 1
}
```

---

#### POST /chat/agent

Send a message using LangGraph agent workflow.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "message": "Analyze this code and suggest improvements",
  "conversation_id": 1,
  "agent_config": {
    "max_iterations": 5,
    "tools": ["code_analyzer", "documentation_search"]
  }
}
```

**Response:** `200 OK`
```json
{
  "message": {
    "id": 2,
    "sender": "assistant",
    "content": "I've analyzed the code and found...",
    "message_type": "text",
    "created_at": "2024-01-01T12:00:05Z",
    "metadata": {
      "agent_steps": [
        {"tool": "code_analyzer", "result": "..."},
        {"tool": "documentation_search", "result": "..."}
      ]
    }
  },
  "conversation_id": 1
}
```

---

### Document Upload (RAG)

#### POST /upload

Upload a document for RAG-based conversations.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body:**
```
file: <binary file data>
conversation_id: 1
```

**Supported File Types:**
- PDF (.pdf)
- Word Documents (.docx, .doc)
- Text Files (.txt)
- Markdown (.md)

**Response:** `200 OK`
```json
{
  "file_id": "abc-123-def-456",
  "filename": "document.pdf",
  "size": 1024000,
  "status": "indexed",
  "conversation_id": 1
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `400 Bad Request`: Invalid file type or size
- `413 Payload Too Large`: File exceeds size limit (10MB)

---

## Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong",
  "error_code": "SPECIFIC_ERROR_CODE",
  "request_id": "abc-123-def-456"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `AUTH_INVALID_CREDENTIALS` | Invalid username or password |
| `AUTH_TOKEN_EXPIRED` | Access token has expired |
| `AUTH_TOKEN_INVALID` | Token is malformed or invalid |
| `RESOURCE_NOT_FOUND` | Requested resource doesn't exist |
| `PERMISSION_DENIED` | User lacks permission for this action |
| `VALIDATION_ERROR` | Request data failed validation |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INTERNAL_ERROR` | Server encountered an error |

## Rate Limiting

API requests are rate-limited to prevent abuse:

- **Limit**: 100 requests per minute per IP address
- **Headers**: Rate limit information is included in response headers

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1704110460
```

**Rate Limit Exceeded Response:** `429 Too Many Requests`
```json
{
  "detail": "Too many requests. Please try again later.",
  "retry_after": 45
}
```

## Pagination

List endpoints support pagination using `skip` and `limit` parameters:

**Request:**
```
GET /conversations?skip=20&limit=10
```

**Response:**
```json
{
  "conversations": [...],
  "total": 100,
  "skip": 20,
  "limit": 10
}
```

**Pagination Metadata:**
- `total`: Total number of items available
- `skip`: Number of items skipped
- `limit`: Maximum items returned

## Versioning

The API uses URL-based versioning:

```
/api/v1/...  (Current version)
/api/v2/...  (Future version)
```

Current version: **v1**

## CORS Configuration

The API supports Cross-Origin Resource Sharing (CORS):

**Allowed Origins:**
- Development: `http://localhost:3000`, `http://localhost:5173`
- Production: Configured via `CORS_ORIGINS` environment variable

**Allowed Methods:** GET, POST, PUT, DELETE, OPTIONS

**Allowed Headers:** Authorization, Content-Type

## Security Headers

All responses include security headers:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

## Request/Response Examples

### Complete Chat Flow

1. **Register User**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

2. **Create Conversation**
```bash
curl -X POST http://localhost:8000/conversations \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Help",
    "dialogue_type": "normal"
  }'
```

3. **Send Message**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is Python?",
    "conversation_id": 1,
    "dialogue_type": "normal"
  }'
```

4. **Get Conversation History**
```bash
curl -X GET http://localhost:8000/conversations/1/messages \
  -H "Authorization: Bearer <access_token>"
```

## Interactive API Documentation

AssistGen provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

These interfaces allow you to:
- Explore all available endpoints
- Test API calls directly from the browser
- View request/response schemas
- See example requests and responses

## Client Libraries

### Python

```python
import requests

class AssistGenClient:
    def __init__(self, base_url, access_token):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {access_token}"}
    
    def send_message(self, message, conversation_id=None):
        response = requests.post(
            f"{self.base_url}/chat",
            headers=self.headers,
            json={
                "message": message,
                "conversation_id": conversation_id
            }
        )
        return response.json()

# Usage
client = AssistGenClient("http://localhost:8000", "your_token")
result = client.send_message("Hello!")
print(result)
```

### JavaScript/TypeScript

```typescript
class AssistGenClient {
  constructor(private baseUrl: string, private accessToken: string) {}

  async sendMessage(message: string, conversationId?: number) {
    const response = await fetch(`${this.baseUrl}/chat`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId
      })
    })
    return response.json()
  }
}

// Usage
const client = new AssistGenClient('http://localhost:8000', 'your_token')
const result = await client.sendMessage('Hello!')
console.log(result)
```

## Webhooks (Future Feature)

Webhook support for real-time notifications is planned for v2.

## Support

For API support:
- GitHub Issues: https://github.com/assistgen/assistgen/issues
- Email: support@assistgen.example.com
- Documentation: https://docs.assistgen.example.com
