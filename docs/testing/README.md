# Testing Documentation

This guide covers testing strategies, best practices, and procedures for the AssistGen application.

## Testing Philosophy

AssistGen follows a comprehensive testing approach:

1. **Unit Tests**: Test individual functions and classes in isolation
2. **Integration Tests**: Test interactions between components
3. **End-to-End Tests**: Test complete user workflows
4. **Property-Based Tests**: Test invariants and edge cases

## Test Coverage Requirements

- **Critical modules**: Minimum 70% coverage
- **Service layer**: Minimum 80% coverage
- **API endpoints**: Minimum 70% coverage
- **Utility functions**: Minimum 90% coverage

## Backend Testing (Python)

### Test Framework

- **pytest**: Test runner and framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **httpx**: HTTP client for API testing
- **faker**: Test data generation

### Running Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_user_service.py

# Run specific test
pytest tests/unit/test_user_service.py::test_create_user

# Run tests matching pattern
pytest -k "test_auth"

# Run with verbose output
pytest -v

# Run with print statements
pytest -s

# Run in parallel (faster)
pytest -n auto
```

### Test Organization

```
tests/
├── unit/                    # Unit tests
│   ├── backend/
│   │   ├── conftest.py     # Shared fixtures
│   │   ├── test_user_service.py
│   │   ├── test_conversation_service.py
│   │   └── test_security.py
│   └── README.md
├── integration/             # Integration tests
│   ├── test_api_auth.py
│   ├── test_api_chat.py
│   └── README.md
├── e2e/                     # End-to-end tests
│   ├── test_user_flow.py
│   └── README.md
└── README.md
```

### Writing Unit Tests

**Example: Testing a service method**

```python
# tests/unit/backend/test_user_service.py
import pytest
from app.services.user_service import UserService
from app.models.user import User

@pytest.mark.asyncio
async def test_create_user(db_session):
    """Test user creation with valid data"""
    # Arrange
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123!"
    }
    
    # Act
    user = await UserService.create_user(db_session, user_data)
    
    # Assert
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.hashed_password != "SecurePass123!"  # Password is hashed

@pytest.mark.asyncio
async def test_create_user_duplicate_email(db_session):
    """Test user creation fails with duplicate email"""
    # Arrange
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123!"
    }
    await UserService.create_user(db_session, user_data)
    
    # Act & Assert
    with pytest.raises(ValueError, match="Email already exists"):
        await UserService.create_user(db_session, user_data)
```

### Writing Integration Tests

**Example: Testing API endpoints**

```python
# tests/integration/test_api_auth.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_register_and_login():
    """Test complete registration and login flow"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register user
        register_response = await client.post(
            "/auth/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "SecurePass123!"
            }
        )
        assert register_response.status_code == 201
        data = register_response.json()
        assert "access_token" in data
        assert "user" in data
        
        # Login with credentials
        login_response = await client.post(
            "/auth/login",
            json={
                "username": "newuser",
                "password": "SecurePass123!"
            }
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "access_token" in login_data
        
        # Access protected endpoint
        token = login_data["access_token"]
        profile_response = await client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert profile_response.status_code == 200
        profile = profile_response.json()
        assert profile["username"] == "newuser"
```

### Test Fixtures

**conftest.py** - Shared fixtures:

```python
# tests/unit/backend/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.base import Base

@pytest.fixture
async def db_engine():
    """Create test database engine"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()

@pytest.fixture
async def db_session(db_engine):
    """Create test database session"""
    async_session = sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session

