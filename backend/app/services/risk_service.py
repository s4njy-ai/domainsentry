"""
Risk analysis service for DomainSentry.
"""
import asyncio
import hashlib
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from scipy.stats import entropy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.domain import Domain, DomainScan
from app.schemas.domain import RiskAnalysisRequest, RiskAnalysisResponse


class RiskService:
    """
    Service for domain risk analysis operations.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.config = self._load_risk_config()
    
    def _load_risk_config(self) -> Dict:
        """
        Load risk configuration from YAML file or defaults.
        """
        # Default risk weights configuration
        return {
            "weights": {
                "domain_length": 0.15,
                "entropy_score": 0.25,
                "tld_risk": 0.20,
                "keyword_matches": 0.30,
                "age_days": 0.10
            },
            "high_risk_keywords": [
                "paypal", "bank", "login", "secure", "account", 
                "verify", "confirm", "update", "password", "signin"
            ],
            "suspicious_tlds": [".tk", ".ml", ".ga", ".cf", ".xyz"],
            "max_domain_length": 30,
            "min_entropy_threshold": 3.0
        }
    
    async def analyze_domain_risk(self, request: RiskAnalysisRequest) -> RiskAnalysisResponse:
        """
        Analyze risk for a domain with detailed breakdown.
        """
        start_time = time.time()
        
        # Get or create domain
        domain = await self._get_or_create_domain(request.domain_name)
        
        # Perform risk analysis
        risk_score, risk_factors = await self._calculate_risk_score(
            domain.domain_name, 
            request.force_rescan
        )
        
        # Update domain with new risk score
        domain.risk_score = risk_score
        domain.risk_level = self._get_risk_level(risk_score)
        domain.risk_factors = risk_factors
        domain.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(domain)
        
        # Create scan record
        scan = DomainScan(
            domain_id=domain.id,
            scan_type="risk",
            scan_data={"request": request.dict(), "factors": risk_factors},
            risk_score=risk_score,
            risk_level=self._get_risk_level(risk_score),
            risk_factors=risk_factors,
            scanner_version="1.0.0",
            scan_duration_ms=int((time.time() - start_time) * 1000)
        )
        self.db.add(scan)
        await self.db.commit()
        
        # Generate recommendations based on risk factors
        recommendations = self._generate_recommendations(risk_factors)
        
        analysis_time = int((time.time() - start_time) * 1000)
        
        return RiskAnalysisResponse(
            domain_id=domain.id,
            domain_name=domain.domain_name,
            risk_score=risk_score,
            risk_level=self._get_risk_level(risk_score),
            risk_factors=risk_factors,
            threat_indicators=[],  # Will be populated by threat intelligence providers
            recommendations=recommendations,
            analysis_time_ms=analysis_time,
            scan_id=scan.id
        )
    
    async def _get_or_create_domain(self, domain_name: str) -> Domain:
        """
        Get existing domain or create new one.
        """
        query = select(Domain).where(Domain.domain_name == domain_name)
        result = await self.db.execute(query)
        domain = result.scalar_one_or_none()
        
        if not domain:
            domain = Domain(
                domain_name=domain_name,
                registered_date=datetime.utcnow(),
                source="manual"
            )
            self.db.add(domain)
            await self.db.commit()
            await self.db.refresh(domain)
        
        return domain
    
    async def _calculate_risk_score(self, domain_name: str, force_rescan: bool = False) -> tuple:
        """
        Calculate risk score for a domain based on various factors.
        """
        # Calculate individual risk factors
        domain_length = len(domain_name)
        length_score = self._calculate_length_risk(domain_length)
        
        entropy_score = self._calculate_entropy_risk(domain_name)
        
        tld_risk = self._calculate_tld_risk(domain_name)
        
        keyword_score = self._calculate_keyword_risk(domain_name)
        
        # Age is not applicable for new domains, so we'll set it to a neutral score
        age_score = 0.5  # Neutral score for new domains
        
        # Apply weights
        weighted_score = (
            length_score * self.config["weights"]["domain_length"] +
            entropy_score * self.config["weights"]["entropy_score"] +
            tld_risk * self.config["weights"]["tld_risk"] +
            keyword_score * self.config["weights"]["keyword_matches"] +
            age_score * self.config["weights"]["age_days"]
        )
        
        # Normalize to 0-100 scale
        risk_score = min(100.0, max(0.0, weighted_score * 100))
        
        risk_factors = {
            "domain_length": {
                "score": length_score,
                "weight": self.config["weights"]["domain_length"],
                "raw_value": domain_length
            },
            "entropy_score": {
                "score": entropy_score,
                "weight": self.config["weights"]["entropy_score"],
                "raw_value": round(entropy_score, 2)
            },
            "tld_risk": {
                "score": tld_risk,
                "weight": self.config["weights"]["tld_risk"],
                "raw_value": self._get_tld(domain_name)
            },
            "keyword_matches": {
                "score": keyword_score,
                "weight": self.config["weights"]["keyword_matches"],
                "raw_value": self._find_matching_keywords(domain_name)
            },
            "age_days": {
                "score": age_score,
                "weight": self.config["weights"]["age_days"],
                "raw_value": 0  # New domain
            }
        }
        
        return risk_score, risk_factors
    
    def _calculate_length_risk(self, domain_length: int) -> float:
        """
        Calculate risk based on domain length.
        Very long or very short domains can be suspicious.
        """
        if domain_length > self.config["max_domain_length"]:
            return 1.0  # High risk
        elif domain_length < 3:
            return 0.8  # High risk
        elif domain_length < 6:
            return 0.6  # Medium risk
        elif domain_length > 20:
            return 0.7  # Medium-high risk
        else:
            return 0.2  # Low risk
    
    def _calculate_entropy_risk(self, domain_name: str) -> float:
        """
        Calculate risk based on character entropy.
        High entropy (random-looking) domains are often malicious.
        """
        # Remove TLD part for entropy calculation
        tld_start = domain_name.rfind('.')
        if tld_start != -1:
            domain_part = domain_name[:tld_start]
        else:
            domain_part = domain_name
        
        # Calculate character frequency
        char_counts = {}
        for char in domain_part.lower():
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate probabilities
        total_chars = len(domain_part)
        if total_chars == 0:
            return 0.0
        
        probs = [count / total_chars for count in char_counts.values()]
        
        # Calculate entropy
        ent = entropy(probs, base=2)
        
        # Normalize to 0-1 scale (max entropy for English is roughly 4.7 bits for random)
        max_possible_entropy = 4.7
        normalized_entropy = min(1.0, ent / max_possible_entropy)
        
        # High entropy = higher risk
        if normalized_entropy > self.config["min_entropy_threshold"] / max_possible_entropy:
            return normalized_entropy
        else:
            return normalized_entropy * 0.3  # Lower weight for low entropy
    
    def _calculate_tld_risk(self, domain_name: str) -> float:
        """
        Calculate risk based on Top Level Domain.
        Some TLDs are associated with higher risk.
        """
        tld = self._get_tld(domain_name).lower()
        
        if tld in [susp_tld.lower() for susp_tld in self.config["suspicious_tlds"]]:
            return 0.9  # High risk
        elif tld in [".com", ".net", ".org", ".edu", ".gov"]:
            return 0.1  # Low risk
        else:
            return 0.4  # Medium risk
    
    def _calculate_keyword_risk(self, domain_name: str) -> float:
        """
        Calculate risk based on suspicious keywords in domain.
        """
        domain_lower = domain_name.lower()
        matching_keywords = []
        
        for keyword in self.config["high_risk_keywords"]:
            if keyword in domain_lower:
                matching_keywords.append(keyword)
        
        if len(matching_keywords) == 0:
            return 0.1  # Low risk
        elif len(matching_keywords) == 1:
            return 0.5  # Medium risk
        elif len(matching_keywords) <= 3:
            return 0.7  # High risk
        else:
            return 0.9  # Very high risk
    
    def _get_tld(self, domain_name: str) -> str:
        """
        Extract TLD from domain name.
        """
        parts = domain_name.split('.')
        if len(parts) > 1:
            return '.' + parts[-1]
        return ''
    
    def _find_matching_keywords(self, domain_name: str) -> List[str]:
        """
        Find matching high-risk keywords in domain name.
        """
        domain_lower = domain_name.lower()
        matching_keywords = []
        
        for keyword in self.config["high_risk_keywords"]:
            if keyword in domain_lower:
                matching_keywords.append(keyword)
        
        return matching_keywords
    
    def _get_risk_level(self, risk_score: float) -> str:
        """
        Convert risk score to risk level.
        """
        if risk_score < 20:
            return "low"
        elif risk_score < 40:
            return "medium"
        elif risk_score < 60:
            return "high"
        else:
            return "critical"
    
    def _generate_recommendations(self, risk_factors: Dict) -> List[str]:
        """
        Generate recommendations based on risk factors.
        """
        recommendations = []
        
        # Length-based recommendations
        length_factor = risk_factors.get("domain_length", {})
        if length_factor.get("raw_value", 0) > self.config["max_domain_length"]:
            recommendations.append("Domain name is unusually long, which may indicate obfuscation")
        elif length_factor.get("raw_value", 0) < 3:
            recommendations.append("Domain name is very short, potentially indicating typosquatting")
        
        # Entropy-based recommendations
        entropy_factor = risk_factors.get("entropy_score", {})
        if entropy_factor.get("raw_value", 0) > 0.7:
            recommendations.append("High character entropy suggests randomly generated domain, possible botnet C&C")
        
        # TLD-based recommendations
        tld_factor = risk_factors.get("tld_risk", {})
        if tld_factor.get("raw_value", "") in [susp_tld.lower() for susp_tld in self.config["suspicious_tlds"]]:
            recommendations.append(f"Suspicious TLD {tld_factor['raw_value']} commonly used for malicious purposes")
        
        # Keyword-based recommendations
        keyword_factor = risk_factors.get("keyword_matches", {})
        matching_keywords = keyword_factor.get("raw_value", [])
        if len(matching_keywords) > 0:
            recommendations.append(f"Domain contains high-risk keywords: {', '.join(matching_keywords)}")
        
        if not recommendations:
            recommendations.append("No specific risk indicators detected, but continued monitoring recommended")
        
        return recommendations
    
    async def queue_risk_analysis(self, domain_name: str, force_rescan: bool) -> str:
        """
        Queue a risk analysis task (simulated).
        In a real implementation, this would integrate with Celery.
        """
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        
        # In a real implementation, this would send the task to Celery
        # For now, we'll simulate by storing the task in a simple way
        # (in a real app, use Redis or DB to track task status)
        
        return task_id
    
    async def get_analysis_status(self, task_id: str) -> Dict:
        """
        Get the status of a risk analysis task.
        """
        # In a real implementation, this would check Celery task status
        # For now, we'll return a simulated status
        
        # Simulate different statuses based on task ID
        if task_id.endswith("0"):  # Simulate pending
            return {"task_id": task_id, "status": "pending", "progress": 0}
        elif task_id.endswith("1"):  # Simulate in progress
            return {"task_id": task_id, "status": "processing", "progress": 50}
        elif task_id.endswith("2"):  # Simulate completed
            return {"task_id": task_id, "status": "completed", "progress": 100}
        else:  # Default to unknown
            return {"task_id": task_id, "status": "unknown", "progress": 0}
    
    async def get_risk_config(self) -> Dict:
        """
        Get current risk configuration.
        """
        return self.config
    
    async def get_risk_trends(self, days: int = 30) -> Dict:
        """
        Get risk trends over time.
        """
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        # Query for average risk scores over time
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date)
            current_date += timedelta(days=1)
        
        trends = []
        for date in date_range:
            start_of_day = datetime.combine(date, datetime.min.time())
            end_of_day = datetime.combine(date, datetime.max.time())
            
            query = select(func.avg(Domain.risk_score)).where(
                and_(
                    Domain.created_at >= start_of_day,
                    Domain.created_at <= end_of_day,
                )
            )
            result = await self.db.execute(query)
            avg_risk = result.scalar() or 0.0
            
            query_count = select(func.count(Domain.id)).where(
                and_(
                    Domain.created_at >= start_of_day,
                    Domain.created_at <= end_of_day,
                )
            )
            count_result = await self.db.execute(query_count)
            count = count_result.scalar() or 0
            
            trends.append({
                "date": date.isoformat(),
                "avg_risk_score": round(avg_risk, 2),
                "domain_count": count
            })
        
        return {
            "period_days": days,
            "trends": trends,
            "updated_at": datetime.utcnow().isoformat()
        }
    
    async def get_risk_factor_breakdown(self, days: int = 30) -> Dict:
        """
        Get risk factor breakdown over time.
        """
        # For now, return a static breakdown based on our risk model
        # In a real implementation, this would aggregate historical data
        
        return {
            "period_days": days,
            "breakdown": {
                "domain_length": 15,
                "entropy_score": 25,
                "tld_risk": 20,
                "keyword_matches": 30,
                "age_days": 10
            },
            "updated_at": datetime.utcnow().isoformat()
        }