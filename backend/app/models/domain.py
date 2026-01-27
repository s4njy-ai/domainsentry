"""
Domain models for DomainSentry.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Domain(Base):
    """
    Domain model representing a monitored domain.
    """
    __tablename__ = "domains"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_name = Column(String(255), nullable=False, index=True, unique=True)
    registered_date = Column(DateTime, nullable=True)
    expires_date = Column(DateTime, nullable=True)
    updated_date = Column(DateTime, nullable=True)
    
    # WHOIS information
    registrar = Column(String(255), nullable=True)
    registrant_name = Column(String(255), nullable=True)
    registrant_organization = Column(String(255), nullable=True)
    registrant_country = Column(String(2), nullable=True)
    registrant_email = Column(String(255), nullable=True)
    name_servers = Column(JSON, nullable=True)
    
    # Risk scoring
    risk_score = Column(Float, default=0.0, index=True)
    risk_level = Column(String(50), default="low")  # low, medium, high, critical
    risk_factors = Column(JSON, nullable=True)  # List of risk factors and weights
    
    # Threat intelligence
    virustotal_reputation = Column(Integer, nullable=True)
    abuseipdb_reputation = Column(Integer, nullable=True)
    threat_indicators = Column(JSON, nullable=True)
    
    # Certificate information
    certificate_issuer = Column(String(255), nullable=True)
    certificate_subject = Column(String(255), nullable=True)
    certificate_valid_from = Column(DateTime, nullable=True)
    certificate_valid_to = Column(DateTime, nullable=True)
    certificate_serial = Column(String(255), nullable=True)
    
    # Metadata
    source = Column(String(100), default="crt.sh")  # crt.sh, manual, etc.
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    enrichments = relationship("DomainEnrichment", back_populates="domain", cascade="all, delete-orphan")
    scans = relationship("DomainScan", back_populates="domain", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Domain(id={self.id}, domain_name={self.domain_name}, risk_score={self.risk_score})>"


class DomainEnrichment(Base):
    """
    Domain enrichment data from external sources.
    """
    __tablename__ = "domain_enrichments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id"), nullable=False, index=True)
    
    # Enrichment source
    source = Column(String(100), nullable=False)  # whoisxmlapi, virustotal, abuseipdb, etc.
    source_data = Column(JSON, nullable=False)  # Raw data from source
    enrichment_type = Column(String(50), nullable=False)  # whois, threat, reputation, etc.
    
    # Metadata
    is_successful = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    http_status_code = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    domain = relationship("Domain", back_populates="enrichments")
    
    def __repr__(self) -> str:
        return f"<DomainEnrichment(id={self.id}, domain_id={self.domain_id}, source={self.source})>"


class DomainScan(Base):
    """
    Historical scans of domains for tracking changes.
    """
    __tablename__ = "domain_scans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id"), nullable=False, index=True)
    
    # Scan results
    scan_type = Column(String(50), nullable=False)  # full, quick, risk, etc.
    scan_data = Column(JSON, nullable=False)  # Complete scan results
    previous_scan_id = Column(UUID(as_uuid=True), ForeignKey("domain_scans.id"), nullable=True)
    
    # Risk scoring
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(50), nullable=False)
    risk_factors = Column(JSON, nullable=True)
    
    # Metadata
    scanner_version = Column(String(50), nullable=True)
    scan_duration_ms = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    domain = relationship("Domain", back_populates="scans")
    previous_scan = relationship("DomainScan", remote_side=[id])
    
    def __repr__(self) -> str:
        return f"<DomainScan(id={self.id}, domain_id={self.domain_id}, scan_type={self.scan_type})>"