@pytest.fixture
def sample_user():
    """Create sample user data"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123!"
    }
```

### Test Markers

Use markers to categorize tests:

```python
# Mark slow tests
@pytest.mark.slow
async def test_expensive_operation():
    ...

# Mark integration tests
@pytest.mark.integration
async def test_api_integration():
    ...

# Mark tests requiring external services
@pytest.mark.external
async def test_deepseek_api():
    ...
```

Run specific markers:
```bash
# Run only unit tests
pytest -m "not integration and not e2e"

# Skip slow tests
pytest -m "not slow"

# Run only integration tests
pytest -m integration
```

## Frontend Testing (TypeScript/Vue)

### Test Framework

- **Vitest**: Test runner (Vite-native)
- **Vue Test Utils**: Vue component testing
- **Testing Library**: User-centric testing
- **MSW**: API mocking

### Running Tests

```bash
cd frontend

# Run all tests
npm run test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific test file
npm run test src/components/Button.test.ts

# Run in UI mode
npm run test:ui
```

### Writing Component Tests

**Example: Testing a Vue component**

```typescript
// tests/components/Button.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Button from '@/components/Button.vue'

describe('Button', () => {
  it('renders button text', () => {
    const wrapper = mount(Button, {
      props: { text: 'Click me' }
    })
    expect(wrapper.text()).toBe('Click me')
  })

  it('emits click event when clicked', async () => {
    const wrapper = mount(Button)
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
  })

  it('is disabled when loading', () => {
    const wrapper = mount(Button, {
      props: { loading: true }
    })
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })
})
```

### Testing Stores

**Example: Testing Pinia store**

```typescript
// tests/stores/user.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '@/stores/user'

describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initializes with null user', () => {
    const store = useUserStore()
    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })

  it('sets user on login', async () => {
    const store = useUserStore()
    await store.login({ username: 'test', password: 'test123' })
    expect(store.user).not.toBeNull()
    expect(store.isAuthenticated).toBe(true)
  })

  it('clears user on logout', async () => {
    const store = useUserStore()
    await store.login({ username: 'test', password: 'test123' })
    await store.logout()
    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })
})
```

### Mocking API Calls

```typescript
// tests/setup.ts
import { beforeAll, afterEach, afterAll } from 'vitest'
import { setupServer } from 'msw/node'
import { rest } from 'msw'

const handlers = [
  rest.post('/auth/login', (req, res, ctx) => {
    return res(
      ctx.json({
        access_token: 'fake-token',
        user: { id: 1, username: 'test' }
      })
    )
  }),
  
  rest.get('/conversations', (req, res, ctx) => {
    return res(
      ctx.json({
        conversations: [],
        total: 0
      })
    )
  })
]

const server = setupServer(...handlers)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

## End-to-End Testing

### Test Framework

- **Playwright**: Browser automation
- **Cypress**: Alternative E2E framework

### Running E2E Tests

```bash
# Install Playwright
npm install -D @playwright/test

# Run E2E tests
npx playwright test

# Run in headed mode (see browser)
npx playwright test --headed

# Run specific test
npx playwright test tests/e2e/login.spec.ts

# Debug mode
npx playwright test --debug
```

### Writing E2E Tests

**Example: Testing login flow**

```typescript
// tests/e2e/login.spec.ts
import { test, expect } from '@playwright/test'

test('user can login successfully', async ({ page }) => {
  // Navigate to login page
  await page.goto('http://localhost:3000/login')
  
  // Fill in credentials
  await page.fill('input[type="email"]', 'test@example.com')
  await page.fill('input[type="password"]', 'SecurePass123!')
  
  // Click login button
  await page.click('button[type="submit"]')
  
  // Verify redirect to home page
  await expect(page).toHaveURL('http://localhost:3000/')
  
  // Verify user is logged in
  await expect(page.locator('.user-name')).toContainText('test')
})

test('shows error for invalid credentials', async ({ page }) => {
  await page.goto('http://localhost:3000/login')
  
  await page.fill('input[type="email"]', 'wrong@example.com')
  await page.fill('input[type="password"]', 'wrongpass')
  await page.click('button[type="submit"]')
  
  // Verify error message appears
  await expect(page.locator('.error-banner')).toBeVisible()
  await expect(page.locator('.error-banner')).toContainText('Invalid credentials')
})
```

## Test Data Management

### Test Database

Use separate database for testing:

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",  # In-memory database
        echo=False
    )
    yield engine
    await engine.dispose()
```

### Test Data Factories

```python
# tests/factories.py
from faker import Faker
from app.models.user import User

fake = Faker()

class UserFactory:
    @staticmethod
    def create(**kwargs):
        """Create user with fake data"""
        defaults = {
            "username": fake.user_name(),
            "email": fake.email(),
            "hashed_password": fake.password()
        }
        defaults.update(kwargs)
        return User(**defaults)

# Usage
user = UserFactory.create(username="specific_name")
```

## Continuous Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: test_assistgen
        ports:
          - 3306:3306
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run tests
        run: |
          cd frontend
          npm run test:coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./frontend/coverage/coverage-final.json
```

## Testing Best Practices

### 1. Test Naming

Use descriptive test names:

```python
# Good
def test_user_registration_with_valid_data_creates_user():
    ...

def test_user_registration_with_duplicate_email_raises_error():
    ...

# Bad
def test_user():
    ...

def test_registration():
    ...
```

### 2. Arrange-Act-Assert Pattern

```python
def test_create_conversation():
    # Arrange: Set up test data
    user_id = 1
    title = "Test Conversation"
    
    # Act: Execute the function
    conversation = await ConversationService.create_conversation(
        user_id=user_id,
        title=title
    )
    
    # Assert: Verify results
    assert conversation.id is not None
    assert conversation.title == title
    assert conversation.user_id == user_id
```

### 3. Test Independence

Each test should be independent:

```python
# Good: Each test creates its own data
def test_get_user():
    user = UserFactory.create()
    result = await UserService.get_user(user.id)
    assert result.id == user.id

# Bad: Tests depend on each other
user_id = None

def test_create_user():
    global user_id
    user = await UserService.create_user(...)
    user_id = user.id

def test_get_user():
    result = await UserService.get_user(user_id)  # Depends on previous test
```

### 4. Use Fixtures

```python
@pytest.fixture
async def authenticated_user(db_session):
    """Create and return authenticated user"""
    user = await UserService.create_user(
        db_session,
        {
            "username": "testuser",
            "email": "test@example.com",
            "password": "test123"
        }
    )
    return user

async def test_create_conversation(db_session, authenticated_user):
    """Test uses authenticated_user fixture"""
    conversation = await ConversationService.create_conversation(
        user_id=authenticated_user.id,
        title="Test"
    )
    assert conversation.user_id == authenticated_user.id
```

### 5. Mock External Services

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_chat_with_deepseek():
    """Test chat with mocked DeepSeek API"""
    # Mock the LLM service
    with patch('app.services.llm_factory.DeepSeekService') as mock_service:
        mock_service.return_value.chat = AsyncMock(
            return_value="Mocked response"
        )
        
        # Test chat functionality
        response = await chat_handler("Hello")
        assert response == "Mocked response"
        mock_service.return_value.chat.assert_called_once()
```

## Performance Testing

### Load Testing with Locust

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between

class AssistGenUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login before starting tasks"""
        response = self.client.post("/auth/login", json={
            "username": "testuser",
            "password": "test123"
        })
        self.token = response.json()["access_token"]
    
    @task(3)
    def get_conversations(self):
        """Get conversation list (most common operation)"""
        self.client.get(
            "/conversations",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(1)
    def send_message(self):
        """Send chat message (less frequent)"""
        self.client.post(
            "/chat",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "message": "Hello",
                "conversation_id": 1
            }
        )
