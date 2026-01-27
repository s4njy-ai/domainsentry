"""
Domain scan service for business logic operations.
"""
import uuid
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import DomainScan
from app.schemas.domain import DomainScanCreate, DomainScanResponse


class ScanService:
    """
    Service for domain scan-related operations.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_scans(
        self,
        skip: int = 0,
        limit: int = 100,
        domain_id: Optional[uuid.UUID] = None,
        scan_type: Optional[str] = None,
        min_risk_score: Optional[float] = None,
        max_risk_score: Optional[float] = None,
    ) -> List[DomainScanResponse]:
        """
        List domain scans with optional filtering.
        """
        query = select(DomainScan)
        
        # Apply filters
        conditions = []
        if domain_id:
            conditions.append(DomainScan.domain_id == domain_id)
        if scan_type:
            conditions.append(DomainScan.scan_type == scan_type)
        if min_risk_score is not None:
            conditions.append(DomainScan.risk_score >= min_risk_score)
        if max_risk_score is not None:
            conditions.append(DomainScan.risk_score <= max_risk_score)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(DomainScan.created_at.desc())
        
        result = await self.db.execute(query)
        scans = result.scalars().all()
        
        return scans
    
    async def get_scan(self, scan_id: uuid.UUID) -> Optional[DomainScanResponse]:
        """
        Get a domain scan by ID.
        """
        query = select(DomainScan).where(DomainScan.id == scan_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_scan(self, scan_data: DomainScanCreate) -> DomainScanResponse:
        """
        Create a new domain scan.
        """
        scan = DomainScan(**scan_data.dict())
        self.db.add(scan)
        await self.db.commit()
        await self.db.refresh(scan)
        
        return scan
    
    async def get_scans_by_domain(
        self,
        domain_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        scan_type: Optional[str] = None,
        min_risk_score: Optional[float] = None,
        max_risk_score: Optional[float] = None,
    ) -> List[DomainScanResponse]:
        """
        Get all scans for a specific domain.
        """
        query = select(DomainScan).where(DomainScan.domain_id == domain_id)
        
        # Apply additional filters
        conditions = []
        if scan_type:
            conditions.append(DomainScan.scan_type == scan_type)
        if min_risk_score is not None:
            conditions.append(DomainScan.risk_score >= min_risk_score)
        if max_risk_score is not None:
            conditions.append(DomainScan.risk_score <= max_risk_score)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(DomainScan.created_at.desc())
        
        result = await self.db.execute(query)
        scans = result.scalars().all()
        
        return scans