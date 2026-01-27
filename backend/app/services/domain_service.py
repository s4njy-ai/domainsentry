"""
Domain service for business logic operations.
"""
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.domain import Domain
from app.schemas.domain import (
    DomainCreate,
    DomainResponse,
    DomainUpdate,
    DomainListResponse,
    DomainSearchRequest,
)


class DomainService:
    """
    Service for domain-related operations.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_domains(
        self,
        page: int = 1,
        size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        risk_level: Optional[str] = None,
        min_risk_score: Optional[float] = None,
        max_risk_score: Optional[float] = None,
    ) -> DomainListResponse:
        """
        List domains with pagination and filtering.
        """
        # Build query
        query = select(Domain)
        
        # Apply filters
        if risk_level:
            query = query.where(Domain.risk_level == risk_level)
        
        if min_risk_score is not None:
            query = query.where(Domain.risk_score >= min_risk_score)
        
        if max_risk_score is not None:
            query = query.where(Domain.risk_score <= max_risk_score)
        
        # Apply sorting
        sort_column = getattr(Domain, sort_by, Domain.created_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Count total
        count_query = select(func.count()).select_from(Domain)
        if risk_level:
            count_query = count_query.where(Domain.risk_level == risk_level)
        if min_risk_score is not None:
            count_query = count_query.where(Domain.risk_score >= min_risk_score)
        if max_risk_score is not None:
            count_query = count_query.where(Domain.risk_score <= max_risk_score)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)
        
        # Execute query
        result = await self.db.execute(query)
        domains = result.scalars().all()
        
        # Calculate pages
        pages = (total + size - 1) // size if size > 0 else 0
        
        return DomainListResponse(
            items=domains,
            total=total,
            page=page,
            size=size,
            pages=pages,
        )
    
    async def search_domains(self, search_request: DomainSearchRequest) -> DomainListResponse:
        """
        Search domains with advanced filters.
        """
        # Build query
        query = select(Domain)
        
        # Apply text search
        if search_request.query:
            search_term = f"%{search_request.query}%"
            query = query.where(
                or_(
                    Domain.domain_name.ilike(search_term),
                    Domain.registrar.ilike(search_term),
                    Domain.registrant_name.ilike(search_term),
                    Domain.registrant_organization.ilike(search_term),
                    Domain.registrant_email.ilike(search_term),
                    Domain.certificate_issuer.ilike(search_term),
                    Domain.certificate_subject.ilike(search_term),
                )
            )
        
        # Apply filters
        if search_request.risk_level:
            query = query.where(Domain.risk_level == search_request.risk_level)
        
        if search_request.min_risk_score is not None:
            query = query.where(Domain.risk_score >= search_request.min_risk_score)
        
        if search_request.max_risk_score is not None:
            query = query.where(Domain.risk_score <= search_request.max_risk_score)
        
        if search_request.registrar:
            query = query.where(Domain.registrar.ilike(f"%{search_request.registrar}%"))
        
        if search_request.country:
            query = query.where(Domain.registrant_country == search_request.country)
        
        if search_request.date_from:
            query = query.where(Domain.registered_date >= search_request.date_from)
        
        if search_request.date_to:
            query = query.where(Domain.registered_date <= search_request.date_to)
        
        # Apply sorting
        sort_column = getattr(Domain, search_request.sort_by, Domain.created_at)
        if search_request.sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Count total
        count_query = select(func.count()).select_from(Domain)
        
        # Apply same filters to count
        if search_request.query:
            search_term = f"%{search_request.query}%"
            count_query = count_query.where(
                or_(
                    Domain.domain_name.ilike(search_term),
                    Domain.registrar.ilike(search_term),
                    Domain.registrant_name.ilike(search_term),
                    Domain.registrant_organization.ilike(search_term),
                    Domain.registrant_email.ilike(search_term),
                    Domain.certificate_issuer.ilike(search_term),
                    Domain.certificate_subject.ilike(search_term),
                )
            )
        
        if search_request.risk_level:
            count_query = count_query.where(Domain.risk_level == search_request.risk_level)
        
        if search_request.min_risk_score is not None:
            count_query = count_query.where(Domain.risk_score >= search_request.min_risk_score)
        
        if search_request.max_risk_score is not None:
            count_query = count_query.where(Domain.risk_score <= search_request.max_risk_score)
        
        if search_request.registrar:
            count_query = count_query.where(Domain.registrar.ilike(f"%{search_request.registrar}%"))
        
        if search_request.country:
            count_query = count_query.where(Domain.registrant_country == search_request.country)
        
        if search_request.date_from:
            count_query = count_query.where(Domain.registered_date >= search_request.date_from)
        
        if search_request.date_to:
            count_query = count_query.where(Domain.registered_date <= search_request.date_to)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        offset = (search_request.page - 1) * search_request.size
        query = query.offset(offset).limit(search_request.size)
        
        # Execute query
        result = await self.db.execute(query)
        domains = result.scalars().all()
        
        # Calculate pages
        pages = (total + search_request.size - 1) // search_request.size if search_request.size > 0 else 0
        
        return DomainListResponse(
            items=domains,
            total=total,
            page=search_request.page,
            size=search_request.size,
            pages=pages,
        )
    
    async def get_domain(self, domain_id: uuid.UUID) -> Optional[DomainResponse]:
        """
        Get a domain by ID.
        """
        query = select(Domain).where(Domain.id == domain_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_domain_by_name(self, domain_name: str) -> Optional[DomainResponse]:
        """
        Get a domain by name.
        """
        query = select(Domain).where(Domain.domain_name == domain_name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_domain(self, domain_data: DomainCreate) -> DomainResponse:
        """
        Create a new domain.
        """
        # Check if domain already exists
        existing = await self.get_domain_by_name(domain_data.domain_name)
        if existing:
            raise ValueError(f"Domain {domain_data.domain_name} already exists")
        
        # Create domain
        domain = Domain(**domain_data.dict())
        self.db.add(domain)
        await self.db.commit()
        await self.db.refresh(domain)
        
        return domain
    
    async def update_domain(
        self,
        domain_id: uuid.UUID,
        domain_data: DomainUpdate,
    ) -> Optional[DomainResponse]:
        """
        Update a domain.
        """
        # Get domain
        domain = await self.get_domain(domain_id)
        if not domain:
            return None
        
        # Update fields
        update_data = domain_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(domain, field, value)
        
        domain.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(domain)
        
        return domain
    
    async def delete_domain(self, domain_id: uuid.UUID) -> bool:
        """
        Delete a domain.
        """
        # Get domain
        domain = await self.get_domain(domain_id)
        if not domain:
            return False
        
        # Delete domain
        await self.db.delete(domain)
        await self.db.commit()
        
        return True
    
    async def get_domain_stats(self) -> Dict:
        """
        Get domain statistics summary.
        """
        # Total domains
        total_query = select(func.count(Domain.id))
        total_result = await self.db.execute(total_query)
        total = total_result.scalar()
        
        # Active domains
        active_query = select(func.count(Domain.id)).where(Domain.is_active == True)
        active_result = await self.db.execute(active_query)
        active = active_result.scalar()
        
        # Risk level distribution
        risk_query = select(
            Domain.risk_level,
            func.count(Domain.id).label("count"),
        ).group_by(Domain.risk_level)
        risk_result = await self.db.execute(risk_query)
        risk_distribution = {row.risk_level: row.count for row in risk_result}
        
        # Average risk score
        avg_risk_query = select(func.avg(Domain.risk_score))
        avg_risk_result = await self.db.execute(avg_risk_query)
        avg_risk_score = avg_risk_result.scalar() or 0.0
        
        # Domains added today
        today = datetime.utcnow().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        
        today_query = select(func.count(Domain.id)).where(
            and_(
                Domain.created_at >= start_of_day,
                Domain.created_at <= end_of_day,
            )
        )
        today_result = await self.db.execute(today_query)
        today_count = today_result.scalar()
        
        return {
            "total_domains": total,
            "active_domains": active,
            "risk_distribution": risk_distribution,
            "average_risk_score": round(avg_risk_score, 2),
            "domains_added_today": today_count,
            "updated_at": datetime.utcnow().isoformat(),
        }
    
    async def get_risk_distribution(self) -> Dict:
        """
        Get risk score distribution across domains.
        """
        # Create risk buckets
        buckets = [
            (0, 20, "0-20"),
            (20, 40, "20-40"),
            (40, 60, "40-60"),
            (60, 80, "60-80"),
            (80, 101, "80-100"),  # 101 to include 100
        ]
        
        distribution = {}
        for min_score, max_score, label in buckets:
            query = select(func.count(Domain.id)).where(
                and_(
                    Domain.risk_score >= min_score,
                    Domain.risk_score < max_score,
                )
            )
            result = await self.db.execute(query)
            count = result.scalar()
            distribution[label] = count
        
        return distribution
    
    async def get_tld_distribution(self, limit: int = 20) -> List[Dict]:
        """
        Get TLD (Top-Level Domain) distribution.
        """
        # Extract TLD from domain name
        # Simple approach: get everything after last dot
        tld_expr = func.substring(
            Domain.domain_name,
            func.strpos(Domain.domain_name, '.') + 1,
        )
        
        query = select(
            tld_expr.label("tld"),
            func.count(Domain.id).label("count"),
        ).group_by("tld").order_by(func.count(Domain.id).desc()).limit(limit)
        
        result = await self.db.execute(query)
        distribution = [{"tld": row.tld, "count": row.count} for row in result]
        
        return distribution
    
    async def get_daily_timeline(self, days: int = 30) -> List[Dict]:
        """
        Get daily domain registration timeline.
        """
        # Calculate date range
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days - 1)
        
        # Generate all dates in range
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date)
            current_date += timedelta(days=1)
        
        # Query for registrations by date
        timeline = []
        for date in date_range:
            start_of_day = datetime.combine(date, datetime.min.time())
            end_of_day = datetime.combine(date, datetime.max.time())
            
            query = select(func.count(Domain.id)).where(
                and_(
                    Domain.registered_date >= start_of_day,
                    Domain.registered_date <= end_of_day,
                )
            )
            result = await self.db.execute(query)
            count = result.scalar() or 0
            
            timeline.append({
                "date": date.isoformat(),
                "count": count,
            })
        
        return timeline