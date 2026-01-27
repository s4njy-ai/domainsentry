"""
Domain endpoints for DomainSentry API.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_user, get_db
from app.models.domain import Domain
from app.schemas.domain import (
    DomainCreate,
    DomainResponse,
    DomainUpdate,
    DomainListResponse,
    DomainSearchRequest,
)
from app.services.domain_service import DomainService

router = APIRouter()


@router.get("/", response_model=DomainListResponse)
async def list_domains(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    risk_level: Optional[str] = None,
    min_risk_score: Optional[float] = None,
    max_risk_score: Optional[float] = None,
):
    """
    List domains with pagination and filtering.
    """
    service = DomainService(db)
    return await service.list_domains(
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order,
        risk_level=risk_level,
        min_risk_score=min_risk_score,
        max_risk_score=max_risk_score,
    )


@router.post("/search", response_model=DomainListResponse)
async def search_domains(
    search_request: DomainSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Search domains with advanced filters.
    """
    service = DomainService(db)
    return await service.search_domains(search_request)


@router.get("/{domain_id}", response_model=DomainResponse)
async def get_domain(
    domain_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific domain by ID.
    """
    service = DomainService(db)
    domain = await service.get_domain(domain_id)
    
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found",
        )
    
    return domain


@router.post("/", response_model=DomainResponse)
async def create_domain(
    domain_data: DomainCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new domain.
    """
    service = DomainService(db)
    return await service.create_domain(domain_data)


@router.put("/{domain_id}", response_model=DomainResponse)
async def update_domain(
    domain_id: uuid.UUID,
    domain_data: DomainUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a domain.
    """
    service = DomainService(db)
    domain = await service.update_domain(domain_id, domain_data)
    
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found",
        )
    
    return domain


@router.delete("/{domain_id}")
async def delete_domain(
    domain_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a domain.
    """
    service = DomainService(db)
    deleted = await service.delete_domain(domain_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found",
        )
    
    return {"message": "Domain deleted successfully"}


@router.get("/by-name/{domain_name}", response_model=DomainResponse)
async def get_domain_by_name(
    domain_name: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a domain by its name.
    """
    service = DomainService(db)
    domain = await service.get_domain_by_name(domain_name)
    
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found",
        )
    
    return domain


@router.get("/stats/summary")
async def get_domain_stats(
    db: AsyncSession = Depends(get_db),
):
    """
    Get domain statistics summary.
    """
    service = DomainService(db)
    return await service.get_domain_stats()


@router.get("/risk/distribution")
async def get_risk_distribution(
    db: AsyncSession = Depends(get_db),
):
    """
    Get risk score distribution across domains.
    """
    service = DomainService(db)
    return await service.get_risk_distribution()


@router.get("/tld/distribution")
async def get_tld_distribution(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Get TLD (Top-Level Domain) distribution.
    """
    service = DomainService(db)
    return await service.get_tld_distribution(limit)


@router.get("/timeline/daily")
async def get_daily_timeline(
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365),
):
    """
    Get daily domain registration timeline.
    """
    service = DomainService(db)
    return await service.get_daily_timeline(days)