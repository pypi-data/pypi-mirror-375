"""
Corporate API endpoints (profiles, splits, dividends)
"""

from typing import List, Dict
from .base import BaseAPI


class CorporateAPI(BaseAPI):
    """
    Corporate API endpoints

    Provides access to company profiles, stock splits, and dividend information.
    """

    def profiles_list(self, exchange_code: str) -> List[Dict]:
        """
        Get list of symbol profiles for an exchange

        Args:
            exchange_code: Exchange code

        Returns:
            List of profile objects with company information
        """
        return self.client._request("GET", f"/Profile/List/{exchange_code}")

    def profile_get(self, exchange_code: str, symbol_code: str) -> Dict:
        """
        Get profile information for a specific symbol

        Args:
            exchange_code: Exchange code
            symbol_code: Symbol code

        Returns:
            Profile object with detailed company information
        """
        return self.client._request("GET", f"/Profile/Get/{exchange_code}/{symbol_code}")

    def splits_by_exchange(self, exchange_code: str) -> List[Dict]:
        """
        Get recent stock splits for an exchange

        Args:
            exchange_code: Exchange code

        Returns:
            List of split objects
        """
        return self.client._request("GET", f"/Splits/List/{exchange_code}")

    def splits_by_symbol(self, exchange_code: str, symbol_code: str) -> List[Dict]:
        """
        Get stock splits for a specific symbol

        Args:
            exchange_code: Exchange code
            symbol_code: Symbol code

        Returns:
            List of split objects
        """
        return self.client._request("GET", f"/Splits/List/{exchange_code}/{symbol_code}")

    def dividends_by_exchange(self, exchange_code: str) -> List[Dict]:
        """
        Get dividends for an exchange

        Args:
            exchange_code: Exchange code

        Returns:
            List of dividend objects
        """
        return self.client._request("GET", f"/Dividends/List/{exchange_code}")

    def dividends_by_symbol(self, exchange_code: str, symbol_code: str) -> List[Dict]:
        """
        Get dividends for a specific symbol

        Args:
            exchange_code: Exchange code
            symbol_code: Symbol code

        Returns:
            List of dividend objects
        """
        return self.client._request("GET", f"/Dividends/List/{exchange_code}/{symbol_code}")
