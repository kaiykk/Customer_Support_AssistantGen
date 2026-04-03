# AssistGen - Intelligent Customer Service System

A modern, AI-powered customer service platform built with FastAPI, Vue 3, and multiple LLM integrations. AssistGen provides intelligent conversational AI capabilities with support for multiple language models, RAG (Retrieval-Augmented Generation), and advanced search functionality.

## 🌟 Features

### Core Capabilities
- **Multi-LLM Support**: Seamlessly switch between DeepSeek and Ollama language models
- **Intelligent Chat**: Context-aware conversational AI with message history
- **Search-Enhanced Responses**: Integrate web search results into AI responses
- **RAG Integration**: Knowledge base integration with GraphRAG
- **User Management**: Secure authentication and user profile management
- **Conversation History**: Persistent conversation storage and retrieval
- **Real-time Streaming**: Server-sent events for streaming AI responses

### Technical Features
- **Async Architecture**: Built on FastAPI with async/await for high performance
- **Database Support**: MySQL for relational data, Neo4j for graph data
- **Caching Layer**: Redis-based semantic caching for improved performance
- **Comprehensive Logging**: Structured logging with Loguru
- **Security**: JWT authentication, password hashing, CORS protection
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## 📋 Table of Contents

- [Technology Stack](#-technology-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🛠 Technology Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.9+
- **Database**: MySQL 8.0+, Neo4j 5.0+ (optional)
- **Cache**: Redis 7.0+ (optional)
- **ORM**: SQLAlchemy 2.0+ (async)
- **Authentication**: JWT (python-jose)
- **Logging**: Loguru
- **LLM Integration**: OpenAI SDK, Ollama

### Frontend
- **Framework**: Vue 3.3+
- **Language**: TypeScript 5.0+
- **Build Tool**: Vite 4.0+
- **UI Components**: Custom components with modern design
- **State Management**: Vue Composition API
- **HTTP Client**: Axios

### DevOps
- **Containerization**: Docker, Docker Compose
- **Testing**: Pytest (backend), Vitest (frontend)
- **Code Quality**: Black, Flake8, ESLint, Prettier

## 📦 Prerequisites

Before installing AssistGen, ensure you have the following installed:

### Required
- **Python**: 3.9 or higher
- **Node.js**: 16.0 or higher
- **npm** or **yarn**: Latest version
- **MySQL**: 8.0 or higher

### Optional (for enhanced features)
- **Redis**: 7.0 or higher (for caching)
- **Neo4j**: 5.0 or higher (for GraphRAG)
- **Docker**: 20.10+ and Docker Compose 2.0+ (for containerized deployment)

### API Keys
- **DeepSeek API Key**: Required if using DeepSeek LLM (get from [DeepSeek Platform](https://platform.deepseek.com))
- **Ollama**: Required if using local Ollama (install from [Ollama.ai](https://ollama.ai))

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd assistgen-refactored
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# or
yarn install
```

### 4. Database Setup

```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE assistgen CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'assistgen_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON assistgen.* TO 'assistgen_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## ⚙️ Configuration

### 1. Backend Configuration

Create a `.env` file in the `backend` directory:

```bash
# Copy example configuration
cp ../config/development.env.example backend/.env
```

Edit `.env` with your settings:

```env
# Application Settings
APP_NAME=AssistGen
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Database Configuration
DATABASE_URL=mysql+aiomysql://assistgen_user:your_password@localhost:3306/assistgen

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# LLM Configuration
CHAT_SERVICE=DEEPSEEK
REASON_SERVICE=DEEPSEEK
DEEPSEEK_API_KEY=your-deepseek-api-key

# Optional: Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Optional: Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Optional: Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password
```

### 2. Frontend Configuration

Create a `.env` file in the `frontend` directory:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=AssistGen
```

### 3. Configuration Validation

Validate your configuration:

```bash
cd backend
python -m app.core.config_validator
```

For detailed configuration options, see [Configuration Guide](config/configuration-guide.md).

## 🏃 Running the Application

### Development Mode

#### Backend

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run database migrations (first time only)
alembic upgrade head

# Start the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`

#### Frontend

```bash
cd frontend

# Start the development server
npm run dev
# or
yarn dev
```

The frontend will be available at `http://localhost:5173`

### Production Mode

#### Using Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Manual Production Deployment

See [Deployment Guide](docs/deployment/README.md) for detailed production deployment instructions.

## 📚 API Documentation

### Interactive API Documentation

Once the backend is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /register` - Register new user
- `POST /token` - Login and get access token
- `GET /users/me` - Get current user profile

#### Conversations
- `POST /conversations` - Create new conversation
- `GET /conversations` - List user conversations
- `GET /conversations/{id}/messages` - Get conversation messages
- `DELETE /conversations/{id}` - Delete conversation
- `PUT /conversations/{id}/name` - Update conversation name

#### Chat
- `POST /chat` - Send chat message (streaming response)
- `POST /search-chat` - Search-enhanced chat
- `POST /agent-chat` - Agent-based chat with tools

For complete API documentation, see [API Reference](docs/api/README.md).

## 📁 Project Structure

```
assistgen-refactored/
├── backend/                    # Backend application
│   ├── app/
│   │   ├── api/               # API route handlers
│   │   ├── core/              # Core functionality (config, database, security)
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic services
│   │   └── utils/             # Utility functions
│   ├── main.py                # Application entry point
│   ├── requirements.txt       # Python dependencies
│   └── pytest.ini             # Test configuration
├── frontend/                   # Frontend application
│   ├── src/
│   │   ├── components/        # Vue components
│   │   ├── views/             # Page views
│   │   ├── router/            # Vue Router configuration
│   │   ├── stores/            # State management
│   │   ├── api/               # API client
│   │   └── assets/            # Static assets
│   ├── package.json           # Node dependencies
│   └── vite.config.ts         # Vite configuration
├── config/                     # Configuration files
│   ├── development.env.example
│   ├── production.env.example
│   └── configuration-guide.md
├── docs/                       # Documentation
│   ├── api/                   # API documentation
│   ├── architecture/          # Architecture diagrams
│   ├── database/              # Database schema docs
│   └── deployment/            # Deployment guides
├── scripts/                    # Utility scripts
│   ├── analyze_backend.py     # Code analysis
│   └── setup_dev.sh           # Development setup
├── tests/                      # Test suites
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── e2e/                   # End-to-end tests
├── docker-compose.yml          # Docker Compose configuration
└── README.md                   # This file
```

## 💻 Development

### Code Style

#### Backend (Python)
- Follow PEP 8 style guidelines
- Use Black for code formatting
- Use type hints for all functions
- Write docstrings for all public functions and classes

```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy .
```

#### Frontend (TypeScript)
- Follow Vue 3 style guide
- Use ESLint and Prettier
- Use TypeScript for type safety

```bash
# Lint code
npm run lint

# Format code
npm run format
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Adding New Features

1. Create feature branch: `git checkout -b feature/your-feature`
2. Implement feature with tests
3. Update documentation
4. Submit pull request

See [Contributing Guidelines](#-contributing) for more details.

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_user_service.py

# Run tests with specific marker
pytest -m "not slow"
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm run test:unit

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

### End-to-End Tests

```bash
# Run E2E tests
npm run test:e2e
```

## 🚢 Deployment

### Docker Deployment

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app
```

### Manual Deployment

See detailed deployment guides:
- [Production Deployment Guide](docs/deployment/README.md)
- [Docker Deployment](docs/deployment/docker.md)
- [Cloud Deployment](docs/deployment/cloud.md)

### Environment-Specific Configuration

- **Development**: Use `config/development.env.example`
- **Staging**: Use `config/staging.env.example`
- **Production**: Use `config/production.env.example`

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Error
#### Port Already in Use
#### LLM API Error
#### Frontend Can't Connect to Backend
### Debug Mode
### Getting Help

- Check [Documentation](docs/)
- Review [API Documentation](http://localhost:8000/docs)
- Search [Issues](https://github.com/your-repo/issues)
- Contact support

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:
### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run pre-commit checks
pre-commit run --all-files
```

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Vue.js team for the reactive frontend framework
- DeepSeek for AI capabilities
- Ollama for local LLM support
- All contributors and supporters

## 🗺️ Roadmap

### Current Version (v1.0)
- ✅ Multi-LLM support
- ✅ User authentication
- ✅ Conversation management
- ✅ Search-enhanced chat

### Upcoming Features (v1.1)
- 🔄 Voice input/output
- 🔄 Multi-language support
- 🔄 Advanced analytics dashboard
- 🔄 Plugin system

### Future Plans (v2.0)
- 📋 Mobile applications
- 📋 Enterprise features
- 📋 Advanced RAG capabilities
- 📋 Custom model fine-tuning

---

**Built with ❤️ by Kai**
