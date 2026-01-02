from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uuid

from app.routers import auth, consciousness
from app.database import Base, engine
from app.config import settings

# Rate Limiter setup
limiter = Limiter(key_func=get_remote_address)

# Lifespan Context Manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Logic
    print(f"Starting {settings.PROJECT_NAME}...")
    try:
        if "sqlite" in settings.DATABASE_URL:
             Base.metadata.create_all(bind=engine) # Create tables
        yield
    finally:
        # Shutdown Logic
        print("Shutting down... Database connections closing.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

# Register SlowAPI state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Request ID Middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

app.include_router(auth.router)
app.include_router(consciousness.router)

@app.get("/")
@limiter.limit("5/minute")
async def root(request: Request): 
    return {"message": "SovereignCore Online", "status": "Secure"}
