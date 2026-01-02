from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.config import settings

# Initialize Argon2 hasher (Modern replacement for passlib)
password_hash = PasswordHash.recommended()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return password_hash.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire.timestamp()}) # Intentionally using timestamp for JWT standard
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
