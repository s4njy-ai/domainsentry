"""
Health check endpoints for DomainSentry API.
"""
from datetime import datetime
from typing import Dict

from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from fastapi import Depends
from app.api.deps import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/")
async def health_check() -> Dict:
    """
    Basic health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "domainsentry-backend",
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT
    }


@router.get("/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)) -> Dict:
    """
    Detailed health check with database connectivity.
    """
    health_status = {
        "status": "healthy",
        "checks": {
            "database": "ok",
            "redis": "pending",  # We'll implement this later
            "external_apis": "pending"  # We'll implement this later
        },
        "timestamp": datetime.utcnow().isoformat(),
        "service": "domainsentry-backend",
        "version": settings.APP_VERSION
    }
    
    # Test database connectivity
    try:
        await db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> Dict:
    """
    Readiness check for container orchestration.
    """
    # Check if we can connect to database
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
    except Exception:
        return {"status": "not_ready", "timestamp": datetime.utcnow().isoformat()}, 503