# SovereignCore Testing Guide

## Overview

This guide covers the comprehensive test suite for SovereignCore, including unit tests, integration tests, and coverage verification.

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── test_api_server.py       # API endpoint tests
├── test_auth.py             # Authentication and JWT tests
└── test_consciousness.py    # Consciousness functionality tests
```

## Running Tests

### Quick Start

```bash
# Run all tests
pytest

# Run with coverage
./run_tests.sh

# Run specific test file
pytest tests/test_api_server.py

# Run specific test class
pytest tests/test_auth.py::TestJWTTokenCreation

# Run specific test
pytest tests/test_auth.py::TestJWTTokenCreation::test_create_access_token
```

### Coverage Testing

```bash
# Run tests with coverage report
pytest --cov=api_server --cov-report=term-missing tests/

# Generate HTML coverage report
pytest --cov=api_server --cov-report=html tests/
open htmlcov/index.html

# Use the automated script (recommended)
./run_tests.sh
```

### Test Markers

Tests are organized with markers for selective execution:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only security tests
pytest -m security

# Skip slow tests
pytest -m "not slow"

# Run only Redis-dependent tests
pytest -m redis
```

## Test Coverage Requirements

- **Minimum Coverage**: 80%
- **Target Coverage**: 90%+
- **Critical Modules**: 95%+
  - `api_server.py`
  - Authentication functions
  - Security middleware

## Test Categories

### 1. API Endpoint Tests (`test_api_server.py`)

- **Health Checks**: `/health` endpoint
- **Root Endpoint**: `/` welcome message
- **Metrics**: `/metrics` Prometheus endpoint
- **Authentication**: Token generation and refresh
- **Protected Endpoints**: Authorization verification
- **Rate Limiting**: Request throttling
- **Security Headers**: CORS, CSP, HSTS
- **Input Validation**: Pydantic model validation
- **Error Handling**: 404, 405, 422 responses

### 2. Authentication Tests (`test_auth.py`)

- **Password Hashing**: bcrypt hashing and verification
- **JWT Creation**: Access and refresh token generation
- **JWT Validation**: Token decoding and verification
- **Token Expiration**: Time-based token invalidation
- **Login Flow**: Complete authentication workflow
- **Token Refresh**: Refresh token exchange
- **Security**: Timing attack resistance, minimal data exposure

### 3. Consciousness Tests (`test_consciousness.py`)

- **Status Endpoint**: Consciousness state queries
- **Query Processing**: Natural language query handling
- **Input Validation**: Query sanitization and validation
- **Error Handling**: Malformed requests, injection attempts
- **Performance**: Response time benchmarks
- **Integration**: Redis integration, metrics tracking

## Fixtures

Common fixtures available in `conftest.py`:

### Authentication Fixtures

```python
@pytest.fixture
def auth_headers(access_token):
    """Get authorization headers with valid token."""
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def access_token(client, test_user_credentials):
    """Get a valid access token for testing."""
    # Returns valid JWT token
```

### Database Fixtures

```python
@pytest.fixture
def clean_user_db():
    """Ensure user database is in clean state."""
    # Saves and restores DB state

@pytest.fixture
def redis_client():
    """Create Redis client for testing."""
    # Returns Redis client or None if unavailable
```

### Test Data Fixtures

```python
@pytest.fixture
def sample_consciousness_query():
    """Provide sample consciousness query data."""
    return {
        "query": "What is consciousness?",
        "context": {"user_id": "test_user"}
    }
```

## Writing New Tests

### Test Template

```python
import pytest
from fastapi.testclient import TestClient

class TestMyFeature:
    """Tests for my new feature."""
    
    @pytest.fixture
    def auth_headers(self):
        """Get authentication headers."""
        # Use shared fixture from conftest.py
        pass
    
    def test_feature_success(self, client, auth_headers):
        """Test successful feature execution."""
        response = client.get(
            "/api/v1/my-feature",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "expected_field" in response.json()
    
    def test_feature_validation(self, client, auth_headers):
        """Test input validation."""
        response = client.post(
            "/api/v1/my-feature",
            headers=auth_headers,
            json={"invalid": "data"}
        )
        assert response.status_code == 422
```

