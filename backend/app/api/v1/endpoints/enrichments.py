"""
Domain enrichment endpoints for DomainSentry API.
"""
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.domain import DomainEnrichment
from app.schemas.domain import DomainEnrichmentCreate, DomainEnrichmentResponse
from app.services.enrichment_service import EnrichmentService

router = APIRouter()


@router.get("/", response_model=List[DomainEnrichmentResponse])
async def list_enrichments(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    domain_id: uuid.UUID = None,
    source: str = None,
    enrichment_type: str = None,
):
    """
    List domain enrichments with optional filtering.
    """
    service = EnrichmentService(db)
    return await service.list_enrichments(
        skip=skip,
        limit=limit,
        domain_id=domain_id,
        source=source,
        enrichment_type=enrich_type,
    )


@router.get("/{enrichment_id}", response_model=DomainEnrichmentResponse)
async def get_enrichment(
    enrichment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific domain enrichment by ID.
    """
    service = EnrichmentService(db)
    enrichment = await service.get_enrichment(enrichment_id)
    
    if not enrichment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain enrichment not found",
        )
    
    return enrichment


@router.post("/", response_model=DomainEnrichmentResponse)
async def create_enrichment(
    enrichment_data: DomainEnrichmentCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new domain enrichment.
    """
    service = EnrichmentService(db)
    return await service.create_enrichment(enrichment_data)


@router.get("/by-domain/{domain_id}", response_model=List[DomainEnrichmentResponse])
async def get_enrichments_by_domain(
    domain_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    source: str = None,
    enrichment_type: str = None,
):
    """
    Get all enrichments for a specific domain.
    """
    service = EnrichmentService(db)
    return await service.get_enrichments_by_domain(
        domain_id=domain_id,
        skip=skip,
        limit=limit,
        source=source,
        enrichment_type=enrichment_type,
    )