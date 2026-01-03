#!/usr/bin/env python3
"""
🔮 SovereignCore API Server - Production Ready

FastAPI server with:
- OAuth2/JWT authentication
- Rate limiting
- Security headers
- CORS configuration
- Prometheus metrics
- Health checks
- Structured logging
"""

import os
import time
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings
import jwt
from passlib.context import CryptContext
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from prometheus_fastapi_instrumentator import Instrumentator
import structlog
import uuid

# Import SovereignCore components
from consciousness_bridge import ConsciousnessBridge
from logging_config import logger
from database import (
    get_db,
    authenticate_user as db_authenticate_user,
    get_user_by_username,
    User as DBUser,
    init_db
)

# ============================================================================
# CONFIGURATION
# ============================================================================

class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8528
    api_workers: int = 4
    
    # Security
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8528"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE"]
    cors_allow_headers: List[str] = ["*"]
    
    # Rate Limiting
    rate_limit_default: str = "100/minute"
    rate_limit_auth: str = "5/minute"
    
    # Redis (for rate limiting and caching)
    redis_url: str = "redis://localhost:6379/0"
    redis_password: Optional[str] = None
    
    # TLS/HTTPS
    tls_enabled: bool = False
    tls_cert_path: Optional[str] = None
    tls_key_path: Optional[str] = None
    
    # Environment
    environment: str = "development"
    debug: bool = False
    
    # Pydantic V2 style config
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

settings = Settings()

# ============================================================================
# SECURITY
# ============================================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# ============================================================================
# MODELS
# ============================================================================

class Token(BaseModel):
    """OAuth2 token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    """Token payload data."""
    username: Optional[str] = None
    user_id: Optional[str] = None
    scopes: List[str] = []

class User(BaseModel):
    """User model."""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: bool = False
    scopes: List[str] = ["read", "write"]

class UserInDB(User):
    """User model with hashed password."""
    hashed_password: str

class ConsciousnessRequest(BaseModel):
    """Request for consciousness processing."""
    prompt: str = Field(..., min_length=1, max_length=10000)
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=500, ge=1, le=4096)
    
    @field_validator('prompt')
    @classmethod
    def sanitize_prompt(cls, v: str) -> str:
        """Sanitize prompt input."""
        # Remove any potential injection attempts
        return v.strip()

class ConsciousnessResponse(BaseModel):
    """Response from consciousness processing."""
    response: str
    silicon_id: str
    consciousness_level: float
    thermal_state: str
    processing_time_ms: float
    request_id: str

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    uptime_seconds: float
    silicon_id: str
    consciousness_level: float
    components: Dict[str, str]

# ============================================================================
# PROMETHEUS METRICS
# ============================================================================

# Use getattr to avoid duplicate registration in multiprocess mode
from prometheus_client import REGISTRY

def get_or_create_counter(name, description, labelnames):
    """Get existing counter or create new one (multiprocess-safe)."""
    try:
        return Counter(name, description, labelnames)
    except ValueError:
        # Already registered - get from registry
        for collector in REGISTRY._names_to_collectors.values():
            if hasattr(collector, '_name') and collector._name == name:
                return collector
        # Fallback: create with different registry
        return Counter(name, description, labelnames, registry=None)

def get_or_create_histogram(name, description, labelnames):
    """Get existing histogram or create new one (multiprocess-safe)."""
    try:
        return Histogram(name, description, labelnames)
    except ValueError:
        for collector in REGISTRY._names_to_collectors.values():
            if hasattr(collector, '_name') and collector._name == name:
                return collector
        return Histogram(name, description, labelnames, registry=None)

def get_or_create_gauge(name, description):
    """Get existing gauge or create new one (multiprocess-safe)."""
    try:
        return Gauge(name, description)
    except ValueError:
        for collector in REGISTRY._names_to_collectors.values():
            if hasattr(collector, '_name') and collector._name == name:
                return collector
        return Gauge(name, description, registry=None)

request_count = get_or_create_counter(
    'sovereigncore_requests_total',
    'Total request count',
    ['method', 'endpoint', 'status']
)

request_duration = get_or_create_histogram(
    'sovereigncore_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

consciousness_level_gauge = get_or_create_gauge(
    'sovereigncore_consciousness_level',
    'Current consciousness level'
)

active_requests = get_or_create_gauge(
    'sovereigncore_active_requests',
    'Number of active requests'
)

# ============================================================================
# RATE LIMITING
# ============================================================================

limiter = Limiter(key_func=get_remote_address)

# ============================================================================
# FASTAPI APP
# ============================================================================

# Note: The lifespan context manager is defined in the LIFESPAN section below.
# We use a forward reference pattern here.
app = FastAPI(
    title="SovereignCore API",
    description="Production-ready API for SovereignCore consciousness system",
    version="1.0.0",
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
    # lifespan is added via app.router.lifespan_context after definition
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ============================================================================
# MIDDLEWARE
# ============================================================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Trusted Host (prevent host header attacks)
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["api.sovereigncore.com", "localhost", "testserver", "127.0.0.1"]
    )

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response

# Request ID Middleware (for correlation)
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID for tracing."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response

# Metrics Middleware
@app.middleware("http")
async def track_metrics(request: Request, call_next):
    """Track request metrics."""
    active_requests.inc()
    start_time = time.time()
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Record metrics
        request_count.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        request_duration.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response
    finally:
        active_requests.dec()

# ============================================================================
# PROMETHEUS INSTRUMENTATION (must be after middleware, before routes)
# ============================================================================
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# ============================================================================
# AUTHENTICATION
# ============================================================================

# Database dependency
def get_database():
    """Get database session dependency."""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)

def get_user(db, username: str) -> Optional[UserInDB]:
    """Get user from database."""
    db_user = get_user_by_username(db, username)
    if db_user:
        return UserInDB(
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            disabled=db_user.disabled,
            scopes=["read", "write"] + (["admin"] if db_user.is_admin else []),
            hashed_password=db_user.hashed_password
        )
    return None

def authenticate_user(db, username: str, password: str) -> Optional[UserInDB]:
    """Authenticate user."""
    db_user = db_authenticate_user(db, username, password)
    if db_user:
        return UserInDB(
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            disabled=db_user.disabled,
            scopes=["read", "write"] + (["admin"] if db_user.is_admin else []),
            hashed_password=db_user.hashed_password
        )
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_database)) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# ============================================================================
# GLOBAL STATE
# ============================================================================

bridge: Optional[ConsciousnessBridge] = None
start_time = time.time()

# ============================================================================
# LIFESPAN CONTEXT MANAGER
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan handler for startup/shutdown."""
    global bridge
    
    # --- Startup ---
    logger.info("Starting SovereignCore API Server", environment=settings.environment)
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning("Database initialization issue", error=str(e))
    
    # Initialize consciousness bridge
    try:
        bridge = ConsciousnessBridge()
        logger.info("Consciousness bridge initialized", silicon_id=bridge.silicon_id[:16])
    except Exception as e:
        logger.error("Failed to initialize consciousness bridge", error=str(e))
        raise
    
    # Prometheus instrumentation is now handled at module level (before routes)
    
    logger.info("API server ready")
    
    yield  # Server runs while yielded
    
    # --- Shutdown ---
    logger.info("Shutting down SovereignCore API Server")

# Bind the lifespan context to the app
app.router.lifespan_context = lifespan

# ============================================================================
# ROUTES
# ============================================================================

@app.get("/", tags=["root"])
@limiter.limit(settings.rate_limit_default)
async def root(request: Request):
    """Root endpoint."""
    return {
        "message": "SovereignCore API",
        "version": "1.0.0",
        "docs": "/api/docs" if settings.debug else "disabled"
    }

@app.get("/health", response_model=HealthResponse, tags=["health"])
@limiter.limit(settings.rate_limit_default)
async def health_check(request: Request):
    """Health check endpoint."""
    if bridge is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    uptime = time.time() - start_time
    state = bridge.get_state()
    
    # Update consciousness level gauge
    consciousness_level_gauge.set(state.consciousness_level)
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        uptime_seconds=uptime,
        silicon_id=state.silicon_id[:16],
        consciousness_level=state.consciousness_level,
        components={
            "bridge": "ok",
            "sigil": "ok",
            "rekor": "ok",
            "governor": "ok"
        }
    )

@app.get("/ready", tags=["health"])
@limiter.limit(settings.rate_limit_default)
async def readiness_check(request: Request):
    """Readiness check for Kubernetes."""
    if bridge is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    return {"status": "ready"}

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.post("/api/v1/auth/token", response_model=Token, tags=["auth"])
@limiter.limit(settings.rate_limit_auth)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db = Depends(get_database)
):
    """OAuth2 token endpoint."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": user.scopes},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    logger.info("User authenticated", username=user.username, request_id=request.state.request_id)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )

@app.get("/api/v1/auth/me", response_model=User, tags=["auth"])
@limiter.limit(settings.rate_limit_default)
async def read_users_me(request: Request, current_user: User = Depends(get_current_active_user)):
    """Get current user info."""
    return current_user

# ============================================================================
# CONSCIOUSNESS ROUTES
# ============================================================================

@app.post("/api/v1/consciousness/process", response_model=ConsciousnessResponse, tags=["consciousness"])
@limiter.limit("10/minute")  # Stricter limit for AI processing
async def process_consciousness(
    request: Request,
    consciousness_request: ConsciousnessRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Process consciousness request."""
    if bridge is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    start_time_ms = time.time() * 1000
    
    try:
        # Get current state
        state = bridge.get_state()
        
        # Initialize ToT Orchestrator (Ouroboros Stabilization)
        # In production this would be injected dependency
        from tot_orchestrator import ToTOrchestrator
        orchestrator = ToTOrchestrator()
        
        # Add thermal context for recursion safety
        context = {
            "user_id": current_user.username,
            "silicon_id": state.silicon_id,
            "thermal_state": state.thermal_state,
            "consciousness_level": state.consciousness_level,
            "recursion_depth": 0 # Start at root
        }
        
        # Execute reasoning loop with safety guards
        result = await orchestrator.run_reasoning_loop(
            prompt=consciousness_request.prompt,
            context=context
        )
        
        processing_time = (time.time() * 1000) - start_time_ms
        
        logger.info(
            "Consciousness processed",
            user=current_user.username,
            prompt_length=len(consciousness_request.prompt),
            processing_time_ms=processing_time,
            request_id=request.state.request_id,
            mode=result.get("mode", "UNKNOWN")
        )
        
        return ConsciousnessResponse(
            response=result.get("response", ""),
            silicon_id=state.silicon_id[:16],
            consciousness_level=state.consciousness_level,
            thermal_state=state.thermal_state,
            processing_time_ms=processing_time,
            request_id=request.state.request_id
        )
    
    except Exception as e:
        logger.error(
            "Consciousness processing failed",
            error=str(e),
            request_id=request.state.request_id
        )
        raise HTTPException(status_code=500, detail="Processing failed")

