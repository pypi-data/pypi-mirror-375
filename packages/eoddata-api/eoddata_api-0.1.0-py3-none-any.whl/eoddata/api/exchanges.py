"""
Exchanges API endpoints
"""

from typing import List, Dict
from .base import BaseAPI


class ExchangesAPI(BaseAPI):
    """
    Exchanges API endpoints

    Provides access to exchange information and listings.
    """

    def list(self) -> List[Dict]:
        """
        Get list of available exchanges

        Returns:
            List of exchange objects with details like code, name, country, currency, etc.
        """
        return self.client._request("GET", "/Exchange/List")

    def get(self, exchange_code: str) -> Dict:
        """
        Get information about a specific exchange

        Args:
            exchange_code: Exchange code (e.g., "NASDAQ", "NYSE")

        Returns:
            Exchange object with detailed information
        """
        return self.client._request("GET", f"/Exchange/Get/{exchange_code}")
