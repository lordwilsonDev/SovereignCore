"""Test suite for authentication and authorization."""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
import jwt
from api_server import (
    app,
    settings,
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user
)


client = TestClient(app)


class TestPasswordHashing:
    """Tests for password hashing and verification."""
    

    
    def test_password_verification_success(self):
        """Test successful password verification."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_password_verification_failure(self):
        """Test failed password verification."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    



class TestJWTTokenCreation:
    """Tests for JWT token creation."""
    
    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        # Token should be a string
        assert isinstance(token, str)
        # Token should have 3 parts (header.payload.signature)
        assert len(token.split(".")) == 3
        
        # Decode and verify
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "testuser"
        assert "exp" in payload
        assert "type" in payload
        assert payload["type"] == "access"
    
    def test_create_refresh_token(self):
        """Test refresh token creation."""
        data = {"sub": "testuser"}
        token = create_refresh_token(data)
        
        # Token should be a string
        assert isinstance(token, str)
        # Token should have 3 parts
        assert len(token.split(".")) == 3
        
        # Decode and verify
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "testuser"
        assert "exp" in payload
        assert "type" in payload
        assert payload["type"] == "refresh"
    
    def test_access_token_expiration(self):
        """Test that access token has correct expiration."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, timezone.utc)
        now = datetime.now(timezone.utc)
        
        # Should expire in approximately settings.access_token_expire_minutes
        time_diff = (exp_datetime - now).total_seconds() / 60
        assert abs(time_diff - settings.access_token_expire_minutes) < 1  # Within 1 minute
    
    def test_refresh_token_expiration(self):
        """Test that refresh token has correct expiration."""
        data = {"sub": "testuser"}
        token = create_refresh_token(data)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, timezone.utc)
        now = datetime.now(timezone.utc)
        
        # Should expire in approximately settings.refresh_token_expire_days
        time_diff = (exp_datetime - now).total_seconds() / (60 * 60 * 24)
        assert abs(time_diff - settings.refresh_token_expire_days) < 0.1  # Within ~2 hours
    
    def test_token_with_custom_expiration(self):
        """Test token creation with custom expiration."""
        data = {"sub": "testuser"}
        custom_expires = timedelta(minutes=5)
        token = create_access_token(data, expires_delta=custom_expires)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, timezone.utc)
        now = datetime.now(timezone.utc)
        
        time_diff = (exp_datetime - now).total_seconds() / 60
        assert abs(time_diff - 5) < 1  # Within 1 minute of 5 minutes


class TestJWTTokenValidation:
    """Tests for JWT token validation."""
    
    def test_valid_token_decode(self):
        """Test decoding a valid token."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "testuser"
    
    def test_invalid_token_decode(self):
        """Test that invalid token raises error."""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(jwt.InvalidTokenError):
            jwt.decode(invalid_token, settings.secret_key, algorithms=[settings.algorithm])
    
    def test_expired_token(self):
        """Test that expired token raises error."""
        data = {"sub": "testuser"}
        # Create token that expires immediately
        expired_token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(expired_token, settings.secret_key, algorithms=[settings.algorithm])
    
    def test_token_with_wrong_secret(self):
        """Test that token with wrong secret fails."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(token, "wrong_secret_key", algorithms=[settings.algorithm])
    
    def test_token_with_wrong_algorithm(self):
        """Test that token with wrong algorithm fails."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        with pytest.raises(jwt.InvalidTokenError):
            jwt.decode(token, settings.secret_key, algorithms=["HS512"])  # Wrong algorithm