### Best Practices

1. **Use Descriptive Names**: Test names should clearly describe what they test
2. **One Assertion Per Concept**: Keep tests focused
3. **Use Fixtures**: Leverage shared fixtures for common setup
4. **Test Edge Cases**: Include boundary conditions and error cases
5. **Mock External Dependencies**: Use mocks for external services
6. **Clean Up**: Ensure tests clean up after themselves
7. **Document Complex Tests**: Add docstrings explaining test purpose

## Continuous Integration

Tests run automatically on:

- **Every Push**: Unit and integration tests
- **Pull Requests**: Full test suite with coverage
- **Pre-deployment**: Security and performance tests

See `.github/workflows/ci.yml` for CI configuration.

## Coverage Reports

### Terminal Report

```
Name                Stmts   Miss  Cover   Missing
-------------------------------------------------
api_server.py         450     45    90%   123-145, 234-256
consciousness.py      200     15    92%   89-92, 156-160
-------------------------------------------------
TOTAL                 650     60    91%
```

### HTML Report

Generated in `htmlcov/index.html`:
- Line-by-line coverage visualization
- Missing coverage highlighted in red
- Branch coverage details

### JSON Report

Generated in `coverage.json`:
- Machine-readable coverage data
- Integration with CI/CD tools
- Historical coverage tracking

## Troubleshooting

### Tests Failing

```bash
# Run with verbose output
pytest -vv

# Run with print statements visible
pytest -s

# Run with detailed traceback
pytest --tb=long

# Run last failed tests only
pytest --lf
```

### Coverage Issues

```bash
# Check which files are being measured
pytest --cov=api_server --cov-report=term-missing

# Verify .coveragerc configuration
cat .coveragerc

# Clear coverage cache
rm -rf .coverage htmlcov/
```

### Redis Tests Failing

```bash
# Check Redis is running
redis-cli ping

# Skip Redis tests if unavailable
pytest -m "not redis"

# Start Redis for testing
redis-server redis.conf
```

## Performance Testing

### Load Testing with Locust

Create `tests/load_test.py` (see Priority 4 in TODO):

```python
from locust import HttpUser, task, between

class SovereignCoreUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login and get token
        response = self.client.post("/token", data={
            "username": "testuser",
            "password": "testpass123"
        })
        self.token = response.json()["access_token"]
    
    @task
    def query_consciousness(self):
        self.client.post(
            "/api/v1/consciousness/query",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"query": "Test query"}
        )
```

Run load tests:

```bash
locust -f tests/load_test.py --host=http://localhost:8528
```

## Security Testing

### SQL Injection Tests

```python
def test_sql_injection_protection(client, auth_headers):
    """Test SQL injection attempts are blocked."""
    malicious_input = "'; DROP TABLE users; --"
    response = client.post(
        "/api/v1/query",
        headers=auth_headers,
        json={"query": malicious_input}
    )
    # Should handle safely
    assert response.status_code in [200, 400, 422]
```

### XSS Tests

```python
def test_xss_protection(client, auth_headers):
    """Test XSS attempts are sanitized."""
    xss_input = "<script>alert('xss')</script>"
    response = client.post(
        "/api/v1/query",
        headers=auth_headers,
        json={"query": xss_input}
    )
    # Response should not contain unescaped script
    assert "<script>" not in response.text
```

## Next Steps

1. **Run Initial Tests**: `./run_tests.sh`
2. **Review Coverage**: Open `htmlcov/index.html`
3. **Add Missing Tests**: Focus on uncovered lines
4. **Implement Load Tests**: Create `tests/load_test.py`
5. **Set Up CI**: Ensure tests run on every commit

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Locust Documentation](https://docs.locust.io/)
