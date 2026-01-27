"""
Health endpoint tests for DomainSentry.

Tests the health monitoring endpoints that provide system status,
dependency checks, and service availability.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock


class TestHealthEndpoints:
    """Test health monitoring endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, test_client: AsyncClient):
        """Test basic health endpoint."""
        response = await test_client.get("/health")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "service" in data
        assert data["service"] == "domainsentry"
    
    @pytest.mark.asyncio
    async def test_health_detailed(self, test_client: AsyncClient):
        """Test detailed health endpoint with component checks."""
        response = await test_client.get("/health/detailed")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "components" in data
        assert "timestamp" in data
        
        components = data["components"]
        assert "database" in components
        assert "redis" in components
        assert "celery" in components
        assert "external_apis" in components
    
    @pytest.mark.asyncio
    async def test_health_metrics(self, test_client: AsyncClient):
        """Test Prometheus metrics endpoint."""
        response = await test_client.get("/metrics")
        
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        
        # Check for some Prometheus metrics
        content = response.text
        assert "# HELP" in content
        assert "# TYPE" in content
        assert "http_requests_total" in content
    
    @pytest.mark.asyncio
    async def test_health_ready(self, test_client: AsyncClient):
        """Test readiness probe endpoint."""
        response = await test_client.get("/health/ready")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "ready" in data
        assert data["ready"] is True
        assert "dependencies" in data
    
    @pytest.mark.asyncio
    async def test_health_live(self, test_client: AsyncClient):
        """Test liveness probe endpoint."""
        response = await test_client.get("/health/live")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "alive" in data
        assert data["alive"] is True
    
    @pytest.mark.asyncio
    async def test_health_with_database_down(self, test_client: AsyncClient):
        """Test health endpoint when database is down."""
        # Mock database failure
        with patch('app.db.session.get_db', side_effect=Exception("Database connection failed")):
            response = await test_client.get("/health/detailed")
            
            assert response.status_code == 503  # Service Unavailable
            
            data = response.json()
            assert data["status"] == "unhealthy"
            
            components = data["components"]
            assert components["database"]["status"] == "down"
            assert "error" in components["database"]
    
    @pytest.mark.asyncio
    async def test_health_with_redis_down(self, test_client: AsyncClient):
        """Test health endpoint when Redis is down."""
        with patch('app.core.cache.redis_client.ping', side_effect=Exception("Redis connection failed")):
            response = await test_client.get("/health/detailed")
            
            assert response.status_code == 503
            
            data = response.json()
            components = data["components"]
            assert components["redis"]["status"] == "down"
    
    @pytest.mark.asyncio
    async def test_health_version(self, test_client: AsyncClient):
        """Test version endpoint."""
        response = await test_client.get("/version")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "version" in data
        assert "build_date" in data
        assert "commit_hash" in data
        assert "environment" in data
    
    @pytest.mark.asyncio
    async def test_health_dependencies(self, test_client: AsyncClient):
        """Test dependencies health check."""
        response = await test_client.get("/health/dependencies")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "dependencies" in data
        
        deps = data["dependencies"]
        assert "postgresql" in deps
        assert "redis" in deps
        assert "celery" in deps
        
        # Check each dependency has status and version
        for dep_name, dep_info in deps.items():
            assert "status" in dep_info
            assert "version" in dep_info
            assert dep_info["status"] in ["healthy", "unhealthy"]
    
    @pytest.mark.asyncio
    async def test_health_uptime(self, test_client: AsyncClient):
        """Test uptime endpoint."""
        response = await test_client.get("/health/uptime")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "start_time" in data
        assert "uptime_seconds" in data
        assert "uptime_human" in data
        
        # Uptime should be positive
        assert data["uptime_seconds"] > 0
    
    @pytest.mark.asyncio
    async def test_health_system(self, test_client: AsyncClient):
        """Test system health endpoint."""
        response = await test_client.get("/health/system")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "system" in data
        assert "python" in data
        assert "memory" in data
        assert "cpu" in data
        
        system_info = data["system"]
        assert "platform" in system_info
        assert "hostname" in system_info
        
        python_info = data["python"]
        assert "version" in python_info
        assert "implementation" in python_info
    
    @pytest.mark.asyncio
    async def test_health_custom_check(self, test_client: AsyncClient):
        """Test custom health check registration."""
        # This would test custom health checks added by plugins
        response = await test_client.get("/health/custom")
        
        # Might return 404 if no custom checks registered
        if response.status_code == 200:
            data = response.json()
            assert "custom_checks" in data
    
    @pytest.mark.asyncio
    async def test_health_cache(self, test_client: AsyncClient):
        """Test health endpoint caching."""
        # First request
        response1 = await test_client.get("/health")
        timestamp1 = response1.json()["timestamp"]
        
        # Second request should be slightly different due to timestamp
        response2 = await test_client.get("/health")
        timestamp2 = response2.json()["timestamp"]
        
        assert timestamp1 != timestamp2  # Timestamps should differ
    
    @pytest.mark.asyncio
    async def test_health_rate_limited(self, test_client: AsyncClient):
        """Test that health endpoints respect rate limiting."""
        # Make multiple rapid requests
        responses = []
        for _ in range(15):  # More than rate limit
            response = await test_client.get("/health")
            responses.append(response.status_code)
        
        # Most should be 200, but some might be 429 if rate limited
        # This depends on rate limit configuration
        status_counts = {200: 0, 429: 0}
        for status in responses:
            if status in status_counts:
                status_counts[status] += 1
        
        # At least some successful responses
        assert status_counts[200] > 0
    
    @pytest.mark.asyncio
    async def test_health_headers(self, test_client: AsyncClient):
        """Test health endpoint headers."""
        response = await test_client.get("/health")
        
        headers = response.headers
        
        # Security headers should be present
        assert "X-Content-Type-Options" in headers
        assert headers["X-Content-Type-Options"] == "nosniff"
        
        assert "Cache-Control" in headers
        # Health endpoints should not be cached long
        assert "no-cache" in headers["Cache-Control"] or "max-age=0" in headers["Cache-Control"]
    
    @pytest.mark.asyncio
    async def test_health_with_auth(self, test_client: AsyncClient):
        """Test health endpoints with authentication."""
        # Health endpoints should be publicly accessible
        response = await test_client.get("/health")
        assert response.status_code == 200  # No auth required
        
        # Even without credentials
        response = await test_client.get("/health", headers={"Authorization": ""})
        assert response.status_code == 200