```

Run load test:
```bash
# Install locust
pip install locust

# Run test
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Open browser to http://localhost:8089
```

## Test Coverage

### Viewing Coverage Reports

```bash
# Backend coverage
cd backend
pytest --cov=app --cov-report=html
open htmlcov/index.html  # View in browser

# Frontend coverage
cd frontend
npm run test:coverage
open coverage/index.html  # View in browser
```

### Coverage Goals

| Module | Target Coverage |
|--------|----------------|
| Services | 80% |
| API Endpoints | 70% |
| Models | 60% |
| Utilities | 90% |
| Middleware | 70% |

### Improving Coverage

```bash
# Find uncovered lines
pytest --cov=app --cov-report=term-missing

# Output:
# app/services/user_service.py    85%    45-47, 52
#                                        ↑ Uncovered lines
```

## Debugging Tests

### Using pytest debugger

```python
def test_something():
    result = some_function()
    
    # Drop into debugger
    import pdb; pdb.set_trace()
    
    assert result == expected
```

Run with debugger:
```bash
pytest --pdb  # Drop into debugger on failure
pytest -x --pdb  # Stop on first failure and debug
```

### Using print statements

```bash
# Run tests with print output
pytest -s

# Or use logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Test Automation

### Pre-commit Hooks

Install pre-commit hooks to run tests automatically:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
        args: ['-v', '--tb=short']
