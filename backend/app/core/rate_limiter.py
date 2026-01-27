"""
Rate limiting middleware for DomainSentry using slowapi.
"""
from functools import wraps
from typing import Callable, Optional

from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import settings


# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_REQUESTS} per {settings.RATE_LIMIT_PERIOD} seconds"]
)


def get_rate_limit_config():
    """
    Get rate limit configuration.
    """
    return {
        "requests": settings.RATE_LIMIT_REQUESTS,
        "period": settings.RATE_LIMIT_PERIOD
    }


def setup_rate_limiter(app):
    """
    Setup rate limiter for FastAPI app.
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def rate_limit(limit: str):
    """
    Decorator to apply rate limiting to routes.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs or args
            request = kwargs.get("request") or next((arg for arg in args if isinstance(arg, Request)), None)
            
            if request:
                # Apply rate limiting
                await limiter.hit(limit, request.state.identifier if hasattr(request.state, 'identifier') else get_remote_address(request))
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator