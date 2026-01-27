"""
Provider manager service for DomainSentry.
"""
from typing import Dict, List, Optional

from app.providers import CrtShProvider, WhoisProvider
from app.providers.base import BaseProvider, ProviderResult
from app.core.config import settings


class ProviderManager:
    """
    Manager for handling multiple data providers.
    """
    
    def __init__(self):
        self.providers: Dict[str, BaseProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """
        Initialize all configured providers.
        """
        # Initialize crt.sh provider
        crt_sh_config = {
            'enabled': True,
            'api_url': settings.CRT_SH_BASE_URL,
            'max_results': settings.CRT_SH_MAX_RESULTS,
            'timeout': 30
        }
        self.providers['crt_sh'] = CrtShProvider(crt_sh_config)
        
        # Initialize Whois provider
        whois_config = {
            'enabled': bool(settings.WHOISXMLAPI_API_KEY),
            'api_key': settings.WHOISXMLAPI_API_KEY,
            'api_url': 'https://www.whoisxmlapi.com/whoisserver/WhoisService',
            'mock': not settings.WHOISXMLAPI_API_KEY,  # Mock if no API key
            'timeout': 30
        }
        self.providers['whois'] = WhoisProvider(whois_config)
        
        # Optional providers (only enabled if API keys are provided)
        if settings.VIRUSTOTAL_API_KEY:
            from app.providers.virustotal import VirusTotalProvider
            vt_config = {
                'enabled': True,
                'api_key': settings.VIRUSTOTAL_API_KEY,
                'timeout': 30
            }
            self.providers['virustotal'] = VirusTotalProvider(vt_config)
        
        if settings.ABUSEIPDB_API_KEY:
            from app.providers.abuseipdb import AbuseIPDBProvider
            abuse_config = {
                'enabled': True,
                'api_key': settings.ABUSEIPDB_API_KEY,
                'timeout': 30
            }
            self.providers['abuseipdb'] = AbuseIPDBProvider(abuse_config)
    
    async def fetch_all_data(self, domain: str) -> Dict[str, ProviderResult]:
        """
        Fetch data from all enabled providers for a domain.
        """
        results = {}
        
        for provider_name, provider in self.providers.items():
            if provider.enabled:
                try:
                    data = await provider.fetch_data(domain)
                    results[provider_name] = ProviderResult(
                        success=data is not None and 'error' not in data,
                        data=data,
                        error=data.get('error') if data and 'error' in data else None
                    )
                except Exception as e:
                    results[provider_name] = ProviderResult(
                        success=False,
                        error=str(e)
                    )
        
        return results
    
    async def fetch_data(self, provider_name: str, domain: str) -> Optional[ProviderResult]:
        """
        Fetch data from a specific provider.
        """
        if provider_name not in self.providers:
            return ProviderResult(
                success=False,
                error=f"Provider '{provider_name}' not found"
            )
        
        provider = self.providers[provider_name]
        if not provider.enabled:
            return ProviderResult(
                success=False,
                error=f"Provider '{provider_name}' is not enabled"
            )
        
        try:
            data = await provider.fetch_data(domain)
            return ProviderResult(
                success=data is not None and 'error' not in data,
                data=data,
                error=data.get('error') if data and 'error' in data else None
            )
        except Exception as e:
            return ProviderResult(
                success=False,
                error=str(e)
            )
    
    def get_enabled_providers(self) -> List[str]:
        """
        Get list of enabled providers.
        """
        return [name for name, provider in self.providers.items() if provider.enabled]
    
    def get_provider_status(self) -> Dict[str, bool]:
        """
        Get status of all providers.
        """
        return {name: provider.enabled for name, provider in self.providers.items()}
    
    async def test_provider(self, provider_name: str) -> bool:
        """
        Test if a provider is working correctly.
        """
        if provider_name not in self.providers:
            return False
        
        provider = self.providers[provider_name]
        return await provider.is_available()


# Global provider manager instance
provider_manager = ProviderManager()