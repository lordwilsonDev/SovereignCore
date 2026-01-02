"""Pytest configuration and shared fixtures for SovereignCore tests."""
import pytest
import os
import sys
from typing import Generator, Dict
from fastapi.testclient import TestClient
import redis
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api_server import app, get_password_hash
from database import SessionLocal, User, pwd_context, engine, Base

# Create tables for tests
Base.metadata.create_all(bind=engine)

# ============================================================================
# Test Client Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def test_client(db_session) -> TestClient:
    """Create a test client for the FastAPI application.
    
    Overrides the database dependency to use the test session.
    """
    from api_server import get_database
    app.dependency_overrides[get_database] = lambda: db_session
    return TestClient(app)


@pytest.fixture(scope="function")
def client(test_client) -> TestClient:
    """Create a fresh test client for each test function."""
    return test_client


# ============================================================================
# Authentication Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def test_user_credentials() -> Dict[str, str]:
    """Provide test user credentials."""
    return {
        "username": "testuser",
        "password": "testpass123"
    }


@pytest.fixture(scope="session")
def admin_user_credentials() -> Dict[str, str]:
    """Provide admin user credentials."""
    return {
        "username": "admin",
        "password": "admin123"
    }


@pytest.fixture(scope="function")
def access_token(client: TestClient, test_user_credentials: Dict[str, str], test_user_in_db: str) -> str:
    """Get a valid access token for testing.
    
    Args:
        client: Test client fixture
        test_user_credentials: Test user credentials
        test_user_in_db: Ensure user exists
    
    Returns:
        Valid JWT access token
    """
    response = client.post(
        "/api/v1/auth/token",
        data=test_user_credentials
    )
    assert response.status_code == 200, f"Failed to get token: {response.json()}"
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def refresh_token(client: TestClient, test_user_credentials: Dict[str, str], test_user_in_db: str) -> str:
    """Get a valid refresh token for testing."""
    response = client.post(
        "/api/v1/auth/token",
        data=test_user_credentials
    )
    assert response.status_code == 200, f"Failed to get token: {response.json()}"
    return response.json()["refresh_token"]


