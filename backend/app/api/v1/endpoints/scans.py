"""
Domain scan endpoints for DomainSentry API.
"""
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.domain import DomainScan
from app.schemas.domain import DomainScanCreate, DomainScanResponse
from app.services.scan_service import ScanService

router = APIRouter()


@router.get("/", response_model=List[DomainScanResponse])
async def list_scans(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    domain_id: uuid.UUID = None,
    scan_type: str = None,
    min_risk_score: float = None,
    max_risk_score: float = None,
):
    """
    List domain scans with optional filtering.
    """
    service = ScanService(db)
    return await service.list_scans(
        skip=skip,
        limit=limit,
        domain_id=domain_id,
        scan_type=scan_type,
        min_risk_score=min_risk_score,
        max_risk_score=max_risk_score,
    )


@router.get("/{scan_id}", response_model=DomainScanResponse)
async def get_scan(
    scan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific domain scan by ID.
    """
    service = ScanService(db)
    scan = await service.get_scan(scan_id)
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain scan not found",
        )
    
    return scan


@router.post("/", response_model=DomainScanResponse)
async def create_scan(
    scan_data: DomainScanCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new domain scan.
    """
    service = ScanService(db)
    return await service.create_scan(scan_data)


@router.get("/by-domain/{domain_id}", response_model=List[DomainScanResponse])
async def get_scans_by_domain(
    domain_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    scan_type: str = None,
    min_risk_score: float = None,
    max_risk_score: float = None,
):
    """
    Get all scans for a specific domain.
    """
    service = ScanService(db)
    return await service.get_scans_by_domain(
        domain_id=domain_id,
        skip=skip,
        limit=limit,
        scan_type=scan_type,
        min_risk_score=min_risk_score,
        max_risk_score=max_risk_score,
    )