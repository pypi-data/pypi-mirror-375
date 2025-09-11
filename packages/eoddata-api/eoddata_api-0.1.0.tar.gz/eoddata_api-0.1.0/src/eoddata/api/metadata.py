"""
Metadata API endpoints
"""

from typing import List, Dict
from .base import BaseAPI


class MetadataAPI(BaseAPI):
    """
    Metadata API endpoints

    Provides access to exchange types, symbol types, countries, and currencies.
    These endpoints don't require authentication.
    """

    def exchange_types(self) -> List[Dict[str, str]]:
        """
        Get list of exchange types

        Returns:
            List of exchange type objects with 'name' field
        """
        return self.client._request("GET", "/ExchangeType/List", params={})

    def symbol_types(self) -> List[Dict[str, str]]:
        """
        Get list of symbol types

        Returns:
            List of symbol type objects with 'name' field
        """
        return self.client._request("GET", "/SymbolType/List", params={})

    def countries(self) -> List[Dict[str, str]]:
        """
        Get list of countries

        Returns:
            List of country objects with 'code' and 'name' fields
        """
        return self.client._request("GET", "/Country/List", params={})

    def currencies(self) -> List[Dict[str, str]]:
        """
        Get list of currencies

        Returns:
            List of currency objects with 'code' and 'name' fields
        """
        return self.client._request("GET", "/Currency/List", params={})
