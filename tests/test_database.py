"""Tests for database.py - User model and database functions."""
import pytest
from datetime import datetime, timedelta
import uuid


def unique_id():
    """Generate unique suffix for test identifiers."""
    return uuid.uuid4().hex[:8]


class TestUserModel:
    """Tests for User model."""
    
    def test_user_creation(self, db_session):
        """Test that a User can be created with required fields."""
        from database import User, pwd_context
        
        uid = unique_id()
        user = User(
            username=f"user_{uid}",
            email=f"{uid}@example.com",
            full_name="New User",
            hashed_password=pwd_context.hash("password123"),
            disabled=False,
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert f"user_{uid}" in user.username
    
    def test_user_repr(self, db_session):
        """Test User __repr__ method."""
        from database import User
        
        uid = unique_id()
        user = User(
            username=f"repr_{uid}",
            email=f"repr_{uid}@example.com",
            hashed_password="hashed",
            disabled=False,
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()
        
        repr_str = repr(user)
        assert f"repr_{uid}" in repr_str
    
    def test_user_to_dict(self, db_session):
        """Test User to_dict method."""
        from database import User
        
        uid = unique_id()
        user = User(
            username=f"dict_{uid}",
            email=f"dict_{uid}@example.com",
            full_name="Dict User",
            hashed_password="hashed",
            disabled=False,
            is_admin=True
        )
        db_session.add(user)
        db_session.commit()
        
        user_dict = user.to_dict()
        
        assert f"dict_{uid}" in user_dict["username"]
        assert user_dict["is_admin"] == True
        assert "hashed_password" not in user_dict


class TestDatabaseFunctions:
    """Tests for database utility functions."""
    
    def test_get_db_yields_session(self):
        """Test that get_db yields a valid session."""
        from database import get_db
        
        gen = get_db()
        db = next(gen)
        assert db is not None
        try:
            next(gen)
        except StopIteration:
            pass
    
    def test_init_db_creates_tables(self):
        """Test that init_db creates all tables."""
        from database import init_db, Base
        
        init_db()
        assert "users" in Base.metadata.tables
    
    def test_get_user_by_username(self, db_session):
        """Test get_user_by_username."""
        from database import User, get_user_by_username
        
        uid = unique_id()
        user = User(
            username=f"find_{uid}",
            email=f"find_{uid}@example.com",
            hashed_password="hashed",
            disabled=False,
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()
        
        found = get_user_by_username(db_session, f"find_{uid}")
        assert found is not None
        assert found.username == f"find_{uid}"
    
    def test_get_user_by_username_not_found(self, db_session):
        """Test get_user_by_username when user doesn't exist."""
        from database import get_user_by_username
        
        found = get_user_by_username(db_session, f"nonexistent_{unique_id()}")
        assert found is None
    
    def test_get_user_by_email(self, db_session):
        """Test get_user_by_email."""
        from database import User, get_user_by_email
        
        uid = unique_id()
        user = User(
            username=f"email_{uid}",
            email=f"emailtest_{uid}@example.com",
            hashed_password="hashed",
            disabled=False,
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()
        
        found = get_user_by_email(db_session, f"emailtest_{uid}@example.com")
        assert found is not None
    
    def test_verify_password_correct(self):
        """Test verify_password with correct password."""
        from database import verify_password, pwd_context
        
        hashed = pwd_context.hash("secret123")
        assert verify_password("secret123", hashed) == True
    
    def test_verify_password_incorrect(self):
        """Test verify_password with incorrect password."""
        from database import verify_password, pwd_context
        
        hashed = pwd_context.hash("secret123")
        assert verify_password("wrongpassword", hashed) == False


class TestUserAuthentication:
    """Tests for user authentication functions."""
    
    def test_authenticate_user_success(self, db_session):
        """Test authenticate_user with valid credentials."""
        from database import User, authenticate_user, pwd_context
        
        uid = unique_id()
        user = User(
            username=f"auth_{uid}",
            email=f"auth_{uid}@example.com",
            hashed_password=pwd_context.hash("authpass123"),
            disabled=False,
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()
        
        authenticated = authenticate_user(db_session, f"auth_{uid}", "authpass123")
        assert authenticated is not None
        assert authenticated.username == f"auth_{uid}"
    
    def test_authenticate_user_wrong_password(self, db_session):
        """Test authenticate_user with wrong password."""
        from database import User, authenticate_user, pwd_context
        
        uid = unique_id()
        user = User(
            username=f"authwrong_{uid}",
            email=f"authwrong_{uid}@example.com",
            hashed_password=pwd_context.hash("correctpass"),
            disabled=False,
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()
        
        authenticated = authenticate_user(db_session, f"authwrong_{uid}", "wrongpass")
        assert authenticated is None or authenticated is False
    
    def test_authenticate_user_nonexistent(self, db_session):
        """Test authenticate_user with nonexistent user."""
        from database import authenticate_user
        
        authenticated = authenticate_user(db_session, f"ghost_{unique_id()}", "anypass")
        assert authenticated is None or authenticated is False


class TestUserCRUD:
    """Tests for user CRUD operations."""
    
    def test_create_user(self, db_session):
        """Test create_user function."""
        from database import create_user
        
        uid = unique_id()
        user = create_user(
            db=db_session,
            username=f"crud_{uid}",
            email=f"crud_{uid}@example.com",
            password="crudpass123",
            full_name="CRUD User"
        )
        
        assert user is not None
        assert user.username == f"crud_{uid}"
    
    def test_update_last_login(self, db_session):
        """Test update_last_login function."""
        from database import User, update_last_login, pwd_context
        
        uid = unique_id()
        user = User(
            username=f"login_{uid}",
            email=f"login_{uid}@example.com",
            hashed_password=pwd_context.hash("pass"),
            disabled=False,
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()
        
        result = update_last_login(db_session, user.id)
        
        assert result == True
        db_session.refresh(user)
        assert user.last_login is not None
    
    def test_disable_user(self, db_session):
        """Test disable_user function."""
        from database import User, disable_user, pwd_context
        
        uid = unique_id()
        user = User(
            username=f"disable_{uid}",
            email=f"disable_{uid}@example.com",
            hashed_password=pwd_context.hash("pass"),
            disabled=False,
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()
        
        result = disable_user(db_session, user.id)
        
        assert result == True
        db_session.refresh(user)
        assert user.disabled == True
    
    def test_disable_user_not_found(self, db_session):
        """Test disable_user with nonexistent user."""
        from database import disable_user
        
        result = disable_user(db_session, 99999)
        assert result == False
    
    def test_enable_user(self, db_session):
        """Test enable_user function."""
        from database import User, enable_user, pwd_context
        
        uid = unique_id()
        user = User(
            username=f"enable_{uid}",
            email=f"enable_{uid}@example.com",
            hashed_password=pwd_context.hash("pass"),
            disabled=True,  # Start disabled
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()
        
        result = enable_user(db_session, user.id)
        
        assert result == True
        db_session.refresh(user)
        assert user.disabled == False
    
    def test_enable_user_not_found(self, db_session):
        """Test enable_user with nonexistent user."""
        from database import enable_user
        
        result = enable_user(db_session, 99999)
        assert result == False
    
    def test_get_user_by_id(self, db_session):
        """Test get_user_by_id function."""
        from database import User, get_user_by_id, pwd_context
        
        uid = unique_id()
        user = User(
            username=f"byid_{uid}",
            email=f"byid_{uid}@example.com",
            hashed_password=pwd_context.hash("pass"),
            disabled=False,
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()
        
        found = get_user_by_id(db_session, user.id)
        assert found is not None
        assert found.username == f"byid_{uid}"
    
    def test_get_user_by_id_not_found(self, db_session):
        """Test get_user_by_id with nonexistent ID."""
        from database import get_user_by_id
        
        found = get_user_by_id(db_session, 99999)
        assert found is None


class TestPasswordReset:
    """Tests for password reset functions."""
    
    def test_create_password_reset_token(self, db_session):
        """Test create_password_reset_token function."""
        from database import User, create_password_reset_token, pwd_context
        from datetime import timedelta
        
        uid = unique_id()
        user = User(
            username=f"reset_{uid}",
            email=f"reset_{uid}@example.com",
            hashed_password=pwd_context.hash("pass"),
            disabled=False,
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()
        
        token = create_password_reset_token(
            db=db_session,
            user_id=user.id,
            token=f"token_{uid}",
            expires_at=datetime.now() + timedelta(hours=1)
        )
        
        assert token is not None
        assert token.user_id == user.id
        assert token.used == False
    
    def test_mark_token_as_used(self, db_session):
        """Test mark_token_as_used function."""
        from database import User, create_password_reset_token, mark_token_as_used, pwd_context
        from datetime import timedelta
        
        uid = unique_id()
        user = User(
            username=f"markused_{uid}",
            email=f"markused_{uid}@example.com",
            hashed_password=pwd_context.hash("pass"),
            disabled=False,
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()
        
        token = create_password_reset_token(
            db=db_session,
            user_id=user.id,
            token=f"usetoken_{uid}",
            expires_at=datetime.now() + timedelta(hours=1)
        )
        
        result = mark_token_as_used(db_session, token.id)
        
        assert result == True
        db_session.refresh(token)
        assert token.used == True
    
    def test_mark_token_as_used_not_found(self, db_session):
        """Test mark_token_as_used with nonexistent token."""
        from database import mark_token_as_used
        
        result = mark_token_as_used(db_session, 99999)
        assert result == False
    
    def test_update_user_password(self, db_session):
        """Test update_user_password function."""
        from database import User, update_user_password, pwd_context
        
        uid = unique_id()
        old_hash = pwd_context.hash("oldpass")
        user = User(
            username=f"passupd_{uid}",
            email=f"passupd_{uid}@example.com",
            hashed_password=old_hash,
            disabled=False,
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()
        
        result = update_user_password(db_session, user.id, "newpass")
        
        assert result == True
        db_session.refresh(user)
        assert user.hashed_password != old_hash
        assert pwd_context.verify("newpass", user.hashed_password)
    
    def test_update_user_password_not_found(self, db_session):
        """Test update_user_password with nonexistent user."""
        from database import update_user_password
        
        result = update_user_password(db_session, 99999, "newpass")
        assert result == False
