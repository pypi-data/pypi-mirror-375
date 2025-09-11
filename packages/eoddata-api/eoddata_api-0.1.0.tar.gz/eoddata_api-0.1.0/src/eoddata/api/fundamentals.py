"""
Fundamental data API endpoints
"""

from typing import List, Dict
from .base import BaseAPI


class FundamentalsAPI(BaseAPI):
    """
    Fundamental data API endpoints

    Provides access to fundamental financial data like PE ratios, EPS, etc.
    """

    def list(self, exchange_code: str) -> List[Dict]:
        """
        Get fundamental data for all symbols on an exchange

        Args:
            exchange_code: Exchange code

        Returns:
            List of fundamental data objects
        """
        return self.client._request("GET", f"/Fundamental/List/{exchange_code}")

    def get(self, exchange_code: str, symbol_code: str) -> Dict:
        """
        Get fundamental data for a specific symbol

        Args:
            exchange_code: Exchange code
            symbol_code: Symbol code

        Returns:
            Fundamental data object with financial metrics
        """
        return self.client._request("GET", f"/Fundamental/Get/{exchange_code}/{symbol_code}")
