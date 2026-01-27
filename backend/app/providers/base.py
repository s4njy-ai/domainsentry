"""
Base provider interface for DomainSentry.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseProvider(ABC):
    """
    Abstract base class for all providers.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', True)
    
    @abstractmethod
    async def fetch_data(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Fetch data for a domain.
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of the provider.
        """
        pass
    
    async def is_available(self) -> bool:
        """
        Check if the provider is available.
        """
        return self.enabled


class ProviderResult:
    """
    Result wrapper for provider responses.
    """
    
    def __init__(
        self, 
        success: bool, 
        data: Optional[Dict[str, Any]] = None, 
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.data = data or {}
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = None