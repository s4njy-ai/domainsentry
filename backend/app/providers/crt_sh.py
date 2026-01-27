"""
crt.sh Certificate Transparency provider for DomainSentry.
"""
import asyncio
import json
from typing import Any, Dict, List, Optional

import httpx

from app.providers.base import BaseProvider, ProviderResult


class CrtShProvider(BaseProvider):
    """
    Provider for fetching certificate transparency logs from crt.sh.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('api_url', 'https://crt.sh/')
        self.max_results = config.get('max_results', 100)
        self.timeout = config.get('timeout', 30)
    
    def get_provider_name(self) -> str:
        return "crt.sh"
    
    async def fetch_data(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Fetch certificate transparency logs for a domain.
        """
        if not self.enabled:
            return None
        
        try:
            # Construct the URL for crt.sh API
            # Using the JSON format API: https://crt.sh/JSON?q=example.com
            params = {
                'q': domain,
                'exclude_expired': 'yes',
                'limit': self.max_results
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}",
                    params=params
                )
                
                if response.status_code == 200:
                    certificates = response.json()
                    
                    # Process the certificate data
                    processed_data = self._process_certificates(certificates, domain)
                    
                    return {
                        'provider': self.get_provider_name(),
                        'domain': domain,
                        'certificates': processed_data,
                        'total_found': len(processed_data),
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
        except json.JSONDecodeError as e:
            return {
                'provider': self.get_provider_name(),
                'domain': domain,
                'error': f"JSON decode error: {str(e)}",
                'timestamp': self._get_current_timestamp()
            }
        except Exception as e:
            return {
                'provider': self.get_provider_name(),
                'domain': domain,
                'error': f"Unexpected error: {str(e)}",
                'timestamp': self._get_current_timestamp()
            }
    
    def _process_certificates(self, certificates: List[Dict], domain: str) -> List[Dict]:
        """
        Process raw certificate data from crt.sh.
        """
        processed = []
        
        for cert in certificates:
            processed_cert = {
                'id': cert.get('id'),
                'name_value': cert.get('name_value'),
                'common_name': cert.get('common_name'),
                'ca': cert.get('ca'),
                'publisher': cert.get('publisher'),
                'entry_timestamp': cert.get('entry_timestamp'),
                'not_before': cert.get('not_before'),
                'not_after': cert.get('not_after'),
                'sha1': cert.get('sha1'),
                'sha256': cert.get('sha256'),
                'subject': cert.get('subject'),
                'issuer': cert.get('issuer'),
                'serial_number': cert.get('serial_number'),
            }
            
            processed.append(processed_cert)
        
        return processed
    
    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp in ISO format.
        """
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    async def search_by_fingerprint(self, fingerprint: str) -> Optional[Dict[str, Any]]:
        """
        Search certificates by fingerprint (SHA-1 or SHA-256).
        """
        if not self.enabled:
            return None
        
        try:
            params = {
                'q': fingerprint,
                'exclude_expired': 'yes'
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}",
                    params=params
                )
                
                if response.status_code == 200:
                    certificates = response.json()
                    processed_data = self._process_certificates(certificates, "")
                    
                    return {
                        'provider': self.get_provider_name(),
                        'fingerprint': fingerprint,
                        'certificates': processed_data,
                        'total_found': len(processed_data),
                        'timestamp': self._get_current_timestamp()
                    }
        
        except Exception as e:
            return {
                'provider': self.get_provider_name(),
                'fingerprint': fingerprint,
                'error': f"Error searching by fingerprint: {str(e)}",
                'timestamp': self._get_current_timestamp()
            }
        
        return None