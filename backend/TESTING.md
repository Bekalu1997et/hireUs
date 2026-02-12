# Testing Guide

This document describes the testing strategy and how to run tests for the Structured Interview Platform.

## Test Structure

Tests are organized by module and type:

```
app/tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_database.py         # Database session management tests
├── test_security.py         # Security utilities tests (password hashing, JWT)
└── test_auth.py            # Authentication service tests
```

## Test Types

### Unit Tests
Unit tests verify specific functions and classes in isolation.

**Markers**: `@pytest.mark.unit`

**Examples**:
- Password hashing functions
- JWT token creation/validation
- User registration with valid data
- Login with invalid credentials

### Property-Based Tests
Property-based tests verify universal properties across many generated inputs using Hypothesis.

**Markers**: `@pytest.mark.property`

**Examples**:
- Property 4: Authentication Correctness
- Property 5: Role-Based Access Control Enforcement
- Property 7: Password Security

### Integration Tests
Integration tests verify end-to-end workflows across multiple components.

**Markers**: `@pytest.mark.integration`

## Running Tests

### Prerequisites

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create test database:
```bash
createdb hireus_test
```

3. Set up environment variables (optional):
```bash
cp ../.env.example ../.env
```

### Run All Tests

```bash
cd backend
pytest
```

### Run Specific Test Types

```bash
# Unit tests only
pytest -m unit

# Property-based tests only
pytest -m property

# Integration tests only
pytest -m integration
```

### Run Specific Test Files

```bash
# Database tests
pytest app/tests/test_database.py -v

# Security tests
pytest app/tests/test_security.py -v

# Authentication tests
pytest app/tests/test_auth.py -v
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

View coverage report: `open htmlcov/index.html`

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test

```bash
pytest app/tests/test_auth.py::test_register_user_creates_organization_and_founder -v
```

## Test Database

Tests use a separate test database (`hireus_test`) to avoid affecting development data.

The test database is:
- Created fresh for each test session
- Cleaned up after each test
- Isolated from the main database

## Property-Based Testing

Property-based tests use Hypothesis to generate random test data and verify properties hold across all inputs.

**Configuration**:
- Minimum 100 iterations per property test (configured in Hypothesis)
- Custom strategies for generating valid domain objects
- Shrinking to find minimal failing examples

**Example Property Test**:
```python
@pytest.mark.property
@given(password=st.text(min_size=1, max_size=100))
def test_password_never_stored_plaintext(password):
    """Property 7: Password Security"""
    hashed = hash_password(password)
    assert hashed != password
    assert hashed.startswith("$2b$")
```

## Continuous Integration

Tests should be run in CI/CD pipeline before merging:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    cd backend
    pytest --cov=app --cov-report=xml
```

## Troubleshooting

### Database Connection Errors

If you see database connection errors:

1. Ensure PostgreSQL is running
2. Verify test database exists: `psql -l | grep hireus_test`
3. Check database URL in settings

### Import Errors

If you see import errors:

1. Ensure you're in the backend directory
2. Set PYTHONPATH: `export PYTHONPATH="${PYTHONPATH}:$(pwd)"`
3. Verify all dependencies are installed

### Async Test Errors

If async tests fail:

1. Ensure `pytest-asyncio` is installed
2. Check `pytest.ini` has `asyncio_mode = auto`
3. Use `@pytest.mark.asyncio` decorator on async tests

## Test Coverage Goals

- **Line Coverage**: Minimum 80% for all modules
- **Branch Coverage**: Minimum 70% for business logic
- **Property Coverage**: All 28 properties must have corresponding tests
- **Critical Paths**: 100% coverage for authentication and authorization

## Writing New Tests

### Unit Test Template

```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_feature_name(db_session: AsyncSession):
    """Test description."""
    # Arrange
    service = MyService(db_session)
    
    # Act
    result = await service.do_something()
    
    # Assert
    assert result is not None
```

### Property Test Template

```python
@pytest.mark.property
@given(input_data=st.text(min_size=1))
def test_property_name(input_data):
    """
    Property N: Property Name
    
    For any input, property should hold.
    
    Validates: Requirements X.Y
    """
    result = function_under_test(input_data)
    assert property_holds(result)
```

## Current Test Status

### Completed Tests

✅ Database session management (5 tests)
✅ Password hashing and JWT tokens (10+ tests)
✅ Authentication service (15+ tests)
✅ Property 4: Authentication Correctness
✅ Property 5: Role-Based Access Control
✅ Property 7: Password Security

### Pending Tests

⏳ Property tests for remaining properties (Properties 1-3, 6, 8-28)
⏳ Integration tests for complete workflows
⏳ Performance tests for database operations
