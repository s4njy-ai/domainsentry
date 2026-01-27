"""
DomainSentry Backend - FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_client import make_asgi_app

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import engine
from app.metrics.middleware import PrometheusMiddleware

# Configure logging
configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting up DomainSentry backend...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Create database tables if they don't exist
    # Note: In production, use Alembic migrations instead
    if settings.CREATE_DB_TABLES:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    logger.info("Shutting down DomainSentry backend...")
    await engine.dispose()


# Create FastAPI app with lifespan
app = FastAPI(
    title="DomainSentry API",
    description="DomainSentry: OSINT platform for newly registered domains",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# Add Prometheus middleware for metrics
app.add_middleware(PrometheusMiddleware)

# Add prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root() -> dict:
    """
    Root endpoint returning API information.
    """
    return {
        "message": "Welcome to DomainSentry API",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else None,
        "health": "/health",
    }


@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint for monitoring.
    """
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}


@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    """
    Middleware to log all incoming requests.
    """
    logger.info(
        f"Request: {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_host": request.client.host if request.client else None,
        },
    )
    
    response = await call_next(request)
    
    logger.info(
        f"Response: {request.method} {request.url.path} -> {response.status_code}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
        },
    )
    
    return response