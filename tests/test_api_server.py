"""Test suite for API server endpoints."""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import jwt
from api_server import app, get_password_hash


client = TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check_success(self):
        """Test health endpoint returns 200 and correct status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "bridge" in data["components"]


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "SovereignCore" in data["message"]
        assert "version" in data





class TestAuthenticationEndpoints:
    """Tests for authentication endpoints."""
    
    def test_token_endpoint_success(self, test_user_in_db):
        """Test successful token generation."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": test_user_in_db,
                "password": "testpass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    def test_token_endpoint_invalid_credentials(self, test_user_in_db):
        """Test token endpoint with invalid credentials."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": test_user_in_db,
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_token_endpoint_missing_user(self):
        """Test token endpoint with non-existent user."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        assert response.status_code == 401
    



class TestProtectedEndpoints:
    """Tests for endpoints requiring authentication."""
    
    @pytest.fixture
    def auth_headers(self, test_user_in_db):
        """Fixture to get authentication headers."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": test_user_in_db,
                "password": "testpass123"
            }
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_protected_endpoint_without_auth(self):
        """Test protected endpoint without authentication."""
        response = client.get("/api/v1/consciousness/state")
        assert response.status_code == 401
    
    def test_protected_endpoint_with_invalid_token(self):
        """Test protected endpoint with invalid token."""
        response = client.get(
            "/api/v1/consciousness/state",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
    
    def test_protected_endpoint_with_valid_token(self, auth_headers):
        """Test protected endpoint with valid authentication."""
        response = client.get(
            "/api/v1/consciousness/state",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "consciousness_level" in data


class TestConsciousnessEndpoints:
    """Tests for consciousness-related endpoints."""
    
    @pytest.fixture
    def auth_headers(self, test_user_in_db):
        """Fixture to get authentication headers."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": test_user_in_db,
                "password": "testpass123"
            }
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_consciousness_status(self, auth_headers):
        """Test consciousness status endpoint."""
        response = client.get(
            "/api/v1/consciousness/state",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "consciousness_level" in data
        assert "silicon_id" in data
    
    def test_consciousness_query(self, auth_headers):
        """Test consciousness query endpoint."""
        response = client.post(
            "/api/v1/consciousness/process",
            headers=auth_headers,
            json={
                "prompt": "What is consciousness?",
                "context": {"user_id": "test_user"}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "request_id" in data
    
    def test_consciousness_query_invalid_input(self, auth_headers):
        """Test consciousness query with invalid input."""
        response = client.post(
            "/api/v1/consciousness/process",
            headers=auth_headers,
            json={"invalid": "data"}
        )
        assert response.status_code == 422  # Validation error





class TestSecurityHeaders:
    """Tests for security headers."""
    
    def test_security_headers_present(self):
        """Test that security headers are set correctly."""
        response = client.get("/")
        
        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        
        # HSTS header (if HTTPS is enabled)
        if str(response.url).startswith("https"):
            assert "Strict-Transport-Security" in response.headers


class TestCORS:
    """Tests for CORS configuration."""
    
    def test_cors_headers(self):
        """Test that CORS headers are configured."""
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers or response.status_code == 200


class TestInputValidation:
    """Tests for input validation."""
    
    @pytest.fixture
    def auth_headers(self, test_user_in_db):
        """Fixture to get authentication headers."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": test_user_in_db,
                "password": "testpass123"
            }
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_invalid_json_payload(self, auth_headers):
        """Test that invalid JSON is rejected."""
        response = client.post(
            "/api/v1/consciousness/process",
            data="{invalid json}",
            headers={**auth_headers, "Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]
    
    def test_missing_required_fields(self, auth_headers):
        """Test that missing required fields are caught."""
        response = client.post(
            "/api/v1/consciousness/process",
            headers=auth_headers,
            json={}  # Missing required 'prompt' field
        )
        assert response.status_code == 422
        assert "prompt" in response.json()["detail"][0]["loc"]


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_404_not_found(self):
        """Test 404 error for non-existent endpoint."""
        response = client.get("/nonexistent/endpoint")
        assert response.status_code == 404
    
    def test_405_method_not_allowed(self):
        """Test 405 error for wrong HTTP method."""
        response = client.post("/health")  # Health only accepts GET
        assert response.status_code == 405



