"""Database models and connection management for SovereignCore."""
import os
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sovereign_users.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================================
# Database Models
# ============================================================================

class User(Base):
    """User model for authentication and authorization."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    disabled = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"
    
    def to_dict(self):
        """Convert user to dictionary (excluding password)."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "disabled": self.disabled,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }


class PasswordResetToken(Base):
    """Password reset token model."""
    
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f"<PasswordResetToken(user_id={self.user_id}, used={self.used})>"


# ============================================================================
# Database Functions
# ============================================================================

def get_db() -> Session:
    """Get database session.
    
    Yields:
        Database session
    
    Usage:
        with get_db() as db:
            user = db.query(User).filter(User.username == "test").first()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables.
    
    Creates all tables defined in Base metadata.
    """
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")


def create_default_users():
    """Create default users for testing and initial setup."""
    db = SessionLocal()
    try:
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"✓ Database already has {existing_users} user(s)")
            return
        
        # Create default test user
        test_user = User(
            username="testuser",
            email="test@sovereigncore.local",
            full_name="Test User",
            hashed_password=pwd_context.hash("testpass123"),
            disabled=False,
            is_admin=False
        )
        db.add(test_user)
        
        # Create default admin user
        admin_user = User(
            username="admin",
            email="admin@sovereigncore.local",
            full_name="Administrator",
            hashed_password=pwd_context.hash("admin123"),
            disabled=False,
            is_admin=True
        )
        db.add(admin_user)
        
        db.commit()
        print("✓ Default users created:")
        print("  - testuser (password: testpass123)")
        print("  - admin (password: admin123)")
        print("\n⚠️  IMPORTANT: Change these passwords in production!")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error creating default users: {e}")
        raise
    finally:
        db.close()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username.
    
    Args:
        db: Database session
        username: Username to search for
    
    Returns:
        User object or None if not found
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email.
    
    Args:
        db: Database session
        email: Email to search for
    
    Returns:
        User object or None if not found
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID.
    
    Args:
        db: Database session
        user_id: User ID to search for
    
    Returns:
        User object or None if not found
    """
    return db.query(User).filter(User.id == user_id).first()


def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    full_name: Optional[str] = None,
    is_admin: bool = False
) -> User:
    """Create a new user.
    
    Args:
        db: Database session
        username: Username
        email: Email address
        password: Plain text password (will be hashed)
        full_name: Full name (optional)
        is_admin: Whether user is admin (default: False)
    
    Returns:
        Created User object
    
    Raises:
        ValueError: If username or email already exists
    """
    # Check if username exists
    if get_user_by_username(db, username):
        raise ValueError(f"Username '{username}' already exists")
    
    # Check if email exists
    if get_user_by_email(db, email):
        raise ValueError(f"Email '{email}' already exists")
    
    # Create user
    user = User(
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=pwd_context.hash(password),
        disabled=False,
        is_admin=is_admin
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


def update_user_password(db: Session, user_id: int, new_password: str) -> bool:
    """Update user password.
    
    Args:
        db: Database session
        user_id: User ID
        new_password: New plain text password (will be hashed)
    
    Returns:
        True if successful, False otherwise
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.hashed_password = pwd_context.hash(new_password)
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    return True


def update_last_login(db: Session, user_id: int) -> bool:
    """Update user's last login timestamp.
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        True if successful, False otherwise
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    
    return True


def disable_user(db: Session, user_id: int) -> bool:
    """Disable a user account.
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        True if successful, False otherwise
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.disabled = True
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    return True


def enable_user(db: Session, user_id: int) -> bool:
    """Enable a user account.
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        True if successful, False otherwise
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.disabled = False
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    return True


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
    
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user.
    
    Args:
        db: Database session
        username: Username
        password: Plain text password
    
    Returns:
        User object if authentication successful, None otherwise
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    if user.disabled:
        return None
    
    # Update last login
    update_last_login(db, user.id)
    
    return user


# ============================================================================
# Password Reset Functions
# ============================================================================

def create_password_reset_token(
    db: Session,
    user_id: int,
    token: str,
    expires_at: datetime
) -> PasswordResetToken:
    """Create a password reset token.
    
    Args:
        db: Database session
        user_id: User ID
        token: Reset token
        expires_at: Expiration datetime
    
    Returns:
        Created PasswordResetToken object
    """
    reset_token = PasswordResetToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        used=False
    )
    
    db.add(reset_token)
    db.commit()
    db.refresh(reset_token)
    
    return reset_token


def get_password_reset_token(db: Session, token: str) -> Optional[PasswordResetToken]:
    """Get password reset token.
    
    Args:
        db: Database session
        token: Reset token
    
    Returns:
        PasswordResetToken object or None if not found
    """
    return db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.used == False,
        PasswordResetToken.expires_at > datetime.now(timezone.utc)
    ).first()


def mark_token_as_used(db: Session, token_id: int) -> bool:
    """Mark a password reset token as used.
    
    Args:
        db: Database session
        token_id: Token ID
    
    Returns:
        True if successful, False otherwise
    """
    token = db.query(PasswordResetToken).filter(PasswordResetToken.id == token_id).first()
    if not token:
        return False
    
    token.used = True
    db.commit()
    
    return True


# ============================================================================
# Initialization
# ============================================================================

if __name__ == "__main__":
    print("Initializing SovereignCore database...")
    print(f"Database URL: {DATABASE_URL}")
    print()
    
    # Create tables
    init_db()
    
    # Create default users
    create_default_users()
    
    print()
    print("✓ Database initialization complete!")