@pytest.fixture(scope="function")
def auth_headers(access_token: str) -> Dict[str, str]:
    """Get authorization headers with valid token."""
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="function")
def admin_token(client: TestClient, admin_user_credentials: Dict[str, str], test_user_in_db: str) -> str:
    """Get a valid admin access token for testing."""
    # Ensure admin exists
    db = SessionLocal()
    if not db.query(User).filter(User.username == "admin").first():
        admin = User(
            username="admin",
            email="admin@example.com",
            full_name="Admin User",
            hashed_password=pwd_context.hash("admin123"),
            disabled=False,
            is_admin=True
        )
        db.add(admin)
        db.commit()
    db.close()

    response = client.post(
        "/api/v1/auth/token",
        data=admin_user_credentials
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


@pytest.fixture(scope="function")
def admin_headers(admin_token: str) -> Dict[str, str]:
    """Get authorization headers with valid admin token."""
    if admin_token:
        return {"Authorization": f"Bearer {admin_token}"}
    return {}


@pytest.fixture(autouse=True)
def patch_pwd_context(monkeypatch):
    """Patch password context to use plaintext for testing."""
    from passlib.context import CryptContext
    test_context = CryptContext(schemes=["plaintext"], deprecated="auto")
    
    # Patch both module instances
    monkeypatch.setattr("api_server.pwd_context", test_context)
    monkeypatch.setattr("database.pwd_context", test_context)


@pytest.fixture(autouse=True)
def mock_rate_limiter(monkeypatch):
    """Disable rate limiting during tests."""
    monkeypatch.setattr("api_server.limiter.enabled", False)



@pytest.fixture(autouse=True)
def mock_bridge(monkeypatch):
    """Mock the ConsciousnessBridge to prevent complex init during tests."""
    from unittest.mock import MagicMock
    from datetime import datetime
    
    mock = MagicMock()
    # Setup default state
    state = MagicMock()
    state.silicon_id = "test_silicon_id_123"
    state.consciousness_level = 95.5
    state.love_frequency = 528.0
    state.thermal_state = "NOMINAL"
    state.cognitive_mode = "FLOW"
    state.active_since = datetime.now(timezone.utc)
    
    mock.get_state.return_value = state
    
    # Patch the global bridge variable in api_server
    monkeypatch.setattr("api_server.bridge", mock)
    return mock 


@pytest.fixture(scope="function")
def db_session():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def clean_user_db(db_session):
    """Ensure user database is in clean state before test."""
    # Clean users table
    db_session.query(User).delete()
    db_session.commit()
    
    yield
    
    # Cleanup after
    db_session.query(User).delete()
    db_session.commit()


@pytest.fixture(scope="function")
def test_user_in_db(db_session, clean_user_db):
    """Ensure test user exists in database."""
    username = "testuser"
    # Create test user
    user = db_session.query(User).filter(User.username == username).first()
    if not user:
        user = User(
            username=username,
            email="test@example.com",
            full_name="Test User",
            hashed_password="testpass123",  # Plaintext for test
            disabled=False,
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()
    
    # Return a string that also has .username attribute
    # This supports tests using test_user_in_db.username AND test_user_in_db as str
    class TestUserStr(str):
        @property
        def username(self):
            return self
            
    return TestUserStr(username)


# ============================================================================
# Redis Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def redis_client():
    """Create Redis client for testing.
    
    Returns:
        Redis client or None if Redis is not available
    """
    try:
        client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            password=os.getenv("REDIS_PASSWORD"),
            decode_responses=True
        )
        # Test connection
        client.ping()
        return client
    except (redis.ConnectionError, redis.TimeoutError):
        # Redis not available, return None
        return None


@pytest.fixture(scope="function")
def clean_redis(redis_client):
    """Clean Redis test database before and after test.
    
    Args:
        redis_client: Redis client fixture
    
    Yields:
        Redis client
    """
    if redis_client is None:
        pytest.skip("Redis not available")
    
    # Clean before test
    test_keys = redis_client.keys("test:*")
    if test_keys:
        redis_client.delete(*test_keys)
    
    yield redis_client
    
    # Clean after test
    test_keys = redis_client.keys("test:*")
    if test_keys:
        redis_client.delete(*test_keys)


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_consciousness_query() -> Dict:
    """Provide sample consciousness query data.
    
    Returns:
        Dict with sample query data
    """
    return {
        "query": "What is the nature of consciousness?",
        "context": {
            "user_id": "test_user",
            "session_id": "test_session_123",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@pytest.fixture
def sample_queries() -> list:
    """Provide multiple sample queries for batch testing.
    
    Returns:
        List of query dicts
    """
    return [
        {"query": "What is consciousness?", "context": {"user_id": "user1"}},
        {"query": "How does memory work?", "context": {"user_id": "user2"}},
        {"query": "What is self-awareness?", "context": {"user_id": "user3"}},
        {"query": "Can machines think?", "context": {"user_id": "user4"}},
        {"query": "What is intelligence?", "context": {"user_id": "user5"}}
    ]


@pytest.fixture
def invalid_queries() -> list:
    """Provide invalid query data for negative testing.
    
    Returns:
        List of invalid query dicts
    """
    return [
        {},  # Empty
        {"query": ""},  # Empty query
        {"query": None},  # Null query
        {"invalid_field": "test"},  # Wrong field
        {"query": 12345},  # Wrong type
        {"query": ["list", "not", "string"]},  # Wrong type
    ]


# ============================================================================
# Environment Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def test_env_vars():
    """Set up test environment variables.
    
    Yields control to tests, then restores original environment.
    """
    # Save original environment
    original_env = os.environ.copy()
    
    # Set test environment variables
    test_vars = {
        "ENVIRONMENT": "test",
        "SECRET_KEY": "test_secret_key_for_testing_only",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "LOG_LEVEL": "DEBUG"
    }
    
    for key, value in test_vars.items():
        os.environ[key] = value
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# ============================================================================
# Performance Testing Fixtures
# ============================================================================

@pytest.fixture
def benchmark_timer():
    """Provide a simple timer for benchmarking.
    
    Returns:
        Timer context manager
    """
    import time
    from contextlib import contextmanager
    
    @contextmanager
    def timer():
        start = time.time()
        elapsed = {"time": 0}
        yield elapsed
        elapsed["time"] = time.time() - start
    
    return timer


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_redis_unavailable(monkeypatch):
    """Mock Redis as unavailable for testing error handling.
    
    Args:
        monkeypatch: Pytest monkeypatch fixture
    """
    def mock_redis_connection(*args, **kwargs):
        raise redis.ConnectionError("Redis unavailable")
    
    monkeypatch.setattr("redis.Redis.ping", mock_redis_connection)


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers.
    
    Args:
        config: Pytest config object
    """
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "redis: marks tests that require Redis"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically.
    
    Args:
        config: Pytest config object
        items: List of test items
    """
    for item in items:
        # Add 'redis' marker to tests that use redis fixtures
        if "redis_client" in item.fixturenames or "clean_redis" in item.fixturenames:
            item.add_marker(pytest.mark.redis)
        
        # Add 'integration' marker to integration tests
        if "integration" in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)
        
        # Add 'unit' marker to unit tests
        if "unit" in item.nodeid.lower():
            item.add_marker(pytest.mark.unit)


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_artifacts():
    """Clean up test artifacts after test session.
    
    Runs automatically after all tests complete.
    """
    yield
    
    # Clean up any test files, logs, etc.
    import glob
    test_files = glob.glob("test_*.log") + glob.glob("*.test.db")
    for file in test_files:
        try:
            os.remove(file)
        except OSError:
            pass


# ============================================================================
# Logging Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def capture_logs(caplog):
    """Capture logs during test execution.
    
    Args:
        caplog: Pytest caplog fixture
    
    Returns:
        Caplog fixture with INFO level
    """
    import logging
    caplog.set_level(logging.INFO)
    return caplog
