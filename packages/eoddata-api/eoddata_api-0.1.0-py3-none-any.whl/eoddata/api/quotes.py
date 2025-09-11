"""
Quotes API endpoints
"""

from typing import List, Dict, Optional
from .base import BaseAPI


class QuotesAPI(BaseAPI):
    """
    Quotes API endpoints

    Provides access to current and historical price data.
    """

    def list_by_exchange(self, exchange_code: str, date_stamp: Optional[str] = None) -> List[Dict]:
        """
        Get quotes for all symbols on an exchange for a specific date

        Args:
            exchange_code: Exchange code (e.g., "NASDAQ")
            date_stamp: Date in yyyy-MM-dd format (optional, defaults to latest)

        Returns:
            List of quote objects with OHLCV data
        """
        params = {}
        if date_stamp:
            params['DateStamp'] = date_stamp

        return self.client._request("GET", f"/Quote/List/{exchange_code}", params=params)

    def get(self, exchange_code: str, symbol_code: str, date_stamp: Optional[str] = None) -> Dict:
        """
        Get quote for a specific symbol and date

        Args:
            exchange_code: Exchange code
            symbol_code: Symbol code
            date_stamp: Date in yyyy-MM-dd format (optional, defaults to latest)

        Returns:
            Quote object with OHLCV data
        """
        params = {}
        if date_stamp:
            params['DateStamp'] = date_stamp

        return self.client._request("GET", f"/Quote/Get/{exchange_code}/{symbol_code}", params=params)

    def list_by_symbol(self, exchange_code: str, symbol_code: str,
                       from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        """
        Get historical quotes for a symbol within a date range

        Args:
            exchange_code: Exchange code
            symbol_code: Symbol code
            from_date: Start date in yyyy-MM-dd format (optional)
            to_date: End date in yyyy-MM-dd format (optional)

        Returns:
            List of quote objects with OHLCV data
        """
        params = {}
        if from_date:
            params['FromDateStamp'] = from_date
        if to_date:
            params['ToDateStamp'] = to_date

        return self.client._request("GET", f"/Quote/List/{exchange_code}/{symbol_code}", params=params)
