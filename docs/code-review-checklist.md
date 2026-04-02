# Code Review Checklist

Use this checklist when reviewing code changes for AssistGen. Check all applicable items before approving a pull request.

## General Code Quality

### Code Style and Formatting

- [ ] Code follows PEP 8 style guide (Python) or ESLint rules (TypeScript)
- [ ] Consistent indentation (4 spaces for Python, 2 spaces for TypeScript)
- [ ] No trailing whitespace
- [ ] Files end with a newline
- [ ] Line length under 100 characters (Python) or 120 (TypeScript)
- [ ] Imports are organized and sorted
- [ ] No unused imports or variables
- [ ] Meaningful variable and function names
- [ ] Constants are UPPER_CASE
- [ ] Classes are PascalCase
- [ ] Functions/variables are snake_case (Python) or camelCase (TypeScript)

### Code Structure

- [ ] Functions are small and focused (< 50 lines)
- [ ] Classes have single responsibility
- [ ] No duplicate code (DRY principle)
- [ ] No deeply nested code (max 3-4 levels)
- [ ] No magic numbers (use named constants)
- [ ] Proper separation of concerns
- [ ] No circular dependencies

## Documentation

### Code Comments

- [ ] All modules have docstrings
- [ ] All classes have docstrings
- [ ] All public functions have docstrings
- [ ] Docstrings include parameter descriptions
- [ ] Docstrings include return value descriptions
- [ ] Docstrings include usage examples for complex functions
- [ ] Complex logic has inline comments
- [ ] Comments explain "why", not "what"
- [ ] No commented-out code (remove or explain)
- [ ] TODO/FIXME comments have issue numbers

### API Documentation

- [ ] New endpoints documented in API docs
- [ ] Request/response schemas documented
- [ ] Error responses documented
- [ ] Authentication requirements documented
- [ ] Example requests provided

## Testing

### Test Coverage

- [ ] Unit tests for new functions/methods
- [ ] Integration tests for new features
- [ ] Test coverage > 70% for critical modules
- [ ] Edge cases are tested
- [ ] Error conditions are tested
- [ ] Tests are independent (no shared state)
- [ ] Tests have descriptive names
- [ ] Tests use fixtures appropriately

### Test Quality

- [ ] Tests actually test the intended behavior
- [ ] No flaky tests (tests pass consistently)
- [ ] Tests run quickly (< 1 second per test)
- [ ] Mocks are used appropriately
- [ ] Test data is realistic
- [ ] Assertions are specific and meaningful

## Security

### Authentication and Authorization

- [ ] Protected endpoints require authentication
- [ ] User permissions are checked
- [ ] JWT tokens are validated properly
- [ ] Passwords are hashed (never stored plain text)
- [ ] Sensitive data is not logged
- [ ] No hardcoded credentials or API keys

### Input Validation

- [ ] All user inputs are validated
- [ ] SQL injection prevention (use ORM, no raw SQL)
- [ ] XSS prevention (sanitize HTML output)
- [ ] CSRF protection for state-changing operations
- [ ] File upload validation (type, size, content)
- [ ] Rate limiting for expensive operations

### Data Protection

- [ ] Sensitive data is encrypted at rest
- [ ] HTTPS is enforced
- [ ] Security headers are set
- [ ] No sensitive data in URLs or logs
- [ ] User data access is restricted to owner
- [ ] Proper error messages (no information leakage)

## Performance

### Database Operations

- [ ] Queries use indexes effectively
- [ ] No N+1 query problems
- [ ] Pagination for large result sets
- [ ] Database connections are properly closed
- [ ] Transactions are used appropriately
- [ ] Bulk operations for multiple inserts/updates
- [ ] Avoid SELECT * (specify columns)

### API Performance

- [ ] Response times < 500ms for 95th percentile
- [ ] Async/await used for I/O operations
- [ ] No blocking operations in async functions
- [ ] Caching for frequently accessed data
- [ ] Lazy loading for expensive operations
- [ ] Proper timeout configuration

### Frontend Performance

- [ ] Components are lazy-loaded
- [ ] Images are optimized
- [ ] Bundle size is reasonable (< 500KB)
- [ ] No unnecessary re-renders
- [ ] Debouncing for frequent events
- [ ] Virtual scrolling for long lists

## Error Handling

### Exception Handling

- [ ] All exceptions are caught and handled
- [ ] Specific exceptions are caught (not bare `except:`)
- [ ] Errors are logged with context
- [ ] User-friendly error messages
- [ ] Proper HTTP status codes
- [ ] Cleanup in finally blocks
- [ ] No silent failures

### Validation

- [ ] Input validation before processing
- [ ] Type checking (Pydantic schemas)
- [ ] Range validation for numbers
- [ ] Length validation for strings
- [ ] Format validation (email, URL, etc.)
- [ ] Business rule validation

## API Design

### RESTful Principles

