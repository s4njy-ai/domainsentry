"""
Redis caching utilities for DomainSentry.
"""
import json
import pickle
from typing import Any, Optional, Union

import aioredis
from app.core.config import settings


class CacheManager:
    """
    Redis cache manager for DomainSentry.
    """
    
    def __init__(self):
        self.redis = None
    
    async def connect(self):
        """
        Connect to Redis.
        """
        self.redis = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=False  # We'll handle encoding manually
        )
    
    async def disconnect(self):
        """
        Disconnect from Redis.
        """
        if self.redis:
            await self.redis.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.
        """
        if not self.redis:
            return None
        
        try:
            value = await self.redis.get(key)
            if value is not None:
                # Try to deserialize as JSON first, then as pickle if that fails
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # If JSON fails, try pickle
                    return pickle.loads(value)
            return None
        except Exception:
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a value in cache.
        """
        if not self.redis:
            return False
        
        try:
            # Serialize as JSON if possible, otherwise use pickle
            try:
                serialized_value = json.dumps(value)
            except (TypeError, ValueError):
                # If JSON serialization fails, use pickle
                serialized_value = pickle.dumps(value)
            
            if ttl is None:
                ttl = settings.REDIS_CACHE_TTL
            
            await self.redis.setex(key, ttl, serialized_value)
            return True
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete a key from cache.
        """
        if not self.redis:
            return False
        
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception:
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """
        Delete keys matching a pattern.
        """
        if not self.redis:
            return 0
        
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
                return len(keys)
            return 0
        except Exception:
            return 0
    
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in cache.
        """
        if not self.redis:
            return False
        
        try:
            return await self.redis.exists(key) > 0
        except Exception:
            return False


# Global cache instance
cache = CacheManager()


# Helper functions for common caching patterns
async def get_cached_domain(domain_name: str) -> Optional[dict]:
    """
    Get cached domain information.
    """
    key = f"domain:{domain_name}"
    return await cache.get(key)


async def set_cached_domain(domain_name: str, domain_data: dict, ttl: int = 300) -> bool:
    """
    Cache domain information.
    """
    key = f"domain:{domain_name}"
    return await cache.set(key, domain_data, ttl)


async def invalidate_domain_cache(domain_name: str) -> bool:
    """
    Invalidate cached domain information.
    """
    key = f"domain:{domain_name}"
    return await cache.delete(key)


async def get_cached_risk_analysis(domain_name: str) -> Optional[dict]:
    """
    Get cached risk analysis.
    """
    key = f"risk:{domain_name}"
    return await cache.get(key)


async def set_cached_risk_analysis(domain_name: str, risk_data: dict, ttl: int = 1800) -> bool:
    """
    Cache risk analysis.
    """
    key = f"risk:{domain_name}"
    return await cache.set(key, risk_data, ttl)