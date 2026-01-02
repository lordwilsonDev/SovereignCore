"""User management routes for SovereignCore API."""
from datetime import datetime, timedelta
from typing import Optional
import secrets

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr, Field, validator
from slowapi import Limiter
from slowapi.util import get_remote_address

from database import (
    get_db,
    create_user,
    get_user_by_username,
    get_user_by_email,
    update_user_password,
    create_password_reset_token,
    get_password_reset_token,
    mark_token_as_used,
    User as DBUser
)
from logging_config import logger

# Create router
router = APIRouter(prefix="/api/v1/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)

# ============================================================================
# MODELS
# ============================================================================

class UserRegistration(BaseModel):
    """User registration request."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format."""
        if not v.isalnum() and '_' not in v and '-' not in v:
            raise ValueError('Username must be alphanumeric with optional _ or -')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserResponse(BaseModel):
    """User response model."""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    disabled: bool
    is_admin: bool
    created_at: str
    
    class Config:
        from_attributes = True


class PasswordResetRequest(BaseModel):
    """Password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class PasswordChange(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


# ============================================================================
# DATABASE DEPENDENCY
# ============================================================================

def get_database():
    """Get database session dependency."""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# ROUTES
# ============================================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/hour")  # Strict limit to prevent abuse
async def register_user(
    request: Request,
    user_data: UserRegistration,
    db = Depends(get_database)
):
    """Register a new user.
    
    Creates a new user account with the provided credentials.
    Passwords are hashed using bcrypt before storage.
    """
    try:
        # Create user
        new_user = create_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            is_admin=False
        )
        
        logger.info(
            "User registered",
            username=new_user.username,
            email=new_user.email,
            request_id=getattr(request.state, 'request_id', 'unknown')
        )
        
        return UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            full_name=new_user.full_name,
            disabled=new_user.disabled,
            is_admin=new_user.is_admin,
            created_at=new_user.created_at.isoformat()
        )
        
    except ValueError as e:
        # Username or email already exists
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            "User registration failed",
            error=str(e),
            request_id=getattr(request.state, 'request_id', 'unknown')
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/password-reset/request")
@limiter.limit("3/hour")  # Strict limit to prevent abuse
async def request_password_reset(
    request: Request,
    reset_request: PasswordResetRequest,
    db = Depends(get_database)
):
    """Request a password reset.
    
    Generates a password reset token and sends it to the user's email.
    In production, this should send an email with the reset link.
    """
    # Get user by email
    user = get_user_by_email(db, reset_request.email)
    
    # Always return success to prevent email enumeration
    # Don't reveal whether the email exists or not
    response_message = {
        "message": "If the email exists, a password reset link has been sent."
    }
    
    if user:
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # Store token in database
        create_password_reset_token(
            db=db,
            user_id=user.id,
            token=reset_token,
            expires_at=expires_at
        )
        
        logger.info(
            "Password reset requested",
            user_id=user.id,
            email=user.email,
            request_id=getattr(request.state, 'request_id', 'unknown')
        )
        
        # TODO: Send email with reset link
        # In development, log the token (REMOVE IN PRODUCTION)
        if request.app.state.get('debug', False):
            logger.debug("Password reset token", token=reset_token, email=user.email)
    
    return response_message


@router.post("/password-reset/confirm")
@limiter.limit("5/hour")
async def confirm_password_reset(
    request: Request,
    reset_confirm: PasswordResetConfirm,
    db = Depends(get_database)
):
    """Confirm password reset with token.
    
    Validates the reset token and updates the user's password.
    """
    # Get reset token
    token_record = get_password_reset_token(db, reset_confirm.token)
    
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Update password
    success = update_user_password(
        db=db,
        user_id=token_record.user_id,
        new_password=reset_confirm.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )
    
    # Mark token as used
    mark_token_as_used(db, token_record.id)
    
    logger.info(
        "Password reset completed",
        user_id=token_record.user_id,
        request_id=getattr(request.state, 'request_id', 'unknown')
    )
    
    return {"message": "Password has been reset successfully"}


@router.get("/me", response_model=UserResponse)
@limiter.limit("100/minute")
async def get_current_user_info(
    request: Request,
    current_user: DBUser = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Get current user information.
    
    Returns the authenticated user's profile information.
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        disabled=current_user.disabled,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at.isoformat()
    )


@router.get("/{username}", response_model=UserResponse)
@limiter.limit("100/minute")
async def get_user_by_username_route(
    request: Request,
    username: str,
    db = Depends(get_database)
):
    """Get user by username (public profile).
    
    Returns basic user information. Sensitive data is excluded.
    """
    user = get_user_by_username(db, username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        disabled=user.disabled,
        is_admin=user.is_admin,
        created_at=user.created_at.isoformat()
    )
