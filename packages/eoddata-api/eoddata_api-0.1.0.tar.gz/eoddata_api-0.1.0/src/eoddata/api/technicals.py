"""
Technical indicators API endpoints
"""

from typing import List, Dict
from .base import BaseAPI


class TechnicalsAPI(BaseAPI):
    """
    Technical indicators API endpoints

    Provides access to pre-calculated technical indicators.
    """

    def list(self, exchange_code: str) -> List[Dict]:
        """
        Get technical indicators for all symbols on an exchange

        Args:
            exchange_code: Exchange code

        Returns:
            List of technical indicator objects
        """
        return self.client._request("GET", f"/Technical/List/{exchange_code}")

    def get(self, exchange_code: str, symbol_code: str) -> Dict:
        """
        Get technical indicators for a specific symbol

        Args:
            exchange_code: Exchange code
            symbol_code: Symbol code

        Returns:
            Technical indicators object with calculated values
        """
        return self.client._request("GET", f"/Technical/Get/{exchange_code}/{symbol_code}")