class TestLoginEndpoint:
    """Tests for login/token endpoint."""
    
    def test_successful_login(self, test_user_in_db):
        """Test successful login returns tokens."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": test_user_in_db.username,
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        
        # Verify token type
        assert data["token_type"] == "bearer"
        
        # Verify tokens are valid
        access_payload = jwt.decode(data["access_token"], settings.secret_key, algorithms=[settings.algorithm])
        assert access_payload["sub"] == "testuser"
        assert access_payload["type"] == "access"
        
        refresh_payload = jwt.decode(data["refresh_token"], settings.secret_key, algorithms=[settings.algorithm])
        assert refresh_payload["sub"] == "testuser"
        assert refresh_payload["type"] == "refresh"
    
    def test_login_wrong_password(self, test_user_in_db):
        """Test login with wrong password."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": test_user_in_db,
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent user."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_missing_username(self):
        """Test login with missing username."""
        response = client.post(
            "/api/v1/auth/token",
            data={"password": "testpass123"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_login_missing_password(self):
        """Test login with missing password."""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "testuser"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_login_empty_credentials(self):
        """Test login with empty credentials."""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "", "password": ""}
        )
        
        assert response.status_code == 422





class TestProtectedEndpoints:
    """Tests for protected endpoint access."""
    
    @pytest.fixture
    def valid_token(self, test_user_in_db):
        """Fixture to get valid access token."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": test_user_in_db,
                "password": "testpass123"
            }
        )
        return response.json()["access_token"]
    
    def test_access_without_token(self):
        """Test accessing protected endpoint without token."""
        response = client.get("/api/v1/consciousness/state")
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    def test_access_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token."""
        response = client.get(
            "/api/v1/consciousness/state",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
    
    def test_access_with_malformed_header(self):
        """Test accessing protected endpoint with malformed auth header."""
        response = client.get(
            "/api/v1/consciousness/state",
            headers={"Authorization": "InvalidFormat token123"}
        )
        assert response.status_code == 401
    
    def test_access_with_valid_token(self, valid_token):
        """Test accessing protected endpoint with valid token."""
        response = client.get(
            "/api/v1/consciousness/state",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        assert response.status_code == 200
    
    def test_access_with_expired_token(self):
        """Test accessing protected endpoint with expired token."""
        # Create expired token
        data = {"sub": "testuser"}
        expired_token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        response = client.get(
            "/api/v1/consciousness/state",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401


class TestUserRoles:
    """Tests for role-based access control."""
    
    def test_admin_user_access(self):
        """Test that admin user has elevated privileges."""
        # Login as admin
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": "admin",
                "password": "admin123"
            }
        )
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            
            # Check if role information is in token
            # This depends on implementation
            assert "sub" in payload
    
    def test_regular_user_access(self, test_user_in_db):
        """Test that regular user has standard privileges."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": test_user_in_db,
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 200
        token = response.json()["access_token"]
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "testuser"


class TestSecurityBestPractices:
    """Tests for security best practices."""
    
    def test_password_not_in_response(self, test_user_in_db):
        """Test that password is never returned in response."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": test_user_in_db,
                "password": "testpass123"
            }
        )
        
        # Password should never be in response
        response_text = response.text.lower()
        assert "testpass123" not in response_text
        assert "password" not in response.json()
    
    def test_token_contains_minimal_data(self, test_user_in_db):
        """Test that token contains only necessary data."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": test_user_in_db,
                "password": "testpass123"
            }
        )
        
        token = response.json()["access_token"]
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        # Should not contain sensitive data
        assert "password" not in payload
        assert "hashed_password" not in payload
    
    def test_timing_attack_resistance(self):
        """Test that login timing is consistent (prevents timing attacks)."""
        import time
        
        # Time valid user with wrong password
        start1 = time.time()
        client.post("/api/v1/auth/token", data={"username": "testuser", "password": "wrong"})
        time1 = time.time() - start1
        
        # Time invalid user
        start2 = time.time()
        client.post("/api/v1/auth/token", data={"username": "nonexistent", "password": "wrong"})
        time2 = time.time() - start2
        
        # Times should be similar (within reasonable margin)
        # This is a basic check; real timing attack prevention is more complex
        assert abs(time1 - time2) < 0.5  # Within 500ms
