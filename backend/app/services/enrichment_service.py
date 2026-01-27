"""
Domain enrichment service for business logic operations.
"""
import uuid
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import DomainEnrichment
from app.schemas.domain import DomainEnrichmentCreate, DomainEnrichmentResponse


class EnrichmentService:
    """
    Service for domain enrichment-related operations.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_enrichments(
        self,
        skip: int = 0,
        limit: int = 100,
        domain_id: Optional[uuid.UUID] = None,
        source: Optional[str] = None,
        enrichment_type: Optional[str] = None,
    ) -> List[DomainEnrichmentResponse]:
        """
        List domain enrichments with optional filtering.
        """
        query = select(DomainEnrichment)
        
        # Apply filters
        conditions = []
        if domain_id:
            conditions.append(DomainEnrichment.domain_id == domain_id)
        if source:
            conditions.append(DomainEnrichment.source == source)
        if enrichment_type:
            conditions.append(DomainEnrichment.enrichment_type == enrichment_type)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(DomainEnrichment.created_at.desc())
        
        result = await self.db.execute(query)
        enrichments = result.scalars().all()
        
        return enrichments
    
    async def get_enrichment(self, enrichment_id: uuid.UUID) -> Optional[DomainEnrichmentResponse]:
        """
        Get a domain enrichment by ID.
        """
        query = select(DomainEnrichment).where(DomainEnrichment.id == enrichment_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_enrichment(self, enrichment_data: DomainEnrichmentCreate) -> DomainEnrichmentResponse:
        """
        Create a new domain enrichment.
        """
        enrichment = DomainEnrichment(**enrichment_data.dict())
        self.db.add(enrichment)
        await self.db.commit()
        await self.db.refresh(enrichment)
        
        return enrichment
    
    async def get_enrichments_by_domain(
        self,
        domain_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        source: Optional[str] = None,
        enrichment_type: Optional[str] = None,
    ) -> List[DomainEnrichmentResponse]:
        """
        Get all enrichments for a specific domain.
        """
        query = select(DomainEnrichment).where(DomainEnrichment.domain_id == domain_id)
        
        # Apply additional filters
        conditions = []
        if source:
            conditions.append(DomainEnrichment.source == source)
        if enrichment_type:
            conditions.append(DomainEnrichment.enrichment_type == enrichment_type)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(DomainEnrichment.created_at.desc())
        
        result = await self.db.execute(query)
        enrichments = result.scalars().all()
        
        return enrichments