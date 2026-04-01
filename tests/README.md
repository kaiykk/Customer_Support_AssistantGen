# Tests

Test suite for the AssistGen system.

## Structure

- `unit/` - Unit tests for individual components
- `integration/` - Integration tests for service interactions
- `e2e/` - End-to-end tests for complete user flows

## Running Tests

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## Test Coverage

Run with coverage reporting:
```bash
pytest --cov=app --cov-report=html
```

See [Testing Documentation](../docs/testing/README.md) for detailed guidelines.
