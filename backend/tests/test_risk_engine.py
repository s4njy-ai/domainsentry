"""
Comprehensive tests for the DomainSentry Risk Engine.

Covers:
- Domain length scoring
- Entropy calculations
- TLD risk classification
- Keyword matching
- Age-based scoring
- ML pattern recognition
- Overall risk calculation
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import numpy as np

from app.risk_engine import RiskEngine, risk_engine


class TestRiskEngine:
    """Test suite for the RiskEngine class."""
    
    def test_initialization(self):
        """Test that RiskEngine initializes with default config."""
        engine = RiskEngine()
        assert engine.weights is not None
        assert "domain_length" in engine.weights
        assert "entropy_score" in engine.weights
        assert "tld_risk" in engine.weights
        assert "keyword_matches" in engine.weights
        assert "age_days" in engine.weights
    
    def test_entropy_calculation(self):
        """Test Shannon entropy calculation."""
        engine = RiskEngine()
        
        # Test with predictable string
        assert engine.calculate_entropy("aaaaa") == 0.0
        
        # Test with mixed string
        entropy = engine.calculate_entropy("abcde")
        assert entropy > 2.0
        
        # Test with empty string
        assert engine.calculate_entropy("") == 0.0
        
        # Test with random string
        entropy_random = engine.calculate_entropy("x7g9k2p5q")
        assert entropy_random > 3.0
    
    def test_score_domain_length(self):
        """Test domain length scoring."""
        engine = RiskEngine()
        
        # Very short domain
        score, details = engine.score_domain_length("ab.com")
        assert score >= 0.7
        assert "very short" in details["reason"].lower()
        
        # Very long domain
        long_domain = "a" * 35 + ".com"
        score, details = engine.score_domain_length(long_domain)
        assert score >= 0.7
        assert "very long" in details["reason"].lower()
        
        # Normal domain
        score, details = engine.score_domain_length("example.com")
        assert score <= 0.2
        assert "normal" in details["reason"].lower()
        
        # Long domain
        longish_domain = "a" * 25 + ".com"
        score, details = engine.score_domain_length(longish_domain)
        assert 0.3 <= score <= 0.5
        assert "long" in details["reason"].lower()
    
    def test_score_entropy(self):
        """Test entropy-based scoring."""
        engine = RiskEngine()
        
        # Low entropy (predictable)
        score, details = engine.score_entropy("aaaaa.com")
        assert score >= 0.8
        assert "low entropy" in details["reason"].lower()
        
        # High entropy (random)
        score, details = engine.score_entropy("x7g9k2p5q.com")
        assert score >= 0.7
        assert "high entropy" in details["reason"].lower()
        
        # Normal entropy
        score, details = engine.score_entropy("example.com")
        assert score <= 0.2
        assert "normal" in details["reason"].lower()
    
    def test_score_tld(self):
        """Test TLD risk scoring."""
        engine = RiskEngine()
        
        # High-risk TLD
        score, details = engine.score_tld("example.xyz")
        assert score >= 0.8
        assert "high-risk" in details["reason"].lower()
        
        # Medium-risk TLD
        score, details = engine.score_tld("example.biz")
        assert 0.5 <= score <= 0.7
        
        # Low-risk TLD
        score, details = engine.score_tld("example.com")
        assert score <= 0.3
        assert "low-risk" in details["reason"].lower()
        
        # Unknown TLD (default score)
        score, details = engine.score_tld("example.unknown")
        assert 0.4 <= score <= 0.6
    
    def test_score_keywords(self):
        """Test keyword-based scoring."""
        engine = RiskEngine()
        
        # Phishing keyword
        score, details = engine.score_keywords("paypal-login-verify.com")
        assert score >= 0.5
        assert "keyword" in details["reason"].lower()
        assert "paypal" in str(details["matches"]).lower()
        
        # Malware keyword
        score, details = engine.score_keywords("trojan-download-site.com")
        assert score >= 0.7
        assert "trojan" in str(details["matches"]).lower()
        
        # Multiple keywords
        score, details = engine.score_keywords("secure-bank-login-update.com")
        assert score >= 0.8
        assert len(details["matches"]["suspicious"]) >= 3
        
        # No keywords
        score, details = engine.score_keywords("innocuous-domain.com")
        assert score <= 0.2
        assert "no suspicious" in details["reason"].lower()
    
    def test_score_age(self):
        """Test age-based scoring."""
        engine = RiskEngine()
        
        # Brand new domain
        new_date = datetime.utcnow() - timedelta(hours=12)
        score, details = engine.score_age(new_date)
        assert score >= 0.8
        assert "very new" in details["reason"].lower()
        
        # Week old domain
        week_old = datetime.utcnow() - timedelta(days=5)
        score, details = engine.score_age(week_old)
        assert 0.6 <= score <= 0.8
        assert "new" in details["reason"].lower()
        
        # Month old domain
        month_old = datetime.utcnow() - timedelta(days=25)
        score, details = engine.score_age(month_old)
        assert 0.3 <= score <= 0.5
        
        # Established domain
        old_date = datetime.utcnow() - timedelta(days=100)
        score, details = engine.score_age(old_date)
        assert score <= 0.2
        assert "established" in details["reason"].lower()
        
        # Unknown age
        score, details = engine.score_age(None)
        assert score == 0.5
        assert "unknown" in details["reason"].lower()
    
    def test_score_ml_pattern(self):
        """Test ML pattern scoring."""
        engine = RiskEngine()
        
        # DGA-like pattern (high consonant/vowel ratio)
        score, details = engine.score_ml_pattern("xqzbgtpfn.com")
        assert score >= 0.7
        assert "dga" in details["reason"].lower()
        
        # Normal pattern
        score, details = engine.score_ml_pattern("example.com")
        assert score <= 0.3
        assert "normal" in details["reason"].lower()
    
    def test_calculate_overall_risk(self):
        """Test comprehensive risk calculation."""
        engine = RiskEngine()
        
        # High-risk domain
        result = engine.calculate_overall_risk(
            "secure-paypal-login-verify.xyz",
            created_date=datetime.utcnow() - timedelta(hours=6)
        )
        
        assert result["domain"] == "secure-paypal-login-verify.xyz"
        assert result["overall_score"] >= 0.7
        assert result["risk_level"] in ["HIGH", "CRITICAL"]
        assert "component_scores" in result
        assert "recommendations" in result
        
        # Check component scores are present
        comp_scores = result["component_scores"]
        assert "domain_length" in comp_scores
        assert "entropy" in comp_scores
        assert "tld_risk" in comp_scores
        assert "keyword_matches" in comp_scores
        assert "age_days" in comp_scores
        
        # Low-risk domain
        result = engine.calculate_overall_risk(
            "example.com",
            created_date=datetime.utcnow() - timedelta(days=365)
        )
        
        assert result["overall_score"] <= 0.3
        assert result["risk_level"] in ["LOW", "VERY_LOW"]
        assert "recommendations" not in result  # No recommendations for low risk
    
    def test_batch_score_domains(self):
        """Test batch scoring of multiple domains."""
        engine = RiskEngine()
        
        domains = [
            "example.com",
            "secure-login-bank.xyz",
            "malware-download-site.top"
        ]
        
        created_dates = [
            datetime.utcnow() - timedelta(days=365),
            datetime.utcnow() - timedelta(days=2),
            datetime.utcnow() - timedelta(hours=12)
        ]
        
        results = engine.batch_score_domains(domains, created_dates)
        
        assert len(results) == 3
        
        # First should be low risk
        assert results[0]["overall_score"] <= 0.3
        
        # Last should be high risk
        assert results[2]["overall_score"] >= 0.7
    
    def test_update_weights(self):
        """Test weight configuration updates."""
        engine = RiskEngine()
        
        original_weights = engine.weights.copy()
        
        # Update weights
        new_weights = {
            "domain_length": 0.3,
            "entropy_score": 0.2,
            "tld_risk": 0.1,
            "keyword_matches": 0.3,
            "age_days": 0.1
        }
        
        engine.update_weights(new_weights)
        
        # Check weights were updated
        assert engine.weights["domain_length"] == 0.3
        assert engine.weights["entropy_score"] == 0.2
        assert engine.weights["tld_risk"] == 0.1
        
        # Calculate score with new weights
        result = engine.calculate_overall_risk("example.com")
        assert result["weights"] == engine.weights
    
    def test_export_config(self):
        """Test configuration export."""
        engine = RiskEngine()
        
        config = engine.export_config()
        
        assert "weights" in config
        assert "suspicious_keywords" in config
        assert "malware_keywords" in config
        assert "phishing_keywords" in config
        assert "tld_risk_scores" in config
        assert "timestamp" in config
    
    def test_recommendations_generation(self):
        """Test recommendation generation for high-risk domains."""
        engine = RiskEngine()
        
        # Create a high-risk result
        high_risk_result = {
            "overall_score": 0.85,
            "risk_level": "CRITICAL",
            "component_scores": {
                "keyword_matches": {"score": 0.9, "details": {}},
                "tld_risk": {"score": 0.8, "details": {"tld": ".xyz"}},
                "entropy": {"score": 0.7, "details": {}}
            }
        }
        
        recommendations = engine._generate_recommendations(high_risk_result)
        
        assert len(recommendations) > 0
        assert any("IMMEDIATE ACTION" in rec for rec in recommendations)
        assert any("high-risk tld" in rec.lower() for rec in recommendations)
        
        # Test medium risk
        med_risk_result = {
            "overall_score": 0.65,
            "risk_level": "HIGH",
            "component_scores": {
                "keyword_matches": {"score": 0.5, "details": {}},
                "tld_risk": {"score": 0.6, "details": {}},
                "entropy": {"score": 0.4, "details": {}}
            }
        }
        
        recommendations = engine._generate_recommendations(med_risk_result)
        assert any("monitor" in rec.lower() for rec in recommendations)
    
    def test_singleton_instance(self):
        """Test that the singleton instance works correctly."""
        # Import the singleton
        from app.risk_engine import risk_engine
        
        assert risk_engine is not None
        assert hasattr(risk_engine, 'calculate_overall_risk')
        
        # Use the singleton
        result = risk_engine.calculate_overall_risk("test.com")
        assert "domain" in result
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        engine = RiskEngine()
        
        # Empty domain
        result = engine.calculate_overall_risk("")
        assert result["overall_score"] > 0  # Should still produce a score
        
        # Domain without TLD
        result = engine.calculate_overall_risk("example")
        assert "tld_risk" in result["component_scores"]
        
        # Domain with multiple subdomains
        result = engine.calculate_overall_risk("sub1.sub2.example.com")
        assert result["domain"] == "sub1.sub2.example.com"
        
        # Very weird domain
        weird_domain = "a" * 100 + "." + "b" * 50
        result = engine.calculate_overall_risk(weird_domain)
        assert result["overall_score"] >= 0.7  # Should be high risk


class TestRiskEngineIntegration:
    """Integration tests for risk engine with real data."""
    
    def test_with_real_suspicious_domains(self):
        """Test with known suspicious domain patterns."""
        engine = RiskEngine()
        
        suspicious_domains = [
            "paypal-secure-login-verify.xyz",
            "microsoft-account-update.support",
            "bank-of-america-secure.login",
            "apple-id-verification.account"
        ]
        
        for domain in suspicious_domains:
            result = engine.calculate_overall_risk(domain)
            assert result["overall_score"] >= 0.6
            assert result["risk_level"] in ["HIGH", "CRITICAL"]
            
            # Should have keyword matches
            keyword_score = result["component_scores"]["keyword_matches"]["score"]
            assert keyword_score >= 0.5
            
            # Should have recommendations
            assert "recommendations" in result
    
    def test_with_legitimate_domains(self):
        """Test with known legitimate domains."""
        engine = RiskEngine()
        
        legitimate_domains = [
            "google.com",
            "github.com",
            "wikipedia.org",
            "stackoverflow.com",
            "python.org"
        ]
        
        for domain in legitimate_domains:
            result = engine.calculate_overall_risk(
                domain,
                created_date=datetime.utcnow() - timedelta(days=365 * 5)  # 5 years old
            )
            assert result["overall_score"] <= 0.3
            assert result["risk_level"] in ["LOW", "VERY_LOW"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])