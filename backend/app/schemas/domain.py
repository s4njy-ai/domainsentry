"""
Domain schemas for DomainSentry API.
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field, validator


# Base schemas
class DomainBase(BaseModel):
    """Base schema for domain data."""
    domain_name: str = Field(..., max_length=255, description="Domain name")
    registered_date: Optional[datetime] = None
    expires_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    registrar: Optional[str] = None
    registrant_name: Optional[str] = None
    registrant_organization: Optional[str] = None
    registrant_country: Optional[str] = None
    registrant_email: Optional[str] = None
    name_servers: Optional[List[str]] = None
    risk_score: float = Field(0.0, ge=0.0, le=100.0, description="Risk score (0-100)")
    risk_level: str = Field("low", description="Risk level: low, medium, high, critical")
    risk_factors: Optional[Dict[str, float]] = None
    virustotal_reputation: Optional[int] = None
    abuseipdb_reputation: Optional[int] = None
    threat_indicators: Optional[List[str]] = None
    certificate_issuer: Optional[str] = None
    certificate_subject: Optional[str] = None
    certificate_valid_from: Optional[datetime] = None
    certificate_valid_to: Optional[datetime] = None
    certificate_serial: Optional[str] = None
    source: str = Field("crt.sh", description="Source of domain data")
    is_active: bool = True
    notes: Optional[str] = None


class DomainCreate(DomainBase):
    """Schema for creating a new domain."""
    pass


class DomainUpdate(BaseModel):
    """Schema for updating a domain."""
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    risk_factors: Optional[Dict[str, float]] = None
    threat_indicators: Optional[List[str]] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class DomainInDB(DomainBase):
    """Schema for domain data stored in database."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DomainResponse(DomainInDB):
    """Schema for domain API response."""
    pass


# Enrichment schemas
class DomainEnrichmentBase(BaseModel):
    """Base schema for domain enrichment."""
    source: str = Field(..., max_length=100, description="Enrichment source")
    source_data: Dict[str, Any] = Field(..., description="Raw data from source")
    enrichment_type: str = Field(..., max_length=50, description="Type of enrichment")
    is_successful: bool = True
    error_message: Optional[str] = None
    http_status_code: Optional[int] = None


class DomainEnrichmentCreate(DomainEnrichmentBase):
    """Schema for creating domain enrichment."""
    domain_id: uuid.UUID


class DomainEnrichmentInDB(DomainEnrichmentBase):
    """Schema for domain enrichment in database."""
    id: uuid.UUID
    domain_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DomainEnrichmentResponse(DomainEnrichmentInDB):
    """Schema for domain enrichment API response."""
    pass


# Scan schemas
class DomainScanBase(BaseModel):
    """Base schema for domain scan."""
    scan_type: str = Field(..., max_length=50, description="Type of scan")
    scan_data: Dict[str, Any] = Field(..., description="Complete scan results")
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Risk score (0-100)")
    risk_level: str = Field(..., description="Risk level")
    risk_factors: Optional[Dict[str, float]] = None
    scanner_version: Optional[str] = None
    scan_duration_ms: Optional[int] = None


class DomainScanCreate(DomainScanBase):
    """Schema for creating domain scan."""
    domain_id: uuid.UUID
    previous_scan_id: Optional[uuid.UUID] = None


class DomainScanInDB(DomainScanBase):
    """Schema for domain scan in database."""
    id: uuid.UUID
    domain_id: uuid.UUID
    previous_scan_id: Optional[uuid.UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class DomainScanResponse(DomainScanInDB):
    """Schema for domain scan API response."""
    pass


# List and search schemas
class DomainListResponse(BaseModel):
    """Schema for paginated domain list response."""
    items: List[DomainResponse]
    total: int
    page: int
    size: int
    pages: int


class DomainSearchRequest(BaseModel):
    """Schema for domain search request."""
    query: Optional[str] = None
    risk_level: Optional[str] = None
    min_risk_score: Optional[float] = None
    max_risk_score: Optional[float] = None
    registrar: Optional[str] = None
    country: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = 1
    size: int = 20
    sort_by: str = "created_at"
    sort_order: str = "desc"
    
    @validator('size')
    def validate_size(cls, v):
        if v < 1 or v > 100:
            raise ValueError('size must be between 1 and 100')
        return v
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('sort_order must be asc or desc')
        return v


# Risk analysis schemas
class RiskAnalysisRequest(BaseModel):
    """Schema for risk analysis request."""
    domain_name: str
    force_rescan: bool = False


class RiskAnalysisResponse(BaseModel):
    """Schema for risk analysis response."""
    domain_id: uuid.UUID
    domain_name: str
    risk_score: float
    risk_level: str
    risk_factors: Dict[str, float]
    threat_indicators: List[str]
    recommendations: List[str]
    analysis_time_ms: int
    scan_id: Optional[uuid.UUID] = None