- [ ] Proper HTTP methods (GET, POST, PUT, DELETE)
- [ ] Meaningful endpoint paths
- [ ] Consistent naming conventions
- [ ] Proper status codes (200, 201, 400, 401, 404, 500)
- [ ] Idempotent operations where appropriate
- [ ] Versioned API endpoints

### Request/Response

- [ ] Request schemas are well-defined
- [ ] Response schemas are consistent
- [ ] Pagination for list endpoints
- [ ] Filtering and sorting options
- [ ] Proper content-type headers
- [ ] CORS headers configured correctly

## Database Changes

### Schema Changes

- [ ] Migration script created
- [ ] Migration is reversible (downgrade implemented)
- [ ] Migration tested on development database
- [ ] Indexes added for new columns
- [ ] Foreign keys have proper constraints
- [ ] Default values specified
- [ ] NOT NULL constraints appropriate

### Data Integrity

- [ ] Referential integrity maintained
- [ ] Cascading deletes configured correctly
- [ ] Unique constraints where needed
- [ ] Check constraints for valid values
- [ ] Transactions used for multi-step operations

## Frontend Changes

### Component Quality

- [ ] Components are reusable
- [ ] Props are properly typed
- [ ] Events are properly emitted
- [ ] No prop drilling (use stores for global state)
- [ ] Computed properties for derived state
- [ ] Watchers used sparingly

### Accessibility

- [ ] Semantic HTML elements used
- [ ] ARIA labels for interactive elements
- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] Color contrast meets WCAG AA standards
- [ ] Screen reader tested (if possible)
- [ ] Form labels associated with inputs

### User Experience

- [ ] Loading states for async operations
- [ ] Error messages are helpful
- [ ] Success feedback provided
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Smooth transitions and animations
- [ ] No layout shifts during loading

## Dependencies

### Dependency Management

- [ ] New dependencies are necessary
- [ ] Dependencies are up-to-date
- [ ] No known security vulnerabilities
- [ ] License compatibility checked
- [ ] Bundle size impact considered
- [ ] Alternative libraries evaluated

### Version Pinning

- [ ] Exact versions specified in requirements.txt
- [ ] Exact versions specified in package.json
- [ ] Lock files committed (package-lock.json, poetry.lock)

## Git and Version Control

### Commit Quality

- [ ] Commits are atomic (one logical change)
- [ ] Commit messages are descriptive
- [ ] Commit messages follow convention
- [ ] No merge commits in feature branch
- [ ] No large binary files committed
- [ ] Sensitive data not committed

### Branch Management

- [ ] Branch name follows convention
- [ ] Branch is up-to-date with main
- [ ] No merge conflicts
- [ ] Feature branch will be deleted after merge

## Deployment Considerations

### Configuration

- [ ] Environment variables documented
- [ ] Default values provided
- [ ] Configuration validation implemented
- [ ] No hardcoded environment-specific values

### Backwards Compatibility

- [ ] API changes are backwards compatible
- [ ] Database migrations are backwards compatible
- [ ] Deprecation warnings for removed features
- [ ] Migration guide updated if breaking changes

### Monitoring

- [ ] New features have logging
- [ ] Errors are logged with context
- [ ] Performance metrics tracked
- [ ] Alerts configured for failures

## Review Process

### Before Requesting Review

- [ ] All tests pass locally
- [ ] Code is formatted
- [ ] Linter passes with no warnings
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG updated

### During Review

- [ ] Respond to all comments
- [ ] Make requested changes
- [ ] Re-request review after changes
- [ ] Resolve all conversations

### After Approval

- [ ] Squash commits if needed
- [ ] Update branch with latest main
- [ ] Verify CI/CD passes
- [ ] Merge to main
- [ ] Delete feature branch
- [ ] Verify deployment

## Severity Levels

### Critical (Must Fix)

- Security vulnerabilities
- Data loss risks
- Application crashes
- Breaking changes without migration path

### High (Should Fix)

- Performance issues
- Memory leaks
- Incorrect business logic
- Missing error handling

### Medium (Consider Fixing)

- Code style violations
- Missing tests
- Incomplete documentation
- Minor performance issues

### Low (Nice to Have)

- Code organization improvements
- Additional comments
- Refactoring opportunities
- Minor style inconsistencies

## Automated Checks

Run these before requesting review:

```bash
# Backend checks
cd backend
black .                    # Format code
flake8 .                   # Lint code
mypy .                     # Type check
pytest                     # Run tests
pytest --cov=app --cov-report=html  # Coverage

# Frontend checks
cd frontend
npm run lint               # Lint code
npm run type-check         # Type check
npm run test               # Run tests
npm run build              # Verify build works
```

## Review Time Estimates

- **Small change** (< 50 lines): 15 minutes
- **Medium change** (50-200 lines): 30 minutes
- **Large change** (200-500 lines): 1 hour
- **Very large change** (> 500 lines): 2+ hours (consider splitting)

## References

- [Google Code Review Guidelines](https://google.github.io/eng-practices/review/)
- [PEP 8 Style Guide](https://pep8.org/)
- [TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)
- [OWASP Security Guidelines](https://owasp.org/www-project-code-review-guide/)
