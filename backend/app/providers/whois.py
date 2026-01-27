"""
WhoisXMLAPI provider for DomainSentry.
"""
import asyncio
from typing import Any, Dict, List, Optional

import httpx

from app.providers.base import BaseProvider, ProviderResult


class WhoisProvider(BaseProvider):
    """
    Provider for fetching WHOIS data from whoisxmlapi.com.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.mock = config.get('mock', False)
        self.base_url = config.get('api_url', 'https://www.whoisxmlapi.com/whoisserver/WhoisService')
        self.timeout = config.get('timeout', 30)
        
        # Mock data for development/testing
        self.mock_data = {
            "domainName": "",
            "createdDate": "2023-01-01",
            "updatedDate": "2023-01-01",
            "expiresDate": "2024-01-01",
            "registrarName": "Example Registrar",
            "registrant": {
                "name": "John Doe",
                "organization": "Example Corp",
                "country": "US",
                "email": "admin@example.com"
            },
            "nameServers": {
                "hostNames": ["ns1.example.com", "ns2.example.com"]
            }
        }
    
    def get_provider_name(self) -> str:
        return "whoisxmlapi.com"
    
    async def fetch_data(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Fetch WHOIS data for a domain.
        """
        if not self.enabled:
            return None
        
        # If mocking is enabled, return mock data
        if self.mock:
            return self._get_mock_data(domain)
        
        # Check if API key is provided
        if not self.api_key:
            return {
                'provider': self.get_provider_name(),
                'domain': domain,
                'error': 'API key not provided',
                'timestamp': self._get_current_timestamp()
            }
        
        try:
            params = {
                'apiKey': self.api_key,
                'domainName': domain,
                'outputFormat': 'JSON'
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.base_url, params=params)
                
                if response.status_code == 200:
                    whois_data = response.json()
                    
                    # Validate response structure
                    if 'ErrorMessage' in whois_data:
                        return {
                            'provider': self.get_provider_name(),
                            'domain': domain,
                            'error': whois_data['ErrorMessage'],
                            'timestamp': self._get_current_timestamp()
                        }
                    
                    # Process the WHOIS data
                    processed_data = self._process_whois_data(whois_data, domain)
                    
                    return {
                        'provider': self.get_provider_name(),
                        'domain': domain,
                        'whois_data': processed_data,
                        'timestamp': self._get_current_timestamp()
                    }
                else:
                    return {
                        'provider': self.get_provider_name(),
                        'domain': domain,
                        'error': f"HTTP {response.status_code}: {response.text}",
                        'timestamp': self._get_current_timestamp()
                    }
        
        except httpx.RequestError as e:
            return {
                'provider': self.get_provider_name(),
                'domain': domain,
                'error': f"Request error: {str(e)}",
                'timestamp': self._get_current_timestamp()
            }
        except Exception as e:
            return {
                'provider': self.get_provider_name(),
                'domain': domain,
                'error': f"Unexpected error: {str(e)}",
                'timestamp': self._get_current_timestamp()
            }
    
    def _process_whois_data(self, raw_data: Dict, domain: str) -> Dict:
        """
        Process raw WHOIS data from whoisxmlapi.com.
        """
        processed = {
            'domain_name': raw_data.get('domainName', domain),
            'created_date': raw_data.get('createdDate'),
            'updated_date': raw_data.get('updatedDate'),
            'expires_date': raw_data.get('expiresDate'),
            'registrar_name': raw_data.get('registrar', {}).get('name') if 'registrar' in raw_data else raw_data.get('registrarName'),
            'registrant': self._extract_registrant(raw_data),
            'name_servers': self._extract_name_servers(raw_data),
            'status': raw_data.get('status', []),
            'dnssec': raw_data.get('dnssec'),
            'raw_data': raw_data
        }
        
        return processed
    
    def _extract_registrant(self, raw_data: Dict) -> Dict:
        """
        Extract registrant information from WHOIS data.
        """
        # Different formats depending on the registry
        registrant = raw_data.get('registrant', {})
        
        if not registrant:
            # Try alternative structures
            if 'contact' in raw_data and 'admin' in raw_data['contact']:
                registrant = raw_data['contact']['admin']
            elif 'registrarData' in raw_data:
                registrant = raw_data['registrarData'].get('registrant', {})
            else:
                # Fallback to flat structure
                registrant = {
                    'name': raw_data.get('registrantName'),
                    'organization': raw_data.get('registrantOrganization'),
                    'street': raw_data.get('registrantStreet'),
                    'city': raw_data.get('registrantCity'),
                    'state': raw_data.get('registrantState'),
                    'postal_code': raw_data.get('registrantZipCode'),
                    'country': raw_data.get('registrantCountry'),
                    'email': raw_data.get('registrantEmail'),
                    'telephone': raw_data.get('registrantTelephone')
                }
        
        return registrant
    
    def _extract_name_servers(self, raw_data: Dict) -> List[str]:
        """
        Extract name servers from WHOIS data.
        """
        name_servers = []
        
        # Different formats depending on the registry
        if 'nameServers' in raw_data:
            ns_data = raw_data['nameServers']
            if isinstance(ns_data, dict) and 'hostNames' in ns_data:
                name_servers = ns_data['hostNames']
            elif isinstance(ns_data, list):
                name_servers = ns_data
            else:
                # Handle flat array
                name_servers = [ns_data] if isinstance(ns_data, str) else []
        elif 'nameServer' in raw_data:
            # Alternative structure
            ns = raw_data['nameServer']
            if isinstance(ns, list):
                name_servers = ns
            elif isinstance(ns, str):
                name_servers = [ns]
        
        return [ns.lower() for ns in name_servers if ns]
    
    def _get_mock_data(self, domain: str) -> Dict:
        """
        Return mock WHOIS data for development/testing.
        """
        mock_result = self.mock_data.copy()
        mock_result['domainName'] = domain
        
        return {
            'provider': self.get_provider_name(),
            'domain': domain,
            'whois_data': self._process_whois_data(mock_result, domain),
            'timestamp': self._get_current_timestamp(),
            'mocked': True
        }
    
    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp in ISO format.
        """
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    async def is_available(self) -> bool:
        """
        Check if the provider is available (and properly configured).
        """
        if not self.enabled:
            return False
        
        if self.mock:
            return True  # Mock is always available
        
        if not self.api_key:
            return False
        
        # Perform a simple test with a known domain
        try:
            result = await self.fetch_data('google.com')
            return result is not None and 'error' not in result
        except:
            return False