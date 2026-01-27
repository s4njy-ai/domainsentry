"""
Main API router for DomainSentry v1 endpoints.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import domains, enrichments, scans, risk, feeds, health

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(domains.router, prefix="/domains", tags=["domains"])
api_router.include_router(enrichments.router, prefix="/enrichments", tags=["enrichments"])
api_router.include_router(scans.router, prefix="/scans", tags=["scans"])
api_router.include_router(risk.router, prefix="/risk", tags=["risk"])
api_router.include_router(feeds.router, prefix="/feeds", tags=["feeds"])