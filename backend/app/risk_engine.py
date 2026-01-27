"""
Risk Engine for DomainSentry.

Advanced scoring engine for domain risk assessment using ML-lite techniques:
- Domain length analysis
- Character entropy scoring
- TLD risk classification
- Keyword pattern matching
- N-gram analysis
- Temporal scoring (domain age)

Supports configurable weights via YAML and real-time scoring.
"""

import re
import math
from typing import Dict, List, Optional, Tuple, Any
import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RiskEngine:
    """World-class risk scoring engine for domain names."""
    
    def __init__(self, config_path: str = "config/risk_weights.yaml"):
        """Initialize the risk engine with configuration."""
        self.config = self._load_config(config_path)
        self.weights = self.config.get("weights", {})
        
        # Load keyword patterns
        self.suspicious_keywords = self.config.get("suspicious_keywords", [])
        self.malware_keywords = self.config.get("malware_keywords", [])
        self.phishing_keywords = self.config.get("phishing_keywords", [])
        
        # TLD risk scores
        self.tld_risk_scores = self.config.get("tld_risk_scores", {})
        
        # Initialize ML components
        self.tfidf_vectorizer = None
        self.classifier = None
        self._init_ml_models()
        
        logger.info(f"Risk Engine initialized with weights: {self.weights}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load risk configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Risk config not found at {config_path}, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default configuration if config file is missing."""
        return {
            "weights": {
                "domain_length": 0.15,
                "entropy_score": 0.25,
                "tld_risk": 0.20,
                "keyword_matches": 0.30,
                "age_days": 0.10
            },
            "suspicious_keywords": [
                "login", "secure", "account", "verify", "update", "bank",
                "paypal", "microsoft", "apple", "support", "service"
            ],
            "malware_keywords": [
                "trojan", "ransomware", "malware", "virus", "spyware",
                "botnet", "keylogger", "backdoor", "exploit", "payload"
            ],
            "phishing_keywords": [
                "phish", "spoof", "clone", "fake", "impersonate",
                "credential", "password", "auth", "authentication"
            ],
            "tld_risk_scores": {
                ".com": 0.1, ".net": 0.2, ".org": 0.15,
                ".xyz": 0.8, ".top": 0.7, ".loan": 0.9,
                ".click": 0.8, ".win": 0.7, ".biz": 0.6,
                ".info": 0.5, ".online": 0.6, ".site": 0.7,
                ".work": 0.6, ".club": 0.5, ".store": 0.4
            }
        }
    
    def _init_ml_models(self):
        """Initialize ML models for advanced pattern recognition."""
        # Simple TF-IDF vectorizer for domain name analysis
        self.tfidf_vectorizer = TfidfVectorizer(
            analyzer='char',
            ngram_range=(2, 4),
            max_features=1000,
            lowercase=True
        )
        
        # Initialize classifier (would be trained with real data)
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        # TODO: Load pre-trained model or train with historical data
    
    def calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of a string."""
        if not text:
            return 0.0
        
        # Count character frequencies
        freq = {}
        for char in text.lower():
            freq[char] = freq.get(char, 0) + 1
        
        # Calculate entropy
        length = len(text)
        entropy = 0.0
        for count in freq.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def score_domain_length(self, domain: str) -> Tuple[float, Dict]:
        """Score based on domain name length."""
        domain_name = domain.split('.')[0] if '.' in domain else domain
        length = len(domain_name)
        
        # Scoring logic: very short or very long domains are suspicious
        if length < 5:
            score = 0.8  # Very short domains are suspicious
            reason = f"Domain name very short ({length} chars)"
        elif length > 30:
            score = 0.7  # Very long domains are suspicious
            reason = f"Domain name very long ({length} chars)"
        elif length > 20:
            score = 0.4  # Long domains are somewhat suspicious
            reason = f"Domain name long ({length} chars)"
        else:
            score = 0.1  # Normal length
            reason = f"Domain name normal length ({length} chars)"
        
        details = {
            "length": length,
            "score": score,
            "reason": reason
        }
        
        return score, details
    
    def score_entropy(self, domain: str) -> Tuple[float, Dict]:
        """Score based on character entropy."""
        domain_name = domain.split('.')[0] if '.' in domain else domain
        entropy = self.calculate_entropy(domain_name)
        
        # Normalize entropy score (0-1 range)
        # Typical English text has entropy ~4.0-4.5
        if entropy < 2.0:
            score = 0.9  # Too predictable
            reason = f"Low entropy ({entropy:.2f}), predictable pattern"
        elif entropy > 4.5:
            score = 0.8  # Too random (could be DGA)
            reason = f"High entropy ({entropy:.2f}), random pattern"
        elif entropy > 4.0:
            score = 0.3  # Slightly high
            reason = f"Moderate entropy ({entropy:.2f})"
        else:
            score = 0.1  # Normal
            reason = f"Normal entropy ({entropy:.2f})"
        
        details = {
            "entropy": entropy,
            "score": score,
            "reason": reason
        }
        
        return score, details
    
    def score_tld(self, domain: str) -> Tuple[float, Dict]:
        """Score based on TLD risk classification."""
        # Extract TLD
        parts = domain.split('.')
        if len(parts) < 2:
            tld = domain
        else:
            tld = f".{parts[-1]}"
        
        # Look up TLD risk score
        tld_risk = self.tld_risk_scores.get(tld.lower(), 0.5)
        
        # Map to score
        if tld_risk > 0.7:
            score = 0.9
            reason = f"High-risk TLD: {tld}"
        elif tld_risk > 0.5:
            score = 0.6
            reason = f"Medium-risk TLD: {tld}"
        else:
            score = 0.2
            reason = f"Low-risk TLD: {tld}"
        
        details = {
            "tld": tld,
            "tld_risk": tld_risk,
            "score": score,
            "reason": reason
        }
        
        return score, details
    
    def score_keywords(self, domain: str) -> Tuple[float, Dict]:
        """Score based on suspicious keyword matches."""
        domain_lower = domain.lower()
        
        matches = {
            "suspicious": [],
            "malware": [],
            "phishing": []
        }
        
        # Check for keyword matches
        for keyword in self.suspicious_keywords:
            if keyword in domain_lower:
                matches["suspicious"].append(keyword)
        
        for keyword in self.malware_keywords:
            if keyword in domain_lower:
                matches["malware"].append(keyword)
        
        for keyword in self.phishing_keywords:
            if keyword in domain_lower:
                matches["phishing"].append(keyword)
        
        # Calculate score based on matches
        total_matches = (
            len(matches["suspicious"]) +
            len(matches["malware"]) * 2 +  # Malware keywords weighted higher
            len(matches["phishing"]) * 3   # Phishing keywords weighted highest
        )
        
        if total_matches >= 3:
            score = 0.95
            reason = f"Multiple suspicious keywords detected: {matches}"
        elif total_matches >= 2:
            score = 0.75
            reason = f"Suspicious keywords detected: {matches}"
        elif total_matches >= 1:
            score = 0.5
            reason = f"Keyword match detected: {matches}"
        else:
            score = 0.1
            reason = "No suspicious keyword matches"
        
        details = {
            "matches": matches,
            "total_matches": total_matches,
            "score": score,
            "reason": reason
        }
        
        return score, details
    
    def score_age(self, created_date: Optional[datetime] = None) -> Tuple[float, Dict]:
        """Score based on domain age."""
        if not created_date:
            score = 0.5  # Unknown age
            reason = "Domain age unknown"
            age_days = None
        else:
            now = datetime.utcnow()
            age_days = (now - created_date).days
            
            if age_days < 1:
                score = 0.9  # Brand new domain
                reason = f"Domain very new ({age_days} days)"
            elif age_days < 7:
                score = 0.7  # Less than a week old
                reason = f"Domain new ({age_days} days)"
            elif age_days < 30:
                score = 0.4  # Less than a month old
                reason = f"Domain relatively new ({age_days} days)"
            else:
                score = 0.1  # Established domain
                reason = f"Domain established ({age_days} days)"
        
        details = {
            "age_days": age_days,
            "score": score,
            "reason": reason
        }
        
        return score, details
    
    def score_ml_pattern(self, domain: str) -> Tuple[float, Dict]:
        """Score using ML pattern recognition."""
        # This is a placeholder for actual ML scoring
        # In production, this would use a trained model
        
        # Simple heuristic for now
        domain_name = domain.split('.')[0] if '.' in domain else domain
        
        # Check for DGA-like patterns (consecutive consonants/vowels)
        consonants = sum(1 for c in domain_name if c.lower() in 'bcdfghjklmnpqrstvwxyz')
        vowels = sum(1 for c in domain_name if c.lower() in 'aeiou')
        ratio = consonants / (vowels + 1)
        
        if ratio > 3.0:
            score = 0.8
            reason = f"High consonant/vowel ratio ({ratio:.2f}), possible DGA"
        elif ratio > 2.0:
            score = 0.5
            reason = f"Moderate consonant/vowel ratio ({ratio:.2f})"
        else:
            score = 0.2
            reason = f"Normal consonant/vowel ratio ({ratio:.2f})"
        
        details = {
            "consonant_vowel_ratio": ratio,
            "score": score,
            "reason": reason
        }
        
        return score, details
    
    def calculate_overall_risk(
        self,
        domain: str,
        created_date: Optional[datetime] = None,
        additional_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive risk score for a domain.
        
        Args:
            domain: Domain name to score
            created_date: Domain creation date (optional)
            additional_context: Additional context for scoring (optional)
            
        Returns:
            Dictionary with risk score and detailed breakdown
        """
        logger.info(f"Calculating risk score for domain: {domain}")
        
        # Calculate individual component scores
        length_score, length_details = self.score_domain_length(domain)
        entropy_score, entropy_details = self.score_entropy(domain)
        tld_score, tld_details = self.score_tld(domain)
        keyword_score, keyword_details = self.score_keywords(domain)
        age_score, age_details = self.score_age(created_date)
        ml_score, ml_details = self.score_ml_pattern(domain)
        
        # Weighted average calculation
        weighted_scores = [
            length_score * self.weights.get("domain_length", 0.15),
            entropy_score * self.weights.get("entropy_score", 0.25),
            tld_score * self.weights.get("tld_risk", 0.20),
            keyword_score * self.weights.get("keyword_matches", 0.30),
            age_score * self.weights.get("age_days", 0.10)
        ]
        
        # Include ML score if available
        if ml_score:
            ml_weight = 0.15
            # Adjust other weights proportionally
            scale_factor = 1 - ml_weight
            weighted_scores = [score * scale_factor for score in weighted_scores]
            weighted_scores.append(ml_score * ml_weight)
        
        overall_score = sum(weighted_scores)
        
        # Cap score at 0.99
        overall_score = min(0.99, overall_score)
        
        # Determine risk level
        if overall_score >= 0.8:
            risk_level = "CRITICAL"
        elif overall_score >= 0.6:
            risk_level = "HIGH"
        elif overall_score >= 0.4:
            risk_level = "MEDIUM"
        elif overall_score >= 0.2:
            risk_level = "LOW"
        else:
            risk_level = "VERY_LOW"
        
        # Compile result
        result = {
            "domain": domain,
            "overall_score": round(overall_score, 4),
            "risk_level": risk_level,
            "component_scores": {
                "domain_length": {
                    "score": round(length_score, 4),
                    "details": length_details
                },
                "entropy": {
                    "score": round(entropy_score, 4),
                    "details": entropy_details
                },
                "tld_risk": {
                    "score": round(tld_score, 4),
                    "details": tld_details
                },
                "keyword_matches": {
                    "score": round(keyword_score, 4),
                    "details": keyword_details
                },
                "age_days": {
                    "score": round(age_score, 4),
                    "details": age_details
                }
            },
            "ml_pattern_score": {
                "score": round(ml_score, 4),
                "details": ml_details
            } if ml_score else None,
            "weights": self.weights,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add recommendations if score is high
        if overall_score >= 0.6:
            result["recommendations"] = self._generate_recommendations(result)
        
        logger.info(f"Risk calculation complete for {domain}: {risk_level} ({overall_score})")
        
        return result
    
    def _generate_recommendations(self, risk_result: Dict) -> List[str]:
        """Generate actionable recommendations based on risk score."""
        recommendations = []
        
        if risk_result["overall_score"] >= 0.8:
            recommendations.append("🔴 IMMEDIATE ACTION REQUIRED: Investigate this domain immediately")
            recommendations.append("Consider blocking this domain at network perimeter")
            recommendations.append("Submit to VirusTotal/AbuseIPDB for community analysis")
        
        elif risk_result["overall_score"] >= 0.6:
            recommendations.append("🟡 HIGH RISK: Monitor this domain closely")
            recommendations.append("Consider adding to watchlist for further investigation")
            recommendations.append("Check for related domains and infrastructure")
        
        # Specific recommendations based on components
        comp_scores = risk_result["component_scores"]
        
        if comp_scores["keyword_matches"]["score"] >= 0.7:
            recommendations.append("Suspicious keywords detected - verify legitimacy")
        
        if comp_scores["tld_risk"]["score"] >= 0.7:
            recommendations.append(f"High-risk TLD detected: {comp_scores['tld_risk']['details']['tld']}")
        
        if comp_scores["entropy"]["score"] >= 0.7:
            recommendations.append("Unusual character patterns detected - possible DGA")
        
        return recommendations
    
    def batch_score_domains(
        self,
        domains: List[str],
        created_dates: Optional[List[datetime]] = None
    ) -> List[Dict]:
        """
        Calculate risk scores for multiple domains efficiently.
        
        Args:
            domains: List of domain names
            created_dates: Optional list of creation dates
            
        Returns:
            List of risk results
        """
        results = []
        
        for i, domain in enumerate(domains):
            created_date = created_dates[i] if created_dates else None
            result = self.calculate_overall_risk(domain, created_date)
            results.append(result)
        
        return results
    
    def update_weights(self, new_weights: Dict):
        """Update risk weighting configuration."""
        self.weights.update(new_weights)
        logger.info(f"Risk weights updated: {self.weights}")
    
    def export_config(self) -> Dict:
        """Export current configuration."""
        return {
            "weights": self.weights,
            "suspicious_keywords": self.suspicious_keywords,
            "malware_keywords": self.malware_keywords,
            "phishing_keywords": self.phishing_keywords,
            "tld_risk_scores": self.tld_risk_scores,
            "timestamp": datetime.utcnow().isoformat()
        }


# Singleton instance for easy import
risk_engine = RiskEngine()