```

Install hooks:
```bash
pip install pre-commit
pre-commit install
```

### Git Hooks

```bash
# .git/hooks/pre-push
#!/bin/bash

echo "Running tests before push..."

cd backend
pytest
BACKEND_RESULT=$?

cd ../frontend
npm run test
FRONTEND_RESULT=$?

if [ $BACKEND_RESULT -ne 0 ] || [ $FRONTEND_RESULT -ne 0 ]; then
    echo "Tests failed. Push aborted."
    exit 1
fi

echo "All tests passed. Proceeding with push."
exit 0
```

Make executable:
```bash
chmod +x .git/hooks/pre-push
```

## Testing Checklist

Before merging code:

- [ ] All tests pass
- [ ] New code has tests
- [ ] Coverage meets requirements
- [ ] No flaky tests
- [ ] Tests run in reasonable time
- [ ] Integration tests pass
- [ ] E2E tests pass (if applicable)
- [ ] Performance tests pass (if applicable)
- [ ] Tests are documented
- [ ] Test data is cleaned up

## Common Testing Patterns

### Testing Async Functions

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

### Testing Exceptions

```python
def test_raises_exception():
    with pytest.raises(ValueError, match="Invalid input"):
        function_that_raises()
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
])
def test_uppercase(input, expected):
    assert uppercase(input) == expected
```

### Testing Database Transactions

```python
@pytest.mark.asyncio
async def test_transaction_rollback(db_session):
    """Test that failed operations rollback"""
    try:
        user = User(username="test")
        db_session.add(user)
        await db_session.flush()
        
        # Cause an error
        raise Exception("Simulated error")
        
        await db_session.commit()
    except:
        await db_session.rollback()
    
    # Verify user was not saved
    result = await db_session.execute(select(User))
    assert len(result.all()) == 0
```

## Troubleshooting Tests

### Tests Fail Locally But Pass in CI

**Possible causes**:
- Different Python/Node versions
- Missing environment variables
- Database state differences
- Timezone issues

**Solution**:
```bash
# Match CI environment
python --version  # Check version
pip list  # Check dependencies
env | grep TEST  # Check environment variables
```

### Flaky Tests

**Symptoms**: Tests pass sometimes, fail other times

**Common causes**:
- Race conditions in async code
- Timing dependencies
- Shared state between tests
- External service dependencies

**Solutions**:
- Add proper `await` statements
- Use fixtures to isolate state
- Mock external services
- Add retries for network operations

### Slow Tests

**Identify slow tests**:
```bash
pytest --durations=10  # Show 10 slowest tests
```

**Speed up tests**:
- Use in-memory database
- Mock external services
- Run tests in parallel
- Use smaller test datasets

## References

- [pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [Playwright Documentation](https://playwright.dev/)
- [Testing Best Practices](https://testingjavascript.com/)
