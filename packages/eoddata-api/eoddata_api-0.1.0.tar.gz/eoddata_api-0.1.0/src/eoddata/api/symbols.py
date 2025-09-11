"""
Symbols API endpoints
"""

from typing import List, Dict
from .base import BaseAPI


class SymbolsAPI(BaseAPI):
    """
    Symbols API endpoints

    Provides access to symbol listings and information.
    """

    def list(self, exchange_code: str) -> List[Dict]:
        """
        Get list of symbols for a given exchange

        Args:
            exchange_code: Exchange code (e.g., "NASDAQ", "NYSE")

        Returns:
            List of symbol objects with trading information
        """
        return self.client._request("GET", f"/Symbol/List/{exchange_code}")

    def get(self, exchange_code: str, symbol_code: str) -> Dict:
        """
        Get information about a specific symbol

        Args:
            exchange_code: Exchange code
            symbol_code: Symbol code (e.g., "AAPL", "MSFT")

        Returns:
            Symbol object with detailed information
        """
        return self.client._request("GET", f"/Symbol/Get/{exchange_code}/{symbol_code}")