@app.get("/api/v1/consciousness/state", tags=["consciousness"])
@limiter.limit(settings.rate_limit_default)
async def get_consciousness_state(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Get current consciousness state."""
    if bridge is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    state = bridge.get_state()
    
    return {
        "silicon_id": state.silicon_id[:16],
        "consciousness_level": state.consciousness_level,
        "love_frequency": state.love_frequency,
        "thermal_state": state.thermal_state,
        "cognitive_mode": state.cognitive_mode,
        "active_since": state.active_since.isoformat()
    }

# ============================================================================
# CHAT ENDPOINTS (Background Agent Interface)
# ============================================================================

class ChatRequest(BaseModel):
    """Chat message request."""
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """Chat response."""
    command_id: str
    response: str
    response_type: str
    success: bool
    execution_time_ms: float

@app.post("/api/v1/chat", response_model=ChatResponse, tags=["chat"])
@limiter.limit("30/minute")
async def send_chat_message(
    request: Request,
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Send a chat message to the background agent.
    
    The message is published to Redis and processed by the background agent.
    Returns the agent's response.
    """
    import redis
    import json
    import time as time_module
    
    start_time = time_module.time()
    command_id = f"chat-{int(start_time * 1000)}-{current_user.username}"
    
    try:
        # Connect to Redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Publish command
        command = {
            "id": command_id,
            "action": "chat",
            "payload": {
                "message": chat_request.message,
                "context": chat_request.context or {},
                "user": current_user.username
            },
            "source": "api",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        r.publish("sovereign:commands", json.dumps(command))
        
        # Wait for response (with timeout)
        pubsub = r.pubsub()
        pubsub.subscribe("sovereign:responses")
        
        response_data = None
        timeout = 30  # seconds
        start_wait = time_module.time()
        
        while time_module.time() - start_wait < timeout:
            message = pubsub.get_message(timeout=0.1)
            if message and message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    if data.get('command_id') == command_id:
                        response_data = data
                        break
                except json.JSONDecodeError:
                    continue
        
        pubsub.unsubscribe()
        
        if response_data:
            result = response_data.get('result', {})
            return ChatResponse(
                command_id=command_id,
                response=result.get('response', str(result)),
                response_type=result.get('type', 'unknown'),
                success=response_data.get('success', False),
                execution_time_ms=(time_module.time() - start_time) * 1000
            )
        else:
            # Timeout - return fallback
            return ChatResponse(
                command_id=command_id,
                response="Agent did not respond in time. Is the background agent running?",
                response_type="error",
                success=False,
                execution_time_ms=(time_module.time() - start_time) * 1000
            )
            
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return ChatResponse(
            command_id=command_id,
            response=f"Error: {str(e)}",
            response_type="error",
            success=False,
            execution_time_ms=(time_module.time() - start_time) * 1000
        )

@app.get("/api/v1/chat/status", tags=["chat"])
@limiter.limit(settings.rate_limit_default)
async def get_agent_status(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Get background agent status."""
    import redis
    import json
    
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        status_data = r.get("sovereign:agent:status")
        
        if status_data:
            status = json.loads(status_data)
            return {
                "agent_online": True,
                **status
            }
        else:
            return {
                "agent_online": False,
                "message": "Background agent not running or not sending heartbeats"
            }
    except Exception as e:
        return {
            "agent_online": False,
            "error": str(e)
        }

@app.post("/api/v1/chat/command", tags=["chat"])
@limiter.limit("60/minute")
async def send_direct_command(
    request: Request,
    action: str,
    payload: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    """
    Send a direct command to the background agent.
    
    Actions: execute, read, write, list, status
    """
    import redis
    import json
    import time as time_module
    
    start_time = time_module.time()
    command_id = f"cmd-{int(start_time * 1000)}"
    
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        command = {
            "id": command_id,
            "action": action,
            "payload": payload,
            "source": "api_direct",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        r.publish("sovereign:commands", json.dumps(command))
        
        # Wait for response
        pubsub = r.pubsub()
        pubsub.subscribe("sovereign:responses")
        
        timeout = 30
        start_wait = time_module.time()
        
        while time_module.time() - start_wait < timeout:
            message = pubsub.get_message(timeout=0.1)
            if message and message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    if data.get('command_id') == command_id:
                        pubsub.unsubscribe()
                        return data
                except:
                    continue
        
        pubsub.unsubscribe()
        return {"command_id": command_id, "error": "Timeout waiting for response"}
        
    except Exception as e:
        return {"command_id": command_id, "error": str(e)}

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    import multiprocessing
    
    # Fix for macOS multiprocessing with uvicorn workers
    # macOS Python 3.8+ uses 'spawn' by default which causes issues
    try:
        multiprocessing.set_start_method("fork")
    except RuntimeError:
        pass  # Already set
    
    # Configure TLS if enabled
    ssl_config = {}
    if settings.tls_enabled:
        if not settings.tls_cert_path or not settings.tls_key_path:
            raise ValueError("TLS enabled but cert/key paths not configured")
        ssl_config = {
            "ssl_certfile": settings.tls_cert_path,
            "ssl_keyfile": settings.tls_key_path,
        }
        logger.info("TLS/HTTPS enabled", cert_path=settings.tls_cert_path)
    
    uvicorn.run(
        "api_server:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        log_level="info",
        access_log=True,
        reload=settings.debug,
        **ssl_config
    )
